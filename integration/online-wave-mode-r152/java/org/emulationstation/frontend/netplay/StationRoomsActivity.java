package org.emulationstation.frontend.netplay;
import android.app.*;
import android.os.*;
import android.content.*;
import org.emulationstation.frontend.auth.StationTaskNavigation;
import org.emulationstation.frontend.auth.StationTaskPolicy;
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
public final class StationRoomsActivity extends Activity implements StationGraphicsPreferences.Listener {
    private final ExecutorService commands=Executors.newSingleThreadExecutor();
    private final ExecutorService events=Executors.newSingleThreadExecutor();
    private final StationRoomState state=new StationRoomState();
    private final StationRoomFeedback feedback=new StationRoomFeedback();
    private final Set<StationApi.Cancellation> requests=Collections.synchronizedSet(new HashSet<>());
    private volatile boolean active;private boolean busy,launching;private volatile int epoch,page,roomPage;
    private Intent pendingNavigation;
    private final StationGameSession.LaunchReturn nativeReturn=new StationGameSession.LaunchReturn();
    private String selectedItem,launchKey="";private boolean returningFromGame,returningRecovery;private volatile StationOnlineClient client;private StationOnlineGame prepared;
    private TextView status,title,subtitle,connection,peerTitle,roomTitle,chatTitle;private EditText nickname,chat;
    private ScrollView peerScroll,roomScroll,chatScroll;private LinearLayout leftPanel,middlePanel,rightPanel;private boolean narrow;private ImageView heroCover;private StationLobbyIcon heroSymbol;private TextView gamePlatform;private android.graphics.Bitmap heroBitmap;private int paintedMessages;private String paintedRoom="";
    private EditText playerSearch;private StationRoomArtwork artwork;private boolean creating;private Button choose;private TextView createMessage;
    private int section;private String conversationPeer="",conversationName="",lastMessageId="";
    private LinearLayout createOverview,createSetup,setupModes,setupCounts;
    private TextView setupDescription;private Button setupBack,setupConfirm;
    private final java.util.List<StationMultiplayerProfile> setupProfiles=new ArrayList<>();
    private final java.util.List<TextView> setupModeLabels=new ArrayList<>(),setupCountLabels=new ArrayList<>();
    private StationMultiplayerProfile setupProfile;private int setupCapacity;private String setupContext="";
    private LinearLayout createPanel,chatActions;private StationCreateGameCard createCard, ownRoomCard;private String ownRoomCoverItem="";private TextView createGame,chatHint,createInfo;private Button navRooms,navPeople,navCreate,navChat,inviteNavigation;
    // Snapshot revisions update the actions, not the attached cover surface.
    private static final class RoomRow {
        final View root;final StationCreateGameCard display;final LinearLayout content,footer;
        boolean loading,loaded;
        RoomRow(View root,StationCreateGameCard display,LinearLayout content,LinearLayout footer){this.root=root;this.display=display;this.content=content;this.footer=footer;}
    }
    private final Map<String,RoomRow> roomRows=new LinkedHashMap<>();
    private final List<View> desiredRoomRows=new ArrayList<>();
    private final Set<String> usedRoomRows=new HashSet<>();
    private final java.util.Map<String,String> drafts=new java.util.HashMap<>();
    private final java.util.Set<String> seenMessages=new java.util.LinkedHashSet<>();private String pendingPeer="",pendingName="";private TextView inboxNotice;
    private StationPlayerSheet playerSheet;private Dialog codeDialog;
    private final StationRoomRoster roster = new StationRoomRoster();
    private TextView roomReadiness;private LinearLayout ownRoomFooter;
    private String inspectedPeer="",inspectedName="",peerFeedback="";
    private LinearLayout peers,rooms,messages;private Button create,retry,ready,start,leave,send;
    private final ScheduledExecutorService multiplayerEvents=Executors.newSingleThreadScheduledExecutor();
    private ScheduledFuture<?> multiplayerPolling;
    private volatile StationApi.Cancellation multiplayerPollCancellation;
    private volatile int multiplayerPollEpoch;
    private Future<?> polling;private long painted=-1;private int paintedPage=-1,paintedRoomPage=-1;
    private StationHyperspaceView hyperspace;private StationGameRatingView headerRating;private TextView headerPlayers;private JSONObject headerMetadata;private String heroRequestId="";private int heroEpoch=-1;private String profileRequestId="";private int profileEpoch=-1;
    private String heroFactSummary="",heroFactDetail="",heroOnlineDetail="",heroOnlinePlayers="";
    private String heroSynopsis="";private TextView createSynopsis;
    private StationGraphicsPreferences graphics;private StationWaveBackground waves;private FrameLayout graphicsStage;
    private final int green=0xff46dbff,white=0xffeff5ff,muted=0xffaab8ca;
    @Override public void onCreate(Bundle saved){super.onCreate(saved);graphics=StationGraphicsPreferences.get(this);nativeReturn.restore(saved==null?null:saved.getBundle("station.nativeReturn"));StationTaskNavigation.arrived(this);selectedItem=getIntent().getStringExtra("station.itemId");returningFromGame=saved!=null&&saved.getBoolean("returning");returningRecovery=saved!=null&&saved.getBoolean("returningRecovery");artwork=new StationRoomArtwork(this);build();}
    @Override protected void onNewIntent(Intent intent){
        super.onNewIntent(intent);setIntent(intent);StationTaskNavigation.arrived(this);
        pendingNavigation=intent;if(active)applyPendingNavigation(state.get());
    }
    private void applyPendingNavigation(JSONObject snapshot){
        Intent incoming=pendingNavigation;if(incoming==null||snapshot==null||launching||returningFromGame)return;
        pendingNavigation=null;
        String item=incoming.getStringExtra("station.itemId");
        if(item!=null&&StationTaskPolicy.canSelectItem(true,snapshot.optJSONObject("room")!=null,launching,returningFromGame)&&!item.equals(selectedItem)){
            clearRoomSetup();selectedItem=item;prepared=null;roomLayout(false);loadHero();
        }
        String peer=incoming.getStringExtra("station.peerId");
        if(peer!=null&&!peer.isEmpty()){openConversation(peer,roster.resolveName(snapshot,peer));}
    }
    private synchronized void stopMultiplayerPoll(){multiplayerPollEpoch++;if(multiplayerPolling!=null){multiplayerPolling.cancel(true);multiplayerPolling=null;}StationApi.Cancellation cancellation=multiplayerPollCancellation;if(cancellation!=null)cancellation.cancel();}
    @Override public void onSaveInstanceState(Bundle out){out.putBoolean("returning",returningFromGame);out.putBoolean("returningRecovery",returningRecovery);out.putBundle("station.nativeReturn",nativeReturn.save());super.onSaveInstanceState(out);}
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        // RESULT_CANCELED also covers a native-process crash before Service ATTACH.
        // The exact recorded launch is cleaned locally; result codes never authorize Leave.
        if(nativeReturn.completed(requestCode))android.util.Log.i("StationRooms","game stage=native-activity-returned");
    }
    private int dp(float x){return(int)(getResources().getDisplayMetrics().density*x+.5f);}
    private GradientDrawable bg(int color,int rim){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(4));d.setStroke(dp(1),rim);return d;}
    private LinearLayout vertical(){LinearLayout v=new LinearLayout(this);v.setOrientation(1);return v;}
    private LinearLayout row(){LinearLayout v=new LinearLayout(this);v.setGravity(Gravity.CENTER_VERTICAL);return v;}
    private TextView label(String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setFontFeatureSettings("kern");t.setIncludeFontPadding(false);return t;}
    private TextView text(LinearLayout parent,String value,int size,int color){TextView t=label(value,size,color);t.setPadding(0,dp(5),0,dp(5));parent.addView(t,new LinearLayout.LayoutParams(-1,-2));return t;}
    private void bold(TextView t){t.setTypeface(Typeface.create("sans-serif-condensed",Typeface.BOLD));}
    private void styleAction(Button button,int tone){
        // Preserve the button's distinct focus/selected/pressed states; a tint
        // would recolor the complete drawable, including its focus border.
        button.setBackgroundTintList(null);button.setTextSize(13);bold(button);
        button.setFocusable(true);button.setFocusableInTouchMode(false);
    }
    private Button button(LinearLayout parent,String value,Runnable action,boolean primary){
        StationActionButton b=new StationActionButton(this,value,primary);b.compactAppearance();styleAction(b,primary?StationActionButton.PRIMARY:StationActionButton.SECONDARY);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(48));parent.addView(b,lp);b.setOnClickListener(v->action.run());return b;
    }
    private Button navButton(LinearLayout parent,String value,Runnable action){
        StationActionButton b=new StationActionButton(this,value,false);b.compactAppearance();b.setTextSize(12);styleNavigation(b,false);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(48));parent.addView(b,lp);b.setOnClickListener(v->action.run());return b;
    }
    private Button inline(LinearLayout parent,String value,int width,Runnable action,boolean primary){
        LinearLayout holder=vertical();LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(dp(Math.max(48,width)),-2);lp.setMargins(dp(8),0,0,0);parent.addView(holder,lp);return button(holder,value,action,primary);
    }
    /** Static section markers keep primary navigation distinct from connection utilities. */
    private void navigationSection(LinearLayout parent,String name){
        TextView caption=label(name,9,muted);caption.setLetterSpacing(.12f);bold(caption);
        caption.setPadding(dp(10),dp(10),0,dp(5));parent.addView(caption,new LinearLayout.LayoutParams(-1,-2));
    }
    private TextView pill(String value,int color){TextView t=label(value,10,color);bold(t);t.setSingleLine(true);t.setGravity(Gravity.CENTER);t.setPadding(dp(9),dp(5),dp(9),dp(5));t.setBackground(bg(0xff11273b,0xff29475e));return t;}
    private LinearLayout card(LinearLayout parent){LinearLayout c=vertical();c.setPadding(dp(12),dp(9),dp(12),dp(9));c.setBackground(bg(0xf2151f2e,0xff304258));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,0,0,dp(8));parent.addView(c,lp);return c;}
    private LinearLayout panel(LinearLayout parent,float weight,boolean narrow){LinearLayout v=vertical();v.setPadding(dp(8),dp(6),dp(8),dp(6));v.setBackgroundColor(android.graphics.Color.TRANSPARENT);LinearLayout.LayoutParams lp=narrow?new LinearLayout.LayoutParams(-1,dp(280)):new LinearLayout.LayoutParams(0,-1,weight);lp.setMargins(0,0,narrow?0:dp(10),narrow?dp(10):0);parent.addView(v,lp);return v;}
    private ScrollView scroll(LinearLayout parent,LinearLayout content){ScrollView s=new ScrollView(this);s.setFillViewport(true);s.setClipToPadding(false);s.setPadding(0,dp(10),0,0);s.setVerticalScrollBarEnabled(false);s.addView(content,new ScrollView.LayoutParams(-1,-2));parent.addView(s,new LinearLayout.LayoutParams(-1,0,1));return s;}
    private void empty(LinearLayout parent,String icon,String heading,String detail){
        LinearLayout box=vertical();box.setGravity(Gravity.CENTER);box.setPadding(dp(10),dp(10),dp(10),dp(10));parent.addView(box,new LinearLayout.LayoutParams(-1,-1));
        View mark=parent==rooms||parent==messages?new StationLottieIllustration(this,parent==messages?"dialog":"online-robot"):new StationLobbyIcon(this,1);box.addView(mark,new LinearLayout.LayoutParams(dp(parent==peers?72:112),dp(parent==peers?72:112)));
        TextView h=text(box,heading,14,white);h.setGravity(Gravity.CENTER);h.setPadding(0,dp(13),0,dp(6));bold(h);
        TextView d=text(box,detail,12,muted);d.setGravity(Gravity.CENTER);d.setLineSpacing(dp(2),1);
    }
    private void field(EditText field,String hint){field.setTextSize(13);field.setTextColor(white);field.setHintTextColor(muted);field.setPadding(dp(12),dp(8),dp(12),dp(8));field.setBackground(bg(0xff0a1527,0xff2c4361));field.setHint(hint);}
    private void setConnection(String value,boolean online){connection.setText((online?"●  ":"○  ")+value);connection.setTextColor(online?green:muted);}
    private void composer(boolean enabled){chat.setEnabled(enabled);send.setEnabled(enabled);chat.setHint(enabled?"Escreva para sua sala…":"Entre em uma sala");}
    private void loadingLobby(){
        closeSheets();
        setConnection("Conectando",false);peerTitle.setText("JOGADORES");roomTitle.setText("SALAS DISPONÍVEIS");peers.removeAllViews();clearRoomRows();messages.removeAllViews();
        empty(peers,"…","Buscando jogadores","A lista aparece assim que a conexão for confirmada.");empty(rooms,"…","Abrindo o lobby","Preparando suas salas e seus convites.");empty(messages,"↗","Conversa da sala","Entre em uma partida para conversar com outro jogador.");composer(false);roomLayout(false);
    }
    private void unavailableLobby(){
        setConnection("Indisponível",false);peers.removeAllViews();clearRoomRows();
        empty(peers,"○","Conexão pendente","Os jogadores aparecem quando o serviço estiver disponível.");empty(rooms,"!","Salas indisponíveis","Não foi possível conectar agora. Use Reconectar para tentar novamente.");composer(false);
    }
    private void build(){
        getWindow().setStatusBarColor(0xff06080d);getWindow().setNavigationBarColor(0xff06080d);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        narrow=getResources().getConfiguration().screenWidthDp<760;
        FrameLayout stage=new FrameLayout(this);graphicsStage=stage;stage.setBackgroundColor(0xff226fa7);hyperspace=new StationHyperspaceView(this);
        stage.addView(hyperspace,new FrameLayout.LayoutParams(-1,-1));
        waves=new StationWaveBackground(this);waves.setVisibility(View.GONE);stage.addView(waves,new FrameLayout.LayoutParams(-1,-1));applyGraphics();
        LinearLayout root=row();stage.addView(root,new FrameLayout.LayoutParams(-1,-1));setContentView(stage);
        LinearLayout sidebar=vertical();sidebar.setPadding(dp(10),dp(10),dp(10),dp(8));sidebar.setBackgroundColor(0xf906080d);
        root.addView(sidebar,new LinearLayout.LayoutParams(dp(narrow?150:168),-1));
        
        TextView consoleBrand=text(sidebar,"JOGAR ONLINE",18,white);bold(consoleBrand);consoleBrand.setLetterSpacing(.04f);consoleBrand.setPadding(dp(10),dp(2),0,dp(6));
        nickname=new EditText(this);field(nickname,"Seu nome online");nickname.setBackground(null);nickname.setTextSize(11);nickname.setPadding(dp(10),0,dp(10),0);nickname.setSingleLine(true);nickname.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(24)});nickname.setText(getSharedPreferences("station-online-profile",0).getString("nickname","Jogador"));sidebar.addView(nickname,new LinearLayout.LayoutParams(-1,dp(44)));
        nickname.setContentDescription("Seu nome online. Use Reconectar para atualizar.");
        connection=text(sidebar,"○  Conectando",11,muted);connection.setPadding(dp(10),dp(4),dp(10),dp(4));connection.setBackground(null);
        ScrollView sideScroll=new ScrollView(this);sideScroll.setVerticalScrollBarEnabled(false);LinearLayout navItems=vertical();sideScroll.addView(navItems,new ScrollView.LayoutParams(-1,-2));sidebar.addView(sideScroll,new LinearLayout.LayoutParams(-1,0,1));
        navRooms=navButton(navItems,"Salas",()->navigate(0));navigationIcon(navRooms,0);
        navPeople=navButton(navItems,"Pessoas",()->navigate(1));navigationIcon(navPeople,1);
        navCreate=navButton(navItems,"Criar sala",()->navigate(2));navigationIcon(navCreate,2);
        navChat=navButton(navItems,"Conversas",()->{if(!pendingPeer.isEmpty())openConversation(pendingPeer,pendingName);else navigate(3);});navigationIcon(navChat,3);
        for(Button n:new Button[]{navRooms,navPeople,navCreate,navChat}){n.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);n.setTextSize(12);n.setPadding(dp(10),0,dp(6),0);}
        
        TextView signature=text(navItems,"LZ GAMES · COMUNIDADE",8,muted);signature.setLetterSpacing(.08f);signature.setPadding(dp(10),dp(2),0,dp(4));
        inviteNavigation=navButton(navItems,"Usar convite",()->enterCodeDialog());navigationIcon(inviteNavigation,4);
        retry=navButton(navItems,"Reconectar",()->connect());navigationIcon(retry,5);
        Button back=navButton(sidebar,"Voltar",()->exitRooms());navigationIcon(back,6);
        LinearLayout main=vertical();main.setPadding(dp(14),dp(10),dp(14),dp(8));root.addView(main,new LinearLayout.LayoutParams(0,-1,1));
        LinearLayout header=row();main.addView(header,new LinearLayout.LayoutParams(-1,dp(64)));
        FrameLayout art=new FrameLayout(this);header.addView(art,new LinearLayout.LayoutParams(dp(32),dp(40)));heroSymbol=new StationLobbyIcon(this,2);art.addView(heroSymbol,new FrameLayout.LayoutParams(-1,-1));heroCover=new ImageView(this);heroCover.setScaleType(ImageView.ScaleType.FIT_CENTER);art.addView(heroCover,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout names=vertical();LinearLayout.LayoutParams np=new LinearLayout.LayoutParams(0,-2,1);np.setMargins(dp(12),0,dp(12),0);header.addView(names,np);
        // Fixed two-line hierarchy. No horizontal marquee of metadata.
        title=label("PARTIDAS ONLINE",10,green);bold(title);title.setLetterSpacing(.10f);
        names.addView(title,new LinearLayout.LayoutParams(-1,dp(16)));
        subtitle=label(selectedItem==null?"Escolha uma sala ou converse com alguém":"Preparando seu jogo…",18,white);bold(subtitle);subtitle.setSingleLine(true);subtitle.setEllipsize(android.text.TextUtils.TruncateAt.END);
        names.addView(subtitle,new LinearLayout.LayoutParams(-1,dp(24)));
        LinearLayout headline=row();names.addView(headline,new LinearLayout.LayoutParams(-1,dp(24)));
        headerRating=new StationGameRatingView(this);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(dp(90),dp(24));rp.setMargins(0,0,dp(10),0);headline.addView(headerRating,rp);
        headerPlayers=label("—",10,muted);headerPlayers.setGravity(Gravity.CENTER_VERTICAL);headerPlayers.setSingleLine(true);headerPlayers.setEllipsize(android.text.TextUtils.TruncateAt.END);headerPlayers.setCompoundDrawablesWithIntrinsicBounds(new StationSocialIcon(1,dp(15),green),null,null,null);headerPlayers.setCompoundDrawablePadding(dp(5));headline.addView(headerPlayers,new LinearLayout.LayoutParams(0,-1,1));
        gamePlatform=label("",10,green);gamePlatform.setSingleLine(true);gamePlatform.setEllipsize(android.text.TextUtils.TruncateAt.END);gamePlatform.setGravity(Gravity.CENTER_VERTICAL);gamePlatform.setPadding(dp(10),0,0,0);headline.addView(gamePlatform,new LinearLayout.LayoutParams(0,-1,1));
        LinearLayout columns=row();LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,0,1);cp.topMargin=dp(10);main.addView(columns,cp);
        leftPanel=panel(columns,.44f,false);middlePanel=panel(columns,.44f,false);createPanel=panel(columns,.44f,false);createPanel.setPadding(dp(6),0,dp(6),0);rightPanel=panel(columns,.56f,false);
        middlePanel.addOnLayoutChangeListener((view,l,t,r,b,ol,ot,or,ob)->{if(ownRoomCard!=null&&(b-t!=ob-ot||r-l!=or-ol))updateOwnRoomHeight();});
        peerTitle=text(leftPanel,"PESSOAS ONLINE",12,green);bold(peerTitle);
        playerSearch=new EditText(this);field(playerSearch,"Buscar nesta página");playerSearch.setSingleLine(true);playerSearch.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(48)});leftPanel.addView(playerSearch,new LinearLayout.LayoutParams(-1,dp(48)));
        peers=vertical();peerScroll=scroll(leftPanel,peers);peerScroll.setVerticalScrollBarEnabled(true);
        playerSearch.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence s,int a,int c,int n){}public void afterTextChanged(android.text.Editable e){}public void onTextChanged(CharSequence s,int a,int b,int c){if(state.get()!=null)renderPlayers(state.get());}});
        roomTitle=text(middlePanel,"VER SALAS",12,green);roomTitle.setVisibility(View.GONE);middlePanel.setPadding(dp(6),0,dp(6),0);rooms=vertical();roomScroll=scroll(middlePanel,rooms);roomScroll.setPadding(0,0,0,0);roomScroll.setVerticalScrollBarEnabled(true);
        createPanel.setBackgroundColor(android.graphics.Color.TRANSPARENT);createPanel.setPadding(0,0,0,0);
        createCard=new StationCreateGameCard(this);createCard.setViewportBounded(true);createPanel.addView(createCard,new LinearLayout.LayoutParams(-1,-1));
        LinearLayout createActions=createCard.actions;
        createGame=text(createActions,"Jogo não selecionado",18,white);bold(createGame);createGame.setMaxLines(2);createGame.setEllipsize(android.text.TextUtils.TruncateAt.END);
        createGame.setVisibility(View.GONE); // The selected name already belongs to the main header.
        createGame.setAutoSizeTextTypeUniformWithConfiguration(14,18,1,android.util.TypedValue.COMPLEX_UNIT_SP);
        createOverview=vertical();createActions.addView(createOverview,new LinearLayout.LayoutParams(-1,0,1));
        createSynopsis=text(createOverview,"Sinopse indisponível no momento.",12,muted);createSynopsis.setMaxLines(2);createSynopsis.setEllipsize(android.text.TextUtils.TruncateAt.END);
        createSynopsis.setOnClickListener(v->showGameDetails(currentCoverItem(),createInfo==null?"":createInfo.getText().toString()));
        createInfo=label(StationGamePlayerInfo.pending().detail,12,muted);createInfo.setGravity(Gravity.TOP);createInfo.setPadding(0,dp(6),0,dp(6));
        createInfo.setAutoSizeTextTypeUniformWithConfiguration(10,12,1,android.util.TypedValue.COMPLEX_UNIT_SP);createInfo.setEllipsize(android.text.TextUtils.TruncateAt.END);
        createOverview.addView(createInfo,new LinearLayout.LayoutParams(-1,0,1));
        createInfo.setOnClickListener(v->showGameDetails(currentCoverItem(),createInfo.getText().toString()));
        TextView editionNote=text(createOverview,"Todos precisam da mesma edição do jogo.",11,muted);editionNote.setMaxLines(2);
        LinearLayout createButtons=row();createOverview.addView(createButtons,new LinearLayout.LayoutParams(-1,dp(48)));
        choose=button(createButtons,"Escolher jogo",()->chooseGame(),false);navigationIcon(choose,0);compactCreateAction(choose);
        LinearLayout.LayoutParams chooseSize=new LinearLayout.LayoutParams(0,dp(48),1);chooseSize.rightMargin=dp(8);choose.setLayoutParams(chooseSize);
        create=button(createButtons,"Criar sala",()->createRoom(),true);navigationIcon(create,2);compactCreateAction(create);create.setLayoutParams(new LinearLayout.LayoutParams(0,dp(48),1));create.setEnabled(false);
        createMessage=text(createOverview,"",12,muted);createMessage.setMaxLines(3);createMessage.setEllipsize(android.text.TextUtils.TruncateAt.END);createMessage.setVisibility(View.GONE);createMessage.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        createMessage.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("Criar sala").setMessage(createMessage.getText()).setPositiveButton("Fechar",null).show());
        buildRoomSetup(createActions);
        chatTitle=text(rightPanel,"Suas conversas",17,white);bold(chatTitle);chatHint=text(rightPanel,"Selecione uma pessoa ou entre em uma sala",11,muted);
        inboxNotice=text(rightPanel,"",12,green);inboxNotice.setVisibility(View.GONE);inboxNotice.setPadding(0,dp(8),0,dp(8));inboxNotice.setOnClickListener(v->{if(!pendingPeer.isEmpty())openConversation(pendingPeer,pendingName);});
        chatActions=row();rightPanel.addView(chatActions,new LinearLayout.LayoutParams(-1,-2));messages=vertical();chatScroll=scroll(rightPanel,messages);chatScroll.setVerticalScrollBarEnabled(true);
        LinearLayout chatbar=row();rightPanel.addView(chatbar,new LinearLayout.LayoutParams(-1,-2));chat=new EditText(this);field(chat,"Sua mensagem");chat.setMaxLines(3);chat.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);chat.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(500)});chat.setContentDescription("Escrever mensagem");chatbar.addView(chat,new LinearLayout.LayoutParams(0,dp(46),1));send=inline(chatbar,"",48,()->sendChat(),true);navigationIcon(send,StationSocialIcon.SEND);send.setGravity(Gravity.CENTER);send.setContentDescription("Enviar mensagem");
        status=text(main,"Conectando com sua sessão…",11,muted);status.setMaxLines(2);status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);loadingLobby();navigate(0);
        String incoming=getIntent().getStringExtra("station.peerId");if(incoming!=null){conversationPeer=incoming;conversationName="Jogador";section=3;roomLayout(false);}
    }
    private void compactCreateAction(Button button){
        ((StationActionButton)button).compactAppearance();
        LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)button.getLayoutParams();lp.height=dp(48);lp.topMargin=0;lp.bottomMargin=0;button.setLayoutParams(lp);
    }
    private void clearHeroCover(){
        heroCover.setImageDrawable(null);if(createCard!=null)createCard.setCover(null);if(ownRoomCard!=null)ownRoomCard.setCover(null);
        heroBitmap=null; // Artwork cache owns shared bitmaps; never recycle while another row displays one.
    }
    private String coverPlatform(String itemId){
        try{StationCoordinator.Library lib=StationAndroid.get(this).coordinator.current();
            StationCatalog.Item item=lib==null?null:lib.catalog.find(itemId);return item==null?"":item.platform;
        }catch(Exception unavailable){return "";}
    }
    /** Description always comes from the verified catalogue identity, never from a mode title. */
    private String synopsisFor(String itemId){
        StationCoordinator.Library library=client==null?null:client.app.coordinator.current();
        if(library==null||itemId==null)return "Sinopse indisponível no momento.";
        StationCatalog.Item item=library.catalog.find(itemId);
        if(item==null)return "Sinopse indisponível no momento.";
        String description=item.description==null?"":item.description.trim();
        return description.isEmpty()?"Sinopse ainda não cadastrada.":description;
    }
    /** Only explanatory UI copy is cleaned; catalogue names, synopses and verified profiles are unchanged. */
    private static final java.util.regex.Pattern TECHNICAL_COPY=java.util.regex.Pattern.compile("(?iu)\\b(?:github|gitlab|bitbucket|git|handoff|commit|reposit[oó]rio|branch|sha256|sha-256|endpoint|runtime|dex|dll|servidor)\\b|^\\s*(?:fontes(?: do modo)?|refer[eê]ncias|suporte confirmado na documenta[cç][aã]o)\\s*[:\\s]");
    private static String playGuidance(String value){
        if(value==null||value.trim().isEmpty())return "";
        StringBuilder clean=new StringBuilder();
        for(String line:value.split("\\r?\\n")){
            String copy=line.replaceAll("\\[([^\\]]+)\\]\\((?:https?://|www\\.)[^\\s)]+\\)","$1")
                    .replaceAll("(?i)(?:https?://|www\\.)[^\\s]+","").trim();
            if(copy.isEmpty())continue;
            StringBuilder paragraph=new StringBuilder();
            for(String sentence:copy.split("(?<=[.!?;])\\s+")){
                if(TECHNICAL_COPY.matcher(sentence).find())continue;
                if(paragraph.length()>0)paragraph.append(' ');paragraph.append(sentence.trim());
            }
            if(paragraph.length()>0){if(clean.length()>0)clean.append('\n');clean.append(paragraph);}
        }
        return clean.toString();
    }
    private static String onlineNotice(String value){
        if(value==null||value.trim().isEmpty())return "";
        String message=playGuidance(value.replaceAll("(?iu)\\bservidor(?:\\s+(?:Station|PIX))?\\b","serviço online"));
        if(!message.isEmpty())return message;
        String original=value.toLowerCase(java.util.Locale.ROOT);
        if(original.contains("ativação")||original.contains("aguarda")||original.contains("pending")||original.contains("unavailable"))return "Este modo online ainda não está disponível nesta sessão. Aguarde a ativação desta opção.";
        return "Não foi possível concluir esta ação. Confira sua conexão e tente novamente.";
    }
    private int roomViewportHeight(){
        int height=middlePanel==null?0:middlePanel.getHeight();
        return height>0?height:Math.max(dp(180),getResources().getDisplayMetrics().heightPixels-dp(90));
    }
    /** In short windows the existing outer room scroll keeps every action reachable. */
    private static int ownRoomHeight(int viewport,int footer,int textMinimum){return Math.max(Math.max(0,viewport),Math.max(0,footer)+Math.max(0,textMinimum));}
    private int ownRoomRequiredHeight(){
        int footer=0;
        if(ownRoomFooter!=null){footer=ownRoomFooter.getPaddingTop()+ownRoomFooter.getPaddingBottom();for(int i=0;i<ownRoomFooter.getChildCount();i++){
            View child=ownRoomFooter.getChildAt(i);if(child.getVisibility()==View.GONE)continue;
            footer+=child instanceof RoomControls?((RoomControls)child).requiredHeight():child.getMeasuredHeight();
        }}
        return ownRoomHeight(roomViewportHeight(),footer,dp(96));
    }
    private void updateOwnRoomHeight(){
        // Snapshot painting temporarily clears and rebuilds only the actions.
        // Keep the retained surface size until the replacement footer is measured.
        if(ownRoomCard==null||ownRoomFooter==null||ownRoomFooter.getChildCount()==0)return;
        for(int i=0;i<ownRoomFooter.getChildCount();i++){View child=ownRoomFooter.getChildAt(i);if(child.getVisibility()==View.GONE)continue;
            if(child instanceof RoomControls?!((RoomControls)child).hasMeasuredActions():child.getMeasuredHeight()==0)return;
        }
        LinearLayout.LayoutParams size=(LinearLayout.LayoutParams)ownRoomCard.getLayoutParams();
        int height=ownRoomRequiredHeight();if(size.height!=height){size.height=height;ownRoomCard.setLayoutParams(size);}
    }
    private void showGameDetails(String itemId,String instructions){
        String title=client==null||itemId==null?"Informações do jogo":client.name(itemId);
        String guidance=playGuidance(instructions);String message=synopsisFor(itemId)+(guidance.isEmpty()?"":"\n\nComo jogar\n"+guidance);
        new AlertDialog.Builder(this).setTitle(title).setMessage(message).setPositiveButton("Fechar",null).show();
    }
    private void addSynopsis(LinearLayout parent,String itemId,int lines,String instructions){
        TextView synopsis=text(parent,synopsisFor(itemId),12,muted);synopsis.setMaxLines(lines);synopsis.setEllipsize(android.text.TextUtils.TruncateAt.END);synopsis.setLineSpacing(dp(1),1f);
        synopsis.setOnClickListener(v->showGameDetails(itemId,instructions));
        if(lines<=2){TextView detail=text(parent,"Ver detalhes",11,green);detail.setPadding(0,dp(3),0,dp(7));detail.setOnClickListener(v->showGameDetails(itemId,instructions));}
    }
    private void bindHeroCover(){
        if(createCard!=null)createCard.setPlatform(coverPlatform(selectedItem));
        if(ownRoomCard!=null)ownRoomCard.setPlatform(coverPlatform(ownRoomCoverItem));
        heroCover.setImageBitmap(heroBitmap);
        if(createCard!=null)createCard.setCover(heroRequestId.equals(selectedItem)?heroBitmap:null);
        if(ownRoomCard!=null)ownRoomCard.setCover(heroRequestId.equals(ownRoomCoverItem)?heroBitmap:null);
    }
    private static String roomRowKey(String kind,String id,String item){return kind+":"+id.length()+":"+id+":"+item;}
    private void beginRoomRows(){desiredRoomRows.clear();usedRoomRows.clear();ownRoomCard=null;ownRoomCoverItem="";ownRoomFooter=null;start=null;roomReadiness=null;}
    private LinearLayout roomCoverCard(String kind,String id,String item,boolean own){
        String identity=roomRowKey(kind,id,item),key=identity;
        for(int duplicate=1;usedRoomRows.contains(key);duplicate++)key=identity+"#"+duplicate;
        usedRoomRows.add(key);RoomRow binding=roomRows.get(key);
        if(binding==null){
            StationCreateGameCard display=new StationCreateGameCard(this,true);View root;LinearLayout content,footer=null;
            if(own){
                display.setViewportBounded(true);root=display;rooms.addView(root,new LinearLayout.LayoutParams(-1,roomViewportHeight()));
                // Keep human actions at the bottom of the available viewport.
                // Only the text may scroll at large font scales or in short windows.
                ScrollView readiness=new ScrollView(this);readiness.setFillViewport(true);readiness.setVerticalScrollBarEnabled(false);display.actions.addView(readiness,new LinearLayout.LayoutParams(-1,0,1));
                content=vertical();content.setPadding(0,0,dp(6),0);readiness.addView(content,new ScrollView.LayoutParams(-1,-2));
                footer=vertical();footer.setPadding(0,dp(8),0,0);display.actions.addView(footer,new LinearLayout.LayoutParams(-1,-2));
                final LinearLayout retainedFooter=footer;footer.addOnLayoutChangeListener((view,l,t,r,b,ol,ot,or,ob)->{if(ownRoomCard==display&&ownRoomFooter==retainedFooter)updateOwnRoomHeight();});
            }else{
                LinearLayout shell=card(rooms);shell.setPadding(dp(8),dp(2),dp(8),dp(2));shell.addView(display,new LinearLayout.LayoutParams(-1,-2));root=shell;content=display.actions;
            }
            binding=new RoomRow(root,display,content,footer);roomRows.put(key,binding);
        }
        desiredRoomRows.add(binding.root);binding.content.removeAllViews();if(binding.footer!=null)binding.footer.removeAllViews();binding.display.setGameName(client.name(item));binding.display.setPlatform(coverPlatform(item));
        if(own){
            ownRoomCard=binding.display;ownRoomCoverItem=item;ownRoomFooter=binding.footer;
            updateOwnRoomHeight();bindHeroCover();
        }else if(!binding.loading&&!binding.loaded){
            // Cached artwork callbacks may complete immediately. Register identity
            // first, and reject a completion after this row has left the snapshot.
            final String targetKey=key;final RoomRow target=binding;binding.loading=true;
            artwork.load(item,1536,image->{if(roomRows.get(targetKey)==target){target.loading=false;target.loaded=image!=null;target.display.setCover(image);}});
        }
        return binding.content;
    }
    private void reconcileRoomRows(){
        Iterator<Map.Entry<String,RoomRow>> entries=roomRows.entrySet().iterator();
        while(entries.hasNext()){Map.Entry<String,RoomRow> entry=entries.next();if(!usedRoomRows.contains(entry.getKey())){entry.getValue().display.setCover(null);entries.remove();}}
        Set<View> wanted=Collections.newSetFromMap(new IdentityHashMap<View,Boolean>());wanted.addAll(desiredRoomRows);
        for(int i=rooms.getChildCount()-1;i>=0;i--)if(!wanted.contains(rooms.getChildAt(i)))rooms.removeViewAt(i);
        boolean ordered=rooms.getChildCount()==desiredRoomRows.size();for(int i=0;ordered&&i<desiredRoomRows.size();i++)ordered=rooms.getChildAt(i)==desiredRoomRows.get(i);
        // bringChildToFront changes sibling order without detaching TextureView.
        if(!ordered)for(View row:desiredRoomRows)rooms.bringChildToFront(row);
        desiredRoomRows.clear();usedRoomRows.clear();
    }
    private void clearRoomRows(){for(RoomRow binding:roomRows.values())binding.display.setCover(null);roomRows.clear();desiredRoomRows.clear();usedRoomRows.clear();ownRoomCard=null;ownRoomCoverItem="";ownRoomFooter=null;rooms.removeAllViews();}
    /** Catalogue text stays separate from the verified participant roster and footer. */
    private void ownRoomGuide(LinearLayout parent,JSONObject mine){
        TextView heading=text(parent,"SOBRE O JOGO",9,green);bold(heading);heading.setLetterSpacing(.08f);heading.setPadding(0,dp(12),0,dp(4));
        TextView synopsis=text(parent,synopsisFor(mine.optString("itemId")),12,muted);synopsis.setPadding(0,0,0,dp(8));synopsis.setMaxLines(4);synopsis.setEllipsize(android.text.TextUtils.TruncateAt.END);synopsis.setLineSpacing(dp(2),1);
        synopsis.setOnClickListener(v->showGameDetails(mine.optString("itemId"),roomExplanation(mine)));
        String instructions="waiting".equals(mine.optString("state"))?"Marque Estou pronto. Quando todos confirmarem, o anfitrião inicia a partida.":"Use Conversa para falar com os jogadores. Sair deixa esta sala.";
        TextView guide=text(parent,instructions,11,white);guide.setPadding(0,0,0,dp(4));guide.setLineSpacing(dp(2),1);
        TextView details=text(parent,"Ver sinopse completa e como jogar",11,green);details.setPadding(0,dp(3),0,dp(7));details.setOnClickListener(v->showGameDetails(mine.optString("itemId"),roomExplanation(mine)));
    }
    private LinearLayout actionLine(LinearLayout parent){LinearLayout line=row();parent.addView(line,new LinearLayout.LayoutParams(-1,dp(48)));return line;}
    /** Natural button widths avoid stretched faces; narrow windows wrap safely. */
    private static int[] roomControlLayout(int available,int[] wanted,int target,int gap){
        int width=Math.max(0,available),x=0,y=0;int[] boxes=new int[wanted.length*4];
        for(int i=0;i<wanted.length;i++){
            if(wanted[i]<=0)continue;
            int child=Math.min(width,Math.max(target,wanted[i]));
            if(x>0&&x+gap+child>width){x=0;y+=target+gap;}
            else if(x>0)x+=gap;
            boxes[i*4]=x;boxes[i*4+1]=y;boxes[i*4+2]=child;boxes[i*4+3]=target;x+=child;
        }
        return boxes;
    }
    private final class RoomControls extends LinearLayout {
        private int[] boxes=new int[0];
        RoomControls(){super(StationRoomsActivity.this);setOrientation(HORIZONTAL);setPadding(0,dp(3),0,dp(3));addOnLayoutChangeListener((view,l,t,r,b,ol,ot,or,ob)->{if(getParent()==ownRoomFooter)updateOwnRoomHeight();});}
        boolean hasMeasuredActions(){return boxes.length==getChildCount()*4;}
        int requiredHeight(){int height=0;for(int i=0;i+3<boxes.length;i+=4)height=Math.max(height,boxes[i+1]+boxes[i+3]);return height+getPaddingTop()+getPaddingBottom();}
        @Override protected void onMeasure(int widthSpec,int heightSpec){
            int width=Math.max(0,View.MeasureSpec.getSize(widthSpec)-getPaddingLeft()-getPaddingRight());
            int count=getChildCount(),target=dp(48);int[] wanted=new int[count];
            for(int i=0;i<count;i++){
                View view=getChildAt(i);if(view.getVisibility()==View.GONE)continue;
                TextView button=(TextView)view;
                wanted[i]=Math.max(target,(int)Math.ceil(button.getPaint().measureText(button.getText().toString()))+button.getCompoundPaddingLeft()+button.getCompoundPaddingRight()+dp(2));
            }
            boxes=roomControlLayout(width,wanted,target,dp(6));int height=0;
            for(int i=0;i<count;i++){
                View view=getChildAt(i);if(view.getVisibility()==View.GONE)continue;
                view.measure(View.MeasureSpec.makeMeasureSpec(boxes[i*4+2],View.MeasureSpec.EXACTLY),View.MeasureSpec.makeMeasureSpec(target,View.MeasureSpec.EXACTLY));
                height=Math.max(height,boxes[i*4+1]+target);
            }
            setMeasuredDimension(View.resolveSizeAndState(width+getPaddingLeft()+getPaddingRight(),widthSpec,0),View.resolveSizeAndState(height+getPaddingTop()+getPaddingBottom(),heightSpec,0));
        }
        @Override protected void onLayout(boolean changed,int left,int top,int right,int bottom){
            for(int i=0;i<getChildCount()&&i*4+3<boxes.length;i++){
                View view=getChildAt(i);if(view.getVisibility()==View.GONE)continue;
                int x=getPaddingLeft()+boxes[i*4],y=getPaddingTop()+boxes[i*4+1];view.layout(x,y,x+boxes[i*4+2],y+boxes[i*4+3]);
            }
        }
    }
    private LinearLayout roomControls(LinearLayout parent){RoomControls line=new RoomControls();parent.addView(line,new LinearLayout.LayoutParams(-1,-2));return line;}
    private Button roomAction(LinearLayout line,String value,int icon,int tone,Runnable action){
        StationActionButton b=new StationActionButton(this,value,tone,icon);styleAction(b,tone);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(48),1);lp.leftMargin=line.getChildCount()==0?0:dp(8);
        line.addView(b,lp);b.setOnClickListener(v->action.run());b.setEnabled(!busy&&!launching);return b;
    }
    private void navigationIcon(Button button,int kind){((StationActionButton)button).setActionIcon(kind);}
    @Override protected void onResume(){super.onResume();if(hyperspace!=null)hyperspace.setResumed(true);if(headerRating!=null)headerRating.setResumed(true);}
    @Override protected void onPause(){if(hyperspace!=null)hyperspace.setResumed(false);if(headerRating!=null)headerRating.setResumed(false);super.onPause();}
    private void applyGraphics(){
        if(graphics==null)return;
        int mode=graphics.effectiveBackgroundMode();
        if(hyperspace!=null)hyperspace.setVisibility(mode==StationGraphicsPreferences.SKY||mode==StationGraphicsPreferences.ONLINE_WAVES?View.VISIBLE:View.GONE);
        if(waves!=null)waves.setVisibility(mode==StationGraphicsPreferences.WAVES?View.VISIBLE:View.GONE);
        if(graphicsStage!=null)graphicsStage.setBackgroundColor(0xff226fa7);
    }
    @Override public void onGraphicsChanged(StationGraphicsPreferences.State state){applyGraphics();}
    private void navigate(int next){if(next!=2)clearRoomSetup();section=next;roomLayout(room()!=null);if(client!=null&&state.get()!=null){
        if(!busy&&!launching&&next==0&&roomPage!=0)pageRooms(-roomPage);
        else if(!busy&&!launching&&next==1&&page!=0)pagePeers(-page);
        else{painted=-1;paint(state.get());}
    }}
    private static final class GameChoice {final StationCatalog.Item item;GameChoice(StationCatalog.Item i){item=i;}@Override public String toString(){return item.name+"  ·  "+item.platform;}}
    private final class GameChoiceAdapter extends ArrayAdapter<GameChoice>{
        GameChoiceAdapter(java.util.List<GameChoice> choices){super(StationRoomsActivity.this,android.R.layout.simple_list_item_1,choices);}
        @Override public View getView(int position,View recycled,android.view.ViewGroup parent){
            LinearLayout line;ImageView cover;TextView name,platform;
            if(recycled instanceof LinearLayout){line=(LinearLayout)recycled;cover=(ImageView)line.getChildAt(0);LinearLayout labels=(LinearLayout)line.getChildAt(1);name=(TextView)labels.getChildAt(0);platform=(TextView)labels.getChildAt(1);}
            else{line=row();line.setPadding(dp(6),dp(3),dp(6),dp(3));cover=new ImageView(StationRoomsActivity.this);cover.setScaleType(ImageView.ScaleType.FIT_CENTER);line.addView(cover,new LinearLayout.LayoutParams(dp(38),dp(50)));LinearLayout labels=vertical();LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.leftMargin=dp(10);line.addView(labels,lp);name=text(labels,"",13,white);name.setMaxLines(2);name.setEllipsize(android.text.TextUtils.TruncateAt.END);platform=text(labels,"",10,muted);}
            GameChoice choice=getItem(position);if(choice==null)return line;
            final String id=choice.item.itemId;cover.setTag(id);cover.setImageDrawable(null);cover.setContentDescription("Capa de "+choice.item.name);name.setText(choice.item.name);platform.setText(choice.item.platform);
            artwork.load(id,128,bitmap->{if(id.equals(cover.getTag()))cover.setImageBitmap(bitmap);});
            return line;
        }
    }
    private void chooseGame(){
        if(client==null||state.get()==null||busy)return;
        java.util.ArrayList<StationCatalog.Item> items=new java.util.ArrayList<>();java.util.ArrayList<String> names=new java.util.ArrayList<>();
        StationCoordinator.Library lib=client.app.coordinator.current();if(lib==null)return;
        for(StationCatalog.Item item:lib.catalog.items)try{String platform=StationOnlineGame.platform(item.platform);JSONArray engines=state.get().optJSONArray("engines");for(int i=0;engines!=null&&i<engines.length();i++)if(platform.equals(engines.getJSONObject(i).optString("platform"))){items.add(item);names.add(item.name+"  ·  "+item.platform);break;}}catch(Exception unsupported){}
        if(items.isEmpty()){status.setText("Nenhum motor liberado para os jogos deste catálogo.");return;}
        LinearLayout panel=codePanel("Escolher jogo","Busque uma edição do catálogo. Baixe o jogo antes de criar sua sala.");EditText search=new EditText(this);field(search,"Buscar jogo");search.setSingleLine(true);panel.addView(search);
        ListView list=new ListView(this);java.util.ArrayList<GameChoice> choices=new java.util.ArrayList<>();for(StationCatalog.Item item:items)choices.add(new GameChoice(item));ArrayAdapter<GameChoice> adapter=new GameChoiceAdapter(choices);list.setAdapter(adapter);panel.addView(list,new LinearLayout.LayoutParams(-1,dp(170)));
        search.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence s,int a,int c,int n){}public void afterTextChanged(android.text.Editable e){}public void onTextChanged(CharSequence s,int a,int b,int c){adapter.getFilter().filter(s);}});
        list.setOnItemClickListener((parent,view,index,id)->{GameChoice chosen=adapter.getItem(index);if(chosen==null)return;clearRoomSetup();selectedItem=chosen.item.itemId;createGame.setText(chosen.item.name);subtitle.setText(chosen.item.name);codeDialog.dismiss();createCard.setGameName(chosen.item.name);showCreateMessage("",false);loadHero();});displayCodePanel();
    }
    private void confirmWithCover(String heading,String message,String positive,Runnable accepted){
        confirmWithCover(heading,message,positive,accepted,currentCoverItem());
    }
    private void confirmWithCover(String heading,String message,String positive,Runnable accepted,String item){
        LinearLayout content=codePanel(heading,message,item,true);
        LinearLayout actions=roomControls(content);
        roomAction(actions,positive,StationActionButton.iconForLabel(positive),StationActionButton.PRIMARY,()->{codeDialog.dismiss();accepted.run();});
        roomAction(actions,"Cancelar",StationSocialIcon.CLOSE,StationActionButton.SECONDARY,()->codeDialog.dismiss());displayCodePanel();
    }


    @Override protected void onStart(){super.onStart();graphics.addListener(this);applyGraphics();artwork.start();StationPresence.foreground(this,false);active=true;if(returningFromGame)StationTaskNavigation.gameReturned(this);connect();loadHero();}
    @Override protected void onStop(){graphics.removeListener(this);stopMultiplayerPoll();if(hyperspace!=null)hyperspace.setResumed(false);if(headerRating!=null)headerRating.setResumed(false);active=false;epoch++;artwork.stop();cancelAll();closeSheets();super.onStop();}
    @Override protected void onDestroy(){commands.shutdownNow();events.shutdownNow();clearHeroCover();clearRoomRows();artwork.close();multiplayerEvents.shutdownNow();super.onDestroy();}
    private void cancelAll(){if(polling!=null)polling.cancel(true);synchronized(requests){for(StationApi.Cancellation c:requests)c.cancel();requests.clear();}}
    private void connect(){if(!active)return;clearRoomSetup();epoch++;stopMultiplayerPoll();cancelAll();busy=false;creating=false;choose.setEnabled(true);create.setText("Criar sala");feedback.begin();int generation=epoch;state.reset();roster.reset();painted=-1;prepared=null;launchKey="";launching=false;loadingLobby();
        String nick=nickname.getText().toString().trim();if(nick.isEmpty()){status.setText("Escolha seu apelido para entrar.");return;}getPreferences(0).edit().putString("nickname",nick).apply();getSharedPreferences("station-online-profile",0).edit().putString("nickname",nick).apply();
        status.setText("Consultando jogadores e salas…");create.setEnabled(false);polling=events.submit(()->{
            StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);
            try{
                client=new StationOnlineClient(this);client.setPeerPage(page);client.setRoomPage(roomPage);
                runOnUiThread(()->{if(active&&epoch==generation){roomLayout(room()!=null);loadHero();}});
                if(returningFromGame&&!returningRecovery){try{client.call(StationOnlineClient.command("leave"),false,cancel);}catch(StationApi.Failure e){if(!e.code.equals("STATION_ONLINE_ENTER_REQUIRED"))throw e;}returningFromGame=false;}
                JSONObject current=client.call(StationOnlineClient.command("enter").put("nickname",nick),false,cancel);
                if(returningFromGame&&returningRecovery){JSONObject lost=current.optJSONObject("room");if(lost!=null&&"relay-wss-v2".equals(lost.optString("transport")))current=client.call(StationOnlineClient.command("recovery-failed").put("roomId",lost.getString("roomId")).put("generation",lost.getLong("generation")),false,cancel);returningFromGame=false;returningRecovery=false;}
                // Present the verified social snapshot before probing optional v3 support.
                deliver(current,generation);beginMultiplayerDiscovery(client,generation);
                long heartbeat=SystemClock.elapsedRealtime();int pollFailures=0;
                while(active&&epoch==generation&&!Thread.currentThread().isInterrupted()){
                    JSONObject latest=state.get();if(latest!=null)current=latest;
                    try{
                        if(SystemClock.elapsedRealtime()-heartbeat>=20000){current=client.call(StationOnlineClient.command("heartbeat"),false,cancel);heartbeat=SystemClock.elapsedRealtime();deliver(current,generation);}
                        current=client.events(current,page,cancel);deliver(current,generation);pollFailures=0;
                    }catch(Exception error){
                        cancel.check();long wait=StationOnlineClient.pollRetryDelay(error,++pollFailures);if(wait<0)throw error;
                        if(pollFailures==1)recordFailure(error);
                        runOnUiThread(()->{if(active&&epoch==generation&&!busy){setConnection("Aguardando conexão",false);status.setText("A consulta será retomada quando a conexão voltar.");}});
                        Thread.sleep(wait);cancel.check();
                    }
                }
            }catch(Exception e){if(!cancel.cancelled()){runOnUiThread(()->{if(active&&epoch==generation)setConnection("Reconectar",false);});failure(e,generation);}}finally{requests.remove(cancel);}
        });
    }
    private void beginMultiplayerDiscovery(final StationOnlineClient connectedClient,final int generation){
        if(!active||epoch!=generation||client!=connectedClient)return;
        final int pollEpoch=multiplayerPollEpoch;
        multiplayerPolling=multiplayerEvents.schedule(()->{
            StationApi.Cancellation probe=new StationApi.Cancellation();
            synchronized(StationRoomsActivity.this){if(!active||epoch!=generation||pollEpoch!=multiplayerPollEpoch||client!=connectedClient)return;multiplayerPollCancellation=probe;requests.add(probe);}
            String notice="";
            try{
                connectedClient.discoverMultiplayer(probe);probe.check();
                if(!active||epoch!=generation||client!=connectedClient)return;
                deliver(connectedClient.compose(null),generation);
                if(connectedClient.multiplayerEnabled)notice="";
            }catch(Exception error){
                if(probe.cancelled()||!active||epoch!=generation)return;
                recordFailure(error);notice=StationOnlineClient.message(error);
            }finally{requests.remove(probe);if(multiplayerPollCancellation==probe)multiplayerPollCancellation=null;}
            final String message=notice;
            runOnUiThread(()->{
                if(!active||epoch!=generation||pollEpoch!=multiplayerPollEpoch||client!=connectedClient)return;
                if(!busy&&!creating)showCreateMessage(message,!message.isEmpty());
                loadHero();
                if(connectedClient.multiplayerEnabled){
                    scheduleMultiplayerPoll(connectedClient,generation,0,1000);
                }
            });
        },0,TimeUnit.MILLISECONDS);
    }
    /** Exactly one delayed read-only snapshot poll; mutating room actions use action() once. */
    private void scheduleMultiplayerPoll(final StationOnlineClient connectedClient,final int generation,final int failures,long delay){
        if(!active||epoch!=generation||client!=connectedClient)return;
        final int pollEpoch=multiplayerPollEpoch;
        multiplayerPolling=multiplayerEvents.schedule(()->{
            if(!active||epoch!=generation||pollEpoch!=multiplayerPollEpoch||client!=connectedClient)return;
            StationApi.Cancellation poll=new StationApi.Cancellation();
            synchronized(StationRoomsActivity.this){if(!active||epoch!=generation||pollEpoch!=multiplayerPollEpoch||client!=connectedClient)return;multiplayerPollCancellation=poll;requests.add(poll);}
            long next=1000;int consecutive=0;
            try{deliver(connectedClient.pollMultiplayer(poll),generation);}
            catch(Exception error){
                if(poll.cancelled()||!active||epoch!=generation)return;
                consecutive=failures+1;next=StationOnlineClient.pollRetryDelay(error,consecutive);
                if(consecutive==1||next<0)recordFailure(error);
                final boolean terminal=next<0;final String message=StationOnlineClient.message(error);
                runOnUiThread(()->{if(active&&epoch==generation&&client==connectedClient&&!busy&&!creating){showCreateMessage(message,terminal);if(terminal)status.setText(message);}});
            }finally{requests.remove(poll);if(multiplayerPollCancellation==poll)multiplayerPollCancellation=null;}
            final long nextDelay=next;final int nextFailures=consecutive;
            runOnUiThread(()->{if(nextDelay>=0&&active&&epoch==generation&&pollEpoch==multiplayerPollEpoch&&client==connectedClient)scheduleMultiplayerPoll(connectedClient,generation,nextFailures,nextDelay);});
        },Math.max(0,delay),TimeUnit.MILLISECONDS);
    }
    private void deliver(JSONObject snapshot,int generation)throws Exception {if(!active||generation!=epoch)return;if(!state.accept(snapshot))return;runOnUiThread(()->{if(active&&generation==epoch){roster.observe(snapshot);paint(snapshot);applyPendingNavigation(snapshot);}});}
    private static void recordFailure(Throwable error){
        StringBuilder detail=new StringBuilder();Throwable cause=error;
        for(int depth=0;cause!=null&&depth<3;depth++,cause=cause.getCause()){
            detail.append(" type=").append(cause.getClass().getName());
            if(cause instanceof StationApi.Failure){StationApi.Failure api=(StationApi.Failure)cause;detail.append(" http=").append(api.status);if(api.code!=null&&api.code.matches("[A-Z0-9_]{1,80}"))detail.append(" code=").append(api.code);}
            StackTraceElement[] stack=cause.getStackTrace();for(int i=0;i<Math.min(stack.length,8);i++)detail.append(" at=").append(stack[i].getClassName()).append('.').append(stack[i].getMethodName()).append(':').append(stack[i].getLineNumber());
        }
        android.util.Log.w("StationRooms",detail.toString());
    }
    private void failure(Throwable error,int generation){recordFailure(error);runOnUiThread(()->{if(active&&generation==epoch){if(createSetup!=null&&createSetup.getVisibility()==View.VISIBLE)clearRoomSetup();if(creating){creating=false;choose.setEnabled(true);create.setText("Criar sala");showCreateMessage(StationOnlineClient.message(error),true);}feedback.fail(StationOnlineClient.message(error));status.setText(onlineNotice(feedback.text(state.get(),false)));if(state.get()==null)unavailableLobby();busy=false;updateStartState();retry.setEnabled(true);create.setEnabled(state.get()!=null&&room()==null&&!launching);peerFeedback=StationOnlineClient.message(error);if(state.get()!=null)renderConversation(state.get());refreshPlayerSheet();}});}
    interface Work {JSONObject run(StationApi.Cancellation cancel)throws Exception;}
    private void action(Work work){action(work,null);}
    private void action(Work work,Runnable completed){if(busy||!active||client==null||state.get()==null)return;busy=true;feedback.begin();create.setEnabled(false);updateRoomSetupEnabled();refreshPlayerSheet();int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);
        commands.execute(()->{try{JSONObject response=work.run(cancel);deliver(response,generation);runOnUiThread(()->{if(active&&generation==epoch){busy=false;status.setText(onlineNotice(feedback.text(state.get(),false)));updateStartState();create.setEnabled(room()==null&&!launching);if(completed!=null)completed.run();painted=-1;if(state.get()!=null)paint(state.get());updateRoomSetupEnabled();refreshPlayerSheet();}});}catch(Exception e){if(!cancel.cancelled())failure(e,generation);}finally{requests.remove(cancel);}});
    }
    private JSONObject room(){JSONObject snapshot=state.get();return snapshot==null?null:snapshot.optJSONObject("room");}
    private void showCreateMessage(String message,boolean error){
        createMessage.setText(onlineNotice(message));createMessage.setTextColor(error?0xfff4b0a2:green);createMessage.setVisibility(message.isEmpty()?View.GONE:View.VISIBLE);
    }
    private static StationGamePlayerInfo profileInfo(StationMultiplayerProfile p){return StationGamePlayerInfo.fromVerifiedProfile(true,p.maximumPlayers,p.allowed,p.mode,p.controllerProfile).withHelp(p.modeTitle,p.instructions,p.sources);}
    private static StationGamePlayerInfo roomGameInfo(JSONObject r){
        if(r==null||!"station-stream.v3".equals(r.optString("recoveryProtocol")))return StationGamePlayerInfo.pending();
        JSONArray a=r.optJSONArray("allowedPlayerCounts");int[] counts=new int[a==null?0:a.length()];for(int i=0;i<counts.length;i++)counts[i]=a.optInt(i);
        return StationGamePlayerInfo.fromVerifiedProfile(true,r.optInt("maximumPlayers"),counts,r.optString("mode"),r.optString("controllerProfile")).withHelp(r.optString("modeTitle",""),displayHelp(r,"instructions"),displayHelp(r,"sources"));
    }
    private static String[] displayHelp(JSONObject value,String key){
        try{return StationMultiplayerProfile.help(value,key,"sources".equals(key)?512:500,"sources".equals(key));}
        catch(Exception invalid){return new String[0];}
    }
    private static StationGamePlayerInfo.RoomInfo roomInfo(JSONObject r,String self){
        StationGamePlayerInfo info=roomGameInfo(r);JSONArray a=r==null?null:r.optJSONArray("roster");StationGamePlayerInfo.Participant[] people=new StationGamePlayerInfo.Participant[a==null?0:a.length()];
        for(int i=0;i<people.length;i++){JSONObject p=a.optJSONObject(i);if(p!=null)people[i]=new StationGamePlayerInfo.Participant(p.optInt("slot"),p.optString("peerId"),p.optString("nickname"),p.optBoolean("ready"),self.equals(p.optString("peerId")));}
        return info.forRoom(r==null?0:r.optInt("capacity"),r!=null&&"waiting".equals(r.optString("state")),people);
    }
    private String roomExplanation(JSONObject r){
        StationGamePlayerInfo.RoomInfo info=roomInfo(r,state.get()==null?"":state.get().optString("selfId"));
        StringBuilder text=new StringBuilder(playGuidance(info.detail));if(!info.confirmed)return text.toString();
        text.append("\n\n");for(StationGamePlayerInfo.Position p:info.positions){text.append(p.label).append(" · ").append(p.name).append(p.self?" (você)":"").append("\n");}
        if(displayHelp(r,"instructions").length==0&&"battle-single".equals(r.optString("mode"))&&"snes-multitap-port2-v1".equals(r.optString("controllerProfile")))text.append("\nNo jogo, escolha BATTLE GAME → Single Match e marque MAN nos controles dos participantes. As vagas desta sala são para Batalha; confira o limite da campanha na descrição do modo.");
        text.append("\nTodos precisam da mesma edição do jogo. Cada participante controla apenas sua posição e pode usar sua própria rede.");return text.toString();
    }
    // Presentation stays inside the existing cover panel. Only verified profiles grant choices.
    private void buildRoomSetup(LinearLayout parent){
        createSetup=vertical();createSetup.setVisibility(View.GONE);parent.addView(createSetup,new LinearLayout.LayoutParams(-1,0,1));
        TextView heading=text(createSetup,"Partida",11,green);bold(heading);heading.setPadding(0,dp(3),0,dp(2));
        setupModes=roomControls(createSetup);
        TextView counts=text(createSetup,"Jogadores",11,green);bold(counts);counts.setPadding(0,dp(4),0,dp(2));
        setupCounts=roomControls(createSetup);
        setupDescription=label("",12,muted);setupDescription.setGravity(Gravity.TOP);setupDescription.setPadding(0,dp(5),0,dp(4));
        setupDescription.setMaxLines(3);setupDescription.setEllipsize(android.text.TextUtils.TruncateAt.END);
        setupDescription.setContentDescription("Resumo da partida. Toque para ver como jogar.");setupDescription.setOnClickListener(v->{if(setupProfile!=null)showGameDetails(selectedItem,roomSetupDescription(setupProfile,setupCapacity));});
        setupDescription.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        createSetup.addView(setupDescription,new LinearLayout.LayoutParams(-1,-2));
        LinearLayout actions=roomControls(createSetup);
        setupBack=roomAction(actions,"Voltar",StationSocialIcon.BACK,StationActionButton.SECONDARY,()->clearRoomSetup());
        setupConfirm=roomAction(actions,"Criar sala",StationSocialIcon.PLAY,StationActionButton.PRIMARY,()->confirmRoomSetup());
    }
    private static String setupModeName(StationMultiplayerProfile profile){
        StationGamePlayerInfo info=profileInfo(profile);if(info.modeConfirmed){String name=playGuidance(info.modeLabel);if(!name.isEmpty())return name;}
        switch(profile.mode){
            case "two-player":return "Partida para dois";
            case "two-player-a":return "Dois jogadores · modo A";
            case "two-player-b":return "Dois jogadores · modo B";
            case "adventure-coop":return "Aventura cooperativa";
            case "championship-2p":return "Campeonato para dois";
            case "match-multitap":return "Partida em grupo";
            case "normal":return "Modo normal";
            case "vs-race":return "Corrida entre jogadores";
            default:return "Modo aprovado";
        }
    }
    private String roomSetupContext(){
        JSONObject snapshot=state.get();if(snapshot==null||room()!=null||selectedItem==null)return "";
        // Presence, chat and heartbeat revisions do not invalidate a verified game selection.
        return epoch+"/"+snapshot.optString("instance")+"/"+selectedItem+"/"+String.valueOf(snapshot.optJSONArray("engines"));
    }
    private void clearRoomSetup(){
        setupProfiles.clear();setupProfile=null;setupCapacity=0;setupContext="";
        if(createSetup!=null)createSetup.setVisibility(View.GONE);if(createOverview!=null)createOverview.setVisibility(View.VISIBLE);
    }
    private android.graphics.drawable.Drawable choiceFace(boolean selected){
        android.graphics.drawable.StateListDrawable states=new android.graphics.drawable.StateListDrawable();
        GradientDrawable focused=bg(selected?0xff1b3150:0xff151f2e,white);focused.setStroke(dp(2),white);
        states.addState(new int[]{-android.R.attr.state_enabled},bg(0xff101722,0xff223044));
        states.addState(new int[]{android.R.attr.state_pressed},bg(0xff315bab,white));
        states.addState(new int[]{android.R.attr.state_focused},focused);
        states.addState(new int[]{},bg(selected?0xff1b3150:0xff151f2e,selected?green:0xff304258));return new InsetDrawable(states,0,dp(8),0,dp(8));
    }
    private void applyChoiceFace(TextView option,boolean selected){
        option.setBackground(choiceFace(selected));
        // View.setBackground adopts drawable padding. Restore text clearance
        // afterwards, so subsequent snapshots do not collapse chip widths.
        option.setPadding(dp(12),0,dp(12),0);
    }
    private TextView setupChoice(LinearLayout parent,String label,boolean weighted,Runnable selected){
        TextView option=label(label,12,white);bold(option);option.setGravity(Gravity.CENTER);option.setPadding(dp(12),0,dp(12),0);
        option.setSingleLine(true);option.setFocusable(true);option.setClickable(true);
        option.setEllipsize(android.text.TextUtils.TruncateAt.END);
        LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(weighted?0:-2,-1,weighted?1:0);size.rightMargin=dp(5);parent.addView(option,size);
        option.setOnClickListener(v->{if(!busy&&!launching)selected.run();});return option;
    }
    private void showRoomSetup(java.util.List<StationMultiplayerProfile> profiles){
        clearRoomSetup();setupProfiles.addAll(profiles);setupContext=roomSetupContext();if(setupProfiles.isEmpty()||setupContext.isEmpty())return;
        setupModes.removeAllViews();setupModeLabels.clear();
        for(int i=0;i<setupProfiles.size();i++){
            final StationMultiplayerProfile profile=setupProfiles.get(i);String name=setupModeName(profile);int duplicates=0;
            for(StationMultiplayerProfile other:setupProfiles)if(name.equals(setupModeName(other)))duplicates++;
            String label=name+(duplicates>1?" · opção "+(i+1):"");
            TextView option=setupChoice(setupModes,label,false,()->selectRoomMode(profile));option.setContentDescription(label);setupModeLabels.add(option);
        }
        createOverview.setVisibility(View.GONE);createSetup.setVisibility(View.VISIBLE);selectRoomMode(setupProfiles.get(0));
    }
    private void selectRoomMode(StationMultiplayerProfile profile){
        if(!setupProfiles.contains(profile)||!setupContext.equals(roomSetupContext())){clearRoomSetup();showCreateMessage("A seleção mudou. Confira o jogo e escolha a partida novamente.",true);return;}
        int previous=setupCapacity;setupProfile=profile;setupCapacity=profile.permits(previous)?previous:profile.permits(2)?2:profile.allowed[0];
        setupCounts.removeAllViews();setupCountLabels.clear();
        for(int count:profile.allowed){TextView option=setupChoice(setupCounts,count+" jogadores",true,()->{setupCapacity=count;renderRoomSetup();});setupCountLabels.add(option);}
        renderRoomSetup();
    }
    private static String roomSetupDescription(StationMultiplayerProfile profile,int count){
        if(profile==null||!profile.permits(count))return "Escolha uma quantidade permitida para este modo.";
        StationGamePlayerInfo info=profileInfo(profile);StringBuilder detail=new StringBuilder();
        detail.append("Sala para ").append(count).append(" jogadores: você (P1) e ").append(count-1).append(count==2?" convidado.":" convidados.");
        detail.append("\n").append(setupModeName(profile)).append(". ");
        if(info.modeConfirmed)detail.append(info.participationLabel).append(". ");
        else detail.append("A forma de participação segue o modo selecionado no jogo. ");
        detail.append(info.controlsLabel).append(".");
        boolean explained=false;for(String instruction:profile.instructions){String guidance=playGuidance(instruction);if(!guidance.isEmpty()){detail.append("\n").append(guidance);explained=true;}}
        if(!explained&&"battle-single".equals(profile.mode)&&"snes-multitap-port2-v1".equals(profile.controllerProfile))detail.append("\nNo jogo, escolha Battle Game → Single Match e marque MAN nos ").append(count).append(" controles dos participantes.");
        else if(!explained&&"battle-team".equals(profile.mode))detail.append("\nConfigure os ").append(count).append(" participantes e as equipes no menu de batalha do jogo.");
        detail.append("\nTodos precisam da mesma edição instalada. Cada pessoa controla a própria posição.");return detail.toString();
    }
    private void renderRoomSetup(){
        if(setupProfile==null)return;
        for(int i=0;i<setupModeLabels.size();i++){TextView option=setupModeLabels.get(i);boolean selected=setupProfiles.get(i)==setupProfile;option.setTextColor(selected?green:muted);option.setSelected(selected);applyChoiceFace(option,selected);}
        for(int i=0;i<setupCountLabels.size();i++){TextView option=setupCountLabels.get(i);boolean selected=setupProfile.allowed[i]==setupCapacity;option.setTextColor(selected?green:muted);option.setSelected(selected);applyChoiceFace(option,selected);}
        setupDescription.setText(setupCapacity+" jogadores · "+setupModeName(setupProfile)+"\nToque para ver como jogar.");setupConfirm.setText("Criar sala");setupConfirm.setContentDescription("Criar sala para "+setupCapacity+" jogadores");updateRoomSetupEnabled();
    }
    private void updateRoomSetupEnabled(){
        if(setupConfirm==null)return;boolean enabled=!busy&&!launching&&setupProfile!=null&&setupProfile.permits(setupCapacity)&&setupContext.equals(roomSetupContext());
        setupConfirm.setEnabled(enabled);setupBack.setEnabled(!busy&&!launching);
        for(TextView option:setupModeLabels)option.setEnabled(!busy&&!launching);for(TextView option:setupCountLabels)option.setEnabled(!busy&&!launching);
    }
    private void confirmRoomSetup(){
        if(busy||launching||!active||setupProfile==null)return;
        if(!setupContext.equals(roomSetupContext())||!setupProfile.permits(setupCapacity)){clearRoomSetup();showCreateMessage("A seleção mudou. Confira novamente o jogo e os participantes.",true);return;}
        prepareRoom(setupProfile,setupCapacity,setupContext);
    }
    private void createRoom(){
        if(busy||launching||!active||client==null||state.get()==null)return;
        if(selectedItem==null){showCreateMessage("Escolha um jogo antes de criar a sala.",true);return;}
        if(room()!=null){showCreateMessage("Saia da sala atual antes de criar outra.",true);return;}
        final String item=selectedItem,context=roomSetupContext();final java.util.List<StationMultiplayerProfile> modes=new ArrayList<>();
        action(cancel->{modes.addAll(StationOnlineGame.profiles(this,client,item,cancel));if(modes.isEmpty())throw StationMultiplayerProfile.unavailable();return client.compose(null);},()->{
            if(!item.equals(selectedItem)||!active||section!=2||!context.equals(roomSetupContext()))return;
            showCreateMessage("",false);showRoomSetup(modes);
        });
    }
    private static boolean sameRoomSetupProfile(StationMultiplayerProfile chosen,StationMultiplayerProfile verified){
        return chosen!=null&&verified!=null&&chosen.itemId.equals(verified.itemId)&&chosen.contentSha256.equals(verified.contentSha256)
                &&chosen.engineId.equals(verified.engineId)&&chosen.coreSha256.equals(verified.coreSha256)&&chosen.runtimeSha256.equals(verified.runtimeSha256)
                &&chosen.profileId.equals(verified.profileId)&&chosen.profileSha256.equals(verified.profileSha256)
                &&chosen.mode.equals(verified.mode)&&chosen.controllerProfile.equals(verified.controllerProfile)
                &&chosen.maximumPlayers==verified.maximumPlayers&&java.util.Arrays.equals(chosen.allowed,verified.allowed);
    }
    private void prepareRoom(StationMultiplayerProfile chosen,int capacity,String context){
        if(busy||launching||!active||client==null||state.get()==null)return;
        if(selectedItem==null||room()!=null||!context.equals(roomSetupContext())||!chosen.permits(capacity))return;
        final String requested=selectedItem;creating=true;choose.setEnabled(false);create.setText("Conferindo…");prepared=null;
        setupConfirm.setText("Conferindo…");setupDescription.setText("Conferindo a edição, o modo e os "+capacity+" jogadores selecionados…");
        action(cancel->{prepared=StationOnlineGame.prepare(this,client,requested,state.get(),cancel,chosen.profileId);return client.compose(null);},()->{
            creating=false;choose.setEnabled(true);create.setText("Criar sala");
            StationOnlineGame game=prepared;
            if(game==null||!requested.equals(selectedItem)||!context.equals(roomSetupContext())||setupProfile!=chosen||setupCapacity!=capacity){clearRoomSetup();showCreateMessage("A seleção mudou. Confira novamente o jogo e os participantes.",true);return;}
            StationMultiplayerProfile verified=game.multiplayerProfile;
            if(!sameRoomSetupProfile(chosen,verified)||!verified.permits(capacity)){
                clearRoomSetup();showCreateMessage("As opções desta partida foram atualizadas. Escolha novamente o modo e os jogadores.",true);return;
            }
            clearRoomSetup();createVerifiedRoom(game,capacity);
        });
    }
    private void createVerifiedRoom(StationOnlineGame game,int capacity){
        if(busy||launching||!active||!game.itemId.equals(selectedItem)||!game.multiplayerProfile.permits(capacity))return;
        creating=true;choose.setEnabled(false);create.setText("Criando…");showCreateMessage("Confirmando sua sala…",false);
        action(cancel->{JSONObject response=client.call(game.fields(StationOnlineClient.command("create")).put("capacity",capacity),false,cancel);
            if(!StationRoomCreation.confirmed(response,game.itemId))throw new StationOnlineGame.Unavailable("A criação da sala não foi confirmada. Reconecte para conferir.");
            game.verifyRoom(response.getJSONObject("room"));prepared=game;return response;
        },()->{creating=false;choose.setEnabled(true);create.setText("Criar sala");conversationPeer="";showCreateMessage("",false);navigate(0);});
    }
    private void join(String roomId,String itemId){
        if(busy||launching)return;JSONObject snapshot=state.get(),mine=snapshot==null?null:snapshot.optJSONObject("room");
        JSONObject target=findRoom(snapshot,roomId);if(target==null){status.setText("A sala mudou. Atualize a lista antes de entrar.");return;}
        if(mine==null){confirmWithCover("Entrar nesta sala?",roomExplanation(target),"Aceitar e entrar",()->joinConfirmed(roomId,itemId,null,target.optLong("generation"),target.optString("profileId")),itemId);return;}
        if(roomId.equals(mine.optString("roomId"))){status.setText("Você já está nesta sala. Marque Estou pronto para confirmar sua participação.");return;}
        if(!StationPlayerModel.soloWaitingRoom(snapshot)){status.setText("Saia da sala atual antes de entrar em outra.");return;}
        final String previous=mine.optString("roomId");
        confirmWithCover("Entrar na outra sala?","Você está sozinho na sua sala. Ela será encerrada para você entrar na sala de outro jogador. Estou pronto confirma a participação; não muda de sala.\n\n"+roomExplanation(target),"Sair e entrar",()->joinConfirmed(roomId,itemId,previous,target.optLong("generation"),target.optString("profileId")),itemId);
    }
    private void joinConfirmed(String roomId,String itemId,String previous,long confirmedGeneration,String confirmedProfile){
        status.setText("Conferindo se os jogos são idênticos…");final int generation=epoch;
        action(cancel->{
            // Prepare before leaving: a missing local game must preserve the current room.
            StationOnlineGame game=StationOnlineGame.prepare(this,client,itemId,state.get(),cancel,confirmedProfile);
            JSONObject target=client.multiplayerRoom(roomId);if(target==null||target.optLong("generation")!=confirmedGeneration||!confirmedProfile.equals(target.optString("profileId")))throw new StationOnlineGame.Unavailable("A sala mudou. Confira novamente as vagas e o modo.");game.verifyRoom(target);
            JSONObject current=state.get(),mine=current==null?null:current.optJSONObject("room");
            if(mine!=null){
                if(previous==null||!previous.equals(mine.optString("roomId"))||!StationPlayerModel.soloWaitingRoom(current))
                    throw new StationOnlineGame.Unavailable("Sua sala mudou. Atualize a lista antes de entrar em outra.");
                JSONObject left=client.call(StationOnlineClient.command("leave").put("roomId",previous),false,cancel);
                prepared=null;deliver(left,generation);
                if(left.optJSONObject("room")!=null)throw new java.io.IOException("Room leave not acknowledged");
            }
            prepared=game;JSONObject joined=client.call(game.fields(StationOnlineClient.command("join").put("roomId",roomId).put("generation",confirmedGeneration)),false,cancel);
            JSONObject actual=joined.optJSONObject("room");
            if(actual==null||!roomId.equals(actual.optString("roomId"))||!StationPlayerModel.member(actual,joined.optString("selfId")))
                throw new java.io.IOException("Room join not acknowledged");
            game.verifyRoom(actual);return joined;
        },()->{if(playerSheet!=null)playerSheet.dismiss();});
    }
    private void command(String action,String key,Object value){
        final JSONObject displayed=room();final String target=displayed==null?"":displayed.optString("roomId");final long generation=displayed==null?0:displayed.optLong("generation");
        action(cancel->{JSONObject c=StationOnlineClient.command(action);if(key!=null)c.put(key,value);if(!target.isEmpty()){c.put("roomId",target);if("station-stream.v3".equals(displayed.optString("recoveryProtocol")))c.put("generation",generation);}return client.call(c,false,cancel);});
    }
    private void sendChat(){
        String value=chat.getText().toString().trim(),peer=conversationPeer;JSONObject mine=room();if(value.isEmpty()||busy)return;
        if(peer.isEmpty()&&mine==null){status.setText("Escolha uma pessoa ou entre em uma sala.");return;}
        if(!peer.isEmpty()&&!StationSocial.supports(state.get(),"direct-chat-v1")){status.setText("A conversa privada ainda não está disponível nesta sessão.");return;}
        final String targetRoom=mine==null?"":mine.optString("roomId");
        action(cancel->{JSONObject request=StationOnlineClient.command(peer.isEmpty()?"chat":"direct-chat").put("text",value);if(peer.isEmpty())request.put("roomId",targetRoom);else request.put("peerId",peer);return client.call(request,false,cancel);},()->{if(conversationPeer.equals(peer)&&chat.getText().toString().trim().equals(value))chat.setText("");drafts.remove(peer);renderConversation(state.get());});
    }
    private String nickname(JSONObject snapshot,String id){return roster.resolveName(snapshot,id);}
    /** Room membership comes from the signed room, never from the visible people page. */
    private void renderParticipants(LinearLayout parent,JSONObject snapshot){
        parent.removeAllViews();LinearLayout line=row();line.setGravity(Gravity.TOP);parent.addView(line,new LinearLayout.LayoutParams(-1,-2));
        java.util.List<StationRoomRoster.Row> members=roster.rows(snapshot);
        for(int i=0;i<members.size();i++){
            if(i>0&&i%2==0){line=row();line.setGravity(Gravity.TOP);parent.addView(line,new LinearLayout.LayoutParams(-1,-2));}
            StationRoomRoster.Row member=members.get(i);LinearLayout column=vertical();column.setPadding(0,dp(2),0,dp(2));
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,-2,1);cp.leftMargin=i%2==0?0:dp(12);line.addView(column,cp);
            TextView role=text(column,"P"+member.position+" · "+(member.occupied?(member.host?"ANFITRIÃO":"CONVIDADO")+(member.self?" · VOCÊ":""):"VAGA DISPONÍVEL"),9,muted);role.setLetterSpacing(.04f);role.setPadding(0,0,0,dp(2));
            TextView name=text(column,member.name,14,white);bold(name);name.setMaxLines(2);name.setEllipsize(android.text.TextUtils.TruncateAt.END);name.setPadding(0,0,0,dp(2));
            name.setContentDescription(member.occupied?"Participante: "+member.name:"Aguardando outro jogador");
            String readiness=!member.occupied?"Aguardando convite":member.ready?"Pronto":"Ainda não confirmou";
            TextView badge=text(column,readiness,10,member.ready?0xff78deaf:0xffe5c477);badge.setPadding(0,0,0,0);badge.setSingleLine(true);badge.setEllipsize(android.text.TextUtils.TruncateAt.END);
            badge.setCompoundDrawablesWithIntrinsicBounds(new StationSocialIcon(member.ready?StationSocialIcon.READY:StationSocialIcon.PEOPLE,dp(13),member.ready?0xff78deaf:0xffe5c477),null,null,null);badge.setCompoundDrawablePadding(dp(4));
        }
    }

    private void paint(JSONObject snapshot){
        JSONObject latest=state.get();if(latest==null||snapshot.optLong("revision")<latest.optLong("revision")||snapshot.optInt("peerPage",snapshot.optInt("page"))!=page||snapshot.optInt("roomPage",snapshot.optInt("page"))!=roomPage)return;
        if(snapshot.optLong("revision")==painted&&page==paintedPage&&roomPage==paintedRoomPage)return;painted=snapshot.optLong("revision");paintedPage=page;paintedRoomPage=roomPage;
        roster.observe(snapshot);if(inviteNavigation!=null)inviteNavigation.setVisibility(client!=null&&client.multiplayerEnabled?View.GONE:View.VISIBLE);
        create.setEnabled(!busy&&!launching&&room()==null);setConnection("Online",true);status.setText(onlineNotice(feedback.text(snapshot,busy)));
        if(createSetup!=null&&createSetup.getVisibility()==View.VISIBLE&&!setupContext.equals(roomSetupContext())){clearRoomSetup();showCreateMessage("As opções da sala mudaram. Confira o jogo antes de criar.",true);}
        loadHero();
        int ry=roomScroll.getScrollY(),py=peerScroll.getScrollY();beginRoomRows();renderPlayers(snapshot);refreshPlayerSheet();
        JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");roomTitle.setText("SALAS  ·  "+snapshot.optInt("totalRooms"));
        JSONArray inv=snapshot.optJSONArray("invites");if(inv!=null)for(int i=0;i<inv.length();i++){JSONObject v=inv.optJSONObject(i);if(v==null)continue;LinearLayout c=roomCoverCard("invite",v.optString("inviteId"),v.optString("itemId"),false);bold(text(c,"CONVITE RECEBIDO",10,green));text(c,nickname(snapshot,v.optString("fromPeerId"))+"  ·  "+client.name(v.optString("itemId")),14,white);addSynopsis(c,v.optString("itemId"),2,"Todos precisam da mesma edição do jogo.");button(c,"Aceitar e entrar",()->{conversationPeer="";join(v.optString("roomId"),v.optString("itemId"));},true);button(c,"Agora não",()->command("dismiss-invite","text",v.optString("inviteId")),false);}
        JSONArray requests=snapshot.optJSONArray("joinRequests");if(requests!=null)for(int i=0;i<requests.length();i++){JSONObject r=requests.optJSONObject(i);if(r==null)continue;LinearLayout c=card(rooms);desiredRoomRows.add(c);bold(text(c,"PEDIDO PARA JOGAR",10,green));text(c,nickname(snapshot,r.optString("fromPeerId")),15,white);button(c,"Aceitar pedido",()->socialAction("accept-request",null,r.optString("requestId")),true);button(c,"Recusar",()->socialAction("dismiss-request",null,r.optString("requestId")),false);}
        if(mine!=null){
            LinearLayout current=roomCoverCard("own",mine.optString("roomId"),mine.optString("itemId"),true);
            LinearLayout heading=row();current.addView(heading,new LinearLayout.LayoutParams(-1,dp(20)));
            TextView caption=label("SUA SALA",10,green);bold(caption);caption.setLetterSpacing(.12f);heading.addView(caption,new LinearLayout.LayoutParams(0,-2,1));
            caption.setContentDescription("Sua sala. "+client.name(mine.optString("itemId"))+". Toque para ver os detalhes e como jogar.");caption.setOnClickListener(v->showGameDetails(mine.optString("itemId"),roomExplanation(mine)));
            TextView occupancy=text(current,roomInfo(mine,self).summary,11,green);occupancy.setPadding(0,0,0,dp(4));occupancy.setMaxLines(2);
            LinearLayout participants=vertical();current.addView(participants,new LinearLayout.LayoutParams(-1,-2));renderParticipants(participants,snapshot);
            JSONArray rd=mine.optJSONArray("ready");
            roomReadiness=text(current,"",11,muted);roomReadiness.setPadding(0,dp(4),0,dp(4));roomReadiness.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
            ownRoomGuide(current,mine);
            LinearLayout controls=roomControls(ownRoomFooter);
            if("waiting".equals(mine.optString("state"))){
                boolean isReady=contains(rd,self);
                ready=roomAction(controls,isReady?"Desmarcar":"Estou pronto",isReady?StationSocialIcon.NOT_READY:StationSocialIcon.READY,isReady?StationActionButton.SECONDARY:StationActionButton.PRIMARY,()->command("ready","value",!contains(rd,self)));
                ready.setContentDescription(isReady?"Desmarcar sua confirmação":"Confirmar que você está pronto para jogar");
            }
            final String displayedRoom=roomConfirmationKey(snapshot);
            if("waiting".equals(mine.optString("state"))&&self.equals(mine.optString("hostId")))start=roomAction(controls,"Iniciar",StationSocialIcon.PLAY,StationActionButton.PRIMARY,()->startRoom(displayedRoom));
            Button exit=roomAction(controls,"Sair",StationSocialIcon.EXIT,StationActionButton.DANGER,()->command("leave",null,null));
            exit.setContentDescription("Sair da sala atual");
            roomAction(controls,"Conversa",StationSocialIcon.CHAT,StationActionButton.SECONDARY,()->openConversation("",""));
            if(!"station-stream.v3".equals(mine.optString("recoveryProtocol"))&&StationPlayerModel.shareable(snapshot))roomAction(controls,"Convidar",StationSocialIcon.CODE,StationActionButton.SECONDARY,()->showRoomCode());
            if(StationLaunchPolicy.eligible(mine,self.equals(mine.optString("hostId")))){if(!launching&&StationLaunchPolicy.key(mine).equals(launchKey))roomAction(actionLine(ownRoomFooter),"Abrir partida",StationSocialIcon.PLAY,StationActionButton.PRIMARY,()->{launchKey="";launch(mine,snapshot);});else launch(mine,snapshot);}

        }
        JSONArray all=snapshot.optJSONArray("rooms");int count=0;
        for(int i=0;all!=null&&i<all.length();i++){JSONObject r=all.optJSONObject(i);if(r==null||mine!=null&&mine.optString("roomId").equals(r.optString("roomId")))continue;count++;LinearLayout c=roomCoverCard("room",r.optString("roomId"),r.optString("itemId"),false);bold(text(c,client.name(r.optString("itemId")),15,white));text(c,nickname(snapshot,r.optString("hostId"))+"  ·  "+roomInfo(r,self).summary,12,muted);addSynopsis(c,r.optString("itemId"),2,roomExplanation(r));StationGamePlayerInfo.RoomInfo seats=roomInfo(r,self);boolean available="station-stream.v3".equals(r.optString("recoveryProtocol"))?seats.confirmed&&seats.acceptingPlayers&&seats.vacancies>0:"waiting".equals(r.optString("state"))&&r.optInt("players")<r.optInt("capacity",r.optInt("maximumPlayers",2));if(available){boolean social=!"station-stream.v3".equals(r.optString("recoveryProtocol"))&&StationSocial.supports(snapshot,"join-request-v1");Button b=button(c,StationSocial.requested(snapshot,r.optString("roomId"))?"Pedido enviado":social?"Pedir para jogar":"Entrar na sala",()->{if(social)action(cancel->client.call(StationOnlineClient.command("request-join").put("roomId",r.getString("roomId")),false,cancel));else join(r.optString("roomId"),r.optString("itemId"));},true);b.setEnabled(!busy&&!StationSocial.requested(snapshot,r.optString("roomId")));}else text(c,"Partida em andamento ou sala completa",12,muted);}
        if(count==0&&mine==null&&(inv==null||inv.length()==0)){empty(rooms,"+","Ainda não há salas aqui","Crie a primeira sala ou procure pessoas online para combinar uma partida.");desiredRoomRows.add(rooms.getChildAt(rooms.getChildCount()-1));}
        if(snapshot.optInt("roomPage",snapshot.optInt("page"))>0)desiredRoomRows.add(button(rooms,"← Página anterior",()->pageRooms(-1),false));if(!snapshot.isNull("nextRoomPage"))desiredRoomRows.add(button(rooms,"Mais salas →",()->pageRooms(1),false));
        reconcileRoomRows();
        JSONArray direct=snapshot.optJSONArray("directMessages");if(direct!=null)for(int i=0;i<direct.length();i++){JSONObject m=direct.optJSONObject(i);if(m==null||!self.equals(m.optString("toPeerId")))continue;String mid=m.optString("messageId");if(!seenMessages.contains(mid)&&!conversationPeer.equals(m.optString("fromPeerId"))){pendingPeer=m.optString("fromPeerId");pendingName=m.optString("nickname","Jogador");}seenMessages.add(mid);while(seenMessages.size()>128)seenMessages.remove(seenMessages.iterator().next());}
        renderConversation(snapshot);updateStartState();roomLayout(mine!=null);peerScroll.post(()->peerScroll.scrollTo(0,py));roomScroll.post(()->roomScroll.scrollTo(0,ry));
    }
    private void socialAction(String action,String peer,String text){action(cancel->{JSONObject c=StationOnlineClient.command(action);if(peer!=null)c.put("peerId",peer);if(text!=null)c.put("text",text);return client.call(c,false,cancel);});}
    private void openConversation(String id,String name){
        drafts.put(conversationPeer,chat.getText().toString());conversationPeer=id;conversationName=name;lastMessageId="";if(id.equals(pendingPeer)){pendingPeer="";pendingName="";}chat.setText(drafts.containsKey(id)?drafts.get(id):"");if(playerSheet!=null)playerSheet.dismiss();section=3;if(state.get()!=null)renderConversation(state.get());roomLayout(room()!=null);
    }
    private void renderConversation(JSONObject snapshot){
        inboxNotice.setText(pendingName+" • nova mensagem  ›");inboxNotice.setVisibility(pendingPeer.isEmpty()?View.GONE:View.VISIBLE);navChat.setText(pendingPeer.isEmpty()?"Conversas":"Nova mensagem");
        int cy=chatScroll.getScrollY();boolean atBottom=messages.getHeight()-chatScroll.getHeight()-cy<dp(64);messages.removeAllViews();chatActions.removeAllViews();JSONObject mine=snapshot.optJSONObject("room");String self=snapshot.optString("selfId");JSONArray list=null;
        if(!conversationPeer.isEmpty()){
            JSONObject peer=StationPlayerModel.peer(snapshot,conversationPeer);if(peer!=null)conversationName=peer.optString("nickname","Jogador");chatTitle.setText(conversationName);chatHint.setText(peer==null?"Presença não confirmada nesta página":"in-room".equals(peer.optString("status"))?"Em uma sala":"Online no aplicativo");
            inline(chatActions,"Perfil / convite",145,()->showPlayer(conversationPeer,conversationName),false);
            boolean enabled=StationSocial.supports(snapshot,"direct-chat-v1");composer(enabled&&!busy);chat.setHint(enabled?"Mensagem privada…":"Conversa privada aguardando ativação");list=StationSocial.messages(snapshot,conversationPeer);if(section==3)for(int i=0;i<list.length();i++){JSONObject m=list.optJSONObject(i);if(m!=null&&self.equals(m.optString("toPeerId")))StationPresence.markRead(m.optString("messageId"));}
            if(!enabled)empty(messages,"…","Conversa privada em preparação","Combine a partida pela conversa da sala enquanto esta opção não estiver disponível.");
            else if(list.length()==0)empty(messages,"…","Comece a conversa","Combine um jogo com "+conversationName+". As mensagens ficam disponíveis enquanto a presença estiver ativa.");
        }else if(mine!=null){chatTitle.setText("Conversa da sala");chatHint.setText(client.name(mine.optString("itemId")));list=mine.optJSONArray("messages");composer(!busy);if(list==null||list.length()==0)empty(messages,"…","Diga olá","Combine a partida com os participantes da sala.");}
        else{chatTitle.setText("Suas conversas");chatHint.setText("Pessoas online · convites · partidas");composer(false);empty(messages,"…","Jogue junto","Abra Pessoas online e toque em um nome para conversar ou convidar.");}
        for(int i=0;list!=null&&i<list.length();i++){JSONObject m=list.optJSONObject(i);if(m==null)continue;boolean own=self.equals(m.optString("fromPeerId"));LinearLayout bubble=card(messages);LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)bubble.getLayoutParams();lp.setMargins(own?dp(30):0,dp(3),own?0:dp(30),dp(7));bubble.setLayoutParams(lp);bubble.setBackground(bg(own?0xff123c55:0xff17253b,own?0xff245777:0xff2d405b));bold(text(bubble,own?"Você":m.optString("nickname","Jogador"),11,own?green:0xffa4c8e1));TextView value=text(bubble,m.optString("text"),14,white);value.setTextIsSelectable(true);value.setLineSpacing(dp(2),1);String utc=m.optString("utc");String time="";try{time=(m.has("utcMs")?java.time.Instant.ofEpochMilli(m.getLong("utcMs")).atZone(java.time.ZoneId.systemDefault()):java.time.OffsetDateTime.parse(utc).atZoneSameInstant(java.time.ZoneId.systemDefault())).format(java.time.format.DateTimeFormatter.ofPattern("HH:mm"));}catch(Exception ignored){}TextView stamp=text(bubble,time,10,muted);stamp.setGravity(Gravity.RIGHT);}
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
            line.setBackground(new RippleDrawable(ColorStateList.valueOf(0x327ad9f1),base,null));
            line.setFocusable(true);line.setClickable(true);line.setContentDescription(name+(own?", você":available?", disponível":inRoom?", em uma sala":", status não informado")+", abrir perfil");
            TextView dot=label("●",9,available?green:inRoom?0xffd7b877:muted);dot.setGravity(Gravity.CENTER);line.addView(dot,new LinearLayout.LayoutParams(dp(20),-1));
            TextView n=label(name,14,white);n.setSingleLine(true);n.setEllipsize(android.text.TextUtils.TruncateAt.END);line.addView(n,new LinearLayout.LayoutParams(0,-2,1));
            TextView tail=label(own?"você":"›",own?10:22,muted);tail.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);line.addView(tail,new LinearLayout.LayoutParams(dp(38),-1));
            peers.addView(line,new LinearLayout.LayoutParams(-1,dp(48)));line.setOnClickListener(v->{if(!own)openConversation(id,name);else showPlayer(id,name);});
            View separator=new View(this);separator.setBackgroundColor(0xff24354d);peers.addView(separator,new LinearLayout.LayoutParams(-1,dp(1)));
        }
        if(shown==0){TextView empty=text(peers,filter.isEmpty()?"Nenhum jogador nesta página.":"Nenhum nome encontrado nesta página.",12,muted);empty.setPadding(dp(8),dp(18),dp(8),dp(18));}
        if(snapshot.optInt("peerPage",snapshot.optInt("page"))>0)button(peers,"← Página anterior",()->pagePeers(-1),false);
        if(!snapshot.isNull("nextPeerPage"))button(peers,"Próxima página →",()->pagePeers(1),false);
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
        playerSheet.render(model,model.roomItemId.isEmpty()?"":client.name(model.roomItemId),item==null?"Jogo não selecionado":client.name(item),busy,peerFeedback,StationSocial.supports(state.get(),"join-request-v1"));String coverItem=model.roomItemId.isEmpty()?selectedItem:model.roomItemId;StationPlayerSheet sheet=playerSheet;
        if(coverItem==null||coverItem.isEmpty()){sheet.coverItem="";sheet.setCover(null);}
        else if(!coverItem.equals(sheet.coverItem)){sheet.coverItem=coverItem;sheet.setCover(null);artwork.load(coverItem,256,bitmap->{if(sheet==playerSheet&&coverItem.equals(sheet.coverItem))sheet.setCover(bitmap);});}
    }
    private void invitePlayer(String id){
        if(client!=null&&client.multiplayerEnabled){status.setText("Converse com o jogador e peça para entrar pela lista de salas. O convite desta modalidade ainda está em preparação.");return;}
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
        confirmWithCover("Bloquear "+name+"?","Oculta este jogador enquanto estiver online e encerra uma sala compartilhada.","Bloquear",()->{if(playerSheet!=null)playerSheet.dismiss();command("block","peerId",id);});
    }
    private String currentCoverItem(){JSONObject own=room();return section==2||own==null?selectedItem:own.optString("itemId",selectedItem);}
    private LinearLayout codePanel(String heading,String detail){return codePanel(heading,detail,currentCoverItem());}
    private LinearLayout codePanel(String heading,String detail,String item){return codePanel(heading,detail,item,false);}
    private LinearLayout codePanel(String heading,String detail,String item,boolean frameless){
        if(codeDialog!=null)codeDialog.dismiss();codeDialog=new Dialog(this);codeDialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        StationFlowPanel flow=new StationFlowPanel(this);if(frameless)flow.setBackgroundColor(0xff101722);else flow.setBackground(bg(0xff101722,0xff304258));LinearLayout outer=flow.content;
        flow.setPlatform(coverPlatform(item));
        if(item!=null){String game=client==null?"jogo selecionado":client.name(item);artwork.loadHero(item,1536,bitmap->flow.setCover(bitmap,game));}
        if(!frameless){TextView brand=text(outer,"TURBOSTATIONS  /  JOGAR ONLINE",10,green);brand.setLetterSpacing(.1f);bold(brand);}
        TextView title=text(outer,heading,frameless?18:22,white);bold(title);text(outer,detail,12,muted);if(item!=null&&!frameless)addSynopsis(outer,item,2,detail);
        codeDialog.setContentView(flow);return outer;
    }
    private void displayCodePanel(){
        codeDialog.show();Window w=codeDialog.getWindow();if(w==null)return;
        w.setBackgroundDrawableResource(android.R.color.transparent);w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        WindowManager.LayoutParams p=w.getAttributes();p.width=Math.min(dp(740),getResources().getDisplayMetrics().widthPixels-dp(24));p.height=Math.min(dp(440),getResources().getDisplayMetrics().heightPixels-dp(24));p.dimAmount=.72f;p.gravity=Gravity.CENTER;w.setAttributes(p);w.getDecorView().setSystemUiVisibility(getWindow().getDecorView().getSystemUiVisibility());
        w.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
    }
    private void showRoomCode(){
        if(room()!=null&&"station-stream.v3".equals(room().optString("recoveryProtocol"))){status.setText("Entre nesta partida pela lista de salas. O código desta modalidade ainda está em preparação.");return;}
        JSONObject snapshot=state.get();if(!StationPlayerModel.shareable(snapshot)){peerFeedback="O código está disponível quando sua sala tem uma vaga e aguarda jogadores.";refreshPlayerSheet();status.setText(peerFeedback);return;}
        JSONObject mine=snapshot.optJSONObject("room");final String code;
        try{code=mine.has("inviteCode")?StationInvitationCode.display(mine.optString("inviteCode")):StationInvitationCode.encode(snapshot.optString("instance"),mine.optString("roomId"),mine.optString("itemId"));}catch(IllegalArgumentException e){status.setText(e.getMessage());return;}
        LinearLayout panel=codePanel("Código da sua sala",client.name(mine.optString("itemId"))+"\nCompartilhe com outro jogador. "+(code.startsWith("TS1:")?"Ele cola o convite em Código de convite.":"Ele digita ou cola os 8 caracteres em Código de convite.")+" A senha da partida é automática após atualizar o app.");
        TextView value=text(panel,code,code.startsWith("TS1:")?12:26,white);value.setTypeface(Typeface.MONOSPACE);value.setTextIsSelectable(true);value.setPadding(dp(12),dp(12),dp(12),dp(12));value.setBackground(bg(0xff071223,0xff2c4664));
        text(panel,"Válido enquanto esta sala existir e tiver uma vaga. O outro jogador precisa da mesma edição instalada.",11,muted);
        Button copy=button(panel,"Copiar código",()->{android.content.ClipboardManager clipboard=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(clipboard!=null){clipboard.setPrimaryClip(ClipData.newPlainText("Convite TurboStations",code));Toast.makeText(this,"Código copiado",Toast.LENGTH_SHORT).show();}},true);
        compactCreateAction(copy);compactCreateAction(button(panel,"Fechar",()->codeDialog.dismiss(),false));displayCodePanel();
    }
    private void enterCodeDialog(){
        if(busy)return;LinearLayout panel=codePanel("Entrar por código","Digite ou cole o convite de 8 caracteres. Convites antigos também são aceitos.");
        EditText input=new EditText(this);field(input,"7KPM-4XRT");input.setSingleLine(true);input.setTextSize(12);input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(160)});input.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);panel.addView(input,new LinearLayout.LayoutParams(-1,dp(48)));
        TextView error=text(panel,"",12,0xffefad98);error.setVisibility(View.GONE);error.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        Button joinCode=button(panel,"Entrar na sala",()->{
            JSONObject snapshot=state.get();
            try{
                if(busy)throw new IllegalArgumentException("Aguarde a ação atual terminar.");
                if(snapshot==null||!active)throw new IllegalArgumentException("Conecte-se ao lobby antes de entrar.");
                if(snapshot.optJSONObject("room")!=null)throw new IllegalArgumentException("Saia da sala atual antes de usar outro código.");
                StationInvitationCode parsed=StationInvitationCode.parse(input.getText().toString());
                if(!parsed.shortCode.isEmpty()){
                    if(!supportsShortInvite(snapshot))throw new IllegalArgumentException("Os convites curtos ainda não estão disponíveis nesta sessão.");
                    codeDialog.dismiss();joinCode(parsed.shortCode);
                }else{
                    if(!parsed.instance.equals(snapshot.optString("instance")))throw new IllegalArgumentException("Este código expirou após a atualização das salas. Peça um novo convite.");
                    codeDialog.dismiss();join(parsed.roomId,parsed.itemId);
                }
            }catch(IllegalArgumentException e){error.setText(e.getMessage());error.setVisibility(View.VISIBLE);}
        },true);
        compactCreateAction(joinCode);compactCreateAction(button(panel,"Cancelar",()->codeDialog.dismiss(),false));displayCodePanel();
    }

    private static boolean supportsShortInvite(JSONObject snapshot){
        JSONArray caps=snapshot.optJSONArray("roomCapabilities");
        for(int i=0;caps!=null&&i<caps.length();i++)if("short-invite-v1".equals(caps.optString(i)))return true;
        return false;
    }
    private void joinCode(String code){
        status.setText("Localizando a sala…");final int generation=epoch;
        action(cancel->{
            if(room()!=null)throw new StationOnlineGame.Unavailable("Saia da sala atual antes de usar outro convite.");
            JSONObject resolved=client.call(StationOnlineClient.command("resolve-code").put("inviteCode",code),false,cancel);
            JSONObject target=resolved.getJSONObject("resolvedRoom");
            String roomId=target.getString("roomId"),itemId=target.getString("itemId");
            // Validate the signed locator before preparing local files or joining.
            StationInvitationCode.encode(resolved.getString("instance"),roomId,itemId);
            runOnUiThread(()->{if(active&&epoch==generation){selectedItem=itemId;subtitle.setText(client.name(itemId));loadHero();}});
            StationOnlineGame game=StationOnlineGame.prepare(this,client,itemId,resolved,cancel);
            JSONObject joined=client.call(game.fields(StationOnlineClient.command("join").put("roomId",roomId)),false,cancel);
            JSONObject actual=joined.optJSONObject("room");
            if(actual==null||!roomId.equals(actual.optString("roomId"))||!StationPlayerModel.member(actual,joined.optString("selfId")))throw new java.io.IOException("Room join not acknowledged");
            game.verifyRoom(actual);prepared=game;return joined;
        },()->{if(playerSheet!=null)playerSheet.dismiss();conversationPeer="";navigate(0);});
    }

    private void styleNavigation(Button button,boolean selected){
        button.setBackgroundTintList(null);
        ((StationActionButton)button).setNavigationSelected(selected);
    }
    private void roomLayout(boolean joined){
        if(joined){middlePanel.setBackgroundColor(android.graphics.Color.TRANSPARENT);middlePanel.setPadding(0,0,0,0);}
        else{middlePanel.setBackgroundColor(android.graphics.Color.TRANSPARENT);middlePanel.setPadding(dp(6),0,dp(6),0);}
        navRooms.setText(joined?"Sua sala":"Salas");
        leftPanel.setVisibility(section==1?View.VISIBLE:View.GONE);middlePanel.setVisibility(section==0?View.VISIBLE:View.GONE);createPanel.setVisibility(section==2?View.VISIBLE:View.GONE);
        rightPanel.setVisibility(section==3?View.VISIBLE:View.GONE);
        styleNavigation(navRooms,section==0);styleNavigation(navPeople,section==1);styleNavigation(navCreate,section==2);styleNavigation(navChat,section==3);
        if(createGame!=null){createGame.setText(selectedItem==null?"Jogo não selecionado":client==null?"Carregando jogo…":client.name(selectedItem));createCard.setGameName(createGame.getText().toString());}
    }
    private void loadHero(){
        JSONObject ownRoom=room();final String target=section==2||ownRoom==null?selectedItem:ownRoom.optString("itemId",selectedItem);
        if(client==null||target==null||target.isEmpty())return;
        if(target.equals(heroRequestId)&&heroEpoch==epoch){loadHeroProfile(target);return;}
        heroRequestId=target;heroEpoch=epoch;final int generation=epoch;
        heroSynopsis=synopsisFor(target);if(createSynopsis!=null)createSynopsis.setText(heroSynopsis);
        heroFactSummary="";heroFactDetail="";heroOnlineDetail="";heroOnlinePlayers="";headerRating.setRating(-1);headerPlayers.setText("Jogadores a confirmar");if(createInfo!=null)createInfo.setText(StationGamePlayerInfo.pending().detail);gamePlatform.setText("");clearHeroCover();heroSymbol.setVisibility(View.VISIBLE);
        artwork.loadHero(target,1536,bitmap->{if(active&&generation==epoch&&target.equals(heroRequestId)&&!isDestroyed()){heroBitmap=bitmap;bindHeroCover();heroSymbol.setVisibility(bitmap==null?View.VISIBLE:View.GONE);}});
        commands.execute(()->{
            try{
                StationAndroid app=StationAndroid.get(this);StationCoordinator.Library library=app.coordinator.current();StationCatalog.Item item=library==null?null:library.catalog.find(target);if(item==null)return;
                String name=item.name,platform=item.platform;
                final StationGamePlayerFacts.Fact facts=StationGamePlayerFacts.forItem(item);
                runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)){subtitle.setText(name);gamePlatform.setText(platform);heroFactSummary=facts==null?"":facts.summary;heroFactDetail=facts==null?"":facts.detail;renderHeroPlayerInfo();}});
                if(headerMetadata==null)try(java.io.InputStream in=getAssets().open("station-ui-r43/game-metadata.json")){headerMetadata=new JSONObject(new String(StationOnlineGame.read(in,512*1024),java.nio.charset.StandardCharsets.UTF_8));}
                final StationHeaderMetadata details=StationHeaderMetadata.lookup(headerMetadata,item.itemId,item.players);
                runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)){headerRating.setRating(details.rating);}});
            }catch(Exception unavailable){android.util.Log.i("StationOnline","Selected game metadata unavailable");}
        });
        loadHeroProfile(target);
    }
    private void renderHeroPlayerInfo(){
        String label=heroFactSummary.isEmpty()?(heroOnlinePlayers.isEmpty()?"Jogadores a confirmar":"Online: "+heroOnlinePlayers):heroFactSummary;
        headerPlayers.setText(label);headerPlayers.setContentDescription(label);
        String facts=playGuidance(heroFactDetail),online=heroOnlineDetail.isEmpty()?StationGamePlayerInfo.pending().detail:onlineNotice(heroOnlineDetail);
        if(createInfo!=null)createInfo.setText((facts.isEmpty()?"":facts+"\n\n")+"Online: "+online);
    }
    private void loadHeroProfile(final String target){
        if(client==null||!client.multiplayerEnabled||state.get()==null||(target.equals(profileRequestId)&&profileEpoch==epoch))return;
        profileRequestId=target;profileEpoch=epoch;final int generation=epoch;
        commands.execute(()->{
                StationApi.Cancellation check=new StationApi.Cancellation();requests.add(check);
                try{
                    java.util.List<StationMultiplayerProfile> profiles=StationOnlineGame.classifications(this,client,target,check);StringBuilder brief=new StringBuilder(),detail=new StringBuilder();java.util.SortedSet<Integer> counts=new java.util.TreeSet<>();
                    for(StationMultiplayerProfile p:profiles){StationGamePlayerInfo info=profileInfo(p);if(detail.length()>0)detail.append("\n");if(info.singlePlayerConfirmed)counts.add(1);for(int count:p.allowed)counts.add(count);detail.append(info.detail);}
                    brief.setLength(0);for(int count:counts){if(brief.length()>0)brief.append(", ");brief.append(count);}if(brief.length()>0)brief.append(counts.size()==1&&counts.contains(1)?" jogador":" jogadores").append(profiles.size()>1?" · "+profiles.size()+" modos":"");
                    final String b=brief.length()==0?StationGamePlayerInfo.pending().capacityLabel:brief.toString(),d=detail.length()==0?StationGamePlayerInfo.pending().detail:detail.toString();
                    runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)){heroOnlinePlayers=b;heroOnlineDetail=d;renderHeroPlayerInfo();}});
                }catch(Exception unavailable){if(!check.cancelled())recordFailure(unavailable);runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)){heroOnlineDetail=StationOnlineClient.message(unavailable);renderHeroPlayerInfo();}});}
                finally{requests.remove(check);}
        });
    }
    private static boolean contains(JSONArray a,String id){if(a!=null)for(int i=0;i<a.length();i++)if(id.equals(a.optString(i)))return true;return false;}
    private static JSONObject findRoom(JSONObject snapshot,String rid){JSONArray a=snapshot.optJSONArray("rooms");if(a!=null)for(int i=0;i<a.length();i++){JSONObject r=a.optJSONObject(i);if(r!=null&&rid.equals(r.optString("roomId")))return r;}return null;}
    private JSONObject readPoll(Work read,int generation,StationApi.Cancellation cancel)throws Exception{
        int failures=0;
        while(active&&epoch==generation){
            cancel.check();
            try{return read.run(cancel);}
            catch(Exception error){cancel.check();long delay=StationOnlineClient.pollRetryDelay(error,++failures);if(delay<0)throw error;Thread.sleep(delay);cancel.check();}
        }
        throw new java.io.InterruptedIOException("Read poll cancelled by lifecycle");
    }
    private void pagePeers(int delta){if(busy||client==null)return;page=Math.max(0,Math.min(40,page+delta));client.setPeerPage(page);if(!client.multiplayerEnabled){roomPage=page;client.setRoomPage(roomPage);}status.setText("Consultando esta página de pessoas…");int generation=epoch;action(cancel->readPoll(c->client.call(StationOnlineClient.command("heartbeat"),false,c),generation,cancel));}
    private void pageRooms(int delta){if(busy||client==null)return;roomPage=Math.max(0,Math.min(40,roomPage+delta));client.setRoomPage(roomPage);int generation=epoch;
        status.setText("Consultando esta página de salas…");
        if(client.multiplayerEnabled){stopMultiplayerPoll();scheduleMultiplayerPoll(client,generation,0,0);}
        else{page=roomPage;client.setPeerPage(page);action(cancel->readPoll(c->client.call(StationOnlineClient.command("heartbeat"),false,c),generation,cancel));}
    }
    private static String roomConfirmationKey(JSONObject snapshot){JSONObject room=snapshot==null?null:snapshot.optJSONObject("room");return room==null?"":snapshot.optString("instance")+"/"+room.optString("roomId")+"/"+room.optString("itemId")+"/"+room.optLong("generation")+"/"+room.optString("profileId")+"/"+room.optString("profileSha256")+"/"+room.optInt("capacity")+"/"+String.valueOf(room.optJSONArray("roster"))+"/"+room.optString("hostId")+"/"+room.optString("recoveryProtocol")+"/"+String.valueOf(room.optJSONArray("members"))+"/"+String.valueOf(room.optJSONArray("ready"));}
    private static boolean separateRoomNotice(String notice,String overall){
        return notice!=null&&!notice.trim().isEmpty()&&(overall==null||!notice.trim().equals(overall.trim()));
    }
    private void updateStartState(){
        JSONObject snapshot=state.get();String reason=StationRoomStartState.reason(snapshot);
        boolean allowed=!busy&&!launching&&reason.isEmpty();
        if(start!=null){start.setEnabled(allowed);start.setContentDescription("Iniciar partida"+(reason.isEmpty()?"":": "+reason));}
        if(roomReadiness!=null){String notice=busy?"Confirmando sua solicitação…":launching?"Preparando a partida…":reason;roomReadiness.setText(notice);roomReadiness.setVisibility(separateRoomNotice(notice,status==null?null:status.getText().toString())?View.VISIBLE:View.GONE);}
    }
    private void startRoom(final String displayedRoom){
        JSONObject snapshot=state.get();String reason=StationRoomStartState.reason(snapshot);
        if(!active||launching)return;
        if(busy||!reason.isEmpty()){feedback.fail(reason.isEmpty()?"Aguarde a solicitação atual terminar.":reason);status.setText(onlineNotice(feedback.text(state.get(),busy)));return;}
        if(!displayedRoom.equals(roomConfirmationKey(snapshot))){status.setText("A sala mudou. Confira os participantes antes de iniciar.");return;}

        JSONArray transports=snapshot==null?null:snapshot.optJSONArray("transports");
        if(!contains(transports,StationRoomStartState.transport(snapshot))){status.setText("A partida online ainda não está disponível nesta sessão. Aguarde a ativação desta opção; os jogos locais continuam disponíveis.");return;}
        action(cancel->{JSONObject latest=state.get();String changed=StationRoomStartState.reason(latest);if(!changed.isEmpty())throw new StationOnlineGame.Unavailable(changed);if(!displayedRoom.equals(roomConfirmationKey(latest)))throw new StationOnlineGame.Unavailable("A sala mudou. Confira os participantes antes de iniciar.");if(!contains(latest.optJSONArray("transports"),StationRoomStartState.transport(latest)))throw new StationOnlineGame.Unavailable("A conexão da sala aguarda ativação.");return client.call(StationOnlineClient.command("start").put("roomId",latest.getJSONObject("room").getString("roomId")).put("generation",latest.getJSONObject("room").optLong("generation")).put("transport",StationRoomStartState.transport(latest)),false,cancel);});
    }
    private void launch(JSONObject room,JSONObject snapshot){String key=StationLaunchPolicy.key(room);if(launching||nativeReturn.pending()||key.equals(launchKey))return;launchKey=key;launching=true;int generation=epoch;StationApi.Cancellation cancel=new StationApi.Cancellation();requests.add(cancel);status.setText("Conectando a partida online…");android.util.Log.i("StationRooms","launch stage=prepare room="+room.optString("roomId")+" generation="+room.optLong("generation")+" host="+snapshot.optString("selfId").equals(room.optString("hostId")));
        commands.execute(()->{try{StationOnlineGame game=prepared;if(game==null)game=StationOnlineGame.prepare(this,client,room.getString("itemId"),snapshot,cancel);JSONObject gameRoom=room;
            if("station-stream.v3".equals(room.optString("recoveryProtocol"))){
                game.verifyRoom(room);JSONArray links=room.getJSONArray("links"),launchLinks=new JSONArray();String self=snapshot.getString("selfId");boolean host=self.equals(room.getString("hostId"));
                for(int li=0;li<links.length();li++){JSONObject link=links.getJSONObject(li);if(!host&&!self.equals(link.getString("guestPeerId")))continue;
                    JSONObject result=client.multiplayer(game.fields(StationOnlineClient.command("ticket")).put("roomId",room.getString("roomId")).put("generation",room.getLong("generation")).put("linkId",link.getString("linkId")),cancel);
                    JSONObject actual=result.getJSONObject("room");game.verifyRoom(actual);if(actual.getLong("generation")!=room.getLong("generation"))throw new java.io.IOException("Generation changed");
                    JSONObject ticket=result.getJSONObject("ticket");StationMultiplayerSession.checkTicket(ticket,link.getString("linkId"));
                    launchLinks.put(new JSONObject(link.toString()).put("ticket",ticket));
                }
                gameRoom=new JSONObject(room.toString()).put("launchLinks",launchLinks);
            }else if("relay-wss-v1".equals(room.optString("transport"))||"relay-wss-v2".equals(room.optString("transport"))){JSONObject ticketRequest=StationOnlineClient.command("relay-ticket").put("roomId",room.getString("roomId"));if("relay-wss-v2".equals(room.optString("transport")))game.fields(ticketRequest).put("generation",room.getLong("generation"));JSONObject connection=client.call(ticketRequest,false,cancel);gameRoom=connection.getJSONObject("room");android.util.Log.i("StationRooms","launch stage=relay-ticket-received");}
            game.verifyRoom(gameRoom);final boolean systemN64=StationN64Launch.BACKEND.equals(game.backend),systemDolphin=StationDolphinLaunch.BACKEND.equals(game.backend);
            if("n64".equals(game.platform)&&!systemN64)throw new StationOnlineGame.Unavailable("Esta sala usa uma edição anterior. Atualize os participantes e crie uma nova sala para usar o emulador Nintendo 64 do aplicativo.");
            if(("gamecube".equals(game.platform)||"wii".equals(game.platform))&&!systemDolphin)throw new StationOnlineGame.Unavailable("Atualize os participantes e crie uma nova sala para usar o Dolphin do aplicativo.");
            String file=systemN64?StationN64Launch.prepare(this,game,gameRoom,snapshot,cancel):systemDolphin?StationDolphinLaunch.prepare(this,game,gameRoom,snapshot,cancel):StationRetroLaunch.prepare(this,game,gameRoom,snapshot,cancel);
            runOnUiThread(()->{if(active&&generation==epoch){returningFromGame=true;returningRecovery="relay-wss-v2".equals(room.optString("transport"))||"relay-wss-v3".equals(room.optString("transport"));Intent nativeIntent=null;try{nativeIntent=StationGameSession.attach(this,room,new Intent(this,systemN64?StationN64Activity.class:systemDolphin?StationDolphinActivity.class:StationRetroActivity.class).putExtra("station.launch",file));android.util.Log.i("StationRooms","launch stage=activity");startActivityForResult(nativeIntent,nativeReturn.prepare(nativeIntent,room.optString("roomId"),("station-stream.v2".equals(room.optString("recoveryProtocol"))||"station-stream.v3".equals(room.optString("recoveryProtocol")))?room.optLong("generation",-1):0));}catch(RuntimeException e){StationGameSession.discardLaunch(nativeIntent,room.optString("roomId"),("station-stream.v2".equals(room.optString("recoveryProtocol"))||"station-stream.v3".equals(room.optString("recoveryProtocol")))?room.optLong("generation",-1):0);nativeReturn.abort(nativeIntent);returningFromGame=false;discardPreparedLaunch(systemN64,systemDolphin,file);launchFailure(e,generation);}}else discardPreparedLaunch(systemN64,systemDolphin,file);});}catch(Exception e){launchFailure(e,generation);}finally{requests.remove(cancel);}});
    }
    private void discardPreparedLaunch(boolean n64,boolean dolphin,String file){if(n64)StationN64Launch.discard(this,file);else if(dolphin)StationDolphinLaunch.discard(this,file);else StationRetroLaunch.discard(this,file);}
    private void launchFailure(Throwable error,int generation){
        recordFailure(error);
        runOnUiThread(()->{if(active&&generation==epoch){launching=false;busy=false;feedback.fail(StationOnlineClient.message(error));painted=-1;JSONObject current=state.get();if(current!=null)paint(current);}});
    }
    private void exitRooms(){
        // Return never depends on network latency. Foreground presence completes explicit leave.
        JSONObject leaving=room();
        if(leaving!=null){
            android.content.SharedPreferences profile=getSharedPreferences("station-online-profile",0);
            if("station-stream.v3".equals(leaving.optString("recoveryProtocol"))){
                StationRoomLeaveIntent intent=StationRoomLeaveIntent.human(leaving.optString("roomId"),leaving.optLong("generation"),leaving.optString("recoveryProtocol"));
                synchronized(StationRoomLeaveIntent.class){if(!profile.edit().putString(StationRoomLeaveIntent.KEY,intent.encoded).remove("leaveOnCatalog").commit()){status.setText("Não foi possível registrar a saída. Tente novamente.");return;}}
            }else profile.edit().putBoolean("leaveOnCatalog",true).apply();
        }
        finish();
    }
    @Override public void onBackPressed(){if(section==3){navigate(1);return;}exitRooms();}
}
