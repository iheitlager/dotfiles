#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

# shell-common.sh - Shared utilities for shell scripts
# Source this file: source ~/.dotfiles/local/lib/shell-common.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'  # No Color

# Verbose/debug mode (set VERBOSE=true before sourcing or after)
VERBOSE=${VERBOSE:-false}

debug() {
    [[ "$VERBOSE" == true ]] && echo -e "${DIM}${BLUE}[DEBUG]${NC} $*" >&2
}

info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

success() {
    echo -e "${GREEN}✓${NC} $*"
}

warn() {
    echo -e "${YELLOW}!${NC} $*" >&2
}

error() {
    echo -e "${RED}✗${NC} $*" >&2
}

die() {
    error "$@"
    exit 1
}

# Check if command exists
has_cmd() {
    command -v "$1" &>/dev/null
}

# Require a command or exit
require_cmd() {
    has_cmd "$1" || die "Required command not found: $1"
}

# Clipboard utilities (cross-platform)
clipboard_copy() {
    if has_cmd pbcopy; then
        pbcopy
    elif has_cmd xclip; then
        xclip -selection clipboard
    elif has_cmd xsel; then
        xsel --clipboard --input
    else
        die "No clipboard tool found (need pbcopy, xclip, or xsel)"
    fi
}

clipboard_paste() {
    if has_cmd pbpaste; then
        pbpaste
    elif has_cmd xclip; then
        xclip -selection clipboard -o
    elif has_cmd xsel; then
        xsel --clipboard --output
    else
        die "No clipboard tool found (need pbpaste, xclip, or xsel)"
    fi
}

# Render markdown output
render_md() {
    if has_cmd mdcat; then
        mdcat
    elif has_cmd glow; then
        glow -
    else
        cat
    fi
}

# Show help using bat if available
show_help() {
    if has_cmd bat; then
        bat --plain --language=help
    else
        cat
    fi
}

# Confirm prompt (returns 0 for yes, 1 for no)
confirm() {
    local prompt="${1:-Continue?}"
    local default="${2:-n}"

    if [[ "$default" == "y" ]]; then
        read -p "$prompt [Y/n] " -n 1 -r
    else
        read -p "$prompt [y/N] " -n 1 -r
    fi
    echo

    if [[ "$default" == "y" ]]; then
        [[ ! $REPLY =~ ^[Nn]$ ]]
    else
        [[ $REPLY =~ ^[Yy]$ ]]
    fi
}

# Get script version from header comment
# Usage: get_version "$0"
get_version() {
    local script="$1"
    sed -n 's/.*Version: \([0-9.]*\).*/\1/p' "$script" | head -1
}

# Show version
# Usage: show_version "script-name" "$0"
show_version() {
    local name="$1"
    local script="$2"
    local version=$(get_version "$script")
    echo -e "${BOLD}${name}${NC} version ${GREEN}${version}${NC}"
}
