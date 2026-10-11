// SPDX-License-Identifier: WTFPL
// Actual 2.43 JNI ABI: ISO metadata receives both ISO and decryption-key FDs.
package aenu.aps3e;

public final class Emulator extends aenu.emulator.Emulator {
    public static volatile Emulator get;
    public static final class MetaInfo {
        public String eboot_path, iso_uri, name, serial, category, version;
        public int iso_fd = -1, dec_key_fd = -1, resolution, sound_format;
        public byte[] icon;
        public boolean decrypt;
    }
    public static final class CheatInfo {
        public static final int TYPE_U8 = 1;
        public static final int TYPE_U16 = 2;
        public static final int TYPE_U32 = 3;
        public static final int TYPE_U64 = 4;
        public static final long NOT_FOUND = -1L;
        public long addr, value;
        public int type;
    }
    public static final class GameTrophyInfo {
        public String game_name;
        public TrophyInfo[] trophies;
        public static final class TrophyInfo {
            public String description, icon_path, name;
            public long timestamp;
            public byte type;
            public boolean unlocked;
        }
    }
    public native int get_cpu_core_count();
    public native String get_cpu_name(int core);
    public native int get_cpu_max_mhz(int core);
    public native String simple_device_info();
    public native String[] get_native_llvm_cpu_list();
    public native String[] get_support_llvm_cpu_list();
    public native String[] get_vulkan_physical_dev_list();
    public native String generate_config_xml();
    public native String generate_strings_xml();
    public native String generate_java_string_arr();
    public native boolean install_firmware(int fd);
    public native MetaInfo meta_info_from_dir(String directory);
    public native MetaInfo meta_info_from_iso(int fd, int decryptionKeyFd, String uri);
    public native void setup_game_id(String serial);
    public native boolean install_edat(int fd);
    public native boolean install_pkg(int fd);
    public native boolean precompile_ppu_cache(String path);
    public native boolean precompile_ppu_cache(int fd);
    public native GameTrophyInfo trophy_info_from_dir(String realPath, String virtualPath);
    public native CheatInfo[] search_memory(CheatInfo info);
    public native void set_cheat(CheatInfo info);
    public native void get_cheat(CheatInfo info);
    public native void camera_frame(byte[] frame, int width, int height, int format);
}
