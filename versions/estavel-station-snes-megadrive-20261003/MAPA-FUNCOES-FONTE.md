# Índice de declarações nos fontes

Índice de navegação, não parser semântico; assinaturas Java completas em FUNCOES-JAVA-COMPILADAS.txt. Declarações em linhas múltiplas continuam no fonte.

## src/java/org/emulationstation/frontend/AssetInstaller.java

```text
15: private AssetInstaller() {}
16: public static synchronized void installIfNeeded(Context context,File homeDir) {
21: public String[] list(String path)throws IOException{return assets.list(path);}
22: public InputStream open(String path)throws IOException{return assets.open(path);}
```

## src/java/org/emulationstation/frontend/auth/LoginActivity.java

```text
54: private void openCommercial() {
95: public static void ensureAuthorized(Activity activity) {
100: protected void onCreate(Bundle bundle) {
138: public void onConfigurationChanged(Configuration configuration) {
151: private void buildScreen() {
315: public void onClick(View view4) {
321: public boolean onEditorAction(TextView textView, int i3, KeyEvent keyEvent) {
334: public void submit() {
344: public void ok(String name){commercialOk(name);}
345: public void fail(String message){commercialFail(message);}
349: private void openFrontend() {
378: private boolean storageAllowed(){
382: private void storageReturned(){
389: @Override protected void onActivityResult(int request,int result,Intent data){
392: @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] results){
397: protected void onNewIntent(Intent intent) {
407: public void onBackPressed() {
414: private ImageView mark() {
422: private LinearLayout column() {
428: private TextView text(String str, int i, int i2) {
437: private GradientDrawable shape(int i, int i2, int i3) {
445: private void add(LinearLayout linearLayout, View view, int i) {
451: private int dp(int i) {
466: protected void onSizeChanged(int i, int i2, int i3, int i4) {
471: protected void onDraw(Canvas canvas) {
488: @Override protected void onStop() {
496: @Override protected void onDestroy() {
```

## src/java/org/emulationstation/frontend/auth/StationLogin.java

```text
13: public interface Callback {void ok(String name);void fail(String message);}
15: private static final Handler MAIN=new Handler(Looper.getMainLooper());
18: private StationLogin() {}
19: public static String displayName(){StationCoordinator owner=coordinator;StationCoordinator.Library current=owner==null?null:owner.current();return current==null?"":current.displayName;}
20: public static boolean ready(){StationCoordinator current=coordinator;return current!=null&&current.ready();}
21: public static boolean hasLicense(Context context){return new java.io.File(context.getNoBackupFilesDir(),"station-license-id.txt").isFile();}
22: public static boolean rememberAccess(Context context){
25: public static void rememberAccess(Context context,boolean enabled){
28: private static final java.util.WeakHashMap<Activity,StationApi.Cancellation> renewing=new java.util.WeakHashMap<>();
29: public static void ensureAuthorized(Activity activity) {
34: public void ok(String name){synchronized(renewing){renewing.remove(activity);}activity.onWindowFocusChanged(activity.hasWindowFocus());}
35: public void fail(String message){synchronized(renewing){renewing.remove(activity);}showLogin(activity);}
41: private static void showLogin(Activity activity) {
47: public static StationApi.Cancellation begin(Activity activity,String code,Callback callback) {
62: private static String message(Exception error) {
```

## src/java/org/emulationstation/frontend/DownloadService.java

```text
11: private static final Handler MAIN=new Handler(Looper.getMainLooper());
12: private static final Map<String,Job> ACTIVE=new LinkedHashMap<>();
17: private static final class Job {String name,message;long done,total;Job(String name,long done,long total,String message){this.name=name;this.done=done;this.total=total;this.message=message;}}
18: public static void changed(Context context,String id,String name,boolean active,long done,long total,String message,int result){
27: @Override public void onCreate(){
34: @Override public int onStartCommand(Intent intent,int flags,int startId){
38: private void update(boolean force){long now=SystemClock.elapsedRealtime();if(!force&&now-lastUpdate<1000)return;lastUpdate=now;
41: private Notification notification(){
51: @Override public void onDestroy(){if(wake!=null&&wake.isHeld())wake.release();if(instance==this)instance=null;requested=false;super.onDestroy();}
52: @Override public IBinder onBind(Intent intent){return null;}
```

## src/java/org/emulationstation/frontend/station/ExistingCoverCache.java

```text
11: private final Map<String,Long> revisions=new HashMap<>();
12: public ExistingCoverCache(Path directory) throws IOException {
31: @Override public byte[] find(String coverId,long revision) throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationAndroid.java

```text
17: public static synchronized StationAndroid get(Context context) throws Exception {
18: if (instance == null) instance = new StationAndroid(context.getApplicationContext());
21: static StationAndroid current(){return instance;}
29: private StationAndroid(Context context) throws Exception {
38: public PublicKey publicKey() throws Exception {return StationCrypto.publicKey();}
39: public byte[] sign(byte[] payload) throws Exception {return StationCrypto.sign(payload);}
40: public String manufacturer(){return deviceText(Build.MANUFACTURER);}
41: public String model(){return deviceText(Build.MODEL);}
42: public int sdk(){return Build.VERSION.SDK_INT;}
46: api=new StationApi(new StationHttp(),identity,clock,authority,StationConfig.STATION_ASSERTION_KEY_ID);
48: sessions=new StationSessions(api,clock,privateFiles.resolve("station-license-id.txt"));
49: catalogs=new StationCatalogStore(privateFiles.resolve("station-v2/catalog"));
50: covers=new StationCoverStore(privateFiles.resolve("station-v2/covers"),api,sessions,clock,
52: coordinator=new StationCoordinator(api,sessions,catalogs,covers,privateFiles,clock);
54: private static String deviceText(String value) {
59: private static void validateImage(byte[] bytes) throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationApi.java

```text
20: public interface Clock { long millis(); }
27: public Response(int status, String type, long length, InputStream body, Closeable owner) {
30: @Override public void close() throws IOException { owner.close(); }
35: public synchronized void cancel() { cancelled=true; if (abort != null) abort.run(); }
36: @Override public boolean cancelled() { return cancelled || Thread.currentThread().isInterrupted(); }
37: public void check() throws InterruptedIOException {
49: public boolean sessionDenied() { return status == 401 || status == 403; }
56: private Session(StationApi owner,String licenseId,String deviceId,String sessionId,String token,long expires) {
59: public boolean needsRenewal(long monotonicMillis) { return monotonicMillis >= expires - 15000; }
68: private final AtomicBoolean consumed = new AtomicBoolean();
69: private Grant(String itemId,long revision,StationArtifact artifact,String grantId,long expires,Session session) {
76: private CatalogSnapshot(StationCatalog catalog,byte[] signedEnvelope) {
79: public byte[] encoded() { return signedEnvelope.clone(); }
86: private static final PSSParameterSpec PSS=new PSSParameterSpec("SHA-256","MGF1",MGF1ParameterSpec.SHA256,32,1);
94: public StationApi(Transport transport, Device device, Clock clock, PublicKey authority, String authorityId) throws Exception {
99: public String activate(String code, Cancellation cancel) throws Exception {
117: public Session openSession(String licenseId,Cancellation cancel) throws Exception {
135: public String profile(Session session,Cancellation cancel) throws Exception {
141: public StationCatalog catalog(Session session,Cancellation cancel) throws Exception {
144: public CatalogSnapshot catalogSnapshot(Session session,Cancellation cancel) throws Exception {
150: public CatalogSnapshot restoreCatalog(byte[] envelope,Session session) throws Exception {
157: public byte[] cover(Session session,String coverId,Cancellation cancel) throws Exception {
173: public Grant authorize(Session session,String itemId,long expectedRevision,Cancellation cancel) throws Exception {
196: public ArtifactTransfer openArtifact(Grant grant,long maximumBytes,Cancellation cancel) throws Exception {
212: private final AtomicBoolean copied=new AtomicBoolean(),closed=new AtomicBoolean();
213: private ArtifactTransfer(Response response,StationArtifact artifact,long maximum){this.response=response;this.artifact=artifact;this.maximum=maximum;}
214: public StationFiles.Receipt copyToStaging(Path file,Cancellation cancel,StationFiles.Progress progress)throws Exception {
218: public void close()throws IOException{if(closed.compareAndSet(false,true))response.close();}
236: private JSONObject verify(byte[] encoded,String domain,Session session,boolean previousSession) throws Exception {
258: private byte[] identity(String domain,String extra) {
261: private byte[] envelope(byte[] payload) throws Exception {
265: private void valid(Session session) throws IOException {
268: private void notExpired(long deadline) throws IOException { if (clock.millis() >= deadline) throw new IOException("Station authorization expired"); }
269: private static String hexId(String value) throws IOException {
272: private static String token(String token) throws IOException {
275: private static void lifetime(JSONObject body,int seconds) throws Exception {
278: static String string(JSONObject body,String key) throws JSONException,IOException {
281: private static void equal(JSONObject body,String key,String expected) throws JSONException,IOException {
284: private static String field(String key,String value) {return StationProtocol.field(key,value);}
285: private static String mime(String type) {return type == null?"":type.split(";",2)[0].trim().toLowerCase(Locale.ROOT);}
286: private static String utf8(byte[] bytes) throws CharacterCodingException {
290: private static void success(Response response,Cancellation cancel) throws Exception {
301: private static byte[] read(Response response,int maximum,Cancellation cancel) throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationArchive.java

```text
7: private static final class Library {static {System.loadLibrary("station_archive");}static void ready() {}}
8: public void read(Path file,StationInstaller.Sink sink,StationApi.Cancellation cancel)throws Exception {
11: private static native void readArchive(String path,StationInstaller.Sink sink,StationApi.Cancellation cancel) throws Exception;
```

## src/java/org/emulationstation/frontend/station/StationArtifact.java

```text
15: private StationArtifact(String name,long size,String hash,String format,String launch,long expanded,int count) {
19: static StationArtifact parse(JSONObject value) throws Exception {
34: return new StationArtifact(name,size,hash,format,launch,expanded,count);
36: static long bounded(JSONObject value,String key,long maximum)throws Exception {
42: public static String relativePath(String value,int maximum)throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationBundledFiles.java

```text
8: public interface Source { String[] list(String path)throws IOException; InputStream open(String path)throws IOException; }
9: private StationBundledFiles() {}
10: public static int install(Source source,String assetPath,Path target,boolean replaceExisting)throws IOException {
13: private static int install(Source source,String assetPath,Path target,boolean replace,int depth)throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationCatalog.java

```text
24: private Item(String itemId, String name, String platform, long revision, String coverId) {
34: private StationCatalog(long revision, List<Item> items, Map<String, Item> byId) {
40: public Item find(String itemId) { return byId.get(itemId); }
43: public static StationCatalog fromVerifiedPayload(JSONObject payload) throws IOException {
60: return new StationCatalog(revision, items, byId);
66: public byte[] localPayload() throws IOException {
85: public static String libraryId(String value) throws IOException {
91: public static String plainText(String value, int limit) throws IOException {
103: static long integer(JSONObject row, String key) throws JSONException, IOException {
```

## src/java/org/emulationstation/frontend/station/StationCatalogStore.java

```text
10: public StationCatalogStore(Path directory) throws IOException {
13: public synchronized StationApi.CatalogSnapshot read(StationApi api,StationApi.Session session) throws Exception {
33: private Path file(StationApi.Session session) throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationConfig.java

```text
14: private StationConfig() {}
16: public static boolean ready() {
```

## src/java/org/emulationstation/frontend/station/StationCoordinator.java

```text
14: private Library(String displayName,StationCatalog catalog,boolean cached) {
26: public StationCoordinator(StationApi api,StationSessions sessions,StationCatalogStore catalogs,
31: public synchronized Library login(String code,StationApi.Cancellation cancel) throws Exception {
40: public synchronized Library refresh(StationApi.Cancellation cancel) throws Exception {
47: public synchronized Path cover(String itemId,StationApi.Cancellation cancel) throws Exception {
62: public synchronized StationApi.Grant authorize(String itemId,StationApi.Cancellation cancel) throws Exception {
76: public boolean ready() {
81: public Library current() {return library;}
82: public synchronized void logout() {authorized=null;library=null;sessions.forgetSession();}
83: private synchronized void invalidate(StationApi.Session session) {
86: private Library loadCatalog(StationApi.Session session,String name,StationApi.Cancellation cancel) throws Exception {
100: private String loadName(StationApi.Session session,StationApi.Cancellation cancel) throws Exception {
107: private Path nameFile(StationApi.Session session) {
111: private String readName(StationApi.Session session) {
119: private void saveName(StationApi.Session session,String name,StationApi.Cancellation cancel) throws Exception {
```

## src/java/org/emulationstation/frontend/station/StationCoverStore.java

```text
10: public interface PreviousCovers { byte[] find(String coverId,long revision) throws IOException; }
11: public interface ImageValidator { void validate(byte[] bytes) throws IOException; }
12: public interface Waiter { void waitMillis(long millis) throws InterruptedException; }
26: private final Map<String,Checked> checked=new LinkedHashMap<String,Checked>(256,0.75f,true) {
27: protected boolean removeEldestEntry(Map.Entry<String,Checked> e) {return size()>256;}
29: private final Map<String,Long> unavailable=new LinkedHashMap<String,Long>(128,0.75f,true) {
30: protected boolean removeEldestEntry(Map.Entry<String,Long> e) {return size()>128;}
32: public StationCoverStore(Path directory,StationApi api,StationSessions sessions,
36: public StationCoverStore(Path directory,StationApi api,StationSessions sessions,
42: public synchronized Path get(String coverId,long revision,StationApi.Cancellation cancel) throws Exception {
46: public synchronized Path get(StationApi.Session session,String coverId,long revision,StationApi.Cancellation cancel) throws Exception {
```

## src/java/org/emulationstation/frontend/station/StationCrypto.java

```text
16: private static final PSSParameterSpec PSS = new PSSParameterSpec("SHA-256", "MGF1", MGF1ParameterSpec.SHA256, 32, 1);
18: private StationCrypto() {}
20: public static synchronized PublicKey publicKey() throws Exception {
35: public static byte[] sign(byte[] message) throws Exception {
```

## src/java/org/emulationstation/frontend/station/StationDiagnostics.java

```text
8: public interface Observer {void event(Event event,int status,long count);}
9: public interface TraceObserver {void event(Event event,int status,String correlation,String itemTag,String coverTag,long revision);}
10: private static volatile TraceObserver traceObserver=(e,s,c,i,v,r)->{};
11: private static final ThreadLocal<Selection> selected=new ThreadLocal<>();
18: private Scope(Selection value){previous=selected.get();selected.set(value);}
19: public void close(){if(previous==null)selected.remove();else selected.set(previous);}
21: private static volatile Observer observer=(event,status,count)->{};
22: private StationDiagnostics(){}
23: public static void observe(Observer value){observer=value==null?(event,status,count)->{}:value;}
24: public static void observeTrace(TraceObserver value){traceObserver=value==null?(e,s,c,i,v,r)->{}:value;}
25: public static Scope selection(String item,String cover,long revision){return new Scope(new Selection(item,cover,revision));}
26: static String tag(String id){
31: static void trace(Event event,int status,String correlation){
37: public static void record(Event event,int status,long count){
40: static Event route(String path){
50: static void serverFailure(int status,String code){
61: static int status(Exception e){return e instanceof StationApi.Failure?((StationApi.Failure)e).status:0;}
```

## src/java/org/emulationstation/frontend/station/StationDownloads.java

```text
14: private final ConcurrentHashMap<String,StationApi.Cancellation> jobs=new ConcurrentHashMap<>();
15: private final ThreadPoolExecutor worker=new ThreadPoolExecutor(0,1,10,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(4),r->{Thread t=new Thread(r,"Station-install");t.setDaemon(true);return t;});
16: public StationDownloads(StationApi api,StationCoordinator owner,StationInstaller installer,Path staging,Listener listener)throws IOException {
19: public boolean start(String id) {
25: private void run(String id,StationApi.Cancellation cancel) {
71: public void cancel(String id){StationApi.Cancellation job=jobs.get(id);if(job!=null)job.cancel();}
72: public int activeCount(){return jobs.size();}
73: public void uninstall(String id) {
79: public StationInstaller.Installed find(StationCatalog.Item item)throws Exception{return installer.find(item);}
80: public void close(){for(StationApi.Cancellation cancel:jobs.values())cancel.cancel();worker.shutdown();}
82: static String message(Exception error,StationApi.Cancellation cancel) {
```

## src/java/org/emulationstation/frontend/station/StationExistingArtifact.java

```text
9: private StationExistingArtifact(){}
10: static Path find(Path platformDirectory,StationArtifact spec,StationApi.Cancellation cancel)throws Exception {
19: public FileVisitResult preVisitDirectory(Path dir,BasicFileAttributes attrs)throws IOException{
22: public FileVisitResult visitFile(Path file,BasicFileAttributes attrs)throws IOException{
27: public FileVisitResult visitFileFailed(Path file,IOException error)throws IOException{cancel.check();return FileVisitResult.CONTINUE;}
```

## src/java/org/emulationstation/frontend/station/StationFiles.java

```text
15: public interface Cancellation { boolean cancelled(); }
16: public interface Progress { void changed(long received, long total); }
17: public static final Cancellation NEVER_CANCELLED = () -> false;
18: public static final Progress NO_PROGRESS = (received, total) -> {};
25: private StationFiles() {}
86: public static byte[] readBounded(Path file, int maximum) throws IOException {
102: public static String imageExtension(byte[] bytes) throws IOException {
110: public static String archiveType(byte[] prefix) {
119: private static boolean ascii(byte[] data, int at, String value) {
125: private static boolean matches(byte[] data, int at, int[] value) {
131: private static void checkCancelled(Cancellation cancellation) throws InterruptedIOException {
136: private static String hex(byte[] data) {
```

## src/java/org/emulationstation/frontend/station/StationFrontend.java

```text
11: static {System.loadLibrary("station_frontend");}
12: private static final ThreadPoolExecutor commands=pool("Station-catalog",8),images=pool("Station-covers",32);
13: private static final ConcurrentHashMap<String,StationApi.Cancellation> requests=new ConcurrentHashMap<>();
17: private static ThreadPoolExecutor pool(String name,int capacity){return new ThreadPoolExecutor(0,1,10,TimeUnit.SECONDS,new ArrayBlockingQueue<Runnable>(capacity),r->{Thread t=new Thread(r,name);t.setDaemon(true);return t;});}
18: private StationFrontend(){}
19: public static boolean authorized(){StationAndroid app=StationAndroid.current();return app!=null&&app.coordinator.ready();}
20: public static void requestLogin(){StationAndroid app=StationAndroid.current();if(app!=null){
24: public static void configure(String romsRoot) {
36: private static void prepareStorage(StationAndroid app,String romsRoot)throws Exception {
41: StationInstaller installer=new StationInstaller(roms,app.privateFiles.resolve("station-v2/installs"),new StationArchive());
42: downloads=new StationDownloads(app.api,app.coordinator,installer,roms.resolve(".station-v2/staging"),
50: public static void refresh(){execute(()->{
56: private static void publishCurrent(StationAndroid app)throws Exception {
58: StationPublication publication=new StationPublication(library.catalog);
81: public static boolean start(String itemId){StationDownloads current=downloads;return current!=null&&current.start(itemId);}
82: public static void cancel(String itemId){StationDownloads current=downloads;if(current!=null)current.cancel(itemId);}
83: public static boolean remove(String itemId){StationDownloads current=downloads;if(current==null)return false;current.uninstall(itemId);return true;}
84: public static int activeCount(){StationDownloads current=downloads;return current==null?0:current.activeCount();}
85: public static void cover(String itemId){
93: public static void setForeground(boolean visible){boolean resumed=visible&&!foreground;foreground=visible;if(!visible){for(StationApi.Cancellation cancel:requests.values())cancel.cancel();}else if(resumed){if(!configured&&requestedStorageRoot!=null)configure(requestedStorageRoot);else if(configured)reconcile();}}
94: public static void reconcile(){execute(()->{try{StationAndroid app=StationAndroid.current();if(app!=null&&downloads!=null)publishCurrent(app);}catch(Exception e){publishError(utf8("Não foi possível conferir os jogos instalados."));}});}
95: private static boolean execute(Runnable operation){try{commands.execute(operation);return true;}catch(RejectedExecutionException busy){publishError(utf8("Aguarde a consulta em andamento."));return false;}}
96: private static String catalogError(Exception e,String fallback){
103: private static String safeReason(Exception e){if(e instanceof StationStorage.Failure)return ((StationStorage.Failure)e).reason;String m=e.getMessage();if(m!=null&&(m.equals("Symbolic path refused")||m.equals("Invalid catalog identity")))return m;return "operation failed";}
104: private static byte[] utf8(String text){return text.getBytes(StandardCharsets.UTF_8);}
105: private static native void publishPreparation(int done,int total,long bytes);
106: private static native void publishCatalog(byte[][] rows,byte[] displayName);
107: private static native void publishCover(String itemId,byte[] path);
108: private static native void publishJob(String itemId,boolean active,long received,long total,byte[] message,byte[] launch,int result);
109: private static native void publishError(byte[] message);
```

## src/java/org/emulationstation/frontend/station/StationHttp.java

```text
14: public StationHttp() throws Exception {
28: public X509Certificate[] getAcceptedIssuers() { return trust.getAcceptedIssuers(); }
29: public void checkClientTrusted(X509Certificate[] chain, String type) throws CertificateException {
32: public void checkServerTrusted(X509Certificate[] chain, String type) throws CertificateException {
100: static boolean allowed(String method, String path) {
111: private static byte[] decodeHex(String value) throws GeneralSecurityException {
```

## src/java/org/emulationstation/frontend/station/StationInstaller.java

```text
25: private Installed(String id,String platform,long revision,Path launch){this.itemId=id;this.platform=platform;this.revision=revision;this.launchPath=launch;}
31: public StationInstaller(Path roms,Path privateRecords,Reader reader)throws IOException {
81: public Path existingArtifact(StationCatalog.Item item,StationArtifact spec,StationApi.Cancellation cancel)throws Exception {
84: public synchronized Installed find(StationCatalog.Item item)throws Exception {
103: public synchronized void uninstall(String itemId)throws Exception {
123: private Path record(String id)throws IOException {return records.resolve(StationCatalog.libraryId(id)+".json");}
124: private JSONObject readRecord(String id)throws Exception {
129: private Path content(JSONObject value,String id)throws Exception {
135: static Path directory(Path path)throws IOException {
138: static void checkParents(Path path)throws IOException {
142: static String digest(Path file,StationApi.Cancellation cancel)throws Exception {
148: private static void removeEmptyParents(Path path,Path stop)throws IOException {
154: private static void deleteOwnTree(Path path,Path owner)throws IOException {
159: public FileVisitResult visitFile(Path file,java.nio.file.attribute.BasicFileAttributes attrs)throws IOException{Files.delete(file);return FileVisitResult.CONTINUE;}
160: public FileVisitResult postVisitDirectory(Path dir,IOException error)throws IOException{if(error!=null)throw error;Files.delete(dir);return FileVisitResult.CONTINUE;}
163: private static void checkReferences(Path content,Path launch,Set<String> files)throws Exception {
186: public void begin(byte[] utf8,long size,boolean dir)throws Exception {
202: public void data(byte[] bytes,int length)throws Exception {
206: public void end()throws Exception {
212: public void close()throws IOException{if(output!=null){output.close();output=null;}}
```

## src/java/org/emulationstation/frontend/station/StationPlatforms.java

```text
10: private Platform(String label,String folder) {this.label=label;this.folder=folder;}
98: private UnsupportedPlatform(String platform){super("Platform has no verified local mapping");this.platform=platform;}
100: private StationPlatforms() {}
101: public static Platform resolve(String platform) throws IOException {
```

## src/java/org/emulationstation/frontend/station/StationProtocol.java

```text
25: private StationProtocol() {}
27: public static String deviceId(byte[] spki) {
31: public static boolean libraryId(String value) {
42: public static boolean licenseId(String value) {
53: public static boolean activationCode(String value) {
61: public static String base64Url(byte[] data) {
65: public static byte[] decode(String value) {
75: public static byte[] sha256(byte[] data) {
99: public static String field(String name, String value) {
103: public static String field(String name, int value) {
107: public static String quote(String value) {
```

## src/java/org/emulationstation/frontend/station/StationPublication.java

```text
10: private Row(StationCatalog.Item item,StationPlatforms.Platform platform){this.item=item;this.platform=platform;}
15: public StationPublication(StationCatalog catalog)throws IOException {
24: public String warning(){
```

## src/java/org/emulationstation/frontend/station/StationSessions.java

```text
13: public StationSessions(StationApi api,StationApi.Clock clock,Path licenseFile) {
16: public synchronized StationApi.Session activate(String code,StationApi.Cancellation cancel) throws Exception {
24: public synchronized StationApi.Session get(StationApi.Cancellation cancel) throws Exception {
33: public synchronized void denied(StationApi.Session rejected) {
36: public StationApi.Session peek() {return current;}
37: public synchronized void forgetSession() {current=null;}
```

## src/java/org/emulationstation/frontend/station/StationStorage.java

```text
9: private StationStorage() {}
12: public static long usableBytes(Path directory) throws IOException {
22: private Failure(String reason, String message, Exception cause) {
27: public static Path prepareRoot(Path supplied) throws Failure {
```

## src/native/station_archive.c

```text
11: static void fail(JNIEnv *e,const char *reason) {
```

## src/native/station_catalog_abi.hpp

```text
```

## src/native/station_cover_retry.hpp

```text
```

## src/native/station_frontend.cpp

```text
172: API void StationCatalog_refresh(Catalog* catalog,const std::string&){
180: API void StationCatalog_update(Catalog* catalog){drain(catalog);if(owned(catalog)&&catalog->items.empty())apply(catalog);queueCovers(catalog);}
181: API bool StationCatalog_applyPending(Catalog* catalog){drain(catalog);return apply(catalog);}
182: API void StationCatalog_refreshInstalled(Catalog* catalog){if(owned(catalog))command(reconcileMethod);}
183: API void StationCatalog_prioritize(Catalog* catalog,const std::vector<size_t>& indices){
186: API bool StationCatalog_start(Catalog* catalog,size_t index){
191: API void StationCatalog_cancel(Catalog* catalog,size_t index){if(owned(catalog)&&index<catalog->items.size())command(cancelMethod,&catalog->items[index].id);}
192: API bool StationCatalog_uninstall(Catalog* catalog,size_t index){return owned(catalog)&&index<catalog->items.size()&&command(removeMethod,&catalog->items[index].id,true);}
193: API std::vector<size_t> StationCatalog_active(Catalog* catalog){std::vector<size_t> result;if(owned(catalog))for(size_t i=0;i<catalog->items.size();++i){auto job=state.jobs.find(catalog->items[i].id);if(job!=state.jobs.end()&&job->second.progress.active)result.push_back(i);}return result;}
194: API Progress StationCatalog_progress(Catalog* catalog,size_t index){if(owned(catalog)&&index<catalog->items.size()){auto job=state.jobs.find(catalog->items[index].id);if(job!=state.jobs.end())return job->second.progress;}return {};}
198: static void* handle=dlopen("libmain.so",RTLD_NOW|RTLD_NOLOAD);
212: API void StationLicense_sync(LicenseView* view){
217: API void StationLicense_enter(LicenseView* view){StationLicense_sync(view);if(view&&view->state!=2)command(loginMethod);}
219: API void StationStats_init(LocalUsage* self){
225: API void StationStats_update(LocalUsage* self){flush(self);}
226: API void StationStats_background(LocalUsage* self,bool background){if(self){self->background=background;if(background)flush(self);}}
227: API void StationStats_start(LocalUsage* self,const std::string& game,const std::string& platform,const std::string& core){
228: if(!self)return;StationStats_init(self);self->game=game;self->platform=platform;self->core=core;self->gameStarted=std::time(nullptr);
230: API void StationStats_end(LocalUsage* self,const std::string&,double,double,double seconds){
239: API void StationStats_shutdown(LocalUsage* self){if(self){StationStats_end(self,"",0,0,-1);flush(self);self->ready=false;}}
240: API void StationStats_event(LocalUsage* self,const std::string&,const std::string&){flush(self);}
241: API bool StationCore_request(Catalog* catalog){
250: static uintptr_t base=[](){auto symbol=mainSymbol<void*>("_ZN14CatalogServiceC1Ev");Dl_info info{};return symbol&&dladdr(symbol,&info)?reinterpret_cast<uintptr_t>(info.dli_fbase):uintptr_t(0);}();
279: API void StationLoading_draw(void* gui,const void* matrix){
```
