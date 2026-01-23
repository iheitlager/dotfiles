#!/usr/bin/env bash

if [ ! -f $XDG_CONFIG_HOME/secrets ] ; then
    echo "  Creating an empty $XDG_CONFIG_HOME/secrets, put super secret stuff here!"
    echo > "$XDG_CONFIG_HOME/secrets"
fi
chmod og-r "$XDG_CONFIG_HOME/secrets"   

# Enable Homebrew bash as default shell
# First, check if it's in /etc/shells
if ! grep -q "$HOMEBREW_PREFIX/bin/bash" /etc/shells 2>/dev/null; then
    echo "  WARNING: $HOMEBREW_PREFIX/bin/bash is not in /etc/shells"
    echo "  To use Homebrew bash as your default shell, run manually:"
    echo "    sudo sh -c 'echo $HOMEBREW_PREFIX/bin/bash >> /etc/shells'"
    echo "    chsh -s $HOMEBREW_PREFIX/bin/bash"
elif [ "$SHELL" != "$HOMEBREW_PREFIX/bin/bash" ]; then
    # Shell is in /etc/shells, safe to change
    chsh -s "$HOMEBREW_PREFIX/bin/bash"
fi
