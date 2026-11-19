#!/bin/bash
# qt_apps_fps.sh OUTDIR [app ...]   -- run ON the Comet in the sway session.
# Runs Qt6 apps ONE AT A TIME with a scripted interaction and records, per app, raw logs:
#   raw.log          app stdout+stderr with WAYLAND_DEBUG=client (every wl_surface.commit, timestamped) and QSG_INFO
#   metrics.csv      1 Hz CPU / RSS / DRM (etnaviv renderD128) client + memory of the app's process tree
#   phases.txt       wall-clock markers (same HH:MM:SS format as the WAYLAND_DEBUG timestamps) for each phase
#   isolation.txt    proof that nothing else was on screen / running before the app was driven
#   gpu-libs.txt     GL/EGL/Mesa/Qt libraries mapped by the app tree at the end of the active phase
#   kernel.txt       kernel log lines (hang/etnaviv/segfault) during the run, coredumps
#   active.png       screenshot at the end of the scripted phase
# Frame rate = rate of wl_surface.commit on the busiest surface of the app during the active phase.
unset LD_LIBRARY_PATH GST_PLUGIN_PATH PKG_CONFIG_PATH
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 QT_QPA_PLATFORM=wayland
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export SWAYSOCK=$(ls /run/user/1000/sway-ipc.*.sock | head -1)
OUT=${1:?outdir}; shift
APPS=${*:-qml-tvtennis qml-particles qml-pathanimation qml-sprite qt-gallery kirigami-gallery qt-canvas qt-shadereffects qt3d-hellocube qt3d-intro kcalc konsole qterminal kate okular dolphin falkon}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT/assets"; OUT=$(cd "$OUT" && pwd)
ACTIVE_SECS=${ACTIVE_SECS:-25}
SETTLE_SECS=${SETTLE_SECS:-6}
EXTRA_ENV=${EXTRA_ENV:-}
QE=${QE:-/usr/lib64/qt6/examples}
QB=${QB:-/usr/lib64/qt6/bin}

now() { date -u +%H:%M:%S.%3N; }   # WAYLAND_DEBUG timestamps are UTC
python3 - "$OUT/assets" <<'PY'
import sys, os
d = sys.argv[1]
# 40-page PDF: text + vector graphics, so scrolling/zooming exercises real rendering
objs = []
def add(b): objs.append(b); return len(objs)
pages = 40
font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
kids = []
page_objs = []
for p in range(pages):
    lines = []
    lines.append("BT /F1 22 Tf 50 790 Td (GTK4 test document page %d of %d) Tj ET" % (p + 1, pages))
    for i in range(45):
        lines.append("BT /F1 11 Tf 50 %d Td (Line %d: The quick brown fox jumps over the lazy dog 0123456789 etnaviv GC7000) Tj ET" % (760 - i * 12, i))
    for i in range(30):
        lines.append("%.2f %.2f %.2f rg %d %d 12 12 re f" % ((i * 7 % 10) / 10.0, (i * 3 % 10) / 10.0, (i * 9 % 10) / 10.0, 60 + i * 16, 180 - (i % 5) * 14))
    for i in range(20):
        lines.append("0.2 0.4 0.8 RG %d w 50 %d m 540 %d l S" % (1 + i % 3, 140 - i * 5, 100 + (i * 17) % 90))
    stream = "\n".join(lines).encode()
    c = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    page_objs.append(c)
pids = []
pages_id = len(objs) + pages + 1
for c in page_objs:
    pids.append(add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 595 842] /Contents %d 0 R /Resources << /Font << /F1 %d 0 R >> >> >>" % (pages_id, c, font)))
assert add(("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % x for x in pids), pages)).encode()) == pages_id
cat = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id)
buf = bytearray(b"%PDF-1.4\n")
offs = []
for i, o in enumerate(objs):
    offs.append(len(buf))
    buf += b"%d 0 obj\n" % (i + 1) + o + b"\nendobj\n"
x = len(buf)
buf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
for o in offs:
    buf += b"%010d 00000 n \n" % o
buf += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, cat, x)
open(os.path.join(d, "test.pdf"), "wb").write(buf)
# web page: long scrolling content + CSS animation + canvas animation with a self-reported rAF fps counter
html = """<!doctype html><meta charset=utf-8><title>webkit fps page</title>
<style>body{margin:0;font:18px sans-serif}#hud{position:fixed;top:0;left:0;right:0;background:#111;color:#0f0;padding:6px;z-index:9;font:20px monospace}
.box{position:fixed;top:60px;left:0;width:80px;height:80px;background:#e33;animation:mv 2s linear infinite alternate}
@keyframes mv{to{transform:translateX(300px) rotate(360deg)}}
p{margin:6px 12px;padding-top:2px}
canvas{position:fixed;top:150px;right:4px;border:1px solid #888}</style>
<div id=hud>rAF fps: ...</div><div class=box></div><canvas id=c width=200 height=200></canvas>
<div style="margin-top:100px">"""
html += "".join("<p>Row %d: the quick brown fox jumps over the lazy dog, etnaviv GC7000UL 0123456789 &#9731;&#9733;</p>" % i for i in range(int(os.environ.get("PAGE_ROWS", "800"))))
html += """</div><script>
const c=document.getElementById('c').getContext('2d');let n=0,t0=performance.now(),a=0;
function f(t){a+=0.05;c.clearRect(0,0,200,200);for(let i=0;i<40;i++){c.fillStyle='hsl('+((i*9+a*40)%360)+',80%,50%)';
c.fillRect(100+90*Math.cos(a+i/6)-8,100+90*Math.sin(a+i/6)-8,16,16);}
n++;if(t-t0>=1000){document.getElementById('hud').textContent='rAF fps: '+(n*1000/(t-t0)).toFixed(1);n=0;t0=t;}requestAnimationFrame(f);}
requestAnimationFrame(f);</script>"""
open(os.path.join(d, "page.html"), "w").write(html)
plain = "<!doctype html><meta charset=utf-8><title>plain text</title><body style=\"margin:0;font:18px sans-serif\">" + "".join("<p style=\"margin:6px 12px\">Row %d: the quick brown fox jumps over the lazy dog, etnaviv GC7000UL 0123456789</p>" % i for i in range(int(os.environ.get("PAGE_ROWS", "800"))))
open(os.path.join(d, "plain.html"), "w").write(plain)
PY
# ---- helpers -----------------------------------------------------------------------------------------------
windows() { # one line per application window in the sway tree: pid app_id title
  swaymsg -t get_tree 2>/dev/null | python3 -c "
import json,sys
def w(n):
    if n.get('pid') and (n.get('app_id') or n.get('window_properties')) and not n.get('nodes'):
        print(n['pid'], n.get('app_id') or n.get('window_properties',{}).get('class'), (n.get('name') or '')[:60].replace(' ','_'))
    for c in n.get('nodes',[])+n.get('floating_nodes',[]): w(c)
w(json.load(sys.stdin))"
}
KNOWN="qmlscene-qt6 qmlscene galleryexample kirigami2galler canvasexample shadereffectsex hellocube intro principledmateri reflectionprobes cascadedshadowm sceneeffects lights kcalc konsole qterminal kate okular dolphin falkon QtWebEngineProc foot glmark2-es2-way"
clear_screen() { # closes everything that is not the compositor/bar; returns 0 if the tree is empty afterwards
  pkill -x nwg-drawer 2>/dev/null
  pkill -f 'http.server 8099' 2>/dev/null   # stale test web server from an earlier (possibly OOM-killed) Epiphany run
  for pid in $(windows | awk '{print $1}'); do kill "$pid" 2>/dev/null; done
  for n in $KNOWN; do pkill -x "$n" 2>/dev/null; done
  sleep 2
  for pid in $(windows | awk '{print $1}'); do kill -9 "$pid" 2>/dev/null; done
  for n in $KNOWN; do pkill -9 -x "$n" 2>/dev/null; done
  for i in 1 2 3 4 5 6 7 8 9 10; do [ -z "$(windows)" ] && return 0; sleep 1; done
  return 1
}
app_tree() { ps -eo pid=,ppid= | python3 -c "
import sys
root=int(sys.argv[1]); kids={}
for l in sys.stdin:
    a,b=l.split(); kids.setdefault(int(b),[]).append(int(a))
res=[root]; i=0
while i<len(res): res+=kids.get(res[i],[]); i+=1
print(' '.join(map(str,res)))" "$1"; }
extra_windows() { # windows in the sway tree whose pid is not in the process tree of $AP
  local tree; tree=$(app_tree "$AP"); windows | while read -r pid rest; do case " $tree " in *" $pid "*) ;; *) echo "$pid $rest";; esac; done; }
handle_extra() { # keyring prompt -> type $KEYRING_PASSWORD (if set); any other foreign window -> close it
  local ex; ex=$(extra_windows); [ -z "$ex" ] && { echo "extra_windows_found: none"; return; }
  echo "extra_windows_found:"; echo "$ex"
  echo "$ex" | while read -r pid app title; do
    case "$app" in
      gcr-prompter) if [ -n "$KEYRING_PASSWORD" ]; then swaymsg "[pid=$pid] focus" >/dev/null 2>&1; sleep 1; wtype "$KEYRING_PASSWORD"; sleep 0.5; wtype -k Return; sleep 3; echo "handled: typed keyring password into gcr-prompter ($pid)"; else kill "$pid" 2>/dev/null; echo "handled: closed keyring prompt $pid (KEYRING_PASSWORD not set)"; fi;;
      *) kill "$pid" 2>/dev/null; sleep 1; echo "handled: closed foreign window $pid $app";;
    esac; done
  sleep 2; echo "extra_windows_after:"; extra_windows; echo "extra_windows_end"; }
cpu_idle_pct() { # idle percent over 3 s
  read -r _ u1 n1 s1 i1 w1 q1 sq1 _ < /proc/stat; sleep 3; read -r _ u2 n2 s2 i2 w2 q2 sq2 _ < /proc/stat
  local t1=$((u1+n1+s1+i1+w1+q1+sq1)) t2=$((u2+n2+s2+i2+w2+q2+sq2))
  echo $(( 100 * ((i2+w2)-(i1+w1)) / (t2-t1) ))
}
key()  { wtype "$@"; sleep "${KD:-0.4}"; }
rep()  { local n=$1; shift; for _ in $(seq "$n"); do wtype "$@"; sleep "${KD:-0.15}"; done; }
typed(){ wtype -d 10 "$1"; sleep 0.3; wtype -k Return; }

# ---- per-app definitions: cmd_<app> launches, drive_<app> interacts ------------------------------------------
QS() { $QB/qmlscene "$@"; }
cmd_qml-tvtennis()     { QS $QE/quick/animation/behaviors/tvtennis.qml; }
drive_qml-tvtennis()   { sleep $ACTIVE_SECS; }
cmd_qml-particles()    { QS $QE/quick/particles/imageparticle/colored.qml; }
drive_qml-particles()  { sleep $ACTIVE_SECS; }
cmd_qml-pathanimation(){ QS $QE/quick/animation/pathanimation/pathanimation.qml; }
drive_qml-pathanimation(){ sleep $ACTIVE_SECS; }
cmd_qml-sprite()       { QS $QE/quick/imageelements/animatedsprite.qml; }
drive_qml-sprite()     { sleep $ACTIVE_SECS; }
cmd_qt-gallery()       { $QE/quickcontrols/gallery/bin/galleryexample; }
drive_qt-gallery()     { sleep 2; KD=0.35 rep 20 -k Tab; KD=0.3 rep 15 -k Down; KD=0.4 rep 10 -k Page_Down; KD=0.4 rep 8 -k Page_Up; }
cmd_kirigami-gallery() { QT_QUICK_CONTROLS_STYLE=Basic kirigami2gallery; }
drive_kirigami-gallery(){ sleep 3; KD=0.4 rep 10 -k Tab; KD=0.4 rep 10 -k Down; KD=0.5 rep 8 -k Page_Down; KD=0.5 rep 6 -k Page_Up; }
cmd_qt-canvas()        { cd $QE/quick/canvas && QS -I $QE/quick canvas.qml; }
drive_qt-canvas()      { sleep 2; for i in 1 2 3 4; do key -k Down; key -k Return; sleep 4; key -k Escape; done; sleep 2; }
cmd_qt-shadereffects() { $QE/quick/shadereffects/bin/shadereffectsexample; }
drive_qt-shadereffects(){ sleep 2; for i in 1 2 3 4; do key -k Down; key -k Return; sleep 4; key -k Escape; done; sleep 2; }
cmd_qt3d-hellocube()   { $QE/quick3d/hellocube/bin/hellocube; }
drive_qt3d-hellocube() { sleep $ACTIVE_SECS; }
cmd_qt3d-intro()       { $QE/quick3d/intro/bin/intro; }
drive_qt3d-intro()     { sleep $ACTIVE_SECS; }
for ex in principledmaterial reflectionprobes cascadedshadowmaps sceneeffects lights; do
  eval "cmd_qt3d-$ex() { $QE/quick3d/$ex/bin/$ex; }; drive_qt3d-$ex() { sleep \$ACTIVE_SECS; }"
done
cmd_kcalc()            { kcalc; }
drive_kcalc()          { sleep 2; for i in 1 2 3 4 5 6 7 8; do wtype -d 80 "123456789*987654321="; sleep 0.8; key -k Escape; done; sleep 3; }
cmd_konsole()          { konsole --nofork; }
drive_konsole()        { sleep 3; typed "seq 1 300000"; sleep 6; typed "ls -R /usr/share | head -60000"; sleep 6; typed "seq 1 200000"; sleep 5; }
cmd_qterminal()        { qterminal; }
drive_qterminal()      { sleep 3; typed "seq 1 300000"; sleep 6; typed "ls -R /usr/share | head -60000"; sleep 6; typed "seq 1 200000"; sleep 5; }
cmd_kate()             { seq 1 400000 > "$OUT/assets/big.txt"; kate -n "$OUT/assets/big.txt"; }
drive_kate()           { sleep 4; KD=0.5 rep 20 -k Page_Down; KD=0.3 rep 20 -k Page_Up; KD=0.15 rep 60 -k Down; KD=0.5 rep 6 -M ctrl -k End -m ctrl; }
cmd_okular()           { okular "$OUT/assets/test.pdf"; }
drive_okular()         { sleep 4; KD=0.12 rep 60 -k Down; KD=0.5 rep 6 -k Page_Down; KD=0.4 rep 3 -M ctrl -k plus -m ctrl; KD=0.12 rep 60 -k Down; KD=0.5 rep 4 -k Page_Up; }
cmd_dolphin()          { dolphin --new-window /usr/share/icons/Adwaita/symbolic/actions; }
drive_dolphin()        { sleep 3; key -M ctrl -k 1 -m ctrl; sleep 1; KD=0.5 rep 8 -k Page_Down; KD=0.5 rep 6 -k Page_Up; KD=0.5 rep 3 -M ctrl -k plus -m ctrl; KD=0.4 rep 6 -k Page_Down; }
cmd_falkon()           { rm -rf ~/.config/falkon/profiles/qtrun; python3 -m http.server 8099 --bind 127.0.0.1 --directory "$OUT/assets" >/dev/null 2>&1 & falkon --no-extensions --profile=qtrun --new-window "${PAGE_URL:-http://127.0.0.1:8099/plain.html}"; }
drive_falkon()         { sleep 6; key -k Escape; sleep 1; KD=0.1 rep 80 -k Down; KD=0.5 rep 8 -k Page_Down; KD=0.1 rep 40 -k Up; }

# ---- run ----------------------------------------------------------------------------------------------------
{ echo "date=$(date -Is)"; echo "kernel=$(uname -r)"; echo "mesa=$(rpm -q mesa-dri-drivers)"; echo "qt6=$(rpm -q qt6-qtbase)"; echo "qtdeclarative=$(rpm -q qt6-qtdeclarative)"; echo "qtquick3d=$(rpm -q qt6-qtquick3d)"
  echo "GL_RENDERER=$(timeout 30 glmark2-es2-wayland -b build:duration=1 2>&1 | sed -n 's/.*GL_RENDERER: *//p' | head -1)"
  echo "GL_VERSION=$(timeout 30 glmark2-es2-wayland -b build:duration=1 2>&1 | sed -n 's/.*GL_VERSION: *//p' | head -1)"
  echo "extra_env=$EXTRA_ENV"
  echo "output=$(swaymsg -t get_outputs | python3 -c 'import json,sys;[print(o["name"],o["current_mode"],o["scale"]) for o in json.load(sys.stdin)]')"
} > "$OUT/run-info.txt"
swaymsg 'focus_follows_mouse no' >/dev/null 2>&1

: > "$OUT/summary-run.txt"
for app in $APPS; do
  D="$OUT/$app"; rm -rf "$D"; mkdir -p "$D"
  echo "=== $app $(now)"
  # 1. isolation: nothing else on screen
  if clear_screen; then ISO_CLEAR=yes; else ISO_CLEAR=NO; fi
  IDLE=$(cpu_idle_pct); for i in 1 2 3 4 5 6; do [ "$IDLE" -ge 90 ] && break; sleep 5; IDLE=$(cpu_idle_pct); done
  { echo "before_launch: screen_cleared=$ISO_CLEAR windows_left=$(windows | wc -l) cpu_idle_pct=$IDLE"
    echo "windows_before_launch:"; windows; echo "top_cpu_before_launch:"; ps -u mecha -o pid,pcpu,comm --sort=-pcpu | head -6; } > "$D/isolation.txt"
  # 2. launch with debug env
  J0=$(date +%s); T_LAUNCH=$(now)
  env $EXTRA_ENV WAYLAND_DEBUG=client QSG_INFO=1 QT_LOGGING_RULES="qt.scenegraph.general=true;qt.rhi.general=true" bash -c "$(declare -f QS cmd_$app); OUT='$OUT' QE='$QE' QB='$QB' ACTIVE_SECS='$ACTIVE_SECS'; cmd_$app" > "$D/raw.log" 2>&1 &
  AP=$!
  # 3. wait for the window
  W=""; for i in $(seq 1 60); do W=$(windows | head -1); [ -n "$W" ] && break; sleep 1; done
  T_WIN=$(now)
  python3 "$HERE/gtk4_apps_metrics.py" "$AP" "$D/metrics.csv" & MP=$!
  if [ -z "$W" ]; then
    echo "NO WINDOW within 60 s" >> "$D/isolation.txt"; echo "$app: NO WINDOW (see raw.log)" | tee -a "$OUT/summary-run.txt"
    kill -9 $AP $MP 2>/dev/null; continue
  fi
  WPID=$(echo "$W" | awk '{print $1}')
  type "post_$app" >/dev/null 2>&1 && "post_$app"
  swaymsg "[pid=$WPID] focus" >/dev/null 2>&1; swaymsg fullscreen enable >/dev/null 2>&1
  sleep "$SETTLE_SECS"
  handle_extra >> "$D/isolation.txt" 2>&1
  swaymsg "[pid=$WPID] focus" >/dev/null 2>&1
  { echo "after_launch_windows ($(windows | wc -l)):"; windows; echo "cpu_idle_check_note: app is running; see metrics.csv"; } >> "$D/isolation.txt"
  # 4. phases
  { echo "launch=$T_LAUNCH"; echo "window=$T_WIN"; echo "settle_end=$(now)"; } > "$D/phases.txt"
  echo "active_start=$(now)" >> "$D/phases.txt"
  "drive_$app" >> "$D/driver.log" 2>&1
  echo "active_end=$(now)" >> "$D/phases.txt"
  sleep 1; grim "$D/active.png" 2>/dev/null
  echo "final_windows ($(windows | wc -l)):" >> "$D/isolation.txt"; windows >> "$D/isolation.txt"
  for p in $(app_tree "$AP"); do grep -hE "libgallium|libEGL|libGLESv2|libGL\.so|libvulkan|swrast|llvmpipe|libQt6Quick|libQt6Widgets|QtWebEngineCore" /proc/$p/maps 2>/dev/null | awk '{print $6}'; done | sort | uniq -c > "$D/gpu-libs.txt"
  # 5. fdinfo snapshot of the app tree
  for p in $AP $(pgrep -P $AP); do for fd in $(ls /proc/$p/fd 2>/dev/null); do l=$(readlink /proc/$p/fd/$fd 2>/dev/null); [ "$l" = /dev/dri/renderD128 ] && { echo "== pid $p fd $fd"; cat /proc/$p/fdinfo/$fd; }; done; done > "$D/drm-fdinfo.txt" 2>&1
  kill $MP 2>/dev/null; pkill -P $AP 2>/dev/null; kill $AP 2>/dev/null; sleep 2; pkill -9 -P $AP 2>/dev/null; kill -9 $AP 2>/dev/null
  { echo "# kernel log lines during run"; journalctl -k --since "@$J0" --no-pager 2>/dev/null | grep -i -E "hung|etnaviv|gpu|segfault|timeout|fault" ; echo "# coredumps"; coredumpctl list --since "@$J0" --no-pager 2>&1 | tail -n +1; } > "$D/kernel.txt"
  FR=$(grep -c 'wl_surface#[0-9]*.commit' "$D/raw.log")
  echo "$app: commits_logged=$FR" | tee -a "$OUT/summary-run.txt"
done
clear_screen
echo "done $(now)"

