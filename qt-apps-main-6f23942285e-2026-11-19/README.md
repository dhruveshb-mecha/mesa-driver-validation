# Qt 6 apps on Mesa 27 git `6f23942285e` (etnaviv)

Qt 6 apps were run one at a time on the Mecha Comet. A script drives each app and records whether it draws on the GPU, what frame rate it reaches and whether the GPU hangs. There are three runs: all the apps from the script's list with the Fedora Qt, and the Quick 3D and Quick 2D examples with the GLES Qt. The GLES Qt is Qt 6.11.2 built for OpenGL ES (installed in `/opt/qt6-gles`, not a Fedora package).

|| | |
|---|---|
| Date | 2026-11-19 |
| Board | Mecha Comet, i.MX8M Plus, Vivante GC7000UL rev 6204, 3.9 GB RAM, 1080x1240 DSI panel (output scale 2), sway/Wayland |
| Software | Fedora 45 packages, kernel 7.2.4, Mesa 27.0.0~devel git `6f23942285e` (main build), Qt 6.11.2 (`QT_QPA_PLATFORM=wayland`) |
| GL | `Vivante GC7000 rev 6204`, `OpenGL ES 3.0 Mesa 27.0.0-devel` |
| Details | [`fedora-qt/run-info.txt`](fedora-qt/run-info.txt), [`gles-qt-quick3d/run-info.txt`](gles-qt-quick3d/run-info.txt) |

## Summary

- **Quick 3D hangs the GPU with the GLES Qt.** Four of the seven examples (`cascadedshadowmaps`, `principledmaterial`, `reflectionprobes` and `sceneeffects`) each logged one `etnaviv-gpu 38000000.gpu: recover hung GPU!`, with the app's render thread (`QSGRenderThread`) as the offending task. The board stays up. `hellocube`, `intro` and `lights` ran without a hang. Case: [`qt-quick3d-gpu-hang-on-gles-qt-without-override`](../cases/1-gpu-hangs/qt-quick3d-gpu-hang-on-gles-qt-without-override/README.md).
- **Quick 2D examples** ran on the GPU without hangs, with both Qt builds.
- **Fedora Qt:** the Qt Widgets and KDE apps (KCalc, Konsole, qterminal, Kate, Okular, Dolphin) are drawn by the CPU and do not open the GPU. Falkon (a web browser) and the Quick apps use the GPU. `hellocube` and `intro` crash at start with a core dump, and `qt-canvas` opens no window because its QML cannot find the module `shared`.
- **Frame rates** count the frames the app sends to the compositor while it is busy. The DSI panel refreshes at about 51 Hz (measured in [`gtk4-apps-mr46144-2026-11-17`](../gtk4-apps-mr46144-2026-11-17/README.md)), and apps that redraw continuously reach about 50 fps.

## Results: Fedora Qt (default list, no override)

| App | What was driven | On GPU | Busy fps (median) | App CPU mean % | RSS peak MB | GPU hangs | GL errors | Notes |
|---|---|---|---|---|---|---|---|---|
| dolphin | Dolphin, icon view, paging + zoom | NO (CPU raster) | 64.1 | 57.0 | 179.0 | 0 | 0 |  |
| falkon | Falkon (QtWebEngine), 800-row text page, scrolling | YES | 40.6 | 43.0 | 589.0 | 0 | 0 |  |
| kate | Kate, 400000-line file, paging | NO (CPU raster) | 18.8 | 7.0 | 161.0 | 0 | 0 |  |
| kcalc | KCalc, typing expressions | NO (CPU raster) | 56.0 | 7.0 | 82.0 | 0 | 0 |  |
| kirigami-gallery | Kirigami Gallery (Basic style), Tab/arrows/paging | YES | - | 2.0 | 186.0 | 0 | 0 |  |
| konsole | Konsole, `seq 1 300000`, `ls -R` | NO (CPU raster) | 17.7 | 27.0 | 113.0 | 0 | 0 |  |
| okular | Okular, 40-page PDF, scroll + zoom | NO (CPU raster) | 40.8 | 81.0 | 415.0 | 0 | 0 |  |
| qml-particles | Qt Quick example: image particles | YES | 15.1 | 22.0 | 141.0 | 0 | 0 |  |
| qml-pathanimation | Qt Quick example: path animation | YES | 50.6 | 18.0 | 135.0 | 0 | 0 |  |
| qml-sprite | Qt Quick example: animated sprite | YES | - | 1.0 | 148.0 | 0 | 0 |  |
| qml-tvtennis | Qt Quick example: self-running animation (tvtennis) | YES | 50.7 | 23.0 | 119.0 | 0 | 0 |  |
| qt-canvas | Qt Quick canvas example | n/a (no frames drawn) | - | - | - | 0 | 0 | QML error: module "shared" is not installed; no window |
| qt-gallery | Qt Quick Controls gallery, Tab/arrows/paging | YES | 50.7 | 4.0 | 146.0 | 0 | 0 |  |
| qt-shadereffects | Qt Quick shader effects examples | YES | 50.6 | 32.0 | 149.0 | 0 | 0 |  |
| qt3d-hellocube | Quick 3D hellocube | n/a (no frames drawn) | - | - | - | 0 | 0 | aborts at start (core dump); no window |
| qt3d-intro | Quick 3D intro | n/a (no frames drawn) | - | - | - | 0 | 0 | aborts at start (core dump); no window |
| qterminal | qterminal, `seq 1 300000`, `ls -R` | NO (CPU raster) | 19.2 | 14.0 | 82.0 | 0 | 0 |  |

## Results: GLES Qt, Quick 3D examples

| App | What was driven | On GPU | Busy fps (median) | App CPU mean % | RSS peak MB | GPU hangs | GL errors | Notes |
|---|---|---|---|---|---|---|---|---|
| qt3d-cascadedshadowmaps | Quick 3D cascadedshadowmaps | YES | - | 1.0 | 164.0 | 1 | 2 |  |
| qt3d-hellocube | Quick 3D hellocube | YES | 50.4 | 24.0 | 144.0 | 0 | 1 |  |
| qt3d-intro | Quick 3D intro | YES | 25.9 | 18.0 | 129.0 | 0 | 2 |  |
| qt3d-lights | Quick 3D lights | YES | 38.5 | 4.0 | 174.0 | 0 | 1 |  |
| qt3d-principledmaterial | Quick 3D principledmaterial | YES | - | 0.0 | 242.0 | 1 | 1 |  |
| qt3d-reflectionprobes | Quick 3D reflectionprobes | YES | 22.1 | 28.0 | 183.0 | 1 | 1 |  |
| qt3d-sceneeffects | Quick 3D sceneeffects | YES | - | 0.0 | 190.0 | 1 | 0 |  |

## Results: GLES Qt, Quick 2D examples

| App | What was driven | On GPU | Busy fps (median) | App CPU mean % | RSS peak MB | GPU hangs | GL errors | Notes |
|---|---|---|---|---|---|---|---|---|
| qml-particles | Qt Quick example: image particles | YES | 14.9 | 18.0 | 122.0 | 0 | 0 |  |
| qml-pathanimation | Qt Quick example: path animation | YES | 50.6 | 17.0 | 120.0 | 0 | 0 |  |
| qml-sprite | Qt Quick example: animated sprite | YES | - | 1.0 | 126.0 | 0 | 0 |  |
| qml-tvtennis | Qt Quick example: self-running animation (tvtennis) | YES | 50.6 | 22.0 | 103.0 | 0 | 0 |  |

"What was driven" is what the script does to each app, the same as in the earlier Qt run ([`qt-apps-mr46144-2026-11-17`](../qt-apps-mr46144-2026-11-17/README.md)). A `-` under busy fps means the view was static or idle, so there is no frame rate to give. The columns are defined at the top of [`scripts/qt_apps_analyze.py`](../scripts/qt_apps_analyze.py). Each app was run once.

## GPU hangs in the kernel log (GLES Qt, Quick 3D)

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

## Reproduce

On the board, with `scripts/qt_apps_fps.sh`, `qt_apps_analyze.py` and `gtk4_apps_metrics.py` in `~/gtk4-apps`:

```
cd ~/gtk4-apps
./qt_apps_fps.sh ~/qt-final-fedora            # all apps of the default list, Fedora Qt
GLES="QT_QPA_PLATFORM=wayland QT_PLUGIN_PATH=/opt/qt6-gles/plugins QML_IMPORT_PATH=/opt/qt6-gles/qml"
QE=$HOME/qt6-gles-ex EXTRA_ENV="$GLES" ./qt_apps_fps.sh ~/qt-final-gles-3d qt3d-hellocube qt3d-intro qt3d-lights qt3d-principledmaterial qt3d-reflectionprobes qt3d-cascadedshadowmaps qt3d-sceneeffects
QB=/opt/qt6-gles/bin EXTRA_ENV="$GLES" ./qt_apps_fps.sh ~/qt-final-gles-2d qml-tvtennis qml-particles qml-pathanimation qml-sprite
python3 qt_apps_analyze.py <run folder>
```

## Layout

```
README.md
fedora-qt/            run with the Fedora Qt: one folder per app, plus summary.md/csv/json, run-info.txt, summary-run.txt
gles-qt-quick3d/      same, Quick 3D examples on the GLES Qt
gles-qt-quick2d/      same, Quick 2D examples on the GLES Qt
    <app>/  raw.log (Wayland commit log, gzipped when over 1 MB)  metrics.csv  phases.txt
            isolation.txt  gpu-libs.txt  drm-fdinfo.txt  kernel.txt  active.png
```
