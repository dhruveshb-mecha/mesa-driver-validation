#!/usr/bin/python3
"""Run every example of the stock gtk4-demo (Fedora gtk4-devel-tools) one at a time under one GSK renderer.
Usage: gtk4_demo_sweep.py RENDERER OUTDIR [SECS=6] [REGEX]      RENDERER = gl | cairo
Per demo: start `gtk4-demo --run NAME`, wait SECS, grim screenshot, then terminate. Records survived/crashed (signal), exit code,
GLib WARNING/CRITICAL count, the renderer GTK reports (GSK_DEBUG=renderer), whether the screenshot is blank, and writes
OUTDIR/<renderer>/<demo>.{png,log} + OUTDIR/summary-<renderer>.{jsonl,md}.  Last stdout line: GTK4DEMOSWEEP renderer=.. demos=.. ok=.. crashed=.. blank=.. """
import json, os, re, signal, subprocess, sys, time
rend, out = sys.argv[1], sys.argv[2]; secs = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0; pat = re.compile(sys.argv[4] if len(sys.argv) > 4 else ".")
os.makedirs(f"{out}/{rend}", exist_ok=True)
env = dict(os.environ, GSK_RENDERER=rend, GSK_DEBUG="renderer", GDK_BACKEND="wayland")
for k in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH"): env.pop(k, None)
names = [n for n in subprocess.run(["gtk4-demo", "--list"], env=env, capture_output=True, text=True).stdout.split() if pat.search(n)]
try:
    from PIL import Image
except ImportError:
    Image = None
def blank(png):
    if not Image: return None
    im = Image.open(png).convert("RGB").crop((0, 60, 1080, 1200)).resize((64, 64)); return len(set(im.getdata())) < 4
rows = []
for n in names:
    log = f"{out}/{rend}/{n}.log"; png = f"{out}/{rend}/{n}.png"
    with open(log, "w") as lf:
        p = subprocess.Popen(["gtk4-demo", "--run", n], env=env, stdout=lf, stderr=lf, start_new_session=True)
        time.sleep(secs)
        early = p.poll()
        subprocess.run(["grim", png], env=env, capture_output=True)
        if early is None:
            os.killpg(p.pid, signal.SIGTERM)
            try: p.wait(5)
            except subprocess.TimeoutExpired: os.killpg(p.pid, signal.SIGKILL); p.wait()
        time.sleep(0.7)
    txt = open(log, errors="replace").read()
    r = {"demo": n, "renderer_requested": rend, "alive_at_screenshot": early is None, "early_rc": early,
         "crashed": early is not None and early < 0 or (early or 0) > 128, "warnings": len(re.findall(r"-(?:WARNING|CRITICAL)", txt)),
         "gtk_renderer": (re.findall(r"(Gsk\w*Renderer|GskGpuRenderer|Gsk\w+)", txt) or ["?"])[0],
         "blank": blank(png) if os.path.exists(png) else None}
    rows.append(r); print(json.dumps(r), flush=True)
with open(f"{out}/summary-{rend}.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
with open(f"{out}/summary-{rend}.md", "w") as f:
    f.write("| demo | alive | early rc | crashed | warnings | blank screenshot |\n|---|---|---|---|---|---|\n")
    for r in rows: f.write(f"| {r['demo']} | {r['alive_at_screenshot']} | {r['early_rc']} | {r['crashed']} | {r['warnings']} | {r['blank']} |\n")
ok = sum(r["alive_at_screenshot"] and not r["crashed"] for r in rows)
print(f"GTK4DEMOSWEEP renderer={rend} demos={len(rows)} ok={ok} crashed={sum(r['crashed'] for r in rows)} blank={sum(bool(r['blank']) for r in rows)}")
