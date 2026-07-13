#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0


source "$(dirname "${BASH_SOURCE[0]}")/bash_env"

# One-time opam initialisation (compiles OCaml toolchain, takes a few minutes)
if [ ! -d "$OPAMROOT" ]; then
    echo "  Initialising opam (this compiles the OCaml toolchain — takes a few minutes)"
    opam init --disable-sandboxing --yes
fi

eval "$(opam env)"

echo "  Installing ott and coq via opam"
opam install --yes ott coq
