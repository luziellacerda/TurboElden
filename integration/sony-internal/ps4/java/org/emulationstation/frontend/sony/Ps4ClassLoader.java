package org.emulationstation.frontend.sony;

import dalvik.system.DexClassLoader;

/** Child-first only for the explicitly isolated PS4 namespaces, never for Android/Station. */
final class Ps4ClassLoader extends DexClassLoader {
    Ps4ClassLoader(String dex,String optimized,String nativePath,ClassLoader parent) {
        super(dex,optimized,nativePath,parent);
    }
    @Override protected Class<?> loadClass(String name,boolean resolve) throws ClassNotFoundException {
        // Android ClassLoader has no Java SE getClassLoadingLock API.
        // Use the defining loader monitor for the same serialized load contract.
        synchronized (this) {
            Class<?> type=findLoadedClass(name);
            if (type==null && (name.startsWith("org.libsdl.app.") ||
                name.startsWith("com.bachatas4.android.runtime.") ||
                name.startsWith("org.emulationstation.ps4child."))) {
                type=findClass(name);
            }
            if (type==null) type=super.loadClass(name,false);
            if (resolve) resolveClass(type);
            return type;
        }
    }
}
