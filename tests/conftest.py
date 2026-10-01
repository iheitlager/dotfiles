"""pytest configuration for dotfiles tests."""

import sys
from pathlib import Path

# Add local/lib to Python path so arch module can be imported
repo_root = Path(__file__).parent.parent
lib_path = repo_root / "local" / "lib"
sys.path.insert(0, str(lib_path))

# Add claude/ so the refcheck package (tools.refcheck) can be imported
sys.path.insert(0, str(repo_root / "claude"))
