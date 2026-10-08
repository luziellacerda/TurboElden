"""Only replace the carousel's displayed player source; preserve all layout and rating sources."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=Path(r'E:\ESTUDO APK\work\station-neogeo-collection-map-r75-20261007\native-build\native')
PIN='415ba5efad249d273a5fa388a746d4597cbe9006fc56e47da0d04e58752e6e1f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def change(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
def main():
 source=BASE/'native_info.h';assert sha(source)==PIN
 s=source.read_text('utf8')
 s=change(s,'#include "station_players_label.h"','#include "native_players_evidence.h"')
 s=change(s,'const char*heading="";const char*body="";char folderText[6144]={};','const char*heading="";const char*body="";const char*playerEvidenceId=nullptr;char folderText[6144]={};')
 s=change(s,'infoConsoleKey=key;infoDetails=findStationGameDetailsForGame(id,key,heading);','infoConsoleKey=key;infoDetails=findStationGameDetailsForGame(id,key,heading);playerEvidenceId=id;')
 s=change(s,'char players[96]={};stationPlayersLabel(infoDetails?infoDetails->players:"",players,sizeof(players));\n  infoSinglePlayer=strcmp(players,"1 player")==0;\n  for(char*q=players;*q;q++)if(*q==\' \'){*q=0;break;}','char players[96]={};stationVerifiedPlayers(playerEvidenceId,players,sizeof(players));\n  infoSinglePlayer=strcmp(players,"1")==0;')
 output=HERE/'native_info.h'
 if output.exists():assert output.read_text('utf8')==s,'Changed overlay requires explicit review'
 else:output.write_text(s,'utf8')
 manifest={'base':'R75','baseNativeInfoSHA256':PIN,'scope':'Display-only player metadata binding; all ratings, geometry, videos and controls unchanged.','sources':{p.name:sha(p) for p in sorted(HERE.glob('*.h'))}}
 (HERE/'OVERLAY-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
