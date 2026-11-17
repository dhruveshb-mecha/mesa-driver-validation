# Qt 6 GPU validation report

- Mesa: `mesa-dri-drivers-27.0.0~devel-0.1.20261026git7b4b394.fc44.aarch64`; Qt `qt6-qtquick3d-6.11.2-1.fc44.aarch64`; kernel 7.1.5-0.mecha.202608260642.fc44.aarch64
- Date: 2026-11-03 14:32 (board clock); platform plugin: wayland (sway)

## 1. Qt Quick FPS: GPU (OpenGL ES via etnaviv) vs CPU

`opengl` = GPU. `software` = Qt software renderer (CPU, 2D only). `vulkan` = llvmpipe (CPU). Fedora Qt is built for desktop OpenGL only, and etnaviv offers desktop GL 2.1, which is enough for Quick 2D but not Quick 3D. The 3D GPU rows use `MESA_GL_VERSION_OVERRIDE=3.3` (experimental: Mesa reports GL 3.3 on this ES 3.0 GPU). Frame rates are animation ticks and are capped at 60 by Qt. Window size is whatever sway gives it (shown).

| Scene | Items | Backend | Processor | FPS | min FPS | size | shader/pipeline errors |
|---|---|---|---|---|---|---|---|
| Quick 2D (animated gradient rects) | 500 | opengl (desktop GL 2.1) | GPU | 15.9 | 14 | 536x568 | 0 |
| Quick 2D (animated gradient rects) | 500 | software renderer | CPU | 15.1 | 14 | 536x568 | 0 |
| Quick 2D (animated gradient rects) | 2000 | opengl (desktop GL 2.1) | GPU | 4.4 | 2 | 536x568 | 0 |
| Quick 2D (animated gradient rects) | 2000 | software renderer | CPU | 5.8 | 4 | 536x568 | 0 |
| Quick 3D (PBR spheres) | 16 | opengl, default Mesa | GPU (expected to fail) | 60.0 | 60 | 536x568 | 46144 |
| Quick 3D (PBR spheres) | 16 | opengl + Mesa GL 3.3 override | GPU | 12.9 | 10 | 536x568 | 0 |
| Quick 3D (PBR spheres) | 16 | vulkan (llvmpipe) | CPU | 5.8 | 5 | 536x568 | 0 |
| Quick 3D (PBR spheres) | 64 | opengl + Mesa GL 3.3 override | GPU | 7.4 | 4 | 536x568 | 0 |
| Quick 3D (PBR spheres) | 64 | vulkan (llvmpipe) | CPU | 2.1 | 1 | 536x568 | 0 |

Renderer reported by Qt (`QSG_INFO`):

- opengl (desktop GL 2.1): ` | `

## 2. Stock Qt Quick 3D examples (smoke test, OpenGL backend + Mesa GL 3.3 override, 12 s each)

Without the override every example aborts at start (`Failed to create context: 3009`, EGL_BAD_MATCH).

| Example | Result | Notes |
|---|---|---|
| hellocube | WARN | QEGLPlatformContext: Failed to create context: 3009; QQuickItem: Cannot set FocusScope once item has children and is in a window. |
| helloqtquick3d | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| intro | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| lights | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glTexParameter(pname=GL_TEXTURE_MIN_FILTER) |
| principledmaterial | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glTexParameter(pname=GL_TEXTURE_MIN_FILTER) |
| instancing | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| particles3d | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| picking | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| antialiasing | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| custommaterial | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| reflectionprobes | WARN | QEGLPlatformContext: Failed to create context: 3009; Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |
| cascadedshadowmaps | WARN | QEGLPlatformContext: Failed to create context: 3009; QEGLPlatformContext: Failed to create context: 3009 |
| orderindependenttransparency | MISSING | no prebuilt binary |
| sceneeffects | WARN | Mesa: error: GL_INVALID_ENUM in glDisable(GL_DEPTH_CLAMP) |

PASS = ran 12 s without crash or error text in the log. Screenshots (`ex-*.png`) and raw logs are in `/home/mecha/benchmarks/reports/qt-27.0.0~devel-0.1.20261026git7b4b394.fc44-20261103-142740/`.
