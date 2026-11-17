# GTK4 apps on the Comet: GPU use and frame rate

```
date=2026-11-17T06:02:17+05:30
kernel=7.2.4-0.202610231332.fc44.aarch64
mesa=mesa-dri-drivers-27.0.0~devel-0.1.20261113git8838d84.mr46144.fc44.aarch64
gtk4=gtk4-4.22.5-2.fc44.aarch64
libadwaita=libadwaita-1.9.4-1.fc44.aarch64
GL_RENDERER=Vivante GC7000 rev 6204
GL_VERSION=OpenGL ES 3.0 Mesa 27.0.0-devel
output=DSI-1 {'width': 1080, 'height': 1240, 'refresh': 60000, 'picture_aspect_ratio': 'none'} 2.0
pkg_nautilus=nautilus-50.4-2.fc44.aarch64
pkg_papers=papers-49.8-1.fc44.aarch64
pkg_maps=gnome-maps-50.5-1.fc44.aarch64
pkg_epiphany=epiphany-50.6-6.fc44.aarch64
pkg_software=gnome-software-50.4-1.fc44.aarch64
pkg_weather=gnome-weather-50.0-1.fc44.noarch
pkg_system-monitor=gnome-system-monitor-50.0-1.fc44.aarch64
pkg_calendar=gnome-calendar-50.0-1.fc44.aarch64
pkg_console=gnome-console-50.0-1.fc44.aarch64
pkg_ptyxis=ptyxis-50.1-2.fc44.aarch64
pkg_showtime=showtime-50.0-1.fc44.noarch
pkg_fractal=fractal-14.3-1.fc44.aarch64
pkg_snapshot=snapshot-50.0-1.fc44.aarch64
```

| app | on GPU | renderer | busy fps (median) | % frames at 60 Hz pace | p95 frame ms | active-window fps | app CPU mean/max % | RSS peak MB | GPU mem peak MiB | isolated | GPU hangs | app killed | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calendar | YES | GskGLRenderer | 50.9 | 20.6 | 24.4 | 2.7 | 8.0/18.0 | 241.0 | 24.0 | yes (idle 98%) | 0 | no |  |
| console | YES | GskGLRenderer | 51.5 | 35.4 | 46.6 | 11.4 | 18.0/78.0 | 204.0 | 25.0 | yes (idle 98%) | 0 | no |  |
| epiphany | YES | GskGLRenderer | 49.5 | 12.2 | 61.1 | 19.4 | 84.0/385.0 | 1330.0 | 99.0 | yes (idle 99%) | 0 | no | 800-row plain text page served from a local http server, fresh --profile. Renders and scrolls; RSS peak about 1.3 GB. Local file:// pages did not load in this setup. |
| epiphany--animated-page-800rows-OOM | YES | GskGLRenderer | 50.5 | 4.8 | 27.2 | 25.8 | 177.0/377.0 | 2468.0 | 95.0 | yes (idle 99%) | 0 | yes (OOM) | 800-row page with a CSS animation and a canvas requestAnimationFrame loop. Process-tree RSS grows from about 0.6 GB to 2.5 GB when scrolling starts and the kernel OOM killer kills Epiphany (a 4000-row version behaved the same). Which animation is responsible was not isolated. fps are not meaningful because the process died. |
| fractal | YES | GskGLRenderer | 50.3 | 11.3 | 56.7 | 13.2 | 15.0/36.0 | 244.0 | 36.0 | yes (idle 99%) | 0 | no | No Matrix account; the scripted Tab presses walk into the login flow (Homeserver Discovery dialog). Measures Fractal's login UI. |
| maps | YES | GskGLRenderer | 50.0 | 16.1 | 70.5 | 3.2 | 34.0/163.0 | 645.0 | 90.0 | yes (idle 99%) | 0 | no |  |
| nautilus | YES | GskGLRenderer | 49.5 | 8.9 | 68.3 | 16.2 | 24.0/38.0 | 326.0 | 148.0 | yes (idle 98%) | 0 | no |  |
| papers | YES | GskGLRenderer | 24.8 | 5.2 | 65.8 | 16.5 | 20.0/85.0 | 462.0 | 139.0 | yes (idle 98%) | 0 | no |  |
| ptyxis | YES | GskGLRenderer | 50.8 | 20.3 | 30.8 | 14.3 | 11.0/47.0 | 218.0 | 24.0 | yes (idle 99%) | 0 | no |  |
| showtime | YES | GskGLRenderer | 50.8 | 0.0 | 20.1 | 42.6 | 9.0/18.0 | 252.0 | 80.0 | yes (idle 99%) | 0 | no | Video is solid green with GTK's default dmabuf video path while the playback clock advances. The same video renders correctly in showtime--GDK_DISABLE-dmabuf. |
| showtime--GDK_DISABLE-dmabuf | YES | GskGLRenderer | 50.8 | 0.0 | 20.1 | 41.0 | 10.0/36.0 | 248.0 | 133.0 | yes (idle 99%) | 0 | no | Same video with GDK_DISABLE=dmabuf: renders correctly (see active.png). |
| snapshot | YES | GskGLRenderer | 51.0 | 22.2 | 20.6 | 2.0 | 1.0/12.0 | 216.0 | 70.0 | yes (idle 99%) | 0 | no | No camera: static 'No Camera Found' page, nothing animates, so fps are not meaningful. |
| software | YES | GskGLRenderer | - | - | - | 0.0 | 59.0/220.0 | 491.0 | 29.0 | yes (idle 98%) | 0 | no | Static Explore page after a 45 s data refresh. No frames were drawn during the scripted phase, so no fps; the app CPU is background refresh work. |
| system-monitor | YES | GskGLRenderer | 50.8 | 8.6 | 37.7 | 28.3 | 28.0/42.0 | 270.0 | 42.0 | yes (idle 99%) | 0 | no |  |
| weather | YES | GskGLRenderer | 58.8 | 78.3 | 33.5 | 15.9 | 18.0/83.0 | 270.0 | 68.0 | yes (idle 99%) | 0 | no | City set to London; hourly and daily views. |

Definitions (also written into summary.md):
  frame            one line of GDK_DEBUG=frames output ("Gdk-Message: HH:MM:SS.mmm: N: interval=..").
  active phase     the scripted-interaction window (active_start..active_end in phases.txt).
  active fps       frames in the active phase / active phase seconds (average over the whole window, idle gaps included).
  busy fps         1000 / median frame interval over frames whose interval is < 100 ms, i.e. while the app is
                   continuously redrawing (scrolling/animating). This is the number to compare with 60.
  % at 60 Hz pace  share of those busy frames with interval <= 18.0 ms (60 Hz = 16.7 ms).
  GPU              GskGLRenderer in use + /dev/dri/renderD128 (etnaviv) held by the app tree + no software renderer.
