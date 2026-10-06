#pragma once
// Keep the query, native token vector and match cache owned by GuiStore.
// Clearing only its string leaves the old tokens active on the next screen.
static void clearSearchForNavigation(void*p){
 if(at<B>(p,0x648)||at<B>(p,0x598)||*strData((B*)p+0x650))
  fn<void(*)(void*,bool)>(0x219570)(p,true);
}
static bool stationSearchOtherModal(void*p){
 return at<B>(p,0x2050)||at<B>(p,0x1830)||at<B>(p,0x1d98)||at<B>(p,0x5e4);
}
static bool stationSearchEmpty(void*p){
 return at<int>(p,0x370)>=2&&!stationSearchOtherModal(p)&&!at<B>(p,0x648)&&
  *strData((B*)p+0x650)&&at<U>(p,0xf8)==at<U>(p,0x100);
}
static bool stationSearchCanBack(void*p){
 return !stationSearchOtherModal(p)&&(at<B>(p,0x648)||*strData((B*)p+0x650));
}
static void stationSearchBack(void*p){
 // First Back dismisses the keyboard; the next clears the active filter.
 fn<void(*)(void*,bool)>(0x219570)(p,!at<B>(p,0x648));
}
struct StationEmptySearchCache {
 void*owner=nullptr;void*catalog=nullptr;U first=0,end=0;bool valid=false;
 void invalidate(){valid=false;}
 bool reuse(void*p,void*c)const{
  return valid&&owner==p&&catalog==c&&first==at<U>(c,0x88)&&end==at<U>(c,0x90)&&
   *strData((B*)p+0x650)&&at<U>(p,0xf8)==at<U>(p,0x100)&&
   at<int>(p,0x110)==at<int>(c,0xa8)&&at<B>(p,0x114)==at<B>(p,0x148)&&
   !strcmp(strData((B*)p+0x118),strData((B*)p+0x150))&&
   !strcmp(strData((B*)p+0x130),strData((B*)p+0x650));
 }
 void remember(void*p,void*c){
  owner=p;catalog=c;first=at<U>(c,0x88);end=at<U>(c,0x90);
  valid=*strData((B*)p+0x650)&&at<U>(p,0xf8)==at<U>(p,0x100);
 }
};
static StationEmptySearchCache stationEmptySearchCache;
static void stationSearchScope(void*p,void*catalog){
 B*first=at<B*>(catalog,0x88);B*end=at<B*>(catalog,0x90);
 U count=first&&end>=first?(U)(end-first)/0xe8:0;
 const char*platform=strData((B*)p+0x150);bool installed=at<B>(p,0x148)!=0;
 U*begin=at<U*>(p,0xf8),*last=at<U*>(p,0x100),*out=begin;
 for(U*it=begin;it&&it<last;it++)if(*it<count){
  B*item=first+*it*0xe8;
  if((!*platform||!strcmp(strData(item+0x60),platform))&&(!installed||item[0xa8]==1))*out++=*it;
 }
 at<U*>(p,0x100)=out;
 int visible=begin&&out?(int)(out-begin):0;
 if(at<int>(p,0xf0)<0||at<int>(p,0xf0)>=visible){at<int>(p,0xf0)=visible?visible-1:0;at<float>(p,0xf4)=(float)at<int>(p,0xf0);}
 if(out!=last){at<int>(p,0x220)=-1;at<U>(p,0x228)=~0UL;}
}
