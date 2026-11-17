import ctypes,os
g=ctypes.CDLL("libgbm.so.1")
for n in ("gbm_create_device","gbm_bo_create"): getattr(g,n).restype=ctypes.c_void_p
for n in ("gbm_bo_get_plane_count","gbm_bo_get_stride_for_plane","gbm_bo_get_offset","gbm_bo_get_fd_for_plane","gbm_bo_get_modifier"):
    getattr(g,n).argtypes=[ctypes.c_void_p]+([ctypes.c_int] if n!="gbm_bo_get_plane_count" and n!="gbm_bo_get_modifier" else [])
g.gbm_bo_get_modifier.restype=ctypes.c_uint64
g.gbm_bo_get_fd_for_plane.restype=ctypes.c_int
f=lambda s:int.from_bytes(s.encode(),"little")
fd=os.open("/dev/dri/renderD128",os.O_RDWR); d=g.gbm_create_device(fd)
for fmt in ("XR24","NV12"):
    for uname,u in (("RENDERING",4),("LINEAR",16),("SCANOUT|RENDERING",5)):
        bo=g.gbm_bo_create(ctypes.c_void_p(d),1920,1080,f(fmt),u)
        if not bo: print(fmt,uname,"bo=FAIL"); continue
        bo=ctypes.c_void_p(bo); pc=g.gbm_bo_get_plane_count(bo)
        fds=[g.gbm_bo_get_fd_for_plane(bo,i) for i in range(max(pc,2))]
        print(f"{fmt} {uname:18} plane_count={pc} modifier=0x{g.gbm_bo_get_modifier(bo):x} stride0={g.gbm_bo_get_stride_for_plane(bo,0)} fd_for_plane={fds}")
