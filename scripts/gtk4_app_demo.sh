#!/bin/bash
# Scripted GTK4 real-app demo for before/after videos. Run ON the Comet (sway session).
#   gtk4_app_demo.sh LABEL OUTDIR [--no-record] [app ...]
# apps (default: all): text-editor nautilus loupe characters clocks maps
# Per app: caption card (Mesa version, requested renderer, GL_VERSION) -> app with GSK_RENDERER=gl ->
# scripted key input (wtype) -> screenshot -> close. One continuous recording per run: OUTDIR/LABEL.mp4.
# The log of each app is checked: "Failed to realize renderer 'GskGLRenderer'" means GTK fell back to Cairo.
LABEL=${1:?label}; OUT=${2:?outdir}; shift 2
REC=1; [ "$1" = "--no-record" ] && { REC=0; shift; }
APPS=${*:-text-editor nautilus loupe characters clocks maps}
unset LD_LIBRARY_PATH GST_PLUGIN_PATH PKG_CONFIG_PATH
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 GDK_BACKEND=wayland DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export SWAYSOCK=$(ls /run/user/1000/sway-ipc.*.sock | head -1)
export GSK_RENDERER=${GSK_RENDERER:-gl} MESA_DEBUG=1 EGL_LOG_LEVEL=info LIBGL_DEBUG=verbose
mkdir -p "$OUT/$LABEL"; cd "$OUT/$LABEL" || exit 1
SECS_APP=${SECS_APP:-14}
IMG=/usr/share/backgrounds/sway/Sway_Wallpaper_Blue_1920x1080.png

MESA=$(rpm -q mesa-dri-drivers | sed 's/mesa-dri-drivers-//; s/\.aarch64//')
GLV=$(timeout 30 glmark2-es2-wayland -b build:duration=1 2>&1 | sed -n 's/.*GL_VERSION: *//p' | head -1)
GLR=$(timeout 30 glmark2-es2-wayland -b build:duration=1 2>&1 | sed -n 's/.*GL_RENDERER: *//p' | head -1)
{ echo "label=$LABEL"; echo "kernel=$(uname -r)"; echo "mesa=$MESA"; echo "GL_VERSION(es2)=$GLV"; echo "GL_RENDERER=$GLR"; echo "GSK_RENDERER=$GSK_RENDERER"; } > run-info.txt

card() { # card "text" seconds  -> floating caption window (runs in background; $CP = its pid)
  pkill -x nwg-drawer 2>/dev/null
  foot --app-id=card -o font=monospace:size=10 -o colors-dark.background=101820 -o colors-dark.foreground=e8e8e8 -o pad=14x14 \
       sh -c "printf '%s\n' \"\$1\"; sleep $2" _ "$1" 2>/dev/null &
  CP=$!
}
killfocused() { # kill -9 the focused window's process (a normal close can raise "Save changes?" dialogs)
  local pid; pid=$(swaymsg -t get_tree | python3 -c "
import json,sys
def f(n):
    if n.get('focused') and n.get('pid'): return n['pid']
    for c in n.get('nodes',[])+n.get('floating_nodes',[]):
        r=f(c)
        if r: return r
print(f(json.load(sys.stdin)) or '')")
  [ -n "$pid" ] && kill -9 "$pid"
}
cleanup_state() { rm -rf ~/.local/share/org.gnome.TextEditor/drafts ~/.local/share/org.gnome.TextEditor/session.gvariant; }
key() { wtype "$@"; sleep "${KD:-0.5}"; }
rep() { local n=$1; shift; for _ in $(seq "$n"); do wtype "$@"; sleep "${KD:-0.4}"; done; }

drive_text-editor() { sleep 7; for i in 1 2 3 4 5 6 7 8; do wtype -d 15 "The quick brown fox jumps over the lazy dog $i, 0123456789 {}[]()"; wtype -k Return; done
  KD=0.4 rep 3 -M ctrl -k plus -m ctrl; sleep 1; KD=0.4 rep 3 -M ctrl -k minus -m ctrl; wtype -M ctrl -k Home -m ctrl; sleep 1; rep 4 -k Page_Down; }
drive_nautilus() { sleep 4; key -M ctrl -k 1 -m ctrl; sleep 1; KD=0.7 rep 8 -k Page_Down; KD=0.7 rep 5 -k Page_Up; rep 3 -M ctrl -k plus -m ctrl; sleep 1; KD=0.6 rep 4 -k Page_Down; }
drive_loupe() { sleep 5; KD=0.6 rep 4 -k plus; rep 4 -k Right; rep 4 -k Down; rep 4 -k Left; key -k r; sleep 1; key -k r; KD=0.6 rep 5 -k minus; }
drive_characters() { sleep 4; key -k Tab; key -k Tab; key -k Tab; KD=0.5 rep 14 -k Down; rep 8 -k Page_Down; rep 4 -k Page_Up; }
drive_clocks() { sleep 4; for c in Lon Mum Tok; do key -M ctrl -k n -m ctrl; sleep 1.5; wtype -d 80 "$c"; sleep 2; key -k Escape; sleep 1; done; }
drive_maps() { sleep 9; key -k Escape; key -k Tab; KD=1.2 rep 3 -M ctrl -k plus -m ctrl; KD=0.6 rep 6 -k Right; rep 6 -k Down; rep 5 -k Left; KD=1.2 rep 3 -M ctrl -k minus -m ctrl; }
cmd_text-editor() { gnome-text-editor; }
cmd_nautilus()    { nautilus /usr/share/icons/Adwaita/symbolic/actions; }
cmd_loupe()       { loupe "$IMG"; }
cmd_characters()  { gnome-characters; }
cmd_clocks()      { gnome-clocks; }
cmd_maps()        { gnome-maps; }

swaymsg 'for_window [app_id="card"] floating enable, resize set 520 460, move position center' >/dev/null
pkill -x nwg-drawer 2>/dev/null; cleanup_state
if [ $REC = 1 ]; then
  wf-recorder -f "$LABEL.mp4" -y > recorder.log 2>&1 &
  RP=$!; sleep 2
fi
card "GTK4 real apps: $LABEL
Mesa:        $MESA
GL_VERSION:  $GLV
GL_RENDERER: $GLR
Requested:   GSK_RENDERER=$GSK_RENDERER
Kernel:      $(uname -r)" 6; wait $CP

: > summary.txt
for app in $APPS; do
  pkill -x nwg-drawer 2>/dev/null
  card "$app
GSK_RENDERER=$GSK_RENDERER
Mesa $MESA
GL_VERSION: $GLV" 5
  J0=$(date +%s)
  "cmd_$app" > "$app.log" 2>&1 &
  AP=$!
  wait $CP
  "drive_$app"
  sleep 2; grim "$app.png"
  killfocused; sleep 1; kill -9 $AP 2>/dev/null; wait $AP 2>/dev/null; cleanup_state
  journalctl -k --since "@$J0" | grep -i -E "hung|etnaviv|segfault" > "$app.kernel"
  if grep -q "Failed to realize renderer" "$app.log"; then R="FELL BACK TO CAIRO (GL renderer failed)"; else R="GL renderer active"; fi
  H=$(grep -c -i "hung" "$app.kernel")
  echo "$app: $R, gpu_hangs=$H" | tee -a summary.txt
done
card "Result: $LABEL
Mesa $MESA
$(sed 's/ (GL renderer failed)//; s/, gpu_hangs=/  hangs=/' summary.txt)" 9; wait $CP
[ $REC = 1 ] && { kill -INT $RP; wait $RP 2>/dev/null; }
echo done
