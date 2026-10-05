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
    private final StationRoomFeedback feedback=new StationRoomFeedback();
    private final Set<StationApi.Cancellation> requests=Collections.synchronizedSet(new HashSet<>());
    private volatile boolean active;private boolean busy,launching;private volatile int epoch,page;
    private String selectedItem,launchKey="";private boolean returningFromGame;private volatile StationOnlineClient client;private StationOnlineGame prepared;
    private TextView status,title,subtitle,connection,peerTitle,roomTitle,chatTitle;private EditText nickname,chat;
    private ScrollView peerScroll,roomScroll,chatScroll;private LinearLayout leftPanel,middlePanel,rightPanel;private boolean narrow;private ImageView heroCover;private StationLobbyIcon heroSymbol;private TextView gamePlatform;private android.graphics.Bitmap heroBitmap;private int paintedMessages;private String paintedRoom="";
    private EditText playerSearch;
    private StationPlayerSheet playerSheet;private Dialog codeDialog;
    private String inspectedPeer="",inspectedName="",peerFeedback="";
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
        closeSheets();
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
        inline(header,"Código",76,()->enterCodeDialog(),false);
        inline(header,"Voltar",76,()->exitRooms(),false);
        LinearLayout toolbar=new StationLobbySurface(this);toolbar.setGravity(Gravity.CENTER_VERTICAL);toolbar.setPadding(dp(14),dp(10),dp(14),dp(10));LinearLayout.LayoutParams tl=new LinearLayout.LayoutParams(-1,dp(76));tl.setMargins(0,dp(9),dp(6),dp(12));root.addView(toolbar,tl);
        FrameLayout art=new FrameLayout(this);toolbar.addView(art,new LinearLayout.LayoutParams(dp(44),dp(56)));heroSymbol=new StationLobbyIcon(this,2);art.addView(heroSymbol,new FrameLayout.LayoutParams(-1,-1));heroCover=new ImageView(this);heroCover.setScaleType(ImageView.ScaleType.FIT_CENTER);heroCover.setContentDescription("Capa do jogo selecionado");art.addView(heroCover,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout context=vertical();LinearLayout.LayoutParams contextLp=new LinearLayout.LayoutParams(0,-2,1);contextLp.setMargins(dp(14),0,dp(8),0);toolbar.addView(context,contextLp);gamePlatform=text(context,"TURBORAMA  /  MULTIPLAYER",10,green);bold(gamePlatform);
        subtitle=text(context,selectedItem==null?"Sua próxima partida começa aqui":"Preparando seu jogo…",18,white);bold(subtitle);subtitle.setMaxLines(2);subtitle.setEllipsize(android.text.TextUtils.TruncateAt.END);

        nickname=new EditText(this);field(nickname,"Seu apelido");nickname.setSingleLine(true);nickname.setContentDescription("Seu apelido nas salas");nickname.setText(getPreferences(0).getString("nickname","Jogador"));nickname.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(24)});
        LinearLayout actions=toolbar;
        if(narrow){actions=row();LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54));ap.setMargins(0,0,0,dp(10));root.addView(actions,ap);actions.addView(nickname,new LinearLayout.LayoutParams(0,dp(44),1));}else{LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(dp(120),dp(44));np.setMargins(dp(10),dp(4),0,0);toolbar.addView(nickname,np);}
        create=inline(actions,"+  Criar sala",112,()->createRoom(),true);((StationActionButton)create).setMotion(true);create.setEnabled(false);retry=inline(actions,"Reconectar",102,()->connect(),false);
        LinearLayout columns=new LinearLayout(this);columns.setOrientation(narrow?1:0);
        if(narrow){ScrollView body=new ScrollView(this);body.addView(columns);root.addView(body,new LinearLayout.LayoutParams(-1,0,1));}else root.addView(columns,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout left=panel(columns,.27f,narrow),middle=panel(columns,.73f,narrow),right=panel(columns,.32f,narrow);leftPanel=left;middlePanel=middle;rightPanel=right;right.setVisibility(View.GONE);
        peerTitle=text(left,"JOGADORES ONLINE",11,muted);bold(peerTitle);
        playerSearch=new EditText(this);field(playerSearch,"Filtrar nomes desta página");playerSearch.setSingleLine(true);playerSearch.setTextSize(12);playerSearch.setContentDescription("Filtrar jogadores da página atual");playerSearch.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(48)});left.addView(playerSearch,new LinearLayout.LayoutParams(-1,dp(40)));
        peers=vertical();peerScroll=scroll(left,peers);peerScroll.setVerticalScrollBarEnabled(true);
        playerSearch.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence s,int start,int count,int after){}public void onTextChanged(CharSequence s,int start,int before,int count){JSONObject snapshot=state.get();if(snapshot!=null&&snapshot.optInt("page")==page){renderPlayers(snapshot);peerScroll.scrollTo(0,0);}}public void afterTextChanged(android.text.Editable e){}});
        roomTitle=text(middle,"SALAS DISPONÍVEIS",11,green);bold(roomTitle);rooms=vertical();roomScroll=scroll(middle,rooms);
        chatTitle=text(right,"CHAT DA SALA",11,muted);bold(chatTitle);messages=vertical();chatScroll=scroll(right,messages);
        LinearLayout chatbar=row();right.addView(chatbar,new LinearLayout.LayoutParams(-1,-2));chat=new EditText(this);field(chat,"Entre em uma sala");chat.setMaxLines(2);chat.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(500)});chat.setContentDescription("Mensagem para os jogadores da sala");chatbar.addView(chat,new LinearLayout.LayoutParams(0,dp(44),1));send=inline(chatbar,"↑",44,()->sendChat(),true);send.setContentDescription("Enviar mensagem");
        status=text(root,"Conectando com sua sessão…",11,muted);status.setMaxLines(2);status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);loadingLobby();
    }
    private void styleDialog(AlertDialog dialog){dialog.setOnShowListener(d->{dialog.getWindow().setBackgroundDrawable(bg(0xff102018,0xff34583f));dialog.getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(green);dialog.getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(muted);TextView msg=dialog.findViewById(android.R.id.message);if(msg!=null)msg.setTextColor(white);});dialog.show();}

    @Override protected void onStart(){super.onStart();StationPresence.foreground(this,false);active=true;connect();loadHero();}
    @Override protected void onStop(){active=false;epoch++;cancelAll();closeSheets();super.onStop();}
    @Override protected void onDestroy(){commands.shutdownNow();events.shutdownNow();heroCover.setImageDrawable(null);if(heroBitmap!=null){heroBitmap.recycle();heroBitmap=null;}super.onDestroy();}
    private void cancelAll(){if(polling!=null)polling.cancel(true);synchronized(requests){for(StationApi.Cancellation c:requests)c.cancel();requests.clear();}}
    private void connect(){if(!active)return;epoch++;cancelAll();busy=false;feedback.begin();int generation=epoch;state.reset();painted=-1;prepared=null;launchKey="";launching=false;loadingLobby();
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
            }catch(Exception e){if(!cancel.cancelled()){runOnUiThread(()->{if(active&&epoch==generation)setConnection("Reconectar",false);});failure(e,generation);}}finally{requests.remove(cancel);}
        });
    }
    private void deliver(JSONObject snapshot,int generation)throws Exception {if(!active||generation!=epoch)return;if(!state.accept(snapshot))return;runOnUiThread(()->{if(active&&generation==epoch)paint(snapshot);});}
    private static void recordFailure(Throwable error){
        StringBuilder detail=new StringBuilder();Throwable cause=error;
        for(int depth=0;cause!=null&&depth<3;depth++,cause=cause.getCause()){
            detail.append(" type=").append(cause.getClass().getName());
            if(cause instanceof StationApi.Failure){StationApi.Failure api=(StationApi.Failure)cause;detail.append(" http=").append(api.status);if(api.code!=null&&api.code.matches("[A-Z0-9_]{1,80}"))detail.append(" code=").append(api.code);}
            StackTraceElement[] stack=cause.getStackTrace();for(int i=0;i<Math.min(stack.length,8);i++)detail.append(" at=").append(stack[i].getClassName()).append('.').append(stack[i].getMethodName()).append(':').append(stack[i].getLineNumber());
        }
        android.util.Log.w("StationRooms",detail.toString());
    }
    private void failure(Throwable error,int generation){recordFailure(error);runOnUiThread(()->{if(active&&generation==epoch){feedback.fail(StationOnlineClient.message(error));status.setText(feedback.text(state.get(),false));if(state.get()==null)unavailableLobby();busy=false;retry.setEnabled(true);create.setEnabled(state.get()!=null&&room()==null&&!launching);peerFeedback=StationOnlineClient.message(error);refreshPlayerSheet();}});}
    interface Work {JSONObject run(StationApi.Cancellation cancel)throws Exception;}
    private void action(Work work){action(work,null);}
    private void action(Work work,Runnable completed){if(busy||!active||client==null||state.get()==null)return;busy=true;feedback.begin();create.setEnabled(false);refreshPlayerSheet();int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);
        commands.execute(()->{try{JSONObject response=work.run(cancel);deliver(response,generation);runOnUiThread(()->{if(active&&generation==epoch){busy=false;status.setText(feedback.text(state.get(),false));updateStartState();create.setEnabled(room()==null&&!launching);if(completed!=null)completed.run();refreshPlayerSheet();}});}catch(Exception e){if(!cancel.cancelled())failure(e,generation);}finally{requests.remove(cancel);}});
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
        create.setEnabled(!busy&&!launching&&room()==null);setConnection("Online",true);status.setText(feedback.text(snapshot,busy));
        if(selectedItem!=null)subtitle.setText(client.name(selectedItem));
        int py=peerScroll.getScrollY(),ry=roomScroll.getScrollY(),cy=chatScroll.getScrollY();
        peers.removeAllViews();rooms.removeAllViews();messages.removeAllViews();start=null;JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");composer(mine!=null);roomLayout(mine!=null);
        renderPlayers(snapshot);refreshPlayerSheet();
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
            if("waiting".equals(mine.optString("state"))){ready=button(current,contains(rd,self)?"Cancelar confirmação":"Estou pronto  ✓",()->command("ready","value",!contains(rd,self)),true);if(self.equals(mine.optString("hostId")))start=button(current,"Iniciar partida  →",()->startDialog(),false);else text(current,"Quando os dois estiverem prontos, o criador inicia. Seu jogo abrirá automaticamente.",12,muted);}
            if(StationPlayerModel.shareable(snapshot))button(current,"Código da sala",()->showRoomCode(),false);
            leave=button(current,"Sair da sala",()->command("leave",null,null),false);
            JSONArray msgs=mine.optJSONArray("messages");int count=msgs==null?0:msgs.length();
            if(count==0)empty(messages,"…","Diga olá","As mensagens ficam visíveis aos jogadores desta sala.");
            if(msgs!=null)for(int i=0;i<msgs.length();i++){JSONObject m=msgs.optJSONObject(i);if(m==null)continue;LinearLayout bubble=card(messages);boolean own=self.equals(m.optString("fromPeerId"));LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)bubble.getLayoutParams();bp.setMargins(own?dp(18):0,0,own?0:dp(18),dp(8));bubble.setLayoutParams(bp);bubble.setBackground(bg(own?0xff153924:0xff112219,own?0xff326243:0xff254232));bold(text(bubble,m.optString("nickname"),11,green));TextView message=text(bubble,m.optString("text"),13,white);message.setTextIsSelectable(true);message.setLineSpacing(dp(2),1);}
            if(count!=paintedMessages||!mine.optString("roomId").equals(paintedRoom)){chatScroll.post(()->chatScroll.fullScroll(View.FOCUS_DOWN));}else chatScroll.post(()->chatScroll.scrollTo(0,cy));paintedMessages=count;paintedRoom=mine.optString("roomId");
            if(StationLaunchPolicy.eligible(mine.optString("state"),self.equals(mine.optString("hostId")))){
                if(!launching&&StationLaunchPolicy.key(mine).equals(launchKey))button(current,"Tentar abrir a partida novamente",()->{launchKey="";launch(mine,snapshot);},true);
                else launch(mine,snapshot);
            }
        }
        updateStartState();peerScroll.post(()->peerScroll.scrollTo(0,py));roomScroll.post(()->roomScroll.scrollTo(0,ry));
    }


    /** Forty-eight dp touch targets without nested cards, avatars or per-row buttons. */
    private void renderPlayers(JSONObject snapshot){
        peers.removeAllViews();JSONArray list=snapshot.optJSONArray("peers");String self=snapshot.optString("selfId");
        String filter=playerSearch.getText().toString().trim().toLowerCase(java.util.Locale.ROOT);int shown=0;
        peerTitle.setText("ONLINE  ·  "+snapshot.optInt("totalPeers"));
        if(list!=null)for(int i=0;i<list.length();i++){
            JSONObject p=list.optJSONObject(i);if(p==null)continue;String id=p.optString("peerId"),name=p.optString("nickname","Jogador");
            if(!name.toLowerCase(java.util.Locale.ROOT).contains(filter))continue;shown++;
            boolean own=self.equals(id),available="online".equals(p.optString("status")),inRoom="in-room".equals(p.optString("status"));
            LinearLayout line=row();line.setPadding(dp(4),0,dp(5),0);
            android.graphics.drawable.GradientDrawable base=bg(0x00000000,0x00000000);
            line.setBackground(new RippleDrawable(ColorStateList.valueOf(0x3261ee8a),base,null));
            line.setFocusable(true);line.setClickable(true);line.setContentDescription(name+(own?", você":available?", disponível":inRoom?", em uma sala":", status não informado")+", abrir perfil");
            TextView dot=label("●",9,available?green:inRoom?0xffd7b877:muted);dot.setGravity(Gravity.CENTER);line.addView(dot,new LinearLayout.LayoutParams(dp(20),-1));
            TextView n=label(name,14,white);n.setSingleLine(true);n.setEllipsize(android.text.TextUtils.TruncateAt.END);line.addView(n,new LinearLayout.LayoutParams(0,-2,1));
            TextView tail=label(own?"você":"›",own?10:22,muted);tail.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);line.addView(tail,new LinearLayout.LayoutParams(dp(38),-1));
            peers.addView(line,new LinearLayout.LayoutParams(-1,dp(48)));line.setOnClickListener(v->showPlayer(id,name));
            View separator=new View(this);separator.setBackgroundColor(0xff203128);peers.addView(separator,new LinearLayout.LayoutParams(-1,dp(1)));
        }
        if(shown==0){TextView empty=text(peers,filter.isEmpty()?"Nenhum jogador nesta página.":"Nenhum nome encontrado nesta página.",12,muted);empty.setPadding(dp(8),dp(18),dp(8),dp(18));}
        if(snapshot.optInt("page")>0)button(peers,"← Página anterior",()->page(-1),false);
        if(!snapshot.isNull("nextPage"))button(peers,"Próxima página →",()->page(1),false);
    }
    private void closeSheets(){if(playerSheet!=null){playerSheet.dismiss();playerSheet=null;}if(codeDialog!=null){codeDialog.dismiss();codeDialog=null;}inspectedPeer="";inspectedName="";peerFeedback="";}
    private void showPlayer(String id,String name){
        if(playerSheet!=null)playerSheet.dismiss();inspectedPeer=id;inspectedName=name;peerFeedback="";
        playerSheet=new StationPlayerSheet(this,new StationPlayerSheet.Actions(){
            public void invite(){invitePlayer(id);}
            public void code(){showRoomCode();}
            public void block(){confirmBlock(id,name);}
        });
        playerSheet.setOnDismissListener(d->{if(playerSheet==d){playerSheet=null;inspectedPeer="";}});
        refreshPlayerSheet();playerSheet.show();
    }
    private void refreshPlayerSheet(){
        if(playerSheet==null||client==null||inspectedPeer.isEmpty())return;
        StationPlayerModel model=StationPlayerModel.read(state.get(),inspectedPeer,inspectedName,selectedItem);
        String item=model.ownedRoom==null?selectedItem:model.ownedRoom.optString("itemId");
        playerSheet.render(model,model.roomItemId.isEmpty()?"":client.name(model.roomItemId),item==null?"Jogo não selecionado":client.name(item),busy,peerFeedback);
    }
    private void invitePlayer(String id){
        JSONObject snapshot=state.get();StationPlayerModel model=StationPlayerModel.read(snapshot,id,inspectedName,selectedItem);
        if(!model.canInvite||busy){peerFeedback=model.reason;refreshPlayerSheet();return;}
        peerFeedback="Preparando seu convite…";final int generation=epoch;
        action(cancel->{
            JSONObject current=state.get();StationPlayerModel latest=StationPlayerModel.read(current,id,model.name,selectedItem);
            if(!latest.canInvite)throw new StationOnlineGame.Unavailable(latest.reason);
            JSONObject own=current.optJSONObject("room");
            if(own==null){prepared=StationOnlineGame.prepare(this,client,selectedItem,current,cancel);current=client.call(prepared.fields(StationOnlineClient.command("create")),false,cancel);deliver(current,generation);own=current.optJSONObject("room");}
            if(own==null)throw new java.io.IOException("Missing created room");
            return client.call(StationOnlineClient.command("invite").put("roomId",own.getString("roomId")).put("peerId",id),false,cancel);
        },()->{peerFeedback="Convite enviado. O jogador tem 60 segundos para aceitar.";status.setText("Convite enviado para "+model.name+".");});
    }
    private void confirmBlock(String id,String name){
        AlertDialog dialog=new AlertDialog.Builder(new ContextThemeWrapper(this,android.R.style.Theme_Material_Dialog_Alert)).setTitle("Bloquear "+name+"?").setMessage("Oculta este jogador enquanto estiver online e encerra uma sala compartilhada.").setNegativeButton("Cancelar",null).setPositiveButton("Bloquear",(d,w)->{if(playerSheet!=null)playerSheet.dismiss();command("block","peerId",id);}).create();styleDialog(dialog);
    }
    private LinearLayout codePanel(String heading,String detail){
        if(codeDialog!=null)codeDialog.dismiss();codeDialog=new Dialog(this);codeDialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout outer=vertical();outer.setPadding(dp(22),dp(18),dp(22),dp(18));outer.setBackground(bg(0xff0b1711,0xff315441));
        TextView brand=text(outer,"LZ GAMES  /  CONVITE",10,green);brand.setLetterSpacing(.1f);bold(brand);
        TextView title=text(outer,heading,22,white);bold(title);text(outer,detail,12,muted);
        ScrollView body=new ScrollView(this);body.setFillViewport(false);body.setBackground(bg(0xff0b1711,0xff315441));body.addView(outer,new ScrollView.LayoutParams(-1,-2));codeDialog.setContentView(body);return outer;
    }
    private void displayCodePanel(){
        codeDialog.show();Window w=codeDialog.getWindow();if(w==null)return;
        w.setBackgroundDrawableResource(android.R.color.transparent);w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        WindowManager.LayoutParams p=w.getAttributes();p.width=Math.min(dp(500),getResources().getDisplayMetrics().widthPixels-dp(32));p.height=Math.min(dp(410),getResources().getDisplayMetrics().heightPixels-dp(32));p.dimAmount=.72f;p.gravity=Gravity.CENTER;w.setAttributes(p);w.getDecorView().setSystemUiVisibility(getWindow().getDecorView().getSystemUiVisibility());
        w.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
    }
    private void showRoomCode(){
        JSONObject snapshot=state.get();if(!StationPlayerModel.shareable(snapshot)){peerFeedback="O código está disponível quando sua sala tem uma vaga e aguarda jogadores.";refreshPlayerSheet();status.setText(peerFeedback);return;}
        JSONObject mine=snapshot.optJSONObject("room");final String code;
        try{code=StationInvitationCode.encode(snapshot.optString("instance"),mine.optString("roomId"),mine.optString("itemId"));}catch(IllegalArgumentException e){status.setText(e.getMessage());return;}
        LinearLayout panel=codePanel("Código da sua sala",client.name(mine.optString("itemId"))+"\nCompartilhe com outro jogador. Ele entra em Código no lobby e cola o convite.");
        TextView value=text(panel,code,12,white);value.setTypeface(Typeface.MONOSPACE);value.setTextIsSelectable(true);value.setPadding(dp(12),dp(12),dp(12),dp(12));value.setBackground(bg(0xff060f0a,0xff294634));
        text(panel,"Válido enquanto esta sala existir e tiver uma vaga. O outro jogador precisa da mesma edição instalada.",11,muted);
        Button copy=button(panel,"Copiar código",()->{android.content.ClipboardManager clipboard=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(clipboard!=null){clipboard.setPrimaryClip(ClipData.newPlainText("Convite TurboStations",code));Toast.makeText(this,"Código copiado",Toast.LENGTH_SHORT).show();}},true);
        button(panel,"Fechar",()->codeDialog.dismiss(),false);displayCodePanel();
    }
    private void enterCodeDialog(){
        if(busy)return;LinearLayout panel=codePanel("Entrar por código","Cole o código compartilhado por quem criou a sala.");
        EditText input=new EditText(this);field(input,"TS1:…");input.setSingleLine(true);input.setTextSize(12);input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(160)});input.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);panel.addView(input,new LinearLayout.LayoutParams(-1,dp(48)));
        TextView error=text(panel,"",12,0xffefad98);error.setVisibility(View.GONE);error.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        button(panel,"Entrar na sala",()->{
            JSONObject snapshot=state.get();
            try{
                if(busy)throw new IllegalArgumentException("Aguarde a ação atual terminar.");
                if(snapshot==null||!active)throw new IllegalArgumentException("Conecte-se ao lobby antes de entrar.");
                if(snapshot.optJSONObject("room")!=null)throw new IllegalArgumentException("Saia da sala atual antes de usar outro código.");
                StationInvitationCode parsed=StationInvitationCode.parse(input.getText().toString());
                if(!parsed.instance.equals(snapshot.optString("instance")))throw new IllegalArgumentException("Este código expirou após a atualização das salas. Peça um novo convite.");
                codeDialog.dismiss();join(parsed.roomId,parsed.itemId);
            }catch(IllegalArgumentException e){error.setText(e.getMessage());error.setVisibility(View.VISIBLE);}
        },true);
        button(panel,"Cancelar",()->codeDialog.dismiss(),false);displayCodePanel();
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
    private void updateStartState(){if(start!=null)start.setEnabled(!busy&&!launching&&StationRoomStartState.reason(state.get()).isEmpty());}
    private void startDialog(){
        String reason=StationRoomStartState.reason(state.get());
        if(busy||!reason.isEmpty()){feedback.fail(reason.isEmpty()?"Aguarde a solicitação atual terminar.":reason);status.setText(feedback.text(state.get(),busy));return;}

        JSONObject snapshot=state.get();JSONArray transports=snapshot==null?null:snapshot.optJSONArray("transports");
        if(!contains(transports,"relay-wss-v1")){status.setText("A conexão pela internet aguarda a atualização do servidor Station. As salas e os jogos locais continuam disponíveis.");return;}
        AlertDialog dialog=new AlertDialog.Builder(new ContextThemeWrapper(this,android.R.style.Theme_Material_Dialog_Alert))
            .setTitle("Jogar online")
            .setMessage("Os dois jogadores serão conectados pelo servidor TurboStations. Cada um pode usar sua própria rede Wi-Fi ou internet móvel. A qualidade da partida depende da conexão dos dois aparelhos.")
            .setNegativeButton("Cancelar",null).setPositiveButton("Iniciar partida",(d,w)->action(cancel->{String changed=StationRoomStartState.reason(state.get());if(!changed.isEmpty())throw new StationOnlineGame.Unavailable(changed);return client.call(StationOnlineClient.command("start").put("roomId",room().getString("roomId")).put("transport","relay-wss-v1"),false,cancel);})).create();styleDialog(dialog);
    }
    private void launch(JSONObject room,JSONObject snapshot){String key=StationLaunchPolicy.key(room);if(launching||key.equals(launchKey))return;launchKey=key;launching=true;int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);status.setText("Conectando a partida online…");android.util.Log.i("StationRooms","launch stage=prepare room="+room.optString("roomId")+" generation="+room.optLong("generation")+" host="+snapshot.optString("selfId").equals(room.optString("hostId")));
        commands.execute(()->{try{StationOnlineGame game=prepared;if(game==null)game=StationOnlineGame.prepare(this,client,room.getString("itemId"),snapshot,cancel);JSONObject gameRoom=room;
            if("relay-wss-v1".equals(room.optString("transport"))){JSONObject connection=client.call(StationOnlineClient.command("relay-ticket").put("roomId",room.getString("roomId")),false,cancel);gameRoom=connection.getJSONObject("room");android.util.Log.i("StationRooms","launch stage=relay-ticket-received");}
            game.verifyRoom(gameRoom);String file=StationRetroLaunch.prepare(this,game,gameRoom,snapshot,cancel);runOnUiThread(()->{if(active&&generation==epoch){returningFromGame=true;try{android.util.Log.i("StationRooms","launch stage=activity");startActivity(new Intent(this,StationRetroActivity.class).putExtra("station.launch",file).putExtra(StationGameSession.EXTRA,StationGameSession.create(this,room.optString("roomId"))));}catch(RuntimeException e){returningFromGame=false;StationRetroLaunch.discard(this,file);launchFailure(e,generation);}}else StationRetroLaunch.discard(this,file);});}catch(Exception e){launchFailure(e,generation);}finally{requests.remove(cancel);}});
    }
    private void launchFailure(Throwable error,int generation){
        recordFailure(error);
        runOnUiThread(()->{if(active&&generation==epoch){launching=false;busy=false;feedback.fail(StationOnlineClient.message(error));painted=-1;JSONObject current=state.get();if(current!=null)paint(current);}});
    }
    private void exitRooms(){if(busy)return;if(client==null||state.get()==null){finish();return;}action(cancel->{JSONObject result=client.call(StationOnlineClient.command("offline"),false,cancel);runOnUiThread(this::finish);return result;});}
    @Override public void onBackPressed(){exitRooms();}
}
