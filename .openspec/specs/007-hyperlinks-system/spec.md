# Hyperlinks System

**Status:** Active
**Created:** 2026-02-11
**Updated:** 2026-02-11
**Owner:** Ilja Heitlager
**Issue:** [#46](https://github.com/iheitlager/dotfiles/issues/46)
**PR:** [#47](https://github.com/iheitlager/dotfiles/pull/47)

---

## Overview

The Hyperlinks System implements clickable OSC 8 hyperlinks in tmux with Ghostty terminal, enabling users to click links directly in the terminal to open files, URLs, git commits, and GitHub issues.

## Motivation

Modern terminals support OSC 8 escape sequences for creating clickable hyperlinks where the display text can differ from the target URL (like HTML `<a>` tags). This enables:

- Clickable file paths that open in the default application
- Web links with custom display text
- Git commit links that open on GitHub
- GitHub issue references that link directly to the issue page
- Enhanced `ls` output with clickable file links

## Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│                   Ghostty Terminal                   │
│  - Renders OSC 8 hyperlinks                         │
│  - Detects Shift+Cmd+Click                          │
│  - Opens links in system default application        │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Terminal I/O
                 │
┌────────────────▼────────────────────────────────────┐
│                      tmux                            │
│  - Passes through OSC 8 sequences                   │
│  - terminal-features: xterm-ghostty:hyperlinks      │
│  - allow-passthrough: on                            │
│  - mouse: on (captures clicks in alt screen)        │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Shell commands
                 │
┌────────────────▼────────────────────────────────────┐
│              Bash Functions                          │
│  ghostty/bash_aliases                                │
│  - hyperlink(uri, text, id)                         │
│  - file_link(path, text)                            │
│  - web_link(url, text)                              │
│  - git_commit_link(hash, text)                      │
│  - github_issue(number, text)                       │
│  - lsl(path) - ls with links                        │
└──────────────────────────────────────────────────────┘
```

### Data Flow

1. **Bash function** generates OSC 8 escape sequence
2. **tmux** passes sequence through (native hyperlink support)
3. **Ghostty** renders the hyperlink with underline on hover
4. **User** clicks with Shift+Cmd+Click
5. **Ghostty** extracts URL and opens in system default application

## Implementation

### OSC 8 Sequence Format

```
ESC ] 8 ; params ; URI ESC \ text ESC ] 8 ; ; ESC \
```

**Example:**
```bash
printf '\e]8;;https://github.com\e\\GitHub\e]8;;\e\\'
```

**Rendered as:** [GitHub](https://github.com) (clickable)

### tmux Configuration

**File:** `tmux/config/tmux.conf`

```tmux
# Enable native OSC 8 hyperlink support (tmux 3.4+)
# Note: With mouse mode on, use Shift+Cmd+Click to open hyperlinks in Ghostty
set -sa terminal-features ",xterm-ghostty:hyperlinks"
set -sa terminal-features ",xterm-ghostty:RGB"
set -sa terminal-features ",xterm-ghostty:usstyle"
set -sa terminal-features ",xterm-ghostty:extkeys"

# Allow passthrough for OSC sequences
set -g allow-passthrough on

# Enable mouse mode (pane selection, resizing, scrolling)
set -g mouse on
```

**Key settings:**
- `terminal-features :hyperlinks` - Enables native OSC 8 support in tmux 3.4+
- `allow-passthrough on` - Allows OSC sequences to pass through tmux
- `mouse on` - Enables mouse support (requires Shift modifier for links)

### Bash Functions

**File:** `ghostty/bash_aliases`

#### Core Function

```bash
hyperlink() {
    local uri="$1"
    local text="${2:-$uri}"
    local id="${3:-}"

    if [[ -z "$uri" ]]; then
        echo "Usage: hyperlink <uri> [text] [id]" >&2
        return 1
    fi

    local params=""
    if [[ -n "$id" ]]; then
        params="id=${id}"
    fi

    # OSC 8 format with native tmux 3.4+ support
    printf '\e]8;%s;%s\e\\%s\e]8;;\e\\' "$params" "$uri" "$text"
}
```

#### Helper Functions

**file_link** - Create file:// hyperlinks
```bash
file_link() {
    local filepath="$1"
    local text="${2:-}"

    # Resolve to absolute path
    if [[ ! "$filepath" =~ ^/ ]]; then
        filepath="$(realpath "$filepath" 2>/dev/null || echo "$PWD/$filepath")"
    fi

    local hostname
    hostname="$(hostname 2>/dev/null || echo "localhost")"

    local uri="file://${hostname}${filepath}"

    if [[ -z "$text" ]]; then
        text="$(basename "$filepath")"
    fi

    hyperlink "$uri" "$text"
}
```

**web_link** - Create HTTP/HTTPS hyperlinks
```bash
web_link() {
    local url="$1"
    local text="${2:-$url}"

    # Add https:// if no scheme
    if [[ ! "$url" =~ ^https?:// ]]; then
        url="https://${url}"
    fi

    hyperlink "$url" "$text"
}
```

**git_commit_link** - Link to GitHub commits
```bash
git_commit_link() {
    local commit_hash="$1"
    local text="${2:-$commit_hash}"

    # Get remote URL and convert to GitHub HTTPS URL
    local remote_url
    remote_url="$(git config --get remote.origin.url 2>/dev/null)" || return 1

    # Convert SSH to HTTPS
    if [[ "$remote_url" =~ ^git@github\.com:(.+)\.git$ ]]; then
        remote_url="https://github.com/${BASH_REMATCH[1]}"
    fi

    local commit_url="${remote_url}/commit/${commit_hash}"
    hyperlink "$commit_url" "$text"
}
```

**github_issue** - Link to GitHub issues
```bash
github_issue() {
    local issue_number="$1"
    local text="${2:-#${issue_number}}"

    local remote_url
    remote_url="$(git config --get remote.origin.url 2>/dev/null)" || return 1

    # Convert SSH to HTTPS
    if [[ "$remote_url" =~ ^git@github\.com:(.+)\.git$ ]]; then
        remote_url="https://github.com/${BASH_REMATCH[1]}"
    fi

    local issue_url="${remote_url}/issues/${issue_number}"
    hyperlink "$issue_url" "$text"
}
```

**lsl** - Enhanced ls with clickable file links
```bash
lsl() {
    local target="${1:-.}"
    local hostname
    hostname="$(hostname 2>/dev/null || echo "localhost")"

    # Display with eza (or fall back to ls)
    if command -v eza >/dev/null 2>&1; then
        eza -la --color=always --group-directories-first --git --header "$target"
        echo
        echo "📎 Clickable file links:"

        local -a files
        mapfile -t files < <(eza -1a "$target" 2>/dev/null)

        for file in "${files[@]}"; do
            [[ "$file" == "." || "$file" == ".." ]] && continue

            local filepath
            filepath="$(cd "$target" && realpath "$file" 2>/dev/null)" || continue

            if [[ -e "$filepath" ]]; then
                local file_uri="file://${hostname}${filepath}"
                printf "  "
                hyperlink "$file_uri" "$file"
                echo
            fi
        done
    else
        ls -lah "$target"
    fi
}
```

### Ghostty Configuration

**File:** `ghostty/config/config`

```toml
# Shell integration
shell-integration = detect
shell-integration-features = cursor,sudo,title

# Clipboard support
clipboard-read = allow
clipboard-write = allow
```

**Note:** OSC 8 hyperlinks are supported by default in Ghostty. No additional configuration required.

## Usage

### Basic Examples

```bash
# Source the functions
source ~/.dotfiles/ghostty/bash_aliases

# Web link
echo "Visit $(web_link 'https://github.com' 'GitHub')"

# File link
echo "Config: $(file_link ~/.bashrc 'bashrc')"

# Git commit (in a git repo)
echo "See $(git_commit_link 'abc123' 'this commit')"

# GitHub issue (in a git repo)
echo "Fixes $(github_issue 42 'issue #42')"

# List files with clickable links
lsl ~/Documents
```

### Opening Links

**In Ghostty + tmux:**
- **Shift+Cmd+Click** - Opens the hyperlink

**In Ghostty (no tmux):**
- **Cmd+Click** - Opens the hyperlink

## Technical Considerations

### Why Shift+Cmd+Click in tmux?

Tmux operates in "alternate screen" mode, which allows it to capture mouse events for features like:
- Clicking to select panes
- Dragging to resize panes
- Scrolling with the mouse wheel

The **Shift modifier bypasses tmux's mouse capture**, allowing Ghostty to detect and process the hyperlink click.

### Alternative: Disable Mouse Mode

To use regular **Cmd+Click** without Shift:

```tmux
# In tmux.conf
set -g mouse off
```

**Trade-off:** Loses all tmux mouse features (pane selection, resizing, scrolling).

### tmux 3.4+ Native Support

Prior to tmux 3.4, OSC 8 sequences had to be wrapped in DCS passthrough format:

```bash
# OLD approach (before tmux 3.4)
printf '\ePtmux;\e\e]8;;%s\e\e\\\e\\%s\ePtmux;\e\e]8;;\e\e\\\e\\' "$uri" "$text"
```

With tmux 3.4+ and `terminal-features :hyperlinks`, use **direct OSC 8 sequences**:

```bash
# NEW approach (tmux 3.4+)
printf '\e]8;;%s\e\\%s\e]8;;\e\\' "$uri" "$text"
```

## Testing

### Verify Configuration

1. **Check tmux version:**
   ```bash
   tmux -V  # Should be 3.4 or higher
   ```

2. **Check tmux settings:**
   ```bash
   tmux show -gv terminal-features | grep hyperlinks
   tmux show -gv allow-passthrough
   tmux show -gv mouse
   ```

3. **Check terminal type:**
   ```bash
   tmux display -p '#{client_termname}'  # Should be xterm-ghostty
   ```

### Test Hyperlinks

```bash
source ~/.dotfiles/ghostty/bash_aliases

# Test web link
echo "Test: $(hyperlink 'https://github.com' 'GitHub')"

# Test file link
echo "Test: $(file_link ~/.bashrc 'bashrc')"

# Hover over the links - they should underline
# Shift+Cmd+Click to open
```

## Troubleshooting

### Links show as literal text

**Symptom:** Output shows `]8;;https://...` as literal characters

**Cause:** Escape sequences not being interpreted

**Solution:** Ensure bash functions use `printf` (not `echo`) and escape sequences are correct

### Links don't open on click

**Symptom:** Links appear correct but don't open when clicked

**Checklist:**
1. ✅ Using **Shift+Cmd+Click** (not just Cmd+Click)?
2. ✅ Inside Ghostty terminal?
3. ✅ tmux 3.4+ with `terminal-features :hyperlinks`?
4. ✅ Ghostty recognizes terminal type: `tmux display -p '#{client_termname}'`

### Links work outside tmux but not inside

**Symptom:** Cmd+Click works without tmux, requires Shift+Cmd+Click inside tmux

**This is expected behavior.** Tmux captures mouse events in alternate screen mode.

**Options:**
1. Use Shift+Cmd+Click (recommended - keeps mouse mode)
2. Disable mouse mode: `set -g mouse off` (lose tmux mouse features)

## References

### Specifications
- [OSC 8 Hyperlinks Specification](https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda) - Original spec by Egmont Koblinger
- [Ghostty VT External Docs](https://ghostty.org/docs/vt/external) - Ghostty OSC 8 documentation

### Ghostty Discussions
- [Click URL outside vs inside tmux #9735](https://github.com/ghostty-org/ghostty/discussions/9735) - Why URLs need Shift+Cmd+Click in tmux
- [Support for cmd+click without shift #8748](https://github.com/ghostty-org/ghostty/discussions/8748) - Feature request (no solution)

### Terminal Adoption
- [OSC 8 Adoption List](https://github.com/Alhadis/OSC8-Adoption) - Terminals supporting OSC 8

### tmux
- [tmux 3.4 CHANGES](https://raw.githubusercontent.com/tmux/tmux/3.4/CHANGES) - OSC 8 support announcement
- [tmux hyperlinks feature request #911](https://github.com/tmux/tmux/issues/911) - Original feature request

## Future Enhancements

- [ ] Auto-detect hyperlink support in `supports_hyperlinks()`
- [ ] Add hyperlinks to git status output
- [ ] Create hyperlinks in error messages with file:line references
- [ ] Integrate with `fzf` for clickable search results
- [ ] Add hyperlinks to `grep` output

## Version History

### 1.0.0 (2026-02-11)
- Initial implementation
- Core hyperlink functions
- tmux + Ghostty integration
- Documentation and testing
