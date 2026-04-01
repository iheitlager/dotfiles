"""
Bash script extractor for reverse engineering.

Extracts architectural resources from bash scripts by detecting:
- Script metadata (shebang, description)
- Function definitions
- Sourced files (dependencies)
- Interfaces (how functions are called)
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from ..model import Resource, Interface, CodeRef
from . import Extractor, ExtractionError


class BashExtractor(Extractor):
    """Extract architectural resources from bash scripts."""

    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a bash script.

        Args:
            file_path: Path to check

        Returns:
            True if file is a bash script (has .sh extension or bash shebang)
        """
        if not file_path.exists() or not file_path.is_file():
            return False

        # Check extension
        if file_path.suffix in ['.sh', '.bash']:
            return True

        # Check shebang for bash/sh
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline()
                return first_line.startswith('#!') and ('bash' in first_line or 'sh' in first_line)
        except (IOError, UnicodeDecodeError):
            return False

    def extract(self, file_path: Path) -> List[Resource]:
        """Extract resources from bash script.

        Args:
            file_path: Path to bash script

        Returns:
            List containing a single Resource representing the script

        Raises:
            ExtractionError: If extraction fails
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.splitlines()

            # Generate resource ID from filename
            resource_id = self._generate_id(file_path)

            # Detect metadata
            description = self._extract_description(lines)
            is_executable = file_path.stat().st_mode & 0o111 != 0

            # Extract functions
            functions = self._extract_functions(content, lines)

            # Build interfaces from functions
            interfaces = []
            for func_name, func_info in functions.items():
                interface = Interface(
                    id=func_name.replace('_', '-'),
                    protocol='bash-function',
                    direction='request-response',
                    description=func_info.get('description', f"Function: {func_name}")
                )
                interfaces.append(interface)

            # Build implementation references
            implementation = []
            for func_name, func_info in functions.items():
                impl = CodeRef(
                    path=str(file_path),
                    lines=f"{func_info['start_line']}-{func_info['end_line']}",
                    function=func_name,
                    description=func_info.get('description', '')
                )
                implementation.append(impl)

            # Determine script type
            script_type = 'bash-script' if is_executable else 'bash-library'

            # Create resource
            resource = Resource(
                id=resource_id,
                name=self._generate_name(file_path),
                type=script_type,
                technology='Bash',
                description=description or f"Bash script: {file_path.name}",
                repository=str(file_path),
                interfaces=interfaces,
                implementation=implementation
            )

            return [resource]

        except Exception as e:
            raise ExtractionError(
                f"Failed to extract from bash script: {e}",
                file_path=file_path
            )

    def _generate_id(self, file_path: Path) -> str:
        """Generate resource ID from filename.

        Args:
            file_path: Path to file

        Returns:
            Kebab-case ID
        """
        # Remove extension and convert to kebab-case
        name = file_path.stem
        # Replace underscores with hyphens
        name = name.replace('_', '-')
        # Handle camelCase -> kebab-case
        name = re.sub(r'([a-z])([A-Z])', r'\1-\2', name).lower()
        return name

    def _generate_name(self, file_path: Path) -> str:
        """Generate human-readable resource name.

        Args:
            file_path: Path to file

        Returns:
            Title-cased name
        """
        # Remove extension and convert to title case
        name = file_path.stem
        # Replace underscores/hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        return name.title()

    def _extract_description(self, lines: List[str]) -> Optional[str]:
        """Extract script description from header comments.

        Args:
            lines: Script content as lines

        Returns:
            Description if found, None otherwise
        """
        description_lines = []
        in_header = True

        for line in lines:
            line = line.strip()

            # Skip shebang
            if line.startswith('#!'):
                continue

            # Skip empty lines at start
            if not line and in_header:
                continue

            # Collect header comments
            if line.startswith('#'):
                # Remove comment marker and clean up
                comment = line.lstrip('#').strip()
                if comment:  # Ignore empty comment lines
                    description_lines.append(comment)
            elif line:  # Stop at first non-comment line
                break

        if description_lines:
            return ' '.join(description_lines)
        return None

    def _extract_functions(self, content: str, lines: List[str]) -> Dict[str, Dict]:
        """Extract function definitions from script.

        Args:
            content: Full script content
            lines: Script lines (for line number tracking)

        Returns:
            Dictionary mapping function name to metadata
        """
        functions = {}

        # Regex patterns for function definitions
        # Matches: function name() {  OR  name() {
        function_pattern = r'^(?:function\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)\s*\{'

        current_func = None
        func_start_line = None
        brace_count = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Start of function
            match = re.match(function_pattern, stripped)
            if match and current_func is None:
                func_name = match.group(1)
                current_func = func_name
                func_start_line = line_num
                brace_count = 1
                functions[func_name] = {
                    'start_line': line_num,
                    'end_line': None,
                    'description': None
                }
                continue

            # Track braces in function
            if current_func:
                brace_count += stripped.count('{')
                brace_count -= stripped.count('}')

                # End of function (all braces closed)
                if brace_count == 0:
                    functions[current_func]['end_line'] = line_num
                    current_func = None
                    func_start_line = None

        # Extract function descriptions from comments above function
        for func_name, func_info in functions.items():
            start = func_info['start_line']
            # Look for comments in the 5 lines before function
            desc_lines = []
            for i in range(max(0, start - 6), start - 1):
                if i < len(lines):
                    line = lines[i].strip()
                    if line.startswith('#'):
                        comment = line.lstrip('#').strip()
                        if comment:
                            desc_lines.append(comment)

            if desc_lines:
                func_info['description'] = ' '.join(desc_lines)

        return functions
