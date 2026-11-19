# Qt apps on the Comet: GPU use and frame rate

```
date=2026-11-19T17:40:48+05:30
kernel=7.2.4-0.202610231332.fc44.aarch64
mesa=mesa-dri-drivers-27.0.0~devel-0.1.20261119git6f23942285e.fc44.aarch64
qt6=qt6-qtbase-6.11.2-3.fc45.aarch64
qtdeclarative=qt6-qtdeclarative-6.11.2-3.fc45.aarch64
qtquick3d=qt6-qtquick3d-6.11.2-1.fc45.aarch64
GL_RENDERER=Vivante GC7000 rev 6204
GL_VERSION=OpenGL ES 3.0 Mesa 27.0.0-devel
extra_env=
output=DSI-1 {'width': 1080, 'height': 1240, 'refresh': 60000, 'picture_aspect_ratio': 'none'} 2.0
```

| app | on GPU | busy fps (median) | % busy frames <= 22 ms | % > 25 ms | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | GL errors | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dolphin | NO (CPU raster) | 64.1 | 90.8 | 8.1 | 29.5 | 19.5 | 57.0/198.0 | 179.0 | 0.0 | yes (idle 99%) | 0 | 0 |  |
| falkon | YES | 40.6 | 46.6 | 49.4 | 59.0 | 22.6 | 43.0/100.0 | 589.0 | 184.0 | yes (idle 99%) | 0 | 0 |  |
| kate | NO (CPU raster) | 18.8 | 26.3 | 68.4 | 74.5 | 3.8 | 7.0/18.0 | 161.0 | 0.0 | yes (idle 99%) | 0 | 0 |  |
| kcalc | NO (CPU raster) | 56.0 | 62.7 | 34.0 | 69.0 | 17.5 | 7.0/19.0 | 82.0 | 0.0 | yes (idle 99%) | 0 | 0 |  |
| kirigami-gallery | YES | - | - | - | - | 1.2 | 2.0/12.0 | 186.0 | 124.0 | yes (idle 99%) | 0 | 0 |  |
| konsole | NO (CPU raster) | 17.7 | 18.8 | 80.6 | 80.3 | 8.3 | 27.0/112.0 | 113.0 | 0.0 | yes (idle 92%) | 0 | 0 |  |
| okular | NO (CPU raster) | 40.8 | 31.1 | 46.2 | 79.5 | 22.5 | 81.0/158.0 | 415.0 | 0.0 | yes (idle 99%) | 0 | 0 |  |
| qml-particles | YES | 15.1 | 0.0 | 100.0 | 67.6 | 17.6 | 22.0/40.0 | 141.0 | 39.0 | yes (idle 99%) | 0 | 0 |  |
| qml-pathanimation | YES | 50.6 | 99.4 | 0.6 | 20.8 | 35.7 | 18.0/31.0 | 135.0 | 55.0 | yes (idle 99%) | 0 | 0 |  |
| qml-sprite | YES | - | - | - | - | 0.0 | 1.0/19.0 | 148.0 | 71.0 | yes (idle 99%) | 0 | 0 |  |
| qml-tvtennis | YES | 50.7 | 99.8 | 0.0 | 20.7 | 50.7 | 23.0/26.0 | 119.0 | 37.0 | yes (idle 98%) | 0 | 0 |  |
| qt-canvas | n/a (no frames drawn) | - | - | - | - | - | -/- | - | - | yes (idle 99%) | 0 | 0 | no wl_surface.commit logged (no window or app exited) |
| qt-gallery | YES | 50.7 | 91.7 | 4.9 | 24.7 | 7.4 | 4.0/28.0 | 146.0 | 45.0 | yes (idle 99%) | 0 | 0 |  |
| qt-shadereffects | YES | 50.6 | 99.9 | 0.0 | 20.7 | 50.6 | 32.0/39.0 | 149.0 | 54.0 | yes (idle 99%) | 0 | 0 |  |
| qt3d-hellocube | n/a (no frames drawn) | - | - | - | - | - | -/- | - | - | yes (idle 99%) | 0 | 0 |  |
| qt3d-intro | n/a (no frames drawn) | - | - | - | - | - | -/- | - | - | yes (idle 99%) | 0 | 0 |  |
| qterminal | NO (CPU raster) | 19.2 | 36.8 | 62.3 | 57.0 | 5.5 | 14.0/116.0 | 82.0 | 0.0 | yes (idle 99%) | 0 | 0 |  |

Definitions (also written into summary.md):
  commit           one `wl_surface#N.commit()` line of WAYLAND_DEBUG=client output (one presented frame of that surface).
  active phase     the scripted-interaction window (active_start..active_end in phases.txt).
  surface          the Wayland surface with the most commits in the active phase (the app's main drawing surface).
  active fps       commits on that surface / active phase seconds (average over the whole window, idle gaps included).
  busy fps         1000 / median interval between consecutive commits whose gap is < 100 ms, i.e. while the app is
                   continuously redrawing. The panel's vblank rate is the ceiling (see the GTK4 apps run).
  % <= 22 ms       share of busy intervals <= 22 ms (the panel's ~19.7 ms vblank period plus jitter).
  % > 25 ms        share of busy intervals above 25 ms (frames slower than 40 fps).
  GPU              the app tree held a DRM client of /dev/dri/renderD128 (etnaviv) at the end of the active phase and
                   mapped Mesa libgallium. Qt Widgets apps paint on the CPU into shared memory by design (no GPU client).
