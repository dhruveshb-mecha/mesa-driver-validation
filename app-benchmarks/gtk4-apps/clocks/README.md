# GNOME Clocks - tabs and stopwatch

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/gnome-clocks`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. world-clocks-idle
2. stopwatch-tab
3. stopwatch-start

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| world-clocks-idle | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| stopwatch-tab | 4.0 | 3.0 | 3.7 | 3.7 | 3.3 | 3.3 |
| stopwatch-start | 1.8 | 1.7 | 1.8 | 1.7 | 1.8 | 1.8 |

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

- Tab switch and stopwatch: same in all renderers, no events. Mostly static UI, so frame rates are low by nature.

## Screenshots (first GL attempt)

- [world-clocks-idle](attempt-01-gl/world-clocks-idle.png)
- [stopwatch-tab](attempt-01-gl/stopwatch-tab.png)
- [stopwatch-start](attempt-01-gl/stopwatch-start.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
