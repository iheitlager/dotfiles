#!/usr/bin/env bash

source "$(dirname "$0")/bash_env"

# Create a set of folders
if [ ! -d $WORK_DIR ]; then
    echo "  Creating an empty working directory for your git repos"
    mkdir $WORK_DIR
fi
if [ ! -d ~/tmp ]; then
    echo "  Creating an empty temp dir"
    mkdir ~/tmp
fi


# Setup iTerm2
defaults write com.googlecode.iterm2 PromptOnQuit -bool false
