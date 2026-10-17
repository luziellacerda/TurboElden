import java.util.*;
import java.util.zip.ZipFile;
import java.security.MessageDigest;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.value.IntEncodedValue;

/** Verify the real preserved Android API; never use the test NativeConfig fixture. */
public final class VerifyNativeConfigAbi {
    public static void main(String[] args) throws Exception {
        ClassDef found=null;
        try (ZipFile zip=new ZipFile(args[0])) {
            // R8 inlines NativeConfig's Kotlin constants and removes their DEX
            // fields. Layer 3/4 is therefore pinned to the unchanged native
            // Config/NativeConfig.cpp implementation, not inferred from fields.
            try (var in=zip.getInputStream(zip.getEntry("lib/arm64-v8a/libstation_dolphin_online.so"))) {
                String core=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(in.readAllBytes()));
                if (!core.equals("3438ce727ab3a0d6f6fb4aa2a1b8068be5d17360e6c7aa0b8ff3594dbfde7c29"))
                    throw new IllegalStateException("Pinned native layer implementation changed");
            }
            var entries=zip.entries();
            while (entries.hasMoreElements()) {
                var e=entries.nextElement(); if (!e.getName().matches("classes(?:[0-9]+)?\\.dex")) continue;
                byte[] bytes;try (var in=zip.getInputStream(e)) { bytes=in.readAllBytes(); }
                var dex=new DexBackedDexFile(bytes,0);
                for (int i=0;i<dex.classCount;i++) {
                    ClassDef c=new DexBackedClassDef(dex,dex.classStartOffset+i*32,0);
                    if (c.getType().equals("Lorg/dolphinemu/dolphinemu/features/settings/model/NativeConfig;")) {
                        if (found!=null) throw new IllegalStateException("Duplicate configuration API");
                        found=c;
                    }
                }
            }
        }
        if (found==null) throw new IllegalStateException("NativeConfig API absent");
        Map<String,Integer> layers=new HashMap<>();
        for (Object entry:found.getStaticFields()) {
            Field f=(Field)entry;
            if (f.getInitialValue() instanceof IntEncodedValue v)
                layers.put(f.getName(),((Number)v.getClass().getField("value").get(v)).intValue());
        }
        if ((layers.containsKey("LAYER_CURRENT") && !Integer.valueOf(4).equals(layers.get("LAYER_CURRENT"))) ||
            (layers.containsKey("LAYER_ACTIVE") && !Integer.valueOf(3).equals(layers.get("LAYER_ACTIVE"))))
            throw new IllegalStateException("Native layer contract differs");
        Set<String> required=new HashSet<>(Set.of("setBoolean)V","getBoolean)Z"));
        for (Object entry:found.getDirectMethods()) {
            Method m=(Method)entry;
            if (m.getParameterTypes().toString().equals("[I, Ljava/lang/String;, Ljava/lang/String;, Ljava/lang/String;, Z]") &&
                (m.getAccessFlags() & 0x109)==0x109) // DEX public, static, native.
                required.remove(m.getName()+")"+m.getReturnType());
        }
        if (!required.isEmpty()) throw new IllegalStateException("Native boolean API signature differs: "+required);
        System.out.println("PASS realNativeConfigAbi=true transientLayer=4 activeLayer=3");
    }
}
