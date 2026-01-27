#!/usr/bin/env bash

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
# Macbook
############################################################################
# http://osxdaily.com/2007/03/14/how-to-completely-disable-dashboard/
defaults write com.apple.dashboard mcx-disabled -boolean YES

# Disable Notification Center and remove the menu bar icon
launchctl unload -w /System/Library/LaunchAgents/com.apple.notificationcenterui.plist > /dev/null 2>&1

defaults write com.googlecode.iterm2 PromptOnQuit -bool false

############################################################################
# hotkey - Python hotkey daemon (Alt+Enter opens Ghostty)
############################################################################
HOTKEY_SCRIPT="$DOTFILES/local/bin/hotkey"
HOTKEY_PLIST="$HOME/Library/LaunchAgents/com.dotfiles.hotkey.plist"
HOTKEY_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/hotkey"

if [ -f "$HOTKEY_SCRIPT" ]; then
    mkdir -p "$HOME/Library/LaunchAgents"
    mkdir -p "$HOTKEY_STATE"
    
    cat > "$HOTKEY_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dotfiles.hotkey</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/uv</string>
        <string>run</string>
        <string>--script</string>
        <string>$HOTKEY_SCRIPT</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>XDG_STATE_HOME</key>
        <string>${XDG_STATE_HOME:-$HOME/.local/state}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$HOTKEY_STATE/launchd.err.log</string>
</dict>
</plist>
EOF
    
    # Remove old plist if exists
    launchctl unload "$HOME/Library/LaunchAgents/com.dotfiles.hotkeys.plist" 2>/dev/null || true
    rm -f "$HOME/Library/LaunchAgents/com.dotfiles.hotkeys.plist"
    
    # Load the agent
    launchctl unload "$HOTKEY_PLIST" 2>/dev/null || true
    launchctl load -w "$HOTKEY_PLIST"
    echo "  hotkey daemon started (Alt+Enter opens Ghostty)"
    echo "  Logs: $HOTKEY_STATE/hotkey.log"
    echo "  NOTE: Requires Accessibility permissions in System Settings"
fi