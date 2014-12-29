#!/bin/bash

if [ ! -d ~/wc ];
then
    echo "  Creating an empty working directory for your git repos"
    mkdir ~/wc
fi
if [ ! -d ~/tmp ];
then
    echo "  Creating an empty temp dir"
    mkdir ~/tmp
fi
