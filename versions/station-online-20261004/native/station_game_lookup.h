#pragma once
// Exact published item ID and exact native platform label.
static const GameInfo*findStationGameInfo(const char*key,const char*id){
 int first=0,last=NSTATIONGAMEINFOS;
 while(first<last){int middle=first+(last-first)/2,order=strcmp(id,stationGameInfos[middle].id);
  if(order>0)first=middle+1;else last=middle;}
 if(first<NSTATIONGAMEINFOS&&strcmp(stationGameInfos[first].id,id)==0&&strcmp(stationGameInfos[first].system,key)==0)
  return &stationGameInfos[first];
 return nullptr;
}
