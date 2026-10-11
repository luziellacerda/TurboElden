"""Run actual retained-row/footer and human action bodies with bounded host stubs.

No Android pixels, server request, emulator, GPU or gameplay is exercised.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import verify_room_compact_r123 as compact
import verify_room_gpu_reuse_r121 as reuse

ROOT = Path(__file__).resolve().parents[1]
PKG = Path('java/netplay-src/org/emulationstation/frontend/netplay')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


FOOTER_TEST = r'''
 RoomTest footerHost=new RoomTest();
 footerHost.beginRoomRows();footerHost.roomCoverCard("own","mine","game",true);footerHost.reconcileRoomRows();
 RoomRow footerRow=footerHost.roomRows.get(roomRowKey("own","mine","game"));
 check(footerRow.footer!=null);check(footerRow.footer==footerHost.ownRoomFooter);
 check(footerRow.display.actions.getChildCount()==2);
 ScrollView body=(ScrollView)footerRow.display.actions.getChildAt(0);
 check(body.fillViewport);check(!body.scrollbar);check(body.getChildAt(0)==footerRow.content);
 LinearLayout.LayoutParams bodySize=(LinearLayout.LayoutParams)body.getLayoutParams();
 check(bodySize.height==0&&bodySize.weight==1);check(bodySize.width==-1);
 check(footerRow.display.actions.getChildAt(1)==footerRow.footer);
 check(((LinearLayout.LayoutParams)footerRow.footer.getLayoutParams()).height==-2);
 View coverSurface=footerRow.display.surface;LinearLayout footer=footerRow.footer;
 for(int revision=0;revision<600;revision++){
  footerHost.beginRoomRows();LinearLayout content=footerHost.roomCoverCard("own","mine","game",true);
  check(content==footerRow.content);check(content.getChildCount()==0);check(footer.getChildCount()==0);
  for(int i=0;i<4;i++)footer.addView(new View(),new LinearLayout.LayoutParams(48,48));
  footerHost.reconcileRoomRows();check(footerHost.ownRoomFooter==footer);check(footer.getChildCount()==4);
  check(footer.detaches==0&&body.detaches==0&&coverSurface.detaches==0);
 }
 footerHost.beginRoomRows();check(footerHost.ownRoomFooter==null);
 footerHost.roomCoverCard("room","other","game",false);footerHost.reconcileRoomRows();
 check(footerHost.ownRoomFooter==null);check(footerRow.display.surface.detaches==1);
 for(RoomRow row:footerHost.roomRows.values())check(row.footer==null);
 footerHost.clearRoomRows();check(footerHost.ownRoomFooter==null);
 // AT_MOST may clip measured child height; the footer minimum uses the actual
 // production boxes, so actions remain reachable through the outer scroll.
 for(int width=48;width<=600;width+=11)for(int font=1;font<=4;font++)for(int viewport=48;viewport<=432;viewport+=16){
  footerHost.beginRoomRows();footerHost.roomCoverCard("own","minimum","game",true);footerHost.reconcileRoomRows();
  LinearLayout currentFooter=footerHost.ownRoomFooter;RoomControls controls=footerHost.new RoomControls();
  for(int i=0;i<4;i++)controls.addView(new View(),new LinearLayout.LayoutParams(48,48));
  controls.setPadding(0,3,0,3);controls.boxes=roomControlLayout(width,new int[]{100*font,72*font,54*font,84*font},48,6);
  controls.measuredHeight=Math.min(viewport,controls.requiredHeight());
  currentFooter.addView(controls,new LinearLayout.LayoutParams(-1,-2));footerHost.viewport=viewport;footerHost.updateOwnRoomHeight();
  int actual=((LinearLayout.LayoutParams)footerHost.ownRoomCard.getLayoutParams()).height;
  check(actual>=viewport);check(actual>=controls.requiredHeight()+8+96);check(actual-controls.requiredHeight()-8>=96);
  check(controls.requiredHeight()>=controls.measuredHeight);
 }
 // A recurring snapshot must not shrink an expanded retained cover while the
 // old footer is empty or its replacement buttons have not been measured yet.
 footerHost.viewport=90;int retainedHeight=((LinearLayout.LayoutParams)footerHost.ownRoomCard.getLayoutParams()).height;
 for(int revision=0;revision<600;revision++){
  footerHost.beginRoomRows();footerHost.roomCoverCard("own","minimum","game",true);footerHost.reconcileRoomRows();
  check(((LinearLayout.LayoutParams)footerHost.ownRoomCard.getLayoutParams()).height==retainedHeight);
  RoomControls replacement=footerHost.new RoomControls();for(int i=0;i<4;i++)replacement.addView(new View(),new LinearLayout.LayoutParams(48,48));
  footerHost.ownRoomFooter.addView(replacement,new LinearLayout.LayoutParams(-1,-2));footerHost.updateOwnRoomHeight();
  check(!replacement.hasMeasuredActions());check(((LinearLayout.LayoutParams)footerHost.ownRoomCard.getLayoutParams()).height==retainedHeight);
 }
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--json-jar', type=Path, required=True)
    parser.add_argument('--android-jar', type=Path, required=True)
    parser.add_argument('--client-jar', type=Path, required=True)
    parser.add_argument('--rooms-jar', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, default=ROOT/'evidence/room-footer-r124.json')
    args = parser.parse_args()
    if digest(args.json_jar) != compact.JSON_SHA:
        raise AssertionError('Use the existing pinned org.json jar')
    path = ROOT/PKG/'StationRoomsActivity.java'
    new = path.read_text(encoding='utf-8')
    guards = []
    def guard(label, value):
        if not value: raise AssertionError(label)
        guards.append(label)
    for name, expected in compact.INSTALLED_METHOD_SHA.items():
        guard('Exact installed R123 action/authority: '+name,
              hashlib.sha256(compact.method(new,name).encode()).hexdigest()==expected)
    base = ROOT.parent/'station-theme-room-download-r122-20261011'
    old = (base/PKG/'StationRoomsActivity.java').read_text(encoding='utf-8')
    for name in ('roomRowKey','reconcileRoomRows','loadHero','loadHeroProfile','bindHeroCover','roomExplanation','roomInfo','roomSetupDescription','roomLayout','onStart','onStop','onDestroy','onResume','onPause','applyGraphics','deliver','connect','join','joinConfirmed','prepareRoom','createRoom','confirmRoomSetup'):
        guard('Exact R122 non-presentation body: '+name,compact.method(new,name)==compact.method(old,name))
    guard('All command callback literals exact',Counter(re.findall(r'(?<![\w.])command\([^;\n]*',old))==Counter(re.findall(r'(?<![\w.])command\([^;\n]*',new)))
    for name in ('StationRoomRoster.java','StationOnlineCoverView.java','StationCreateGameCard.java','StationFlowPanel.java','StationCoverLayout.java','StationRoomArtwork.java','StationOnlineClient.java','StationOnlineGame.java','StationRetroLaunch.java','StationRoomState.java','StationRoomStartState.java'):
        guard('Exact R122 dependency: '+name,(base/PKG/name).read_bytes()==(ROOT/PKG/name).read_bytes())
    card = compact.method(new,'roomCoverCard')
    guard('Weighted text viewport and fixed trailing footer','new LinearLayout.LayoutParams(-1,0,1)' in card and 'display.actions.addView(footer,new LinearLayout.LayoutParams(-1,-2))' in card)
    paint = compact.method(new,'paint')
    guard('Own-room four actions route to footer','LinearLayout controls=roomControls(ownRoomFooter);' in paint and 'roomAction(actionLine(ownRoomFooter),"Abrir partida"' in paint)
    guard('No detached cover to create a footer','rooms.removeAllViews()' not in paint and 'display.setCover(null)' not in card)
    guard('Canonical synopsis and full distinct details remain accessible','synopsisFor(mine.optString("itemId"))' in compact.method(new,'ownRoomGuide') and 'showGameDetails(mine.optString("itemId"),roomExplanation(mine))' in compact.method(new,'ownRoomGuide'))
    guard('Footer guide adds no active work',not re.search(r'postDelayed|Timer|Executor|StationApi|BitmapFactory|MediaPlayer',compact.method(new,'ownRoomGuide')))
    guard('Minimum uses unclipped action boxes','child instanceof RoomControls?((RoomControls)child).requiredHeight():child.getMeasuredHeight()' in compact.method(new,'ownRoomRequiredHeight'))
    guard('Outer scroll fallback retains original roomScroll','roomScroll=scroll(middlePanel,rooms)' in compact.method(new,'build'))
    guard('Height changes are layout driven only',not re.search(r'postDelayed|Timer|Executor|StationApi|MediaPlayer',compact.method(new,'updateOwnRoomHeight')+compact.method(new,'ownRoomRequiredHeight')))
    guard('No resize from empty replacement footer','ownRoomFooter.getChildCount()==0' in compact.method(new,'updateOwnRoomHeight'))
    guard('No resize before replacement actions measured','hasMeasuredActions()' in compact.method(new,'updateOwnRoomHeight'))

    room_class = reuse.block(new,new.index('    private static final class RoomRow')).strip()
    room_fields = '\n'.join(x for x in new.splitlines() if any((' '+name+'=') in x for name in ('roomRows','desiredRoomRows','usedRoomRows')))
    row_methods = '\n'.join(compact.method(new,name) for name in ('roomRowKey','beginRoomRows','roomCoverCard','reconcileRoomRows','clearRoomRows','ownRoomHeight','ownRoomRequiredHeight','updateOwnRoomHeight','roomControlLayout'))
    row_stubs = reuse.ROOM_STUBS.replace('int width,height;LayoutParams(int w,int h){width=w;height=h;}','int width,height;float weight;LayoutParams(int w,int h){width=w;height=h;}LayoutParams(int w,int h,float value){this(w,h);weight=value;}')
    row_stubs = row_stubs.replace('void setFillViewport(boolean b){}void setVerticalScrollBarEnabled(boolean b){}','boolean fillViewport,scrollbar;void setFillViewport(boolean b){fillViewport=b;}void setVerticalScrollBarEnabled(boolean b){scrollbar=b;}')
    row_stubs = row_stubs.replace('Object start,roomReadiness;','Object start,roomReadiness;LinearLayout ownRoomFooter;')
    row_stubs = row_stubs.replace('void setPadding(int a,int b,int c,int d){}','int paddingTop,paddingBottom,measuredHeight;void setPadding(int a,int b,int c,int d){paddingTop=b;paddingBottom=d;}int getPaddingTop(){return paddingTop;}int getPaddingBottom(){return paddingBottom;}static final int GONE=8;int getVisibility(){return 0;}int getMeasuredHeight(){return measuredHeight;}interface LayoutListener{void changed(View v,int l,int t,int r,int b,int ol,int ot,int or,int ob);}void addOnLayoutChangeListener(LayoutListener listener){}')
    controls_class=reuse.block(new,new.index('    private final class RoomControls'))
    row_stubs+='\nclass RoomControls extends LinearLayout {int[] boxes=new int[0];\n'+reuse.block(controls_class,controls_class.index('        int requiredHeight()')).strip()+'\n'+reuse.block(controls_class,controls_class.index('        boolean hasMeasuredActions()')).strip()+'\n}\n'
    row_main = reuse.ROOM_TEST.replace('check(((LinearLayout.LayoutParams)own.root.getLayoutParams()).height==260);','check(((LinearLayout.LayoutParams)own.root.getLayoutParams()).height==320);')
    row_main = row_main.replace(' System.out.println("PASS roomReuse="+checks);',FOOTER_TEST+'\n System.out.println("PASS roomReuse="+checks);')
    row_program='import java.util.*;\npublic class RoomTest {\n'+row_stubs+room_class+'\n'+room_fields+'\n'+row_methods+'\n'+row_main+'\n}'
    start = paint.index('            JSONArray rd=mine.optJSONArray("ready");')
    end = paint.index('            if(StationLaunchPolicy.eligible(',start)
    fragment = paint[start:end].replace('roomReadiness=text(current,"",11,muted);roomReadiness.setPadding(0,dp(4),0,dp(4));roomReadiness.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);','roomReadiness=new TextView();')
    # Recursive lookup sees the fixed footer outside the text container.
    action_stubs=compact.STUBS.replace('LinearLayout current=new LinearLayout();BODY','LinearLayout current=new LinearLayout();current.addView(ownRoomFooter,new LinearLayout.LayoutParams(-1,-2));BODY').replace('BODY',fragment)
    action_stubs+='\nLinearLayout ownRoomFooter=new LinearLayout();void ownRoomGuide(LinearLayout parent,JSONObject mine){}\n'
    action_methods=compact.first_method(new,'action')+'\n'+'\n'.join(compact.method(new,name) for name in ('roomControlLayout','roomConfirmationKey','contains','roomAction','startRoom','separateRoomNotice','updateStartState','action','command','room','failure'))
    action_program='package org.emulationstation.frontend.netplay;\nimport org.json.*;import java.util.*;import java.util.concurrent.*;\npublic class RoomCompactHost {\n'+action_stubs+'\n'+action_methods+'\n'+compact.MAIN+'\n}'
    outputs=[]
    with tempfile.TemporaryDirectory(prefix='station-room-footer-r124-') as directory:
        temporary=Path(directory)
        for name,program in (('RoomTest',row_program),('RoomCompactHost',action_program)):
            probe=temporary/(name+'.java');probe.write_text(program,encoding='utf-8')
            inputs=[probe]
            if name=='RoomCompactHost': inputs.append(ROOT/PKG/'StationRoomStartState.java')
            run=subprocess.run([str(args.jdk/'bin/javac.exe'),'-encoding','UTF-8','--release','8','-cp',str(args.json_jar),'-d',str(temporary),*map(str,inputs)],capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stderr)
            qualified='org.emulationstation.frontend.netplay.'+name if name=='RoomCompactHost' else name
            run=subprocess.run([str(args.jdk/'bin/java.exe'),'-cp',str(temporary)+os.pathsep+str(args.json_jar),qualified],capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stderr)
            outputs.append(run.stdout.strip())
        production=temporary/'production';production.mkdir()
        dependencies=(args.android_jar,args.client_jar,args.rooms_jar)
        run=subprocess.run([str(args.jdk/'bin/javac.exe'),'-encoding','UTF-8','--release','8','-proc:none','-cp',os.pathsep.join(map(str,dependencies)),'-d',str(production),str(path)],capture_output=True,text=True)
        if run.returncode:raise AssertionError(run.stderr)
    evidence={'revision':'R124','status':'PASS','scope':'Actual retained-row bodies, footer identity, human callbacks and 48dp wrapping executed on host; complete StationRoomsActivity compiled against API34 and exact R123 module jars.','results':outputs,'sourceGuardChecks':len(guards),'guards':guards,'sourceSha256':digest(path),'recipeSha256':digest(__file__),'productionJavaCompile':{'status':'PASS','sources':1,'classpathSha256':dict(zip(('androidApi34','r123Client','r123Rooms'),map(digest,dependencies)))},'limits':['No Android pixels/layout execution or font/readability approval.','Host view stubs verify parent/order/weight/identity and attach counts; Android owns actual LinearLayout measurement.','No physical room/gameplay/ANR/thermal validation.']}
    args.evidence.parent.mkdir(parents=True,exist_ok=True)
    args.evidence.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for output in outputs: print(output)
    print('PASS sourceGuards='+str(len(guards))+' productionJavaSources=1')


if __name__=='__main__':main()
