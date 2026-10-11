package org.emulationstation.frontend.netplay;

public final class StationSinglePassAnimationStateProbe {
    private static void require(boolean value,String message){if(!value)throw new AssertionError(message);}
    public static void main(String[] args){
        StationSinglePassAnimationState failed=new StationSinglePassAnimationState();int decodeCalls=0;
        for(int i=0;i<10000;i++)if(failed.beginLoad()){decodeCalls++;failed.finishLoad(false);}
        require(decodeCalls==1,"a permanent decode failure must be attempted exactly once");
        require(failed.loadFailed(),"failed load is terminal");

        StationSinglePassAnimationState ready=new StationSinglePassAnimationState();
        require(ready.beginLoad(),"first successful load starts");ready.finishLoad(true);
        require(!ready.beginLoad()&&ready.loadReady(),"successful load cannot be duplicated");
        ready.resetPlayback();ready.setRunning(true,100);require(ready.frameTime(150,200)==50,"clock advances");
        ready.setRunning(false,160);require(ready.frameTime(1000,200)==60,"clock pauses");
        ready.setRunning(true,1100);require(ready.frameTime(1300,200)==60,"fallback wraps continuously");
        require(ready.shouldContinue(),"visible fallback keeps rendering");
        ready.setRunning(false,1310);require(!ready.shouldContinue(),"hidden fallback stops rendering");
        require(ready.frameTime(9000,200)==70,"hidden fallback clock stays paused");
        System.out.println("StationSinglePassAnimationStateProbe: 10 checks passed");
    }
}
