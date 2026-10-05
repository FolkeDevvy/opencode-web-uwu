#!/usr/bin/env bash
# ♡ uwu ✧ one installer for everything in this repo.
#
#   ./uwu.sh                         pick what to install / remove from a menu
#   ./uwu.sh install web tui vscode  install those
#   ./uwu.sh install all             install everything
#   ./uwu.sh uninstall lockscreen    remove that
#   ./uwu.sh status                  show what's installed
#   ./uwu.sh list                    show the components
#
# Options:
#   --day          Plasma theme: use uwu day instead of uwu night
#   --yes, -y      don't ask for confirmation
#
# Everything installs per user (no root), and uninstall only removes what this
# installer added.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
BIN="$HOME/.local/bin"
STATE="$DATA/uwu"
mkdir -p "$STATE"

# ─────────────────────────────── looks ───────────────────────────────
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    PINK=$'\e[38;2;255;143;200m'; LAV=$'\e[38;2;199;162;255m'; MINT=$'\e[38;2;143;245;207m'
    DIM=$'\e[38;2;199;157;187m'; RED=$'\e[38;2;255;107;143m'; BOLD=$'\e[1m'; OFF=$'\e[0m'
else
    PINK=; LAV=; MINT=; DIM=; RED=; BOLD=; OFF=
fi
say()  { printf '%s\n' "$*"; }
ok()   { say "  ${MINT}✓${OFF} $*"; }
info() { say "  ${LAV}♡${OFF} $*"; }
warn() { say "  ${RED}!${OFF} $*"; }
have() { command -v "$1" >/dev/null 2>&1; }

COMPONENTS=(web tui vscode term plasma lockscreen)
declare -A TITLE=(
    [web]="opencode web"   [tui]="opencode TUI"   [vscode]="uwu IDE (VS Code)"
    [term]="uwu-term"      [plasma]="Plasma theme" [lockscreen]="lock screen"
)
declare -A DESC=(
    [web]="Firefox theme for the opencode web UI, with falling sakura"
    [tui]="pastel themes for the opencode terminal UI"
    [vscode]="VS Code extension: themes, file icons, sparkles, mascot"
    [term]="the kawaii terminal emulator"
    [plasma]="KDE Plasma 6: panel, start menu, title bars, colours, wallpaper, splash"
    [lockscreen]="KDE Plasma 6 lock screen with the sleepy bunny"
)

# ─────────────────────────────── opencode web (Firefox) ───────────────────────────────
WEB_CSS="uwu-opencode.css"
WEB_IMPORT="@import url(\"$WEB_CSS\"); /* uwu: opencode web theme */"
WEB_PREF='user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true); // uwu'

firefox_profiles() {
    # every profile in every Firefox location (classic, XDG, Flatpak, Snap)
    local root ini path rel
    for root in "$HOME/.mozilla/firefox" "$CONF/mozilla/firefox" \
                "$HOME/.var/app/org.mozilla.firefox/.mozilla/firefox" "$HOME/snap/firefox/common/.mozilla/firefox"; do
        ini="$root/profiles.ini"
        [ -f "$ini" ] || continue
        rel=1
        while IFS= read -r line; do
            case "$line" in
                \[*) rel=1 ;;
                IsRelative=*) rel="${line#IsRelative=}" ;;
                Path=*)
                    path="${line#Path=}"
                    [ "$rel" = 1 ] && path="$root/$path"
                    [ -d "$path" ] && echo "$path" ;;
            esac
        done < "$ini"
    done | awk '!seen[$0]++'
}

web_status() {
    local p
    while IFS= read -r p; do [ -f "$p/chrome/$WEB_CSS" ] && return 0; done < <(firefox_profiles)
    return 1
}
web_check() { [ -n "$(firefox_profiles)" ] || { warn "no Firefox profile found (start Firefox once first)"; return 1; }; }

web_install() {
    local p n=0 uc
    while IFS= read -r p; do
        mkdir -p "$p/chrome"
        cp "$HERE/opencode/web/chrome/userContent.css" "$p/chrome/$WEB_CSS"
        uc="$p/chrome/userContent.css"
        # pull our file in from the top of userContent.css, keeping anything you already have
        if ! grep -qF "$WEB_IMPORT" "$uc" 2>/dev/null; then
            {
                echo "$WEB_IMPORT"
                if [ -f "$uc" ]; then cat "$uc"; fi
            } > "$uc.uwu-tmp"
            mv "$uc.uwu-tmp" "$uc"
        fi
        # Firefox only reads userContent.css with this pref on
        if ! grep -qs 'toolkit.legacyUserProfileCustomizations.stylesheets", true' "$p/user.js"; then
            echo "$WEB_PREF" >> "$p/user.js"
        fi
        n=$((n + 1))
    done < <(firefox_profiles)
    ok "opencode web theme added to $n Firefox profile(s). Restart Firefox, then open opencode web."
}

web_uninstall() {
    local p uc
    while IFS= read -r p; do
        rm -f "$p/chrome/$WEB_CSS"
        uc="$p/chrome/userContent.css"
        if [ -f "$uc" ]; then
            grep -vF "$WEB_IMPORT" "$uc" > "$uc.uwu-tmp"; mv "$uc.uwu-tmp" "$uc"
            [ -s "$uc" ] || rm -f "$uc"   # it only held our line
        fi
        if [ -f "$p/user.js" ]; then
            grep -vF "$WEB_PREF" "$p/user.js" > "$p/user.js.uwu-tmp"; mv "$p/user.js.uwu-tmp" "$p/user.js"
            [ -s "$p/user.js" ] || rm -f "$p/user.js"
        fi
        rmdir "$p/chrome" 2>/dev/null || true   # only if we left it empty
    done < <(firefox_profiles)
    ok "opencode web theme removed from Firefox. Restart Firefox."
}

# ─────────────────────────────── opencode TUI ───────────────────────────────
TUI_DIR="$CONF/opencode/themes"
TUI_CFG="$CONF/opencode/cli.json"
tui_status() { [ -f "$TUI_DIR/uwu.json" ]; }
tui_check() { have opencode || info "opencode isn't on your PATH; installing the themes anyway"; return 0; }

tui_install() {
    mkdir -p "$TUI_DIR"
    cp "$HERE"/opencode/tui/themes/*.json "$TUI_DIR/"
    # pick the theme, unless you already chose one yourself
    if [ ! -f "$TUI_CFG" ]; then
        printf '{\n  "$schema": "https://opencode.ai/v2/cli.json",\n  "theme": { "name": "uwu", "mode": "system" }\n}\n' > "$TUI_CFG"
        sha256sum "$TUI_CFG" | cut -d' ' -f1 > "$STATE/tui-created-config"
        ok "opencode TUI themes installed and selected (uwu)."
    elif have python3 && python3 - "$TUI_CFG" "$STATE/tui-previous-theme.json" <<'PY'
import json, sys
cfg, backup = sys.argv[1], sys.argv[2]
data = json.load(open(cfg))
json.dump({"theme": data.get("theme")}, open(backup, "w"))
data["theme"] = {"name": "uwu", "mode": "system"}
json.dump(data, open(cfg, "w"), indent=2)
open(cfg, "a").write("\n")
PY
    then
        ok "opencode TUI themes installed and selected (uwu). Your previous theme is saved for uninstall."
    else
        ok "opencode TUI themes installed. Pick one in opencode with /themes → uwu."
    fi
}

tui_uninstall() {
    rm -f "$TUI_DIR/uwu.json" "$TUI_DIR/uwu-transparent.json"
    if [ -f "$STATE/tui-created-config" ]; then
        # we made cli.json: remove it, unless you've edited it since
        if [ -f "$TUI_CFG" ] && [ "$(sha256sum "$TUI_CFG" | cut -d' ' -f1)" = "$(cat "$STATE/tui-created-config")" ]; then
            rm -f "$TUI_CFG"
        fi
        rm -f "$STATE/tui-created-config"
    elif [ -f "$STATE/tui-previous-theme.json" ] && [ -f "$TUI_CFG" ] && have python3; then
        python3 - "$TUI_CFG" "$STATE/tui-previous-theme.json" <<'PY'
import json, sys
cfg, backup = sys.argv[1], sys.argv[2]
data = json.load(open(cfg))
old = json.load(open(backup)).get("theme")
if isinstance(data.get("theme"), dict) and data["theme"].get("name", "").startswith("uwu"):
    if old is None:
        data.pop("theme", None)
    else:
        data["theme"] = old
    json.dump(data, open(cfg, "w"), indent=2)
    open(cfg, "a").write("\n")
PY
        rm -f "$STATE/tui-previous-theme.json"
    fi
    ok "opencode TUI themes removed."
}

# ─────────────────────────────── VS Code ───────────────────────────────
VSIX="$(ls "$HERE"/vscode/uwu-code-*.vsix 2>/dev/null | sort -V | tail -1)"
EXT_ID="folkedevvy.uwu-code"
vscode_clis() { local c; for c in code code-oss codium vscodium; do have "$c" && echo "$c"; done; }
vscode_status() {
    local c
    for c in $(vscode_clis); do "$c" --list-extensions 2>/dev/null | grep -qix "$EXT_ID" && return 0; done
    return 1
}
vscode_check() { [ -n "$(vscode_clis)" ] || { warn "no VS Code found (code, code-oss or codium)"; return 1; }; }

vscode_install() {
    local c
    for c in $(vscode_clis); do
        if "$c" --install-extension "$VSIX" --force >/dev/null 2>&1; then
            ok "uwu IDE installed in $c. Pick a theme with Ctrl+K Ctrl+T → uwu."
        else
            warn "couldn't install the extension in $c"
        fi
    done
    if kawaii_workbench_patched; then
        kawaii_workbench_refresh
    else
        info "For the full kawaii IDE: Ctrl+Shift+P → \"uwu: Enable Kawaii Workbench\"."
    fi
    info "Restart VS Code (close every window) so the new version takes over."
}

# every VS Code install the Kawaii Workbench is applied to, as its uwu-kawaii/ folder
# (UWU_VSCODE_ROOTS adds install folders this list doesn't know about)
kawaii_workbench_dirs() {
    local d f
    for d in /usr/share/code /usr/lib/code /opt/visual-studio-code /usr/share/codium /opt/vscodium \
             /usr/lib/vscodium "$HOME/.local/share/code" "$HOME/VSCode-linux-x64" ${UWU_VSCODE_ROOTS:-}; do
        [ -d "$d" ] || continue
        find "$d" -maxdepth 9 -name 'workbench*.html' -exec grep -l 'uwu-kawaii:start' {} + 2>/dev/null |
            while read -r f; do [ -d "$(dirname "$f")/uwu-kawaii" ] && echo "$(dirname "$f")/uwu-kawaii"; done
    done | sort -u
}
kawaii_workbench_patched() { [ -n "$(kawaii_workbench_dirs)" ]; }

# The Kawaii Workbench lives in a copy inside VS Code's own folder, so updating the
# extension alone doesn't change it. Swap in the new files (same names, so
# workbench.html and its checksum stay as they are).
kawaii_workbench_refresh() {
    local src="$HERE/vscode/uwu-code/workbench" dir run
    while read -r dir; do
        [ -n "$dir" ] || continue
        if diff -rq "$src" "$dir" >/dev/null 2>&1; then continue; fi
        run=""
        if [ ! -w "$dir" ] || [ ! -w "$(dirname "$dir")" ]; then
            have sudo || { warn "can't update the Kawaii Workbench in $dir (no write access). In VS Code run"
                           warn "Ctrl+Shift+P → \"uwu: Enable Kawaii Workbench\" to re-apply it."; continue; }
            info "updating the Kawaii Workbench inside VS Code needs your password (sudo):"
            run=sudo
        fi
        if $run sh -c 'rm -rf "$2" && cp -r "$1" "$2"' sh "$src" "$dir"; then
            ok "Kawaii Workbench updated in $(dirname "$dir")."
        else
            warn "couldn't update the Kawaii Workbench in $dir. In VS Code run"
            warn "Ctrl+Shift+P → \"uwu: Enable Kawaii Workbench\" to re-apply it."
        fi
    done < <(kawaii_workbench_dirs)
}

vscode_uninstall() {
    local c
    if kawaii_workbench_patched; then
        warn "the Kawaii Workbench is still switched on. In VS Code run Ctrl+Shift+P →"
        warn "\"uwu: Disable Kawaii Workbench\" first, so VS Code's own look comes back."
        if [ -t 0 ] && [ "$ASSUME_YES" = 0 ]; then
            read -r -p "  remove the extension anyway? [y/N] " a
            [[ "$a" =~ ^[yY] ]] || { info "skipped the uwu IDE"; return 0; }
        fi
    fi
    for c in $(vscode_clis); do
        "$c" --uninstall-extension "$EXT_ID" >/dev/null 2>&1 && ok "uwu IDE removed from $c."
    done
}

# ─────────────────────────────── uwu-term ───────────────────────────────
TERM_DIR="$DATA/uwu-term"
term_status() { [ -x "$BIN/uwu-term" ] && [ -d "$TERM_DIR/app" ]; }
term_check() {
    have npm || { warn "uwu-term needs npm (and gcc, make, python to build node-pty)"; return 1; }
    have make || have gmake || { warn "uwu-term needs make and a C++ compiler (Arch: base-devel)"; return 1; }
}

term_install() {
    local src="$HERE/terminal/uwu-term" app="$TERM_DIR/app" deps
    info "building uwu-term (a minute or two)…"
    rm -rf "$app"; mkdir -p "$app"
    cp -R "$src"/{main.js,preload.js,package.json,package-lock.json,renderer,shell,assets} "$app/"
    # use the system electron when there is one (Arch: pacman -S electron), else bundle it
    if have electron; then deps="--omit=dev"; else deps=""; fi
    if ! (cd "$app" && npm ci $deps --no-audit --no-fund >"$TERM_DIR/npm.log" 2>&1); then
        warn "npm install failed, see $TERM_DIR/npm.log"; return 1
    fi
    mkdir -p "$BIN" "$DATA/applications" "$DATA/icons/hicolor/scalable/apps" "$DATA/icons/hicolor/256x256/apps"
    cat > "$BIN/uwu-term" <<EOF
#!/bin/sh
# ♡ uwu-term launcher (installed by uwu.sh)
APP="$app"
if command -v electron >/dev/null 2>&1; then
    exec electron "\$APP" --ozone-platform-hint=auto "\$@"
fi
exec "\$APP/node_modules/electron/dist/electron" "\$APP" --ozone-platform-hint=auto "\$@"
EOF
    chmod +x "$BIN/uwu-term"
    sed "s|^Exec=uwu-term|Exec=$BIN/uwu-term|" "$src/packaging/arch/uwu-term.desktop" > "$DATA/applications/uwu-term.desktop"
    cp "$src/assets/icon.svg" "$DATA/icons/hicolor/scalable/apps/uwu-term.svg"
    cp "$src/assets/icon.png" "$DATA/icons/hicolor/256x256/apps/uwu-term.png"
    have update-desktop-database && update-desktop-database "$DATA/applications" >/dev/null 2>&1
    ok "uwu-term installed. Find it in your app launcher, or run uwu-term."
    case ":$PATH:" in *":$BIN:"*) ;; *) info "add $BIN to your PATH to run uwu-term from a terminal" ;; esac
}

term_uninstall() {
    rm -rf "$TERM_DIR"
    rm -f "$BIN/uwu-term" "$DATA/applications/uwu-term.desktop" \
          "$DATA/icons/hicolor/scalable/apps/uwu-term.svg" "$DATA/icons/hicolor/256x256/apps/uwu-term.png"
    ok "uwu-term removed (your ~/.config/uwu-term settings are kept)."
}

# ─────────────────────────────── Plasma theme + lock screen ───────────────────────────────
plasma_status() { [ -d "$DATA/plasma/desktoptheme/uwu" ]; }
plasma_check() {
    have plasmashell || have plasma-apply-colorscheme || { warn "KDE Plasma doesn't seem to be installed"; return 1; }
}
plasma_install() {
    local args=()
    [ "$DAY" = 1 ] && args+=(--day)
    bash "$HERE/kde/plasma/install.sh" "${args[@]}" | sed 's/^/  /'
}
plasma_uninstall() {
    if [ -x "$DATA/uwu-plasma/uninstall.sh" ]; then
        bash "$DATA/uwu-plasma/uninstall.sh" | sed 's/^/  /'
    else
        bash "$HERE/kde/plasma/uninstall.sh" | sed 's/^/  /'
    fi
}

lockscreen_status() { [ -f "$DATA/uwu-lockscreen/lockscreen/LockScreen.qml" ]; }
lockscreen_check() { plasma_check; }
lockscreen_install() { bash "$HERE/kde/lockscreen/install.sh" | sed 's/^/  /'; }
lockscreen_uninstall() {
    if [ -x "$DATA/uwu-lockscreen/uninstall.sh" ]; then
        bash "$DATA/uwu-lockscreen/uninstall.sh" | sed 's/^/  /'
    else
        bash "$HERE/kde/lockscreen/uninstall.sh" | sed 's/^/  /'
    fi
}

# ─────────────────────────────── driver ───────────────────────────────
is_installed() { "${1}_status" >/dev/null 2>&1; }

banner() {
    say ""
    say "  ${PINK}${BOLD}♡ uwu ✧${OFF} ${DIM}kawaii everything installer${OFF}"
    say ""
}

show_status() {
    local i=1 c mark
    for c in "${COMPONENTS[@]}"; do
        if is_installed "$c"; then mark="${MINT}✓ installed${OFF}"; else mark="${DIM}· not installed${OFF}"; fi
        printf "  %s%-11s%s %-22s %s\n" "$PINK" "$c" "$OFF" "${TITLE[$c]}" "$mark"
        i=$((i + 1))
    done
}

run() {  # run ACTION COMPONENT...
    local action=$1; shift
    local c failed=0
    for c in "$@"; do
        say ""
        say "  ${LAV}${BOLD}${TITLE[$c]}${OFF}"
        if [ "$action" = install ]; then
            "${c}_check" || { failed=1; continue; }
            "${c}_install" || failed=1
        else
            if ! is_installed "$c"; then info "not installed, nothing to do"; continue; fi
            "${c}_uninstall" || failed=1
        fi
    done
    say ""
    if [ "$failed" = 0 ]; then say "  ${PINK}✧ all done! ♡${OFF}"; else say "  ${RED}some parts didn't finish, see above${OFF}"; fi
    return $failed
}

expand() {  # names → components (accepts "all")
    local n out=()
    for n in "$@"; do
        if [ "$n" = all ]; then out+=("${COMPONENTS[@]}"); continue; fi
        out+=("$n")
    done
    printf '%s\n' "${out[@]}" | awk '!seen[$0]++'
}

confirm() {
    [ "$ASSUME_YES" = 1 ] && return 0
    [ -t 0 ] || return 0
    read -r -p "  $1 [Y/n] " a
    [[ -z "$a" || "$a" =~ ^[yY] ]]
}

menu() {
    local -A pick=()
    local c i key
    while true; do
        clear 2>/dev/null || true
        banner
        i=1
        for c in "${COMPONENTS[@]}"; do
            local box="[ ]" state
            [ -n "${pick[$c]:-}" ] && box="${PINK}[♥]${OFF}"
            if is_installed "$c"; then state="${MINT}✓ installed${OFF}"; else state="${DIM}·${OFF}"; fi
            printf "  %s  %s%d%s  %-20s %s\n" "$box" "$BOLD" "$i" "$OFF" "${TITLE[$c]}" "$state"
            printf "          %s%s%s\n" "$DIM" "${DESC[$c]}" "$OFF"
            i=$((i + 1))
        done
        say ""
        say "  ${DIM}1-${#COMPONENTS[@]} pick · a all · n none · ${OFF}${BOLD}i${OFF}${DIM} install · ${OFF}${BOLD}u${OFF}${DIM} uninstall · ${OFF}${BOLD}d${OFF}${DIM} Plasma day/night ($( [ "$DAY" = 1 ] && echo day || echo night )) · q quit${OFF}"
        read -r -p "  ♡ " key || exit 0
        case "$key" in
            [1-9])
                c="${COMPONENTS[$((key - 1))]:-}"
                [ -n "$c" ] && { if [ -n "${pick[$c]:-}" ]; then unset "pick[$c]"; else pick[$c]=1; fi; } ;;
            a|A) for c in "${COMPONENTS[@]}"; do pick[$c]=1; done ;;
            n|N) pick=() ;;
            d|D) DAY=$((1 - DAY)) ;;
            i|I|u|U)
                local chosen=()
                for c in "${COMPONENTS[@]}"; do [ -n "${pick[$c]:-}" ] && chosen+=("$c"); done
                if [ ${#chosen[@]} -eq 0 ]; then continue; fi
                if [[ "$key" =~ [iI] ]]; then run install "${chosen[@]}"; else run uninstall "${chosen[@]}"; fi
                say ""
                read -r -p "  press enter to go back to the menu ♡ " _ || exit 0
                pick=() ;;
            q|Q|"") exit 0 ;;
        esac
    done
}

DAY=0
ASSUME_YES=0
ARGS=()
for a in "$@"; do
    case "$a" in
        --day) DAY=1 ;;
        --night) DAY=0 ;;
        -y|--yes) ASSUME_YES=1 ;;
        -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) ARGS+=("$a") ;;
    esac
done
set -- "${ARGS[@]+"${ARGS[@]}"}"

case "${1:-menu}" in
    menu)
        if [ -t 0 ]; then menu; else show_status; fi ;;
    status|list)
        banner; show_status
        [ "$1" = list ] && { say ""; for c in "${COMPONENTS[@]}"; do printf "  %s%-11s%s %s\n" "$PINK" "$c" "$OFF" "${DESC[$c]}"; done; } ;;
    install|uninstall)
        action=$1; shift
        [ $# -gt 0 ] || { warn "say what to $action, e.g. ./uwu.sh $action web tui (or all)"; exit 1; }
        for n in "$@"; do
            [ "$n" = all ] || [ -n "${TITLE[$n]+x}" ] || { warn "unknown component: $n (try: ${COMPONENTS[*]} or all)"; exit 1; }
        done
        mapfile -t chosen < <(expand "$@")
        banner
        names=(); for c in "${chosen[@]}"; do names+=("${TITLE[$c]}"); done
        confirm "$action: $(IFS=,; echo "${names[*]}" | sed 's/,/, /g')?" || exit 0
        run "$action" "${chosen[@]}" ;;
    *)
        warn "unknown command: $1"; sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
