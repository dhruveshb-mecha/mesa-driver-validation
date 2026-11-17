// vblank rate of a DRM card: relative DRM_IOCTL_WAIT_VBLANK x N, prints measured Hz per crtc index 0..2
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <sys/ioctl.h>
#include <drm/drm.h>
static double now(){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec*1e-9;}
int main(int argc,char**argv){
  int fd=open(argv[1],O_RDWR); if(fd<0){perror("open");return 1;}
  for(int crtc=0;crtc<3;crtc++){
    union drm_wait_vblank vbl={0}; vbl.request.type=_DRM_VBLANK_RELATIVE|(crtc?(crtc<<_DRM_VBLANK_HIGH_CRTC_SHIFT)&_DRM_VBLANK_HIGH_CRTC_MASK:0); vbl.request.sequence=1;
    if(ioctl(fd,DRM_IOCTL_WAIT_VBLANK,&vbl)){printf("%s crtc%d: wait_vblank failed\n",argv[1],crtc);continue;}
    double t0=now(); unsigned s0=vbl.reply.sequence; int n=120;
    for(int i=0;i<n;i++){vbl.request.type=_DRM_VBLANK_RELATIVE|(crtc?(crtc<<_DRM_VBLANK_HIGH_CRTC_SHIFT)&_DRM_VBLANK_HIGH_CRTC_MASK:0);vbl.request.sequence=1; if(ioctl(fd,DRM_IOCTL_WAIT_VBLANK,&vbl))break;}
    double t1=now(); printf("%s crtc%d: %u vblanks in %.3f s = %.2f Hz (period %.2f ms)\n",argv[1],crtc,vbl.reply.sequence-s0,t1-t0,(vbl.reply.sequence-s0)/(t1-t0),1000*(t1-t0)/(vbl.reply.sequence-s0));
  }
  return 0;}
