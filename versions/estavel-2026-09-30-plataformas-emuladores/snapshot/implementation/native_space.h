// Uso autorizado: consulte AGENTS.md e USO-E-ACESSO.md; direitos de terceiros preservados.
// Clouds-only background. Aircraft and stars have no rendering or update work.
static void drawNativeClouds(float,float,float);
static void drawNativeSpace(float w,float h){
 if(w<=0||h<=0)return;
 fn<void(*)(float,float,float,float,unsigned,unsigned,bool,int,int)>(0x2e2c38)(0,0,w,h,0x020604ff,0x060A08ff,false,4,5);
 static unsigned started;unsigned now=fn<unsigned(*)()>(0x39e240)();if(!started)started=now;float t=(unsigned)(now-started)*.001f;
 drawNativeClouds(w,h,t);
}
