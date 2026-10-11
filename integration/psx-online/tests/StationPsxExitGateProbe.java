package org.emulationstation.frontend.netplay;
import java.util.concurrent.CountDownLatch;
public final class StationPsxExitGateProbe {
    static int checks;
    static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
    public static void main(String[] args)throws Exception {
        CountDownLatch entered=new CountDownLatch(1),leave=new CountDownLatch(1);
        Thread owner=new Thread(()->{entered.countDown();try{leave.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}},"actual-SDL-owner-probe");
        check(!StationPsxExitGate.ended(owner)); // NEW is not completion.
        owner.start();entered.await();
        check(!StationPsxExitGate.ownerEnded(true,null,owner)); // SDL global was cleared, owner still alive.
        for(int flags=0;flags<8;flags++)check(!StationPsxExitGate.mayRetire((flags&1)!=0,(flags&2)!=0,(flags&4)!=0,null,owner));
        leave.countDown();owner.join();
        check(StationPsxExitGate.ownerEnded(true,null,owner));
        for(int flags=0;flags<8;flags++)check(StationPsxExitGate.mayRetire((flags&1)!=0,(flags&2)!=0,(flags&4)!=0,null,owner)==(flags==7));
        check(StationPsxExitGate.mayRetire(true,true,true,null,null)); // Human canceled before owner existed.
        check(!StationPsxExitGate.mayRetire(false,true,true,null,null)); // Failure never authorizes.
        check(!StationPsxExitGate.mayRetire(true,false,true,null,null)); // IO/Binder not closed.
        check(!StationPsxExitGate.mayRetire(true,true,false,null,null)); // Other app process forbidden.
        Thread next=new Thread(()->{});check(!StationPsxExitGate.mayRetire(true,true,true,next,null));
        System.out.println("PSX human exit gate checks="+checks);
    }
}
