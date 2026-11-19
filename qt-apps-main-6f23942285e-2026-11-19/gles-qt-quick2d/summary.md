# Qt apps on the Comet: GPU use and frame rate

```
date=2026-11-19T18:02:03+05:30
kernel=7.2.4-0.202610231332.fc44.aarch64
mesa=mesa-dri-drivers-27.0.0~devel-0.1.20261119git6f23942285e.fc44.aarch64
qt6=qt6-qtbase-6.11.2-3.fc45.aarch64
qtdeclarative=qt6-qtdeclarative-6.11.2-3.fc45.aarch64
qtquick3d=qt6-qtquick3d-6.11.2-1.fc45.aarch64
GL_RENDERER=Vivante GC7000 rev 6204
GL_VERSION=OpenGL ES 3.0 Mesa 27.0.0-devel
extra_env=QT_QPA_PLATFORM=wayland QT_PLUGIN_PATH=/opt/qt6-gles/plugins QML_IMPORT_PATH=/opt/qt6-gles/qml
output=DSI-1 {'width': 1080, 'height': 1240, 'refresh': 60000, 'picture_aspect_ratio': 'none'} 2.0
```

| app | on GPU | busy fps (median) | % busy frames <= 22 ms | % > 25 ms | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | GL errors | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qml-particles | YES | 14.9 | 0.0 | 100.0 | 80.4 | 13.9 | 18.0/38.0 | 122.0 | 36.0 | yes (idle 99%) | 0 | 0 |  |
| qml-pathanimation | YES | 50.6 | 99.7 | 0.1 | 20.7 | 35.6 | 17.0/27.0 | 120.0 | 63.0 | yes (idle 99%) | 0 | 0 |  |
| qml-sprite | YES | - | - | - | - | 0.0 | 1.0/23.0 | 126.0 | 47.0 | yes (idle 99%) | 0 | 0 |  |
| qml-tvtennis | YES | 50.6 | 99.9 | 0.1 | 20.7 | 50.6 | 22.0/24.0 | 103.0 | 35.0 | yes (idle 99%) | 0 | 0 |  |

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
