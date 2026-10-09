package org.emulationstation.frontend.netplay;

import android.os.Bundle;
import android.os.Parcel;
import android.os.ResultReceiver;
import android.util.Log;

/** Only framework ResultReceiver parcels cross the private process boundary. */
final class StationSessionChannel {
    private StationSessionChannel() {}

    static ResultReceiver transport(ResultReceiver local) {
        if (local == null) return null;
        Parcel parcel = Parcel.obtain();
        try {
            local.writeToParcel(parcel, 0);
            parcel.setDataPosition(0);
            return ResultReceiver.CREATOR.createFromParcel(parcel);
        } finally {
            parcel.recycle();
        }
    }

    @SuppressWarnings("deprecation")
    static ResultReceiver read(Bundle data, String key) {
        if (data == null) return null;
        try {
            data.setClassLoader(ResultReceiver.class.getClassLoader());
            Object value = data.getParcelable(key);
            if (value instanceof ResultReceiver) return (ResultReceiver) value;
            Log.e("StationRooms", "session stage=invalid-receiver-type");
        } catch (RuntimeException error) {
            // A malformed callback must never kill the catalog's main process.
            Log.e("StationRooms", "session stage=invalid-receiver type=" + error.getClass().getSimpleName());
        }
        return null;
    }
}
