#!/bin/bash
# Plays the GTK4 stock demos (GL renderer) one after another (add 'flutter' as 3rd arg to also play the Flutter benchmark scenes) on the Comet screen, for screen recording.
# No logging. Usage (on the Comet): video_demo.sh [START_DELAY=20] [SECS_PER_DEMO=12] [flutter]     e.g.  ./video_demo.sh 30 15
# Order: working demos first; the two demos that hang/black out the GPU (shadertoy, path_text) are last.
D=${1:-20}; S=${2:-12}; F=${3:-}
unset LD_LIBRARY_PATH GST_PLUGIN_PATH
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 GDK_BACKEND=wayland
GTK_DEMOS="gears glarea fishbowl frames sliding_puzzle paintable_animated css_blendmodes css_shadows path_maze path_spinner listview_colors iconscroll shadertoy path_text"
FLUTTER_SCENES="circles:200 images:8 text:20 shadows:8 gradients:8 blur:4 opacity:8"
echo "Starting in $D s - start your recording now"; sleep "$D"
for d in $GTK_DEMOS; do
  GSK_RENDERER=gl gtk4-demo --run "$d" >/dev/null 2>&1 &
  p=$!; sleep "$S"; kill "$p" 2>/dev/null; wait "$p" 2>/dev/null; sleep 1
done
[ "$F" = flutter ] && for sc in $FLUTTER_SCENES; do
  GDK_GL=gles timeout -k 2 "$((S+3))" ~/flutter-apps/gpu_bench/gpu_bench "${sc%%:*}" "${sc##*:}" "$S" >/dev/null 2>&1; sleep 1
done
echo "Done"
