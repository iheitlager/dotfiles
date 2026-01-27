#!/usr/bin/env bash
# tmux installation and setup

TPM_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/tmux/plugins/tpm"

# Install TPM (Tmux Plugin Manager)
if [ ! -d "$TPM_DIR" ]; then
    echo "  Installing TPM (Tmux Plugin Manager)..."
    git clone https://github.com/tmux-plugins/tpm "$TPM_DIR"
    echo "  TPM installed. Run 'prefix + I' inside tmux to install plugins."
else
    echo "  TPM already installed at $TPM_DIR"
    echo "  Update with: cd $TPM_DIR && git pull"
fi

echo ""
echo "  tmux tips:"
echo "    prefix + I     Install plugins"
echo "    prefix + U     Update plugins"
echo "    prefix + |     Split vertical"
echo "    prefix + -     Split horizontal"
echo "    Alt+arrows     Switch panes"
echo "    Shift+arrows   Switch windows"
