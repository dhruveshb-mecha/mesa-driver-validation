# GTK4 renderer comparison: GL vs Cairo (vs Vulkan=llvmpipe) over 16 scenes

**Verdict:** DATA

## What was run
`gtk4_bench.py` scenes (widgets, rounded, textures, shadows, gradients, text, blur ...) at several item counts, GSK GL vs Cairo.

## Result
GL is slower than Cairo in 14 of 16 scenes (geomean 0.5x), blur worst (about 1 s/frame p95). GL wins on text. 20-widget scene: Cairo 33.8 fps, GL 13.3, Vulkan 20.4. Light 2D scenes reach ~50.7 fps for both renderers: the display refresh is the cap there.

## Why it matters
GTK4 apps look better on Cairo than on GL for many-widget scenes at the moment; useful data for deciding which renderer to ship by default.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_bench_matrix.py /tmp/gtk4-bench
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-matrix` | RAN_OK | 0 | 313.5 | 0 | 82.0 | yes |
| `attempt-02-20-widget-scene` | RAN_OK | 0 | 35.6 | 0 | 83.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-matrix**
```
widgets    n=10  full  cairo -> 49.6 fps p95 30.3 ms (size 540x620)
widgets    n=10  full  gl    -> 25.9 fps p95 48.3 ms (size 540x620)
widgets    n=40  full  cairo -> 26.7 fps p95 47.7 ms (size 540x620)
widgets    n=40  full  gl    -> 6.7 fps p95 165.9 ms (size 540x620)
text       n=10  full  cairo -> 16.5 fps p95 151.4 ms (size 808x620)
text       n=10  full  gl    -> 30.3 fps p95 67.0 ms (size 830x620)
text       n=40  full  cairo -> 5.0 fps p95 381.9 ms (size 3480x620)
... (19 more distinct lines) ...
blur       n=40  full  gl    -> 1.2 fps p95 931.0 ms (size 541x629)
widgets    n=40  small cairo -> 24.6 fps p95 49.2 ms (size 536x541)
widgets    n=40  small gl    -> 6.9 fps p95 165.8 ms (size 536x568)
shadows    n=40  small cairo -> 3.2 fps p95 380.8 ms (size 536x564)
shadows    n=40  small gl    -> 2.1 fps p95 499.9 ms (size 536x543)
rounded    n=40  small cairo -> 6.5 fps p95 250.4 ms (size 1475x1008)
rounded    n=40  small gl    -> 4.5 fps p95 233.3 ms (size 1221x807)
```

**attempt-02-20-widget-scene**
```
renderer=CairoRenderer widgets=20 fps=33.8 frame_ms avg=29.6 p95=35.5 max=36.4
renderer=GLRenderer widgets=20 fps=13.3 frame_ms avg=75.2 p95=83.3 max=99.2
renderer=VulkanRenderer widgets=20 fps=20.4 frame_ms avg=48.9 p95=63.4 max=85.0
```

