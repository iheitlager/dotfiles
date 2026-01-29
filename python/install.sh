#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0


source "$(dirname "$0")/bash_env"

if [ ! -d $WORKON_DIR ] ; then
    echo "  Creating an empty Virtual env directory"
    mkdir $WORKON_DIR
fi

# pip.conf is now XDG compliant at ~/.config/pip/pip.conf
# (handled by config/pip/ via bootstrap link_config_files)
