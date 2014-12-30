#!/usr/bin/env bash

# install Vundle
# taken from https://github.com/gmarik/Vundle.vim
if [ ! -d ~/.vim/bundle/Vundle.vim ];
then
   git clone https://github.com/gmarik/Vundle.vim.git ~/.vim/bundle/Vundle.vim
fi
