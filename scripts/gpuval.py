#!/usr/bin/env python3
"""Mecha Comet GPU validation runner.

  gpuval.py sysinfo [--run-id ID]
  gpuval.py run  [--label L] [--run-id ID] [--phase N] [--category C] [--id REGEX]
                 [--skip-risky] [--es3-override] [--list] [--tester NAME]
  gpuval.py mark RUN_ID TEST_ID PASS|FAIL|PARTIAL|SKIP|N/A "note" [screenshot]
  gpuval.py report RUN_ID [BASELINE_RUN_ID]

Every run lives in runs/<run-id>/ and is append-only. Re-running with the same --run-id resumes:
tests that already have a result are skipped, and a test that was in flight when the board
rebooted is recorded as BOARD_RESET (with the previous boot's kernel log saved)."""
import argparse, datetime, glob, hashlib, json, os, platform, re, shutil, signal, subprocess, sys, time
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
HANG_RE = re.compile(r"etnaviv.*(hang|fault|timeout|reset|recover|error)|gpu hang|GPU .*(hung|reset)|Oops|Call trace|Internal error", re.I)
PASSING = {"PASS", "RAN_OK"}

def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (p.stdout + p.stderr).strip()
    except Exception as e:
        return f"ERROR: {e}"

def now(): return datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
def boot_id(): return Path("/proc/sys/kernel/random/boot_id").read_text().strip()

def append_jsonl(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n"); f.flush(); os.fsync(f.fileno())

def read_jsonl(path):
    if not Path(path).exists(): return []
    return [json.loads(l) for l in open(path) if l.strip()]

def load_manifest():
    tests = []
    for f in sorted((ROOT / "manifest" / "tests").glob("*.yaml")):
        for t in yaml.safe_load(open(f)) or []:
            t.setdefault("category", f.stem); t.setdefault("type", "auto"); t.setdefault("phase", 1)
            t.setdefault("timeout", 120); t.setdefault("risk", "low"); t.setdefault("tags", [])
            t.setdefault("requires", []); t.setdefault("expected", "pass"); t["_file"] = f.name
            tests.append(t)
    ids = [t["id"] for t in tests]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup: sys.exit(f"duplicate test ids: {dup}")
    return tests

def manifest_hash():
    h = hashlib.sha256()
    for f in sorted((ROOT / "manifest").rglob("*.yaml")): h.update(f.read_bytes())
    return h.hexdigest()[:12]

def base_env(es3_override, keep_env=False):
    env = dict(os.environ)
    cfg = yaml.safe_load(open(ROOT / "manifest" / "env.yaml"))
    if not keep_env:
        for k in cfg.get("unset", []): env.pop(k, None)
    env.update({k: str(v) for k, v in cfg.get("set", {}).items()})
    if es3_override: env["MESA_GLES_VERSION_OVERRIDE"] = "3.0"
    env["GPUVAL_ROOT"] = str(ROOT)
    return env

def kernel_log(start, end, boot=None):
    b = f"-b {boot}" if boot is not None else ""
    out = sh(f'journalctl -k {b} --since "@{int(start)}" --until "@{int(end)+2}" -o short-precise --no-pager 2>&1')
    if "No journal" in out or out.startswith("ERROR"):
        out = sh("dmesg 2>&1 | tail -200")
    return out

# ------------------------------------------------------------------ sysinfo
def display_mode():
    try:
        o = json.loads(sh("swaymsg -t get_outputs -r 2>/dev/null"))[0]; m = o["current_mode"]
        return f"{o['name']} {m['width']}x{m['height']}@{m['refresh']/1000:.0f}Hz scale={o.get('scale')}"
    except Exception: return "unknown"

def cmd_sysinfo(run_dir):
    d = run_dir / "sysinfo"; d.mkdir(parents=True, exist_ok=True)
    items = {
        "uname": "uname -a", "os-release": "cat /etc/os-release", "lscpu": "lscpu",
        "dri": "ls -l /dev/dri/ /dev/video* /dev/media* 2>&1",
        "mesa-packages": "rpm -qa | grep -Ei '^(mesa|libdrm|libglvnd|vulkan|wayland|sway|gtk4|qt6-qtbase-[0-9]|qt6-qtdeclarative-[0-9]|chromium|gstreamer1-[a-z-]*-[0-9]|libcamera|mechanix)' | sort",
        "mesa-rpm-info": "rpm -qi mesa-dri-drivers",
        "kernel-gpu": "journalctl -k -b 0 --no-pager 2>&1 | grep -Ei 'etnaviv|vivante|galcore|drm|hantro|imx219|imx-' | head -80",
        "modules": "lsmod | grep -Ei 'etnaviv|gpu|drm|hantro|v4l2|imx'",
        "gpu-probe": f"python3 {ROOT/'scripts'/'gles3_probe.py'}",
        "vulkaninfo": "vulkaninfo --summary 2>&1 | head -40",
        "sway-outputs": "swaymsg -t get_outputs 2>&1 | grep -E 'name|current_mode|width|height|refresh|scale' | head -20",
        "devfreq": "for d in /sys/class/devfreq/*; do echo $d; cat $d/cur_freq 2>&1; cat $d/available_frequencies 2>&1; done",
        "thermal": "for z in /sys/class/thermal/thermal_zone*; do echo $z $(cat $z/type) $(cat $z/temp); done",
        "memory": "free -h; df -h /",
        "boots": "journalctl --list-boots --no-pager | tail -5",
        "gst-gl-plugins": "gst-inspect-1.0 2>/dev/null | grep -Ei 'opengl:|v4l2codecs|libcamera|gtkwayland' | head -40",
        "env-relevant": "env | grep -Ei '^(MESA|ETNA|EGL|GALLIUM|LIBGL|GSK|GDK|QT_|QSG|WGPU|WAYLAND|XDG_)' | sort",
    }
    for name, c in items.items():
        (d / f"{name}.txt").write_text(f"$ {c}\n\n" + sh(c, 120) + "\n")
    probe = {}
    try: probe = json.loads(sh(f"python3 {ROOT/'scripts'/'gles3_probe.py'} 2>/dev/null"))
    except Exception: pass
    meta = {
        "host": platform.node(), "kernel": platform.release(), "boot_id": boot_id(),
        "mesa_rpm": sh("rpm -q --qf '%{VERSION}-%{RELEASE}' mesa-dri-drivers"),
        "gl_version": probe.get("info", {}).get("version"), "gl_renderer": probe.get("info", {}).get("renderer"),
        "os": re.search(r'PRETTY_NAME="?([^"\n]+)', open("/etc/os-release").read()).group(1),
        "chromium": sh("chromium-browser --version 2>/dev/null | head -1"),
        "gtk4": sh("rpm -q --qf '%{VERSION}' gtk4"), "qt6": sh("rpm -q --qf '%{VERSION}' qt6-qtbase"),
        "gstreamer": sh("gst-launch-1.0 --version 2>/dev/null | head -1"),
        "display": display_mode(),
    }
    sw = [l for l in meta["gl_renderer"].lower().split()] if meta["gl_renderer"] else []
    meta["software_rendering"] = any(x in (meta["gl_renderer"] or "").lower() for x in ("llvmpipe", "softpipe", "swrast"))
    return meta

# ------------------------------------------------------------------ run
def select(tests, a):
    out = []
    for t in tests:
        if a.phase and t["phase"] > a.phase: continue
        if a.category and t["category"] not in a.category.split(","): continue
        if a.id and not re.search(a.id, t["id"]): continue
        if a.skip_risky and t["risk"] == "high": continue
        out.append(t)
    rank = {"low": 0, "medium": 1, "high": 2}
    return sorted(out, key=lambda t: (rank.get(t["risk"], 0), t["phase"]))   # risky tests last

def thermal():
    out = {}
    for z in glob.glob("/sys/class/thermal/thermal_zone*"):
        try: out[Path(z, "type").read_text().strip()] = int(Path(z, "temp").read_text()) / 1000
        except Exception: pass
    return out

def to_num(v): return float(v) if re.fullmatch(r"-?[\d.]+", v) else v

def compute_metrics(spec, texts):
    m = {}
    for k, rx in (spec or {}).items():
        vals = next((v for v in (re.findall(rx, t) for t in texts) if v), [])   # first source that matches
        if vals: m[k] = to_num(vals[0]) if len(vals) == 1 else [to_num(v) for v in vals]
    return m

def log_texts(run_dir, row):
    tdir = run_dir / row.get("log_dir", "")
    ts = [(tdir / n).read_text(errors="replace") for n in ("stdout.txt", "stderr.txt") if (tdir / n).exists()]
    for f in (tdir / "artifacts").rglob("*.md") if (tdir / "artifacts").exists() else []:
        ts.append(f.read_text(errors="replace"))
    return ts

def snapshot(globs):
    return {p: os.path.getmtime(p) for g in globs for p in glob.glob(os.path.expanduser(g), recursive=True)}

def run_one(t, run_dir, env):
    tdir = run_dir / "logs" / t["category"] / t["id"]; tdir.mkdir(parents=True, exist_ok=True)
    row = {"id": t["id"], "category": t["category"], "type": t["type"], "tags": t["tags"], "expected": t["expected"],
           "risk": t["risk"], "phase": t["phase"], "boot_id": boot_id(), "log_dir": str(tdir.relative_to(run_dir))}
    missing = [r for r in t["requires"] if not shutil.which(r, path=env.get("PATH"))
               and not os.path.exists(os.path.expanduser(r))]
    if t["type"] == "manual":
        (tdir / "steps.txt").write_text(f"{t.get('steps','')}\n\nPASS CRITERIA: {t.get('pass_criteria','')}\n")
        return {**row, "status": "PENDING_MANUAL", "rc": None, "duration_s": 0}
    if missing:
        return {**row, "status": "SKIP_MISSING", "rc": None, "duration_s": 0, "note": f"not installed: {', '.join(missing)}"}
    (tdir / "cmd.txt").write_text(t["cmd"].strip() + "\n")
    collect = snapshot(t.get("collect", []))
    state = run_dir / "inflight.json"
    state.write_text(json.dumps({"id": t["id"], "boot_id": boot_id(), "start": time.time(), "log_dir": row["log_dir"]})); os.sync()
    sh("sync")
    start = time.time(); temp0 = thermal()
    shot_timer = None
    if t.get("run_for") and shutil.which("grim") and not t.get("no_screenshot"):
        import threading
        shot_timer = threading.Timer(max(3, t["timeout"] * 0.6), lambda: subprocess.run(
            ["grim", str(tdir / "screenshot.png")], env=env, capture_output=True))
        shot_timer.start()
    out, err = open(tdir / "stdout.txt", "w"), open(tdir / "stderr.txt", "w")
    p = subprocess.Popen(["bash", "-c", t["cmd"]], stdout=out, stderr=err, env=env, start_new_session=True, cwd=str(ROOT))
    timed_out = False
    def _cleanup(signum, frame):   # runner killed (Ctrl-C, timeout): don't orphan the test's GUI app
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        sys.exit(130)
    signal.signal(signal.SIGTERM, _cleanup); signal.signal(signal.SIGINT, _cleanup)
    try: p.wait(timeout=t["timeout"])
    except subprocess.TimeoutExpired:
        timed_out = True
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try: os.killpg(p.pid, sig)
            except ProcessLookupError: break
            try: p.wait(timeout=8); break
            except subprocess.TimeoutExpired: pass
    end = time.time(); out.close(); err.close()
    if shot_timer: shot_timer.cancel()
    temp1 = thermal()
    rc = p.returncode
    klog = kernel_log(start, end); (tdir / "kernel.txt").write_text(klog + "\n")
    hang = [l for l in klog.splitlines() if HANG_RE.search(l)]
    stdout = (tdir / "stdout.txt").read_text(errors="replace")
    metrics = {}   # recomputed at report time (includes artifact reports)
    arts = []
    for pth, mt in snapshot(t.get("collect", [])).items():
        if pth not in collect or mt > collect[pth]:
            dst = tdir / "artifacts" / os.path.relpath(pth, os.path.expanduser("~")).replace("/", "__").lstrip("._")
            dst.parent.mkdir(exist_ok=True)
            try:
                shutil.copytree(pth, dst) if os.path.isdir(pth) else shutil.copy2(pth, dst); arts.append(str(dst.relative_to(run_dir)))
            except Exception: pass
    if timed_out and t.get("run_for"): status = "RAN_OK"
    elif timed_out: status = "TIMEOUT"
    elif rc == 0: status = "RAN_OK"
    else: status = "RAN_FAIL"
    if t.get("pass_regex") and status == "RAN_OK" and not re.search(t["pass_regex"], stdout + (tdir / "stderr.txt").read_text(errors="replace")): status = "RAN_FAIL"
    if hang: status = "GPU_HANG" if status != "RAN_FAIL" or any("etnaviv" in l.lower() for l in hang) else status
    state.unlink(missing_ok=True)
    return {**row, "status": status, "rc": rc, "timed_out": timed_out, "duration_s": round(end - start, 1),
            "metrics": metrics, "kernel_flags": hang[:10], "artifacts": arts,
            "temp_c_before": temp0, "temp_c_after": temp1,
            "screenshot": "screenshot.png" if (tdir / "screenshot.png").exists() else None}

def recover_inflight(run_dir):
    state = run_dir / "inflight.json"
    if not state.exists(): return
    s = json.loads(state.read_text())
    tdir = run_dir / s["log_dir"]
    prev = kernel_log(s["start"] - 5, s["start"] + 3600, boot="-1") if s["boot_id"] != boot_id() else ""
    (tdir / "kernel_previous_boot.txt").write_text(prev + "\n")
    row = {"id": s["id"], "log_dir": s["log_dir"], "status": "BOARD_RESET", "rc": None, "boot_id": s["boot_id"],
           "note": "board rebooted/crashed while this test was running", "category": s["log_dir"].split("/")[1], "duration_s": None}
    t = next((x for x in load_manifest() if x["id"] == s["id"]), {})
    row.update(tags=t.get("tags", []), expected=t.get("expected", "pass"), risk=t.get("risk"), type="auto", phase=t.get("phase"))
    append_jsonl(run_dir / "results.jsonl", row); state.unlink()
    print(f"!! recovered in-flight test {s['id']}: BOARD_RESET (previous boot kernel log saved)")

def cmd_run(a):
    tests = load_manifest()
    sel = select(tests, a)
    if a.list:
        for t in sel: print(f"{t['phase']} {t['risk']:4} {t['type']:6} {t['id']}")
        return
    rid = a.run_id or f"{now()}_{a.label or 'run'}"
    run_dir = RUNS / rid; run_dir.mkdir(parents=True, exist_ok=True)
    resume = (run_dir / "run.json").exists()
    recover_inflight(run_dir)
    env = base_env(a.es3_override)
    os.environ.update({k: env[k] for k in ("XDG_RUNTIME_DIR", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS") if k in env})
    socks = glob.glob(os.path.join(env.get("XDG_RUNTIME_DIR", ""), "sway-ipc.*.sock"))
    if socks: os.environ["SWAYSOCK"] = env["SWAYSOCK"] = socks[0]
    if not resume:
        meta = cmd_sysinfo(run_dir)
        meta.update(run_id=rid, label=a.label, tester=a.tester or os.environ.get("USER"), started=datetime.datetime.now().isoformat(),
                    manifest_hash=manifest_hash(), runner_git=(sh(f"git -C {ROOT} rev-parse --short HEAD 2>/dev/null") if (ROOT/".git").exists() else None) or (ROOT/".revision").read_text().strip() if (ROOT/".revision").exists() else None,
                    es3_override=a.es3_override, argv=sys.argv)
        (run_dir / "run.json").write_text(json.dumps(meta, indent=1))
        print(f"run {rid}: {meta['mesa_rpm']}  {meta['gl_version']}  {meta['gl_renderer']}")
        if meta["software_rendering"]: sys.exit("ABORT: software renderer detected (llvmpipe) - not testing the GPU")
    done = {r["id"] for r in read_jsonl(run_dir / "results.jsonl")}
    for t in sel:
        if t["id"] in done: continue
        print(f"[{t['category']}] {t['id']} ...", flush=True)
        r = run_one(t, run_dir, base_env(a.es3_override, t.get("keep_env", False)) | {k: v for k, v in env.items() if k == "SWAYSOCK"})
        append_jsonl(run_dir / "results.jsonl", r)
        print(f"    -> {r['status']} {r.get('duration_s')}s {r.get('metrics') or ''} {r.get('note','')}", flush=True)
        time.sleep(t.get("cooldown", 3))
    meta = json.loads((run_dir / "run.json").read_text()); meta["finished"] = datetime.datetime.now().isoformat()
    (run_dir / "run.json").write_text(json.dumps(meta, indent=1))
    sums = []
    for f in sorted(run_dir.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS": sums.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(run_dir)}")
    (run_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    cmd_report(argparse.Namespace(run=rid, baseline=None))

# ------------------------------------------------------------------ mark / report
def cmd_mark(a):
    run_dir = RUNS / a.run; (run_dir / "screenshots").mkdir(exist_ok=True)
    shot = None
    if a.screenshot:
        shot = f"screenshots/{a.test}__{Path(a.screenshot).name}"; shutil.copy2(a.screenshot, run_dir / shot)
    append_jsonl(run_dir / "verdicts.jsonl", {"id": a.test, "verdict": a.verdict, "note": a.note, "screenshot": shot, "at": now()})
    print(f"marked {a.test} = {a.verdict}")

def effective(run_dir):
    res = {r["id"]: r for r in read_jsonl(run_dir / "results.jsonl")}
    spec = {t["id"]: t.get("metrics") for t in load_manifest()}
    for r in res.values():
        if spec.get(r["id"]) and r.get("log_dir"):
            r["metrics"] = compute_metrics(spec[r["id"]], log_texts(run_dir, r))
    for v in read_jsonl(run_dir / "verdicts.jsonl"):
        r = res.setdefault(v["id"], {"id": v["id"], "category": "?", "tags": [], "expected": "pass"})
        r["verdict"], r["vnote"], r["screenshot"] = v["verdict"], v["note"], v["screenshot"]
    return res

def shown(r):
    st = r.get("verdict") or r["status"]
    exp = r.get("expected", "pass")
    if exp != "pass" and st not in PASSING | {"SKIP_MISSING"}:
        return f"{st} (expected: {exp})"
    return st

def cmd_report(a):
    run_dir = RUNS / a.run
    meta = json.loads((run_dir / "run.json").read_text())
    res = effective(run_dir); base = effective(RUNS / a.baseline) if a.baseline else None
    bmeta = json.loads((RUNS / a.baseline / "run.json").read_text()) if a.baseline else None
    L = [f"# GPU validation report: {a.run}", "",
         f"- **Mesa:** `{meta['mesa_rpm']}`  |  **GL:** {meta['gl_version']}  |  **Renderer:** {meta['gl_renderer']}",
         f"- **Kernel:** {meta['kernel']}  |  **OS:** {meta['os']}  |  **Display:** `{meta.get('display')}`",
         f"- **Tester:** {meta.get('tester')}  |  **Runner:** `{meta.get('runner_git')}`  manifest `{meta['manifest_hash']}`  |  ES3 override: {meta['es3_override']}"]
    if bmeta: L.append(f"- **Baseline:** `{a.baseline}` Mesa `{bmeta['mesa_rpm']}`, {bmeta['gl_version']}")
    L.append("")
    cats = {}
    for r in res.values(): cats.setdefault(r["category"], []).append(r)
    L += ["## Summary by category", "", "| Category | Pass | Fail | Hang/Reset | Skipped | Manual pending |", "|---|---|---|---|---|---|"]
    for c, rs in sorted(cats.items()):
        st = [(r.get("verdict") or r["status"]) for r in rs]
        L.append(f"| {c} | {sum(s in PASSING for s in st)} | {sum(s in ('FAIL','RAN_FAIL','TIMEOUT','PARTIAL') for s in st)} | "
                 f"{sum(s in ('GPU_HANG','BOARD_RESET') for s in st)} | {sum(s in ('SKIP','SKIP_MISSING','N/A') for s in st)} | {sum(s == 'PENDING_MANUAL' for s in st)} |")
    tags = {}
    for r in res.values():
        for tg in r.get("tags", []): tags.setdefault(tg, []).append(r)
    if tags:
        L += ["", "## Feature matrix", "", "| Feature tag | Tests | Status |", "|---|---|---|"]
        for tg, rs in sorted(tags.items()):
            L.append(f"| {tg} | {', '.join(r['id'] for r in rs)} | {', '.join(shown(r) for r in rs)} |")
    L += ["", "## All results", "", "| Test | Result | Time | Metrics | " + ("Baseline | " if base else "") + "Logs / notes |", "|---|---|---|" + "---|" * (2 if base else 1) + "---|"]
    for tid, r in sorted(res.items(), key=lambda kv: (kv[1]["category"], kv[0])):
        m = ", ".join(f"{k}={(v if not isinstance(v, list) else (str(v[:3]) + '..' + f'({len(v)})' if len(v) > 4 else v))}" for k, v in (r.get("metrics") or {}).items())
        if r.get("temp_c_after"): m += f" T={max(r['temp_c_after'].values()):.0f}C"
        if r.get("screenshot"):
            sp = r["screenshot"] if (run_dir / r["screenshot"]).exists() else f"{r['log_dir']}/{r['screenshot']}"
            m += f" [shot]({sp})"
        note = (r.get("vnote") or r.get("note") or "") + (" ⚠ " + r["kernel_flags"][0][-120:] if r.get("kernel_flags") else "")
        b = shown(base[tid]) if base and tid in base else ("-" if base else None)
        L.append(f"| `{tid}` | {shown(r)} | {r.get('duration_s','')} | {m} | " + (f"{b} | " if base else "") + f"`{r.get('log_dir','')}` {note} |")
    (run_dir / "REPORT.md").write_text("\n".join(L) + "\n"); print(f"report: {run_dir/'REPORT.md'}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("--label"); r.add_argument("--run-id"); r.add_argument("--phase", type=int)
    r.add_argument("--category"); r.add_argument("--id"); r.add_argument("--skip-risky", action="store_true")
    r.add_argument("--es3-override", action="store_true"); r.add_argument("--list", action="store_true"); r.add_argument("--tester")
    m = sp.add_parser("mark"); [m.add_argument(x) for x in ("run", "test", "verdict", "note")]; m.add_argument("screenshot", nargs="?")
    p = sp.add_parser("report"); p.add_argument("run"); p.add_argument("baseline", nargs="?")
    s = sp.add_parser("sysinfo"); s.add_argument("--run-id", default="sysinfo-" + now())
    a = ap.parse_args()
    if a.cmd == "run": cmd_run(a)
    elif a.cmd == "mark": cmd_mark(a)
    elif a.cmd == "report": cmd_report(a)
    elif a.cmd == "sysinfo": d = RUNS / a.run_id; d.mkdir(parents=True, exist_ok=True); print(json.dumps(cmd_sysinfo(d), indent=1))

if __name__ == "__main__": main()
