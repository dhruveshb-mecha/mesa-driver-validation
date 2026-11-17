# Ricochlime (Flutter + Flame game) - menu and gameplay

Track: **flutter**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/home/mecha/flutter-apps/ricochlime/bin/ricochlime`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. menu-idle
2. tap-play-start-game
3. gameplay-shooting-taps

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-default | a01-gles | a02-default | a02-gles |
|---|---|---|---|---|
| menu-idle | 0.0 | 0.0 | 0.0 | 0.0 |
| tap-play-start-game | 33.6 | 36.0 | 34.8 | 35.8 |
| gameplay-shooting-taps | 35.0 | 37.8 | 35.2 | 37.6 |

A static screen redraws only on change, so ~0 fps there is correct; judge throughput from the phases that scroll, zoom or animate.

## Health per attempt

| attempt | app alive at end | GPU hang events | other etnaviv/drm kernel lines | llvmpipe seen in log |
|---|---|---|---|---|
| attempt-01-default | True | 0 | 0 | False |
| attempt-01-gles | True | 0 | 0 | False |
| attempt-02-default | True | 0 | 0 | False |
| attempt-02-gles | True | 0 | 0 | False |

## What this shows / what to look into

- Real Flame-engine game: menu, start game and shooting taps run at 36-38 fps with `GDK_GL=gles` for 4 runs, no hangs or errors.
- Without `GDK_GL=gles` it falls back to software rendering (logged) and still reaches 34-35 fps, so on this 2D pixel-art game the GPU path is only ~7% faster than the CPU fallback. Possible that the frame rate is capped by the game loop; not investigated.
- Package: Flathub aarch64 build 1.13.1.

## Screenshots (first GL attempt)

- [menu-idle](attempt-01-gles/menu-idle.png)
- [tap-play-start-game](attempt-01-gles/tap-play-start-game.png)
- [gameplay-shooting-taps](attempt-01-gles/gameplay-shooting-taps.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
