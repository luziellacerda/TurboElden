package org.emulationstation.frontend.netplay;

import android.animation.ValueAnimator;
import android.app.*;
import android.content.*;
import android.graphics.*;
import android.opengl.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.nio.*;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

/** Exact carousel GLES shader; cached artwork; rendering only while visible. */
final class StationOnlineCoverView extends FrameLayout implements TextureView.SurfaceTextureListener {
    private final ImageView original;
    private TextureView texture;
    private final Rect visibleRect=new Rect();
    private final Activity owner;
    private Bitmap bitmap;
    private int model=-1;
    private Worker worker;
    private boolean resumed=true,scheduled;
    private long elapsed,last;
    private final ViewTreeObserver.OnPreDrawListener visibility=()->{motion();return true;};
    private final Runnable frame=()->{
        scheduled=false;if(!visible()){last=0;return;}
        long now=SystemClock.uptimeMillis();if(last!=0&&ValueAnimator.areAnimatorsEnabled())elapsed+=Math.min(100,now-last);last=now;
        worker.draw(bitmap,model,texture.getWidth(),texture.getHeight(),(int)((elapsed*60L/1000L)%1000000));
        if(ValueAnimator.areAnimatorsEnabled())schedule();
    };
    private final Application.ActivityLifecycleCallbacks lifecycle=new Application.ActivityLifecycleCallbacks(){
        public void onActivityResumed(Activity a){if(a==owner){resumed=true;motion();}}
        public void onActivityPaused(Activity a){if(a==owner){resumed=false;motion();}}
        public void onActivityCreated(Activity a,Bundle b){} public void onActivityStarted(Activity a){}
        public void onActivityStopped(Activity a){} public void onActivitySaveInstanceState(Activity a,Bundle b){}
        public void onActivityDestroyed(Activity a){}
    };
    StationOnlineCoverView(Context c){
        super(c);Context a=c;while(a instanceof ContextWrapper&&!(a instanceof Activity))a=((ContextWrapper)a).getBaseContext();owner=a instanceof Activity?(Activity)a:null;
        original=new ImageView(c);original.setScaleType(ImageView.ScaleType.FIT_CENTER);addView(original,new LayoutParams(-1,-1));
        texture=new TextureView(c);texture.setOpaque(false);texture.setSurfaceTextureListener(this);addView(texture,new LayoutParams(-1,-1));
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_NO);
    }
    static int profile(String value){
        String k=value==null?"":value.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]","");
        if(k.equals("gamecube")||k.equals("nintendogamecube")||k.equals("gc"))return 5;
        if(k.equals("wiiu")||k.equals("nintendowiiu"))return 6;
        if(k.equals("switch")||k.equals("nintendoswitch"))return 7;
        if(k.equals("playstation")||k.equals("playstation1")||k.equals("ps1")||k.equals("psx"))return 8;
        if(k.equals("dreamcast")||k.equals("segadreamcast"))return 4;
        if(k.equals("neogeo")||k.equals("neogeocd"))return 3;
        if(k.equals("n64")||k.equals("n64br")||k.startsWith("nintendo64"))return 2;
        if(k.startsWith("megadrive")||k.equals("genesis"))return 1;
        if(k.startsWith("supernintendo")||k.equals("snes")||k.equals("snesbr"))return 0;
        return -1;
    }
    void setPlatform(String value){int next=profile(value);if(next!=model){model=next;refresh();}}
    void setImageBitmap(Bitmap value){if(bitmap==value)return;bitmap=value;original.setImageBitmap(value);elapsed=0;last=0;refresh();requestLayout();}
    float aspect(){return bitmap==null?2f/3f:(float)bitmap.getWidth()/bitmap.getHeight();}
    private void refresh(){texture.setAlpha(0);motion();}
    private boolean visible(){return worker!=null&&!worker.failed&&bitmap!=null&&model>=0&&resumed&&isAttachedToWindow()&&isShown()&&getWindowVisibility()==VISIBLE&&hasWindowFocus()&&getGlobalVisibleRect(visibleRect)&&!visibleRect.isEmpty();}
    private void schedule(){if(!scheduled){scheduled=true;postDelayed(frame,34);}}
    private void motion(){if(frame==null)return;if(visible()){if(ValueAnimator.areAnimatorsEnabled()||texture.getAlpha()==0)schedule();}else{removeCallbacks(frame);scheduled=false;last=0;}}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();resumed=true;if(owner!=null)owner.getApplication().registerActivityLifecycleCallbacks(lifecycle);getViewTreeObserver().addOnPreDrawListener(visibility);motion();}
    @Override protected void onDetachedFromWindow(){resumed=false;removeCallbacks(frame);scheduled=false;if(owner!=null)owner.getApplication().unregisterActivityLifecycleCallbacks(lifecycle);if(getViewTreeObserver().isAlive())getViewTreeObserver().removeOnPreDrawListener(visibility);super.onDetachedFromWindow();}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);motion();}
    @Override protected void onVisibilityChanged(View v,int state){super.onVisibilityChanged(v,state);motion();}
    @Override protected void onWindowVisibilityChanged(int state){super.onWindowVisibilityChanged(state);motion();}
    public void onSurfaceTextureAvailable(SurfaceTexture surface,int w,int h){worker=new Worker(surface);motion();}
    public void onSurfaceTextureSizeChanged(SurfaceTexture surface,int w,int h){refresh();}
    public boolean onSurfaceTextureDestroyed(SurfaceTexture surface){Worker old=worker;worker=null;motion();if(old!=null)old.close();else surface.release();return false;}
    public void onSurfaceTextureUpdated(SurfaceTexture surface){}

    private final class Worker {
        final HandlerThread thread=new HandlerThread("Station-cover-GLES");
        final Handler handler;final SurfaceTexture source;final AtomicBoolean queued=new AtomicBoolean();
        volatile boolean closed,failed;
        EGLDisplay display=EGL14.EGL_NO_DISPLAY;EGLContext context=EGL14.EGL_NO_CONTEXT;EGLSurface window=EGL14.EGL_NO_SURFACE;Surface surface;
        int program,tex,clock,modelLocation;Bitmap uploaded;
        final FloatBuffer vertices=ByteBuffer.allocateDirect(64).order(ByteOrder.nativeOrder()).asFloatBuffer();
        Worker(SurfaceTexture value){source=value;thread.start();handler=new Handler(thread.getLooper());}
        int stage(int type,String prefix){int shader=GLES20.glCreateShader(type);GLES20.glShaderSource(shader,prefix+StationCoverLightingShader.SOURCE);GLES20.glCompileShader(shader);int[] ok={0};GLES20.glGetShaderiv(shader,GLES20.GL_COMPILE_STATUS,ok,0);if(ok[0]==0){String log=GLES20.glGetShaderInfoLog(shader);GLES20.glDeleteShader(shader);throw new IllegalStateException(log);}return shader;}
        int loc(String name){return GLES20.glGetUniformLocation(program,name);}
        void init(){
            display=EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);int[] version=new int[2];if(!EGL14.eglInitialize(display,version,0,version,1))throw new IllegalStateException("EGL initialize");
            int[] config={EGL14.EGL_RENDERABLE_TYPE,EGL14.EGL_OPENGL_ES2_BIT,EGL14.EGL_SURFACE_TYPE,EGL14.EGL_WINDOW_BIT,EGL14.EGL_RED_SIZE,8,EGL14.EGL_GREEN_SIZE,8,EGL14.EGL_BLUE_SIZE,8,EGL14.EGL_ALPHA_SIZE,8,EGL14.EGL_NONE};
            EGLConfig[] choices=new EGLConfig[1];int[] count=new int[1];if(!EGL14.eglChooseConfig(display,config,0,choices,0,1,count,0)||count[0]==0)throw new IllegalStateException("EGL config");
            context=EGL14.eglCreateContext(display,choices[0],EGL14.EGL_NO_CONTEXT,new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION,2,EGL14.EGL_NONE},0);
            surface=new Surface(source);window=EGL14.eglCreateWindowSurface(display,choices[0],surface,new int[]{EGL14.EGL_NONE},0);
            if(!EGL14.eglMakeCurrent(display,window,window,context))throw new IllegalStateException("EGL current");
            int v=stage(GLES20.GL_VERTEX_SHADER,"#version 100\n#define VERTEX\n"),f=stage(GLES20.GL_FRAGMENT_SHADER,"#version 100\n#define FRAGMENT\n");
            program=GLES20.glCreateProgram();GLES20.glAttachShader(program,v);GLES20.glAttachShader(program,f);GLES20.glBindAttribLocation(program,0,"VertexCoord");GLES20.glBindAttribLocation(program,1,"TexCoord");GLES20.glBindAttribLocation(program,2,"COLOR");GLES20.glLinkProgram(program);GLES20.glDeleteShader(v);GLES20.glDeleteShader(f);
            int[] ok={0};GLES20.glGetProgramiv(program,GLES20.GL_LINK_STATUS,ok,0);if(ok[0]==0)throw new IllegalStateException("Cover GLES link");
            GLES20.glUseProgram(program);GLES20.glUniformMatrix4fv(loc("MVPMatrix"),1,false,new float[]{1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1},0);
            GLES20.glUniform1i(loc("u_tex"),0);GLES20.glUniform1f(loc("saturation"),1);GLES20.glUniform1f(loc("ledGain"),1.6f);GLES20.glUniform1f(loc("sheenGain"),0);clock=loc("FrameCount");modelLocation=loc("magazineModel");
            GLES20.glVertexAttrib4f(2,1,1,1,1);int[] ids={0};GLES20.glGenTextures(1,ids,0);tex=ids[0];GLES20.glBindTexture(GLES20.GL_TEXTURE_2D,tex);
            GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D,GLES20.GL_TEXTURE_MIN_FILTER,GLES20.GL_LINEAR);GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D,GLES20.GL_TEXTURE_MAG_FILTER,GLES20.GL_LINEAR);GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D,GLES20.GL_TEXTURE_WRAP_S,GLES20.GL_CLAMP_TO_EDGE);GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D,GLES20.GL_TEXTURE_WRAP_T,GLES20.GL_CLAMP_TO_EDGE);
            GLES20.glUniform4f(loc("ledColor"),.659f,.333f,.969f,1);
            android.util.Log.i("StationCover","Shared carousel GLES engine ready");
        }
        void draw(Bitmap image,int model,int w,int h,int frame){
            if(closed||failed||w<1||h<1||!queued.compareAndSet(false,true))return;
            handler.post(()->{try{
                if(closed)return;if(program==0)init();
                if(uploaded!=image){int iw=image.getWidth(),ih=image.getHeight();int[] pixels=new int[iw*ih];image.getPixels(pixels,0,iw,0,0,iw,ih);
                    ByteBuffer rgba=ByteBuffer.allocateDirect(iw*ih*4);for(int y=ih-1;y>=0;y--)for(int x=0;x<iw;x++){int c=pixels[y*iw+x];rgba.put((byte)(c>>16)).put((byte)(c>>8)).put((byte)c).put((byte)(c>>24));}rgba.flip();GLES20.glTexImage2D(GLES20.GL_TEXTURE_2D,0,GLES20.GL_RGBA,iw,ih,0,GLES20.GL_RGBA,GLES20.GL_UNSIGNED_BYTE,rgba);uploaded=image;}
                GLES20.glViewport(0,0,w,h);GLES20.glClearColor(0,0,0,0);GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT);
                float fit=Math.min((float)w/image.getWidth(),(float)h/image.getHeight()),sx=image.getWidth()*fit/w,sy=image.getHeight()*fit/h;
                vertices.clear();vertices.put(-sx).put(sy).put(0).put(1).put(-sx).put(-sy).put(0).put(0).put(sx).put(sy).put(1).put(1).put(sx).put(-sy).put(1).put(0).position(0);
                GLES20.glEnableVertexAttribArray(0);GLES20.glEnableVertexAttribArray(1);GLES20.glVertexAttribPointer(0,2,GLES20.GL_FLOAT,false,16,vertices);vertices.position(2);GLES20.glVertexAttribPointer(1,2,GLES20.GL_FLOAT,false,16,vertices);
                GLES20.glUniform1i(clock,frame);GLES20.glUniform1f(modelLocation,model);GLES20.glDrawArrays(GLES20.GL_TRIANGLE_STRIP,0,4);
                if(!EGL14.eglSwapBuffers(display,window))throw new IllegalStateException("EGL swap");
                post(()->{if(worker==this&&bitmap==image&&!closed)texture.setAlpha(1);});
            }catch(RuntimeException e){failed=true;android.util.Log.w("StationCover","Shared cover renderer unavailable: "+e.getMessage());post(()->{texture.setAlpha(0);motion();});}finally{queued.set(false);}});
        }
        void close(){closed=true;handler.post(()->{
            if(display!=EGL14.EGL_NO_DISPLAY){if(program!=0)GLES20.glDeleteProgram(program);if(tex!=0)GLES20.glDeleteTextures(1,new int[]{tex},0);EGL14.eglMakeCurrent(display,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_CONTEXT);if(window!=EGL14.EGL_NO_SURFACE)EGL14.eglDestroySurface(display,window);if(context!=EGL14.EGL_NO_CONTEXT)EGL14.eglDestroyContext(display,context);EGL14.eglReleaseThread();EGL14.eglTerminate(display);}
            if(surface!=null)surface.release();source.release();uploaded=null;thread.quitSafely();
        });}
    }
}
