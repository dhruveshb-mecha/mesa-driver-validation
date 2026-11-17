# GTK4 stock demo `shadertoy` hangs the GPU under both the GL and the Cairo renderer

**Verdict:** GPU HANG (needs triage)

## What was run
`gtk4-demo --run shadertoy`: a GtkGLArea running the default preset, a heavy raymarching fragment shader ("battered alien planet", MAX_ITER 65).

## Result
6 `recover hung GPU!` events per run with GSK_RENDERER=gl and 6 with GSK_RENDERER=cairo (offending task `gtk4-demo --run shadertoy`; some events list an empty task name). The project notes record 3 of 3 repeats per renderer. The screenshot shows the image only partially drawn (missing tiles) after the recoveries.

## Why it matters
Because Cairo shows it too, the trigger is the GLES shader inside the GtkGLArea, not GSK. **Caveat:** the shader may simply be too heavy for a GC7000UL at this size, so the hang may be the GPU watchdog timing out rather than a bug.

## What to look into
Check whether a hang on a long-running fragment shader is expected and what the kernel hang timeout is. Lighter shadertoy presets (Mandelbrot etc.) have not been tried.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_demo_sweep.py gl /tmp/gtk4-demo-repro-shadertoy-gl 7 '^shadertoy$'
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gl-renderer` | GPU_HANG | 0 | 11.9 | 6 | 75.0 | yes |
| `attempt-02-cairo-renderer` | GPU_HANG | 0 | 9.7 | 6 | 76.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Kernel GPU events (etnaviv)
Lines from the kernel journal window of each attempt, time of day only.

**attempt-01-gl-renderer**
```
17:09:27.923378 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:27.927010 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:31.387802 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:31.389826 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:32.459780 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:32.461823 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:33.515944 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:33.517954 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:34.571795 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:34.573869 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:35.667510 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:35.669750 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo ()
```

**attempt-02-cairo-renderer**
```
17:09:43.035942 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:43.038152 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:44.203968 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:44.205949 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:45.339614 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:45.341674 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:46.435808 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:46.437883 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:47.515650 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:47.517434 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run shadertoy)
17:09:48.611774 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:48.613934 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo ()
```

## Key lines from the logs

**attempt-01-gl-renderer**
```
{"demo": "shadertoy", "renderer_requested": "gl", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 4, "gtk_renderer": "GskGLRenderer", "blank": null}
```

**attempt-02-cairo-renderer**
```
{"demo": "shadertoy", "renderer_requested": "cairo", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 4, "gtk_renderer": "GskCairoRenderer", "blank": null}
```

