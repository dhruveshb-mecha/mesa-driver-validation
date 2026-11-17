# Stock `flutter create` counter app with `GDK_GL=gles`

**Verdict:** PASS

## What was run
Smallest possible real Flutter app, cross-built from the stock template.

## Result
Renders with GLCONTEXT=OK. The default-environment launch is in `2-functional-failures/flutter-gtk3-embedder-no-gl-context-without-gdk-gl-gles`.

## Why it matters
Shows the fix is only the environment variable.

## Command (as run on the Comet)
```
(GDK_GL=gles ~/flutter-apps/demo_counter/flutter_counter_demo 2>&1 | grep -E "Impeller|rror|Failed") & sleep 7; grim /tmp/flutter-counter-gles.png; sleep 1; pkill -x flutter_counter; wait
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gdk-gl-gles` | RAN_OK | 0 | 8.5 | 0 | 73.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

