// Pure layout for the offline synopsis and optional console photo.
// Portrait falls back to full-width text; landscape reserves a right column.
struct StationInfoRect {float x,y,w,h;};
struct StationInfoLayout {StationInfoRect text,console;bool photo;};
static constexpr StationInfoLayout stationInfoLayout(float width,float height,float left,bool photo){
 float top=height*.454f,bottom=height*.830f,right=width*.965f;
 bool show=photo&&width>=height*1.25f;
 float photoWidth=show?width*.175f:0.f,gap=show?width*.018f:0.f;
 float textWidth=right-left-photoWidth-gap;
 if(textWidth<width*.22f){show=false;photoWidth=gap=0;textWidth=right-left;}
 return {{left,top,textWidth,bottom-top},{right-photoWidth,top,photoWidth,bottom-top},show};
}
