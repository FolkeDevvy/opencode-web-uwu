/*
    ♡ uwu lock screen ✧ entry point loaded by kscreenlocker_greet.

    Keeps the same root API as Plasma's own lock screen, and only imports
    plain QtQuick so it loads on every Plasma 6 release. KDE-only extras
    (sleep / switch user, caps lock) live in their own files and load through
    Loaders, so a missing module can never stop you from unlocking.
*/
import QtQuick

Item {
    id: root
    property bool debug: false
    property string notification
    signal clearPassword()
    signal notificationRepeated()

    // kscreenlocker looks for this one
    property bool viewVisible: false

    implicitWidth: 1280
    implicitHeight: 800

    UwuLock {
        anchors.fill: parent
    }
}
