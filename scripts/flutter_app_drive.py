#!/usr/bin/python3
"""Drive a real, unmodified Flutter Linux (GTK) app on the Comet with synthetic pointer input (wlrctl) and measure the presented frame
rate from the app's Wayland surface commits (WAYLAND_DEBUG=client).  Works on release builds: no VM service or app change is needed.

Usage: flutter_app_drive.py PROFILE OUTDIR            PROFILE = localsend | ente_auth | firmware_updater
Prints one line per phase:  FLUTTERAPP {"app","phase","fps","commits","secs"}  and a final FLUTTERAPPSUMMARY.
Coordinates are logical px of the 540x620 DSI panel (scale 2); they were taken from screenshots of each app's first screen.
fps of an idle phase only says how often the app redraws on its own (0 for a static screen is correct); the interesting numbers are the
phases with input (tab switches, route transitions, scrolling)."""
import json, os, re, subprocess, sys, threading, time

PROFILES = {
    # exe, cwd, extra LD_LIBRARY_PATH, [(phase, action list, seconds)]; actions: ("tap",x,y) ("scroll",dy) ("wait",s)
    "localsend": dict(
        exe="~/flutter-apps/localsend/localsend_app", ld="~/flutter-apps/ld-ayatana",
        phases=[("idle-receive-screen (animated radar)", [], 6),
                ("tab-switch-send", [("tap", 270, 594)], 4),
                ("tab-switch-settings", [("tap", 449, 594)], 4),
                ("settings-scroll-down-up", [("scroll", 12), ("wait", .4)] * 6 + [("scroll", -12), ("wait", .4)] * 6, 6),
                ("tab-switch-receive", [("tap", 91, 594)], 4)]),
    "ente_auth": dict(
        exe="~/flutter-apps/ente_auth/enteauth", ld="~/flutter-apps/ente_auth/lib",
        phases=[("idle-onboarding-carousel", [], 8),
                ("route-transition-log-in", [("tap", 390, 590)], 5),
                ("route-transition-back", [("tap", 30, 60)], 4)]),
    "firmware_updater": dict(
        exe="~/flutter-apps/firmware_updater/firmware-updater", ld="", env=dict(PATH=os.path.expanduser("~/flutter-apps/shims") + ":" + os.environ.get("PATH", "")),
        phases=[("idle-spinner (waiting for fwupd)", [], 8)]),
}
prof = sys.argv[1]; out = sys.argv[2]; P = PROFILES[prof]
os.makedirs(out, exist_ok=True)
env = dict(os.environ, XDG_RUNTIME_DIR="/run/user/1000", WAYLAND_DISPLAY="wayland-1", GDK_BACKEND="wayland", GDK_GL=os.environ.get("GDK_GL", "gles"),
           WAYLAND_DEBUG="client", **P.get("env", {}))
env.pop("LD_LIBRARY_PATH", None)
if P["ld"]: env["LD_LIBRARY_PATH"] = os.path.expanduser(P["ld"])
exe = os.path.expanduser(P["exe"])
commits = []; lock = threading.Lock(); applog = open(f"{out}/app-stderr.log", "w")
app = subprocess.Popen([exe], cwd=os.path.dirname(exe), env=env, stdout=open(f"{out}/app-stdout.log", "w"), stderr=subprocess.PIPE, text=True,
                       errors="replace", start_new_session=True)
def reader():
    for line in app.stderr:
        if not re.match(r"\[\d+:\d+:[\d.]+\]\s*\{", line): applog.write(line); applog.flush()
        m = re.match(r"\[(\d+):(\d+):([\d.]+)\]\s*\{mesa egl surface queue\}\s*-> wl_surface#\d+\.commit\(\)", line)
        if m:
            with lock: commits.append(int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)))
threading.Thread(target=reader, daemon=True).start()
penv = {k: v for k, v in env.items() if k != "WAYLAND_DEBUG"}   # helper tools must not print the protocol trace
def w(*a): subprocess.run(["wlrctl", "pointer", *map(str, a)], env=penv, capture_output=True)
def act(a):
    if a[0] == "tap": w("move", -3000, -3000); w("move", a[1], a[2]); w("click", "left")
    elif a[0] == "scroll": w("move", -3000, -3000); w("move", 270, 400); w("scroll", 0, a[1])
    elif a[0] == "wait": time.sleep(a[1])
def utc(): t = time.gmtime(); return t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec + (time.time() % 1)
time.sleep(8)                                     # startup
rows = []
for name, actions, secs in P["phases"]:
    t0 = utc(); start = time.time()
    for a in actions: act(a)
    time.sleep(max(0, secs - (time.time() - start)))
    t1 = utc(); dt = time.time() - start
    with lock: n = sum(t0 <= c <= t1 for c in commits)
    r = dict(app=prof, phase=name, fps=round(n / dt, 1), commits=n, secs=round(dt, 1)); rows.append(r)
    print("FLUTTERAPP " + json.dumps(r), flush=True)
    subprocess.run(["grim", f"{out}/{re.sub('[^a-z0-9]+', '-', name.lower()).strip('-')}.png"], env=penv)
alive = app.poll() is None
print(f"FLUTTERAPPSUMMARY app={prof} phases={len(rows)} app_alive={alive} max_fps={max(r['fps'] for r in rows)}")
try: os.killpg(app.pid, 15)
except Exception: pass
