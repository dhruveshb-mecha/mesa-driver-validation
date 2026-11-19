# GTK4 demo `badapple` fails to import video frames (NV12 dmabuf) with the GL renderer

**Verdict:** FAIL

## What was run
GTK's own demo `badapple` (`gtk4-demo --run badapple`, GTK 4.24.1) was started with `GSK_RENDERER=gl` on a Wayland/sway session and left running for 20 seconds, then a screenshot was taken. Mesa is 27.0.0~devel git `6f23942285e` and the kernel is 7.2.4 (see `artifacts/run-info.txt`).

The control run is identical except that `GDK_DISABLE=dmabuf` is set, which stops GTK from using shared dmabuf buffers.

## Result
With the default settings the demo printed 18 errors from Mesa, and each one was followed by a GTK error:
```
MESA: error: etna_resource_from_handle:1055: BO size 28672 is too small for RS engine height padding (268439552, format PIPE_FORMAT_R8_UNORM)
(gtk4-demo:3341): Gdk-CRITICAL **: Failed to download 128x128 dmabuf texture (format NV12:0x600000000000001)
```
The demo kept running and the GPU did not hang. In the control run neither error appeared.

The default screenshot has faint vertical streaks over the background. The control screenshot has no streaks and shows a faded hexagon shape instead.

The Mesa message comes from the etnaviv function `etna_resource_from_handle`. It says the buffer (28672 bytes, format `PIPE_FORMAT_R8_UNORM`) is too small for a padded height of 268439552. The frame is a 128x128 NV12 texture in the Vivante tiled layout (modifier `0x600000000000001`).

In the earlier GTK4 app run, the video in Showtime was solid green with the default dmabuf path and correct with `GDK_DISABLE=dmabuf` ([`gtk4-apps-mr46144-2026-11-17/showtime`](../../../gtk4-apps-mr46144-2026-11-17/showtime/)).

## Command (as run on the Comet)
```
python3 ~/gpu-test/scripts/gtk4_demo_sweep.py gl /home/mecha/cases-run/badapple-dmabuf/artifacts/x 20 "^badapple$"
```
and for the control
```
GDK_DISABLE=dmabuf python3 ~/gpu-test/scripts/gtk4_demo_sweep.py gl /home/mecha/cases-run/badapple-nodmabuf/artifacts/x 20 "^badapple$"
```

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gl-renderer-default-dmabuf-errors` | RAN_FAIL | 0 | 23 | 0 | 76.0 | no |
| `attempt-02-control-gdk-disable-dmabuf-no-errors` | RAN_OK | 0 | 23 | 0 | 74.0 | no |

Each attempt folder holds `cmd.txt`, `stdout.txt`, `kernel.txt` (kernel journal during the run), `kernel-gpu-events.txt` (etnaviv and DRM lines only), `result.json`, and `artifacts/` with the demo's output (`badapple.log`), the screenshot (`badapple.png`) and `run-info.txt` (package versions).

## Key lines from the logs

**attempt-01-gl-renderer-default-dmabuf-errors**
```
{"demo": "badapple", "renderer_requested": "gl", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 21, "gtk_renderer": "GskGLRenderer", "blank": null}
```

**attempt-02-control-gdk-disable-dmabuf-no-errors**
```
{"demo": "badapple", "renderer_requested": "gl", "alive_at_screenshot": true, "early_rc": null, "crashed": false, "warnings": 1, "gtk_renderer": "GskGLRenderer", "blank": null}
```
