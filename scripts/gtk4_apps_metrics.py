#!/usr/bin/env python3
"""gtk4_apps_metrics.py PID OUT.csv  -- 1 Hz sampler, run on the board next to one app.

Per second: wall time, whole-system CPU busy %, CPU % of the app's process tree (100 = one core),
RSS of the tree, number of processes, how many DRM clients of /dev/dri/renderD128 (etnaviv) the tree
holds and the total GPU-visible memory they report in fdinfo (drm-total-memory).
Stops when the PID is gone or when killed.
"""
import os, sys, time

pid = int(sys.argv[1])
out = sys.argv[2]
HZ = os.sysconf('SC_CLK_TCK')
RENDER = '/dev/dri/renderD128'


def proc_tree(root):
    kids = {}
    for d in os.listdir('/proc'):
        if d.isdigit():
            try:
                with open(f'/proc/{d}/stat') as f:
                    s = f.read()
                ppid = int(s.rsplit(')', 1)[1].split()[1])
                kids.setdefault(ppid, []).append(int(d))
            except Exception:
                pass
    res = [root]
    i = 0
    while i < len(res):
        res += kids.get(res[i], [])
        i += 1
    return res


def ticks(p):
    try:
        f = open(f'/proc/{p}/stat').read().rsplit(')', 1)[1].split()
        return int(f[11]) + int(f[12])
    except Exception:
        return 0


def rss_kib(p):
    try:
        for l in open(f'/proc/{p}/status'):
            if l.startswith('VmRSS:'):
                return int(l.split()[1])
    except Exception:
        pass
    return 0


def sys_times():
    f = open('/proc/stat').readline().split()[1:]
    v = list(map(int, f))
    idle = v[3] + v[4]
    return sum(v), idle


def drm(procs):
    clients = {}
    for p in procs:
        try:
            fds = os.listdir(f'/proc/{p}/fd')
        except Exception:
            continue
        for fd in fds:
            try:
                if os.readlink(f'/proc/{p}/fd/{fd}') != RENDER:
                    continue
                cid, mem = None, 0
                for l in open(f'/proc/{p}/fdinfo/{fd}'):
                    if l.startswith('drm-client-id:'):
                        cid = (p, l.split()[1])
                    elif l.startswith('drm-total-memory:'):
                        mem = int(l.split()[1])
                if cid is not None:
                    clients[cid] = mem
            except Exception:
                pass
    return len(clients), sum(clients.values()) / 1024.0


with open(out, 'w') as o:
    o.write('epoch,hms,sys_busy_pct,app_cpu_pct,rss_mb,nproc,drm_clients,drm_total_mem_mib\n')
    o.flush()
    last_tot, last_idle = sys_times()
    last_app = {}
    last_t = time.time()
    while True:
        time.sleep(1.0)
        if not os.path.exists(f'/proc/{pid}'):
            break
        t = time.time()
        procs = proc_tree(pid)
        tot, idle = sys_times()
        busy = 100.0 * (1 - (idle - last_idle) / max(1, tot - last_tot))
        last_tot, last_idle = tot, idle
        cur = {p: ticks(p) for p in procs}
        dt = t - last_t
        app = sum(max(0, cur[p] - last_app.get(p, cur[p])) for p in procs) / HZ / dt * 100.0
        last_app, last_t = cur, t
        rss = sum(rss_kib(p) for p in procs) / 1024.0
        n, mem = drm(procs)
        o.write('%.3f,%s,%.1f,%.1f,%.1f,%d,%d,%.1f\n' % (
            t, time.strftime('%H:%M:%S', time.localtime(t)), busy, app, rss, len(procs), n, mem))
        o.flush()
