# GTK4 apps: GPU use and frame rate (Mesa 27 `mr46144`)

Thirteen stock GNOME GTK4 apps run one at a time on the Mecha Comet, with a scripted interaction, to check whether they render on the GPU and what frame rate they reach.

| | |
|---|---|
| Date | 2026-11-17 |
| Board | Mecha Comet, i.MX8M Plus, Vivante GC7000UL rev 6204, 3.9 GB RAM, 1080x1240 DSI panel (output scale 2), sway/Wayland |
| Software | Fedora 44 aarch64, kernel 7.2.4, **Mesa 27.0.0~devel git 8838d84 (`mr46144`)**, GTK 4.22.5, libadwaita 1.9.4 |
| GL | `Vivante GC7000 rev 6204`, `OpenGL ES 3.0 Mesa 27.0.0-devel` |
| Details | [`run-info.txt`](run-info.txt) |

## Summary

- **All 13 apps render on the GPU.** Each one runs its UI on `GskGLRenderer` over EGL on `/dev/dri/renderD128` (etnaviv). No software renderer, no GPU hang in the kernel log, no coredump. Epiphany's page content is composited by WebKit; only its GTK side was checked.
- **No app reaches 60 fps, and none can on screen.** The panel's real vblank rate is **50.85 Hz (19.67 ms)**, measured from the kernel ([`vblank-measurement.txt`](vblank-measurement.txt)), while sway and GTK assume 60 Hz. Apps that redraw continuously settle at about 50 fps, which is that cap. Papers is below it (24.8 fps). Weather's frame clock reports about 59 fps, but frames above 50.8 per second cannot be shown. A non-GTK control (glmark2 without vsync) runs light fullscreen scenes at 295-633 fps, so the GPU is not the limit.
- **Showtime's video is solid green** with GTK's default dmabuf video path and correct with `GDK_DISABLE=dmabuf`.
- **Epiphany is killed by the kernel OOM killer on an animated page** (process-tree RSS 0.6 GB to 2.5 GB when scrolling starts, 3.9 GB board). A plain scrolling page works.

## Results

| App | What was driven | On GPU | Busy fps (median) | Frames at 60 Hz pace | Frames at display pace | App CPU mean % | RSS peak MB | App killed |
|---|---|---|---|---|---|---|---|---|
| Nautilus (Files) | icon view, Page Up/Down, zoom | YES | 49.5 | 8.9% | 53.7% | 24.0 | 326.0 | no |
| Papers (Documents) | 40-page PDF, scroll + zoom | YES | 24.8 | 5.2% | 14.9% | 20.0 | 462.0 | no |
| Maps | zoom + pan (live tiles) | YES | 50.0 | 16.1% | 62.5% | 34.0 | 645.0 | no |
| Epiphany (Web), plain page | 800-row text page, scrolling | YES | 49.5 | 12.2% | 64.8% | 84.0 | 1330.0 | no |
| Epiphany, animated page | CSS + canvas animation, scrolling (OOM-killed) | YES | 50.5 | 4.8% | 89.1% | 177.0 | 2468.0 | yes (OOM) |
| Software | static page, no frames drawn | YES | - | - | - | 59.0 | 491.0 | no |
| Weather | London, hourly/daily views | YES | 58.8 | 78.3% | 90.2% | 18.0 | 270.0 | no |
| System Monitor | Resources tab, live graphs | YES | 50.8 | 8.6% | 88.6% | 28.0 | 270.0 | no |
| Calendar | month view paging | YES | 50.9 | 20.6% | 91.2% | 8.0 | 241.0 | no |
| Console (kgx) | `seq 1 300000`, `ls -R` | YES | 51.5 | 35.4% | 82.5% | 18.0 | 204.0 | no |
| Ptyxis (Terminal) | `seq 1 300000`, `ls -R` | YES | 50.8 | 20.3% | 87.9% | 11.0 | 218.0 | no |
| Showtime (Video), default | VP9 720p30 playing: green picture | YES | 50.8 | 0.0% | 100.0% | 9.0 | 252.0 | no |
| Showtime, `GDK_DISABLE=dmabuf` | same video: correct picture | YES | 50.8 | 0.0% | 100.0% | 10.0 | 248.0 | no |
| Fractal (Matrix) | login flow (no account) | YES | 50.3 | 11.3% | 70.2% | 15.0 | 244.0 | no |
| Snapshot (Camera) | "No Camera Found" page (static) | YES | 51.0 | 22.2% | 95.6% | 1.0 | 216.0 | no |

Reading the columns:

- **Busy fps**: 1000 / median frame interval while the app is continuously redrawing (frames less than 100 ms apart). Idle time is excluded.
- **Frames at 60 Hz pace**: share of those frames with interval <= 18 ms.
- **Frames at display pace**: share with interval <= 21.6 ms (1.1 x the measured 19.67 ms vblank).
- **On GPU**: `GskGLRenderer` in the log, `/dev/dri/renderD128` held by the app's process tree, no software renderer.
- Complete tables and definitions: [`summary.md`](summary.md), [`summary.csv`](summary.csv), [`summary.json`](summary.json).

## Findings

1. **The display runs at 50.85 Hz, not 60.** Four measurements with `scripts/drm_vblank_rate.c` (`DRM_IOCTL_WAIT_VBLANK` on `/dev/dri/card2`): 50.82 to 50.87 Hz. The cause (pixel clock or DSI timing) was not investigated; it is a display/kernel matter, not Mesa.
2. **Showtime shows a green picture with the default dmabuf path.** Same VP9 720p30 file, playback clock advancing: default is solid green ([`showtime/active.png`](showtime/active.png)); with `GDK_DISABLE=dmabuf` the picture is correct ([`showtime--GDK_DISABLE-dmabuf/active.png`](showtime--GDK_DISABLE-dmabuf/active.png)). It resembles the Chromium NV12 colour problem in [`../chromium-nv12-mr46144/`](../chromium-nv12-mr46144/README.md); the cause here was not isolated.
3. **Epiphany: plain page works, animated page is OOM-killed.** With a fresh profile and the page served over local http, the plain page renders and scrolls (49.5 fps busy median, RSS peak 1.3 GB). A page with a CSS animation plus a canvas animation loop grows the tree from about 0.6 GB to 2.5 GB when scrolling starts and the kernel kills Epiphany (800-row and 4000-row versions both). Which animation is responsible, and whether it is GPU-related, was not isolated. Local `file://` pages did not load, and Epiphany's session restore reopens old windows unless a fresh `--profile` is used. The earlier [`../app-benchmarks`](../app-benchmarks/README.md) run reported that Epiphany loaded no page at all; with a fresh profile and http it does.
4. **Papers is the slowest animating app** (24.8 fps busy median, 15% of frames at display pace). Maps (62%) and Nautilus (54%) keep display pace only part of the time; p95 frame times for Nautilus, Maps and Papers are 66-71 ms.
5. **Software, Snapshot and Fractal are not meaningful fps tests.** Software drew no frames during the scripted phase (static Explore page after a 45 s refresh). Snapshot has no camera and shows a static "No Camera Found" page. Fractal has no Matrix account; the scripted Tab presses walk into its login flow.

## Method

[`scripts/gtk4_apps_fps.sh`](../scripts/gtk4_apps_fps.sh) runs on the board, one app at a time, with `GDK_DEBUG=frames:opengl GSK_DEBUG=renderer`. Frame intervals come from the GDK frame-clock log, not from the compositor, and the logging adds a little overhead. [`gtk4_apps_metrics.py`](../scripts/gtk4_apps_metrics.py) samples CPU, RSS and the etnaviv fdinfo of the app's process tree once per second. [`gtk4_apps_analyze.py`](../scripts/gtk4_apps_analyze.py) produces the summary.

**Isolation.** Before every app the script closes all other windows, kills known app processes, closes the launcher drawer and any stale test web server, and requires an empty sway tree and CPU >= 90% idle (98-99% in every run). After launch, any window outside the app's process tree is detected and handled (a keyring prompt gets `KEYRING_PASSWORD` if set, anything else is closed), then re-checked. The result is in each app's `isolation.txt`. The first full run of Nautilus, Papers, Maps, Weather, System Monitor, Calendar, Console, Ptyxis and Showtime logged exactly one app window each but predates the explicit foreign-window check.

**Limits.**
- Input is scripted with `wtype`, about 25-40 s per app. Apps repaint only when something changes, so fps are meaningful only while animating or scrolling.
- Maps, Software and Weather depend on the internet at test time.
- fdinfo exposes memory only, not GPU engine time.
- One run per app on one image; run-to-run variance was not measured.

## Reproduce

On the board (sway session running; packages `nautilus papers gnome-maps epiphany gnome-software gnome-weather gnome-system-monitor gnome-calendar gnome-console ptyxis showtime fractal snapshot`, install with `dnf install --exclude='mesa*'` so the Mesa under test is not replaced):

```
scp scripts/gtk4_apps_fps.sh scripts/gtk4_apps_metrics.py mecha@<comet>:gtk4-apps/
ssh mecha@<comet>
cd gtk4-apps
./gtk4_apps_fps.sh ~/gtk4-apps-run/full                          # all 13 apps, ~15 min
./gtk4_apps_fps.sh ~/gtk4-apps-run/one showtime                  # a single app
EXTRA_ENV="GDK_DISABLE=dmabuf" ./gtk4_apps_fps.sh ~/gtk4-apps-run/showtime-no-dmabuf showtime
EXTRA_ENV="EPI_PAGE=http://127.0.0.1:8099/plain.html" ./gtk4_apps_fps.sh ~/gtk4-apps-run/epiphany-plain epiphany
```

Then copy the run directory to a laptop and summarise it with `python3 scripts/gtk4_apps_analyze.py <rundir>`. Per-app notes in `notes.txt` are optional and are shown in the table. The display rate is measured with `scripts/drm_vblank_rate.c`: cross-compile with `aarch64-linux-gnu-gcc`, run `./drm_vblank_rate /dev/dri/card2` on the board, and write the resulting `period_ms=` line into `vblank-measurement.txt`.

## Layout

```
README.md  summary.md  summary.csv  summary.json  run-info.txt  vblank-measurement.txt
<app>/        raw.log        app output including the GDK frame-clock lines
              metrics.csv    1 Hz CPU / RSS / etnaviv DRM clients and memory
              phases.txt     wall-clock markers (same time format as raw.log)
              isolation.txt  what was on screen before and after launch
              kernel.txt     kernel log lines during the run, coredump list
              drm-fdinfo.txt etnaviv fdinfo snapshot
              active.png     screenshot at the end of the scripted phase
              notes.txt      optional remarks
<app>--<variant>/   same files for an A/B run (environment switch or page)
```
