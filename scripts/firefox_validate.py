#!/usr/bin/env python3
"""Firefox counterpart of the Chromium validators (scripts run on the Comet).

Drives Firefox over Marionette (built in; no geckodriver needed) and runs:
  support      - about:support graphics section (renderer, WebGL, compositor, blocklist reasons)
  probe        - assets/webgl2-probe.html (render targets, MSAA, transform feedback)
  load         - WebGL vertex-load page, same as bench-webgl (200 / 1000 vertices)   [--load N]
  conformance  - same sampled Khronos WebGL tests as validate_full.py
  aquarium     - WebGL Aquarium fps (GPU only; Firefox has no SwiftShader switch)
Usage: firefox_validate.py OUTDIR [support] [probe] [conformance] [aquarium]   (default: all)
Output: OUTDIR/firefox-validation.json + firefox-validation.md + screenshots.
"""
import base64, json, os, socket, subprocess, sys, time, urllib.request, shutil

out = sys.argv[1]
phases = [a for a in sys.argv[2:] if not a.startswith('-')] or ['support', 'probe', 'conformance', 'aquarium']
os.makedirs(out, exist_ok=True)
R = {}
HERE = os.path.dirname(os.path.abspath(__file__))
def save(): json.dump(R, open(f'{out}/firefox-validation.json', 'w'), indent=1)
def say(*a): print(*a, flush=True)

PREFS = """
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("startup.homepage_welcome_url", "");
user_pref("startup.homepage_welcome_url.additional", "");
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("browser.tabs.warnOnClose", false);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("browser.startup.page", 0);
user_pref("app.update.enabled", false);
user_pref("privacy.reduceFingerprinting", false);
"""

class Marionette:
    def __init__(self, port=2828, timeout=60):
        t0 = time.time()
        while True:
            try: self.s = socket.create_connection(('127.0.0.1', port), 3); break
            except OSError:
                if time.time() - t0 > timeout: raise
                time.sleep(1)
        self.s.settimeout(120); self.id = 0; self.buf = b''; self._read()   # hello
        self.cmd('WebDriver:NewSession', {'capabilities': {}})
        self.cmd('WebDriver:SetTimeouts', {'script': 30000, 'pageLoad': 60000})
    def _read(self):
        while b':' not in self.buf: self.buf += self.s.recv(65536)
        n, rest = self.buf.split(b':', 1); n = int(n)
        while len(rest) < n: rest += self.s.recv(65536)
        self.buf = rest[n:]; return json.loads(rest[:n])
    def cmd(self, name, params=None):
        self.id += 1; m = json.dumps([0, self.id, name, params or {}]).encode()
        self.s.sendall(str(len(m)).encode() + b':' + m)
        while True:
            r = self._read()
            if r[0] == 1 and r[1] == self.id:
                if r[2]: raise RuntimeError(f"{name}: {r[2]}")
                return r[3]
    def go(self, url): self.cmd('WebDriver:Navigate', {'url': url})
    def js(self, script, args=None):
        r = self.cmd('WebDriver:ExecuteScript', {'script': script, 'args': args or []}); return r.get('value') if isinstance(r, dict) else r
    def shot(self, path):
        r = self.cmd('WebDriver:TakeScreenshot', {'full': False}); open(path, 'wb').write(base64.b64decode(r['value']))
    def new_tab(self, url='about:blank'):
        r = self.cmd('WebDriver:NewWindow', {'type': 'tab'}); self.cmd('WebDriver:SwitchToWindow', {'handle': r['handle']}); self.go(url); return r['handle']
    def close_tab(self, h):
        hs = self.cmd('WebDriver:CloseWindow');
        if hs: self.cmd('WebDriver:SwitchToWindow', {'handle': hs[0] if isinstance(hs[0], str) else hs[0].get('handle')})

class Firefox:
    def __init__(self, tag, extra_env=None):
        self.prof = f'/tmp/ffprof-{tag}'; shutil.rmtree(self.prof, ignore_errors=True); os.makedirs(self.prof)
        open(f'{self.prof}/user.js', 'w').write(PREFS)
        env = os.environ | {'MOZ_ENABLE_WAYLAND': '1', 'MOZ_REMOTE_ALLOW_SYSTEM_ACCESS': '1'} | (extra_env or {})
        self.log = open(f'{out}/firefox-{tag}.log', 'w')
        self.p = subprocess.Popen(['firefox', '--new-instance', '--no-remote', '--profile', self.prof, '--marionette', 'about:blank'],
                                  env=env, stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        self.m = Marionette()
    def stop(self):
        try: self.m.cmd('Marionette:Quit', {'flags': ['eForceQuit']})
        except Exception: pass
        try: self.p.wait(10)
        except Exception: os.killpg(self.p.pid, 9)

# ------------------------------------------------------------------ about:support
def phase_support():
    """about:support can't be navigated by Marionette; read the same Troubleshoot snapshot in chrome context."""
    import re
    ff = Firefox('support'); m = ff.m
    try:
        time.sleep(3)
        m.cmd('Marionette:SetContext', {'value': 'chrome'})
        snap = m.js("""const {Troubleshoot}=ChromeUtils.importESModule("resource://gre/modules/Troubleshoot.sys.mjs");
            return Troubleshoot.snapshot().then(s=>JSON.stringify({version:s.application.version, graphics:s.graphics}));""")
        m.cmd('Marionette:SetContext', {'value': 'content'})
        g = json.loads(snap); json.dump(g, open(f'{out}/about-support-graphics.json', 'w'), indent=1)
        gr = g['graphics']
        pick = {k: gr[k] for k in gr if re.search(r'Renderer|Vendor|Driver|WebGL|Compositor|Window|Protocol|WebRender|Acceler|Failure|Blocklist|Device|EGL|GLX|wayland|DMABUF|Hardware', k, re.I)}
        txt = json.dumps(gr)
        R['support'] = dict(firefox=g['version'], software_gl=bool(re.search(r'llvmpipe|softpipe|swrast', txt, re.I)), **{k: (v if isinstance(v, (str, int, float, bool)) or v is None else json.dumps(v)[:300]) for k, v in pick.items()})
        for k, v in list(R['support'].items())[:25]: say(f'  {k}: {v}')
    finally: ff.stop(); save()

# ------------------------------------------------------------------ probe page
def phase_probe():
    ff = Firefox('probe'); m = ff.m
    try:
        m.go('file://' + os.path.join(HERE, '..', 'assets', 'webgl2-probe.html')); time.sleep(3)
        txt = m.js("return document.getElementById('o').textContent")
        R['probe'] = dict(x.split('=', 1) for x in (txt or '').splitlines() if '=' in x); m.shot(f'{out}/shot-probe.png'); say('  ', R['probe'])
    finally: ff.stop(); save()

# ------------------------------------------------------------------ Khronos conformance
KH = 'https://www.khronos.org/registry/webgl/sdk/tests/'
def fetch(u): return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode()
def collect(base, lst, maxv):
    tests = []
    try: txt = fetch(KH + base + lst)
    except Exception: return tests
    for line in txt.splitlines():
        line = line.split('#')[0].strip()
        if not line: continue
        tok = line.split(); path = tok[-1]
        if '--min-version' in tok:
            v = tok[tok.index('--min-version') + 1]
            if tuple(map(int, v.split('.'))) > maxv: continue
        if path.endswith('.txt'):
            sub = os.path.dirname(path); tests += collect(base + (sub + '/' if sub else ''), os.path.basename(path), maxv)
        else: tests.append(base + path)
    return tests
POLL = """const t=document.body?document.body.innerText:'';return JSON.stringify({
 done:/TEST COMPLETE|Overall results|All tests (passed|complete)/i.test(t),
 pass:(t.match(/^PASS/gm)||[]).length, fail:(t.match(/^FAIL/gm)||[]).length,
 failLines:(t.match(/^FAIL.*$/gm)||[]).slice(0,3)})"""

def phase_conformance(k=3):
    tests = []
    for base, maxv in (('conformance/', (1, 0, 4)), ('conformance2/', (2, 0, 1))):
        allt = collect(base, '00_test_list.txt', maxv); groups = {}
        for t in allt: groups.setdefault(t.split('/')[1], []).append(t)
        for g, l in groups.items():
            step = max(1, len(l) // k); tests += l[::step][:k]
    say(f'-- conformance sample: {len(tests)} tests (same selection rule as Chromium run)')
    ff = Firefox('conformance'); m = ff.m; rows = []
    for i, t in enumerate(tests):
        res = None
        try:
            m.go(KH + t); last = None; same = 0; t0 = time.time()
            while time.time() - t0 < 60:
                time.sleep(1.5)
                v = m.js(POLL)
                if not v: continue
                res = json.loads(v)
                if res['done']: break
                key = (res['pass'], res['fail']); same = same + 1 if key == last else 0; last = key
                if same >= 4 and res['pass'] + res['fail'] > 0: break
        except Exception as e:
            say('   driver error', str(e)[:100])
            if ff.p.poll() is not None:
                ff = Firefox('conformance-restart'); m = ff.m
        if not res: status = 'TIMEOUT/NO-RESULT'; res = dict(pass_=0, fail=0, failLines=[])
        else: status = 'FAIL' if res['fail'] else ('PASS' if res['pass'] and res['done'] else ('PASS?' if res['pass'] else 'NO-ASSERTIONS'))
        rows.append(dict(test=t, status=status, pass_=res.get('pass', 0), fail=res.get('fail', 0), failLines=res.get('failLines', [])))
        say(f'  [{i+1}/{len(tests)}] {status:13} {t}')
        if i % 10 == 0: R['conformance'] = dict(rows=rows, planned=len(tests)); save()
    ff.stop(); R['conformance'] = dict(rows=rows, planned=len(tests)); save()
    cnt = {}
    for r in rows: cnt[r['status']] = cnt.get(r['status'], 0) + 1
    say(f"CONFORMANCE pass={cnt.get('PASS', 0) + cnt.get('PASS?', 0)} fail={cnt.get('FAIL', 0)} timeout={cnt.get('TIMEOUT/NO-RESULT', 0)} other={cnt.get('NO-ASSERTIONS', 0)} total={len(rows)}")

# ------------------------------------------------------------------ pages (screenshots of visual/manual pages)
PAGES = [  # (name, url, wait_s)
    ('webglreport-v2', 'https://webglreport.com/?v=2', 8),
    ('three-shadowmap', 'https://threejs.org/examples/webgl_shadowmap.html', 12),
    ('three-instancing', 'https://threejs.org/examples/webgl_instancing_performance.html', 14),
    ('three-bloom', 'https://threejs.org/examples/webgl_postprocessing_unreal_bloom.html', 14),
    ('three-gpgpu-water', 'https://threejs.org/examples/webgl_gpgpu_water.html', 14),
    ('three-msaa-rb', 'https://threejs.org/examples/webgl_multisampled_renderbuffers.html', 12),
    ('three-points', 'https://threejs.org/examples/webgl_points_sprites.html', 12),
]
def phase_pages():
    ff = Firefox('pages'); m = ff.m; R['pages'] = {}
    try:
        for name, url, wait in PAGES:
            try:
                m.go(url); time.sleep(wait)
                txt = m.js("return document.body?document.body.innerText.slice(0,6000):''") or ''
                m.shot(f'{out}/shot-{name}.png'); open(f'{out}/text-{name}.txt', 'w').write(txt)
                R['pages'][name] = dict(ok=True, chars=len(txt)); say(f'  {name}: shot saved ({len(txt)} chars text)')
            except Exception as e: R['pages'][name] = dict(ok=False, err=str(e)[:200]); say(f'  {name}: ERROR {str(e)[:120]}')
            save()
    finally: ff.stop()

# ------------------------------------------------------------------ aquarium
def phase_aquarium():
    ff = Firefox('aquarium'); m = ff.m; samples = []
    try:
        m.go('https://webglsamples.org/aquarium/aquarium.html')
        for _ in range(12):
            time.sleep(3); v = m.js("const e=document.getElementById('fps');return e?e.textContent:''")
            if v and v.strip().replace('.', '').isdigit(): samples.append(float(v))
        m.shot(f'{out}/shot-aquarium.png')
    finally: ff.stop()
    R['aquarium'] = dict(samples=samples, avg=round(sum(samples[2:]) / max(1, len(samples[2:])), 1) if samples else None); say('  aquarium', R['aquarium']); save()

def report():
    L = ['# Firefox validation', '']
    if 'support' in R: L += ['## about:support', ''] + [f'- {k}: {v}' for k, v in R['support'].items() if k not in ('graphics',)] + ['']
    if 'probe' in R: L += ['## WebGL2 probe', ''] + [f'- {k}: {v}' for k, v in R['probe'].items()] + ['']
    if 'conformance' in R:
        rows = R['conformance']['rows']; cnt = {}
        for r in rows: cnt[r['status']] = cnt.get(r['status'], 0) + 1
        L += [f'## Khronos conformance sample ({len(rows)} tests)', '', ', '.join(f'{k}: {v}' for k, v in sorted(cnt.items())), '']
        for r in rows:
            if r['status'] not in ('PASS',): L.append(f"- {r['status']} `{r['test']}` {r['failLines'][:1]}")
        L.append('')
    if 'aquarium' in R: L += ['## Aquarium', '', f"avg fps: {R['aquarium']['avg']}  samples: {R['aquarium']['samples']}", '']
    open(f'{out}/firefox-validation.md', 'w').write('\n'.join(L))

if __name__ == '__main__':
    for ph in phases:
        say(f'== {ph}')
        try: {'support': phase_support, 'pages': phase_pages, 'probe': phase_probe, 'conformance': phase_conformance, 'aquarium': phase_aquarium}[ph]()
        except Exception as e: say(f'!! {ph} failed: {e!r}'); R[ph + '_error'] = repr(e); save()
    report(); say(f'report: {out}/firefox-validation.md')
