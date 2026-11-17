# GTK4 stock demo `layoutmanager2` aborts with the GL renderer (cairo assertion)

**Verdict:** FAIL (probably not Mesa)

## What was run
`gtk4-demo --run layoutmanager2` with `GSK_RENDERER=gl`.

## Result
SIGABRT (project notes: 3 of 3 repeats; one run is kept here): `cairo-surface.c:1822: cairo_surface_set_device_scale: Assertion status == CAIRO_STATUS_SUCCESS failed`. No GPU hang.

## Why it matters
Looks like a GTK/cairo issue (huge surface), not the GPU driver. Listed for completeness so it is not mistaken for a Mesa bug.

## What to look into
None. Do not triage in Mesa.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_demo_sweep.py gl /tmp/gtk4-demo-repro-layoutmanager2-gl 7 '^layoutmanager2$'
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gl-renderer` | RAN_FAIL | 0 | 9.9 | 0 | 77.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-gl-renderer**
```
{"demo": "layoutmanager2", "renderer_requested": "gl", "alive_at_screenshot": false, "early_rc": -6, "crashed": true, "warnings": 2, "gtk_renderer": "GskGLRenderer", "blank": null}
```

