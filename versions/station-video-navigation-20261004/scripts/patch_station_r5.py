from pathlib import Path
ROOT=Path(r'E:\ESTUDO APK\work\station-netplay-20261004')
N=ROOT/'native'
def edit(name,a,b):
    p=N/name;s=p.read_text('utf-8');assert a in s,(name,a[:100]);p.write_text(s.replace(a,b),encoding='utf-8')

edit('native_carousel.cpp','static void stopSystemVideo720();','static void stopSystemVideo720();\nstatic void pauseSystemVideo720();')
edit('native_carousel.cpp','stopSystemVideo();lastSystem=','pauseSystemVideo720();lastSystem=')
edit('native_carousel.cpp','if(!systemsMode||modal(p))stopSystemVideo();','if(!systemsMode||modal(p))pauseSystemVideo720();')
edit('native_carousel.cpp','if(p==settingsBackText||isStoreUiLabel(p))return;','if(p==settingsBackText||p==settingsNetplayText||isStoreUiLabel(p))return;')
edit('native_settings.h','static void drawSettingsSkinHook(void*p,void*matrix){','static void drawSettingsSkinHook(void*p,void*matrix){\n if(!at<B>(p,0x2050))return;')
edit('laser_assets.h','{"Super Nintendo",0xE50914FF,0xFCE6E8FF,0x00000000},','{"Super Nintendo",0xA855F7FF,0xF3E8FFFF,0x00000000},')
edit('laser_assets.h','{"Super Nintendo - BR",0xE50914FF,0xFCE6E8FF,0x00000000},','{"Super Nintendo - BR",0xA855F7FF,0xF3E8FFFF,0x00000000},')
edit('native_system_video720.h','#include "system_video720_assets.h"','#include "system_video720_assets.h"\n#include "video720_posters.h"\n#include "video720_policy.h"')
edit('native_system_video720.h','static unsigned video720NextStart;','static unsigned video720UseCounter;\nstatic unsigned video720PreviewProgram;static int video720PreviewMVP;')
edit('native_system_video720.h','struct Video720Frame {const char*asset;unsigned texture,retryAt;bool ready;};','struct Video720Frame {const char*asset;unsigned texture,retryAt,lastUse;bool ready;};')
edit('native_system_video720.h','static void clearVideo720Frames(){','static bool video720PaintedAsset(void*,const char*);\nstatic bool video720FrameTexture(Video720Frame*f){\n if(f->texture){f->lastUse=++video720UseCounter;return true;}\n Video720Frame*oldest=nullptr;unsigned count=0;\n for(auto&candidate:video720Frames)if(candidate.texture){\n  count++;\n  if(&candidate!=f&&(!gui||!video720PaintedAsset(gui,candidate.asset))&&\n      (!oldest||video720Older(candidate.lastUse,oldest->lastUse)))oldest=&candidate;\n }\n if(count>=video720TextureBudget){\n  if(!oldest)return false;\n  video720DeleteTexture(oldest->texture);oldest->texture=0;oldest->ready=false;\n }\n auto&s=spaceGL;s.GenTextures(1,&f->texture);if(!f->texture)return false;\n s.BindTexture(0x0de1,f->texture);s.TexImage2D(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,nullptr);\n s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);\n s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);\n f->lastUse=++video720UseCounter;return true;\n}\nstatic bool ensureVideo720PreviewProgram(){\n auto&g=laserGL;if(video720PreviewProgram&&g.IsProgram(video720PreviewProgram))return true;\n const char*vertex="#version 100\\nattribute vec4 VertexCoord;attribute vec2 TexCoord;uniform mat4 MVPMatrix;varying vec2 uv;void main(){uv=TexCoord;gl_Position=MVPMatrix*VertexCoord;}";\n const char*fragment="#version 100\\nprecision mediump float;uniform sampler2D frame;varying vec2 uv;void main(){gl_FragColor=vec4(texture2D(frame,uv).rgb,1.);}";\n video720PreviewProgram=compileSpaceProgram(vertex,fragment,true);if(!video720PreviewProgram)return false;\n video720PreviewMVP=g.GetUniformLocation(video720PreviewProgram,"MVPMatrix");g.UseProgram(video720PreviewProgram);\n spaceGL.Uniform1i(g.GetUniformLocation(video720PreviewProgram,"frame"),0);return true;\n}\nstatic void seedVideo720Preview(const char*asset){\n auto*f=video720Retained(asset,true);if(!f)return;f->lastUse=++video720UseCounter;if(f->ready)return;\n for(const auto&poster:video720Posters)if(video720Same(asset,poster.asset)){\n  spaceGL.ActiveTexture(0x84c0);if(!video720FrameTexture(f))return;\n  spaceGL.BindTexture(0x0de1,f->texture);\n  // First decoded video frame, packed bottom row first to match retained FBO UVs.\n  spaceGL.TexImage2D(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,poster.pixels);\n  f->ready=true;return;\n }\n}\nstatic void clearVideo720Frames(){')
edit('native_system_video720.h','if(!f->texture){\n  s.GenTextures(1,&f->texture);s.BindTexture(0x0de1,f->texture);\n  s.TexImage2D(0x0de1,0,0x1907,720,720,0,0x1907,0x8363,nullptr);\n  s.TexParameteri(0x0de1,0x2801,0x2601);s.TexParameteri(0x0de1,0x2800,0x2601);\n  s.TexParameteri(0x0de1,0x2802,0x812f);s.TexParameteri(0x0de1,0x2803,0x812f);\n }','if(!video720FrameTexture(f))return;')
edit('native_system_video720.h','static void stopSystemVideo720(){','static void pauseSystemVideo720(){\n // Release every decoder on list/settings entry, retain only bounded GPU previews.\n // Repeated hidden-menu frames do no work after the first release.\n for(int i=0;i<video720SlotCount;i++)if(video720Slots[i].asset||video720Slots[i].texture)retireVideo720Slot(i,true);\n}\nstatic void stopSystemVideo720(){')
edit('native_system_video720.h','clearVideo720Frames();video720NextStart=0;','clearVideo720Frames();video720UseCounter=0;')
edit('native_system_video720.h','{stopSystemVideo720();return;}','{pauseSystemVideo720();return;}')
edit('native_system_video720.h','if(video720Context!=context){stopSystemVideo720();video720Context=context;}','if(video720Context!=context){stopSystemVideo720();video720Context=context;video720PreviewProgram=0;}')
edit('native_system_video720.h','if(!ensureSystemVideoProgram())return;\n for(int n=0;','bool liveSupported=ensureSystemVideoProgram();\n if(!ensureVideo720PreviewProgram())return;\n for(int k=0;k<paintedCount;k++)seedVideo720Preview(video720Asset(p,painted[k].index));\n if(!liveSupported)wantedCount=0;\n for(int n=0;')
edit('native_system_video720.h','if(!v.texture&&(!video720NextStart||(int)(now-video720NextStart)>=0)){','if(!v.texture){')
edit('native_system_video720.h','video720NextStart=now+80;v.startedAt=now;','v.startedAt=now;')
edit('native_system_video720.h','const auto*f=video720Retained(asset);if(!f||!f->ready||!shipCompositeProgram)continue;\n   g.UseProgram(shipCompositeProgram);g.UniformMatrix4fv(shipCompositeMVP,1,0,mvp);g.Uniform1f(shipCompositeOpacity,1.f);','const auto*f=video720Retained(asset);if(!f||!f->ready)continue;\n   g.UseProgram(video720PreviewProgram);g.UniformMatrix4fv(video720PreviewMVP,1,0,mvp);')

(N/'video720_policy.h').write_text('''// Pure policy shared with host regression tests. Error retry and idle pacing stay separate.
#pragma once
static constexpr unsigned video720TextureBudget=8;
static constexpr unsigned video720TextureBytes=720u*720u*2u;
static constexpr unsigned video720MaxRetainedBytes=video720TextureBudget*video720TextureBytes;
static bool video720Older(unsigned a,unsigned b){return static_cast<int>(a-b)<0;}
''',encoding='utf-8')
print('R5 native source updated')
