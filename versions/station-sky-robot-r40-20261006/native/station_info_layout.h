// Pure layout for synopsis text and an optional local console photo.
// Systems/collections and games retain their existing vertical text bands.
// Portrait or unavailable artwork keeps the complete text width.
struct StationInfoRect {float x,y,w,h;};
struct StationInfoLayout {StationInfoRect text,console;bool photo;};
static constexpr StationInfoLayout stationInfoLayout(float width,float height,float left,bool photo,bool systems=false){
 if(!(width>0.f)||!(height>0.f))return {{0,0,0,0},{0,0,0,0},false};
 float top=height*(systems?.422f:.454f),bottom=height*(systems?.812f:.830f),right=width*.965f;
 // Clamp an off-screen content origin before reserving the right-hand photo slot.
 if(!(left>=0.f))left=0.f;if(left>right)left=right;
 bool show=photo&&!systems&&width>=height*1.25f;
 float photoWidth=show?width*.175f:0.f,gap=show?width*.018f:0.f;
 float textWidth=right-left-photoWidth-gap;
 if(textWidth<width*.22f){show=false;photoWidth=gap=0;textWidth=right-left;}
 return {{left,top,textWidth,bottom-top},{right-photoWidth,top,photoWidth,bottom-top},show};
}
