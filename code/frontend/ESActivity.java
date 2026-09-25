package org.emulationstation.frontend;

import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Process;
import android.os.StrictMode;
import android.provider.Settings;
import android.util.Log;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.Writer;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import kotlin.UByte;
import org.apache.commons.codec.digest.MessageDigestAlgorithms;
import org.apache.commons.compress.archivers.ArchiveStreamFactory;
import org.apache.commons.compress.archivers.sevenz.SevenZArchiveEntry;
import org.apache.commons.compress.archivers.sevenz.SevenZFile;
import org.apache.commons.lang3.CharEncoding;
import org.libsdl.app.SDLActivity;

public class ESActivity extends SDLActivity {
    private static final String HOME_DIR_NAME = "EmulationStation";
    private static final String PROFILE_IMAGE_PREFIX = "profile_";
    private static final int PROFILE_IMAGE_SIZE = 512;
    static final int PROFILE_PICK_CANCELLED = 3;
    static final int PROFILE_PICK_IDLE = 0;
    static final int PROFILE_PICK_PICKING = 1;
    static final int PROFILE_PICK_SAVED = 2;
    private static final int REQUEST_LEGACY_STORAGE = 4242;
    private static final int REQUEST_NOTIFICATIONS = 4243;
    private static final int REQUEST_PROFILE_IMAGE = 4244;
    public static final String TAG = "EmulationStation";
    private static ESActivity sInstance;
    private static boolean sNotificationsRequested;
    private static volatile int sProfilePickState = 0;
    private static boolean sStorageRequested;

    static Context getAppContext() {
        if (sInstance != null) {
            return sInstance.getApplicationContext();
        }
        return null;
    }

    public static String getHardwareId() {
        String id;
        Context context = getAppContext();
        if (context == null || (id = Settings.Secure.getString(context.getContentResolver(), "android_id")) == null || id.isEmpty()) {
            return "";
        }
        try {
            MessageDigest digest = MessageDigest.getInstance(MessageDigestAlgorithms.SHA_256);
            byte[] hash = digest.digest(("WayOs:" + id).getBytes(CharEncoding.UTF_8));
            StringBuilder hex = new StringBuilder(hash.length * 2);
            for (byte b : hash) {
                hex.append(String.format("%02x", Integer.valueOf(b & UByte.MAX_VALUE)));
            }
            return hex.toString();
        } catch (Exception e) {
            Log.w("EmulationStation", "Could not hash the hardware id", e);
            return "";
        }
    }

    public static void showLoadingOverlay(String name) {
        LoadingOverlay.show(sInstance, name);
    }

    public static void hideLoadingOverlay() {
        LoadingOverlay.hide(sInstance);
    }

    public static void pickProfileImage() {
        ESActivity activity = sInstance;
        if (activity == null) {
            sProfilePickState = 3;
        } else {
            sProfilePickState = 1;
            activity.runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Intent intent;
                    try {
                        if (Build.VERSION.SDK_INT >= 33) {
                            intent = new Intent("android.provider.action.PICK_IMAGES");
                        } else {
                            intent = new Intent("android.intent.action.GET_CONTENT");
                            intent.setType("image/*");
                            intent.addCategory("android.intent.category.OPENABLE");
                        }
                        ESActivity.this.startActivityForResult(intent, ESActivity.REQUEST_PROFILE_IMAGE);
                    } catch (Exception e) {
                        Log.w("EmulationStation", "Could not open the image picker", e);
                        ESActivity.sProfilePickState = 3;
                    }
                }
            });
        }
    }

    public static int getProfilePickState() {
        return sProfilePickState;
    }

    public static void resetProfilePickState() {
        sProfilePickState = 0;
    }

    public static String getProfileImagePath() {
        File newest = newestProfileImage();
        return newest != null ? newest.getAbsolutePath() : "";
    }

    public static void clearProfileImage() {
        File[] files;
        Context context = getAppContext();
        if (context == null || (files = context.getFilesDir().listFiles()) == null) {
            return;
        }
        for (File file : files) {
            if (file.getName().startsWith(PROFILE_IMAGE_PREFIX)) {
                file.delete();
            }
        }
    }

    private static File newestProfileImage() {
        Context context = getAppContext();
        if (context == null) {
            return null;
        }
        File[] files = context.getFilesDir().listFiles();
        File newest = null;
        if (files != null) {
            for (File file : files) {
                if (file.getName().startsWith(PROFILE_IMAGE_PREFIX) && file.getName().endsWith(".png") && (newest == null || file.lastModified() > newest.lastModified())) {
                    newest = file;
                }
            }
        }
        return newest;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode != REQUEST_PROFILE_IMAGE) {
            super.onActivityResult(requestCode, resultCode, data);
            return;
        }
        final Uri uri = (resultCode != -1 || data == null) ? null : data.getData();
        if (uri == null) {
            sProfilePickState = 3;
        } else {
            new Thread(new Runnable(this) {
                final ESActivity this$0;

                {
                    this.this$0 = this;
                }

                @Override
                public void run() {
                    ESActivity.sProfilePickState = ESActivity.saveProfileImage(uri) ? 2 : 3;
                }
            }, "ProfileImage").start();
        }
    }

    public static boolean saveProfileImage(Uri uri) {
        boolean z;
        Context context = getAppContext();
        if (context == null) {
            return false;
        }
        try {
            ContentResolver resolver = context.getContentResolver();
            BitmapFactory.Options bounds = new BitmapFactory.Options();
            bounds.inJustDecodeBounds = true;
            InputStream probe = resolver.openInputStream(uri);
            BitmapFactory.decodeStream(probe, null, bounds);
            if (probe != null) {
                try {
                    probe.close();
                } catch (Exception e) {
                    e = e;
                    z = false;
                }
            }
            if (bounds.outWidth > 0 && bounds.outHeight > 0) {
                int sample = 1;
                while (Math.min(bounds.outWidth, bounds.outHeight) / (sample * 2) >= 512) {
                    sample *= 2;
                }
                BitmapFactory.Options options = new BitmapFactory.Options();
                options.inSampleSize = sample;
                InputStream in = resolver.openInputStream(uri);
                Bitmap bitmap = BitmapFactory.decodeStream(in, null, options);
                if (in != null) {
                    in.close();
                }
                if (bitmap == null) {
                    return false;
                }
                int rotation = 0;
                try {
                    InputStream exifIn = resolver.openInputStream(uri);
                    if (exifIn != null) {
                        ExifInterface exif = new ExifInterface(exifIn);
                        switch (exif.getAttributeInt("Orientation", 1)) {
                            case 3:
                                rotation = 180;
                                break;
                            case 6:
                                rotation = 90;
                                break;
                            case 8:
                                rotation = 270;
                                break;
                        }
                        exifIn.close();
                    }
                } catch (Exception e2) {
                }
                int side = Math.min(bitmap.getWidth(), bitmap.getHeight());
                int left = (bitmap.getWidth() - side) / 2;
                int top = (bitmap.getHeight() - side) / 2;
                Matrix matrix = new Matrix();
                z = false;
                float scale = 512.0f / side;
                try {
                    matrix.postScale(scale, scale);
                    if (rotation != 0) {
                        try {
                            matrix.postRotate(rotation);
                        } catch (Exception e3) {
                            e = e3;
                        }
                    }
                    Bitmap square = Bitmap.createBitmap(bitmap, left, top, side, side, matrix, true);
                    if (square != bitmap) {
                        bitmap.recycle();
                    }
                    File dir = context.getFilesDir();
                    try {
                        File temp = new File(dir, "profile.tmp");
                        File target = new File(dir, PROFILE_IMAGE_PREFIX + System.currentTimeMillis() + ".png");
                        FileOutputStream out = new FileOutputStream(temp);
                        boolean written = square.compress(Bitmap.CompressFormat.PNG, 100, out);
                        out.close();
                        square.recycle();
                        if (written) {
                            clearProfileImage();
                            return temp.renameTo(target);
                        }
                        temp.delete();
                        return false;
                    } catch (Exception e4) {
                        e = e4;
                    }
                } catch (Exception e5) {
                    e = e5;
                }
                Log.w("EmulationStation", "Could not save the profile image", e);
                return z;
            }
            return false;
        } catch (Exception e6) {
            e = e6;
            z = false;
        }
    }

    static void requestNotificationPermission() {
        if (Build.VERSION.SDK_INT < 33 || sNotificationsRequested || sInstance == null) {
            return;
        }
        sNotificationsRequested = true;
        if (sInstance.checkSelfPermission("android.permission.POST_NOTIFICATIONS") == 0) {
            return;
        }
        sInstance.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                ESActivity.sInstance.requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"}, ESActivity.REQUEST_NOTIFICATIONS);
            }
        });
    }

    @Override
    protected String[] getLibraries() {
        return new String[]{"SDL2", "main"};
    }

    @Override
    protected String[] getArguments() {
        return new String[]{"--home", getHomeDir().getAbsolutePath()};
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        sInstance = this;
        StrictMode.setVmPolicy(new StrictMode.VmPolicy.Builder().build());
        super.onCreate(savedInstanceState);
        getWindow().addFlags(128);
        if (Build.VERSION.SDK_INT >= 28) {
            getWindow().getAttributes().layoutInDisplayCutoutMode = 1;
        }
        hideSystemUi();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideSystemUi();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (HttpBridge.activeFileDownloads().count == 0) {
            Log.i("EmulationStation", "Activity destroyed with nothing downloading - ending the process");
            Process.killProcess(Process.myPid());
        } else {
            Log.i("EmulationStation", "Activity destroyed with a download running - keeping the process for it");
        }
    }

    private void hideSystemUi() {
        getWindow().getDecorView().setSystemUiVisibility(5894);
    }

    private static File getHomeDir() {
        return new File(Environment.getExternalStorageDirectory(), "EmulationStation");
    }

    public static String getStorageRoot() {
        return getHomeDir().getAbsolutePath();
    }

    private static void extractSevenZip(File archive, File folder, String rootPath) throws Exception {
        SevenZFile seven = new SevenZFile(archive);
        try {
            byte[] buffer = new byte[262144];
            while (true) {
                SevenZArchiveEntry entry = seven.getNextEntry();
                if (entry != null) {
                    File target = new File(folder, entry.getName()).getCanonicalFile();
                    if (!target.getPath().startsWith(rootPath)) {
                        throw new Exception("7z entry escapes the folder: " + entry.getName());
                    }
                    if (entry.isDirectory()) {
                        target.mkdirs();
                    } else {
                        File parent = target.getParentFile();
                        if (parent != null && !parent.exists() && !parent.mkdirs()) {
                            throw new Exception("could not create " + parent);
                        }
                        OutputStream out = new FileOutputStream(target);
                        while (true) {
                            try {
                                int read = seven.read(buffer);
                                if (read <= 0) {
                                    break;
                                } else {
                                    out.write(buffer, 0, read);
                                }
                            } catch (Throwable th) {
                                out.close();
                                throw th;
                            }
                        }
                        out.close();
                    }
                } else {
                    seven.close();
                    return;
                }
            }
        } catch (Throwable th2) {
            seven.close();
            throw th2;
        }
    }

    /* JADX WARN: Code duplicated, block: B:109:0x0223 A[Catch: Exception -> 0x0365, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:111:0x0240  */
    /* JADX WARN: Code duplicated, block: B:116:0x026d A[Catch: Exception -> 0x0365, TRY_ENTER, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:121:0x0280 A[Catch: Exception -> 0x0365, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:124:0x028a A[Catch: Exception -> 0x0365, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:128:0x02b8 A[LOOP:2: B:122:0x0284->B:128:0x02b8, LOOP_END] */
    /* JADX WARN: Code duplicated, block: B:134:0x02d6 A[Catch: Exception -> 0x0365, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:137:0x02e6 A[Catch: Exception -> 0x0365, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:141:0x0310 A[LOOP:4: B:135:0x02e0->B:141:0x0310, LOOP_END] */
    /* JADX WARN: Code duplicated, block: B:146:0x031c A[Catch: Exception -> 0x0365, TryCatch #13 {Exception -> 0x0365, blocks: (B:96:0x0202, B:99:0x020b, B:112:0x0246, B:116:0x026d, B:118:0x0275, B:130:0x02c1, B:121:0x0280, B:122:0x0284, B:124:0x028a, B:126:0x02b3, B:131:0x02c8, B:132:0x02d0, B:134:0x02d6, B:135:0x02e0, B:137:0x02e6, B:139:0x030b, B:143:0x0312, B:144:0x0316, B:146:0x031c, B:148:0x032c, B:150:0x0332, B:152:0x033a, B:155:0x0340, B:101:0x0210, B:102:0x0213, B:105:0x021b, B:106:0x021f, B:95:0x01fe, B:109:0x0223, B:110:0x023f, B:98:0x0208), top: B:192:0x00b5, inners: #5 }] */
    /* JADX WARN: Code duplicated, block: B:188:0x0149 A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:190:0x0134 A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:202:0x02b3 A[SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:207:0x030b A[SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:214:0x01f8 A[SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:215:0x01cd A[SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:217:0x0141 A[SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:221:0x01a9 A[EDGE_INSN: B:221:0x01a9->B:80:0x01a9 BREAK  A[LOOP:7: B:193:0x018c->B:77:0x01a0], SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:29:0x00b7 A[Catch: Exception -> 0x0369, TRY_ENTER, TRY_LEAVE, TryCatch #3 {Exception -> 0x0369, blocks: (B:16:0x005e, B:29:0x00b7, B:32:0x00c2, B:36:0x00f5), top: B:173:0x005e }] */
    /* JADX WARN: Code duplicated, block: B:32:0x00c2 A[Catch: Exception -> 0x0369, TRY_ENTER, TRY_LEAVE, TryCatch #3 {Exception -> 0x0369, blocks: (B:16:0x005e, B:29:0x00b7, B:32:0x00c2, B:36:0x00f5), top: B:173:0x005e }] */
    /* JADX WARN: Code duplicated, block: B:34:0x00ea A[Catch: Exception -> 0x00aa, TRY_ENTER, TRY_LEAVE, TryCatch #1 {Exception -> 0x00aa, blocks: (B:18:0x008d, B:22:0x00a1, B:24:0x00a6, B:25:0x00a9, B:34:0x00ea, B:20:0x0098), top: B:170:0x008d, inners: #0 }] */
    /* JADX WARN: Code duplicated, block: B:36:0x00f5 A[Catch: Exception -> 0x0369, TRY_ENTER, TRY_LEAVE, TryCatch #3 {Exception -> 0x0369, blocks: (B:16:0x005e, B:29:0x00b7, B:32:0x00c2, B:36:0x00f5), top: B:173:0x005e }] */
    /* JADX WARN: Code duplicated, block: B:43:0x0114 A[Catch: all -> 0x0214, TRY_LEAVE, TryCatch #9 {all -> 0x0214, blocks: (B:40:0x0109, B:41:0x010c, B:43:0x0114), top: B:184:0x0109 }] */
    /* JADX WARN: Code duplicated, block: B:47:0x012e A[Catch: all -> 0x01f2, TRY_LEAVE, TryCatch #8 {all -> 0x01f2, blocks: (B:45:0x0118, B:47:0x012e, B:53:0x0141), top: B:182:0x0118 }] */
    /* JADX WARN: Code duplicated, block: B:75:0x0194  */
    public static String extractRom(String zipPath, String extensions, String destDir) throws Throwable {
        String str;
        List<File> files;
        String[] playlists;
        int length;
        int i;
        List<File> files2;
        String name;
        String ext;
        List<File> files3;
        String[] playlists2;
        List<File> files4;
        String[] playlists3;
        String rootPath;
        ZipInputStream zip;
        ZipInputStream zip2;
        byte[] buffer;
        ZipEntry entry;
        File target;
        File parent;
        OutputStream out;
        OutputStream out2;
        int read;
        Writer writer;
        File zipFile = new File(zipPath);
        String stem = zipFile.getName();
        int dot = stem.lastIndexOf(46);
        File folder = new File(destDir, dot > 0 ? stem.substring(0, dot) : stem);
        List<String> wanted = new ArrayList<>();
        for (String ext2 : extensions.toLowerCase().split("\\|")) {
            String ext3 = ext2.trim();
            if (!ext3.isEmpty() && !ext3.equals(ArchiveStreamFactory.ZIP) && !ext3.equals(ArchiveStreamFactory.SEVEN_Z)) {
                wanted.add(ext3);
            }
        }
        try {
            File marker = new File(folder, ".extracted");
            String stamp = zipFile.length() + ":" + zipFile.lastModified();
            boolean fresh = false;
            if (!marker.isFile()) {
                if (fresh) {
                    str = "";
                } else {
                    deleteTree(folder);
                    if (folder.mkdirs()) {
                        throw new Exception("could not create " + folder);
                    }
                    rootPath = folder.getCanonicalPath() + File.separator;
                    if (!zipFile.getName().toLowerCase().endsWith(".7z")) {
                        str = "";
                        zip = new ZipInputStream(new BufferedInputStream(new FileInputStream(zipFile)));
                        buffer = new byte[262144];
                        while (true) {
                            entry = zip.getNextEntry();
                            if (entry != null) {
                                zip.close();
                                break;
                            }
                            zipFile = zipFile;
                            target = new File(folder, entry.getName()).getCanonicalFile();
                            if (target.getPath().startsWith(rootPath)) {
                                throw new Exception("zip entry escapes the folder: " + entry.getName());
                            }
                            if (entry.isDirectory()) {
                                target.mkdirs();
                            } else {
                                parent = target.getParentFile();
                                if (parent != null) {
                                    if (parent.exists()) {
                                    }
                                    out = new FileOutputStream(target);
                                    while (true) {
                                        read = zip.read(buffer);
                                        if (read > 0) {
                                            break;
                                            break;
                                        }
                                        ZipInputStream zip3 = zip;
                                        out2 = out;
                                        File target2 = target;
                                        out2.write(buffer, 0, read);
                                        target = target2;
                                        out = out2;
                                        zip = zip3;
                                    }
                                    zip2 = zip;
                                    out.close();
                                    dot = dot;
                                    zip = zip2;
                                }
                                out = new FileOutputStream(target);
                                while (true) {
                                    read = zip.read(buffer);
                                    if (read > 0) {
                                        break;
                                        break;
                                    }
                                    ZipInputStream zip4 = zip;
                                    out2 = out;
                                    File target3 = target;
                                    out2.write(buffer, 0, read);
                                    target = target3;
                                    out = out2;
                                    zip = zip4;
                                }
                                zip2 = zip;
                                out.close();
                                dot = dot;
                                zip = zip2;
                            }
                            zip2.close();
                            throw th;
                        }
                    }
                    extractSevenZip(zipFile, folder, rootPath);
                    str = "";
                    writer = new FileWriter(marker);
                    writer.write(stamp);
                    writer.close();
                }
                files = new ArrayList<>();
                collectFiles(folder, files);
                playlists = new String[]{"m3u", "cue", "gdi", "ccd"};
                length = playlists.length;
                i = 0;
                while (i < length) {
                    ext = playlists[i];
                    if (wanted.isEmpty()) {
                        for (File file : files) {
                            files4 = files;
                            playlists3 = playlists;
                            if (file.getName().toLowerCase().endsWith("." + ext)) {
                                return file.getAbsolutePath();
                            }
                            playlists = playlists3;
                            files = files4;
                        }
                        files3 = files;
                        playlists2 = playlists;
                    } else {
                        while (r15.hasNext()) {
                            files4 = files;
                            playlists3 = playlists;
                            if (file.getName().toLowerCase().endsWith("." + ext)) {
                                return file.getAbsolutePath();
                            }
                            playlists = playlists3;
                            files = files4;
                        }
                        files3 = files;
                        playlists2 = playlists;
                    }
                    i++;
                    playlists = playlists2;
                    files = files3;
                }
                files2 = files;
                for (String ext4 : wanted) {
                    for (File file2 : files2) {
                        if (file2.getName().toLowerCase().endsWith("." + ext4)) {
                            return file2.getAbsolutePath();
                        }
                    }
                }
                while (r0.hasNext()) {
                    name = file.getName();
                    if (name.startsWith(".")) {
                    }
                }
                Log.w("EmulationStation", "No file matching " + extensions + " inside " + zipPath);
                return str;
            }
            try {
                BufferedReader reader = new BufferedReader(new FileReader(marker));
                try {
                    fresh = stamp.equals(reader.readLine());
                    reader.close();
                    try {
                        if (fresh) {
                            deleteTree(folder);
                            if (folder.mkdirs()) {
                                throw new Exception("could not create " + folder);
                            }
                            rootPath = folder.getCanonicalPath() + File.separator;
                            if (!zipFile.getName().toLowerCase().endsWith(".7z")) {
                                extractSevenZip(zipFile, folder, rootPath);
                                str = "";
                            } else {
                                str = "";
                                try {
                                    zip = new ZipInputStream(new BufferedInputStream(new FileInputStream(zipFile)));
                                    try {
                                        buffer = new byte[262144];
                                        while (true) {
                                            entry = zip.getNextEntry();
                                            if (entry != null) {
                                                zip.close();
                                                break;
                                            }
                                            zipFile = zipFile;
                                            try {
                                                target = new File(folder, entry.getName()).getCanonicalFile();
                                                if (target.getPath().startsWith(rootPath)) {
                                                    throw new Exception("zip entry escapes the folder: " + entry.getName());
                                                }
                                                if (entry.isDirectory()) {
                                                    try {
                                                        target.mkdirs();
                                                    } catch (Throwable th) {
                                                        th = th;
                                                        zip2 = zip;
                                                    }
                                                } else {
                                                    parent = target.getParentFile();
                                                    try {
                                                        try {
                                                            if (parent != null) {
                                                                try {
                                                                    if (!parent.exists() || parent.mkdirs()) {
                                                                        out = new FileOutputStream(target);
                                                                        while (true) {
                                                                            try {
                                                                                read = zip.read(buffer);
                                                                                if (read > 0) {
                                                                                    break;
                                                                                }
                                                                                ZipInputStream zip5 = zip;
                                                                                out2 = out;
                                                                                File target4 = target;
                                                                                try {
                                                                                    out2.write(buffer, 0, read);
                                                                                    target = target4;
                                                                                    out = out2;
                                                                                    zip = zip5;
                                                                                } catch (Throwable th2) {
                                                                                    th = th2;
                                                                                    out2.close();
                                                                                    throw th;
                                                                                }
                                                                            } catch (Throwable th3) {
                                                                                th = th3;
                                                                                out2 = out;
                                                                            }
                                                                        }
                                                                        zip2 = zip;
                                                                        out.close();
                                                                        dot = dot;
                                                                        zip = zip2;
                                                                    } else {
                                                                        try {
                                                                            throw new Exception("could not create " + parent);
                                                                        } catch (Throwable th4) {
                                                                            th = th4;
                                                                            zip2 = zip;
                                                                        }
                                                                    }
                                                                } catch (Throwable th5) {
                                                                    th = th5;
                                                                    zip2 = zip;
                                                                }
                                                            }
                                                            out.close();
                                                            dot = dot;
                                                            zip = zip2;
                                                        } catch (Throwable th6) {
                                                            th = th6;
                                                        }
                                                        out = new FileOutputStream(target);
                                                        while (true) {
                                                            read = zip.read(buffer);
                                                            if (read > 0) {
                                                                break;
                                                                break;
                                                            }
                                                            ZipInputStream zip6 = zip;
                                                            out2 = out;
                                                            File target5 = target;
                                                            out2.write(buffer, 0, read);
                                                            target = target5;
                                                            out = out2;
                                                            zip = zip6;
                                                        }
                                                        zip2 = zip;
                                                    } catch (Throwable th7) {
                                                        th = th7;
                                                        zip2 = zip;
                                                    }
                                                }
                                            } catch (Throwable th8) {
                                                th = th8;
                                                zip2 = zip;
                                            }
                                            zip2.close();
                                            throw th;
                                        }
                                    } catch (Throwable th9) {
                                        th = th9;
                                        zip2 = zip;
                                    }
                                } catch (Exception e) {
                                    e = e;
                                }
                            }
                            writer = new FileWriter(marker);
                            try {
                                writer.write(stamp);
                                writer.close();
                            } catch (Throwable th10) {
                                writer.close();
                                throw th10;
                            }
                        } else {
                            str = "";
                        }
                        files = new ArrayList<>();
                        collectFiles(folder, files);
                        playlists = new String[]{"m3u", "cue", "gdi", "ccd"};
                        length = playlists.length;
                        i = 0;
                        while (i < length) {
                            ext = playlists[i];
                            if (wanted.isEmpty() || wanted.contains(ext)) {
                                while (r15.hasNext()) {
                                    files4 = files;
                                    playlists3 = playlists;
                                    if (file.getName().toLowerCase().endsWith("." + ext)) {
                                        return file.getAbsolutePath();
                                    }
                                    playlists = playlists3;
                                    files = files4;
                                }
                                files3 = files;
                                playlists2 = playlists;
                            } else {
                                files3 = files;
                                playlists2 = playlists;
                            }
                            i++;
                            playlists = playlists2;
                            files = files3;
                        }
                        files2 = files;
                        while (r0.hasNext()) {
                            while (r4.hasNext()) {
                                if (file2.getName().toLowerCase().endsWith("." + ext4)) {
                                    return file2.getAbsolutePath();
                                }
                            }
                        }
                        for (File file3 : files2) {
                            name = file3.getName();
                            if (name.startsWith(".") && (wanted.isEmpty() || wanted.contains("*"))) {
                                return file3.getAbsolutePath();
                            }
                        }
                        try {
                            Log.w("EmulationStation", "No file matching " + extensions + " inside " + zipPath);
                            return str;
                        } catch (Exception e2) {
                            e = e2;
                        }
                    } catch (Exception e3) {
                        e = e3;
                    }
                } catch (Throwable th11) {
                    reader.close();
                    throw th11;
                }
            } catch (Exception e4) {
                e = e4;
                str = "";
            }
        } catch (Exception e5) {
            e = e5;
            str = "";
        }
        Log.w("EmulationStation", "Could not extract " + zipPath, e);
        deleteTree(folder);
        return str;
    }

    private static void collectFiles(File dir, List<File> out) {
        File[] entries = dir.listFiles();
        if (entries == null) {
            return;
        }
        Arrays.sort(entries);
        for (File entry : entries) {
            if (entry.isDirectory()) {
                collectFiles(entry, out);
            } else if (!entry.getName().equals(".extracted")) {
                out.add(entry);
            }
        }
    }

    private static void deleteTree(File file) {
        if (file == null || !file.exists()) {
            return;
        }
        File[] entries = file.listFiles();
        if (entries != null) {
            for (File entry : entries) {
                deleteTree(entry);
            }
        }
        file.delete();
    }

    public static String getCoresDir() {
        ESActivity activity = sInstance;
        if (activity == null) {
            return "";
        }
        File dir = new File(activity.getFilesDir(), "cores");
        if (!dir.exists() && !dir.mkdirs()) {
            Log.e("EmulationStation", "Could not create " + dir);
            return "";
        }
        return dir.getAbsolutePath();
    }

    public static boolean hasStorageAccess() {
        ESActivity activity = sInstance;
        if (activity == null) {
            return false;
        }
        if (Build.VERSION.SDK_INT >= 30) {
            return Environment.isExternalStorageManager();
        }
        return activity.checkSelfPermission("android.permission.WRITE_EXTERNAL_STORAGE") == 0;
    }

    public static void requestStorageAccess() {
        ESActivity activity = sInstance;
        if (activity == null || sStorageRequested) {
            return;
        }
        sStorageRequested = true;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                ESActivity.this.startStorageRequest();
            }
        });
    }

    public void startStorageRequest() {
        if (Build.VERSION.SDK_INT < 30) {
            requestPermissions(new String[]{"android.permission.READ_EXTERNAL_STORAGE", "android.permission.WRITE_EXTERNAL_STORAGE"}, REQUEST_LEGACY_STORAGE);
            return;
        }
        try {
            Intent intent = new Intent("android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION");
            intent.setData(Uri.parse("package:" + getPackageName()));
            startActivity(intent);
        } catch (Exception e) {
            Log.w("EmulationStation", "Could not open the per-app storage settings, falling back to the full list", e);
            try {
                startActivity(new Intent("android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION"));
            } catch (Exception fallbackError) {
                Log.e("EmulationStation", "No way to ask for storage access on this device", fallbackError);
            }
        }
    }

    public static void installResources() {
        ESActivity activity = sInstance;
        if (activity == null) {
            return;
        }
        AssetInstaller.installIfNeeded(activity, getHomeDir());
    }

    public static void finishApp() {
        ESActivity activity = sInstance;
        if (activity == null) {
            return;
        }
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                ESActivity.this.finishAndRemoveTask();
            }
        });
    }

    public static void restartApp() {
        ESActivity activity = sInstance;
        if (activity == null) {
            return;
        }
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Log.i("EmulationStation", "Restarting the app in a fresh process");
                Intent restart = new Intent(ESActivity.this, (Class<?>) RestartActivity.class);
                restart.putExtra(RestartActivity.EXTRA_PID, Process.myPid());
                restart.addFlags(268435456);
                ESActivity.this.startActivity(restart);
            }
        });
    }
}
