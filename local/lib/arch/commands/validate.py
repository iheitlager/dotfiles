"""Validate command implementation for arch CLI.

Displays validation results with schema validation, referential integrity
checks, error/warning tables, and summary statistics.
"""

from rich.console import Console
from rich.table import Table

from ..model import ArchitectureModel
from ..validator import ValidationResult


def render_validate(
    model: ArchitectureModel,
    result: ValidationResult,
) -> int:
    """Render validation results with summary statistics.

    Args:
        model: The architecture model that was validated
        result: Validation result from ArchitectureValidator

    Returns:
        Exit code: 0 for valid, 1 for invalid
    """
    console = Console()

    # Display results
    if result.valid:
        console.print("✅ [bold green]Validation passed[/bold green]")
        console.print(f"   No errors found")

        if result.warnings:
            console.print(f"\n⚠️  [bold yellow]{len(result.warnings)} warning(s)[/bold yellow]")
            for warning in result.warnings:
                console.print(f"   [yellow]•[/yellow] {warning.message}")
                if warning.path:
                    console.print(f"     Path: {warning.path}")

    else:
        console.print(f"❌ [bold red]Validation failed[/bold red]")
        console.print(f"   {len(result.errors)} error(s), {len(result.warnings)} warning(s)\n")

        # Show errors in table
        if result.errors:
            table = Table(title="Errors", show_header=True, header_style="bold red")
            table.add_column("Rule", style="cyan")
            table.add_column("Message", style="white")
            table.add_column("Path", style="yellow")

            for error in result.errors:
                table.add_row(
                    error.rule or "—",
                    error.message,
                    error.path or "—"
                )

            console.print(table)

        # Show warnings in table
        if result.warnings:
            console.print()
            table = Table(title="Warnings", show_header=True, header_style="bold yellow")
            table.add_column("Rule", style="cyan")
            table.add_column("Message", style="white")
            table.add_column("Path", style="yellow")

            for warning in result.warnings:
                table.add_row(
                    warning.rule or "—",
                    warning.message,
                    warning.path or "—"
                )

            console.print(table)

    # Display summary statistics (always shown)
    console.print()
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Resources: {model.resource_count()}")
    console.print(f"  Interfaces: {model.interface_count()}")
    console.print(f"  Relationships: {len(model.relationships)}")
    console.print(f"  Sequences: {model.sequence_count()}")
    console.print(f"  State Machines: {model.state_machine_count()}")

    # Final status message
    console.print()
    if result.valid:
        console.print("✅ [bold green]Architecture is valid[/bold green]")
        return 0
    else:
        console.print("❌ [bold red]Architecture is invalid[/bold red]")
        return 1
