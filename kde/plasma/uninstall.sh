#!/bin/sh
# ♡ uwu for KDE Plasma: put your previous look back and remove the theme files.
set -eu
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
STATE="$DATA/uwu-plasma"
have() { command -v "$1" >/dev/null 2>&1; }
KWRITE=$(have kwriteconfig6 && echo kwriteconfig6 || echo kwriteconfig5)
QDBUS=$(have qdbus6 && echo qdbus6 || (have qdbus && echo qdbus) || echo "")

get() { [ -f "$STATE/backup.conf" ] && sed -n "s/^$1=//p" "$STATE/backup.conf" || true; }
lnf=$(get lookandfeel); scheme=$(get colorscheme); ptheme=$(get plasmatheme)
dlib=$(get decolibrary); dtheme=$(get decotheme); sengine=$(get splashengine); stheme=$(get splashtheme)

echo "♡ restoring your previous look…"
have plasma-apply-lookandfeel && plasma-apply-lookandfeel --apply "${lnf:-org.kde.breeze.desktop}" >/dev/null 2>&1 || true
have plasma-apply-colorscheme && plasma-apply-colorscheme "${scheme:-BreezeLight}" >/dev/null 2>&1 || true
have plasma-apply-desktoptheme && plasma-apply-desktoptheme "${ptheme:-default}" >/dev/null 2>&1 || true
$KWRITE --file kwinrc --group org.kde.kdecoration2 --key library "${dlib:-org.kde.breeze}"
$KWRITE --file kwinrc --group org.kde.kdecoration2 --key theme "${dtheme:-Breeze}"
$KWRITE --file ksplashrc --group KSplash --key Engine "${sengine:-KSplashQML}"
$KWRITE --file ksplashrc --group KSplash --key Theme "${stheme:-org.kde.breeze.desktop}"
if [ -n "$QDBUS" ]; then
    $QDBUS org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
    $QDBUS org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
        panels().forEach(function (p) {
            p.widgets().forEach(function (w) {
                w.currentConfigGroup = ["General"];
                if (w.readConfig("icon", "") === "uwu-launcher") {
                    w.writeConfig("icon", "start-here-kde-symbolic");
                    w.reloadConfig();
                }
            });
        });' >/dev/null 2>&1 || true
fi

rm -rf "$DATA/plasma/desktoptheme/uwu" "$DATA/plasma/look-and-feel/org.uwu.night.desktop" \
       "$DATA/plasma/look-and-feel/org.uwu.day.desktop" "$DATA/aurorae/themes/uwu-night" \
       "$DATA/aurorae/themes/uwu-day" "$DATA/color-schemes/UwuNight.colors" "$DATA/color-schemes/UwuDay.colors" \
       "$DATA/icons/hicolor/scalable/apps/uwu-launcher.svg"
echo "  (the sakura wallpaper stays in $DATA/wallpapers/uwu-sakura until you pick another wallpaper and delete it)"
rm -rf "$STATE"
echo "♡ removed. bye bye!"
