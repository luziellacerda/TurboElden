#pragma once
// Presentation preference only. Default preserves the existing black theme.
static int stationThemeId;
static unsigned stationThemeRevision;
static unsigned stationThemeColor(unsigned color){
 if(stationThemeId!=1)return color;
 unsigned rgb=color>>8;
 switch(rgb){
 case 0x020604:rgb=0x031329;break;case 0x060A08:rgb=0x092C52;break;
 case 0x030805:case 0x030705:rgb=0x030C1B;break;
 case 0x080C09:rgb=0x071A33;break;case 0x101B13:rgb=0x0D2745;break;
 case 0x17251B:case 0x151D17:rgb=0x123251;break;
 case 0x131E17:case 0x121A14:rgb=0x10263E;break;
 case 0x1B281F:rgb=0x14344F;break;case 0x203F2A:rgb=0x1B4165;break;
 case 0x284D32:rgb=0x215378;break;case 0x366C43:rgb=0x2B6B92;break;
 default:return color; // Semantic action colors, images and LEDs do not change.
 }
 return (rgb<<8)|(color&255);
}
struct StationThemeRect {float x,y,w,h;};
static bool stationThemeContains(StationThemeRect r,float x,float y){return x>=r.x&&x<=r.x+r.w&&y>=r.y&&y<=r.y+r.h;}
