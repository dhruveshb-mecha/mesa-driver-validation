# Real GTK4 apps: widget-factory (GL and Cairo), node-editor, gnome-text-editor

**Verdict:** PASS

## What was run
Each app launched for ~12-15 s under `GSK_RENDERER=gl` (and Cairo for widget-factory); screenshot taken.

## Result
All render, no crash, no hang.

## Why it matters
The normal GTK4 desktop use case is fine. Failures are limited to the specific stock demos listed under 1/2.

## Command (as run on the Comet)
```
GSK_RENDERER=gl GSK_DEBUG=renderer gtk4-widget-factory
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gtk4.widget-factory-gl` | RAN_OK | -15 | 15.1 | 0 | 80.0 | yes |
| `attempt-02-gtk4.widget-factory-cairo` | RAN_OK | -15 | 15.1 | 0 | 83.0 | yes |
| `attempt-03-gtk4.node-editor-gl` | RAN_OK | -15 | 12.1 | 0 | 79.0 | yes |
| `attempt-04-gtk4.gnome-text-editor-gl` | RAN_OK | -15 | 12.1 | 0 | 78.0 | yes |
| `attempt-05-screenshot-gtk4.widget-factory-gl` | RAN_OK | -15 | 15.1 | 0 | 76.0 | no |
| `attempt-06-screenshot-gtk4.widget-factory-cairo` | RAN_OK | -15 | 15.1 | 0 | 78.0 | no |
| `attempt-07-screenshot-gtk4.node-editor-gl` | RAN_OK | -15 | 12.1 | 0 | 75.0 | no |
| `attempt-08-screenshot-gtk4.gnome-text-editor-gl` | RAN_OK | -15 | 12.1 | 0 | 73.0 | no |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-gtk4.widget-factory-gl**
```
Environment variable GSK_RENDERER=gl set, trying GskGLRenderer
Using renderer 'GskGLRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-02-gtk4.widget-factory-cairo**
```
Environment variable GSK_RENDERER=cairo set, trying GskCairoRenderer
Using renderer 'GskCairoRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-03-gtk4.node-editor-gl**
```
Environment variable GSK_RENDERER=gl set, trying GskGLRenderer
Using renderer 'GskGLRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-04-gtk4.gnome-text-editor-gl**
```
Environment variable GSK_RENDERER=gl set, trying GskGLRenderer
Using renderer 'GskGLRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-05-screenshot-gtk4.widget-factory-gl**
```
Environment variable GSK_RENDERER=gl set, trying GskGLRenderer
Using renderer 'GskGLRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-06-screenshot-gtk4.widget-factory-cairo**
```
Environment variable GSK_RENDERER=cairo set, trying GskCairoRenderer
Using renderer 'GskCairoRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-07-screenshot-gtk4.node-editor-gl**
```
Environment variable GSK_RENDERER=gl set, trying GskGLRenderer
Using renderer 'GskGLRenderer' for surface 'GdkWaylandToplevel'
```

**attempt-08-screenshot-gtk4.gnome-text-editor-gl**
```
Environment variable GSK_RENDERER=gl set, trying GskGLRenderer
Using renderer 'GskGLRenderer' for surface 'GdkWaylandToplevel'
```

