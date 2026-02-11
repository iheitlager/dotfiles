"""Mermaid diagram generator for architecture models.

Generates Mermaid flowchart diagrams from Grounded C4 architecture models
with support for multiple zoom levels (landscape, domain, service).
"""

from typing import List, Tuple, Set
from ..model import Resource, Relationship, Interface, ArchitectureModel
from ..path_resolver import PathResolver


def generate_mermaid(
    model: ArchitectureModel,
    resolver: PathResolver,
    zoom: str = "landscape",
) -> str:
    """Generate Mermaid diagram from architecture model.

    Args:
        model: The architecture model to visualize
        resolver: PathResolver for looking up resources/interfaces
        zoom: View level - "landscape" | "domain" | "service"

    Returns:
        Mermaid diagram as a string
    """
    # Collect nodes and relationships for this zoom level
    nodes, relationships = _collect_nodes_for_view(model, resolver, zoom)

    # Render as Mermaid syntax
    diagram = _render_mermaid_graph(nodes, relationships, resolver, zoom)

    return diagram


def _collect_nodes_for_view(
    model: ArchitectureModel,
    resolver: PathResolver,
    zoom: str,
) -> Tuple[List[Resource], List[Relationship]]:
    """Filter resources and relationships based on zoom level.

    Args:
        model: Architecture model
        resolver: PathResolver for filtering
        zoom: View level

    Returns:
        Tuple of (resources to include, relationships to include)
    """
    nodes = []

    if zoom == "landscape":
        # Landscape: Only root resources (depth 0)
        nodes = model.resources

    elif zoom == "domain":
        # Domain: Abstract resources and their direct children
        for resource in model.resources:
            for res, depth in resource.walk_tree():
                # Include root, abstract resources, and direct children of abstract
                if depth == 0 or res.abstract:
                    if res not in nodes:
                        nodes.append(res)
                # Include direct children of abstract resources
                elif res.parent and res.parent.abstract:
                    if res not in nodes:
                        nodes.append(res)

    elif zoom == "service":
        # Service: All concrete resources with interfaces
        for resource in model.resources:
            for res, depth in resource.walk_tree():
                if not res.abstract:
                    nodes.append(res)

    else:
        # Default: show everything
        for resource in model.resources:
            for res, depth in resource.walk_tree():
                nodes.append(res)

    # Filter relationships to only include those between visible nodes
    node_paths = {n.full_path for n in nodes}

    # Also include interface paths for service view
    interface_paths = set()
    if zoom == "service":
        for node in nodes:
            for interface in node.interfaces:
                interface_paths.add(f"{node.full_path}.{interface.id}")

    visible_paths = node_paths | interface_paths

    filtered_relationships = []
    for rel in model.relationships:
        # Parse from/to to get resource paths (strip interface suffix if present)
        from_parts = rel.from_ref.split(".")
        to_parts = rel.to_ref.split(".")

        # Check if both endpoints are visible
        # Try full path first (for interfaces), then resource path
        from_visible = rel.from_ref in visible_paths
        to_visible = rel.to_ref in visible_paths

        # Also check if the resource part is visible (ignore interface suffix)
        if not from_visible:
            from_result = resolver.resolve(rel.from_ref)
            if from_result.found and from_result.resource:
                from_visible = from_result.resource.full_path in node_paths

        if not to_visible:
            to_result = resolver.resolve(rel.to_ref)
            if to_result.found and to_result.resource:
                to_visible = to_result.resource.full_path in node_paths

        if from_visible and to_visible:
            filtered_relationships.append(rel)

    return nodes, filtered_relationships


def _render_mermaid_graph(
    nodes: List[Resource],
    relationships: List[Relationship],
    resolver: PathResolver,
    zoom: str,
) -> str:
    """Render filtered nodes and relationships as Mermaid syntax.

    Args:
        nodes: Resources to include
        relationships: Relationships to include
        resolver: PathResolver for lookups
        zoom: View level (affects detail shown)

    Returns:
        Mermaid diagram string
    """
    lines = ["graph TB"]

    # Track which IDs we've seen to avoid duplicates
    seen_ids = set()

    # Render nodes
    if zoom == "domain":
        # For domain view, group by abstract parents
        _render_domain_view(lines, nodes, seen_ids)
    else:
        # For landscape and service views, render flat
        for resource in nodes:
            node_id = _sanitize_id(resource.full_path)
            if node_id in seen_ids:
                continue
            seen_ids.add(node_id)

            label = _format_node_label(resource, include_type=(zoom != "landscape"))
            lines.append(f"    {node_id}[{label}]")

            # For service view, also render interfaces
            if zoom == "service" and resource.interfaces:
                for interface in resource.interfaces:
                    iface_id = _sanitize_id(f"{resource.full_path}.{interface.id}")
                    iface_label = f"{interface.id}<br/>{interface.protocol}"
                    lines.append(f"    {iface_id}[{iface_label}]")
                    # Connect resource to its interfaces
                    lines.append(f"    {node_id} --> {iface_id}")

    # Render relationships
    if lines:
        lines.append("")  # Blank line before relationships

    for rel in relationships:
        from_id = _sanitize_id(rel.from_ref)
        to_id = _sanitize_id(rel.to_ref)

        if rel.description:
            arrow = f"|{rel.description}|"
        else:
            arrow = ""

        # Handle via (intermediary)
        if rel.via:
            via_id = _sanitize_id(rel.via)
            lines.append(f"    {from_id} -->{arrow} {via_id}")
            lines.append(f"    {via_id} --> {to_id}")
        else:
            lines.append(f"    {from_id} -->{arrow} {to_id}")

    return "\n".join(lines)


def _render_domain_view(
    lines: List[str],
    nodes: List[Resource],
    seen_ids: Set[str],
) -> None:
    """Render domain view with subgraphs for abstract resources.

    Args:
        lines: Output lines list (modified in place)
        nodes: Resources to render
        seen_ids: Set of IDs already rendered (modified in place)
    """
    # Group nodes by parent
    root_nodes = [n for n in nodes if not n.parent or n.parent not in nodes]

    for root in root_nodes:
        node_id = _sanitize_id(root.full_path)
        if node_id in seen_ids:
            continue

        # Find children of this node that are in the nodes list
        children = [n for n in nodes if n.parent == root and n != root]

        if root.abstract and children:
            # Render as subgraph
            seen_ids.add(node_id)
            subgraph_id = f"cluster_{node_id}"
            lines.append(f"    subgraph {subgraph_id}[\"{root.name}\"]")

            # Render children
            for child in children:
                child_id = _sanitize_id(child.full_path)
                if child_id not in seen_ids:
                    seen_ids.add(child_id)
                    label = _format_node_label(child, include_type=True)
                    lines.append(f"        {child_id}[{label}]")

            lines.append("    end")
        else:
            # Render as regular node
            seen_ids.add(node_id)
            label = _format_node_label(root, include_type=True)
            lines.append(f"    {node_id}[{label}]")


def _format_node_label(
    resource: Resource,
    include_type: bool = True,
    include_tech: bool = False,
) -> str:
    """Format resource display label for Mermaid node.

    Args:
        resource: Resource to format
        include_type: Whether to include resource type
        include_tech: Whether to include technology info

    Returns:
        Formatted label string with HTML line breaks
    """
    parts = [resource.name]

    if include_type:
        parts.append(resource.type)

    if include_tech and resource.technology:
        parts.append(resource.technology)

    # Join with <br/> for multiline labels
    return "<br/>".join(parts)


def _sanitize_id(path: str) -> str:
    """Convert dotted path to valid Mermaid node ID.

    Args:
        path: Dotted path like "system.service.interface"

    Returns:
        Sanitized ID like "system_service_interface"
    """
    # Replace dots and dashes with underscores
    # Mermaid IDs can't have dots or dashes
    return path.replace(".", "_").replace("-", "_")
