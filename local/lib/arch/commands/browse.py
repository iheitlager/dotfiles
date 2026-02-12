"""Interactive fzf browser for architecture resources.

Provides an interactive browser similar to the spec command,
allowing navigation of the architecture model with fzf.
"""

import os
import subprocess
import sys
import tempfile
from typing import List, Tuple, Optional

from ..model import Resource, Interface, ArchitectureModel
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


def _build_resource_entry(
    resource: Resource,
    full_path: str,
    index: int,
    indent_level: int = 0,
) -> List[Tuple[str, str, int, str, str, str]]:
    """Build fzf entries for a resource and its children.

    Returns list of tuples: (type, full_path, line, display_name, metadata, indent_level)
    """
    entries = []

    # Resource entry
    icon = _get_resource_icon(resource)
    display_name = f"{icon} {resource.name}"
    metadata = f"[{resource.type}]"
    if resource.technology:
        metadata += f" • {resource.technology}"

    entries.append((
        "RESOURCE",
        full_path,
        index,
        display_name,
        metadata,
        str(indent_level)
    ))

    # Interface entries (indented under resource)
    for iface in resource.interfaces:
        iface_path = f"{full_path}.{iface.id}"
        iface_display = f"→ {iface.id}"
        iface_meta = f"({iface.protocol}, {iface.direction})"

        entries.append((
            "INTERFACE",
            iface_path,
            index,
            iface_display,
            iface_meta,
            str(indent_level + 1)
        ))

    # Recursively add children
    for child in resource.children:
        child_path = f"{full_path}.{child.id}"
        child_entries = _build_resource_entry(
            child,
            child_path,
            index,
            indent_level + 1
        )
        entries.extend(child_entries)

    return entries


def _build_fzf_list(model: ArchitectureModel) -> List[Tuple[str, str, int, str, str, str]]:
    """Build the list of entries for fzf.

    Returns list of tuples: (type, full_path, line, display_name, metadata, indent_level)
    """
    all_entries = []
    line_index = 0

    for resource in model.resources:
        entries = _build_resource_entry(
            resource,
            resource.id,
            line_index,
            indent_level=0
        )
        all_entries.extend(entries)
        line_index += len(entries)

    return all_entries


def _format_fzf_entry(
    entry_type: str,
    display_name: str,
    metadata: str,
    indent_level: int,
    line: int,
) -> str:
    """Format an entry for fzf display with indentation.

    Returns: "line|formatted_display"
    """
    indent = "  " * indent_level

    if entry_type == "RESOURCE":
        # Resource entries: no prefix
        formatted = f"{line}|{indent}{display_name:<50}  {metadata}"
    else:
        # Interface entries: with arrow prefix
        formatted = f"{line}|{indent}   {display_name:<47}  {metadata}"

    return formatted


def _build_preview_content(
    entry_type: str,
    full_path: str,
    model: ArchitectureModel,
    resolver: PathResolver,
) -> str:
    """Build preview content for a selected entry."""
    lines = []

    if entry_type == "RESOURCE":
        # Look up resource by path
        resource = resolver.resolve_resource(full_path)
        if not resource:
            return f"Resource not found: {full_path}"

        # Build preview
        icon = _get_resource_icon(resource)
        lines.append(f"{icon} {resource.name}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"ID:          {resource.id}")
        lines.append(f"Type:        {resource.type}")
        lines.append(f"Path:        {full_path}")

        if resource.technology:
            lines.append(f"Technology:  {resource.technology}")

        if resource.abstract:
            lines.append(f"Abstract:    Yes")

        if resource.repository:
            lines.append(f"Repository:  {resource.repository}")

        if resource.instance:
            lines.append(f"Instance:    {resource.instance}")

        if resource.description:
            lines.append("")
            lines.append("Description:")
            lines.append(resource.description)

        if resource.tags:
            lines.append("")
            lines.append(f"Tags:        {', '.join(resource.tags)}")

        # Show interfaces
        if resource.interfaces:
            lines.append("")
            lines.append(f"Interfaces ({len(resource.interfaces)}):")
            for iface in resource.interfaces:
                lines.append(f"  → {iface.id}")
                lines.append(f"    Protocol:    {iface.protocol}")
                lines.append(f"    Direction:   {iface.direction}")
                if iface.description:
                    lines.append(f"    Description: {iface.description}")
                if iface.topic:
                    lines.append(f"    Topic:       {iface.topic}")

        # Show children count
        if resource.children:
            lines.append("")
            lines.append(f"Children ({len(resource.children)}):")
            for child in resource.children:
                child_icon = _get_resource_icon(child)
                lines.append(f"  {child_icon} {child.name} ({child.id})")

        # Show implementation references
        if resource.implementation:
            lines.append("")
            lines.append("Implementation:")
            for impl in resource.implementation:
                lines.append(f"  {impl.path}")
                if impl.line_start:
                    lines.append(f"    Lines: {impl.line_start}-{impl.line_end or impl.line_start}")

    elif entry_type == "INTERFACE":
        # Look up interface by path
        interface = resolver.resolve_interface(full_path)
        if not interface:
            return f"Interface not found: {full_path}"

        # Build preview
        lines.append(f"→ {interface.id}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Protocol:    {interface.protocol}")
        lines.append(f"Direction:   {interface.direction}")
        lines.append(f"Path:        {full_path}")

        if interface.description:
            lines.append("")
            lines.append("Description:")
            lines.append(interface.description)

        if interface.topic:
            lines.append("")
            lines.append(f"Topic:       {interface.topic}")

    return "\n".join(lines)


def _check_fzf_installed() -> bool:
    """Check if fzf is installed."""
    try:
        subprocess.run(
            ["which", "fzf"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def render_browser(model: ArchitectureModel, resolver: PathResolver) -> int:
    """Render interactive fzf browser for architecture.

    Args:
        model: The architecture model to browse
        resolver: PathResolver for lookups

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check if fzf is installed
    if not _check_fzf_installed():
        print("❌ Error: fzf is not installed", file=sys.stderr)
        print("   Install it with: brew install fzf", file=sys.stderr)
        return 1

    # Build fzf list
    entries = _build_fzf_list(model)

    if not entries:
        print("❌ Error: No resources found in architecture", file=sys.stderr)
        return 1

    # Create temp files for data and preview
    temp_data = tempfile.NamedTemporaryFile(mode='w', delete=False, prefix='arch-fzf-data-')
    temp_preview_script = tempfile.NamedTemporaryFile(mode='w', delete=False, prefix='arch-fzf-preview-', suffix='.sh')

    try:
        # Format entries for fzf display and write metadata
        fzf_input_lines = []
        for entry_type, full_path, line, display_name, metadata, indent_level in entries:
            # Format for display
            formatted = _format_fzf_entry(
                entry_type,
                display_name,
                metadata,
                int(indent_level),
                line
            )
            fzf_input_lines.append(formatted)

            # Write metadata to temp file
            temp_data.write(f"{entry_type}|{full_path}|{line}\n")

        temp_data.close()

        # Create preview script that calls back to arch
        preview_script = f"""#!/bin/bash
# Preview script for arch browser
LINE_NUM=$(($1 + 1))
DATA=$(sed -n "${{LINE_NUM}}p" {temp_data.name})
TYPE=$(echo "$DATA" | cut -d'|' -f1)
PATH=$(echo "$DATA" | cut -d'|' -f2)

# Call arch to render preview
{sys.executable} {os.path.abspath(sys.argv[0])} __preview__ "$TYPE" "$PATH"
"""
        temp_preview_script.write(preview_script)
        temp_preview_script.close()
        os.chmod(temp_preview_script.name, 0o755)

        # Run fzf
        fzf_input = "\n".join(fzf_input_lines)

        fzf_cmd = [
            "fzf",
            "--ansi",
            "--height=100%",
            "--layout=reverse",
            "--border",
            "--delimiter=|",
            "--with-nth=2..",
            "--prompt=Architecture > ",
            "--header=Enter: view | Ctrl-/: zoom | Ctrl-D: scroll down | Ctrl-U: scroll up",
            f"--preview={temp_preview_script.name} {{n}}",
            "--preview-window=right:60%:wrap",
            "--bind=ctrl-/:change-preview-window(80%|60%:wrap)",
            "--bind=ctrl-d:preview-half-page-down",
            "--bind=ctrl-u:preview-half-page-up",
        ]

        result = subprocess.run(
            fzf_cmd,
            input=fzf_input,
            text=True,
            capture_output=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            # User selected an entry
            selected = result.stdout.strip()
            # Extract line number from the selected entry
            if '|' in selected:
                line_num = int(selected.split('|')[0])
                # Get the entry data
                with open(temp_data.name, 'r') as f:
                    lines = f.readlines()
                    if 0 <= line_num < len(lines):
                        entry_data = lines[line_num].strip()
                        entry_type, full_path, _ = entry_data.split('|', 2)

                        # Show full preview
                        preview = _build_preview_content(entry_type, full_path, model, resolver)
                        print("\n" + preview)

        return 0

    finally:
        # Clean up temp files
        try:
            os.unlink(temp_data.name)
            os.unlink(temp_preview_script.name)
        except:
            pass


def render_preview(entry_type: str, full_path: str, model: ArchitectureModel, resolver: PathResolver) -> None:
    """Render preview content for fzf (called by preview script).

    Args:
        entry_type: Type of entry (RESOURCE or INTERFACE)
        full_path: Full dotted path to the entry
        model: The architecture model
        resolver: PathResolver for lookups
    """
    preview = _build_preview_content(entry_type, full_path, model, resolver)
    print(preview)
