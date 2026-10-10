#pragma once

// roundedQuad reaches Renderer::drawTriangleStrips, which rewrites the vertex
// inputs and blend factors. Preserve exactly the subset touched by that call,
// following SpaceState's VAO/non-VAO rules without querying unrelated GL state.
struct Video720RetainedDrawState {
 int program,array,active,texture,vao,blend[4];
 struct Attribute{int enable,size,type,normalized,stride,buffer;void*pointer;}attributes[4];
 explicit Video720RetainedDrawState(int currentProgram):program(currentProgram),array(0),active(0),texture(0),vao(0),blend{},attributes{}{
  auto&g=laserGL;auto&s=spaceGL;
  g.GetIntegerv(0x8894,&array);g.GetIntegerv(0x84e0,&active);
  s.ActiveTexture(0x84c0);g.GetIntegerv(0x8069,&texture);
  unsigned blendNames[4]={0x80c9,0x80c8,0x80cb,0x80ca};for(int i=0;i<4;i++)g.GetIntegerv(blendNames[i],&blend[i]);
  if(spaceUseVAO)g.GetIntegerv(0x85b5,&vao);else for(int i=0;i<4;i++){
   auto&a=attributes[i];s.GetVertexAttribiv(i,0x8622,&a.enable);s.GetVertexAttribiv(i,0x8623,&a.size);
   s.GetVertexAttribiv(i,0x8625,&a.type);s.GetVertexAttribiv(i,0x886a,&a.normalized);
   s.GetVertexAttribiv(i,0x8624,&a.stride);s.GetVertexAttribiv(i,0x889f,&a.buffer);s.GetVertexAttribPointerv(i,0x8645,&a.pointer);
  }
 }
 ~Video720RetainedDrawState(){
  auto&g=laserGL;auto&s=spaceGL;
  if(spaceUseVAO)s.BindVertexArray(vao);else for(int i=0;i<4;i++){
   auto&a=attributes[i];s.BindBuffer(0x8892,a.buffer);s.VertexAttribPointer(i,a.size,a.type,(B)a.normalized,a.stride,a.pointer);
   if(a.enable)s.EnableVertexAttribArray(i);else s.DisableVertexAttribArray(i);
  }
  s.BindBuffer(0x8892,array);s.ActiveTexture(0x84c0);s.BindTexture(0x0de1,texture);s.ActiveTexture(active);
  s.BlendFuncSeparate(blend[0],blend[1],blend[2],blend[3]);g.UseProgram(program);
 }
};
