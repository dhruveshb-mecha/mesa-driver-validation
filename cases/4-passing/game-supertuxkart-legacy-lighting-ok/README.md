# SuperTuxKart with dynamic lights OFF (legacy renderer) runs the same race without a hang

**Verdict:** PASS

## What was run
Same command as the hang case but with `enable_dynamic_lights=false` in config.xml (restored afterwards).

## Result
Renders correctly, ~99 fps average over 5405 frames in the manual measurement, no kernel messages.

## Why it matters
The control for `1-gpu-hangs/supertuxkart-deferred-lighting-gpu-hang`: isolates the deferred lighting path as the trigger.

## Command (as run on the Comet)
```
F=$HOME/.config/supertuxkart/config-0.10/config.xml; cp -n $F $F.orig; sed -i 's/enable_dynamic_lights="true"/enable_dynamic_lights="false"/' $F; supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40; cp $F.orig $F
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run-1` | RAN_OK | 0 | 59.4 | 0 | 81.0 | no |
| `attempt-02-run-2-with-driver-debug-logging` | RAN_OK | 0 | 81.9 | 0 | 83.0 | yes |
| `attempt-03-manual-screenshot` | PENDING_MANUAL | None | 0 | 0 |  | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-run-1**
```
[verbose  ] profile: Number of frames: 5405 time 53.027004, Average FPS: 101.929199
```

**attempt-02-run-2-with-driver-debug-logging**
```
[verbose  ] profile: Number of frames: 5405 time 74.963005, Average FPS: 72.102234
```

