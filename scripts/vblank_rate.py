#!/usr/bin/python3
"""Measure the REAL display vblank rate seen by a Wayland client (Comet, sway + DSI panel) from wp_presentation feedback.
Runs a trivial GTK4 window (scripts/gtk4_bench.py widgets 1) with WAYLAND_DEBUG=client and reads the `presented(...)` events:
presentation timestamp, the refresh interval the compositor CLAIMS, and the DRM vblank sequence number (+1 per real vblank).
Prints  VBLANK claimed_hz=.. measured_hz=.. interval_ms_median=.. max_fps_vsync=..  (measured_hz = sequence delta / elapsed time)."""
import os, re, statistics as st, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH")}
env.update(GDK_BACKEND="wayland", GSK_RENDERER="gl", WAYLAND_DEBUG="client")
p = subprocess.run(["python3", f"{here}/gtk4_bench.py", "widgets", "1", "8"], env=env, capture_output=True, text=True, timeout=60)
rows = []
for l in p.stderr.splitlines():
    m = re.search(r"wp_presentation_feedback#\d+\.presented\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)", l)
    if m:
        hi, lo, ns, refresh, sh, sl, fl = map(int, m.groups()); rows.append((((hi << 32) | lo) * 10**9 + ns, refresh, (sh << 32) | sl))
if len(rows) < 20: print("VBLANK error: too few presentation events", len(rows)); sys.exit(1)
ts = [r[0] for r in rows]; seq = [r[2] for r in rows]; span = (ts[-1] - ts[0]) / 1e9
d = [(b - a) / 1e6 for a, b in zip(ts, ts[1:])]; hz = (seq[-1] - seq[0]) / span
print(f"VBLANK claimed_hz={1e9 / rows[0][1]:.2f} measured_hz={hz:.2f} interval_ms_median={st.median(d):.2f} max_fps_vsync={hz:.1f} presents={len(rows)}")
