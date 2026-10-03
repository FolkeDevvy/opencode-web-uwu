// Optional: sleep / hibernate / switch user. Loaded through a Loader, so if
// this Plasma module is ever missing the lock screen still works.
import QtQuick
import org.kde.plasma.private.sessions

Row {
    id: sessions
    property real u: 1
    property var pal
    spacing: 14 * u

    SessionManagement {
        id: sm
    }

    Repeater {
        model: [
            { label: "☾  sleep", show: sm.canSuspend, act: () => sm.suspend() },
            { label: "❄  hibernate", show: sm.canHibernate, act: () => sm.hibernate() },
            { label: "⇄  switch user", show: sm.canSwitchUser, act: () => sm.switchUser() },
        ]
        delegate: Pill {
            required property var modelData
            u: sessions.u
            pal: sessions.pal
            text: modelData.label
            visible: modelData.show
            onClicked: modelData.act()
        }
    }
}
