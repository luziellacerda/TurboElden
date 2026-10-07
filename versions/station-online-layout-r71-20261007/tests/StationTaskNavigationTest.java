package org.emulationstation.frontend.netplay;
import org.emulationstation.frontend.auth.StationTaskPolicy;
import org.emulationstation.frontend.auth.StationTaskPolicy.Task;

/** Host policy fixtures; Android task execution is a separate device validation. */
public final class StationTaskNavigationTest {
    private static int checks;
    private static void ok(boolean value){checks++;if(!value)throw new AssertionError("navigation check "+checks);}
    private static Task task(int id,String base,String top){return new Task(id,base,top,true,true);}
    public static void main(String[] args){
        String es=StationTaskPolicy.FRONTEND,rooms=StationTaskPolicy.ROOMS,game=StationTaskPolicy.GAME,menu=StationTaskPolicy.NETPLAY;
        ok(StationTaskPolicy.resumeTask(new Task[0],-1)==-1);
        Task frontend=task(1,es,es),lobby=task(2,rooms,rooms);
        ok(StationTaskPolicy.resumeTask(new Task[]{lobby,frontend},-1)==1);
        ok(StationTaskPolicy.resumeTask(new Task[]{lobby},-1)==2);
        ok(StationTaskPolicy.resumeTask(new Task[]{task(3,menu,rooms)},-1)==3);
        for(String top:new String[]{es,rooms,menu,game,"child.configuration.Activity"}){
            Task stack=task(1,es,top);
            ok(StationTaskPolicy.resumeTask(new Task[]{stack},-1)==1);
            ok(StationTaskPolicy.gameTask(new Task[]{stack},1)==1); // Registered game survives child configuration.
            ok(StationTaskPolicy.gameTask(new Task[]{stack},-1)==(game.equals(top)?1:-1));
        }
        for(String local:StationTaskPolicy.LOCAL_GAMES){
            Task running=task(9,local,local),child=task(9,local,"child.configuration.Activity");
            ok(StationTaskPolicy.gameTask(new Task[]{frontend,running},-1)==9);
            ok(StationTaskPolicy.resumeTask(new Task[]{frontend,running},-1)==9);
            ok(StationTaskPolicy.resumeTask(new Task[]{frontend,child},-1)==9);
            ok(StationTaskPolicy.resumeTask(new Task[]{task(1,es,local)},-1)==1);
            ok(!StationTaskPolicy.localGame(local+".Settings"));
            ok(StationTaskPolicy.resumeTask(new Task[]{new Task(9,local,local,false,true),frontend},9)==1);
            ok(StationTaskPolicy.resumeTask(new Task[]{new Task(9,local,local,true,false),frontend},9)==1);
        }
        for(String denied:new String[]{"org.emulationstation.frontend.auth.LoginActivity","org.emulationstation.frontend.RestartActivity","com.armsx2.BootSplashActivity","org.vita3k.emulator.MainActivity","com.izzy2lost.x1box.SettingsActivity","unknown.Activity"}){
            ok(StationTaskPolicy.resumeTask(new Task[]{task(9,denied,denied)},-1)==-1);
            ok(StationTaskPolicy.gameTask(new Task[]{task(9,denied,denied)},-1)==-1);
        }
        for(int mask=0;mask<16;mask++)ok(StationTaskPolicy.canSelectItem((mask&1)!=0,(mask&2)!=0,(mask&4)!=0,(mask&8)!=0)==(mask==1));
        ok(StationTaskPolicy.gameTask(new Task[]{task(2,rooms,game),task(1,es,game)},1)==1);
        ok(StationTaskPolicy.gameTask(new Task[]{task(2,rooms,game)},123)==2);
        ok(StationTaskPolicy.resumeTask(new Task[]{new Task(-1,es,es,true,true)},-1)==-1);
        System.out.println("StationTaskNavigationTest: "+checks+" checks passed");
    }
}
