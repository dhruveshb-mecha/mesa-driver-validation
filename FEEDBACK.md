# GLES 3.0 validation feedback: Mesa 27.0.0~devel (7b4b394) on Mecha Comet (i.MX8MP, GC7000UL rev 6204)

Kernel 7.1.5, Fedora 44 aarch64, sway/Wayland. Single board, single Mesa build. Every item below points at a folder under `cases/` in this repo that holds the logs and screenshots for it. DRAFT.

## 1. What to look into (priority order)

| # | Issue | Type | Confidence it is a driver bug | What to look into |
|---|-------|------|-------------------------------|-----|
| 1 | GPU hang: GTK4 `path_text` (GL renderer only) | kernel "recover hung GPU", black window | High: small scene, no heavy shader, Cairo is fine | Reproduce, capture an etnaviv command stream, identify the offending op |
| 2 | GPU hang: SuperTuxKart deferred lighting (native ES 3.0, no overrides) | hang at track load, 3/3 | High: only `enable_dynamic_lights=true` triggers it | Same; bisect which pass/feature (MRT, fp16 RT, UBO, instancing) |
| 3 | `GL_FRAMEBUFFER_UNSUPPORTED` for 4x MSAA RGBA16F renderbuffer | missing feature | High: RGBA8 MSAA passes, no GL error raised | Check whether GC7000UL is meant to support it. If not, the extension should not claim it |
| 4 | WebGL2 conformance: `ext-color-buffer-float` fails, `sync-webgl-specific` times out | conformance | Medium to high: same in Chromium (ANGLE) and Firefox (native) | Check float RT support and fence/sync objects |
| 5 | SIGSEGV in `dri_drawable_bind_images` (GTK4 GL renderer, text scene) | userspace crash | Medium: deterministic, window-system path, trigger unknown | Analyse the stack; core dumps are available |
| 6 | GPU hang: Qt Quick 3D examples | hang | **Low until retested**: needs `MESA_GL_VERSION_OVERRIDE=3.3` (unsupported) | Retest on a GLES Qt build first (our side) |
| 7 | GPU hang: GTK4 `shadertoy` (both renderers) | hang | Low: heavy raymarching shader, may just be a watchdog timeout | Check whether the kernel hang timeout is expected to trip here |
| 8 | wgpu native examples: 7 of 24 fail on GL (compute needs ES 3.1, some features missing) | feature gap | Expected for ES 3.0 | Check whether ES 3.1 compute is feasible on GC7000UL |

Not Mesa problems: Bevy present-mode panic, `layoutmanager2` abort (cairo), iced 0.14 BadMatch.

## 2. Per-issue detail

### 1. GTK4 `path_text` hang (best candidate)
- Repro: `GSK_RENDERER=gl gtk4-demo --run path_text` (gtk4-devel-tools 4.22.5), or
  `python3 scripts/gtk4_demo_sweep.py gl /tmp/out 7 '^path_text$'`
- Observed: `etnaviv-gpu 38000000.gpu: recover hung GPU!` twice in the dedicated repro and twice in the full GL sweep; window left black. In the Cairo sweep `path_text` does not hang and renders correctly.
- Established: GL-renderer-specific, small scene, board recovers.
- Unknown: which GSK GL op (path/text tessellation, stencil, clip) emits the bad command stream.
- Next experiment (ours): `GSK_DEBUG=` renderer tracing plus `ETNA_MESA_DEBUG` cmdstream dump for the failing frame.
- Evidence: `cases/1-gpu-hangs/gtk4-path_text-gl-renderer-gpu-hang/` (kernel events, black-window screenshot in `attempt-01-*/artifacts/path_text.png`, Cairo control screenshot in `attempt-03-*/artifacts/path_text.png`).

### 2. SuperTuxKart deferred lighting hang
- Repro: `supertuxkart --no-start-screen --track=lighthouse --numkarts=4 --profile-time=40`
- Observed: hang at track load with `enable_dynamic_lights=true` (2 harness runs in the evidence, 3/3 in manual attempts). With `false`: 98.97 fps average, no kernel messages.
  Context reports `OpenGL ES 3.0 Mesa 27.0.0-devel`, so no override is involved.
- Established: the deferred path is the trigger. Shadows, SSAO, MLAA, motion blur and bloom were already off.
- Unknown: which feature in the deferred path.
- Evidence: `cases/1-gpu-hangs/supertuxkart-deferred-lighting-gpu-hang/` (hang), `cases/4-passing/game-supertuxkart-legacy-lighting-ok/` (control, with screenshot).

### 3. 4x MSAA RGBA16F renderbuffer
- Evidence: `cases/2-functional-failures/gles3-msaa-4x-rgba16f-framebuffer-unsupported/`.
- Repro: `scripts/gles3_probe.py` (in this repo), checks `msaa_4x_resolve_content_rgba16f[_with_depth]`.
- Observed: `glRenderbufferStorageMultisample(..., 4, GL_RGBA16F, ...)` raises no error, but the FBO is
  `GL_FRAMEBUFFER_UNSUPPORTED` (0x8cdd). RGBA8 passes. User-visible: three.js `webgl_multisampled_renderbuffers` shows a blank half.
- Question: ES 3.0 requires color-renderable formats to support at least 4 samples, and RGBA16F becomes color-renderable via
  EXT_color_buffer_float. Is the gap intended on GC7000UL?

### 4. WebGL2 conformance
- Evidence: `cases/2-functional-failures/webgl2-conformance-ext-color-buffer-float-and-sync-timeout/` (per-test results for both browsers).
- 113-test sample: Chromium 109 pass / 3 fail / 1 timeout, Firefox 110 / 2 / 1.
- Both fail `ext-color-buffer-float.html` and time out on `sync-webgl-specific.html`. The two browsers share a driver but not a GL stack
  (ANGLE vs native), which points at Mesa.
- Chromium only: `read-pixels-from-fbo-test.html` (INVALID_OPERATION on readPixels, wrong colours) and `khr-parallel-shader-compile.html`.
  Firefox only: `readpixels-16gb-wasm-memory.html` (probably a memory limit).

### 5. GTK4 GL SIGSEGV
- Evidence: `cases/2-functional-failures/gtk4-gl-renderer-sigsegv-in-dri_drawable_bind_images/` (3 attempts, stack in the case README).
- Repro: `GDK_BACKEND=wayland GSK_RENDERER=gl python3 scripts/gtk4_bench.py text 30 4`. Crashes 4/4 at n=30. Cairo is fine.
- Stack (every core): `dri_drawable_bind_images <- dri2_allocate_textures <- dri_st_framebuffer_validate <- st_update_framebuffer_state <- st_Clear <- gsk_gpu_render_pass_op_gl_command`.
- Ruled out: plain large windows, per-frame resize of the requested size. Not ruled out: window size changing as many labels move in a Gtk.Fixed.
- To look into: can this be reproduced from the stack alone? Core dumps are available; a smaller GTK reproducer would help.

### 6 and 7. Hangs with caveats
State the caveats up front or the reports will be dismissed.
- Qt: Fedora Qt6 has no GLES backend, so the test uses `MESA_GL_VERSION_OVERRIDE=3.3 MESA_GLSL_VERSION_OVERRIDE=330`. Four to five hang events per attempt in three attempts.
  Evidence: `cases/1-gpu-hangs/qt-quick3d-gpu-hang-with-gl33-override/` (kernel events, per-example screenshots).
- shadertoy: hangs under both renderers, so the cause is the GLES shader inside the GtkGLArea, not GSK.
  To check: is a hang on a long-running shader expected, and what is the timeout?
  Evidence: `cases/1-gpu-hangs/gtk4-shadertoy-gpu-hang-both-renderers/`.

### 8. wgpu compute
- Evidence: `cases/2-functional-failures/wgpu-native-examples-7-of-24-fail-no-compute-and-missing-features/`.
- `boids`, `render_with_compute`, `uniform_values`: `max_compute_workgroups_per_dimension requested 65535, allowed 0`. Needs ES 3.1.
  `texture_arrays`, `conservative_raster`, `ray_aabb_compute`: required wgpu features absent. `water`: wgpu validation error (not examined).

## 3. Things that work (
- ES 3.0 context creation and rendering in GTK4, Qt, Chromium, Firefox, iced (wgpu 30 GL), Flutter (Impeller GLES, 17/17 scenes, no hangs).
- 110/111 stock gtk4-demo examples alive under the GL renderer; `gears` and `glarea` are fine.
- 17 of 24 wgpu native examples run on GL.
- **Not working although the harness said OK:** gamescope + glmark2 (ran on llvmpipe, a CPU score), and any Vulkan-based
  test (llvmpipe). Do not count them as GPU passes.
- Performance, for scale: Quick 3D with the override is ~4x faster than llvmpipe (24.7 vs 5.9 fps).
  Flutter is weakest on gradients, blur and opacity layers (5-13 fps). GTK4 GL is slower than Cairo in 14 of 16 scenes.


## 4. Evidence in this repo
- One folder per case under `cases/` (index: `cases/INDEX.md`). Each attempt folder has the command, stdout, stderr, kernel journal, etnaviv-only kernel lines and screenshots where taken.
- Passing runs are kept as controls under `cases/4-passing/` (for example the SuperTuxKart legacy-lighting run and the GTK4 Cairo control for `path_text`).
- Repro scripts used by the commands are in `scripts/`. Environment of the board (Mesa package, kernel, GPU probe) is in `environment/`.
- Not included: raw per-test dumps of runs that are not cited above, and the 98 MB full-logging Chromium Vice City log.

## 5. Addons: real-application track (`app-benchmarks/`)
Ten mainstream GTK4 apps (3 renderer modes x 2 attempts) and four real Flutter apps were run on the same Mesa build; details, logs and screenshots in `app-benchmarks/`. No GPU hang, crash or software fallback in 76 runs. Three items to look into:

| # | Observation | Evidence | What to look into |
|---|---|---|---|
| A | GNOME Text Editor: GL renderer 4-8 fps vs Cairo 34 fps scrolling a 30000-line file (typing 5 vs 24 fps). Default renderer is the GL one. Large-image zoom (Loupe) is the opposite: GL ~5x faster. | `app-benchmarks/gtk4-apps/text-editor/`, `loupe/` | Text-heavy GL content (glyph atlas upload, many small draws); relate to the 14-of-16 GL-slower scenes in the synthetic matrix |
| B | Flutter (GTK3) cannot create a GL context without `GDK_GL=gles`; older engines silently fall back to CPU rendering, the newer one draws nothing | `app-benchmarks/flutter-apps/localsend/`, `ente-auth/` (default vs gles attempts) | Set `GDK_GL=gles` for the session; check why GTK3 on this Mesa cannot create its default GL context |
| C | Epiphany (WebKitGTK 6) loads no page at all, GPU toggles do not change it | `app-benchmarks/gtk4-apps/epiphany/` | WebKit-side check; not shown to be Mesa. WebGL via WebKit is untested |
