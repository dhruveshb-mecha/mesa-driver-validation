# Official flutter/samples `animations` app (17 pages), driven with wlrctl, fps from Wayland commit counting

**Verdict:** PASS

## What was run
`flutter/demo_animations` built with the stock SDK; `flutter_anim_drive.py` clicks through the pages and counts `wl_surface.commit` events per second. A page-by-page screenshot is taken.

## Result
All 17 pages render with no hang or crash. Peak ~39 fps (see samples.json).

## Why it matters
Real-world Flutter app behaviour, beyond synthetic scenes.

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/flutter_anim_drive.py /tmp/flutter-anim-drive 6
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-complete-run` | RAN_OK | 0 | 194.9 | 0 | 74.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-complete-run**
```
FLUTTERANIM {"sample": "AnimatedContainer", "fps": 0.0, "commits": 0, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "PageRouteBuilder", "fps": 4.1, "commits": 20, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "AnimationController", "fps": 0.4, "commits": 2, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "Tweens", "fps": 0.4, "commits": 2, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "AnimatedBuilder", "fps": 27.6, "commits": 137, "secs": 5.0, "alive": true}
FLUTTERANIM {"sample": "CustomTween", "fps": 8.3, "commits": 41, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "TweenSequences", "fps": 0.0, "commits": 0, "secs": 4.9, "alive": true}
... (5 more distinct lines) ...
FLUTTERANIM {"sample": "SpringPhysics", "fps": 39.4, "commits": 195, "secs": 5.0, "alive": true}
FLUTTERANIM {"sample": "AnimatedList", "fps": 0.0, "commits": 0, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "AnimatedPositioned", "fps": 0.0, "commits": 0, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "AnimatedSwitcher", "fps": 8.7, "commits": 43, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "HeroAnimation", "fps": 0.0, "commits": 0, "secs": 4.9, "alive": true}
FLUTTERANIM {"sample": "CurvedAnimation", "fps": 0.0, "commits": 0, "secs": 4.9, "alive": true}
FLUTTERANIMSUMMARY samples=18 ok=18 min_fps=0.0 max_fps=39.4 app_died=0
```

