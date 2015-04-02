#!/usr/bin/env bash

source "$(dirname "$0")/bash_env"

if [ ! -d $WORKON_DIR ] ; then
    echo "  Creating an empty Virtual env directory"
    mkdir $WORKON_DIR
fi


sudo pip install virtualenv
sudo pip install evernote
