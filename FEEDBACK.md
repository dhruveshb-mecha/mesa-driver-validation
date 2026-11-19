# GLES 3.0 validation findings: Mesa 27.0.0~devel on Mecha Comet (i.MX8MP, GC7000UL rev 6204)

Fedora aarch64, sway/Wayland, single board. Sections 1 to 5 are from the first run on Mesa git `7b4b394` (kernel 7.1.5). Section 6 lists later runs on other Mesa builds. Every item points at a folder under `cases/` that holds the logs and screenshots.

## 1. Issues found

| # | Issue | What happens | Case |
|---|-------|--------------|------|
| 1 | GTK4 `path_text`, GL renderer only | kernel `recover hung GPU!`, window stays black; Cairo renderer is fine | `gtk4-path_text-gl-renderer-gpu-hang` |
| 2 | SuperTuxKart deferred lighting (native ES 3.0, no overrides) | hang at track load, 3 of 3 attempts | `supertuxkart-deferred-lighting-gpu-hang` |
| 3 | 4x MSAA RGBA16F renderbuffer | `GL_FRAMEBUFFER_UNSUPPORTED`, no GL error raised; RGBA8 passes | `gles3-msaa-4x-rgba16f-framebuffer-unsupported` |
| 4 | WebGL2 conformance sample | `ext-color-buffer-float` fails and `sync-webgl-specific` times out in both browsers | `webgl2-conformance-ext-color-buffer-float-and-sync-timeout` |
| 5 | GTK4 GL renderer, text scene | SIGSEGV in `dri_drawable_bind_images` | `gtk4-gl-renderer-sigsegv-in-dri_drawable_bind_images` |
| 6 | Qt Quick 3D examples | GPU hangs (with the GL 3.3 override on Fedora's Qt) | `qt-quick3d-gpu-hang-with-gl33-override` |
| 7 | GTK4 `shadertoy` | GPU hang with both renderers | `gtk4-shadertoy-gpu-hang-both-renderers` |
| 8 | wgpu native examples | 7 of 24 fail on GL (compute needs ES 3.1, some features missing) | `wgpu-native-examples-7-of-24-fail-no-compute-and-missing-features` |

## 2. Per-issue detail

### 1. GTK4 `path_text` hang
- Repro: `GSK_RENDERER=gl gtk4-demo --run path_text` (gtk4-devel-tools 4.22.5), or `python3 scripts/gtk4_demo_sweep.py gl /tmp/out 7 '^path_text$'`.
- Observed: `etnaviv-gpu 38000000.gpu: recover hung GPU!` twice in the dedicated repro and twice in the full GL sweep; window left black. In the Cairo sweep `path_text` does not hang and renders correctly. The board recovers.
- Evidence: `cases/1-gpu-hangs/gtk4-path_text-gl-renderer-gpu-hang/` (kernel events, black-window screenshot in `attempt-01-*/artifacts/path_text.png`, Cairo control screenshot in `attempt-03-*/artifacts/path_text.png`).

### 2. SuperTuxKart deferred lighting hang
- Repro: `supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40`
- Observed: hang at track load with `enable_dynamic_lights=true` (2 harness runs in the evidence, 3 of 3 in manual attempts). With `false`: 98.97 fps average, no kernel messages. The context reports `OpenGL ES 3.0 Mesa 27.0.0-devel`, so no override is involved. Shadows, SSAO, MLAA, motion blur and bloom were already off.
- Evidence: `cases/1-gpu-hangs/supertuxkart-deferred-lighting-gpu-hang/` (hang), `cases/4-passing/game-supertuxkart-legacy-lighting-ok/` (control, with screenshot).

### 3. 4x MSAA RGBA16F renderbuffer
- Repro: `scripts/gles3_probe.py` (in this repo), checks `msaa_4x_resolve_content_rgba16f[_with_depth]`.
- Observed: `glRenderbufferStorageMultisample(..., 4, GL_RGBA16F, ...)` raises no error, but the FBO is `GL_FRAMEBUFFER_UNSUPPORTED` (0x8cdd). RGBA8 passes. In three.js `webgl_multisampled_renderbuffers` one half of the page is blank.
- Evidence: `cases/2-functional-failures/gles3-msaa-4x-rgba16f-framebuffer-unsupported/`.

### 4. WebGL2 conformance
- 113-test sample: Chromium 109 pass / 3 fail / 1 timeout, Firefox 110 / 2 / 1.
- Both browsers fail `ext-color-buffer-float.html` and time out on `sync-webgl-specific.html`.
- Chromium only: `read-pixels-from-fbo-test.html` (INVALID_OPERATION on readPixels, wrong colours) and `khr-parallel-shader-compile.html`. Firefox only: `readpixels-16gb-wasm-memory.html`.
- Evidence: `cases/2-functional-failures/webgl2-conformance-ext-color-buffer-float-and-sync-timeout/` (per-test results for both browsers).

### 5. GTK4 GL SIGSEGV
- Repro: `GDK_BACKEND=wayland GSK_RENDERER=gl python3 scripts/gtk4_bench.py text 30 4`. Crashes 4 of 4 at n=30. Cairo is fine.
- Stack (every core): `dri_drawable_bind_images <- dri2_allocate_textures <- dri_st_framebuffer_validate <- st_update_framebuffer_state <- st_Clear <- gsk_gpu_render_pass_op_gl_command`. Core dumps are available.
- Does not crash: a plain window up to 3000x620, per-frame resize of the requested size.
- Evidence: `cases/2-functional-failures/gtk4-gl-renderer-sigsegv-in-dri_drawable_bind_images/` (3 attempts, stack in the case README).

### 6. Qt Quick 3D hangs
- Fedora's Qt 6 has no GLES backend, so this test uses `MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330`. Four to five hang events per attempt in three attempts.
- Evidence: `cases/1-gpu-hangs/qt-quick3d-gpu-hang-with-gl33-override/` (kernel events, per-example screenshots). The same examples were run on a Qt built for OpenGL ES without any override in "Later runs" at the end of this file.

### 7. GTK4 `shadertoy` hang
- Observed: hangs with both the GL and the Cairo renderer.
- Evidence: `cases/1-gpu-hangs/gtk4-shadertoy-gpu-hang-both-renderers/`.

### 8. wgpu compute
- `boids`, `render_with_compute`, `uniform_values`: `max_compute_workgroups_per_dimension requested 65535, allowed 0`.
- `texture_arrays`, `conservative_raster`, `ray_aabb_compute`: required wgpu features absent. `water`: wgpu validation error (not examined).
- Evidence: `cases/2-functional-failures/wgpu-native-examples-7-of-24-fail-no-compute-and-missing-features/`.

## 3. Things that work
- ES 3.0 context creation and rendering in GTK4, Qt, Chromium, Firefox, iced (wgpu 30 GL), Flutter (Impeller GLES, 17 of 17 scenes, no hangs).
- 110 of 111 stock gtk4-demo examples stay alive under the GL renderer; `gears` and `glarea` are fine.
- 17 of 24 wgpu native examples run on GL.
- The harness reported OK for gamescope + glmark2 and for the Vulkan-based tests, but those ran on llvmpipe (CPU), so they are not GPU passes.
- Performance, for scale: Quick 3D with the override ran at 24.7 fps against 5.9 fps on llvmpipe. Flutter is slowest on gradients, blur and opacity layers (5 to 13 fps). GTK4 GL is slower than Cairo in 14 of 16 scenes.

## 4. Evidence in this repo
- One folder per case under `cases/` (index: `cases/INDEX.md`). Each attempt folder has the command, stdout, stderr, kernel journal, etnaviv-only kernel lines and screenshots where taken.
- Passing runs are kept as controls under `cases/4-passing/` (for example the SuperTuxKart legacy-lighting run and the GTK4 Cairo control for `path_text`).
- The scripts used by the commands are in `scripts/`. The board's environment (Mesa package, kernel, GPU probe) is in `environment/`.
- Not included: raw per-test dumps of runs that are not cited above, and the 98 MB full-logging Chromium Vice City log.

## 5. Real-application track (`app-benchmarks/`)
Ten mainstream GTK4 apps (3 renderer modes x 2 attempts) and four real Flutter apps were run on the same Mesa build. Details, logs and screenshots are in `app-benchmarks/`. There was no GPU hang, crash or software fallback in 76 runs. Three observations:

| # | Observation | Evidence |
|---|---|---|
| A | GNOME Text Editor: GL renderer 4-8 fps vs Cairo 34 fps scrolling a 30000-line file (typing 5 vs 24 fps). The default renderer is the GL one. Large-image zoom (Loupe) is the other way round: GL about 5x faster. | `app-benchmarks/gtk4-apps/text-editor/`, `loupe/` |
| B | Flutter (GTK3) cannot create a GL context without `GDK_GL=gles`; older engines fall back to CPU rendering without a message, the newer one draws nothing. | `app-benchmarks/flutter-apps/localsend/`, `ente-auth/` (default vs gles attempts) |
| C | Epiphany (WebKitGTK 6) loads no page at all, and the GPU toggles do not change it. WebGL via WebKit was not tested. | `app-benchmarks/gtk4-apps/epiphany/` |

## 6. Later runs on other Mesa builds
- **`mr46144` (git `8838d84`), 2026-11-13 to 11-17:** Chromium NV12 video, GTK4 apps and Qt apps. See `chromium-nv12-mr46144/`, `gtk4-apps-mr46144-2026-11-17/` and `qt-apps-mr46144-2026-11-17/`.
- **Mesa main build (git `6f23942285e`), 2026-11-19:**
  - `path_text` still hangs the GPU with the GL renderer and does not with Cairo: attempts 04 and 05 in `cases/1-gpu-hangs/gtk4-path_text-gl-renderer-gpu-hang/`.
  - Four of the seven Qt Quick 3D examples hang the GPU on a Qt built for OpenGL ES without any override: `cases/1-gpu-hangs/qt-quick3d-gpu-hang-on-gles-qt-without-override/`. Logs of all Qt apps are in `qt-apps-main-6f23942285e-2026-11-19/`.
  - GTK4's `badapple` demo logs a Mesa error from `etna_resource_from_handle` for each NV12 dmabuf frame with the GL renderer, and none with `GDK_DISABLE=dmabuf`: `cases/2-functional-failures/gtk4-badapple-nv12-dmabuf-import-error/`.
