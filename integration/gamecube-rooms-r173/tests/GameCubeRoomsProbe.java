import java.util.Arrays;
import org.emulationstation.frontend.netplay.StationGamePlayerInfo;

/** Exercise the signed presentation/roster gate, never grant a real server seat. */
public final class GameCubeRoomsProbe {
    static int checks;
    static void need(boolean value) { ++checks; if(!value) throw new AssertionError("check="+checks); }
    static StationGamePlayerInfo info(boolean approved,int max,int[] counts,String controller) {
        return StationGamePlayerInfo.fromVerifiedProfile(approved,max,counts,"local-multiplayer",controller);
    }
    static StationGamePlayerInfo.Participant member(int slot) {
        return new StationGamePlayerInfo.Participant(slot,"peer"+slot,"Player "+slot,false,slot==1);
    }
    public static void main(String[] args) {
        String controller="dolphin-gamecube-four-ports-v1";
        StationGamePlayerInfo game=info(true,4,new int[]{2,3,4},controller);
        if(args.length>0&&"baseline".equals(args[0])) {
            StationGamePlayerInfo.RoomInfo room=game.forRoom(2,true,new StationGamePlayerInfo.Participant[]{member(1)});
            need(!game.onlineApproved&&!room.confirmed&&!room.acceptingPlayers&&room.vacancies==-1);
            System.out.println("baselineReproduced=true checks="+checks);return;
        }
        need(game.onlineApproved);need(Arrays.equals(game.allowedPlayerCounts(),new int[]{2,3,4}));
        for(int capacity=2;capacity<=4;capacity++) {
            for(int count=1;count<=capacity;count++) {
                StationGamePlayerInfo.Participant[] people=new StationGamePlayerInfo.Participant[count];
                for(int i=0;i<count;i++)people[i]=member(i+1);
                StationGamePlayerInfo.RoomInfo room=game.forRoom(capacity,true,people);
                need(room.confirmed);need(room.capacity==capacity);need(room.present==count);
                need(room.vacancies==capacity-count);need(room.acceptingPlayers==(count<capacity));
                need(room.positions.size()==capacity);
            }
            StationGamePlayerInfo.Participant[] people=new StationGamePlayerInfo.Participant[capacity];
            for(int i=0;i<capacity;i++)people[i]=member(i+1);
            StationGamePlayerInfo.RoomInfo started=game.forRoom(capacity,false,people);
            need(started.confirmed);need(!started.acceptingPlayers);need(started.vacancies==0);
        }
        need(!info(false,4,new int[]{2,3,4},controller).onlineApproved);
        need(!info(true,5,new int[]{2,3,4,5},controller).onlineApproved);
        need(!info(true,4,new int[]{2,3},controller).onlineApproved);
        need(!info(true,4,new int[]{2,2,4},controller).onlineApproved);
        need(!info(true,4,new int[]{4,3},controller).onlineApproved);
        need(!info(true,4,new int[]{2,3,4},"invented-gamecube-profile").onlineApproved);
        need(!info(true,4,new int[]{2,3,4},"dolphin-wii-remotes-four-v1").onlineApproved);
        StationGamePlayerInfo two=info(true,2,new int[]{2},controller);
        need(two.onlineApproved);need(two.permits(2));need(!two.permits(3));
        need(!two.forRoom(3,true,new StationGamePlayerInfo.Participant[]{member(1)}).confirmed);
        need(!game.forRoom(2,true,new StationGamePlayerInfo.Participant[]{member(1),member(1)}).confirmed);
        need(!game.forRoom(2,true,new StationGamePlayerInfo.Participant[]{member(2)}).confirmed);
        need(!game.forRoom(2,true,new StationGamePlayerInfo.Participant[]{member(1),member(3)}).confirmed);
        need(!game.forRoom(2,false,new StationGamePlayerInfo.Participant[]{member(1)}).confirmed);
        StationGamePlayerInfo solo=info(true,1,new int[0],controller);
        need(solo.singlePlayerConfirmed);need(!solo.onlineApproved);
        System.out.println("gamecubeChecks="+checks+" physicalGameplayValidated=false");
    }
}
