package org.emulationstation.frontend.netplay;
import java.io.IOException;
import org.dolphinemu.dolphinemu.features.settings.model.NativeConfig;
public final class GamecubeCpuPolicyProbe {
    public static void main(String[] args) throws Exception {
        int checks=0;
        for (String platform : new String[]{null,"","wii","psx","n64","snes","gamecubex"}) {
            NativeConfig.reset(); StationDolphinCpuPolicy.configure(platform);
            if (NativeConfig.writes!=0 || NativeConfig.reads!=0)
                throw new AssertionError("Unrequested platform changed");
            checks++;
        }
        NativeConfig.reset(); StationDolphinCpuPolicy.configure("gamecube");
        if (NativeConfig.writes!=1 || NativeConfig.reads!=1)
            throw new AssertionError("Missing transient override or verification");
        checks++;
        NativeConfig.reset(); NativeConfig.refuseReadback=true;
        try { StationDolphinCpuPolicy.configure("gamecube"); throw new AssertionError("Wrong effective mode admitted"); }
        catch (IOException expected) {
            if (!"DOLPHIN_GAMECUBE_CPU_MODE".equals(expected.getMessage())) throw expected;
            checks++;
        }
        NativeConfig.reset(); NativeConfig.rejectWrite=true;
        try { StationDolphinCpuPolicy.configure("gamecube"); throw new AssertionError("Native failure ignored"); }
        catch (java.lang.reflect.InvocationTargetException expected) { checks++; }
        System.out.println("PASS contracts="+checks+" fixturesOutsideApk=true");
    }
}
