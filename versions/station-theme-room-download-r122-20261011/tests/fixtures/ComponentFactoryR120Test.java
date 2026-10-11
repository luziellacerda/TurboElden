package org.emulationstation.frontend.station;

import android.app.*;
import android.content.*;
import android.content.pm.ApplicationInfo;
import androidx.core.app.CoreComponentFactory;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicReference;

/** Host fixture only: real Station factory/presence, stub Android/AndroidX APIs. */
public final class ComponentFactoryR120Test {
    private static int checks;
    private static void check(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError("check " + checks + ": " + message);
    }
    private static void arguments(ClassLoader loader, String name, Intent intent) {
        check(CoreComponentFactory.lastLoader == loader, "ClassLoader reference preserved");
        check(CoreComponentFactory.lastName == name, "class name reference preserved");
        check(CoreComponentFactory.lastIntent == intent, "Intent reference preserved");
    }
    private static ClassLoader absentDelegate() {
        return new ClassLoader(ComponentFactoryR120Test.class.getClassLoader()) {
            @Override protected Class<?> loadClass(String name, boolean resolve)
                    throws ClassNotFoundException {
                if (name.equals("androidx.core.app.CoreComponentFactory"))
                    throw new ClassNotFoundException("fixture: delegate deliberately absent");
                return super.loadClass(name, resolve);
            }
        };
    }
    public static void main(String[] ignored) throws Exception {
        ClassLoader loader = ComponentFactoryR120Test.class.getClassLoader();
        String name = new String("original.component.Name");
        Intent intent = new Intent();
        ApplicationInfo info = new ApplicationInfo();
        StationComponentFactory factory = new StationComponentFactory();
        int before = CoreComponentFactory.constructions.get();

        check(factory.instantiateClassLoader(loader, info) == CoreComponentFactory.resultLoader,
                "original ClassLoader result preserved");
        check(CoreComponentFactory.lastLoader == loader, "input ClassLoader preserved");
        check(CoreComponentFactory.lastInfo == info, "ApplicationInfo reference preserved");
        Application first = factory.instantiateApplication(loader, name);
        check(first == CoreComponentFactory.application, "original Application preserved");
        arguments(loader, name, null);
        check(first.callbacks.size() == 1, "presence registered once for Application");
        Object observer = first.callbacks.get(0);
        check(factory.instantiateApplication(loader, name) == first, "same Application returned unchanged");
        check(first.callbacks.size() == 1 && first.callbacks.get(0) == observer,
                "same Application never registers another observer");

        check(factory.instantiateActivity(loader, name, intent) == CoreComponentFactory.activity,
                "original Activity preserved");
        arguments(loader, name, intent);
        check(factory.instantiateService(loader, name, intent) == CoreComponentFactory.service,
                "original Service preserved");
        arguments(loader, name, intent);
        check(factory.instantiateReceiver(loader, name, intent) == CoreComponentFactory.receiver,
                "original Receiver preserved");
        arguments(loader, name, intent);
        check(factory.instantiateProvider(loader, name) == CoreComponentFactory.provider,
                "original Provider preserved");
        arguments(loader, name, null);
        check(first.callbacks.size() == 1, "component creation never installs more presence callbacks");
        check(CoreComponentFactory.constructions.get() == before + 1, "delegate constructed only once");

        CoreComponentFactory.application = new Application();
        Application second = factory.instantiateApplication(loader, name);
        check(second != first && second == CoreComponentFactory.application, "second original Application preserved");
        check(second.callbacks.size() == 1 && first.callbacks.size() == 1,
                "one independent observer per Application");

        InstantiationException originalError = new InstantiationException("fixture delegate failure");
        CoreComponentFactory.failure = originalError;
        for (int component = 0; component < 5; component++) {
            try {
                if (component == 0) factory.instantiateApplication(loader, name);
                else if (component == 1) factory.instantiateActivity(loader, name, intent);
                else if (component == 2) factory.instantiateService(loader, name, intent);
                else if (component == 3) factory.instantiateReceiver(loader, name, intent);
                else factory.instantiateProvider(loader, name);
                throw new AssertionError("delegate error was swallowed");
            } catch (InstantiationException error) {
                check(error == originalError, "delegate exception identity preserved");
            }
        }
        CoreComponentFactory.failure = null;
        check(second.callbacks.size() == 1, "failed application construction adds no callback");
        RuntimeException loaderError = new IllegalStateException("fixture ClassLoader failure");
        CoreComponentFactory.loaderFailure = loaderError;
        try { factory.instantiateClassLoader(loader, info); throw new AssertionError("ClassLoader error swallowed"); }
        catch (RuntimeException error) { check(error == loaderError, "ClassLoader exception preserved"); }
        CoreComponentFactory.loaderFailure = null;

        try {
            new StationComponentFactory().instantiateApplication(absentDelegate(), name);
            throw new AssertionError("missing delegate silently fell back");
        } catch (InstantiationException error) {
            check(error.getCause() instanceof ClassNotFoundException, "missing delegate reports original cause");
        }
        try {
            new StationComponentFactory().instantiateClassLoader(absentDelegate(), info);
            throw new AssertionError("missing delegate ClassLoader silently fell back");
        } catch (IllegalStateException error) {
            check(error.getCause() instanceof InstantiationException, "missing delegate ClassLoader fails explicitly");
            check(error.getCause().getCause() instanceof ClassNotFoundException, "ClassLoader failure retains cause");
        }
        check(second.callbacks.size() == 1, "absent delegate adds no callback");

        StationComponentFactory concurrent = new StationComponentFactory();
        CountDownLatch start = new CountDownLatch(1);
        AtomicReference<Throwable> failed = new AtomicReference<>();
        Thread[] threads = new Thread[8];
        int concurrentBefore = CoreComponentFactory.constructions.get();
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                try {
                    start.await();
                    if (concurrent.instantiateActivity(loader, name, intent) != CoreComponentFactory.activity)
                        throw new AssertionError("concurrent delegated Activity changed");
                } catch (Throwable error) { failed.compareAndSet(null, error); }
            });
            threads[i].start();
        }
        start.countDown();
        for (Thread thread : threads) thread.join();
        check(failed.get() == null, "concurrent initialization preserves delegate results");
        check(CoreComponentFactory.constructions.get() == concurrentBefore + 1,
                "concurrent initialization constructs one delegate");
        System.out.println("PASS " + checks + " checks (real factory/presence; host API stubs; no Android/gameplay)");
    }
}
