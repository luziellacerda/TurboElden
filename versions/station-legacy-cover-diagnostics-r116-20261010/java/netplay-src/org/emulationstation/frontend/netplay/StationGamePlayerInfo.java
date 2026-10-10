package org.emulationstation.frontend.netplay;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Presentation only. Call after exact signed profile verification; never grants a seat.
 * Catalog/history player counts intentionally are not inputs to this class. */
public final class StationGamePlayerInfo {
    public final boolean onlineApproved, singlePlayerConfirmed, modeConfirmed;
    public final String capacityLabel, modeLabel, participationLabel, controlsLabel;
    public final String summary, detail;
    private final int[] allowed;

    private StationGamePlayerInfo(boolean online, boolean single, int[] counts,
            String capacity, String mode, boolean modeKnown, String participation,
            String controls, String explanation) {
        onlineApproved=online;singlePlayerConfirmed=single;allowed=counts.clone();
        capacityLabel=capacity;modeLabel=mode;modeConfirmed=modeKnown;
        participationLabel=participation;controlsLabel=controls;
        summary=capacity+(modeKnown?" · "+mode:"");
        detail=explanation;
    }

    public static StationGamePlayerInfo pending() {
        return new StationGamePlayerInfo(false,false,new int[0],
                "Jogadores online a confirmar","Modo de jogo a confirmar",false,
                "Participação a confirmar","Controles a confirmar",
                "O modo online desta edição ainda aguarda confirmação de jogadores e controles. As vagas serão exibidas após a aprovação.");
    }

    /** approved must originate in the already verified profile, not catalog metadata. */
    public static StationGamePlayerInfo fromVerifiedProfile(boolean approved,int maximumPlayers,
            int[] allowedCounts,String mode,String controllerProfile) {
        if(!approved||allowedCounts==null)return pending();
        if(maximumPlayers==1&&allowedCounts.length==0)
            return new StationGamePlayerInfo(false,true,new int[0],"1 jogador",
                    "Individual",true,"Um jogador","Controles individuais",
                    "Esta edição foi confirmada para um jogador. Não há sala online aprovada para este modo.");
        if(maximumPlayers<2||maximumPlayers>5||allowedCounts.length<1||allowedCounts.length>4)return pending();
        int previous=1;
        for(int count:allowedCounts){if(count<=previous||count>maximumPlayers)return pending();previous=count;}
        if(previous!=maximumPlayers)return pending();
        String controls;
        if("standard-2p-v1".equals(controllerProfile)&&maximumPlayers==2)
            controls="Um controle por jogador";
        else if("snes-multitap-port2-v1".equals(controllerProfile))
            controls="Controles do SNES · Multitap automático";
        else if("megadrive-sega-teamplayer-v1".equals(controllerProfile))
            controls="Controles do Mega Drive · Team Player automático";
        else if("megadrive-ea-4way-v1".equals(controllerProfile))
            controls="Controles do Mega Drive · EA 4 Way automático";
        else if("direct-four-ports-v1".equals(controllerProfile)&&maximumPlayers<=4)
            controls="Um controle exclusivo por jogador · portas P1 a P4";
        else if("psx-dualshock-2p-v1".equals(controllerProfile)&&maximumPlayers==2)
            controls="Um controle DualShock por jogador";
        else return pending();
        String modeText,participation;boolean known=true;
        if("simultaneous".equals(mode)){modeText="Simultâneo";participation="Todos jogam ao mesmo tempo";}
        else if("alternating".equals(mode)){modeText="Alternado";participation="Um jogador por vez";}
        else if("battle-single".equals(mode)){modeText="Batalha individual";participation="Todos jogam ao mesmo tempo";}
        else if("battle-team".equals(mode)){modeText="Batalha em equipes";participation="Todos jogam ao mesmo tempo";}
        else{modeText="Modo de jogo a confirmar";participation="Participação simultânea ou alternada a confirmar";known=false;}
        String capacity="Online: "+joinCounts(allowedCounts)+" jogadores";
        return new StationGamePlayerInfo(true,false,allowedCounts,capacity,modeText,known,
                participation,controls,capacity+". "+modeText+". "+participation+". "+controls+".");
    }

    private static String joinCounts(int[] counts) {
        StringBuilder text=new StringBuilder();
        for(int i=0;i<counts.length;i++){
            if(i>0)text.append(i==counts.length-1?" ou ":", ");
            text.append(counts[i]);
        }
        return text.toString();
    }

    public boolean permits(int count){for(int value:allowed)if(value==count)return true;return false;}
    public int[] allowedPlayerCounts(){return allowed.clone();}

    /** Help arrives inside the same signed, exact profile as its player limits. */
    public StationGamePlayerInfo withHelp(String title,String[] instructions,String[] sources){
        if(!onlineApproved&&!singlePlayerConfirmed)return this;
        boolean named=title!=null&&!title.isEmpty();String label=named?title:modeLabel;
        StringBuilder explanation=new StringBuilder(capacityLabel).append(". ").append(label).append(". ").append(participationLabel).append(". ").append(controlsLabel).append('.');
        if(instructions!=null)for(String line:instructions)explanation.append("\n").append(line);
        if(sources!=null&&sources.length>0){explanation.append("\nSuporte confirmado na documentação do jogo e do motor:");for(String source:sources)explanation.append("\n").append(source);}
        return new StationGamePlayerInfo(onlineApproved,singlePlayerConfirmed,allowed,capacityLabel,label,modeConfirmed||named,participationLabel,controlsLabel,explanation.toString());
    }

    /** A roster entry must come from the signed room, not the online people page. */
    public static final class Participant {
        public final int slot;public final String peerId,name;public final boolean ready,self;
        public Participant(int slot,String peerId,String name,boolean ready,boolean self){
            this.slot=slot;this.peerId=peerId;this.name=name;this.ready=ready;this.self=self;
        }
    }
    public static final class Position {
        public final int slot;public final boolean occupied,ready,self,host;
        public final String label,name,status;
        private Position(int slot,Participant participant,boolean waiting){
            this.slot=slot;label="P"+slot;occupied=participant!=null;
            host=slot==1&&occupied;ready=occupied&&participant.ready;self=occupied&&participant.self;
            name=occupied?displayName(participant.name):"Vaga livre";
            status=!occupied?"Aguardando jogador":!waiting?"Na partida":ready?"Pronto":"Ainda não confirmou";
        }
    }
    public static final class RoomInfo {
        public final boolean confirmed,acceptingPlayers;
        public final int present,capacity,vacancies;
        public final String occupancyLabel,positionsLabel,summary,detail;
        public final List<Position> positions;
        private RoomInfo(boolean confirmed,boolean accepting,int present,int capacity,int vacancies,
                String occupancy,List<Position> positions,StationGamePlayerInfo game){
            this.confirmed=confirmed;acceptingPlayers=accepting;this.present=present;this.capacity=capacity;this.vacancies=vacancies;
            occupancyLabel=occupancy;this.positions=Collections.unmodifiableList(new ArrayList<Position>(positions));
            StringBuilder labels=new StringBuilder();for(Position position:positions){if(labels.length()>0)labels.append(" · ");labels.append(position.label);}
            positionsLabel=labels.toString();summary=occupancy+(game.modeConfirmed?" · "+game.modeLabel:"");
            detail=confirmed?occupancy+". "+game.detail:game.onlineApproved?
                    "A lista de participantes precisa ser confirmada novamente antes de mostrar as vagas.":game.detail;
        }
    }

    /** waiting is true only for the signed room state "waiting". Started rooms
     * have a frozen roster: a historical room capacity does not mean open seats. */
    public RoomInfo forRoom(int roomCapacity,boolean waiting,Participant[] participants){
        if(!onlineApproved||!permits(roomCapacity)||participants==null||participants.length<1||participants.length>roomCapacity)
            return unknownRoom();
        Participant[] bySlot=new Participant[roomCapacity+1];Set<String> ids=new HashSet<String>();int selfCount=0;
        for(Participant participant:participants){
            if(participant==null||participant.slot<1||participant.slot>roomCapacity||bySlot[participant.slot]!=null||
                    participant.peerId==null||participant.peerId.trim().isEmpty()||!ids.add(participant.peerId)||participant.self&&++selfCount>1)
                return unknownRoom();
            bySlot[participant.slot]=participant;
        }
        if(bySlot[1]==null||!waiting&&!permits(participants.length))return unknownRoom();
        int present=participants.length,vacancies=waiting?roomCapacity-present:0;
        List<Position> positions=new ArrayList<Position>();
        for(int slot=1;slot<=roomCapacity;slot++)if(waiting||bySlot[slot]!=null)positions.add(new Position(slot,bySlot[slot],waiting));
        String occupancy=waiting?present+" de "+roomCapacity+" jogadores · "+(vacancies==0?"Sala completa":vacancies==1?"1 vaga":vacancies+" vagas"):
                present+" jogadores na partida";
        return new RoomInfo(true,waiting&&vacancies>0,present,roomCapacity,vacancies,occupancy,positions,this);
    }
    private RoomInfo unknownRoom(){return new RoomInfo(false,false,-1,-1,-1,"Participantes a confirmar",Collections.<Position>emptyList(),this);}
    private static String displayName(String name){
        if(name==null)return "Nome não disponível";
        StringBuilder clean=new StringBuilder();for(int i=0;i<name.length()&&clean.length()<80;i++){char c=name.charAt(i);if(!Character.isISOControl(c))clean.append(c);}
        String result=clean.toString().trim();return result.isEmpty()?"Nome não disponível":result;
    }
}
