# WebGL Report and a set of three.js examples in Chromium and Firefox (screenshots)

**Verdict:** PASS (1 known failure)

## What was run
Manually driven page loads with screenshots (bloom, instancing, GPGPU water, shadow map, points, MSAA renderbuffer).

## Result
All pages render except `webgl_multisampled_renderbuffers` (blank right half, the MSAA RGBA16F finding in `2-functional-failures`).

## Why it matters
Visual confirmation of real-world WebGL content on both engines.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-chromium-pages` | PENDING_MANUAL | None | 0 | 0 |  | no |
| `attempt-02-firefox-pages` | PENDING_MANUAL | None | 0 | 0 |  | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

