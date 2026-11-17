# Extended GPU validation report

- Mesa: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`; kernel 7.1.5-0.mecha.202608260642.fc44.aarch64; Chromium 156.0.8078.47 Built from source for Fedora release 44 (Forty Four)
- Date: 2026-11-03 14:18 (board clock, no RTC); phases: conformance

## 2. Khronos WebGL conformance (sample, 113 of ~700 tests, ≤3 per directory, WebGL1 + WebGL2)

Status counts: **FAIL** 3, **PASS** 109, **TIMEOUT/NO-RESULT** 1

Not PASS:

| Test | Status | pass/fail | first failures |
|---|---|---|---|
| conformance/extensions/khr-parallel-shader-compile.html | FAIL | 4/2 | FAIL Querying shader status should not wait for compilation. Took 874.7999999970198 ms; FAIL Program should have taken many more than 6 frames to compile. Actual value: 0 frames, duration 890.60000000 |
| conformance2/extensions/ext-color-buffer-float.html | FAIL | 181/4 | FAIL floating-point RGBA16F render target not supported; FAIL floating-point R32F render target not supported; FAIL floating-point RG32F render target not supported |
| conformance2/reading/read-pixels-from-fbo-test.html | FAIL | 187/7 | FAIL getError expected: NO_ERROR. Was INVALID_OPERATION : readPixels should generate no error; FAIL Expected color = 127.5,255,0,0, was = 0,0,0; FAIL getError expected: NO_ERROR. Was INVALID_OPERATION |
| conformance2/sync/sync-webgl-specific.html | TIMEOUT/NO-RESULT | 0/0 |  |

Full list in `results.json`.

Raw logs, screenshots (`shot-*.png`) and `results.json` are in `/home/mecha/benchmarks/reports/full-validation-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-141125/`.
