# wgpu native example sweep on the GL backend: 17/24 run, 7 panic (no compute shaders, missing optional features)

**Verdict:** EXPECTED ES 3.0 LIMITS

## What was run
wgpu-rs examples cross-built, `WGPU_BACKEND=gl`, 12 s each (windowed) or until exit (headless).

## Result
Panics: `boids`, `render_with_compute`, `uniform_values` -> `RequestDeviceError LimitsExceeded max_compute_workgroups_per_dimension requested 65535 allowed 0` (no compute on ES 3.0); `texture_arrays`, `conservative_raster`, `ray_aabb_compute` -> `No suitable GPU adapters found` (they require wgpu features the GL/ES 3.0 device lacks); `water` -> wgpu validation error handled as fatal (cause not examined). The other 17 run, e.g. cube 50.6 fps, skybox 45.4, msaa_line 47.9, shadow 15.4. bunnymark GL: 43.8 / 22.7 / 8.4 fps at 100 / 500 / 2000 bunnies.

## Why it matters
Compute shaders need OpenGL ES 3.1, but etnaviv on GC7000UL exposes ES 3.0. So these are feature gaps, not bugs. Listed so the reviewing team does not read the sweep as 24/24.

## What to look into
Check whether ES 3.1 (compute) is feasible on GC7000UL. Otherwise nothing.

## Command (as run on the Comet)
```
~/bin/validate-full native
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-examples-sweep` | RAN_OK | 0 | 208.8 | 0 | 81.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-examples-sweep**
```
| boids | FAIL | 101 | - | thread 'main' (164968) panicked at examples/features/src/framework.rs:305:14: |
| texture_arrays | FAIL | 101 | - | thread 'main' (165167) panicked at examples/features/src/utils.rs:226:24: |
| uniform_values | FAIL | 101 | - | thread 'main' (165252) panicked at examples/features/src/uniform_values/mod.rs:141:14: |
| render_with_compute | FAIL | 101 | - | thread 'main' (165258) panicked at examples/features/src/framework.rs:305:14: |
| conservative_raster | FAIL | 101 | - | thread 'main' (165262) panicked at examples/features/src/utils.rs:226:24: |
| ray_aabb_compute | FAIL | 101 | - | thread 'main' (165352) panicked at examples/features/src/utils.rs:226:24: |
```

