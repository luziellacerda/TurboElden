package android.content.res;
import java.io.*;
/** Reads the exact packaged engines bytes from a caller-supplied JVM fixture. */
public final class AssetManager {
    private final byte[] data;
    public AssetManager(byte[] data){ this.data = data.clone(); }
    public InputStream open(String name) throws IOException {
        if(!"station-online/engines.json".equals(name))throw new IOException("Unexpected fixture asset");
        return new ByteArrayInputStream(data);
    }
}
