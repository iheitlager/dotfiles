#!/usr/bin/env bash
# Copyright 2026 Ilja Heitlager
# SPDX-License-Identifier: Apache-2.0


# Lot's of examples taken from https://github.com/mathiasbynens/dotfiles/blob/master/.osx

source "$DOTFILES/osx/bash_env"

# Create a set of folders
if [ ! -d $WORK_DIR ]; then
    echo "  Creating an empty working directory for your git repos"
    mkdir $WORK_DIR
fi
# I prefer to have a persistent TEMP dir next to $TMPDIR and ~/.Trash
if [ ! -d ~/tmp ]; then
    echo "  Creating an empty temp dir"
    mkdir ~/tmp
fi

###########################################################################
# Power Management (Mac mini sensible defaults)
###########################################################################
echo "  Configuring power management defaults..."
sudo pmset -a sleep 30            # Sleep after 30 min inactivity
sudo pmset -a disksleep 10        # Spin down disks after 10 min
sudo pmset -a displaysleep 10     # Display off after 10 min
sudo pmset -a networkoversleep 0  # Keep network active during sleep (SSH, Wake-on-LAN)
sudo pmset -a powernap 1          # Power Nap on (default)
# Note: auto-trader launch.sh overrides these to never-sleep when agents are running

###########################################################################
# Macbook
############################################################################
# http://osxdaily.com/2007/03/14/how-to-completely-disable-dashboard/
defaults write com.apple.dashboard mcx-disabled -boolean YES

# Disable Notification Center and remove the menu bar icon
launchctl unload -w /System/Library/LaunchAgents/com.apple.notificationcenterui.plist > /dev/null 2>&1

defaults write com.googlecode.iterm2 PromptOnQuit -bool false

# Note: Alt+Enter hotkey is now handled natively by Ghostty
# See: config/ghostty/config → keybind = global:alt+enter=toggle_quick_terminal
