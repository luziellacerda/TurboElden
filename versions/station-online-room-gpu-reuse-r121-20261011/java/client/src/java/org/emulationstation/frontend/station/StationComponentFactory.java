package org.emulationstation.frontend.station;

import android.app.Activity;
import android.app.AppComponentFactory;
import android.app.Application;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.ContentProvider;
import android.content.Intent;
import android.content.pm.ApplicationInfo;

/** Keep the original AndroidX factory and applications; add a presentation observer. */
public final class StationComponentFactory extends AppComponentFactory {
    private volatile AppComponentFactory original;

    private AppComponentFactory original(ClassLoader loader) throws InstantiationException {
        AppComponentFactory result=original;
        if(result!=null)return result;
        synchronized(this){
            if(original==null){
                try{
                    original=(AppComponentFactory)Class.forName("androidx.core.app.CoreComponentFactory",true,loader)
                            .getDeclaredConstructor().newInstance();
                }catch(ReflectiveOperationException|ClassCastException error){
                    InstantiationException failure=new InstantiationException("Original component factory unavailable");
                    failure.initCause(error);throw failure;
                }
            }
            return original;
        }
    }

    @Override public ClassLoader instantiateClassLoader(ClassLoader loader,ApplicationInfo info){
        try{return original(loader).instantiateClassLoader(loader,info);}
        catch(InstantiationException error){throw new IllegalStateException(error);}
    }
    @Override public Application instantiateApplication(ClassLoader loader,String name)
            throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        Application application=original(loader).instantiateApplication(loader,name);
        StationControllerPresence.install(application);
        return application;
    }
    @Override public Activity instantiateActivity(ClassLoader loader,String name,Intent intent)
            throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(loader).instantiateActivity(loader,name,intent);
    }
    @Override public Service instantiateService(ClassLoader loader,String name,Intent intent)
            throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(loader).instantiateService(loader,name,intent);
    }
    @Override public BroadcastReceiver instantiateReceiver(ClassLoader loader,String name,Intent intent)
            throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(loader).instantiateReceiver(loader,name,intent);
    }
    @Override public ContentProvider instantiateProvider(ClassLoader loader,String name)
            throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(loader).instantiateProvider(loader,name);
    }
}
