# Qt 6.11.2 Quick 3D examples hang the GPU (runs with an unsupported GL 3.3 override)

**Verdict:** GPU HANG

## What was run
`validate-qt` smoke-runs the stock Qt Quick 2D/3D examples. Fedora's Qt6 has no GLES backend and etnaviv exposes desktop GL 2.1, so the test forces `MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330`.

## Result
4-5 `recover hung GPU!` events per run in 3 independent runs, offending task `QSGRenderThread` of the Quick 3D examples principledmaterial, reflectionprobes, cascadedshadowmaps, sceneeffects. The board stays up. The validator prints PASS/WARN for those examples; only the kernel log shows the hangs.

With the override, Quick 3D ran at 24.7 fps against 5.9 fps on llvmpipe (16 PBR spheres), and Quick 2D at 24.0 against 18.7 fps. The same examples were also run on a Qt built for OpenGL ES without any override: [`qt-quick3d-gpu-hang-on-gles-qt-without-override`](../qt-quick3d-gpu-hang-on-gles-qt-without-override/README.md).

## Command (as run on the Comet)
```
~/bin/validate-qt
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-run-1` | GPU_HANG | 0 | 302.2 | 5 |  | no |
| `attempt-02-run-2` | GPU_HANG | 0 | 303.4 | 4 | 79.0 | no |
| `attempt-03-run-3-with-driver-debug-logging` | GPU_HANG | 0 | 310.3 | 5 | 80.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Kernel GPU events (etnaviv)
Lines from the kernel journal window of each attempt, time of day only.

**attempt-01-run-1**
```
15:11:57.421359 etnaviv-gpu 38000000.gpu: recover hung GPU!
15:11:57.424636 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/principledmaterial/bin/principledmaterial)
15:13:04.112730 etnaviv-gpu 38000000.gpu: recover hung GPU!
15:13:08.663540 etnaviv-gpu 38000000.gpu: recover hung GPU!
15:13:08.667659 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/reflectionprobes/bin/reflectionprobes)
15:13:21.295633 etnaviv-gpu 38000000.gpu: recover hung GPU!
15:13:21.301520 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/cascadedshadowmaps/bin/cascadedshadowmaps)
15:13:34.015732 etnaviv-gpu 38000000.gpu: recover hung GPU!
15:13:34.019573 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/sceneeffects/bin/sceneeffects)
```

**attempt-02-run-2**
```
10:08:38.396956 etnaviv-gpu 38000000.gpu: recover hung GPU!
10:08:38.400811 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/principledmaterial/bin/principledmaterial)
10:09:44.765481 etnaviv-gpu 38000000.gpu: recover hung GPU!
10:09:49.828254 etnaviv-gpu 38000000.gpu: recover hung GPU!
10:09:49.831652 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/reflectionprobes/bin/reflectionprobes)
10:10:14.667575 etnaviv-gpu 38000000.gpu: recover hung GPU!
10:10:14.672223 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/sceneeffects/bin/sceneeffects)
```

**attempt-03-run-3-with-driver-debug-logging**
```
14:31:06.171773 etnaviv-gpu 38000000.gpu: recover hung GPU!
14:31:06.175321 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/principledmaterial/bin/principledmaterial)
14:32:12.819419 etnaviv-gpu 38000000.gpu: recover hung GPU!
14:32:12.824426 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/custommaterial/bin/custommaterial)
14:32:17.891625 etnaviv-gpu 38000000.gpu: recover hung GPU!
14:32:17.895836 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/reflectionprobes/bin/reflectionprobes)
14:32:30.059390 etnaviv-gpu 38000000.gpu: recover hung GPU!
14:32:30.062691 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/cascadedshadowmaps/bin/cascadedshadowmaps)
14:32:43.235508 etnaviv-gpu 38000000.gpu: recover hung GPU!
14:32:43.239267 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/usr/lib64/qt6/examples/quick3d/sceneeffects/bin/sceneeffects)
```

## Key lines from the logs

**attempt-01-run-1**
```
| hellocube | WARN | QEGLPlatformContext: Failed to create context: 3009; QQuickItem: Cannot set FocusScope once item has children and is in a window. |
| helloqtquick3d | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| intro | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| lights | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| principledmaterial | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| instancing | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| particles3d | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| picking | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| antialiasing | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| custommaterial | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| reflectionprobes | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| cascadedshadowmaps | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| sceneeffects | PASS |  |
PASS = ran 12 s without crash or error text in the log. Screenshots (`ex-*.png`) and raw logs are in `/home/mecha/benchmarks/reports/qt-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261102-150839/`.
```

**attempt-02-run-2**
```
| hellocube | WARN | QEGLPlatformContext: Failed to create context: 3009; QQuickItem: Cannot set FocusScope once item has children and is in a window. |
| helloqtquick3d | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| intro | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| lights | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| principledmaterial | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| instancing | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| particles3d | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| picking | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| antialiasing | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| custommaterial | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| reflectionprobes | WARN | QEGLPlatformContext: Failed to create context: 3009 |
| cascadedshadowmaps | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| sceneeffects | PASS |  |
PASS = ran 12 s without crash or error text in the log. Screenshots (`ex-*.png`) and raw logs are in `/home/mecha/benchmarks/reports/qt-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-100519/`.
```

**attempt-03-run-3-with-driver-debug-logging**
```
| hellocube | WARN | QEGLPlatformContext: Failed to create context: 3009; QQuickItem: Cannot set FocusScope once item has children and is in a window. |
| helloqtquick3d | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| intro | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| lights | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glTexParameter(pname=GL_TEXTURE_MIN_FILTER) |
| principledmaterial | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glTexParameter(pname=GL_TEXTURE_MIN_FILTER) |
| instancing | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| particles3d | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| picking | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| antialiasing | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| custommaterial | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| reflectionprobes | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| cascadedshadowmaps | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| sceneeffects | WARN | Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
PASS = ran 12 s without crash or error text in the log. Screenshots (`ex-*.png`) and raw logs are in `/home/mecha/benchmarks/reports/qt-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-142740/`.
```

