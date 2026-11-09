#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

# Install or update Mistral Vibe CLI (Vibe Code)
# https://pypi.org/project/mistral-vibe/
# Pin to 3.14: default 3.15 has no rpds-py wheels yet (PyO3 max is 3.14)
uv tool install --upgrade --python 3.14 mistral-vibe

# Vibe uses ~/.vibe as VIBE_HOME (it ignores XDG). Symlink the whole directory
# to the versioned topic config: a dir-level link survives vibe's atomic config
# writes (a file-level link gets replaced on every save). Runtime files written
# into the directory are covered by config/.gitignore.
# Layer 2 (~/.config/vibe -> ai/vibe/config) is linked by script/bootstrap.
DOTFILES="${DOTFILES:-$HOME/.dotfiles}"
if [ -L "$HOME/.vibe" ]; then
    ln -sfn "$DOTFILES/ai/vibe/config" "$HOME/.vibe"
elif [ -e "$HOME/.vibe" ]; then
    echo "warning: $HOME/.vibe is a real directory; move its contents into $DOTFILES/ai/vibe/config and re-run" >&2
else
    ln -s "$DOTFILES/ai/vibe/config" "$HOME/.vibe"
fi
