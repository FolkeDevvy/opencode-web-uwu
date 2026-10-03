"""Record a QML scene at an exact 60 fps.

Run under libfaketime (FAKETIME="+0 x0.05"): the whole process, Qt's animations
included, runs 20x slower than real time, so grabbing a frame every 1/60 s of
*virtual* time gives smooth, exact frames however slow grabbing is.
"""
import argparse, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kde" / "lockscreen" / "preview"))
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlPropertyMap
from PySide6.QtQuick import QQuickView
import preview as lp

ap = argparse.ArgumentParser()
ap.add_argument("qml"); ap.add_argument("out")
ap.add_argument("--size", default="1920x1080"); ap.add_argument("--seconds", type=float, default=5)
ap.add_argument("--lock", action="store_true"); ap.add_argument("--theme", default="night")
ap.add_argument("--script", default=""); ap.add_argument("--stages", default="")
a = ap.parse_args()
W, H = (int(v) for v in a.size.split("x"))
app = QGuiApplication(sys.argv)
v = QQuickView(); v.setResizeMode(QQuickView.SizeRootObjectToView); v.setColor(Qt.black)
if a.lock:
    ctx = v.rootContext(); auth = lp.FakeAuthenticator("uwu"); cfg = QQmlPropertyMap(app)
    for k, val in (("theme", a.theme), ("useWallpaper", False), ("petals", True), ("petalCount", 40)): cfg.insert(k, val)
    ctx.setContextProperty("authenticator", auth); ctx.setContextProperty("kscreenlocker_userName", "Folke")
    ctx.setContextProperty("kscreenlocker_userImage", ""); ctx.setContextProperty("config", cfg); ctx.setContextProperty("wallpaper", None)
v.setSource(QUrl.fromLocalFile(a.qml))
if v.status() != QQuickView.Ready:
    [print(e.toString()) for e in v.errors()]; sys.exit(1)
v.setGeometry(0, 0, W, H); v.show()
root = v.rootObject()
for item in filter(None, a.stages.split(",")):      # "ms:stage"
    ms, st = item.split(":"); QTimer.singleShot(int(ms), lambda st=int(st): root.setProperty("stage", st))
def run_script(script):
    """Like the preview's runner, but every keystroke gets an absolute time, so a slow
    frame grab can never reorder typing and Enter."""
    t = 0
    for step in filter(None, (x.strip() for x in script.split(";"))):
        cmd, _, arg = step.partition(" ")
        if cmd == "wait":
            t += int(arg)
        elif cmd == "type":
            for ch in arg:
                QTimer.singleShot(t, lambda ch=ch: lp.press(v, ord(ch.upper()) if ch.isalnum() else 0, ch))
                t += 90
        elif cmd == "enter":
            QTimer.singleShot(t, lambda: lp.press(v, Qt.Key_Return, "\r"))
            t += 10


if a.script:
    run_script(a.script)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", "60",
                       "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv444p", a.out], stdin=subprocess.PIPE)
total = int(a.seconds * 60); n = 0; t0 = time.monotonic()
def tick():
    global n
    while n < total and time.monotonic() - t0 >= n / 60:
        img = v.grabWindow().convertToFormat(v.grabWindow().Format.Format_ARGB32)
        ff.stdin.write(bytes(img.constBits())[: W * H * 4]); n += 1
    if n >= total:
        ff.stdin.close(); ff.wait(); app.quit()
timer = QTimer(); timer.setInterval(2); timer.timeout.connect(tick); timer.start()
app.exec()
print("frames", n)
