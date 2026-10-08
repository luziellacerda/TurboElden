from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'java';N='netplay-src/org/emulationstation/frontend/netplay/'
def read(name):return (OUT/(N+name)).read_text('utf8')
def put(name,s):(OUT/(N+name)).write_text(s,encoding='utf8',newline='\n')
def change(s,a,b,n=1):
 assert s.count(a)==n,(a[:100],s.count(a),n)
 return s.replace(a,b)
s=read('StationOnlineClient.java')
s=change(s,'    private JSONObject socialSnapshot,multiplayerSnapshot;private long combinedRevision;','    private JSONObject socialSnapshot,multiplayerSnapshot;private long combinedRevision;private String presentationKey="";')
s=change(s,'        multiplayerSnapshot=next;','        if(socialSnapshot!=null&&!socialSnapshot.getString("selfId").equals(next.getString("selfId")))throw new java.io.IOException("Multiplayer identity mismatch");\n        multiplayerSnapshot=next;')
s=change(s,'            JSONObject mp=multiplayerSnapshot;String[] fields=', '            JSONObject mp=multiplayerSnapshot;if(!out.getString("selfId").equals(mp.getString("selfId")))throw new java.io.IOException("Multiplayer identity mismatch");String[] fields=')
s=change(s,'                out.put("transports",new JSONArray().put("relay-wss-v3"));','''                JSONObject own=mp.optJSONObject("room");out.put("messages",own==null?new JSONArray():own.optJSONArray("messages"));
                out.put("nextPage",JSONObject.NULL);
                out.put("transports",new JSONArray().put("relay-wss-v3"));''')
s=change(s,'                JSONObject own=mp.optJSONObject("room");out.put("messages"','''                java.util.HashSet<String> members=new java.util.HashSet<>();JSONArray all=mp.optJSONArray("rooms");
                for(int i=0;all!=null&&i<all.length();i++){JSONObject room=all.optJSONObject(i);JSONArray roster=room==null?null:room.optJSONArray("members");for(int j=0;roster!=null&&j<roster.length();j++)members.add(roster.optString(j));}
                JSONObject mine=mp.optJSONObject("room");JSONArray ours=mine==null?null:mine.optJSONArray("members");for(int i=0;ours!=null&&i<ours.length();i++)members.add(ours.optString(i));
                JSONArray peers=out.optJSONArray("peers");for(int i=0;peers!=null&&i<peers.length();i++){JSONObject peer=peers.optJSONObject(i);if(peer!=null&&members.contains(peer.optString("peerId"))&&("online".equals(peer.optString("status"))||"in-room".equals(peer.optString("status"))))peer.put("status","in-room");}
                JSONObject own=mp.optJSONObject("room");out.put("messages"''')
s=change(s,'        out.put("revision",++combinedRevision).put("page",page);return out;','''        JSONObject visible=new JSONObject(out.toString());
        for(String k:new String[]{"revision","serverTimeMs","serverTime","serverUtc","requestId"})visible.remove(k);
        String key=visible.toString()+"/"+page;if(!key.equals(presentationKey)){presentationKey=key;combinedRevision++;}
        out.put("revision",combinedRevision).put("page",page);return out;''')
s=change(s,'            JSONObject clean=new JSONObject();','''            if(java.util.Arrays.asList("request-join","accept-request","dismiss-request","invite","dismiss-invite").contains(action))throw new StationOnlineGame.Unavailable("Combine a partida pela conversa e entre pela lista de salas. Os convites desta modalidade ainda estão em preparação.");
            JSONObject clean=new JSONObject();''')
s=change(s,'"linkId","value","nickname","peerId","text"','"linkId","value","nickname","text"')
s=change(s,'            multiplayer(clean,cancel);return compose(null);','''            if(!action.equals("create")&&!clean.has("generation")){
                JSONObject target=multiplayerRoom(clean.optString("roomId"));
                if(target==null)throw new StationOnlineGame.Unavailable("A sala mudou. Atualize a lista e confirme novamente.");
                clean.put("roomId",target.getString("roomId")).put("generation",target.getLong("generation"));
            }
            multiplayer(clean,cancel);return compose(null);''')
s=change(s,'    private synchronized boolean ownMultiplayer()', '''    synchronized JSONObject multiplayerRoom(String id)throws Exception {
        if(multiplayerSnapshot==null)return null;JSONObject own=multiplayerSnapshot.optJSONObject("room");
        if(own!=null&&(id.isEmpty()||id.equals(own.optString("roomId"))))return new JSONObject(own.toString());
        JSONArray rooms=multiplayerSnapshot.optJSONArray("rooms");for(int i=0;rooms!=null&&i<rooms.length();i++){JSONObject r=rooms.optJSONObject(i);if(r!=null&&id.equals(r.optString("roomId")))return new JSONObject(r.toString());}return null;
    }
    private synchronized boolean ownMultiplayer()''')
s=change(s,'                case "STATION_MULTIPLAYER_DISABLED":','''                case "STATION_MULTIPLAYER_GAME_UNCLASSIFIED":case "STATION_MULTIPLAYER_PROFILE_UNAPPROVED":case "STATION_MULTIPLAYER_CAPACITY_UNSUPPORTED":return "O jogo, o modo ou esta quantidade de jogadores ainda aguarda confirmação. Escolha uma opção aprovada.";
                case "STATION_MULTIPLAYER_GENERATION_MISMATCH":return "A sala mudou. Confira novamente os participantes antes de continuar.";
                case "STATION_MULTIPLAYER_ROOM_FULL":return "Esta sala já está completa.";
                case "STATION_MULTIPLAYER_NOT_READY":return "Todos os participantes precisam marcar Estou pronto.";
                case "STATION_MULTIPLAYER_DISABLED":''')
put('StationOnlineClient.java',s)
s=read('StationGameSession.java')
s=change(s,'StationOnlineClient.command("leave").put("roomId",room),new StationApi.Cancellation())','StationOnlineClient.command("leave").put("roomId",room).put("generation",binding.getLong("generation")),new StationApi.Cancellation())')
s=change(s,'((StationApi.Failure)error).code.equals("STATION_MULTIPLAYER_GENERATION_MISMATCH")','java.util.Arrays.asList("STATION_MULTIPLAYER_GENERATION_MISMATCH","STATION_MULTIPLAYER_UNRECOVERABLE","STATION_MULTIPLAYER_GAME_MISMATCH","STATION_MULTIPLAYER_PROFILE_UNAPPROVED","STATION_MULTIPLAYER_MEMBERSHIP_REQUIRED").contains(((StationApi.Failure)error).code)')
put('StationGameSession.java',s)
s=read('StationRetroLaunch.java')
s=change(s,'        if(multi){\n            int local=','        if(multi){\n            set(config,"netplay_share_digital","0");set(config,"netplay_share_analog","0");\n            int local=')
put('StationRetroLaunch.java',s)
s=read('StationRoomsActivity.java')
s=change(s,'    @Override protected void onPause(){stopMultiplayerPoll();','    @Override protected void onPause(){')
s=change(s,'    @Override protected void onStop(){','    @Override protected void onStop(){stopMultiplayerPoll();')
s=change(s,'Os dois estão prontos. Pode iniciar.','Todos estão prontos. Pode iniciar.')
s=change(s,'+"/"+room.optString("itemId");}','+"/"+room.optString("itemId")+"/"+room.optLong("generation")+"/"+room.optString("profileId")+"/"+room.optString("profileSha256")+"/"+room.optInt("capacity")+"/"+String.valueOf(room.optJSONArray("roster"));}')
s=change(s,'r.optInt("players")<r.optInt("maximumPlayers",2)','r.optInt("players")<r.optInt("capacity",r.optInt("maximumPlayers",2))')
s=change(s,'r.optInt("players")+" / "+r.optInt("maximumPlayers",2)','r.optInt("players")+" / "+r.optInt("capacity",r.optInt("maximumPlayers",2))')
s=change(s,'            return joined;\n        },()->{if(playerSheet!=null)playerSheet.dismiss();});','            game.verifyRoom(actual);return joined;\n        },()->{if(playerSheet!=null)playerSheet.dismiss();});')
s=change(s,'    private void invitePlayer(String id){','''    private void invitePlayer(String id){
        if(client!=null&&client.multiplayerEnabled){status.setText("Converse com o jogador e peça para entrar pela lista de salas. O convite desta modalidade ainda está em preparação.");return;}''')
s=change(s,'    private void showRoomCode(){','''    private void showRoomCode(){
        if(room()!=null&&"station-stream.v3".equals(room().optString("recoveryProtocol"))){status.setText("Entre nesta partida pela lista de salas. O código desta modalidade ainda está em preparação.");return;}''')
s=change(s,'try{time=java.time.OffsetDateTime.parse(utc).atZoneSameInstant(java.time.ZoneId.systemDefault()).format(java.time.format.DateTimeFormatter.ofPattern("HH:mm"));}', 'try{time=(m.has("utcMs")?java.time.Instant.ofEpochMilli(m.getLong("utcMs")).atZone(java.time.ZoneId.systemDefault()):java.time.OffsetDateTime.parse(utc).atZoneSameInstant(java.time.ZoneId.systemDefault())).format(java.time.format.DateTimeFormatter.ofPattern("HH:mm"));}')
put('StationRoomsActivity.java',s)
print('R77 contract, room generations, fixed sharing and lifecycle refined')

s=read('StationRetroActivity.java')
s=change(s,'}catch(Exception error){android.util.Log.e("StationRooms","game stage=launch-failed','}catch(Exception|LinkageError error){android.util.Log.e("StationRooms","game stage=launch-failed')
s=change(s,'public void nativeControl(long e,boolean pause,boolean shown){runOnUiThread(()->{if(!sessionFinished&&nativeLoaded)stationRecoveryControl(e,pause,shown);});}','public void nativeControl(long e,boolean pause,boolean shown){runOnUiThread(()->{if(!sessionFinished&&nativeLoaded)try{stationRecoveryControl(e,pause,shown);}catch(LinkageError error){fatal("NATIVE_HOOK");}});}')
put('StationRetroActivity.java',s)
