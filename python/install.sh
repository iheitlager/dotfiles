#!/usr/bin/env bash

source "$(dirname "$0")/bash_env"

if [ ! -d $WORKON_DIR ] ; then
    mkdir $WORKON_DIR
fi
