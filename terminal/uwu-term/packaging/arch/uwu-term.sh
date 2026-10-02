#!/bin/sh
# ♡ uwu-term launcher: runs the app with Arch's system Electron.
# Native Wayland on Plasma (falls back to X11 automatically). Extra Electron
# flags can go in ~/.config/uwu-term-flags.conf, one per line.
flags=""
conf="${XDG_CONFIG_HOME:-$HOME/.config}/uwu-term-flags.conf"
[ -f "$conf" ] && flags="$(grep -v '^[[:space:]]*#' "$conf")"
# shellcheck disable=SC2086
exec electron /usr/lib/uwu-term --ozone-platform-hint=auto $flags "$@"
