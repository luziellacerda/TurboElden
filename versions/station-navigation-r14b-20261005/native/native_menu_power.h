// Power policy scoped to GuiStore rendering, never to an emulator's frame loop.
// SDL's monotonic counter and sleeping delay avoid a busy-wait FPS limiter.
static unsigned menuLastInteraction;
static void noteStoreInteraction(){menuLastInteraction=fn<unsigned(*)()>(0x39e240)();}
static int storeMenuTargetFps(bool dialog,bool interacting,bool loading){
 // A visible carousel has ongoing LED/button/scene animation even without touch.
 // Keep its existing interactive cadence; only a covering idle dialog uses 15.
 // Video clips still decode at their encoded 30 fps. Emulator and background
 // lifecycle are outside this GuiStore-only policy and remain unchanged.
 return !dialog||interacting||loading?60:15;
}
static void paceStoreMenu(void*p){
 static U(*counter)();static U(*frequency)();static void(*delay)(unsigned);
 static bool searched;static U hz,next;static int previousFps;
 if(!searched){
  searched=true;void*sdl=dlopen("libSDL2.so",2);
  counter=(U(*)())dlsym(sdl,"SDL_GetPerformanceCounter");
  frequency=(U(*)())dlsym(sdl,"SDL_GetPerformanceFrequency");
  delay=(void(*)(unsigned))dlsym(sdl,"SDL_Delay");
  if(frequency)hz=frequency();
 }
 if(!counter||!delay||!hz)return;
 unsigned tick=fn<unsigned(*)()>(0x39e240)();
 bool dialog=modal(p);
 bool interacting=menuLastInteraction&&(unsigned)(tick-menuLastInteraction)<650;
 int fps=storeMenuTargetFps(dialog,interacting,at<int>(p,0x370)!=3);
 U now=counter(),period=hz/(U)fps;
 if(!next||fps!=previousFps||now>next+hz/4){
  next=now;previousFps=fps;
  __android_log_print(4,"TurboCarousel","MENU power target=%d fps; context=%s",fps,dialog?"dialog":systemsMode?"platforms":"games");
 }
 if(next>now){
  U milliseconds=((next-now)*1000+hz-1)/hz;
  if(milliseconds>0&&milliseconds<=67)delay((unsigned)milliseconds);
  now=counter();
 }
 // Keep a monotonic schedule without catching up with bursts after suspension.
 next=(now>next+period?now:next)+period;
}
