# Chromium 156 playing https://quenq.com/apps/vice-city/ — CLEAN performance session (LOGMODE=light: --v=0, no GPU-command tracing, scripts/chromium_play.py)
Fresh throw-away profile, WebGL: ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0). ~5 min of play (the game auto-started; intro cutscenes / first street scene).
Files: fps.csv (1 Hz requestAnimationFrame fps + 99th-pct frame time), summary.txt, kernel.log, system.csv, screenshots/ (every 60 s), chromium.log (17 KB), webgl.txt.

Results: gpu_hangs=0, no crash. avg 11.6 fps, median 4.6, p5 1.9, max 53.5 (227 one-second windows).
 - 0-60 s (loading + first cutscene): avg 28 fps, peaks 47-54
 - 60-227 s (3D street/interior scenes): avg ~5 fps (range 1-25), typically 3-9 fps
 - SoC 75-83 C
This is the real in-game rate: the full-logging session (`../attempt-02-full-logging-session`) was similar in the 3D scenes (about 4-5 fps), so GPU-command tracing was NOT the main cause of the slowness,
only a partial one (avg 7.7 vs 11.6 fps overall). The earlier "~60 fps" short test was most likely just the loading screen, not gameplay.
Note: the overlay is not visible in the fullscreen game screenshots (the game canvas covers it); the numbers are in fps.csv.
Not established: whether the limit is GPU fill rate/vertex work of this scene (GC7000UL), CPU/JS (WASM game logic), or the driver. 
