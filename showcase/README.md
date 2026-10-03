# ♡ uwu showcase ✧

One video of everything in this repo working together, from boot to lock screen:

[▶ uwu-showcase.mp4](uwu-showcase.mp4) (1080p, 60 fps)

The story:
1. boot splash
2. Plasma desktop and start menu
3. uwu-term
4. uwu IDE (VS Code)
5. opencode web
6. opencode TUI
7. switching to day colours
8. turning a monitor 90°
9. locking (a wrong password, then the right one) and unlocking

## What's real

| | |
| --- | --- |
| Splash screen, lock screen | The real QML, recorded at an exact 60 fps by `qmlrec.py` |
| uwu-term, uwu IDE, opencode web | Their real recordings (from each project's `screenshots/`) |
| opencode TUI, day-mode windows | Real screenshots |
| Desktop, panel, start menu, title bars, wallpaper | Drawn from the real Plasma theme files by `kde/plasma/preview/preview.py` |
| Cursor, window open animations, transitions | Staged by `make_showcase.py` |

Plasma itself wasn't running: the desktop shell is drawn from the theme's real files.

## Rebuild it

Needs PySide6, ffmpeg and libfaketime (`pip install PySide6 libfaketime`).

```sh
# 1. record the QML scenes. libfaketime slows the clock, so every frame is exact
FT=$(python3 -c "import libfaketime, os; print(os.path.join(os.path.dirname(libfaketime.__file__), 'vendor/libfaketime/src/libfaketime.so.1'))")
export LD_PRELOAD=$FT QT_QPA_PLATFORM=offscreen
L=../kde/lockscreen/lockscreen/LockScreen.qml
FAKETIME="+0 x0.05" python3 qmlrec.py ../kde/plasma/look-and-feel/org.uwu.night.desktop/contents/splash/Splash.qml \
    clips/q-splash.mp4 --seconds 5.5 --stages "500:2,1200:3,1900:4,2600:5,3400:6"
FAKETIME="@2026-10-03 21:41:30 x0.05" python3 qmlrec.py $L clips/q-lock.mp4 --lock --seconds 15 \
    --script "wait 3600; type hunter2; wait 800; enter; wait 3300; type uwu; wait 600; enter; wait 3000"
FAKETIME="@2026-10-03 21:41:30 x0.05" python3 qmlrec.py $L clips/q-lock-portrait.mp4 --lock --size 1080x1920 \
    --seconds 6 --script "wait 1800; type uwu; wait 2500"
unset LD_PRELOAD

# 2. put it all together
QT_QPA_PLATFORM=offscreen python3 make_showcase.py
```
