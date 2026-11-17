# Deterministic userspace SIGSEGV in Mesa (`dri_drawable_bind_images`) with GTK4's GL renderer

**Verdict:** CRASH

## What was run
`gtk4_bench.py text 30 4`: a GTK4 window with many Gtk.Labels moved every frame inside a Gtk.Fixed, `GSK_RENDERER=gl`, repeated 6 times.

## Result
SIGSEGV 6/6 (also 4/4 at n=20 and n=30, rare at n=10). Same stack in every core: `dri_drawable_bind_images <- dri2_allocate_textures <- dri_st_framebuffer_validate <- st_framebuffer_validate <- st_manager_validate_framebuffers <- st_update_framebuffer_state <- st_Clear <- gsk_gpu_render_pass_op_gl_command <- gsk_gl_frame_submit` (all inside libgallium-27.0.0-devel.so, +0xb8c70). No kernel messages: a window-system framebuffer path, not a GPU hang. The same program with `GSK_RENDERER=cairo` is fine.

## Why it matters
Not reproduced by: a plain window up to 3000x620, per-frame resizing of the requested size. Not ruled out: the window size changing as many labels move. Exact trigger unknown.

## What to look into
Check whether the stack alone points at the bug. Core dumps are available, and a smaller reproducer can be built.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_crash_repro.py 12 text 10
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run-1` | RAN_OK | 0 | 81.6 | 0 | 82.0 | no |
| `attempt-02-run-2` | RAN_FAIL | 0 | 50.2 | 0 | 81.0 | no |
| `attempt-03-run-3-with-driver-debug-logging` | RAN_FAIL | 0 | 50.6 | 0 | 81.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-run-1**
```
  run 1: ok 27.9 fps size 817x620
  run 2: ok 24.3 fps size 863x620
  run 3: ok 24.6 fps size 821x620
  run 4: ok 25.2 fps size 833x620
  run 5: ok 24.3 fps size 840x620
  run 6: ok 24.5 fps size 849x620
  run 7: ok 24.0 fps size 920x620
  run 8: ok 24.5 fps size 855x620
  run 9: ok 24.5 fps size 862x620
  run 10: ok 25.0 fps size 879x620
  run 11: ok 24.9 fps size 838x620
  run 12: ok 24.9 fps size 839x620
CRASHREPRO scene=text n=10 runs=12 segv=0 ok=12 other=0 median_fps=24.55 top_frame=#0  0x0000ffff95578c70 dri_drawable_bind_images (libgallium-27.0.0-devel.so + 0xb8c70)
```

**attempt-02-run-2**
```
  run 1: SIGSEGV
  run 2: SIGSEGV
  run 3: SIGSEGV
  run 4: SIGSEGV
  run 5: SIGSEGV
  run 6: SIGSEGV
CRASHREPRO scene=text n=30 runs=6 segv=6 ok=0 other=0 median_fps=0 top_frame=#0  0x0000ffff70558c70 dri_drawable_bind_images (libgallium-27.0.0-devel.so + 0xb8c70)
```

**attempt-03-run-3-with-driver-debug-logging**
```
  run 1: SIGSEGV
  run 2: SIGSEGV
  run 3: SIGSEGV
  run 4: SIGSEGV
  run 5: SIGSEGV
  run 6: SIGSEGV
CRASHREPRO scene=text n=30 runs=6 segv=6 ok=0 other=0 median_fps=0 top_frame=#0  0x0000ffff9cd68c70 dri_drawable_bind_images (libgallium-27.0.0-devel.so + 0xb8c70)
```

