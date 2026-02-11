"""List command implementation for arch CLI.

Displays architecture resources in a tree structure with metadata,
color-coding, and filtering options.
"""

from typing import Optional, List
from rich.console import Console
from rich.tree import Tree
from rich.text import Text

from ..model import Resource, ArchitectureModel
from ..path_resolver import PathResolver


def _get_resource_icon(resource: Resource) -> str:
    """Get an appropriate emoji icon for a resource type."""
    type_icons = {
        "system": "📦",
        "bash-script": "🔧",
        "go-service": "🚀",
        "web-app": "🌐",
        "ios-app": "📱",
        "filesystem": "📁",
        "rds-postgresql": "🗄️",
        "elasticache-redis": "💾",
        "s3-bucket": "🪣",
        "kafka": "📨",
        "sagemaker-endpoint": "🤖",
        "step-functions-workflow": "⚙️",
    }

    # Try exact match first
    if resource.type in type_icons:
        return type_icons[resource.type]

    # Try partial matches
    type_lower = resource.type.lower()
    if "service" in type_lower:
        return "🚀"
    elif "script" in type_lower:
        return "🔧"
    elif "app" in type_lower:
        return "📱"
    elif "database" in type_lower or "db" in type_lower:
        return "🗄️"
    elif "cache" in type_lower:
        return "💾"
    elif "storage" in type_lower or "bucket" in type_lower:
        return "🪣"
    elif "workflow" in type_lower or "pipeline" in type_lower:
        return "⚙️"

    # Default icon
    return "📄"


def _format_resource_label(resource: Resource) -> Text:
    """Format a resource label with color coding and metadata."""
    icon = _get_resource_icon(resource)

    # Build label text
    label = f"{icon} {resource.name} ({resource.id})"

    # Add type in brackets
    label += f" [{resource.type}]"

    # Add technology if present
    if resource.technology:
        label += f" • {resource.technology}"

    # Color code based on abstract/concrete
    if resource.abstract:
        # Abstract resources in dim/gray
        text = Text(label, style="dim")
    else:
        # Concrete resources in green
        text = Text(label, style="green")

    return text


def _add_resource_details(tree: Tree, resource: Resource) -> None:
    """Add interface and child count details to a resource tree node."""
    # Show interface count and details
    if resource.interfaces:
        interface_branch = tree.add(f"[cyan]Interfaces: {len(resource.interfaces)}[/cyan]")
        for interface in resource.interfaces:
            interface_label = (
                f"[yellow]→[/yellow] {interface.id} "
                f"[dim]({interface.protocol}, {interface.direction})[/dim]"
            )
            interface_branch.add(interface_label)


def _build_resource_tree(resource: Resource, parent_tree: Optional[Tree] = None) -> Tree:
    """Recursively build a tree for a resource and its children."""
    # Create label with color coding
    label = _format_resource_label(resource)

    # Create tree node
    if parent_tree is None:
        tree = Tree(label)
    else:
        tree = parent_tree.add(label)

    # Add interfaces as details
    if resource.interfaces:
        _add_resource_details(tree, resource)

    # Recursively add children
    for child in resource.children:
        _build_resource_tree(child, tree)

    return tree


def _filter_resources(
    resources: List[Resource],
    resource_type: Optional[str] = None,
    tag: Optional[str] = None,
    query: Optional[str] = None,
) -> List[Resource]:
    """Filter resources based on type, tag, or query."""
    filtered = resources

    # Filter by type
    if resource_type:
        filtered = [r for r in filtered if r.type == resource_type]

    # Filter by tag
    if tag:
        filtered = [r for r in filtered if tag in r.tags]

    # Filter by query (search in name or description)
    if query:
        query_lower = query.lower()
        filtered = [
            r for r in filtered
            if query_lower in r.name.lower()
            or (r.description and query_lower in r.description.lower())
        ]

    return filtered


def render_list(
    model: ArchitectureModel,
    resolver: PathResolver,
    resource_type: Optional[str] = None,
    tag: Optional[str] = None,
    query: Optional[str] = None,
    protocol: Optional[str] = None,
) -> None:
    """Render the architecture model as a tree structure.

    Args:
        model: The architecture model to display
        resolver: PathResolver for filtering operations
        resource_type: Filter by resource type (e.g., "go-service")
        tag: Filter by tag
        query: Search query for name/description
        protocol: Filter interfaces by protocol
    """
    console = Console()

    # Apply filters
    resources = model.resources

    if resource_type or tag or query:
        resources = _filter_resources(resources, resource_type, tag, query)

    if not resources:
        console.print("[yellow]No resources found matching filters.[/yellow]")
        return

    # Build and display tree for each root resource
    for resource in resources:
        tree = _build_resource_tree(resource)
        console.print(tree)
        console.print()  # Blank line between trees

    # Display summary statistics
    total_resources = model.resource_count()
    total_interfaces = model.interface_count()
    total_relationships = len(model.relationships)

    console.print("[bold]Summary:[/bold]")
    console.print(f"  Resources: {total_resources}")
    console.print(f"  Interfaces: {total_interfaces}")
    console.print(f"  Relationships: {total_relationships}")

    # Show filter info if applied
    if resource_type or tag or query or protocol:
        console.print(f"\n[dim]Filters applied:[/dim]")
        if resource_type:
            console.print(f"  [dim]Type: {resource_type}[/dim]")
        if tag:
            console.print(f"  [dim]Tag: {tag}[/dim]")
        if query:
            console.print(f"  [dim]Query: {query}[/dim]")
        if protocol:
            console.print(f"  [dim]Protocol: {protocol}[/dim]")
