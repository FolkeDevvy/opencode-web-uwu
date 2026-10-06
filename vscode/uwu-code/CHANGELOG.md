# Changelog

## 0.4.1

- **Kawaii Workbench is much lighter.** The little looping animations (the floating mascot,
  heartbeats, hops and wiggles) now play a few times and then rest, instead of running forever
  and keeping VS Code busy redrawing. Idle CPU dropped from about 100% to about 16% (software
  rendering).
- The Workbench no longer sets the animated `"expand"` cursor, and switches it back to normal on
  installs where it set it before (only if you haven't changed it since).
- Calm mode (Reduce Motion) uses cheaper selectors, which also helps scrolling.
- **Tab labels are centred again.** With VS Code's classic tab layout, the text sat low in its
  pill, the file icon was clipped, and the ✕ sat high.

## 0.4.0

- **The falling sakura petals are gone,** from both the editor and the Kawaii Workbench window.
  They were more distracting than cute. The *Toggle Sakura Petals* command and the
  `uwu.petals.*` settings are removed; leftover settings are ignored.
- Clicking the status-bar mascot now gives you a sparkle burst.
- After an uwu-code update, you're offered to re-apply the Kawaii Workbench, so VS Code picks up
  the new look (here: the window without petals).

## 0.3.0

- **Much lighter petals.** They're now still pictures on one layer that slides with a GPU
  transform, instead of hundreds of self-animating SVG petals. Idle CPU dropped from about 270%
  to about 14% (software rendering).
- Editor petals move when the Kawaii Workbench is on and stay still without it. The new
  `uwu.petals.style: "classic"` setting brings back the old self-animating petals.
- Petal re-positioning while scrolling now happens only near the edge of the petal layer.
- Kawaii Workbench: the window petals use the same light layer. The title-bar shimmer runs only on
  hover, and the command palette border no longer spins.
- Kawaii Workbench: VS Code's *Reduce Motion* setting now acts as a calm mode that stops every
  animation.

## 0.2.1

- Kawaii Workbench: the activity-bar dock is now a clean floating pill. VS Code's own frame behind
  it is gone, there's a gap before the side bar, and the active icon bubble fits inside the pill.

## 0.2.0

- **Kawaii Workbench** (opt-in: `uwu: Enable Kawaii Workbench`) turns VS Code into uwu IDE:
  - a boot splash, floating candy panels, window-wide petals and the Nunito UI font
  - custom-drawn activity icons, candy-pill tabs, ♡/♥ tree arrows and a branded title bar
  - a command palette with a rainbow border, and bow/paw stickers
  - click heart bursts, typing sparkles, save confetti, and a floating mascot with tips
- Backups, checksum fix, a sudo fallback for system installs, an offer to re-apply after VS Code
  updates, and `uwu: Disable Kawaii Workbench` to undo it all
- New **uwu cuties** file icon theme
- `uwu.workbench.*` settings for each Kawaii Workbench effect

## 0.1.1

- Petals no longer jump or flicker while scrolling. They're now attached to the document like
  wallpaper, so they scroll smoothly with your code.
- Petals stay out of your code by default: they're invisible over the first ~24 text columns and
  fade in towards the right (`uwu.petals.area`, set it to `everywhere` for the old look).
- Default petal opacity is now 0.7, and the light-theme boost is smaller.

## 0.1.0

- First release ✧
- uwu strawberry-milk night and uwu sakura cream day colour themes
- Sakura petals behind the code, sparkle burst on save, gutter hearts, error kaomoji, and a
  status-bar mascot
