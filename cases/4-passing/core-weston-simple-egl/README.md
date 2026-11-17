# weston-simple-egl on the Wayland compositor

**Verdict:** PASS

## What was run
Plain EGL client, 12 s.

## Result
~50-51 fps (vsync-locked; see "Reading the fps numbers" in the top-level README).

## Why it matters
EGL window-surface path works on sway.

## Command (as run on the Comet)
```
stdbuf -oL weston-simple-egl
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run` | RAN_OK | -15 | 12.0 | 0 | 80.0 | yes |
| `attempt-02-earlier-run-with-screenshot` | RAN_OK | -15 | 12.0 | 0 | 75.0 | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-run**
```
Using config: r8g8b8a8
255 frames in 5 seconds: 51.000000 fps
252 frames in 5 seconds: 50.400002 fps
```

**attempt-02-earlier-run-with-screenshot**
```
Using config: r8g8b8a8
257 frames in 5 seconds: 51.400002 fps
253 frames in 5 seconds: 50.599998 fps
```

