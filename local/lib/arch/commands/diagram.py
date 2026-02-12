"""Diagram command implementation for arch CLI.

Generates architecture diagrams in various formats (currently Mermaid)
with support for different zoom levels and output destinations.
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

from ..model import ArchitectureModel
from ..path_resolver import PathResolver
from ..generators.mermaid import generate_mermaid


def render_diagram(
    model: ArchitectureModel,
    resolver: PathResolver,
    format: str = "mermaid",
    zoom: str = "landscape",
    output: Optional[str] = None,
    preview: bool = False,
) -> int:
    """Render architecture diagram.

    Args:
        model: The architecture model to visualize
        resolver: PathResolver for filtering
        format: Diagram format ("mermaid" currently)
        zoom: View level ("landscape", "domain", "service")
        output: Optional output file path
        preview: Whether to preview with glow (if available)

    Returns:
        Exit code: 0 for success, 1 for error
    """
    # Generate diagram based on format
    if format == "mermaid":
        diagram = generate_mermaid(model, resolver, zoom)
    else:
        print(f"Error: Unsupported format '{format}'", file=sys.stderr)
        return 1

    # Handle output destination
    if output:
        # Write to file with markdown wrapper
        output_path = Path(output)
        _write_diagram_file(diagram, output_path, format)
        print(f"✅ Diagram written to: {output}")

        # Optional preview
        if preview and _has_glow():
            _preview_with_glow(output_path)

    else:
        # Print to stdout
        print(diagram)

    return 0


def _write_diagram_file(diagram: str, output_path: Path, format: str) -> None:
    """Write diagram to file with markdown code fence.

    Args:
        diagram: The diagram content
        output_path: Where to write the file
        format: Diagram format (for code fence language)
    """
    content = f"""# Architecture Diagram

```{format}
{diagram}
```
"""
    output_path.write_text(content)


def _has_glow() -> bool:
    """Check if glow is available for previewing markdown.

    Returns:
        True if glow command is available
    """
    try:
        subprocess.run(
            ["glow", "--version"],
            capture_output=True,
            check=False
        )
        return True
    except FileNotFoundError:
        return False


def _preview_with_glow(file_path: Path) -> None:
    """Preview markdown file with glow.

    Args:
        file_path: Path to markdown file
    """
    try:
        subprocess.run(
            ["glow", str(file_path)],
            check=False
        )
    except Exception as e:
        print(f"Warning: Could not preview with glow: {e}", file=sys.stderr)
