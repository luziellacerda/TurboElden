package org.emulationstation.frontend;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.util.Log;
import androidx.core.content.FileProvider;
import java.io.File;

public final class GameLauncher {
    private GameLauncher() {
    }

    public static String launch(Activity activity, String pkg, String cls, String action, String dataPath, String mime, int flags, boolean useContentUri, String[] extraKeys, String[] extraValues, String[] extraTypes) {
        Uri uri;
        try {
            Intent intent = new Intent();
            if (action != null && !action.isEmpty()) {
                intent.setAction(action);
            }
            if (cls != null && !cls.isEmpty()) {
                intent.setClassName(pkg, cls);
            } else {
                intent.setPackage(pkg);
            }
            if (dataPath != null && !dataPath.isEmpty()) {
                if (dataPath.contains("://")) {
                    uri = Uri.parse(dataPath);
                } else if (useContentUri) {
                    uri = FileProvider.getUriForFile(activity, activity.getPackageName() + ".fileprovider", new File(dataPath));
                    intent.addFlags(1);
                } else {
                    uri = Uri.fromFile(new File(dataPath));
                }
                if (mime != null && !mime.isEmpty()) {
                    intent.setDataAndType(uri, mime);
                } else {
                    intent.setData(uri);
                }
            }
            int count = extraKeys == null ? 0 : extraKeys.length;
            for (int i = 0; i < count; i++) {
                String key = extraKeys[i];
                String value = extraValues[i];
                String type = extraTypes[i];
                if ("int".equals(type)) {
                    intent.putExtra(key, parseInt(value));
                } else if ("bool".equals(type)) {
                    intent.putExtra(key, parseBool(value));
                } else {
                    intent.putExtra(key, value);
                }
            }
            try {
                intent.addFlags(flags);
                intent.addFlags(268435456);
                Log.i(ESActivity.TAG, "Starting " + intent);
                activity.startActivity(intent);
                return null;
            } catch (ActivityNotFoundException e) {
                e = e;
                Log.e(ESActivity.TAG, "Nothing can handle this intent", e);
                return "emulator not found: " + pkg + ((cls == null || cls.isEmpty()) ? "" : "/" + cls);
            } catch (SecurityException e2) {
                e = e2;
                Log.e(ESActivity.TAG, "Not allowed to start this intent", e);
                return "not allowed to start " + pkg + " (try content=1 in the launch command)";
            } catch (Exception e3) {
                e = e3;
                Log.e(ESActivity.TAG, "Could not start the emulator", e);
                return String.valueOf(e);
            }
        } catch (ActivityNotFoundException e4) {
            e = e4;
        } catch (SecurityException e5) {
            e = e5;
        } catch (Exception e6) {
            e = e6;
        }
    }

    private static int parseInt(String value) {
        try {
            if (!value.startsWith("0x") && !value.startsWith("0X")) {
                return Integer.parseInt(value);
            }
            return Integer.parseInt(value.substring(2), 16);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private static boolean parseBool(String value) {
        return "1".equals(value) || "true".equalsIgnoreCase(value);
    }
}
