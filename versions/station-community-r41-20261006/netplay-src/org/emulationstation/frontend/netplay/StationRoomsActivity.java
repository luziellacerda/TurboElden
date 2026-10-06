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
    private int section;private String conversationPeer="",conversationName="",lastMessageId="";
    private LinearLayout createPanel,chatActions;private TextView createGame,chatHint;private Button navRooms,navPeople,navCreate,navChat;
    private final java.util.Map<String,String> drafts=new java.util.HashMap<>();
    private final java.util.Set<String> seenMessages=new java.util.LinkedHashSet<>();private String pendingPeer="",pendingName="";private TextView inboxNotice;
    private StationPlayerSheet playerSheet;private Dialog codeDialog;
    private String inspectedPeer="",inspectedName="",peerFeedback="";
    private LinearLayout peers,rooms,messages;private Button create,retry,ready,start,leave,send;
    private Future<?> polling;private long painted=-1;private int paintedPage=-1;
    private final int green=0xff56dea2,white=0xffedf2f4,muted=0xff9aaab2;
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
    private LinearLayout panel(LinearLayout parent,float weight,boolean narrow){LinearLayout v=vertical();v.setPadding(dp(12),dp(12),dp(12),dp(10));v.setBackground(bg(0xff121c21,0xff26343c));LinearLayout.LayoutParams lp=narrow?new LinearLayout.LayoutParams(-1,dp(280)):new LinearLayout.LayoutParams(0,-1,weight);lp.setMargins(0,0,narrow?0:dp(10),narrow?dp(10):0);parent.addView(v,lp);return v;}
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
        getWindow().setStatusBarColor(0xff0b1115);getWindow().setNavigationBarColor(0xff0b1115);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        narrow=getResources().getConfiguration().screenWidthDp<760;
        LinearLayout root=row();root.setBackgroundColor(0xff0b1115);setContentView(root);
        LinearLayout sidebar=vertical();sidebar.setPadding(dp(12),dp(16),dp(12),dp(10));sidebar.setBackgroundColor(0xff10191d);
        root.addView(sidebar,new LinearLayout.LayoutParams(dp(narrow?130:174),-1));
        TextView brand=text(sidebar,"LZ GAMES",18,white);bold(brand);text(sidebar,"COMUNIDADE",10,green).setLetterSpacing(.15f);
        connection=text(sidebar,"○  Conectando",11,muted);connection.setPadding(0,dp(10),0,dp(18));
        ScrollView sideScroll=new ScrollView(this);sideScroll.setVerticalScrollBarEnabled(false);LinearLayout navItems=vertical();sideScroll.addView(navItems,new ScrollView.LayoutParams(-1,-2));sidebar.addView(sideScroll,new LinearLayout.LayoutParams(-1,0,1));
        navRooms=button(navItems,"Ver salas",()->navigate(0),false);navRooms.setCompoundDrawablesWithIntrinsicBounds(new StationSocialIcon(0,dp(20),green),null,null,null);navRooms.setCompoundDrawablePadding(dp(10));
        navPeople=button(navItems,"Pessoas online",()->navigate(1),false);navPeople.setCompoundDrawablesWithIntrinsicBounds(new StationSocialIcon(1,dp(20),green),null,null,null);navPeople.setCompoundDrawablePadding(dp(10));
        navCreate=button(navItems,"Criar sala",()->navigate(2),false);navCreate.setCompoundDrawablesWithIntrinsicBounds(new StationSocialIcon(2,dp(20),green),null,null,null);navCreate.setCompoundDrawablePadding(dp(10));
        navChat=button(navItems,"Conversa",()->{if(!pendingPeer.isEmpty())openConversation(pendingPeer,pendingName);else navigate(3);},false);navChat.setCompoundDrawablesWithIntrinsicBounds(new StationSocialIcon(3,dp(20),green),null,null,null);navChat.setCompoundDrawablePadding(dp(10));
        for(Button n:new Button[]{navRooms,navPeople,navCreate,navChat}){n.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);n.setTextSize(12);n.setPadding(dp(10),0,dp(6),0);}
        
        button(navItems,"Código de convite",()->enterCodeDialog(),false);retry=button(navItems,"Reconectar",()->connect(),false);button(sidebar,"Voltar ao catálogo",()->exitRooms(),false);
        LinearLayout main=vertical();main.setPadding(dp(18),dp(10),dp(16),dp(8));root.addView(main,new LinearLayout.LayoutParams(0,-1,1));
        LinearLayout header=row();main.addView(header,new LinearLayout.LayoutParams(-1,dp(52)));
        FrameLayout art=new FrameLayout(this);header.addView(art,new LinearLayout.LayoutParams(dp(32),dp(40)));heroSymbol=new StationLobbyIcon(this,2);art.addView(heroSymbol,new FrameLayout.LayoutParams(-1,-1));heroCover=new ImageView(this);heroCover.setScaleType(ImageView.ScaleType.FIT_CENTER);art.addView(heroCover,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout names=vertical();LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(0,-2,1);np.setMargins(dp(12),0,dp(12),0);header.addView(names,np);
        title=text(names,"Encontre sua próxima partida",18,white);bold(title);title.setSingleLine(true);title.setEllipsize(android.text.TextUtils.TruncateAt.END);
        subtitle=text(names,selectedItem==null?"Escolha uma sala ou converse com alguém":"Preparando seu jogo…",11,muted);subtitle.setSingleLine(true);subtitle.setEllipsize(android.text.TextUtils.TruncateAt.END);
        gamePlatform=new TextView(this);
        nickname=new EditText(this);field(nickname,"Seu nome online");nickname.setSingleLine(true);nickname.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(24)});nickname.setText(getSharedPreferences("station-online-profile",0).getString("nickname","Jogador"));header.addView(nickname,new LinearLayout.LayoutParams(dp(narrow?95:135),dp(40)));
        nickname.setContentDescription("Seu nome online. Use Reconectar para atualizar.");
        LinearLayout columns=row();LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,0,1);cp.topMargin=dp(10);main.addView(columns,cp);
        leftPanel=panel(columns,.44f,false);middlePanel=panel(columns,.44f,false);createPanel=panel(columns,.44f,false);rightPanel=panel(columns,.56f,false);
        peerTitle=text(leftPanel,"PESSOAS ONLINE",12,green);bold(peerTitle);
        playerSearch=new EditText(this);field(playerSearch,"Buscar nesta página");playerSearch.setSingleLine(true);playerSearch.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(48)});leftPanel.addView(playerSearch,new LinearLayout.LayoutParams(-1,dp(40)));
        peers=vertical();peerScroll=scroll(leftPanel,peers);peerScroll.setVerticalScrollBarEnabled(true);
        playerSearch.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence s,int a,int c,int n){}public void afterTextChanged(android.text.Editable e){}public void onTextChanged(CharSequence s,int a,int b,int c){if(state.get()!=null)renderPlayers(state.get());}});
        roomTitle=text(middlePanel,"VER SALAS",12,green);bold(roomTitle);rooms=vertical();roomScroll=scroll(middlePanel,rooms);roomScroll.setVerticalScrollBarEnabled(true);
        ScrollView createScroll=new ScrollView(this);LinearLayout createBody=vertical();createScroll.addView(createBody,new ScrollView.LayoutParams(-1,-2));createPanel.addView(createScroll,new LinearLayout.LayoutParams(-1,-1));
        bold(text(createBody,"CRIAR SALA",12,green));text(createBody,"Uma partida, dois jogadores",20,white);text(createBody,"Escolha o jogo. A sala fica visível para as pessoas conectadas ao aplicativo.",13,muted);
        createGame=text(createBody,"Jogo não selecionado",16,white);bold(createGame);button(createBody,"Escolher jogo",()->chooseGame(),false);
        text(createBody,"Os dois jogadores precisam ter a mesma edição instalada. O aplicativo confere o jogo antes de abrir a sala.",12,muted);
        create=button(createBody,"Criar sala deste jogo",()->{conversationPeer="";navigate(0);createRoom();},true);create.setEnabled(false);
        chatTitle=text(rightPanel,"CONVERSAS",15,white);bold(chatTitle);chatHint=text(rightPanel,"Selecione uma pessoa ou entre em uma sala",11,muted);
        inboxNotice=text(rightPanel,"",12,green);inboxNotice.setVisibility(View.GONE);inboxNotice.setPadding(0,dp(8),0,dp(8));inboxNotice.setOnClickListener(v->{if(!pendingPeer.isEmpty())openConversation(pendingPeer,pendingName);});
        chatActions=row();rightPanel.addView(chatActions,new LinearLayout.LayoutParams(-1,-2));messages=vertical();chatScroll=scroll(rightPanel,messages);chatScroll.setVerticalScrollBarEnabled(true);
        LinearLayout chatbar=row();rightPanel.addView(chatbar,new LinearLayout.LayoutParams(-1,-2));chat=new EditText(this);field(chat,"Sua mensagem");chat.setMaxLines(3);chat.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);chat.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(500)});chat.setContentDescription("Escrever mensagem");chatbar.addView(chat,new LinearLayout.LayoutParams(0,dp(46),1));send=inline(chatbar,"↑",44,()->sendChat(),true);send.setContentDescription("Enviar mensagem");
        status=text(main,"Conectando com sua sessão…",11,muted);status.setMaxLines(2);status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);loadingLobby();navigate(0);
        String incoming=getIntent().getStringExtra("station.peerId");if(incoming!=null){conversationPeer=incoming;conversationName="Jogador";section=1;roomLayout(false);}
    }
    private void navigate(int next){section=next;roomLayout(room()!=null);if(client!=null&&state.get()!=null){painted=-1;paint(state.get());}}
    private static final class GameChoice {final StationCatalog.Item item;GameChoice(StationCatalog.Item i){item=i;}@Override public String toString(){return item.name+"  ·  "+item.platform;}}
    private void chooseGame(){
        if(client==null||state.get()==null||busy)return;
        java.util.ArrayList<StationCatalog.Item> items=new java.util.ArrayList<>();java.util.ArrayList<String> names=new java.util.ArrayList<>();
        StationCoordinator.Library lib=client.app.coordinator.current();if(lib==null)return;
        for(StationCatalog.Item item:lib.catalog.items)try{String platform=StationOnlineGame.platform(item.platform);JSONArray engines=state.get().optJSONArray("engines");for(int i=0;engines!=null&&i<engines.length();i++)if(platform.equals(engines.getJSONObject(i).optString("platform"))){items.add(item);names.add(item.name+"  ·  "+item.platform);break;}}catch(Exception unsupported){}
        if(items.isEmpty()){status.setText("Nenhum motor liberado para os jogos deste catálogo.");return;}
        LinearLayout panel=codePanel("Escolher jogo","Busque uma edição do catálogo. Baixe o jogo antes de criar sua sala.");EditText search=new EditText(this);field(search,"Buscar jogo");search.setSingleLine(true);panel.addView(search);
        ListView list=new ListView(this);java.util.ArrayList<GameChoice> choices=new java.util.ArrayList<>();for(StationCatalog.Item item:items)choices.add(new GameChoice(item));ArrayAdapter<GameChoice> adapter=new ArrayAdapter<>(new ContextThemeWrapper(this,android.R.style.Theme_Material),android.R.layout.simple_list_item_1,choices);list.setAdapter(adapter);panel.addView(list,new LinearLayout.LayoutParams(-1,dp(210)));
        search.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence s,int a,int c,int n){}public void afterTextChanged(android.text.Editable e){}public void onTextChanged(CharSequence s,int a,int b,int c){adapter.getFilter().filter(s);}});
        list.setOnItemClickListener((parent,view,index,id)->{GameChoice chosen=adapter.getItem(index);if(chosen==null)return;selectedItem=chosen.item.itemId;createGame.setText(chosen.item.name);subtitle.setText(chosen.item.name);codeDialog.dismiss();if(heroBitmap!=null){heroCover.setImageDrawable(null);heroBitmap.recycle();heroBitmap=null;}loadHero();});displayCodePanel();
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
    private void failure(Throwable error,int generation){recordFailure(error);runOnUiThread(()->{if(active&&generation==epoch){feedback.fail(StationOnlineClient.message(error));status.setText(feedback.text(state.get(),false));if(state.get()==null)unavailableLobby();busy=false;retry.setEnabled(true);create.setEnabled(state.get()!=null&&room()==null&&!launching);peerFeedback=StationOnlineClient.message(error);if(state.get()!=null)renderConversation(state.get());refreshPlayerSheet();}});}
    interface Work {JSONObject run(StationApi.Cancellation cancel)throws Exception;}
    private void action(Work work){action(work,null);}
    private void action(Work work,Runnable completed){if(busy||!active||client==null||state.get()==null)return;busy=true;feedback.begin();create.setEnabled(false);refreshPlayerSheet();int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);
        commands.execute(()->{try{JSONObject response=work.run(cancel);deliver(response,generation);runOnUiThread(()->{if(active&&generation==epoch){busy=false;status.setText(feedback.text(state.get(),false));updateStartState();create.setEnabled(room()==null&&!launching);if(completed!=null)completed.run();painted=-1;if(state.get()!=null)paint(state.get());refreshPlayerSheet();}});}catch(Exception e){if(!cancel.cancelled())failure(e,generation);}finally{requests.remove(cancel);}});
    }
    private JSONObject room(){JSONObject snapshot=state.get();return snapshot==null?null:snapshot.optJSONObject("room");}
    private void createRoom(){if(selectedItem==null){status.setText("Abra um jogo e toque em Jogar online para criar uma sala dele.");return;}
        status.setText("Conferindo arquivo e versão do motor…");action(cancel->{prepared=StationOnlineGame.prepare(this,client,selectedItem,state.get(),cancel);return client.call(prepared.fields(StationOnlineClient.command("create")),false,cancel);});}
    private void join(String roomId,String itemId){
        if(busy||launching)return;JSONObject snapshot=state.get(),mine=snapshot==null?null:snapshot.optJSONObject("room");
        if(mine==null){joinConfirmed(roomId,itemId,null);return;}
        if(roomId.equals(mine.optString("roomId"))){status.setText("Você já está nesta sala. Marque Estou pronto para confirmar sua participação.");return;}
        if(!StationPlayerModel.soloWaitingRoom(snapshot)){status.setText("Saia da sala atual antes de entrar em outra.");return;}
        final String previous=mine.optString("roomId");
        AlertDialog dialog=new AlertDialog.Builder(new ContextThemeWrapper(this,android.R.style.Theme_Material_Dialog_Alert))
            .setTitle("Entrar na outra sala?")
            .setMessage("Você está sozinho na sua sala. Ela será encerrada para você entrar na sala de outro jogador. Estou pronto confirma a participação; não muda de sala.")
            .setNegativeButton("Cancelar",null).setPositiveButton("Sair e entrar",(d,w)->joinConfirmed(roomId,itemId,previous)).create();styleDialog(dialog);
    }
    private void joinConfirmed(String roomId,String itemId,String previous){
        status.setText("Conferindo se os jogos são idênticos…");final int generation=epoch;
        action(cancel->{
            // Prepare before leaving: a missing local game must preserve the current room.
            StationOnlineGame game=StationOnlineGame.prepare(this,client,itemId,state.get(),cancel);
            JSONObject current=state.get(),mine=current==null?null:current.optJSONObject("room");
            if(mine!=null){
                if(previous==null||!previous.equals(mine.optString("roomId"))||!StationPlayerModel.soloWaitingRoom(current))
                    throw new StationOnlineGame.Unavailable("Sua sala mudou. Atualize a lista antes de entrar em outra.");
                JSONObject left=client.call(StationOnlineClient.command("leave").put("roomId",previous),false,cancel);
                prepared=null;deliver(left,generation);
                if(left.optJSONObject("room")!=null)throw new java.io.IOException("Room leave not acknowledged");
            }
            prepared=game;JSONObject joined=client.call(game.fields(StationOnlineClient.command("join").put("roomId",roomId)),false,cancel);
            JSONObject actual=joined.optJSONObject("room");
            if(actual==null||!roomId.equals(actual.optString("roomId"))||!StationPlayerModel.member(actual,joined.optString("selfId")))
                throw new java.io.IOException("Room join not acknowledged");
            return joined;
        },()->{if(playerSheet!=null)playerSheet.dismiss();});
    }
    private void command(String action,String key,Object value){action(cancel->{JSONObject c=StationOnlineClient.command(action);if(key!=null)c.put(key,value);JSONObject r=room();if(r!=null)c.put("roomId",r.getString("roomId"));return client.call(c,false,cancel);});}
    private void sendChat(){
        String value=chat.getText().toString().trim(),peer=conversationPeer;JSONObject mine=room();if(value.isEmpty()||busy)return;
        if(peer.isEmpty()&&mine==null){status.setText("Escolha uma pessoa ou entre em uma sala.");return;}
        if(!peer.isEmpty()&&!StationSocial.supports(state.get(),"direct-chat-v1")){status.setText("Conversa privada aguardando atualização do servidor.");return;}
        final String targetRoom=mine==null?"":mine.optString("roomId");
        action(cancel->{JSONObject request=StationOnlineClient.command(peer.isEmpty()?"chat":"direct-chat").put("text",value);if(peer.isEmpty())request.put("roomId",targetRoom);else request.put("peerId",peer);return client.call(request,false,cancel);},()->{if(conversationPeer.equals(peer)&&chat.getText().toString().trim().equals(value))chat.setText("");drafts.remove(peer);renderConversation(state.get());});
    }
    private String nickname(JSONObject snapshot,String id){JSONArray p=snapshot.optJSONArray("peers");if(p!=null)for(int i=0;i<p.length();i++){JSONObject v=p.optJSONObject(i);if(v!=null&&id.equals(v.optString("peerId")))return v.optString("nickname","Jogador");}return "Jogador";}
    private void paint(JSONObject snapshot){
        JSONObject latest=state.get();if(latest==null||snapshot.optLong("revision")<latest.optLong("revision")||snapshot.optInt("page")!=page)return;
        if(snapshot.optLong("revision")==painted&&snapshot.optInt("page")==paintedPage)return;painted=snapshot.optLong("revision");paintedPage=page;
        create.setEnabled(!busy&&!launching&&room()==null);setConnection("Online",true);status.setText(feedback.text(snapshot,busy));
        if(selectedItem!=null)subtitle.setText(client.name(selectedItem));
        int ry=roomScroll.getScrollY(),py=peerScroll.getScrollY();rooms.removeAllViews();start=null;renderPlayers(snapshot);refreshPlayerSheet();
        JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");roomTitle.setText("SALAS  ·  "+snapshot.optInt("totalRooms"));
        JSONArray inv=snapshot.optJSONArray("invites");if(inv!=null)for(int i=0;i<inv.length();i++){JSONObject v=inv.optJSONObject(i);if(v==null)continue;LinearLayout c=card(rooms);bold(text(c,"CONVITE RECEBIDO",10,green));text(c,nickname(snapshot,v.optString("fromPeerId"))+"  ·  "+client.name(v.optString("itemId")),14,white);button(c,"Aceitar e entrar",()->{conversationPeer="";join(v.optString("roomId"),v.optString("itemId"));},true);button(c,"Agora não",()->command("dismiss-invite","text",v.optString("inviteId")),false);}
        JSONArray requests=snapshot.optJSONArray("joinRequests");if(requests!=null)for(int i=0;i<requests.length();i++){JSONObject r=requests.optJSONObject(i);if(r==null)continue;LinearLayout c=card(rooms);bold(text(c,"PEDIDO PARA JOGAR",10,green));text(c,nickname(snapshot,r.optString("fromPeerId")),15,white);button(c,"Aceitar pedido",()->socialAction("accept-request",null,r.optString("requestId")),true);button(c,"Recusar",()->socialAction("dismiss-request",null,r.optString("requestId")),false);}
        if(mine!=null){
            LinearLayout current=card(rooms);bold(text(current,"SUA SALA",10,green));bold(text(current,client.name(mine.optString("itemId")),16,white));JSONArray members=mine.optJSONArray("members"),rd=mine.optJSONArray("ready");text(current,(members==null?0:members.length())+" / 2 jogadores",12,muted);
            for(int i=0;members!=null&&i<members.length();i++){String id=members.optString(i);text(current,(contains(rd,id)?"✓  ":"○  ")+nickname(snapshot,id)+(self.equals(id)?" (você)":""),13,contains(rd,id)?green:white);}
            if("waiting".equals(mine.optString("state"))){ready=button(current,contains(rd,self)?"Cancelar confirmação":"Estou pronto",()->command("ready","value",!contains(rd,self)),true);if(self.equals(mine.optString("hostId")))start=button(current,"Iniciar partida",()->startDialog(),false);else text(current,"O anfitrião inicia quando os dois estiverem prontos.",12,muted);}
            button(current,"Conversar na sala",()->openConversation("",""),false);if(StationPlayerModel.shareable(snapshot))button(current,"Código da sala",()->showRoomCode(),false);button(current,"Sair da sala",()->command("leave",null,null),false);
            if(StationLaunchPolicy.eligible(mine.optString("state"),self.equals(mine.optString("hostId")))){if(!launching&&StationLaunchPolicy.key(mine).equals(launchKey))button(current,"Tentar abrir novamente",()->{launchKey="";launch(mine,snapshot);},true);else launch(mine,snapshot);}
        }
        JSONArray all=snapshot.optJSONArray("rooms");int count=0;
        for(int i=0;all!=null&&i<all.length();i++){JSONObject r=all.optJSONObject(i);if(r==null||mine!=null&&mine.optString("roomId").equals(r.optString("roomId")))continue;count++;LinearLayout c=card(rooms);bold(text(c,client.name(r.optString("itemId")),15,white));text(c,nickname(snapshot,r.optString("hostId"))+"  ·  "+r.optInt("players")+" / "+r.optInt("maximumPlayers",2)+" jogadores",12,muted);boolean available="waiting".equals(r.optString("state"))&&r.optInt("players")<r.optInt("maximumPlayers",2);if(available){boolean social=StationSocial.supports(snapshot,"join-request-v1");Button b=button(c,StationSocial.requested(snapshot,r.optString("roomId"))?"Pedido enviado":social?"Pedir para jogar":"Entrar na sala",()->{if(social)action(cancel->client.call(StationOnlineClient.command("request-join").put("roomId",r.getString("roomId")),false,cancel));else join(r.optString("roomId"),r.optString("itemId"));},true);b.setEnabled(!busy&&!StationSocial.requested(snapshot,r.optString("roomId")));}else text(c,"Partida em andamento ou sala completa",12,muted);}
        if(count==0&&mine==null&&(inv==null||inv.length()==0))empty(rooms,"+","Ainda não há salas aqui","Crie a primeira sala ou procure pessoas online para combinar uma partida.");
        if(snapshot.optInt("page")>0)button(rooms,"← Página anterior",()->page(-1),false);if(!snapshot.isNull("nextPage"))button(rooms,"Mais salas →",()->page(1),false);
        JSONArray direct=snapshot.optJSONArray("directMessages");if(direct!=null)for(int i=0;i<direct.length();i++){JSONObject m=direct.optJSONObject(i);if(m==null||!self.equals(m.optString("toPeerId")))continue;String mid=m.optString("messageId");if(!seenMessages.contains(mid)&&!conversationPeer.equals(m.optString("fromPeerId"))){pendingPeer=m.optString("fromPeerId");pendingName=m.optString("nickname","Jogador");}seenMessages.add(mid);while(seenMessages.size()>128)seenMessages.remove(seenMessages.iterator().next());}
        renderConversation(snapshot);updateStartState();roomLayout(mine!=null);peerScroll.post(()->peerScroll.scrollTo(0,py));roomScroll.post(()->roomScroll.scrollTo(0,ry));
    }
    private void socialAction(String action,String peer,String text){action(cancel->{JSONObject c=StationOnlineClient.command(action);if(peer!=null)c.put("peerId",peer);if(text!=null)c.put("text",text);return client.call(c,false,cancel);});}
    private void openConversation(String id,String name){
        drafts.put(conversationPeer,chat.getText().toString());conversationPeer=id;conversationName=name;lastMessageId="";if(id.equals(pendingPeer)){pendingPeer="";pendingName="";}chat.setText(drafts.containsKey(id)?drafts.get(id):"");if(playerSheet!=null)playerSheet.dismiss();if(narrow)section=3;if(state.get()!=null)renderConversation(state.get());roomLayout(room()!=null);
    }
    private void renderConversation(JSONObject snapshot){
        inboxNotice.setText(pendingName+" • nova mensagem  ›");inboxNotice.setVisibility(pendingPeer.isEmpty()?View.GONE:View.VISIBLE);navChat.setText(pendingPeer.isEmpty()?"Conversa":"Nova mensagem");
        int cy=chatScroll.getScrollY();boolean atBottom=messages.getHeight()-chatScroll.getHeight()-cy<dp(64);messages.removeAllViews();chatActions.removeAllViews();JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");JSONArray list=null;
        if(!conversationPeer.isEmpty()){
            JSONObject peer=StationPlayerModel.peer(snapshot,conversationPeer);if(peer!=null)conversationName=peer.optString("nickname","Jogador");chatTitle.setText(conversationName);chatHint.setText(peer==null?"Presença não confirmada nesta página":"in-room".equals(peer.optString("status"))?"Em uma sala":"Online no aplicativo");
            inline(chatActions,"Perfil / convite",145,()->showPlayer(conversationPeer,conversationName),false);
            boolean enabled=StationSocial.supports(snapshot,"direct-chat-v1");composer(enabled&&!busy);chat.setHint(enabled?"Mensagem privada…":"Conversa privada aguardando ativação");list=StationSocial.messages(snapshot,conversationPeer);if(!narrow||section==3)for(int i=0;i<list.length();i++){JSONObject m=list.optJSONObject(i);if(m!=null&&self.equals(m.optString("toPeerId")))StationPresence.markRead(m.optString("messageId"));}
            if(!enabled)empty(messages,"…","Conversa privada em preparação","As salas e seus convites já estão disponíveis. Esta conversa depende da atualização do serviço.");
            else if(list.length()==0)empty(messages,"…","Comece a conversa","Combine um jogo com "+conversationName+". As mensagens ficam disponíveis enquanto a presença estiver ativa.");
        }else if(mine!=null){chatTitle.setText("Conversa da sala");chatHint.setText(client.name(mine.optString("itemId")));list=mine.optJSONArray("messages");composer(!busy);if(list==null||list.length()==0)empty(messages,"…","Diga olá","Combine a partida com os participantes da sala.");}
        else{chatTitle.setText("Suas conversas");chatHint.setText("Pessoas online · convites · partidas");composer(false);empty(messages,"…","Jogue junto","Abra Pessoas online e toque em um nome para conversar ou convidar.");}
        for(int i=0;list!=null&&i<list.length();i++){JSONObject m=list.optJSONObject(i);if(m==null)continue;boolean own=self.equals(m.optString("fromPeerId"));LinearLayout bubble=card(messages);LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)bubble.getLayoutParams();lp.setMargins(own?dp(30):0,dp(3),own?0:dp(30),dp(7));bubble.setLayoutParams(lp);bubble.setBackground(bg(own?0xff174b3f:0xff202d35,0x00202d35));bold(text(bubble,own?"Você":m.optString("nickname","Jogador"),11,own?green:0xffa4c8e1));TextView value=text(bubble,m.optString("text"),14,white);value.setTextIsSelectable(true);value.setLineSpacing(dp(2),1);String utc=m.optString("utc");String time="";try{time=java.time.OffsetDateTime.parse(utc).atZoneSameInstant(java.time.ZoneId.systemDefault()).format(java.time.format.DateTimeFormatter.ofPattern("HH:mm"));}catch(Exception ignored){}TextView stamp=text(bubble,time,10,muted);stamp.setGravity(Gravity.RIGHT);}
        String last=StationSocial.last(list);boolean changed=!last.equals(lastMessageId);lastMessageId=last;if(changed&&atBottom)chatScroll.post(()->chatScroll.fullScroll(View.FOCUS_DOWN));else chatScroll.post(()->chatScroll.scrollTo(0,cy));
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
            peers.addView(line,new LinearLayout.LayoutParams(-1,dp(48)));line.setOnClickListener(v->{if(!own)openConversation(id,name);else showPlayer(id,name);});
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
            public void join(){joinPlayer(id);}
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
        playerSheet.render(model,model.roomItemId.isEmpty()?"":client.name(model.roomItemId),item==null?"Jogo não selecionado":client.name(item),busy,peerFeedback,StationSocial.supports(state.get(),"join-request-v1"));
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
    private void joinPlayer(String id){
        StationPlayerModel model=StationPlayerModel.read(state.get(),id,inspectedName,selectedItem);
        if(!model.canJoin||busy){peerFeedback=model.reason;refreshPlayerSheet();return;}
        if(StationSocial.supports(state.get(),"join-request-v1")){action(cancel->client.call(StationOnlineClient.command("request-join").put("roomId",model.joinRoomId),false,cancel),()->{peerFeedback="Pedido enviado. Aguarde o convite do anfitrião.";refreshPlayerSheet();});}
        else join(model.joinRoomId,model.joinItemId);
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
        leftPanel.setVisibility(section==1?View.VISIBLE:View.GONE);middlePanel.setVisibility(section==0?View.VISIBLE:View.GONE);createPanel.setVisibility(section==2?View.VISIBLE:View.GONE);
        rightPanel.setVisibility(!narrow||section==3?View.VISIBLE:View.GONE);
        navRooms.setAlpha(section==0?1:.65f);navPeople.setAlpha(section==1?1:.65f);navCreate.setAlpha(section==2?1:.65f);navChat.setAlpha(section==3?1:.65f);
        if(createGame!=null)createGame.setText(selectedItem==null?"Jogo não selecionado":client==null?"Carregando jogo…":client.name(selectedItem));
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
    private void exitRooms(){
        // Return never depends on network latency. Foreground presence completes explicit leave.
        if(room()!=null)getSharedPreferences("station-online-profile",0).edit().putBoolean("leaveOnCatalog",true).apply();
        finish();
    }
    @Override public void onBackPressed(){if(narrow&&section==3){navigate(1);return;}exitRooms();}
}
