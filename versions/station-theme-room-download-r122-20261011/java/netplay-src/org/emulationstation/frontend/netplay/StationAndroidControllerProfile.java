package org.emulationstation.frontend.netplay;

import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

/** Adapt the legacy Xbox Bluetooth profile only when Android reports standard mapped keys.
 * Asset copying restores the upstream profile before every launch, including disconnected pads.
 * No offline mappings, room slots, player ownership or native runtime are changed.
 */
final class StationAndroidControllerProfile {
    private static final String XBOX = "Xbox Wireless Controller";
    static void prepare(File directory) throws IOException {
        boolean found = false;
        for (int id : InputDevice.getDeviceIds()) {
            InputDevice device = InputDevice.getDevice(id);
            if (device == null || device.isVirtual() || device.getVendorId() != 1118
                    || device.getProductId() != 736 || !XBOX.equals(device.getName())) continue;
            if ((device.getSources() & InputDevice.SOURCE_GAMEPAD) != InputDevice.SOURCE_GAMEPAD) continue;
            boolean[] keys = device.hasKeys(KeyEvent.KEYCODE_BUTTON_A, KeyEvent.KEYCODE_BUTTON_B,
                    KeyEvent.KEYCODE_BUTTON_X, KeyEvent.KEYCODE_BUTTON_Y,
                    KeyEvent.KEYCODE_BUTTON_START, KeyEvent.KEYCODE_BUTTON_SELECT,
                    KeyEvent.KEYCODE_BUTTON_L1, KeyEvent.KEYCODE_BUTTON_R1);
            // Keep upstream mapping if any pad sharing this identity uses legacy keycodes.
            if (!standardKeys(keys)
                    || device.getMotionRange(MotionEvent.AXIS_LTRIGGER) == null
                    || device.getMotionRange(MotionEvent.AXIS_RTRIGGER) == null) return;
            found = true;
        }
        if (!found) return;
        File target = new File(directory, "android/Xbox One Wireless Controller.cfg");
        File temp = new File(target.getParentFile(), target.getName() + ".tmp");
        Files.write(temp.toPath(), standardProfile().getBytes(StandardCharsets.UTF_8));
        Files.move(temp.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
    }
    static boolean standardKeys(boolean[] keys) {
        if (keys == null || keys.length != 8) return false;
        for (boolean key : keys) if (!key) return false;
        return true;
    }
    static String standardProfile() {
        return "input_driver = \"android\"\n"
            + "input_device = \"Xbox Wireless Controller\"\n"
            + "input_device_display_name = \"Xbox / BSP-D3 (Android)\"\n"
            + "input_vendor_id = \"1118\"\ninput_product_id = \"736\"\n"
            + "input_b_btn = \"96\"\ninput_a_btn = \"97\"\n"
            + "input_y_btn = \"99\"\ninput_x_btn = \"100\"\n"
            + "input_start_btn = \"108\"\ninput_select_btn = \"109\"\n"
            + "input_l_btn = \"102\"\ninput_r_btn = \"103\"\n"
            + "input_l3_btn = \"106\"\ninput_r3_btn = \"107\"\n"
            + "input_l2_axis = \"+6\"\ninput_r2_axis = \"+7\"\n"
            + "input_up_btn = \"h0up\"\ninput_down_btn = \"h0down\"\n"
            + "input_left_btn = \"h0left\"\ninput_right_btn = \"h0right\"\n"
            + "input_l_x_plus_axis = \"+0\"\ninput_l_x_minus_axis = \"-0\"\n"
            + "input_l_y_plus_axis = \"+1\"\ninput_l_y_minus_axis = \"-1\"\n"
            + "input_r_x_plus_axis = \"+2\"\ninput_r_x_minus_axis = \"-2\"\n"
            + "input_r_y_plus_axis = \"+3\"\ninput_r_y_minus_axis = \"-3\"\n";
    }
}
