#!/usr/bin/python3
"""GTK4 / GSK renderer micro-benchmark for the Comet (run on the device; renderer chosen with GSK_RENDERER).

Usage: GSK_RENDERER=gl gtk4_bench.py SCENE N [SECS] [small]
Scenes (each animates N items every frame so every frame must be re-rendered):
  widgets    N Gtk.Buttons                       (many small draws, text, borders)
  text       N labels with long text             (glyph atlas / text pipeline)
  shadows    N boxes with blurred box-shadow     (blur: offscreen passes)
  gradients  N boxes, linear + radial gradients  (gradient shaders)
  rounded    N overlapping rounded boxes, opacity 0.7 (rounded clips, opacity groups, blending)
  textures   N 128x128 textures, scaled          (texture upload/sampling)
  blur       N boxes with CSS filter: blur(6px)  (heaviest offscreen path)
Prints one JSON line: {"scene","n","renderer","size","fps","p50_ms","p95_ms","max_ms","frames"}.
'small' makes the window floating ~640x480 (via swaymsg) to separate fill-rate from per-draw cost.
"""
import json, math, os, subprocess, sys
import gi
gi.require_version("Gtk", "4.0"); gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, GLib

scene = sys.argv[1]; N = int(sys.argv[2]); SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
small = "small" in sys.argv
APP_ID = "org.mecha.gtk4bench"
frames = []

CSS = """
.sh   { background: #3465a4; border-radius: 10px; box-shadow: 0 6px 14px rgba(0,0,0,.6), 0 0 4px rgba(0,0,0,.4); min-width: 90px; min-height: 60px; }
.gr   { background-image: linear-gradient(135deg, #e66465, #9198e5 60%, #2ecc71), radial-gradient(circle at 30% 30%, rgba(255,255,255,.7), transparent 60%); border-radius: 6px; min-width: 110px; min-height: 80px; }
.rd   { background: #ef2929; border-radius: 24px; border: 3px solid #fce94f; opacity: .7; min-width: 140px; min-height: 100px; }
.bl   { background: #73d216; border-radius: 12px; filter: blur(6px); min-width: 100px; min-height: 70px; }
"""

def make_item(i):
    if scene == "widgets":  return Gtk.Button(label=f"btn {i}")
    if scene == "text":     return Gtk.Label(label=f"The quick brown fox {i} jumps over the lazy dog 0123456789")
    box = Gtk.Box()
    if scene == "shadows":  box.add_css_class("sh")
    elif scene == "gradients": box.add_css_class("gr")
    elif scene == "rounded": box.add_css_class("rd")
    elif scene == "blur":   box.add_css_class("bl")
    elif scene == "textures":
        data = bytes((x * 7 + i * 13) & 255 if k != 3 else 255 for y in range(128) for x in range(128) for k in range(4))
        tex = Gdk.MemoryTexture.new(128, 128, Gdk.MemoryFormat.R8G8B8A8, GLib.Bytes.new(data), 128 * 4)
        pic = Gtk.Picture.new_for_paintable(tex); pic.set_size_request(128, 128); return pic
    else: raise SystemExit(f"unknown scene {scene}")
    return box

def on_activate(app):
    prov = Gtk.CssProvider(); prov.load_from_string(CSS)
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    win = Gtk.ApplicationWindow(application=app)
    if small: win.set_default_size(640, 480)
    else: win.fullscreen()
    fx = Gtk.Fixed(); win.set_child(fx)
    items = []
    for i in range(N):
        w = make_item(i); fx.put(w, 0, 0); items.append(w)
    win.present()
    if small:   # best effort: make the sway window floating and 640x480
        def float_it():
            subprocess.run(["swaymsg", f'[app_id="{APP_ID}"] floating enable, resize set 640 480'], capture_output=True)
            return GLib.SOURCE_REMOVE
        GLib.timeout_add(700, float_it)
    start = [None]

    def tick(widget, clock):
        t = clock.get_frame_time() / 1e6
        if start[0] is None: start[0] = t
        dt = t - start[0]
        w = max(fx.get_width(), 400); h = max(fx.get_height(), 400)
        for i, b in enumerate(items):
            a = dt * 1.5 + i * 0.1
            fx.move(b, w / 2 + math.cos(a) * (w / 2 - 90) * (i % 7 + 1) / 7, h / 2 + math.sin(a) * (h / 2 - 60) * (i % 5 + 1) / 5)
        frames.append(t)
        if dt > SECS + 1.0:
            ts = [x for x in frames if x - start[0] > 1.0]   # drop 1s warm-up
            d = sorted((b - a) * 1000 for a, b in zip(ts, ts[1:]))
            fps = (len(ts) - 1) / (ts[-1] - ts[0])
            print(json.dumps(dict(scene=scene, n=N, renderer=win.get_native().get_renderer().__class__.__name__,
                                  size=f"{fx.get_width()}x{fx.get_height()}", fps=round(fps, 1),
                                  p50_ms=round(d[len(d) // 2], 1), p95_ms=round(d[int(len(d) * .95)], 1),
                                  max_ms=round(d[-1], 1), frames=len(ts))), flush=True)
            app.quit(); return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE
    win.add_tick_callback(tick)

app = Gtk.Application(application_id=APP_ID)
app.connect("activate", on_activate)
app.run([])
