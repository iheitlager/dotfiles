Explain the current git diff in plain language.

## Usage

```
/diff           Explain unstaged changes
ai --diff       Same, one-shot
```

## Process

1. Get the current diff (unstaged first, then staged)
2. Summarize what changed and why it matters
3. Note any potential issues

## Prompt

Explain this git diff in plain language. Be concise.

Structure your response as:
- **Summary**: One sentence overview
- **Changes**: Bullet points of what changed
- **Notes**: Any concerns or suggestions (optional)
