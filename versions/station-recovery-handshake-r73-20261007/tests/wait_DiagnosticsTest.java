package org.emulationstation.frontend.netplay;

import java.util.concurrent.TimeUnit;

/** Executable pure-Java checks of the actual tunnel's bounded diagnostic sampler. */
public final class wait_DiagnosticsTest {
    private static int checks;
    private static void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    private static long sec(long value){return TimeUnit.SECONDS.toNanos(value);}
    private static String take(StationRecoveryTunnel.WaitDiagnostics d,long time,long epoch,long state){
        return d.sample(time,epoch,state,17,123,100,123,99,88,true,-1);
    }
    public static void main(String[] args){
        StationRecoveryTunnel.WaitDiagnostics d=new StationRecoveryTunnel.WaitDiagnostics();
        check(d.due(sec(100)),"first wait snapshot due");
        String expected="event=wait-diagnostic epoch=2 state=1 nativeStatus=17 tx.next=123 accepted=100 cursor=123 rx.next=99 rx.delivered=88 localReady=true readySent=-1";
        check(expected.equals(take(d,sec(100),2,1)),"only the requested fixed numeric/boolean tuple");
        check(!d.due(sec(100)),"not twice at same time");
        check(take(d,sec(109),2,1)==null,"no early repeated snapshot");
        check(!d.due(sec(110)-1),"ten-second floor");
        check(d.due(sec(110)),"ten-second interval opens");
        check(expected.equals(take(d,sec(110),2,1)),"unchanged wait can be measured at bounded interval");
        check(take(d,sec(119),99,0)==null,"epoch and state change do not bypass interval");
        for(int i=2;i<6;i++)check(take(d,sec(100+10*i),2,1)!=null,"snapshot within six-entry budget "+i);
        check(take(d,sec(160),2,1)==null,"no seventh snapshot");
        check(take(d,sec(3600),2,1)==null,"long wait stays silent");
        check(take(d,sec(3600),2,2)==null,"playing hides diagnostics and resets budget");
        check(take(d,sec(3601),3,0)!=null,"later genuine wait receives new budget");
        d.reset();check(d.due(sec(3601)),"explicit playing transition resets even between ticks");
        check(take(d,sec(3601),4,1)!=null,"reset takes immediate numeric snapshot");
        check(take(d,sec(3661),4,1)==null,"elapsed minute limit even with unused count");
        d.reset();check(take(d,-sec(50),0,0)!=null,"nanoTime may be negative");
        check(take(d,-sec(41),0,0)==null,"negative clock still rate limited");
        check(take(d,-sec(40),0,0)!=null,"negative clock permits exact interval");
        d.reset();String unavailable=d.sample(0,0,0,-1,0,0,0,0,0,false,-1);
        check(unavailable.endsWith("localReady=false readySent=-1"),"unprepared local stream is represented without guessing");
        check(unavailable.contains("nativeStatus=-1"),"unknown native state is preserved");
        check(!unavailable.contains("ticket")&&!unavailable.contains("proof")&&!unavailable.contains("roomId")&&!unavailable.contains("path"),"no identifying or secret fields");
        System.out.println("wait_DiagnosticsTest: "+checks+" checks passed");
    }
}
