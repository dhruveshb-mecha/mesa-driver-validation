# Stock Flutter (GTK embedder + Impeller OpenGLES) renders all 17 benchmark scenes with `GDK_GL=gles`

**Verdict:** PASS

## What was run
`flutter/` gpu_bench app cross-built on x86, 17 scenes (images, circles, text, list, shadows, clip, opacity, blur, gradients ...) at ~1072x1042.

## Result
17/17 scenes, no GPU hangs, no crashes. fps (small/large item counts): images 44/37, circles 43/26, text 41/29, list 27, shadows 25/11, clip 19/8, opacity 13/5, blur 13/5, gradients 12/5. Weak spots are offscreen passes (gradients, blur, opacity layers).

## Why it matters
Flutter's `rasterDuration` is CPU submission time and under-reports GPU load, so fps is the reliable number. The second attempt reruns the matrix with all logging env vars on (`VERBOSE=1`, per-scene gzipped logs).

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/flutter_bench_matrix.py /tmp/flutter-bench
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run-with-driver-debug-logging` | RAN_OK | 0 | 182.6 | 0 | 81.0 | yes |
| `attempt-02-run-verbose-all-log-env-vars` | RAN_OK | 0 | 182.4 | 0 | 81.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-run-with-driver-debug-logging**
```
circles    n=10  -> 44.8 fps, raster p50 6.2 / p95 10.9 ms, total p95 27.1 ms (1072x1042)
circles    n=50  -> 21.0 fps, raster p50 26.7 / p95 86.2 ms, total p95 158.2 ms (1072x1042)
gradients  n=8   -> 12.2 fps, raster p50 10.1 / p95 13.4 ms, total p95 161.6 ms (1072x1042)
gradients  n=24  -> 4.8 fps, raster p50 131.9 / p95 199.1 ms, total p95 443.6 ms (1072x1042)
shadows    n=8   -> 21.4 fps, raster p50 2.0 / p95 2.8 ms, total p95 66.8 ms (1072x1042)
shadows    n=24  -> 9.5 fps, raster p50 3.6 / p95 4.4 ms, total p95 163.1 ms (1072x1042)
blur       n=4   -> 8.0 fps, raster p50 5.4 / p95 10.6 ms, total p95 137.8 ms (1072x1042)
... (4 more distinct lines) ...
clip       n=24  -> 8.0 fps, raster p50 20.0 / p95 22.2 ms, total p95 197.5 ms (1072x1042)
text       n=20  -> 34.3 fps, raster p50 3.3 / p95 4.2 ms, total p95 30.6 ms (1072x1042)
text       n=60  -> 24.4 fps, raster p50 6.8 / p95 8.0 ms, total p95 49.1 ms (1072x1042)
images     n=8   -> 31.2 fps, raster p50 1.6 / p95 2.5 ms, total p95 41.1 ms (1072x1042)
images     n=24  -> 24.4 fps, raster p50 2.2 / p95 2.9 ms, total p95 59.7 ms (1072x1042)
list       n=1   -> 26.9 fps, raster p50 4.1 / p95 5.0 ms, total p95 25.4 ms (1072x1042)
FLUTTERMATRIX runs=17 ok=17 failed=0 min_fps=4.3 max_fps=44.8
```

**attempt-02-run-verbose-all-log-env-vars**
```
circles    n=10  -> 41.9 fps, raster p50 6.2 / p95 10.9 ms, total p95 25.5 ms (1072x1042)
circles    n=50  -> 26.3 fps, raster p50 21.4 / p95 37.4 ms, total p95 60.1 ms (1072x1042)
gradients  n=8   -> 12.0 fps, raster p50 9.8 / p95 12.6 ms, total p95 158.4 ms (1072x1042)
gradients  n=24  -> 4.8 fps, raster p50 97.0 / p95 204.6 ms, total p95 487.4 ms (1072x1042)
shadows    n=8   -> 24.9 fps, raster p50 2.0 / p95 2.3 ms, total p95 40.2 ms (1072x1042)
shadows    n=24  -> 11.2 fps, raster p50 3.6 / p95 4.2 ms, total p95 90.2 ms (1072x1042)
blur       n=4   -> 12.8 fps, raster p50 6.2 / p95 12.8 ms, total p95 80.8 ms (1072x1042)
... (4 more distinct lines) ...
clip       n=24  -> 7.8 fps, raster p50 19.4 / p95 41.3 ms, total p95 253.4 ms (1072x1042)
text       n=20  -> 45.0 fps, raster p50 3.0 / p95 4.0 ms, total p95 16.2 ms (1072x1042)
text       n=60  -> 32.9 fps, raster p50 6.4 / p95 7.7 ms, total p95 25.9 ms (1072x1042)
images     n=8   -> 43.1 fps, raster p50 1.9 / p95 3.1 ms, total p95 23.6 ms (1072x1042)
images     n=24  -> 37.9 fps, raster p50 2.2 / p95 2.5 ms, total p95 26.3 ms (1072x1042)
list       n=1   -> 31.3 fps, raster p50 3.4 / p95 4.6 ms, total p95 22.1 ms (1072x1042)
FLUTTERMATRIX runs=17 ok=17 failed=0 min_fps=4.8 max_fps=45.0
```

