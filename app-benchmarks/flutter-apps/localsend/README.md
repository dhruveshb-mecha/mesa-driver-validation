# LocalSend (Flutter) - animated radar, tabs, settings

Track: **flutter**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/home/mecha/flutter-apps/localsend/localsend_app`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. receive-screen-animated-radar
2. tab-switch-send
3. tab-switch-settings
4. settings-scroll
5. tab-switch-receive

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-default | a01-gles | a02-default | a02-gles |
|---|---|---|---|---|
| receive-screen-animated-radar | 28.3 | 28.2 | 28.5 | 28.5 |
| tab-switch-send | 30.2 | 28.5 | 31.0 | 29.5 |
| tab-switch-settings | 5.0 | 4.5 | 4.7 | 4.5 |
| settings-scroll | 2.5 | 2.5 | 2.5 | 2.5 |
| tab-switch-receive | 31.0 | 30.2 | 30.7 | 30.0 |

A static screen redraws only on change, so ~0 fps there is correct; judge throughput from the phases that scroll, zoom or animate.

## Health per attempt

| attempt | app alive at end | GPU hang events | other etnaviv/drm kernel lines | llvmpipe seen in log |
|---|---|---|---|---|
| attempt-01-default | True | 0 | 0 | False |
| attempt-01-gles | True | 0 | 0 | False |
| attempt-02-default | True | 0 | 0 | False |
| attempt-02-gles | True | 0 | 0 | False |

## What this shows / what to look into

- Renders and animates (radar animation 28-30 fps) with `GDK_GL=gles`; no GPU events in 4 runs.
- **Without `GDK_GL=gles` the app logs `Failed to create OpenGL context: Unable to create a GL context` and silently falls back to software rendering**, at the same ~28-31 fps. So the fps of this app says nothing about GPU speed: a CPU-rendered UI is just as fast at this complexity. Do not read the `default` columns as GPU results.
- Package: Flathub aarch64 build 1.18.2, bundle copied to the board and run against the board's Mesa (not the Flatpak runtime).

## Screenshots (first GL attempt)

- [receive-screen-animated-radar](attempt-01-gles/receive-screen-animated-radar.png)
- [tab-switch-send](attempt-01-gles/tab-switch-send.png)
- [tab-switch-settings](attempt-01-gles/tab-switch-settings.png)
- [settings-scroll](attempt-01-gles/settings-scroll.png)
- [tab-switch-receive](attempt-01-gles/tab-switch-receive.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
