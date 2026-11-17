#!/usr/bin/env python3
"""gtk4_apps_analyze.py RUNDIR  -- turns the raw logs written by gtk4_apps_fps.sh into summary.md / summary.csv.

Raw logs are never modified. Definitions (also written into summary.md):
  frame            one line of GDK_DEBUG=frames output ("Gdk-Message: HH:MM:SS.mmm: N: interval=..").
  active phase     the scripted-interaction window (active_start..active_end in phases.txt).
  active fps       frames in the active phase / active phase seconds (average over the whole window, idle gaps included).
  busy fps         1000 / median frame interval over frames whose interval is < 100 ms, i.e. while the app is
                   continuously redrawing (scrolling/animating). This is the number to compare with 60.
  % at 60 Hz pace  share of those busy frames with interval <= 18.0 ms (60 Hz = 16.7 ms).
  % at display pace share of those busy frames with interval <= 1.1 x the measured real vblank period (vblank-measurement.txt).
  GPU              GskGLRenderer in use + /dev/dri/renderD128 (etnaviv) held by the app tree + no software renderer.
"""
import csv, json, os, re, statistics, sys

run = sys.argv[1]
VB = None  # measured real vblank period (ms) of the display, from vblank-measurement.txt (period_ms=..)
try:
    VB = float(re.search(r'period_ms=([\d.]+)', open(os.path.join(run, 'vblank-measurement.txt')).read()).group(1))
except Exception:
    pass
FRAME = re.compile(r'Gdk-Message: (\d\d):(\d\d):(\d\d\.\d+): +(\d+): (?:interval=\s*([\d.]+))?')


def secs(hms):
    h, m, s = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def read_phases(p):
    d = {}
    for l in open(p):
        if '=' in l:
            k, v = l.strip().split('=', 1)
            d[k] = secs(v)
    return d


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))] if v else None


rows = []
apps = [d for d in sorted(os.listdir(run)) if os.path.isfile(os.path.join(run, d, 'raw.log'))]
for app in apps:
    D = os.path.join(run, app)
    raw = open(os.path.join(D, 'raw.log'), errors='replace').read()
    r = {'app': app}
    rend = re.findall(r"Using renderer '([A-Za-z]+)'", raw)
    r['renderer'] = ','.join(sorted(set(rend))) or 'none-logged'
    soft = bool(re.search(r'llvmpipe|swrast|softpipe|Failed to realize|GskCairoRenderer', raw))
    egl = 'Device: /dev/dri/renderD128' in raw
    gles = re.search(r'OpenGL ES version: ([\d.]+)', raw)
    r['gl'] = ('GLES ' + gles.group(1)) if gles else ('EGL' if egl else 'none-logged')
    # frames
    frames = []
    for m in FRAME.finditer(raw):
        t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        frames.append((t, float(m.group(5)) if m.group(5) else None))
    ph = read_phases(os.path.join(D, 'phases.txt')) if os.path.exists(os.path.join(D, 'phases.txt')) else {}
    r['frames_total'] = len(frames)
    if 'active_start' in ph and 'active_end' in ph:
        a0, a1 = ph['active_start'], ph['active_end']
        act = [f for f in frames if a0 <= f[0] <= a1]
        dur = max(0.001, a1 - a0)
        r['active_s'] = round(dur, 1)
        r['active_frames'] = len(act)
        r['active_fps'] = round(len(act) / dur, 1)
        busy = [f[1] for f in act if f[1] is not None and f[1] < 100]
        r['busy_frames'] = len(busy)
        if busy:
            med = statistics.median(busy)
            r['busy_median_ms'] = round(med, 1)
            r['busy_p95_ms'] = round(pct(busy, 0.95), 1)
            r['busy_fps'] = round(1000.0 / med, 1)
            r['pct_at_60'] = round(100.0 * sum(1 for x in busy if x <= 18.0) / len(busy), 1)
            r['pct_over_25ms'] = round(100.0 * sum(1 for x in busy if x > 25.0) / len(busy), 1)
            if VB:
                r['pct_at_display'] = round(100.0 * sum(1 for x in busy if x <= VB * 1.1) / len(busy), 1)
        # frames after the settle phase but outside active (idle) are not counted
        s0, s1 = ph.get('window', a0), ph.get('settle_end', a0)
        r['settle_frames'] = len([f for f in frames if s0 <= f[0] <= s1])
    # metrics
    m_path = os.path.join(D, 'metrics.csv')
    drm_clients = 0
    if os.path.exists(m_path) and 'active_start' in ph:
        cpu, sysb, mem, drmn = [], [], [], []
        for row in csv.DictReader(open(m_path)):
            t = secs(row['hms'])
            if ph['active_start'] <= t <= ph['active_end']:
                cpu.append(float(row['app_cpu_pct'])); sysb.append(float(row['sys_busy_pct']))
            mem.append(float(row['drm_total_mem_mib'])); drmn.append(int(row['drm_clients']))
        if cpu:
            r['app_cpu_mean'] = round(statistics.mean(cpu), 0); r['app_cpu_max'] = round(max(cpu), 0)
            r['sys_busy_mean'] = round(statistics.mean(sysb), 0)
        r['drm_clients_max'] = max(drmn) if drmn else 0
        r['rss_peak_mb'] = round(max(float(x['rss_mb']) for x in csv.DictReader(open(m_path))), 0)
        r['drm_mem_peak_mib'] = round(max(mem), 0) if mem else 0
        drm_clients = r['drm_clients_max']
    gpu = ('GskGL' in r['renderer'] or 'NGL' in r['renderer'].upper()) and egl and drm_clients > 0 and not soft
    r['gpu'] = 'YES' if gpu else ('NO' if soft or (rend and 'GL' not in r['renderer']) else 'UNCONFIRMED')
    # isolation + kernel
    iso = open(os.path.join(D, 'isolation.txt')).read() if os.path.exists(os.path.join(D, 'isolation.txt')) else ''
    m = re.search(r'screen_cleared=(\w+) windows_left=(\d+) cpu_idle_pct=(\d+)', iso)
    r['isolated'] = 'yes' if (m and m.group(1) == 'yes' and m.group(2) == '0') else 'NO'
    r['idle_before'] = m.group(3) if m else '?'
    mx = re.search(r'extra_windows_after:\n((?:\d+ .*\n)*)extra_windows_end', iso)
    r['foreign_windows_left'] = len([l for l in mx.group(1).splitlines() if l.strip()]) if mx else 0
    r['foreign_windows_handled'] = len(re.findall(r'^handled:', iso, re.M))
    if r['foreign_windows_left']:
        r['isolated'] = 'NO'
    m2 = re.search(r'after_launch_windows \((\d+)\)', iso)
    r['windows'] = m2.group(1) if m2 else '?'
    kern = open(os.path.join(D, 'kernel.txt')).read() if os.path.exists(os.path.join(D, 'kernel.txt')) else ''
    kl = [l for l in kern.splitlines() if l and not l.startswith('#') and 'No coredumps' not in l]
    r['kernel_hits'] = len([l for l in kl if re.search(r'hung|segfault|etnaviv.*(timeout|fault)|gpu.*(hang|timeout|fault)', l, re.I)])
    r['app_killed'] = 'yes (OOM)' if re.search(r'\bKilled\b', raw) and 'oom' in open(os.path.join(D, 'notes.txt')).read().lower() else ('yes' if re.search(r'\bKilled\b', raw) else 'no')
    r['coredump'] = 'no' if 'No coredumps' in kern else 'CHECK'
    r['notes'] = open(os.path.join(D, 'notes.txt')).read().strip() if os.path.exists(os.path.join(D, 'notes.txt')) else ''
    if not frames and not r['notes']:
        r['notes'] = 'no frame-clock lines logged (app idle or no window)'
    rows.append(r)

cols = ['app', 'gpu', 'renderer', 'gl', 'isolated', 'idle_before', 'windows', 'active_s', 'active_frames', 'active_fps',
        'busy_frames', 'busy_median_ms', 'busy_p95_ms', 'busy_fps', 'pct_at_60', 'pct_at_display', 'pct_over_25ms', 'app_cpu_mean', 'app_cpu_max',
        'sys_busy_mean', 'foreign_windows_handled', 'foreign_windows_left', 'rss_peak_mb', 'app_killed', 'drm_clients_max', 'drm_mem_peak_mib', 'kernel_hits', 'coredump', 'notes']
with open(os.path.join(run, 'summary.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, cols, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
json.dump(rows, open(os.path.join(run, 'summary.json'), 'w'), indent=1)

info = open(os.path.join(run, 'run-info.txt')).read() if os.path.exists(os.path.join(run, 'run-info.txt')) else ''
def g(r, k): return '-' if r.get(k) is None else str(r.get(k))
with open(os.path.join(run, 'summary.md'), 'w') as f:
    f.write('# GTK4 apps on the Comet: GPU use and frame rate\n\n```\n' + info + '```\n\n')
    f.write('| app | on GPU | renderer | busy fps (median) | % frames at 60 Hz pace | % frames at display pace | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | app killed | notes |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        f.write('| %s | %s | %s | %s | %s | %s | %s | %s | %s/%s | %s | %s | %s (idle %s%%) | %s | %s | %s |\n' % (
            r['app'], r['gpu'], r['renderer'], g(r, 'busy_fps'), g(r, 'pct_at_60'), g(r, 'pct_at_display'), g(r, 'busy_p95_ms'), g(r, 'active_fps'),
            g(r, 'app_cpu_mean'), g(r, 'app_cpu_max'), g(r, 'rss_peak_mb'), g(r, 'drm_mem_peak_mib'), r['isolated'], r['idle_before'], r['kernel_hits'], r['app_killed'], r['notes'].replace('\n', ' ')))
    f.write('\nDefinitions' + __doc__.split('Definitions', 1)[1])
print(open(os.path.join(run, 'summary.md')).read())
