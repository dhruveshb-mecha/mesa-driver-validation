#!/usr/bin/env python3
"""qt_apps_analyze.py RUNDIR  -- turns the raw logs written by qt_apps_fps.sh into summary.md / summary.csv / summary.json.

Raw logs are never modified. Definitions (also written into summary.md):
  commit           one `wl_surface#N.commit()` line of WAYLAND_DEBUG=client output (one presented frame of that surface).
  active phase     the scripted-interaction window (active_start..active_end in phases.txt).
  surface          the Wayland surface with the most commits in the active phase (the app's main drawing surface).
  active fps       commits on that surface / active phase seconds (average over the whole window, idle gaps included).
  busy fps         1000 / median interval between consecutive commits whose gap is < 100 ms, i.e. while the app is
                   continuously redrawing. The panel's vblank rate is the ceiling (see the GTK4 apps run).
  % <= 22 ms       share of busy intervals <= 22 ms (the panel's ~19.7 ms vblank period plus jitter).
  % > 25 ms        share of busy intervals above 25 ms (frames slower than 40 fps).
  GPU              the app tree held a DRM client of /dev/dri/renderD128 (etnaviv) at the end of the active phase and
                   mapped Mesa libgallium. Qt Widgets apps paint on the CPU into shared memory by design (no GPU client).
"""
import csv, json, os, re, statistics, sys

run = sys.argv[1]
COMMIT = re.compile(r'\[(\d\d):(\d\d):(\d\d\.\d+)\][^\n]*?-> wl_surface#(\d+)\.commit\(\)')


def secs(hms):
    h, m, x = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + float(x)


def read_phases(p):
    d = {}
    for l in open(p):
        if '=' in l:
            k, v = l.strip().split('=', 1)
            try:
                d[k] = secs(v)
            except ValueError:
                pass
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
    ph = read_phases(os.path.join(D, 'phases.txt')) if os.path.exists(os.path.join(D, 'phases.txt')) else {}
    commits = {}
    for m in COMMIT.finditer(raw):
        commits.setdefault(int(m.group(4)), []).append((int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))) * 1000.0)
    r['commits_total'] = sum(len(v) for v in commits.values())
    if 'active_start' in ph and 'active_end' in ph and commits:
        a0, a1 = ph['active_start'] * 1000.0, ph['active_end'] * 1000.0
        act = {s: [t for t in v if a0 <= t <= a1] for s, v in commits.items()}
        sid = max(act, key=lambda s: len(act[s]))
        ts = act[sid]
        dur = max(0.001, (a1 - a0) / 1000.0)
        r['active_s'] = round(dur, 1)
        r['surfaces'] = len([s for s in act if len(act[s]) > 5])
        r['active_commits'] = len(ts)
        r['active_fps'] = round(len(ts) / dur, 1)
        busy = [b - a for a, b in zip(ts, ts[1:]) if b - a < 100]
        r['busy_frames'] = len(busy)
        if busy:
            med = statistics.median(busy)
            r['busy_median_ms'] = round(med, 1)
            r['busy_p95_ms'] = round(pct(busy, 0.95), 1)
            r['busy_fps'] = round(1000.0 / med, 1)
            r['pct_le_22'] = round(100.0 * sum(1 for x in busy if x <= 22.0) / len(busy), 1)
            r['pct_over_25ms'] = round(100.0 * sum(1 for x in busy if x > 25.0) / len(busy), 1)
    m_path = os.path.join(D, 'metrics.csv')
    drm_clients = 0
    if os.path.exists(m_path):
        cpu, sysb, mem, drmn, rss = [], [], [], [], []
        for row in csv.DictReader(open(m_path)):
            mem.append(float(row['drm_total_mem_mib'])); drmn.append(int(row['drm_clients'])); rss.append(float(row['rss_mb']))
            cpu.append(float(row['app_cpu_pct'])); sysb.append(float(row['sys_busy_pct']))
        if cpu:
            r['app_cpu_mean'] = round(statistics.mean(cpu), 0); r['app_cpu_max'] = round(max(cpu), 0)
            r['sys_busy_mean'] = round(statistics.mean(sysb), 0)
            r['rss_peak_mb'] = round(max(rss), 0)
        r['drm_clients_max'] = max(drmn) if drmn else 0
        r['drm_mem_peak_mib'] = round(max(mem), 0) if mem else 0
        drm_clients = r['drm_clients_max']
    libs = open(os.path.join(D, 'gpu-libs.txt')).read() if os.path.exists(os.path.join(D, 'gpu-libs.txt')) else ''
    gall = 'libgallium' in libs
    soft = bool(re.search(r'llvmpipe|swrast|softpipe', libs + '\n'.join(l for l in raw.splitlines() if 'Physical device' not in l)))
    r['uses_gl_libs'] = 'yes' if re.search(r'libEGL|libGLESv2|libGL\.so', libs) else 'no'
    if not commits or (r.get('active_commits', 0) == 0 and drm_clients == 0):
        r['gpu'] = 'n/a (no frames drawn)'
    elif drm_clients > 0 and gall and not soft:
        r['gpu'] = 'YES'
    elif drm_clients == 0:
        r['gpu'] = 'NO (CPU raster)'
    else:
        r['gpu'] = 'UNCONFIRMED'
    iso = open(os.path.join(D, 'isolation.txt')).read() if os.path.exists(os.path.join(D, 'isolation.txt')) else ''
    m = re.search(r'screen_cleared=(\w+) windows_left=(\d+) cpu_idle_pct=(\d+)', iso)
    r['isolated'] = 'yes' if (m and m.group(1) == 'yes' and m.group(2) == '0') else 'NO'
    r['idle_before'] = m.group(3) if m else '?'
    mx = re.search(r'extra_windows_after:\n((?:\d+ .*\n)*)extra_windows_end', iso)
    r['foreign_windows_left'] = len([l for l in mx.group(1).splitlines() if l.strip()]) if mx else 0
    r['foreign_windows_handled'] = len(re.findall(r'^handled:', iso, re.M))
    if r['foreign_windows_left']:
        r['isolated'] = 'NO'
    kern = open(os.path.join(D, 'kernel.txt')).read() if os.path.exists(os.path.join(D, 'kernel.txt')) else ''
    kl = [l for l in kern.splitlines() if l and not l.startswith('#') and 'No coredumps' not in l]
    r['gpu_hangs'] = len([l for l in kl if re.search(r'recover hung GPU|etnaviv.*(timeout|fault)|gpu.*(hang|timeout|fault)', l, re.I)])
    r['segfault'] = len([l for l in kl if re.search(r'segfault', l, re.I)])
    r['app_killed'] = 'yes' if re.search(r'\bKilled\b', raw) else 'no'
    r['coredump'] = 'no' if 'No coredumps' in kern else 'CHECK'
    errs = re.findall(r'(?:Failed to create (?:EGL )?context[^\n]*|EGL_BAD_[A-Z_]+|shader[^\n]*(?:error|fail)[^\n]*|Cannot create[^\n]*)', raw, re.I)
    r['gl_errors'] = len(errs)
    r['notes'] = open(os.path.join(D, 'notes.txt')).read().strip() if os.path.exists(os.path.join(D, 'notes.txt')) else ''
    if not commits and not r['notes']:
        r['notes'] = 'no wl_surface.commit logged (no window or app exited)'
    rows.append(r)

cols = ['app', 'gpu', 'uses_gl_libs', 'isolated', 'idle_before', 'surfaces', 'active_s', 'active_commits', 'active_fps', 'busy_frames', 'busy_median_ms',
        'busy_p95_ms', 'busy_fps', 'pct_le_22', 'pct_over_25ms', 'app_cpu_mean', 'app_cpu_max', 'sys_busy_mean', 'foreign_windows_handled',
        'foreign_windows_left', 'rss_peak_mb', 'app_killed', 'drm_clients_max', 'drm_mem_peak_mib', 'gpu_hangs', 'segfault', 'coredump', 'gl_errors', 'notes']
with open(os.path.join(run, 'summary.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, cols, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
json.dump(rows, open(os.path.join(run, 'summary.json'), 'w'), indent=1)

info = open(os.path.join(run, 'run-info.txt')).read() if os.path.exists(os.path.join(run, 'run-info.txt')) else ''
def g(r, k): return '-' if r.get(k) is None else str(r.get(k))
with open(os.path.join(run, 'summary.md'), 'w') as f:
    f.write('# Qt apps on the Comet: GPU use and frame rate\n\n```\n' + info + '```\n\n')
    f.write('| app | on GPU | busy fps (median) | % busy frames <= 22 ms | % > 25 ms | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | GL errors | notes |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        f.write('| %s | %s | %s | %s | %s | %s | %s | %s/%s | %s | %s | %s (idle %s%%) | %s | %s | %s |\n' % (
            r['app'], r['gpu'], g(r, 'busy_fps'), g(r, 'pct_le_22'), g(r, 'pct_over_25ms'), g(r, 'busy_p95_ms'), g(r, 'active_fps'),
            g(r, 'app_cpu_mean'), g(r, 'app_cpu_max'), g(r, 'rss_peak_mb'), g(r, 'drm_mem_peak_mib'), r['isolated'], r['idle_before'],
            r['gpu_hangs'], r['gl_errors'], r['notes'].replace('\n', ' ')))
    f.write('\nDefinitions' + __doc__.split('Definitions', 1)[1])
print(open(os.path.join(run, 'summary.md')).read())
