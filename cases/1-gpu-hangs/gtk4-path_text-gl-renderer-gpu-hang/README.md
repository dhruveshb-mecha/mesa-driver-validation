# GTK4 stock demo `path_text` hangs the GPU with the GL renderer (Cairo renderer is fine)

**Verdict:** GPU HANG

## What was run
Runs the stock `gtk4-demo --run path_text` (Fedora gtk4-devel-tools 4.22.5) with `GSK_RENDERER=gl` on a Wayland/sway session and screenshots it.

## Result
`etnaviv-gpu 38000000.gpu: recover hung GPU!` 2 times in the dedicated repro and 2 times in the full GL sweep, offending task `gtk4-demo (gtk4-demo --run path_text)`. The window ends up completely black (screenshot in the artifacts). The board stays up. The project notes record the same result in 3 of 3 repeats; the two harness runs here are the ones that were kept.

## Why it matters
Best driver-bug candidate from the GTK4 work: a small scene with no heavy shader. In the Cairo sweep (`attempt-03`) `path_text` causes no hang and renders the text on a path correctly. **Note:** both sweeps also contain the `shadertoy` hangs (a separate case), so their kernel sections list shadertoy events too; the `path_text` events are the ones whose offending task names `--run path_text`.

## What to look into
Reproduce with the command below and identify which GSK GL op (path/text tessellation, stencil, clip) produces the command stream the GPU cannot finish. An etnaviv command stream has not been captured yet.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_demo_sweep.py gl /tmp/gtk4-demo-repro-path_text-gl 7 '^path_text$'
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-repro-gl-renderer-hang` | GPU_HANG | 0 | 9.3 | 2 | 75.0 | yes |
| `attempt-02-sweep-of-111-demos-gl-renderer` | GPU_HANG | 0 | 807.2 | 6 | 74.0 | yes |
| `attempt-03-control-cairo-renderer-renders-correctly` | GPU_HANG | 0 | 799.0 | 6 | 73.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Kernel GPU events (etnaviv)
Lines from the kernel journal window of each attempt, time of day only.

**attempt-01-repro-gl-renderer-hang**
```
17:09:58.340416 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:58.346311 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run path_text)
17:09:59.364180 etnaviv-gpu 38000000.gpu: recover hung GPU!
17:09:59.369207 etnaviv-gpu 38000000.gpu: offending task: gtk4-demo (gtk4-demo --run path_text)
```

**attempt-02-sweep-of-111-demos-gl-renderer**
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

**attempt-03-control-cairo-renderer-renders-correctly**
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

**attempt-01-repro-gl-renderer-hang**
```
{"demo": "path_text", "renderer_requested": "gl", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 2, "gtk_renderer": "GskGLRenderer", "blank": null}
```

**attempt-02-sweep-of-111-demos-gl-renderer**
```
{"demo": "path_text", "renderer_requested": "gl", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 2, "gtk_renderer": "GskGLRenderer", "blank": null}
```

**attempt-03-control-cairo-renderer-renders-correctly**
```
{"demo": "path_text", "renderer_requested": "cairo", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 2, "gtk_renderer": "GskCairoRenderer", "blank": null}
```

