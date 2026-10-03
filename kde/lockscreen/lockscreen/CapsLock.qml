// Optional: is caps lock on? Loaded through a Loader (KDE-only module).
import QtQuick
import org.kde.plasma.private.keyboardindicator as KeyboardIndicator

QtObject {
    readonly property bool on: caps.locked
    property KeyboardIndicator.KeyState caps: KeyboardIndicator.KeyState {
        key: Qt.Key_CapsLock
    }
}
