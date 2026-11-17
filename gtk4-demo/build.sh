#!/bin/bash
# Cross-compile the GTK4 demo for the Comet (arm64) on an x86 laptop. Needs: aarch64-linux-gnu-gcc, podman.
# Sysroot: arm64 gtk4-devel/glib2-devel unpacked (not executed) by an x86 Fedora 44 container.
set -euo pipefail
S=${S:-$HOME/gtk4-sysroot}; HERE=$(cd "$(dirname "$0")" && pwd)
if [ ! -d $S/usr/include/gtk-4.0 ]; then
  mkdir -p $S; podman run --rm --platform linux/amd64 -v $S:/sysroot:Z docker.io/library/fedora:44 bash -c \
   'dnf -y --use-host-config --forcearch=aarch64 --installroot=/sysroot --releasever=44 --setopt=tsflags=noscripts --setopt=install_weak_deps=False install gtk4-devel glib2-devel libepoxy-devel'
  podman unshare chown -R 0:0 $S
fi
export PKG_CONFIG_LIBDIR=$S/usr/lib64/pkgconfig:$S/usr/share/pkgconfig PKG_CONFIG_SYSROOT_DIR=$S
aarch64-linux-gnu-gcc -O2 -o $HERE/gtk4_demo $HERE/demo.c --sysroot=$S $(pkg-config --cflags --libs gtk4 epoxy) -lm \
  -Wl,-rpath-link=$S/usr/lib64 -Wl,--unresolved-symbols=ignore-in-shared-libs
file $HERE/gtk4_demo
