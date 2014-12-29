#!/bin/bash

if [ ! -f ~/.localrc ];
then
    echo "  Creating an empyt ~/.localrc, put super secret stuff here!"
    echo > ~/.localrc
fi
