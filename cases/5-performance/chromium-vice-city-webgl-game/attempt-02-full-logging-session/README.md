# Chromium 156 playing https://quenq.com/apps/vice-city/ — session with ALL logging on (scripts/chromium_play.py)
Started 18:02:33 (board time), stopped ~18:12 by `touch STOP`. Fresh throw-away profile. WebGL renderer: ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0), WebGL 2.0.

Files: fps.csv (1 Hz rAF fps, 99th-pct frame time), summary.txt, kernel.log (journalctl -kf), system.csv (SoC temp 79-83 C), screenshots/ (every 60 s),
chromium.log.gz (Chromium --v=1 + --enable-gpu-service-logging, Mesa/EGL debug), webgl.txt, script-output.txt.

Results: no `recover hung GPU` (gpu_hangs=0); kernel log only has WiFi `bgscan already stopped!` and one HDMI-audio ELD line. Game renders correctly (screenshots: cutscene in Marco's Bistro).
fps: avg 7.7, min 0.05, max 58.9 over 211 one-second windows; first 60 s averaged ~21 fps (peaks 43-59), then 0.3-8 fps.

CAVEAT — the fps numbers are NOT a clean performance measurement: --enable-gpu-service-logging writes every WebGL command to stderr
(chromium.log has ~665,000 `[.WebGL...]cmd: kBindSampler / kDisableVertexAttribArray / ...` lines, ~98 MB uncompressed). That tracing cost some speed, but NOT most of it: the later clean run (../chromium-vice-city-clean, --v=0, no GPU tracing) also gives only ~4-5 fps in the 3D scenes (avg 11.6 overall vs 7.7 here).
Use the clean run for fps; this session is the one with full logs.
