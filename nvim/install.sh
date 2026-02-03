#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

set -e

# XDG directories
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
DOTFILES="${DOTFILES:-$(cd "$(dirname "$0")/.." && pwd)}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NVIM_CONFIG="$SCRIPT_DIR/config"

echo "  Setting up Neovim..."

############################################################################
# Ensure config symlink exists (fallback if bootstrap didn't run)
############################################################################
if [ ! -L "$XDG_CONFIG_HOME/nvim" ]; then
    if [ -d "$XDG_CONFIG_HOME/nvim" ] || [ -f "$XDG_CONFIG_HOME/nvim" ]; then
        # Backup existing config
        echo "  Backing up existing nvim config..."
        mv "$XDG_CONFIG_HOME/nvim" "$XDG_CONFIG_HOME/nvim.backup.$(date +%s)"
    fi
    echo "  Creating symlink: $XDG_CONFIG_HOME/nvim -> $NVIM_CONFIG"
    ln -s "$NVIM_CONFIG" "$XDG_CONFIG_HOME/nvim"
fi

# Verify symlink points to correct location
CURRENT_TARGET=$(readlink "$XDG_CONFIG_HOME/nvim" 2>/dev/null || echo "")
if [ "$CURRENT_TARGET" != "$NVIM_CONFIG" ]; then
    echo "  ⚠ Warning: nvim symlink points to $CURRENT_TARGET instead of $NVIM_CONFIG"
    echo "  Run: ln -sfn $NVIM_CONFIG $XDG_CONFIG_HOME/nvim"
fi

############################################################################
# Install plugins and compile treesitter parsers
############################################################################
if ! command -v nvim &> /dev/null; then
    echo "  ⚠ Warning: nvim not found, skipping plugin installation"
    exit 0
fi

echo "  Installing Neovim plugins..."
nvim --headless "+Lazy! sync" +qa
echo "  ✓ Plugins installed"

echo "  Compiling Treesitter parsers..."
PARSERS="lua vim vimdoc bash python javascript typescript json yaml markdown"
nvim --headless "+TSInstall! $PARSERS" +qa
echo "  ✓ Treesitter parsers compiled"

echo "  ✓ Neovim setup complete"
