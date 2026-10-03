#!/usr/bin/env python3
"""Preview the uwu lock screen without locking anything.

Loads lockscreen/LockScreen.qml the way kscreenlocker_greet does, with a fake
`authenticator` that accepts the password "uwu". Needs PySide6
(`pip install PySide6`). On Plasma you can also test the real thing safely with
the greeter's own testing mode (see the README).

    python3 preview.py                        # 1280x720 window
    python3 preview.py --size 1080x1920       # a monitor turned 90° (portrait)
    python3 preview.py --theme day --name "Folke"

Scripted runs (used for the screenshots):
    python3 preview.py --script "wait 1500; shot a.png; type hunter2; enter; wait 900; shot b.png"
"""
import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Property, QTimer, QUrl, Signal, Slot, Qt, QByteArray
from PySide6.QtCore import QEvent
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtQml import QQmlPropertyMap
from PySide6.QtQuick import QQuickView
from PySide6.QtTest import QTest

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / "lockscreen" / "LockScreen.qml"


class FakeAuthenticator(QObject):
    """Same surface as kscreenlocker's PamAuthenticators (Plasma 6.x)."""
    succeeded = Signal()
    failed = Signal(int, QObject)
    busyChanged = Signal()
    promptChanged = Signal()
    promptForSecretChanged = Signal()
    infoMessageChanged = Signal()
    errorMessageChanged = Signal()
    hadPromptChanged = Signal()

    def __init__(self, password):
        super().__init__()
        self._password = password
        self._busy = False
        self._had_prompt = False
        self._prompt_secret = ""

    def _get_busy(self):
        return self._busy

    def _get_had_prompt(self):
        return self._had_prompt

    def _get_prompt_secret(self):
        return self._prompt_secret

    def _empty(self):
        return ""

    busy = Property(bool, _get_busy, notify=busyChanged)
    hadPrompt = Property(bool, _get_had_prompt, notify=hadPromptChanged)
    promptForSecret = Property(str, _get_prompt_secret, notify=promptForSecretChanged)
    prompt = Property(str, _empty, notify=promptChanged)
    infoMessage = Property(str, _empty, notify=infoMessageChanged)
    errorMessage = Property(str, _empty, notify=errorMessageChanged)

    @Slot()
    def startAuthenticating(self):
        if not self._prompt_secret:
            self._prompt_secret = "Password: "
            self._had_prompt = True
            self.promptForSecretChanged.emit()
            self.hadPromptChanged.emit()

    @Slot(QByteArray)
    def respond(self, response):
        attempt = bytes(response).decode()
        print("respond:", "*" * len(attempt), flush=True)
        self._busy = True
        self.busyChanged.emit()

        def check():
            self._busy = False
            self.busyChanged.emit()
            if attempt == self._password:
                print("succeeded", flush=True)
                self.succeeded.emit()
            else:
                print("failed", flush=True)
                self.failed.emit(0, None)

        QTimer.singleShot(700, check)


def press(view, key, text):
    for kind in (QEvent.KeyPress, QEvent.KeyRelease):
        QGuiApplication.sendEvent(view, QKeyEvent(kind, key, Qt.NoModifier, text))


def run_script(view, script, app):
    steps = [s.strip() for s in script.split(";") if s.strip()]
    delay = 0
    for step in steps:
        cmd, _, arg = step.partition(" ")
        if cmd == "wait":
            delay += int(arg)
            continue

        def act(cmd=cmd, arg=arg):
            if cmd == "shot":
                view.grabWindow().save(arg)
                print("shot", arg, flush=True)
            elif cmd == "type":
                for i, ch in enumerate(arg):
                    QTimer.singleShot(i * 90, lambda ch=ch: press(view, ord(ch.upper()) if ch.isalnum() else 0, ch))
            elif cmd == "enter":
                press(view, Qt.Key_Return, "\r")
            elif cmd == "esc":
                press(view, Qt.Key_Escape, "")
            elif cmd == "move":
                from PySide6.QtCore import QPoint
                x, y = (int(v) for v in arg.split(","))
                QTest.mouseMove(view, QPoint(x, y))
            elif cmd == "click":
                from PySide6.QtCore import QPoint
                x, y = (int(v) for v in arg.split(","))
                QTest.mouseClick(view, Qt.LeftButton, Qt.NoModifier, QPoint(x, y))
            elif cmd == "quit":
                app.quit()

        QTimer.singleShot(delay, act)
        delay += 10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--theme", default="night", choices=["night", "day"])
    ap.add_argument("--name", default="Folke")
    ap.add_argument("--password", default="uwu")
    ap.add_argument("--petals", type=int, default=40)
    ap.add_argument("--wallpaper", action="store_true", help="tint over a sample wallpaper colour instead of the gradient")
    ap.add_argument("--script", default="")
    ap.add_argument("--pos", default="0,0")
    args = ap.parse_args()

    app = QGuiApplication(sys.argv)
    w, h = (int(v) for v in args.size.split("x"))

    view = QQuickView()
    ctx = view.rootContext()
    auth = FakeAuthenticator(args.password)
    config = QQmlPropertyMap(app)
    config.insert("theme", args.theme)
    config.insert("useWallpaper", args.wallpaper)
    config.insert("petals", args.petals > 0)
    config.insert("petalCount", args.petals)
    ctx.setContextProperty("authenticator", auth)
    ctx.setContextProperty("kscreenlocker_userName", args.name)
    ctx.setContextProperty("kscreenlocker_userImage", "")
    ctx.setContextProperty("config", config)
    ctx.setContextProperty("wallpaper", None)
    view.engine().quit.connect(lambda: (print("UNLOCKED - greeter would exit", flush=True), app.quit()))
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    if args.wallpaper:
        view.setColor("#5a7fb0")
    view.setSource(QUrl.fromLocalFile(str(MAIN)))
    if view.status() != QQuickView.Ready:
        for e in view.errors():
            print("QML error:", e.toString(), file=sys.stderr)
        return 1
    px, py = (int(v) for v in args.pos.split(","))
    view.setGeometry(px, py, w, h)
    view.setTitle("uwu lock screen preview")
    view.show()
    view.requestActivate()
    if args.script:
        run_script(view, args.script, app)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
