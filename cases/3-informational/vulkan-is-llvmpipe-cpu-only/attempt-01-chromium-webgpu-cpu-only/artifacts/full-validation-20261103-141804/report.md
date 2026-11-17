# Extended GPU validation report

- Mesa: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`; kernel 7.1.5-0.mecha.202608260642.fc44.aarch64; Chromium 156.0.8078.47 Built from source for Fedora release 44 (Forty Four)
- Date: 2026-11-03 14:21 (board clock, no RTC); phases: webgpu

## 3. WebGPU samples and wgpu.rs web examples

Adapter seen by Chromium: `{"vendor":"google","arch":"swiftshader","device":"","desc":""}`

| Source | Page | rAF FPS | Page text |
|---|---|---|---|
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/helloTriangle/ | 15.7 |  |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/rotatingCube/ | 13.4 |  |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/instancedCube/ | 13.5 |  |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/cubemap/ | 8.9 |  |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/shadowMapping/ | 3.8 |  |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/particles/ | 0.5 | simulate deltaTime HDR settings ⚠️ Display isn't compatible toneMappingMode standard extended brightnessFactor Close Controls |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/computeBoids/ | 6.0 | deltaT rule1Distance rule2Distance rule3Distance rule1Scale rule2Scale rule3Scale Close Controls |
| webgpu-samples | https://webgpu.github.io/webgpu-samples/sample/gameOfLife/ | 5.5 | timestep width height workgroupSize 4 8 16 Close Controls |
| wgpu.rs | https://wgpu.rs/examples/?example=cube | - | Back to home page  WebGL2  WebGPU |
| wgpu.rs | https://wgpu.rs/examples/?example=boids | - | Back to home page  WebGL2  WebGPU |
| wgpu.rs | https://wgpu.rs/examples/?example=shadow | - | Back to home page  WebGL2  WebGPU |
| wgpu.rs | https://wgpu.rs/examples/?example=skybox | - | Back to home page  WebGL2  WebGPU |
| wgpu.rs | https://wgpu.rs/examples/?example=water | - | Back to home page  WebGL2  WebGPU |
| wgpu.rs | https://wgpu.rs/examples/?example=bunnymark | - | Back to home page  WebGL2  WebGPU |

Raw logs, screenshots (`shot-*.png`) and `results.json` are in `/home/mecha/benchmarks/reports/full-validation-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-141804/`.
