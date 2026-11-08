#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

# Install or update Mistral Vibe CLI (Vibe Code)
# https://pypi.org/project/mistral-vibe/
# Pin to 3.14: default 3.15 has no rpds-py wheels yet (PyO3 max is 3.14)
uv tool install --upgrade --python 3.14 mistral-vibe

# Setup XDG compliant Vibe config directory and symlinks
# Layer 2: ~/.config/vibe → ~/.dotfiles/ai/vibe/config (linked by script/bootstrap)
XDG_VIBE="${XDG_CONFIG_HOME:-$HOME/.config}/vibe"

# Symlink versionable items INTO ~/.vibe
mkdir -p "$HOME/.vibe"
ln -sfn "$XDG_VIBE/config.toml" "$HOME/.vibe/config.toml"

# Symlink all directories found in config
for dir in "$XDG_VIBE"/*/; do
    [ -d "$dir" ] && ln -sfn "$dir" "$HOME/.vibe/$(basename "$dir")"
done
