"""Generate only the PSX opt-in changes from exact current R126 Java sources."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parents[1]/'versions/station-dolphin-online-r126-20261011/java'
PKG=Path('org/emulationstation/frontend/netplay')

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('Expected exact route anchor: '+old[:120])
    return text.replace(old,new)

def main():
    before={}
    game=BASE/PKG/'StationOnlineGame.java'
    text=game.read_text(encoding='utf-8');before[game.name]=hashlib.sha256(game.read_bytes()).hexdigest()
    text=once(text,'        if(!"retroarch".equals(backend)&&!n64&&!dolphin)',
        '        boolean psx="psx".equals(engine.getString("platform"))&&StationPsxLaunch.BACKEND.equals(backend);\n'
        '        if(!"retroarch".equals(backend)&&!n64&&!dolphin&&!psx)')
    text=once(text,'String library=n64||dolphin?', 'String library=n64||dolphin||psx?')
    target=ROOT/'java'/PKG/game.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
    rooms=BASE/PKG/'StationRoomsActivity.java'
    text=rooms.read_text(encoding='utf-8');before[rooms.name]=hashlib.sha256(rooms.read_bytes()).hexdigest()
    text=once(text,'systemDolphin=StationDolphinLaunch.BACKEND.equals(game.backend);',
        'systemDolphin=StationDolphinLaunch.BACKEND.equals(game.backend),systemPsx=StationPsxLaunch.BACKEND.equals(game.backend);')
    text=once(text,':StationRetroLaunch.prepare(this,game,gameRoom,snapshot,cancel);',
        ':systemPsx?StationPsxLaunch.prepare(this,game,gameRoom,snapshot,cancel):StationRetroLaunch.prepare(this,game,gameRoom,snapshot,cancel);')
    text=once(text,':StationRetroActivity.class).putExtra("station.launch",file)',
        ':systemPsx?StationPsxOnlineActivity.class:StationRetroActivity.class).putExtra("station.launch",file)')
    if text.count('discardPreparedLaunch(systemN64,systemDolphin,file)')!=2:raise ValueError('PSX discard anchors')
    text=text.replace('discardPreparedLaunch(systemN64,systemDolphin,file)','discardPreparedLaunch(systemN64,systemDolphin,systemPsx,file)')
    text=once(text,'private void discardPreparedLaunch(boolean n64,boolean dolphin,String file)',
        'private void discardPreparedLaunch(boolean n64,boolean dolphin,boolean psx,String file)')
    text=once(text,'else StationRetroLaunch.discard(this,file);}',
        'else if(psx)StationPsxLaunch.discard(this,file);else StationRetroLaunch.discard(this,file);}')
    (ROOT/'java'/PKG/rooms.name).write_text(text,encoding='utf-8')
    (ROOT/'recipe'/'route-base-sha256.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changedRoutes':['psx'],'baseSha256':before,'otherRouteBodiesPreserved':True}))

if __name__=='__main__':main()
