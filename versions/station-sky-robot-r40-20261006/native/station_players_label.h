#pragma once
// Published counts: exact count or inclusive range. Preserve 8+ as open-ended.
// No default player count when the catalog has no data.
static void stationPlayersLabel(const char* value,char* output,unsigned capacity){
 if(!output||!capacity)return;
 output[0]=0;
 if(!value||!*value){if(capacity>1){output[0]='-';output[1]=0;}return;}
 const char* end=value;while(*end)++end;
 const char* number=value;const char* dash=nullptr;
 bool valid=true,plus=false;
 for(const char*p=value;p<end;++p){
  if(*p=='-'&&!dash&&p>value&&p+1<end)dash=p;
  else if(*p=='+'&&p+1==end&&!dash)plus=true;
  else if(*p<'0'||*p>'9')valid=false;
 }
 if(!valid){if(capacity>1){output[0]='-';output[1]=0;}return;}
 if(dash)number=dash+1;
 const bool single=!plus&&end-number==1&&*number=='1';
 const char* suffix=single?" player":" players";
 unsigned at=0;
 for(const char*p=number;p<end&&at+1<capacity;++p)output[at++]=*p;
 for(const char*p=suffix;*p&&at+1<capacity;++p)output[at++]=*p;
 output[at]=0;
}
