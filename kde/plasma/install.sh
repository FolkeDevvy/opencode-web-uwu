#!/bin/sh
# ♡ uwu for KDE Plasma 6: installs and applies the theme (per user, no root).
#
#   ./install.sh                 apply uwu night
#   ./install.sh --day           apply uwu day
#   ./install.sh --no-apply      only install; pick the parts yourself in System Settings
#   ./install.sh --keep-launcher-icon   don't swap the start menu icon for the uwu one
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
STATE="$DATA/uwu-plasma"
VARIANT=night
APPLY=1
ICON=1
for a in "$@"; do
    case "$a" in
        --day) VARIANT=day ;;
        --night) VARIANT=night ;;
        --no-apply) APPLY=0 ;;
        --keep-launcher-icon) ICON=0 ;;
        -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
        *) echo "unknown option: $a"; exit 1 ;;
    esac
done

have() { command -v "$1" >/dev/null 2>&1; }
KREAD=$(have kreadconfig6 && echo kreadconfig6 || echo kreadconfig5)
KWRITE=$(have kwriteconfig6 && echo kwriteconfig6 || echo kwriteconfig5)
QDBUS=$(have qdbus6 && echo qdbus6 || (have qdbus && echo qdbus) || echo "")

echo "♡ installing uwu for Plasma…"
copy() { mkdir -p "$2"; rm -rf "$2/$(basename "$1")"; cp -R "$1" "$2/"; }
copy "$HERE/desktoptheme/uwu"                    "$DATA/plasma/desktoptheme"
copy "$HERE/look-and-feel/org.uwu.night.desktop" "$DATA/plasma/look-and-feel"
copy "$HERE/look-and-feel/org.uwu.day.desktop"   "$DATA/plasma/look-and-feel"
copy "$HERE/aurorae/uwu-night"                   "$DATA/aurorae/themes"
copy "$HERE/aurorae/uwu-day"                     "$DATA/aurorae/themes"
copy "$HERE/wallpapers/uwu-sakura"               "$DATA/wallpapers"
mkdir -p "$DATA/color-schemes" "$DATA/icons/hicolor/scalable/apps"
cp "$HERE/color-schemes/UwuNight.colors" "$HERE/color-schemes/UwuDay.colors" "$DATA/color-schemes/"
cp "$HERE/icons/uwu-launcher.svg" "$DATA/icons/hicolor/scalable/apps/"
mkdir -p "$STATE"
install -m 755 "$HERE/uninstall.sh" "$STATE/uninstall.sh"

if [ "$APPLY" = 0 ]; then
    echo "✧ installed. Pick it in System Settings → Colours & Themes → Global Theme (uwu night / uwu day)."
    exit 0
fi

# remember what you had, so uninstall.sh can put it back
if [ ! -f "$STATE/backup.conf" ]; then
    {
        echo "lookandfeel=$($KREAD --file kdeglobals --group KDE --key LookAndFeelPackage)"
        echo "colorscheme=$($KREAD --file kdeglobals --group General --key ColorScheme)"
        echo "plasmatheme=$($KREAD --file plasmarc --group Theme --key name)"
        echo "decolibrary=$($KREAD --file kwinrc --group org.kde.kdecoration2 --key library)"
        echo "decotheme=$($KREAD --file kwinrc --group org.kde.kdecoration2 --key theme)"
        echo "splashengine=$($KREAD --file ksplashrc --group KSplash --key Engine)"
        echo "splashtheme=$($KREAD --file ksplashrc --group KSplash --key Theme)"
    } > "$STATE/backup.conf"
fi

LNF="org.uwu.$VARIANT.desktop"
SCHEME=$([ "$VARIANT" = day ] && echo UwuDay || echo UwuNight)
echo "♡ applying uwu $VARIANT…"
have plasma-apply-lookandfeel && plasma-apply-lookandfeel --apply "$LNF" >/dev/null 2>&1 || true
# apply each part explicitly too (works even if the global theme step skipped something)
have plasma-apply-colorscheme && plasma-apply-colorscheme "$SCHEME" >/dev/null 2>&1 || true
have plasma-apply-desktoptheme && plasma-apply-desktoptheme uwu >/dev/null 2>&1 || true
$KWRITE --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
$KWRITE --file kwinrc --group org.kde.kdecoration2 --key theme "__aurorae__svg__uwu-$VARIANT"
$KWRITE --file ksplashrc --group KSplash --key Engine KSplashQML
$KWRITE --file ksplashrc --group KSplash --key Theme "$LNF"
[ -n "$QDBUS" ] && $QDBUS org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
have plasma-apply-wallpaperimage && plasma-apply-wallpaperimage "$DATA/wallpapers/uwu-sakura" >/dev/null 2>&1 || true

# the start menu button: the uwu sakura icon
if [ "$ICON" = 1 ] && [ -n "$QDBUS" ]; then
    $QDBUS org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
        panels().forEach(function (p) {
            p.widgets().forEach(function (w) {
                if (["org.kde.plasma.kickoff", "org.kde.plasma.kicker", "org.kde.plasma.kickerdash"].indexOf(w.type) >= 0) {
                    w.currentConfigGroup = ["General"];
                    w.writeConfig("icon", "uwu-launcher");
                    w.reloadConfig();
                }
            });
        });' >/dev/null 2>&1 || echo "  (couldn't set the start menu icon; right-click it → Configure → Icon → uwu-launcher)"
fi

cat <<DONE

✧ uwu $VARIANT is on! ♡
  Switch any time: System Settings → Colours & Themes → Global Theme → uwu night / uwu day
  Splash screen: shows from your next login.
  Remove: $STATE/uninstall.sh
DONE
