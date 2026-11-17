# Epiphany (GNOME Web, WebKitGTK 6) - CSS + canvas2D + WebGL2 page

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/epiphany --incognito-mode file:///home/mecha/appbench-run-412853/page.html`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. css-canvas-webgl-page
2. scroll-page

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| css-canvas-webgl-page | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| scroll-page | 0.0 | 1.6 | 0.0 | 0.0 | 1.6 | 0.0 |

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

- **Does not load any page on this board**: the tab stays on 'Blank page' with the load bar near the start, for the CSS/canvas/WebGL page, for a one-line local HTML file and for https://example.org. Same in default, gl and cairo.
- Diagnostics kept in `diagnostics/` (screenshots): disabling WebKit's DMABUF renderer and its compositing mode, and setting the session bus explicitly, change nothing; there are no Mesa/EGL errors and no kernel events.
- Cause is not isolated, so this is not a Mesa finding. It needs a WebKitGTK-side check (web process start-up on this image). WebKit's security sandbox was deliberately not disabled.
- Consequence: WebGL through WebKitGTK is **untested** here. WebGL on this Mesa is covered by the Chromium/Firefox cases.

## Screenshots (first GL attempt)

- [css-canvas-webgl-page](attempt-01-gl/css-canvas-webgl-page.png)
- [scroll-page](attempt-01-gl/scroll-page.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
