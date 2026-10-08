from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'java';N='netplay-src/org/emulationstation/frontend/netplay/'
BASE=Path(r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\compiled-final\java')
def read(n):return (OUT/(N+n)).read_text('utf8')
def put(n,s):(OUT/(N+n)).write_text(s,encoding='utf8',newline='\n')
def change(s,a,b,n=1):
 assert s.count(a)==n,(a[:95],s.count(a),n)
 return s.replace(a,b)
s=read('StationOnlineGame.java')
s=change(s,'    static String platform(String raw)throws IOException {','''    static JSONObject engine(Context context,String raw)throws Exception {
        String platform=platform(raw);JSONObject manifest;try(InputStream input=context.getAssets().open("station-online/engines.json")){manifest=new JSONObject(new String(read(input,32768),StandardCharsets.UTF_8));}
        JSONArray entries=manifest.getJSONArray("engines");for(int i=0;i<entries.length();i++){JSONObject e=entries.getJSONObject(i);if(platform.equals(e.getString("platform"))&&e.optBoolean("launchReady")&&"station-stream.v3".equals(e.optString("recoveryProtocol")))return e;}
        throw new Unavailable("Esta plataforma ainda aguarda um motor aprovado para estas salas.");
    }
    static List<StationMultiplayerProfile> profiles(Context context,StationOnlineClient client,String itemId,StationApi.Cancellation cancel)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw StationMultiplayerProfile.unavailable();
        return StationMultiplayerProfile.choices(client.profileSnapshot(itemId,cancel),itemId,engine(context,item.platform));
    }
    static String platform(String raw)throws IOException {''')
s=change(s,'        StationCatalog.Item item=client.item(itemId);if(item==null)throw new Unavailable("Selecione um jogo do catálogo antes de criar a sala.");','''        JSONObject own=snapshot==null?null:snapshot.optJSONObject("room");String profileId=own!=null&&itemId.equals(own.optString("itemId"))?own.optString("profileId"):"";
        return prepare(context,client,itemId,snapshot,cancel,profileId);
    }
    static StationOnlineGame prepare(Context context,StationOnlineClient client,String itemId,JSONObject snapshot,StationApi.Cancellation cancel,String profileId)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw new Unavailable("Selecione um jogo do catálogo antes de criar a sala.");''')
s=change(s,'StationMultiplayerProfile.find(fresh,itemId,engine);','StationMultiplayerProfile.find(fresh,itemId,engine,profileId);')
put('StationOnlineGame.java',s)
s=read('StationRoomsActivity.java')
s=change(s,'private TextView createGame,chatHint;','private TextView createGame,chatHint,createInfo;')
s=change(s,'        createGame=text(createActions,"Jogo não selecionado",20,white);bold(createGame);','        createGame=text(createActions,"Jogo não selecionado",20,white);bold(createGame);\n        createInfo=text(createActions,StationGamePlayerInfo.pending().detail,12,muted);createInfo.setLineSpacing(dp(2),1);')
s=change(s,'    private void createRoom(){','''    private static StationGamePlayerInfo profileInfo(StationMultiplayerProfile p){return StationGamePlayerInfo.fromVerifiedProfile(true,p.maximumPlayers,p.allowed,p.mode,p.controllerProfile);}
    private static StationGamePlayerInfo roomGameInfo(JSONObject r){
        if(r==null||!"station-stream.v3".equals(r.optString("recoveryProtocol")))return StationGamePlayerInfo.pending();
        JSONArray a=r.optJSONArray("allowedPlayerCounts");int[] counts=new int[a==null?0:a.length()];for(int i=0;i<counts.length;i++)counts[i]=a.optInt(i);
        return StationGamePlayerInfo.fromVerifiedProfile(true,r.optInt("maximumPlayers"),counts,r.optString("mode"),r.optString("controllerProfile"));
    }
    private static StationGamePlayerInfo.RoomInfo roomInfo(JSONObject r,String self){
        StationGamePlayerInfo info=roomGameInfo(r);JSONArray a=r==null?null:r.optJSONArray("roster");StationGamePlayerInfo.Participant[] people=new StationGamePlayerInfo.Participant[a==null?0:a.length()];
        for(int i=0;i<people.length;i++){JSONObject p=a.optJSONObject(i);if(p!=null)people[i]=new StationGamePlayerInfo.Participant(p.optInt("slot"),p.optString("peerId"),p.optString("nickname"),p.optBoolean("ready"),self.equals(p.optString("peerId")));}
        return info.forRoom(r==null?0:r.optInt("capacity"),r!=null&&"waiting".equals(r.optString("state")),people);
    }
    private String roomExplanation(JSONObject r){
        StationGamePlayerInfo.RoomInfo info=roomInfo(r,state.get()==null?"":state.get().optString("selfId"));
        StringBuilder text=new StringBuilder(info.detail);if(!info.confirmed)return text.toString();
        text.append("\\n\\n");for(StationGamePlayerInfo.Position p:info.positions){text.append(p.label).append(" · ").append(p.name).append(p.self?" (você)":"").append("\\n");}
        if("battle-single".equals(r.optString("mode"))&&"snes-multitap-port2-v1".equals(r.optString("controllerProfile")))text.append("\\nNo jogo, escolha BATTLE GAME → Single Match e marque MAN nos controles dos participantes. O modo Normal é individual.");
        text.append("\\nTodos precisam da mesma edição do jogo. Cada participante controla apenas sua posição e pode usar sua própria rede.");return text.toString();
    }
    private void createRoom(){
        if(busy||launching||!active||client==null||state.get()==null)return;
        if(selectedItem==null){showCreateMessage("Escolha um jogo antes de criar a sala.",true);return;}
        if(room()!=null){showCreateMessage("Saia da sala atual antes de criar outra.",true);return;}
        final String item=selectedItem;final java.util.List<StationMultiplayerProfile> modes=new ArrayList<>();
        action(cancel->{modes.addAll(StationOnlineGame.profiles(this,client,item,cancel));if(modes.isEmpty())throw StationMultiplayerProfile.unavailable();return client.compose(null);},()->{
            if(!item.equals(selectedItem)||!active)return;
            if(modes.size()==1){prepareRoom(modes.get(0).profileId);return;}
            String[] labels=new String[modes.size()];for(int i=0;i<labels.length;i++)labels[i]=profileInfo(modes.get(i)).summary;
            new AlertDialog.Builder(this).setTitle("Modo da partida").setItems(labels,(d,i)->prepareRoom(modes.get(i).profileId)).setNegativeButton("Cancelar",null).show();
        });
    }
    private void prepareRoom(String profileId){''')
s=change(s,'prepared=StationOnlineGame.prepare(this,client,requested,state.get(),cancel);','prepared=StationOnlineGame.prepare(this,client,requested,state.get(),cancel,profileId);')
s=change(s,'choices[i]="Até "+counts[i]+" jogadores"','choices[i]=counts[i]+" vagas"')
s=change(s,'new AlertDialog.Builder(this).setTitle("Jogadores na sala").setSingleChoiceItems','new AlertDialog.Builder(this).setTitle(profileInfo(game.multiplayerProfile).modeLabel+" · vagas").setSingleChoiceItems')
s=change(s,'        if(mine==null){joinConfirmed(roomId,itemId,null);return;}','''        JSONObject target=findRoom(snapshot,roomId);if(target==null){status.setText("A sala mudou. Atualize a lista antes de entrar.");return;}
        if(mine==null){confirmWithCover("Entrar nesta sala?",roomExplanation(target),"Aceitar e entrar",()->joinConfirmed(roomId,itemId,null,target.optLong("generation"),target.optString("profileId")),itemId);return;}''')
s=change(s,'()->joinConfirmed(roomId,itemId,previous),itemId);','()->joinConfirmed(roomId,itemId,previous,target.optLong("generation"),target.optString("profileId")),itemId);')
s=change(s,'Estou pronto confirma a participação; não muda de sala.","Sair e entrar"','Estou pronto confirma a participação; não muda de sala.\\n\\n"+roomExplanation(target),"Sair e entrar"')
s=change(s,'private void joinConfirmed(String roomId,String itemId,String previous){','private void joinConfirmed(String roomId,String itemId,String previous,long confirmedGeneration,String confirmedProfile){')
s=change(s,'StationOnlineGame game=StationOnlineGame.prepare(this,client,itemId,state.get(),cancel);','''StationOnlineGame game=StationOnlineGame.prepare(this,client,itemId,state.get(),cancel,confirmedProfile);
            JSONObject target=client.multiplayerRoom(roomId);if(target==null||target.optLong("generation")!=confirmedGeneration||!confirmedProfile.equals(target.optString("profileId")))throw new StationOnlineGame.Unavailable("A sala mudou. Confira novamente as vagas e o modo.");game.verifyRoom(target);''')
s=change(s,'prepared=game;JSONObject joined=client.call(game.fields(StationOnlineClient.command("join").put("roomId",roomId)),false,cancel);','prepared=game;JSONObject joined=client.call(game.fields(StationOnlineClient.command("join").put("roomId",roomId).put("generation",confirmedGeneration)),false,cancel);')
s=change(s,'    private void command(String action,String key,Object value){action(cancel->{JSONObject c=StationOnlineClient.command(action);if(key!=null)c.put(key,value);JSONObject r=room();if(r!=null)c.put("roomId",r.getString("roomId"));return client.call(c,false,cancel);});}','''    private void command(String action,String key,Object value){
        final JSONObject displayed=room();final String target=displayed==null?"":displayed.optString("roomId");final long generation=displayed==null?0:displayed.optLong("generation");
        action(cancel->{JSONObject c=StationOnlineClient.command(action);if(key!=null)c.put(key,value);if(!target.isEmpty()){c.put("roomId",target);if("station-stream.v3".equals(displayed.optString("recoveryProtocol")))c.put("generation",generation);}return client.call(c,false,cancel);});
    }''')
s=change(s,'StationOnlineClient.command("start").put("roomId",latest.getJSONObject("room").getString("roomId")).put("transport"','StationOnlineClient.command("start").put("roomId",latest.getJSONObject("room").getString("roomId")).put("generation",latest.getJSONObject("room").optLong("generation")).put("transport"')
s=change(s,'            LinearLayout participants=vertical();','            text(current,roomInfo(mine,self).summary,12,green);\n            LinearLayout participants=vertical();')
s=change(s,'text(c,nickname(snapshot,r.optString("hostId"))+"  ·  "+r.optInt("players")+" / "+r.optInt("capacity",r.optInt("maximumPlayers",2))+" jogadores",12,muted);','text(c,nickname(snapshot,r.optString("hostId"))+"  ·  "+roomInfo(r,self).summary,12,muted);')
s=change(s,'boolean available="waiting".equals(r.optString("state"))&&r.optInt("players")<r.optInt("capacity",r.optInt("maximumPlayers",2));','StationGamePlayerInfo.RoomInfo seats=roomInfo(r,self);boolean available="station-stream.v3".equals(r.optString("recoveryProtocol"))?seats.confirmed&&seats.acceptingPlayers&&seats.vacancies>0:"waiting".equals(r.optString("state"))&&r.optInt("players")<r.optInt("capacity",r.optInt("maximumPlayers",2));')
s=change(s,'text(content,"Cada jogador pode usar sua própria rede. Confira os participantes antes de começar.",12,muted);','text(content,roomExplanation(snapshot.optJSONObject("room")),12,muted);')
s=change(s,'headerPlayers.setText(details.players);headerPlayers.setContentDescription("Jogadores suportados pelo jogo: "+details.players);','headerPlayers.setText("Jogadores a confirmar");headerPlayers.setContentDescription("Quantidade de jogadores online ainda não confirmada");')
s=change(s,'            }catch(Exception unavailable){android.util.Log.i("StationOnline","Selected game metadata unavailable");}','''                StationApi.Cancellation check=new StationApi.Cancellation();requests.add(check);
                try{
                    java.util.List<StationMultiplayerProfile> profiles=StationOnlineGame.profiles(this,client,target,check);StringBuilder brief=new StringBuilder(),detail=new StringBuilder();java.util.SortedSet<Integer> counts=new java.util.TreeSet<>();
                    for(StationMultiplayerProfile p:profiles){StationGamePlayerInfo info=profileInfo(p);if(detail.length()>0)detail.append("\\n");for(int count:p.allowed)counts.add(count);detail.append(info.detail);}
                    brief.setLength(0);for(int count:counts){if(brief.length()>0)brief.append(", ");brief.append(count);}if(brief.length()>0)brief.append(" jogadores").append(profiles.size()>1?" · "+profiles.size()+" modos":"");
                    final String b=brief.length()==0?StationGamePlayerInfo.pending().capacityLabel:brief.toString(),d=detail.length()==0?StationGamePlayerInfo.pending().detail:detail.toString();
                    runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)){headerPlayers.setText(b);headerPlayers.setContentDescription(b);if(createInfo!=null)createInfo.setText(d);}});
                }catch(Exception unavailable){runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)&&createInfo!=null)createInfo.setText(StationGamePlayerInfo.pending().detail);});}
                finally{requests.remove(check);}
            }catch(Exception unavailable){android.util.Log.i("StationOnline","Selected game metadata unavailable");}''')
s=change(s,'headerRating.setRating(-1);headerPlayers.setText("—");','headerRating.setRating(-1);headerPlayers.setText("Jogadores a confirmar");if(createInfo!=null)createInfo.setText(StationGamePlayerInfo.pending().detail);')
s=change(s,'        Button invite=navButton(navItems,"Usar convite",()->enterCodeDialog());navigationIcon(invite,4);','        inviteNavigation=navButton(navItems,"Usar convite",()->enterCodeDialog());navigationIcon(inviteNavigation,4);')
s=change(s,'private Button navRooms,navPeople,navCreate,navChat;','private Button navRooms,navPeople,navCreate,navChat,inviteNavigation;')
s=change(s,'        if(target==null||target.isEmpty()||(target.equals(heroRequestId)&&heroEpoch==epoch))return;','        if(client==null||state.get()==null||target==null||target.isEmpty()||(target.equals(heroRequestId)&&heroEpoch==epoch))return;')
s=change(s,'        roster.observe(snapshot);','        roster.observe(snapshot);if(inviteNavigation!=null)inviteNavigation.setVisibility(client!=null&&client.multiplayerEnabled?View.GONE:View.VISIBLE);')
put('StationRoomsActivity.java',s)
s=(BASE/(N+'StationPlayerModel.java')).read_text('utf8')
s=change(s,'        return room!=null&&snapshot.optString','        if(room!=null&&"station-stream.v3".equals(room.optString("recoveryProtocol")))return false;\n        return room!=null&&snapshot.optString')
s=change(s,'r!=null&&id.equals(r.optString("hostId"))','r!=null&&(id.equals(r.optString("hostId"))||member(r,id))')
s=change(s,'        boolean share=shareable(snapshot),invite=false;','''        if(target!=null&&"station-stream.v3".equals(target.optString("recoveryProtocol")))join=p!=null&&!self&&"waiting".equals(target.optString("state"))&&target.optInt("players")<target.optInt("capacity")&&(mine==null||soloWaitingRoom(snapshot));
        boolean share=shareable(snapshot),invite=false;''')
s=change(s,'        return new StationPlayerModel(id,name,status,item,label,reason,p!=null,self,online,invite,share,mine,target,join);','''        if(snapshot!=null&&snapshot.optInt("multiplayerVersion")==3){invite=false;share=false;if(target==null&&!self&&!member(mine,id))reason="Converse com este jogador e combine a entrada pela lista de salas.";}
        return new StationPlayerModel(id,name,status,item,label,reason,p!=null,self,online,invite,share,mine,target,join);''')
put('StationPlayerModel.java',s)
s=(BASE/(N+'StationPlayerSheet.java')).read_text('utf8')
s=change(s,'            else button(busy?"Aguarde…":model.inviteLabel,','            else if(model.canInvite)button(busy?"Aguarde…":model.inviteLabel,')
put('StationPlayerSheet.java',s)
print('Exact mode chooser and verified game/room/accept/start presentation integrated')
