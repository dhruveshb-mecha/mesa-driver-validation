# Chromium video and NV12 on Mesa 27 `mr46144` (etnaviv)

Video playback in Chromium on the Mecha Comet, and a set of small test programs that isolate why the picture is wrong when Chromium uses the GPU for NV12 frames.

| | |
|---|---|
| Date | 2026-11-13 |
| Board | Mecha Comet, i.MX8M Plus, Vivante GC7000UL rev 6204, 3.9 GB RAM, sway/Wayland |
| Software | Fedora 44 aarch64, kernel 7.2.4, Chromium 156 (Fedora build, `--ozone-platform=wayland`) |
| Mesa builds | `7b4b394` (before) and **`8838d84` `mr46144`** (after: includes the etnaviv patch "Allocate the planes of an NV12 resource") |
| Details | [`output/environment.txt`](output/environment.txt) |

## Summary

1. **Allocation is fixed.** With `mr46144`, `gbm_bo_create(NV12)` returns two planes and two fds. Before, it returned one plane, and Chromium with default flags showed no video (`gbm_pixmap_wayland.cc: Cannot create bo with format=(Y_UV, 420, 8unorm, ExtSamplerOn)`).
2. **Playback is much smoother, but the picture is wrong.** Dropped frames fall from about 37-49% (CPU-copy workaround) to 9-19% on 30 fps local clips. With default flags the picture has a colour tint, vertical streaks and a diagonal tear; with the workaround flag it is clean.
3. **The fault is in the GPU colour conversion of a single NV12 image, not in the buffers.** Reading and writing each plane separately through the GPU is exact. Sampling both planes as one NV12 `EGLImage` through `samplerExternalOES` (the path Chromium uses) returns wrong colours with simple test patterns.
4. **Decoding is software.** `chrome://gpu` reports "Video Decode: Software only"; compositing, rasterization and canvas are hardware accelerated through ANGLE on `Vivante GC7000 rev 6204`.
5. **YouTube stalls** on this board: after 8-18 s the playback position freezes while a buffering spinner shows. Cause not found.

## 1. NV12 allocation

[`output/gbmplanes.txt`](output/gbmplanes.txt) (`test-programs/gbmplanes.py`, 1920x1080 on `mr46144`):

```
NV12 RENDERING          plane_count=2 modifier=0x0 stride0=1920 fd_for_plane=[10, 11]
NV12 LINEAR             plane_count=2 modifier=0x0 stride0=1920 fd_for_plane=[12, 13]
NV12 SCANOUT|RENDERING  plane_count=2 modifier=0x0 stride0=1920 fd_for_plane=[14, 15]
```

On `7b4b394` the same call returned `plane_count=1` with a single fd (measured before the update; that raw output was not kept).

## 2. Chromium playback of local clips

Player page counts `getVideoPlaybackQuality()` frames; 30 s clips; `mr46144`.

| Clip | Default flags: dropped | CPU-copy flag (`--disable-gpu-memory-buffer-video-frames`): dropped | Picture with default flags |
|---|---|---|---|
| VP9 1080p30 | 107 / 900 = **11.9%** | 437 / 900 = 48.6% | tinted, streaks |
| VP9 720p30 | 93 / 900 = **10.3%** | - | tinted, streaks |
| H.264 1080p30 | 103 / 530 = **19.4%** (stopped at 17.5 s) | - | tinted, streaks |

Raw samples: [`local-clips/`](local-clips/). Screenshots: [`default-flags-vp9_1080p30.png`](local-clips/default-flags-vp9_1080p30.png) (corrupted) and [`cpu-copy-flag-vp9_1080p30.png`](local-clips/cpu-copy-flag-vp9_1080p30.png) (clean). Earlier runs on `7b4b394` (raw logs not kept): default flags showed 0 frames; with the CPU-copy flag VP9 1080p30 dropped about 49%, VP9 720p30 46%, H.264 1080p30 37%, AV1 1080p30 75%. CPU use was 200-300% (4 cores) with the workaround and 110-260% with default flags.

## 3. Where the colour error comes from

Programs in [`test-programs/`](test-programs/); raw output in [`output/`](output/). All use a GBM NV12 buffer allocated on `/dev/dri/renderD128`, EGL dma-buf import and an ES context on the etnaviv GPU. Both NV12 usages (`RENDERING`, `LINEAR`) come back with modifier `0x0` (linear).

| Test | Result |
|---|---|
| Plain system-memory NV12 / I420 / RGBA through the GStreamer GL sink | identical and correct ([`screenshots/gst-glimagesink-nv12-i420-rgba.png`](screenshots/gst-glimagesink-nv12-i420-rgba.png)) |
| Control: XRGB8888 linear buffer, same harness (`xr24_ctl`) | 0 / 32 cells wrong |
| One NV12 `EGLImage`, `samplerExternalOES`, 8 colour bars (`nv12_dmabuf_test`): 256x256, 640x360, 1280x720, 1920x1080 linear, 640x360 rendering | **31 / 32 cells wrong** in every case ([`screenshots/nv12_compare.png`](screenshots/nv12_compare.png)) |
| Each plane imported separately as R8 and GR88; CPU writes, GPU reads (`nv12_planes`, section A) | 0 wrong (640x360 and 1920x1080, both usages) |
| Same planes; GPU writes with `glTexSubImage2D` (ES 3 `GL_RED` / `GL_RG`), CPU reads (section B) | 0 wrong |
| One NV12 image, luma ramp with neutral chroma (section C0) | about half of the sampled pixels wrong; low luma clamps to black |
| One NV12 image, flat Y=126, varying U or V (section E) | see below |

Notes on reading these results:

- **Layout, stride and GPU/CPU access are correct** (sections A and B). The faulty step is the YUV-to-RGB conversion of the combined image.
- **Luma with neutral chroma** (section D, flat U=V=128): output is close to expected but with a gain of about 1.35 instead of 1.164 (Y=64 gives 47 against an expected 56, Y=126 gives 130 against 128, Y=200 gives 231 against 214). That fits the narrow-range expansion being applied twice (1.164 x 1.164); this is an inference, not verified.
- **Chroma is mis-mapped** (section E, flat Y=126, expected R/G/B in the right column):

  | Changed | Value | Got r,g,b | Expected r,g,b |
  |---|---|---|---|
  | U | 64 | 28, 207, 1 | 128, 153, 0 |
  | U | 192 | 233, 53, 255 | 128, 103, 255 |
  | V | 64 | 12, 12, 12 | 26, 180, 128 |
  | V | 192 | 251, 250, 251 | 230, 76, 128 |

  Changing only U moves red and blue together, with green opposite; changing only V moves all three channels equally, so it acts like brightness. U and V are not mapped to Cb and Cr correctly.
- The XRGB control is valid for linear buffers only. A tiled `RENDERING` XRGB buffer cannot be filled linearly from the CPU, so no control was recorded for it.
- Not tested: Chromium's own GPU-side buffer writes, and an older Mesa build for comparison.

## 4. `chrome://gpu` (Wayland)

[`output/chrome-gpu-wayland.txt`](output/chrome-gpu-wayland.txt): ANGLE on `Mesa, Vivante GC7000 rev 6204, OpenGL ES 3.0 Mesa 27.0.0-devel`; Canvas, Compositing and Rasterization hardware accelerated; "Video Decode: Software only. Hardware acceleration disabled"; video acceleration information empty. The board's hardware decoder (Hantro VPU, `/dev/video4-6`) is not used by this Chromium build.

## 5. YouTube

Chromium driven over the DevTools protocol (`test-programs/chromium/ytprobe.py`), muted, no ad, 40-45 s per run; the probe records `getVideoPlaybackQuality()` and player state. Network was not the limit (10 MB/s download, 25 ms ping).

**60 fps** (Big Buck Bunny, `aqz-KE-bpKQ`), [`youtube/60fps/`](youtube/60fps/):

| Run | Frames dropped / decoded | CPU | Picture |
|---|---|---|---|
| 720p, default flags | 990 / 1839 = **54%** | about 320% | tinted, streaks |
| 1080p, default flags | 480 / 825 = **58%** | about 330% | not inspected |
| 720p, CPU-copy flag | 1083 / 1552 = **70%** | about 310% | clean |

**About 24 fps** (Big Buck Bunny, `YE7VzlLtp-4`), [`youtube/30fps/`](youtube/30fps/):

| Run | Dropped / decoded at stall onset | Dropped / decoded at end of run |
|---|---|---|
| 480p, default flags | 65 / 326 = 20% | 156 / 944 = 17% |
| 720p, default flags | 61 / 268 = 23% | 221 / 892 = 25% |
| 720p, default flags, `--mute-audio` | 105 / 314 = 33% | 342 / 934 = 37% |
| 720p, CPU-copy flag | 135 / 338 = 40% | 578 / 954 = 61% |
| 720p, CPU-copy flag, `--mute-audio` | 139 / 228 = 61% | 462 / 719 = 64% |

Observations:

- **Stall.** In every YouTube run the video's `currentTime` freezes after 8-19 s (8-13.6 s at 24 fps, 13.6-18.7 s at 60 fps) with `readyState` 4, 54.7 s buffered, not seeking and not hidden, while the frame counters keep rising and a buffering spinner is shown ([`720p-default-extended-probe.txt`](youtube/30fps/720p-default-extended-probe.txt)). It also happens with `--mute-audio`. Local files play to the end. The cause was not found.
- **Fence errors.** Default-flag runs log 7-43 `gpu_fence.cc: sync_file_info status error` lines in Chromium's stderr per run; CPU-copy runs log none. Not investigated.
- **60 fps source** is beyond what four cores decode in software; compare the 24 fps rows.

## Reproduce

Build for the board (headers from the target sysroot, libraries copied from the board's `/usr/lib64`):

```
aarch64-linux-gnu-gcc -Iinc test-programs/nv12_dmabuf_test.c -o nv12_dmabuf_test \
    libgbm.so.1 libEGL.so.1 libGLESv2.so.2 -Wl,--unresolved-symbols=ignore-in-shared-libs
```

`nv12_planes.c` additionally needs the GLES3 headers. On the board:

```
python3 gbmplanes.py
./nv12_dmabuf_test 640 360 16      # args: width height usage (4 = RENDERING, 16 = LINEAR); exit 1 on mismatch
./nv12_planes 640 360 16           # sections A-E
./xr24_ctl 16                      # control, usage only
test-programs/chromium/run_clip.sh <clip> <outdir>                                  # local clip in Chromium (Wayland), samples + screenshot
test-programs/chromium/run_clip.sh <clip> <outdir> --disable-gpu-memory-buffer-video-frames   # CPU-copy comparison
python3 test-programs/chromium/ytprobe.py <youtube url> <hd720|large|hd1080> <seconds>        # against a running Chromium on port 9222
```

Chromium 156 on Wayland crashes on the first keyboard event (`xkb_state_update_mask` in `ui::WaylandKeyboard::OnModifiers`); the tests above send no keys. Running through Xwayland (`--ozone-platform=x11`) avoids the crash.

## Layout

```
README.md
test-programs/   nv12_dmabuf_test.c  nv12_planes.c  xr24_ctl.c  gbmplanes.py
                 chromium/  player.html  run_clip.sh  ytprobe.py  ytprobe2.py  cdptext.py
output/          raw output of the test programs, chrome://gpu dump, package/kernel versions
local-clips/     per-second player samples and screenshots for the local clips
youtube/         60fps/ and 30fps/: probe samples (one line per ~5 s) and screenshots
screenshots/     expected-vs-GPU colour bars, GStreamer reference, first Chromium screenshots
```
