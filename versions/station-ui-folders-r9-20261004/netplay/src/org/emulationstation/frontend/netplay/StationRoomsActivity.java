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
    private TextView status,title,subtitle,connection,peerTitle,roomTitle,chatTitle;private EditText nickname,chat;
    private ScrollView peerScroll,roomScroll,chatScroll;private LinearLayout leftPanel,middlePanel,rightPanel;private boolean narrow;private ImageView heroCover;private StationLobbyIcon heroSymbol;private TextView gamePlatform;private android.graphics.Bitmap heroBitmap;private int paintedMessages;private String paintedRoom="";
    private LinearLayout peers,rooms,messages;private Button create,retry,ready,start,leave,send;
    private Future<?> polling;private long painted=-1;private int paintedPage=-1;
    private final int green=0xff61ee8a,white=0xffeffff3,muted=0xffa8c0b0;
    @Override public void onCreate(Bundle saved){super.onCreate(saved);selectedItem=getIntent().getStringExtra("station.itemId");returningFromGame=saved!=null&&saved.getBoolean("returning");build();}
    @Override public void onSaveInstanceState(Bundle out){out.putBoolean("returning",returningFromGame);super.onSaveInstanceState(out);}
    private int dp(float x){return(int)(getResources().getDisplayMetrics().density*x+.5f);}
    private GradientDrawable bg(int color,int rim){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(14));d.setStroke(dp(1),rim);return d;}
    private LinearLayout vertical(){LinearLayout v=new LinearLayout(this);v.setOrientation(1);return v;}
    private LinearLayout row(){LinearLayout v=new LinearLayout(this);v.setGravity(Gravity.CENTER_VERTICAL);return v;}
    private TextView label(String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setFontFeatureSettings("kern");t.setIncludeFontPadding(false);return t;}
    private TextView text(LinearLayout parent,String value,int size,int color){TextView t=label(value,size,color);t.setPadding(0,dp(5),0,dp(5));parent.addView(t,new LinearLayout.LayoutParams(-1,-2));return t;}
    private void bold(TextView t){t.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));}
    private Button button(LinearLayout parent,String value,Runnable action,boolean primary){
        Button b=new StationActionButton(this,value,primary);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(44));lp.setMargins(0,dp(6),0,dp(2));parent.addView(b,lp);b.setOnClickListener(v->action.run());return b;
    }
    private Button inline(LinearLayout parent,String value,int width,Runnable action,boolean primary){
        LinearLayout holder=vertical();LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(dp(width),-2);lp.setMargins(dp(8),0,0,0);parent.addView(holder,lp);Button result=button(holder,value,action,primary); result.setLayoutParams(new LinearLayout.LayoutParams(-1,dp(44)));return result;
    }
    private TextView pill(String value,int color){TextView t=label(value,10,color);bold(t);t.setSingleLine(true);t.setGravity(Gravity.CENTER);t.setPadding(dp(9),dp(5),dp(9),dp(5));t.setBackground(bg(0xff14241c,0xff294634));return t;}
    private LinearLayout card(LinearLayout parent){LinearLayout c=vertical();c.setPadding(dp(12),dp(9),dp(12),dp(9));c.setBackground(bg(0xff112219,0xff254232));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,0,0,dp(8));parent.addView(c,lp);return c;}
    private LinearLayout panel(LinearLayout parent,float weight,boolean narrow){LinearLayout v=vertical();v.setPadding(dp(12),dp(12),dp(12),dp(10));v.setBackground(bg(0xff0b1711,0xff24392c));LinearLayout.LayoutParams lp=narrow?new LinearLayout.LayoutParams(-1,dp(280)):new LinearLayout.LayoutParams(0,-1,weight);lp.setMargins(0,0,narrow?0:dp(10),narrow?dp(10):0);parent.addView(v,lp);return v;}
    private ScrollView scroll(LinearLayout parent,LinearLayout content){ScrollView s=new ScrollView(this);s.setFillViewport(true);s.setClipToPadding(false);s.setPadding(0,dp(10),0,0);s.setVerticalScrollBarEnabled(false);s.addView(content,new ScrollView.LayoutParams(-1,-2));parent.addView(s,new LinearLayout.LayoutParams(-1,0,1));return s;}
    private void empty(LinearLayout parent,String icon,String heading,String detail){
        LinearLayout box=vertical();box.setGravity(Gravity.CENTER);box.setPadding(dp(10),dp(10),dp(10),dp(10));parent.addView(box,new LinearLayout.LayoutParams(-1,-1));
        StationLobbyIcon mark=new StationLobbyIcon(this,parent==peers?1:parent==messages?3:2);box.addView(mark,new LinearLayout.LayoutParams(dp(72),dp(72)));
        TextView h=text(box,heading,14,white);h.setGravity(Gravity.CENTER);h.setPadding(0,dp(13),0,dp(6));bold(h);
        TextView d=text(box,detail,12,muted);d.setGravity(Gravity.CENTER);d.setLineSpacing(dp(2),1);
    }
    private void field(EditText field,String hint){field.setTextSize(13);field.setTextColor(white);field.setHintTextColor(muted);field.setPadding(dp(12),dp(8),dp(12),dp(8));field.setBackground(bg(0xff08130d,0xff2b4935));field.setHint(hint);}
    private void setConnection(String value,boolean online){connection.setText((online?"●  ":"○  ")+value);connection.setTextColor(online?green:muted);}
    private void composer(boolean enabled){chat.setEnabled(enabled);send.setEnabled(enabled);chat.setHint(enabled?"Escreva para sua sala…":"Entre em uma sala");}
    private void loadingLobby(){
        setConnection("Conectando",false);peerTitle.setText("JOGADORES");roomTitle.setText("SALAS DISPONÍVEIS");peers.removeAllViews();rooms.removeAllViews();messages.removeAllViews();
        empty(peers,"…","Buscando jogadores","A lista aparece assim que a conexão for confirmada.");empty(rooms,"…","Abrindo o lobby","Preparando suas salas e seus convites.");empty(messages,"↗","Conversa da sala","Entre em uma partida para conversar com outro jogador.");composer(false);roomLayout(false);
    }
    private void unavailableLobby(){
        setConnection("Indisponível",false);peers.removeAllViews();rooms.removeAllViews();
        empty(peers,"○","Conexão pendente","Os jogadores aparecem quando o serviço estiver disponível.");empty(rooms,"!","Salas indisponíveis","Não foi possível conectar agora. Use Reconectar para tentar novamente.");composer(false);
    }
    private void build(){
        getWindow().setStatusBarColor(0xff050c08);getWindow().setNavigationBarColor(0xff050c08);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        narrow=getResources().getConfiguration().screenWidthDp<600;
        LinearLayout root=vertical();root.setPadding(dp(18),dp(12),dp(12),dp(10));root.setBackground(new GradientDrawable(GradientDrawable.Orientation.TL_BR,new int[]{0xff101d15,0xff050b08,0xff09150e}));setContentView(root);
        LinearLayout header=row();root.addView(header,new LinearLayout.LayoutParams(-1,dp(44)));
        TextView brand=pill("LZ GAMES",green);if(!narrow)header.addView(brand,new LinearLayout.LayoutParams(dp(80),dp(28)));
        title=label("Salas online",narrow?18:21,white);bold(title);LinearLayout.LayoutParams titleLp=new LinearLayout.LayoutParams(0,-2,1);titleLp.setMargins(dp(12),0,0,0);header.addView(title,titleLp);
        connection=pill("○  Conectando",muted);header.addView(connection,new LinearLayout.LayoutParams(-2,dp(28)));
        inline(header,"Voltar",76,()->exitRooms(),false);
        LinearLayout toolbar=new StationLobbySurface(this);toolbar.setGravity(Gravity.CENTER_VERTICAL);toolbar.setPadding(dp(14),dp(10),dp(14),dp(10));LinearLayout.LayoutParams tl=new LinearLayout.LayoutParams(-1,dp(100));tl.setMargins(0,dp(9),dp(6),dp(12));root.addView(toolbar,tl);
        FrameLayout art=new FrameLayout(this);toolbar.addView(art,new LinearLayout.LayoutParams(dp(60),dp(78)));heroSymbol=new StationLobbyIcon(this,2);art.addView(heroSymbol,new FrameLayout.LayoutParams(-1,-1));heroCover=new ImageView(this);heroCover.setScaleType(ImageView.ScaleType.FIT_CENTER);heroCover.setContentDescription("Capa do jogo selecionado");art.addView(heroCover,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout context=vertical();LinearLayout.LayoutParams contextLp=new LinearLayout.LayoutParams(0,-2,1);contextLp.setMargins(dp(14),0,dp(8),0);toolbar.addView(context,contextLp);gamePlatform=text(context,"TURBORAMA  /  MULTIPLAYER",10,green);bold(gamePlatform);
        subtitle=text(context,selectedItem==null?"Sua próxima partida começa aqui":"Preparando seu jogo…",18,white);bold(subtitle);subtitle.setMaxLines(2);subtitle.setEllipsize(android.text.TextUtils.TruncateAt.END);
        text(context,"2 jogadores  ·  Convites  ·  Chat da sala",11,muted);
        nickname=new EditText(this);field(nickname,"Seu apelido");nickname.setSingleLine(true);nickname.setContentDescription("Seu apelido nas salas");nickname.setText(getPreferences(0).getString("nickname","Jogador"));nickname.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(24)});
        LinearLayout actions=toolbar;
        if(narrow){actions=row();LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54));ap.setMargins(0,0,0,dp(10));root.addView(actions,ap);actions.addView(nickname,new LinearLayout.LayoutParams(0,dp(44),1));}else{LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(dp(140),dp(44));np.setMargins(dp(10),dp(4),0,0);toolbar.addView(nickname,np);}
        create=inline(actions,"+  Criar sala",112,()->createRoom(),true);((StationActionButton)create).setMotion(true);create.setEnabled(false);retry=inline(actions,"Reconectar",102,()->connect(),false);
        LinearLayout columns=new LinearLayout(this);columns.setOrientation(narrow?1:0);
        if(narrow){ScrollView body=new ScrollView(this);body.addView(columns);root.addView(body,new LinearLayout.LayoutParams(-1,0,1));}else root.addView(columns,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout left=panel(columns,.27f,narrow),middle=panel(columns,.73f,narrow),right=panel(columns,.32f,narrow);leftPanel=left;middlePanel=middle;rightPanel=right;right.setVisibility(View.GONE);
        peerTitle=text(left,"JOGADORES",11,muted);bold(peerTitle);peers=vertical();peerScroll=scroll(left,peers);
        roomTitle=text(middle,"SALAS DISPONÍVEIS",11,green);bold(roomTitle);rooms=vertical();roomScroll=scroll(middle,rooms);
        chatTitle=text(right,"CHAT DA SALA",11,muted);bold(chatTitle);messages=vertical();chatScroll=scroll(right,messages);
        LinearLayout chatbar=row();right.addView(chatbar,new LinearLayout.LayoutParams(-1,-2));chat=new EditText(this);field(chat,"Entre em uma sala");chat.setMaxLines(2);chat.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(500)});chat.setContentDescription("Mensagem para os jogadores da sala");chatbar.addView(chat,new LinearLayout.LayoutParams(0,dp(44),1));send=inline(chatbar,"↑",44,()->sendChat(),true);send.setContentDescription("Enviar mensagem");
        status=text(root,"Conectando com sua sessão…",11,muted);status.setMaxLines(2);status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);loadingLobby();
    }
    private void contactActions(View anchor,String id,String name){PopupMenu menu=new PopupMenu(this,anchor);menu.getMenu().add("Bloquear contato").setOnMenuItemClickListener(item->{
        AlertDialog dialog=new AlertDialog.Builder(new ContextThemeWrapper(this,android.R.style.Theme_Material_Dialog_Alert)).setTitle("Bloquear "+name+"?").setMessage("Oculta este contato enquanto estiver online e encerra a sala compartilhada.").setNegativeButton("Cancelar",null).setPositiveButton("Bloquear",(d,w)->command("block","peerId",id)).create();styleDialog(dialog);return true;});menu.show();}
    private void styleDialog(AlertDialog dialog){dialog.setOnShowListener(d->{dialog.getWindow().setBackgroundDrawable(bg(0xff102018,0xff34583f));dialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(green);dialog.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(muted);TextView msg=dialog.findViewById(android.R.id.message);if(msg!=null)msg.setTextColor(white);});dialog.show();}

    @Override protected void onStart(){super.onStart();StationPresence.foreground(this,false);active=true;connect();loadHero();}
    @Override protected void onStop(){active=false;epoch++;cancelAll();super.onStop();}
    @Override protected void onDestroy(){commands.shutdownNow();events.shutdownNow();heroCover.setImageDrawable(null);if(heroBitmap!=null){heroBitmap.recycle();heroBitmap=null;}super.onDestroy();}
    private void cancelAll(){if(polling!=null)polling.cancel(true);synchronized(requests){for(StationApi.Cancellation c:requests)c.cancel();requests.clear();}}
    private void connect(){if(!active)return;epoch++;cancelAll();int generation=epoch;state.reset();painted=-1;prepared=null;launchKey="";launching=false;loadingLobby();
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
    private void failure(Throwable error,int generation){runOnUiThread(()->{if(active&&generation==epoch){status.setText(StationOnlineClient.message(error));if(state.get()==null)unavailableLobby();busy=false;retry.setEnabled(true);create.setEnabled(state.get()!=null&&!launching);}});}
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
        create.setEnabled(!busy&&!launching);setConnection("Online",true);status.setText("Convide um jogador ou entre em uma sala para começar.");
        if(selectedItem!=null)subtitle.setText(client.name(selectedItem));
        int py=peerScroll.getScrollY(),ry=roomScroll.getScrollY(),cy=chatScroll.getScrollY();
        peers.removeAllViews();rooms.removeAllViews();messages.removeAllViews();JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");composer(mine!=null);roomLayout(mine!=null);
        peerTitle.setText("JOGADORES  ·  "+snapshot.optInt("totalPeers"));JSONArray list=snapshot.optJSONArray("peers");
        if(list==null||list.length()==0)empty(peers,"○","Ninguém nesta página","Os jogadores conectados aparecerão aqui.");
        if(list!=null)for(int i=0;i<list.length();i++){
            JSONObject p=list.optJSONObject(i);if(p==null)continue;String id=p.optString("peerId"),name=p.optString("nickname");boolean isSelf=self.equals(id);
            LinearLayout contact=card(peers),line=row();contact.addView(line,new LinearLayout.LayoutParams(-1,-2));
            String initial=name.trim().isEmpty()?"?":name.trim().substring(0,name.trim().offsetByCodePoints(0,1)).toUpperCase(java.util.Locale.ROOT);
            TextView avatar=label(initial,15,green);bold(avatar);avatar.setGravity(Gravity.CENTER);avatar.setBackground(bg(0xff234330,0xff39664a));line.addView(avatar,new LinearLayout.LayoutParams(dp(32),dp(32)));
            LinearLayout identity=vertical();LinearLayout.LayoutParams identityLp=new LinearLayout.LayoutParams(0,-2,1);identityLp.setMargins(dp(8),0,0,0);line.addView(identity,identityLp);
            TextView n=text(identity,name,13,white);bold(n);n.setSingleLine(true);n.setEllipsize(android.text.TextUtils.TruncateAt.END);text(identity,isSelf?"● Você":"● Online",10,green);
            if(!isSelf){TextView more=label("⋮",22,muted);more.setGravity(Gravity.CENTER);more.setContentDescription("Opções de "+name);line.addView(more,new LinearLayout.LayoutParams(dp(36),dp(44)));more.setOnClickListener(v->contactActions(v,id,name));if(mine!=null&&self.equals(mine.optString("hostId")))button(contact,"Convidar",()->command("invite","peerId",id),false);}
        }
        if(snapshot.optInt("page")>0)button(peers,"Página anterior",()->page(-1),false);
        if(!snapshot.isNull("nextPage"))button(peers,"Próxima página",()->page(1),false);
        if(mine==null){
            roomTitle.setText("SALAS DISPONÍVEIS");chatTitle.setText("CHAT DA SALA");JSONArray inv=snapshot.optJSONArray("invites");
            if(inv!=null)for(int i=0;i<inv.length();i++){JSONObject v=inv.optJSONObject(i);if(v==null)continue;String rid=v.optString("roomId");LinearLayout invitation=card(rooms);TextView tag=text(invitation,"CONVITE RECEBIDO",10,green);bold(tag);bold(text(invitation,nickname(snapshot,v.optString("fromPeerId")),15,white));if(!v.optString("itemId").isEmpty())button(invitation,"Aceitar convite",()->join(rid,v.optString("itemId")),true);button(invitation,"Dispensar",()->command("dismiss-invite","text",v.optString("inviteId")),false);}
            JSONArray rs=snapshot.optJSONArray("rooms");if((rs==null||rs.length()==0)&&(inv==null||inv.length()==0))empty(rooms,"+","A próxima sala pode ser sua","Crie uma sala deste jogo e convide alguém da lista.");
            if(rs!=null)for(int i=0;i<rs.length();i++){JSONObject r=rs.optJSONObject(i);if(r==null)continue;LinearLayout entry=card(rooms);TextView game=text(entry,client.name(r.optString("itemId")),15,white);bold(game);game.setMaxLines(2);game.setEllipsize(android.text.TextUtils.TruncateAt.END);boolean available="waiting".equals(r.optString("state"))&&r.optInt("players")<2;text(entry,r.optInt("players")+" / 2 jogadores  ·  "+(available?"Vaga disponível":"Em preparação"),11,available?green:muted);if(available)button(entry,"Entrar na sala  →",()->join(r.optString("roomId"),r.optString("itemId")),true);}
            empty(messages,"↗","O encontro começa aqui","Entre em uma sala para combinar a partida e conversar.");paintedMessages=0;paintedRoom="";
        }else{
            roomTitle.setText("SUA SALA");chatTitle.setText("CHAT  ·  SUA SALA");create.setEnabled(false);
            LinearLayout current=card(rooms);TextView game=text(current,client.name(mine.optString("itemId")),16,white);bold(game);
            String phase="connecting".equals(mine.optString("state"))?"Conectando os jogadores":"starting".equals(mine.optString("state"))?"Abrindo a partida":"Aguardando confirmação";
            text(current,phase,12,green);JSONArray members=mine.optJSONArray("members"),rd=mine.optJSONArray("ready");
            if(members!=null)for(int i=0;i<members.length();i++){String id=members.optString(i);text(current,(contains(rd,id)?"✓  ":"○  ")+nickname(snapshot,id)+(self.equals(id)?" (você)":"")+(contains(rd,id)?"  ·  Pronto":"  ·  Aguardando"),13,contains(rd,id)?green:white);}
            if("waiting".equals(mine.optString("state"))){ready=button(current,contains(rd,self)?"Cancelar confirmação":"Estou pronto  ✓",()->command("ready","value",!contains(rd,self)),true);if(self.equals(mine.optString("hostId")))start=button(current,"Iniciar partida  →",()->startDialog(),false);}
            leave=button(current,"Sair da sala",()->command("leave",null,null),false);
            JSONArray msgs=mine.optJSONArray("messages");int count=msgs==null?0:msgs.length();
            if(count==0)empty(messages,"…","Diga olá","As mensagens ficam visíveis aos jogadores desta sala.");
            if(msgs!=null)for(int i=0;i<msgs.length();i++){JSONObject m=msgs.optJSONObject(i);if(m==null)continue;LinearLayout bubble=card(messages);boolean own=self.equals(m.optString("fromPeerId"));LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)bubble.getLayoutParams();bp.setMargins(own?dp(18):0,0,own?0:dp(18),dp(8));bubble.setLayoutParams(bp);bubble.setBackground(bg(own?0xff153924:0xff112219,own?0xff326243:0xff254232));bold(text(bubble,m.optString("nickname"),11,green));TextView message=text(bubble,m.optString("text"),13,white);message.setTextIsSelectable(true);message.setLineSpacing(dp(2),1);}
            if(count!=paintedMessages||!mine.optString("roomId").equals(paintedRoom)){chatScroll.post(()->chatScroll.fullScroll(View.FOCUS_DOWN));}else chatScroll.post(()->chatScroll.scrollTo(0,cy));paintedMessages=count;paintedRoom=mine.optString("roomId");
            if("connecting".equals(mine.optString("state"))||("starting".equals(mine.optString("state"))&&self.equals(mine.optString("hostId"))))launch(mine,snapshot);
        }
        peerScroll.post(()->peerScroll.scrollTo(0,py));roomScroll.post(()->roomScroll.scrollTo(0,ry));
    }

    private void roomLayout(boolean joined){
        rightPanel.setVisibility(joined?View.VISIBLE:View.GONE);
        if(!narrow){LinearLayout.LayoutParams l=(LinearLayout.LayoutParams)leftPanel.getLayoutParams(),m=(LinearLayout.LayoutParams)middlePanel.getLayoutParams(),r=(LinearLayout.LayoutParams)rightPanel.getLayoutParams();l.weight=joined?.24f:.27f;m.weight=joined?.42f:.73f;r.weight=.34f;leftPanel.setLayoutParams(l);middlePanel.setLayoutParams(m);rightPanel.setLayoutParams(r);}
    }
    private void loadHero(){
        if(selectedItem==null||heroBitmap!=null)return;final int generation=epoch;
        commands.execute(()->{
            android.graphics.Bitmap bitmap=null;
            try{
                StationAndroid app=StationAndroid.get(this);StationCoordinator.Library library=app.coordinator.current();StationCatalog.Item item=library==null?null:library.catalog.find(selectedItem);if(item==null)return;
                String name=item.name,platform=item.platform;
                runOnUiThread(()->{if(active&&generation==epoch){subtitle.setText(name);gamePlatform.setText(platform.toUpperCase(java.util.Locale.ROOT)+"  /  MULTIPLAYER");}});
                // Display the existing validated catalog cache only; no second cover download.
                java.nio.file.Path file=app.privateFiles.resolve("station-v2/covers").resolve(item.coverId+"-"+item.revision+".img");
                if(java.nio.file.Files.isRegularFile(file,java.nio.file.LinkOption.NOFOLLOW_LINKS)&&java.nio.file.Files.size(file)<=5*1024*1024){
                    byte[] bytes=StationFiles.readBounded(file,5*1024*1024);
                    android.graphics.BitmapFactory.Options options=new android.graphics.BitmapFactory.Options();options.inJustDecodeBounds=true;android.graphics.BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
                    if(options.outWidth<1||options.outHeight<1||options.outWidth>8192||options.outHeight>8192)return;
                    options.inJustDecodeBounds=false;options.inSampleSize=1;while(Math.max(options.outWidth,options.outHeight)/options.inSampleSize>256)options.inSampleSize*=2;
                    bitmap=android.graphics.BitmapFactory.decodeByteArray(bytes,0,bytes.length,options);
                }
            }catch(Exception unavailable){android.util.Log.i("StationOnline","Selected game artwork not cached");}
            final android.graphics.Bitmap readyBitmap=bitmap;
            if(readyBitmap!=null)runOnUiThread(()->{if(active&&generation==epoch&&!isDestroyed()){heroBitmap=readyBitmap;heroCover.setImageBitmap(readyBitmap);heroSymbol.setVisibility(View.GONE);}else readyBitmap.recycle();});
        });
    }
    private static boolean contains(JSONArray a,String id){if(a!=null)for(int i=0;i<a.length();i++)if(id.equals(a.optString(i)))return true;return false;}
    private static JSONObject findRoom(JSONObject snapshot,String rid){JSONArray a=snapshot.optJSONArray("rooms");if(a!=null)for(int i=0;i<a.length();i++){JSONObject r=a.optJSONObject(i);if(r!=null&&rid.equals(r.optString("roomId")))return r;}return null;}
    private void page(int delta){if(busy||client==null)return;page=Math.max(0,Math.min(40,page+delta));client.page=page;action(cancel->client.call(StationOnlineClient.command("heartbeat"),false,cancel));}
    private void startDialog(){LinearLayout panel=vertical();panel.setPadding(dp(20),dp(8),dp(20),dp(8));text(panel,"No mesmo Wi-Fi, use o IP local deste telefone. Pela internet, é preciso um IP alcançável e liberar a porta no roteador. Conexão direta pode não funcionar sob CGNAT.",14,muted);
        EditText address=new EditText(this);field(address,"IP deste anfitrião");address.setSingleLine(true);address.setTextColor(white);address.setHintTextColor(muted);address.setHint("IP deste anfitrião");address.setText(localAddress());panel.addView(address);
        EditText port=new EditText(this);field(port,"Porta");port.setTextColor(white);port.setInputType(2);port.setText("55435");panel.addView(port);
        AlertDialog dialog=new AlertDialog.Builder(new ContextThemeWrapper(this,android.R.style.Theme_Material_Dialog_Alert)).setTitle("Conectar os aparelhos").setView(panel).setNegativeButton("Cancelar",null).setPositiveButton("Iniciar",(d,w)->action(cancel->{int p;try{p=Integer.parseInt(port.getText().toString());}catch(NumberFormatException e){throw new StationOnlineGame.Unavailable("Porta inválida.");}return client.call(StationOnlineClient.command("start").put("roomId",room().getString("roomId")).put("address",address.getText().toString().trim()).put("port",p),false,cancel);})).create();styleDialog(dialog);}
    private String localAddress(){try{Enumeration<NetworkInterface> ns=NetworkInterface.getNetworkInterfaces();while(ns.hasMoreElements()){NetworkInterface n=ns.nextElement();if(!n.isUp()||n.isLoopback())continue;Enumeration<InetAddress> as=n.getInetAddresses();while(as.hasMoreElements()){InetAddress a=as.nextElement();if(a instanceof Inet4Address&&a.isSiteLocalAddress())return a.getHostAddress();}}}catch(Exception ignored){}return "";}
    private void launch(JSONObject room,JSONObject snapshot){String key=room.optString("roomId")+":"+room.optLong("generation");if(launching||key.equals(launchKey))return;launchKey=key;launching=true;int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);status.setText("Preparando partida direta…");
        commands.execute(()->{try{StationOnlineGame game=prepared;if(game==null)game=StationOnlineGame.prepare(this,client,room.getString("itemId"),snapshot,cancel);game.verifyRoom(room);String file=StationRetroLaunch.prepare(this,game,room,snapshot,cancel);runOnUiThread(()->{if(active&&generation==epoch){returningFromGame=true;try{startActivity(new Intent(this,StationRetroActivity.class).putExtra("station.launch",file).putExtra(StationGameSession.EXTRA,StationGameSession.create(this,room.optString("roomId"))));}catch(RuntimeException e){returningFromGame=false;launching=false;StationRetroLaunch.discard(this,file);failure(e,generation);}}else StationRetroLaunch.discard(this,file);});}catch(Exception e){launching=false;failure(e,generation);}finally{requests.remove(cancel);}});
    }
    private void exitRooms(){if(busy)return;if(client==null||state.get()==null){finish();return;}action(cancel->{JSONObject result=client.call(StationOnlineClient.command("offline"),false,cancel);runOnUiThread(this::finish);return result;});}
    @Override public void onBackPressed(){exitRooms();}
}
