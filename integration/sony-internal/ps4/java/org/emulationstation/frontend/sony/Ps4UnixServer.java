package org.emulationstation.frontend.sony;

import android.net.LocalServerSocket;
import android.net.LocalSocket;
import android.net.LocalSocketAddress;
import android.os.ParcelFileDescriptor;
import android.os.Process;
import android.system.Os;
import android.system.OsConstants;
import android.system.ErrnoException;
import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

/** Filesystem AF_UNIX listener with an explicit owned descriptor, matching native pathname sockets. */
final class Ps4UnixServer implements Closeable {
    final File path;
    private final LocalServerSocket server;
    private final ParcelFileDescriptor owner;
    private boolean closed;
    Ps4UnixServer(File path) throws IOException {
        this.path=path;
        if (path.getAbsolutePath().getBytes(StandardCharsets.UTF_8).length>=108)
            throw new IOException("Caminho PS4 longo demais");
        if (path.exists()) throw new IOException("A sessão PS4 já existe");
        LocalSocket bound=new LocalSocket(LocalSocket.SOCKET_STREAM);
        ParcelFileDescriptor descriptor=null;
        LocalServerSocket listener=null;
        try {
            bound.bind(new LocalSocketAddress(path.getAbsolutePath(),LocalSocketAddress.Namespace.FILESYSTEM));
            descriptor=ParcelFileDescriptor.dup(bound.getFileDescriptor());
            listener=new LocalServerSocket(descriptor.getFileDescriptor());
        } catch (IOException e) {
            if (listener!=null) listener.close();
            if (descriptor!=null) descriptor.close();
            path.delete(); throw e;
        } finally { bound.close(); }
        owner=descriptor; server=listener;
    }
    LocalSocket accept() throws IOException {
        LocalSocket socket=server.accept();
        if (socket.getPeerCredentials().getUid()!=Process.myUid()) {
            socket.close(); throw new IOException("Sessão PS4 não autorizada");
        }
        return socket;
    }
    @Override public synchronized void close() throws IOException {
        if(closed)return;closed=true;
        // LocalServerSocket(FileDescriptor) borrows the FD. Shutdown also wakes accept().
        try {Os.shutdown(owner.getFileDescriptor(),OsConstants.SHUT_RDWR);}catch(ErrnoException ignored){}
        try { server.close(); } finally { owner.close(); path.delete(); }
    }
}
