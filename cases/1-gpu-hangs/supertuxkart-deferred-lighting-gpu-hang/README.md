# SuperTuxKart 1.5 on native OpenGL ES 3.0 hangs the GPU at track load when dynamic lights (deferred renderer) are enabled

**Verdict:** GPU HANG

## What was run
`supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40` with the default config (`enable_dynamic_lights=true`). Context is `OpenGL ES 3.0 Mesa 27.0.0-devel`, no GL version override.

## Result
`recover hung GPU!` at track load (offending task `supertuxkart`), the game never reaches the profile phase. Reproduced in 2 harness runs here plus 3/3 manual attempts (manual attempts are not in the harness logs).

## Why it matters
Native ES 3.0, no override, so this is the cleanest hang report we have. With `enable_dynamic_lights=false` the same race runs fine (98.97 fps average, 5405 frames, no kernel messages), see `../../4-passing/game-supertuxkart-legacy-lighting-ok`. Shadows, SSAO, MLAA, motion blur and bloom were already off, so the trigger is something in the deferred lighting path (float/half-float RTs, MRT, UBOs, instancing ...).

## What to look into
Bisect which pass/feature in the deferred pipeline produces the hanging command stream (command-stream dump of the failing frame).

## Command (as run on the Comet)
```
supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run-1-first-detected-by-harness` | GPU_HANG | 0 | 120.8 | 1 | 81.0 | no |
| `attempt-02-run-2-with-driver-debug-logging` | GPU_HANG | 0 | 120.9 | 1 | 82.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Kernel GPU events (etnaviv)
Lines from the kernel journal window of each attempt, time of day only.

**attempt-01-run-1-first-detected-by-harness**
```
07:40:00.947499 etnaviv-gpu 38000000.gpu: recover hung GPU!
07:40:00.949521 etnaviv-gpu 38000000.gpu: offending task: supertuxkart (supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40)
```

**attempt-02-run-2-with-driver-debug-logging**
```
15:13:31.011634 etnaviv-gpu 38000000.gpu: recover hung GPU!
15:13:31.014146 etnaviv-gpu 38000000.gpu: offending task: supertuxkart (supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40)
```

## Key lines from the logs

**attempt-01-run-1-first-detected-by-harness**
```
[info   ] [IrrDriver Logger]: Using renderer: OpenGL ES 3.0 Mesa 27.0.0-devel
[info   ] IrrDriver: OpenGL version: 3.0
[info   ] IrrDriver: OpenGL vendor: Mesa
[info   ] IrrDriver: OpenGL renderer: Vivante GC7000 rev 6204
[info   ] IrrDriver: OpenGL version string: OpenGL ES 3.0 Mesa 27.0.0-devel
```

**attempt-02-run-2-with-driver-debug-logging**
```
[info   ] [IrrDriver Logger]: Using renderer: OpenGL ES 3.0 Mesa 27.0.0-devel
[info   ] IrrDriver: OpenGL version: 3.0
[info   ] IrrDriver: OpenGL vendor: Mesa
[info   ] IrrDriver: OpenGL renderer: Vivante GC7000 rev 6204
[info   ] IrrDriver: OpenGL version string: OpenGL ES 3.0 Mesa 27.0.0-devel
```

