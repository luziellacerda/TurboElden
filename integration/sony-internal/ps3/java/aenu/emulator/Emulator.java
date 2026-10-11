// SPDX-License-Identifier: WTFPL
// JNI identities and signatures preserved from the pinned official aPS3e 2.43.
package aenu.emulator;

import android.view.Surface;

public class Emulator {
    public static final class BootException extends Exception {
        public BootException() { super(); }
        public BootException(String message) { super(message); }
    }
    public static final class ConfigFileException extends Exception {
        public ConfigFileException() { super(); }
    }
    public static final class Path {
        public String uri;
        public int fd = -1;
        public int dec_key_fd = -1;
        public static Path from(String uri, int fd, int keyFd) {
            Path path = new Path(); path.uri = uri; path.fd = fd; path.dec_key_fd = keyFd;
            return path;
        }
    }
    public static final class Config implements AutoCloseable {
        private long n_handle;
        private String config_path;
        private native long native_open_config(String text);
        private native long native_open_config_file(String path);
        private native String native_close_config(long handle);
        private native void native_close_config_file(long handle, String path);
        private native String native_load_config_entry(long handle, String tag);
        private native String[] native_load_config_entry_ty_arr(long handle, String tag);
        private native String[] native_list_children(long handle, String tag);
        private native void native_save_config_entry(long handle, String tag, String value);
        private native void native_save_config_entry_ty_arr(long handle, String tag, String[] value);
        public static Config open(String text) throws ConfigFileException {
            Config config = new Config(); config.n_handle = config.native_open_config(text);
            if (config.n_handle == 0) throw new ConfigFileException();
            return config;
        }
        public static Config openFile(String path) throws ConfigFileException {
            Config config = new Config(); config.config_path = path;
            config.n_handle = config.native_open_config_file(path);
            if (config.n_handle == 0) throw new ConfigFileException();
            return config;
        }
        public String load(String tag) { requireOpen(); return native_load_config_entry(n_handle, tag); }
        public String[] children(String tag) { requireOpen(); return native_list_children(n_handle, tag); }
        public void save(String tag, String value) { requireOpen(); native_save_config_entry(n_handle, tag, value); }
        public String closeText() {
            requireOpen(); long handle = n_handle; n_handle = 0;
            return native_close_config(handle);
        }
        private void requireOpen() { if (n_handle == 0) throw new IllegalStateException("Configuration is closed"); }
        @Override public void close() {
            if (n_handle != 0) { long handle = n_handle; n_handle = 0; native_close_config(handle); }
        }
    }
    public native void setup_game_path(String path);
    public native void setup_game_path(Path path);
    public native void setup_surface(Surface surface);
    public native void boot() throws BootException;
    public native void key_event(int keyCode, boolean pressed, int value);
    public native void quit();
    public native boolean is_running();
    public native boolean is_paused();
    public native void pause();
    public native void resume();
    public native void change_surface(int width, int height);
}
