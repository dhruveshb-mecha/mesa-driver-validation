# Case index

| case | verdict | attempts |
|---|---|---|
| **1. GPU hangs (kernel `recover hung GPU!`)** | | |
| [`gtk4-path_text-gl-renderer-gpu-hang`](1-gpu-hangs/gtk4-path_text-gl-renderer-gpu-hang/README.md) | GPU HANG | 5 |
| [`supertuxkart-deferred-lighting-gpu-hang`](1-gpu-hangs/supertuxkart-deferred-lighting-gpu-hang/README.md) | GPU HANG | 2 |
| [`qt-quick3d-gpu-hang-with-gl33-override`](1-gpu-hangs/qt-quick3d-gpu-hang-with-gl33-override/README.md) | GPU HANG | 3 |
| [`qt-quick3d-gpu-hang-on-gles-qt-without-override`](1-gpu-hangs/qt-quick3d-gpu-hang-on-gles-qt-without-override/README.md) | GPU HANG | 1 |
| [`gtk4-shadertoy-gpu-hang-both-renderers`](1-gpu-hangs/gtk4-shadertoy-gpu-hang-both-renderers/README.md) | GPU HANG (needs triage) | 2 |
| **2. Functional failures and non-Mesa findings** | | |
| [`gtk4-badapple-nv12-dmabuf-import-error`](2-functional-failures/gtk4-badapple-nv12-dmabuf-import-error/README.md) | FAIL | 2 |
| [`gles3-msaa-4x-rgba16f-framebuffer-unsupported`](2-functional-failures/gles3-msaa-4x-rgba16f-framebuffer-unsupported/README.md) | FAIL | 2 |
| [`webgl2-conformance-ext-color-buffer-float-and-sync-timeout`](2-functional-failures/webgl2-conformance-ext-color-buffer-float-and-sync-timeout/README.md) | FAIL | 2 |
| [`gtk4-gl-renderer-sigsegv-in-dri_drawable_bind_images`](2-functional-failures/gtk4-gl-renderer-sigsegv-in-dri_drawable_bind_images/README.md) | CRASH | 3 |
| [`gtk4-layoutmanager2-gl-abort-cairo-assertion`](2-functional-failures/gtk4-layoutmanager2-gl-abort-cairo-assertion/README.md) | FAIL (probably not Mesa) | 1 |
| [`flutter-gtk3-embedder-no-gl-context-without-gdk-gl-gles`](2-functional-failures/flutter-gtk3-embedder-no-gl-context-without-gdk-gl-gles/README.md) | FAIL (config) | 2 |
| [`gamescope-glmark2-runs-on-llvmpipe-not-the-gpu`](2-functional-failures/gamescope-glmark2-runs-on-llvmpipe-not-the-gpu/README.md) | MISLEADING PASS | 1 |
| [`wgpu-native-examples-7-of-24-fail-no-compute-and-missing-features`](2-functional-failures/wgpu-native-examples-7-of-24-fail-no-compute-and-missing-features/README.md) | EXPECTED ES 3.0 LIMITS | 1 |
| [`bevy-main-gl-surfaceless-instance-panic`](2-functional-failures/bevy-main-gl-surfaceless-instance-panic/README.md) | FAIL (not Mesa) | 2 |
| **3. Informational** | | |
| [`vulkan-is-llvmpipe-cpu-only`](3-informational/vulkan-is-llvmpipe-cpu-only/README.md) | INFO | 4 |
| **4. Passing runs (control data: what works)** | | |
| [`core-gles3-context-and-render-target-probes`](4-passing/core-gles3-context-and-render-target-probes/README.md) | PASS | 4 |
| [`core-weston-simple-egl`](4-passing/core-weston-simple-egl/README.md) | PASS | 2 |
| [`benchmark-glmark2-es2-fullscreen-and-windowed`](4-passing/benchmark-glmark2-es2-fullscreen-and-windowed/README.md) | PASS | 2 |
| [`soak-glmark2-10-minute-loop`](4-passing/soak-glmark2-10-minute-loop/README.md) | PASS | 1 |
| [`game-supertuxkart-legacy-lighting-ok`](4-passing/game-supertuxkart-legacy-lighting-ok/README.md) | PASS | 3 |
| [`gtk4-widget-factory-node-editor-text-editor-gl-and-cairo`](4-passing/gtk4-widget-factory-node-editor-text-editor-gl-and-cairo/README.md) | PASS | 8 |
| [`gtk4-stock-demo-sweep-111-demos-gl-vs-cairo`](4-passing/gtk4-stock-demo-sweep-111-demos-gl-vs-cairo/README.md) | PASS (3 exceptions) | 2 |
| [`gtk4-own-demo-widgets-and-glarea-gl-vs-cairo`](4-passing/gtk4-own-demo-widgets-and-glarea-gl-vs-cairo/README.md) | PASS | 4 |
| [`flutter-mechanix-apps-5-real-apps`](4-passing/flutter-mechanix-apps-5-real-apps/README.md) | PASS | 9 |
| [`flutter-gpu_bench-17-scenes-impeller-gles-with-gdk-gl-gles`](4-passing/flutter-gpu_bench-17-scenes-impeller-gles-with-gdk-gl-gles/README.md) | PASS | 2 |
| [`flutter-official-animations-sample-driven-with-pointer`](4-passing/flutter-official-animations-sample-driven-with-pointer/README.md) | PASS | 1 |
| [`flutter-stock-counter-app-with-gdk-gl-gles`](4-passing/flutter-stock-counter-app-with-gdk-gl-gles/README.md) | PASS | 1 |
| [`wgpu-native-cube-bunnymark-gl`](4-passing/wgpu-native-cube-bunnymark-gl/README.md) | PASS | 3 |
| [`wgpu-iced-master-wgpu30-gl`](4-passing/wgpu-iced-master-wgpu30-gl/README.md) | PASS | 2 |
| [`browser-chromium-webgl-validation-and-aquarium`](4-passing/browser-chromium-webgl-validation-and-aquarium/README.md) | PASS | 4 |
| [`browser-firefox-webgl2-and-aquarium`](4-passing/browser-firefox-webgl2-and-aquarium/README.md) | PASS | 4 |
| [`browser-webgl-report-and-threejs-example-pages`](4-passing/browser-webgl-report-and-threejs-example-pages/README.md) | PASS (1 known failure) | 2 |
| **5. Performance data** | | |
| [`gtk4-renderer-matrix-gl-vs-cairo-16-scenes`](5-performance/gtk4-renderer-matrix-gl-vs-cairo-16-scenes/README.md) | DATA | 2 |
| [`chromium-vice-city-webgl-game`](5-performance/chromium-vice-city-webgl-game/README.md) | DATA | 2 |
