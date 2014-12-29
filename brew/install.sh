#!/bin/sh
#
# Homebrew
#
# This installs some of the common dependencies needed (or at least desired)
# using Homebrew.

PACKAGES=( brew-cask )
# Check for Homebrew
if test ! $(which brew)
then
  echo "  Installing Homebrew for you."
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
else
  echo "  Found Homebrew, already installed."
fi

# Install homebrew packages
# brew install grc coreutils spark
for package in $PACKAGES; do
    if ! brew install $package
    then
        brew upgrade $package
    fi
done

exit 0
