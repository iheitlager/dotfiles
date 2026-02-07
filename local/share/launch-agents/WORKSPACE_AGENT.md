# Workspace Agent Instructions

You are running in a **workspace** tmux session with a shell pane on the right.

## Layout

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   Claude (you)      │   Shell (pane 2)    │
│   pane 1            │                     │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

## Right Pane Commands

You can run commands in the right pane using tmux send-keys:

```bash
# Run a command in the right pane
tmux send-keys -t "$WORKSPACE_SESSION:workspace.2" 'command here' Enter

# Examples:
tmux send-keys -t "$WORKSPACE_SESSION:workspace.2" 'make test' Enter
tmux send-keys -t "$WORKSPACE_SESSION:workspace.2" 'git status' Enter
tmux send-keys -t "$WORKSPACE_SESSION:workspace.2" 'nvim file.py' Enter
```

## Capture Right Pane Output

To see what's displayed in the right pane:

```bash
tmux capture-pane -t "$WORKSPACE_SESSION:workspace.2" -p
```

## Interactive Programs

For interactive programs (nvim, htop, ctop):

```bash
# Start program
tmux send-keys -t "$WORKSPACE_SESSION:workspace.2" 'nvim file.py' Enter

# Send keystrokes (after delay)
sleep 1
tmux send-keys -t "$WORKSPACE_SESSION:workspace.2" ':q!' Enter

# Capture output to see state
tmux capture-pane -t "$WORKSPACE_SESSION:workspace.2" -p
```

## When to Use Right Pane

Use the right pane for:
- Running tests (`make test`, `pytest`)
- Watching logs (`tail -f`)
- Interactive tools (`nvim`, `ctop`, `htop`)
- Long-running processes
- Anything the user wants to see running

Keep your conversation in the left pane for thinking and responses.

## Environment

- Session: `$WORKSPACE_SESSION`
- Your pane: 1 (left)
- Shell pane: 2 (right)
- Working directory: Same as where workspace was started

---

## Architecture References

For understanding the dotfiles system architecture:
- **Core system spec**: `~/.dotfiles/.openspec/specs/dotfiles-core/spec.md` - Complete specification of the dotfiles architecture
- **Shortcuts system**: `~/.dotfiles/.openspec/specs/shortcuts-system/spec.md` - Keyboard shortcuts documentation system
- **XDG integration**: `~/.dotfiles/docs/xdg_setup.md` - XDG Base Directory implementation details
- **Modern CLI tools**: `~/.dotfiles/docs/coloring.md` - Terminal colors and modern command-line tools
