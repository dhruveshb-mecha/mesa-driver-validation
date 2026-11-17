# Firefox: WebGL2, about:support, probe page, Aquarium

**Verdict:** PASS

## What was run
Native Firefox (Wayland) WebGL checks.

## Result
WebGL2 context on the hardware renderer; Aquarium runs.

## Why it matters
Second browser engine on the native GLES path (Chromium uses ANGLE).

## Command (as run on the Comet)
```
rm -rf /tmp/ffprof; mkdir -p /tmp/ffprof; MOZ_ENABLE_WAYLAND=1 firefox --new-instance --profile /tmp/ffprof --no-remote file://$HOME/gpu-test/assets/webgl2-probe.html
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-firefox.webgl2` | RAN_OK | -15 | 40.4 | 0 | 85.0 | yes |
| `attempt-02-firefox.about-support` | RAN_OK | 0 | 32.3 | 0 | 83.0 | yes |
| `attempt-03-firefox.webgl2-probe` | RAN_OK | 0 | 26.5 | 0 | 83.0 | yes |
| `attempt-04-firefox.aquarium` | RAN_OK | 0 | 64.1 | 0 | 82.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-02-firefox.about-support**
```
  webgl1Renderer: Mesa -- Vivante GC7000 rev 6204
  webgl1Version: OpenGL ES 3.0 Mesa 27.0.0-devel
  webgl1Extensions: ANGLE_instanced_arrays EXT_blend_minmax EXT_color_buffer_half_float EXT_frag_depth EXT_sRGB EXT_texture_compression_rgtc MOZ_debug OES_element_index_uint OES_fbo_render_mipmap OES_
  webgl1WSIInfo: EGL_VENDOR: Mesa Project
  webgl2Renderer: Mesa -- Vivante GC7000 rev 6204
  webgl2Version: OpenGL ES 3.0 Mesa 27.0.0-devel
  webgl2Extensions: EXT_color_buffer_float EXT_texture_compression_rgtc MOZ_debug OES_draw_buffers_indexed WEBGL_compressed_texture_astc WEBGL_compressed_texture_etc WEBGL_compressed_texture_etc1 WEBG
```

**attempt-03-firefox.webgl2-probe**
```
   {'webgl2': 'OK', 'renderer': 'Vivante GC1000, or similar', 'version': 'WebGL 2.0', 'max_samples': '4', 'ext_color_buffer_float': 'true', 'rt_RGBA16F': 'PASS', 'rt_RGBA32F': 'PASS', 'rt_RGBA32UI': '
```

