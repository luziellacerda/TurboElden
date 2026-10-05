package org.emulationstation.frontend.station;

import java.nio.file.Path;

/** Native decoder streams members into the checked Java installer; it never writes files. */
public final class StationArchive implements StationInstaller.Reader {
    private static final class Library {static {System.loadLibrary("station_archive");}static void ready() {}}
    public void read(Path file,StationInstaller.Sink sink,StationApi.Cancellation cancel)throws Exception {
        Library.ready();readArchive(file.toAbsolutePath().toString(),sink,cancel);
    }
    private static native void readArchive(String path,StationInstaller.Sink sink,StationApi.Cancellation cancel) throws Exception;
}
