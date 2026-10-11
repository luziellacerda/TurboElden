// SPDX-License-Identifier: WTFPL
package aenu.lang;

/** No static library lookup: Ps3Bootstrap loads the verified private library first. */
public final class System {
    private System() {}
    public static native void setenv(String key, String value, boolean overwrite);
    public static void setenv(String key, String value) { setenv(key, value, true); }
}
