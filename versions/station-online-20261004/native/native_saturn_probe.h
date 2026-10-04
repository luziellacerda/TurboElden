// Temporary bounded diagnosis of the original Saturn frontend. No core options
// or engine state are changed; the readback occurs only at three frame counts.
static bool saturnProbeActive;
static unsigned saturnProbeFrame;
static UiString saturnPlayerProbeHook(const void*core,const void*game){
 saturnProbeActive=uiContains(strData(core),"yabasanshiro");saturnProbeFrame=0;
 UiString result=vitaRunHook(core,game);saturnProbeActive=false;return result;
}
static void saturnCoreProbeHook(void*core){
 fn<V>(0x2be414)(core);
 if(!saturnProbeActive)return;
 unsigned frame=++saturnProbeFrame;if(frame!=1&&frame!=120&&frame!=600)return;
 void*state=at<void*>((void*)base,0x3cf338);if(!state||!loadSpaceGL())return;
 void*gles=dlopen("libGLESv3.so",2);
 auto error=(unsigned(*)())dlsym(gles,"glGetError");
 auto read=(void(*)(int,int,int,int,unsigned,unsigned,void*))dlsym(gles,"glReadPixels");
 auto pixelStore=(void(*)(unsigned,int))dlsym(gles,"glPixelStorei");
 if(!error||!read||!pixelStore)return;
 auto&g=laserGL;auto&s=spaceGL;
 unsigned priorError=error();int fbo=0,readFbo=0,pack=0,align=0,row=0,rows=0,pixels=0,vao=0,program=0;
 g.GetIntegerv(0x8ca6,&fbo);g.GetIntegerv(0x8caa,&readFbo);g.GetIntegerv(0x88ed,&pack);
 g.GetIntegerv(0xd05,&align);g.GetIntegerv(0xd02,&row);g.GetIntegerv(0xd03,&rows);g.GetIntegerv(0xd04,&pixels);
 g.GetIntegerv(0x85b5,&vao);g.GetIntegerv(0x8b8d,&program);
 unsigned target=at<unsigned>(state,0x318),width=at<unsigned>(state,0x330),height=at<unsigned>(state,0x334);
 s.BindBuffer(0x88eb,0);pixelStore(0xd05,1);pixelStore(0xd02,0);pixelStore(0xd03,0);pixelStore(0xd04,0);
 s.BindFramebuffer(0x8d40,target);B rgb[4]={};int lit=0;
 if(width&&height)for(int y=1;y<=3;y++)for(int x=1;x<=3;x++){read(width*x/4,height*y/4,1,1,0x1908,0x1401,rgb);if(rgb[0]>8||rgb[1]>8||rgb[2]>8)lit++;}
 unsigned readError=error();s.BindFramebuffer(0x8ca9,fbo);s.BindFramebuffer(0x8ca8,readFbo);
 s.BindBuffer(0x88eb,pack);pixelStore(0xd05,align);pixelStore(0xd02,row);pixelStore(0xd03,rows);pixelStore(0xd04,pixels);
 __android_log_print(4,"TurboSaturnProbe","frame=%u nativeVideoCount=%lu fbo=%u bound=%d size=%ux%u lit=%d/9 errorBefore=%x readError=%x vao=%d program=%d",frame,at<U>(state,0x178),target,fbo,width,height,lit,priorError,readError,vao,program);
}
