# Chromium 156: GPU validation, WebGL load tests, WebGL Aquarium (GPU vs SwiftShader CPU)

**Verdict:** PASS

## What was run
`validate-chromium-gpu` plus draw-call load pages (200/1000 draws per frame) and the WebGL Aquarium.

## Result
WebGL2 via `ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0)`. 1000 draws/frame: 47.9 fps. Aquarium: 9.7 fps on GPU vs 1.0 fps on SwiftShader.

## Why it matters
Hardware WebGL is active (about 10x the CPU path in the aquarium).

## Command (as run on the Comet)
```
~/bin/validate-chromium-gpu
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gpu-validation` | RAN_OK | 0 | 197.2 | 0 | 81.0 | yes |
| `attempt-02-webgl-200-draws` | RAN_OK | 0 | 60.5 | 0 | 78.0 | yes |
| `attempt-03-webgl-1000-draws` | RAN_OK | 0 | 60.5 | 0 | 77.0 | yes |
| `attempt-04-aquarium-gpu-vs-cpu` | RAN_OK | 0 | 143.8 | 0 | 81.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-gpu-validation**
```
-- WebGL 200 draws/frame [CPU (SwiftShader)]
-- Canvas2D 300 gradient circles [CPU (--disable-gpu)]
- **webgl2**: renderer `ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0)`, version `WebGL 2.0 (OpenGL ES 3.0 Chromium) glsl=WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)`
- **webgl**: renderer `ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0)`, version `WebGL 1.0 (OpenGL ES 2.0 Chromium) glsl=WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)`
| WebGL 50 draws/frame | GPU | 42.9 | 22.9 | 39.9 | 800x480 |
| WebGL 200 draws/frame | GPU | 43.8 | 22.1 | 39.7 | 800x480 |
| WebGL 1000 draws/frame | GPU | 40.3 | 23.7 | 39.9 | 800x480 |
| WebGL 5000 draws/frame | GPU | 35.3 | 26.4 | 40.0 | 800x480 |
| Canvas2D 300 gradient circles | GPU | 5.9 | 161.6 | 234.8 | 800x480 |
| WebGL 200 draws/frame | CPU (SwiftShader) | 10.6 | 72.4 | 95.9 | 800x480 |
| Canvas2D 300 gradient circles | CPU (--disable-gpu) | 3.5 | 258.7 | 294.4 | 800x480 |
- GPU vs CPU for "Canvas2D 300 gradient circles": **1.7x** (5.9 vs 3.5 fps)
- GPU vs CPU for "WebGL 200 draws/frame": **4.1x** (43.8 vs 10.6 fps)
```

**attempt-02-webgl-200-draws**
```
BENCH webgl2 vendor=Google Inc. (Mesa) renderer=ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0) version=WebGL 2.0 (OpenGL ES 3.0 Chromium)
BENCH webgl vendor=Google Inc. (Mesa) renderer=ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0) version=WebGL 1.0 (OpenGL ES 2.0 Chromium)
BENCH RESULT canvas=500x205 draws_per_frame=200 fps=48.0 avg_ms=20.1 p95_ms=20.2
```

**attempt-03-webgl-1000-draws**
```
BENCH webgl2 vendor=Google Inc. (Mesa) renderer=ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0) version=WebGL 2.0 (OpenGL ES 3.0 Chromium)
BENCH webgl vendor=Google Inc. (Mesa) renderer=ANGLE (Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0) version=WebGL 1.0 (OpenGL ES 2.0 Chromium)
BENCH RESULT canvas=500x205 draws_per_frame=1000 fps=47.9 avg_ms=20.3 p95_ms=20.2
```

**attempt-04-aquarium-gpu-vs-cpu**
```
| GPU | 9.7 | [1.0, 6.0, 11.0, 10.0, 10.0, 8.0, 9.0, 10.0, 9.0, 10.0, 10.0] |
| CPU (SwiftShader) | 1.0 | [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] |
```

