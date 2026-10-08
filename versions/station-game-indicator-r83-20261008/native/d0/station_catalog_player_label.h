#pragma once
#include <cstddef>
#include <cstring>

// Fixed grammar emitted by the reviewed Java helper. Never parse title guesses or ranges.
static inline void stationUnknownPlayers(char*out,size_t capacity){
 if(out&&capacity){out[0]=0;if(capacity>=4)std::memcpy(out,"\xE2\x80\x94",4);}
}
static inline bool stationPlayerEvidenceLabel(const char*value,size_t length,char*out,size_t capacity){
 stationUnknownPlayers(out,capacity);if(!value||!out||length>=capacity||length<1||length>7)return false;
 if(length==1&&value[0]=='1'){std::memcpy(out,"1",2);return true;}
 size_t number=0;unsigned count=0;
 while(number<length&&value[number]>='0'&&value[number]<='9')count=count*10+(unsigned)(value[number++]-'0');
 if(number<1||number>2||value[0]=='0'||count<2||count>16||length!=number+5)return false;
 bool simultaneous=true,alternating=true;
 for(size_t i=0;i<5;i++){if(value[number+i]!=" sim."[i])simultaneous=false;if(value[number+i]!=" alt."[i])alternating=false;}
 if(!simultaneous&&!alternating)return false;
 std::memcpy(out,value,length);out[length]=0;return true;
}

// Show human silhouettes only for a known simultaneous count; never turn alternation into seats.
static inline int stationPlayerPictogramCount(const char*value){
 if(!value)return 0;
 if(std::strcmp(value,"1")==0)return 1;
 if(value[0]>='2'&&value[0]<='5'&&std::strcmp(value+1," sim.")==0)return value[0]-'0';
 return 0;
}
