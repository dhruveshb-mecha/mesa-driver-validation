# Extended GPU validation report

- Mesa: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`; kernel 7.1.5-0.mecha.202608260642.fc44.aarch64; Chromium 156.0.8078.47 Built from source for Fedora release 44 (Forty Four)
- Date: 2026-11-03 14:40 (board clock, no RTC); phases: aquarium

## 4. WebGL Aquarium (default 500 fish, full window)

| Mode | avg FPS | samples |
|---|---|---|
| GPU | 9.7 | [1.0, 6.0, 11.0, 10.0, 10.0, 8.0, 9.0, 10.0, 9.0, 10.0, 10.0] |
| CPU (SwiftShader) | 1.0 | [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] |

Raw logs, screenshots (`shot-*.png`) and `results.json` are in `/home/mecha/benchmarks/reports/full-validation-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-143741/`.
