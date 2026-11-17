# GNOME Font Viewer - list scroll and search

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/gnome-font-viewer`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. font-list-idle
2. scroll-font-list
3. search-sans

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| font-list-idle | 30.7 | 29.0 | 29.0 | 30.3 | 29.3 | 29.7 |
| scroll-font-list | 17.6 | 27.1 | 26.7 | 13.6 | 27.0 | 25.9 |
| search-sans | 32.2 | 31.7 | 31.2 | 31.5 | 31.2 | 31.5 |

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

- GL is faster than Cairo when scrolling the font list: gl 26-27 fps vs cairo 14-18 fps.
- Idle phases show ~29-30 fps in every mode including Cairo: something redraws at ~30 Hz without input. Not renderer related; cause not investigated.

## Screenshots (first GL attempt)

- [font-list-idle](attempt-01-gl/font-list-idle.png)
- [scroll-font-list](attempt-01-gl/scroll-font-list.png)
- [search-sans](attempt-01-gl/search-sans.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
