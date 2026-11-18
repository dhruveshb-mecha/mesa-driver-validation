# Qt apps on Mesa 27 `mr46144` (etnaviv)

Qt 6 apps run one at a time on the Mecha Comet with a scripted interaction, to see whether they draw on the GPU and what frame rate they reach. The Quick 3D examples are also run with a GL 3.3 override and on a Qt built for GLES, because Fedora's Qt 6 has no GLES backend.

| | |
|---|---|
| Date | 2026-11-17 |
| Board | Mecha Comet, i.MX8M Plus, Vivante GC7000UL rev 6204, 3.9 GB RAM, 1080x1240 DSI panel (output scale 2), sway/Wayland |
| Software | Fedora 44 aarch64, kernel 7.2.4, Mesa 27.0.0~devel git 8838d84 (`mr46144`), Qt 6.11.2 (Fedora build, `QT_QPA_PLATFORM=wayland`) |
| GL | `Vivante GC7000 rev 6204`, `OpenGL ES 3.0 Mesa 27.0.0-devel` |
| Details | [`default/run-info.txt`](default/run-info.txt) |

## Summary

Qt Quick apps draw on the GPU. Their scene graph goes through EGL on `/dev/dri/renderD128` (etnaviv) with `libgallium` mapped. The self-running animations (tvtennis, pathanimation, shadereffects) reach the panel's real refresh of about 51 fps. Image particles run at 25.1 fps, with 99.6% of busy frames over 25 ms.

Qt Widgets and KDE apps (KCalc, Konsole, qterminal, Kate, Okular, Dolphin) paint on the CPU into shared memory and open no etnaviv client. Their frame rate is CPU raster speed, so it is not limited by the display and can read above 51 fps.

Falkon (QtWebEngine) has etnaviv clients in its GPU process. It scrolled a text page at 47 fps, with 43% of busy frames over 25 ms. Its RHI log lists a Vulkan llvmpipe device, but that is only enumeration.

Quick 3D does not start on Fedora's Qt without `MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330`: `hellocube` and `intro` abort at start with a core dump. With the override `hellocube` runs at 50.6 fps and `intro` at 25.8 fps.

Three Quick 3D examples hang the GPU with the override: `principledmaterial`, `reflectionprobes` and `sceneeffects` each logged one `etnaviv-gpu: recover hung GPU!` (offending task `QSGRenderThread`), and `cascadedshadowmaps` drew only 11 frames. The same examples hung on Mesa `7b4b394` (see [`cases/1-gpu-hangs/qt-quick3d-gpu-hang-with-gl33-override/`](../cases/1-gpu-hangs/qt-quick3d-gpu-hang-with-gl33-override/README.md)).

Because the override is unsupported, I repeated the test on a Qt 6.11.2 built with `-opengl es2` (a local build installed under `/opt/qt6-gles`, not a Fedora package). It runs Quick 3D on `OpenGL ES 3.0 Mesa 27.0.0-devel` with no override. In two runs of the seven examples, `principledmaterial`, `reflectionprobes` and `sceneeffects` hung the GPU both times. `cascadedshadowmaps` drew 11 frames both times and logged a hang in run 1 only. `hellocube`, `intro` and `lights` never hung. Frame rates match the Fedora Qt runs (hellocube 50.7 fps, intro 26 fps).

Kirigami Gallery only starts with `QT_QUICK_CONTROLS_STYLE=Basic`; with the default KDE style it exits with code 255 and prints nothing. The Qt Quick canvas example did not start (`module "shared" is not installed`).

## Results: default configuration

| App | What was driven | On GPU | Busy fps (median) | Busy frames > 25 ms | App CPU mean % | RSS peak MB | GPU hangs | Notes |
|---|---|---|---|---|---|---|---|---|
| dolphin | Dolphin, icon view, paging + zoom | NO (CPU raster) | 62.5 | 8.6% | 46.0 | 198.0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| falkon | Falkon (QtWebEngine), 800-row text page, scrolling | YES | 47.3 | 43.3% | 47.0 | 625.0 | 0 | QtWebEngine; static text page; GPU process holds etnaviv clients (Vulkan probe lists llvmpipe, enumeration only) |
| kate | Kate, 400000-line file, paging | NO (CPU raster) | 16.8 | 76.2% | 7.0 | 159.0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| kcalc | KCalc, typing expressions | NO (CPU raster) | 56.7 | 33.8% | 8.0 | 80.0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| kirigami-gallery | Kirigami Gallery (Basic style), Tab/arrows/paging | YES | - | - | 2.0 | 187.0 | 0 | needs QT_QUICK_CONTROLS_STYLE=Basic (default KDE style exits 255, no message); UI idle between key presses |
| konsole | Konsole, `seq 1 300000`, `ls -R` | NO (CPU raster) | 17.4 | 74.5% | 22.0 | 112.0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| okular | Okular, 40-page PDF, scroll + zoom | NO (CPU raster) | 42.1 | 42.1% | 82.0 | 326.0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| qml-particles | Qt Quick example: image particles | YES | 25.1 | 99.6% | 30.0 | 150.0 | 0 |  |
| qml-pathanimation | Qt Quick example: path animation | YES | 50.7 | 0.2% | 18.0 | 144.0 | 0 |  |
| qml-sprite | Qt Quick example: animated sprite | YES | - | - | 1.0 | 155.0 | 0 | static scene between key presses; fps not meaningful |
| qml-tvtennis | Qt Quick example: self-running animation (tvtennis) | YES | 50.7 | 0.3% | 23.0 | 117.0 | 0 |  |
| qt-canvas | Qt Quick canvas example | n/a (no frames drawn) | - | - | - | - | 0 | QML error: module "shared" is not installed (examples import path); no window |
| qt-gallery | Qt Quick Controls gallery, Tab/arrows/paging | YES | - | - | 1.0 | 145.0 | 0 | UI idle between key presses; fps not meaningful |
| qt-shadereffects | Qt Quick shader effects examples | YES | 50.6 | 0.3% | 33.0 | 151.0 | 0 |  |
| qt3d-hellocube | Quick 3D hellocube | n/a (no frames drawn) | - | - | - | - | 0 | aborts at start without the GL 3.3 override (core dump); see gl33-override/ |
| qt3d-intro | Quick 3D intro | n/a (no frames drawn) | - | - | - | - | 0 | aborts at start without the GL 3.3 override (core dump); see gl33-override/ |
| qterminal | qterminal, `seq 1 300000`, `ls -R` | NO (CPU raster) | 18.9 | 62.8% | 14.0 | 80.0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |

## Results: Quick 3D with `MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330`

| App | What was driven | On GPU | Busy fps (median) | Busy frames > 25 ms | App CPU mean % | RSS peak MB | GPU hangs | Notes |
|---|---|---|---|---|---|---|---|---|
| qt3d-cascadedshadowmaps | Quick 3D cascadedshadowmaps | YES | - | - | 1.0 | 200.0 | 0 | no hang logged but only 11 frames drawn; view static |
| qt3d-hellocube | Quick 3D hellocube | YES | 50.6 | 2.8% | 28.0 | 178.0 | 0 |  |
| qt3d-intro | Quick 3D intro | YES | 25.8 | 54.3% | 18.0 | 157.0 | 0 |  |
| qt3d-lights | Quick 3D lights | YES | 45.6 | 38.5% | 5.0 | 214.0 | 0 | UI nearly idle; thin fps sample |
| qt3d-principledmaterial | Quick 3D principledmaterial | YES | - | - | 0.0 | 282.0 | 1 | GPU hang: recover hung GPU! (QSGRenderThread); 3D view stays black |
| qt3d-reflectionprobes | Quick 3D reflectionprobes | YES | - | - | 30.0 | 224.0 | 1 | GPU hang: recover hung GPU! (QSGRenderThread) |
| qt3d-sceneeffects | Quick 3D sceneeffects | YES | - | - | 0.0 | 228.0 | 1 | GPU hang: recover hung GPU! (QSGRenderThread); 3D view black |

About the columns. "On GPU" means the app tree held a DRM client of `/dev/dri/renderD128` at the end of the scripted phase and mapped Mesa `libgallium`; "n/a" means no frame was drawn. "Busy fps" is 1000 divided by the median interval between consecutive `wl_surface.commit` events on the app's busiest surface, over intervals shorter than 100 ms (continuous redraw). The panel's real refresh, about 51 Hz, is the ceiling for apps that present on the GPU. "Busy frames > 25 ms" is the share of those intervals above 25 ms, which is slower than 40 fps.

Apps whose UI sits idle between key presses (Gallery, Kirigami Gallery, sprite, lights) have no meaningful frame rate; they are listed to show they draw on the GPU. Each app was run once in this table. Falkon loaded a static page, which is not a GPU stress. The per-app `summary.md`, `summary.csv` and `summary.json` hold the full metric set (p95 frame time, active-window fps, GPU memory, isolation checks).

## Results: Quick 3D on a GLES Qt (`-opengl es2`), no override

Qt 6.11.2 built from source with `-DINPUT_opengl=es2` (qtbase, qtshadertools, qtsvg, qtdeclarative, qtwayland, qtquick3d), installed to `/opt/qt6-gles` next to the Fedora Qt. Run with `QT_QPA_PLATFORM=wayland QT_PLUGIN_PATH=/opt/qt6-gles/plugins QML_IMPORT_PATH=/opt/qt6-gles/qml`, no `MESA_GL_VERSION_OVERRIDE`. Raw output: [`gles-qt-no-override-run1/`](gles-qt-no-override-run1/) and [`gles-qt-no-override-run2/`](gles-qt-no-override-run2/) (same command, repeated). Hang = `etnaviv-gpu 38000000.gpu: recover hung GPU!` in `kernel.txt`, offending task `QSGRenderThread`.

| App | Run 1: busy fps / frames | Run 1: GPU hang | Run 2: busy fps / frames | Run 2: GPU hang |
|---|---|---|---|---|
| qt3d-hellocube | 50.7 / 1700+ | no | 50.7 / 1762 | no |
| qt3d-intro | 26.0 / about 1100 | no | 25.9 / 1168 | no |
| qt3d-lights | 43.1 / 140 | no | 43.8 / 147 | no |
| qt3d-principledmaterial | - / 11 | yes | 50.6 / 798 | yes |
| qt3d-reflectionprobes | - / about 200 | yes | - / 206 | yes |
| qt3d-cascadedshadowmaps | - / 11 | yes | - / 11 | no (still only 11 frames) |
| qt3d-sceneeffects | - / 10 | yes | 51.1 / 305 | yes |

Busy fps is the median over the frames drawn before any hang, so it describes only the part where the app ran. `lights` averages 4 to 5 fps over the scripted window (idle between key presses). Two runs only; where a hang occurs varies between runs. Per-run `summary.md` / `summary.csv` / `summary.json` hold the full metric set.

## Method

[`scripts/qt_apps_fps.sh`](../scripts/qt_apps_fps.sh) runs on the board in the sway session. For each app it closes every other window and kills stale processes, waits for the CPU to idle, launches the app with `WAYLAND_DEBUG=client`, drives it with `wtype`, and records the raw log, a 1 Hz CPU/RSS/DRM sampler ([`scripts/gtk4_apps_metrics.py`](../scripts/gtk4_apps_metrics.py)), the libraries the app mapped, kernel log lines, and a screenshot. [`scripts/qt_apps_analyze.py`](../scripts/qt_apps_analyze.py) turns the raw logs into the summaries without modifying them.

```
./qt_apps_fps.sh OUTDIR [app ...]
EXTRA_ENV="MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330" ./qt_apps_fps.sh OUTDIR qt3d-hellocube qt3d-intro
python3 qt_apps_analyze.py OUTDIR
```

## Layout

```
README.md
default/         one folder per app: raw.log (Wayland protocol trace + app output; files over 1 MB are gzipped), metrics.csv, phases.txt, isolation.txt,
                 gpu-libs.txt, kernel.txt, drm-fdinfo.txt, active.png, notes.txt; summary.md/csv/json, run-info.txt
gl33-override/   same, for the Quick 3D examples run with the GL 3.3 override
gles-qt-no-override-run1/, -run2/   same, for the Quick 3D examples on the GLES Qt build (no override)
```
