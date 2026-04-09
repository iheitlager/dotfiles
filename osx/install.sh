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
# Power Management
###########################################################################
echo "  Configuring power management for profile: ${MACHINE_PROFILE:-laptop}..."
if [ "${MACHINE_PROFILE:-laptop}" = "workstation" ]; then
  # Always-on server (Mac mini)
  sudo pmset -a sleep 0             # Never sleep
  sudo pmset -a disksleep 0         # Never spin down disks
  sudo pmset -a displaysleep 15     # Display off after 15 min
  sudo pmset -a standby 0           # Disable standby mode
  sudo pmset -a networkoversleep 0  # Keep network active during sleep
  sudo pmset -a powernap 1          # Power Nap on (background tasks, backups)
  sudo pmset -a womp 1              # Wake on magic packet (Wake-on-LAN)
  sudo pmset -a autorestart 1       # Auto-restart after power failure
else
  # Laptop defaults
  sudo pmset -a sleep 30            # Sleep after 30 min inactivity
  sudo pmset -a disksleep 10        # Spin down disks after 10 min
  sudo pmset -a displaysleep 10     # Display off after 10 min
  sudo pmset -a standby 1           # Enable standby
  sudo pmset -a networkoversleep 0  # Keep network active during sleep
  sudo pmset -a powernap 1          # Power Nap on
  sudo pmset -a womp 0              # No wake on LAN
  sudo pmset -a autorestart 0       # No auto-restart after power failure
fi

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
