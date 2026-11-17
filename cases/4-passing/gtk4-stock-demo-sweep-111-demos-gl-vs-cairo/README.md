# All 111 stock `gtk4-demo` examples, run with GL and with Cairo

**Verdict:** PASS (3 exceptions)

## What was run
`gtk4_demo_sweep.py`: each example is run for 6 s, screenshot + log per demo, crash/blank detection.

## Result
GL: 110/111 alive after 6 s. Cairo: 111/111. The exceptions are in `1-gpu-hangs` (path_text, shadertoy) and `2-functional-failures` (layoutmanager2). `gears` and `glarea` (the GtkGLArea demos besides shadertoy) are fine. Only `video_player` (no video) and `iconview_edit` are blank by design.

## Why it matters
Gives the reviewing team the full coverage picture, so the three problem demos are seen against 108 that work. Full per-demo table: `summary-*.md`. Screenshots for the failing demos and a representative set of working ones are included for both renderers.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_demo_sweep.py gl /tmp/gtk4-demo-sweep 6
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gl-renderer` | GPU_HANG | 0 | 807.2 | 6 | 74.0 | yes |
| `attempt-02-cairo-renderer` | GPU_HANG | 0 | 799.0 | 6 | 73.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Kernel GPU events (etnaviv)
Lines from the kernel journal window of each attempt, time of day only.

**attempt-01-gl-renderer**
```
16:44:05.612301 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:44:05.614417 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:44:09.043602 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:44:09.045791 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:44:10.115964 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:44:10.117932 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:44:11.211800 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:44:11.214690 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo ()
16:46:40.043724 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:46:40.047165 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run path_text)
16:46:41.083395 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:46:41.086624 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run path_text)
```

**attempt-02-cairo-renderer**
```
16:57:30.099495 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:57:30.102572 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:57:31.307980 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:57:31.310035 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:57:32.443973 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:57:32.446027 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:57:33.539774 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:57:33.541859 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:57:34.612611 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:57:34.614736 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
16:57:35.715737 etnaviv-gpu 38000000.gpu: recover hung GPU!
16:57:35.718354 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo ()
```

## Key lines from the logs

**attempt-01-gl-renderer**
```
GTK4DEMOSWEEP renderer=gl demos=111 ok=110 crashed=1 blank=0
```

**attempt-02-cairo-renderer**
```
GTK4DEMOSWEEP renderer=cairo demos=111 ok=111 crashed=0 blank=0
```

