#!/usr/bin/python3
"""Drive the stock Flutter 'animations' sample (flutter/samples, built by flutter/build-arm64.sh APP=demo_animations) on the Comet.
Opens each sample from the list with synthetic pointer input (wlrctl), taps its controls, and measures the real presented frame rate from the
app's Wayland surface commits (WAYLAND_DEBUG=client) -- no changes to the app. Usage: flutter_anim_drive.py OUTDIR [SECS_PER_SAMPLE=6]
Prints one line per sample: FLUTTERANIM {"sample","fps","commits","secs"} and a final FLUTTERANIMSUMMARY samples=.. ok=.. min_fps=.. max_fps=.. app_died=..
Coordinates are logical px of the 540x620 DSI panel (scale 2); the list rows were taken from screenshots."""
import json, os, re, signal, subprocess, sys, threading, time
out = sys.argv[1]; secs = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
os.makedirs(out, exist_ok=True)
env = dict(os.environ, XDG_RUNTIME_DIR="/run/user/1000", WAYLAND_DISPLAY="wayland-1", GDK_BACKEND="wayland", GDK_GL="gles", WAYLAND_DEBUG="client")
for k in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH"): env.pop(k, None)
VERBOSE = os.environ.get("VERBOSE") == "1"   # VERBOSE=1: every log source on + the full unfiltered stderr (incl. Wayland protocol trace) kept gzipped
if VERBOSE:
    env.update(MESA_DEBUG="1", EGL_LOG_LEVEL="debug", LIBGL_DEBUG="verbose", G_MESSAGES_DEBUG="all", GDK_DEBUG="opengl,events,misc,dnd,input,cursor,eventloop",
               FLUTTER_ENGINE_SWITCHES="2", FLUTTER_ENGINE_SWITCH_1="verbose-logging=true", FLUTTER_ENGINE_SWITCH_2="trace-startup=true")
    import gzip; fulllog = gzip.open(f"{out}/app-stderr-full.log.gz", "wt", errors="replace")
# (name, list position "top"/"bottom", y in logical px)
TOP = [("AnimatedContainer", 225), ("PageRouteBuilder", 273), ("AnimationController", 321), ("Tweens", 370), ("AnimatedBuilder", 417),
       ("CustomTween", 466), ("TweenSequences", 514), ("FadeTransition", 562)]
BOTTOM = [("FocusImage", 163), ("CardSwipe", 211), ("FlutterAnimate", 259), ("RepeatingAnimation", 307), ("SpringPhysics", 355),
          ("AnimatedList", 403), ("AnimatedPositioned", 451), ("AnimatedSwitcher", 499), ("HeroAnimation", 547), ("CurvedAnimation", 595)]
commits = []; lock = threading.Lock(); alive = [True]
applog = open(f"{out}/app-stderr.log", "w")   # the app's own stderr (Impeller/GDK/GLib messages); Wayland protocol debug lines are not kept (too large) -- only their GL-swap timestamps, see commits.csv
app = subprocess.Popen([os.path.expanduser("~/flutter-apps/demo_animations/animations")], cwd=os.path.expanduser("~/flutter-apps/demo_animations"),
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace", start_new_session=True)
def reader():
    for line in app.stderr:
        if VERBOSE: fulllog.write(line)
        if not re.match(r"\[\d+:\d+:[\d.]+\]\s*\{", line): applog.write(line); applog.flush()
        m = re.match(r"\[(\d+):(\d+):([\d.]+)\]\s*\{mesa egl surface queue\}\s*-> wl_surface#\d+\.commit\(\)", line)   # GL buffer swaps of the app window
        if m:
            with lock: commits.append(int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)))   # UTC seconds of day
    alive[0] = False
threading.Thread(target=reader, daemon=True).start()
def w(*a): subprocess.run(["wlrctl", "pointer", *map(str, a)], env=env, capture_output=True)
def tap(x, y): w("move", -3000, -3000); w("move", x, y); w("click", "left")
def scroll(dy): w("move", -3000, -3000); w("move", 270, 400); w("scroll", 0, dy)
def count(t0, t1):
    with lock: return sum(t0 % 86400 <= c <= t1 % 86400 for c in commits)
time.sleep(6)
rows = []
def sample(name, pos, y):
    if not alive[0]: return
    scroll(-3000); time.sleep(0.5)
    if pos == "bottom": scroll(3000); time.sleep(0.8)
    tap(270, y); time.sleep(2.0)
    t0 = time.time()
    for ty in (313, 400, 500): tap(270, ty); time.sleep(0.4)          # generic: press any button / card in the middle of the page
    time.sleep(secs / 2); subprocess.run(["grim", f"{out}/{name}.png"], env=env, capture_output=True); time.sleep(secs / 2 - 1.2)
    t1 = time.time(); n = count(t0 + 1.5, t1); span = max(t1 - t0 - 1.5, 0.1)
    r = {"sample": name, "fps": round(n / span, 1), "commits": n, "secs": round(span, 1), "alive": alive[0]}
    rows.append(r); print("FLUTTERANIM " + json.dumps(r), flush=True)
    tap(15, 125); time.sleep(1.0)                                       # back arrow
for n, y in TOP: sample(n, "top", y)
for n, y in BOTTOM: sample(n, "bottom", y)
if alive[0]:
    try: os.killpg(app.pid, signal.SIGTERM)
    except ProcessLookupError: pass
applog.close()
if VERBOSE: fulllog.close()
with lock, open(f"{out}/commits.csv", "w") as f:
    f.write("utc_seconds_of_day\n"); f.writelines(f"{c:.6f}\n" for c in commits)
json.dump(rows, open(f"{out}/samples.json", "w"), indent=1)
fps = [r["fps"] for r in rows]
print(f"FLUTTERANIMSUMMARY samples={len(rows)} ok={sum(r['alive'] for r in rows)} min_fps={min(fps, default=0)} max_fps={max(fps, default=0)} app_died={0 if alive[0] else 1}")
