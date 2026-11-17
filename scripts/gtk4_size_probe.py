#!/usr/bin/python3
"""Minimal reproducer: a GTK4 window whose content requests WxH (forces a surface larger than the output), GL renderer.
Usage: GSK_RENDERER=gl gtk4_size_probe.py W H [resize]   ->  (with "resize" the requested width changes every frame by +-step)
       -> prints 'OK WxH' after 1.5s of frames, or crashes (SIGSEGV)."""
import sys, gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
W, H = int(sys.argv[1]), int(sys.argv[2]); n = [0]; resize = 'resize' in sys.argv
STEP = int(sys.argv[sys.argv.index('resize') + 1]) if resize and len(sys.argv) > sys.argv.index('resize') + 1 else 40
def act(app):
    win = Gtk.ApplicationWindow(application=app); lbl = Gtk.Label(label="size probe"); lbl.set_size_request(W, H); win.set_child(lbl); win.present()
    def tick(w, clock):
        n[0] += 1
        if resize: lbl.set_size_request(W + (n[0] % 12) * STEP, H)
        if n[0] > 90:
            print(f"OK {W}x{H} actual={lbl.get_width()}x{lbl.get_height()} renderer={win.get_native().get_renderer().__class__.__name__}", flush=True); app.quit(); return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE
    win.add_tick_callback(tick)
a = Gtk.Application(application_id="org.mecha.sizeprobe"); a.connect("activate", act); a.run([])
