"""Reverse engineer command implementation for arch CLI.

Extracts architectural resources from code and config files,
displaying results and optionally saving to architecture directory.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from ..model import ArchitectureModel
from ..reverse_engineer import ReverseEngineer
from ..loader import save_architecture


def render_reverse_engineer(
    model: ArchitectureModel,
    output_path: Optional[Path] = None,
    interactive: bool = False,
) -> int:
    """Render reverse engineering results.

    Args:
        model: Extracted architecture model
        output_path: Where to save the model (if provided)
        interactive: Whether to prompt for confirmation before saving

    Returns:
        Exit code: 0 for success, 1 for error
    """
    console = Console()

    # Display summary
    console.print("\n[bold]🔍 Reverse Engineering Results[/bold]\n")

    if not model.resources:
        console.print("[yellow]⚠️  No resources extracted[/yellow]")
        console.print("   Try a different source directory or check file formats")
        return 0

    # Show resource count
    console.print(f"[green]✓[/green] Extracted {len(model.resources)} resource(s)\n")

    # Build summary table
    table = Table(title="Extracted Resources", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Type", style="yellow")
    table.add_column("Interfaces", style="green")

    for resource in model.resources:
        table.add_row(
            resource.id,
            resource.name,
            resource.type,
            str(len(resource.interfaces))
        )

    console.print(table)

    # Show extraction errors if any
    if hasattr(model, 'metadata') and 'extraction_errors' in model.metadata:
        errors = model.metadata['extraction_errors']
        console.print(f"\n[yellow]⚠️  {len(errors)} extraction error(s) occurred[/yellow]")
        for error in errors[:5]:  # Show first 5
            console.print(f"   {error}")
        if len(errors) > 5:
            console.print(f"   ... and {len(errors) - 5} more")

    # Handle output
    if output_path:
        # Interactive confirmation
        if interactive:
            console.print()
            confirmed = Confirm.ask(
                f"Save extracted architecture to [cyan]{output_path}[/cyan]?",
                default=True
            )
            if not confirmed:
                console.print("\n[yellow]Cancelled - no files written[/yellow]")
                return 0

        # Save to file
        try:
            save_architecture(model, output_path)
            console.print(f"\n[green]✓[/green] Architecture saved to: [cyan]{output_path}[/cyan]")

            # Suggest next steps
            console.print("\n[bold]Next steps:[/bold]")
            console.print("  arch validate         Validate the extracted architecture")
            console.print("  arch list             List all extracted resources")
            console.print("  arch diagram          Generate diagrams from the model")

            return 0

        except Exception as e:
            console.print(f"\n[red]✗[/red] Failed to save: {e}", style="red")
            return 1

    else:
        # No output path - just display results
        console.print("\n[dim]Use --output to save the extracted architecture[/dim]")
        return 0


def run_reverse_engineer(
    source: Path,
    output: Optional[Path] = None,
    interactive: bool = False,
    recursive: bool = True,
) -> int:
    """Run reverse engineering on source directory.

    Args:
        source: Source directory to analyze
        output: Output file path (optional)
        interactive: Whether to prompt before saving
        recursive: Whether to scan recursively

    Returns:
        Exit code: 0 for success, 1 for error
    """
    console = Console()

    console.print(f"\n[bold]🔍 Reverse Engineering[/bold]")
    console.print(f"   Source: [cyan]{source}[/cyan]")
    if output:
        console.print(f"   Output: [cyan]{output}[/cyan]")
    console.print()

    try:
        # Initialize reverse engineer
        reverser = ReverseEngineer()

        # Show available extractors
        extractors = reverser.get_extractor_info()
        console.print("[bold]Available extractors:[/bold]")
        for name, description in extractors.items():
            console.print(f"  • {name}: {description}")
        console.print()

        # Extract architecture
        console.print("[bold]Scanning files...[/bold]")
        model = reverser.extract_from_directory(
            source,
            recursive=recursive
        )

        # Render results
        return render_reverse_engineer(model, output, interactive)

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}", style="red")
        return 1
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}", style="red")
        import traceback
        traceback.print_exc()
        return 1
