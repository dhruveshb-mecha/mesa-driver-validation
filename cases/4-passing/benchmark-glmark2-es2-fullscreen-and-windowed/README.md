# glmark2-es2 full suite, fullscreen and windowed

**Verdict:** PASS

## What was run
Two ~5.5 min runs of the complete glmark2-es2 scene list.

## Result
Fullscreen score 103. Both runs complete with no hang and no kernel errors.

## Why it matters
Broad ES 2.0 coverage of the driver at sustained load.

## Command (as run on the Comet)
```
glmark2-es2-wayland --fullscreen
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-fullscreen` | RAN_OK | 0 | 336.8 | 0 | 82.0 | yes |
| `attempt-02-windowed` | RAN_OK | 0 | 335.8 | 0 | 82.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-fullscreen**
```
[build] use-vbo=false: FPS: 318 FrameTime: 3.150 ms
[build] use-vbo=true: FPS: 374 FrameTime: 2.680 ms
[texture] texture-filter=nearest: FPS: 195 FrameTime: 5.154 ms
[texture] texture-filter=linear: FPS: 165 FrameTime: 6.092 ms
[texture] texture-filter=mipmap: FPS: 168 FrameTime: 5.970 ms
[shading] shading=gouraud: FPS: 186 FrameTime: 5.404 ms
[shading] shading=blinn-phong-inf: FPS: 140 FrameTime: 7.156 ms
... (20 more distinct lines) ...
[conditionals] fragment-steps=0:vertex-steps=5: FPS: 145 FrameTime: 6.911 ms
[function] fragment-complexity=low:fragment-steps=5: FPS: 57 FrameTime: 17.563 ms
[function] fragment-complexity=medium:fragment-steps=5: FPS: 56 FrameTime: 18.037 ms
[loop] fragment-loop=false:fragment-steps=5:vertex-steps=5: FPS: 77 FrameTime: 13.007 ms
[loop] fragment-steps=5:fragment-uniform=false:vertex-steps=5: FPS: 74 FrameTime: 13.520 ms
[loop] fragment-steps=5:fragment-uniform=true:vertex-steps=5: FPS: 47 FrameTime: 21.703 ms
                                  glmark2 Score: 103 
```

**attempt-02-windowed**
```
[build] use-vbo=false: FPS: 465 FrameTime: 2.154 ms
[build] use-vbo=true: FPS: 521 FrameTime: 1.922 ms
[texture] texture-filter=nearest: FPS: 418 FrameTime: 2.395 ms
[texture] texture-filter=linear: FPS: 408 FrameTime: 2.452 ms
[texture] texture-filter=mipmap: FPS: 446 FrameTime: 2.246 ms
[shading] shading=gouraud: FPS: 319 FrameTime: 3.138 ms
[shading] shading=blinn-phong-inf: FPS: 222 FrameTime: 4.511 ms
... (20 more distinct lines) ...
[conditionals] fragment-steps=0:vertex-steps=5: FPS: 281 FrameTime: 3.563 ms
[function] fragment-complexity=low:fragment-steps=5: FPS: 146 FrameTime: 6.896 ms
[function] fragment-complexity=medium:fragment-steps=5: FPS: 100 FrameTime: 10.020 ms
[loop] fragment-loop=false:fragment-steps=5:vertex-steps=5: FPS: 151 FrameTime: 6.654 ms
[loop] fragment-steps=5:fragment-uniform=false:vertex-steps=5: FPS: 153 FrameTime: 6.573 ms
[loop] fragment-steps=5:fragment-uniform=true:vertex-steps=5: FPS: 94 FrameTime: 10.671 ms
                                  glmark2 Score: 190 
```

