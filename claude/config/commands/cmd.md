Generate shell commands from natural language descriptions.

## Usage

```
/cmd <description>      Generate a shell command
```

## Examples

```
/cmd find all python files over 1mb
/cmd list docker containers using most memory
/cmd compress all jpg files in current directory
/cmd find and kill process on port 3000
```

## Guidelines

- Prefer common POSIX tools when possible
- Use safe defaults (interactive prompts for destructive operations)
- Chain commands with && for dependent operations
- Quote variables and paths with spaces
- Add comments for complex pipelines

## Output

1. Show the generated command with explanation
2. Ask for confirmation before running
3. Execute if approved

## Prompt

Generate a shell command for the given task.

Rules:
- Return ONLY the command, no explanation
- Use bash syntax
- Prefer common POSIX tools when possible
- If multiple commands needed, chain with && or use subshells
- For destructive operations, include safety checks
- Use quotes around variables and paths with spaces
