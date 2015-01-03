#!/usr/bin/env bash

VIM_ROOT=$HOME/.vim

rm -rf $VIM_ROOT

# install Vundle
# taken from https://github.com/gmarik/Vundle.vim
if [ ! -d "$VIM_ROOT/bundle/Vundle.vim" ]; then
    git clone https://github.com/gmarik/Vundle.vim.git "$VIM_ROOT/bundle/Vundle.vim"
fi

yes | vim +PluginInstall +qall

# http://ethanschoonover.com/solarized/vim-colors-solarized
# There is no other way?
F=$VIM_ROOT/bundle/vim-colors-solarized/colors/solarized.vim
if [ -f "$F" ]; then
    mkdir -p "$VIM_ROOT/colors"
    ln -sf "$F" $VIM_ROOT/colors/`basename "$F"`
fi
