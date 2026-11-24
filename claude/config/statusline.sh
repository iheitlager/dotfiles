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
ORANGE="\033[38;5;208m"
RED="\033[38;5;203m"
MAUVE="\033[38;5;183m"
TEAL="\033[38;5;152m"
DIM="\033[2m\033[38;5;240m"
RESET="\033[0m"
BOLD="\033[1m"

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
model=$(echo "$input" | jq -r 'if (.model | type) == "object" then .model.id else .model end // "claude"')
# tokens in context: current usage if present, else derived from the percentage and the window size
context_tokens=$(echo "$input" | jq -r '(.context_window.current_usage // {}) as $u
    | if ($u | length) > 0 then (($u.input_tokens // 0) + ($u.cache_creation_input_tokens // 0) + ($u.cache_read_input_tokens // 0))
      else ((.context_window.used_percentage // 0) * (.context_window.context_window_size // 200000) / 100) end | floor')
# percentage of the 200k price threshold; above 200k it overshoots (400k = 200%)
context_pct=$(( context_tokens * 100 / 200000 ))
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
    *"fable"*)  model_short="fable" ;;
    *"mythos"*) model_short="mythos" ;;
    *)          model_short="claude" ;;
esac

# purple below 180k tokens, orange from 180k, red from 200k
context_color="$MAUVE"
context_icon=" "
if [[ "$context_tokens" -ge 200000 ]]; then
    context_color="$RED"
    context_icon=" "
elif [[ "$context_tokens" -ge 180000 ]]; then
    context_color="$ORANGE"
    context_icon=" "
fi
context_k=$(( (context_tokens + 500) / 1000 ))k

# cold cache: the last request wrote most of its context to the cache instead of reading it
# (the cache expired after a pause, the context was replaced, or a new session started)
cache_written=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
cold=""
if [[ "$context_tokens" -ge 20000 && $(( cache_written * 2 )) -gt "$context_tokens" ]]; then
    cold=" ${YELLOW}↻ cold${RESET}"
fi

segment1="${BLUE}${BOLD}${model_short}${RESET}"
segment2="${TEAL} ${folder}${RESET}"
segment3="${GREEN} ${branch}${RESET}"
segment4="${context_color}${context_icon} ${context_pct}% · ${context_k}${RESET}${cold}"
segment5="${PEACH} \$${cost}${RESET}"

printf '%b' "${segment1} ${DIM}${SEP}${RESET}${segment2}${DIM} ${SEP}${RESET}${segment3}${DIM} ${SEP}${RESET}${segment4}${DIM} ${SEP}${RESET}${segment5}"
