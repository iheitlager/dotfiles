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

# Install Vundle
# taken from https://github.com/gmarik/Vundle.vim
if [ ! -d "$VIM_DATA/bundle/Vundle.vim" ]; then
    git clone --quiet https://github.com/gmarik/Vundle.vim.git "$VIM_DATA/bundle/Vundle.vim"
fi

# Run PluginInstall silently (headless vim)
vim -es -u "$XDG_CONFIG_HOME/vim/vimrc" -i NONE -c "PluginInstall" -c "qa"

# http://ethanschoonover.com/solarized/vim-colors-solarized
# There is no other way?
F=$VIM_DATA/bundle/vim-colors-solarized/colors/solarized.vim
if [ -f "$F" ]; then
    ln -sf "$F" "$VIM_DATA/colors/$(basename "$F")"
fi

############################################################################
# Neovim setup
############################################################################
echo "  Setting up Neovim..."

# Neovim uses XDG by default, just ensure config is linked
if [ -d "$XDG_CONFIG_HOME/nvim" ] && [ ! -L "$XDG_CONFIG_HOME/nvim" ]; then
    # Backup existing config if it's a directory
    mv "$XDG_CONFIG_HOME/nvim" "$XDG_CONFIG_HOME/nvim.backup.$(date +%s)"
fi

# Symlink nvim config from dotfiles
ln -sfn "$DOTFILES/config/nvim" "$XDG_CONFIG_HOME/nvim"

# Run lazy.nvim sync (headless)
if command -v nvim &> /dev/null; then
    echo "  Installing Neovim plugins..."
    nvim --headless "+Lazy! sync" +qa 2>/dev/null || true
fi
