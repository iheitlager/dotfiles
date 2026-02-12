#!/usr/bin/env bash
# Catppuccin Mocha statusline for Claude Code
# Shows: model | folder | branch | context | price

# Read JSON input
input=$(cat)

# Separator (simple chevron like nvim)
SEP="›"  # Use › or > or │

# Catppuccin Mocha colors (matching Ghostty theme)
# Base colors
BG="\033[48;5;235m"           # #1e1e2e (background)
FG="\033[38;5;189m"           # #cdd6f4 (foreground)

# Accent colors (using Catppuccin palette)
BLUE="\033[38;5;117m"         # #89b4fa
GREEN="\033[38;5;151m"        # #a6e3a1
YELLOW="\033[38;5;223m"       # #f9e2af
PINK="\033[38;5;218m"         # #f5c2e7
PEACH="\033[38;5;216m"        # #fab387
MAUVE="\033[38;5;183m"        # #cba6f7
TEAL="\033[38;5;152m"         # #94e2d5
GRAY="\033[38;5;240m"         # #45475a

# Dim foreground for separators
DIM="\033[2m\033[38;5;240m"   # Dimmed gray

RESET="\033[0m"
BOLD="\033[1m"

# Extract data from JSON input
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')

# Handle model field - could be a string or an object with .id
model_raw=$(echo "$input" | jq -r 'if (.model | type) == "object" then .model.id else .model end // "claude"')
model="$model_raw"

# Extract context window information
context_used=$(echo "$input" | jq -r '(.context_window.total_input_tokens // 0) + (.context_window.total_output_tokens // 0)')
context_limit=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

# Use total cost if available, otherwise calculate from current usage
total_cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
if [[ -n "$total_cost" ]]; then
    cost=$(printf "%.4f" "$total_cost")
else
    input_tokens=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
    output_tokens=$(echo "$input" | jq -r '.context_window.current_usage.output_tokens // 0')
    cost=$(awk -v input="${input_tokens:-0}" -v output="${output_tokens:-0}" 'BEGIN {printf "%.4f", (input * 3 + output * 15) / 1000000}')
fi

# Calculate context percentage
if [[ "${context_limit:-0}" -gt 0 ]]; then
    context_pct=$(awk -v used="${context_used:-0}" -v limit="${context_limit:-1}" 'BEGIN {printf "%.0f", (used / limit) * 100}')
else
    context_pct=0
fi

# Format context display
if [[ "${context_used:-0}" -gt 1000 ]]; then
    context_display=$(awk -v used="${context_used:-0}" 'BEGIN {printf "%.1fk", used / 1000}')
else
    context_display="${context_used:-0}"
fi

if [[ "${context_limit:-0}" -gt 1000 ]]; then
    limit_display=$(awk -v limit="${context_limit:-0}" 'BEGIN {printf "%.0fk", limit / 1000}')
else
    limit_display="${context_limit:-0}"
fi

# Get folder name
folder=$(basename "$cwd")

# Get git branch
branch=""
if git -C "$cwd" rev-parse --git-dir &>/dev/null 2>&1; then
    branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)

    # Get ahead/behind counts
    if counts=$(git -C "$cwd" rev-list --left-right --count @{upstream}...HEAD 2>/dev/null); then
        behind=${counts%%	*}
        ahead=${counts##*	}

        if [[ "$ahead" -gt 0 ]]; then
            branch="$branch ↑$ahead"
        fi
        if [[ "$behind" -gt 0 ]]; then
            branch="$branch ↓$behind"
        fi
    fi
else
    branch="no git"
fi

# Map model names to short versions
case "$model" in
    *"opus"*) model_short="opus" ;;
    *"sonnet"*) model_short="sonnet" ;;
    *"haiku"*) model_short="haiku" ;;
    *) model_short="claude" ;;
esac

# Build statusline segments (nvim-style with icons and separators)
# Format: color + icon + text + dim separator

# Segment 1: Model (with lightning icon)
segment1="${BLUE}${BOLD} ${model_short}${RESET}"

# Segment 2: Folder (with folder icon)
segment2="${TEAL} ${folder}${RESET}"

# Segment 3: Branch (with git branch icon)
segment3="${GREEN} ${branch}${RESET}"

# Segment 4: Context (with dynamic icon based on usage)
context_color="$MAUVE"
context_icon=""
if [[ "$context_pct" -ge 90 ]]; then
    context_color="$PEACH"
    context_icon=" "  # Warning
elif [[ "$context_pct" -ge 75 ]]; then
    context_color="$YELLOW"
    context_icon=" "  # Alert
else
    context_icon=" "  # Database/memory
fi
segment4="${context_color}${context_icon} ${context_display}/${limit_display} ${context_pct}%${RESET}"

# Segment 5: Price (with dollar icon)
segment5="${PEACH} \$${cost}${RESET}"

# Combine all segments with dim separators
printf '%b' "${segment1} ${DIM}${SEP}${RESET} ${segment2} ${DIM}${SEP}${RESET} ${segment3} ${DIM}${SEP}${RESET} ${segment4} ${DIM}${SEP}${RESET} ${segment5} "
