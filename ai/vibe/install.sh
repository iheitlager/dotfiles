#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

# Install or update Mistral Vibe CLI (Vibe Code)
# https://pypi.org/project/mistral-vibe/
# Pin to 3.14: default 3.15 has no rpds-py wheels yet (PyO3 max is 3.14)
uv tool install --upgrade --python 3.14 mistral-vibe

# No ~/.vibe symlink needed: ai/vibe/bash_env sets VIBE_HOME to
# ~/.config/vibe, which script/bootstrap links to ai/vibe/config
# (dir-level link, so vibe's atomic config writes cannot break it;
# runtime files written into the directory are gitignored).
