#!/bin/sh
# ♡ uwu lock screen installer (per user, no root needed). Plasma 6.1 or newer.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
DEST="$DATA/uwu-lockscreen"
OVERLAY="$DATA/plasma/shells/org.kde.plasma.desktop"

if [ -e "$OVERLAY" ] && [ ! -f "$OVERLAY/.uwu-lockscreen" ]; then
    echo "✗ You already have your own copy of the desktop shell at"
    echo "  $OVERLAY"
    echo "  uwu-lockscreen won't overwrite it. Move it away and run this again."
    exit 1
fi

# the lock screen lives in Plasma's desktop shell package since 6.1
SHELL_FOUND=""
IFS=: ; for d in ${XDG_DATA_DIRS:-/usr/local/share:/usr/share}; do
    [ -f "$d/plasma/shells/org.kde.plasma.desktop/contents/lockscreen/LockScreen.qml" ] && SHELL_FOUND="$d" && break
done; unset IFS
if [ -z "$SHELL_FOUND" ]; then
    echo "✗ Plasma's desktop shell (Plasma 6.1 or newer) isn't installed, so there's nothing to theme."
    exit 1
fi

echo "♡ installing the uwu lock screen…"
mkdir -p "$DEST"
rm -rf "$DEST/lockscreen"
cp -R "$HERE/lockscreen" "$DEST/lockscreen"
install -m 755 "$HERE/sync.sh" "$DEST/sync.sh"
install -m 755 "$HERE/uninstall.sh" "$DEST/uninstall.sh"

# refresh the copy at every login, before plasmashell starts…
mkdir -p "$CONF/plasma-workspace/env"
cat > "$CONF/plasma-workspace/env/uwu-lockscreen.sh" <<HOOK
# ♡ uwu lock screen: keep the lock screen in sync with Plasma updates
[ -x "$DEST/sync.sh" ] && "$DEST/sync.sh" >/dev/null 2>&1 || true
HOOK

# …and right after Plasma itself gets updated
if command -v systemctl >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1; then
    UNITS="$CONF/systemd/user"
    mkdir -p "$UNITS"
    cat > "$UNITS/uwu-lockscreen-sync.service" <<UNIT
[Unit]
Description=uwu lock screen: follow Plasma updates

[Service]
Type=oneshot
# give the package manager time to finish unpacking
ExecStartPre=/bin/sleep 20
ExecStart=$DEST/sync.sh
UNIT
    cat > "$UNITS/uwu-lockscreen-sync.path" <<UNIT
[Unit]
Description=uwu lock screen: watch for Plasma updates

[Path]
PathChanged=/usr/share/plasma/shells/org.kde.plasma.desktop/metadata.json

[Install]
WantedBy=default.target
UNIT
    systemctl --user daemon-reload
    systemctl --user enable --now uwu-lockscreen-sync.path >/dev/null 2>&1 || true
fi

"$DEST/sync.sh"

cat <<'DONE'

✧ done! Lock with Meta+L (or Ctrl+Alt+L) to see it.

Try it first without locking anything:
    /usr/lib/kscreenlocker_greet --testing
(type your real password to close it, or press Ctrl+C in the terminal)

Settings: System Settings → Screen Locking → Appearance → Configure…
Remove:   ~/.local/share/uwu-lockscreen/uninstall.sh
DONE
