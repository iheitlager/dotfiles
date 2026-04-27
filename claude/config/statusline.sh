#!/usr/bin/env bash
# Catppuccin Mocha statusline for Claude Code
# Shows: model | folder | branch | context | price

input=$(cat)

SEP="›"

# Catppuccin Mocha colors
BLUE="\033[38;5;117m"
GREEN="\033[38;5;151m"
YELLOW="\033[38;5;223m"
PEACH="\033[38;5;216m"
MAUVE="\033[38;5;183m"
TEAL="\033[38;5;152m"
DIM="\033[2m\033[38;5;240m"
RESET="\033[0m"
BOLD="\033[1m"

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
model=$(echo "$input" | jq -r 'if (.model | type) == "object" then .model.id else .model end // "claude"')
context_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0' | xargs printf "%.4f")

folder=$(basename "$cwd")

branch=""
if git -C "$cwd" rev-parse --git-dir &>/dev/null; then
    branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
    if counts=$(git -C "$cwd" rev-list --left-right --count @{upstream}...HEAD 2>/dev/null); then
        behind=${counts%%	*}
        ahead=${counts##*	}
        [[ "$ahead" -gt 0 ]] && branch="$branch ↑$ahead"
        [[ "$behind" -gt 0 ]] && branch="$branch ↓$behind"
    fi
else
    branch="no git"
fi

case "$model" in
    *"opus"*)   model_short="opus" ;;
    *"sonnet"*) model_short="sonnet" ;;
    *"haiku"*)  model_short="haiku" ;;
    *)          model_short="claude" ;;
esac

context_color="$MAUVE"
context_icon=" "
if [[ "$context_pct" -ge 90 ]]; then
    context_color="$PEACH"
    context_icon=" "
elif [[ "$context_pct" -ge 75 ]]; then
    context_color="$YELLOW"
    context_icon=" "
fi

segment1="${BLUE}${BOLD}${model_short}${RESET}"
segment2="${TEAL} ${folder}${RESET}"
segment3="${GREEN} ${branch}${RESET}"
segment4="${context_color}${context_icon} ${context_pct}%${RESET}"
segment5="${PEACH} \$${cost}${RESET}"

printf '%b' "${segment1} ${DIM}${SEP}${RESET}${segment2}${DIM} ${SEP}${RESET}${segment3}${DIM} ${SEP}${RESET}${segment4}${DIM} ${SEP}${RESET}${segment5}"
