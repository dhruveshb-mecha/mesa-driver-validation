# Real Flutter apps (standard GTK embedder) — build on the laptop, run on the Comet
The Mechanix apps use the eLinux embedder and are *not* what we test here.  `gpu_bench/` is a plain Flutter Linux (GTK) app
built with the stock Flutter SDK; it uses Impeller's OpenGL ES backend through GTK3/EGL on the Comet's Mesa.

* `build-arm64.sh` — one-time setup + build (details inside).  Needs: x64 Linux laptop, clang, cmake, ninja, aarch64 binutils,
  `apt-get download qemu-user` (no root needed), ssh access to the Comet (for a sysroot copy).
* Why the extra steps: Flutter refuses x64→arm64 cross builds (flutter/flutter#74929) because no x64-hosted arm64 `gen_snapshot`
  is published.  We run the official arm64 `gen_snapshot` under qemu-user and remove that one check in the tool.
* Run on the board with `GDK_BACKEND=wayland GDK_GL=gles ./gpu_bench SCENE [N] [SECONDS]`.  Without `GDK_GL=gles` GTK3 prints
  `Failed to create OpenGL context: Unable to create a GL context` and nothing is drawn.

## demo_counter
Stock `flutter create` counter app. Build: `APP=demo_counter bash build-arm64.sh`, copy `build/linux/arm64/release/bundle/` to `~/flutter-apps/demo_counter/`
on the Comet. Needs `GDK_GL=gles` (see harness tests `toolkit.flutter-demo.counter-{gles,default}`).
