/*
    ♡ uwu splash screen: the bunny hops while Plasma starts.
    ksplashqml sets `stage` from 1 to 6 as startup progresses.
    Only plain QtQuick, so it loads on any Plasma 6.
*/
import QtQuick

Rectangle {
    id: root
    property int stage
    readonly property real u: Math.min(width, height) / 1080

    gradient: Gradient {
        GradientStop { position: 0; color: "#ffeaf4" }
        GradientStop { position: 0.55; color: "#ffd9ec" }
        GradientStop { position: 1; color: "#eedcff" }
    }

    FontLoader { id: nunito; source: "fonts/Nunito-900.ttf" }

    // drifting petals
    Repeater {
        model: 26
        Image {
            id: petal
            property real start: Math.random()
            property real t: start
            property real x0: Math.random() * root.width * 1.1 - root.width * 0.1
            property real sway: (20 + Math.random() * 40) * root.u
            property real phase: Math.random() * 6.28
            source: "images/petal-" + (index % 4) + ".png"
            width: (14 + Math.random() * 16) * root.u
            height: width
            opacity: 0.75 * Math.min(1, t * 10, (1 - t) * 10)
            x: x0 + t * 160 * root.u + Math.sin(t * 9 + phase) * sway
            y: -height + t * (root.height + 2 * height)
            rotation: t * 540 + phase * 50
            NumberAnimation on t {
                id: fall
                from: petal.start
                to: 1
                duration: (1 - petal.start) * 9000 + 1
                onFinished: { petal.start = 0; petal.x0 = Math.random() * root.width; fall.duration = 9000; fall.restart(); }
            }
        }
    }

    Item {
        id: content
        anchors.centerIn: parent
        width: 360 * root.u
        height: 330 * root.u
        opacity: 0
        Component.onCompleted: fadeIn.start()
        NumberAnimation on opacity { id: fadeIn; running: false; to: 1; duration: 600 }

        // the bunny, hopping
        Image {
            id: bunny
            source: root.stage >= 6 ? "images/bunny-love.svg" : "images/bunny-awake.svg"
            sourceSize.width: 256
            sourceSize.height: 256
            width: 170 * root.u
            height: width
            anchors.horizontalCenter: parent.horizontalCenter
            property real hop: 0
            y: 40 * root.u - hop * 34 * root.u
            SequentialAnimation on hop {
                loops: Animation.Infinite
                NumberAnimation { to: 1; duration: 320; easing.type: Easing.OutQuad }
                NumberAnimation { to: 0; duration: 420; easing.type: Easing.OutBounce }
                PauseAnimation { duration: 260 }
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 235 * root.u
            text: root.stage >= 6 ? "welcome back ♡" : "getting cozy…"
            color: "#57264c"
            font.family: nunito.status === FontLoader.Ready ? nunito.name : "sans-serif"
            font.weight: Font.Black
            font.pixelSize: 30 * root.u
        }

        // hearts fill up as Plasma starts
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 290 * root.u
            spacing: 10 * root.u
            Repeater {
                model: 6
                Text {
                    text: index < root.stage ? "♥" : "♡"
                    color: index < root.stage ? "#ff5fae" : "#c78fb0"
                    font.pixelSize: 26 * root.u
                    scale: index === root.stage - 1 ? 1.25 : 1
                    Behavior on scale { NumberAnimation { duration: 300; easing.type: Easing.OutBack } }
                }
            }
        }
    }

    onStageChanged: if (stage >= 6) outro.start()
    NumberAnimation { id: outro; target: content; property: "scale"; to: 1.08; duration: 400; easing.type: Easing.OutBack }
}
