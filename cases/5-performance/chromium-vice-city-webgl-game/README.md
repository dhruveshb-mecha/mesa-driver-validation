# Real WebGL game (Vice City, https://quenq.com/apps/vice-city/) in Chromium for ~5 minutes

**Verdict:** DATA

## What was run
Chromium on Wayland with an in-page requestAnimationFrame fps overlay via DevTools; clean session (light logging) and a full-logging session.

## Result
No GPU hang, no crash. Clean session: average 11.6 fps, median 4.6, 3D street scenes about 5 fps (1-25), loading/cutscene part ~28 fps with peaks 47-54. SoC 75-83 C.

## Why it matters
Cause of the slowness is not established (GPU fill/vertex work, CPU/WASM, or the driver). The full-logging session (including GPU-command tracing) was similar in the 3D scenes, so tracing is not the main factor. The huge raw Chromium log (98 MB) is not shipped.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-clean-session` | PENDING_MANUAL | None | 0 | 0 |  | no |
| `attempt-02-full-logging-session` | PENDING_MANUAL | None | 0 | 0 |  | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

