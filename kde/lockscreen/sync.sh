#!/bin/sh
# ♡ uwu lock screen: keep the per-user copy of Plasma's desktop shell in sync.
#
# Since Plasma 6.1 the lock screen lives inside the desktop shell package
# (org.kde.plasma.desktop), and KDE only lets a user override a package as a
# whole. So we keep a copy of the system package in ~/.local/share with our
# lockscreen/ folder swapped in. This script refreshes that copy whenever
# Plasma is updated. It runs at login and right after Plasma updates; it's
# quick when nothing changed.
set -eu

DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
OURS="$DATA/uwu-lockscreen/lockscreen"
OVERLAY="$DATA/plasma/shells/org.kde.plasma.desktop"
MARK="$OVERLAY/.uwu-lockscreen"

find_system() (
    IFS=:
    for d in ${XDG_DATA_DIRS:-/usr/local/share:/usr/share}; do
        if [ -f "$d/plasma/shells/org.kde.plasma.desktop/metadata.json" ]; then
            echo "$d/plasma/shells/org.kde.plasma.desktop"
            return
        fi
    done
)

# never touch an override that isn't ours
if [ -e "$OVERLAY" ] && [ ! -f "$MARK" ]; then
    echo "uwu-lockscreen: $OVERLAY exists and isn't ours, leaving it alone" >&2
    exit 0
fi

# uninstalled (our files are gone): remove the copy so Plasma uses its own again
if [ ! -f "$OURS/LockScreen.qml" ]; then
    [ -f "$MARK" ] && rm -rf "$OVERLAY"
    exit 0
fi

SYSTEM="$(find_system)"
if [ -z "$SYSTEM" ] || [ ! -f "$SYSTEM/contents/lockscreen/LockScreen.qml" ]; then
    # no Plasma 6.1+ desktop shell found: don't leave a stale copy around
    echo "uwu-lockscreen: Plasma's desktop shell (6.1 or newer) not found" >&2
    [ -f "$MARK" ] && rm -rf "$OVERLAY"
    exit 0
fi

stamp="$( (cd "$SYSTEM" && find . -type f -exec stat -c '%n %s %Y' {} + ; cd "$OURS" && find . -type f -exec stat -c 'uwu %n %s %Y' {} +) | sort | md5sum | cut -d' ' -f1)"
if [ -f "$MARK" ] && [ "$(cat "$MARK")" = "$stamp" ]; then
    exit 0
fi

# build the new copy next to the old one, then swap it in
mkdir -p "$(dirname "$OVERLAY")"
tmp="$OVERLAY.uwu-new"
rm -rf "$tmp"
cp -RL "$SYSTEM" "$tmp"
chmod -R u+w "$tmp"
rm -rf "$tmp/contents/lockscreen"
cp -RL "$OURS" "$tmp/contents/lockscreen"
echo "$stamp" > "$tmp/.uwu-lockscreen"
if [ -e "$OVERLAY" ]; then
    mv "$OVERLAY" "$OVERLAY.uwu-old"
fi
mv "$tmp" "$OVERLAY"
rm -rf "$OVERLAY.uwu-old"
echo "uwu-lockscreen: synced with $SYSTEM"
