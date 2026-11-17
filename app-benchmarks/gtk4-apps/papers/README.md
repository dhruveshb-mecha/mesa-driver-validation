# Papers (GNOME Document Viewer) - 60-page PDF scroll and zoom

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/papers /home/mecha/appbench-run-411428/doc.pdf`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. open-60-page-pdf-idle
2. page-down-keys
3. zoom-in-button
4. scroll-zoomed-pages
5. zoom-out-button

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| open-60-page-pdf-idle | 0.0 | 10.0 | 0.0 | 0.0 | 10.3 | 0.0 |
| page-down-keys | 14.6 | 12.3 | 12.0 | 15.3 | 12.0 | 11.9 |
| zoom-in-button | 5.0 | 3.5 | 5.2 | 5.5 | 5.7 | 5.0 |
| scroll-zoomed-pages | 18.0 | 18.3 | 18.1 | 18.3 | 18.1 | 18.3 |
| zoom-out-button | 9.5 | 9.7 | 9.5 | 9.7 | 9.5 | 10.0 |

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

- PDF paging and zoom behave the same in GL and Cairo (page-down 12-15 fps, zoomed scroll ~18 fps in all modes).
- The first 3 s 'idle' phase differs (default 10 fps, gl/cairo 0) because the document finishes rendering at slightly different times; not a renderer difference.
- Mouse-wheel scrolling did not reach the window in the page-fit view with our synthetic input; keyboard (space) is used instead.

## Screenshots (first GL attempt)

- [open-60-page-pdf-idle](attempt-01-gl/open-60-page-pdf-idle.png)
- [page-down-keys](attempt-01-gl/page-down-keys.png)
- [zoom-in-button](attempt-01-gl/zoom-in-button.png)
- [scroll-zoomed-pages](attempt-01-gl/scroll-zoomed-pages.png)
- [zoom-out-button](attempt-01-gl/zoom-out-button.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
