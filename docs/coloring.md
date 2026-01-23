# Terminal Coloring & Modern CLI Tools

This dotfiles setup uses modern Rust-based CLI tools that provide rich color output and better defaults than traditional Unix utilities.

## Tool Stack

| Tool | Replaces | Purpose |
|------|----------|---------|
| `eza` | `ls` | Modern file listing with git integration |
| `bat` | `cat` | Syntax-highlighted file viewing |
| `rg` (ripgrep) | `grep` | Fast recursive search |
| `fd` | `find` | Fast file finder |
| `delta` | `diff` | Git diff with syntax highlighting |
| `fzf` | — | Fuzzy finder for interactive selection |
| `jq` | — | JSON processor with colored output |
| `yq` | — | YAML processor |

Install all via Homebrew:
```bash
brew install fd jq yq delta fzf bat eza rg
```

---

## eza (Modern ls)

### Aliases Defined

```bash
alias ls='eza --color=always --group-directories-first'
alias ll='eza -la --color=always --group-directories-first --git --header'
alias la='eza -a --color=always --group-directories-first'
alias lt='eza --tree --color=always --git-ignore --level=3'
alias l='eza -F --color=always'
alias lr="ls -lAt | head"  # most recent files
```

### Features
- **Git integration**: Shows file status (modified, staged, ignored) in `ll` output
- **Icons**: Enable with `--icons` (requires Nerd Font)
- **Tree view**: `lt` shows directory structure respecting `.gitignore`
- **Headers**: Column headers in long listing

### Color Configuration

eza uses `EZA_COLORS` environment variable (extended LS_COLORS format):

```bash
# Example: customize directory and git colors
export EZA_COLORS="di=1;34:ln=36:*.md=33:ga=32:gm=33:gd=31"
```

| Code | Meaning |
|------|---------|
| `di` | Directories |
| `ln` | Symlinks |
| `ga` | Git added |
| `gm` | Git modified |
| `gd` | Git deleted |

---

## bat (Modern cat)

### Usage Patterns

```bash
# View file with syntax highlighting
bat file.py

# Plain output (no line numbers, decorations)
bat --plain file.txt
bat -p file.txt

# Specific language highlighting
bat --language=json data.txt
bat --language=help <(command --help)

# Show non-printable characters
bat -A file.txt
```

### Integrated Aliases

```bash
# Format help output
help() {
    "$@" --help 2>&1 | bat --plain --language=help
}

# View environment and aliases with highlighting
alias a='alias | sort | bat --plain --language=bash'
alias e='env | sort | bat --plain --language=bash'

# Cheat sheets with highlighting
cheat() {
    curl -s "cheat.sh/$1" | bat --plain --language=help
}

# Port listing
alias ports='lsof -iTCP -sTCP:LISTEN -n -P | bat -p --language=perl'
```

### Configuration

bat reads `~/.config/bat/config`:

```bash
# Set default theme
--theme="Dracula"

# Always show line numbers
--style="numbers,changes,header"

# Use italics
--italic-text=always
```

List themes: `bat --list-themes`

---

## ripgrep (rg) - Fast Search

### Aliases

```bash
# Quick grep wrapper that uses rg when available
gg() {
    if command -v rg &> /dev/null; then
        rg --color=always "$@"
    else
        grep -r "$@" .
    fi
}
```

### Common Patterns

```bash
rg "pattern"                    # Search current dir recursively
rg -i "pattern"                 # Case insensitive
rg -w "word"                    # Whole word match
rg -t py "def "                 # Search only Python files
rg -g "*.md" "TODO"             # Glob pattern filter
rg -l "pattern"                 # List matching files only
rg -C 3 "pattern"               # 3 lines of context
rg --json "pattern" | jq        # JSON output for processing
```

### Color Configuration

```bash
export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"
```

In `~/.ripgreprc`:
```
--colors=match:fg:yellow
--colors=match:style:bold
--colors=path:fg:magenta
--colors=line:fg:green
--smart-case
```

---

## fd (Fast find)

### Aliases

```bash
# Quick file finder
ff() {
    if command -v fd &> /dev/null; then
        fd "$@"
    else
        find . -iname "*$1*"
    fi
}
```

### Common Patterns

```bash
fd "pattern"                    # Find files matching pattern
fd -e py                        # Find by extension
fd -t d "src"                   # Find directories only
fd -t f -x wc -l                # Execute command on results
fd -H "pattern"                 # Include hidden files
fd --changed-within 1d          # Recently modified
```

---

## delta (Git Diff)

Configured in `~/.gitconfig`:

```ini
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true
    side-by-side = true
    line-numbers = true
    syntax-theme = Dracula
    plus-style = "syntax #012800"
    minus-style = "syntax #340001"
    line-numbers-minus-style = "#444444"
    line-numbers-plus-style = "#444444"
    line-numbers-zero-style = "#444444"
    file-style = "bold yellow ul"
    file-decoration-style = "none"
    hunk-header-decoration-style = "cyan box"
    hunk-header-file-style = "red"
    hunk-header-line-number-style = "#067a00"
    hunk-header-style = "file line-number syntax"

[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
```

### Features
- **Side-by-side**: Split view for easier comparison
- **Line numbers**: Both sides numbered
- **Syntax highlighting**: Code-aware coloring
- **Navigate**: Use `n`/`N` to jump between files

---

## fzf (Fuzzy Finder)

### Shell Integration

```bash
# History search with fzf (Ctrl+R replacement)
_bash_history -s              # Interactive history selection
_bash_history -s -g "git"     # Filter then select

# File selection
vim $(fzf)                    # Open file in vim
cd $(fd -t d | fzf)           # cd to directory
```

### fzf Options Used

```bash
fzf \
    --height=50% \
    --layout=reverse \
    --border \
    --preview 'echo {}' \
    --preview-window=up:3:wrap \
    --header='Select command' \
    --prompt='> ' \
    --color='header:italic:underline'
```

### Environment Configuration

```bash
# Default fzf options
export FZF_DEFAULT_OPTS='
    --height=40%
    --layout=reverse
    --border
    --color=fg:#f8f8f2,bg:#282a36,hl:#bd93f9
    --color=fg+:#f8f8f2,bg+:#44475a,hl+:#bd93f9
    --color=info:#ffb86c,prompt:#50fa7b,pointer:#ff79c6
    --color=marker:#ff79c6,spinner:#ffb86c,header:#6272a4
'

# Use fd for fzf file finding
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
```

---

## jq & yq (Data Processing)

### jq (JSON)

```bash
# Pretty print JSON with colors
cat data.json | jq .

# Extract field
curl -s api.example.com | jq '.items[].name'

# Colorized output is default when stdout is terminal
```

### yq (YAML)

```bash
# Pretty print YAML
yq . file.yaml

# Convert YAML to JSON
yq -o=json . file.yaml

# Extract value
yq '.spec.containers[0].image' deployment.yaml
```

---

## Traditional GREP Colors

For tools that still use GREP_COLORS:

```bash
export GREP_COLORS='ms=01;32:mc=01;31:sl=:cx=:fn=35:ln=32:bn=32:se=36'

# Color codes:
# ms=01;32    # Matching text (bold green - customized from default red)
# mc=01;31    # Matching text in context (bold red)
# fn=35       # Filename (magenta)
# ln=32       # Line number (green)
# se=36       # Separator (cyan)
```

---

## ANSI Color Code Reference

### Text Attributes

| Code | Effect |
|------|--------|
| `00` | Reset/Normal |
| `01` | Bold/Bright |
| `02` | Dim |
| `04` | Underline |
| `05` | Blink |
| `07` | Reverse |
| `08` | Hidden |

### Foreground Colors

| Code | Color |
|------|-------|
| `30` | Black |
| `31` | Red |
| `32` | Green |
| `33` | Yellow |
| `34` | Blue |
| `35` | Magenta |
| `36` | Cyan |
| `37` | White |

### Background Colors

| Code | Color |
|------|-------|
| `40` | Black |
| `41` | Red |
| `42` | Green |
| `43` | Yellow |
| `44` | Blue |
| `45` | Magenta |
| `46` | Cyan |
| `47` | White |

### 256 Colors

```bash
# Foreground: 38;5;N where N is 0-255
# Background: 48;5;N
echo -e "\033[38;5;208mOrange text\033[0m"
```

### True Color (24-bit)

```bash
# Foreground: 38;2;R;G;B
# Background: 48;2;R;G;B
echo -e "\033[38;2;255;100;0mTrue orange\033[0m"
```

---

## macOS LSCOLORS (BSD ls)

For fallback to system `ls`:

```bash
export LSCOLORS="GxFxCxDxBxegedabagaced"
```

LSCOLORS uses pairs of letters (foreground/background) for:
1. Directory
2. Symlink
3. Socket
4. Pipe
5. Executable
6. Block special
7. Character special
8. Setuid executable
9. Setgid executable
10. Sticky directory (other-writable)
11. Directory (other-writable)

Color codes: `a`=black, `b`=red, `c`=green, `d`=brown, `e`=blue, `f`=magenta, `g`=cyan, `h`=light grey, `x`=default. Capitals = bold.
