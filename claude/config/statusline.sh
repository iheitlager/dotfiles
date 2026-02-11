#!/usr/bin/env bash
# Claude Code statusline
# Shows: [agent-id ·] model · context-bar XX% · $cost [· +add/-del]
#
# Data is piped in as JSON from Claude Code on each update.
# AGENT_ID env var is set by launch-agents for swarm/workspace sessions.

input=$(cat)

# Model: shorten "Claude Sonnet 4.5" → "sonnet-4.5"
MODEL=$(echo "$input" | jq -r '.model.display_name // .model.id // "?"')
MODEL_SHORT=$(echo "$MODEL" \
    | sed 's/^Claude //i' \
    | sed 's/ 20[0-9][0-9][0-9][0-9][0-9][0-9]$//' \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' ' '-')

# Context window: 8-char progress bar + percentage
PCT=$(echo "$input" | jq -r '(.context_window.used_percentage // 0) | floor')
FILLED=$(( PCT * 8 / 100 ))
BAR=""
for i in $(seq 1 8); do
    [[ $i -le $FILLED ]] && BAR="${BAR}█" || BAR="${BAR}░"
done

# Session cost in USD
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0' | awk '{printf "%.3f", $1}')

# Lines changed (only shown when non-zero)
ADDED=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
REMOVED=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')

# Agent identity (set by launch-agents; empty in solo/interactive sessions)
AGENT="${AGENT_ID:-}"

# Compose statusline
out=""
[[ -n "$AGENT" ]] && out="${AGENT} · "
out="${out}${MODEL_SHORT} · ${BAR} ${PCT}% · \$${COST}"
[[ $((ADDED + REMOVED)) -gt 0 ]] && out="${out} · +${ADDED}/-${REMOVED}"

echo "$out"
