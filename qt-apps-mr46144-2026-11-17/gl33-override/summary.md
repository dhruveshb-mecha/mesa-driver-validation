# Qt apps on the Comet: GPU use and frame rate

```
date=2026-11-17T12:04:38+05:30
kernel=7.2.4-0.202610231332.fc44.aarch64
mesa=mesa-dri-drivers-27.0.0~devel-0.1.20261113git8838d84.mr46144.fc44.aarch64
qt6=qt6-qtbase-6.11.2-3.fc44.aarch64
qtdeclarative=qt6-qtdeclarative-6.11.2-3.fc44.aarch64
qtquick3d=qt6-qtquick3d-6.11.2-1.fc44.aarch64
GL_RENDERER=Vivante GC7000 rev 6204
GL_VERSION=OpenGL ES 3.0 Mesa 27.0.0-devel
extra_env=MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330
output=DSI-1 {'width': 1080, 'height': 1240, 'refresh': 60000, 'picture_aspect_ratio': 'none'} 2.0
```

| app | on GPU | busy fps (median) | % busy frames <= 22 ms | % > 25 ms | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | GL errors | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qt3d-cascadedshadowmaps | YES | - | - | - | - | 0.0 | 1.0/17.0 | 200.0 | 496.0 | yes (idle 99%) | 0 | 0 | no hang logged but only 11 frames drawn; view static |
| qt3d-hellocube | YES | 50.6 | 97.2 | 2.8 | 20.7 | 49.3 | 28.0/36.0 | 178.0 | 72.0 | yes (idle 99%) | 0 | 0 |  |
| qt3d-intro | YES | 25.8 | 45.5 | 54.3 | 41.8 | 32.8 | 18.0/33.0 | 157.0 | 297.0 | yes (idle 99%) | 0 | 0 |  |
| qt3d-lights | YES | 45.6 | 50.0 | 38.5 | 31.3 | 4.2 | 5.0/19.0 | 214.0 | 280.0 | yes (idle 99%) | 0 | 0 | UI nearly idle; thin fps sample |
| qt3d-principledmaterial | YES | - | - | - | - | 0.0 | 0.0/0.0 | 282.0 | 248.0 | yes (idle 99%) | 1 | 0 | GPU hang: recover hung GPU! (QSGRenderThread); 3D view stays black |
| qt3d-reflectionprobes | YES | - | - | - | - | 6.1 | 30.0/36.0 | 224.0 | 131.0 | yes (idle 99%) | 1 | 0 | GPU hang: recover hung GPU! (QSGRenderThread) |
| qt3d-sceneeffects | YES | - | - | - | - | 0.0 | 0.0/0.0 | 228.0 | 213.0 | yes (idle 99%) | 1 | 0 | GPU hang: recover hung GPU! (QSGRenderThread); 3D view black |

Definitions:

| Term | Definition |
|---|---|
| `commit` | One `wl_surface#N.commit()` line of WAYLAND_DEBUG=client output (one presented frame of that surface). |
| `active phase` | The scripted-interaction window (`active_start..active_end` in `phases.txt`). |
| `surface` | The Wayland surface with the most commits in the active phase (the app's main drawing surface). |
| `active fps` | Commits on that surface / active phase seconds (average over the whole window, idle gaps included). |
| `busy fps` | 1000 / median interval between consecutive commits whose gap is < 100 ms, i.e. while the app is continuously redrawing. The panel's vblank rate is the ceiling (see the GTK4 apps run). |
| `% <= 22 ms` | Share of busy intervals <= 22 ms (the panel's ~19.7 ms vblank period plus jitter). |
| `% > 25 ms` | Share of busy intervals above 25 ms (frames slower than 40 fps). |
| `GPU` | The app tree held a DRM client of `/dev/dri/renderD128` (etnaviv) at the end of the active phase and mapped Mesa libgallium. Qt Widgets apps paint on the CPU into shared memory by design (no GPU client). |
