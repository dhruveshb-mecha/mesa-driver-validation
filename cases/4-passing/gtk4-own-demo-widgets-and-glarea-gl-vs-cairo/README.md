# Own minimal GTK4 C demo (widgets + GtkGLArea), GL vs Cairo

**Verdict:** PASS

## What was run
`gtk4-demo/demo.c` (this repo's source in gpu-test): animated widgets scene and GtkGLArea scene, 10 s each, GTK frame-clock fps printed.

## Result
Both modes run on both renderers; fps lines in stdout.

## Why it matters
A small known-good GTK4 program to compare renderers without stock-demo noise.

## Command (as run on the Comet)
```
(GSK_RENDERER=gl ~/gtk4-demo/gtk4_demo widgets 8 2>&1 | grep GTK4DEMO) & sleep 5; grim /tmp/gtk4demo-widgets-gl.png; wait
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-gtk4.demo-widgets-gl` | RAN_OK | 0 | 10.4 | 0 | 75.0 | yes |
| `attempt-02-gtk4.demo-widgets-cairo` | RAN_OK | 0 | 10.1 | 0 | 75.0 | yes |
| `attempt-03-gtk4.demo-glarea-gl` | RAN_OK | 0 | 10.2 | 0 | 77.0 | yes |
| `attempt-04-gtk4.demo-glarea-cairo` | RAN_OK | 0 | 10.3 | 0 | 76.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-gtk4.demo-widgets-gl**
```
GTK4DEMO {"mode":"widgets","renderer":"GskGLRenderer","gl":"n/a","frames":340,"fps":35.8,"size":"536x568"}
```

**attempt-02-gtk4.demo-widgets-cairo**
```
GTK4DEMO {"mode":"widgets","renderer":"GskCairoRenderer","gl":"n/a","frames":302,"fps":31.8,"size":"536x568"}
```

**attempt-03-gtk4.demo-glarea-gl**
```
GTK4DEMO {"mode":"glarea","renderer":"GskGLRenderer","gl":"Vivante GC7000 rev 6204 | OpenGL ES 3.0 Mesa 27.0.0-devel","frames":374,"fps":39.4,"size":"536x568"}
```

**attempt-04-gtk4.demo-glarea-cairo**
```
GTK4DEMO {"mode":"glarea","renderer":"GskCairoRenderer","gl":"Vivante GC7000 rev 6204 | OpenGL ES 3.0 Mesa 27.0.0-devel","frames":183,"fps":19.2,"size":"536x568"}
```

