package org.emulationstation.frontend.netplay;
import android.app.*;
import android.os.*;
import android.content.*;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.*;
import android.view.*;
import android.widget.*;
import org.emulationstation.frontend.station.*;
import org.json.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

/** Real signed Station room snapshots. No public lobby, simulated peers or polling on the UI thread. */
public final class StationRoomsActivity extends Activity {
    private final ExecutorService commands=Executors.newSingleThreadExecutor();
    private final ExecutorService events=Executors.newSingleThreadExecutor();
    private final StationRoomState state=new StationRoomState();
    private final Set<StationApi.Cancellation> requests=Collections.synchronizedSet(new HashSet<>());
    private volatile boolean active;private boolean busy,launching;private volatile int epoch,page;
    private String selectedItem,launchKey="";private boolean returningFromGame;private volatile StationOnlineClient client;private StationOnlineGame prepared;
    private TextView status,title,peerTitle,roomTitle;private EditText nickname,chat;
    private LinearLayout peers,rooms;private Button create,retry,ready,start,leave;
    private Future<?> polling;private long painted=-1;private int paintedPage=-1;
    private final int green=0xff61ee8a,white=0xffeffff3,muted=0xffa8c0b0;
    @Override public void onCreate(Bundle saved){super.onCreate(saved);selectedItem=getIntent().getStringExtra("station.itemId");returningFromGame=saved!=null&&saved.getBoolean("returning");build();}
    @Override public void onSaveInstanceState(Bundle out){out.putBoolean("returning",returningFromGame);super.onSaveInstanceState(out);}
    private int dp(float x){return(int)(getResources().getDisplayMetrics().density*x+.5f);}
    private GradientDrawable bg(int color,int rim){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(12));d.setStroke(dp(1),rim);return d;}
    private LinearLayout vertical(){LinearLayout v=new LinearLayout(this);v.setOrientation(1);return v;}
    private TextView text(LinearLayout parent,String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setPadding(dp(8),dp(7),dp(8),dp(7));parent.addView(t,new LinearLayout.LayoutParams(-1,-2));return t;}
    private Button button(LinearLayout parent,String label,Runnable action,boolean primary){Button b=new Button(this);b.setText(label);b.setAllCaps(false);b.setTextSize(14);b.setTextColor(primary?0xff041309:white);b.setMinHeight(dp(44));b.setBackground(new RippleDrawable(ColorStateList.valueOf(0x5077ffa7),bg(primary?green:0xff12291b,primary?green:0xff284c35),null));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(dp(4),dp(4),dp(4),dp(4));parent.addView(b,lp);b.setOnClickListener(v->action.run());return b;}
    private void build(){
        getWindow().setStatusBarColor(0xff050b07);getWindow().setNavigationBarColor(0xff050b07);
        LinearLayout root=vertical();root.setPadding(dp(14),dp(8),dp(14),dp(8));root.setBackgroundColor(0xff050b07);setContentView(root);
        text(root,"LZ GAMES  /  TURBORAMA • ONLINE",12,green).setTypeface(null,Typeface.BOLD);
        title=text(root,"Encontre uma partida",24,white);title.setTypeface(null,Typeface.BOLD);
        LinearLayout toolbar=new LinearLayout(this);toolbar.setGravity(Gravity.CENTER_VERTICAL);root.addView(toolbar,new LinearLayout.LayoutParams(-1,-2));
        nickname=new EditText(this);nickname.setSingleLine(true);nickname.setTextColor(white);nickname.setHintTextColor(muted);nickname.setHint("Seu apelido");nickname.setText(getPreferences(0).getString("nickname","Jogador"));nickname.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(24)});toolbar.addView(nickname,new LinearLayout.LayoutParams(0,dp(44),1));
        LinearLayout buttons=new LinearLayout(this);toolbar.addView(buttons,new LinearLayout.LayoutParams(dp(390),-2));
        LinearLayout a=vertical(),b=vertical(),c=vertical();buttons.addView(a,new LinearLayout.LayoutParams(0,-2,1));buttons.addView(b,new LinearLayout.LayoutParams(0,-2,1));buttons.addView(c,new LinearLayout.LayoutParams(0,-2,1));
        create=button(a,"Criar sala",()->createRoom(),true);retry=button(b,"Reconectar",()->connect(),false);button(c,"Voltar",()->exitRooms(),false);
        LinearLayout columns=new LinearLayout(this);root.addView(columns,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout left=vertical(),right=vertical();left.setBackground(bg(0xff0a160f,0xff1d3a28));right.setBackground(bg(0xff0a160f,0xff1d3a28));
        LinearLayout.LayoutParams ll=new LinearLayout.LayoutParams(0,-1,.36f);ll.setMargins(0,dp(8),dp(6),dp(4));columns.addView(left,ll);
        LinearLayout.LayoutParams rl=new LinearLayout.LayoutParams(0,-1,.64f);rl.setMargins(dp(6),dp(8),0,dp(4));columns.addView(right,rl);
        peerTitle=text(left,"Jogadores online",16,green);ScrollView ps=new ScrollView(this);peers=vertical();ps.addView(peers);left.addView(ps,new LinearLayout.LayoutParams(-1,0,1));
        roomTitle=text(right,"Salas disponíveis",16,green);ScrollView rs=new ScrollView(this);rooms=vertical();rs.addView(rooms);right.addView(rs,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout chatbar=new LinearLayout(this);right.addView(chatbar,new LinearLayout.LayoutParams(-1,-2));chat=new EditText(this);chat.setTextColor(white);chat.setHintTextColor(muted);chat.setHint("Mensagem para sua sala");chat.setMaxLines(2);chat.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(500)});chatbar.addView(chat,new LinearLayout.LayoutParams(0,-2,1));LinearLayout send=vertical();chatbar.addView(send,new LinearLayout.LayoutParams(dp(100),-2));button(send,"Enviar",()->sendChat(),true);
        status=text(root,"Conectando com sua sessão…",12,muted);
    }
    @Override protected void onStart(){super.onStart();StationPresence.foreground(this,false);active=true;connect();}
    @Override protected void onStop(){active=false;epoch++;cancelAll();super.onStop();}
    @Override protected void onDestroy(){commands.shutdownNow();events.shutdownNow();super.onDestroy();}
    private void cancelAll(){if(polling!=null)polling.cancel(true);synchronized(requests){for(StationApi.Cancellation c:requests)c.cancel();requests.clear();}}
    private void connect(){if(!active)return;epoch++;cancelAll();int generation=epoch;state.reset();painted=-1;prepared=null;launchKey="";launching=false;
        String nick=nickname.getText().toString().trim();if(nick.isEmpty()){status.setText("Escolha seu apelido para entrar.");return;}getPreferences(0).edit().putString("nickname",nick).apply();getSharedPreferences("station-online-profile",0).edit().putString("nickname",nick).apply();
        status.setText("Consultando jogadores e salas…");create.setEnabled(false);polling=events.submit(()->{
            StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);
            try{
                client=new StationOnlineClient(this);client.page=page;
                if(returningFromGame){try{client.call(StationOnlineClient.command("leave"),false,cancel);}catch(StationApi.Failure e){if(!e.code.equals("STATION_ONLINE_ENTER_REQUIRED"))throw e;}returningFromGame=false;}
                JSONObject current=client.call(StationOnlineClient.command("enter").put("nickname",nick),false,cancel);deliver(current,generation);
                long heartbeat=SystemClock.elapsedRealtime();
                while(active&&epoch==generation&&!Thread.currentThread().isInterrupted()){
                    JSONObject latest=state.get();if(latest!=null)current=latest;
                    if(SystemClock.elapsedRealtime()-heartbeat>=20000){current=client.call(StationOnlineClient.command("heartbeat"),false,cancel);heartbeat=SystemClock.elapsedRealtime();deliver(current,generation);}
                    try{current=client.events(current,page,cancel);deliver(current,generation);}
                    catch(StationApi.Failure e){if(!e.code.equals("STATION_ONLINE_POLL_EXISTS"))throw e;Thread.sleep(1000);cancel.check();}
                }
            }catch(Exception e){if(!cancel.cancelled())failure(e,generation);}finally{requests.remove(cancel);}
        });
    }
    private void deliver(JSONObject snapshot,int generation)throws Exception {if(!active||generation!=epoch)return;if(!state.accept(snapshot))return;runOnUiThread(()->{if(active&&generation==epoch)paint(snapshot);});}
    private void failure(Throwable error,int generation){runOnUiThread(()->{if(active&&generation==epoch){status.setText(StationOnlineClient.message(error));busy=false;retry.setEnabled(true);create.setEnabled(state.get()!=null&&!launching);}});}
    interface Work {JSONObject run(StationApi.Cancellation cancel)throws Exception;}
    private void action(Work work){if(busy||!active||client==null||state.get()==null)return;busy=true;create.setEnabled(false);int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);
        commands.execute(()->{try{JSONObject response=work.run(cancel);deliver(response,generation);runOnUiThread(()->{if(active&&generation==epoch){busy=false;create.setEnabled(!launching);}});}catch(Exception e){if(!cancel.cancelled())failure(e,generation);}finally{requests.remove(cancel);}});
    }
    private JSONObject room(){JSONObject snapshot=state.get();return snapshot==null?null:snapshot.optJSONObject("room");}
    private void createRoom(){if(selectedItem==null){status.setText("Abra um jogo e toque em Jogar online para criar uma sala dele.");return;}
        status.setText("Conferindo arquivo e versão do motor…");action(cancel->{prepared=StationOnlineGame.prepare(this,client,selectedItem,state.get(),cancel);return client.call(prepared.fields(StationOnlineClient.command("create")),false,cancel);});}
    private void join(String roomId,String itemId){status.setText("Conferindo se os jogos são idênticos…");action(cancel->{prepared=StationOnlineGame.prepare(this,client,itemId,state.get(),cancel);return client.call(prepared.fields(StationOnlineClient.command("join").put("roomId",roomId)),false,cancel);});}
    private void command(String action,String key,Object value){action(cancel->{JSONObject c=StationOnlineClient.command(action);if(key!=null)c.put(key,value);JSONObject r=room();if(r!=null)c.put("roomId",r.getString("roomId"));return client.call(c,false,cancel);});}
    private void sendChat(){if(room()==null){status.setText("Entre em uma sala para conversar.");return;}String value=chat.getText().toString().trim();if(value.isEmpty())return;action(cancel->{JSONObject r=room();JSONObject result=client.call(StationOnlineClient.command("chat").put("roomId",r.getString("roomId")).put("text",value),false,cancel);runOnUiThread(()->{if(chat.getText().toString().trim().equals(value))chat.setText("");});return result;});}
    private String nickname(JSONObject snapshot,String id){JSONArray p=snapshot.optJSONArray("peers");if(p!=null)for(int i=0;i<p.length();i++){JSONObject v=p.optJSONObject(i);if(v!=null&&id.equals(v.optString("peerId")))return v.optString("nickname","Jogador");}return "Jogador";}
    private void paint(JSONObject snapshot){
        JSONObject latest=state.get();if(latest==null||snapshot.optLong("revision")<latest.optLong("revision"))return;
        if(snapshot.optInt("page")!=page)return;
        if(snapshot.optLong("revision")==painted&&snapshot.optInt("page")==paintedPage)return;painted=snapshot.optLong("revision");paintedPage=snapshot.optInt("page");
        create.setEnabled(!busy&&!launching);status.setText("Conexão direta entre aparelhos • servidor próprio para salas e chat");
        if(selectedItem!=null)title.setText(client.name(selectedItem));
        peers.removeAllViews();rooms.removeAllViews();JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");
        peerTitle.setText("Online • "+snapshot.optInt("totalPeers"));JSONArray list=snapshot.optJSONArray("peers");
        if(list!=null)for(int i=0;i<list.length();i++){JSONObject p=list.optJSONObject(i);if(p==null)continue;String id=p.optString("peerId"),name=p.optString("nickname");text(peers,"●  "+name+(self.equals(id)?" • você":""),15,white);
            if(!self.equals(id)){if(mine!=null&&self.equals(mine.optString("hostId")))button(peers,"Convidar "+name,()->command("invite","peerId",id),false);button(peers,"Bloquear contato",()->new AlertDialog.Builder(this).setTitle("Bloquear "+name+"?").setMessage("Oculta este contato enquanto estiver online e encerra a sala compartilhada.").setNegativeButton("Cancelar",null).setPositiveButton("Bloquear",(d,w)->command("block","peerId",id)).show(),false);}}
        if(snapshot.optInt("page")>0)button(peers,"Página anterior",()->page(-1),false);
        if(!snapshot.isNull("nextPage"))button(peers,"Próxima página",()->page(1),false);
        if(mine==null){
            roomTitle.setText("Salas disponíveis");JSONArray inv=snapshot.optJSONArray("invites");if(inv!=null)for(int i=0;i<inv.length();i++){JSONObject v=inv.optJSONObject(i);if(v==null)continue;String rid=v.optString("roomId");text(rooms,"Convite de "+nickname(snapshot,v.optString("fromPeerId")),14,green);if(!v.optString("itemId").isEmpty())button(rooms,"Aceitar convite",()->join(rid,v.optString("itemId")),true);button(rooms,"Dispensar",()->command("dismiss-invite","text",v.optString("inviteId")),false);}
            JSONArray rs=snapshot.optJSONArray("rooms");if(rs==null||rs.length()==0)text(rooms,"Nenhuma sala nesta página. Crie uma e convide outro jogador.",15,muted);
            if(rs!=null)for(int i=0;i<rs.length();i++){JSONObject r=rs.optJSONObject(i);if(r==null)continue;text(rooms,client.name(r.optString("itemId"))+" • "+r.optInt("players")+"/2",16,white);if("waiting".equals(r.optString("state"))&&r.optInt("players")<2)button(rooms,"Entrar na sala",()->join(r.optString("roomId"),r.optString("itemId")),true);}
        }else{
            roomTitle.setText(client.name(mine.optString("itemId")));text(rooms,"Sala privada para 2 jogadores • "+("connecting".equals(mine.optString("state"))?"preparando conexão":"starting".equals(mine.optString("state"))?"abrindo o anfitrião":"aguardando confirmação"),13,green);
            JSONArray members=mine.optJSONArray("members"),rd=mine.optJSONArray("ready");if(members!=null)for(int i=0;i<members.length();i++){String id=members.optString(i);text(rooms,nickname(snapshot,id)+(contains(rd,id)?" • pronto":" • aguardando"),15,white);}
            if("waiting".equals(mine.optString("state"))){ready=button(rooms,contains(rd,self)?"Cancelar pronto":"Estou pronto",()->command("ready","value",!contains(rd,self)),true);if(self.equals(mine.optString("hostId")))start=button(rooms,"Iniciar conexão direta",()->startDialog(),false);}
            leave=button(rooms,"Sair da sala",()->command("leave",null,null),false);
            JSONArray msgs=mine.optJSONArray("messages");if(msgs!=null)for(int i=0;i<msgs.length();i++){JSONObject m=msgs.optJSONObject(i);if(m!=null)text(rooms,m.optString("nickname")+"\n"+m.optString("text"),14,white);}
            if("connecting".equals(mine.optString("state"))||("starting".equals(mine.optString("state"))&&self.equals(mine.optString("hostId"))))launch(mine,snapshot);
        }
    }
    private static boolean contains(JSONArray a,String id){if(a!=null)for(int i=0;i<a.length();i++)if(id.equals(a.optString(i)))return true;return false;}
    private static JSONObject findRoom(JSONObject snapshot,String rid){JSONArray a=snapshot.optJSONArray("rooms");if(a!=null)for(int i=0;i<a.length();i++){JSONObject r=a.optJSONObject(i);if(r!=null&&rid.equals(r.optString("roomId")))return r;}return null;}
    private void page(int delta){if(busy||client==null)return;page=Math.max(0,Math.min(40,page+delta));client.page=page;action(cancel->client.call(StationOnlineClient.command("heartbeat"),false,cancel));}
    private void startDialog(){LinearLayout panel=vertical();panel.setPadding(dp(20),dp(8),dp(20),dp(8));text(panel,"No mesmo Wi-Fi, use o IP local deste telefone. Pela internet, é preciso um IP alcançável e liberar a porta no roteador. Conexão direta pode não funcionar sob CGNAT.",14,muted);
        EditText address=new EditText(this);address.setSingleLine(true);address.setTextColor(white);address.setHintTextColor(muted);address.setHint("IP deste anfitrião");address.setText(localAddress());panel.addView(address);
        EditText port=new EditText(this);port.setTextColor(white);port.setInputType(2);port.setText("55435");panel.addView(port);
        new AlertDialog.Builder(this).setTitle("Conectar os aparelhos").setView(panel).setNegativeButton("Cancelar",null).setPositiveButton("Iniciar",(d,w)->action(cancel->{int p;try{p=Integer.parseInt(port.getText().toString());}catch(NumberFormatException e){throw new StationOnlineGame.Unavailable("Porta inválida.");}return client.call(StationOnlineClient.command("start").put("roomId",room().getString("roomId")).put("address",address.getText().toString().trim()).put("port",p),false,cancel);})).show();}
    private String localAddress(){try{Enumeration<NetworkInterface> ns=NetworkInterface.getNetworkInterfaces();while(ns.hasMoreElements()){NetworkInterface n=ns.nextElement();if(!n.isUp()||n.isLoopback())continue;Enumeration<InetAddress> as=n.getInetAddresses();while(as.hasMoreElements()){InetAddress a=as.nextElement();if(a instanceof Inet4Address&&a.isSiteLocalAddress())return a.getHostAddress();}}}catch(Exception ignored){}return "";}
    private void launch(JSONObject room,JSONObject snapshot){String key=room.optString("roomId")+":"+room.optLong("generation");if(launching||key.equals(launchKey))return;launchKey=key;launching=true;int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);status.setText("Preparando partida direta…");
        commands.execute(()->{try{StationOnlineGame game=prepared;if(game==null)game=StationOnlineGame.prepare(this,client,room.getString("itemId"),snapshot,cancel);game.verifyRoom(room);String file=StationRetroLaunch.prepare(this,game,room,snapshot,cancel);runOnUiThread(()->{if(active&&generation==epoch){returningFromGame=true;try{startActivity(new Intent(this,StationRetroActivity.class).putExtra("station.launch",file).putExtra(StationGameSession.EXTRA,StationGameSession.create(this,room.optString("roomId"))));}catch(RuntimeException e){returningFromGame=false;launching=false;StationRetroLaunch.discard(this,file);failure(e,generation);}}else StationRetroLaunch.discard(this,file);});}catch(Exception e){launching=false;failure(e,generation);}finally{requests.remove(cancel);}});
    }
    private void exitRooms(){if(busy)return;if(client==null||state.get()==null){finish();return;}action(cancel->{JSONObject result=client.call(StationOnlineClient.command("offline"),false,cancel);runOnUiThread(this::finish);return result;});}
    @Override public void onBackPressed(){exitRooms();}
}
