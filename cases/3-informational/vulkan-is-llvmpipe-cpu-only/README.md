# The board has no Vulkan GPU driver: Vulkan is llvmpipe (CPU) only

**Verdict:** INFO

## What was run
`vulkaninfo` and every Vulkan-backed test (Chromium WebGPU, wgpu/bunnymark Vulkan, iced Vulkan, Bevy Vulkan).

## Result
Only `llvmpipe` is enumerated. WebGPU in Chromium runs on SwiftShader/llvmpipe (test expects `cpu-only`). iced without `WGPU_BACKEND=gl` silently picks Vulkan = llvmpipe. The harness marks `wgpu.bevy-eased-motion-vulkan` RAN_OK, but the adapter is llvmpipe, so it is a CPU result. wgpu bunnymark: Vulkan/llvmpipe 31.7 / 9.6 fps at 100 / 500 bunnies vs GL on the GPU 43.8 / 22.7.

## Why it matters
Any app that defaults to Vulkan (wgpu, Bevy, Flutter-Vulkan) runs on the CPU unless forced to GL. Worth a default in the image or a clear message.

## What to look into
None (Vivante has no Vulkan driver in Mesa).

## Command (as run on the Comet)
```
~/bin/validate-full webgpu
```
`scripts/...` and `~/gpu-test/scripts/...` in the command refer to the scripts in this repo's `scripts/` folder.

## Attempts

| folder | harness status | rc | duration (s) | GPU hangs in kernel log | SoC temp after (C) | Mesa driver debug logging |
|---|---|---|---|---|---|---|
| `attempt-01-chromium-webgpu-cpu-only` | RAN_OK | 0 | 220.5 | 0 | 83.0 | yes |
| `attempt-02-wgpu-bunnymark-vulkan-llvmpipe` | RAN_OK | -15 | 20.3 | 0 | 84.0 | yes |
| `attempt-03-iced-vulkan-llvmpipe` | RAN_OK | -15 | 15.1 | 0 | 85.0 | yes |
| `attempt-04-bevy-0.1x-vulkan-llvmpipe` | RAN_OK | -15 | 30.3 | 0 | 84.0 | yes |

Each attempt folder holds: `cmd.txt`, `stdout.txt`, `stderr.txt`, `kernel.txt` (journal window of that run), `kernel-gpu-events.txt` (etnaviv/DRM lines only), `screenshot.png` where taken, `result.json` (harness record), and `artifacts/` where the test produced extra files. Files over 1 MB are gzipped.

## Key lines from the logs

**attempt-01-chromium-webgpu-cpu-only**
```
| Source | Page | rAF FPS | Page text |
```

**attempt-02-wgpu-bunnymark-vulkan-llvmpipe**
```
[2026-11-03T09:06:33.297Z INFO  wgpu_examples::framework] Selected adapter: llvmpipe (LLVM 22.1.8, 128 bits) (Vulkan)
[2026-11-03T09:06:34.547Z INFO  wgpu_examples::framework] Frame time 715.85ms (1.4 FPS)
[2026-11-03T09:06:35.698Z INFO  wgpu_examples::framework] Frame time 164.55ms (6.1 FPS)
[2026-11-03T09:06:36.723Z INFO  wgpu_examples::framework] Frame time 128.07ms (7.8 FPS)
[2026-11-03T09:06:37.838Z INFO  wgpu_examples::framework] Frame time 111.53ms (9.0 FPS)
[2026-11-03T09:06:38.974Z INFO  wgpu_examples::framework] Frame time 141.93ms (7.0 FPS)
[2026-11-03T09:06:39.998Z INFO  wgpu_examples::framework] Frame time 113.77ms (8.8 FPS)
... (5 more distinct lines) ...
[2026-11-03T09:06:46.294Z INFO  wgpu_examples::framework] Frame time 98.08ms (10.2 FPS)
[2026-11-03T09:06:47.358Z INFO  wgpu_examples::framework] Frame time 88.73ms (11.3 FPS)
[2026-11-03T09:06:48.398Z INFO  wgpu_examples::framework] Frame time 94.52ms (10.6 FPS)
[2026-11-03T09:06:49.434Z INFO  wgpu_examples::framework] Frame time 86.33ms (11.6 FPS)
[2026-11-03T09:06:50.449Z INFO  wgpu_examples::framework] Frame time 92.32ms (10.8 FPS)
[2026-11-03T09:06:51.524Z INFO  wgpu_examples::framework] Frame time 89.54ms (11.2 FPS)
[2026-11-03T09:06:52.537Z INFO  wgpu_examples::framework] Frame time 84.39ms (11.9 FPS)
```

**attempt-03-iced-vulkan-llvmpipe**
```
ICED_FPS 1.0
ICED_FPS 110.0
ICED_FPS 60.9
ICED_FPS 63.9
ICED_FPS 63.0
ICED_FPS 62.6   [x2]
ICED_FPS 61.4
... (4 more distinct lines) ...
ICED_FPS 62.5
            name: "llvmpipe (LLVM 22.1.8, 128 bits)",
            driver: "llvmpipe",
            backend: Vulkan,
        name: "llvmpipe (LLVM 22.1.8, 128 bits)",
        driver: "llvmpipe",
        backend: Vulkan,
```

**attempt-04-bevy-0.1x-vulkan-llvmpipe**
```
2026-11-03T09:11:25.786412Z  INFO bevy_render::renderer: AdapterInfo { name: "llvmpipe (LLVM 22.1.8, 128 bits)", vendor: 65541, device: 0, device_type: Cpu, device_pci_bus_id: "", driver: "llvmpipe", 
2026-11-03T09:11:25.786596Z  WARN bevy_render::renderer: The selected adapter is using a driver that only supports software rendering. This is likely to be very slow. See https://bevy.org/learn/errors
2026-11-03T09:11:27.457382Z  INFO bevy_diagnostic: fps               :    9.378694   (avg 7.605135)
2026-11-03T09:11:28.506464Z  INFO bevy_diagnostic: fps               :    6.359228   (avg 6.644634)
2026-11-03T09:11:29.531270Z  INFO bevy_diagnostic: fps               :    6.376147   (avg 6.772986)
2026-11-03T09:11:31.428766Z  INFO bevy_diagnostic: fps               :    0.898753   (avg 6.477633)
2026-11-03T09:11:33.049733Z  INFO bevy_diagnostic: fps               :    1.385770   (avg 6.042117)
... (15 more distinct lines) ...
2026-11-03T09:11:48.788240Z  INFO bevy_diagnostic: fps               :    1.252432   (avg 3.908482)
2026-11-03T09:11:49.585975Z  INFO bevy_diagnostic: fps               :    1.248706   (avg 3.848033)
2026-11-03T09:11:50.426936Z  INFO bevy_diagnostic: fps               :    1.188944   (avg 3.788942)
2026-11-03T09:11:52.072944Z  INFO bevy_diagnostic: fps               :    1.280259   (avg 3.679791)
2026-11-03T09:11:52.932837Z  INFO bevy_diagnostic: fps               :    1.153417   (avg 3.627158)
2026-11-03T09:11:53.785971Z  INFO bevy_diagnostic: fps               :    1.171693   (avg 3.577047)
2026-11-03T09:11:54.601935Z  INFO bevy_diagnostic: fps               :    1.227429   (avg 3.530055)
```

