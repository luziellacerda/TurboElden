// Shared game-list action design. Geometry only, driven by the existing visible
// GuiStore frame; no thread, timer, texture, decoder or background invalidation.
static unsigned gameActionColor(float nx,float ny,unsigned now,int slot,bool disabled){
 unsigned top=disabled?0x163523ff:0x126039ff,bottom=disabled?0x0B2015ff:0x092D1Eff;
 unsigned color=blendColor(top,bottom,ny);
 if(disabled)return color;
 float phase=((now+(unsigned)slot*170u)%3400u)/3400.f;
 float center=-.32f+phase*1.64f;
 float light=actionEase(actionClamp(1-absolute(nx+(ny-.5f)*.14f-center)/.18f));
 return blendColor(color,0x78FFABff,light*.36f);
}
static void drawGameAction(float x,float y,float w,float h,int slot,bool disabled,bool focused,bool confirming){
 if(w<=0||h<=0)return;
 unsigned now=fn<unsigned(*)()>(0x39e240)();
 float pulse=disabled?0:actionCycle(now,2800,(unsigned)slot*170);
 float edge=h*.022f,pad=h*.075f;
 unsigned rim=confirming?0xF37F77ff:disabled?0x335A40ff:focused?0xD6FFE7ff:blendColor(0x35BD67ff,0x8EFFA8ff,pulse);
 if(!disabled)openButtonFill(x-pad,y-pad,w+2*pad,h+2*pad,0x3AFF7000u|(unsigned)(15+17*pulse),0x3AFF7005);
 openButtonFill(x-edge,y-edge,w+2*edge,h+2*edge,rim,disabled?0x234530ff:0x238C51ff);
 Vertex vertices[286];unsigned count=0;float radius=h*.24f;
 fn<void(*)(unsigned)>(0x2e52e8)(0);
 for(int row=0;row<8;row++){
  float yy[2]={h*row/8,h*(row+1)/8};
  float inset[2]={actionInset(yy[0],h,radius),actionInset(yy[1],h,radius)};
  for(int col=0;col<=16;col++)for(int side=0;side<2;side++){
   float xx=inset[side]+(w-2*inset[side])*col/16;
   unsigned color=fn<unsigned(*)(unsigned)>(0x2e3980)(gameActionColor(xx/w,yy[side]/h,now,slot,disabled));
   Vertex v={x+xx,y+yy[side],0,0,color};
   if(row&&col==0&&side==0){vertices[count]=vertices[count-1];count++;vertices[count++]=v;}
   vertices[count++]=v;
  }
 }
 fn<void(*)(const Vertex*,unsigned,int,int)>(0x2e5470)(vertices,count,4,5);
}
