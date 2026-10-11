#pragma once
struct StationConsoleCrop{unsigned left,top,right,bottom;};
struct StationConsoleFit{float x,y,w,h,u0,v0,u1,v1;};
static StationConsoleCrop stationConsoleBounds(const unsigned char* pixels,unsigned w,unsigned h){
 StationConsoleCrop r{w,h,0,0};
 if(!pixels||!w||!h||w>4096||h>4096)return {0,0,w,h};
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++)if(pixels[(y*w+x)*4+3]){
  if(x<r.left)r.left=x;if(y<r.top)r.top=y;
  if(x+1>r.right)r.right=x+1;if(y+1>r.bottom)r.bottom=y+1;
 }
 if(r.right<=r.left||r.bottom<=r.top)return {0,0,w,h};
 // Preserve a transparent texel around antialiased edges where one exists.
 if(r.left)r.left--;if(r.top)r.top--;
 if(r.right<w)r.right++;if(r.bottom<h)r.bottom++;
 return r;
}
static StationConsoleFit stationConsoleFit(const StationInfoRect&slot,const StationConsoleCrop&crop,unsigned w,unsigned h){
 if(!w||!h||crop.right<=crop.left||crop.bottom<=crop.top||crop.right>w||crop.bottom>h||!(slot.w>0)||!(slot.h>0))return {};
 float cw=(float)(crop.right-crop.left),ch=(float)(crop.bottom-crop.top);
 float scale=slot.w/cw,byHeight=slot.h/ch;if(byHeight<scale)scale=byHeight;
 float dw=cw*scale,dh=ch*scale;
 return {slot.x+(slot.w-dw)*.5f,slot.y+(slot.h-dh)*.5f,dw,dh,
         crop.left/(float)w,crop.top/(float)h,crop.right/(float)w,crop.bottom/(float)h};
}
