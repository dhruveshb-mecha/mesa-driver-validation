// control for nv12_dmabuf_test: same harness with a plain XRGB8888 GBM buffer
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <gbm.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>
#define FOURCC(a,b,c,d) ((unsigned)(a)|((unsigned)(b)<<8)|((unsigned)(c)<<16)|((unsigned)(d)<<24))
static const unsigned BAR[8]={0xffffff,0xffff00,0x00ffff,0x00ff00,0xff00ff,0xff0000,0x0000ff,0x000000};
int main(int argc,char**argv){ int W=640,H=360; unsigned use=argc>1?atoi(argv[1]):16;
  int fd=open("/dev/dri/renderD128",O_RDWR); struct gbm_device*gd=gbm_create_device(fd);
  struct gbm_bo*bo=gbm_bo_create(gd,W,H,GBM_FORMAT_XRGB8888,use); if(!bo){printf("FAIL bo\n");return 2;}
  int pfd=gbm_bo_get_fd_for_plane(bo,0),stride=gbm_bo_get_stride_for_plane(bo,0),off=gbm_bo_get_offset(bo,0); unsigned long long mod=gbm_bo_get_modifier(bo);
  printf("XR24 %dx%d use=%u planes=%d stride=%d offset=%d modifier=0x%llx\n",W,H,use,gbm_bo_get_plane_count(bo),stride,off,mod);
  size_t len=lseek(pfd,0,SEEK_END); lseek(pfd,0,SEEK_SET); unsigned char*m=mmap(0,len,PROT_READ|PROT_WRITE,MAP_SHARED,pfd,0); if(m==MAP_FAILED){perror("mmap");return 4;}
  for(int y=0;y<H;y++)for(int x=0;x<W;x++){unsigned c=BAR[((x/(W/8))+(y/(H/4)))%8]; unsigned char*p=m+off+y*stride+x*4; p[0]=c&255;p[1]=(c>>8)&255;p[2]=(c>>16)&255;p[3]=255;}
  PFNEGLGETPLATFORMDISPLAYEXTPROC gpd=(PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
  EGLDisplay dpy=gpd(0x31D7,gd,NULL); EGLint a,b; eglInitialize(dpy,&a,&b); eglBindAPI(EGL_OPENGL_ES_API); EGLConfig cfg;EGLint n;EGLint ca[]={EGL_RENDERABLE_TYPE,EGL_OPENGL_ES2_BIT,EGL_SURFACE_TYPE,0,EGL_NONE};
  eglChooseConfig(dpy,ca,&cfg,1,&n); EGLint xa[]={EGL_CONTEXT_CLIENT_VERSION,2,EGL_NONE}; EGLContext ctx=eglCreateContext(dpy,cfg,EGL_NO_CONTEXT,xa); eglMakeCurrent(dpy,EGL_NO_SURFACE,EGL_NO_SURFACE,ctx);
  EGLint at[40];int k=0;
  #define A(x,y) at[k++]=x;at[k++]=y;
  A(EGL_WIDTH,W)A(EGL_HEIGHT,H)A(EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('X','R','2','4'))A(EGL_DMA_BUF_PLANE0_FD_EXT,pfd)A(EGL_DMA_BUF_PLANE0_OFFSET_EXT,off)A(EGL_DMA_BUF_PLANE0_PITCH_EXT,stride)
  if(mod!=0&&mod!=0x00ffffffffffffffULL){A(EGL_DMA_BUF_PLANE0_MODIFIER_LO_EXT,(EGLint)(mod&0xffffffff))A(EGL_DMA_BUF_PLANE0_MODIFIER_HI_EXT,(EGLint)(mod>>32))} A(EGL_NONE,EGL_NONE)
  PFNEGLCREATEIMAGEKHRPROC cimg=(PFNEGLCREATEIMAGEKHRPROC)eglGetProcAddress("eglCreateImageKHR"); PFNGLEGLIMAGETARGETTEXTURE2DOESPROC tgt=(PFNGLEGLIMAGETARGETTEXTURE2DOESPROC)eglGetProcAddress("glEGLImageTargetTexture2DOES");
  EGLImageKHR img=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,at); if(img==EGL_NO_IMAGE_KHR){printf("FAIL import 0x%x\n",eglGetError());return 7;}
  GLuint tex;glGenTextures(1,&tex);glBindTexture(GL_TEXTURE_2D,tex);tgt(GL_TEXTURE_2D,(GLeglImageOES)img);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
  GLuint rt,fb;glGenTextures(1,&rt);glBindTexture(GL_TEXTURE_2D,rt);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,W,H,0,GL_RGBA,GL_UNSIGNED_BYTE,0);
  glGenFramebuffers(1,&fb);glBindFramebuffer(GL_FRAMEBUFFER,fb);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,rt,0);
  glBindTexture(GL_TEXTURE_2D,tex);
  const char*vs="attribute vec2 p;varying vec2 t;void main(){t=p*0.5+0.5;gl_Position=vec4(p,0,1);}";
  const char*fs="precision mediump float;varying vec2 t;uniform sampler2D s;void main(){gl_FragColor=vec4(texture2D(s,t).rgb,1.0);}";
  GLuint v=glCreateShader(GL_VERTEX_SHADER),f=glCreateShader(GL_FRAGMENT_SHADER);glShaderSource(v,1,&vs,0);glCompileShader(v);glShaderSource(f,1,&fs,0);glCompileShader(f);
  GLuint pr=glCreateProgram();glAttachShader(pr,v);glAttachShader(pr,f);glBindAttribLocation(pr,0,"p");glLinkProgram(pr);glUseProgram(pr);
  float q[]={-1,-1,1,-1,-1,1,1,1};glEnableVertexAttribArray(0);glVertexAttribPointer(0,2,GL_FLOAT,0,0,q);glViewport(0,0,W,H);glDrawArrays(GL_TRIANGLE_STRIP,0,4);glFinish();
  unsigned char*px=malloc(W*H*4);glReadPixels(0,0,W,H,GL_RGBA,GL_UNSIGNED_BYTE,px); int bad=0;
  for(int by=0;by<4;by++)for(int bx=0;bx<8;bx++){int x=bx*(W/8)+W/16,y=by*(H/4)+H/8;unsigned c=BAR[(bx+by)%8];unsigned char*p=px+((size_t)y*W+x)*4; /* c is 0xRRGGBB, px is RGBA */
    int d=abs(p[0]-(int)((c>>16)&255))+abs(p[1]-(int)((c>>8)&255))+abs(p[2]-(int)(c&255)); if(d>6){bad++;if(bad<=4)printf("  MISMATCH (%d,%d) got %d,%d,%d expected %d,%d,%d\n",bx,by,p[0],p[1],p[2],c&255,(c>>8)&255,(c>>16)&255);}}
  printf("XR24 CONTROL RESULT: %d/32 cells wrong\n",bad); return bad!=0; }
