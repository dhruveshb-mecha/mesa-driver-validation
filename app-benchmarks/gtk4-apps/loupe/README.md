# Loupe (GNOME Image Viewer) - 6000x4000 JPEG zoom

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/loupe /home/mecha/appbench-run-409904/images/photo1.jpg`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. fit-6000x4000-jpeg-idle
2. zoom-in-keys
3. zoom-out-keys

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| fit-6000x4000-jpeg-idle | 14.7 | 12.7 | 12.7 | 14.7 | 12.7 | 13.0 |
| zoom-in-keys | 3.0 | 17.7 | 17.8 | 3.3 | 17.5 | 18.2 |
| zoom-out-keys | 4.0 | 18.3 | 17.7 | 4.0 | 17.7 | 17.8 |

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

- **GL is ~5x faster than Cairo** for zooming a 6000x4000 JPEG with the keyboard: gl 17.7-18.2 fps, cairo 3.0-4.0 fps. This is the GPU doing what it should.
- Control for the text-editor result: the GL renderer is not slow in general, it is slow for some content.

## Screenshots (first GL attempt)

- [fit-6000x4000-jpeg-idle](attempt-01-gl/fit-6000x4000-jpeg-idle.png)
- [zoom-in-keys](attempt-01-gl/zoom-in-keys.png)
- [zoom-out-keys](attempt-01-gl/zoom-out-keys.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
