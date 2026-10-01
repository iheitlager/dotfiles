"""JSON file cache with 30-day TTL, keyed by MD5 hash.

Adapted from paper-scanner's JSONFileCache pattern.
Uses XDG_CACHE_HOME — non-essential cached data, safe to delete.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

CACHE_DIR = Path(
    __import__("os").environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
) / "my-brain" / "refcheck"

DEFAULT_TTL = timedelta(days=30)


def _hash_key(key: str) -> str:
    """MD5 hash of key for filesystem-safe filenames."""
    return hashlib.md5(key.encode()).hexdigest()


class JSONFileCache:
    """File-per-entry JSON cache with TTL expiry."""

    def __init__(self, cache_dir: Path | None = None, ttl: timedelta = DEFAULT_TTL):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{_hash_key(key)}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """Return cached value or None if missing/expired."""
        path = self._path(key)
        if not path.exists():
            return None
        age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
        if age > self.ttl:
            path.unlink()
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Write value to cache."""
        path = self._path(key)
        path.write_text(json.dumps(data))


class TitleIndex:
    """Maps normalized titles to DOIs for cross-query cache hits."""

    def __init__(self, cache_dir: Path | None = None):
        self.index_file = (cache_dir or CACHE_DIR) / "title_index.json"
        self._index: dict[str, str] | None = None

    def _load(self) -> dict[str, str]:
        if self._index is not None:
            return self._index
        if self.index_file.exists():
            try:
                self._index = json.loads(self.index_file.read_text())
            except (json.JSONDecodeError, OSError):
                self._index = {}
        else:
            self._index = {}
        return self._index

    def _save(self) -> None:
        if self._index is not None:
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            self.index_file.write_text(json.dumps(self._index))

    @staticmethod
    def normalize_title(title: str) -> str:
        """Lowercase, strip punctuation and whitespace for matching."""
        import re
        return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()

    def get_doi(self, title: str) -> str | None:
        """Look up DOI by normalized title."""
        return self._load().get(self.normalize_title(title))

    def put(self, title: str, doi: str) -> None:
        """Register title → DOI mapping."""
        idx = self._load()
        idx[self.normalize_title(title)] = doi
        self._save()
