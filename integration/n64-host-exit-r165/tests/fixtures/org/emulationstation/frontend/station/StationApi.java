package org.emulationstation.frontend.station;

import java.io.IOException;

public final class StationApi {
    public static final class Cancellation {
        private boolean stopped;
        public void cancel(){stopped=true;}
        public boolean cancelled(){return stopped;}
    }
    public static final class Offline extends IOException {}
    public static final class Failure extends IOException {
        public final int status;
        public final String code;
        public Failure(int status,String code){this.status=status;this.code=code;}
    }
}
