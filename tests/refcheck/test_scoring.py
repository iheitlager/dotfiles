"""Tests for refcheck title matching and bib parsing."""

from tools.refcheck.bibtex import parse_bib_file
from tools.refcheck.models import ReferenceQuery
from tools.refcheck.scoring import MIN_TITLE_SIMILARITY, best_similarity


def test_same_title_passes_threshold():
    q = ReferenceQuery(title="Chain-of-thought prompting elicits reasoning")
    assert best_similarity(q, "Chain-of-Thought Prompting Elicits Reasoning") >= MIN_TITLE_SIMILARITY


def test_unrelated_title_fails_threshold():
    q = ReferenceQuery(title="Digital Sovereignty as a Quality Attribute")
    candidate = "A Study of Software Architecture Erosion in Large Systems"
    assert best_similarity(q, candidate) < MIN_TITLE_SIMILARITY


def test_empty_query_scores_zero():
    assert best_similarity(ReferenceQuery(), "Anything") == 0.0


def test_parse_bib_file(tmp_path):
    bib = tmp_path / "refs.bib"
    bib.write_text("@article{wei2022,\n  title={Chain-of-thought prompting},\n  author={Wei, Jason},\n  year={2022}\n}\n")
    entries = parse_bib_file(bib)
    assert len(entries) == 1
    assert entries[0].year == 2022
