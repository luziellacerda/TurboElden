package org.emulationstation.frontend.sony;

import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;

/** Actual aPS3e 2.43 ControlId values, verified from the pinned DEX. */
final class Ps3Input {
    private final aenu.aps3e.Emulator emulator;
    private final int[][] sources = new int[3][26]; // Touch, physical keys, physical axes.
    private final int[] values = new int[26];
    Ps3Input(aenu.aps3e.Emulator emulator) { this.emulator = emulator; }
    synchronized void control(int id, int value) {
        control(0, id, value);
    }
    private synchronized void control(int source, int id, int value) {
        if (id < 1 || id > 25) return;
        value = Math.max(0, Math.min(255, value));
        sources[source][id] = value;
        value = Math.max(sources[0][id],Math.max(sources[1][id],sources[2][id]));
        if (values[id] == value) return;
        values[id] = value; emulator.key_event(id, value != 0, value);
    }
    synchronized void releaseAll() {
        for (int id = 1; id <= 25; id++) {
            for (int source = 0; source < sources.length; source++) sources[source][id] = 0;
            if (values[id] != 0) { values[id] = 0; emulator.key_event(id, false, 0); }
        }
    }
    synchronized void releaseTouch() { for (int id = 1; id <= 25; id++) control(0,id,0); }
    boolean key(KeyEvent event) {
        int id;
        switch (event.getKeyCode()) {
            case KeyEvent.KEYCODE_DPAD_LEFT: id = 1; break;
            case KeyEvent.KEYCODE_DPAD_UP: id = 2; break;
            case KeyEvent.KEYCODE_DPAD_RIGHT: id = 3; break;
            case KeyEvent.KEYCODE_DPAD_DOWN: id = 4; break;
            case KeyEvent.KEYCODE_BUTTON_X: id = 5; break;
            case KeyEvent.KEYCODE_BUTTON_A: id = 6; break;
            case KeyEvent.KEYCODE_BUTTON_B: id = 7; break;
            case KeyEvent.KEYCODE_BUTTON_Y: id = 8; break;
            case KeyEvent.KEYCODE_BUTTON_L1: id = 17; break;
            case KeyEvent.KEYCODE_BUTTON_L2: id = 18; break;
            case KeyEvent.KEYCODE_BUTTON_THUMBL: id = 19; break;
            case KeyEvent.KEYCODE_BUTTON_R1: id = 20; break;
            case KeyEvent.KEYCODE_BUTTON_R2: id = 21; break;
            case KeyEvent.KEYCODE_BUTTON_THUMBR: id = 22; break;
            case KeyEvent.KEYCODE_BUTTON_START: id = 23; break;
            case KeyEvent.KEYCODE_BUTTON_SELECT: id = 24; break;
            case KeyEvent.KEYCODE_BUTTON_MODE: id = 25; break;
            default: return false;
        }
        if (event.getAction() != KeyEvent.ACTION_DOWN && event.getAction() != KeyEvent.ACTION_UP) return false;
        control(1, id, event.getAction() == KeyEvent.ACTION_DOWN ? 255 : 0); return true;
    }
    boolean motion(MotionEvent event) {
        if ((event.getSource() & InputDevice.SOURCE_JOYSTICK) != InputDevice.SOURCE_JOYSTICK) return false;
        if (event.getActionMasked() != MotionEvent.ACTION_MOVE) return false;
        axis(event, MotionEvent.AXIS_X, 9, 11);
        axis(event, MotionEvent.AXIS_Y, 10, 12);
        axis(event, MotionEvent.AXIS_Z, 13, 15);
        axis(event, MotionEvent.AXIS_RZ, 14, 16);
        axis(event, MotionEvent.AXIS_HAT_X, 1, 3);
        axis(event, MotionEvent.AXIS_HAT_Y, 2, 4);
        trigger(event, MotionEvent.AXIS_LTRIGGER, MotionEvent.AXIS_BRAKE, 18);
        trigger(event, MotionEvent.AXIS_RTRIGGER, MotionEvent.AXIS_GAS, 21);
        return true;
    }
    private void axis(MotionEvent event, int axis, int negative, int positive) {
        if (!hasAxis(event, axis)) return; // Do not erase digital keys for absent hat/stick axes.
        float value = centered(event, axis);
        control(2, negative, value < 0 ? Math.round(-value * 255) : 0);
        control(2, positive, value > 0 ? Math.round(value * 255) : 0);
    }
    private void trigger(MotionEvent event, int axis, int fallback, int id) {
        InputDevice device = event.getDevice();
        int selected = device != null && device.getMotionRange(axis, event.getSource()) != null ? axis : fallback;
        if (!hasAxis(event, selected)) return; // Preserve L2/R2 key events on digital controllers.
        control(2, id, Math.round(Math.max(0, centered(event, selected)) * 255));
    }
    private float centered(MotionEvent event, int axis) {
        InputDevice device = event.getDevice();
        InputDevice.MotionRange range = device == null ? null : device.getMotionRange(axis, event.getSource());
        if (range == null) return 0;
        float value = event.getAxisValue(axis);
        return Math.abs(value) <= range.getFlat() ? 0 : Math.max(-1, Math.min(1, value));
    }
    private boolean hasAxis(MotionEvent event, int axis) {
        InputDevice device = event.getDevice();
        return device != null && device.getMotionRange(axis, event.getSource()) != null;
    }
    static boolean physicalControllerPresent() {
        for (int id : InputDevice.getDeviceIds()) {
            InputDevice device = InputDevice.getDevice(id);
            if (device != null && !device.isVirtual() &&
                (device.supportsSource(InputDevice.SOURCE_GAMEPAD) || device.supportsSource(InputDevice.SOURCE_JOYSTICK)))
                return true;
        }
        return false;
    }
}
