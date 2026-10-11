package org.emulationstation.frontend.sony;

import android.app.Application;
import android.content.Context;
import android.os.Build;
import android.os.Looper;
import android.system.ErrnoException;
import android.system.Os;
import android.system.OsConstants;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.RandomAccessFile;
import java.nio.channels.FileLock;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** Verified private assets. Called only by a Sony owner worker, never by the frontend. */
public final class StationSonyAssets {
    private static final int MAX_DESCRIPTOR_BYTES = 4 * 1024 * 1024;
    private static final long MAX_ARTIFACT_BYTES = 2L * 1024 * 1024 * 1024;
    private static final Map<String, Prepared> PREPARED = new HashMap<>();
    private static final Map<String, String> LOADED_SONAMES = new HashMap<>();
    private static final Set<String> SYSTEM_LIBRARIES;
    static {
        Set<String> names = new HashSet<>();
        Collections.addAll(names, "libandroid.so", "libc.so", "libdl.so", "libm.so",
            "liblog.so", "libz.so", "libvulkan.so", "libOpenSLES.so", "libEGL.so",
            "libGLESv1_CM.so", "libGLESv2.so", "libGLESv3.so", "libjnigraphics.so");
        SYSTEM_LIBRARIES = Collections.unmodifiableSet(names);
    }
    private StationSonyAssets() { }

    /** Optional progress on the calling worker; no callback is scheduled by this class. */
    public interface Progress {
        void onArtifact(String relativePath, int completed, int total);
    }

    public static Prepared prepare(Context context, String system, String expectedManifestSha256)
            throws IOException {
        return prepare(context, system, expectedManifestSha256, null);
    }

    public static Prepared prepare(Context context, String system, String expectedManifestSha256,
            Progress progress) throws IOException {
        requireWorker();
        if (context == null || !("ps3".equals(system) || "ps4".equals(system)) ||
                !sha256Text(expectedManifestSha256)) throw new IOException("Invalid Sony module request");
        Context app = context.getApplicationContext();
        if (app == null) app = context;
        String process = Application.getProcessName();
        if (!(app.getPackageName() + ":station_" + system).equals(process)) {
            throw new IOException("Sony native assets require their dedicated owner process");
        }
        synchronized (PREPARED) {
            String key = system + ":" + expectedManifestSha256;
            Prepared cached = PREPARED.get(key);
            if (cached != null) return cached;
            byte[] descriptor = readBounded(app.getAssets().open("sony/" + system + "/module.json"),
                MAX_DESCRIPTOR_BYTES);
            if (!hex(digest().digest(descriptor)).equals(expectedManifestSha256)) {
                throw new IOException("Sony module descriptor hash mismatch");
            }
            Prepared result = parse(app, system, descriptor);
            int completed = 0;
            for (Artifact artifact : result.artifacts.values()) {
                stage(app, result, artifact);
                if (progress != null) progress.onArtifact(artifact.path, ++completed, result.artifacts.size());
            }
            PREPARED.put(key, result);
            return result;
        }
    }

    public static final class Prepared {
        private final String system;
        private final String moduleId;
        private final File root;
        private final Map<String, Artifact> artifacts;
        private final Map<String, Artifact> bionicSonames;
        private Prepared(String system, String moduleId, File root, Map<String, Artifact> artifacts,
                Map<String, Artifact> bionicSonames) {
            this.system = system;
            this.moduleId = moduleId;
            this.root = root;
            this.artifacts = Collections.unmodifiableMap(artifacts);
            this.bionicSonames = Collections.unmodifiableMap(bionicSonames);
        }
        public String system() { return system; }
        public String moduleId() { return moduleId; }
        public File nativeDirectory() throws IOException { return safeChild(root, "native", true); }
        public File nativeFile(String basename) throws IOException {
            if (!basename.matches("lib[A-Za-z0-9_+.-]+\\.so")) throw new IOException("Invalid native name");
            return declared("native/" + basename);
        }
        /** Accepts the original asset-relative path, or one optional original assets/ prefix. */
        public File assetFile(String upstreamRelativePath) throws IOException {
            if (upstreamRelativePath != null && upstreamRelativePath.startsWith("assets/")) {
                upstreamRelativePath = upstreamRelativePath.substring("assets/".length());
            }
            validateRelative(upstreamRelativePath);
            return declared("upstream/" + upstreamRelativePath);
        }
        private File declared(String path) throws IOException {
            Artifact artifact = artifacts.get(path);
            if (artifact == null) throw new IOException("Undeclared Sony artifact");
            File file = safeChild(root, path, false);
            if (!file.isFile() || !artifact.verified || file.length() != artifact.bytes ||
                    file.lastModified() != artifact.modified) throw new IOException("Sony artifact is not prepared or changed");
            return file;
        }
    }

    /** Loads only Bionic libraries, closing private DT_NEEDED dependencies before the entry. */
    public static synchronized void loadNative(Prepared prepared, String basename) throws IOException {
        requireWorker();
        if (prepared == null) throw new IOException("Sony module is not prepared");
        if ("ps4".equals(prepared.system)) {
            throw new IOException("PS4 native loads must be performed by its child-owned JNI bootstrap");
        }
        List<Artifact> ordered = nativeOrder(prepared, basename);
        for (Artifact artifact : ordered) {
            String path = prepared.declared(artifact.path).getCanonicalPath();
            String loaded = LOADED_SONAMES.get(artifact.soname);
            if (loaded != null) {
                if (!loaded.equals(path)) throw new IOException("Sony native SONAME collision");
                continue;
            }
            try { System.load(path); }
            catch (UnsatisfiedLinkError cause) {
                throw new IOException("Sony native entry could not be loaded: " + artifact.soname, cause);
            }
            LOADED_SONAMES.put(artifact.soname, path);
        }
    }

    /** PS4 executes System.load in its child-owned class, not in this parent-classloader helper. */
    public static synchronized File[] nativeLoadPlan(Prepared prepared, String basename) throws IOException {
        requireWorker();
        if (prepared == null) throw new IOException("Sony module is not prepared");
        List<Artifact> ordered = nativeOrder(prepared, basename);
        File[] paths = new File[ordered.size()];
        for (int i = 0; i < ordered.size(); ++i) paths[i] = prepared.declared(ordered.get(i).path);
        return paths;
    }

    private static List<Artifact> nativeOrder(Prepared prepared, String basename) throws IOException {
        if (!(Application.getProcessName().endsWith(":station_" + prepared.system))) {
            throw new IOException("Sony native load requires its dedicated process");
        }
        Artifact selected = prepared.artifacts.get("native/" + basename);
        if (selected == null || !"bionic".equals(selected.kind)) {
            throw new IOException("Artifact is not an audited Bionic native entry");
        }
        List<Artifact> ordered = new ArrayList<>();
        order(prepared, selected, new HashSet<>(), new HashSet<>(), ordered);
        // An absolute entry path does not isolate DT_NEEDED: reject an already mapped foreign SONAME.
        rejectForeignMaps(prepared, ordered);
        return ordered;
    }

    private static void order(Prepared prepared, Artifact artifact, Set<String> visiting,
            Set<String> visited, List<Artifact> ordered) throws IOException {
        if (visited.contains(artifact.path)) return;
        if (!visiting.add(artifact.path)) throw new IOException("Cyclic private native dependency");
        for (String dependency : artifact.needed) {
            Artifact privateDependency = prepared.bionicSonames.get(dependency);
            if (privateDependency != null) order(prepared, privateDependency, visiting, visited, ordered);
            else if (!SYSTEM_LIBRARIES.contains(dependency)) {
                throw new IOException("Unresolved Sony native dependency: " + dependency);
            }
        }
        visiting.remove(artifact.path);
        visited.add(artifact.path);
        ordered.add(artifact);
    }

    private static void rejectForeignMaps(Prepared prepared, List<Artifact> ordered) throws IOException {
        Map<String, String> desired = new HashMap<>();
        for (Artifact artifact : ordered) desired.put(artifact.soname,
            prepared.declared(artifact.path).getCanonicalPath());
        try (BufferedReader maps = new BufferedReader(new InputStreamReader(
                new FileInputStream("/proc/self/maps"), StandardCharsets.UTF_8))) {
            String line;
            while ((line = maps.readLine()) != null) {
                int slash = line.indexOf('/');
                if (slash < 0) continue;
                String mapped = line.substring(slash);
                if (mapped.endsWith(" (deleted)")) mapped = mapped.substring(0, mapped.length() - 10);
                String name = mapped.substring(mapped.lastIndexOf('/') + 1);
                String expected = desired.get(name);
                if (expected != null && !expected.equals(mapped)) {
                    throw new IOException("Foreign native library already loaded: " + name);
                }
            }
        }
    }

    private static final class Artifact {
        final String asset, path, sha256, kind, soname;
        final long bytes;
        final List<String> needed;
        boolean verified;
        long modified;
        Artifact(JSONObject row) throws JSONException, IOException {
            asset = row.getString("asset"); path = row.getString("path");
            sha256 = row.getString("sha256"); bytes = row.getLong("bytes"); kind = row.getString("kind");
            validateRelative(asset); validateRelative(path);
            if (!sha256Text(sha256) || bytes < 0 || bytes > MAX_ARTIFACT_BYTES ||
                    !("bionic".equals(kind) || "glibc".equals(kind) || "asset".equals(kind))) {
                throw new IOException("Invalid Sony artifact metadata");
            }
            needed = new ArrayList<>();
            soname = "asset".equals(kind) ? null : row.getString("soname");
            if (soname != null) {
                if (!soname.matches("[A-Za-z0-9_+.-]+")) throw new IOException("Invalid native SONAME");
                JSONArray dependencies = row.getJSONArray("needed");
                for (int i = 0; i < dependencies.length(); ++i) {
                    String dependency = dependencies.getString(i);
                    if (!dependency.matches("[A-Za-z0-9_+.-]+")) throw new IOException("Invalid native dependency");
                    needed.add(dependency);
                }
            }
            if ("asset".equals(kind) != path.startsWith("upstream/")) {
                throw new IOException("Sony artifact kind/path mismatch");
            }
            if (!"asset".equals(kind) && !path.matches("native/lib[A-Za-z0-9_+.-]+\\.so")) {
                throw new IOException("Invalid private native path");
            }
        }
    }

    private static Prepared parse(Context context, String system, byte[] raw) throws IOException {
        try {
            JSONObject descriptor = new JSONObject(new String(raw, StandardCharsets.UTF_8));
            String moduleId = descriptor.getString("moduleId");
            if (descriptor.getInt("schemaVersion") != 1 || !system.equals(descriptor.getString("system")) ||
                    !"arm64-v8a".equals(descriptor.getString("abi")) ||
                    !moduleId.matches("[a-z0-9-]{1,96}") ||
                    !sha256Text(descriptor.getString("sourceApkSha256")) ||
                    Build.VERSION.SDK_INT < descriptor.getInt("minSdk")) {
                throw new IOException("Sony module is not compatible with this owner");
            }
            boolean arm64 = false;
            for (String abi : Build.SUPPORTED_ABIS) arm64 |= "arm64-v8a".equals(abi);
            if (!arm64 || !android.os.Process.is64Bit()) throw new IOException("Sony requires an ARM64 process");
            File trusted = context.getNoBackupFilesDir().getCanonicalFile();
            File root = safeChild(trusted, "station-sony/" + system + "/" + moduleId, true);
            Map<String, Artifact> artifacts = new LinkedHashMap<>();
            Map<String, Artifact> sonames = new HashMap<>();
            JSONArray files = descriptor.getJSONArray("files");
            if (files.length() == 0 || files.length() > 10000) throw new IOException("Invalid Sony module file count");
            Set<String> assets = new HashSet<>();
            for (int i = 0; i < files.length(); ++i) {
                Artifact artifact = new Artifact(files.getJSONObject(i));
                if (!artifact.asset.equals("sony/" + system + "/" + artifact.path) ||
                        !assets.add(artifact.asset) || artifacts.put(artifact.path, artifact) != null) {
                    throw new IOException("Duplicate or foreign Sony artifact");
                }
                if ("bionic".equals(artifact.kind) && sonames.put(artifact.soname, artifact) != null) {
                    throw new IOException("Duplicate private Bionic SONAME");
                }
            }
            for (Artifact artifact : sonames.values()) for (String dependency : artifact.needed) {
                if (!sonames.containsKey(dependency) && !SYSTEM_LIBRARIES.contains(dependency)) {
                    throw new IOException("Unclosed private Bionic dependency");
                }
            }
            return new Prepared(system, moduleId, root, artifacts, sonames);
        } catch (JSONException cause) { throw new IOException("Invalid Sony module descriptor", cause); }
    }

    private static void stage(Context context, Prepared prepared, Artifact artifact) throws IOException {
        File target = safeChild(prepared.root, artifact.path, false);
        File parent = safeChild(prepared.root, artifact.path.substring(0, artifact.path.lastIndexOf('/')), true);
        File lockDirectory = safeChild(prepared.root, ".locks", true);
        File lockFile = safeChild(lockDirectory, hex(digest().digest(artifact.path.getBytes(StandardCharsets.UTF_8))) + ".lock", false);
        try (RandomAccessFile locking = new RandomAccessFile(lockFile, "rw");
                FileLock held = locking.getChannel().lock()) {
            noLink(target);
            if (target.isFile() && target.length() == artifact.bytes && hashFile(target).equals(artifact.sha256)) {
                if (!target.setReadOnly()) throw new IOException("Sony artifact permissions could not be restored");
                artifact.modified = target.lastModified(); artifact.verified = true; return;
            }
            if (target.exists() && !target.isFile()) throw new IOException("Sony artifact target is not a regular file");
            File temporary = safeChild(parent, target.getName() + ".station-part", false);
            noLink(temporary);
            if (temporary.exists() && !temporary.isFile()) throw new IOException("Invalid Sony staging file");
            // Only this module-owned temporary is replaced under its exclusive artifact lock.
            if (temporary.exists() && !temporary.setWritable(true, true)) throw new IOException("Sony staging file is locked");
            boolean published = false;
            try {
                MessageDigest hash = digest();
                long count = 0;
                try (InputStream source = context.getAssets().open(artifact.asset);
                        FileOutputStream destination = new FileOutputStream(temporary, false)) {
                    byte[] buffer = new byte[128 * 1024];
                    int read;
                    while ((read = source.read(buffer)) != -1) {
                        if (Thread.currentThread().isInterrupted()) throw new IOException("Sony preparation interrupted");
                        count += read;
                        if (count > artifact.bytes) throw new IOException("Sony artifact exceeds its pinned length");
                        hash.update(buffer, 0, read); destination.write(buffer, 0, read);
                    }
                    destination.getFD().sync();
                }
                if (count != artifact.bytes || !hex(hash.digest()).equals(artifact.sha256)) {
                    throw new IOException("Sony artifact hash or length mismatch");
                }
                if (!temporary.setReadOnly()) throw new IOException("Sony artifact permissions could not be set");
                noLink(target);
                Files.move(temporary.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE,
                    StandardCopyOption.REPLACE_EXISTING);
                artifact.modified = target.lastModified(); artifact.verified = true;
                published = true;
            } finally {
                if (!published && temporary.exists()) {
                    noLink(temporary);
                    if (!temporary.delete()) throw new IOException("Sony temporary artifact could not be removed");
                }
            }
        }
    }

    private static File safeChild(File root, String relative, boolean directory) throws IOException {
        validateRelative(relative);
        File canonicalRoot = root.getCanonicalFile();
        noLink(root);
        File current = canonicalRoot;
        String[] parts = relative.split("/");
        for (int i = 0; i < parts.length; ++i) {
            current = new File(current, parts[i]);
            noLink(current);
            if (i < parts.length - 1 || directory) {
                if (!current.exists() && !current.mkdir() && !current.isDirectory()) {
                    throw new IOException("Sony private directory could not be created");
                }
                if (!current.isDirectory()) throw new IOException("Sony private directory is not a directory");
            }
            String path = current.getCanonicalPath();
            if (!path.startsWith(canonicalRoot.getPath() + File.separator)) {
                throw new IOException("Sony path escaped private module");
            }
        }
        return current;
    }

    private static void noLink(File file) throws IOException {
        try {
            if (OsConstants.S_ISLNK(Os.lstat(file.getPath()).st_mode)) throw new IOException("Sony paths may not be symbolic links");
        } catch (ErrnoException cause) {
            if (cause.errno != OsConstants.ENOENT) throw new IOException("Sony path could not be inspected", cause);
        }
    }
    private static void validateRelative(String path) throws IOException {
        if (path == null || path.isEmpty() || path.length() > 512 || path.startsWith("/") ||
                path.indexOf('\\') >= 0 || path.indexOf(':') >= 0 || path.indexOf('\0') >= 0) {
            throw new IOException("Invalid Sony relative path");
        }
        for (String part : path.split("/", -1)) if (part.isEmpty() || ".".equals(part) || "..".equals(part)) {
            throw new IOException("Invalid Sony path segment");
        }
    }
    private static void requireWorker() throws IOException {
        if (Looper.myLooper() == Looper.getMainLooper()) throw new IOException("Sony preparation may not block the UI thread");
    }
    private static boolean sha256Text(String value) { return value != null && value.matches("[0-9a-f]{64}"); }
    private static MessageDigest digest() {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException impossible) { throw new AssertionError(impossible); }
    }
    private static String hex(byte[] raw) {
        char[] chars = new char[raw.length * 2];
        char[] digits = "0123456789abcdef".toCharArray();
        for (int i = 0; i < raw.length; ++i) { chars[i * 2] = digits[(raw[i] >> 4) & 15]; chars[i * 2 + 1] = digits[raw[i] & 15]; }
        return new String(chars);
    }
    private static String hashFile(File file) throws IOException {
        MessageDigest hash = digest();
        try (InputStream source = new FileInputStream(file)) {
            byte[] buffer = new byte[128 * 1024]; int read;
            while ((read = source.read(buffer)) != -1) {
                if (Thread.currentThread().isInterrupted()) throw new IOException("Sony verification interrupted");
                hash.update(buffer, 0, read);
            }
        }
        return hex(hash.digest());
    }
    private static byte[] readBounded(InputStream source, int maximum) throws IOException {
        try (InputStream closed = source; java.io.ByteArrayOutputStream result = new java.io.ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192]; int read;
            while ((read = closed.read(buffer)) != -1) {
                if (result.size() + read > maximum) throw new IOException("Sony descriptor exceeds its bound");
                result.write(buffer, 0, read);
            }
            return result.toByteArray();
        }
    }
}
