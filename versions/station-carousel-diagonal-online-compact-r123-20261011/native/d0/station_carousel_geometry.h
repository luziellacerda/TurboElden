#pragma once
// Presentation only. 7.5 degrees is the official CarouselComponent wheel default;
// this optional 2D adaptation is not a claim about the private PC coverflow renderer.
namespace stationCarouselGeometry {
struct Point {float x,y;};
struct Bounds {float x,y,w,h;};
inline int neighborCount(int style,bool cellEffects){return style==2&&cellEffects?10:6;}
inline float sideCosine(){return .7071067812f;}
inline float sideSine(){return .7071067812f;}
inline float sideNear(){return 1-sideSine()/2.4f;}
// The right-hand slots show their right edge nearer the viewer. Account for the
// perspective narrowing in the layout, rather than leaving a full flat-slot gap.
inline float sideWidthRatio(){float a=sideSine()/2.4f;return sideNear()*sideCosine()/(1-a*a);}
inline float sideLeftInset(){return .5f-sideNear()*sideCosine()*.5f/(1+sideSine()/2.4f);}
struct Transform {
 float cx=0,cy=0,c=1,s=0;bool active=false;
 float depth=0,vertical=1;bool projective=false;
 Point map(float x,float y)const {
  if(!active)return {x,y};float dx=x-cx,dy=y-cy;
  if(projective){float denominator=1+depth*dx;return {cx+c*dx/denominator,cy+vertical*dy/denominator};}
  return {cx+c*dx-s*dy,cy+s*dx+c*dy};
 }
 Point inverse(float x,float y)const {
  if(!active)return {x,y};float dx=x-cx,dy=y-cy;
  if(projective){
   float denominator=c-depth*dx;
   if(denominator<=.000001f)return {-1000000.f,-1000000.f}; // Outside the visible, positive-W plane.
   float localX=dx/denominator;return {cx+localX,cy+dy*(1+depth*localX)/vertical};
  }
  float det=c*c+s*s;return {cx+(c*dx+s*dy)/det,cy+(-s*dx+c*dy)/det};
 }
 // Compose the existing shader MVP with the homogeneous plane projection.
 // No shader, UV or vertex layout change: GLES supplies perspective-correct varyings.
 void compose(const float*original,float*output)const {
  float homography[16]={c+cx*depth,cy*depth,0,depth,0,vertical,0,0,0,0,1,0,
                        cx*(1-c-cx*depth),cy*(1-vertical-cx*depth),0,1-cx*depth};
  for(int column=0;column<4;column++)for(int row=0;row<4;row++){
   float value=0;for(int k=0;k<4;k++)value+=original[k*4+row]*homography[column*4+k];
   output[column*4+row]=value;
  }
 }
 Bounds bounds(float x,float y,float w,float h)const {
  if(!active)return {x,y,w,h};
  Point q[4]={map(x,y),map(x+w,y),map(x,y+h),map(x+w,y+h)};
  float left=q[0].x,right=left,top=q[0].y,bottom=top;
  for(int i=1;i<4;i++){if(q[i].x<left)left=q[i].x;if(q[i].x>right)right=q[i].x;if(q[i].y<top)top=q[i].y;if(q[i].y>bottom)bottom=q[i].y;}
  return {left,top,right-left,bottom-top};
 }
};
inline Transform make(float x,float y,float w,float h,int position,int selected,int style,bool cellEffects,int facing=0) {
 Transform t;
 if((style!=1&&style!=2)||!cellEffects||position<0||position==selected||!(w>0)||!(h>0))return t;
 if(style==2){
  // Explicit Android adaptation of the XML coverflow type; XML supplies no Y angle.
  float cosine=sideCosine(),sine=sideSine(),near=sideNear(); // 45 degrees, no trig per frame.
  t.cx=x+w*.5f;t.cy=y+h*.5f;t.c=near*cosine;t.vertical=near;
  // Facing follows the drawn slot, not the catalog index: forward neighbors can
  // wrap to index zero while remaining on the right of the selected cover.
  int direction=facing?facing:(position<selected?-1:1);
  t.depth=(direction<0?sine:-sine)/(1.2f*w);t.active=true;t.projective=true;return t;
 }
 constexpr float cosine=.9914448614f,sine=.1305261922f;
 float fitX=w/(cosine*w+sine*h),fitY=h/(sine*w+cosine*h),fit=fitX<fitY?fitX:fitY;
 t.cx=x+w*.5f;t.cy=y+h*.5f;t.c=cosine*fit;t.s=(position<selected?sine:-sine)*fit;t.active=true;
 return t;
}
inline int lower(float value){int n=(int)value;return value<n?n-1:n;}
inline int upper(float value){int n=(int)value;return value>n?n+1:n;}
}
