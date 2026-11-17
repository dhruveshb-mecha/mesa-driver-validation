# Bevy main (0.20-dev, wgpu 30) finds the Vivante GL adapter but panics: no present modes (surfaceless EGL)

**Verdict:** FAIL (not Mesa)

## What was run
Bevy PBR cube benchmark cross-built on the laptop (`assets/bevy-gl-test`), run with the wgpu GL backend and with Vulkan.

## Result
GL: adapter is `Vivante GC7000 rev 6204 / OpenGL ES 3.0 Mesa 27.0.0-devel`, then panic in `bevy_render/src/view/window/mod.rs` "Fallback system failed to choose present mode ... Options: []". wgpu-hal logs "No (or unknown) windowing system present. Using surfaceless platform". Vulkan: panics at startup (llvmpipe only).

## Why it matters
Most likely Bevy creating its wgpu instance before the window exists, so there are no present modes. **Not fully proven:** the `Using surfaceless platform` line is also printed by the working wgpu examples (see `4-passing/wgpu-native-cube-bunnymark-gl`), so that line alone is not the proof; the hard evidence is the empty present-mode list `Options: []`. Treat it as a Bevy/wgpu integration problem unless a Mesa-side reason turns up.

## What to look into
None in Mesa. A Bevy/wgpu issue.

## Command (as run on the Comet)
```
WGPU_BACKEND=gl RUST_LOG=wgpu_hal=debug,bevy_render=info,warn ~/wgpu-apps/bevy-gl-test 20 12
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-wgpu-gl-backend` | RAN_FAIL | 0 | 1.2 | 0 | 82.0 | yes |
| `attempt-02-wgpu-vulkan-backend` | RAN_FAIL | 101 | 0.4 | 0 | 80.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-wgpu-gl-backend**
```
    "EGL_MESA_platform_surfaceless",
2026-11-03T09:07:33.106946Z DEBUG wgpu_hal::gles::egl: No (or unknown) windowing system ((None, Some(Instance(Dynamic(Library@0xaaaaf986ee50))))) present. Using surfaceless platform
    "EGL_KHR_surfaceless_context",
2026-11-03T09:07:33.190979Z DEBUG wgpu_hal::gles::egl: 	EGL context: +surfaceless
2026-11-03T09:07:33.196748Z DEBUG wgpu_hal::gles::adapter: Vendor: Mesa
2026-11-03T09:07:33.196893Z DEBUG wgpu_hal::gles::adapter: Renderer: Vivante GC7000 rev 6204
2026-11-03T09:07:33.196906Z DEBUG wgpu_hal::gles::adapter: Version: OpenGL ES 3.0 Mesa 27.0.0-devel
2026-11-03T09:07:33.196935Z DEBUG wgpu_hal::gles::adapter: SL version: OpenGL ES GLSL ES 3.00
2026-11-03T09:07:33.196948Z DEBUG wgpu_hal::gles::adapter: Supported GL Extensions: {
    "GL_OES_surfaceless_context",
2026-11-03T09:07:33.197454Z  INFO bevy_render::renderer: AdapterInfo { name: "Vivante GC7000 rev 6204", vendor: 65541, device: 0, device_type: Other, device_pci_bus_id: "", driver: "", driver_info: "O
thread 'Compute Task Pool (1)' (155623) panicked at /home/jack/.cargo/git/checkouts/bevy-50d7e162b728c6c6/ae61521/crates/bevy_render/src/view/window/mod.rs:913:13:
internal error: entered unreachable code: Fallback system failed to choose present mode. This is a bug. Mode: Fifo, Options: []
```

**attempt-02-wgpu-vulkan-backend**
```
2026-11-03T09:07:37.432841Z  WARN bevy_render::renderer: The selected adapter is using a driver that only supports software rendering. This is likely to be very slow. See https://bevy.org/learn/errors
thread 'main' (155652) panicked at /home/jack/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/wgpu-hal-30.0.1/src/lib.rs:494:5:
```

