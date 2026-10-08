package org.emulationstation.frontend.netplay;
import android.opengl.*;
public final class SharedCoverProbe {
 public static void main(String[] args){
  EGLDisplay d=EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);int[] v=new int[2];if(!EGL14.eglInitialize(d,v,0,v,1))throw new IllegalStateException("display");
  EGLConfig[] cs=new EGLConfig[1];int[] n=new int[1];EGL14.eglChooseConfig(d,new int[]{EGL14.EGL_RENDERABLE_TYPE,4,EGL14.EGL_SURFACE_TYPE,1,EGL14.EGL_RED_SIZE,8,EGL14.EGL_GREEN_SIZE,8,EGL14.EGL_BLUE_SIZE,8,EGL14.EGL_NONE},0,cs,0,1,n,0);
  EGLContext c=EGL14.eglCreateContext(d,cs[0],EGL14.EGL_NO_CONTEXT,new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION,2,EGL14.EGL_NONE},0);
  EGLSurface s=EGL14.eglCreatePbufferSurface(d,cs[0],new int[]{EGL14.EGL_WIDTH,16,EGL14.EGL_HEIGHT,16,EGL14.EGL_NONE},0);
  if(!EGL14.eglMakeCurrent(d,s,s,c))throw new IllegalStateException("context");
  int p=GLES20.glCreateProgram();int[] ok={0};
  for(int type:new int[]{GLES20.GL_VERTEX_SHADER,GLES20.GL_FRAGMENT_SHADER}){
   int shader=GLES20.glCreateShader(type);GLES20.glShaderSource(shader,"#version 100\n#define "+(type==GLES20.GL_VERTEX_SHADER?"VERTEX":"FRAGMENT")+"\n"+StationCoverLightingShader.SOURCE);GLES20.glCompileShader(shader);GLES20.glGetShaderiv(shader,GLES20.GL_COMPILE_STATUS,ok,0);
   if(ok[0]==0)throw new IllegalStateException(GLES20.glGetShaderInfoLog(shader));GLES20.glAttachShader(p,shader);GLES20.glDeleteShader(shader);
  }
  GLES20.glLinkProgram(p);GLES20.glGetProgramiv(p,GLES20.GL_LINK_STATUS,ok,0);if(ok[0]==0)throw new IllegalStateException(GLES20.glGetProgramInfoLog(p));
  System.out.println("R86_SHARED_CAROUSEL_GLES_COMPILE_LINK_OK "+GLES20.glGetString(GLES20.GL_RENDERER));
  GLES20.glDeleteProgram(p);EGL14.eglMakeCurrent(d,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_CONTEXT);EGL14.eglDestroySurface(d,s);EGL14.eglDestroyContext(d,c);EGL14.eglTerminate(d);
 }
}
