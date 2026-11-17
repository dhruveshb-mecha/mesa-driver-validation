"""Per-application workflows (what a user does in each app). cmd = what a user would launch; kill = anchored patterns that clean
single-instance apps before/after a run; phases = (name, [actions], seconds).
Actions: tap x y | dtap x y | move x y | scroll dy [x y] | type text [MODS] | wait s.   x,y = logical px of the 540x620 panel."""
D = "{DATA}"      # replaced by app_drive.py with a fresh per-run copy of ~/appbench-data (no remembered file positions)
def rep(actions, n): return list(actions) * n
def sc(dy, n, gap=.3, x=270, y=400): return rep([("scroll", dy, x, y), ("wait", gap)], n)
PROFILES = {"gtk4": {
    # --- viewers / file manager: GL-rendered content (images, thumbnails, PDF pages) ---
    "loupe": dict(schemas="Loupe", focus=(250, 72), cmd=["/usr/bin/loupe", f"{D}/images/photo1.jpg"], kill=["^/usr/bin/loupe"], phases=[
        ("fit-6000x4000-jpeg-idle", [], 3),
        ("zoom-in-keys", rep([("type", "+"), ("wait", .45)], 10), 6),
        ("zoom-out-keys", rep([("type", "-"), ("wait", .45)], 10), 6)]),
    "nautilus": dict(schemas="nautilus", cmd=["/usr/bin/nautilus", "--new-window", f"{D}/files"], kill=["^/usr/bin/nautilus"], phases=[
        ("folder-grid-idle", [], 3),
        ("open-folder-with-image-thumbnails", [("dtap", 100, 115), ("wait", 4)], 6),
        ("scroll-thumbnails-down", sc(10, 14, .3, 270, 300), 6),
        ("scroll-thumbnails-up", sc(-10, 14, .3, 270, 300), 6),
        ("switch-to-list-view", [("tap", 492, 595), ("wait", 1), ("tap", 492, 530)], 4)]),
    "text-editor": dict(schemas="TextEditor", cmd=["/usr/bin/gnome-text-editor", f"{D}/long.txt"], kill=["^/usr/bin/gnome-text-editor"], phases=[
        ("open-30000-line-file-idle", [], 3),
        ("scroll-down-fast", sc(25, 20, .25, 270, 400), 7),
        ("scroll-up-fast", sc(-25, 20, .25, 270, 400), 7),
        ("type-text", [("tap", 270, 400)] + rep([("type", "hello gpu test "), ("wait", .3)], 8), 5)]),
    "papers": dict(schemas="Papers", focus=(270, 72), cmd=["/usr/bin/papers", f"{D}/doc.pdf"], kill=["^/usr/bin/papers"], phases=[
        ("open-60-page-pdf-idle", [], 3),
        ("page-down-keys", rep([("type", " "), ("wait", .4)], 15), 7),
        ("zoom-in-button", [("tap", 500, 525), ("wait", .8), ("tap", 500, 525), ("wait", .8), ("tap", 500, 525)], 4),
        ("scroll-zoomed-pages", sc(15, 20, .25, 270, 400), 7),
        ("zoom-out-button", [("tap", 500, 575), ("wait", .8), ("tap", 500, 575), ("wait", .8), ("tap", 500, 575)], 4)]),
    # --- map (vector/raster tiles from the network: fps depends on tile arrival too) ---
    "maps": dict(schemas="Maps", cmd=["/usr/bin/gnome-maps"], kill=["^/usr/bin/gnome-maps"], startup=10, phases=[
        ("world-map-idle", [], 3),
        ("select-country-globe-view", [("dtap", 345, 306), ("wait", 1.6), ("dtap", 345, 306)], 8),
        ("idle-country-view", [], 4)]),
    # --- web engine (WebKitGTK 6, GPU compositing): local page with CSS animation + canvas2D + WebGL2 ---
    "epiphany": dict(schemas="epiphany|Epiphany", cmd=["/usr/bin/epiphany", "--incognito-mode", "file://{DATA}/page.html"],
                     kill=["^/usr/bin/epiphany", "WebKitWebProcess", "WebKitNetworkProcess", "WebKitGPUProcess"], startup=12, phases=[
        ("css-canvas-webgl-page", [], 8),
        ("scroll-page", sc(8, 10, .3, 270, 300), 5)]),
    # --- small libadwaita apps: widgets, lists, popovers, text input ---
    "calculator": dict(schemas="Calculator", cmd=["/usr/bin/gnome-calculator"], kill=["^/usr/bin/gnome-calculator"], phases=[
        ("startup-idle", [], 3),
        ("type-expression", [("type", "12345679*9="), ("wait", 1)], 4),
        ("open-mode-popover", [("tap", 267, 72), ("wait", 1.5)], 3)]),
    "characters": dict(schemas="Characters", focus=(340, 72), cmd=["/usr/bin/gnome-characters"], kill=["^/usr/bin/gjs-console /usr/bin/gnome-characters", "^/usr/bin/gnome-characters"], phases=[
        ("emoji-grid-idle", [], 3),
        ("switch-emoji-categories", [x for y in (252, 297, 340, 384, 429, 472, 516, 561) for x in (("tap", 96, y), ("wait", 1.2))], 11),
        ("search-heart", [("tap", 24, 24), ("wait", .6), ("type", "heart"), ("wait", 1.5)], 4)]),
    "clocks": dict(schemas="clocks", cmd=["/usr/bin/gnome-clocks"], kill=["^/usr/bin/gnome-clocks"], phases=[
        ("world-clocks-idle", [], 3),
        ("stopwatch-tab", [("tap", 320, 586)], 3),
        ("stopwatch-start", [("tap", 270, 420), ("wait", 4)], 6)]),
    "font-viewer": dict(schemas="FontViewer|font-viewer", cmd=["/usr/bin/gnome-font-viewer"], kill=["^/usr/bin/gnome-font-viewer"], phases=[
        ("font-list-idle", [], 3),
        ("scroll-font-list", sc(12, 20, .25, 270, 400), 7),
        ("search-sans", [("tap", 270, 60), ("wait", .5), ("type", "sans"), ("wait", 1.5)], 4)]),
}, "flutter": {
    # Flutter Linux apps use the GTK3 embedder (Impeller GLES). mode gles = GDK_GL=gles (needed), default = control without it.
    "localsend": dict(cmd=["/home/mecha/flutter-apps/localsend/localsend_app"], ld="/home/mecha/flutter-apps/ld-ayatana",
                      kill=["flutter-apps/localsend/localsend_app"], phases=[
        ("receive-screen-animated-radar", [], 6),
        ("tab-switch-send", [("tap", 270, 594)], 4),
        ("tab-switch-settings", [("tap", 449, 594)], 4),
        ("settings-scroll", sc(12, 6, .4) + sc(-12, 6, .4), 6),
        ("tab-switch-receive", [("tap", 91, 594)], 4)]),
    "ente-auth": dict(cmd=["/home/mecha/flutter-apps/ente_auth/enteauth"], ld="/home/mecha/flutter-apps/ente_auth/lib",
                      kill=["flutter-apps/ente_auth/enteauth"], phases=[
        ("onboarding-carousel", [], 8),
        ("route-to-log-in-page", [("tap", 390, 590)], 5),
        ("type-email-in-field", [("tap", 270, 182), ("wait", .5), ("type", "user@example.com")], 4),
        ("route-back", [("tap", 30, 60)], 4)]),
    "ricochlime": dict(cmd=["/home/mecha/flutter-apps/ricochlime/bin/ricochlime"], kill=["flutter-apps/ricochlime/bin/ricochlime"], phases=[
        ("menu-idle", [], 4),
        ("tap-play-start-game", [("tap", 270, 245), ("wait", 2)], 5),
        ("gameplay-shooting-taps", [x for i in range(10) for x in (("tap", 100 + 40 * (i % 6), 300 + 20 * (i % 3)), ("wait", 1.2))], 14)]),
    "firmware-updater": dict(cmd=["/home/mecha/flutter-apps/firmware_updater/firmware-updater"],
                             env={"PATH": "/home/mecha/flutter-apps/shims:/usr/local/bin:/usr/bin"},
                             kill=["flutter-apps/firmware_updater/firmware-updater"], phases=[
        ("startup-spinner-waiting-for-fwupd", [], 8)]),
}}
