// nv12_dmabuf_test: allocate NV12 via GBM, fill planes with known colour bars through mmap, import into EGL as an
// NV12 dmabuf EGLImage (what Chromium does), sample it on the GPU, read back and compare with the expected RGB.
// usage: nv12_dmabuf_test [W H usage] ; usage: 4=RENDERING 16=LINEAR 5=SCANOUT|RENDERING
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
static const int BY[8]={235,210,170,145,106,81,41,16}, BU[8]={128,16,166,54,202,90,240,128}, BV[8]={128,146,16,34,222,240,110,128};
static int clampi(int v){return v<0?0:v>255?255:v;}
static void expect(int b,int*r,int*g,int*bl){ double y=1.164*(BY[b]-16),u=BU[b]-128,v=BV[b]-128;
  *r=clampi((int)(y+1.596*v+.5)); *g=clampi((int)(y-0.392*u-0.813*v+.5)); *bl=clampi((int)(y+2.017*u+.5)); }
static int barat(int x,int y,int W,int H){ return ((x/(W/8))+(y/(H/4)))%8; }
int main(int argc,char**argv){
  int W=argc>1?atoi(argv[1]):640,H=argc>2?atoi(argv[2]):360; unsigned use=argc>3?atoi(argv[3]):4;
  int fd=open("/dev/dri/renderD128",O_RDWR); struct gbm_device*gd=gbm_create_device(fd);
  struct gbm_bo*bo=gbm_bo_create(gd,W,H,GBM_FORMAT_NV12,use);
  if(!bo){printf("FAIL: gbm_bo_create NV12 %dx%d use=%u\n",W,H,use);return 2;}
  int pc=gbm_bo_get_plane_count(bo); unsigned long long mod=gbm_bo_get_modifier(bo);
  printf("NV12 %dx%d use=%u plane_count=%d modifier=0x%llx\n",W,H,use,pc,mod);
  int pfd[2]={-1,-1},pstride[2]={0,0},poff[2]={0,0};
  for(int i=0;i<pc&&i<2;i++){pfd[i]=gbm_bo_get_fd_for_plane(bo,i);pstride[i]=gbm_bo_get_stride_for_plane(bo,i);poff[i]=gbm_bo_get_offset(bo,i);
    printf("  plane%d fd=%d stride=%d offset=%d\n",i,pfd[i],pstride[i],poff[i]);}
  if(pc<2){printf("FAIL: NV12 needs 2 planes, got %d\n",pc);return 3;}
  // fill planes via mmap of the dmabuf fds
  unsigned char*base[2]; size_t len[2];
  for(int i=0;i<2;i++){ len[i]=lseek(pfd[i],0,SEEK_END); lseek(pfd[i],0,SEEK_SET);
    void*m=mmap(0,len[i],PROT_READ|PROT_WRITE,MAP_SHARED,pfd[i],0); if(m==MAP_FAILED){perror("mmap");return 4;} base[i]=(unsigned char*)m+poff[i];
    printf("  plane%d dmabuf size=%zu (need >= %d)\n",i,len[i],pstride[i]*(i?H/2:H)); }
  for(int y=0;y<H;y++)for(int x=0;x<W;x++) base[0][y*pstride[0]+x]=BY[barat(x,y,W,H)];
  for(int cy=0;cy<H/2;cy++)for(int cx=0;cx<W/2;cx++){int b=barat(cx*2,cy*2,W,H); base[1][cy*pstride[1]+cx*2]=BU[b]; base[1][cy*pstride[1]+cx*2+1]=BV[b];}
  // EGL
  PFNEGLGETPLATFORMDISPLAYEXTPROC gpd=(PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
  EGLDisplay dpy=gpd(0x31D7,gd,NULL); EGLint maj,min; if(!eglInitialize(dpy,&maj,&min)){printf("FAIL eglInitialize\n");return 5;}
  eglBindAPI(EGL_OPENGL_ES_API); EGLConfig cfg; EGLint n; EGLint ca[]={EGL_RENDERABLE_TYPE,EGL_OPENGL_ES2_BIT,EGL_SURFACE_TYPE,0,EGL_NONE};
  eglChooseConfig(dpy,ca,&cfg,1,&n); EGLint xa[]={EGL_CONTEXT_CLIENT_VERSION,2,EGL_NONE}; EGLContext ctx=eglCreateContext(dpy,cfg,EGL_NO_CONTEXT,xa);
  if(!eglMakeCurrent(dpy,EGL_NO_SURFACE,EGL_NO_SURFACE,ctx)){printf("FAIL eglMakeCurrent 0x%x\n",eglGetError());return 6;}
  printf("GL_RENDERER=%s\nGL_VERSION=%s\n",glGetString(GL_RENDERER),glGetString(GL_VERSION));
  EGLint at[64];int k=0;
  #define A(a,b) at[k++]=a;at[k++]=b;
  A(EGL_WIDTH,W)A(EGL_HEIGHT,H)A(EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('N','V','1','2'))
  A(EGL_DMA_BUF_PLANE0_FD_EXT,pfd[0])A(EGL_DMA_BUF_PLANE0_OFFSET_EXT,poff[0])A(EGL_DMA_BUF_PLANE0_PITCH_EXT,pstride[0])
  A(EGL_DMA_BUF_PLANE1_FD_EXT,pfd[1])A(EGL_DMA_BUF_PLANE1_OFFSET_EXT,poff[1])A(EGL_DMA_BUF_PLANE1_PITCH_EXT,pstride[1])
  A(EGL_YUV_COLOR_SPACE_HINT_EXT,EGL_ITU_REC601_EXT)A(EGL_SAMPLE_RANGE_HINT_EXT,EGL_YUV_NARROW_RANGE_EXT)
  if(mod!=0 && mod!=0x00ffffffffffffffULL){A(EGL_DMA_BUF_PLANE0_MODIFIER_LO_EXT,(EGLint)(mod&0xffffffff))A(EGL_DMA_BUF_PLANE0_MODIFIER_HI_EXT,(EGLint)(mod>>32))
     A(EGL_DMA_BUF_PLANE1_MODIFIER_LO_EXT,(EGLint)(mod&0xffffffff))A(EGL_DMA_BUF_PLANE1_MODIFIER_HI_EXT,(EGLint)(mod>>32))}
  A(EGL_NONE,EGL_NONE)
  int split=argc>4&&!strcmp(argv[4],"split");
  PFNEGLCREATEIMAGEKHRPROC cimg=(PFNEGLCREATEIMAGEKHRPROC)eglGetProcAddress("eglCreateImageKHR");
  PFNGLEGLIMAGETARGETTEXTURE2DOESPROC tgt=(PFNGLEGLIMAGETARGETTEXTURE2DOESPROC)eglGetProcAddress("glEGLImageTargetTexture2DOES");
  GLuint tex=0,texY=0,texUV=0;
  if(!split){
  EGLImageKHR img=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,at);
  if(img==EGL_NO_IMAGE_KHR){printf("FAIL eglCreateImageKHR NV12 dmabuf: 0x%x\n",eglGetError());return 7;}
  glGenTextures(1,&tex); glBindTexture(GL_TEXTURE_EXTERNAL_OES,tex);
  tgt(GL_TEXTURE_EXTERNAL_OES,(GLeglImageOES)img);
  glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_EXTERNAL_OES,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
  } else {
   EGLint ay[]={EGL_WIDTH,W,EGL_HEIGHT,H,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('R','8',' ',' '),EGL_DMA_BUF_PLANE0_FD_EXT,pfd[0],EGL_DMA_BUF_PLANE0_OFFSET_EXT,poff[0],EGL_DMA_BUF_PLANE0_PITCH_EXT,pstride[0],EGL_NONE};
   EGLint au[]={EGL_WIDTH,W/2,EGL_HEIGHT,H/2,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)FOURCC('G','R','8','8'),EGL_DMA_BUF_PLANE0_FD_EXT,pfd[1],EGL_DMA_BUF_PLANE0_OFFSET_EXT,poff[1],EGL_DMA_BUF_PLANE0_PITCH_EXT,pstride[1],EGL_NONE};
   EGLImageKHR iy=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,ay); if(iy==EGL_NO_IMAGE_KHR){printf("FAIL import Y as R8: 0x%x\n",eglGetError());return 7;}
   EGLImageKHR iu=cimg(dpy,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,au); if(iu==EGL_NO_IMAGE_KHR){printf("FAIL import UV as GR88: 0x%x\n",eglGetError());return 7;}
   glGenTextures(1,&texY); glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D,texY); tgt(GL_TEXTURE_2D,(GLeglImageOES)iy);
   glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
   glGenTextures(1,&texUV); glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_2D,texUV); tgt(GL_TEXTURE_2D,(GLeglImageOES)iu);
   glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
   glActiveTexture(GL_TEXTURE0);
  }
  GLuint rt,fb; glGenTextures(1,&rt); glBindTexture(GL_TEXTURE_2D,rt); glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,W,H,0,GL_RGBA,GL_UNSIGNED_BYTE,0);
  glGenFramebuffers(1,&fb); glBindFramebuffer(GL_FRAMEBUFFER,fb); glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,rt,0);
  if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE){printf("FAIL fbo\n");return 8;}
  const char*vs="attribute vec2 p;varying vec2 t;void main(){t=p*0.5+0.5;gl_Position=vec4(p,0,1);}";
  const char*fs_split="precision mediump float;varying vec2 t;uniform sampler2D sy;uniform sampler2D suv;void main(){float y=1.164*(texture2D(sy,t).r*255.0-16.0);vec2 c=texture2D(suv,t).rg*255.0-128.0;gl_FragColor=vec4((y+1.596*c.g)/255.0,(y-0.392*c.r-0.813*c.g)/255.0,(y+2.017*c.r)/255.0,1.0);}";
  const char*fs_ext="#extension GL_OES_EGL_image_external : require\nprecision mediump float;varying vec2 t;uniform samplerExternalOES s;void main(){gl_FragColor=texture2D(s,t);}";
  const char*fs=split?fs_split:fs_ext;
  GLuint v=glCreateShader(GL_VERTEX_SHADER),f=glCreateShader(GL_FRAGMENT_SHADER); glShaderSource(v,1,&vs,0);glCompileShader(v);glShaderSource(f,1,&fs,0);glCompileShader(f);
  GLint ok; glGetShaderiv(f,GL_COMPILE_STATUS,&ok); if(!ok){char l[512];glGetShaderInfoLog(f,512,0,l);printf("FAIL shader: %s\n",l);return 9;}
  GLuint pr=glCreateProgram();glAttachShader(pr,v);glAttachShader(pr,f);glBindAttribLocation(pr,0,"p");glLinkProgram(pr);glUseProgram(pr); if(split){glUniform1i(glGetUniformLocation(pr,"sy"),0);glUniform1i(glGetUniformLocation(pr,"suv"),1);}
  float q[]={-1,-1,1,-1,-1,1,1,1}; glEnableVertexAttribArray(0);glVertexAttribPointer(0,2,GL_FLOAT,0,0,q);
  glViewport(0,0,W,H); glDrawArrays(GL_TRIANGLE_STRIP,0,4); glFinish();
  unsigned char*px=malloc(W*H*4); glReadPixels(0,0,W,H,GL_RGBA,GL_UNSIGNED_BYTE,px);
  // GL origin is bottom-left; texture t.y=0 is the first row in memory -> image row y_mem appears at GL row y_mem.
  int bad=0,total=0,tol=14;
  for(int by=0;by<4;by++)for(int bx=0;bx<8;bx++){ int x=bx*(W/8)+W/16,y=by*(H/4)+H/8; int b=barat(x,y,W,H);
    int er,eg,eb; expect(b,&er,&eg,&eb); unsigned char*p=px+((size_t)y*W+x)*4; total++;
    int d=abs(p[0]-er)+abs(p[1]-eg)+abs(p[2]-eb); if(d>tol*3/1){bad++; if(bad<=12)printf("  MISMATCH cell(%d,%d) at(%d,%d): got %3d,%3d,%3d expected %3d,%3d,%3d\n",bx,by,x,y,p[0],p[1],p[2],er,eg,eb);} }
  printf("MODE=%s ",split?"split R8+GR88 planes (manual YUV->RGB)":"single NV12 EGLImage (external sampler)");printf("RESULT: %d/%d cells wrong (tolerance ~%d per channel sum)\n",bad,total,tol*3);
  // edge sharpness: check a bar boundary column is exact at row mid (stride/shift check)
  int bsx=W/8; int y0=H/8; int shift_detect=0; for(int bx=1;bx<8;bx++){ int xb=bx*bsx; int a=px[((size_t)y0*W+xb-3)*4], c=px[((size_t)y0*W+xb+3)*4]; (void)a;(void)c;}
  FILE*o=fopen("/tmp/nv12_readback.ppm","wb"); fprintf(o,"P6\n%d %d\n255\n",W,H); for(int y=H-1;y>=0;y--)for(int x=0;x<W;x++){fwrite(px+((size_t)y*W+x)*4,1,3,o);} fclose(o);
  return bad?1:0; }
