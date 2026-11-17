#!/usr/bin/env python3
"""Run the real-Flutter benchmark app (flutter/gpu_bench, standard GTK embedder, Impeller GLES) over scenes x counts.
Runs on the Comet.  Usage: flutter_bench_matrix.py OUT [--quick]  [APPDIR=~/flutter-apps/gpu_bench]
GTK3 needs GDK_GL=gles on this driver (otherwise 'Unable to create a GL context' and nothing is drawn)."""
import glob, json, os, subprocess, sys, math
out = sys.argv[1]; quick = "--quick" in sys.argv
app = os.path.expanduser(next((a for a in sys.argv[2:] if not a.startswith("--")), "~/flutter-apps/gpu_bench"))
os.makedirs(out, exist_ok=True)
env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH", "PKG_CONFIG_PATH")}
env.update(GDK_BACKEND="wayland", GDK_GL="gles")
VERBOSE = os.environ.get("VERBOSE") == "1"   # VERBOSE=1: all log sources on; each run's full stdout+stderr (incl. Wayland protocol trace) kept gzipped in OUT/logs/
if VERBOSE:
    import gzip
    env.update(MESA_DEBUG="1", EGL_LOG_LEVEL="debug", LIBGL_DEBUG="verbose", G_MESSAGES_DEBUG="all", WAYLAND_DEBUG="client",
               GDK_DEBUG="opengl,events,misc,dnd,input,cursor,eventloop",
               FLUTTER_ENGINE_SWITCHES="2", FLUTTER_ENGINE_SWITCH_1="verbose-logging=true", FLUTTER_ENGINE_SWITCH_2="trace-startup=true")
    os.makedirs(f"{out}/logs", exist_ok=True)
SCENES = [("circles", [10, 50]), ("gradients", [8, 24]), ("shadows", [8, 24]), ("blur", [4, 12]), ("opacity", [8, 24]),
          ("clip", [8, 24]), ("text", [20, 60]), ("images", [8, 24]), ("list", [1])]
SECS = "5" if quick else "8"
if quick: SCENES = [(s, c[:1]) for s, c in SCENES]
rows = []
for scene, counts in SCENES:
    for n in counts:
        row = None
        for attempt in (1, 2):
            try:
                p = subprocess.run([f"{app}/gpu_bench", scene, str(n), SECS], env=env, capture_output=True, text=True, timeout=90, cwd=app)
                if VERBOSE:
                    with gzip.open(f"{out}/logs/{scene}-{n}-attempt{attempt}.log.gz", "wt", errors="replace") as lf:
                        lf.write(f"# cmd: gpu_bench {scene} {n} {SECS}  (rc={p.returncode})\n# ---- stdout ----\n{p.stdout}\n# ---- stderr ----\n{p.stderr}")
                line = next((l for l in p.stdout.splitlines() if l.startswith("FLUTTERBENCH ")), None)
                if line: row = json.loads(line[len("FLUTTERBENCH "):]); row["attempt"] = attempt; break
                row = dict(scene=scene, n=n, error=f"rc={p.returncode} " + "\n".join(l for l in (p.stdout + p.stderr).splitlines() if "rror" in l or "WARN" in l)[-300:], attempt=attempt)
            except subprocess.TimeoutExpired:
                row = dict(scene=scene, n=n, error="timeout 90s", attempt=attempt)
        rows.append(row)
        with open(f"{out}/flutter-bench.jsonl", "a") as f: f.write(json.dumps(row) + "\n")
        print(f"{scene:10} n={n:<3} -> " + (f"{row['fps']} fps, raster p50 {row['raster_p50_ms']} / p95 {row['raster_p95_ms']} ms, total p95 {row['total_p95_ms']} ms ({row['size']})" if "fps" in row else row["error"]), flush=True)
L = ["# Real Flutter app (GTK embedder, Impeller OpenGLES) on etnaviv", "", "| scene | n | fps | raster p50 ms | raster p95 ms | total p95 ms | frames |", "|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['scene']} | {r['n']} | " + (f"{r['fps']} | {r['raster_p50_ms']} | {r['raster_p95_ms']} | {r['total_p95_ms']} | {r['frames']} |" if "fps" in r else f"{r['error']} | | | | |"))
open(f"{out}/flutter-bench.md", "w").write("\n".join(L) + "\n")
ok = [r for r in rows if "fps" in r]
print(f"FLUTTERMATRIX runs={len(rows)} ok={len(ok)} failed={len(rows) - len(ok)} min_fps={min((r['fps'] for r in ok), default=0)} max_fps={max((r['fps'] for r in ok), default=0)}")
