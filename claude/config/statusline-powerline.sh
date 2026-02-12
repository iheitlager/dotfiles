#!/usr/bin/env bash
# Powerline-style statusline for Claude Code
# Shows: model | folder | branch | context | price

# Read JSON input
input=$(cat)

# Powerline separator (use these for powerline fonts)
SEP=""  #
SEP_THIN="" #

# Color codes (256 color palette for better powerline look)
# Background colors
BG_MODEL="\033[48;5;25m"      # Deep blue
BG_FOLDER="\033[48;5;240m"    # Dark gray
BG_BRANCH="\033[48;5;142m"    # Yellow-green
BG_CONTEXT="\033[48;5;61m"    # Purple
BG_PRICE="\033[48;5;166m"     # Orange

# Foreground colors (for text)
FG_WHITE="\033[38;5;15m"
FG_BLACK="\033[38;5;0m"

# Separator colors (foreground = previous bg)
FG_MODEL="\033[38;5;25m"
FG_FOLDER="\033[38;5;240m"
FG_BRANCH="\033[38;5;142m"
FG_CONTEXT="\033[38;5;61m"
FG_PRICE="\033[38;5;166m"

RESET="\033[0m"

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

# Build powerline segments
# Segment 1: Model
segment1="${BG_MODEL}${FG_WHITE} ⚡ ${model_short} ${RESET}"
sep1="${FG_MODEL}${BG_FOLDER}${SEP}${RESET}"

# Segment 2: Folder
segment2="${BG_FOLDER}${FG_WHITE} 📁 ${folder} ${RESET}"
sep2="${FG_FOLDER}${BG_BRANCH}${SEP}${RESET}"

# Segment 3: Branch
segment3="${BG_BRANCH}${FG_BLACK} ⎇ ${branch} ${RESET}"
sep3="${FG_BRANCH}${BG_CONTEXT}${SEP}${RESET}"

# Segment 4: Context
context_icon="🧠"
if [[ "$context_pct" -ge 90 ]]; then
    context_icon="⚠️"
elif [[ "$context_pct" -ge 75 ]]; then
    context_icon="⚡"
fi
segment4="${BG_CONTEXT}${FG_WHITE} ${context_icon} ${context_display}/${limit_display} ${context_pct}% ${RESET}"
sep4="${FG_CONTEXT}${BG_PRICE}${SEP}${RESET}"

# Segment 5: Price
segment5="${BG_PRICE}${FG_WHITE} 💰 \$${cost} ${RESET}"
sep5="${FG_PRICE}${SEP}${RESET}"

# Combine all segments and output directly using printf
printf "${segment1}${sep1}${segment2}${sep2}${segment3}${sep3}${segment4}${sep4}${segment5}${sep5} "
