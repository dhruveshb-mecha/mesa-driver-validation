// nv12_planes: GBM NV12 bo, each plane imported as its own EGLImage (R8 for Y, GR88 for UV), as ANGLE/Chromium does.
// A) CPU writes pattern via mmap -> GPU samples each plane -> compare   (read half)
// B) GPU writes pattern via glTexSubImage2D into the plane textures -> CPU reads via mmap -> compare (write half)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <linux/dma-buf.h>
#include <gbm.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>
#include <GLES3/gl3.h>
#define FOURCC(a,b,c,d) ((unsigned)(a)|((unsigned)(b)<<8)|((unsigned)(c)<<16)|((unsigned)(d)<<24))
static void dsync(int fd,unsigned long flags){struct dma_buf_sync s={flags};ioctl(fd,DMA_BUF_IOCTL_SYNC,&s);}
static unsigned char PY(int x,int y,int s){return (x+3*y+s)&255;}
static unsigned char PU(int x,int y,int s){return (2*x+y+s)&255;}
static unsigned char PV(int x,int y,int s){return (x+5*y+s)&255;}
static PFNEGLCREATEIMAGEKHRPROC cimg; static PFNGLEGLIMAGETARGETTEXTURE2DOESPROC tgt;
static GLuint prog,fbo,rt;
static void sample_plane(GLuint tex,int w,int h,unsigned char*out){ // render tex.rg into RGBA FBO, read back
  glBindTexture(GL_TEXTURE_2D,tex); glViewport(0,0,w,h); glDrawArrays(GL_TRIANGLE_STRIP,0,4); glFinish(); glReadPixels(0,0,w,h,GL_RGBA,GL_UNSIGNED_BYTE,out);}
int main(int argc,char**argv){
  int W=atoi(argv[1]),H=atoi(argv[2]); unsigned use=atoi(argv[3]);
  int fd=open("/dev/dri/renderD128",O_RDWR); struct gbm_device*gd=gbm_create_device(fd);
  struct gbm_bo*bo=gbm_bo_create(gd,W,H,GBM_FORMAT_NV12,use); if(!bo){printf("FAIL bo\n");return 2;}
  int pc=gbm_bo_get_plane_count(bo); unsigned long long mod=gbm_bo_get_modifier(bo);
  int pfd[2],ps[2],po[2]; for(int i=0;i<2;i++){pfd[i]=gbm_bo_get_fd_for_plane(bo,i);ps[i]=gbm_bo_get_stride_for_plane(bo,i);po[i]=gbm_bo_get_offset(bo,i);}
  printf("NV12 %dx%d use=%u planes=%d mod=0x%llx  stride Y=%d UV=%d off Y=%d UV=%d\n",W,H,use,pc,mod,ps[0],ps[1],po[0],po[1]);
  if(pc<2)return 3;
  unsigned char*base[2]; for(int i=0;i<2;i++){size_t len=lseek(pfd[i],0,SEEK_END);lseek(pfd[i],0,SEEK_SET);void*m=mmap(0,len,PROT_READ|PROT_WRITE,MAP_SHARED,pfd[i],0);if(m==MAP_FAILED){perror("mmap");return 4;}base[i]=(unsigned char*)m+po[i];}
  PFNEGLGETPLATFORMDISPLAYEXTPROC gpd=(PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
  EGLDisplay dpy=gpd(0x31D7,gd,NULL); EGLint a,b; eglInitialize(dpy,&a,&b); eglBindAPI(EGL_OPENGL_ES_API);
  EGLConfig cfg; EGLint n,ca[]={EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT,EGL_SURFACE_TYPE,0,EGL_NONE}; eglChooseConfig(dpy,ca,&cfg,1,&n);
  EGLint xa[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE}; EGLContext ctx=eglCreateContext(dpy,cfg,EGL_NO_CONTEXT,xa); eglMakeCurrent(dpy,EGL_NO_SURFACE,EGL_NO_SURFACE,ctx);
  printf("GL_RENDERER=%s GL_VERSION=%s\n",glGetString(GL_RENDERER),glGetString(GL_VERSION));
  cimg=(PFNEGLCREATEIMAGEKHRPROC)eglGetProcAddress("eglCreateImageKHR"); tgt=(PFNGLEGLIMAGETARGETTEXTURE2DOESPROC)eglGetProcAddress("glEGLImageTargetTexture2DOES");
  EGLint ay[]={EGL_WIDTH,W,EGL_HEIGHT,H,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('R','8',' ',' '),EGL_DMA_BUF_PLANE0_FD_EXT,pfd[0],EGL_DMA_BUF_PLANE0_OFFSET_EXT,po[0],EGL_DMA_BUF_PLANE0_PITCH_EXT,ps[0],EGL_NONE};
  EGLint au[]={EGL_WIDTH,W/2,EGL_HEIGHT,H/2,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('G','R','8','8'),EGL_DMA_BUF_PLANE0_FD_EXT,pfd[1],EGL_DMA_BUF_PLANE0_OFFSET_EXT,po[1],EGL_DMA_BUF_PLANE0_PITCH_EXT,ps[1],EGL_NONE};
  EGLImageKHR iy=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,ay); if(iy==EGL_NO_IMAGE_KHR){printf("FAIL import R8 0x%x\n",eglGetError());return 7;}
  EGLImageKHR iu=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,au); if(iu==EGL_NO_IMAGE_KHR){printf("FAIL import GR88 0x%x\n",eglGetError());return 7;}
  GLuint ty,tu; glGenTextures(1,&ty); glBindTexture(GL_TEXTURE_2D,ty); tgt(GL_TEXTURE_2D,(GLeglImageOES)iy);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
  glGenTextures(1,&tu); glBindTexture(GL_TEXTURE_2D,tu); tgt(GL_TEXTURE_2D,(GLeglImageOES)iu);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
  glGenTextures(1,&rt); glBindTexture(GL_TEXTURE_2D,rt); glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,W,H,0,GL_RGBA,GL_UNSIGNED_BYTE,0);
  glGenFramebuffers(1,&fbo); glBindFramebuffer(GL_FRAMEBUFFER,fbo); glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,rt,0);
  const char*vs="attribute vec2 p;varying vec2 t;void main(){t=p*0.5+0.5;gl_Position=vec4(p,0,1);}";
  const char*fs="precision mediump float;varying vec2 t;uniform sampler2D s;void main(){gl_FragColor=texture2D(s,t);}";
  GLuint v=glCreateShader(GL_VERTEX_SHADER),f=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(v,1,&vs,0);glCompileShader(v);glShaderSource(f,1,&fs,0);glCompileShader(f);
  prog=glCreateProgram();glAttachShader(prog,v);glAttachShader(prog,f);glBindAttribLocation(prog,0,"p");glLinkProgram(prog);glUseProgram(prog);
  float q[]={-1,-1,1,-1,-1,1,1,1};glEnableVertexAttribArray(0);glVertexAttribPointer(0,2,GL_FLOAT,0,0,q);
  unsigned char*px=malloc((size_t)W*H*4); int bad,tot;
  // ---- A: CPU write, GPU read
  dsync(pfd[0],DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);dsync(pfd[1],DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);
  for(int y=0;y<H;y++)for(int x=0;x<W;x++)base[0][(size_t)y*ps[0]+x]=PY(x,y,0);
  for(int y=0;y<H/2;y++)for(int x=0;x<W/2;x++){base[1][(size_t)y*ps[1]+2*x]=PU(x,y,0);base[1][(size_t)y*ps[1]+2*x+1]=PV(x,y,0);}
  dsync(pfd[0],DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);dsync(pfd[1],DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);
  sample_plane(ty,W,H,px); bad=0;tot=0; for(int y=0;y<H;y++)for(int x=0;x<W;x++){tot++; if(px[((size_t)y*W+x)*4]!=PY(x,y,0)){if(bad<4)printf("  A.Y mismatch (%d,%d) got %d want %d\n",x,y,px[((size_t)y*W+x)*4],PY(x,y,0));bad++;}}
  printf("A (CPU write -> GPU read) Y plane: %d/%d wrong\n",bad,tot);
  sample_plane(tu,W/2,H/2,px); bad=0;tot=0; for(int y=0;y<H/2;y++)for(int x=0;x<W/2;x++){tot++; unsigned char*p=px+((size_t)y*(W/2)+x)*4; if(p[0]!=PU(x,y,0)||p[1]!=PV(x,y,0)){if(bad<4)printf("  A.UV mismatch (%d,%d) got %d,%d want %d,%d  [GR88: r=first byte]\n",x,y,p[0],p[1],PU(x,y,0),PV(x,y,0));bad++;}}
  printf("A (CPU write -> GPU read) UV plane: %d/%d wrong\n",bad,tot);
  // ---- B: GPU write via glTexSubImage2D, CPU read
  unsigned char*sy=malloc((size_t)W*H),*suv=malloc((size_t)W*H/2);
  for(int y=0;y<H;y++)for(int x=0;x<W;x++)sy[(size_t)y*W+x]=PY(x,y,77);
  for(int y=0;y<H/2;y++)for(int x=0;x<W/2;x++){suv[((size_t)y*(W/2)+x)*2]=PU(x,y,77);suv[((size_t)y*(W/2)+x)*2+1]=PV(x,y,77);}
  glPixelStorei(GL_UNPACK_ALIGNMENT,1);
  glBindTexture(GL_TEXTURE_2D,ty); glTexSubImage2D(GL_TEXTURE_2D,0,0,0,W,H,GL_RED,GL_UNSIGNED_BYTE,sy); GLenum e1=glGetError();
  glBindTexture(GL_TEXTURE_2D,tu); glTexSubImage2D(GL_TEXTURE_2D,0,0,0,W/2,H/2,GL_RG,GL_UNSIGNED_BYTE,suv); GLenum e2=glGetError();
  glFinish(); printf("B glTexSubImage2D errors: Y=0x%x UV=0x%x\n",e1,e2);
  dsync(pfd[0],DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ);dsync(pfd[1],DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ);
  bad=0;tot=0;for(int y=0;y<H;y++)for(int x=0;x<W;x++){tot++;if(base[0][(size_t)y*ps[0]+x]!=PY(x,y,77)){if(bad<4)printf("  B.Y mismatch (%d,%d) got %d want %d\n",x,y,base[0][(size_t)y*ps[0]+x],PY(x,y,77));bad++;}}
  printf("B (GPU write -> CPU read) Y plane: %d/%d wrong\n",bad,tot);
  bad=0;tot=0;for(int y=0;y<H/2;y++)for(int x=0;x<W/2;x++){tot++;unsigned char u=base[1][(size_t)y*ps[1]+2*x],vv=base[1][(size_t)y*ps[1]+2*x+1];if(u!=PU(x,y,77)||vv!=PV(x,y,77)){if(bad<4)printf("  B.UV mismatch (%d,%d) got %d,%d want %d,%d\n",x,y,u,vv,PU(x,y,77),PV(x,y,77));bad++;}}
  printf("B (GPU write -> CPU read) UV plane: %d/%d wrong\n",bad,tot);

  // ---- C: single NV12 EGLImage + samplerExternalOES (Chromium "ExtSamplerOn" path)
  { EGLint at[]={EGL_WIDTH,W,EGL_HEIGHT,H,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('N','V','1','2'),
     EGL_DMA_BUF_PLANE0_FD_EXT,pfd[0],EGL_DMA_BUF_PLANE0_OFFSET_EXT,po[0],EGL_DMA_BUF_PLANE0_PITCH_EXT,ps[0],
     EGL_DMA_BUF_PLANE1_FD_EXT,pfd[1],EGL_DMA_BUF_PLANE1_OFFSET_EXT,po[1],EGL_DMA_BUF_PLANE1_PITCH_EXT,ps[1],
     EGL_YUV_COLOR_SPACE_HINT_EXT,EGL_ITU_REC601_EXT,EGL_SAMPLE_RANGE_HINT_EXT,EGL_YUV_NARROW_RANGE_EXT,EGL_NONE};
    EGLImageKHR ie=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,at); if(ie==EGL_NO_IMAGE_KHR){printf("C import fail 0x%x\n",eglGetError());return 0;}
    GLuint te; glGenTextures(1,&te); glBindTexture(GL_TEXTURE_EXTERNAL_OES,te); tgt(GL_TEXTURE_EXTERNAL_OES,(GLeglImageOES)ie);
    glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
    const char*fse="#extension GL_OES_EGL_image_external : require\nprecision mediump float;varying vec2 t;uniform samplerExternalOES s;void main(){gl_FragColor=texture2D(s,t);}";
    GLuint f2=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(f2,1,&fse,0);glCompileShader(f2);GLuint p2=glCreateProgram();glAttachShader(p2,v);glAttachShader(p2,f2);glBindAttribLocation(p2,0,"p");glLinkProgram(p2);glUseProgram(p2);
    glBindFramebuffer(GL_FRAMEBUFFER,fbo);
    for(int mode=0;mode<2;mode++){ // 0: Y ramp, chroma neutral; 1: Y const 126, chroma varies (u by x, v by y)
      for(int y=0;y<H;y++)for(int x=0;x<W;x++)base[0][(size_t)y*ps[0]+x]= mode==0? 16+(x*219/(W-1)) : 126;
      for(int y=0;y<H/2;y++)for(int x=0;x<W/2;x++){base[1][(size_t)y*ps[1]+2*x]= mode==0?128: 100+(x*56/(W/2-1)); base[1][(size_t)y*ps[1]+2*x+1]= mode==0?128: 100+(y*56/(H/2-1));}
      glViewport(0,0,W,H);glDrawArrays(GL_TRIANGLE_STRIP,0,4);glFinish();glReadPixels(0,0,W,H,GL_RGBA,GL_UNSIGNED_BYTE,px);
      int bad2=0,n2=0; for(int y=0;y<H;y+=7)for(int x=0;x<W;x+=7){ int Y=mode==0?16+(x*219/(W-1)):126,U=mode==0?128:100+((x/2)*56/(W/2-1)),V=mode==0?128:100+((y/2)*56/(H/2-1));
        double yy=1.164*(Y-16),u=U-128,vv=V-128; int er=yy+1.596*vv,eg=yy-.392*u-.813*vv,eb=yy+2.017*u; if(er<0)er=0;if(er>255)er=255;if(eg<0)eg=0;if(eg>255)eg=255;if(eb<0)eb=0;if(eb>255)eb=255;
        unsigned char*q2=px+((size_t)y*W+x)*4; n2++; if(abs(q2[0]-er)+abs(q2[1]-eg)+abs(q2[2]-eb)>24){ if(bad2<3)printf("  C%d (%d,%d) got %d,%d,%d want %d,%d,%d\n",mode,x,y,q2[0],q2[1],q2[2],er,eg,eb); bad2++;} }
      printf("C%d external sampler, %s: %d/%d sampled pixels wrong\n",mode,mode==0?"luma ramp + neutral chroma":"flat luma + varying chroma",bad2,n2); }
  }

  // ---- D: luma response of the external sampler, neutral chroma (128), with proper dma-buf sync, CPU writer and GPU writer
  { EGLint at[]={EGL_WIDTH,W,EGL_HEIGHT,H,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('N','V','1','2'),
     EGL_DMA_BUF_PLANE0_FD_EXT,pfd[0],EGL_DMA_BUF_PLANE0_OFFSET_EXT,po[0],EGL_DMA_BUF_PLANE0_PITCH_EXT,ps[0],
     EGL_DMA_BUF_PLANE1_FD_EXT,pfd[1],EGL_DMA_BUF_PLANE1_OFFSET_EXT,po[1],EGL_DMA_BUF_PLANE1_PITCH_EXT,ps[1],
     EGL_YUV_COLOR_SPACE_HINT_EXT,EGL_ITU_REC601_EXT,EGL_SAMPLE_RANGE_HINT_EXT,EGL_YUV_NARROW_RANGE_EXT,EGL_NONE};
    EGLImageKHR ie=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,at);
    GLuint te; glGenTextures(1,&te); glBindTexture(GL_TEXTURE_EXTERNAL_OES,te); tgt(GL_TEXTURE_EXTERNAL_OES,(GLeglImageOES)ie);
    glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
    const char*fse="#extension GL_OES_EGL_image_external : require\nprecision mediump float;varying vec2 t;uniform samplerExternalOES s;void main(){gl_FragColor=texture2D(s,t);}";
    GLuint v2=glCreateShader(GL_VERTEX_SHADER);const char*vs2="attribute vec2 p;varying vec2 t;void main(){t=p*0.5+0.5;gl_Position=vec4(p,0,1);}";glShaderSource(v2,1,&vs2,0);glCompileShader(v2);
    GLuint f2=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(f2,1,&fse,0);glCompileShader(f2);GLuint p2=glCreateProgram();glAttachShader(p2,v2);glAttachShader(p2,f2);glBindAttribLocation(p2,0,"p");glLinkProgram(p2);glUseProgram(p2);
    glBindFramebuffer(GL_FRAMEBUFFER,fbo); glViewport(0,0,W,H);
    int Ys[]={16,32,64,96,126,160,200,235};
    printf("D: external sampler, flat Y, U=V=128, expected gray = 1.164*(Y-16)\n   writer   Y  expected | got r,g,b (centre pixel)\n");
    for(int w=0;w<2;w++) for(int k=0;k<8;k++){ int Y=Ys[k];
      if(w==0){ dsync(pfd[0],DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);dsync(pfd[1],DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);
        memset(base[0],Y,(size_t)ps[0]*H); memset(base[1],128,(size_t)ps[1]*(H/2)); dsync(pfd[0],DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);dsync(pfd[1],DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE); }
      else { unsigned char*a=malloc((size_t)W*H);memset(a,Y,(size_t)W*H);unsigned char*b=malloc((size_t)W*H/2);memset(b,128,(size_t)W*H/2);
        glBindTexture(GL_TEXTURE_2D,ty);glTexSubImage2D(GL_TEXTURE_2D,0,0,0,W,H,GL_RED,GL_UNSIGNED_BYTE,a);glBindTexture(GL_TEXTURE_2D,tu);glTexSubImage2D(GL_TEXTURE_2D,0,0,0,W/2,H/2,GL_RG,GL_UNSIGNED_BYTE,b);glFinish();free(a);free(b);glBindTexture(GL_TEXTURE_EXTERNAL_OES,te);}
      glDrawArrays(GL_TRIANGLE_STRIP,0,4);glFinish();glReadPixels(0,0,W,H,GL_RGBA,GL_UNSIGNED_BYTE,px);
      unsigned char*q2=px+((size_t)(H/2)*W+W/2)*4; double e=1.164*(Y-16); if(e>255)e=255;
      printf("   %-6s %3d  %6.1f   | %3d,%3d,%3d   (diff %+.0f)\n",w?"GPU":"CPU",Y,e,q2[0],q2[1],q2[2],q2[1]-e); }
  }

  // ---- E: chroma response, flat Y=126, vary U (V=128) then V (U=128)
  { EGLint at[]={EGL_WIDTH,W,EGL_HEIGHT,H,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('N','V','1','2'),
     EGL_DMA_BUF_PLANE0_FD_EXT,pfd[0],EGL_DMA_BUF_PLANE0_OFFSET_EXT,po[0],EGL_DMA_BUF_PLANE0_PITCH_EXT,ps[0],
     EGL_DMA_BUF_PLANE1_FD_EXT,pfd[1],EGL_DMA_BUF_PLANE1_OFFSET_EXT,po[1],EGL_DMA_BUF_PLANE1_PITCH_EXT,ps[1],
     EGL_YUV_COLOR_SPACE_HINT_EXT,EGL_ITU_REC601_EXT,EGL_SAMPLE_RANGE_HINT_EXT,EGL_YUV_NARROW_RANGE_EXT,EGL_NONE};
    EGLImageKHR ie=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,at);
    GLuint te; glGenTextures(1,&te); glBindTexture(GL_TEXTURE_EXTERNAL_OES,te); tgt(GL_TEXTURE_EXTERNAL_OES,(GLeglImageOES)ie);
    glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
    const char*fse="#extension GL_OES_EGL_image_external : require\nprecision mediump float;varying vec2 t;uniform samplerExternalOES s;void main(){gl_FragColor=texture2D(s,t);}";
    GLuint v2=glCreateShader(GL_VERTEX_SHADER);const char*vs2="attribute vec2 p;varying vec2 t;void main(){t=p*0.5+0.5;gl_Position=vec4(p,0,1);}";glShaderSource(v2,1,&vs2,0);glCompileShader(v2);
    GLuint f2=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(f2,1,&fse,0);glCompileShader(f2);GLuint p2=glCreateProgram();glAttachShader(p2,v2);glAttachShader(p2,f2);glBindAttribLocation(p2,0,"p");glLinkProgram(p2);glUseProgram(p2);
    glBindFramebuffer(GL_FRAMEBUFFER,fbo); glViewport(0,0,W,H);
    int Cs[]={64,96,112,128,144,160,192};
    printf("E: external sampler, Y=126 flat; expected R=y+1.596V' G=y-0.392U'-0.813V' B=y+2.017U' (U'=U-128,V'=V-128, y=128)\n   which  C   | got r,g,b        | expected r,g,b\n");
    for(int w=0;w<2;w++)for(int k=0;k<7;k++){ int C=Cs[k]; int U=w==0?C:128,V=w==0?128:C;
      dsync(pfd[0],DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);dsync(pfd[1],DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);
      memset(base[0],126,(size_t)ps[0]*H); for(int y=0;y<H/2;y++)for(int x=0;x<W/2;x++){base[1][(size_t)y*ps[1]+2*x]=U;base[1][(size_t)y*ps[1]+2*x+1]=V;}
      dsync(pfd[0],DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);dsync(pfd[1],DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);
      glDrawArrays(GL_TRIANGLE_STRIP,0,4);glFinish();glReadPixels(0,0,W,H,GL_RGBA,GL_UNSIGNED_BYTE,px);
      unsigned char*q2=px+((size_t)(H/2)*W+W/2)*4; double y=128,u=U-128,vv=V-128; double er=y+1.596*vv,eg=y-.392*u-.813*vv,eb=y+2.017*u; if(er<0)er=0;if(er>255)er=255;if(eg<0)eg=0;if(eg>255)eg=255;if(eb<0)eb=0;if(eb>255)eb=255;
      printf("   %s=%3d     | %3d,%3d,%3d      | %3.0f,%3.0f,%3.0f\n",w?"V":"U",C,q2[0],q2[1],q2[2],er,eg,eb); }
  }
  return 0;}
