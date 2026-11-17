#!/usr/bin/python3
"""Play a web game in Chromium on the Comet until you stop it, with a live fps overlay and everything logged.
Usage (on the Comet):  chromium_play.py [URL] [OUTDIR]        default URL = https://quenq.com/apps/vice-city/
Stop: Ctrl-C, or  `touch OUTDIR/STOP`, or close the Chromium window.
Overlay (top-left of the page): page fps from requestAnimationFrame (this is the presented frame rate; the panel is 60 Hz) + 1% low + frame-time.
OUTDIR gets: fps.csv (1 Hz: t, fps, min_fps, p99_frame_ms, frames), chromium.log (Chromium --v=1 + GPU service logging, Mesa/EGL debug on stderr),
kernel.log (journalctl -kf, etnaviv hang detection), system.csv (temperature/GPU freq every 10 s), screenshots/ (every 60 s), webgl.txt (renderer strings), summary.txt.
LOGMODE=light env var = clean performance run (Chromium --v=0, no --enable-gpu-service-logging, which writes every GL command and slows the game a lot).
Third-party site: fresh throw-away profile, nothing is stored."""
import asyncio, json, os, signal, subprocess, sys, tempfile, time, urllib.request, shutil
import websockets
URL = sys.argv[1] if len(sys.argv) > 1 else "https://quenq.com/apps/vice-city/"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(f"~/play-{time.strftime('%Y%m%d_%H%M%S')}")
os.makedirs(f"{OUT}/screenshots", exist_ok=True)
env = {k: v for k, v in os.environ.items() if k not in ("LD_LIBRARY_PATH", "GST_PLUGIN_PATH", "PKG_CONFIG_PATH")}
env.update(XDG_RUNTIME_DIR="/run/user/1000", WAYLAND_DISPLAY="wayland-1", MESA_DEBUG="1", EGL_LOG_LEVEL="info", LIBGL_DEBUG="verbose")
LIGHT = os.environ.get("LOGMODE") == "light"   # LOGMODE=light: --v=0, no GPU-command tracing (clean fps run); default = everything on (slow!)
PROF = tempfile.mkdtemp(prefix="vcprof-")
OVERLAY = r"""
(() => {
  if (window.top !== window || window.__fpsInstalled) return; window.__fpsInstalled = true;
  const d = document.createElement('div');
  d.style.cssText = 'position:fixed;left:6px;top:6px;z-index:2147483647;background:rgba(0,0,0,.7);color:#0f0;font:bold 20px monospace;padding:4px 8px;pointer-events:none;white-space:pre';
  const attach = () => (document.body || document.documentElement).appendChild(d);
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', attach) : attach();
  let last = performance.now(), frames = 0, times = [], t0 = last;
  function tick(now) {
    times.push(now - last); last = now; frames++;
    if (now - t0 >= 1000) {
      const s = times.slice().sort((a, b) => a - b), p99 = s[Math.min(s.length - 1, Math.floor(s.length * .99))];
      const fps = frames * 1000 / (now - t0);
      d.textContent = `FPS ${fps.toFixed(1)}   1%low ${(1000 / p99).toFixed(1)}   ${(1000 / fps).toFixed(1)} ms`;
      console.log('VCFPS ' + JSON.stringify({fps: +fps.toFixed(2), p99_ms: +p99.toFixed(1), frames}));
      frames = 0; times = []; t0 = now;
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
"""
chrom = subprocess.Popen(["chromium-browser", f"--user-data-dir={PROF}", "--ozone-platform=wayland", "--no-first-run", "--no-sandbox",
    *(["--enable-logging=stderr", "--v=0"] if LIGHT else ["--enable-logging=stderr", "--v=1", "--enable-gpu-service-logging"]), "--remote-debugging-port=9333", "--remote-allow-origins=*", URL],
    env=env, stdout=open(f"{OUT}/chromium.log", "w"), stderr=subprocess.STDOUT, start_new_session=True)
kern = subprocess.Popen(["journalctl", "-k", "-f", "-n0", "--no-pager"], stdout=open(f"{OUT}/kernel.log", "w"), stderr=subprocess.DEVNULL)
stop = False
def _stop(*a):
    global stop; stop = True
signal.signal(signal.SIGINT, _stop); signal.signal(signal.SIGTERM, _stop)
def rd(p):
    try: return open(p).read().strip()
    except Exception: return ""
async def sysloop():
    with open(f"{OUT}/system.csv", "w") as f:
        f.write("time,soc_temp_c,gpu_freq_hz\n")
        while not stop:
            t = rd("/sys/class/thermal/thermal_zone0/temp"); fq = rd("/sys/class/devfreq/38000000.gpu/cur_freq") or rd("/sys/devices/platform/soc@0/38000000.gpu/devfreq/38000000.gpu/cur_freq")
            f.write(f"{time.strftime('%H:%M:%S')},{int(t) / 1000 if t.isdigit() else ''},{fq}\n"); f.flush()
            await asyncio.sleep(10)
async def main():
    ws_url = None
    for _ in range(60):
        try:
            tabs = json.load(urllib.request.urlopen("http://127.0.0.1:9333/json", timeout=2))
            pg = [t for t in tabs if t.get("type") == "page"]
            if pg: ws_url = pg[0]["webSocketDebuggerUrl"]; break
        except Exception: pass
        await asyncio.sleep(1)
    if not ws_url: print("could not reach Chromium debugging port"); return
    csv = open(f"{OUT}/fps.csv", "w"); csv.write("time,fps,p99_frame_ms,frames\n")
    allfps = []; msgid = [0]
    async with websockets.connect(ws_url, max_size=None) as ws:
        async def call(method, **params):
            msgid[0] += 1; await ws.send(json.dumps({"id": msgid[0], "method": method, "params": params})); return msgid[0]
        await call("Runtime.enable"); await call("Page.enable")
        await call("Page.addScriptToEvaluateOnNewDocument", source=OVERLAY)
        await call("Runtime.evaluate", expression=OVERLAY)
        gl = ("(()=>{const c=document.createElement('canvas');const o={};for(const k of ['webgl2','webgl']){const g=c.getContext(k);if(g){const e=g.getExtension('WEBGL_debug_renderer_info');"
              "o[k]={renderer:e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER),vendor:e?g.getParameter(e.UNMASKED_VENDOR_WEBGL):'',version:g.getParameter(g.VERSION)};}}return JSON.stringify(o)})()")
        gl_id = await call("Runtime.evaluate", expression=gl, returnByValue=True)
        nxt_shot = time.time() + 20
        while not stop and chrom.poll() is None and not os.path.exists(f"{OUT}/STOP"):
            try: raw = await asyncio.wait_for(ws.recv(), timeout=1)
            except asyncio.TimeoutError: raw = None
            except websockets.ConnectionClosed: break
            if raw:
                m = json.loads(raw)
                if m.get("id") == gl_id: open(f"{OUT}/webgl.txt", "w").write(m["result"]["result"].get("value", str(m)) + "\n")
                if m.get("method") == "Runtime.consoleAPICalled":
                    a = m["params"]["args"]
                    if a and str(a[0].get("value", "")).startswith("VCFPS "):
                        j = json.loads(a[0]["value"][6:]); allfps.append(j["fps"])
                        csv.write(f"{time.strftime('%H:%M:%S')},{j['fps']},{j['p99_ms']},{j['frames']}\n"); csv.flush()
            if time.time() >= nxt_shot:
                nxt_shot = time.time() + 60
                subprocess.run(["grim", f"{OUT}/screenshots/{time.strftime('%H%M%S')}.png"], env=env, capture_output=True)
    return allfps
sysrun = None
async def runner():
    t = asyncio.create_task(sysloop())
    try: return await main()
    finally: t.cancel()
try: allfps = asyncio.run(runner()) or []
except Exception as e: allfps = []; print("error:", e)
stop = True
try: os.killpg(chrom.pid, signal.SIGTERM)
except ProcessLookupError: pass
kern.terminate(); time.sleep(1)
kl = open(f"{OUT}/kernel.log", errors="replace").read()
hangs = kl.count("recover hung GPU")
s = sorted(allfps)
summary = (f"url={URL}\nseconds_with_fps={len(allfps)}\navg_fps={sum(allfps)/len(allfps):.1f}\nmin_fps={s[0]}\nmax_fps={s[-1]}\n"
           f"p5_fps={s[int(len(s)*.05)]}\ngpu_hangs={hangs}\nchromium_exit={chrom.poll()}\n") if allfps else f"no fps samples; gpu_hangs={hangs}\n"
open(f"{OUT}/summary.txt", "w").write(summary); print(summary); shutil.rmtree(PROF, ignore_errors=True)
