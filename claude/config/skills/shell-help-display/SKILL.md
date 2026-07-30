# Shell Help Display Pattern

Display help text with syntax highlighting when `bat` is available, falling back to `cat`.

## Usage Pattern

```bash
show_help() {
    local help_cmd="cat"
    command -v bat &>/dev/null && help_cmd="bat --plain --language=help"
    
    $help_cmd << 'EOF'
Usage: command [OPTIONS]

Description of the command.

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Verbose output

EXAMPLES:
    command -v      Run with verbose output

EOF
}
```

## Key Points

1. **Use `'EOF'` (quoted)** - Prevents variable expansion in heredoc, keeps `$VAR` literal
2. **Use `bat --plain`** - No line numbers, no decorations
3. **Use `--language=help`** - Proper syntax highlighting for help text
4. **Local variable** - Don't pollute global namespace
5. **Single check** - `command -v bat &>/dev/null &&` is concise

## Alternative: Inline One-liner

For simple cases where you don't need a function:

```bash
{ command -v bat &>/dev/null && bat --plain --language=help || cat; } << 'EOF'
Usage: simple-command [args]
EOF
```

## Help Text Conventions

Structure help text consistently:

```
Usage: command [OPTIONS] [ARGUMENTS]

Brief description of what the command does.

OPTIONS:
    -s, --short     Short option description
    -l, --long ARG  Option with argument

ARGUMENTS:
    ARG             Required argument description

EXAMPLES:
    command -s          Example with short flag
    command --long foo  Example with argument

ENVIRONMENT:
    VAR_NAME        Environment variable description

SEE ALSO:
    related-command, other-command
```
