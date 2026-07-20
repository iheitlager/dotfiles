#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

# Symlink pandoc data directory to XDG_DATA_HOME/pandoc.
# Pandoc reads templates, filters, and defaults from this location natively.

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
PANDOC_DATA="$XDG_DATA_HOME/pandoc"
PANDOC_SRC="$DOTFILES/pandoc/data"

if [ -L "$PANDOC_DATA" ] && [ "$(readlink "$PANDOC_DATA")" = "$PANDOC_SRC" ]; then
  printf "\r\033[2K  [ \033[00;32mOK\033[0m ] pandoc data dir already linked\n"
elif [ -e "$PANDOC_DATA" ]; then
  printf "\r\033[2K  [\033[0;31mFAIL\033[0m] $PANDOC_DATA exists but is not the expected symlink — remove it manually\n"
  exit 1
else
  ln -s "$PANDOC_SRC" "$PANDOC_DATA"
  printf "\r\033[2K  [ \033[00;32mOK\033[0m ] linked $PANDOC_DATA -> $PANDOC_SRC\n"
fi
