#!/usr/bin/env python3
"""Reference validator — check if cited papers actually exist.

Chain order (first successful hit wins):
  1. DOI redirect validation
  2. Crossref bibliographic search
  3. OpenAlex title search
  4. Semantic Scholar title+year search

Usage:
  refcheck "Kambhampati 2024 LLMs can't plan"
  refcheck --doi "10.48550/arXiv.2402.01817"
  refcheck --title "Chain-of-thought prompting" --author "Wei" --year 2022
  refcheck --bib references.bib --rate-limit 1.0
"""

import argparse
import sys
import time
from dataclasses import asdict
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.refcheck.bibtex import parse_bib_file
from tools.refcheck.cache import JSONFileCache, TitleIndex
from tools.refcheck.executors.arxiv import ArxivExecutor
from tools.refcheck.executors.crossref import CrossrefExecutor
from tools.refcheck.executors.doi import DOIExecutor
from tools.refcheck.executors.openalex import OpenAlexExecutor
from tools.refcheck.executors.semantic_scholar import SemanticScholarExecutor
from tools.refcheck.models import ReferenceQuery, ReferenceResult

EXECUTORS = [
    DOIExecutor(),
    ArxivExecutor(),
    CrossrefExecutor(),
    OpenAlexExecutor(),
    SemanticScholarExecutor(),
]


def check_one(
    query: ReferenceQuery,
    cache: JSONFileCache,
    title_index: TitleIndex,
) -> ReferenceResult | None:
    """Run the executor chain for a single reference. First hit wins."""

    # 1. Check cache by DOI
    if query.doi:
        cached = cache.get(query.doi)
        if cached:
            result = _dict_to_result(cached)
            result.cache_hit = True
            return result

    # 2. Check cache by title → DOI lookup
    if query.title:
        known_doi = title_index.get_doi(query.title)
        if known_doi:
            cached = cache.get(known_doi)
            if cached:
                result = _dict_to_result(cached)
                result.cache_hit = True
                return result
            # Known DOI but expired cache — inject DOI into query for chain
            if not query.doi:
                query.doi = known_doi

    # 3. Run executor chain
    for executor in EXECUTORS:
        result = executor.check(query)
        if result is not None:
            # Cache the result
            if result.doi:
                cache.set(result.doi, asdict(result))
                if result.title:
                    title_index.put(result.title, result.doi)
            elif result.title:
                # No DOI found, cache by title hash
                cache.set(f"title:{result.title.lower()}", asdict(result))
            return result

    return None


def _dict_to_result(d: dict) -> ReferenceResult:
    """Reconstruct ReferenceResult from cached dict."""
    return ReferenceResult(
        source=d.get("source", "cache"),
        title=d.get("title", ""),
        authors=d.get("authors", []),
        year=d.get("year"),
        doi=d.get("doi"),
        url=d.get("url"),
        confidence=d.get("confidence", 1.0),
        cache_hit=True,
        raw=d.get("raw", {}),
    )


def format_result(query_label: str, result: ReferenceResult | None) -> str:
    """Format a single check result for terminal output."""
    if result is None:
        return f"\u2717 [all failed] {query_label} \u2014 NOT FOUND"

    parts = []
    # Authors
    if result.authors:
        first = result.authors[0].split()[-1]  # last name
        if len(result.authors) > 1:
            parts.append(f"{first} et al.")
        else:
            parts.append(first)
    # Year
    if result.year:
        parts.append(f"({result.year})")
    # Title (truncated)
    title = result.title
    if len(title) > 60:
        title = title[:57] + "..."
    parts.append(f'"{title}"')
    # DOI
    if result.doi:
        parts.append(f"DOI: {result.doi}")
    # Cache
    cache_tag = " (cached)" if result.cache_hit else ""

    return f"\u2713 [{result.source}] {' '.join(parts)}{cache_tag}"


def parse_free_text(text: str) -> ReferenceQuery:
    """Best-effort parse of a free-form reference string."""
    import re

    query = ReferenceQuery(raw_text=text)

    # Try to extract year (4 digits, 19xx or 20xx)
    year_match = re.search(r"\b((?:19|20)\d{2})\b", text)
    if year_match:
        query.year = int(year_match.group(1))

    # Try to extract DOI
    doi_match = re.search(r"(10\.\d{4,}/\S+)", text)
    if doi_match:
        query.doi = doi_match.group(1).rstrip(".,;)")

    # Use whole text as title guess (minus year/doi if found)
    title = text
    if year_match:
        title = title.replace(year_match.group(0), "").strip()
    if doi_match:
        title = title.replace(doi_match.group(0), "").strip()
    # Clean up leftover punctuation
    title = re.sub(r"\s+", " ", title).strip(" .,;:-")
    if title:
        query.title = title

    return query


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate academic references against real databases."
    )
    parser.add_argument("query", nargs="?", help="Free-form reference string")
    parser.add_argument("--title", help="Paper title")
    parser.add_argument("--author", action="append", help="Author name (repeatable)")
    parser.add_argument("--year", type=int, help="Publication year")
    parser.add_argument("--doi", help="DOI identifier")
    parser.add_argument("--bib", help="Path to .bib file for batch validation")
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Max requests per second (default: 1.0)",
    )

    args = parser.parse_args()

    cache = JSONFileCache()
    title_index = TitleIndex()
    delay = 1.0 / args.rate_limit if args.rate_limit > 0 else 0

    queries: list[tuple[str, ReferenceQuery]] = []

    if args.bib:
        # Batch mode
        entries = parse_bib_file(args.bib)
        if not entries:
            print(f"No entries found in {args.bib}", file=sys.stderr)
            sys.exit(1)
        for entry in entries:
            label = f"{entry.cite_key}: {entry.title or '(no title)'}"
            q = ReferenceQuery(
                title=entry.title,
                authors=entry.author_list(),
                year=entry.year,
                doi=entry.doi,
            )
            queries.append((label, q))
    elif args.title or args.doi or args.author:
        # Structured query
        q = ReferenceQuery(
            title=args.title,
            authors=args.author or [],
            year=args.year,
            doi=args.doi,
        )
        label = args.title or args.doi or "query"
        queries.append((label, q))
    elif args.query:
        # Free-form
        q = parse_free_text(args.query)
        queries.append((args.query, q))
    else:
        parser.print_help()
        sys.exit(1)

    found = 0
    total = len(queries)

    for i, (label, query) in enumerate(queries):
        result = check_one(query, cache, title_index)
        print(format_result(label, result))
        if result is not None:
            found += 1

        # Rate limiting between requests (skip for cache hits and last item)
        if i < total - 1 and delay > 0 and (result is None or not result.cache_hit):
            time.sleep(delay)

    if total > 1:
        print(f"\n{found}/{total} references validated")

    sys.exit(0 if found == total else 1)


if __name__ == "__main__":
    main()
