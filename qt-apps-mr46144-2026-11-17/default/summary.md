# Qt apps on the Comet: GPU use and frame rate

```
date=2026-11-17T12:02:26+05:30
kernel=7.2.4-0.202610231332.fc44.aarch64
mesa=mesa-dri-drivers-27.0.0~devel-0.1.20261113git8838d84.mr46144.fc44.aarch64
qt6=qt6-qtbase-6.11.2-3.fc44.aarch64
qtdeclarative=qt6-qtdeclarative-6.11.2-3.fc44.aarch64
qtquick3d=qt6-qtquick3d-6.11.2-1.fc44.aarch64
GL_RENDERER=Vivante GC7000 rev 6204
GL_VERSION=OpenGL ES 3.0 Mesa 27.0.0-devel
extra_env=
output=DSI-1 {'width': 1080, 'height': 1240, 'refresh': 60000, 'picture_aspect_ratio': 'none'} 2.0
```

| app | on GPU | busy fps (median) | % busy frames <= 22 ms | % > 25 ms | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | GL errors | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dolphin | NO (CPU raster) | 62.5 | 89.6 | 8.6 | 31.3 | 19.8 | 46.0/209.0 | 198.0 | 0.0 | yes (idle 99%) | 0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| falkon | YES | 47.3 | 53.2 | 43.3 | 40.9 | 24.0 | 47.0/100.0 | 625.0 | 141.0 | yes (idle 99%) | 0 | 0 | QtWebEngine; static text page; GPU process holds etnaviv clients (Vulkan probe lists llvmpipe, enumeration only) |
| kate | NO (CPU raster) | 16.8 | 19.0 | 76.2 | 70.6 | 3.9 | 7.0/17.0 | 159.0 | 0.0 | yes (idle 99%) | 0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| kcalc | NO (CPU raster) | 56.7 | 60.0 | 33.8 | 69.2 | 17.5 | 8.0/20.0 | 80.0 | 0.0 | yes (idle 99%) | 0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| kirigami-gallery | YES | - | - | - | - | 1.2 | 2.0/13.0 | 187.0 | 124.0 | yes (idle 99%) | 0 | 0 | needs QT_QUICK_CONTROLS_STYLE=Basic (default KDE style exits 255, no message); UI idle between key presses |
| konsole | NO (CPU raster) | 17.4 | 24.1 | 74.5 | 76.7 | 7.0 | 22.0/112.0 | 112.0 | 0.0 | yes (idle 99%) | 0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| okular | NO (CPU raster) | 42.1 | 32.2 | 42.1 | 76.0 | 23.3 | 82.0/155.0 | 326.0 | 0.0 | yes (idle 99%) | 0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |
| qml-particles | YES | 25.1 | 0.4 | 99.6 | 66.9 | 21.7 | 30.0/42.0 | 150.0 | 39.0 | yes (idle 99%) | 0 | 0 |  |
| qml-pathanimation | YES | 50.7 | 99.8 | 0.2 | 20.6 | 35.7 | 18.0/28.0 | 144.0 | 62.0 | yes (idle 99%) | 0 | 0 |  |
| qml-sprite | YES | - | - | - | - | 0.0 | 1.0/20.0 | 155.0 | 47.0 | yes (idle 99%) | 0 | 0 | static scene between key presses; fps not meaningful |
| qml-tvtennis | YES | 50.7 | 99.7 | 0.3 | 20.6 | 50.7 | 23.0/27.0 | 117.0 | 35.0 | yes (idle 99%) | 0 | 0 |  |
| qt-canvas | n/a (no frames drawn) | - | - | - | - | - | -/- | - | - | yes (idle 99%) | 0 | 0 | QML error: module "shared" is not installed (examples import path); no window |
| qt-gallery | YES | - | - | - | - | 0.9 | 1.0/3.0 | 145.0 | 40.0 | yes (idle 99%) | 0 | 0 | UI idle between key presses; fps not meaningful |
| qt-shadereffects | YES | 50.6 | 99.6 | 0.3 | 20.6 | 50.7 | 33.0/38.0 | 151.0 | 54.0 | yes (idle 99%) | 0 | 0 |  |
| qt3d-hellocube | n/a (no frames drawn) | - | - | - | - | - | -/- | - | - | yes (idle 99%) | 0 | 0 | aborts at start without the GL 3.3 override (core dump); see gl33-override/ |
| qt3d-intro | n/a (no frames drawn) | - | - | - | - | - | -/- | - | - | yes (idle 99%) | 0 | 0 | aborts at start without the GL 3.3 override (core dump); see gl33-override/ |
| qterminal | NO (CPU raster) | 18.9 | 33.6 | 62.8 | 58.3 | 5.4 | 14.0/115.0 | 80.0 | 0.0 | yes (idle 99%) | 0 | 0 | Qt Widgets: painted on the CPU into shared memory, no GPU client |

Definitions:

| Term | Definition |
|---|---|
| commit | One `wl_surface#N.commit()` line of WAYLAND_DEBUG=client output (one presented frame of that surface). |
| active phase | The scripted-interaction window (`active_start..active_end` in `phases.txt`). |
| surface | The Wayland surface with the most commits in the active phase (the app's main drawing surface). |
| active fps | Commits on that surface divided by active phase seconds (average over the whole window, idle gaps included). |
| busy fps | `1000 / median interval` between consecutive commits whose gap is `< 100 ms`, i.e. while the app is continuously redrawing. The panel's vblank rate is the ceiling (see the GTK4 apps run). |
| % <= 22 ms | Share of busy intervals <= 22 ms (the panel's ~19.7 ms vblank period plus jitter). |
| % > 25 ms | Share of busy intervals above 25 ms (frames slower than 40 fps). |
| GPU | The app tree held a DRM client of `/dev/dri/renderD128` (etnaviv) at the end of the active phase and mapped Mesa libgallium. Qt Widgets apps paint on the CPU into shared memory by design (no GPU client). |

