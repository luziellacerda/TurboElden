package org.emulationstation.frontend;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;

public final class ImageBridge {
    private ImageBridge() {
    }

    public static int[] decode(byte[] data) {
        return decode(data, 0);
    }

    public static int[] decode(byte[] data, int wantedHeight) {
        if (data == null || data.length == 0) {
            return null;
        }
        try {
            BitmapFactory.Options options = new BitmapFactory.Options();
            if (wantedHeight > 0) {
                options.inJustDecodeBounds = true;
                BitmapFactory.decodeByteArray(data, 0, data.length, options);
                int sample = 1;
                while (options.outHeight > 0 && options.outHeight / (sample * 2) >= wantedHeight) {
                    sample *= 2;
                }
                options = new BitmapFactory.Options();
                options.inSampleSize = sample;
            }
            options.inPreferredConfig = Bitmap.Config.ARGB_8888;
            options.inScaled = false;
            options.inPremultiplied = false;
            Bitmap bitmap = BitmapFactory.decodeByteArray(data, 0, data.length, options);
            if (bitmap == null) {
                return null;
            }
            int width = bitmap.getWidth();
            int height = bitmap.getHeight();
            int[] result = new int[(width * height) + 2];
            result[0] = width;
            result[1] = height;
            bitmap.getPixels(result, 2, width, 0, 0, width, height);
            bitmap.recycle();
            return result;
        } catch (Exception e) {
            Log.e(ESActivity.TAG, "Could not decode an image", e);
            return null;
        } catch (OutOfMemoryError e2) {
            Log.e(ESActivity.TAG, "Out of memory decoding an image", e2);
            return null;
        }
    }
}
