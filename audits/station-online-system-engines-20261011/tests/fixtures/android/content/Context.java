package android.content;
import android.content.res.AssetManager;
/** Isolated JVM fixture: only getAssets is exercised, no Android execution. */
public final class Context {
    private final AssetManager assets;
    public Context(byte[] data){ assets = new AssetManager(data); }
    public AssetManager getAssets(){ return assets; }
}
