#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0


# XDG-compliant vim directories
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
VIM_DATA="$XDG_DATA_HOME/vim"

# Create XDG directory structure
mkdir -p "$VIM_DATA/bundle"
mkdir -p "$VIM_DATA/colors"


############################################################################
# Neovim setup
############################################################################
echo "  Setting up Neovim..."

# Neovim uses XDG by default, just ensure config is linked
if [ -d "$XDG_CONFIG_HOME/nvim" ] && [ ! -L "$XDG_CONFIG_HOME/nvim" ]; then
    # Backup existing config if it's a directory
    mv "$XDG_CONFIG_HOME/nvim" "$XDG_CONFIG_HOME/nvim.backup.$(date +%s)"
fi

# Run lazy.nvim sync (headless)
if command -v nvim &> /dev/null; then
    echo "  Installing Neovim plugins..."
    if nvim --headless "+Lazy! sync" +qa 2>&1; then
        echo "  ✓ Neovim plugins installed successfully"
    else
        echo "  ⚠ Warning: Neovim plugin installation had issues (non-fatal)"
    fi
fi
