#!/usr/bin/env python3
"""Reproducer/rate counter for the intermittent SIGSEGV in Mesa dri_drawable_bind_images seen with GTK4's GL renderer.
Runs `gtk4_bench.py SCENE N` with GSK_RENDERER=gl K times; reports crashes (rc -11) and, if coredumpctl works, the top frame.
Usage: gtk4_crash_repro.py [K=10] [SCENE=text] [N=10]"""
import glob, os, subprocess, sys, json, statistics
K = int(sys.argv[1]) if len(sys.argv) > 1 else 10
scene = sys.argv[2] if len(sys.argv) > 2 else "text"; n = sys.argv[3] if len(sys.argv) > 3 else "10"
here = os.path.dirname(os.path.abspath(__file__))
env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH", "PKG_CONFIG_PATH")}
env.update(GDK_BACKEND="wayland", GSK_RENDERER="gl")
s = glob.glob(f"/run/user/{os.getuid()}/sway-ipc.*.sock")
if s: env.setdefault("SWAYSOCK", s[0])
segv = ok = other = 0; fps = []; sizes = []
for i in range(K):
    p = subprocess.run([sys.executable, f"{here}/gtk4_bench.py", scene, n, "4"], env=env, capture_output=True, text=True, timeout=90)
    line = next((l for l in p.stdout.splitlines() if l.startswith("{")), None)
    if p.returncode == -11: segv += 1; print(f"  run {i+1}: SIGSEGV", flush=True)
    elif line: r = json.loads(line); ok += 1; fps.append(r["fps"]); sizes.append(r["size"]); print(f"  run {i+1}: ok {r['fps']} fps size {r['size']}", flush=True)
    else: other += 1; print(f"  run {i+1}: rc={p.returncode} no output", flush=True)
top = ""
try:
    out = subprocess.run(["coredumpctl", "info", "--no-pager", "-r", "-1"], capture_output=True, text=True).stdout
    top = next((l.strip() for l in out.splitlines() if l.strip().startswith("#0")), "")
except Exception: pass
print(f"CRASHREPRO scene={scene} n={n} runs={K} segv={segv} ok={ok} other={other} median_fps={statistics.median(fps) if fps else 0} top_frame={top}")
