#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0


# XDG compliant: use DOCKER_CONFIG or default to ~/.config/docker
DOCKER_CONFIG="${DOCKER_CONFIG:-$HOME/.config/docker}"
mkdir -p "$DOCKER_CONFIG/cli-plugins"
ln -sfn $(which docker-buildx) "$DOCKER_CONFIG/cli-plugins/docker-buildx"
# Note: 'docker buildx install' is deprecated - the symlink above is sufficient
# docker buildx install
