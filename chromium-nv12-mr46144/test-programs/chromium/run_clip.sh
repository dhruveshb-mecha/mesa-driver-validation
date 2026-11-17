#!/bin/bash
# run_clip.sh CLIP OUTDIR [extra chromium flags...]  -- run on the Comet. Plays CLIP in chromium (wayland), samples title stats + CPU.
CLIP=$1; OUT=$2; shift 2
unset LD_LIBRARY_PATH GST_PLUGIN_PATH PKG_CONFIG_PATH
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
export SWAYSOCK=$(ls /run/user/1000/sway-ipc.*.sock | head -1)
D=~/chromium-video; mkdir -p "$OUT"; N=$(basename "${CLIP%%\?*}"); case "$CLIP" in http*) SRC="$CLIP";; *) SRC="file://$D/$CLIP";; esac; PROF=$(mktemp -d)
pkill -x nwg-drawer 2>/dev/null
chromium-browser --user-data-dir=$PROF --no-first-run --no-default-browser-check --ozone-platform=wayland \
  --remote-debugging-port=9222 --autoplay-policy=no-user-gesture-required --enable-logging=stderr --v=0 "$@" \
  "file://$D/player.html?src=$SRC" > "$OUT/$N.chromium.log" 2>&1 &
sleep 5; swaymsg fullscreen enable >/dev/null 2>&1
: > "$OUT/$N.samples.txt"
for i in $(seq 1 45); do
  T=$(curl -s http://127.0.0.1:9222/json | python3 -c "import json,sys;print([t['title'] for t in json.load(sys.stdin) if t['title'].startswith('STAT')][0][5:])" 2>/dev/null)
  C=$(ps -eo pcpu,comm | awk '/chrom/{s+=$1} END{print s}')
  echo "$(date +%s.%N) cpu=$C $T" >> "$OUT/$N.samples.txt"
  echo "$T" | grep -q '"ended"' && break
  [ $i = 12 ] && grim "$OUT/$N.png"
  sleep 1
done
pkill -x chromium-browse; sleep 1; rm -rf "$PROF"
