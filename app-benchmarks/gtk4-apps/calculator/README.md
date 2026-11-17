# GNOME Calculator - widgets and popover

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/gnome-calculator`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. startup-idle
2. type-expression
3. open-mode-popover

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| startup-idle | 28.3 | 29.0 | 28.3 | 28.0 | 29.3 | 28.3 |
| type-expression | 24.5 | 23.5 | 23.5 | 24.5 | 24.0 | 24.2 |
| open-mode-popover | 2.3 | 2.0 | 1.7 | 2.3 | 2.0 | 1.7 |

A static screen redraws only on change, so ~0 fps there is correct; judge throughput from the phases that scroll, zoom or animate.

## Health per attempt

| attempt | app alive at end | GPU hang events | other etnaviv/drm kernel lines | llvmpipe seen in log |
|---|---|---|---|---|
| attempt-01-cairo | True | 0 | 0 | False |
| attempt-01-default | True | 0 | 0 | False |
| attempt-01-gl | True | 0 | 0 | False |
| attempt-02-cairo | True | 0 | 0 | False |
| attempt-02-default | True | 0 | 0 | False |
| attempt-02-gl | True | 0 | 0 | False |

## What this shows / what to look into

- Widgets and popover only. Same behaviour in all renderers, no events. ~28-29 fps while 'idle' in every mode (see font-viewer note).

## Screenshots (first GL attempt)

- [startup-idle](attempt-01-gl/startup-idle.png)
- [type-expression](attempt-01-gl/type-expression.png)
- [open-mode-popover](attempt-01-gl/open-mode-popover.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
