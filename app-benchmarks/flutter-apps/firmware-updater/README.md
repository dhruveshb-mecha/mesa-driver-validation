# Canonical Firmware Updater (Flutter) - startup

Track: **flutter**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/home/mecha/flutter-apps/firmware_updater/firmware-updater`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. startup-spinner-waiting-for-fwupd

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-default | a01-gles | a02-default | a02-gles |
|---|---|---|---|---|
| startup-spinner-waiting-for-fwupd | 0.0 | 0.0 | 0.0 | 0.0 |

A static screen redraws only on change, so ~0 fps there is correct; judge throughput from the phases that scroll, zoom or animate.

## Health per attempt

| attempt | app alive at end | GPU hang events | other etnaviv/drm kernel lines | llvmpipe seen in log |
|---|---|---|---|---|
| attempt-01-default | True | 0 | 0 | False |
| attempt-01-gles | True | 0 | 0 | False |
| attempt-02-default | True | 0 | 0 | False |
| attempt-02-gles | True | 0 | 0 | False |

## What this shows / what to look into

- Impeller GLES starts and the window draws a spinner, then the app waits for the fwupd service, which is not running on this board, and stops repainting (0 fps). It never reaches its real UI, so this is a start-up check only, not a performance case.
- A `snapctl` shim (prints `mode: run`) is needed because the app is snap-packaged; it lives in `~/flutter-apps/shims` on the board. No GPU events.

## Screenshots (first GL attempt)

- [startup-spinner-waiting-for-fwupd](attempt-01-gles/startup-spinner-waiting-for-fwupd.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
