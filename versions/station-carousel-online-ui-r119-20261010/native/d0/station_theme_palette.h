#pragma once
// Presentation preference only. Default preserves the existing black theme.
static int stationThemeId;
static unsigned stationThemeRevision;
// Both choices keep the complete Turborama UI palette. Only the sky changes.
static unsigned stationThemeColor(unsigned color){return color;}
static unsigned stationSkyTop(){return stationThemeId==1?0x0B4B83ffu:0x020604ffu;}
static unsigned stationSkyBottom(){return stationThemeId==1?0x267CBBffu:0x060A08ffu;}
struct StationThemeRect {float x,y,w,h;};
static bool stationThemeContains(StationThemeRect r,float x,float y){return x>=r.x&&x<=r.x+r.w&&y>=r.y&&y<=r.y+r.h;}
