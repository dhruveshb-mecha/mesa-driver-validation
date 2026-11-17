#!/bin/bash
# Cross-build flutter/gpu_bench for the Comet (linux-arm64) on an x64 Linux laptop.  Idempotent; see README.md.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=${W:-$HOME/flutter-build}; COMET=${COMET:-mecha@comet.local}; FLUTTER_VER=${FLUTTER_VER:-3.47.9}
mkdir -p "$W"; cd "$W"
# 1. Flutter SDK (x64)
[ -d flutter ] || { curl -sSL -o flutter.tar.xz https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VER}-stable.tar.xz; tar -xf flutter.tar.xz; }
export PATH=$W/flutter/bin:$PATH FLUTTER_SUPPRESS_ANALYTICS=true CI=true
HASH=$(cat flutter/bin/internal/engine.version)
# 2. arm64 sysroot copied from the board (headers + libs + pkg-config files + gcc runtime + loader)
if [ ! -d sysroot/usr/include ]; then
  mkdir -p sysroot/usr/lib64 sysroot/usr/lib sysroot/usr/share
  rsync -a --links $COMET:/usr/include sysroot/usr/;  rsync -a --links $COMET:/usr/lib64/ sysroot/usr/lib64/
  rsync -a --links $COMET:/usr/lib/gcc sysroot/usr/lib/; rsync -a --links $COMET:/usr/share/pkgconfig sysroot/usr/share/
  rsync -aL $COMET:/usr/lib/ld-linux-aarch64.so.1 sysroot/usr/lib/; chmod -R u+w sysroot
  python3 - <<PY
import os; r=os.path.abspath('sysroot')
for d,ds,fs in os.walk(r):
    for n in fs+ds:
        p=os.path.join(d,n)
        if os.path.islink(p) and os.readlink(p).startswith('/'): t=os.readlink(p); os.remove(p); os.symlink(os.path.relpath(r+t,d),p)
PY
  ln -sfn usr/lib64 sysroot/lib64; ln -sfn usr/lib sysroot/lib
fi
# 3. qemu-user (no root): run the arm64 gen_snapshot on x64
[ -x qemu/x/usr/bin/qemu-aarch64 ] || { mkdir -p qemu; (cd qemu; apt-get download qemu-user; dpkg-deb -x qemu-user_*.deb x); }
# 4. arm64 engine artifacts into the SDK cache + qemu wrapper for gen_snapshot
E=flutter/bin/cache/artifacts/engine; B=https://storage.googleapis.com/flutter_infra_release/flutter/$HASH
if [ ! -d $E/linux-arm64-release ]; then
  mkdir -p $E/linux-arm64 $E/linux-arm64-release $E/linux-arm64-profile
  for z in linux-arm64/artifacts.zip linux-arm64-release/linux-arm64-flutter-gtk.zip linux-arm64-profile/linux-arm64-flutter-gtk.zip; do
    curl -sSL -o /tmp/_e.zip $B/$z; unzip -oq /tmp/_e.zip -d $E/$(dirname $z); done
  for d in linux-arm64-release linux-arm64-profile; do mv $E/$d/gen_snapshot $E/$d/gen_snapshot.real
    printf '#!/bin/sh\nexec %s -L %s "$(dirname "$0")/gen_snapshot.real" "$@"\n' "$W/qemu/x/usr/bin/qemu-aarch64" "$W/sysroot" > $E/$d/gen_snapshot; chmod +x $E/$d/gen_snapshot; done
fi
# 5. remove the hard-coded x64->arm64 refusal in the tool, force snapshot rebuild
F=flutter/packages/flutter_tools/lib/src/commands/build_linux.dart
if grep -q "Cross-build from Linux x64 host to Linux arm64 target is not currently supported" $F; then
  python3 - <<PY
s=open("$F").read(); a=s.index("    // TODO(fujino): https://github.com/flutter/flutter/issues/74929"); b=s.index("      );\n    }\n",a)+len("      );\n    }\n")
open("$F","w").write(s[:a]+s[b:])
PY
  rm -f flutter/bin/cache/flutter_tools.snapshot flutter/bin/cache/flutter_tools.stamp
fi
# 6. build
S=$W/sysroot; export PKG_CONFIG_LIBDIR=$S/usr/lib64/pkgconfig:$S/usr/share/pkgconfig PKG_CONFIG_SYSROOT_DIR=$S PKG_CONFIG_PATH=
APP=${APP:-gpu_bench}   # any app dir next to this script, e.g. APP=demo_counter
cd "$HERE/$APP"
flutter build linux --release --target-platform linux-arm64 --target-sysroot $S
echo "bundle: $PWD/build/linux/arm64/release/bundle   (rsync to the Comet: ~/flutter-apps/$APP/)"
