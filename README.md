# Mesa etnaviv OpenGL ES 3.0 validation on the Mecha Comet

Test harness, scripts and results for validating the Mesa `etnaviv` OpenGL ES 3.0 work on the Mecha Comet
(NXP i.MX8M Plus, Vivante GC7000UL rev 6204, 1080x1240 DSI panel, Fedora 44 aarch64, sway/Wayland).

## Results

Results come from different Mesa builds and board images, so they are kept in separate folders and are not directly comparable.

| Folder | What it covers | Mesa | Kernel | Date |
|---|---|---|---|---|
| [`FEEDBACK.md`](FEEDBACK.md) | Prioritised list of issues to look into, each pointing at a case folder | 27.0.0~devel `7b4b394` | 7.1.5 | 2026-11-02..04 |
| [`cases/`](cases/INDEX.md) | One folder per case: GPU hangs, functional failures, passing controls, performance. Every case has the exact command, stdout/stderr, kernel log and screenshots | `7b4b394` | 7.1.5 | 2026-11-02..03 |
| [`app-benchmarks/`](app-benchmarks/README.md) | Real GTK4 and Flutter apps (10 + 4 apps, several renderer modes, 2 attempts each) | `7b4b394` | 7.1.5 | 2026-11-04 |
| [`baseline-fedora-mesa-26.2.6/`](baseline-fedora-mesa-26.2.6/README.md) | The same board with stock Fedora Mesa 26.2.6 (exposes only OpenGL ES 2.0) | 26.2.6 | 7.2.4 | 2026-11-07 |
| [`chromium-nv12-mr46144/`](chromium-nv12-mr46144/README.md) | Chromium and YouTube video playback, and test programs that isolate a wrong-colour NV12 import | 27.0.0~devel `8838d84` (`mr46144`) | 7.2.4 | 2026-11-13 |
| [`gtk4-apps-mr46144-2026-11-17/`](gtk4-apps-mr46144-2026-11-17/README.md) | 13 stock GTK4 apps: GPU use and frame rate | `8838d84` (`mr46144`) | 7.2.4 | 2026-11-17 |
| [`qt-apps-mr46144-2026-11-17/`](qt-apps-mr46144-2026-11-17/README.md) | Qt 6 apps (Qt Quick, Quick 3D, Qt Widgets, Falkon): GPU use, frame rate, Quick 3D GPU hangs | `8838d84` (`mr46144`) | 7.2.4 | 2026-11-17 |

### Headlines

From the 7b4b394 runs ([`FEEDBACK.md`](FEEDBACK.md)):

- GPU hangs (`etnaviv-gpu: recover hung GPU!`): GTK4 `path_text` with the GL renderer, and SuperTuxKart deferred lighting.
- `GL_FRAMEBUFFER_UNSUPPORTED` for a 4x MSAA RGBA16F renderbuffer; WebGL2 conformance failures (`ext-color-buffer-float`, `sync-webgl-specific`); a SIGSEGV in `dri_drawable_bind_images`.
- Real apps ([`app-benchmarks/`](app-benchmarks/README.md)): no hang, crash, llvmpipe fallback or etnaviv kernel message in 76 runs.

From the stock-Mesa baseline: on Fedora's Mesa 26.2.6 the GPU exposes only OpenGL ES 2.0, so the GTK4 GL renderer and Flutter Impeller cannot start.

From the `mr46144` build:

- **NV12 allocation is fixed** (two planes), so Chromium plays video with default flags and drops far fewer frames. **The picture is still wrong:** the GPU colour conversion of a single NV12 image returns incorrect colours, while per-plane access is exact ([`chromium-nv12-mr46144/`](chromium-nv12-mr46144/README.md)).
- Qt Quick apps render on the GPU (self-running animations at the panel ceiling); Qt Widgets and KDE apps paint on the CPU. The Quick 3D examples still hang the GPU, both with the GL 3.3 override on Fedora Qt and on a GLES Qt build without it ([`qt-apps-mr46144-2026-11-17/`](qt-apps-mr46144-2026-11-17/README.md)).
- All 13 GTK4 apps render on the GPU with no hangs. Showtime's video is solid green with GTK's default dmabuf path; Epiphany is OOM-killed on an animated page ([`gtk4-apps-mr46144-2026-11-17/`](gtk4-apps-mr46144-2026-11-17/README.md)).

## Run the harness

Needs a running sway session on the Comet and the packages in [`manifest/packages.txt`](manifest/packages.txt). Install them with `--exclude='mesa*'` so the Mesa under test is not replaced: a plain `dnf install` of a `-devel` package can silently downgrade the custom Mesa.

```
make push COMET=mecha@<comet>          # laptop: copy this repo to ~/gpu-test on the Comet
ssh mecha@<comet>; cd gpu-test
make list                              # what will run
make run LABEL=<name>                  # everything, risky tests last
make report RUN=<run-id> BASE=<baseline-run-id>
```

A run writes `runs/<run-id>/` (`run.json`, `sysinfo/`, `results.jsonl`, `logs/<category>/<test-id>/`, `REPORT.md`). Statuses: `RAN_OK RAN_FAIL TIMEOUT GPU_HANG BOARD_RESET SKIP_MISSING PENDING_MANUAL`. `GPU_HANG` means etnaviv hang/fault/reset lines appeared in the kernel log during the test; `expected:` in the manifest keeps known limits (Vulkan and WebGPU have no GPU driver here) from looking like regressions.

The case folders under `cases/` call the scripts in `scripts/` as `~/gpu-test/scripts/...`, i.e. this repository copied to `~/gpu-test` on the board.

## Layout

```
README.md  FEEDBACK.md  Makefile
manifest/        test definitions (one YAML per category), env applied to every test, package list
scripts/         runner (gpuval.py), probes and drivers for GTK4, Flutter, browsers, wgpu, video;
                 gtk4_apps_*.{sh,py} (GTK4 apps frame-rate harness), qt_apps_*.{sh,py} (Qt apps), drm_vblank_rate.c, vblank_rate.py
gtk4-demo/       GtkGLArea demo source
flutter/         Flutter benchmark apps (gpu_bench, demo_counter) and the arm64 cross-build script
environment/     sysinfo of the full 7b4b394 run and the environment variables used
cases/           evidence per case; cases/INDEX.md lists them
app-benchmarks/  real-application results (GTK4, Flutter)
baseline-fedora-mesa-26.2.6/
chromium-nv12-mr46144/
gtk4-apps-mr46144-2026-11-17/
qt-apps-mr46144-2026-11-17/
SHA256SUMS       checksums of all result files
```

Case folders contain `README.md` (what was run, result, why it matters, what to look into), and one `attempt-NN-<label>/` per execution with `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt`, `kernel-gpu-events.txt`, `result.json`, screenshots and `artifacts/`. Files over 1 MB are stored gzipped.
