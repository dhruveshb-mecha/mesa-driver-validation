# Ente Auth (Flutter) - onboarding carousel and routes

Track: **flutter**   Mesa on the board: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`   Verdict: **PASS (renders, no GPU events)**

## What was run
`/home/mecha/flutter-apps/ente_auth/enteauth`

Workflow phases (synthetic pointer/keyboard input, see `../../tools/profiles.py`):

1. onboarding-carousel
2. route-to-log-in-page
3. type-email-in-field
4. route-back

## Frame rate per phase (presented frames per second of the app's main surface)

| phase | a01-default | a01-gles | a02-default | a02-gles |
|---|---|---|---|---|
| onboarding-carousel | 0.0 | 5.5 | 0.0 | 5.7 |
| route-to-log-in-page | 0.0 | 3.6 | 0.0 | 4.0 |
| type-email-in-field | 0.0 | 5.2 | 0.0 | 5.0 |
| route-back | 0.0 | 5.5 | 0.0 | 5.0 |

A static screen redraws only on change, so ~0 fps there is correct; judge throughput from the phases that scroll, zoom or animate.

## Health per attempt

| attempt | app alive at end | GPU hang events | other etnaviv/drm kernel lines | llvmpipe seen in log |
|---|---|---|---|---|
| attempt-01-default | True | 0 | 0 | False |
| attempt-01-gles | True | 0 | 0 | False |
| attempt-02-default | True | 0 | 0 | False |
| attempt-02-gles | True | 0 | 0 | False |

## What this shows / what to look into

- Renders with `GDK_GL=gles` (carousel, Log in page, text field). Frame rates are low (4-6 fps) because the screens are mostly static.
- **Without `GDK_GL=gles` the window stays empty** (0 frames): this newer engine has no software fallback after `Failed to create OpenGL context`. Every Flutter app on the image needs `GDK_GL=gles` set for the session.
- Built from source (4.4.27) on the laptop because only x86_64 packages exist; see `../README.md`.

## Screenshots (first GL attempt)

- [onboarding-carousel](attempt-01-gles/onboarding-carousel.png)
- [route-to-log-in-page](attempt-01-gles/route-to-log-in-page.png)
- [type-email-in-field](attempt-01-gles/type-email-in-field.png)
- [route-back](attempt-01-gles/route-back.png)

## Files
Each `attempt-NN-<mode>/` has `cmd.txt` (exact environment + command), `result.json`, `kernel-gpu-events.txt` (etnaviv/drm lines of that run), `renderer-evidence.txt` (renderer / EGL lines from the app log), `app-stdout.txt`, `app-stderr.txt`, `kernel.txt` and the screenshots.
