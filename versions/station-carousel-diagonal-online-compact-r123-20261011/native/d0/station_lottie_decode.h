#pragma once
static bool stationLottieDecode(unsigned*dst,unsigned pixels,const unsigned*rle,unsigned begin,unsigned end,unsigned words){
 if(!dst||!rle||end>words||begin>end||(end-begin)%2)return false;unsigned written=0;
 for(unsigned i=begin;i<end;i+=2){unsigned run=rle[i],color=rle[i+1];if(!run||run>pixels-written)return false;for(unsigned j=0;j<run;j++)dst[written++]=color;}
 return written==pixels;
}
