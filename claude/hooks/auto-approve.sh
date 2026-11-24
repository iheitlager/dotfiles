#!/usr/bin/env bash
# PreToolUse hook: auto-approve Write to non-sensitive paths.
# Outputs permissionDecision=allow for safe paths; exits 0 (normal flow) otherwise.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

approve() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

if [ "$TOOL" = "Write" ]; then
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

  # Deny sensitive paths — let the deny list or user handle these
  case "$FILE" in
    ~/.ssh/*|"$HOME/.ssh/"*) exit 0 ;;
    ~/.aws/*|"$HOME/.aws/"*) exit 0 ;;
    ~/.config/secrets*|"$HOME/.config/secrets"*) exit 0 ;;
    /etc/*) exit 0 ;;
    ~/.crontab|"$HOME/.crontab") exit 0 ;;
  esac

  approve "safe Write path auto-approved"
fi

exit 0
