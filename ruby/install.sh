#!/usr/bin/env bash

## install rvm
command curl -sSL https://rvm.io/mpapis.asc | gpg --import -
\curl -L https://get.rvm.io | bash -s stable
# cleanup
rm $HOME/.profile

# activate rvm
source "$HOME/.rvm/scripts/rvm"

# download ruby through rvm
rvm install ruby-2.4.1
