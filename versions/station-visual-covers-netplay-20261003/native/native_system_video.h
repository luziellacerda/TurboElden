// Shared GL/JNI utilities only. No atlas player or fallback video exists.
#include <jni.h>
static jfloatArray systemVideoTransform;
static unsigned systemVideoProgram;
static int systemVideoMVP,systemVideoUV;
static void*systemVideoContext;
static JNIEnv* videoEnv(){
 static JNIEnv*(*get)();
 if(!get)get=(JNIEnv*(*)())dlsym(dlopen("libSDL2.so",2),"SDL_AndroidGetJNIEnv");
 return get?get():nullptr;
}
static jobject videoActivity(){
 static jobject(*get)();
 if(!get)get=(jobject(*)())dlsym(dlopen("libSDL2.so",2),"SDL_AndroidGetActivity");
 return get?get():nullptr;
}
static void* videoGLContext(){
 static void*(*get)();
 if(!get)get=(void*(*)())dlsym(dlopen("libEGL.so",2),"eglGetCurrentContext");
 return get?get():nullptr;
}
static bool videoJniException(JNIEnv*env){
 if(!env->ExceptionCheck())return false;
 env->ExceptionClear();log("SYSTEM VIDEO Java unavailable; retain decoded video frame when available");return true;
}
static bool ensureVideoJni(JNIEnv*env){
 if(!env)return false;
 if(!systemVideoTransform){jfloatArray a=env->NewFloatArray(16);if(a){systemVideoTransform=(jfloatArray)env->NewGlobalRef(a);env->DeleteLocalRef(a);}}
 return !videoJniException(env)&&systemVideoTransform;
}
static void stopSystemVideo(){stopSystemVideo720();}
struct VideoExternalBinding{
 int original;
 VideoExternalBinding(){spaceGL.ActiveTexture(0x84c0);laserGL.GetIntegerv(0x8d67,&original);}
 ~VideoExternalBinding(){spaceGL.ActiveTexture(0x84c0);spaceGL.BindTexture(0x8d65,(unsigned)original);}
};
static bool ensureSystemVideoProgram(){
 void*context=videoGLContext();
 if(systemVideoContext!=context){systemVideoContext=context;systemVideoProgram=0;}
 auto&g=laserGL;
 if(systemVideoProgram&&g.IsProgram(systemVideoProgram))return true;
 const char*vs="#version 100\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;uniform mat4 videoTransform;varying vec2 videoUV;void main(){gl_Position=MVPMatrix*VertexCoord;videoUV=(videoTransform*vec4(TexCoord,0.,1.)).xy;}";
 const char*fs="#version 100\n#extension GL_OES_EGL_image_external : require\nprecision mediump float;uniform samplerExternalOES videoFrame;varying vec2 videoUV;void main(){gl_FragColor=vec4(texture2D(videoFrame,videoUV).rgb,1.);}";
 systemVideoProgram=compileSpaceProgram(vs,fs,true);if(!systemVideoProgram)return false;
 systemVideoMVP=g.GetUniformLocation(systemVideoProgram,"MVPMatrix");systemVideoUV=g.GetUniformLocation(systemVideoProgram,"videoTransform");
 g.UseProgram(systemVideoProgram);spaceGL.Uniform1i(g.GetUniformLocation(systemVideoProgram,"videoFrame"),0);
 log("SYSTEM VIDEO native card ready; one 720p video per visible card; native loop; no atlas or second layer");return true;
}
