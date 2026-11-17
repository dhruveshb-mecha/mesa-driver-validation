#!/usr/bin/env python3
"""Run scripts/gtk4_bench.py over scenes x item counts x renderers (cairo = CPU reference, gl = GPU) and
write OUT/gtk4-bench.jsonl + gtk4-bench.md (comparison table).  Usage: gtk4_bench_matrix.py OUT [--quick]"""
import glob, json, os, subprocess, sys, math
out = sys.argv[1]; quick = "--quick" in sys.argv
os.makedirs(out, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH", "PKG_CONFIG_PATH")}
env.update(GDK_BACKEND="wayland")
socks = glob.glob(f"/run/user/{os.getuid()}/sway-ipc.*.sock")
if socks: env.setdefault("SWAYSOCK", socks[0])
SCENES = ["widgets", "text", "shadows", "gradients", "rounded", "textures", "blur"]
COUNTS = [10] if quick else [10, 40]
SECS = "4" if quick else "6"
plan = [(s, n, False) for s in SCENES for n in COUNTS] + ([] if quick else [(s, 40, True) for s in ("widgets", "shadows", "rounded")])
rows = []
for scene, n, small in plan:
    for r in ("cairo", "gl"):
        cmd = [sys.executable, f"{here}/gtk4_bench.py", scene, str(n), SECS] + (["small"] if small else [])
        row = None
        for attempt in (1, 2):            # one retry: failures so far were intermittent
            try:
                p = subprocess.run(cmd, env=env | {"GSK_RENDERER": r}, capture_output=True, text=True, timeout=90)
                line = next((l for l in p.stdout.splitlines() if l.startswith("{")), None)
                if line: row = json.loads(line); row["attempt"] = attempt; break
                err = "\n".join(l for l in p.stderr.splitlines() if "portal" not in l)[-300:]
                row = dict(scene=scene, n=n, renderer=r, error=f"rc={p.returncode} {err or 'no output'}", attempt=attempt)
            except subprocess.TimeoutExpired:
                row = dict(scene=scene, n=n, renderer=r, error="timeout 90s", attempt=attempt)
        row["req"] = r; row["small"] = small; rows.append(row)
        print(f"{scene:10} n={n:<3} {'small' if small else 'full ':5} {r:5} -> " + (f"{row['fps']} fps p95 {row['p95_ms']} ms (size {row['size']})" if "fps" in row else row["error"]), flush=True)
        with open(f"{out}/gtk4-bench.jsonl", "a") as f: f.write(json.dumps(row) + "\n")
L = ["# GTK4 renderer benchmark (Cairo = CPU, GL = GPU via etnaviv)", "", "| scene | n | window | cairo fps | gl fps | gl/cairo | gl p95 ms | gl max ms |", "|---|---|---|---|---|---|---|---|"]
ratios = []
for scene, n, small in plan:
    c = next((x for x in rows if (x["scene"], x["n"], x["small"], x["req"]) == (scene, n, small, "cairo")), {})
    g = next((x for x in rows if (x["scene"], x["n"], x["small"], x["req"]) == (scene, n, small, "gl")), {})
    if "fps" in c and "fps" in g:
        ratio = g["fps"] / c["fps"]; ratios.append(ratio)
        L.append(f"| {scene} | {n} | {'640x480' if small else 'full'} ({g['size']}) | {c['fps']} | {g['fps']} | {ratio:.2f}x | {g['p95_ms']} | {g['max_ms']} |")
    else: L.append(f"| {scene} | {n} | {'small' if small else 'full'} | {c.get('fps', c.get('error'))} | {g.get('fps', g.get('error'))} | - | - | - |")
open(f"{out}/gtk4-bench.md", "w").write("\n".join(L) + "\n")
gm = math.exp(sum(math.log(r) for r in ratios) / len(ratios)) if ratios else 0
wins = sum(1 for r in ratios if r > 1.0)
print(f"GTK4BENCH runs={len(rows)} gl_faster_in={wins}/{len(ratios)} gl_vs_cairo_geomean={gm:.2f}")
