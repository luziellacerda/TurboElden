package org.emulationstation.frontend;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Process;

public final class RestartActivity extends Activity {
    public static final String EXTRA_PID = "pid";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        int pid = getIntent().getIntExtra(EXTRA_PID, 0);
        if (pid > 0 && pid != Process.myPid()) {
            Process.killProcess(pid);
        }
        Intent launch = new Intent(this, (Class<?>) ESActivity.class);
        launch.addFlags(268468224);
        startActivity(launch);
        finish();
        Runtime.getRuntime().exit(0);
    }
}
