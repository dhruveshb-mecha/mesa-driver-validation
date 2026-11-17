# Nautilus (GNOME Files) - thumbnail grid scrolling

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/nautilus --new-window /home/mecha/appbench-run-408717/files`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. folder-grid-idle
2. open-folder-with-image-thumbnails
3. scroll-thumbnails-down
4. scroll-thumbnails-up
5. switch-to-list-view

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| folder-grid-idle | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| open-folder-with-image-thumbnails | 15.2 | 20.2 | 19.8 | 10.8 | 20.2 | 12.7 |
| scroll-thumbnails-down | 13.7 | 19.2 | 13.0 | 11.0 | 14.8 | 13.7 |
| scroll-thumbnails-up | 14.5 | 10.8 | 10.5 | 9.7 | 13.5 | 10.0 |
| switch-to-list-view | 14.0 | 21.5 | 21.0 | 14.0 | 20.7 | 21.2 |

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

- Thumbnail grid and list view: GL (default/gl) and Cairo are within run-to-run noise of each other (10-21 fps, large spread between the two attempts because thumbnails load asynchronously).
- No hang or crash in 6 runs; this is the 'file manager with many image thumbnails' case people use daily.

## Screenshots (first GL attempt)

- [folder-grid-idle](attempt-01-gl/folder-grid-idle.png)
- [open-folder-with-image-thumbnails](attempt-01-gl/open-folder-with-image-thumbnails.png)
- [scroll-thumbnails-down](attempt-01-gl/scroll-thumbnails-down.png)
- [scroll-thumbnails-up](attempt-01-gl/scroll-thumbnails-up.png)
- [switch-to-list-view](attempt-01-gl/switch-to-list-view.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
