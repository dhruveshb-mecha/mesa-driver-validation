# GNOME Text Editor - 30000-line file scroll and typing

Track: **gtk4**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/usr/bin/gnome-text-editor /home/mecha/appbench-run-410623/long.txt`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. open-30000-line-file-idle
2. scroll-down-fast
3. scroll-up-fast
4. type-text

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-cairo | a01-default | a01-gl | a02-cairo | a02-default | a02-gl |
|---|---|---|---|---|---|---|
| open-30000-line-file-idle | 37.7 | 0.0 | 8.0 | 38.0 | 0.0 | 7.3 |
| scroll-down-fast | 34.9 | 10.0 | 3.9 | 33.6 | 7.9 | 6.4 |
| scroll-up-fast | 34.7 | 4.1 | 7.9 | 34.0 | 5.6 | 7.0 |
| type-text | 24.4 | 6.4 | 4.8 | 24.0 | 5.8 | 5.0 |

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

- **GL renderer is 4-8x slower than Cairo here.** Scrolling a 30000-line file: gl 4-8 fps, default 4-10 fps, cairo 34-35 fps; typing: gl ~5, cairo ~24. Both attempts agree (see the table).
- `default` is the GL renderer (log: `Using renderer 'GskGLRenderer'`), so an out-of-the-box user gets the slow path.
- The scroll input rate is the same in all modes (one wheel event per 0.25 s), and Cairo reaches 34 fps under it, so the GL path, not the input, is the limit. Text-heavy content is the case to profile (glyph/atlas upload, many small draws).
- Matches the earlier synthetic result in `cases/5-performance/gtk4-renderer-matrix-gl-vs-cairo-16-scenes` (GL slower than Cairo in 14 of 16 scenes), now seen in a real app.
- No GPU hang, crash or kernel message in any of the 6 runs.

## Screenshots (first GL attempt)

- [open-30000-line-file-idle](attempt-01-gl/open-30000-line-file-idle.png)
- [scroll-down-fast](attempt-01-gl/scroll-down-fast.png)
- [scroll-up-fast](attempt-01-gl/scroll-up-fast.png)
- [type-text](attempt-01-gl/type-text.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
