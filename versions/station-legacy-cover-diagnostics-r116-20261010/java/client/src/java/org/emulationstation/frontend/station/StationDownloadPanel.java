package org.emulationstation.frontend.station;

import android.app.*;
import android.os.*;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.util.LruCache;
import android.view.*;
import android.widget.*;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;

/** Full-screen download list opened by the additional native header notice. */
public final class StationDownloadPanel extends Dialog {
 private static StationDownloadPanel visible;
 private static final ExecutorService controls=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"Station-download-control");t.setDaemon(true);return t;});
 private final Activity owner;private final Handler main=new Handler(Looper.getMainLooper());
 private final LruCache<String,Bitmap> images=new LruCache<String,Bitmap>(8*1024*1024){@Override protected int sizeOf(String key,Bitmap value){return value.getAllocationByteCount();}};
 private final Set<String> loading=new HashSet<>();
 private final Set<Runnable> delayedCoverRetries=new HashSet<>();
 private final Map<String,StationCoverQueue.Handle> coverHandles=new HashMap<>();
 private List<StationDownloads.Entry> rows=Collections.emptyList();private final Adapter adapter=new Adapter();
 private TextView summary;private boolean closed;
 private final Runnable tick=new Runnable(){public void run(){if(closed)return;rows=StationFrontend.downloadEntries();adapter.notifyDataSetChanged();int active=0;for(StationDownloads.Entry e:rows)if(e.active())active++;
  summary.setText(active==0?"Seus downloads":"Downloads em andamento · "+active);main.postDelayed(this,1000);}};
 private final Application.ActivityLifecycleCallbacks lifecycle=new Application.ActivityLifecycleCallbacks(){
  public void onActivityStopped(Activity a){if(a==owner)dismiss();}public void onActivityDestroyed(Activity a){if(a==owner)dismiss();}
  public void onActivityCreated(Activity a,Bundle b){}public void onActivityStarted(Activity a){}public void onActivityResumed(Activity a){}public void onActivityPaused(Activity a){}public void onActivitySaveInstanceState(Activity a,Bundle b){}
 };
 public static boolean open(Activity a){if(a==null||a.isFinishing())return false;a.runOnUiThread(()->{if(a.isFinishing()||a.isDestroyed()||visible!=null)return;visible=new StationDownloadPanel(a);visible.show();});return true;}
 private StationDownloadPanel(Activity a){super(a,android.R.style.Theme_Material_NoActionBar_Fullscreen);owner=a;}
 private int dp(float n){return Math.round(n*owner.getResources().getDisplayMetrics().density);}
 private GradientDrawable background(int color,int radius){GradientDrawable b=new GradientDrawable();b.setColor(color);b.setCornerRadius(dp(radius));return b;}
 private TextView text(String value,int size,int color){TextView t=new TextView(owner);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setGravity(Gravity.CENTER_VERTICAL);return t;}
 private TextView button(String label,int color){TextView t=text(label,13,0xffedf9f2);t.setGravity(Gravity.CENTER);t.setTypeface(null,Typeface.BOLD);t.setBackground(background(color,8));t.setPadding(dp(14),0,dp(14),0);t.setMinWidth(dp(82));t.setFocusable(true);return t;}
 @Override protected void onCreate(Bundle state){super.onCreate(state);getWindow().setLayout(-1,-1);getWindow().getDecorView().setSystemUiVisibility(5894);
  LinearLayout page=new LinearLayout(owner);page.setOrientation(1);page.setPadding(dp(24),dp(14),dp(24),dp(12));page.setBackgroundColor(0xff080e0c);
  LinearLayout header=new LinearLayout(owner);header.setGravity(Gravity.CENTER_VERTICAL);
  TextView back=button("‹  VOLTAR",0xff18291f);back.setOnClickListener(v->dismiss());header.addView(back,new LinearLayout.LayoutParams(-2,dp(38)));
  TextView title=text("DOWNLOADS",23,0xfff2fff6);title.setTypeface(null,Typeface.BOLD);title.setPadding(dp(20),0,0,0);header.addView(title,new LinearLayout.LayoutParams(0,dp(42),1));
  summary=text("Seus downloads",13,0xff9bb5a5);header.addView(summary);page.addView(header);
  TextView hint=text("Se a conexão cair, o download aguarda e tenta novamente. Você pode pausar ou cancelar.",13,0xff9bb5a5);page.addView(hint,new LinearLayout.LayoutParams(-1,dp(32)));
  FrameLayout listArea=new FrameLayout(owner);ListView list=new ListView(owner);list.setDivider(null);list.setDividerHeight(dp(8));list.setAdapter(adapter);list.setCacheColorHint(Color.TRANSPARENT);
  TextView empty=text("Nenhum download nesta sessão.\nEscolha um jogo e toque em BAIXAR.",17,0xffabc3b4);empty.setGravity(Gravity.CENTER);listArea.addView(empty,new FrameLayout.LayoutParams(-1,-1));listArea.addView(list,new FrameLayout.LayoutParams(-1,-1));list.setEmptyView(empty);page.addView(listArea,new LinearLayout.LayoutParams(-1,0,1));
  TextView foot=text("Ao retomar uma transferência interrompida, o arquivo pode começar do início. Jogos já instalados são preservados.",11,0xff779583);page.addView(foot,new LinearLayout.LayoutParams(-1,dp(24)));
  setContentView(page);owner.getApplication().registerActivityLifecycleCallbacks(lifecycle);main.post(tick);
 }
 @Override public void dismiss(){if(!closed){closed=true;main.removeCallbacks(tick);for(Runnable retry:delayedCoverRetries)main.removeCallbacks(retry);delayedCoverRetries.clear();owner.getApplication().unregisterActivityLifecycleCallbacks(lifecycle);for(StationCoverQueue.Handle handle:coverHandles.values())handle.cancel();coverHandles.clear();loading.clear();images.evictAll();if(visible==this)visible=null;}super.dismiss();}
 private static String time(long ms){long s=Math.max(0,ms/1000);return s>=3600?String.format(Locale.ROOT,"%d:%02d:%02d",s/3600,s/60%60,s%60):String.format(Locale.ROOT,"%d:%02d",s/60,s%60);}
 private static String bytes(double n){return n>=1048576?String.format(Locale.ROOT,"%.1f MB",n/1048576):String.format(Locale.ROOT,"%.0f KB",n/1024);}
 private final class Row extends LinearLayout {
  ImageView cover;TextView name,status,details,pause,cancel;ProgressBar progress;
  Row(){super(owner);setGravity(Gravity.CENTER_VERTICAL);setPadding(dp(10),dp(9),dp(12),dp(9));setBackground(background(0xff142019,10));
   cover=new ImageView(owner);cover.setScaleType(ImageView.ScaleType.FIT_CENTER);cover.setBackground(background(0xff09100c,4));addView(cover,new LinearLayout.LayoutParams(dp(67),dp(89)));
   LinearLayout content=new LinearLayout(owner);content.setOrientation(1);content.setPadding(dp(15),0,dp(16),0);addView(content,new LinearLayout.LayoutParams(0,dp(88),1));
   name=text("",16,0xfff0fff5);name.setTypeface(null,Typeface.BOLD);name.setSingleLine();name.setEllipsize(android.text.TextUtils.TruncateAt.END);content.addView(name,new LinearLayout.LayoutParams(-1,dp(24)));
   status=text("",12,0xff68e897);content.addView(status,new LinearLayout.LayoutParams(-1,dp(23)));
   progress=new ProgressBar(owner,null,android.R.attr.progressBarStyleHorizontal);progress.setMax(1000);progress.setProgressTintList(android.content.res.ColorStateList.valueOf(0xff43dd83));content.addView(progress,new LinearLayout.LayoutParams(-1,dp(5)));
   details=text("",11,0xffa8c3b2);details.setMaxLines(2);content.addView(details,new LinearLayout.LayoutParams(-1,0,1));
   LinearLayout actions=new LinearLayout(owner);actions.setOrientation(LinearLayout.HORIZONTAL);actions.setGravity(Gravity.CENTER_VERTICAL);pause=button("PAUSAR",0xff235638);cancel=button("CANCELAR",0xff542a30);actions.addView(pause,new LinearLayout.LayoutParams(dp(104),dp(34)));LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(dp(104),dp(34));cp.leftMargin=dp(8);actions.addView(cancel,cp);addView(actions,new LinearLayout.LayoutParams(dp(216),-2));
  }
 }
 private final class Adapter extends BaseAdapter {
  public int getCount(){return rows.size();}public Object getItem(int p){return rows.get(p);}public long getItemId(int p){return p;}
  public View getView(int p,View old,android.view.ViewGroup parent){Row r=old instanceof Row?(Row)old:new Row();StationDownloads.Entry e=rows.get(p);
   r.name.setText(e.name);r.status.setText(e.message+" · "+e.platform);r.status.setTextColor(e.state==StationDownloads.State.ERROR?0xffff8793:0xff68e897);
   long done=e.state==StationDownloads.State.DOWNLOADING?e.networkDone:e.done,total=e.state==StationDownloads.State.DOWNLOADING?e.networkTotal:e.total;
   r.progress.setIndeterminate(total<=0&&(e.state==StationDownloads.State.AUTHORIZING||e.state==StationDownloads.State.PREPARING));r.progress.setProgress(total>0?(int)Math.min(1000,done*1000d/total):0);
   String speed=e.bytesPerSecond>0?bytes(e.bytesPerSecond)+"/s":"—";String remaining=e.bytesPerSecond>0&&e.networkTotal>e.networkDone?time((long)((e.networkTotal-e.networkDone)*1000d/e.bytesPerSecond)):"—";
   r.details.setText((total>0?bytes(done)+" / "+bytes(total)+"  ·  ":"")+"Velocidade "+speed+"  ·  Tempo "+time(e.elapsedMillis)+"  ·  Falta "+remaining);
   boolean retry=e.state==StationDownloads.State.PAUSED||e.state==StationDownloads.State.ERROR;
   r.pause.setText(e.state==StationDownloads.State.ERROR?"TENTAR DE NOVO":retry?"CONTINUAR":"PAUSAR");r.pause.setVisibility(e.state==StationDownloads.State.COMPLETE||e.state==StationDownloads.State.CANCELLED?View.GONE:View.VISIBLE);
   r.pause.setEnabled(e.state!=StationDownloads.State.PREPARING);r.pause.setAlpha(r.pause.isEnabled()?1f:.4f);r.pause.setOnClickListener(v->controls.execute(()->{if(retry)StationFrontend.resumeDownload(e.id);else StationFrontend.pauseDownload(e.id);}));
   r.cancel.setVisibility(e.state!=StationDownloads.State.COMPLETE?View.VISIBLE:View.GONE);r.cancel.setOnClickListener(v->new AlertDialog.Builder(owner).setTitle("Cancelar download?").setMessage(e.name).setNegativeButton("MANTER",null).setPositiveButton("CANCELAR",(d,w)->controls.execute(()->{StationFrontend.cancel(e.id);main.post(tick);})).show());
   String key=e.coverId+"-"+e.revision;r.cover.setImageBitmap(images.get(key));r.cover.setContentDescription("Capa de "+e.name);loadCover(e,key);return r;
  }
 }
 private void loadCover(StationDownloads.Entry e,String key){if(closed||images.get(key)!=null||!loading.add(key))return;
  StationCoverQueue.Handle handle=StationFrontend.coverWork(e.id,new StationCoverQueue.Work(){
   @Override public void process(Path file,StationApi.Cancellation cancel)throws Exception{
    byte[] bytes=StationFiles.readBounded(file,5*1024*1024);cancel.check();
    BitmapFactory.Options o=new BitmapFactory.Options();o.inJustDecodeBounds=true;BitmapFactory.decodeByteArray(bytes,0,bytes.length,o);
    if(o.outWidth<1||o.outHeight<1||o.outWidth>8192||o.outHeight>8192)throw new java.io.IOException("Invalid cover bounds");
    int max=Math.max(o.outWidth,o.outHeight);o.inSampleSize=1;while(max/o.inSampleSize>256)o.inSampleSize*=2;o.inJustDecodeBounds=false;
    Bitmap bitmap=BitmapFactory.decodeByteArray(bytes,0,bytes.length,o);if(bitmap==null)throw new java.io.IOException("Cover decode failed");
    boolean handedOff=false;try{cancel.check();deliverCover(key,bitmap);handedOff=true;}finally{if(!handedOff&&!bitmap.isRecycled())bitmap.recycle();}
   }
   @Override public void failed(int result,long retryMillis){deliverCover(key,null);}
  });
  coverHandles.put(key,handle);
 }
 private void deliverCover(String key,Bitmap result){main.post(()->{
  coverHandles.remove(key);
  if(closed){if(result!=null&&!result.isRecycled())result.recycle();return;}
  if(result!=null){images.put(key,result);loading.remove(key);adapter.notifyDataSetChanged();}
  else {Runnable retry=new Runnable(){@Override public void run(){delayedCoverRetries.remove(this);if(!closed)loading.remove(key);}};delayedCoverRetries.add(retry);main.postDelayed(retry,30000);}
 });}
}
