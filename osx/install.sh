#!/usr/bin/env bash

# Lot's of examples taken from https://github.com/mathiasbynens/dotfiles/blob/master/.osx

source "$(dirname "$0")/bash_env"

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
# Macbook
############################################################################
# http://osxdaily.com/2007/03/14/how-to-completely-disable-dashboard/
defaults write com.apple.dashboard mcx-disabled -boolean YES

# Disable Notification Center and remove the menu bar icon
launchctl unload -w /System/Library/LaunchAgents/com.apple.notificationcenterui.plist > /dev/null 2>&1
############################################################################
# Terminal & iTerm2
############################################################################
# Use solarized from https://github.com/tomislav/osx-terminal.app-colors-solarized
TERM_PROFILE='Workstation';
CURRENT_PROFILE="$(defaults read com.apple.terminal 'Default Window Settings')";
if [ "${CURRENT_PROFILE}" != "${TERM_PROFILE}" ]; then
    open "$(dirname "$0")/${TERM_PROFILE}.terminal";
    sleep 1; # Wait a bit to make sure the theme is loaded
    defaults write com.apple.terminal 'Default Window Settings' -string "${TERM_PROFILE}";
    defaults write com.apple.terminal 'Startup Window Settings' -string "${TERM_PROFILE}";
    # fix: https://github.com/mathiasbynens/dotfiles/pull/347/files
    defaults import com.apple.Terminal "$HOME/Library/Preferences/com.apple.Terminal.plist"
fi;

defaults write com.googlecode.iterm2 PromptOnQuit -bool false

############################################################################
# skhd - simple hotkey daemon
############################################################################
# Start skhd service (config is auto-loaded from $XDG_CONFIG_HOME/skhd/skhdrc)
if command -v skhd &> /dev/null; then
    brew services start skhd 2>/dev/null || true
    echo "  skhd service started (Alt+Return opens Ghostty)"
fi