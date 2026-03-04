#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

# Load XDG-compliant env (CARGO_HOME, RUSTUP_HOME, PATH)
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export CARGO_HOME="${CARGO_HOME:-$XDG_DATA_HOME/cargo}"
export RUSTUP_HOME="${RUSTUP_HOME:-$XDG_DATA_HOME/rustup}"
export PATH="$CARGO_HOME/bin:$PATH"

echo "  Setting up Rust toolchain..."

# rustup must be installed via brew first (see brew_packages)
if ! command -v rustup &>/dev/null; then
    echo "  ⚠ rustup not found — run: brew install rustup"
    exit 1
fi

# Init cargo shims if cargo is missing (rustup installed but not initialised)
if ! command -v cargo &>/dev/null; then
    echo "  Initialising cargo shims..."
    rustup-init -y --no-modify-path
    # Source cargo env to make cargo available in this session
    local_cargo_env="${CARGO_HOME}/env"
    [ -f "$local_cargo_env" ] && source "$local_cargo_env"
fi

# Set default stable toolchain if none set
if ! rustup toolchain list 2>&1 | grep -q "default"; then
    echo "  Setting default Rust toolchain to stable..."
    rustup default stable
fi

echo "  ✓ $(rustc --version 2>/dev/null || echo 'rustc not found')"
echo "  ✓ $(cargo --version 2>/dev/null || echo 'cargo not found')"
echo "  ✓ CARGO_HOME  = $CARGO_HOME"
echo "  ✓ RUSTUP_HOME = $RUSTUP_HOME"
