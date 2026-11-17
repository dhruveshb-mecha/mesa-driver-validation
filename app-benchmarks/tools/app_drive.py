#!/usr/bin/python3
"""Run ONE real application through a scripted workflow on the Comet and record everything needed to judge the Mesa driver.

Usage (on the board):  app_drive.py TRACK APP MODE OUTDIR
  TRACK  gtk4 | flutter           (which profile table to use, see profiles.py)
  APP    profile name, e.g. nautilus, loupe, localsend
  MODE   gtk4:    default | gl | cairo      -> GSK_RENDERER unset / gl / cairo   (default = what a user gets)
         flutter: gles | default            -> GDK_GL=gles / unset (GTK3 cannot create a GL context without it)
Records in OUTDIR: cmd.txt  app-stdout.txt  app-stderr.txt  kernel.txt  kernel-gpu-events.txt  renderer-evidence.txt
                   result.json (per phase fps / commits, app alive, GPU events, exit status)  <phase>.png screenshots
Frame rate = Wayland surface commits per second of the app's main surface (WAYLAND_DEBUG=client), so it needs no change to the app and works
for the GL (EGL swap) and Cairo (wl_shm) paths alike.  Static screens legitimately show ~0 fps; only phases that animate or scroll say
anything about throughput.  Coordinates are logical px of the 540x620 DSI panel (= screenshot px / 2).
Nothing here sets anything but renderer selection and logging variables; Mesa is whatever is installed on the board."""
import json, os, re, shlex, shutil, signal, subprocess, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profiles import PROFILES

track, app, mode, out = sys.argv[1:5]
P = PROFILES[track][app]
os.makedirs(out, exist_ok=True)
home = os.path.expanduser("~")
env = dict(os.environ, XDG_RUNTIME_DIR="/run/user/1000", WAYLAND_DISPLAY="wayland-1", SWAYSOCK=next((f"/run/user/1000/{f}" for f in os.listdir("/run/user/1000") if f.startswith("sway-ipc")), ""),
           GDK_BACKEND="wayland", XDG_SESSION_TYPE="wayland", WAYLAND_DEBUG="client",
           MESA_DEBUG="1", EGL_LOG_LEVEL="info", LIBGL_DEBUG="verbose")          # Mesa driver logging, same as the validation runs
env.pop("LD_LIBRARY_PATH", None)
if track == "gtk4":
    env["GSK_DEBUG"] = "renderer"; env["GDK_DEBUG"] = "opengl"
    if mode != "default": env["GSK_RENDERER"] = mode
else:
    if mode == "gles": env["GDK_GL"] = "gles"
env.update({k: os.path.expanduser(v) for k, v in P.get("env", {}).items()})
if P.get("ld"): env["LD_LIBRARY_PATH"] = os.path.expanduser(P["ld"])

penv = {k: v for k, v in env.items() if k not in ("WAYLAND_DEBUG",)}      # helper tools must not print the protocol trace

def sh(*a, **k): return subprocess.run(list(map(str, a)), env=penv, capture_output=True, text=True, **k)
for pat in P.get("kill", []): subprocess.run(["pkill", "-f", pat])          # single-instance apps: start from a clean state
time.sleep(1)
# Clean slate every run: GNOME apps remember zoom, view mode, scroll position, last file. Reset their settings and use a fresh copy of the data
# under a unique name (file-position metadata is keyed by path).
if P.get("schemas"):
    sc = subprocess.run(["gsettings", "list-schemas"], capture_output=True, text=True, env=penv).stdout.split()
    for s in sc:
        if re.search(r"^org\.gnome\.(%s)(\.|$)" % P["schemas"], s): subprocess.run(["gsettings", "reset-recursively", s], env=penv, capture_output=True)
DATA = f"{home}/appbench-run-{os.getpid()}"
shutil.copytree(f"{home}/appbench-data", DATA, symlinks=True)
cmd = [os.path.expanduser(c).replace("{DATA}", DATA) for c in P["cmd"]]
shown = {k: env[k] for k in env if k in ("GSK_RENDERER", "GDK_GL", "GDK_BACKEND", "LD_LIBRARY_PATH", "GSK_DEBUG", "GDK_DEBUG", "MESA_DEBUG", "EGL_LOG_LEVEL", "LIBGL_DEBUG") or k in P.get("env", {})}
open(f"{out}/cmd.txt", "w").write(" ".join(f"{k}={shlex.quote(v)}" for k, v in shown.items()) + " " + " ".join(map(shlex.quote, cmd)) + f"\n# track={track} app={app} mode={mode}\n")
t_start_wall = time.strftime("%Y-%m-%d %H:%M:%S")
commits = {}; lock = threading.Lock()
errlog = open(f"{out}/app-stderr.txt", "w")
proc = subprocess.Popen(cmd, cwd=os.path.dirname(cmd[0]) if os.path.isabs(cmd[0]) else home, env=env, stdout=open(f"{out}/app-stdout.txt", "w"),
                        stderr=subprocess.PIPE, text=True, errors="replace", start_new_session=True)
rx = re.compile(r"\[(\d+):(\d+):([\d.]+)\]\s*(?:\{[^}]*\}\s*)?-> wl_surface#(\d+)\.commit\(\)")   # GL path: "{mesa egl surface queue} ->", Cairo/wl_shm path: no queue tag
proto = re.compile(r"^\[\d+:\d+:[\d.]+\]")
def reader():
    for line in proc.stderr:
        m = rx.match(line)
        if m:
            with lock: commits.setdefault(m.group(4), []).append(int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)))
        elif not proto.match(line):           # keep the app's own messages, drop the Wayland protocol trace
            errlog.write(line); errlog.flush()
threading.Thread(target=reader, daemon=True).start()
def utc(): t = time.gmtime(); return t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec + (time.time() % 1)
def tap(x, y, n=1):
    sh("wlrctl", "pointer", "move", -3000, -3000); sh("wlrctl", "pointer", "move", x, y)
    for _ in range(n): sh("wlrctl", "pointer", "click", "left")
def act(a):
    k = a[0]
    if k == "tap": tap(a[1], a[2])
    elif k == "dtap": tap(a[1], a[2], 2)
    elif k == "move": sh("wlrctl", "pointer", "move", -3000, -3000); sh("wlrctl", "pointer", "move", a[1], a[2])
    elif k == "scroll":                                                     # ("scroll", dy[, x, y])
        x, y = (a[2], a[3]) if len(a) > 3 else (270, 400)
        sh("wlrctl", "pointer", "move", -3000, -3000); sh("wlrctl", "pointer", "move", x, y); sh("wlrctl", "pointer", "scroll", 0, a[1])
    elif k == "type": sh("wlrctl", "keyboard", "type", a[1], *(["modifiers", a[2]] if len(a) > 2 else []))
    elif k == "wait": time.sleep(a[1])
time.sleep(P.get("startup", 8))
if P.get("focus"): tap(*P["focus"]); time.sleep(1)      # one neutral click on the title so wheel/key input reaches the window
focus_ok = None
phases = []
for name, actions, secs in P["phases"]:
    t0 = utc(); start = time.time()
    for a in actions:
        if proc.poll() is not None: break
        act(a)
    time.sleep(max(0, secs - (time.time() - start)))
    t1 = utc(); dt = time.time() - start
    with lock:
        per = {s: sum(t0 <= c <= t1 for c in ts) for s, ts in commits.items()}
    main = max(commits, key=lambda s: len(commits[s])) if commits else None       # the app's main surface = most commits overall
    n = per.get(main, 0) if main else 0
    png = re.sub("[^a-z0-9]+", "-", name.lower()).strip("-") + ".png"
    sh("grim", f"{out}/{png}")
    phases.append(dict(phase=name, fps=round(n / dt, 1), commits=n, secs=round(dt, 1), screenshot=png, surfaces_commits=per))
    print("PHASE " + json.dumps({k: v for k, v in phases[-1].items() if k != "surfaces_commits"}), flush=True)
alive = proc.poll() is None
try: os.killpg(proc.pid, signal.SIGTERM)
except Exception: pass
time.sleep(2)
try: os.killpg(proc.pid, signal.SIGKILL)
except Exception: pass
for pat in P.get("kill", []): subprocess.run(["pkill", "-f", pat])
shutil.rmtree(DATA, ignore_errors=True)
kern = subprocess.run(["journalctl", "-k", "--since", t_start_wall, "--no-pager"], capture_output=True, text=True).stdout
open(f"{out}/kernel.txt", "w").write(kern)
gpu = [l for l in kern.splitlines() if re.search(r"etnaviv|drm|gpu|recover|hung", l, re.I)]
open(f"{out}/kernel-gpu-events.txt", "w").write("\n".join(gpu) + ("\n" if gpu else ""))
err = open(f"{out}/app-stderr.txt").read()
ev = [l for l in err.splitlines() if re.search(r"renderer|GL_RENDERER|Using|OpenGL|EGL|llvmpipe|etnaviv|vivante|libEGL|MESA|Mesa", l)]
open(f"{out}/renderer-evidence.txt", "w").write("\n".join(ev[:200]) + "\n")
llvm = bool(re.search(r"llvmpipe|softpipe", err, re.I))
res = dict(track=track, app=app, mode=mode, cmd=cmd, started=t_start_wall, app_alive_at_end=alive, exit_code=proc.poll(),
           gpu_hang_events=sum(bool(re.search(r"recover hung|hung GPU|GPU hang", l, re.I)) for l in gpu), kernel_gpu_lines=len(gpu),
           software_renderer_seen=llvm, main_surface=max(commits, key=lambda s: len(commits[s])) if commits else None, phases=phases,
           mesa=subprocess.run(["rpm", "-q", "mesa-dri-drivers"], capture_output=True, text=True).stdout.strip())
json.dump(res, open(f"{out}/result.json", "w"), indent=1)
print(f"SUMMARY {app}/{mode} alive={alive} gpu_hangs={res['gpu_hang_events']} llvmpipe_seen={llvm} max_fps={max([p['fps'] for p in phases] or [0])}")
