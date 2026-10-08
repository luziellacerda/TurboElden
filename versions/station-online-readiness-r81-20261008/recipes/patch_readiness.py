"""Apply only reviewed readiness/UI changes to the complete frozen R79 Java set."""
from pathlib import Path
ROOT=Path(r'E:\ESTUDO APK\work\station-online-readiness-r81-20261008\java\netplay-src\org\emulationstation\frontend\netplay')

def replace(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)

p=ROOT/'StationOnlineClient.java'
s=p.read_text('utf8')
s=replace(s,'''        try{return multiplayer(command("capabilities").put("itemId",item),cancel);}
        catch(StationApi.Failure e){if(e.status==404||e.status==503)throw new StationOnlineGame.Unavailable("A classificação por jogo e as novas salas aguardam publicação no servidor.");throw e;}''','''        return multiplayer(command("capabilities").put("itemId",item),cancel);''')
s=replace(s,'''        try{multiplayer(command("capabilities"),cancel);}catch(StationApi.Failure e){if(e.status!=404&&e.status!=503)throw e;}''','''        // Preserve the actual service failure; a status alone does not prove missing activation.
        multiplayer(command("capabilities"),cancel);''')
s=replace(s,'''            if(status==404||status==503)return "O serviço de salas ainda não está disponível neste servidor.";''','''            if(status==404)return "O servidor não encontrou o recurso solicitado para esta ação. Toque em Reconectar para consultar novamente.";
            if(status==503)return "O serviço de salas está indisponível no momento. Toque em Reconectar para tentar novamente.";''')
p.write_text(s,'utf8')

p=ROOT/'StationOnlineGame.java'
s=p.read_text('utf8')
anchor='    static String platform(String raw)throws IOException {'
s=replace(s,anchor,'''    static List<StationMultiplayerProfile> classifications(Context context,StationOnlineClient client,String itemId,StationApi.Cancellation cancel)throws Exception {
        StationCatalog.Item item=client.item(itemId);if(item==null)throw StationMultiplayerProfile.unavailable();
        return StationMultiplayerProfile.classifications(client.profileSnapshot(itemId,cancel),itemId,engine(context,item.platform));
    }
'''+anchor)
p.write_text(s,'utf8')

p=ROOT/'StationRoomsActivity.java'
s=p.read_text('utf8')
s=replace(s,'String notice="As novas salas aguardam ativação no servidor. A capa e os dados do jogo continuam disponíveis.";','String notice="";')
s=replace(s,'recordFailure(error);notice="Não foi possível consultar esta modalidade online. Seus dados e sua capa continuam disponíveis. Use Reconectar para tentar novamente.";','recordFailure(error);notice=StationOnlineClient.message(error);')
s=replace(s,'java.util.List<StationMultiplayerProfile> profiles=StationOnlineGame.profiles(this,client,target,check);','java.util.List<StationMultiplayerProfile> profiles=StationOnlineGame.classifications(this,client,target,check);')
s=replace(s,'for(int count:p.allowed)counts.add(count);detail.append(info.detail);','if(info.singlePlayerConfirmed)counts.add(1);for(int count:p.allowed)counts.add(count);detail.append(info.detail);')
s=replace(s,'if(brief.length()>0)brief.append(" jogadores").append(profiles.size()>1?" · "+profiles.size()+" modos":"");','if(brief.length()>0)brief.append(counts.size()==1&&counts.contains(1)?" jogador":" jogadores").append(profiles.size()>1?" · "+profiles.size()+" modos":"");')
s=replace(s,'}catch(Exception unavailable){runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)&&createInfo!=null)createInfo.setText(StationGamePlayerInfo.pending().detail);});}','}catch(Exception unavailable){if(!check.cancelled())recordFailure(unavailable);runOnUiThread(()->{if(active&&generation==epoch&&target.equals(heroRequestId)&&createInfo!=null)createInfo.setText(StationOnlineClient.message(unavailable));});}')
p.write_text(s,'utf8')
print('Applied reviewed readiness changes to three R79 files')
