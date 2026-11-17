#!/usr/bin/env python3
"""Headless GLES 3.0 capability probe (EGL surfaceless + ctypes, no extra packages).
Prints JSON; exit 0 if no FAIL."""
import ctypes as C, json, sys, struct

egl = C.CDLL("libEGL.so.1"); gl = C.CDLL("libGLESv2.so.2")
P = C.c_void_p
egl.eglGetProcAddress.restype = P
egl.eglGetProcAddress.argtypes = [C.c_char_p]
egl.eglGetPlatformDisplay.restype = P; egl.eglGetPlatformDisplay.argtypes = [C.c_uint, P, P]
egl.eglInitialize.argtypes = [P, C.POINTER(C.c_int), C.POINTER(C.c_int)]
egl.eglChooseConfig.argtypes = [P, C.POINTER(C.c_int), C.POINTER(P), C.c_int, C.POINTER(C.c_int)]
egl.eglCreateContext.restype = P; egl.eglCreateContext.argtypes = [P, P, P, C.POINTER(C.c_int)]
egl.eglMakeCurrent.argtypes = [P, P, P, P]
egl.eglQueryString.restype = C.c_char_p; egl.eglQueryString.argtypes = [P, C.c_int]
gl.glGetString.restype = C.c_char_p; gl.glGetString.argtypes = [C.c_uint]
gl.glGetStringi.restype = C.c_char_p; gl.glGetStringi.argtypes = [C.c_uint, C.c_uint]
gl.glMapBufferRange.restype = P
gl.glMapBufferRange.argtypes = [C.c_uint, C.c_ssize_t, C.c_ssize_t, C.c_uint]
gl.glShaderSource.argtypes = [C.c_uint, C.c_int, C.POINTER(C.c_char_p), P]
gl.glBufferData.argtypes = [C.c_uint, C.c_ssize_t, P, C.c_uint]
gl.glClearColor.argtypes = [C.c_float] * 4

R = {"checks": [], "info": {}}
def check(name, status, detail=""):
    R["checks"].append({"name": name, "status": status, "detail": str(detail)})
def geti(p):
    v = C.c_int(); gl.glGetIntegerv(p, C.byref(v)); return v.value

def setup():
    dpy = egl.eglGetPlatformDisplay(0x31DD, None, None)   # EGL_PLATFORM_SURFACELESS_MESA
    if not dpy: raise RuntimeError("no surfaceless EGL display")
    a, b = C.c_int(), C.c_int()
    if not egl.eglInitialize(dpy, C.byref(a), C.byref(b)): raise RuntimeError("eglInitialize failed")
    egl.eglBindAPI(0x30A0)
    cfg_attr = (C.c_int * 5)(0x3040, 0x40, 0x3033, 1, 0x3038)   # RENDERABLE=ES3, SURFACE=PBUFFER
    cfg = P(); n = C.c_int()
    if not egl.eglChooseConfig(dpy, cfg_attr, C.byref(cfg), 1, C.byref(n)) or n.value < 1:
        raise RuntimeError("no ES3 EGL config")
    ctx_attr = (C.c_int * 5)(0x3098, 3, 0x30FB, 0, 0x3038)
    ctx = egl.eglCreateContext(dpy, cfg, None, ctx_attr)
    if not ctx: raise RuntimeError("ES 3.0 context creation failed")
    if not egl.eglMakeCurrent(dpy, None, None, ctx): raise RuntimeError("eglMakeCurrent failed")
    R["info"]["egl_version"] = f"{a.value}.{b.value}"
    R["info"]["egl_vendor"] = (egl.eglQueryString(dpy, 0x3053) or b"").decode()
    return dpy

def fbo_status(color_attach):
    fbo = C.c_uint(); gl.glGenFramebuffers(1, C.byref(fbo)); gl.glBindFramebuffer(0x8D40, fbo)
    color_attach()
    st = gl.glCheckFramebufferStatus(0x8D40)
    gl.glBindFramebuffer(0x8D40, 0); gl.glDeleteFramebuffers(1, C.byref(fbo))
    return st

def tex_rt(ifmt, fmt, typ):
    def f():
        t = C.c_uint(); gl.glGenTextures(1, C.byref(t)); gl.glBindTexture(0x0DE1, t)
        gl.glTexImage2D(0x0DE1, 0, ifmt, 64, 64, 0, fmt, typ, None)
        gl.glFramebufferTexture2D(0x8D40, 0x8CE0, 0x0DE1, t, 0)
    return f

def rb_attach(ifmt, att, samples=0):
    def f():
        r = C.c_uint(); gl.glGenRenderbuffers(1, C.byref(r)); gl.glBindRenderbuffer(0x8D41, r)
        if samples: gl.glRenderbufferStorageMultisample(0x8D41, samples, ifmt, 64, 64)
        else: gl.glRenderbufferStorage(0x8D41, ifmt, 64, 64)
        gl.glFramebufferRenderbuffer(0x8D40, att, 0x8D41, r)
    return f

def depth_with_color(dfmt, att):
    def f():
        tex_rt(0x8058, 0x1908, 0x1401)()
        rb_attach(dfmt, att)()
    return f

def transform_feedback(nverts):
    def sh(kind, src):
        s = gl.glCreateShader(kind); arr = (C.c_char_p * 1)(src.encode())
        gl.glShaderSource(s, 1, arr, None); gl.glCompileShader(s)
        ok = C.c_int(); gl.glGetShaderiv(s, 0x8B81, C.byref(ok))
        if not ok.value: raise RuntimeError("shader compile failed")
        return s
    # surfaceless context has no default framebuffer: draw needs a complete FBO even with RASTERIZER_DISCARD
    fbo = C.c_uint(); gl.glGenFramebuffers(1, C.byref(fbo)); gl.glBindFramebuffer(0x8D40, fbo); tex_rt(0x8058, 0x1908, 0x1401)()
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, sh(0x8B31, "#version 300 es\nin float a; out float b; out float c;\n"
        "void main(){ b = a*2.0; c = a+1.0; gl_Position = vec4(0.0,0.0,0.0,1.0); gl_PointSize=1.0; }"))
    gl.glAttachShader(prog, sh(0x8B30, "#version 300 es\nprecision mediump float; out vec4 o; void main(){ o=vec4(1.0); }"))
    names = (C.c_char_p * 2)(b"b", b"c")
    gl.glTransformFeedbackVaryings(prog, 2, names, 0x8C8C)   # INTERLEAVED
    gl.glLinkProgram(prog)
    ok = C.c_int(); gl.glGetProgramiv(prog, 0x8B82, C.byref(ok))
    if not ok.value: raise RuntimeError("link failed")
    gl.glUseProgram(prog)
    data = (C.c_float * nverts)(*[float(i) for i in range(nverts)])
    vb = C.c_uint(); gl.glGenBuffers(1, C.byref(vb)); gl.glBindBuffer(0x8892, vb)
    gl.glBufferData(0x8892, nverts * 4, C.cast(data, P), 0x88E4)
    loc = gl.glGetAttribLocation(prog, b"a"); gl.glEnableVertexAttribArray(loc)
    gl.glVertexAttribPointer(loc, 1, 0x1406, 0, 0, None)
    tb = C.c_uint(); gl.glGenBuffers(1, C.byref(tb)); gl.glBindBuffer(0x8C8E, tb)
    gl.glBufferData(0x8C8E, nverts * 8, None, 0x88E6)
    gl.glBindBufferBase(0x8C8E, 0, tb)
    gl.glEnable(0x8C89)   # RASTERIZER_DISCARD
    gl.glBeginTransformFeedback(0x0000); gl.glDrawArrays(0x0000, 0, nverts); gl.glEndTransformFeedback()
    gl.glDisable(0x8C89); gl.glFinish()
    p = gl.glMapBufferRange(0x8C8E, 0, nverts * 8, 1)
    if not p: raise RuntimeError(f"map failed, glError=0x{gl.glGetError():x}")
    out = struct.unpack(f"{nverts*2}f", C.string_at(p, nverts * 8)); gl.glUnmapBuffer(0x8C8E)
    err = gl.glGetError()
    bad = [i for i in range(nverts) if out[2*i] != 2.0*i or out[2*i+1] != i+1.0]
    if err and not bad: raise RuntimeError(f"unexpected GL error 0x{err:x}")
    gl.glBindFramebuffer(0x8D40, 0)
    return bad

def msaa_resolve(with_depth, half=False):
    """Draw into a 4x MSAA renderbuffer, resolve with glBlitFramebuffer, read back. Returns (inside, outside, edge_blend, err)."""
    W = 64
    def fb(): f = C.c_uint(); gl.glGenFramebuffers(1, C.byref(f)); return f
    def rb(fmt, samples):
        r = C.c_uint(); gl.glGenRenderbuffers(1, C.byref(r)); gl.glBindRenderbuffer(0x8D41, r)
        gl.glRenderbufferStorageMultisample(0x8D41, samples, fmt, W, W); return r
    ms = fb(); gl.glBindFramebuffer(0x8D40, ms)
    gl.glFramebufferRenderbuffer(0x8D40, 0x8CE0, 0x8D41, rb(0x881A if half else 0x8058, 4))
    if with_depth: gl.glFramebufferRenderbuffer(0x8D40, 0x8D00, 0x8D41, rb(0x81A6, 4))   # DEPTH_COMPONENT24
    gl_err = gl.glGetError(); st_ = gl.glCheckFramebufferStatus(0x8D40)
    if st_ != 0x8CD5: raise RuntimeError(f"msaa fbo incomplete: status 0x{st_:x} (0x8cd6=INCOMPLETE_ATTACHMENT 0x8cd5=complete 0x8d56=INCOMPLETE_MULTISAMPLE 0x8cdd=UNSUPPORTED) glerr-after-storage 0x{gl_err:x}")
    one = fb(); gl.glBindFramebuffer(0x8D40, one); (tex_rt(0x881A, 0x1908, 0x140B) if half else tex_rt(0x8058, 0x1908, 0x1401))()
    gl.glBindFramebuffer(0x8D40, ms); gl.glViewport(0, 0, W, W)
    gl.glClearColor(0.0, 1.0, 0.0, 1.0); gl.glClear(0x4000 | (0x100 if with_depth else 0))
    if with_depth: gl.glEnable(0x0B71)   # DEPTH_TEST
    def sh(kind, src):
        s_ = gl.glCreateShader(kind); arr = (C.c_char_p * 1)(src.encode()); gl.glShaderSource(s_, 1, arr, None); gl.glCompileShader(s_); return s_
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, sh(0x8B31, "#version 300 es\nvoid main(){ vec2 p[3]=vec2[3](vec2(-1.,-1.),vec2(1.,-1.),vec2(-1.,1.)); gl_Position=vec4(p[gl_VertexID],0.,1.); }"))
    gl.glAttachShader(prog, sh(0x8B30, "#version 300 es\nprecision mediump float; out vec4 o; void main(){ o=vec4(1.,0.,0.,1.); }"))
    gl.glLinkProgram(prog); gl.glUseProgram(prog); gl.glDrawArrays(0x0004, 0, 3)
    gl.glBindFramebuffer(0x8CA8, ms); gl.glBindFramebuffer(0x8CA9, one)   # READ / DRAW
    gl.glBlitFramebuffer(0, 0, W, W, 0, 0, W, W, 0x4000, 0x2600)
    err = gl.glGetError()
    gl.glBindFramebuffer(0x8D40, one)
    if half:
        buf = (C.c_float * (W * W * 4))(); gl.glReadPixels(0, 0, W, W, 0x1908, 0x1406, buf)
        px = lambda x, y: tuple(round(buf[(y * W + x) * 4 + k] * 255) for k in range(3))
    else:
        buf = (C.c_ubyte * (W * W * 4))(); gl.glReadPixels(0, 0, W, W, 0x1908, 0x1401, buf)
        px = lambda x, y: tuple(buf[(y * W + x) * 4: (y * W + x) * 4 + 3])
    inside, outside = px(8, 8), px(W - 8, W - 8)
    blend = sum(1 for i in range(W) if 0 < px(i, W - 1 - i)[0] < 255 or 0 < px(i, W - 1 - i)[1] < 255 or (0 < px(i, W - 2 - i)[0] < 255))
    gl.glDisable(0x0B71); gl.glBindFramebuffer(0x8D40, 0)
    return inside, outside, blend, err

def main():
    try: setup()
    except Exception as e:
        check("es3_context", "FAIL", e); R["verdict"] = "FAIL"; print(json.dumps(R, indent=1)); return 1
    ver = gl.glGetString(0x1F02).decode(); ren = gl.glGetString(0x1F01).decode()
    R["info"].update(version=ver, renderer=ren, vendor=gl.glGetString(0x1F00).decode(),
                     glsl=gl.glGetString(0x8B8C).decode())
    n = geti(0x821D); exts = [gl.glGetStringi(0x1F03, i).decode() for i in range(n)]
    R["info"]["extensions"] = exts
    check("es3_context", "PASS" if "OpenGL ES 3." in ver else "FAIL", ver)
    check("hardware_renderer", "FAIL" if any(s in ren.lower() for s in ("llvmpipe", "softpipe", "swrast")) else "PASS", ren)
    for name, pn in (("MAX_TEXTURE_SIZE", 0x0D33), ("MAX_3D_TEXTURE_SIZE", 0x8073), ("MAX_ARRAY_TEXTURE_LAYERS", 0x88FF),
                     ("MAX_DRAW_BUFFERS", 0x8824), ("MAX_COLOR_ATTACHMENTS", 0x8CDF), ("MAX_SAMPLES", 0x8D57),
                     ("MAX_TF_SEPARATE_ATTRIBS", 0x8C8B), ("MAX_VERTEX_UNIFORM_VECTORS", 0x8DFB)):
        R["info"][name] = geti(pn)
    FL, RI, RGBA = 0x1406, 0x8D99, 0x1908
    for name, args in (("rt_RGBA8", (0x8058, RGBA, 0x1401)), ("rt_SRGB8_ALPHA8", (0x8C43, RGBA, 0x1401)),
                       ("rt_RGBA16F", (0x881A, RGBA, 0x140B)), ("rt_RGBA32I", (0x8D82, RI, 0x1404)),
                       ("rt_RGBA32UI", (0x8D70, RI, 0x1405)), ("rt_RGBA32F", (0x8814, RGBA, FL))):
        gl.glGetError()
        st = fbo_status(tex_rt(*args))
        # RGBA32F/RGBA16F render targets are only required with EXT_color_buffer_float
        need_ext = name in ("rt_RGBA32F", "rt_RGBA16F")
        status = "PASS" if st == 0x8CD5 else ("INFO" if need_ext and "GL_EXT_color_buffer_float" not in exts else "FAIL")
        check(name, status, f"fbo status 0x{st:x}")
    check("ext_color_buffer_float", "PASS" if "GL_EXT_color_buffer_float" in exts else "INFO", "extension advertised?")
    check("depth_D32F", "PASS" if fbo_status(depth_with_color(0x8CAC, 0x8D00)) == 0x8CD5 else "FAIL", "DEPTH_COMPONENT32F")
    check("depth_D32F_S8", "PASS" if fbo_status(depth_with_color(0x8CAD, 0x821A)) == 0x8CD5 else "FAIL", "DEPTH32F_STENCIL8")
    for s in (4,):
        gl.glGetError()
        st = fbo_status(rb_attach(0x8058, 0x8CE0, s)); err = gl.glGetError()
        check(f"msaa_{s}x_renderbuffer", "PASS" if st == 0x8CD5 and not err else "FAIL", f"status 0x{st:x} err 0x{err:x}")
    for wd, half in ((False, False), (True, False), (False, True), (True, True)):
        nm = "msaa_4x_resolve_content" + ("_rgba16f" if half else "") + ("_with_depth" if wd else "")
        try:
            ins, outs, blend, err = msaa_resolve(wd, half)
            ok = ins == (255, 0, 0) and outs == (0, 255, 0) and not err
            check(nm, "PASS" if ok else "FAIL", f"inside px {ins} (want 255,0,0), outside px {outs} (want 0,255,0), edge-blended px {blend}, glerr 0x{err:x}")
        except Exception as e:
            check(nm, "FAIL", e)
    for nv in (16, 200, 1000):   # vertex counts from small to large
        try:
            bad = transform_feedback(nv)
            check(f"transform_feedback_{nv}_verts", "PASS" if not bad else "FAIL",
                  "all outputs correct" if not bad else f"{len(bad)} wrong, first bad vertex {bad[0]}")
        except Exception as e:
            check(f"transform_feedback_{nv}_verts", "FAIL", e)
    if "--only" in sys.argv:
        import re; rx = re.compile(sys.argv[sys.argv.index("--only") + 1])
        R["checks"] = [c for c in R["checks"] if rx.search(c["name"])]
        R["info"].pop("extensions", None)
    fails = [c for c in R["checks"] if c["status"] == "FAIL"]
    R["verdict"] = "FAIL" if fails else "PASS"
    print(json.dumps(R, indent=1))
    return 1 if fails else 0

sys.exit(main())
