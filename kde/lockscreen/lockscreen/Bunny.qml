// The mochi bunny: sleeps while the screen is idle, perks up when you type,
// pouts at a wrong password and goes heart-eyed when you get in.
import QtQuick

Item {
    id: bunny
    property real u: 1
    property var pal
    property string mood: "sleepy"   // sleepy | awake | sad | love
    property string message: ""

    width: 130 * u
    height: 130 * u

    function say(text, ms) {
        message = text;
        bubbleTimer.interval = ms || 3800;
        bubbleTimer.restart();
    }
    function hop() { hopAnim.restart(); }
    function shake() { shakeAnim.restart(); }

    Item {
        id: body
        anchors.fill: parent

        // a gentle bob, slower and lower while asleep
        property real bob
        SequentialAnimation on bob {
            loops: Animation.Infinite
            NumberAnimation { to: 1; duration: bunny.mood === "sleepy" ? 2400 : 1400; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0; duration: bunny.mood === "sleepy" ? 2400 : 1400; easing.type: Easing.InOutSine }
        }
        property real jump: 0
        property real tilt: 0

        transform: [
            Translate { y: -body.bob * 6 * bunny.u - body.jump * 26 * bunny.u },
            Rotation { origin.x: body.width / 2; origin.y: body.height; angle: body.tilt },
            Scale {
                origin.x: body.width / 2; origin.y: body.height
                // breathe while asleep
                yScale: bunny.mood === "sleepy" ? 1 - body.bob * 0.035 : 1
            }
        ]

        Repeater {
            model: ["sleepy", "awake", "sad", "love"]
            Image {
                required property string modelData
                anchors.fill: parent
                source: `assets/bunny-${modelData}.svg`
                sourceSize.width: 256
                sourceSize.height: 256
                smooth: true
                opacity: bunny.mood === modelData ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: 180 } }
            }
        }
    }

    SequentialAnimation {
        id: hopAnim
        NumberAnimation { target: body; property: "jump"; to: 1; duration: 220; easing.type: Easing.OutQuad }
        NumberAnimation { target: body; property: "jump"; to: 0; duration: 380; easing.type: Easing.OutBounce }
    }
    SequentialAnimation {
        id: shakeAnim
        loops: 2
        NumberAnimation { target: body; property: "tilt"; to: -9; duration: 90 }
        NumberAnimation { target: body; property: "tilt"; to: 9; duration: 140 }
        NumberAnimation { target: body; property: "tilt"; to: 0; duration: 90 }
    }

    // speech bubble, to the right of the bunny
    Rectangle {
        id: bubble
        anchors.left: parent.right
        anchors.leftMargin: 4 * bunny.u
        anchors.top: parent.top
        anchors.topMargin: 6 * bunny.u
        width: Math.min(bubbleText.implicitWidth + 30 * bunny.u, 300 * bunny.u)
        height: bubbleText.implicitHeight + 18 * bunny.u
        radius: 18 * bunny.u
        topLeftRadius: 4 * bunny.u
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0; color: bunny.pal.pink }
            GradientStop { position: 1; color: bunny.pal.lav }
        }
        opacity: bunny.message !== "" ? 1 : 0
        scale: bunny.message !== "" ? 1 : 0.8
        transformOrigin: Item.TopLeft
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 220 } }
        Behavior on scale { NumberAnimation { duration: 320; easing.type: Easing.OutBack } }

        Text {
            id: bubbleText
            anchors.centerIn: parent
            width: Math.min(implicitWidth, 270 * bunny.u)
            text: bunny.message
            wrapMode: Text.Wrap
            color: "#2a0c22"
            font.family: bunny.pal.font
            font.weight: Font.ExtraBold
            font.pixelSize: 15 * bunny.u
        }
    }
    Timer {
        id: bubbleTimer
        onTriggered: bunny.message = ""
    }
}
