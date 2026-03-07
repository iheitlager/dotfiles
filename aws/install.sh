#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

# Install or upgrade AWS CLI via the official PKG installer (macOS)
# Bypasses Homebrew bottles — avoids "no bottle available" on Tier 3 configs.
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

set -e

# If awscli is still managed by Homebrew, remove it first
if brew list awscli &>/dev/null; then
    echo "  🧹 Removing Homebrew awscli (migrating to official installer)..."
    brew unpin awscli 2>/dev/null || true
    brew uninstall awscli
fi

LATEST=$(curl -s https://raw.githubusercontent.com/aws/aws-cli/v2/CHANGELOG.rst \
    | grep -m1 '^[0-9]' | awk '{print $1}')
CURRENT=$(/usr/local/bin/aws --version 2>/dev/null | awk '{print $1}' | cut -d/ -f2 || echo "none")

if [[ "$CURRENT" == "$LATEST" ]]; then
    echo "  ✅ awscli already up to date ($CURRENT)"
    exit 0
fi

echo "  ⬆️  Updating awscli: $CURRENT → $LATEST"

TMPDIR=$(mktemp -d)
PKG="$TMPDIR/awscli.pkg"

curl -fsSL "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "$PKG"
sudo installer -pkg "$PKG" -target /

rm -rf "$TMPDIR"

echo "  ✅ awscli $(/usr/local/bin/aws --version 2>/dev/null | awk '{print $1}' | cut -d/ -f2) installed"
