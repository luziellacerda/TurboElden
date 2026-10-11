// SPDX-License-Identifier: WTFPL
package aenu.hardware;

/** Owner JNI identity, loaded privately by Ps3Bootstrap. */
public final class ProcessorInfo {
    private ProcessorInfo() {}
    public static native String gpu_get_physical_device_name_vk();
}
