# wgpu native examples on the GL backend: cube and bunnymark (100 / 500)

**Verdict:** PASS

## What was run
wgpu-rs examples cross-built, `WGPU_BACKEND=gl`, screenshot taken.

## Result
Adapter is `Vivante GC7000 rev 6204 (Gl)`; both render. The wgpu-hal log says `Using surfaceless platform` here too, and rendering works. The full 24-example sweep (17 pass) is in `2-functional-failures/wgpu-native-examples-7-of-24-fail-...`.

## Why it matters
wgpu 30 on GL is a usable path on this board.

## Command (as run on the Comet)
```
WGPU_BACKEND=gl RUST_LOG=info ~/wgpu/target/release/wgpu-examples cube
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-cube` | RAN_OK | -15 | 15.0 | 0 | 81.0 | yes |
| `attempt-02-bunnymark-100` | RAN_OK | -15 | 20.4 | 0 | 81.0 | yes |
| `attempt-03-bunnymark-500` | RAN_OK | -15 | 20.3 | 0 | 82.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-cube**
```
[2026-11-03T09:05:28.243Z INFO  wgpu_examples::framework] Selected adapter: Vivante GC7000 rev 6204 (Gl)
```

**attempt-02-bunnymark-100**
```
Spawning 100 bunnies, total at 100
[2026-11-03T09:05:46.292Z INFO  wgpu_examples::framework] Selected adapter: Vivante GC7000 rev 6204 (Gl)
```

**attempt-03-bunnymark-500**
```
Spawning 500 bunnies, total at 500
[2026-11-03T09:06:09.761Z INFO  wgpu_examples::framework] Selected adapter: Vivante GC7000 rev 6204 (Gl)
```

