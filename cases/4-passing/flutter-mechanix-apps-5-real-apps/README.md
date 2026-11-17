# Five real Mecha Flutter apps (clock, notes, files, calculator, settings)

**Verdict:** PASS

## What was run
Each app launched for 25 s with the installed Flutter embedder; screenshot taken.

## Result
All five render and run without hang or crash. The `notes` app logs 11x `Unhandled Exception: MissingPluginException(No implementation found for method dismissMenu on channel native_adaptive_toolbox/menu)`: a missing app plugin on this platform, unrelated to the GPU.

## Why it matters
The production Flutter apps work on the driver.

## Command (as run on the Comet)
```
mechanix_clock -b /usr/share/mechanix/mechanix-clock/ -s 1
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-clock` | RAN_OK | -15 | 25.1 | 0 | 79.0 | yes |
| `attempt-02-notes` | RAN_OK | -15 | 25.1 | 0 | 78.0 | yes |
| `attempt-03-files` | RAN_OK | -15 | 25.1 | 0 | 80.0 | yes |
| `attempt-04-calculator` | RAN_OK | -15 | 25.1 | 0 | 79.0 | yes |
| `attempt-05-settings` | RAN_OK | -15 | 25.1 | 0 | 78.0 | yes |
| `attempt-06-screenshot-clock` | RAN_OK | -15 | 25.1 | 0 | 73.0 | no |
| `attempt-07-screenshot-files` | RAN_OK | -15 | 25.1 | 0 | 73.0 | no |
| `attempt-08-screenshot-calculator` | RAN_OK | -15 | 25.1 | 0 | 72.0 | no |
| `attempt-09-screenshot-settings` | RAN_OK | -15 | 25.1 | 0 | 72.0 | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-02-notes**
```
[ERROR:flutter/runtime/dart_vm_initializer.cc(40)] Unhandled Exception: MissingPluginException(No implementation found for method dismissMenu on channel native_adaptive_toolbox/menu)   [x11]
```

