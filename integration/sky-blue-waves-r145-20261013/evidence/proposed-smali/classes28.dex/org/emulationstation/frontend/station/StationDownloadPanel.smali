.class public final Lorg/emulationstation/frontend/station/StationDownloadPanel;
.super Landroid/app/Dialog;
.source "StationDownloadPanel.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;,
        Lorg/emulationstation/frontend/station/StationDownloadPanel$Row;
    }
.end annotation


# static fields
.field private static final controls:Ljava/util/concurrent/ExecutorService;

.field private static visible:Lorg/emulationstation/frontend/station/StationDownloadPanel;


# instance fields
.field private final adapter:Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;

.field private closed:Z

.field private confirmation:Landroid/app/Dialog;

.field private final coverHandles:Ljava/util/Map;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Lorg/emulationstation/frontend/station/StationCoverQueue$Handle;",
            ">;"
        }
    .end annotation
.end field

.field private final delayedCoverRetries:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Ljava/lang/Runnable;",
            ">;"
        }
    .end annotation
.end field

.field private final images:Landroid/util/LruCache;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Landroid/util/LruCache<",
            "Ljava/lang/String;",
            "Landroid/graphics/Bitmap;",
            ">;"
        }
    .end annotation
.end field

.field private final lifecycle:Landroid/app/Application$ActivityLifecycleCallbacks;

.field private final loading:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private final main:Landroid/os/Handler;

.field private final owner:Landroid/app/Activity;

.field private rows:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Lorg/emulationstation/frontend/station/StationDownloads$Entry;",
            ">;"
        }
    .end annotation
.end field

.field private summary:Landroid/widget/TextView;

.field private final tick:Ljava/lang/Runnable;


# direct methods
.method public static synthetic $r8$lambda$p_wWDCiIDC4Idh-zYyGtbjqPx1M(Lorg/emulationstation/frontend/station/StationDownloadPanel;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->refreshRows()V

    return-void
.end method

.method static constructor <clinit>()V
    .locals 1

    .line 17
    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda6;

    invoke-direct {v0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda6;-><init>()V

    invoke-static {v0}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor(Ljava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    sput-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->controls:Ljava/util/concurrent/ExecutorService;

    return-void
.end method

.method private constructor <init>(Landroid/app/Activity;)V
    .locals 2

    .line 34
    const v0, 0x103022f

    invoke-direct {p0, p1, v0}, Landroid/app/Dialog;-><init>(Landroid/content/Context;I)V

    .line 18
    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    .line 19
    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$1;

    const/high16 v1, 0x800000

    invoke-direct {v0, p0, v1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$1;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;I)V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->images:Landroid/util/LruCache;

    .line 20
    new-instance v0, Ljava/util/HashSet;

    invoke-direct {v0}, Ljava/util/HashSet;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->loading:Ljava/util/Set;

    .line 21
    new-instance v0, Ljava/util/HashSet;

    invoke-direct {v0}, Ljava/util/HashSet;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->delayedCoverRetries:Ljava/util/Set;

    .line 22
    new-instance v0, Ljava/util/HashMap;

    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->coverHandles:Ljava/util/Map;

    .line 23
    invoke-static {}, Ljava/util/Collections;->emptyList()Ljava/util/List;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->rows:Ljava/util/List;

    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;

    const/4 v1, 0x0

    invoke-direct {v0, p0, v1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Lorg/emulationstation/frontend/station/StationDownloadPanel$1;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->adapter:Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;

    .line 27
    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$2;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$2;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->tick:Ljava/lang/Runnable;

    .line 28
    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$3;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$3;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->lifecycle:Landroid/app/Application$ActivityLifecycleCallbacks;

    .line 34
    iput-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    return-void
.end method

.method static synthetic access$100(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Z
    .locals 0

    .line 15
    iget-boolean p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    return p0
.end method

.method static synthetic access$1000(D)Ljava/lang/String;
    .locals 0

    .line 15
    invoke-static {p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->bytes(D)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$1100(J)Ljava/lang/String;
    .locals 0

    .line 15
    invoke-static {p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->time(J)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$1200(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Landroid/util/LruCache;
    .locals 0

    .line 15
    iget-object p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->images:Landroid/util/LruCache;

    return-object p0
.end method

.method static synthetic access$1300(Lorg/emulationstation/frontend/station/StationDownloadPanel;Lorg/emulationstation/frontend/station/StationDownloads$Entry;Ljava/lang/String;)V
    .locals 0

    .line 15
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->loadCover(Lorg/emulationstation/frontend/station/StationDownloads$Entry;Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$1400(Lorg/emulationstation/frontend/station/StationDownloadPanel;Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V
    .locals 0

    .line 15
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmCancel(Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V

    return-void
.end method

.method static synthetic access$1500()Ljava/util/concurrent/ExecutorService;
    .locals 1

    .line 15
    sget-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->controls:Ljava/util/concurrent/ExecutorService;

    return-object v0
.end method

.method static synthetic access$1600(Lorg/emulationstation/frontend/station/StationDownloadPanel;Ljava/lang/String;Landroid/graphics/Bitmap;)V
    .locals 0

    .line 15
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->deliverCover(Ljava/lang/String;Landroid/graphics/Bitmap;)V

    return-void
.end method

.method static synthetic access$1700(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Ljava/util/Set;
    .locals 0

    .line 15
    iget-object p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->delayedCoverRetries:Ljava/util/Set;

    return-object p0
.end method

.method static synthetic access$1800(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Ljava/util/Set;
    .locals 0

    .line 15
    iget-object p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->loading:Ljava/util/Set;

    return-object p0
.end method

.method static synthetic access$200(Lorg/emulationstation/frontend/station/StationDownloadPanel;)V
    .locals 0

    .line 15
    invoke-direct {p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->refreshRows()V

    return-void
.end method

.method static synthetic access$300(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Landroid/os/Handler;
    .locals 0

    .line 15
    iget-object p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    return-object p0
.end method

.method static synthetic access$400(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Landroid/app/Activity;
    .locals 0

    .line 15
    iget-object p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    return-object p0
.end method

.method static synthetic access$500(Lorg/emulationstation/frontend/station/StationDownloadPanel;F)I
    .locals 0

    .line 15
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result p0

    return p0
.end method

.method static synthetic access$600(Lorg/emulationstation/frontend/station/StationDownloadPanel;II)Landroid/graphics/drawable/GradientDrawable;
    .locals 0

    .line 15
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->background(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$700(Lorg/emulationstation/frontend/station/StationDownloadPanel;Ljava/lang/String;II)Landroid/widget/TextView;
    .locals 0

    .line 15
    invoke-direct {p0, p1, p2, p3}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->text(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$800(Lorg/emulationstation/frontend/station/StationDownloadPanel;Ljava/lang/String;Z)Landroid/widget/TextView;
    .locals 0

    .line 15
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->button(Ljava/lang/String;Z)Landroid/widget/TextView;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$900(Lorg/emulationstation/frontend/station/StationDownloadPanel;)Ljava/util/List;
    .locals 0

    .line 15
    iget-object p0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->rows:Ljava/util/List;

    return-object p0
.end method

.method private background(II)Landroid/graphics/drawable/GradientDrawable;
    .locals 1

    .line 36
    new-instance v0, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v0}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    int-to-float p1, p2

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result p1

    int-to-float p1, p1

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    return-object v0
.end method

.method private button(Ljava/lang/String;Z)Landroid/widget/TextView;
    .locals 1

    .line 38
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-static {v0, p1, p2}, Lorg/emulationstation/frontend/station/StationDownloadUi;->action(Landroid/app/Activity;Ljava/lang/String;Z)Landroid/widget/TextView;

    move-result-object p1

    return-object p1
.end method

.method private static bytes(D)Ljava/lang/String;
    .locals 3

    .line 54
    const-wide/high16 v0, 0x4130000000000000L    # 1048576.0

    cmpl-double v2, p0, v0

    if-ltz v2, :cond_0

    sget-object v2, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    div-double/2addr p0, v0

    invoke-static {p0, p1}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p0

    filled-new-array {p0}, [Ljava/lang/Object;

    move-result-object p0

    const-string p1, "%.1f MB"

    invoke-static {v2, p1, p0}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    goto :goto_0

    :cond_0
    sget-object v0, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    const-wide/high16 v1, 0x4090000000000000L    # 1024.0

    div-double/2addr p0, v1

    invoke-static {p0, p1}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p0

    filled-new-array {p0}, [Ljava/lang/Object;

    move-result-object p0

    const-string p1, "%.0f KB"

    invoke-static {v0, p1, p0}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    :goto_0
    return-object p0
.end method

.method private confirmCancel(Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V
    .locals 9

    .line 87
    iget-boolean v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->isDestroyed()Z

    move-result v0

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    if-eqz v0, :cond_0

    goto :goto_1

    .line 88
    :cond_0
    iget-object v1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    const-string v2, "Cancelar download?"

    iget-object v3, p1, Lorg/emulationstation/frontend/station/StationDownloads$Entry;->name:Ljava/lang/String;

    const-string v4, "A transfer\u00eancia ser\u00e1 removida da lista. Jogos e saves j\u00e1 instalados permanecem no telefone."

    const-string v5, "CANCELAR"

    new-instance v6, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda3;

    invoke-direct {v6, p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda3;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V

    const-string v7, "MANTER"

    const/4 v8, 0x0

    invoke-static/range {v1 .. v8}, Lorg/emulationstation/frontend/station/StationDownloadUi;->messageDialog(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/app/Dialog;

    move-result-object p1

    .line 89
    iput-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda4;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda4;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Landroid/app/Dialog;)V

    invoke-virtual {p1, v0}, Landroid/app/Dialog;->setOnDismissListener(Landroid/content/DialogInterface$OnDismissListener;)V

    .line 90
    :try_start_0
    invoke-virtual {p1}, Landroid/app/Dialog;->show()V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-static {v0, p1}, Lorg/emulationstation/frontend/station/StationDownloadUi;->sizeDialog(Landroid/app/Activity;Landroid/app/Dialog;)V
    :try_end_0
    .catch Landroid/view/WindowManager$BadTokenException; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception p1

    const/4 p1, 0x0

    iput-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    .line 91
    :goto_0
    return-void

    .line 87
    :cond_1
    :goto_1
    return-void
.end method

.method private deliverCover(Ljava/lang/String;Landroid/graphics/Bitmap;)V
    .locals 2

    .line 106
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    new-instance v1, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda5;

    invoke-direct {v1, p0, p1, p2}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda5;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Ljava/lang/String;Landroid/graphics/Bitmap;)V

    invoke-virtual {v0, v1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 111
    return-void
.end method

.method private dp(F)I
    .locals 1

    .line 35
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr p1, v0

    invoke-static {p1}, Ljava/lang/Math;->round(F)I

    move-result p1

    return p1
.end method

.method static isOpen()Z
    .locals 1

    .line 33
    sget-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->visible:Lorg/emulationstation/frontend/station/StationDownloadPanel;

    if-eqz v0, :cond_0

    iget-boolean v0, v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    if-nez v0, :cond_0

    const/4 v0, 0x1

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    :goto_0
    return v0
.end method

.method static synthetic lambda$open$1(Landroid/app/Activity;)V
    .locals 1

    .line 32
    invoke-virtual {p0}, Landroid/app/Activity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_1

    invoke-virtual {p0}, Landroid/app/Activity;->isDestroyed()Z

    move-result v0

    if-nez v0, :cond_1

    sget-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->visible:Lorg/emulationstation/frontend/station/StationDownloadPanel;

    if-eqz v0, :cond_0

    goto :goto_0

    :cond_0
    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;-><init>(Landroid/app/Activity;)V

    sput-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->visible:Lorg/emulationstation/frontend/station/StationDownloadPanel;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->show()V

    :cond_1
    :goto_0
    return-void
.end method

.method static synthetic lambda$static$0(Ljava/lang/Runnable;)Ljava/lang/Thread;
    .locals 2

    .line 17
    new-instance v0, Ljava/lang/Thread;

    const-string v1, "Station-download-control"

    invoke-direct {v0, p0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    const/4 p0, 0x1

    invoke-virtual {v0, p0}, Ljava/lang/Thread;->setDaemon(Z)V

    return-object v0
.end method

.method private loadCover(Lorg/emulationstation/frontend/station/StationDownloads$Entry;Ljava/lang/String;)V
    .locals 1

    .line 92
    iget-boolean v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->images:Landroid/util/LruCache;

    invoke-virtual {v0, p2}, Landroid/util/LruCache;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->loading:Ljava/util/Set;

    invoke-interface {v0, p2}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    goto :goto_0

    .line 93
    :cond_0
    iget-object p1, p1, Lorg/emulationstation/frontend/station/StationDownloads$Entry;->id:Ljava/lang/String;

    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$4;

    invoke-direct {v0, p0, p2}, Lorg/emulationstation/frontend/station/StationDownloadPanel$4;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Ljava/lang/String;)V

    invoke-static {p1, v0}, Lorg/emulationstation/frontend/station/StationFrontend;->coverWork(Ljava/lang/String;Lorg/emulationstation/frontend/station/StationCoverQueue$Work;)Lorg/emulationstation/frontend/station/StationCoverQueue$Handle;

    move-result-object p1

    .line 104
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->coverHandles:Ljava/util/Map;

    invoke-interface {v0, p2, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 105
    return-void

    .line 92
    :cond_1
    :goto_0
    return-void
.end method

.method public static open(Landroid/app/Activity;)Z
    .locals 1

    .line 32
    if-eqz p0, :cond_1

    invoke-virtual {p0}, Landroid/app/Activity;->isFinishing()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    :cond_0
    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda0;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda0;-><init>(Landroid/app/Activity;)V

    invoke-virtual {p0, v0}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    const/4 p0, 0x1

    return p0

    :cond_1
    :goto_0
    const/4 p0, 0x0

    return p0
.end method

.method private refreshRows()V
    .locals 3

    .line 25
    iget-boolean v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    if-eqz v0, :cond_0

    return-void

    :cond_0
    invoke-static {}, Lorg/emulationstation/frontend/station/StationFrontend;->downloadEntries()Ljava/util/List;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->rows:Ljava/util/List;

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->adapter:Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;->notifyDataSetChanged()V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->rows:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    const/4 v1, 0x0

    :cond_1
    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_2

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lorg/emulationstation/frontend/station/StationDownloads$Entry;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/station/StationDownloads$Entry;->active()Z

    move-result v2

    if-eqz v2, :cond_1

    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    .line 26
    :cond_2
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->summary:Landroid/widget/TextView;

    if-nez v1, :cond_3

    const-string v1, "Seus downloads"

    goto :goto_1

    :cond_3
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " em andamento"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    :goto_1
    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void
.end method

.method private text(Ljava/lang/String;II)Landroid/widget/TextView;
    .locals 2

    .line 37
    new-instance v0, Landroid/widget/TextView;

    iget-object v1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-direct {v0, v1}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    int-to-float p1, p2

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextSize(F)V

    invoke-virtual {v0, p3}, Landroid/widget/TextView;->setTextColor(I)V

    const/16 p1, 0x10

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setGravity(I)V

    return-object v0
.end method

.method private static time(J)Ljava/lang/String;
    .locals 7

    .line 53
    const-wide/16 v0, 0x3e8

    div-long/2addr p0, v0

    const-wide/16 v0, 0x0

    invoke-static {v0, v1, p0, p1}, Ljava/lang/Math;->max(JJ)J

    move-result-wide p0

    const-wide/16 v0, 0xe10

    cmp-long v2, p0, v0

    const-wide/16 v3, 0x3c

    if-ltz v2, :cond_0

    sget-object v2, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    div-long v0, p0, v0

    invoke-static {v0, v1}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v0

    div-long v5, p0, v3

    rem-long/2addr v5, v3

    invoke-static {v5, v6}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v1

    rem-long/2addr p0, v3

    invoke-static {p0, p1}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object p0

    filled-new-array {v0, v1, p0}, [Ljava/lang/Object;

    move-result-object p0

    const-string p1, "%d:%02d:%02d"

    invoke-static {v2, p1, p0}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    goto :goto_0

    :cond_0
    sget-object v0, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    div-long v1, p0, v3

    invoke-static {v1, v2}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v1

    rem-long/2addr p0, v3

    invoke-static {p0, p1}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object p0

    filled-new-array {v1, p0}, [Ljava/lang/Object;

    move-result-object p0

    const-string p1, "%d:%02d"

    invoke-static {v0, p1, p0}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    :goto_0
    return-object p0
.end method

.method static wideRows(F)Z
    .locals 1

    .line 55
    const/high16 v0, 0x44160000    # 600.0f

    cmpl-float p0, p0, v0

    if-ltz p0, :cond_0

    const/4 p0, 0x1

    goto :goto_0

    :cond_0
    const/4 p0, 0x0

    :goto_0
    return p0
.end method


# virtual methods
.method public dismiss()V
    .locals 4

    .line 52
    iget-boolean v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    if-nez v0, :cond_3

    const/4 v0, 0x1

    iput-boolean v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    iget-object v1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->tick:Ljava/lang/Runnable;

    invoke-virtual {v0, v1}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    const/4 v1, 0x0

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    iput-object v1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->delayedCoverRetries:Ljava/util/Set;

    invoke-interface {v0}, Ljava/util/Set;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_1

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/Runnable;

    iget-object v3, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    invoke-virtual {v3, v2}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V

    goto :goto_0

    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->delayedCoverRetries:Ljava/util/Set;

    invoke-interface {v0}, Ljava/util/Set;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->getApplication()Landroid/app/Application;

    move-result-object v0

    iget-object v2, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->lifecycle:Landroid/app/Application$ActivityLifecycleCallbacks;

    invoke-virtual {v0, v2}, Landroid/app/Application;->unregisterActivityLifecycleCallbacks(Landroid/app/Application$ActivityLifecycleCallbacks;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->coverHandles:Ljava/util/Map;

    invoke-interface {v0}, Ljava/util/Map;->values()Ljava/util/Collection;

    move-result-object v0

    invoke-interface {v0}, Ljava/util/Collection;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_1
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_2

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lorg/emulationstation/frontend/station/StationCoverQueue$Handle;

    invoke-interface {v2}, Lorg/emulationstation/frontend/station/StationCoverQueue$Handle;->cancel()V

    goto :goto_1

    :cond_2
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->coverHandles:Ljava/util/Map;

    invoke-interface {v0}, Ljava/util/Map;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->loading:Ljava/util/Set;

    invoke-interface {v0}, Ljava/util/Set;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->images:Landroid/util/LruCache;

    invoke-virtual {v0}, Landroid/util/LruCache;->evictAll()V

    sget-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->visible:Lorg/emulationstation/frontend/station/StationDownloadPanel;

    if-ne v0, p0, :cond_3

    sput-object v1, Lorg/emulationstation/frontend/station/StationDownloadPanel;->visible:Lorg/emulationstation/frontend/station/StationDownloadPanel;

    :cond_3
    invoke-super {p0}, Landroid/app/Dialog;->dismiss()V

    invoke-static {}, Lorg/emulationstation/frontend/station/StationDownloadUi;->resumeNotices()V

    return-void
.end method

.method synthetic lambda$confirmCancel$3$org-emulationstation-frontend-station-StationDownloadPanel(Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V
    .locals 1

    .line 88
    iget-object p1, p1, Lorg/emulationstation/frontend/station/StationDownloads$Entry;->id:Ljava/lang/String;

    invoke-static {p1}, Lorg/emulationstation/frontend/station/StationFrontend;->cancel(Ljava/lang/String;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    new-instance v0, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda1;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda1;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;)V

    invoke-virtual {p1, v0}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    return-void
.end method

.method synthetic lambda$confirmCancel$4$org-emulationstation-frontend-station-StationDownloadPanel(Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V
    .locals 2

    .line 88
    sget-object v0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->controls:Ljava/util/concurrent/ExecutorService;

    new-instance v1, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda2;

    invoke-direct {v1, p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda2;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Lorg/emulationstation/frontend/station/StationDownloads$Entry;)V

    invoke-interface {v0, v1}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    return-void
.end method

.method synthetic lambda$confirmCancel$5$org-emulationstation-frontend-station-StationDownloadPanel(Landroid/app/Dialog;Landroid/content/DialogInterface;)V
    .locals 0

    .line 89
    iget-object p2, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    if-ne p2, p1, :cond_0

    const/4 p1, 0x0

    iput-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->confirmation:Landroid/app/Dialog;

    :cond_0
    return-void
.end method

.method synthetic lambda$deliverCover$6$org-emulationstation-frontend-station-StationDownloadPanel(Ljava/lang/String;Landroid/graphics/Bitmap;)V
    .locals 2

    .line 107
    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->coverHandles:Ljava/util/Map;

    invoke-interface {v0, p1}, Ljava/util/Map;->remove(Ljava/lang/Object;)Ljava/lang/Object;

    .line 108
    iget-boolean v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->closed:Z

    if-eqz v0, :cond_1

    if-eqz p2, :cond_0

    invoke-virtual {p2}, Landroid/graphics/Bitmap;->isRecycled()Z

    move-result p1

    if-nez p1, :cond_0

    invoke-virtual {p2}, Landroid/graphics/Bitmap;->recycle()V

    :cond_0
    return-void

    .line 109
    :cond_1
    if-eqz p2, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->images:Landroid/util/LruCache;

    invoke-virtual {v0, p1, p2}, Landroid/util/LruCache;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    iget-object p2, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->loading:Ljava/util/Set;

    invoke-interface {p2, p1}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->adapter:Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;->notifyDataSetChanged()V

    goto :goto_0

    .line 110
    :cond_2
    new-instance p2, Lorg/emulationstation/frontend/station/StationDownloadPanel$5;

    invoke-direct {p2, p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel$5;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;Ljava/lang/String;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->delayedCoverRetries:Ljava/util/Set;

    invoke-interface {p1, p2}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    iget-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    const-wide/16 v0, 0x7530

    invoke-virtual {p1, p2, v0, v1}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 111
    :goto_0
    return-void
.end method

.method synthetic lambda$onCreate$2$org-emulationstation-frontend-station-StationDownloadPanel(Landroid/view/View;)V
    .locals 0

    .line 42
    invoke-virtual {p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dismiss()V

    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 12

    .line 39
    invoke-super {p0, p1}, Landroid/app/Dialog;->onCreate(Landroid/os/Bundle;)V

    invoke-virtual {p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->getWindow()Landroid/view/Window;

    move-result-object p1

    const/4 v0, -0x1

    invoke-virtual {p1, v0, v0}, Landroid/view/Window;->setLayout(II)V

    invoke-virtual {p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object p1

    const/16 v1, 0x1706

    invoke-virtual {p1, v1}, Landroid/view/View;->setSystemUiVisibility(I)V

    .line 40
    new-instance p1, Landroid/widget/LinearLayout;

    iget-object v1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-direct {p1, v1}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v1, 0x1

    invoke-virtual {p1, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/high16 v2, 0x41800000    # 16.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v3

    const/high16 v4, 0x41200000    # 10.0f

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v5

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v2

    const/high16 v6, 0x41000000    # 8.0f

    invoke-direct {p0, v6}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v7

    invoke-virtual {p1, v3, v5, v2, v7}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const v2, -0xd7814b

    invoke-virtual {p1, v2}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    .line 41
    new-instance v2, Landroid/widget/LinearLayout;

    iget-object v3, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-direct {v2, v3}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/16 v3, 0x10

    invoke-virtual {v2, v3}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 42
    const-string v3, "\u2039  VOLTAR"

    const/4 v5, 0x0

    invoke-direct {p0, v3, v5}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->button(Ljava/lang/String;Z)Landroid/widget/TextView;

    move-result-object v3

    new-instance v7, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda7;

    invoke-direct {v7, p0}, Lorg/emulationstation/frontend/station/StationDownloadPanel$$ExternalSyntheticLambda7;-><init>(Lorg/emulationstation/frontend/station/StationDownloadPanel;)V

    invoke-virtual {v3, v7}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    new-instance v7, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v8, 0x42400000    # 48.0f

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v8

    const/4 v9, -0x2

    invoke-direct {v7, v9, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v3, v7}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 43
    new-instance v3, Landroid/widget/LinearLayout;

    iget-object v7, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-direct {v3, v7}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    invoke-virtual {v3, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/high16 v7, 0x41600000    # 14.0f

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v7

    invoke-virtual {v3, v7, v5, v5, v5}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    new-instance v7, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v8, 0x3f800000    # 1.0f

    invoke-direct {v7, v5, v9, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v2, v3, v7}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 44
    const/16 v7, 0x12

    const v10, -0xf0401

    const-string v11, "DOWNLOADS"

    invoke-direct {p0, v11, v7, v10}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->text(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v7

    const/4 v10, 0x0

    invoke-virtual {v7, v10, v1}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v1, v0, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v3, v7, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 45
    const v1, -0x793626

    const-string v7, "Seus downloads"

    const/16 v11, 0xd

    invoke-direct {p0, v7, v11, v1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->text(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->summary:Landroid/widget/TextView;

    new-instance v7, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v7, v0, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v3, v1, v7}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-virtual {p1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 46
    const-string v1, "Sem internet, a transfer\u00eancia aguarda a conex\u00e3o. Voc\u00ea pode pausar ou cancelar."

    const v2, -0x624734

    invoke-direct {p0, v1, v11, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->text(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    const/high16 v2, 0x40800000    # 4.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v3

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v4

    invoke-virtual {v1, v5, v3, v5, v4}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v0, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v1, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 47
    new-instance v1, Landroid/widget/FrameLayout;

    iget-object v3, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-direct {v1, v3}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    new-instance v3, Landroid/widget/ListView;

    iget-object v4, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-direct {v3, v4}, Landroid/widget/ListView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v3, v10}, Landroid/widget/ListView;->setDivider(Landroid/graphics/drawable/Drawable;)V

    invoke-direct {p0, v6}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v4

    invoke-virtual {v3, v4}, Landroid/widget/ListView;->setDividerHeight(I)V

    iget-object v4, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->adapter:Lorg/emulationstation/frontend/station/StationDownloadPanel$Adapter;

    invoke-virtual {v3, v4}, Landroid/widget/ListView;->setAdapter(Landroid/widget/ListAdapter;)V

    invoke-virtual {v3, v5}, Landroid/widget/ListView;->setCacheColorHint(I)V

    invoke-virtual {v3, v5}, Landroid/widget/ListView;->setClipToPadding(Z)V

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v2

    invoke-virtual {v3, v5, v5, v5, v2}, Landroid/widget/ListView;->setPadding(IIII)V

    .line 48
    const/16 v2, 0xe

    const v4, -0x583f30

    const-string v6, "Seus downloads aparecem aqui.\nSelecione um jogo e toque em BAIXAR."

    invoke-direct {p0, v6, v2, v4}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->text(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    const/16 v4, 0x11

    invoke-virtual {v2, v4}, Landroid/widget/TextView;->setGravity(I)V

    new-instance v4, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v4, v0, v0}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v2, v4}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance v4, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v4, v0, v0}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v3, v4}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-virtual {v3, v2}, Landroid/widget/ListView;->setEmptyView(Landroid/view/View;)V

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v2, v0, v5, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {p1, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 49
    const/16 v1, 0xc

    const v2, -0x7d614b

    const-string v3, "A retomada pode reiniciar o arquivo. Jogos instalados e saves s\u00e3o preservados."

    invoke-direct {p0, v3, v1, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->text(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    const/high16 v2, 0x40a00000    # 5.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->dp(F)I

    move-result v2

    invoke-virtual {v1, v5, v2, v5, v5}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v2, v0, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 50
    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/station/StationDownloadPanel;->setContentView(Landroid/view/View;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->owner:Landroid/app/Activity;

    invoke-virtual {p1}, Landroid/app/Activity;->getApplication()Landroid/app/Application;

    move-result-object p1

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->lifecycle:Landroid/app/Application$ActivityLifecycleCallbacks;

    invoke-virtual {p1, v0}, Landroid/app/Application;->registerActivityLifecycleCallbacks(Landroid/app/Application$ActivityLifecycleCallbacks;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->main:Landroid/os/Handler;

    iget-object v0, p0, Lorg/emulationstation/frontend/station/StationDownloadPanel;->tick:Ljava/lang/Runnable;

    invoke-virtual {p1, v0}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 51
    return-void
.end method
