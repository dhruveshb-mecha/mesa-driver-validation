# 10-minute glmark2 soak loop (thermal + stability)

**Verdict:** PASS

## What was run
glmark2-es2 looped for ~11 minutes, with SoC temperatures before/after.

## Result
Completed, score 92, no GPU hang and no kernel errors. SoC reached 80+ C (see `result.json`).

## Why it matters
Shows the GPU is stable under sustained load: the hangs elsewhere are specific workloads, not general instability.

## Command (as run on the Comet)
```
end=$((SECONDS+600)); n=0
while [ $SECONDS -lt $end ]; do n=$((n+1)); echo "--- iteration $n"; glmark2-es2-wayland --fullscreen || exit 1; done
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run` | RAN_OK | 0 | 672.4 | 0 | 81.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-run**
```
                                  glmark2 Score: 88 
                                  glmark2 Score: 92 
```

