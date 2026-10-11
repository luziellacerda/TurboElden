"""Compile the actual R121/R122 room-action bodies with host UI stubs.

Verifies relocation only; no Android, network, GPU, controller or gameplay runs.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path('java/netplay-src/org/emulationstation/frontend/netplay')
BASE = ROOT.parent / 'station-online-room-gpu-reuse-r121-20261011'


def body(source, start):
    opening = source.index('{', start)
    depth, quote, comment, escaped = 0, '', '', False
    i = opening
    while i < len(source):
        c, pair = source[i], source[i:i + 2]
        if comment == '//':
            if c == '\n': comment = ''
        elif comment == '/*':
            if pair == '*/': comment = ''; i += 1
        elif quote:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == quote: quote = ''
        elif pair in ('//', '/*'): comment = pair; i += 1
        elif c in ('"', "'"): quote = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return source[start:i + 1]
        i += 1
    raise AssertionError('Unbalanced Java block')


def method(source, name):
    match = re.search(r'(?m)^    (?:(?:private|public|protected|static|final|@Override)\s+)*[\w<>.\[\]]+\s+' + re.escape(name) + r'\(', source)
    if not match: raise AssertionError('Missing method ' + name)
    return body(source, match.start()).strip()


def action_body(source):
    start = source.index('            JSONArray rd=mine.optJSONArray("ready");', source.index('private void paint'))
    end = source.index('            LinearLayout secondary=actionLine(current);', start)
    return source[start:end]


STUBS = r'''
static int checks;
static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
static class View {static final int ACCESSIBILITY_LIVE_REGION_POLITE=1;boolean enabled=true;String description="";void setEnabled(boolean v){enabled=v;}void setContentDescription(String v){description=v;}}
static class Button extends View {String label;int tone,icon;Runnable action;void setOnClickListener(java.util.function.Consumer<View> v){action=()->v.accept(this);}}
static class StationActionButton extends Button {
 static final int PRIMARY=1,SECONDARY=2,DANGER=3;
 StationActionButton(Object owner,String text,int value,int symbol){label=text;tone=value;icon=symbol;}
}
static class LinearLayout extends View {
 final List<View> children=new ArrayList<>();
 static class LayoutParams {int width,height,leftMargin;float weight;LayoutParams(int w,int h){width=w;height=h;}LayoutParams(int w,int h,float f){this(w,h);weight=f;}}
 void addView(View view,LayoutParams lp){children.add(view);}
 int getChildCount(){return children.size();}
}
static class TextView extends View {static final int ACCESSIBILITY_LIVE_REGION_POLITE=1;void setMinHeight(int n){}void setAccessibilityLiveRegion(int n){}}
static class StationSocialIcon {static final int EXIT=1,READY=2,NOT_READY=3,PLAY=4;}
static class JSONArray {final List<String> ids=new ArrayList<>();int length(){return ids.size();}String optString(int i){return ids.get(i);}}
static class JSONObject {
 final String state,host;final JSONArray ready;
 JSONObject(String s,String h,JSONArray r){state=s;host=h;ready=r;}
 String optString(String key){return "state".equals(key)?state:"hostId".equals(key)?host:"";}
 JSONArray optJSONArray(String key){return ready;}
}
boolean busy,launching;int muted;Button ready,start;TextView roomReadiness;
final List<String> calls=new ArrayList<>();
int dp(int v){return v;}
void styleAction(Button v,int tone){}
TextView text(LinearLayout p,String s,int size,int color){TextView v=new TextView();p.addView(v,new LinearLayout.LayoutParams(-1,-2));return v;}
LinearLayout actionLine(LinearLayout p){LinearLayout v=new LinearLayout();p.addView(v,new LinearLayout.LayoutParams(-1,dp(48)));return v;}
void command(String op,String key,Object value){calls.add(op+"/"+key+"/"+value);}
void startDialog(){calls.add("startDialog");}
static List<Button> buttons(LinearLayout parent){List<Button> values=new ArrayList<>();for(View v:parent.children){if(v instanceof Button)values.add((Button)v);if(v instanceof LinearLayout)values.addAll(buttons((LinearLayout)v));}return values;}
static Map<String,String> inventory(LinearLayout p){Map<String,String> values=new TreeMap<>();for(Button b:buttons(p)){check(!values.containsKey(b.label));values.put(b.label,b.enabled+"/"+b.tone+"/"+b.icon+"/"+b.description);}return values;}
static LinearLayout rowOf(LinearLayout p,Button b){for(View v:p.children)if(v instanceof LinearLayout){LinearLayout row=(LinearLayout)v;if(row.children.contains(b))return row;}return null;}
'''


MAIN = r'''
public static void main(String[] args){
 int cases=0;
 for(String state:new String[]{"waiting","starting","playing","recovering","ended",""})
 for(boolean host:new boolean[]{false,true})for(boolean readyState:new boolean[]{false,true})
 for(boolean busy:new boolean[]{false,true})for(boolean launching:new boolean[]{false,true})
 for(boolean readyPresent:new boolean[]{false,true}){
  JSONArray rd=readyPresent?new JSONArray():null;if(rd!=null&&readyState)rd.ids.add("self");
  JSONObject room=new JSONObject(state,host?"self":"other",rd);
  RoomControlsLegacy old=new RoomControlsLegacy();RoomControlsCurrent now=new RoomControlsCurrent();
  old.busy=now.busy=busy;old.launching=now.launching=launching;
  LinearLayout before=old.render(room,"self"),after=now.render(room,"self");
  check(inventory(before).equals(inventory(after)));
  check((old.start!=null)==(now.start!=null));
  check((now.start!=null)==("waiting".equals(state)&&host));
  List<Button> previous=buttons(before),current=buttons(after);
  Button exit=null;for(Button b:current)if("Sair".equals(b.label))exit=b;
  check(exit!=null);check(exit.enabled==(!busy&&!launching));
  if(now.start!=null){check(rowOf(after,now.start)==rowOf(after,exit));check(rowOf(after,now.ready)!=rowOf(after,exit));}
  check((now.ready!=null)=="waiting".equals(state));
  for(Button a:previous)for(Button b:current)if(a.label.equals(b.label)){
   old.calls.clear();now.calls.clear();a.action.run();b.action.run();check(old.calls.equals(now.calls));
  }
  cases++;
 }
 System.out.println("PASS roomStates="+cases+" checks="+checks);
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jdk', required=True, type=Path)
    parser.add_argument('--evidence', default=ROOT/'evidence/room-controls-r122.json', type=Path)
    args = parser.parse_args()
    old_path, path = BASE/PACKAGE/'StationRoomsActivity.java', ROOT/PACKAGE/'StationRoomsActivity.java'
    old, new = old_path.read_text(encoding='utf-8'), path.read_text(encoding='utf-8')
    guards = []
    def guard(name, ok):
        if not ok: raise AssertionError(name)
        guards.append(name)
    names = re.findall(r'(?m)^    (?:(?:private|public|protected|static|final|@Override)\s+)*[\w<>.\[\]]+\s+(\w+)\(', old)
    for name in sorted(set(names)-{'build','paint'}):
        # Overloads are compared as the complete text between method declarations.
        matches = re.findall(r'(?m)^    (?:(?:private|public|protected|static|final|@Override)\s+)*[\w<>.\[\]]+\s+' + re.escape(name) + r'\(',old)
        if len(matches)==1: guard('unchanged method: '+name,method(old,name)==method(new,name))
    old_build,new_build=method(old,'build'),method(new,'build')
    old_nickname=next(line for line in old_build.splitlines() if 'nickname=new EditText' in line)
    new_nickname=next(line for line in new_build.splitlines() if 'nickname=new EditText' in line)
    description='        nickname.setContentDescription("Seu nome online. Use Reconectar para atualizar.");'
    guard('build differs only by nickname relocation',old_build.replace(old_nickname+'\n','').replace(description+'\n','')==new_build.replace(new_nickname+'\n','').replace(description+'\n',''))
    guard('nickname below left title',new_build.index('"JOGAR ONLINE"')<new_build.index('nickname=new EditText')<new_build.index('connection=text(sidebar'))
    guard('nickname leaves main header', 'header.addView(nickname' not in new_build and 'sidebar.addView(nickname' in new_nickname)
    guard('nickname has no card',new_nickname.count('setBackground(null)')==1 and 'setBackground(bg(' not in new_nickname)
    guard('nickname smaller font and previous touch height', 'setTextSize(11)' in new_nickname and 'dp(44)' in new_nickname)
    for token in ('setSingleLine(true)','LengthFilter(24)','getSharedPreferences("station-online-profile",0).getString("nickname","Jogador")','field(nickname,"Seu nome online")'):
        guard('nickname behavior retained: '+token,token in old_nickname and token in new_nickname)
    old_paint,new_paint=method(old,'paint'),method(new,'paint')
    guard('all source outside build/paint byte-equivalent',old.replace(old_build,'__BUILD__').replace(old_paint,'__PAINT__')==new.replace(new_build,'__BUILD__').replace(new_paint,'__PAINT__'))
    old_exit_start=old_paint.index('            StationActionButton exit=')
    old_exit_end=old_paint.index('\n            TextView game=',old_exit_start)
    old_exit=old_paint[old_exit_start:old_exit_end]+'\n'
    old_actions,new_actions=action_body(old),action_body(new)
    guard('paint differs only by moved controls',old_paint.replace(old_exit,'').replace(old_actions,'')==new_paint.replace(new_actions,''))
    guard('single leave action retained',new_actions.count('command("leave",null,null)')==1)
    guard('ready callback retained','()->command("ready","value",!contains(rd,self))' in old_actions and '()->command("ready","value",!contains(rd,self))' in new_actions)
    guard('start confirmation retained','()->startDialog()' in old_actions and '()->startDialog()' in new_actions)
    guard('all command argument literals retained',Counter(re.findall(r'(?<![\w.])command\([^;\n]*',old))==Counter(re.findall(r'(?<![\w.])command\([^;\n]*',new)))
    for filename in ('StationOnlineCoverView.java','StationCreateGameCard.java','StationCoverLayout.java','StationFlowPanel.java','StationRoomArtwork.java'):
        guard('unchanged rendering/artwork: '+filename,(BASE/PACKAGE/filename).read_bytes()==(ROOT/PACKAGE/filename).read_bytes())
    common=method(new,'roomAction')+'\n'+method(new,'contains')
    # Both snippets are byte-exact source bodies, not a reimplementation of state logic.
    legacy=old_exit+'\n'+old_actions
    def harness(name,actions):
        return 'class '+name+' extends RoomControlsHost {\n'+common+'\nLinearLayout render(JSONObject mine,String self){LinearLayout current=new LinearLayout(),heading=new LinearLayout();current.addView(heading,new LinearLayout.LayoutParams(-1,48));\n'+actions+'\nreturn current;}\n}\n'
    program='import java.util.*;\nclass RoomControlsHost {\n'+STUBS+MAIN+'}\n'+harness('RoomControlsLegacy',legacy)+harness('RoomControlsCurrent',new_actions)
    with tempfile.TemporaryDirectory(prefix='station-room-controls-r122-') as folder:
        temporary=Path(folder);source=temporary/'RoomControlsHost.java';source.write_text(program,encoding='utf-8')
        compiled=subprocess.run([str(args.jdk/'bin/javac.exe'),'-encoding','UTF-8','-d',str(temporary),str(source)],capture_output=True,text=True)
        if compiled.returncode:raise AssertionError(compiled.stderr)
        result=subprocess.run([str(args.jdk/'bin/java.exe'),'-cp',str(temporary),'RoomControlsHost'],check=True,capture_output=True,text=True).stdout.strip()
    counts=re.fullmatch(r'PASS roomStates=(\d+) checks=(\d+)',result)
    if not counts: raise AssertionError(result)
    receipt={'revision':'R122','status':'PASS','scope':'compiled real R121/R122 action bodies with host UI/JSON stubs; comparative source guards','roomStates':int(counts[1]),'checks':int(counts[2]),'sourceGuardChecks':len(guards),'guards':guards,'sha256':{'baselineRooms':hashlib.sha256(old_path.read_bytes()).hexdigest(),'currentRooms':hashlib.sha256(path.read_bytes()).hexdigest(),'testRecipe':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'limitations':['No Android layout or rendering executed','No server request, GPU, controller or gameplay exercised','Physical readability of sidebar and room controls remains pending']}
    args.evidence.parent.mkdir(parents=True,exist_ok=True);args.evidence.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result);print('PASS sourceGuards='+str(len(guards)))


if __name__=='__main__':main()
