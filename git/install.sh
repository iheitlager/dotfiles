#!/usr/bin/env bash
# Point the dotfiles repo at its own tracked hooks directory.
# Bootstrap runs all install.sh files automatically.
DOTFILES="${DOTFILES:-$HOME/.dotfiles}"
git -C "$DOTFILES" config --local core.hooksPath "$DOTFILES/git/hooks"
