// A little candy pill button.
import QtQuick

Rectangle {
    id: pill
    property real u: 1
    property var pal
    property alias text: label.text
    signal clicked()

    implicitWidth: label.implicitWidth + 36 * u
    implicitHeight: 40 * u
    radius: height / 2
    color: hover.hovered ? pal.pillHover : pal.pill
    border.width: 1.5 * u
    border.color: pal.line
    scale: tap.pressed ? 0.94 : hover.hovered ? 1.06 : 1
    Behavior on scale { NumberAnimation { duration: 220; easing.type: Easing.OutBack } }
    Behavior on color { ColorAnimation { duration: 160 } }

    Text {
        id: label
        anchors.centerIn: parent
        color: pal.text
        font.family: pal.font
        font.weight: Font.ExtraBold
        font.pixelSize: 15 * pill.u
    }
    HoverHandler { id: hover; cursorShape: Qt.PointingHandCursor }
    TapHandler { id: tap; onTapped: pill.clicked() }
}
