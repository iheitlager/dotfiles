#!/usr/bin/env bash

source "$(dirname "$0")/bash_env"

if [ ! -d $WORKON_DIR ] ; then
    echo "  Creating an empty Virtual env directory"
    mkdir $WORKON_DIR
fi

if [ ! -d ~/.pip ] ; then
    echo "  creating ~/.pip directory"
    mkdir ~/.pip
fi
ln -fs `pwd`/pip.conf ~/.pip/pip.conf

