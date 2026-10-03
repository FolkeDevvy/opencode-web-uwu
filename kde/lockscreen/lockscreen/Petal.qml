// One sakura petal: falls across the screen, swaying and tumbling, pushed
// sideways by the shared wind. When it leaves the screen it picks a fresh
// random path and falls again.
import QtQuick

Image {
    id: petal
    property real areaW: 1920
    property real areaH: 1080
    property real u: 1
    property real push: 0          // shared wind: how far gusts have blown things so far
    property real pushStart: 0
    property bool soft: false      // big blurry "bokeh" petal in front
    property bool first: true

    property real t: 0             // 0 → 1 over one fall
    property real x0: 0
    property real drift: 0         // how far it travels sideways in one fall
    property real swayAmp: 0
    property real swayFreq: 1
    property real phase: 0
    property real spin: 0
    property real flipFreq: 1
    property real depth: 1         // farther petals are smaller, slower, fainter

    width: (soft ? 150 : 26) * u * depth
    height: width
    sourceSize.width: soft ? 168 : 48
    sourceSize.height: soft ? 168 : 48
    smooth: true
    mipmap: !soft
    opacity: (soft ? 0.5 : 0.45 + 0.5 * depth) * Math.min(1, t * 12, (1 - t) * 12)

    x: x0 + drift * t + (push - pushStart) * depth + Math.sin(t * 6.283 * swayFreq + phase) * swayAmp - width / 2
    y: -height + t * (areaH + 2 * height)
    rotation: spin * t * 360 + phase * 57
    transform: Scale {
        origin.x: petal.width / 2
        xScale: 0.35 + 0.65 * Math.abs(Math.cos(petal.t * 6.283 * petal.flipFreq + petal.phase))
    }

    function reseed() {
        const r = Math.random;
        depth = soft ? 0.8 + r() * 0.6 : 0.45 + r() * 0.55;
        source = soft ? `assets/petal-blur-${Math.floor(r() * 3)}.png` : `assets/petal-${Math.floor(r() * 4)}.png`;
        // the wind blows left → right, so start some petals off the left edge
        x0 = -areaW * 0.25 + r() * areaW * 1.1;
        drift = (120 + r() * 260) * u;
        swayAmp = (16 + r() * 40) * u * depth;
        swayFreq = 0.6 + r() * 1.4;
        phase = r() * 6.283;
        spin = (r() < 0.5 ? -1 : 1) * (0.3 + r() * 1.2);
        flipFreq = 0.5 + r() * 2;
        fall.duration = (soft ? 16000 : 11000 + r() * 9000) / (0.6 + depth * 0.5) * Math.max(0.7, areaH / 1080 / Math.max(u, 0.55) * 0.9);
        // on the very first fall, start part-way so the screen isn't empty
        fall.from = first ? r() : 0;
        pushStart = push;
        first = false;
    }

    NumberAnimation on t {
        id: fall
        to: 1
        running: false
        onFinished: { petal.reseed(); fall.start(); }
    }

    // wait until the layer has a size, or every petal would start at x = 0
    property bool started: false
    function begin() {
        if (started || areaW <= 0 || areaH <= 0) return;
        started = true;
        reseed();
        fall.start();
    }
    onAreaWChanged: begin()
    onAreaHChanged: begin()
    Component.onCompleted: begin()
}
