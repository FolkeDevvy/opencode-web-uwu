// The sakura layer: a crowd of petals plus wind gusts that come and go.
import QtQuick

Item {
    id: petals
    property real u: 1
    property int count: 40
    property bool soft: false
    property real wind          // wind speed, px per second
    property real push: 0       // how far the wind has blown, so far

    FrameAnimation {
        running: true
        onTriggered: petals.push += petals.wind * frameTime
    }

    // calm → gust → calm, on a slow irregular loop
    SequentialAnimation on wind {
        loops: Animation.Infinite
        NumberAnimation { to: 0; duration: 5000 }
        NumberAnimation { to: 70 * petals.u; duration: 4200; easing.type: Easing.InOutSine }
        NumberAnimation { to: 25 * petals.u; duration: 3000; easing.type: Easing.InOutSine }
        NumberAnimation { to: 110 * petals.u; duration: 3800; easing.type: Easing.InOutSine }
        NumberAnimation { to: 0; duration: 7000; easing.type: Easing.InOutSine }
    }

    Repeater {
        model: petals.count
        Petal {
            areaW: petals.width
            areaH: petals.height
            u: petals.u
            soft: petals.soft
            push: petals.push
        }
    }
}
