# Real-application benchmarks on Mesa 27 (Mecha Comet)

Goal: check the Mesa driver that is on the device (**Mesa 27.0.0~devel git 7b4b394**, `OpenGL ES 3.0 Mesa 27.0.0-devel`, `Vivante GC7000 rev 6204`, kernel 7.1.5, Fedora 44 aarch64, sway/Wayland, 1080x1240 panel) with software people actually use, in two separate tracks:

| track | folder | what | toolkit |
|---|---|---|---|
| GTK4 apps | [`gtk4-apps/`](gtk4-apps/README.md) | 10 mainstream GNOME apps, each in 3 renderer modes x 2 attempts | GTK 4.22.5 / libadwaita 1.9.4 |
| Flutter apps | [`flutter-apps/`](flutter-apps/README.md) | 4 real Flutter Linux apps, with and without `GDK_GL=gles`, 2 attempts | Flutter GTK3 embedder (no released Flutter uses GTK4) |

This complements `../cases/` (synthetic probes, stress and failure cases). Nothing here replaces `../FEEDBACK.md`; see the addendum there.

## Results at a glance

- **No GPU hang, crash, llvmpipe fallback or etnaviv/drm kernel message in any of the 76 runs.**
- **GTK4 Text Editor: GL renderer 4-8x slower than Cairo** (scrolling a 30000-line file 4-8 vs 34 fps; typing 5 vs 24 fps). The default renderer on this image is the GL one. Loupe (large image zoom) and Font Viewer are the opposite: GL is 1.5-5x faster than Cairo. So the GL path is good for some content and weak for text-heavy content.
- **Flutter needs `GDK_GL=gles`.** Without it GTK3 logs `Failed to create OpenGL context`; older engines (LocalSend, Ricochlime) silently render in software at similar fps, the newer one (Ente Auth) draws nothing.
- **Epiphany (WebKitGTK 6) loads no page at all** on this image; GPU toggles do not change it. Cause unknown, not shown to be Mesa. WebGL is therefore untested through WebKit.
- Flutter and GTK apps with mostly static screens give low fps by nature; only phases that scroll, zoom or animate say anything about throughput.

## How a run works

`tools/app_drive.py TRACK APP MODE OUTDIR` (runs on the board): resets the app's GNOME settings and uses a fresh copy of the test data (apps remember zoom, view mode and file position), launches the app as a user would, injects pointer/keyboard input with `wlrctl` following `tools/profiles.py`, counts Wayland surface commits of the app's main surface per phase (`WAYLAND_DEBUG=client`), takes a screenshot per phase, and records the kernel journal, the app's stdout/stderr and Mesa driver logging (`MESA_DEBUG=1 EGL_LOG_LEVEL=info LIBGL_DEBUG=verbose`). `tools/make_testdata.py` generates the inputs (images, 60-page PDF, 30000-line file, folder of 400 files, HTML page). `tools/collect.py` + `notes.json` turn raw results into these folders (numbers and interpretation are kept apart).

Per attempt folder: `cmd.txt` (exact environment and command), `result.json`, `kernel-gpu-events.txt`, `renderer-evidence.txt`, `app-stdout.txt`, `app-stderr.txt`, `kernel.txt`, one screenshot per phase.

Reproduce: generate test data, copy `tools/` and the data to the board, then e.g. `python3 app_drive.py gtk4 text-editor cairo /tmp/out`.

## Limits (read before quoting numbers)

- One board, one Mesa build, no baseline, so nothing here is called a regression.
- fps = presented frames of the app's main surface under synthetic input at a fixed pace (a wheel event every 0.25-0.4 s, a key every 0.4 s). It is comparable between modes of the same app, not between apps, and not a GPU-utilisation figure.
- Idle phases of some apps show a steady ~28-30 fps in every mode including Cairo (Calculator, Font Viewer, LocalSend): something redraws at ~30 Hz independent of the renderer. Not investigated.
- Wheel scrolling did not reach Papers (page-fit view) or Characters with synthetic input; keys and taps are used there.
- Maps depends on network tiles. Epiphany did not load pages (see its folder).
- Two attempts per mode: they agree closely, but 2 is not a statistical sample.
- Board changes made for this track: `dnf install nautilus papers gnome-maps epiphany` with `--exclude='mesa*'` (Mesa unchanged), app bundles under `~/flutter-apps/`, a `snapctl` shim, test data and tools under `~/appbench*`.
- Discarded runs (kept out of the repo): a first sweep whose frame counter missed Cairo's commit lines, and a second one where apps reused remembered state from earlier runs.
