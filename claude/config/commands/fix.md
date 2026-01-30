Help fix an error or problem.

## Usage

```
/fix <error>           Analyze and suggest fix
ai --fix "error msg"   Same, one-shot
```

## Examples

```
ai --fix "ModuleNotFoundError: No module named 'foo'"
ai --fix "permission denied"
some_cmd 2>&1 | ai --fix
```

## Prompt

Analyze this error and provide a fix. Be concise and actionable.

Structure:
- **Problem**: What went wrong (one line)
- **Fix**: The command or code to fix it
- **Why**: Brief explanation (optional)
