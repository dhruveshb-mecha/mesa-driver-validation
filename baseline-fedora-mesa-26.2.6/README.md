# Baseline: Fedora mainline Mesa 26.2.6 on the Comet (2026-11-07)

The same board with Fedora's stock `mesa-*` 26.2.6-1.fc44 packages instead of the custom Mesa 27.0.0~devel (7b4b394) used in `cases/`.
Scope of this baseline: core GTK apps and Flutter apps on the GTK3 embedder (no eLinux apps).

**Not directly comparable to `cases/` yet:** the board image changed between the two runs (see `state.txt`: kernel 7.2.4, image 20261105-0909;
the earlier runs were kernel 7.1.5). Re-run the custom Mesa 27 on this same image for a clean A/B.

| check | result | file |
|---|---|---|
| GL version exposed | **OpenGL ES 2.0 Mesa 26.2.6**, renderer `Vivante GC7000 rev 6204`, glmark2 ES2 score ~930 | `glmark2.txt` |
| ES 3.0 headless probe (`scripts/gles3_probe.py`) | FAIL: `no ES3 EGL config` | `gles3-probe.txt` |
| GTK4 `GSK_RENDERER=gl` | cannot start the GL renderer: ES 3.0, GL 3.3 and legacy 3.3 contexts all fail, `Failed to realize renderer 'GskGLRenderer' ... No EGL configuration available` | `gtk4-gl.txt` |
| GTK4 `GSK_RENDERER=cairo` | app stays up until the timeout (rc=124); GDK still logs one `Unable to create a GL context` warning | `gtk4-cairo.txt` |
| Flutter GTK3 apps (`demo_counter`, `gpu_bench`, `GDK_GL=gles`) | Impeller starts, then SIGABRT (rc=134, core dump): `No provider of glBlitFramebuffer found ... OpenGL ES 3.0` | `flutter-counter.txt`, `flutter-gpu_bench.txt`, `kernel.txt` |
| GPU hangs (`recover hung GPU`) | none, but nothing GL-3 can run to trigger one | `kernel.txt` |

Meaning: on mainline Mesa this GPU has no ES 3.0, so every ES 3.0 consumer (GTK4 GL renderer, Flutter Impeller) fails at startup. This is the
baseline the ES 3.0 work is measured against. The hangs and crashes in `cases/` are only reachable with ES 3.0 enabled.

Not done: screenshots (the first attempt caught the app launcher on top, so it is not kept), GTK4 demo sweep, Flutter apps beyond the two above.

## Real GTK4 apps (`gtk4-real-apps/`)
Six real Fedora GTK4 / libadwaita apps, each launched for 9 s with `GSK_RENDERER=gl` and with `GSK_RENDERER=cairo`:
Text Editor, Nautilus, Loupe, Characters, Clocks, Maps. `contact-sheet-top-gl-bottom-cairo.png` shows them side by side.
- All twelve launches stay alive and no GPU hang appears (the `*.kernel` files are not kept because they are empty).
- With `gl` every app logs `Failed to realize renderer 'GskGLRenderer' ... No EGL configuration available` and falls back to Cairo, so the two rows look the same.
  This is why "it runs" is not enough for a before/after: the real difference is which renderer is active, and it has to be shown on screen.
- Maps with `gl` showed no window after 9 s (the process was alive, the Cairo run was fine). Not investigated: it may just be a slow first start.
- The Mechanix app drawer (`nwg-drawer`) was found open as a full-screen overlay and hid the apps in the first attempt; it must be closed before screenshots or recording.
