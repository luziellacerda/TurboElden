"""Exercise exact production start/action/control bodies with bounded host fixtures.

No Android window, network, GPU, controller, emulator or gameplay is exercised.
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
from verify_room_controls_r122 import method as first_method, body

ROOT = Path(__file__).resolve().parents[1]
PKG = Path('java/netplay-src/org/emulationstation/frontend/netplay')
BASE = ROOT.parent / 'station-theme-room-download-r122-20261011'
JSON_SHA = '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796'
INSTALLED_SOURCE = '780a0bfa3580fc761ad1289bdf36f84dbf53188afd28065030806fe576a0ef44'
# Pinned canonical bodies from the exact initially installed R123 Rooms source.
INSTALLED_METHOD_SHA = {
    "startRoom": "13ebba158806b73b6f3047bccea6e5bfa9f1a58c867e681454afe4e7024c95ee",
    "roomConfirmationKey": "42f84122efc190613533c0eec8fd6ac7d725a9750261adfd807e8f4575d9eec4",
    "action": "17228489b9dfe0b269a5358cbcc92fe5b765133e247edb1f568307c7fb71807e",
    "command": "6be79c07d32f2849dcef7fb3eb982764b5abc42cf02841204d650276027018a1",
    "failure": "80aa0b25d71108fc3b70bcadd31d7d5e7392e422976b6d51910f15d406e1f239",
    "roomControlLayout": "ac98353a74d7975925be9dc99b569f93726e83d619c9d429de522ce2b96a6184",
    "roomAction": "b0d3580cc7ac1786f0500e90fe6c95a30cd8a6e84207231551c1276c3f8a177b",
    "createRoom": "855cc8e6bcc332f15023be10739a5f6a57f985a313d8230032398d9cf037b3ac",
    "confirmRoomSetup": "c890423a0ce904e72c15a9b7f58b7aa2c37aa75368acda073614a55796b708b5",
    "prepareRoom": "2f67ad02bc0e4a01f36ab758ec197ee06921f1e5aa1eba732cf04090875cd1ad",
    "createVerifiedRoom": "e4e14f13ca04e6333f4e001b7104224c6b974e0c6ed68feb5572564f88e248db",
    "selectRoomMode": "516b58409dbfce966f3696d908f3ac880d506de838aebb52d4c098603a59b731",
    "showRoomSetup": "2dbe1001041b27a18b6e08825cc63193e36d6a8b520a8e0b582ca29e799ca027",
    "updateRoomSetupEnabled": "06cc749f518ef7cecaf4914d4f2f51997abc6ca0e9993bd6ede439d961e9eb5a",
    "join": "d705a2c2edbd7034eba81929c52f25ddc6e373841f9651f509feaec174dcce57",
    "joinConfirmed": "4bd8bfda5bc71da0894735b3905b88ed25c60df86fe0072adc67d5466a76ca36",
    "launch": "de5178130b769dff2908da0af2c7d4276d98339a8bae2735b29ad09e08f23bed"
}


def method(source, name):
    # Execute the two-argument authority method rather than its forwarding overload.
    if name == 'action':
        return body(source,source.index('    private void action(Work work,Runnable completed)')).strip()
    return first_method(source,name)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


STUBS = r'''
static int checks,cases;
static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
static class View {
 static final int VISIBLE=0,GONE=8;
 boolean enabled=true;String description="";int visibility=VISIBLE;
 void setEnabled(boolean v){enabled=v;}void setContentDescription(String v){description=v;}
 void setVisibility(int v){visibility=v;}int getVisibility(){return visibility;}
}
static class Button extends View {
 String label;Runnable click;
 void setOnClickListener(java.util.function.Consumer<View> listener){click=()->listener.accept(this);}
 void setText(String value){label=value;}
}
static class StationActionButton extends Button {
 static final int PRIMARY=1,SECONDARY=0,DANGER=2;
 StationActionButton(Object owner,String value,int tone,int icon){label=value;}
}
static class LinearLayout extends View {
 final List<View> children=new ArrayList<>();
 static class LayoutParams {int width,height,leftMargin;float weight;LayoutParams(int w,int h){width=w;height=h;}LayoutParams(int w,int h,float value){this(w,h);weight=value;}}
 void addView(View v,LayoutParams size){children.add(v);}int getChildCount(){return children.size();}
}
static class TextView extends View {String value="";void setText(String text){value=text;}CharSequence getText(){return value;}}
static class StationSocialIcon {static final int EXIT=1,READY=2,NOT_READY=3,PLAY=4,CHAT=5,CODE=6;}
static class StationPlayerModel {static boolean shareable(JSONObject snapshot){return snapshot.optBoolean("shareable");}}
static class StationApi {static class Cancellation {boolean cancelled(){return false;}}}
static class StationOnlineGame {static class Unavailable extends Exception {Unavailable(String value){super(value);}}}
static class State {JSONObject value;JSONObject get(){return value;}}
static class Feedback {String error="";void begin(){error="";}void fail(String value){error=value;}String text(JSONObject snapshot,boolean busy){return error;}}
static class Queue implements Executor {
 final ArrayDeque<Runnable> tasks=new ArrayDeque<>();
 public void execute(Runnable value){tasks.add(value);}
 void drain(){while(!tasks.isEmpty())tasks.remove().run();}
}
static class StationOnlineClient {
 final List<JSONObject> sent=new ArrayList<>();final State state;
 boolean failCall;
 StationOnlineClient(State value){state=value;}
 static JSONObject command(String action){return new JSONObject().put("command",action);}
 static String message(Throwable error){return error.getMessage();}
 JSONObject call(JSONObject command,boolean ignored,StationApi.Cancellation cancellation)throws Exception{if(failCall)throw new StationOnlineGame.Unavailable("Falha sintética");sent.add(command);return state.get();}
}
interface Work {JSONObject run(StationApi.Cancellation cancellation)throws Exception;}
boolean active=true,busy,launching,creating;int epoch,painted;
State state=new State();Feedback feedback=new Feedback();Queue commands=new Queue();
StationOnlineClient client=new StationOnlineClient(state);
Set<StationApi.Cancellation> requests=new HashSet<>();
Button create=new Button(),choose=new Button(),retry=new Button(),ready,start;TextView status=new TextView(),roomReadiness;View createSetup;
int conversationCalls,inviteCalls;String failure="",peerFeedback="";
int dp(int value){return value;}
void styleAction(Button button,int tone){}
LinearLayout roomControls(LinearLayout parent){LinearLayout value=new LinearLayout();parent.addView(value,new LinearLayout.LayoutParams(-1,-2));return value;}
void updateRoomSetupEnabled(){}void refreshPlayerSheet(){}void paint(JSONObject snapshot){}
void runOnUiThread(Runnable task){task.run();}
void deliver(JSONObject response,int generation){if(active&&generation==epoch)state.value=response;}
static void recordFailure(Throwable error){}
void clearRoomSetup(){}void showCreateMessage(String text,boolean error){}void unavailableLobby(){}void renderConversation(JSONObject snapshot){}
String onlineNotice(String value){return value;}
void openConversation(String peer,String name){conversationCalls++;}
void showRoomCode(){inviteCalls++;}
static Button find(LinearLayout parent,String value){for(View v:parent.children){if(v instanceof Button&&((Button)v).label.equals(value))return(Button)v;if(v instanceof LinearLayout){Button found=find((LinearLayout)v,value);if(found!=null)return found;}}return null;}
static int buttonCount(LinearLayout parent){int total=0;for(View v:parent.children){if(v instanceof Button)total++;if(v instanceof LinearLayout)total+=buttonCount((LinearLayout)v);}return total;}
LinearLayout render(JSONObject snapshot){JSONObject mine=snapshot.getJSONObject("room");String self=snapshot.optString("selfId");LinearLayout current=new LinearLayout();BODY return current;}
'''


MAIN = r'''
static JSONObject fixture(int capacity,int count,boolean allReady,String protocol){
 JSONArray roster=new JSONArray(),members=new JSONArray(),ready=new JSONArray();
 for(int i=1;i<=count;i++){String id="p"+i;roster.put(new JSONObject().put("peerId",id).put("slot",i).put("nickname","Jogador "+i).put("ready",allReady));members.put(id);if(allReady)ready.put(id);}
 JSONObject room=new JSONObject().put("roomId","room").put("itemId","game").put("generation",3).put("profileId","profile").put("profileSha256","hash").put("capacity",capacity).put("state","waiting").put("hostId","p1").put("recoveryProtocol",protocol).put("allowedPlayerCounts",new JSONArray().put(count)).put("roster",roster).put("members",members).put("ready",ready);
 String transport="station-stream.v3".equals(protocol)?"relay-wss-v3":"station-stream.v2".equals(protocol)?"relay-wss-v2":"relay-wss-v1";
 return new JSONObject().put("instance","instance").put("selfId","p1").put("room",room).put("transports",new JSONArray().put(transport));
}
static RoomCompactHost host(JSONObject fixture){RoomCompactHost host=new RoomCompactHost();host.state.value=fixture;return host;}
static JSONObject copy(JSONObject value){return new JSONObject(value.toString());}
static void reject(JSONObject current){RoomCompactHost host=host(current);host.startRoom(roomConfirmationKey(current));check(host.client.sent.isEmpty());check(host.commands.tasks.isEmpty());cases++;}
public static void main(String[] args){
 for(String protocol:new String[]{"station-stream.v3","station-stream.v2","legacy"})
 for(int capacity=2;capacity<=5;capacity++)for(int count=2;count<=capacity;count++){
  if(!"station-stream.v3".equals(protocol)&&count!=2)continue;
  JSONObject current=fixture(capacity,count,true,protocol);RoomCompactHost host=host(current);LinearLayout controls=host.render(current);
  Button start=find(controls,"Iniciar"),ready=find(controls,"Desmarcar"),leave=find(controls,"Sair"),chat=find(controls,"Conversa");
  check(start!=null&&ready!=null&&leave!=null&&chat!=null);host.start=start;host.updateStartState();check(start.enabled);
  start.click.run();start.click.run();check(host.busy);check(host.commands.tasks.size()==1);check(host.client.sent.isEmpty());
  host.commands.drain();check(host.client.sent.size()==1);JSONObject command=host.client.sent.get(0);
  check(command.optString("command").equals("start"));check(command.getString("roomId").equals("room"));check(command.getLong("generation")==3);check(command.getString("transport").equals(StationRoomStartState.transport(current)));
  check(!host.busy&&host.requests.isEmpty());cases++;
 }
 for(int capacity=2;capacity<=5;capacity++)for(int count=2;count<=capacity;count++)for(boolean allReady:new boolean[]{false,true}){
  JSONObject current=fixture(capacity,count,allReady,"station-stream.v3");
  if(!allReady)reject(current);
  for(String field:new String[]{"instance","roomId","itemId","profileId","profileSha256","capacity","generation","roster"}){
   RoomCompactHost host=host(current);LinearLayout controls=host.render(current);Button start=find(controls,"Iniciar");JSONObject changed=copy(current);
   JSONObject room=changed.getJSONObject("room");
   if(field.equals("instance"))changed.put(field,"new-instance");else if(field.equals("roster"))room.getJSONArray(field).getJSONObject(1).put("nickname","Novo nome");else if(field.equals("capacity")||field.equals("generation"))room.put(field,room.getInt(field)+1);else room.put(field,"changed");
   host.state.value=changed;start.click.run();check(host.commands.tasks.isEmpty());check(host.client.sent.isEmpty());cases++;
   host=host(current);controls=host.render(current);start=find(controls,"Iniciar");start.click.run();
   if(allReady){check(host.commands.tasks.size()==1);host.state.value=changed;host.commands.drain();check(host.client.sent.isEmpty());check(!host.feedback.error.isEmpty());}
   else check(host.commands.tasks.isEmpty());cases++;
  }
 }
 // Legacy rooms have no roster. Their displayed guest and ready state still bind start.
 for(String protocol:new String[]{"station-stream.v2","legacy"})for(String mutation:new String[]{"members","ready","hostId","recoveryProtocol"}){
  JSONObject current=fixture(2,2,true,protocol);current.getJSONObject("room").remove("roster");
  RoomCompactHost host=host(current);host.startRoom(roomConfirmationKey(current));host.commands.drain();check(host.client.sent.size()==1);cases++;
  JSONObject changed=copy(current),room=changed.getJSONObject("room");
  if(mutation.equals("members")){room.put("members",new JSONArray().put("p1").put("p3"));room.put("ready",new JSONArray().put("p1").put("p3"));}
  else if(mutation.equals("ready"))room.put("ready",new JSONArray().put("p2").put("p1"));
  else if(mutation.equals("hostId")){room.put("hostId","p2");changed.put("selfId","p2");}
  else {String next=protocol.equals("legacy")?"station-stream.v2":"legacy";room.put("recoveryProtocol",next);changed.put("transports",new JSONArray().put(next.equals("legacy")?"relay-wss-v1":"relay-wss-v2"));}
  check(StationRoomStartState.reason(changed).isEmpty());
  host=host(current);LinearLayout controls=host.render(current);host.state.value=changed;find(controls,"Iniciar").click.run();check(host.commands.tasks.isEmpty());check(host.client.sent.isEmpty());cases++;
  host=host(current);controls=host.render(current);find(controls,"Iniciar").click.run();host.state.value=changed;host.commands.drain();check(host.client.sent.isEmpty());check(!host.feedback.error.isEmpty());cases++;
 }
 JSONObject base=fixture(4,4,true,"station-stream.v3");
 for(String defect:new String[]{"guest","state","missing-self","duplicate-id","duplicate-slot","slot-zero","slot-high","missing-ready","count","empty-roster","capacity-low","capacity-high","transport"}){
  JSONObject bad=copy(base),room=bad.getJSONObject("room");JSONArray roster=room.getJSONArray("roster");
  switch(defect){
   case "guest":bad.put("selfId","p2");break;case "state":room.put("state","starting");break;
   case "missing-self":bad.put("selfId","absent");room.put("hostId","absent");break;
   case "duplicate-id":roster.getJSONObject(1).put("peerId","p1");break;
   case "duplicate-slot":roster.getJSONObject(1).put("slot",1);break;
   case "slot-zero":roster.getJSONObject(1).put("slot",0);break;case "slot-high":roster.getJSONObject(1).put("slot",5);break;
   case "missing-ready":roster.getJSONObject(1).put("ready",false);break;
   case "count":room.put("allowedPlayerCounts",new JSONArray().put(2));break;
   case "empty-roster":room.put("roster",new JSONArray());break;
   case "capacity-low":room.put("capacity",1);break;case "capacity-high":room.put("capacity",6);break;
   case "transport":bad.put("transports",new JSONArray());break;
  }
  reject(bad);
  RoomCompactHost host=host(base);host.render(base);host.startRoom(roomConfirmationKey(base));check(host.commands.tasks.size()==1);host.state.value=bad;host.commands.drain();check(host.client.sent.isEmpty());check(!host.feedback.error.isEmpty());cases++;
 }
 for(boolean active:new boolean[]{false,true})for(boolean busy:new boolean[]{false,true})for(boolean launching:new boolean[]{false,true}){
  RoomCompactHost host=host(base);host.active=active;host.busy=busy;host.launching=launching;host.startRoom(roomConfirmationKey(base));
  check(host.commands.tasks.size()==(active&&!busy&&!launching?1:0));cases++;
 }
 for(String protocol:new String[]{"station-stream.v3","station-stream.v2"})for(boolean readyValue:new boolean[]{false,true}){
  JSONObject snapshot=fixture(2,2,readyValue,protocol);RoomCompactHost host=host(snapshot);LinearLayout controls=host.render(snapshot);
  Button ready=find(controls,readyValue?"Desmarcar":"Estou pronto");ready.click.run();host.commands.drain();JSONObject sent=host.client.sent.get(0);
  check(sent.optString("command").equals("ready"));check(sent.optBoolean("value")==!readyValue);check(sent.optString("roomId").equals("room"));
  check("station-stream.v3".equals(protocol)?sent.optLong("generation")==3:!sent.has("generation"));
  host=host(snapshot);controls=host.render(snapshot);find(controls,"Sair").click.run();host.commands.drain();check(host.client.sent.get(0).optString("command").equals("leave"));
  host=host(snapshot);controls=host.render(snapshot);find(controls,"Conversa").click.run();check(host.conversationCalls==1);check(host.client.sent.isEmpty());cases++;
 }
 for(String roomState:new String[]{"waiting","starting","playing","recovering","ended",""})for(boolean owner:new boolean[]{false,true})for(boolean busy:new boolean[]{false,true})for(boolean launching:new boolean[]{false,true}){
  JSONObject snapshot=fixture(2,2,false,"station-stream.v3");snapshot.getJSONObject("room").put("state",roomState);if(!owner)snapshot.put("selfId","p2");
  RoomCompactHost host=host(snapshot);host.busy=busy;host.launching=launching;LinearLayout controls=host.render(snapshot);
  check(find(controls,"Sair")!=null&&find(controls,"Conversa")!=null);
  check((find(controls,"Iniciar")!=null)==(owner&&roomState.equals("waiting")));
  check((find(controls,"Estou pronto")!=null)==roomState.equals("waiting"));
  for(String label:new String[]{"Sair","Conversa","Iniciar","Estou pronto"}){Button button=find(controls,label);if(button!=null)check(button.enabled==(!busy&&!launching));}cases++;
 }
 for(int width=48;width<=1000;width+=7)for(int count=1;count<=5;count++)for(int scale=1;scale<=4;scale++){
  int[] wanted=new int[count];for(int i=0;i<count;i++)wanted[i]=(i%2==0?116:82)*scale;
  int[] boxes=roomControlLayout(width,wanted,48,6);
  for(int i=0;i<count;i++){int at=i*4;check(boxes[at]>=0&&boxes[at]+boxes[at+2]<=width);check(boxes[at+2]>=48&&boxes[at+3]==48);if(i>0){int previous=(i-1)*4;check(boxes[at+1]>boxes[previous+1]||boxes[at]>=boxes[previous]+boxes[previous+2]+6);}}cases++;
 }
 RoomCompactHost host=host(base);host.roomReadiness=new TextView();host.updateStartState();check(host.roomReadiness.visibility==View.GONE);host.busy=true;host.updateStartState();check(host.roomReadiness.visibility==View.VISIBLE);
 // A reason repeated by the global live status is not painted twice. Other notices remain visible.
 check(!separateRoomNotice("Convide os jogadores para esta sala.","Convide os jogadores para esta sala."));check(!separateRoomNotice("","Outro texto"));check(separateRoomNotice("Preparando a partida…","Falha anterior"));check(separateRoomNotice("Preparando a partida…",null));check(!separateRoomNotice(null,"Estado"));cases++;
 host=host(fixture(2,1,true,"station-stream.v3"));host.roomReadiness=new TextView();String pending=StationRoomStartState.reason(host.state.get());host.status.setText(pending);host.updateStartState();check(host.roomReadiness.visibility==View.GONE);check(host.roomReadiness.value.equals(pending));host.status.setText("Informação distinta");host.updateStartState();check(host.roomReadiness.visibility==View.VISIBLE);check(host.status.value.equals("Informação distinta"));cases++;
 // A failed authorized request clears busy and restores the current valid UI immediately.
 host=host(base);host.render(base);host.startRoom(roomConfirmationKey(base));host.updateStartState();check(!host.start.enabled);host.client.failCall=true;host.commands.drain();check(!host.busy);check(host.start.enabled);check(host.status.value.equals("Falha sintética"));check(host.feedback.error.equals("Falha sintética"));check(host.requests.isEmpty());cases++;
 host=host(base);host.render(base);host.busy=true;host.updateStartState();host.failure(new StationOnlineGame.Unavailable("Ignorar"),host.epoch+1);check(host.busy);check(!host.start.enabled);check(host.status.value.isEmpty());cases++;
 host=host(base);host.render(base);host.busy=true;host.updateStartState();host.active=false;host.failure(new StationOnlineGame.Unavailable("Ignorar"),host.epoch);check(host.busy);check(!host.start.enabled);check(host.status.value.isEmpty());cases++;
 System.out.println("PASS cases="+cases+" checks="+checks);
}
'''

# Drawable stubs record the actual selector/geometry commands. They do not render
# Android pixels. TextView.setBackground deliberately models drawable-padding
# adoption, which exposed the unpadded chips on the physical screenshot.
DRAWABLE_STUBS = r'''
static int cases,checks;
static void check(boolean ok){checks++;if(!ok)throw new AssertionError("drawable check "+checks);}
static class android {static class R {static class attr {static final int state_enabled=1,state_pressed=2,state_focused=3;}}}
static class Color {static final int TRANSPARENT=0;}
static class Gravity {static final int START=1,CENTER_VERTICAL=2;}
static class Drawable {}
static class ColorDrawable extends Drawable {final int color;ColorDrawable(int value){color=value;}}
static class GradientDrawable extends Drawable {int color,border,stroke;float radius;void setColor(int v){color=v;}void setCornerRadius(float v){radius=v;}void setStroke(int w,int c){stroke=w;border=c;}}
static class LayerDrawable extends Drawable {final Drawable[] children;int width,height,gravity;LayerDrawable(Drawable[] v){children=v;}void setLayerWidth(int layer,int v){check(layer==1);width=v;}void setLayerHeight(int layer,int v){check(layer==1);height=v;}void setLayerGravity(int layer,int v){check(layer==1);gravity=v;}}
static class StateListDrawable extends Drawable {
 final java.util.List<int[]> specs=new java.util.ArrayList<>();final java.util.List<Drawable> children=new java.util.ArrayList<>();
 void addState(int[] spec,Drawable drawable){specs.add(spec);children.add(drawable);}
 Drawable choose(boolean enabled,boolean pressed,boolean focused){
  boolean[] state={false,enabled,pressed,focused};
  for(int i=0;i<specs.size();i++){boolean fits=true;for(int wanted:specs.get(i))if(wanted>0?!state[wanted]:state[-wanted])fits=false;if(fits)return children.get(i);}
  throw new AssertionError("No drawable state");
 }
}
static class InsetDrawable extends Drawable {final Drawable child;final int top,bottom;InsetDrawable(Drawable value,int l,int t,int r,int b){child=value;top=t;bottom=b;}}
static class ColorStateList {final int value;ColorStateList(int v){value=v;}static ColorStateList valueOf(int v){return new ColorStateList(v);}}
static class RippleDrawable extends Drawable {final Drawable child;RippleDrawable(ColorStateList color,Drawable value,Drawable mask){child=value;}}
static class StationGraphicsPreferences {static final int CELL_EFFECTS=1,UI_TRANSITIONS=2;}
static class Graphics {boolean enabled;boolean isEnabled(int bit){return enabled;}}
static class TextView {Drawable background;int left,right;String order="";void setBackground(Drawable v){background=v;left=right=0;order+="B";}void setPadding(int l,int t,int r,int b){left=l;right=r;order+="P";}}
static final int PRIMARY=1,DANGER=2;
boolean navigation,compact,selected;int tone;Graphics graphics=new Graphics();Drawable background;Object tint=new Object();int left,right;
int green=0xff46dbff,white=0xffeff5ff;
int dp(float value){return Math.round(value);}boolean isSelected(){return selected;}
void setBackground(Drawable v){background=v;left=right=0;}void setBackgroundTintList(Object v){tint=v;}void setPadding(int l,int t,int r,int b){left=l;right=r;}
static Drawable unwrap(Drawable value){while(value instanceof InsetDrawable||value instanceof RippleDrawable)value=value instanceof InsetDrawable?((InsetDrawable)value).child:((RippleDrawable)value).child;return value;}
static void flat(Drawable value,int expected){
 if(expected==0){check(value instanceof ColorDrawable);check(((ColorDrawable)value).color==0);return;}
 check(value instanceof LayerDrawable);LayerDrawable layer=(LayerDrawable)value;check(layer.children.length==2);check(layer.children[0] instanceof ColorDrawable&&((ColorDrawable)layer.children[0]).color==0);check(layer.children[1] instanceof GradientDrawable);check(((GradientDrawable)layer.children[1]).color==expected);check(layer.width==2&&layer.height==14);check(layer.gravity==(Gravity.START|Gravity.CENTER_VERTICAL));
}
'''
DRAWABLE_MAIN = r'''
public static void main(String[] args){
 for(boolean selected:new boolean[]{false,true})for(boolean compact:new boolean[]{false,true})for(boolean effects:new boolean[]{false,true})for(int tone=0;tone<=2;tone++){
  ActionDrawableHost host=new ActionDrawableHost();host.navigation=true;host.selected=selected;host.compact=compact;host.tone=tone;host.graphics.enabled=effects;host.applyFace();
  check(host.background instanceof StateListDrawable);check(host.tint==null);check(host.left==10&&host.right==6);
  StateListDrawable states=(StateListDrawable)host.background;
  for(boolean enabled:new boolean[]{false,true})for(boolean pressed:new boolean[]{false,true})for(boolean focused:new boolean[]{false,true}){
   int expected=!enabled?0:pressed||focused?0xffeff5ff:selected?0xff46dbff:0;flat(states.choose(enabled,pressed,focused),expected);cases++;
  }
 }
 for(boolean compact:new boolean[]{false,true})for(boolean effects:new boolean[]{false,true})for(int tone=0;tone<=2;tone++){
  ActionDrawableHost host=new ActionDrawableHost();host.tone=tone;host.compact=compact;host.graphics.enabled=effects;host.applyFace();check(host.tint==null);check(host.left==12&&host.right==12);
  StateListDrawable states=(StateListDrawable)unwrap(host.background);
  GradientDrawable disabled=(GradientDrawable)states.choose(false,false,false);check(disabled.color==0xff142033&&disabled.border==0xff24334b);
  GradientDrawable pressed=(GradientDrawable)states.choose(true,true,false);check(pressed.color==(tone==DANGER?0xff663244:0xff315bab)&&pressed.border==0xffeff5ff);
  GradientDrawable normal=(GradientDrawable)states.choose(true,false,false);check(normal.color==(tone==PRIMARY?0xff244eb3:tone==DANGER?0xff3b1b2a:0xff151f2e));
  check(normal.border==(tone==PRIMARY?0xff4774cf:tone==DANGER?0xff824453:0xff304258));cases++;
 }
 ActionDrawableHost host=new ActionDrawableHost();TextView text=new TextView();
 for(int revision=0;revision<128;revision++){
  host.applyChoiceFace(text,revision%2==0);check(text.left==12&&text.right==12);check(text.order.endsWith("BP"));check(text.background instanceof InsetDrawable);InsetDrawable inset=(InsetDrawable)text.background;check(inset.top==8&&inset.bottom==8);cases++;
 }
 System.out.println("PASS drawableCases="+cases+" drawableChecks="+checks);
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--json-jar', type=Path, required=True)
    parser.add_argument('--android-jar', type=Path)
    parser.add_argument('--client-jar', type=Path)
    parser.add_argument('--rooms-jar', type=Path)
    args = parser.parse_args()
    if digest(args.json_jar) != JSON_SHA:
        raise ValueError('Use existing pinned org.json 20250517 jar')
    old_path, path = BASE/PKG/'StationRoomsActivity.java', ROOT/PKG/'StationRoomsActivity.java'
    old, new = old_path.read_text(encoding='utf-8'), path.read_text(encoding='utf-8')
    guards = []
    def guard(label, value):
        if not value: raise AssertionError(label)
        guards.append(label)
    preserved_methods = ('action','command','createRoom','confirmRoomSetup','prepareRoom','createVerifiedRoom','sameRoomSetupProfile','roomSetupContext','showRoomSetup','selectRoomMode','updateRoomSetupEnabled','join','joinConfirmed','launch','launchFailure','onStart','onStop','onDestroy','connect','deliver','readPoll','roomCoverCard','roomRowKey','beginRoomRows','reconcileRoomRows','clearRoomRows','loadHero','loadHeroProfile','bindHeroCover','roomAction','roomExplanation','roomInfo','roomSetupDescription')
    for name in preserved_methods:
        guard('Exact R122 method: '+name, method(old,name)==method(new,name))
    guard('Failure changes only UI refresh after busy clear',method(new,'failure').replace('busy=false;updateStartState();','busy=false;')==method(old,'failure'))
    for name in ('StationRoomStartState.java','StationRoomState.java','StationRoomRoster.java','StationOnlineClient.java','StationOnlineGame.java','StationRetroLaunch.java','StationOnlineCoverView.java','StationCreateGameCard.java','StationFlowPanel.java','StationCoverLayout.java','StationRoomArtwork.java'):
        guard('Exact R122 dependency: '+name,(BASE/PKG/name).read_bytes()==(ROOT/PKG/name).read_bytes())
    guard('No duplicate start confirmation', all(token not in new for token in ('startDialog','confirmationPlayers','confirmStart','Tudo pronto para jogar')))
    paint=method(new,'paint')
    start=paint.index('            JSONArray rd=mine.optJSONArray("ready");')
    end=paint.index('            if(StationLaunchPolicy.eligible(',start)
    fragment=paint[start:end]
    guard('Start captures displayed snapshot identity','final String displayedRoom=roomConfirmationKey(snapshot);' in fragment and '()->startRoom(displayedRoom)' in fragment)
    guard('Ready callback remains exact','()->command("ready","value",!contains(rd,self))' in fragment)
    guard('Human leave remains exact','()->command("leave",null,null)' in fragment)
    guard('No own-room synopsis duplicated','addSynopsis(current,' not in paint and 'showGameDetails(mine.optString("itemId"),roomExplanation(mine))' in paint)
    old_key=method(old,'roomConfirmationKey')
    new_key=method(new,'roomConfirmationKey')
    suffix='+"/"+room.optString("hostId")+"/"+room.optString("recoveryProtocol")+"/"+String.valueOf(room.optJSONArray("members"))+"/"+String.valueOf(room.optJSONArray("ready"))'
    guard('Fingerprint retains old fields and adds legacy host/protocol/members/ready',new_key.replace(suffix,'')==old_key)
    guard('Frameless join confirmation still exists without duplicate synopsis','if(item!=null&&!frameless)addSynopsis(outer,item,2,detail);' in new)
    guard('Required join confirmation keeps human acceptance','()->{codeDialog.dismiss();accepted.run();}' in new and 'roomAction(actions,"Cancelar",StationSocialIcon.CLOSE,StationActionButton.SECONDARY,()->codeDialog.dismiss())' in new)
    old_setup=method(old,'renderRoomSetup');new_setup=method(new,'renderRoomSetup')
    guard('Mode/count selection loops unchanged except post-background padding',old_setup[:old_setup.index('        setupDescription.setText')]==new_setup[:new_setup.index('        setupDescription.setText')].replace('applyChoiceFace(option,selected);','option.setBackground(choiceFace(selected));'))
    guard('Mode/count chips use same bounded packing as room actions','setupModes=roomControls(createSetup);' in new and 'setupCounts=roomControls(createSetup);' in new)
    guard('Instructions remain available on demand','showGameDetails(selectedItem,roomSetupDescription(setupProfile,setupCapacity))' in new)
    guard('Start command payload preserved', 'StationOnlineClient.command("start").put("roomId",latest.getJSONObject("room").getString("roomId")).put("generation",latest.getJSONObject("room").optLong("generation")).put("transport",StationRoomStartState.transport(latest))' in method(new,'startRoom'))
    guard('Transport checked on command worker','if(!contains(latest.optJSONArray("transports"),StationRoomStartState.transport(latest)))' in method(new,'startRoom'))
    guard('Room action targets remain 48dp','dp(48)' in method(new,'roomAction') and 'target=dp(48)' in new)
    guard('Nickname original exact line',next(line for line in old.splitlines() if 'nickname=new EditText' in line)==next(line for line in new.splitlines() if 'nickname=new EditText' in line))
    guard('Sidebar has no extra groups or margins','navigationSection(navItems,' not in method(new,'build') and 'bottomMargin=' not in method(new,'navButton'))
    guard('All command callback literals preserved',Counter(re.findall(r'(?<![\w.])command\([^;\n]*',old))==Counter(re.findall(r'(?<![\w.])command\([^;\n]*',new)))
    old_button=(BASE/PKG/'StationActionButton.java').read_text(encoding='utf-8')
    new_button=(ROOT/PKG/'StationActionButton.java').read_text(encoding='utf-8')
    for name in ('onDraw','allowsMotion','mayAnimate','animateIfVisible','setEnabled','onAttachedToWindow','onDetachedFromWindow','onWindowVisibilityChanged','onVisibilityChanged','onWindowFocusChanged','onGraphicsChanged','compactAppearance','setActionIcon','updateClip','onSizeChanged'):
        guard('Button lifecycle/economy exact: '+name,method(old_button,name)==method(new_button,name))
    guard('Navigation uses an independent all-state flat selector','navigationFace(Color.TRANSPARENT)' in new_button and 'navigationFace(isSelected()?0xff46dbff:Color.TRANSPARENT)' in new_button)
    guard('Focus/press/disabled retained',all(value in new_button for value in ('state_focused','state_pressed','state_enabled','face(fill,focus)')))
    for name in ('startRoom','roomConfirmationKey','action','command','failure','roomControlLayout','roomAction','createRoom','confirmRoomSetup','prepareRoom','createVerifiedRoom','selectRoomMode','showRoomSetup','updateRoomSetupEnabled','join','joinConfirmed','launch'):
        guard('Exact installed R123 authority: '+name,hashlib.sha256(method(new,name).encode('utf-8')).hexdigest()==INSTALLED_METHOD_SHA[name])
    guard('Summary uses natural height without viewport or weight','createSetup.addView(setupDescription,new LinearLayout.LayoutParams(-1,-2));' in new and 'ScrollView explanation=' not in method(new,'buildRoomSetup') and 'setupDescription.setMinHeight' not in new)
    guard('Choice padding restored after background',method(new,'applyChoiceFace').index('option.setBackground')<method(new,'applyChoiceFace').index('option.setPadding(dp(12)'))
    guard('Own-room game title not repeated','TextView game=text(current,client.name' not in paint)
    guard('Repeated notice suppresses only presentation','separateRoomNotice(notice,status==null?null:status.getText().toString())' in method(new,'updateStartState'))
    fragment=fragment.replace('roomReadiness=text(current,"",11,muted);roomReadiness.setPadding(0,dp(4),0,dp(4));roomReadiness.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);','roomReadiness=new TextView();')
    methods=first_method(new,'action')+'\n'+'\n'.join(method(new,name) for name in ('roomControlLayout','roomConfirmationKey','contains','roomAction','startRoom','separateRoomNotice','updateStartState','action','command','room','failure'))
    program='package org.emulationstation.frontend.netplay;\nimport org.json.*;import java.util.*;import java.util.concurrent.*;\npublic class RoomCompactHost {\n'+STUBS.replace('BODY',fragment)+'\n'+methods+'\n'+MAIN+'\n}\n'
    java_compile=None
    with tempfile.TemporaryDirectory(prefix='station-room-compact-r123-') as directory:
        temporary=Path(directory)
        probe=temporary/'RoomCompactHost.java';probe.write_text(program,encoding='utf-8')
        sources=[probe,ROOT/PKG/'StationRoomStartState.java']
        result=subprocess.run([str(args.jdk/'bin/javac.exe'),'-encoding','UTF-8','--release','8','-cp',str(args.json_jar),'-d',str(temporary),*map(str,sources)],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)
        result=subprocess.run([str(args.jdk/'bin/java.exe'),'-cp',str(temporary)+os.pathsep+str(args.json_jar),'org.emulationstation.frontend.netplay.RoomCompactHost'],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)
        output=result.stdout.strip()
        drawable_methods='\n'.join(method(new_button,name) for name in ('face','navigationFace','applyFace'))+'\n'+'\n'.join(method(new,name).replace('android.graphics.drawable.','') for name in ('bg','choiceFace','applyChoiceFace'))
        drawable=temporary/'ActionDrawableHost.java';drawable.write_text('public class ActionDrawableHost {\n'+DRAWABLE_STUBS+'\n'+drawable_methods+'\n'+DRAWABLE_MAIN+'\n}\n',encoding='utf-8')
        result=subprocess.run([str(args.jdk/'bin/javac.exe'),'-encoding','UTF-8','--release','8','-d',str(temporary),str(drawable)],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)
        result=subprocess.run([str(args.jdk/'bin/java.exe'),'-cp',str(temporary),'ActionDrawableHost'],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)
        drawable_counts=re.fullmatch(r'PASS drawableCases=(\d+) drawableChecks=(\d+)',result.stdout.strip())
        if not drawable_counts:raise AssertionError(result.stdout)
        dependencies=(args.android_jar,args.client_jar,args.rooms_jar)
        if any(dependencies):
            if not all(dependencies):raise ValueError('Supply android/client/rooms jars together')
            production=temporary/'production';production.mkdir()
            result=subprocess.run([str(args.jdk/'bin/javac.exe'),'-encoding','UTF-8','--release','8','-proc:none','-cp',os.pathsep.join(map(str,dependencies)),'-d',str(production),str(path),str(ROOT/PKG/'StationActionButton.java')],capture_output=True,text=True)
            if result.returncode:raise AssertionError(result.stderr)
            java_compile={'status':'PASS','sources':2,'classpathSha256':{label:digest(file) for label,file in zip(('androidApi34','r122Client','r122Rooms'),dependencies)}}
    counts=re.fullmatch(r'PASS cases=(\d+) checks=(\d+)',output)
    if not counts:raise AssertionError(output)
    receipt={'revision':'R123','status':'PASS','scope':'Actual production start/action/command/control layout bodies and StationRoomStartState executed on host; actual callback snippet rendered with minimal UI stubs; drawable-selector and padding-order bodies executed with recording stubs; source comparisons against R122 and installed R123. No Android pixel rendering/window, network, gameplay or hardware controller validation.','installedSource':INSTALLED_SOURCE,'cases':int(counts[1]),'checks':int(counts[2]),'drawableCases':int(drawable_counts[1]),'drawableChecks':int(drawable_counts[2]),'sourceGuards':len(guards),'guardNames':guards,'productionJavaCompile':java_compile,'sha256':{'rooms':digest(path),'actions':digest(ROOT/PKG/'StationActionButton.java'),'roomStartState':digest(ROOT/PKG/'StationRoomStartState.java'),'jsonJar':digest(args.json_jar),'testRecipe':digest(__file__)},'limits':['Host viewport packing is not an Android text/readability measurement.','Drawable stubs verify recorded selectors and padding order, not device pixels.','Below 48px usable width an action cannot preserve both bounds and a 48px target.','Physical flow, font scale and participants on an Android device remain to be checked.']}
    (ROOT/'evidence/room-compact-r123.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(output);print('PASS drawableCases='+str(drawable_counts[1])+' drawableChecks='+str(drawable_counts[2]));print('PASS sourceGuards='+str(len(guards)))


if __name__=='__main__':main()
