#!/usr/bin/env bash

# XDG-compliant vim directories
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
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
