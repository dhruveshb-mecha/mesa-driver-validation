#!/usr/bin/python3
"""Turn the raw board results (rsync of ~/appbench/results/<track>/) into the evidence folders of this repo.
Usage: collect.py RAW_RESULTS_DIR TRACK      (TRACK = gtk4 | flutter)   -> app-benchmarks/<track>-apps/<app>/{README.md, attempt-NN-<mode>/...}
Every attempt folder keeps: cmd.txt, result.json, kernel-gpu-events.txt, renderer-evidence.txt, app-stdout.txt, app-stderr.txt, kernel.txt,
and the per-phase screenshots; files over 1 MB are gzipped.  Per-app README = workflow, fps table (phase x mode x attempt), health table, notes.
notes.json (next to this script) holds the hand-written interpretation per app, so numbers and words stay separate."""
import gzip, json, os, shutil, sys
raw, track = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
dest = f"{root}/{track}-apps"; notes = json.load(open(f"{here}/notes.json")) if os.path.exists(f"{here}/notes.json") else {}
TITLES = json.load(open(f"{here}/titles.json"))
def put(src, dst):
    if os.path.getsize(src) > 1_000_000:
        with open(src, "rb") as a, gzip.open(dst + ".gz", "wb") as b: shutil.copyfileobj(a, b)
    else: shutil.copy(src, dst)
apps = sorted(d for d in os.listdir(raw) if os.path.isdir(f"{raw}/{d}"))
index = []
for app in apps:
    attempts = sorted(d for d in os.listdir(f"{raw}/{app}") if d.startswith("attempt-"))
    out = f"{dest}/{app}"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    R = {}
    for a in attempts:
        os.makedirs(f"{out}/{a}")
        for f in os.listdir(f"{raw}/{app}/{a}"):
            if f == "kernel.txt" and os.path.getsize(f"{raw}/{app}/{a}/{f}") == 0: continue
            put(f"{raw}/{app}/{a}/{f}", f"{out}/{a}/{f}")
        R[a] = json.load(open(f"{raw}/{app}/{a}/result.json"))
    first = next(iter(R.values()))
    phases = [p["phase"] for p in first["phases"]]
    cols = list(R)
    def cell(a, ph):
        p = next((p for p in R[a]["phases"] if p["phase"] == ph), None); return "-" if p is None else f"{p['fps']}"
    hang = sum(r["gpu_hang_events"] for r in R.values()); sw = any(r["software_renderer_seen"] for r in R.values())
    died = [a for a, r in R.items() if not r["app_alive_at_end"]]
    verdict = "GPU HANG" if hang else ("APP EXITED/CRASHED" if died else "PASS (renders, no GPU events)")
    L = [f"# {TITLES.get(app, app)}", "", f"Track: **{track}**   Mesa on the board: `{first['mesa']}`   Verdict: **{verdict}**", "",
         "## What was run", f"`{' '.join(first['cmd'])}`", "", "Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):", ""]
    L += [f"{i + 1}. {p}" for i, p in enumerate(phases)]
    L += ["", "## Frame rate per phase (presented frames per second of the app's main surface)", "",
          "| phase | " + " | ".join(c.replace("attempt-", "a") for c in cols) + " |", "|---|" + "---|" * len(cols)]
    L += [f"| {ph} | " + " | ".join(cell(c, ph) for c in cols) + " |" for ph in phases]
    L += ["", "A static screen redraws only on change, so ~0 fps there is correct; judge throughput from the phases that scroll, zoom or animate.", "",
          "## Health per attempt", "", "| attempt | app alive at end | GPU hang events | other etnaviv/drm kernel lines | llvmpipe seen in log |", "|---|---|---|---|---|"]
    L += [f"| {c} | {R[c]['app_alive_at_end']} | {R[c]['gpu_hang_events']} | {R[c]['kernel_gpu_lines'] - R[c]['gpu_hang_events']} | {R[c]['software_renderer_seen']} |" for c in cols]
    n = notes.get(app)
    if n: L += ["", "## What this shows / what to look into", ""] + [f"- {x}" for x in n]
    shots = [c for c in cols if c.endswith("-gl") or c.endswith("-gles")][:1] or cols[:1]
    L += ["", "## Screenshots (first GL attempt)", ""] + [f"- [{p['phase']}]({shots[0]}/{p['screenshot']})" for p in R[shots[0]]["phases"]]
    L += ["", "## Files", "Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), "
          "`renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots."]
    open(f"{out}/README.md", "w").write("\n".join(L) + "\n")
    best = max((p["fps"] for r in R.values() for p in r["phases"]), default=0)
    index.append((app, verdict, hang, best, len(attempts)))
print(json.dumps(index))
json.dump(index, open(f"{dest}/.index.json", "w"))
