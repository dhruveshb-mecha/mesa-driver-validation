# OpenGL ES 3.0 context, RGBA32 render targets, float depth, transform feedback

**Verdict:** PASS

## What was run
`scripts/gles3_probe.py` native EGL/GLES probes on the Vivante device.

## Result
All pass: `OpenGL ES 3.0 Mesa 27.0.0-devel`, renderer `Vivante GC7000 rev 6204` (hardware), MAX_SAMPLES=4.

## Why it matters
Baseline that the driver exposes a working ES 3.0 context and the basic render-target formats.

## Command (as run on the Comet)
```
python3 scripts/gles3_probe.py --only 'es3_context|hardware_renderer' | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['info'],indent=1)); [print(c['status'],c['name'],c['detail']) for c in d['checks']]; sys.exit(d['verdict']!='PASS')"
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gles3.context` | RAN_OK | 0 | 0.6 | 0 | 81.0 | yes |
| `attempt-02-gles3.rgba32-targets` | RAN_OK | 0 | 0.6 | 0 | 81.0 | yes |
| `attempt-03-gles3.float-depth` | RAN_OK | 0 | 0.6 | 0 | 80.0 | yes |
| `attempt-04-gles3.transform-feedback` | RAN_OK | 0 | 0.6 | 0 | 80.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-gles3.context**
```
 "renderer": "Vivante GC7000 rev 6204",
 "MAX_SAMPLES": 4,
PASS es3_context OpenGL ES 3.0 Mesa 27.0.0-devel
PASS hardware_renderer Vivante GC7000 rev 6204
```

**attempt-02-gles3.rgba32-targets**
```
PASS rt_RGBA32I fbo status 0x8cd5
PASS rt_RGBA32UI fbo status 0x8cd5
PASS rt_RGBA32F fbo status 0x8cd5
PASS ext_color_buffer_float extension advertised?
```

**attempt-03-gles3.float-depth**
```
PASS depth_D32F DEPTH_COMPONENT32F
PASS depth_D32F_S8 DEPTH32F_STENCIL8
```

**attempt-04-gles3.transform-feedback**
```
PASS transform_feedback_16_verts all outputs correct
PASS transform_feedback_200_verts all outputs correct
PASS transform_feedback_1000_verts all outputs correct
```

