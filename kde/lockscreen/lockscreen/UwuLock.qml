/*
    ♡ uwu lock screen ✧

    Context properties provided by kscreenlocker_greet (Plasma 6):
      authenticator           PAM conversation (startAuthenticating, respond, …)
      kscreenlocker_userName  full name (or login name)
      config                  this theme's settings (config.xml)
      wallpaper               the lock screen wallpaper, drawn underneath us

    Layout: on a landscape screen the clock sits on the left and the login card
    on the right; on a tall (rotated) screen they stack top to bottom. After a
    few seconds without input everything but the clock fades away and the bunny
    falls asleep. Typing goes straight into the password field at any time.
*/
import QtQuick

Item {
    id: lock

    // ───────────────────────────── settings ─────────────────────────────
    function setting(name, fallback) {
        try {
            if (typeof config !== "undefined" && config && config[name] !== undefined && config[name] !== null && config[name] !== "")
                return config[name];
        } catch (e) {}
        return fallback;
    }
    readonly property bool day: setting("theme", "night") === "day"
    readonly property bool useWallpaper: setting("useWallpaper", false) === true || setting("useWallpaper", false) === "true"
    readonly property bool showPetals: setting("petals", true) !== false && setting("petals", true) !== "false"
    readonly property int petalCount: Math.max(0, Math.min(120, Number(setting("petalCount", 40))))
    readonly property bool reduceMotion: setting("reduceMotion", false) === true || setting("reduceMotion", false) === "true"

    readonly property string userName: typeof kscreenlocker_userName !== "undefined" && kscreenlocker_userName ? kscreenlocker_userName : "cutie"
    readonly property string firstName: userName.split(" ")[0]

    // ───────────────────────────── sizing ─────────────────────────────
    // one unit ≈ 1px on a 1080p screen; tall (rotated) screens use their width
    readonly property real u: Math.max(0.55, Math.min(2.4, Math.min(width, height) / 1080))
    readonly property bool portrait: height > width
    // the card and bunny grow a bit on tall screens, where there's room to spare
    readonly property real cu: u * (portrait ? 1.3 : 1)

    FontLoader { id: f600; source: "fonts/Nunito-600.ttf" }
    FontLoader { id: f800; source: "fonts/Nunito-800.ttf" }
    FontLoader { id: f900; source: "fonts/Nunito-900.ttf" }

    QtObject {
        id: pal
        readonly property string font: f900.status === FontLoader.Ready ? f900.name : "sans-serif"
        readonly property color pink: lock.day ? "#ff6fb5" : "#ff8fc8"
        readonly property color hot: "#ff5fae"
        readonly property color lav: lock.day ? "#a77bff" : "#c7a2ff"
        readonly property color mint: "#8ff5cf"
        readonly property color text: lock.day ? "#57264c" : "#ffeaf6"
        readonly property color muted: lock.day ? "#9a5f8a" : "#d6a8c8"
        readonly property color card: lock.day ? Qt.rgba(1, 0.97, 0.985, 0.82) : Qt.rgba(0.14, 0.07, 0.17, 0.78)
        readonly property color field: lock.day ? "#ffffff" : "#1d0f24"
        readonly property color line: lock.day ? Qt.rgba(0.91, 0.26, 0.56, 0.35) : Qt.rgba(1, 0.56, 0.78, 0.38)
        readonly property color pill: lock.day ? Qt.rgba(1, 1, 1, 0.6) : Qt.rgba(0.2, 0.1, 0.24, 0.6)
        readonly property color pillHover: lock.day ? Qt.rgba(1, 0.88, 0.94, 0.9) : Qt.rgba(0.32, 0.15, 0.36, 0.85)
        readonly property color bgTop: lock.day ? "#ffe9f3" : "#140a1c"
        readonly property color bgMid: lock.day ? "#ffd6ea" : "#2a1236"
        readonly property color bgBottom: lock.day ? "#f3dcff" : "#3b1840"
    }

    // ───────────────────────────── state ─────────────────────────────
    property bool uiVisible: false
    // 0 = idle (just the clock), 1 = awake (login card); everything moves off this one value
    property real awakeT: uiVisible ? 1 : 0
    Behavior on awakeT { NumberAnimation { duration: 650; easing.type: Easing.OutCubic } }
    function mix(a, b, t) { return a + (b - a) * t; }
    property bool seenMove: false
    property bool unlocking: false
    property bool passwordless: false
    property int fails: 0

    function wake() {
        if (unlocking) return;
        uiVisible = true;
        idleTimer.restart();
    }
    function sleep() {
        if (unlocking || password.text.length > 0) return;
        uiVisible = false;
        bunny.mood = "sleepy";
    }
    onUiVisibleChanged: {
        if (uiVisible) {
            try { Window.window.requestActivate(); } catch (e) {}
            if (bunny.mood === "sleepy") { bunny.mood = "awake"; bunny.hop(); }
        }
        authenticate();
    }

    function authenticate() {
        if (typeof authenticator !== "undefined") authenticator.startAuthenticating();
    }
    function submit() {
        if (unlocking) return;
        if (passwordless) { celebrate(); return; }
        if (password.text.length === 0) { bunny.say("type your password first ♡", 2200); bunny.hop(); return; }
        const pw = password.text;
        if (typeof authenticator === "undefined") return;
        if (authenticator.pamTimeout) {
            pendingPassword = pw;      // newer Plasma: PAM still cooling down after a failure
            return;
        }
        authenticator.respond(pw);
    }
    property string pendingPassword: ""
    readonly property bool authBusy: typeof authenticator !== "undefined" && authenticator !== null && authenticator.busy === true

    function celebrate() {
        unlocking = true;
        uiVisible = true;
        bunny.mood = "love";
        bunny.say(pick(["welcome back! ♡", "yay, it's you! ✧", "missed you ♡", "hiii ♡ (^o^)"]), 2000);
        bunny.hop();
        for (let i = 0; i < 26; i++) heartBurst.createObject(lock, { x0: cardSlot.x + cardSlot.width / 2, y0: cardSlot.y + cardSlot.height / 2, u: lock.u });
        outro.start();
    }
    function pick(list) { return list[Math.floor(Math.random() * list.length)]; }

    Connections {
        target: typeof authenticator !== "undefined" ? authenticator : null
        ignoreUnknownSignals: true
        function onSucceeded() {
            if (authenticator.hadPrompt) {
                lock.celebrate();
            } else {
                // no password needed (e.g. a passwordless account): wait for a click
                lock.passwordless = true;
                lock.wake();
                bunny.mood = "awake";
                bunny.say("no password needed ♡ press enter", 4000);
            }
        }
        function onFailed(kind) {
            if (kind != 0) return;   // fingerprint / smartcard tries report separately
            lock.fails++;
            password.text = "";
            bunny.mood = "sad";
            bunny.shake();
            bunny.say(lock.fails >= 3 ? lock.pick(["deep breaths… you've got this ♡", "caps lock, maybe? (-_-;)", "still not it… (T_T)"])
                                      : lock.pick(["that's not it… (>_<)", "nope! try again ♡", "hmm, wrong password (T_T)"]), 3500);
            shakeCard.restart();
            sadTimer.restart();
            lock.authenticate();
        }
        function onInfoMessageChanged() { if (authenticator.infoMessage) bunny.say(authenticator.infoMessage, 5000); }
        function onErrorMessageChanged() { if (authenticator.errorMessage) bunny.say(authenticator.errorMessage, 5000); }
        function onPromptChanged() { if (authenticator.prompt) bunny.say(authenticator.prompt, 5000); }
        function onPromptForSecretChanged() { password.forceActiveFocus(); }
        function onPamTimeoutChanged() {
            if (!authenticator.pamTimeout && lock.pendingPassword.length > 0) {
                authenticator.respond(lock.pendingPassword);
                lock.pendingPassword = "";
            }
        }
    }

    Timer { id: idleTimer; interval: 12000; onTriggered: lock.sleep() }
    Timer { id: sadTimer; interval: 2600; onTriggered: if (!lock.unlocking) bunny.mood = lock.uiVisible ? "awake" : "sleepy" }
    // keep PAM listening while the prompt is up (same heartbeat as Plasma's own)
    Timer { interval: 1000; running: lock.uiVisible && !lock.unlocking; repeat: true; onTriggered: lock.authenticate() }

    // ───────────────────────────── background ─────────────────────────────
    Rectangle {
        anchors.fill: parent
        visible: !lock.useWallpaper
        gradient: Gradient {
            GradientStop { position: 0; color: pal.bgTop }
            GradientStop { position: 0.55; color: pal.bgMid }
            GradientStop { position: 1; color: pal.bgBottom }
        }
    }
    // the user's wallpaper (drawn by the greeter underneath), softly tinted
    Rectangle {
        anchors.fill: parent
        visible: lock.useWallpaper
        color: lock.day ? Qt.rgba(1, 0.85, 0.93, 0.45) : Qt.rgba(0.12, 0.04, 0.14, 0.5)
    }
    // dreamy colour glows drifting about
    Repeater {
        model: [
            { c: "pink", x: 0.12, y: 0.2, s: 0.75, d: 23000 },
            { c: "lav", x: 0.88, y: 0.8, s: 0.85, d: 29000 },
            { c: "mint", x: 0.8, y: 0.1, s: 0.45, d: 31000 },
            { c: "butter", x: 0.22, y: 0.92, s: 0.42, d: 37000 },
        ]
        Image {
            id: blob
            required property var modelData
            property real wob: 0
            source: `assets/blob-${modelData.c}.png`
            width: Math.max(lock.width, lock.height) * modelData.s
            height: width
            smooth: true
            opacity: lock.day ? 0.5 : 0.28
            x: lock.width * modelData.x - width / 2 + Math.sin(wob * 6.283) * 60 * lock.u
            y: lock.height * modelData.y - height / 2 + Math.cos(wob * 6.283) * 40 * lock.u
            NumberAnimation on wob { from: 0; to: 1; duration: blob.modelData.d; loops: Animation.Infinite; running: !lock.reduceMotion }
        }
    }
    // polka dots
    Image {
        anchors.fill: parent
        source: lock.day ? "assets/dots-day.png" : "assets/dots-night.png"
        fillMode: Image.Tile
        sourceSize.width: Math.round(28 * lock.u)
        sourceSize.height: Math.round(28 * lock.u)
        smooth: true
    }

    // falling sakura (behind the UI), big soft ones drifting a little closer
    Petals {
        anchors.fill: parent
        visible: lock.showPetals && !lock.reduceMotion
        u: lock.u
        count: visible ? lock.petalCount : 0
    }
    Petals {
        anchors.fill: parent
        visible: lock.showPetals && !lock.reduceMotion
        u: lock.u
        soft: true
        count: visible ? Math.max(1, Math.round(lock.petalCount / 10)) : 0
    }

    // ───────────────────────────── input catcher ─────────────────────────────
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: lock.uiVisible ? Qt.ArrowCursor : Qt.BlankCursor
        onPressed: { lock.wake(); password.forceActiveFocus(); }
        onPositionChanged: {
            // the first move event can be synthetic (the window appearing under the pointer)
            if (lock.seenMove) lock.wake();
            lock.seenMove = true;
        }
    }

    // ───────────────────────────── the clock ─────────────────────────────
    Item {
        id: hero
        width: clockRow.width
        height: clockCol.height
        property real cx: lock.mix(lock.width / 2, lock.portrait ? lock.width / 2 : lock.width * 0.3, lock.awakeT)
        property real cy: lock.mix(lock.height * (lock.portrait ? 0.38 : 0.46), lock.height * (lock.portrait ? 0.23 : 0.5), lock.awakeT)
        x: cx - width / 2
        y: cy - height / 2
        scale: lock.mix(1.12, 1, lock.awakeT)

        property date now: new Date()
        Timer { interval: 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: hero.now = new Date() }
        readonly property string time: Qt.formatTime(now, Qt.locale().timeFormat(Locale.ShortFormat).replace(/[.:]ss/, ""))

        Column {
            id: clockCol
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 4 * lock.u

            Item {
                id: clockRow
                anchors.horizontalCenter: parent.horizontalCenter
                width: clock.implicitWidth
                height: clock.implicitHeight * 0.86
                // soft pink glow under the digits
                Text {
                    x: 0; y: 6 * lock.u
                    text: clock.text
                    font: clock.font
                    color: pal.pink
                    opacity: 0.35
                }
                Text {
                    id: clock
                    text: hero.time
                    color: pal.text
                    font.family: pal.font
                    font.weight: Font.Black
                    font.pixelSize: (lock.portrait ? 200 : 170) * lock.u
                    font.letterSpacing: 2 * lock.u
                }
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "✿ " + Qt.formatDate(hero.now, "dddd, d MMMM") + " ✿"
                color: pal.muted
                font.family: pal.font
                font.weight: Font.ExtraBold
                font.pixelSize: (lock.portrait ? 30 : 26) * lock.u
            }
        }
    }

    // ───────────────────────────── the login card ─────────────────────────────
    Item {
        id: cardSlot
        width: 440 * lock.cu
        height: card.height
        x: (lock.portrait ? lock.width / 2 : lock.width * 0.7) - width / 2
        y: (lock.portrait ? lock.height * 0.57 : lock.height * 0.54) - height / 2 + (1 - lock.awakeT) * 50 * lock.cu
        opacity: lock.awakeT
        visible: opacity > 0.01

        property real shake: 0
        SequentialAnimation {
            id: shakeCard
            NumberAnimation { target: cardSlot; property: "shake"; to: -18; duration: 60 }
            NumberAnimation { target: cardSlot; property: "shake"; to: 16; duration: 80 }
            NumberAnimation { target: cardSlot; property: "shake"; to: -10; duration: 80 }
            NumberAnimation { target: cardSlot; property: "shake"; to: 6; duration: 70 }
            NumberAnimation { target: cardSlot; property: "shake"; to: 0; duration: 60 }
        }

        Rectangle {
            id: card
            x: cardSlot.shake * lock.cu
            width: parent.width
            height: cardCol.height + 70 * lock.cu + 40 * lock.cu
            radius: 34 * lock.cu
            color: pal.card
            border.width: 2 * lock.cu
            border.color: pal.line

            // a soft glow halo behind the card
            Rectangle {
                z: -1
                anchors.fill: parent
                anchors.margins: -10 * lock.cu
                radius: parent.radius + 10 * lock.cu
                color: "transparent"
                border.width: 10 * lock.cu
                border.color: Qt.alpha(pal.pink, lock.day ? 0.16 : 0.12)
            }

            Column {
                id: cardCol
                anchors.horizontalCenter: parent.horizontalCenter
                y: 70 * lock.cu
                width: parent.width - 64 * lock.cu
                spacing: 14 * lock.cu

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: lock.userName
                    color: pal.text
                    font.family: pal.font
                    font.weight: Font.Black
                    font.pixelSize: 32 * lock.cu
                    elide: Text.ElideRight
                    width: Math.min(implicitWidth, parent.width)
                    horizontalAlignment: Text.AlignHCenter
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: {
                        const h = hero.now.getHours();
                        const part = h < 5 ? "it's late, sleepyhead" : h < 12 ? "good morning" : h < 18 ? "good afternoon" : "good evening";
                        return part + " ♡ welcome back";
                    }
                    color: pal.muted
                    font.family: pal.font
                    font.weight: Font.Bold
                    font.pixelSize: 16 * lock.cu
                }

                Item { width: 1; height: 4 * lock.cu }

                // password pill
                Rectangle {
                    id: field
                    width: parent.width
                    height: 60 * lock.cu
                    radius: height / 2
                    color: pal.field
                    border.width: 2.5 * lock.cu
                    border.color: bunny.mood === "sad" ? pal.hot : password.activeFocus ? pal.pink : pal.line
                    Behavior on border.color { ColorAnimation { duration: 200 } }

                    Text {
                        id: lockIcon
                        anchors.verticalCenter: parent.verticalCenter
                        x: 22 * lock.cu
                        text: lock.passwordless ? "♡" : "✿"
                        color: pal.pink
                        font.family: pal.font
                        font.weight: Font.Black
                        font.pixelSize: 22 * lock.cu
                        RotationAnimation on rotation { from: 0; to: 360; duration: 9000; loops: Animation.Infinite; running: !lock.reduceMotion }
                    }

                    TextInput {
                        id: password
                        anchors.left: lockIcon.right
                        anchors.leftMargin: 12 * lock.cu
                        anchors.right: go.left
                        anchors.rightMargin: 10 * lock.cu
                        anchors.verticalCenter: parent.verticalCenter
                        focus: true
                        clip: true
                        echoMode: TextInput.Password
                        passwordCharacter: "♥"
                        passwordMaskDelay: 0
                        color: pal.pink
                        selectionColor: pal.lav
                        font.family: pal.font
                        font.weight: Font.Black
                        font.pixelSize: 24 * lock.cu
                        font.letterSpacing: 3 * lock.cu
                        // read-only (not disabled) while PAM checks, so focus never gets lost
                        readOnly: lock.unlocking || lock.authBusy
                        inputMethodHints: Qt.ImhSensitiveData | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
                        onAccepted: lock.submit()
                        Keys.onEscapePressed: { text = ""; lock.uiVisible = false; bunny.mood = "sleepy"; }
                        property int lastLength: 0
                        onTextChanged: {
                            if (text.length > 0) lock.wake();
                            if (text.length > lastLength && cursorRectangle) {
                                const p = mapToItem(lock, cursorRectangle.x, cursorRectangle.y);
                                heartPop.createObject(lock, { x0: p.x, y0: p.y, u: lock.cu, color: lock.pick([pal.pink, pal.lav, pal.hot, "#ffe59a"]) });
                                if (bunny.mood !== "love") bunny.mood = "awake";
                            }
                            lastLength = text.length;
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            visible: password.text.length === 0
                            text: lock.passwordless ? "press enter to come in ♡" : "password ♡"
                            color: pal.muted
                            opacity: 0.75
                            font.family: pal.font
                            font.weight: Font.Bold
                            font.pixelSize: 18 * lock.cu
                        }
                    }

                    // round unlock button
                    Rectangle {
                        id: go
                        anchors.right: parent.right
                        anchors.rightMargin: 7 * lock.cu
                        anchors.verticalCenter: parent.verticalCenter
                        width: 46 * lock.cu
                        height: width
                        radius: width / 2
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0; color: pal.pink }
                            GradientStop { position: 1; color: pal.lav }
                        }
                        scale: goTap.pressed ? 0.88 : goHover.hovered ? 1.1 : 1
                        Behavior on scale { NumberAnimation { duration: 220; easing.type: Easing.OutBack } }
                        Text {
                            anchors.centerIn: parent
                            anchors.horizontalCenterOffset: 1 * lock.cu
                            text: lock.authBusy || lock.unlocking ? "♥" : "➜"
                            color: "#2a0c22"
                            font.family: pal.font
                            font.weight: Font.Black
                            font.pixelSize: 20 * lock.cu
                            SequentialAnimation on scale {
                                running: lock.authBusy || lock.unlocking
                                loops: Animation.Infinite
                                NumberAnimation { to: 1.3; duration: 260 }
                                NumberAnimation { to: 1; duration: 260 }
                            }
                        }
                        HoverHandler { id: goHover; cursorShape: Qt.PointingHandCursor }
                        TapHandler { id: goTap; onTapped: { lock.submit(); password.forceActiveFocus(); } }
                    }
                }

                // caps lock (KDE-only module, loaded if available)
                Loader {
                    id: capsLoader
                    source: "CapsLock.qml"
                    active: typeof authenticator !== "undefined"
                }
                Text {
                    // fixed size, so the card doesn't jump when a message appears
                    width: parent.width
                    height: 20 * lock.cu
                    horizontalAlignment: Text.AlignHCenter
                    text: capsLoader.item && capsLoader.item.on ? "⇪ caps lock is on" : lock.fails > 0 && !lock.unlocking ? "tries: " + "♡".repeat(Math.min(lock.fails, 8)) : ""
                    color: capsLoader.item && capsLoader.item.on ? pal.hot : pal.muted
                    font.family: pal.font
                    font.weight: Font.ExtraBold
                    font.pixelSize: 14 * lock.cu
                }
            }
        }
    }

    // ───────────────────────────── bunny ─────────────────────────────
    Bunny {
        id: bunny
        u: lock.cu
        pal: pal
        // sits on top of the card while awake; naps above the clock while idle
        // naps above the clock while idle, sits on the card while awake
        x: lock.mix(hero.cx - width / 2, cardSlot.x + card.x + cardSlot.width / 2 - width / 2, lock.awakeT)
        y: lock.mix(hero.y - height - 10 * lock.cu, cardSlot.y - height * 0.55, lock.awakeT)
    }

    // ───────────────────────────── bottom bar ─────────────────────────────
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 34 * lock.u
        spacing: 14 * lock.u
        opacity: lock.uiVisible && !lock.unlocking ? 1 : 0
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 400 } }

        Loader {
            source: "Sessions.qml"
            active: typeof authenticator !== "undefined"
            onLoaded: { item.u = Qt.binding(() => lock.u); item.pal = pal; }
        }
    }
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 34 * lock.u
        visible: !lock.uiVisible
        opacity: 0.7
        text: "type to unlock ♡"
        color: pal.muted
        font.family: pal.font
        font.weight: Font.ExtraBold
        font.pixelSize: 17 * lock.u
        SequentialAnimation on opacity {
            loops: Animation.Infinite
            running: !lock.uiVisible && !lock.reduceMotion
            NumberAnimation { to: 0.25; duration: 1600; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.7; duration: 1600; easing.type: Easing.InOutSine }
        }
    }

    // ───────────────────────────── little effects ─────────────────────────────
    Component {
        id: heartPop
        Text {
            id: hp
            property real x0: 0
            property real y0: 0
            property real u: 1
            property real k
            property real dx: (Math.random() - 0.5) * 50
            x: x0 + dx * k * u
            y: y0 - 50 * k * u
            text: Math.random() < 0.5 ? "♥" : "✧"
            font.family: pal.font
            font.weight: Font.Black
            font.pixelSize: (14 + Math.random() * 10) * u
            opacity: 1 - k
            NumberAnimation on k { from: 0; to: 1; duration: 700; easing.type: Easing.OutCubic; onFinished: hp.destroy() }
        }
    }
    Component {
        id: heartBurst
        Text {
            id: hb
            property real x0: 0
            property real y0: 0
            property real u: 1
            property real k
            property real ang: Math.random() * 6.283
            property real dist: (140 + Math.random() * 260)
            x: x0 + Math.cos(ang) * dist * k * u
            y: y0 + Math.sin(ang) * dist * k * u - 60 * k * u
            text: ["♥", "♡", "✧", "✿"][Math.floor(Math.random() * 4)]
            color: [pal.pink, pal.lav, pal.hot, "#ffe59a", pal.mint][Math.floor(Math.random() * 5)]
            font.family: pal.font
            font.weight: Font.Black
            font.pixelSize: (18 + Math.random() * 22) * u
            opacity: 1 - k * k
            rotation: k * 180
            NumberAnimation on k { from: 0; to: 1; duration: 900; easing.type: Easing.OutCubic; onFinished: hb.destroy() }
        }
    }

    // fade to the desktop, then let the greeter quit
    SequentialAnimation {
        id: outro
        PauseAnimation { duration: 450 }
        ParallelAnimation {
            NumberAnimation { target: cardSlot; property: "scale"; to: 1.06; duration: 260; easing.type: Easing.InCubic }
            NumberAnimation { target: lock; property: "opacity"; to: 0; duration: 260 }
        }
        ScriptAction { script: Qt.quit() }
    }

    Keys.onPressed: event => { lock.wake(); event.accepted = false; }

    Component.onCompleted: {
        password.forceActiveFocus();
        authenticate();
    }
}
