# GNOME Maps - tile map pan and zoom

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/gnome-maps`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. world-map-idle
2. select-country-globe-view
3. idle-country-view

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| world-map-idle | 0.3 | 2.7 | 3.0 | 0.7 | 2.7 | 2.7 |
| select-country-globe-view | 1.1 | 1.1 | 1.0 | 1.2 | 1.1 | 1.1 |
| idle-country-view | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

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

- Works under every renderer; frame rates are low (1-3 fps) because the view is mostly static and tiles arrive over the network. The phases are too static to say anything about throughput.
- No hang, crash or llvmpipe. Treat this as a does-it-render check (screenshots show the world map, then the globe/country view).

## Screenshots (first GL attempt)

- [world-map-idle](attempt-01-gl/world-map-idle.png)
- [select-country-globe-view](attempt-01-gl/select-country-globe-view.png)
- [idle-country-view](attempt-01-gl/idle-country-view.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
