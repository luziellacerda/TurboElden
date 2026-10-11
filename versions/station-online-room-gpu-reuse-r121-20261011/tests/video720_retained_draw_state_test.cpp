#include <cassert>
#include <cstdint>

using B=unsigned char;

struct AttributeState {int enable,size,type,normalized,stride,buffer;void*pointer;};
static int currentProgram,currentArray,currentActive,currentTexture0,currentVao,currentBlend[4];
static AttributeState currentAttributes[4];
static bool spaceUseVAO;

static void getInteger(unsigned name,int*out){
 switch(name){
  case 0x8b8d:*out=currentProgram;break;
  case 0x8894:*out=currentArray;break;
  case 0x84e0:*out=currentActive;break;
  case 0x8069:*out=currentTexture0;break;
  case 0x85b5:*out=currentVao;break;
  case 0x80c9:*out=currentBlend[0];break;
  case 0x80c8:*out=currentBlend[1];break;
  case 0x80cb:*out=currentBlend[2];break;
  case 0x80ca:*out=currentBlend[3];break;
  default:assert(false);
 }
}
static void useProgram(unsigned value){currentProgram=(int)value;}
static void activeTexture(unsigned value){currentActive=(int)value;}
static void bindTexture(unsigned target,unsigned value){assert(target==0x0de1);assert(currentActive==0x84c0);currentTexture0=(int)value;}
static void bindBuffer(unsigned target,unsigned value){assert(target==0x8892);currentArray=(int)value;}
static void blendFuncSeparate(unsigned a,unsigned b,unsigned c,unsigned d){currentBlend[0]=(int)a;currentBlend[1]=(int)b;currentBlend[2]=(int)c;currentBlend[3]=(int)d;}
static void bindVertexArray(unsigned value){currentVao=(int)value;}
static void getVertexAttrib(unsigned index,unsigned name,int*out){
 assert(index<4);auto&a=currentAttributes[index];
 switch(name){case 0x8622:*out=a.enable;break;case 0x8623:*out=a.size;break;case 0x8625:*out=a.type;break;case 0x886a:*out=a.normalized;break;case 0x8624:*out=a.stride;break;case 0x889f:*out=a.buffer;break;default:assert(false);}
}
static void getVertexAttribPointer(unsigned index,unsigned name,void**out){assert(index<4);assert(name==0x8645);*out=currentAttributes[index].pointer;}
static void vertexAttribPointer(unsigned index,int size,unsigned type,B normalized,int stride,const void*pointer){
 assert(index<4);auto&a=currentAttributes[index];a.size=size;a.type=(int)type;a.normalized=normalized;a.stride=stride;a.buffer=currentArray;a.pointer=const_cast<void*>(pointer);
}
static void enableVertexAttrib(unsigned index){assert(index<4);currentAttributes[index].enable=1;}
static void disableVertexAttrib(unsigned index){assert(index<4);currentAttributes[index].enable=0;}

struct MockLaserGL {void(*GetIntegerv)(unsigned,int*);void(*UseProgram)(unsigned);};
struct MockSpaceGL {
 void(*ActiveTexture)(unsigned);void(*BindTexture)(unsigned,unsigned);void(*BindBuffer)(unsigned,unsigned);
 void(*BlendFuncSeparate)(unsigned,unsigned,unsigned,unsigned);void(*BindVertexArray)(unsigned);
 void(*GetVertexAttribiv)(unsigned,unsigned,int*);void(*GetVertexAttribPointerv)(unsigned,unsigned,void**);
 void(*VertexAttribPointer)(unsigned,int,unsigned,B,int,const void*);void(*EnableVertexAttribArray)(unsigned);void(*DisableVertexAttribArray)(unsigned);
};
static MockLaserGL laserGL={getInteger,useProgram};
static MockSpaceGL spaceGL={activeTexture,bindTexture,bindBuffer,blendFuncSeparate,bindVertexArray,getVertexAttrib,getVertexAttribPointer,vertexAttribPointer,enableVertexAttrib,disableVertexAttrib};

#include "../native/d0/video720_retained_draw_state.h"

struct Snapshot {int program,array,active,texture,vao,blend[4];AttributeState attributes[4];};
static Snapshot resetState(){
 currentProgram=17;currentArray=23;currentActive=0x84c3;currentTexture0=31;currentVao=41;
 currentBlend[0]=0x302;currentBlend[1]=0x303;currentBlend[2]=1;currentBlend[3]=0x303;
 for(int i=0;i<4;i++)currentAttributes[i]={i&1,2+i,0x1406,0,20,50+i,(void*)(uintptr_t)(i*4)};
 Snapshot result={currentProgram,currentArray,currentActive,currentTexture0,currentVao,{currentBlend[0],currentBlend[1],currentBlend[2],currentBlend[3]}, {}};
 for(int i=0;i<4;i++)result.attributes[i]=currentAttributes[i];return result;
}
static bool sameAttribute(const AttributeState&a,const AttributeState&b){return a.enable==b.enable&&a.size==b.size&&a.type==b.type&&a.normalized==b.normalized&&a.stride==b.stride&&a.buffer==b.buffer&&a.pointer==b.pointer;}
static void mutateDrawState(){
 useProgram(99);activeTexture(0x84c0);bindTexture(0x0de1,77);blendFuncSeparate(1,0,1,0);
 bindBuffer(0x8892,88);for(unsigned i=0;i<4;i++){vertexAttribPointer(i,4,0x1401,1,24,(void*)(uintptr_t)(16+i));enableVertexAttrib(i);}
}
static void assertCommonRestored(const Snapshot&before){
 assert(currentProgram==before.program);assert(currentArray==before.array);assert(currentActive==before.active);assert(currentTexture0==before.texture);assert(currentVao==before.vao);
 for(int i=0;i<4;i++)assert(currentBlend[i]==before.blend[i]);
}

int main(){
 spaceUseVAO=false;auto before=resetState();
 {Video720RetainedDrawState state(currentProgram);mutateDrawState();}
 assertCommonRestored(before);for(int i=0;i<4;i++)assert(sameAttribute(currentAttributes[i],before.attributes[i]));

 spaceUseVAO=true;before=resetState();
 {Video720RetainedDrawState state(currentProgram);mutateDrawState();}
 assertCommonRestored(before);
 // SpaceState restores the bound VAO but does not rewind its stored pointers.
 for(int i=0;i<4;i++)assert(!sameAttribute(currentAttributes[i],before.attributes[i]));
}
