// ♡ uwu lock screen settings page (System Settings → Screen Locking → Appearance)
import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: form
    twinFormLayouts: typeof parentLayout !== "undefined" ? parentLayout : []

    property string cfg_theme
    property alias cfg_useWallpaper: useWallpaper.checked
    property alias cfg_petals: petals.checked
    property alias cfg_petalCount: petalCount.value
    property alias cfg_reduceMotion: reduceMotion.checked

    QQC2.RadioButton {
        Kirigami.FormData.label: "Colours:"
        text: "🌙 strawberry-milk night"
        checked: form.cfg_theme !== "day"
        onToggled: form.cfg_theme = "night"
    }
    QQC2.RadioButton {
        text: "🌸 sakura cream day"
        checked: form.cfg_theme === "day"
        onToggled: form.cfg_theme = "day"
    }
    QQC2.CheckBox {
        id: useWallpaper
        Kirigami.FormData.label: "Background:"
        text: "Show the wallpaper under a pastel tint"
    }
    QQC2.CheckBox {
        id: petals
        Kirigami.FormData.label: "Sakura:"
        text: "Falling petals"
    }
    QQC2.SpinBox {
        id: petalCount
        Kirigami.FormData.label: "How many:"
        enabled: petals.checked
        from: 0
        to: 120
        stepSize: 5
    }
    QQC2.CheckBox {
        id: reduceMotion
        Kirigami.FormData.label: "Motion:"
        text: "Calm mode (no petals or drifting)"
    }
}
