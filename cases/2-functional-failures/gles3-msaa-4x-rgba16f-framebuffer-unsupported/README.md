# 4x multisampled RGBA16F renderbuffer gives GL_FRAMEBUFFER_UNSUPPORTED although EXT_color_buffer_float is advertised

**Verdict:** FAIL

## What was run
`scripts/gles3_probe.py` checks render targets and 4x MSAA renderbuffers (RGBA8, SRGB8_ALPHA8, RGBA16F) with resolve-content checks, with and without a D24 MSAA depth attachment.

## Result
RGBA8 4x MSAA passes (inside/outside/edge-blended pixels correct, with and without depth). RGBA16F 4x MSAA: `glRenderbufferStorageMultisample` raises no GL error but the framebuffer status is `0x8cdd GL_FRAMEBUFFER_UNSUPPORTED`. Non-MSAA RGBA16F render target is complete.

## Why it matters
User-visible: three.js `webgl_multisampled_renderbuffers` (half-float MSAA target) shows a blank right half in both Chromium (ANGLE) and Firefox (native GLES), see `attempt-02` screenshots. My reading of the ES 3.0 spec is that color-renderable formats must support at least 4 samples; RGBA16F becomes color-renderable with EXT_color_buffer_float.

## What to look into
Check whether 4x MSAA on RGBA16F is intended to be unsupported on GC7000UL. If so, the renderbuffer call should fail (or the extension should not claim it), not succeed silently.

## Command (as run on the Comet)
```
python3 scripts/gles3_probe.py --only 'msaa|rt_SRGB|rt_RGBA16F|rt_RGBA8' | python3 -c "import json,sys; d=json.load(sys.stdin); [print(c['status'],c['name'],c['detail']) for c in d['checks']]; sys.exit(d['verdict']!='PASS')"
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-native-probe` | RAN_FAIL | 1 | 0.6 | 0 | 79.0 | yes |
| `attempt-02-chromium-threejs-msaa-renderbuffer-screenshot` | PENDING_MANUAL | None | 0 | 0 |  | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-native-probe**
```
PASS rt_RGBA8 fbo status 0x8cd5
PASS rt_SRGB8_ALPHA8 fbo status 0x8cd5
PASS rt_RGBA16F fbo status 0x8cd5
PASS msaa_4x_renderbuffer status 0x8cd5 err 0x0
PASS msaa_4x_resolve_content inside px (255, 0, 0) (want 255,0,0), outside px (0, 255, 0) (want 0,255,0), edge-blended px 64, glerr 0x0
PASS msaa_4x_resolve_content_with_depth inside px (255, 0, 0) (want 255,0,0), outside px (0, 255, 0) (want 0,255,0), edge-blended px 64, glerr 0x0
FAIL msaa_4x_resolve_content_rgba16f msaa fbo incomplete: status 0x8cdd (0x8cd6=INCOMPLETE_ATTACHMENT 0x8cd5=complete 0x8d56=INCOMPLETE_MULTISAMPLE 0x8cdd=UNSUPPORTED) glerr-after-storage 0x0
FAIL msaa_4x_resolve_content_rgba16f_with_depth msaa fbo incomplete: status 0x8cdd (0x8cd6=INCOMPLETE_ATTACHMENT 0x8cd5=complete 0x8d56=INCOMPLETE_MULTISAMPLE 0x8cdd=UNSUPPORTED) glerr-after-storage 0
```

