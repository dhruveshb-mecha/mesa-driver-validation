# Extended GPU validation report

- Mesa: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`; kernel 7.1.5-0.mecha.202608260642.fc44.aarch64; Chromium 156.0.8078.47 Built from source for Fedora release 44 (Forty Four)
- Date: 2026-11-03 15:19 (board clock, no RTC); phases: native

## 1. Native wgpu examples (GL backend on Vivante via etnaviv) — 17/24 ran without panic

Windowed examples run 12 s then are stopped by timeout (rc 124 = healthy); headless ones exit by themselves (rc 0).

| Example | Result | rc | avg FPS | note |
|---|---|---|---|---|
| hello_triangle | PASS | 124 | - |  |
| cube | PASS | 124 | 50.6 |  |
| boids | FAIL | 101 | - | thread 'main' (164968) panicked at examples/features/src/framework.rs:305:14: |
| shadow | PASS | 124 | 15.4 |  |
| skybox | PASS | 124 | 45.4 |  |
| water | FAIL | 101 | - | [2026-11-03T09:46:50.754Z ERROR wgpu_core::error] Handling wgpu errors as fatal by default |
| msaa_line | PASS | 124 | 47.9 |  |
| mipmap | PASS | 124 | 35.6 |  |
| render_to_texture | PASS | 0 | - |  |
| multiple_render_targets | PASS | 124 | 32.4 |  |
| texture_arrays | FAIL | 101 | - | thread 'main' (165167) panicked at examples/features/src/utils.rs:226:24: |
| storage_texture | PASS | 0 | - |  |
| stencil_triangles | PASS | 124 | 50.5 |  |
| srgb_blend | PASS | 124 | 50.5 |  |
| uniform_values | FAIL | 101 | - | thread 'main' (165252) panicked at examples/features/src/uniform_values/mod.rs:141:14: |
| render_with_compute | FAIL | 101 | - | thread 'main' (165258) panicked at examples/features/src/framework.rs:305:14: |
| conservative_raster | FAIL | 101 | - | thread 'main' (165262) panicked at examples/features/src/utils.rs:226:24: |
| hello_workgroups | PASS | 0 | - |  |
| hello_synchronization | PASS | 0 | - |  |
| repeated_compute | PASS | 0 | - |  |
| big_compute_buffers | PASS | 124 | - |  |
| ray_aabb_compute | FAIL | 101 | - | thread 'main' (165352) panicked at examples/features/src/utils.rs:226:24: |
| timestamp_queries | PASS | 0 | - |  |
| error_scope | PASS | 0 | - |  |

### bunnymark scaling

| Backend | Bunnies | avg FPS | Result |
|---|---|---|---|
| gl | 100 | 43.8 | PASS |
| gl | 500 | 22.7 | PASS |
| gl | 2000 | 8.4 | PASS |
| vulkan (llvmpipe, CPU) | 100 | 31.7 | PASS |
| vulkan (llvmpipe, CPU) | 500 | 9.6 | PASS |

Raw logs, screenshots (`shot-*.png`) and `results.json` are in `/home/mecha/benchmarks/reports/full-validation-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-151602/`.
