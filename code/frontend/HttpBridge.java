package org.emulationstation.frontend;

import android.util.Log;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.RandomAccessFile;
import java.net.ConnectException;
import java.net.HttpURLConnection;
import java.net.NoRouteToHostException;
import java.net.SocketTimeoutException;
import java.net.URI;
import java.net.URL;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import javax.net.ssl.SSLException;
import org.apache.commons.lang3.CharEncoding;

public final class HttpBridge {
    private static final int BUSY_RETRIES = 30;
    private static final int CONNECT_TIMEOUT = 15000;
    private static final int IO_BUFFER = 262144;
    private static final int MAX_REDIRECTS = 5;
    private static final int PARALLEL_CONNECTIONS = 24;
    private static final long PARALLEL_MIN_SIZE = 8388608;
    private static final int READ_TIMEOUT = 30000;
    private static final int SEGMENT_READ_TIMEOUT = 12000;
    private static final int SEGMENT_RETRIES = 12;
    private static final long SEGMENT_RETRY_MAX_MS = 15000;
    public static final int STATUS_BAD_STATUS = 3;
    public static final int STATUS_INVALID = 4;
    public static final int STATUS_IN_PROGRESS = 0;
    public static final int STATUS_IO_ERROR = 2;
    public static final int STATUS_SUCCESS = 1;
    private static final ExecutorService POOL = Executors.newFixedThreadPool(4);
    private static final ExecutorService FILE_POOL = Executors.newCachedThreadPool();
    private static final ConcurrentHashMap<Integer, Request> REQUESTS = new ConcurrentHashMap<>();
    private static final AtomicInteger NEXT_ID = new AtomicInteger(1);

    private HttpBridge() {
    }

    private static final class Request {
        volatile boolean cancelled;
        volatile byte[] content;
        volatile boolean deferSuccess;
        volatile boolean downloadOk;
        final AtomicLong downloadedBytes;
        volatile String error;
        volatile boolean isFile;
        volatile int status;
        volatile String title;
        volatile long total;
        volatile boolean userCancelled;

        private Request() {
            this.status = 0;
            this.error = "";
            this.downloadedBytes = new AtomicLong(0L);
            this.total = -1L;
            this.cancelled = false;
            this.deferSuccess = false;
            this.downloadOk = false;
            this.isFile = false;
            this.title = "";
            this.userCancelled = false;
        }
    }

    static final class DownloadSnapshot {
        int count;
        long downloaded;
        String firstTitle;
        long total;

        DownloadSnapshot() {
        }
    }

    static DownloadSnapshot activeFileDownloads() {
        DownloadSnapshot snapshot = new DownloadSnapshot();
        for (Request request : REQUESTS.values()) {
            if (request.isFile && !request.userCancelled && request.status == 0) {
                if (snapshot.count == 0) {
                    snapshot.firstTitle = request.title;
                }
                snapshot.count++;
                snapshot.downloaded += request.downloadedBytes.get();
                if (snapshot.total >= 0) {
                    snapshot.total = request.total > 0 ? snapshot.total + request.total : -1L;
                }
            }
        }
        return snapshot;
    }

    public static int start(String url) {
        return startInternal(url, null, null, false);
    }

    public static int startPost(final String url, final String formBody) {
        int id = NEXT_ID.getAndIncrement();
        final Request request = new Request();
        REQUESTS.put(Integer.valueOf(id), request);
        try {
            POOL.execute(new Runnable() {
                @Override
                public void run() {
                    HttpBridge.executePost(url, formBody, request);
                }
            });
        } catch (Exception e) {
            Log.e(ESActivity.TAG, "Could not queue POST", e);
            request.status = 2;
            request.error = String.valueOf(e);
        }
        return id;
    }

    public static void executePost(String url, String formBody, Request request) {
        HttpURLConnection connection = null;
        try {
            byte[] body = formBody.getBytes(CharEncoding.UTF_8);
            connection = (HttpURLConnection) new URL(url).openConnection();
            connection.setConnectTimeout(CONNECT_TIMEOUT);
            connection.setReadTimeout(READ_TIMEOUT);
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setFixedLengthStreamingMode(body.length);
            connection.setRequestProperty("User-Agent", "WayOs");
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            OutputStream out = connection.getOutputStream();
            out.write(body);
            out.close();
            int code = connection.getResponseCode();
            InputStream in = code >= 400 ? connection.getErrorStream() : connection.getInputStream();
            ByteArrayOutputStream memory = new ByteArrayOutputStream();
            if (in != null) {
                byte[] buffer = new byte[16384];
                while (true) {
                    int read = in.read(buffer);
                    if (read <= 0) {
                        break;
                    } else {
                        memory.write(buffer, 0, read);
                    }
                }
                in.close();
            }
            request.content = memory.toByteArray();
            if (code >= 200 && code <= 299) {
                request.status = 1;
                if (connection == null) {
                    return;
                }
                return;
            }
            request.error = "HTTP " + code;
            request.status = 3;
        } catch (Exception e) {
            Log.w(ESActivity.TAG, "POST failed: " + url + " (" + e + ")");
            request.error = describeFailure(e);
            request.status = 2;
        } finally {
            if (0 != 0) {
                connection.disconnect();
            }
        }
    }

    public static int startDownload(String url, String destPath) {
        return startInternal(url, destPath, null, false);
    }

    public static int startCoreDownload(String url, String destDir) {
        return startInternal(url, new File(destDir, ".core-download.zip").getAbsolutePath(), destDir, false);
    }

    public static int startZipDownload(String url, String destDir) {
        return startInternal(url, new File(destDir, ".pack-download.zip").getAbsolutePath(), destDir, true);
    }

    private static int startInternal(String url, final String destPath, final String extractDir, final boolean extractAll) {
        ExecutorService executorService;
        final String url2;
        int id = NEXT_ID.getAndIncrement();
        final Request request = new Request();
        request.deferSuccess = extractDir != null;
        if (destPath != null) {
            request.isFile = true;
            String name = new File(destPath).getName();
            int dot = name.lastIndexOf(46);
            if (dot > 0) {
                name = name.substring(0, dot);
            }
            request.title = extractDir != null ? "emulador" : name;
        }
        REQUESTS.put(Integer.valueOf(id), request);
        if (destPath == null) {
            try {
                executorService = POOL;
            } catch (Exception e) {
                e = e;
                url2 = url;
                Log.e(ESActivity.TAG, "Could not queue request for " + url2, e);
                request.status = 2;
                request.error = String.valueOf(e);
                return id;
            }
        } else {
            try {
                executorService = FILE_POOL;
            } catch (Exception e2) {
                e = e2;
                url2 = url;
                Log.e(ESActivity.TAG, "Could not queue request for " + url2, e);
                request.status = 2;
                request.error = String.valueOf(e);
                return id;
            }
        }
        url2 = url;
        try {
            executorService.execute(new Runnable() {
                @Override
                public void run() throws Throwable {
                    HttpBridge.execute(url2, destPath, request);
                    if (extractDir != null && request.downloadOk) {
                        boolean z = extractAll;
                        String str = destPath;
                        if (z) {
                            HttpBridge.extractAll(str, extractDir, request);
                        } else {
                            HttpBridge.extractCores(str, extractDir, request);
                        }
                    }
                    if (destPath != null && extractDir == null && !request.userCancelled) {
                        DownloadService.notifyFinished(request.title, request.status == 1, request.error);
                    }
                }
            });
            if (destPath != null) {
                DownloadService.ensureRunning();
            }
        } catch (Exception e3) {
            e = e3;
            Log.e(ESActivity.TAG, "Could not queue request for " + url2, e);
            request.status = 2;
            request.error = String.valueOf(e);
        }
        return id;
    }

    private static String redactUrl(String url) {
        int at = url.indexOf("/drawers.json/");
        if (at < 0) {
            return url;
        }
        int from = "/drawers.json/".length() + at;
        int to = url.indexOf(47, from);
        return url.substring(0, from) + "<chave>" + (to < 0 ? "" : url.substring(to));
    }

    private static String normalizeUrl(String raw) throws Exception {
        boolean needs = false;
        for (int i = 0; i < raw.length(); i++) {
            char c = raw.charAt(i);
            if (c == ' ' || c > 127) {
                needs = true;
                break;
            }
        }
        if (!needs) {
            return raw;
        }
        URL parsed = new URL(raw);
        return new URI(parsed.getProtocol(), parsed.getUserInfo(), parsed.getHost(), parsed.getPort(), parsed.getPath(), parsed.getQuery(), parsed.getRef()).toASCIIString();
    }

    public static void execute(String url, String destPath, Request request) throws Throwable {
        OutputStream fileOut;
        HttpURLConnection connection;
        Throwable th;
        String url2;
        File part;
        StringBuilder sb;
        File parent;
        HttpURLConnection connection2 = null;
        OutputStream fileOut2 = null;
        try {
            try {
                url2 = normalizeUrl(url);
                String current = url2;
                int redirect = 0;
                while (true) {
                    try {
                        connection2 = (HttpURLConnection) new URL(current).openConnection();
                        connection2.setConnectTimeout(CONNECT_TIMEOUT);
                        connection2.setReadTimeout(READ_TIMEOUT);
                        connection2.setInstanceFollowRedirects(false);
                        connection2.setRequestProperty("User-Agent", ESActivity.TAG);
                        connection2.setRequestProperty("Accept-Encoding", "identity");
                        int code = connection2.getResponseCode();
                        boolean isRedirect = code == 301 || code == 302 || code == 303 || code == 307 || code == 308;
                        if (isRedirect) {
                            if (redirect >= 5) {
                                request.error = "too many redirects";
                                request.status = 4;
                                if (0 != 0) {
                                    try {
                                        fileOut2.close();
                                    } catch (Exception e) {
                                    }
                                }
                                if (connection2 != null) {
                                    connection2.disconnect();
                                }
                                if (destPath == null || request.downloadOk) {
                                    return;
                                }
                                File part2 = new File(destPath + ".part");
                                if (!part2.exists() || part2.delete()) {
                                    return;
                                }
                                Log.w(ESActivity.TAG, "Could not delete " + part2);
                                return;
                            }
                            String location = connection2.getHeaderField("Location");
                            connection2.disconnect();
                            if (location != null && !location.isEmpty()) {
                                current = new URL(new URL(current), location).toString();
                                redirect++;
                            }
                            request.error = "redirect without a location";
                            request.status = 4;
                            if (0 != 0) {
                                try {
                                    fileOut2.close();
                                } catch (Exception e2) {
                                }
                            }
                            if (connection2 != null) {
                                connection2.disconnect();
                            }
                            if (destPath == null || request.downloadOk) {
                                return;
                            }
                            File part3 = new File(destPath + ".part");
                            if (!part3.exists() || part3.delete()) {
                                return;
                            }
                            Log.w(ESActivity.TAG, "Could not delete " + part3);
                            return;
                        }
                        if (code >= 200 && code <= 299) {
                            request.total = connection2.getContentLengthLong();
                            if (destPath != null && (parent = new File(destPath).getParentFile()) != null && !parent.exists() && !parent.mkdirs()) {
                                throw new Exception("could not create " + parent);
                            }
                            File part4 = destPath != null ? new File(destPath + ".part") : null;
                            boolean parallel = part4 != null && request.total >= PARALLEL_MIN_SIZE && "bytes".equalsIgnoreCase(connection2.getHeaderField("Accept-Ranges"));
                            if (parallel) {
                                connection2.disconnect();
                                connection2 = null;
                                Log.i(ESActivity.TAG, "Downloading " + request.total + " bytes over 24 connections: " + current);
                                downloadInParts(current, part4, request);
                            } else {
                                InputStream in = new BufferedInputStream(connection2.getInputStream(), 262144);
                                ByteArrayOutputStream memoryOut = null;
                                if (part4 != null) {
                                    fileOut2 = new BufferedOutputStream(new FileOutputStream(part4), 262144);
                                } else {
                                    memoryOut = new ByteArrayOutputStream();
                                }
                                try {
                                    byte[] buffer = new byte[262144];
                                    while (true) {
                                        int read = in.read(buffer);
                                        if (read <= 0) {
                                            OutputStream fileOut3 = fileOut2;
                                            in.close();
                                            if (fileOut3 == null) {
                                                request.content = memoryOut.toByteArray();
                                                fileOut2 = fileOut3;
                                                break;
                                            } else {
                                                fileOut3.close();
                                                fileOut2 = null;
                                                break;
                                            }
                                        }
                                        if (request.cancelled) {
                                            throw new CancelledException();
                                        }
                                        if (fileOut2 != null) {
                                            fileOut2.write(buffer, 0, read);
                                        } else {
                                            memoryOut.write(buffer, 0, read);
                                        }
                                        fileOut = fileOut2;
                                        boolean parallel2 = parallel;
                                        try {
                                            request.downloadedBytes.addAndGet(read);
                                            fileOut2 = fileOut;
                                            parallel = parallel2;
                                        } catch (CancelledException e3) {
                                            fileOut2 = fileOut;
                                            request.error = "cancelled";
                                            request.status = 2;
                                            if (fileOut2 != null) {
                                                try {
                                                    fileOut2.close();
                                                } catch (Exception e4) {
                                                }
                                            }
                                            if (connection2 != null) {
                                                connection2.disconnect();
                                            }
                                            if (destPath == null || request.downloadOk) {
                                                return;
                                            }
                                            part = new File(destPath + ".part");
                                            if (!part.exists() || part.delete()) {
                                                return;
                                            }
                                            sb = new StringBuilder();
                                            Log.w(ESActivity.TAG, sb.append("Could not delete ").append(part).toString());
                                            return;
                                        } catch (Exception e5) {
                                            e = e5;
                                            fileOut2 = fileOut;
                                            Log.w(ESActivity.TAG, "Request failed: " + url2, e);
                                            request.error = describeFailure(e);
                                            request.status = 2;
                                            if (fileOut2 != null) {
                                                try {
                                                    fileOut2.close();
                                                } catch (Exception e6) {
                                                }
                                            }
                                            if (connection2 != null) {
                                                connection2.disconnect();
                                            }
                                            if (destPath == null || request.downloadOk) {
                                                return;
                                            }
                                            part = new File(destPath + ".part");
                                            if (!part.exists() || part.delete()) {
                                                return;
                                            }
                                            sb = new StringBuilder();
                                            Log.w(ESActivity.TAG, sb.append("Could not delete ").append(part).toString());
                                            return;
                                        } catch (Throwable th2) {
                                            connection = connection2;
                                            th = th2;
                                            if (fileOut != null) {
                                                try {
                                                    fileOut.close();
                                                } catch (Exception e7) {
                                                }
                                            }
                                            if (connection != null) {
                                                connection.disconnect();
                                            }
                                            if (destPath == null || request.downloadOk) {
                                                throw th;
                                            }
                                            File part5 = new File(destPath + ".part");
                                            if (!part5.exists() || part5.delete()) {
                                                throw th;
                                            }
                                            Log.w(ESActivity.TAG, "Could not delete " + part5);
                                            throw th;
                                        }
                                    }
                                } catch (CancelledException e8) {
                                } catch (Exception e9) {
                                    e = e9;
                                } catch (Throwable th3) {
                                    fileOut = fileOut2;
                                    connection = connection2;
                                    th = th3;
                                }
                            }
                            if (part4 != null) {
                                File dest = new File(destPath);
                                if (dest.exists() && !dest.delete()) {
                                    throw new Exception("could not replace " + destPath);
                                }
                                if (!part4.renameTo(dest)) {
                                    throw new Exception("could not rename " + part4);
                                }
                                request.content = new byte[0];
                            }
                            request.downloadOk = true;
                            if (!request.deferSuccess) {
                                request.status = 1;
                            }
                            if (fileOut2 != null) {
                                try {
                                    fileOut2.close();
                                } catch (Exception e10) {
                                }
                            }
                            if (connection2 != null) {
                                connection2.disconnect();
                            }
                            if (destPath == null || request.downloadOk) {
                                return;
                            }
                            part = new File(destPath + ".part");
                            if (!part.exists() || part.delete()) {
                                return;
                            }
                            sb = new StringBuilder();
                            Log.w(ESActivity.TAG, sb.append("Could not delete ").append(part).toString());
                            return;
                        }
                        request.error = "HTTP " + code + " em " + redactUrl(current);
                        request.status = 3;
                        Log.w(ESActivity.TAG, "HTTP " + code + " -> " + redactUrl(current));
                        if (0 != 0) {
                            try {
                                fileOut2.close();
                            } catch (Exception e11) {
                            }
                        }
                        if (connection2 != null) {
                            connection2.disconnect();
                        }
                        if (destPath == null || request.downloadOk) {
                            return;
                        }
                        File part6 = new File(destPath + ".part");
                        if (!part6.exists() || part6.delete()) {
                            return;
                        }
                        Log.w(ESActivity.TAG, "Could not delete " + part6);
                        return;
                    } catch (CancelledException e12) {
                    } catch (Exception e13) {
                        e = e13;
                    }
                }
            } catch (Throwable th4) {
                fileOut = null;
                connection = null;
                th = th4;
            }
        } catch (CancelledException e14) {
        } catch (Exception e15) {
            e = e15;
            url2 = url;
        } catch (Throwable th5) {
            fileOut = null;
            connection = null;
            th = th5;
        }
    }

    private static final class CancelledException extends Exception {
        CancelledException() {
            super("cancelled");
        }
    }

    private static void downloadInParts(final String url, File part, final Request request) throws Exception {
        RandomAccessFile file;
        long total = request.total;
        long j = 1;
        long segment = ((total + 24) - 1) / 24;
        RandomAccessFile file2 = new RandomAccessFile(part, "rw");
        final Exception[] failure = new Exception[1];
        try {
            file2.setLength(total);
            final FileChannel channel = file2.getChannel();
            int i = 24;
            Thread[] workers = new Thread[24];
            int i2 = 0;
            while (true) {
                if (i2 >= i) {
                    file = file2;
                    break;
                }
                final long start = ((long) i2) * segment;
                file = file2;
                try {
                    final long end = Math.min(total, start + segment) - j;
                    if (start > end) {
                        break;
                    }
                    int i3 = i2;
                    Thread[] workers2 = workers;
                    long total2 = total;
                    try {
                        workers2[i3] = new Thread(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    HttpBridge.downloadRange(url, channel, start, end, request);
                                } catch (Exception e) {
                                    synchronized (failure) {
                                        if (failure[0] == null) {
                                            failure[0] = e;
                                        }
                                        request.cancelled = true;
                                    }
                                }
                            }
                        }, "Download-" + i3);
                        workers2[i3].start();
                        i2 = i3 + 1;
                        workers = workers2;
                        file2 = file;
                        i = 24;
                        total = total2;
                        j = 1;
                    } catch (Throwable th) {
                        th = th;
                    }
                } catch (Throwable th2) {
                    th = th2;
                }
                th = th;
                file.close();
                throw th;
            }
            for (Thread worker : workers) {
                if (worker != null) {
                    worker.join();
                }
            }
            file.close();
            if (failure[0] != null) {
                if (failure[0] instanceof CancelledException) {
                    throw failure[0];
                }
                throw new Exception("download em partes falhou: " + failure[0].getMessage(), failure[0]);
            }
            if (request.cancelled) {
                throw new CancelledException();
            }
        } catch (Throwable th3) {
            th = th3;
            file = file2;
        }
    }

    private static String describeFailure(Throwable e) {
        for (Throwable cause = e; cause != null; cause = cause.getCause()) {
            if (cause instanceof UnknownHostException) {
                return "sem internet: não foi possível encontrar o servidor";
            }
            if (cause instanceof SocketTimeoutException) {
                return "o servidor demorou demais para responder";
            }
            if ((cause instanceof ConnectException) || (cause instanceof NoRouteToHostException)) {
                return "não foi possível conectar ao servidor";
            }
            if (cause instanceof SSLException) {
                return "falha na conexão segura com o servidor";
            }
            if ((cause instanceof IOException) && cause.getMessage() != null && cause.getMessage().contains("ENOSPC")) {
                return "sem espaço no armazenamento";
            }
        }
        return String.valueOf(e.getMessage() != null ? e.getMessage() : e);
    }

    /* JADX WARN: Code duplicated, block: B:126:0x0311  */
    /* JADX WARN: Code duplicated, block: B:133:0x0378  */
    /* JADX WARN: Code duplicated, block: B:150:0x03ab  */
    /* JADX WARN: Code duplicated, block: B:192:0x038f A[SYNTHETIC] */
    public static void downloadRange(String url, FileChannel channel, long start, long end, Request request) throws Exception {
        int busy;
        int attempt;
        long position;
        int busy2;
        HttpURLConnection connection;
        byte[] buffer = new byte[262144];
        int busy3 = 0;
        long position2 = start;
        int attempt2 = 0;
        while (position2 <= end) {
            if (request.cancelled) {
                throw new CancelledException();
            }
            HttpURLConnection connection2 = null;
            try {
                try {
                    try {
                        connection2 = (HttpURLConnection) new URL(url).openConnection();
                        try {
                            connection2.setConnectTimeout(CONNECT_TIMEOUT);
                            connection2.setReadTimeout(SEGMENT_READ_TIMEOUT);
                            connection2.setRequestProperty("User-Agent", ESActivity.TAG);
                            connection2.setRequestProperty("Accept-Encoding", "identity");
                            connection2.setRequestProperty("Range", "bytes=" + position2 + "-" + end);
                            int code = connection2.getResponseCode();
                            if (code == 429 || code == 503) {
                                try {
                                    connection2.disconnect();
                                    connection2 = null;
                                    busy3++;
                                    if (busy3 > 30) {
                                        attempt = attempt2;
                                        position = position2;
                                        throw new Exception("servidor ocupado (HTTP " + code + ")");
                                    }
                                    attempt = attempt2;
                                    position = position2;
                                    try {
                                        Thread.sleep(Math.min(5000L, ((long) busy3) * 700));
                                        if (0 != 0) {
                                            connection2.disconnect();
                                        }
                                        attempt2 = attempt;
                                        buffer = buffer;
                                        position2 = position;
                                    } catch (CancelledException e) {
                                        e = e;
                                    } catch (Exception e2) {
                                        e = e2;
                                        attempt2 = attempt;
                                        position2 = position;
                                        attempt2++;
                                        if (attempt2 <= 12) {
                                            busy = busy3;
                                            throw e;
                                        }
                                        try {
                                            int busy4 = busy3;
                                            try {
                                                long wait = Math.min(SEGMENT_RETRY_MAX_MS, 500 << Math.min(attempt2 - 1, 16));
                                                busy = busy4;
                                                try {
                                                    Log.w(ESActivity.TAG, "Range " + start + "-" + end + " retry " + attempt2 + " at " + position2 + " in " + wait + "ms: " + e.getMessage());
                                                    Thread.sleep(wait);
                                                    if (connection2 != null) {
                                                        connection2.disconnect();
                                                    }
                                                    busy3 = busy;
                                                    buffer = buffer;
                                                } catch (Throwable th) {
                                                    e = th;
                                                    if (connection2 != null) {
                                                        connection2.disconnect();
                                                    }
                                                    throw e;
                                                }
                                            } catch (Throwable th2) {
                                                e = th2;
                                                if (connection2 != null) {
                                                    connection2.disconnect();
                                                }
                                                throw e;
                                            }
                                        } catch (Throwable th3) {
                                            e = th3;
                                        }
                                        e = th;
                                        if (connection2 != null) {
                                            connection2.disconnect();
                                        }
                                        throw e;
                                    } catch (Throwable th4) {
                                        e = th4;
                                        if (connection2 != null) {
                                            connection2.disconnect();
                                        }
                                        throw e;
                                    }
                                } catch (CancelledException e3) {
                                    e = e3;
                                    connection2 = connection2;
                                } catch (Exception e4) {
                                    e = e4;
                                    busy3 = busy3;
                                    connection2 = connection2;
                                } catch (Throwable th5) {
                                    e = th5;
                                    connection2 = connection2;
                                }
                            } else if (code == 206) {
                                try {
                                    InputStream in = connection2.getInputStream();
                                    while (true) {
                                        if (position2 > end) {
                                            busy2 = busy3;
                                            connection = connection2;
                                            break;
                                        }
                                        try {
                                            busy2 = busy3;
                                            connection = connection2;
                                            try {
                                                int read = in.read(buffer, 0, (int) Math.min(buffer.length, (end - position2) + 1));
                                                if (read <= 0) {
                                                    break;
                                                }
                                                if (request.cancelled) {
                                                    throw new CancelledException();
                                                }
                                                long at = position2;
                                                for (ByteBuffer chunk = ByteBuffer.wrap(buffer, 0, read); chunk.hasRemaining(); chunk = chunk) {
                                                    int attempt3 = attempt2;
                                                    try {
                                                        int attempt4 = channel.write(chunk, at);
                                                        at += (long) attempt4;
                                                        attempt2 = attempt3;
                                                        buffer = buffer;
                                                    } catch (CancelledException e5) {
                                                        e = e5;
                                                        connection2 = connection;
                                                    } catch (Exception e6) {
                                                        e = e6;
                                                        buffer = buffer;
                                                        attempt2 = attempt3;
                                                        busy3 = busy2;
                                                        connection2 = connection;
                                                        attempt2++;
                                                        if (attempt2 <= 12) {
                                                            busy = busy3;
                                                            throw e;
                                                        }
                                                        int busy5 = busy3;
                                                        long wait2 = Math.min(SEGMENT_RETRY_MAX_MS, 500 << Math.min(attempt2 - 1, 16));
                                                        busy = busy5;
                                                        Log.w(ESActivity.TAG, "Range " + start + "-" + end + " retry " + attempt2 + " at " + position2 + " in " + wait2 + "ms: " + e.getMessage());
                                                        Thread.sleep(wait2);
                                                        if (connection2 != null) {
                                                            connection2.disconnect();
                                                        }
                                                        busy3 = busy;
                                                        buffer = buffer;
                                                        e = th;
                                                        if (connection2 != null) {
                                                            connection2.disconnect();
                                                        }
                                                        throw e;
                                                    } catch (Throwable th6) {
                                                        e = th6;
                                                        connection2 = connection;
                                                        if (connection2 != null) {
                                                            connection2.disconnect();
                                                        }
                                                        throw e;
                                                    }
                                                }
                                                buffer = buffer;
                                                position2 += (long) read;
                                                try {
                                                    request.downloadedBytes.addAndGet(read);
                                                    attempt2 = 0;
                                                    buffer = buffer;
                                                    busy3 = busy2;
                                                    connection2 = connection;
                                                } catch (CancelledException e7) {
                                                    e = e7;
                                                    connection2 = connection;
                                                } catch (Exception e8) {
                                                    e = e8;
                                                    attempt2 = attempt2;
                                                    busy3 = busy2;
                                                    connection2 = connection;
                                                    attempt2++;
                                                    if (attempt2 <= 12) {
                                                        busy = busy3;
                                                        throw e;
                                                    }
                                                    int busy6 = busy3;
                                                    long wait3 = Math.min(SEGMENT_RETRY_MAX_MS, 500 << Math.min(attempt2 - 1, 16));
                                                    busy = busy6;
                                                    Log.w(ESActivity.TAG, "Range " + start + "-" + end + " retry " + attempt2 + " at " + position2 + " in " + wait3 + "ms: " + e.getMessage());
                                                    Thread.sleep(wait3);
                                                    if (connection2 != null) {
                                                        connection2.disconnect();
                                                    }
                                                    busy3 = busy;
                                                    buffer = buffer;
                                                    e = th;
                                                    if (connection2 != null) {
                                                        connection2.disconnect();
                                                    }
                                                    throw e;
                                                } catch (Throwable th7) {
                                                    e = th7;
                                                    connection2 = connection;
                                                    if (connection2 != null) {
                                                        connection2.disconnect();
                                                    }
                                                    throw e;
                                                }
                                            } catch (CancelledException e9) {
                                                e = e9;
                                                connection2 = connection;
                                            } catch (Exception e10) {
                                                e = e10;
                                                buffer = buffer;
                                                busy3 = busy2;
                                                connection2 = connection;
                                            } catch (Throwable th8) {
                                                e = th8;
                                                connection2 = connection;
                                            }
                                        } catch (CancelledException e11) {
                                            e = e11;
                                        } catch (Exception e12) {
                                            e = e12;
                                            buffer = buffer;
                                        } catch (Throwable th9) {
                                            e = th9;
                                        }
                                        try {
                                            throw e;
                                        } catch (Throwable th10) {
                                            e = th10;
                                            if (connection2 != null) {
                                                connection2.disconnect();
                                            }
                                            throw e;
                                        }
                                    }
                                    in.close();
                                    if (position2 <= end) {
                                        throw new IOException("connection closed at " + position2 + " of " + end);
                                    }
                                    if (connection != null) {
                                        connection.disconnect();
                                    }
                                    attempt2 = attempt2;
                                    busy3 = busy2;
                                    buffer = buffer;
                                } catch (CancelledException e13) {
                                    e = e13;
                                } catch (Exception e14) {
                                    e = e14;
                                    buffer = buffer;
                                } catch (Throwable th11) {
                                    e = th11;
                                }
                            } else {
                                buffer = buffer;
                                int busy7 = busy3;
                                try {
                                    throw new Exception("HTTP " + code + " numa faixa (servidor ignorou Range)");
                                } catch (CancelledException e15) {
                                    e = e15;
                                    connection2 = connection2;
                                } catch (Exception e16) {
                                    e = e16;
                                    busy3 = busy7;
                                    connection2 = connection2;
                                    attempt2++;
                                    if (attempt2 <= 12) {
                                        busy = busy3;
                                        throw e;
                                    }
                                    int busy8 = busy3;
                                    long wait4 = Math.min(SEGMENT_RETRY_MAX_MS, 500 << Math.min(attempt2 - 1, 16));
                                    busy = busy8;
                                    Log.w(ESActivity.TAG, "Range " + start + "-" + end + " retry " + attempt2 + " at " + position2 + " in " + wait4 + "ms: " + e.getMessage());
                                    Thread.sleep(wait4);
                                    if (connection2 != null) {
                                        connection2.disconnect();
                                    }
                                    busy3 = busy;
                                    buffer = buffer;
                                    e = th;
                                    if (connection2 != null) {
                                        connection2.disconnect();
                                    }
                                    throw e;
                                } catch (Throwable th12) {
                                    e = th12;
                                    connection2 = connection2;
                                    if (connection2 != null) {
                                        connection2.disconnect();
                                    }
                                    throw e;
                                }
                            }
                        } catch (CancelledException e17) {
                            e = e17;
                        } catch (Exception e18) {
                            e = e18;
                            buffer = buffer;
                        } catch (Throwable th13) {
                            e = th13;
                        }
                    } catch (CancelledException e19) {
                        e = e19;
                    }
                } catch (CancelledException e20) {
                    e = e20;
                }
            } catch (Exception e21) {
                e = e21;
                buffer = buffer;
            } catch (Throwable th14) {
                e = th14;
            }
        }
    }

    public static void extractCores(String zipPath, String destDir, Request request) {
        File file;
        ZipInputStream zip = null;
        int extracted = 0;
        try {
            try {
                ZipInputStream zip2 = new ZipInputStream(new BufferedInputStream(new FileInputStream(zipPath)));
                byte[] buffer = new byte[65536];
                while (true) {
                    ZipEntry entry = zip2.getNextEntry();
                    if (entry == null) {
                        if (extracted == 0) {
                            throw new Exception("the zip has no .so inside");
                        }
                        request.status = 1;
                        try {
                            zip2.close();
                        } catch (Exception e) {
                        }
                        file = new File(zipPath);
                        break;
                    }
                    String name = new File(entry.getName()).getName();
                    if (!entry.isDirectory() && name.endsWith(".so")) {
                        File part = new File(destDir, name + ".part");
                        File dest = new File(destDir, name);
                        OutputStream out = new FileOutputStream(part);
                        while (true) {
                            try {
                                int read = zip2.read(buffer);
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
                        if (dest.exists() && !dest.delete()) {
                            throw new Exception("could not replace " + dest);
                        }
                        if (!part.renameTo(dest)) {
                            throw new Exception("could not rename " + part);
                        }
                        extracted++;
                    }
                }
            } catch (Exception e2) {
                Log.w(ESActivity.TAG, "Could not extract core from " + zipPath, e2);
                request.error = String.valueOf(e2.getMessage() != null ? e2.getMessage() : e2);
                request.status = 4;
                if (0 != 0) {
                    try {
                        zip.close();
                    } catch (Exception e3) {
                    }
                }
                file = new File(zipPath);
            }
            file.delete();
        } catch (Throwable th2) {
            if (0 != 0) {
                try {
                    zip.close();
                } catch (Exception e4) {
                }
            }
            new File(zipPath).delete();
            throw th2;
        }
    }

    public static void extractAll(String zipPath, String destDir, Request request) throws Throwable {
        Throwable th;
        ZipInputStream zip = null;
        int extracted = 0;
        try {
            try {
                File root = new File(destDir).getCanonicalFile();
                String rootPath = root.getPath() + File.separator;
                zip = new ZipInputStream(new BufferedInputStream(new FileInputStream(zipPath)));
                try {
                    byte[] buffer = new byte[65536];
                    while (true) {
                        ZipEntry entry = zip.getNextEntry();
                        if (entry == null) {
                            ZipInputStream zip2 = zip;
                            if (extracted == 0) {
                                throw new Exception("the zip is empty");
                            }
                            Log.i(ESActivity.TAG, "Extracted " + extracted + " files from " + zipPath + " into " + destDir);
                            request.status = 1;
                            try {
                                zip2.close();
                            } catch (Exception e) {
                            }
                            new File(zipPath).delete();
                            return;
                        }
                        File target = new File(root, entry.getName()).getCanonicalFile();
                        if (!target.getPath().startsWith(rootPath)) {
                            throw new Exception("zip entry escapes the destination: " + entry.getName());
                        }
                        if (entry.isDirectory()) {
                            target.mkdirs();
                        } else {
                            File parent = target.getParentFile();
                            if (parent != null && !parent.exists() && !parent.mkdirs()) {
                                throw new Exception("could not create " + parent);
                            }
                            File part = new File(target.getPath() + ".part");
                            OutputStream out = new FileOutputStream(part);
                            while (true) {
                                try {
                                    int read = zip.read(buffer);
                                    if (read <= 0) {
                                        break;
                                    }
                                    try {
                                        out.write(buffer, 0, read);
                                    } catch (Throwable th2) {
                                        th = th2;
                                        out.close();
                                        throw th;
                                    }
                                } catch (Throwable th3) {
                                    th = th3;
                                }
                            }
                            out.close();
                            if (target.exists() && !target.delete()) {
                                throw new Exception("could not replace " + target);
                            }
                            try {
                                if (!part.renameTo(target)) {
                                    throw new Exception("could not rename " + part);
                                }
                                extracted++;
                                zip = zip;
                            } catch (Exception e2) {
                                e = e2;
                                zip = zip;
                            } catch (Throwable th4) {
                                th = th4;
                                zip = zip;
                                if (zip != null) {
                                    try {
                                        zip.close();
                                    } catch (Exception e3) {
                                    }
                                }
                                new File(zipPath).delete();
                                throw th;
                            }
                        }
                        Log.w(ESActivity.TAG, "Could not extract " + zipPath, e);
                        request.error = String.valueOf(e.getMessage() != null ? e.getMessage() : e);
                        request.status = 4;
                        if (zip != null) {
                            try {
                                zip.close();
                            } catch (Exception e4) {
                            }
                        }
                        new File(zipPath).delete();
                        return;
                    }
                } catch (Exception e5) {
                    e = e5;
                } catch (Throwable th5) {
                    th = th5;
                }
            } catch (Throwable th6) {
                th = th6;
            }
        } catch (Exception e6) {
            e = e6;
        }
    }

    public static int poll(int id) {
        Request request = REQUESTS.get(Integer.valueOf(id));
        if (request == null) {
            return 2;
        }
        return request.status;
    }

    public static byte[] content(int id) {
        Request request = REQUESTS.get(Integer.valueOf(id));
        return (request == null || request.content == null) ? new byte[0] : request.content;
    }

    public static String error(int id) {
        Request request = REQUESTS.get(Integer.valueOf(id));
        return request == null ? "unknown request" : request.error;
    }

    public static long[] progress(int id) {
        Request request = REQUESTS.get(Integer.valueOf(id));
        if (request != null) {
            return new long[]{request.downloadedBytes.get(), request.total};
        }
        return new long[]{0, -1};
    }

    public static void cancel(int id) {
        Request request = REQUESTS.get(Integer.valueOf(id));
        if (request != null) {
            request.userCancelled = true;
            request.cancelled = true;
        }
    }

    public static void release(int id) {
        Request request = REQUESTS.remove(Integer.valueOf(id));
        if (request != null) {
            request.cancelled = true;
        }
    }
}
