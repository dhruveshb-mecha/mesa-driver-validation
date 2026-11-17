# gtk4-demo — standard GTK4 C demo app

`demo.c`, cross-built on the x86 laptop (`./build.sh`; arm64 gtk4-devel unpacked into `~/gtk4-sysroot` by an x86 Fedora 44 podman container,
nothing arm64 is executed). Copy `gtk4_demo` to `~/gtk4-demo/` on the Comet.

    GSK_RENDERER=gl|cairo ./gtk4_demo widgets 10   # header bar, button, entry, switch, scale, progress bar, spinner, scrolling 10000-row GtkListView
    GSK_RENDERER=gl|cairo ./gtk4_demo glarea  10   # GtkGLArea, GLES 3.0 shaders, 60 rotating lit quads/cubes (the cube mesh is rough: this is a draw-load, not a modelling demo)

Prints `GTK4DEMO {"mode","renderer","gl","frames","fps","size"}`. Harness tests: `toolkit.gtk4.demo-{widgets,glarea}-{cairo,gl}`.
