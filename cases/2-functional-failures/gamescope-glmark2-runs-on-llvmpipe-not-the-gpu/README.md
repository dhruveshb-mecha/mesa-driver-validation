# gamescope + glmark2 passes but renders on llvmpipe (CPU), not on the Vivante GPU

**Verdict:** MISLEADING PASS

## What was run
`gamescope -W 1280 -H 720 -- glmark2-es2 --fullscreen -b build`.

## Result
glmark2 reports `GL_RENDERER: llvmpipe (LLVM 22.1.8, 128 bits)` and `GL_VERSION: OpenGL ES 3.2 Mesa 27.0.0-devel`; score 31. gamescope itself logs `Failed to get DRM FD from renderer`, `Failed to initialize glamor, falling back to sw` and `DRI3 error: Could not get DRI3 device`; its Vulkan device is llvmpipe.

## Why it matters
gamescope needs Vulkan, and the only Vulkan device is llvmpipe, so the whole nested session is software rendered. The score says nothing about the GPU, and the `ES 3.2` string is llvmpipe's, not etnaviv's (etnaviv reports ES 3.0).

## What to look into
Nothing in Mesa (there is no Vulkan driver for Vivante). Consequence: gamescope is not usable for GPU testing on this board.

## Command (as run on the Comet)
```
gamescope -W 1280 -H 720 -- glmark2-es2 --fullscreen -b build
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run` | RAN_OK | 0 | 13.1 | 0 | 83.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-run**
```
    GL_RENDERER:    llvmpipe (LLVM 22.1.8, 128 bits)
    GL_VERSION:     OpenGL ES 3.2 Mesa 27.0.0-devel
                                  glmark2 Score: 31 
[gamescope] [Info]  vulkan: selecting physical device 'llvmpipe (LLVM 22.1.8, 128 bits)': queue family 0 (general queue family 0)
[gamescope] [Error] wlserver: [types/wlr_drm.c:211] Failed to get DRM FD from renderer
Failed to initialize glamor, falling back to sw
MESA-EGL: warning: DRI3 error: Could not get DRI3 device
MESA-EGL: warning: Ensure your X server supports DRI3 to get accelerated rendering
```

