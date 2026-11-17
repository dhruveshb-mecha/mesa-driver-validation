# Khronos WebGL2 conformance sample: `ext-color-buffer-float` fails and `sync-webgl-specific` times out in both browsers

**Verdict:** FAIL

## What was run
Same 113-test sample of the Khronos WebGL conformance suite run in Chromium 156 (ANGLE on Mesa) and Firefox (native GLES).

## Result
Chromium 109 pass / 3 fail / 1 timeout; Firefox 110 pass / 2 fail / 1 timeout (113 tests each). **Common to both:** `conformance2/extensions/ext-color-buffer-float.html` fails and `conformance2/sync/sync-webgl-specific.html` times out. **Chromium only:** `conformance2/reading/read-pixels-from-fbo-test.html` (INVALID_OPERATION on readPixels, wrong colours) and `conformance/extensions/khr-parallel-shader-compile.html`. **Firefox only:** `conformance2/wasm/readpixels-16gb-wasm-memory.html` (a 16 GB wasm memory test, probably a memory limit rather than the driver).

## Why it matters
Two different browsers with different GL stacks (ANGLE vs native) fail the same tests, which points at Mesa/etnaviv (float colour buffers, sync objects), possibly related to the MSAA float finding.

## What to look into
Look at float colour-buffer render targets and fence/sync objects.

## Command (as run on the Comet)
```
~/bin/validate-full conformance
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-chromium` | RAN_OK | 0 | 395.9 | 0 | 81.0 | yes |
| `attempt-02-firefox` | RAN_OK | 0 | 568.6 | 0 | 81.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-chromium**
```
  [1/113] PASS          conformance/attribs/gl-bindAttribLocation-aliasing.html
  [2/113] PASS          conformance/attribs/gl-disabled-vertex-attrib-update.html
  [3/113] PASS          conformance/attribs/gl-vertexattribpointer.html
  [4/113] PASS          conformance/buffers/buffer-bind-test.html
  [5/113] PASS          conformance/buffers/buffer-uninitialized.html
  [6/113] PASS          conformance/buffers/index-validation-large-buffer.html
  [7/113] PASS          conformance/canvas/buffer-offscreen-test.html
... (106 more distinct lines) ...
Status counts: **FAIL** 3, **PASS** 109, **TIMEOUT/NO-RESULT** 1
Not PASS:
| Test | Status | pass/fail | first failures |
| conformance/extensions/khr-parallel-shader-compile.html | FAIL | 4/2 | FAIL Querying shader status should not wait for compilation. Took 874.7999999970198 ms; FAIL Program should have taken many mor
| conformance2/extensions/ext-color-buffer-float.html | FAIL | 181/4 | FAIL floating-point RGBA16F render target not supported; FAIL floating-point R32F render target not supported; FAIL floating-poin
| conformance2/reading/read-pixels-from-fbo-test.html | FAIL | 187/7 | FAIL getError expected: NO_ERROR. Was INVALID_OPERATION : readPixels should generate no error; FAIL Expected color = 127.5,255,0,
| conformance2/sync/sync-webgl-specific.html | TIMEOUT/NO-RESULT | 0/0 |  |
```

**attempt-02-firefox**
```
  [1/113] PASS          conformance/attribs/gl-bindAttribLocation-aliasing.html
  [2/113] PASS          conformance/attribs/gl-disabled-vertex-attrib-update.html
  [3/113] PASS          conformance/attribs/gl-vertexattribpointer.html
  [4/113] PASS          conformance/buffers/buffer-bind-test.html
  [5/113] PASS          conformance/buffers/buffer-uninitialized.html
  [6/113] PASS          conformance/buffers/index-validation-large-buffer.html
  [7/113] PASS          conformance/canvas/buffer-offscreen-test.html
... (100 more distinct lines) ...
  [108/113] PASS          conformance2/uniforms/dependent-buffer-change.html
  [109/113] PASS          conformance2/vertex_arrays/vertex-array-object.html
  [110/113] PASS          conformance2/vertex_arrays/vertex-array-object-and-disabled-attributes.html
  [111/113] PASS          conformance2/wasm/bufferdata-2gb-in-4gb-wasm-memory.html
  [112/113] PASS          conformance2/wasm/getbuffersubdata-2gb-in-4gb-wasm-memory.html
  [113/113] FAIL          conformance2/wasm/readpixels-16gb-wasm-memory.html
CONFORMANCE pass=110 fail=2 timeout=1 other=0 total=113
```

