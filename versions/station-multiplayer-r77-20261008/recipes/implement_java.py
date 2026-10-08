from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=Path(r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\compiled-final\java')
OUT=ROOT/'java'
N='netplay-src/org/emulationstation/frontend/netplay/'
C='client/src/java/org/emulationstation/frontend/station/'
def put(name,text):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8',newline='\n')
def base(name):return (BASE/name).read_text('utf8')
def change(text,old,new,count=1):
 assert text.count(old)==count,(old[:90],text.count(old),count)
 return text.replace(old,new)
# Add a fixed authenticated endpoint; the legacy endpoint and proof remain unchanged.
s=base(C+'StationApi.java')
s=change(s,'    public String profile(Session session,Cancellation cancel) throws Exception {','''    public JSONObject multiplayer(Session session,JSONObject request,Cancellation cancel)throws Exception {
        String id=string(request,"requestId");
        if(!id.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("Invalid multiplayer request");
        byte[] body=request.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
        if(body.length>8192)throw new IOException("Multiplayer request too large");
        JSONObject result=signed("POST","online/multiplayer/command",body,session,"TurboRamaStationAndroid/online/v1",524288,cancel);
        equal(result,"requestId",id);JSONObject snapshot=result.getJSONObject("snapshot");
        if(snapshot.getInt("schemaVersion")!=1||snapshot.getInt("multiplayerVersion")!=3||!"station-multiplayer.v3".equals(snapshot.getString("capability")))throw new IOException("Unsupported multiplayer snapshot");
        return snapshot;
    }
    public String multiplayerRelayRequestProof(Session session,String ticket)throws Exception {
        valid(session);token(ticket);
        if(session.proofMode.equals("none"))throw new IOException("Multiplayer request proof required");
        return requestProof(session,"GET",ROOT+"online/multiplayer/relay",null,ticket);
    }
    public String profile(Session session,Cancellation cancel) throws Exception {''')
put(C+'StationApi.java',s)
# v2 wire is retained byte-for-byte; v3 has a distinct protocol magic.
s=base(N+'StationRecoveryWire.java').replace('StationRecoveryWire','StationMultiplayerWire').replace('TSR2','TSR3').replace('0x54535232','0x54535233')
put(N+'StationMultiplayerWire.java',s)
# Retain R76 single-writer pump and bounded replay in each independent channel.
s=base(N+'StationRecoveryTunnel.java').replace('StationRecoveryTunnel','StationMultiplayerTunnel').replace('StationRecoveryWire','StationMultiplayerWire').replace('station-stream.v2','station-stream.v3').replace('/v1/station/online/relay','/v1/station/online/multiplayer/relay')
s=change(s,'    private void nativeInput(){try{','''    interface SocketBinding {boolean bind(int sourcePort);void release(int sourcePort);}
    private SocketBinding socketBinding;
    void socketBinding(SocketBinding value){if(startedTransport)throw new IllegalStateException("Started");socketBinding=value;}
    private Socket connectHost()throws Exception {
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(45);
        while(!closed.get()&&System.nanoTime()<deadline){
            Socket candidate=new Socket();local=candidate;int source=0;boolean bound=false,retained=false;
            try{
                candidate.bind(new InetSocketAddress(InetAddress.getByName("127.0.0.1"),0));source=candidate.getLocalPort();
                if(socketBinding==null||!socketBinding.bind(source))throw new IOException("SLOT_BINDING");bound=true;
                candidate.connect(new InetSocketAddress("127.0.0.1",hostPort),250);
                if(closed.get())throw new IOException("CLOSED");retained=true;return candidate;
            }catch(java.net.ConnectException|java.net.SocketTimeoutException retry){
                if(closed.get())throw retry;
            }finally{if(!retained){candidate.close();if(bound)socketBinding.release(source);}}
            nativeHint.tryAcquire(50,TimeUnit.MILLISECONDS);
        }
        throw new IOException("NATIVE_LISTENER");
    }
    private void nativeInput(){try{''')
s=change(s,'host?StationHostConnector.connect(hostPort,System.nanoTime()+TimeUnit.SECONDS.toNanos(45),closed::get,s->local=s,nativeHint):accept.accept()','host?connectHost():accept.accept()')
# Session.update acquires session -> gate. Never call its fatal callbacks with gate held.
s=change(s,'StationMultiplayerWire frame=null;boolean retry=false;long nativeState=', 'StationMultiplayerWire frame=null;boolean retry=false,protocolFailure=false;long nativeState=')
s=change(s,'if(nativeState>=0&&(nativeState&4)!=0){fatal("NATIVE_PROTOCOL");return;}\n                if(rx.delivered!=ackSent)', 'if(nativeState>=0&&(nativeState&4)!=0)protocolFailure=true;\n                else if(rx.delivered!=ackSent)')
s=change(s,'            if(retry){Thread.sleep(25);continue;}', '            if(protocolFailure){fatal(current,"NATIVE_PROTOCOL");return;}\n            if(retry){Thread.sleep(25);continue;}')
# TSR3 suspends an owner across attachments: HELLO alone cannot clear that state.
# Each newly authenticated Remote announces foreground through the same writer,
# after WELCOME and before PAUSED/READY. Failed sends retry via a fresh Remote.
s=change(s,'                else if(rx.delivered!=ackSent)', '                else if(foreground&&!current.foregroundAnnounced){current.foregroundAnnounced=true;frame=new StationMultiplayerWire(12,epoch,0);}\n                else if(rx.delivered!=ackSent)')
s=change(s,'    private final class Remote extends WebSocketClient {', '    private final class Remote extends WebSocketClient {\n        private boolean foregroundAnnounced; // guarded by gate; selected only by the single writer')
# Decide whether an error belongs to the live Remote atomically, then notify outside gate.
s=change(s,'    private void fatal(String category){long nowEpoch;boolean visible;Remote current;', '''    private void fatal(String category){fatal(null,category);}
    private void fatal(Remote source,String category){long nowEpoch;boolean visible;Remote current;''')
s=change(s,'synchronized(gate){if(terminal||closed.get())return;terminal=true;', 'synchronized(gate){if(terminal||closed.get()||(source!=null&&remote!=source))return;terminal=true;')
s=change(s,'if(!"station-stream.v3".equals(handshake.getFieldValue("Sec-WebSocket-Protocol"))){fatal("PROTOCOL");return;}', 'if(!"station-stream.v3".equals(handshake.getFieldValue("Sec-WebSocket-Protocol"))){fatal(this,"PROTOCOL");return;}')
s=change(s,'@Override public void onMessage(String text){fatal("PROTOCOL");}', '@Override public void onMessage(String text){fatal(this,"PROTOCOL");}')
s=change(s,'if(desiredState==3){fatal("SERVER_STATE");return;}', 'if(desiredState==3){fatal(this,"SERVER_STATE");return;}')
s=change(s,'}catch(Exception error){fatal("PROTOCOL");}}', '}catch(Exception error){fatal(this,"PROTOCOL");}}')
put(N+'StationMultiplayerTunnel.java',s)
# Fixed path derived from the pinned authority.
s=base(N+'StationRelayTls.java')
s=change(s,' static SSLSocketFactory create()throws Exception {',''' static URI multiplayerEndpoint()throws Exception {
  URI base=endpoint();return new URI("wss",null,base.getHost(),base.getPort(),"/v1/station/online/multiplayer/relay",null,null);
 }
 static SSLSocketFactory create()throws Exception {''')
put(N+'StationRelayTls.java',s)
print('API, v3 wire, independent tunnel and pinned TLS endpoint prepared')
# Client authority merges two independently signed snapshots after per-source revision checks.
s=base(N+'StationOnlineClient.java')
s=change(s,'    final StationAndroid app;volatile int page;','''    final StationAndroid app;volatile int page;
    volatile boolean multiplayerEnabled;private boolean multiplayerProbed;
    private JSONObject socialSnapshot,multiplayerSnapshot;private long combinedRevision;
    JSONObject multiplayer(JSONObject request,StationApi.Cancellation cancel)throws Exception {
        StationApi.Session session=null;
        try(StationSessions.Lease lease=app.sessions.acquire(cancel)){
            session=lease.session;JSONObject result=app.api.multiplayer(session,request,cancel);
            JSONObject ticket=result.optJSONObject("ticket");
            if(ticket!=null)ticket.put("requestProof",app.api.multiplayerRelayRequestProof(session,ticket.getString("ticket")));
            acceptMultiplayer(result);multiplayerEnabled=true;return result;
        }catch(StationApi.Failure e){if(session!=null&&e.sessionDenied())app.sessions.denied(session);throw e;}
    }
    JSONObject profileSnapshot(String item,StationApi.Cancellation cancel)throws Exception {
        try{return multiplayer(command("capabilities").put("itemId",item),cancel);}
        catch(StationApi.Failure e){if(e.status==404||e.status==503)throw new StationOnlineGame.Unavailable("A classificação por jogo e as novas salas aguardam publicação no servidor.");throw e;}
    }
    private synchronized void acceptMultiplayer(JSONObject next)throws Exception {
        String instance=next.getString("instance");long revision=next.getLong("revision");
        if(!instance.matches("[0-9a-f]{32}")||revision<0)throw new java.io.IOException("Multiplayer revision");
        if(multiplayerSnapshot!=null){if(!instance.equals(multiplayerSnapshot.getString("instance")))throw new java.io.IOException("Multiplayer server restarted");if(revision<multiplayerSnapshot.getLong("revision"))return;}
        multiplayerSnapshot=next;
    }
    synchronized JSONObject compose(JSONObject social)throws Exception {
        if(social!=null){
            if(socialSnapshot!=null){if(!social.getString("instance").equals(socialSnapshot.getString("instance")))throw new java.io.IOException("Online server restarted");if(social.getLong("revision")<socialSnapshot.getLong("revision"))social=null;}
            if(social!=null)socialSnapshot=social;
        }
        if(socialSnapshot==null)throw new java.io.IOException("Social snapshot unavailable");
        JSONObject out=new JSONObject(socialSnapshot.toString());
        if(multiplayerEnabled&&multiplayerSnapshot!=null){
            JSONObject mp=multiplayerSnapshot;String[] fields={"multiplayerVersion","capability","profiles","classification","profileCount"};
            for(String k:fields)if(mp.has(k))out.put(k,mp.get(k));
            // Legacy membership wins only while an already existing v2 room remains present.
            if(out.optJSONObject("room")==null||mp.optJSONObject("room")!=null){
                for(String k:new String[]{"room","rooms","totalRooms","messages","invites","joinRequests"})out.put(k,mp.has(k)?mp.get(k):k.equals("room")?JSONObject.NULL:k.equals("totalRooms")?0:new JSONArray());
                out.put("transports",new JSONArray().put("relay-wss-v3"));
                JSONArray socialCaps=new JSONArray();JSONArray old=out.optJSONArray("socialCapabilities");
                for(int i=0;old!=null&&i<old.length();i++)if(!"join-request-v1".equals(old.optString(i)))socialCaps.put(old.get(i));
                out.put("socialCapabilities",socialCaps);out.put("roomCapabilities",new JSONArray());
            }
        }
        // A local presentation revision never becomes an authority/request proof.
        out.put("revision",++combinedRevision).put("page",page);return out;
    }
    JSONObject pollMultiplayer(StationApi.Cancellation cancel)throws Exception {multiplayer(command("snapshot"),cancel);return compose(null);}
    private synchronized boolean ownMultiplayer(){return multiplayerSnapshot!=null&&multiplayerSnapshot.optJSONObject("room")!=null;}
    private static boolean roomAction(String a){return java.util.Arrays.asList("create","join","ready","start","leave","relay-ticket","resume-relay","chat","request-join","accept-request","dismiss-request","invite","dismiss-invite").contains(a);}
''')
s=change(s,'        if(!events)request.put("page",page);','''        String action=request.optString("action");
        if(!events&&roomAction(action)&&(request.has("profileId")||ownMultiplayer())){
            JSONObject clean=new JSONObject();
            String[] keys={"action","requestId","roomId","itemId","contentSha256","engineId","coreSha256","runtimeSha256","profileId","profileSha256","capacity","generation","linkId","value","nickname","peerId","text"};
            for(String key:keys)if(request.has(key))clean.put(key,request.get(key));
            if(action.equals("relay-ticket"))clean.put("action","ticket");if(action.equals("resume-relay"))clean.put("action","resume");
            multiplayer(clean,cancel);return compose(null);
        }
        if(!events&&(action.equals("create")||action.equals("join")))throw StationMultiplayerProfile.unavailable();
        if(!events)request.put("page",page);''')
s=change(s,'            return result;','''            if(!events&&action.equals("enter")&&!multiplayerProbed){
                // Probe outside this lease below; acquiring nested leases can block renewal.
                multiplayerProbed=true;
            }
            return compose(result);''')
# Add a probe separate from enter, called by UI after its lease has closed.
s=change(s,'    JSONObject events(JSONObject snapshot,int page,StationApi.Cancellation cancel)throws Exception {','''    void discoverMultiplayer(StationApi.Cancellation cancel)throws Exception {
        try{multiplayer(command("capabilities"),cancel);}catch(StationApi.Failure e){if(e.status!=404&&e.status!=503)throw e;}
    }
    JSONObject events(JSONObject snapshot,int page,StationApi.Cancellation cancel)throws Exception {
        synchronized(this){if(socialSnapshot!=null)snapshot=socialSnapshot;}''')
s=change(s,'                case "STATION_ONLINE_SOCIAL_DISABLED":','''                case "STATION_MULTIPLAYER_DISABLED":return "As novas salas aguardam ativação no servidor.";
                case "STATION_MULTIPLAYER_PROFILE_UNAVAILABLE":case "STATION_MULTIPLAYER_PROFILE_INVALID":case "STATION_MULTIPLAYER_CAPACITY_INVALID":return "Este jogo ou quantidade de jogadores ainda não tem classificação confirmada para jogar online.";
                case "STATION_ONLINE_SOCIAL_DISABLED":''')
put(N+'StationOnlineClient.java',s)
# prepare performs a fresh authority read AND hashes the installed uncompressed game.
s=base(N+'StationOnlineGame.java')
s=change(s,'    final File rom,core,runtime;final String options,recoveryProtocol;','    final File rom,core,runtime;final String options,recoveryProtocol;final StationMultiplayerProfile multiplayerProfile;')
s=change(s,'String hash,String options)throws Exception {','String hash,String options,StationMultiplayerProfile profile)throws Exception {')
s=change(s,'        itemId=id;this.name=name;','        multiplayerProfile=profile;itemId=id;this.name=name;')
s=change(s,'        boolean allowed=false;JSONArray approved=snapshot.getJSONArray("engines");','''        if("station-stream.v3".equals(engine.optString("recoveryProtocol"))){
            JSONObject fresh=client.profileSnapshot(itemId,cancel);
            StationMultiplayerProfile p=StationMultiplayerProfile.find(fresh,itemId,engine);
            File rom=installedRom(itemId);String hash=sha(rom,cancel);
            if(!p.contentSha256.equals(hash))throw new Unavailable("A edição instalada não corresponde ao jogo catalogado para esta sala.");
            File core=new File(context.getApplicationInfo().nativeLibraryDir,engine.getString("library"));File runtime=new File(context.getApplicationInfo().nativeLibraryDir,"libstation_retroarch.so");
            if(!sha(core,cancel).equals(p.coreSha256)||!sha(runtime,cancel).equals(p.runtimeSha256))throw new Unavailable("Atualize o aplicativo para usar o motor aprovado desta sala.");
            boolean extension=false;JSONArray ext=engine.getJSONArray("extensions");for(int j=0;j<ext.length();j++)if(rom.getName().toLowerCase(Locale.ROOT).endsWith("."+ext.getString(j)))extension=true;
            if(!extension)throw new Unavailable("O arquivo instalado não é um cartucho compatível com este motor online.");
            return new StationOnlineGame(itemId,item.name,platform,engine,rom,core,runtime,hash,p.options,p);
        }
        // R77 never grants new seats from the old descriptive metadata.
        if(!snapshot.optBoolean("legacyGameProfileVerified",false))throw StationMultiplayerProfile.unavailable();
        boolean allowed=false;JSONArray approved=snapshot.getJSONArray("engines");''')
s=change(s,'sha(rom,cancel),engine.getString("options"));','sha(rom,cancel),engine.getString("options"),null);')
s=change(s,'    JSONObject fields(JSONObject request)throws JSONException {','    JSONObject fields(JSONObject request)throws JSONException {if(multiplayerProfile!=null)return multiplayerProfile.fields(request);')
s=change(s,'    void verifyRoom(JSONObject room)throws Exception {','    void verifyRoom(JSONObject room)throws Exception {\n        if(multiplayerProfile!=null){multiplayerProfile.verify(room);return;}')
put(N+'StationOnlineGame.java',s)
print('Exact-game preparation and authenticated v3 client prepared')
# Native launch keeps existing controls/assets and uses an explicit per-game controller profile.
s=base(N+'StationRetroLaunch.java')
s=change(s,'        boolean recoverable="relay-wss-v2".equals(room.optString("transport"));boolean relay=recoverable||"relay-wss-v1".equals(room.optString("transport"));JSONObject tunnel=relay?room.getJSONObject("relay"):null;','''        boolean multi=game.multiplayerProfile!=null;
        boolean recoverable="relay-wss-v2".equals(room.optString("transport"));boolean relay=multi||recoverable||"relay-wss-v1".equals(room.optString("transport"));JSONObject tunnel=relay&&!multi?room.getJSONObject("relay"):null;''')
s=change(s,'        if(relay&&(!"/v1/station/online/relay"','        if(relay&&!multi&&(!"/v1/station/online/relay"')
s=change(s,'set(config,"netplay_max_connections","1");','set(config,"netplay_max_connections",String.valueOf(multi?room.getJSONArray("roster").length()-1:1));')
s=change(s,'set(config,"input_libretro_device_p1","1");set(config,"input_libretro_device_p2","1");','''set(config,"input_libretro_device_p1","1");set(config,"input_libretro_device_p2",multi?String.valueOf(game.multiplayerProfile.devices[1]):"1");
        if(multi){
            int local=StationMultiplayerProfile.slot(room,snapshot.getString("selfId"));
            for(int n=1;n<=16;n++){
                set(config,"netplay_request_device_p"+n,String.valueOf(n==local));
                if(n>2)set(config,"input_libretro_device_p"+n,String.valueOf(n<=game.multiplayerProfile.devices.length?game.multiplayerProfile.devices[n-1]:0));
            }
        }''')
s=change(s,'        if(relay){launch.put("relayTicket",','''        if(multi){
            int count=room.getJSONArray("roster").length(),local=StationMultiplayerProfile.slot(room,snapshot.getString("selfId"));
            JSONArray links=room.getJSONArray("launchLinks");if(links.length()!=(local==1?count-1:1))throw new IOException("Missing channel tickets");
            launch.put("recoveryProtocol","station-stream.v3").put("generation",room.getLong("generation")).put("localSlot",local)
                .put("expectedDeviceMask",StationMultiplayerProfile.mask(room)).put("participantCount",count).put("multiplayerLinks",links);
        }
        if(relay&&!multi){launch.put("relayTicket",''')
put(N+'StationRetroLaunch.java',s)
# Session HTTP authority remains in the bound, main-process service.
s=base(N+'StationGameSession.java')
s=change(s,'    private final boolean recovery;','''    private final boolean recovery,multiplayer;
    private final java.util.Set<String> multiplayerTickets=java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap<String,Boolean>());''')
s=change(s,'recovery=binding!=null&&"station-stream.v2".equals(binding.optString("recoveryProtocol"));','multiplayer=binding!=null&&"station-stream.v3".equals(binding.optString("recoveryProtocol"));recovery=multiplayer||(binding!=null&&"station-stream.v2".equals(binding.optString("recoveryProtocol")));')
s=s.replace('"optionsSha256","recoveryProtocol","generation"','"optionsSha256","recoveryProtocol","generation","itemId","profileId","profileSha256","links"')
# the old ticket loop must retain its v2-only keys (no missing field access).
s=change(s,'for(String key:new String[]{"roomId","engineId","coreSha256","runtimeSha256","contentSha256","optionsSha256","recoveryProtocol","generation","itemId","profileId","profileSha256","links"})request.put(key,binding.get(key));','for(String key:new String[]{"roomId","engineId","coreSha256","runtimeSha256","contentSha256","optionsSha256","recoveryProtocol","generation"})request.put(key,binding.get(key));')
s=change(s,'departure.execute(()->{try{StationOnlineClient c=new StationOnlineClient(app);','departure.execute(()->{try{if(multiplayer){new StationOnlineClient(app).multiplayer(StationOnlineClient.command("leave").put("roomId",room),new StationApi.Cancellation());return;}StationOnlineClient c=new StationOnlineClient(app);')
s=change(s,'terminal.execute(()->{try{new StationOnlineClient(app).call(','terminal.execute(()->{try{if(multiplayer){new StationOnlineClient(app).multiplayer(StationOnlineClient.command("failed").put("roomId",room).put("generation",binding.getLong("generation")),new StationApi.Cancellation());return;}new StationOnlineClient(app).call(')
s=change(s,'        }else if(event==2){visible=false;if(!recovery)pause();}','''        }else if(event==2){visible=false;if(!recovery)pause();}
        else if(event==5&&multiplayer){
            if(data==null)return;final String link=data.getString("linkId","");final long serial=data.getLong("serial",-1);
            boolean known=false;org.json.JSONArray links=binding.optJSONArray("links");for(int i=0;links!=null&&i<links.length();i++){JSONObject l=links.optJSONObject(i);if(l!=null&&link.equals(l.optString("linkId")))known=true;}
            if(!known||serial<1||!multiplayerTickets.add(link))return;
            try{worker.execute(()->{try{multiplayerTicket(link,serial);}finally{multiplayerTickets.remove(link);}});}catch(RejectedExecutionException ignored){multiplayerTickets.remove(link);}
        }''')
s=change(s,'    private void ticket(){','''    private void multiplayerTicket(String link,long serial){
        if(closed||failed||!visible)return;StationApi.Cancellation cancel=new StationApi.Cancellation();pending=cancel;Bundle value=new Bundle();value.putString("linkId",link);value.putLong("serial",serial);
        try{
            JSONObject request=StationOnlineClient.command("resume");
            for(String key:new String[]{"roomId","generation","itemId","engineId","coreSha256","runtimeSha256","contentSha256","profileId","profileSha256"})request.put(key,binding.get(key));
            request.put("linkId",link);JSONObject result=new StationOnlineClient(app).multiplayer(request,cancel);
            JSONObject r=result.getJSONObject("room");if(!room.equals(r.getString("roomId"))||r.getLong("generation")!=binding.getLong("generation"))throw new java.io.IOException("Generation");
            JSONObject ticket=result.getJSONObject("ticket");StationMultiplayerSession.checkTicket(ticket,link);value.putString("descriptor",ticket.toString());send(103,value);
        }catch(Exception error){value.putBoolean("terminal",error instanceof StationApi.Failure&&(((StationApi.Failure)error).licenseDenied()||((StationApi.Failure)error).status==404||((StationApi.Failure)error).code.equals("STATION_MULTIPLAYER_GENERATION_MISMATCH")));send(104,value);}finally{pending=null;}
    }
    private void ticket(){''')
s=change(s,'        try{StationOnlineClient c=new StationOnlineClient(app);\n            if(listening&&!acknowledged)', '''        try{StationOnlineClient c=new StationOnlineClient(app);
            if(multiplayer){
                JSONObject result=c.multiplayer(StationOnlineClient.command("heartbeat").put("roomId",room).put("generation",binding.getLong("generation")),cancel);
                JSONObject r=result.optJSONObject("room");
                if(r==null||!room.equals(r.optString("roomId"))||r.optLong("generation",-1)!=binding.getLong("generation")||"unrecoverable".equals(r.optString("state"))){Bundle v=new Bundle();v.putBoolean("terminal",true);send(102,v);roomEnded();}
                return;
            }
            if(listening&&!acknowledged)''')
put(N+'StationGameSession.java',s)
# Native activity delegates only v3 transport to one coordinator; v2 behavior remains available.
s=base(N+'StationRetroActivity.java')
s=change(s,'    private StationRelayTunnel relay;private boolean relayPaused;','''    private StationRelayTunnel relay;private boolean relayPaused;
    private StationMultiplayerSession multiplayer;
    public static native boolean stationMultiplayerConfigure(int localSlot,int expectedDeviceMask,int participantCount,boolean host);
    public static native boolean stationMultiplayerBind(int sourcePort,int remoteSlot);
    public static native boolean stationMultiplayerUnbind(int sourcePort,int remoteSlot);''')
s=change(s,'            if("station-stream.v2".equals(launch.optString("recoveryProtocol"))){','''            if("station-stream.v3".equals(launch.optString("recoveryProtocol"))){
                System.loadLibrary("station_retroarch");
                if(!stationMultiplayerConfigure(launch.getInt("localSlot")-1,launch.getInt("expectedDeviceMask"),launch.getInt("participantCount"),host))throw new IllegalStateException("Native roster");
                multiplayer=new StationMultiplayerSession(launch,new StationMultiplayerSession.Listener(){
                    public void nativeControl(long e,boolean pause,boolean shown){runOnUiThread(()->{if(!sessionFinished&&nativeLoaded)stationRecoveryControl(e,pause,shown);});}
                    public long nativeStatus(){return nativeLoaded?stationRecoveryStatus():-1;}
                    public boolean nativeStalled(){return nativeLoaded&&stationRecoveryStalled();}
                    public boolean bind(int p,int slot){return nativeLoaded&&stationMultiplayerBind(p,slot);}
                    public void unbind(int p,int slot){if(nativeLoaded)stationMultiplayerUnbind(p,slot);}
                    public void ticket(String link,long serial){if(sessionEvents!=null&&!sessionFinished){Bundle b=new Bundle();b.putString("linkId",link);b.putLong("serial",serial);sessionEvents.send(5,b);}}
                    public void ready(){runOnUiThread(()->{listening=true;if(visible&&sessionEvents!=null)sessionEvents.send(3,null);});}
                    public void state(boolean wait,boolean sync){runOnUiThread(()->{recoveryWaiting=wait;recoverySynchronizing=sync;drawRecovery();});}
                    public void fatal(String category){runOnUiThread(()->{if(sessionFinished||recoveryLost)return;recoveryLost=true;recoveryReason=category;recoveryWaiting=true;if(sessionEvents!=null)sessionEvents.send(6,null);drawRecovery();});}
                    public void trace(String event){android.util.Log.i("StationRecovery", "v3 "+event);}
                });
                launch.put("address","127.0.0.1").put("port",multiplayer.localPort());
            }else if("station-stream.v2".equals(launch.optString("recoveryProtocol"))){''')
s=change(s,'if(recovery!=null&&transportStarted)recovery.visible(false);drawRecovery();','if(recovery!=null&&transportStarted)recovery.visible(false);if(multiplayer!=null&&transportStarted)multiplayer.visible(false);drawRecovery();')
s=change(s,'super.onCreate(state);if(recovery!=null){','super.onCreate(state);if(recovery!=null||multiplayer!=null){')
s=change(s,'nativeLoaded=true;if(recovery!=null)installRecoveryPanel();','nativeLoaded=true;if(recovery!=null||multiplayer!=null)installRecoveryPanel();')
s=change(s,'            if(recovery!=null&&code==101){','''            if(multiplayer!=null&&code==103){try{multiplayer.provide(value.getString("linkId"),value.getLong("serial"),new JSONObject(value.getString("descriptor")));}catch(Exception error){multiplayer.unavailable(value.getString("linkId"),value.getLong("serial"),true);}}
            else if(multiplayer!=null&&code==104){multiplayer.unavailable(value.getString("linkId"),value.getLong("serial"),value.getBoolean("terminal"));}
            else if(multiplayer!=null&&code==102&&value.getBoolean("terminal")){multiplayer.visible(false);recoveryLost=true;recoveryReason="AUTHORITY";recoveryWaiting=true;drawRecovery();}
            else if(recovery!=null&&code==101){''')
s=change(s,'if(recovery!=null)recovery.start();if(relay!=null)relay.start();','if(recovery!=null)recovery.start();if(multiplayer!=null)multiplayer.start();if(relay!=null)relay.start();')
s=change(s,'        if(recovery!=null){recovery.visible(true);drawRecovery();}','        if(recovery!=null){recovery.visible(true);drawRecovery();}if(multiplayer!=null){multiplayer.visible(true);drawRecovery();}')
s=change(s,'public void onNetplayListening(){','public void onNetplayListening(){if(multiplayer!=null){multiplayer.listening();return;}')
s=change(s,'visible=false;if(recovery!=null){','visible=false;if(multiplayer!=null){if(transportStarted)multiplayer.visible(false);drawRecovery();}if(recovery!=null){')
s=s.replace('if(recovery!=null)recovery.close();','if(multiplayer!=null)multiplayer.close();if(recovery!=null)recovery.close();')
s=change(s,'sessionEvents.send(recovery!=null&&!humanExit?6:4,null);','sessionEvents.send((recovery!=null||multiplayer!=null)&&!humanExit?6:4,null);')
s=s.replace('avisa o outro jogador.','avisa os demais jogadores.')
put(N+'StationRetroActivity.java',s)
print('Launch, bound session and NativeActivity v3 integrated')
# Public UI consumes capacity and controller slots signed by the server.
s=base(N+'StationRoomRoster.java')
s=change(s,'        JSONArray members = room.optJSONArray("members");\n        JSONArray ready = room.optJSONArray("ready");','''        if("station-stream.v3".equals(room.optString("recoveryProtocol"))){
            int capacity=room.optInt("capacity",0);if(capacity<2||capacity>4)return Collections.emptyList();
            JSONArray roster=room.optJSONArray("roster");ArrayList<Row> result=new ArrayList<Row>();String self=snapshot.optString("selfId");
            for(int slot=1;slot<=capacity;slot++){
                JSONObject player=null;for(int i=0;roster!=null&&i<roster.length();i++){JSONObject p=roster.optJSONObject(i);if(p!=null&&p.optInt("slot")==slot){if(player!=null)return Collections.emptyList();player=p;}}
                if(player==null){result.add(new Row(slot,"",EMPTY_SLOT,false,false,false,false));continue;}
                String id=player.optString("peerId"),name=player.optString("nickname");result.add(new Row(slot,id,name.isEmpty()?NAME_UNAVAILABLE:name,!name.isEmpty(),self.equals(id),slot==1,player.optBoolean("ready")));
            }
            return Collections.unmodifiableList(result);
        }
        JSONArray members = room.optJSONArray("members");
        JSONArray ready = room.optJSONArray("ready");''')
put(N+'StationRoomRoster.java',s)
s=base(N+'StationRoomStartState.java')
s=change(s,'        JSONArray members=room.optJSONArray("members"),ready=room.optJSONArray("ready");','''        if("station-stream.v3".equals(room.optString("recoveryProtocol"))){
            int capacity=room.optInt("capacity");JSONArray roster=room.optJSONArray("roster"),allowed=room.optJSONArray("allowedPlayerCounts");
            if(capacity<2||capacity>4||roster==null||roster.length()<2||roster.length()>capacity)return "Convide os jogadores para esta sala.";
            boolean countAllowed=false;for(int i=0;allowed!=null&&i<allowed.length();i++)if(allowed.optInt(i)==roster.length())countAllowed=true;
            if(!countAllowed)return "Este modo não aceita a quantidade atual de jogadores. Aguarde mais participantes.";
            java.util.HashSet<String> ids=new java.util.HashSet<>();java.util.HashSet<Integer> slots=new java.util.HashSet<>();
            for(int i=0;i<roster.length();i++){JSONObject p=roster.optJSONObject(i);if(p==null||p.optString("peerId").isEmpty()||!ids.add(p.optString("peerId"))||p.optInt("slot")<1||p.optInt("slot")>capacity||!slots.add(p.optInt("slot")))return "A lista de participantes precisa ser atualizada.";if(!p.optBoolean("ready"))return "Todos os participantes precisam marcar Estou pronto.";}
            if(!ids.contains(self)||!slots.contains(1))return "A lista de participantes precisa ser atualizada.";
            return has(snapshot.optJSONArray("transports"),"relay-wss-v3")?"":"A conexão da sala aguarda ativação.";
        }
        JSONArray members=room.optJSONArray("members"),ready=room.optJSONArray("ready");''')
s=change(s,'        return room!=null&&','        if(room!=null&&"station-stream.v3".equals(room.optString("recoveryProtocol")))return "relay-wss-v3";\n        return room!=null&&')
put(N+'StationRoomStartState.java',s)
s=base(N+'StationLaunchPolicy.java')
s=change(s,'static boolean eligible(JSONObject room,boolean host){','''static boolean eligible(JSONObject room,boolean host){if("station-stream.v3".equals(room.optString("recoveryProtocol")))return "relay-wss-v3".equals(room.optString("transport"))&&!room.optBoolean("recoveryStarted",false)&&room.optLong("generation")>0&&("starting".equals(room.optString("state"))||"synchronizing".equals(room.optString("state"))||"waiting-reconnect".equals(room.optString("state")));''')
put(N+'StationLaunchPolicy.java',s)
s=base(N+'StationRoomsActivity.java')
s=change(s,'    private Future<?> polling;','''    private final ScheduledExecutorService multiplayerEvents=Executors.newSingleThreadScheduledExecutor();
    private ScheduledFuture<?> multiplayerPolling;
    private Future<?> polling;''')
s=change(s,'                deliver(current,generation);\n                long heartbeat=','''                client.discoverMultiplayer(cancel);current=client.compose(null);deliver(current,generation);
                if(client.multiplayerEnabled){
                    if(multiplayerPolling!=null)multiplayerPolling.cancel(true);
                    multiplayerPolling=multiplayerEvents.scheduleWithFixedDelay(()->{
                        if(!active||epoch!=generation)return;StationApi.Cancellation c=new StationApi.Cancellation();requests.add(c);
                        try{deliver(client.pollMultiplayer(c),generation);}catch(Exception e){if(!c.cancelled())recordFailure(e);}finally{requests.remove(c);}
                    },1,1,TimeUnit.SECONDS);
                }
                long heartbeat=''')
s=change(s,'if(returningFromGame&&returningRecovery){JSONObject lost=current.optJSONObject("room");','if(returningFromGame&&returningRecovery){JSONObject lost=current.optJSONObject("room");') if False else s
# Full listener re-entry must not manufacture a new native stream for an old generation.
s=change(s,'if(returningFromGame&&returningRecovery){JSONObject lost=current.optJSONObject("room");','if(returningFromGame&&returningRecovery){JSONObject lost=current.optJSONObject("room");') if False else s
# Cancel this separate poll using the same lifecycle gates as the existing events path.
s=change(s,'    @Override public void onSaveInstanceState(Bundle out){','''    private void stopMultiplayerPoll(){if(multiplayerPolling!=null){multiplayerPolling.cancel(true);multiplayerPolling=null;}}
    @Override public void onSaveInstanceState(Bundle out){''')
s=change(s,'    @Override protected void onPause(){','    @Override protected void onPause(){stopMultiplayerPoll();')
# Read the exact method boundary rather than replacing an older Activity.
start=s.index('    private void createRoom(){');end=s.index('    private void join(String roomId',start)
s=s[:start]+'''    private void createRoom(){
        if(busy||launching||!active||client==null||state.get()==null)return;
        if(selectedItem==null){showCreateMessage("Escolha um jogo antes de criar a sala.",true);return;}
        if(room()!=null){showCreateMessage("Saia da sala atual antes de criar outra.",true);return;}
        final String requested=selectedItem;creating=true;choose.setEnabled(false);create.setText("Conferindo…");prepared=null;
        showCreateMessage("Conferindo a edição, o modo e os jogadores permitidos…",false);
        action(cancel->{prepared=StationOnlineGame.prepare(this,client,requested,state.get(),cancel);return client.compose(null);},()->{
            creating=false;choose.setEnabled(true);create.setText("Criar sala");
            StationOnlineGame game=prepared;if(game==null||!requested.equals(selectedItem))return;
            int[] counts=game.multiplayerProfile.allowed;
            if(counts.length==1){createVerifiedRoom(game,counts[0]);return;}
            String[] choices=new String[counts.length];for(int i=0;i<counts.length;i++)choices[i]="Até "+counts[i]+" jogadores";
            final int[] chosen={counts.length-1};
            new AlertDialog.Builder(this).setTitle("Jogadores na sala").setSingleChoiceItems(choices,chosen[0],(d,index)->chosen[0]=index)
                .setNegativeButton("Cancelar",null).setPositiveButton("Criar sala",(d,index)->createVerifiedRoom(game,counts[chosen[0]])).show();
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
''' +s[end:]
# Two columns, up to two rows. Each name belongs to the explicit controller slot.
s=change(s,'            StationRoomRoster.Row member=members.get(i);LinearLayout column=vertical();','''            if(i>0&&i%2==0){line=row();line.setGravity(Gravity.TOP);parent.addView(line,new LinearLayout.LayoutParams(-1,-2));}
            StationRoomRoster.Row member=members.get(i);LinearLayout column=vertical();''')
s=change(s,'cp.leftMargin=i==0?0:dp(12);','cp.leftMargin=i%2==0?0:dp(12);')
s=change(s,'TextView role=text(column,member.occupied?','TextView role=text(column,"P"+member.position+" · "+(member.occupied?')
s=change(s,':"VAGA DISPONÍVEL",9,muted);',':"VAGA DISPONÍVEL"),9,muted);')
s=change(s,'boolean social=StationSocial.supports(snapshot,"join-request-v1");','boolean social=!"station-stream.v3".equals(r.optString("recoveryProtocol"))&&StationSocial.supports(snapshot,"join-request-v1");')
s=change(s,'if(StationPlayerModel.shareable(snapshot))roomAction','if(!"station-stream.v3".equals(mine.optString("recoveryProtocol"))&&StationPlayerModel.shareable(snapshot))roomAction')
# Do not expose legacy invite generation in a v3 room.
s=change(s,'    private void startDialog(){','    private void startDialog(){') if False else s
s=change(s,'"Escolha seu jogo e convide alguém. Os dois precisam ter a mesma edição instalada."','"A quantidade de jogadores depende do jogo e do modo aprovado. Todos precisam da mesma edição instalada."')
s=change(s,'            if("relay-wss-v1".equals(room.optString("transport"))','''            if("station-stream.v3".equals(room.optString("recoveryProtocol"))){
                game.verifyRoom(room);JSONArray links=room.getJSONArray("links"),launchLinks=new JSONArray();String self=snapshot.getString("selfId");boolean host=self.equals(room.getString("hostId"));
                for(int li=0;li<links.length();li++){JSONObject link=links.getJSONObject(li);if(!host&&!self.equals(link.getString("guestPeerId")))continue;
                    JSONObject result=client.multiplayer(game.fields(StationOnlineClient.command("ticket")).put("roomId",room.getString("roomId")).put("generation",room.getLong("generation")).put("linkId",link.getString("linkId")),cancel);
                    JSONObject actual=result.getJSONObject("room");game.verifyRoom(actual);if(actual.getLong("generation")!=room.getLong("generation"))throw new java.io.IOException("Generation changed");
                    JSONObject ticket=result.getJSONObject("ticket");StationMultiplayerSession.checkTicket(ticket,link.getString("linkId"));
                    launchLinks.put(new JSONObject(link.toString()).put("ticket",ticket));
                }
                gameRoom=new JSONObject(room.toString()).put("launchLinks",launchLinks);
            }else if("relay-wss-v1".equals(room.optString("transport"))''')
s=s.replace('returningRecovery="relay-wss-v2".equals(room.optString("transport"))','returningRecovery="relay-wss-v2".equals(room.optString("transport"))||"relay-wss-v3".equals(room.optString("transport"))')
s=s.replace('"station-stream.v2".equals(room.optString("recoveryProtocol"))?room.optLong','("station-stream.v2".equals(room.optString("recoveryProtocol"))||"station-stream.v3".equals(room.optString("recoveryProtocol")))?room.optLong')
# Task guard closes scheduled executor only at final destruction.
s=change(s,'super.onDestroy();','multiplayerEvents.shutdownNow();super.onDestroy();')
put(N+'StationRoomsActivity.java',s)
print('Room UI, exact capacity chooser, roster and launch integration prepared')
