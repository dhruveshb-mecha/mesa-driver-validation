# GNOME Characters - emoji grid scroll and search

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/gnome-characters`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. emoji-grid-idle
2. switch-emoji-categories
3. search-heart

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| emoji-grid-idle | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| switch-emoji-categories | 22.9 | 22.4 | 22.4 | 23.3 | 22.2 | 22.6 |
| search-heart | 26.5 | 24.7 | 24.5 | 26.0 | 24.7 | 25.0 |

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

- Emoji category switching renders at ~22-23 fps in all three modes; search ~25 fps. No differences between renderers.
- Mouse-wheel scrolling did not reach the window with our synthetic input, so categories are switched by taps instead.

## Screenshots (first GL attempt)

- [emoji-grid-idle](attempt-01-gl/emoji-grid-idle.png)
- [switch-emoji-categories](attempt-01-gl/switch-emoji-categories.png)
- [search-heart](attempt-01-gl/search-heart.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
