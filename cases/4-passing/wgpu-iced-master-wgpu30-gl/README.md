# iced (git master, wgpu 30) on the GL backend renders the animated canvas on the Vivante device

**Verdict:** PASS

## What was run
`assets/iced-wgpu30-test` cross-built on the laptop, `WGPU_BACKEND=gl`.

## Result
~62 fps (capped by iced's 16 ms timer, not the display) with the correct image. iced 0.14 (wgpu 27) fails with BadMatch; wgpu <= 27 is not usable.

## Why it matters
The wgpu 30 GL path works end-to-end including presentation.

## Command (as run on the Comet)
```
WGPU_BACKEND=gl RUST_LOG=iced_wgpu=info,wgpu_hal=info,warn ~/wgpu-apps/iced-wgpu30-test
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-wgpu30-gl-backend` | RAN_OK | -15 | 15.0 | 0 | 81.0 | yes |
| `attempt-02-iced-0.14-cpu-fallback-screenshot` | PENDING_MANUAL | None | 0 | 0 |  | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-wgpu30-gl-backend**
```
ICED_FPS 60.3
ICED_FPS 61.8
ICED_FPS 62.2
ICED_FPS 62.8   [x2]
ICED_FPS 61.9
ICED_FPS 62.3   [x3]
ICED_FPS 63.1   [x2]
ICED_FPS 62.0
ICED_FPS 61.1
ICED_FPS 63.8
[2026-11-03T09:06:56Z INFO  iced_wgpu::window::compositor] Available adapters: [
            name: "Vivante GC7000 rev 6204",
        name: "Vivante GC7000 rev 6204",
```

