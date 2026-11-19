# Qt 6.11.2 Quick 3D examples hang the GPU on a Qt built for OpenGL ES (no GL override)

**Verdict:** GPU HANG

## What was run
The Qt Quick 3D example apps that ship with Qt (`hellocube`, `intro`, `lights`, `principledmaterial`, `reflectionprobes`, `cascadedshadowmaps`, `sceneeffects`) were run one after another with the test script `scripts/qt_apps_fps.sh`. The script starts each app, drives it for about 25 seconds and records the logs.

Qt is version 6.11.2 built for OpenGL ES (installed in `/opt/qt6-gles`, not a Fedora package), so the apps get a real `OpenGL ES 3.0` context and no `MESA_GL_VERSION_OVERRIDE` is needed. Mesa is 27.0.0~devel git `6f23942285e` and the kernel is 7.2.4. The exact versions are in `artifacts/run-info.txt`.

## Result
Four of the seven examples hung the GPU: `cascadedshadowmaps`, `principledmaterial`, `reflectionprobes` and `sceneeffects`. Each one logged a single `etnaviv-gpu 38000000.gpu: recover hung GPU!` in the kernel log, and the offending task was the app's own render thread (`QSGRenderThread`). The board stays up.

The other three ran without a hang: `hellocube` at 50.4 fps, `intro` at 25.9 fps and `lights` at 38.5 fps. A `-` for fps in the raw summary means the view was static, so no frame rate could be measured.

No override is used in this run. The same examples were also run with Fedora's Qt and the GL 3.3 override: [`qt-quick3d-gpu-hang-with-gl33-override`](../qt-quick3d-gpu-hang-with-gl33-override/README.md). The app logs show no shader or GL error before the reset.

## Command (as run on the Comet)
```
cd ~/gtk4-apps   # scripts/qt_apps_fps.sh, qt_apps_analyze.py and gtk4_apps_metrics.py copied here
QE=$HOME/qt6-gles-ex EXTRA_ENV="QT_QPA_PLATFORM=wayland QT_PLUGIN_PATH=/opt/qt6-gles/plugins QML_IMPORT_PATH=/opt/qt6-gles/qml" ./qt_apps_fps.sh ~/qt-final-gles-3d qt3d-hellocube qt3d-intro qt3d-lights qt3d-principledmaterial qt3d-reflectionprobes qt3d-cascadedshadowmaps qt3d-sceneeffects
```

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gles-qt-6.11.2-mesa-main-6f23942285e` | GPU_HANG | 0 | 331 | 4 |  | no |

The attempt folder holds `cmd.txt`, `stdout.txt` (the script's summary), `kernel.txt` (kernel lines per app), `kernel-gpu-events.txt`, `result.json` and `artifacts/`. In `artifacts/` there are the summary files, `run-info.txt`, and for each app its `kernel.txt`, `phases.txt` and a screenshot taken at the end (`active.png`). The full per-app logs of this run (Wayland commit log, CPU and memory samples) are in [`qt-apps-main-6f23942285e-2026-11-19/gles-qt-quick3d/`](../../../qt-apps-main-6f23942285e-2026-11-19/gles-qt-quick3d/).

## Kernel GPU events (etnaviv)
Kernel lines for each app, with the time of day.

**attempt-01-gles-qt-6.11.2-mesa-main-6f23942285e**
```
qt3d-cascadedshadowmaps    18:00:31 etnaviv-gpu 38000000.gpu: recover hung GPU!
qt3d-cascadedshadowmaps    18:00:31 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/home/mecha/qt6-gles-ex/quick3d/cascadedshadowmaps/bin/cascadedshadowmaps)
qt3d-principledmaterial    17:58:52 etnaviv-gpu 38000000.gpu: recover hung GPU!
qt3d-principledmaterial    17:58:52 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/home/mecha/qt6-gles-ex/quick3d/principledmaterial/bin/principledmaterial)
qt3d-reflectionprobes      17:59:41 etnaviv-gpu 38000000.gpu: recover hung GPU!
qt3d-reflectionprobes      17:59:41 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/home/mecha/qt6-gles-ex/quick3d/reflectionprobes/bin/reflectionprobes)
qt3d-sceneeffects          18:01:20 etnaviv-gpu 38000000.gpu: recover hung GPU!
qt3d-sceneeffects          18:01:20 etnaviv-gpu 38000000.gpu: offending task: QSGRenderThread (/home/mecha/qt6-gles-ex/quick3d/sceneeffects/bin/sceneeffects)
```

## Key lines from the logs

**attempt-01-gles-qt-6.11.2-mesa-main-6f23942285e**
```
qt3d-hellocube: commits_logged=1592
qt3d-intro: commits_logged=1131
qt3d-lights: commits_logged=138
qt3d-principledmaterial: commits_logged=12
qt3d-reflectionprobes: commits_logged=225
qt3d-cascadedshadowmaps: commits_logged=11
qt3d-sceneeffects: commits_logged=10
```
