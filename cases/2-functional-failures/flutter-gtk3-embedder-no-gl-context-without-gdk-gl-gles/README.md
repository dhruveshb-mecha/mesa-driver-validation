# Flutter (GTK3 embedder) cannot create a GL context by default; works with `GDK_GL=gles`

**Verdict:** FAIL (config)

## What was run
Stock Flutter Linux app, cross-built on x86 (`flutter/build-arm64.sh`), Impeller OpenGLES. Two launches: default environment vs `GDK_GL=gles`.

## Result
Default: "Failed to create OpenGL context", the app runs headless and presents nothing (`GLCONTEXT=FAIL`). With `GDK_GL=gles`: renders correctly (see passing cases).

## Why it matters
Not a Mesa bug. GTK3 asks for desktop GL and etnaviv only exposes ES 3.0 + GL 2.1 compat. Needs `GDK_GL=gles` in the image or app launcher.

## What to look into
Nothing in Mesa. Set `GDK_GL=gles` as an image/app-launcher default.

## Command (as run on the Comet)
```
out=$(GDK_BACKEND=wayland ~/flutter-apps/gpu_bench/gpu_bench circles 10 4 2>&1); if echo "$out" | grep -q "Failed to create OpenGL context"; then echo "GLCONTEXT=FAIL (GTK3 cannot create a GL context with default settings)"; else echo "GLCONTEXT=OK"; fi
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gpu_bench-default-env` | RAN_FAIL | 0 | 6.7 | 0 | 79.0 | yes |
| `attempt-02-stock-counter-app-default-env` | RAN_FAIL | 0 | 8.1 | 0 | 73.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-gpu_bench-default-env**
```
GLCONTEXT=FAIL (GTK3 cannot create a GL context with default settings)
```

**attempt-02-stock-counter-app-default-env**
```
GLCONTEXT=FAIL (GTK3 cannot create a GL context with default settings)
```

