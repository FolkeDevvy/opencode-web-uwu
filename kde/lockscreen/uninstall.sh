#!/bin/sh
# ♡ uwu lock screen: remove it and go back to Plasma's own lock screen.
set -eu
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
OVERLAY="$DATA/plasma/shells/org.kde.plasma.desktop"

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user disable --now uwu-lockscreen-sync.path >/dev/null 2>&1 || true
    rm -f "$CONF/systemd/user/uwu-lockscreen-sync.path" "$CONF/systemd/user/uwu-lockscreen-sync.service"
    systemctl --user daemon-reload >/dev/null 2>&1 || true
fi
rm -f "$CONF/plasma-workspace/env/uwu-lockscreen.sh"
# only remove the shell copy if it's the one we made
if [ -f "$OVERLAY/.uwu-lockscreen" ]; then
    rm -rf "$OVERLAY"
fi
rm -rf "$DATA/uwu-lockscreen"
echo "♡ removed. Plasma's own lock screen is back. bye bye!"
