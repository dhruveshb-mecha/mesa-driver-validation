# Flutter application track

Real Flutter Linux applications. Flutter's Linux embedder is **GTK3** (not GTK4) in every released SDK, so these exercise GTK3 + EGL on Mesa 27. Modes: `gles` = `GDK_GL=gles` (required), `default` = control without it.

| app | source | verdict | what stands out |
|---|---|---|---|
| [localsend](localsend/README.md) | Flathub aarch64 build 1.18.2 | PASS with `gles` | animated radar 28-30 fps; **`default` silently falls back to software rendering at the same fps** |
| [ente-auth](ente-auth/README.md) | built from source (4.4.27) | PASS with `gles` | **`default` draws nothing** (no software fallback in this engine) |
| [ricochlime](ricochlime/README.md) | Flathub aarch64 build 1.13.1 | PASS with `gles` | Flame game, 36-38 fps; software fallback in `default` reaches 34-35 fps |
| [firmware-updater](firmware-updater/README.md) | built from source (Canonical) | start-up only | waits for fwupd (not running), stops repainting |

Key point for the image: **GTK3 cannot create a GL context on this board unless `GDK_GL=gles` is set.** Apps built on older engines hide it behind a software fallback, which makes a CPU-rendered UI look like a GPU one.

Not run: **Fladder** (needs glibc 2.44, board has 2.43), **Spotube** (needs `webkit2gtk-4.1`, not on the board), **RustDesk** (not approved: remote-desktop tool that contacts public servers), **Ente Photos** (Electron, not Flutter).

Prebuilt Flathub bundles were extracted on the laptop and run against the board's own Mesa (the Flatpak runtime is not used). Sources built from scratch needed these laptop-side build workarounds (not board changes): a sysroot copied from the board plus Fedora `-devel` RPMs for libsecret, libcurl and Ayatana app-indicator, JNI headers with an empty `libjvm.so` stub, generated Rust bridge code, and three CMake tweaks; bundles also ship the Ayatana runtime libraries.
