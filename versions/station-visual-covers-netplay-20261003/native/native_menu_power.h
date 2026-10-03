// Power policy scoped to GuiStore rendering, never to an emulator's frame loop.
// SDL's monotonic counter and sleeping delay avoid a busy-wait FPS limiter.
static unsigned menuLastInteraction;
static void noteStoreInteraction(){menuLastInteraction=fn<unsigned(*)()>(0x39e240)();}
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
 float cursorDifference=at<float>(p,0xf4)-(float)at<int>(p,0xf0);
 bool transition=!dialog&&(cursorDifference>.002f||cursorDifference<-.002f);
 bool interacting=menuLastInteraction&&(unsigned)(tick-menuLastInteraction)<650;
 int fps=(interacting||transition||at<int>(p,0x370)!=3)?60:
         (!dialog&&systemsMode&&video720Asset(p,at<int>(p,0xf0))?30:15);
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
