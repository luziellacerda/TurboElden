.class public final Lorg/emulationstation/frontend/sony/Ps4Activity;
.super Landroid/app/Activity;
.source "Ps4Activity.java"

# interfaces
.implements Landroid/view/TextureView$SurfaceTextureListener;
.implements Landroid/hardware/input/InputManager$InputDeviceListener;


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/emulationstation/frontend/sony/Ps4Activity$ApplicationName;,
        Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;
    }
.end annotation


# static fields
.field private static final SETTINGS:[Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;


# instance fields
.field private volatile audio:Lorg/emulationstation/frontend/sony/Ps4Audio;

.field private final completed:Ljava/util/concurrent/atomic/AtomicBoolean;

.field private volatile control:Lorg/emulationstation/frontend/sony/Ps4Control;

.field private display:Landroid/view/TextureView;

.field private volatile entry:Ljava/lang/Class;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/lang/Class<",
            "*>;"
        }
    .end annotation
.end field

.field private input:Landroid/hardware/input/InputManager;

.field private lastProgress:J

.field private layout:Landroid/widget/FrameLayout;

.field private notice:Landroid/widget/LinearLayout;

.field private volatile phase:Ljava/lang/String;

.field private requested:Landroid/net/Uri;

.field private retainedTexture:Landroid/graphics/SurfaceTexture;

.field private volatile running:Z

.field private session:Ljava/io/File;

.field private settingsBody:Landroid/widget/LinearLayout;

.field private settingsCategory:I

.field private settingsConfig:Ljava/io/File;

.field private settingsEpoch:I

.field private settingsLeaving:Z

.field private settingsMessage:Landroid/widget/TextView;

.field private settingsMode:Z

.field private settingsSaving:Z

.field private final started:Ljava/util/concurrent/atomic/AtomicBoolean;

.field private status:Landroid/widget/TextView;

.field private final stopper:Ljava/util/concurrent/ExecutorService;

.field private final stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

.field private volatile surface:Landroid/view/Surface;

.field private final surfaceLock:Ljava/lang/Object;

.field private title:Landroid/widget/TextView;

.field private touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

.field private final worker:Ljava/util/concurrent/ExecutorService;


# direct methods
.method public static synthetic $r8$lambda$GRToAzFSuTxmrCN52LRA8-tSMiw(Lorg/emulationstation/frontend/sony/Ps4Activity;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->updatePhysical()V

    return-void
.end method

.method public static synthetic $r8$lambda$NpylQbYJ804etUSAqMUtSXfk_bw(Lorg/emulationstation/frontend/sony/Ps4Activity;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->showSettings()V

    return-void
.end method

.method public static synthetic $r8$lambda$XQdZXAcaPh4XCctBdR3bDXTEiA8(Lorg/emulationstation/frontend/sony/Ps4Activity;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finishOwner()V

    return-void
.end method

.method public static synthetic $r8$lambda$c4JHNzf8Jp5HCOCYHrGVNgDhvYE(Lorg/emulationstation/frontend/sony/Ps4Activity;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->prepareAndRun()V

    return-void
.end method

.method public static synthetic $r8$lambda$fOgwjlBFLmWMzXIxg8Rk-LdxbTQ(Lorg/emulationstation/frontend/sony/Ps4Activity;Ljava/lang/String;)V
    .locals 0

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->nativeEvent(Ljava/lang/String;)V

    return-void
.end method

.method static constructor <clinit>()V
    .locals 18

    const/16 v0, 0xb

    .line 301
    new-array v0, v0, [Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    new-instance v9, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    const-string v1, "Stretch"

    const-string v2, "Crop"

    const-string v3, "Fit"

    filled-new-array {v3, v1, v2}, [Ljava/lang/String;

    move-result-object v8

    const/4 v2, 0x0

    const/4 v3, 0x2

    const-string v4, "GPU"

    const-string v5, "display_mode"

    const-string v6, "Enquadramento"

    const-string v7, "Fit"

    move-object v1, v9

    invoke-direct/range {v1 .. v8}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v1, 0x0

    aput-object v9, v0, v1

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    sget-object v16, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;

    new-array v3, v1, [Ljava/lang/String;

    const/4 v11, 0x0

    const/4 v12, 0x1

    const-string v13, "GPU"

    const-string v14, "present_rb_swap"

    const-string v15, "Corrigir canais de cor"

    move-object v10, v2

    move-object/from16 v17, v3

    invoke-direct/range {v10 .. v17}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v3, 0x1

    aput-object v2, v0, v3

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    sget-object v10, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;

    new-array v11, v1, [Ljava/lang/String;

    const/4 v5, 0x0

    const/4 v6, 0x1

    const-string v7, "GPU"

    const-string v8, "hdr_allowed"

    const-string v9, "Permitir HDR"

    move-object v4, v2

    invoke-direct/range {v4 .. v11}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v4, 0x2

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    sget-object v11, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;

    new-array v12, v1, [Ljava/lang/String;

    const/4 v6, 0x0

    const/4 v7, 0x1

    const-string v8, "GPU"

    const-string v9, "fsr_enabled"

    const-string v10, "Filtro FSR"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v4, 0x3

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    sget-object v11, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;

    new-array v12, v1, [Ljava/lang/String;

    const-string v8, "GPU"

    const-string v9, "rcas_enabled"

    const-string v10, "Nitidez RCAS"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v4, 0x4

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    const-string v4, "Fifo"

    const-string v5, "FifoRelaxed"

    const-string v6, "Immediate"

    const-string v7, "Mailbox"

    filled-new-array {v6, v7, v4, v5}, [Ljava/lang/String;

    move-result-object v12

    const/4 v6, 0x0

    const/4 v7, 0x2

    const-string v8, "GPU"

    const-string v9, "present_mode"

    const-string v10, "Apresenta\u00e7\u00e3o dos quadros"

    const-string v11, "Mailbox"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v4, 0x5

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    sget-object v11, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;

    new-array v12, v1, [Ljava/lang/String;

    const/4 v6, 0x1

    const/4 v7, 0x1

    const-string v8, "General"

    const-string v9, "big_core_affinity"

    const-string v10, "Priorizar n\u00facleos de alto desempenho"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v4, 0x6

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    sget-object v11, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;

    new-array v12, v1, [Ljava/lang/String;

    const-string v8, "Vulkan"

    const-string v9, "pipeline_cache_enabled"

    const-string v10, "Cache de pipelines"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/4 v4, 0x7

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    const/16 v4, 0x3c

    .line 310
    invoke-static {v4}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v11

    new-array v12, v1, [Ljava/lang/String;

    const/4 v7, 0x0

    const-string v8, "GPU"

    const-string v9, "vblank_frequency"

    const-string v10, "Frequ\u00eancia VBlank"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/16 v4, 0x8

    aput-object v2, v0, v4

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    .line 311
    invoke-static {v3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v11

    new-array v12, v1, [Ljava/lang/String;

    const/4 v6, 0x2

    const-string v8, "General"

    const-string v9, "console_language"

    const-string v10, "Idioma do sistema"

    move-object v5, v2

    invoke-direct/range {v5 .. v12}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/16 v3, 0x9

    aput-object v2, v0, v3

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    const/4 v10, 0x0

    new-array v11, v1, [Ljava/lang/String;

    const/4 v5, 0x3

    const/4 v6, 0x0

    const-string v7, "Audio"

    const-string v8, "audio_backend"

    const-string v9, "Backend de \u00e1udio"

    move-object v4, v2

    invoke-direct/range {v4 .. v11}, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;[Ljava/lang/String;)V

    const/16 v1, 0xa

    aput-object v2, v0, v1

    sput-object v0, Lorg/emulationstation/frontend/sony/Ps4Activity;->SETTINGS:[Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    return-void
.end method

.method public constructor <init>()V
    .locals 1

    .line 28
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    .line 29
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda28;

    invoke-direct {v0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda28;-><init>()V

    invoke-static {v0}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor(Ljava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    .line 30
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda29;

    invoke-direct {v0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda29;-><init>()V

    invoke-static {v0}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor(Ljava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopper:Ljava/util/concurrent/ExecutorService;

    .line 31
    new-instance v0, Ljava/lang/Object;

    invoke-direct {v0}, Ljava/lang/Object;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    .line 32
    new-instance v0, Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-direct {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    new-instance v0, Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-direct {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->started:Ljava/util/concurrent/atomic/AtomicBoolean;

    new-instance v0, Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-direct {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    .line 40
    const-string v0, "prepare"

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->phase:Ljava/lang/String;

    return-void
.end method

.method static synthetic access$000(Lorg/emulationstation/frontend/sony/Ps4Activity;)Lorg/emulationstation/frontend/sony/Ps4Control;
    .locals 0

    .line 28
    iget-object p0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    return-object p0
.end method

.method private addSetting(Lorg/json/JSONObject;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;)V
    .locals 6

    .line 346
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->currentSetting(Lorg/json/JSONObject;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;)Ljava/lang/Object;

    move-result-object v0

    .line 347
    iget-object v1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->section:Ljava/lang/String;

    invoke-virtual {p1, v1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const/4 v2, 0x0

    const/4 v3, 0x1

    if-eqz v1, :cond_0

    iget-object v1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->section:Ljava/lang/String;

    invoke-virtual {p1, v1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p1

    iget-object v1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->key:Ljava/lang/String;

    invoke-virtual {p1, v1}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result p1

    if-eqz p1, :cond_0

    move p1, v3

    goto :goto_0

    :cond_0
    move p1, v2

    :goto_0
    if-eqz v0, :cond_4

    .line 348
    sget-object v1, Lorg/json/JSONObject;->NULL:Ljava/lang/Object;

    if-ne v0, v1, :cond_1

    goto :goto_1

    :cond_1
    instance-of v1, v0, Ljava/lang/Boolean;

    if-eqz v1, :cond_3

    move-object v1, v0

    check-cast v1, Ljava/lang/Boolean;

    invoke-virtual {v1}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v1

    if-eqz v1, :cond_2

    const-string v1, "Ativado"

    goto :goto_2

    :cond_2
    const-string v1, "Desativado"

    goto :goto_2

    :cond_3
    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    goto :goto_2

    :cond_4
    :goto_1
    const-string v1, "Padr\u00e3o do motor"

    :goto_2
    if-nez p1, :cond_5

    if-eqz v0, :cond_5

    .line 349
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p1, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, " \u00b7 padr\u00e3o"

    invoke-virtual {p1, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 350
    :cond_5
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v4, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->label:Ljava/lang/String;

    invoke-virtual {p1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v4, "   \u00b7   "

    invoke-virtual {p1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsButton(Ljava/lang/String;)Landroid/widget/Button;

    move-result-object p1

    invoke-virtual {p1, v3}, Landroid/widget/Button;->setSingleLine(Z)V

    .line 351
    sget-object v1, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {p1, v1}, Landroid/widget/Button;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    const/16 v1, 0x13

    invoke-virtual {p1, v1}, Landroid/widget/Button;->setGravity(I)V

    .line 352
    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v4, 0x28

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v4

    const/4 v5, -0x1

    invoke-direct {v1, v5, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    const/4 v4, 0x5

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v4

    iput v4, v1, Landroid/widget/LinearLayout$LayoutParams;->bottomMargin:I

    iget-object v4, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    invoke-virtual {v4, p1, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 353
    iget v1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->kind:I

    if-eqz v1, :cond_8

    sget-object v1, Lorg/json/JSONObject;->NULL:Ljava/lang/Object;

    if-eq v0, v1, :cond_8

    iget v1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->kind:I

    if-ne v1, v3, :cond_6

    instance-of v1, v0, Ljava/lang/Boolean;

    if-eqz v1, :cond_8

    :cond_6
    iget v1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->kind:I

    const/4 v3, 0x2

    if-ne v1, v3, :cond_7

    instance-of v1, v0, Ljava/lang/String;

    if-nez v1, :cond_7

    goto :goto_3

    .line 356
    :cond_7
    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda27;

    invoke-direct {v1, p0, p2, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda27;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;)V

    invoke-virtual {p1, v1}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-void

    .line 354
    :cond_8
    :goto_3
    invoke-virtual {p1, v2}, Landroid/widget/Button;->setEnabled(Z)V

    const p2, 0x3f3851ec    # 0.72f

    invoke-virtual {p1, p2}, Landroid/widget/Button;->setAlpha(F)V

    return-void
.end method

.method private addTouchSetting()V
    .locals 5

    const/4 v0, 0x0

    .line 391
    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "touch"

    const/4 v2, 0x1

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 392
    const-string v1, "Ativados"

    goto :goto_0

    :cond_0
    const-string v1, "Desativados"

    :goto_0
    const-string v2, "Controles de toque   \u00b7   "

    invoke-virtual {v2, v1}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsButton(Ljava/lang/String;)Landroid/widget/Button;

    move-result-object v1

    const/16 v2, 0x13

    .line 393
    invoke-virtual {v1, v2}, Landroid/widget/Button;->setGravity(I)V

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda12;

    invoke-direct {v2, p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda12;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Z)V

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 396
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v3, 0x28

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v3

    const/4 v4, -0x1

    invoke-direct {v2, v4, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-void
.end method

.method private buildNotice()V
    .locals 6

    .line 83
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    const/16 v2, 0x1c

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v3

    const/16 v4, 0x16

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v5

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v2

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v4

    invoke-virtual {v0, v3, v5, v2, v4}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 84
    new-instance v0, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v0}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    const v2, -0x11f1e9dd

    invoke-virtual {v0, v2}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    const/16 v2, 0x12

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v2

    int-to-float v2, v2

    invoke-virtual {v0, v2}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    invoke-virtual {v2, v0}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 85
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->title:Landroid/widget/TextView;

    const-string v2, "PlayStation 4"

    invoke-virtual {v0, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->title:Landroid/widget/TextView;

    const/4 v2, -0x1

    invoke-virtual {v0, v2}, Landroid/widget/TextView;->setTextColor(I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->title:Landroid/widget/TextView;

    sget-object v2, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v0, v2, v1}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->title:Landroid/widget/TextView;

    const/high16 v1, 0x41b80000    # 23.0f

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTextSize(F)V

    .line 86
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->status:Landroid/widget/TextView;

    const-string v1, "Preparando o motor\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->status:Landroid/widget/TextView;

    const v1, -0x493621

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTextColor(I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->status:Landroid/widget/TextView;

    const/high16 v1, 0x41700000    # 15.0f

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTextSize(F)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->status:Landroid/widget/TextView;

    const/16 v1, 0xc

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v1

    const/4 v2, 0x0

    invoke-virtual {v0, v2, v1, v2, v2}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 87
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->title:Landroid/widget/TextView;

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->status:Landroid/widget/TextView;

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 88
    new-instance v0, Landroid/widget/FrameLayout$LayoutParams;

    const/16 v1, 0x190

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v1

    const/4 v2, -0x2

    const/16 v3, 0x11

    invoke-direct {v0, v1, v2, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    invoke-virtual {v1, v2, v0}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-void
.end method

.method private checkStopped()V
    .locals 2
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/InterruptedException;
        }
    .end annotation

    .line 174
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    :cond_0
    new-instance v0, Ljava/lang/InterruptedException;

    const-string v1, "Owner stopped"

    invoke-direct {v0, v1}, Ljava/lang/InterruptedException;-><init>(Ljava/lang/String;)V

    throw v0
.end method

.method private closeSession()V
    .locals 2

    .line 199
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    const/4 v1, 0x0

    iput-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    if-eqz v0, :cond_0

    :try_start_0
    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Control;->close()V
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    .line 200
    :catch_0
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->audio:Lorg/emulationstation/frontend/sony/Ps4Audio;

    iput-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->audio:Lorg/emulationstation/frontend/sony/Ps4Audio;

    if-eqz v0, :cond_1

    :try_start_1
    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Audio;->close()V
    :try_end_1
    .catch Ljava/io/IOException; {:try_start_1 .. :try_end_1} :catch_1

    .line 201
    :catch_1
    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->session:Ljava/io/File;

    if-eqz v0, :cond_2

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    .line 202
    :cond_2
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda24;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda24;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method private confirmExit()V
    .locals 3

    .line 178
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMode:Z

    if-eqz v0, :cond_1

    .line 179
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-eqz v0, :cond_0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->leaveSettings()V

    goto :goto_0

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopOwner()V

    :goto_0
    return-void

    .line 182
    :cond_1
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    if-nez v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-eqz v0, :cond_2

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finishOwner()V

    return-void

    .line 183
    :cond_2
    new-instance v0, Landroid/app/AlertDialog$Builder;

    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string v1, "Sair do PS4?"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "Encerrar esta partida e voltar \u00e0 lista de jogos?"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "Continuar"

    const/4 v2, 0x0

    .line 184
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda4;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda4;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    const-string v2, "Sair"

    invoke-virtual {v0, v2, v1}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    return-void
.end method

.method private currentSetting(Lorg/json/JSONObject;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;)Ljava/lang/Object;
    .locals 1

    .line 325
    iget-object v0, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->section:Ljava/lang/String;

    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_0

    .line 326
    iget-object v0, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->key:Ljava/lang/String;

    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object p2, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->key:Ljava/lang/String;

    invoke-virtual {p1, p2}, Lorg/json/JSONObject;->opt(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p1

    return-object p1

    .line 327
    :cond_0
    iget-object p1, p2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->documentedDefault:Ljava/lang/Object;

    return-object p1
.end method

.method private static directory(Ljava/io/File;)Ljava/io/File;
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 175
    invoke-virtual {p0}, Ljava/io/File;->isDirectory()Z

    move-result v0

    if-nez v0, :cond_1

    invoke-virtual {p0}, Ljava/io/File;->mkdirs()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    :cond_0
    new-instance p0, Ljava/io/IOException;

    const-string v0, "Sem espa\u00e7o para preparar PS4"

    invoke-direct {p0, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_1
    :goto_0
    invoke-virtual {p0}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object p0

    return-object p0
.end method

.method private dp(I)I
    .locals 1

    int-to-float p1, p1

    .line 176
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr p1, v0

    invoke-static {p1}, Ljava/lang/Math;->round(F)I

    move-result p1

    return p1
.end method

.method private finishOwner()V
    .locals 1

    .line 211
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda13;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda13;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method static synthetic lambda$new$0(Ljava/lang/Runnable;)Ljava/lang/Thread;
    .locals 2

    .line 29
    new-instance v0, Ljava/lang/Thread;

    const-string v1, "StationPS4-Owner"

    invoke-direct {v0, p0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    return-object v0
.end method

.method static synthetic lambda$new$1(Ljava/lang/Runnable;)Ljava/lang/Thread;
    .locals 2

    .line 30
    new-instance v0, Ljava/lang/Thread;

    const-string v1, "StationPS4-Stop"

    invoke-direct {v0, p0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    return-object v0
.end method

.method static synthetic lambda$prepareAndRun$6(I)V
    .locals 0

    return-void
.end method

.method private leaveSettings()V
    .locals 2

    .line 402
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    :cond_0
    const/4 v0, 0x1

    .line 403
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsLeaving:Z

    iget v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    add-int/2addr v1, v0

    iput v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    .line 405
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda23;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda23;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-interface {v0, v1}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    return-void
.end method

.method private nativeEvent(Ljava/lang/String;)V
    .locals 2

    .line 166
    const-string v0, "BACHATA/1 EVENT Frame"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    const-string v1, "BACHATA/1 EVENT Running"

    if-nez v0, :cond_1

    invoke-virtual {v1, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    .line 168
    :cond_0
    const-string v0, "BACHATA/1 ERROR code="

    invoke-virtual {p1, v0}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result p1

    if-eqz p1, :cond_2

    const-string p1, "O motor PS4 informou uma falha de execu\u00e7\u00e3o."

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->warning(Ljava/lang/String;)V

    goto :goto_1

    .line 167
    :cond_1
    :goto_0
    invoke-virtual {v1, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_2

    new-instance p1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda22;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda22;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    :cond_2
    :goto_1
    return-void
.end method

.method private prepareAndRun()V
    .locals 17

    move-object/from16 v1, p0

    const/4 v2, 0x0

    const/4 v3, 0x1

    .line 92
    :try_start_0
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v4, 0x1f

    if-lt v0, v4, :cond_8

    .line 93
    const-string v0, "ps4"

    const-string v4, "4b23febf422c09ecf363dc4e8b56a832ddb89512f41e7230f24f9cb5a5322b3e"

    new-instance v5, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda15;

    invoke-direct {v5, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda15;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-static {v1, v0, v4, v5}, Lorg/emulationstation/frontend/sony/StationSonyAssets;->prepare(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/sony/StationSonyAssets$Progress;)Lorg/emulationstation/frontend/sony/StationSonyAssets$Prepared;

    move-result-object v0

    .line 95
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->checkStopped()V

    .line 96
    new-instance v4, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getFilesDir()Ljava/io/File;

    move-result-object v5

    const-string v6, "ps4"

    invoke-direct {v4, v5, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v4

    .line 97
    new-instance v5, Ljava/io/File;

    const-string v6, "native-runtime"

    invoke-direct {v5, v4, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v5}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v5

    new-instance v6, Ljava/io/File;

    const-string v7, "storage"

    invoke-direct {v6, v4, v7}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v6}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v6

    .line 98
    new-instance v7, Ljava/io/File;

    const-string v8, "xdg"

    invoke-direct {v7, v6, v8}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    new-instance v7, Ljava/io/File;

    const-string v8, "shader-cache/mesa"

    invoke-direct {v7, v6, v8}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    .line 99
    new-instance v7, Ljava/io/File;

    const-string v8, ".local/share"

    invoke-direct {v7, v6, v8}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v7

    .line 100
    new-instance v8, Ljava/io/File;

    new-instance v9, Ljava/io/File;

    const-string v10, "shadPS4"

    invoke-direct {v9, v7, v10}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    const-string v10, "config.json"

    invoke-direct {v8, v9, v10}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    iput-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    .line 103
    const-string v8, "HOME"

    invoke-virtual {v6}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v9

    invoke-static {v8, v9, v3}, Landroid/system/Os;->setenv(Ljava/lang/String;Ljava/lang/String;Z)V

    .line 104
    const-string v8, "XDG_DATA_HOME"

    invoke-virtual {v7}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v7

    invoke-static {v8, v7, v3}, Landroid/system/Os;->setenv(Ljava/lang/String;Ljava/lang/String;Z)V

    .line 105
    const-string v7, "derived/owner.dex"

    invoke-virtual {v0, v7}, Lorg/emulationstation/frontend/sony/StationSonyAssets$Prepared;->assetFile(Ljava/lang/String;)Ljava/io/File;

    move-result-object v7

    .line 106
    invoke-virtual {v7}, Ljava/io/File;->setReadOnly()Z

    move-result v8

    if-eqz v8, :cond_7

    .line 107
    new-instance v8, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getCodeCacheDir()Ljava/io/File;

    move-result-object v9

    const-string v10, "ps4-owner"

    invoke-direct {v8, v9, v10}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v8}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v8

    .line 108
    new-instance v9, Lorg/emulationstation/frontend/sony/Ps4ClassLoader;

    invoke-virtual {v7}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v7

    invoke-virtual {v8}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v8

    .line 109
    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/StationSonyAssets$Prepared;->nativeDirectory()Ljava/io/File;

    move-result-object v10

    invoke-virtual {v10}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v10

    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getClassLoader()Ljava/lang/ClassLoader;

    move-result-object v11

    invoke-direct {v9, v7, v8, v10, v11}, Lorg/emulationstation/frontend/sony/Ps4ClassLoader;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)V

    .line 110
    const-string v7, "org.emulationstation.ps4child.Ps4NativeEntry"

    invoke-virtual {v9, v7}, Lorg/emulationstation/frontend/sony/Ps4ClassLoader;->loadClass(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v7

    .line 111
    new-instance v8, Ljava/util/LinkedHashSet;

    invoke-direct {v8}, Ljava/util/LinkedHashSet;-><init>()V

    .line 112
    const-string v9, "libbachata_native_runtime.so"

    const-string v10, "libbachata_pkg.so"

    filled-new-array {v9, v10}, [Ljava/lang/String;

    move-result-object v9

    move v10, v2

    :goto_0
    const/4 v11, 0x2

    if-ge v10, v11, :cond_1

    aget-object v11, v9, v10

    .line 113
    invoke-static {v0, v11}, Lorg/emulationstation/frontend/sony/StationSonyAssets;->nativeLoadPlan(Lorg/emulationstation/frontend/sony/StationSonyAssets$Prepared;Ljava/lang/String;)[Ljava/io/File;

    move-result-object v11

    array-length v12, v11

    move v13, v2

    :goto_1
    if-ge v13, v12, :cond_0

    aget-object v14, v11, v13

    invoke-virtual {v14}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v8, v14}, Ljava/util/LinkedHashSet;->add(Ljava/lang/Object;)Z

    add-int/lit8 v13, v13, 0x1

    goto :goto_1

    :cond_0
    add-int/lit8 v10, v10, 0x1

    goto :goto_0

    .line 114
    :cond_1
    const-string v9, "loadNative"

    const-class v10, [Ljava/lang/String;

    const-class v11, Ljava/lang/String;

    filled-new-array {v10, v11}, [Ljava/lang/Class;

    move-result-object v10

    new-array v11, v2, [Ljava/lang/String;

    .line 115
    invoke-virtual {v8, v11}, Ljava/util/LinkedHashSet;->toArray([Ljava/lang/Object;)[Ljava/lang/Object;

    move-result-object v8

    const-string v11, "derived/pkg-rsa.bin"

    invoke-virtual {v0, v11}, Lorg/emulationstation/frontend/sony/StationSonyAssets$Prepared;->assetFile(Ljava/lang/String;)Ljava/io/File;

    move-result-object v11

    invoke-virtual {v11}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v11

    filled-new-array {v8, v11}, [Ljava/lang/Object;

    move-result-object v8

    .line 114
    invoke-static {v7, v9, v10, v8}, Lorg/emulationstation/frontend/sony/Ps4Game;->invoke(Ljava/lang/Class;Ljava/lang/String;[Ljava/lang/Class;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 118
    iput-object v7, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->entry:Ljava/lang/Class;

    .line 119
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->checkStopped()V

    .line 120
    new-instance v7, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getNoBackupFilesDir()Ljava/io/File;

    move-result-object v8

    const-string v9, "ps4-runtime"

    invoke-direct {v7, v8, v9}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v7

    invoke-static {v0, v7}, Lorg/emulationstation/frontend/sony/Ps4Runtime;->prepare(Lorg/emulationstation/frontend/sony/StationSonyAssets$Prepared;Ljava/io/File;)Ljava/io/File;

    .line 121
    iget-boolean v0, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMode:Z

    if-eqz v0, :cond_2

    .line 122
    const-string v0, "settings"

    iput-object v0, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->phase:Ljava/lang/String;

    iget-object v0, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0, v3}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    .line 123
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda16;

    invoke-direct {v0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda16;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {v1, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/InterruptedException; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    .line 159
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->closeSession()V

    return-void

    .line 125
    :cond_2
    :try_start_1
    const-string v0, "import"

    iput-object v0, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->phase:Ljava/lang/String;

    const-string v0, "PlayStation 4"

    const-string v7, "Preparando o jogo\u2026"

    invoke-direct {v1, v0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->show(Ljava/lang/String;Ljava/lang/String;)V

    .line 126
    iget-object v0, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->requested:Landroid/net/Uri;

    new-instance v7, Ljava/io/File;

    const-string v8, "games"

    invoke-direct {v7, v4, v8}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v4

    iget-object v7, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->entry:Ljava/lang/Class;

    new-instance v8, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda17;

    invoke-direct {v8, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda17;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-static {v1, v0, v4, v7, v8}, Lorg/emulationstation/frontend/sony/Ps4Game;->prepare(Landroid/content/Context;Landroid/net/Uri;Ljava/io/File;Ljava/lang/Class;Ljava/util/function/BiConsumer;)Lorg/emulationstation/frontend/sony/Ps4Game;

    move-result-object v0

    .line 128
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->checkStopped()V

    .line 129
    new-instance v4, Ljava/io/File;

    new-instance v7, Ljava/lang/StringBuilder;

    invoke-direct {v7}, Ljava/lang/StringBuilder;-><init>()V

    const-string v8, "s/"

    invoke-virtual {v7, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v8

    invoke-virtual {v8}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v8

    const-string v9, "-"

    const-string v10, ""

    invoke-virtual {v8, v9, v10}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v8

    const/16 v9, 0xa

    invoke-virtual {v8, v2, v9}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v8

    invoke-virtual {v7, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v7}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v7

    invoke-direct {v4, v6, v7}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-static {v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    move-result-object v4

    iput-object v4, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->session:Ljava/io/File;

    .line 130
    new-instance v4, Ljava/io/File;

    iget-object v7, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->session:Ljava/io/File;

    const-string v8, "c"

    invoke-direct {v4, v7, v8}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    new-instance v7, Ljava/io/File;

    iget-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->session:Ljava/io/File;

    const-string v9, "a"

    invoke-direct {v7, v8, v9}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 131
    new-instance v8, Lorg/emulationstation/frontend/sony/Ps4Control;

    new-instance v9, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda18;

    invoke-direct {v9, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda18;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-direct {v8, v4, v9}, Lorg/emulationstation/frontend/sony/Ps4Control;-><init>(Ljava/io/File;Ljava/util/function/Consumer;)V

    iput-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    new-instance v8, Lorg/emulationstation/frontend/sony/Ps4Audio;

    new-instance v9, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda19;

    invoke-direct {v9, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda19;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-direct {v8, v7, v9}, Lorg/emulationstation/frontend/sony/Ps4Audio;-><init>(Ljava/io/File;Ljava/util/function/Consumer;)V

    iput-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->audio:Lorg/emulationstation/frontend/sony/Ps4Audio;

    .line 132
    const-string v10, "libbachata_native_runtime.so"

    const-string v11, "--override-root"

    iget-object v8, v0, Lorg/emulationstation/frontend/sony/Ps4Game;->root:Ljava/io/File;

    invoke-virtual {v8}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v12

    const-string v13, "--bachata-storage-root"

    .line 133
    invoke-virtual {v6}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v14

    const-string v15, "--bachata-socket"

    invoke-virtual {v4}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v16

    filled-new-array/range {v10 .. v16}, [Ljava/lang/String;

    move-result-object v4

    .line 134
    new-instance v8, Ljava/lang/StringBuilder;

    invoke-direct {v8}, Ljava/lang/StringBuilder;-><init>()V

    const-string v9, "HOME="

    invoke-virtual {v8, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v6}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v9

    invoke-virtual {v8, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v8}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v8

    new-instance v9, Ljava/lang/StringBuilder;

    invoke-direct {v9}, Ljava/lang/StringBuilder;-><init>()V

    const-string v10, "TMPDIR="

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v10, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->session:Ljava/io/File;

    invoke-virtual {v10}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v10

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v9}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    new-instance v10, Ljava/lang/StringBuilder;

    invoke-direct {v10}, Ljava/lang/StringBuilder;-><init>()V

    const-string v11, "XDG_CACHE_HOME="

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    new-instance v11, Ljava/io/File;

    const-string v12, "xdg"

    invoke-direct {v11, v6, v12}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 135
    invoke-virtual {v11}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v11

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v10}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v10

    new-instance v11, Ljava/lang/StringBuilder;

    invoke-direct {v11}, Ljava/lang/StringBuilder;-><init>()V

    const-string v12, "MESA_SHADER_CACHE_DIR="

    invoke-virtual {v11, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    new-instance v12, Ljava/io/File;

    const-string v13, "shader-cache/mesa"

    invoke-direct {v12, v6, v13}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 136
    invoke-virtual {v12}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v11, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    new-instance v11, Ljava/lang/StringBuilder;

    invoke-direct {v11}, Ljava/lang/StringBuilder;-><init>()V

    const-string v12, "BACHATA_ALSA_SOCKET="

    invoke-virtual {v11, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 137
    invoke-virtual {v7}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v7

    invoke-virtual {v11, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v7

    filled-new-array {v8, v9, v10, v6, v7}, [Ljava/lang/String;

    move-result-object v6

    .line 139
    iget-object v7, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    monitor-enter v7
    :try_end_1
    .catch Ljava/lang/InterruptedException; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    .line 140
    :goto_2
    :try_start_2
    iget-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v8}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v8

    if-nez v8, :cond_4

    iget-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    if-eqz v8, :cond_3

    iget-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    invoke-virtual {v8}, Landroid/view/Surface;->isValid()Z

    move-result v8

    if-nez v8, :cond_4

    :cond_3
    iget-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    invoke-virtual {v8}, Ljava/lang/Object;->wait()V

    goto :goto_2

    .line 141
    :cond_4
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->checkStopped()V

    iget-object v8, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    .line 142
    monitor-exit v7
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 143
    :try_start_3
    iget-object v7, v0, Lorg/emulationstation/frontend/sony/Ps4Game;->title:Ljava/lang/String;

    const-string v9, "Iniciando o jogo\u2026"

    invoke-direct {v1, v7, v9}, Lorg/emulationstation/frontend/sony/Ps4Activity;->show(Ljava/lang/String;Ljava/lang/String;)V

    const-string v7, "game"

    iput-object v7, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->phase:Ljava/lang/String;

    iput-boolean v3, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    .line 144
    new-instance v7, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda20;

    invoke-direct {v7, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda20;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {v1, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 145
    iget-object v7, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->entry:Ljava/lang/Class;

    const-string v9, "run"

    const-class v10, Landroid/view/Surface;

    const-class v11, [Ljava/lang/String;

    const-class v12, [Ljava/lang/String;

    const-class v13, Ljava/lang/String;

    const-class v14, Ljava/util/function/IntConsumer;

    filled-new-array {v10, v11, v12, v13, v14}, [Ljava/lang/Class;

    move-result-object v10

    .line 146
    invoke-virtual {v5}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v5

    new-instance v11, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda21;

    invoke-direct {v11}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda21;-><init>()V

    filled-new-array {v8, v4, v6, v5, v11}, [Ljava/lang/Object;

    move-result-object v4

    .line 145
    invoke-static {v7, v9, v10, v4}, Lorg/emulationstation/frontend/sony/Ps4Game;->invoke(Ljava/lang/Class;Ljava/lang/String;[Ljava/lang/Class;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    .line 147
    iput-boolean v2, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    iget-object v5, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v5, v3}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    .line 148
    iget-object v5, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v5}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v5

    if-eqz v5, :cond_5

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finishOwner()V

    goto/16 :goto_5

    .line 149
    :cond_5
    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps4Game;->title:Ljava/lang/String;

    check-cast v4, Ljava/lang/Integer;

    invoke-virtual {v4}, Ljava/lang/Integer;->intValue()I

    move-result v4

    if-nez v4, :cond_6

    const-string v4, "Partida encerrada."

    goto :goto_3

    :cond_6
    const-string v4, "O motor n\u00e3o conseguiu iniciar ou manter este jogo."

    :goto_3
    invoke-direct {v1, v0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->show(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_3
    .catch Ljava/lang/InterruptedException; {:try_start_3 .. :try_end_3} :catch_0
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    goto :goto_5

    :catchall_0
    move-exception v0

    .line 142
    :try_start_4
    monitor-exit v7
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_0

    :try_start_5
    throw v0

    .line 106
    :cond_7
    new-instance v0, Ljava/io/IOException;

    const-string v4, "N\u00e3o foi poss\u00edvel proteger o motor PS4"

    invoke-direct {v0, v4}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 92
    :cond_8
    new-instance v0, Ljava/io/IOException;

    const-string v4, "O motor PS4 requer Android 12 ou mais recente"

    invoke-direct {v0, v4}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_5
    .catch Ljava/lang/InterruptedException; {:try_start_5 .. :try_end_5} :catch_0
    .catchall {:try_start_5 .. :try_end_5} :catchall_1

    :catchall_1
    move-exception v0

    .line 153
    :try_start_6
    iget-object v4, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v4, v3}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    iput-boolean v2, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    .line 154
    iget-object v2, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v2}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v2

    if-eqz v2, :cond_9

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finishOwner()V

    goto :goto_5

    .line 155
    :cond_9
    instance-of v2, v0, Ljava/io/IOException;

    if-eqz v2, :cond_a

    invoke-virtual {v0}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v2

    goto :goto_4

    :cond_a
    const-string v2, "N\u00e3o foi poss\u00edvel iniciar o motor PS4 interno."

    .line 156
    :goto_4
    const-string v3, "PlayStation 4"

    if-nez v2, :cond_b

    const-string v2, "O jogo n\u00e3o p\u00f4de ser preparado."

    :cond_b
    invoke-direct {v1, v3, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->show(Ljava/lang/String;Ljava/lang/String;)V

    .line 157
    const-string v2, "StationPS4Owner"

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Internal owner failed in "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v4, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->phase:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v2, v3, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    goto :goto_5

    .line 151
    :catch_0
    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Thread;->interrupt()V

    iget-object v0, v1, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0, v3}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finishOwner()V
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_2

    .line 159
    :goto_5
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->closeSession()V

    return-void

    :catchall_2
    move-exception v0

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->closeSession()V

    throw v0
.end method

.method private progress(Ljava/lang/String;JJ)V
    .locals 6

    .line 162
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v0

    iget-wide v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->lastProgress:J

    sub-long v2, v0, v2

    const-wide/16 v4, 0xfa

    cmp-long v2, v2, v4

    if-gez v2, :cond_0

    cmp-long v2, p2, p4

    if-eqz v2, :cond_0

    return-void

    :cond_0
    iput-wide v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->lastProgress:J

    .line 163
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-wide/16 v1, 0x0

    cmp-long p1, p4, v1

    if-lez p1, :cond_1

    new-instance p1, Ljava/lang/StringBuilder;

    const-string v1, " \u00b7 "

    invoke-direct {p1, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    const-wide/16 v1, 0x64

    mul-long/2addr p2, v1

    div-long/2addr p2, p4

    invoke-static {v1, v2, p2, p3}, Ljava/lang/Math;->min(JJ)J

    move-result-wide p2

    invoke-virtual {p1, p2, p3}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    const-string p2, "%"

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    goto :goto_0

    :cond_1
    const-string p1, "\u2026"

    :goto_0
    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    const-string p2, "PlayStation 4"

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->show(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method private readNativeConfig()Lorg/json/JSONObject;
    .locals 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;,
            Lorg/json/JSONException;
        }
    .end annotation

    .line 315
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    if-eqz v0, :cond_4

    .line 316
    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v0

    if-nez v0, :cond_0

    new-instance v0, Lorg/json/JSONObject;

    invoke-direct {v0}, Lorg/json/JSONObject;-><init>()V

    return-object v0

    .line 317
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->isFile()Z

    move-result v0

    if-eqz v0, :cond_3

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->length()J

    move-result-wide v0

    const-wide/32 v2, 0x80000

    cmp-long v0, v0, v2

    if-gtz v0, :cond_3

    .line 318
    new-instance v0, Ljava/io/FileInputStream;

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    invoke-direct {v0, v1}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V

    :try_start_0
    new-instance v1, Ljava/io/ByteArrayOutputStream;

    invoke-direct {v1}, Ljava/io/ByteArrayOutputStream;-><init>()V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    const/16 v2, 0x2000

    .line 319
    :try_start_1
    new-array v2, v2, [B

    .line 320
    :goto_0
    invoke-virtual {v0, v2}, Ljava/io/InputStream;->read([B)I

    move-result v3

    const/4 v4, -0x1

    if-eq v3, v4, :cond_2

    invoke-virtual {v1}, Ljava/io/ByteArrayOutputStream;->size()I

    move-result v4

    add-int/2addr v4, v3

    const/high16 v5, 0x80000

    if-gt v4, v5, :cond_1

    const/4 v4, 0x0

    invoke-virtual {v1, v2, v4, v3}, Ljava/io/ByteArrayOutputStream;->write([BII)V

    goto :goto_0

    :cond_1
    new-instance v2, Ljava/io/IOException;

    const-string v3, "Configura\u00e7\u00e3o PS4 muito grande"

    invoke-direct {v2, v3}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v2

    .line 321
    :cond_2
    new-instance v2, Lorg/json/JSONObject;

    new-instance v3, Ljava/lang/String;

    invoke-virtual {v1}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object v4

    sget-object v5, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v3, v4, v5}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V

    invoke-direct {v2, v3}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 322
    :try_start_2
    invoke-virtual {v1}, Ljava/io/ByteArrayOutputStream;->close()V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    invoke-virtual {v0}, Ljava/io/InputStream;->close()V

    return-object v2

    :catchall_0
    move-exception v2

    .line 318
    :try_start_3
    invoke-virtual {v1}, Ljava/io/ByteArrayOutputStream;->close()V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    goto :goto_1

    :catchall_1
    move-exception v1

    :try_start_4
    invoke-virtual {v2, v1}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :goto_1
    throw v2
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_2

    :catchall_2
    move-exception v1

    :try_start_5
    invoke-virtual {v0}, Ljava/io/InputStream;->close()V
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_3

    goto :goto_2

    :catchall_3
    move-exception v0

    invoke-virtual {v1, v0}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :goto_2
    throw v1

    .line 317
    :cond_3
    new-instance v0, Ljava/io/IOException;

    const-string v1, "Arquivo de configura\u00e7\u00e3o PS4 inv\u00e1lido"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 315
    :cond_4
    new-instance v0, Ljava/io/IOException;

    const-string v1, "Configura\u00e7\u00e3o PS4 indispon\u00edvel"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
.end method

.method private saveSettingsEntry(Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;)V
    .locals 2

    .line 368
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-eqz v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsSaving:Z

    if-nez v0, :cond_1

    iget v0, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->kind:I

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x1

    .line 369
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsSaving:Z

    .line 370
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMessage:Landroid/widget/TextView;

    const-string v1, "Salvando configura\u00e7\u00e3o\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 371
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda10;

    invoke-direct {v1, p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda10;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;)V

    invoke-interface {v0, v1}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private selectSettingsCategory(I)V
    .locals 4

    .line 330
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    if-nez v0, :cond_0

    goto :goto_0

    .line 331
    :cond_0
    iput p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsCategory:I

    iget v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    add-int/lit8 v1, v1, 0x1

    iput v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    .line 332
    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    const-string v2, "Lendo configura\u00e7\u00e3o\u2026"

    const/16 v3, 0xd

    invoke-direct {p0, v2, v3}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsText(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v2

    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 333
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda26;

    invoke-direct {v2, p0, v1, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda26;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;II)V

    invoke-interface {v0, v2}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private settingsActive()Z
    .locals 1

    .line 264
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsLeaving:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-nez v0, :cond_0

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_0

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->isDestroyed()Z

    move-result v0

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ExecutorService;->isShutdown()Z

    move-result v0

    if-nez v0, :cond_0

    const/4 v0, 0x1

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    :goto_0
    return v0
.end method

.method private settingsBackground(I)Landroid/graphics/drawable/GradientDrawable;
    .locals 1

    .line 253
    new-instance v0, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v0}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    const/4 p1, 0x7

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result p1

    int-to-float p1, p1

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    return-object v0
.end method

.method private settingsButton(Ljava/lang/String;)Landroid/widget/Button;
    .locals 3

    .line 256
    new-instance v0, Landroid/widget/Button;

    invoke-direct {v0, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 p1, 0x0

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setAllCaps(Z)V

    const/high16 v1, 0x41500000    # 13.0f

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextSize(F)V

    const v1, -0x161107

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextColor(I)V

    .line 257
    invoke-virtual {v0, p1}, Landroid/widget/Button;->setMinHeight(I)V

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setMinimumHeight(I)V

    const/16 v1, 0xc

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v2

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v1

    invoke-virtual {v0, v2, p1, v1, p1}, Landroid/widget/Button;->setPadding(IIII)V

    const p1, -0xe7d9ce

    .line 258
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBackground(I)Landroid/graphics/drawable/GradientDrawable;

    move-result-object p1

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setBackground(Landroid/graphics/drawable/Drawable;)V

    return-object v0
.end method

.method private settingsError(Ljava/lang/String;)V
    .locals 1

    .line 399
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda30;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda30;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method private settingsText(Ljava/lang/String;I)Landroid/widget/TextView;
    .locals 1

    .line 261
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    int-to-float p1, p2

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextSize(F)V

    const p1, -0x161107

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextColor(I)V

    return-object v0
.end method

.method private show(Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 172
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda25;

    invoke-direct {v0, p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda25;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method private showSettings()V
    .locals 15

    .line 267
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    .line 268
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    invoke-virtual {v0}, Landroid/widget/FrameLayout;->removeAllViews()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    const v1, -0xd7814b

    invoke-virtual {v0, v1}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    .line 269
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v2, 0x10

    .line 270
    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v3

    const/16 v4, 0xa

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v5

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v6

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v7

    invoke-virtual {v0, v3, v5, v6, v7}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    new-instance v5, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v6, -0x1

    invoke-direct {v5, v6, v6}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v3, v0, v5}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 271
    new-instance v3, Landroid/widget/LinearLayout;

    invoke-direct {v3, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    invoke-virtual {v3, v2}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 272
    const-string v2, "\u2039  Voltar"

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsButton(Ljava/lang/String;)Landroid/widget/Button;

    move-result-object v2

    sget-object v5, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v2, v5, v1}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;I)V

    .line 273
    new-instance v5, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda5;

    invoke-direct {v5, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda5;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {v2, v5}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v7, 0x5e

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v7

    const/16 v8, 0x26

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v8

    invoke-direct {v5, v7, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v3, v2, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 274
    const-string v2, "PS4  /  Configura\u00e7\u00f5es"

    const/16 v5, 0x13

    invoke-direct {p0, v2, v5}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsText(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v2

    sget-object v7, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v2, v7, v1}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    const/16 v7, 0xe

    .line 275
    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v7

    const/4 v8, 0x0

    invoke-virtual {v2, v7, v8, v8, v8}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v7, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v9, -0x2

    const/high16 v10, 0x3f800000    # 1.0f

    invoke-direct {v7, v8, v9, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v3, v2, v7}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 276
    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v7, 0x2c

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v7

    invoke-direct {v2, v6, v7}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v3, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 277
    const-string v2, "Op\u00e7\u00f5es do motor \u00b7 altera\u00e7\u00f5es valem no pr\u00f3ximo jogo"

    const/16 v3, 0xc

    invoke-direct {p0, v2, v3}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsText(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v2

    iput-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMessage:Landroid/widget/TextView;

    const v7, -0x6c5746

    .line 278
    invoke-virtual {v2, v7}, Landroid/widget/TextView;->setTextColor(I)V

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMessage:Landroid/widget/TextView;

    const/4 v7, 0x3

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v7

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v4

    invoke-virtual {v2, v8, v7, v8, v4}, Landroid/widget/TextView;->setPadding(IIII)V

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMessage:Landroid/widget/TextView;

    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 279
    new-instance v2, Landroid/widget/LinearLayout;

    invoke-direct {v2, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    new-instance v4, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v4, v6, v8, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v0, v2, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 280
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 281
    new-instance v4, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v7, 0x8c

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v7

    invoke-direct {v4, v7, v6}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v0, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 282
    const-string v4, "Sistema"

    const-string v7, "\u00c1udio"

    const-string v11, "Imagem"

    const-string v12, "Desempenho"

    filled-new-array {v11, v12, v4, v7}, [Ljava/lang/String;

    move-result-object v4

    move v7, v8

    :goto_0
    const/4 v11, 0x4

    if-ge v7, v11, :cond_1

    .line 284
    aget-object v11, v4, v7

    invoke-direct {p0, v11}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsButton(Ljava/lang/String;)Landroid/widget/Button;

    move-result-object v11

    invoke-virtual {v11, v5}, Landroid/widget/Button;->setGravity(I)V

    .line 285
    sget-object v12, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v11, v12, v1}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;I)V

    new-instance v12, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda6;

    invoke-direct {v12, p0, v7}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda6;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;I)V

    invoke-virtual {v11, v12}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 286
    new-instance v12, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v13, 0x27

    invoke-direct {p0, v13}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v13

    invoke-direct {v12, v6, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v13

    const/4 v14, 0x7

    invoke-direct {p0, v14}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v14

    invoke-virtual {v12, v8, v8, v13, v14}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {v0, v11, v12}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    add-int/lit8 v7, v7, 0x1

    goto :goto_0

    .line 288
    :cond_1
    new-instance v0, Landroid/widget/ScrollView;

    invoke-direct {v0, p0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, v8}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v8, v6, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v2, v0, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 289
    new-instance v2, Landroid/widget/LinearLayout;

    invoke-direct {v2, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    iput-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    invoke-virtual {v2, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v2, v6, v9}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/ScrollView;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 290
    iget v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsCategory:I

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->selectSettingsCategory(I)V

    return-void
.end method

.method private stopOwner()V
    .locals 3

    .line 187
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopping:Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v1, 0x0

    const/4 v2, 0x1

    invoke-virtual {v0, v1, v2}, Ljava/util/concurrent/atomic/AtomicBoolean;->compareAndSet(ZZ)Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    .line 188
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    if-eqz v0, :cond_1

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Touch;->clear()V

    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    if-eqz v0, :cond_2

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Control;->neutral()V

    .line 189
    :cond_2
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    monitor-enter v0

    :try_start_0
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    invoke-virtual {v1}, Ljava/lang/Object;->notifyAll()V

    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 190
    const-string v0, "PlayStation 4"

    const-string v1, "Encerrando\u2026"

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->show(Ljava/lang/String;Ljava/lang/String;)V

    .line 191
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-eqz v0, :cond_3

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finishOwner()V

    return-void

    .line 192
    :cond_3
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopper:Ljava/util/concurrent/ExecutorService;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda11;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda11;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-interface {v0, v1}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    return-void

    :catchall_0
    move-exception v1

    .line 189
    :try_start_1
    monitor-exit v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    throw v1
.end method

.method private updatePhysical()V
    .locals 6

    .line 240
    invoke-static {}, Landroid/view/InputDevice;->getDeviceIds()[I

    move-result-object v0

    array-length v1, v0

    const/4 v2, 0x0

    move v3, v2

    :goto_0
    const/4 v4, 0x1

    if-ge v3, v1, :cond_1

    aget v5, v0, v3

    invoke-static {v5}, Landroid/view/InputDevice;->getDevice(I)Landroid/view/InputDevice;

    move-result-object v5

    if-eqz v5, :cond_0

    invoke-virtual {v5}, Landroid/view/InputDevice;->getSources()I

    move-result v5

    invoke-static {v5}, Lorg/emulationstation/frontend/sony/Ps4Control;->gamepad(I)Z

    move-result v5

    if-eqz v5, :cond_0

    move v0, v4

    goto :goto_1

    :cond_0
    add-int/lit8 v3, v3, 0x1

    goto :goto_0

    :cond_1
    move v0, v2

    .line 241
    :goto_1
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    if-eqz v1, :cond_4

    if-eqz v0, :cond_2

    invoke-virtual {v1}, Lorg/emulationstation/frontend/sony/Ps4Touch;->clear()V

    :cond_2
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    iget-boolean v3, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    if-eqz v3, :cond_3

    if-nez v0, :cond_3

    invoke-virtual {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v3, "touch"

    invoke-interface {v0, v3, v4}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0

    if-eqz v0, :cond_3

    goto :goto_2

    :cond_3
    const/16 v2, 0x8

    :goto_2
    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/sony/Ps4Touch;->setVisibility(I)V

    :cond_4
    return-void
.end method

.method private warning(Ljava/lang/String;)V
    .locals 1

    .line 170
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda0;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda0;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method


# virtual methods
.method public dispatchGenericMotionEvent(Landroid/view/MotionEvent;)Z
    .locals 1

    .line 223
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    if-eqz v0, :cond_0

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/sony/Ps4Control;->motion(Landroid/view/MotionEvent;)Z

    move-result v0

    if-eqz v0, :cond_0

    const/4 p1, 0x1

    return p1

    :cond_0
    invoke-super {p0, p1}, Landroid/app/Activity;->dispatchGenericMotionEvent(Landroid/view/MotionEvent;)Z

    move-result p1

    return p1
.end method

.method public dispatchKeyEvent(Landroid/view/KeyEvent;)Z
    .locals 1

    .line 222
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    if-eqz v0, :cond_0

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/sony/Ps4Control;->key(Landroid/view/KeyEvent;)Z

    move-result v0

    if-eqz v0, :cond_0

    const/4 p1, 0x1

    return p1

    :cond_0
    invoke-super {p0, p1}, Landroid/app/Activity;->dispatchKeyEvent(Landroid/view/KeyEvent;)Z

    move-result p1

    return p1
.end method

.method synthetic lambda$addSetting$19$org-emulationstation-frontend-sony-Ps4Activity(Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Landroid/content/DialogInterface;I)V
    .locals 1

    .line 362
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->choices:[Ljava/lang/String;

    aget-object p3, v0, p3

    invoke-direct {p0, p1, p3}, Lorg/emulationstation/frontend/sony/Ps4Activity;->saveSettingsEntry(Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;)V

    :cond_0
    invoke-interface {p2}, Landroid/content/DialogInterface;->dismiss()V

    return-void
.end method

.method synthetic lambda$addSetting$20$org-emulationstation-frontend-sony-Ps4Activity(Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;Landroid/view/View;)V
    .locals 2

    .line 357
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result p3

    if-eqz p3, :cond_4

    iget-boolean p3, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsSaving:Z

    if-eqz p3, :cond_0

    goto :goto_1

    .line 358
    :cond_0
    iget p3, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->kind:I

    const/4 v0, 0x1

    if-ne p3, v0, :cond_1

    check-cast p2, Ljava/lang/Boolean;

    invoke-virtual {p2}, Ljava/lang/Boolean;->booleanValue()Z

    move-result p2

    xor-int/2addr p2, v0

    invoke-static {p2}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object p2

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->saveSettingsEntry(Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;)V

    goto :goto_1

    :cond_1
    const/4 p3, -0x1

    const/4 v0, 0x0

    .line 360
    :goto_0
    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->choices:[Ljava/lang/String;

    array-length v1, v1

    if-ge v0, v1, :cond_3

    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->choices:[Ljava/lang/String;

    aget-object v1, v1, v0

    invoke-virtual {v1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_2

    move p3, v0

    :cond_2
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 361
    :cond_3
    new-instance p2, Landroid/app/AlertDialog$Builder;

    invoke-direct {p2, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->label:Ljava/lang/String;

    invoke-virtual {p2, v0}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p2

    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->choices:[Ljava/lang/String;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda9;

    invoke-direct {v1, p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda9;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;)V

    invoke-virtual {p2, v0, p3, v1}, Landroid/app/AlertDialog$Builder;->setSingleChoiceItems([Ljava/lang/CharSequence;ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    const-string p2, "Cancelar"

    const/4 p3, 0x0

    .line 363
    invoke-virtual {p1, p2, p3}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    invoke-virtual {p1}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    :cond_4
    :goto_1
    return-void
.end method

.method synthetic lambda$addTouchSetting$24$org-emulationstation-frontend-sony-Ps4Activity(ZLandroid/view/View;)V
    .locals 1

    .line 394
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result p2

    if-eqz p2, :cond_1

    iget-boolean p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsSaving:Z

    if-eqz p2, :cond_0

    goto :goto_0

    :cond_0
    const/4 p2, 0x0

    .line 395
    invoke-virtual {p0, p2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object p2

    invoke-interface {p2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object p2

    xor-int/lit8 p1, p1, 0x1

    const-string v0, "touch"

    invoke-interface {p2, v0, p1}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object p1

    invoke-interface {p1}, Landroid/content/SharedPreferences$Editor;->apply()V

    iget p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsCategory:I

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->selectSettingsCategory(I)V

    :cond_1
    :goto_0
    return-void
.end method

.method synthetic lambda$closeSession$12$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 3

    .line 203
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    const/16 v1, 0x8

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Touch;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/sony/Ps4Touch;->setVisibility(I)V

    .line 204
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->display:Landroid/view/TextureView;

    if-eqz v0, :cond_1

    invoke-virtual {v0, v1}, Landroid/view/TextureView;->setVisibility(I)V

    .line 206
    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    monitor-enter v0

    :try_start_0
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    const/4 v2, 0x0

    if-eqz v1, :cond_2

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    invoke-virtual {v1}, Landroid/view/Surface;->release()V

    iput-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    :cond_2
    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 207
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->retainedTexture:Landroid/graphics/SurfaceTexture;

    if-eqz v0, :cond_3

    invoke-virtual {v0}, Landroid/graphics/SurfaceTexture;->release()V

    iput-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->retainedTexture:Landroid/graphics/SurfaceTexture;

    :cond_3
    return-void

    :catchall_0
    move-exception v1

    .line 206
    :try_start_1
    monitor-exit v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    throw v1
.end method

.method synthetic lambda$confirmExit$10$org-emulationstation-frontend-sony-Ps4Activity(Landroid/content/DialogInterface;I)V
    .locals 0

    .line 184
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopOwner()V

    return-void
.end method

.method synthetic lambda$finishOwner$13$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 1

    .line 214
    invoke-static {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$ApplicationName;->expected(Landroid/app/Activity;)Z

    move-result v0

    if-eqz v0, :cond_0

    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v0

    invoke-static {v0}, Landroid/os/Process;->killProcess(I)V

    :cond_0
    return-void
.end method

.method synthetic lambda$finishOwner$14$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 4

    .line 212
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finish()V

    .line 214
    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda1;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda1;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    const-wide/16 v2, 0xc8

    invoke-virtual {v0, v1, v2, v3}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    return-void
.end method

.method synthetic lambda$nativeEvent$7$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 2

    .line 167
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->updatePhysical()V

    return-void
.end method

.method synthetic lambda$onCreate$2$org-emulationstation-frontend-sony-Ps4Activity(Landroid/view/View;)V
    .locals 0

    .line 76
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->confirmExit()V

    return-void
.end method

.method synthetic lambda$prepareAndRun$3$org-emulationstation-frontend-sony-Ps4Activity(Ljava/lang/String;II)V
    .locals 6

    .line 0
    int-to-long v2, p2

    int-to-long v4, p3

    .line 94
    const-string v1, "Preparando o motor"

    move-object v0, p0

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/sony/Ps4Activity;->progress(Ljava/lang/String;JJ)V

    return-void
.end method

.method synthetic lambda$prepareAndRun$4$org-emulationstation-frontend-sony-Ps4Activity(Ljava/lang/Long;Ljava/lang/Long;)V
    .locals 6

    .line 127
    invoke-virtual {p1}, Ljava/lang/Long;->longValue()J

    move-result-wide v2

    invoke-virtual {p2}, Ljava/lang/Long;->longValue()J

    move-result-wide v4

    const-string v1, "Preparando o jogo"

    move-object v0, p0

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/sony/Ps4Activity;->progress(Ljava/lang/String;JJ)V

    return-void
.end method

.method synthetic lambda$prepareAndRun$5$org-emulationstation-frontend-sony-Ps4Activity(Ljava/lang/String;)V
    .locals 1

    .line 131
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    if-eqz v0, :cond_0

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->warning(Ljava/lang/String;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$saveSettingsEntry$21$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 2

    .line 383
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    :cond_0
    const/4 v0, 0x0

    .line 384
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsSaving:Z

    .line 385
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMessage:Landroid/widget/TextView;

    const-string v1, "Salvo \u00b7 altera\u00e7\u00f5es valem no pr\u00f3ximo jogo"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsCategory:I

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->selectSettingsCategory(I)V

    return-void
.end method

.method synthetic lambda$saveSettingsEntry$22$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 1

    .line 387
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-eqz v0, :cond_0

    const/4 v0, 0x0

    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsSaving:Z

    :cond_0
    return-void
.end method

.method synthetic lambda$saveSettingsEntry$23$org-emulationstation-frontend-sony-Ps4Activity(Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;Ljava/lang/Object;)V
    .locals 3

    .line 373
    :try_start_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->readNativeConfig()Lorg/json/JSONObject;

    move-result-object v0

    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->section:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    .line 374
    iget-object v2, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->section:Ljava/lang/String;

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_1

    if-eqz v1, :cond_0

    goto :goto_0

    :cond_0
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Se\u00e7\u00e3o PS4 inv\u00e1lida"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    :cond_1
    :goto_0
    if-nez v1, :cond_2

    .line 375
    new-instance v1, Lorg/json/JSONObject;

    invoke-direct {v1}, Lorg/json/JSONObject;-><init>()V

    iget-object v2, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->section:Ljava/lang/String;

    invoke-virtual {v0, v2, v1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    .line 376
    :cond_2
    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->key:Ljava/lang/String;

    invoke-virtual {v1, p1, p2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    .line 377
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const/4 p2, 0x2

    invoke-virtual {v0, p2}, Lorg/json/JSONObject;->toString(I)Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p2, "\n"

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    sget-object p2, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {p1, p2}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object p1

    .line 378
    array-length p2, p1

    const/high16 v0, 0x80000

    if-gt p2, v0, :cond_4

    .line 379
    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    invoke-virtual {p2}, Ljava/io/File;->getParentFile()Ljava/io/File;

    move-result-object p2

    invoke-static {p2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->directory(Ljava/io/File;)Ljava/io/File;

    new-instance p2, Landroid/util/AtomicFile;

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsConfig:Ljava/io/File;

    invoke-direct {p2, v0}, Landroid/util/AtomicFile;-><init>(Ljava/io/File;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_2

    .line 380
    :try_start_1
    invoke-virtual {p2}, Landroid/util/AtomicFile;->startWrite()Ljava/io/FileOutputStream;

    move-result-object v0
    :try_end_1
    .catch Ljava/io/IOException; {:try_start_1 .. :try_end_1} :catch_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_2

    :try_start_2
    invoke-virtual {v0, p1}, Ljava/io/FileOutputStream;->write([B)V

    invoke-virtual {p2, v0}, Landroid/util/AtomicFile;->finishWrite(Ljava/io/FileOutputStream;)V
    :try_end_2
    .catch Ljava/io/IOException; {:try_start_2 .. :try_end_2} :catch_0
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_2

    .line 382
    :try_start_3
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda2;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda2;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    goto :goto_2

    :catch_0
    move-exception p1

    goto :goto_1

    :catch_1
    move-exception p1

    const/4 v0, 0x0

    :goto_1
    if-eqz v0, :cond_3

    .line 381
    invoke-virtual {p2, v0}, Landroid/util/AtomicFile;->failWrite(Ljava/io/FileOutputStream;)V

    :cond_3
    throw p1

    .line 378
    :cond_4
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Configura\u00e7\u00e3o PS4 muito grande"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1
    :try_end_3
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_2

    .line 387
    :catch_2
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda3;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda3;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    const-string p1, "N\u00e3o foi poss\u00edvel salvar a configura\u00e7\u00e3o do PS4."

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsError(Ljava/lang/String;)V

    :goto_2
    return-void
.end method

.method synthetic lambda$selectSettingsCategory$17$org-emulationstation-frontend-sony-Ps4Activity(IILorg/json/JSONObject;)V
    .locals 4

    .line 337
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-eqz v0, :cond_3

    iget v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    if-ne p1, v0, :cond_3

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsBody:Landroid/widget/LinearLayout;

    if-nez p1, :cond_0

    goto :goto_1

    .line 338
    :cond_0
    invoke-virtual {p1}, Landroid/widget/LinearLayout;->removeAllViews()V

    .line 339
    sget-object p1, Lorg/emulationstation/frontend/sony/Ps4Activity;->SETTINGS:[Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;

    array-length v0, p1

    const/4 v1, 0x0

    :goto_0
    if-ge v1, v0, :cond_2

    aget-object v2, p1, v1

    iget v3, v2, Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;->group:I

    if-ne v3, p2, :cond_1

    invoke-direct {p0, p3, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->addSetting(Lorg/json/JSONObject;Lorg/emulationstation/frontend/sony/Ps4Activity$Setting;)V

    :cond_1
    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_2
    const/4 p1, 0x2

    if-ne p2, p1, :cond_3

    .line 340
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->addTouchSetting()V

    :cond_3
    :goto_1
    return-void
.end method

.method synthetic lambda$selectSettingsCategory$18$org-emulationstation-frontend-sony-Ps4Activity(II)V
    .locals 2

    .line 335
    :try_start_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->readNativeConfig()Lorg/json/JSONObject;

    move-result-object v0

    .line 336
    new-instance v1, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda14;

    invoke-direct {v1, p0, p1, p2, v0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda14;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;IILorg/json/JSONObject;)V

    invoke-virtual {p0, v1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 342
    :catch_0
    const-string p1, "N\u00e3o foi poss\u00edvel ler a configura\u00e7\u00e3o do PS4."

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsError(Ljava/lang/String;)V

    :goto_0
    return-void
.end method

.method synthetic lambda$settingsError$25$org-emulationstation-frontend-sony-Ps4Activity(Ljava/lang/String;)V
    .locals 1

    .line 399
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsActive()Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMessage:Landroid/widget/TextView;

    if-eqz v0, :cond_0

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$show$9$org-emulationstation-frontend-sony-Ps4Activity(Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 172
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->title:Landroid/widget/TextView;

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->status:Landroid/widget/TextView;

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->notice:Landroid/widget/LinearLayout;

    const/4 p2, 0x0

    invoke-virtual {p1, p2}, Landroid/widget/LinearLayout;->setVisibility(I)V

    :cond_0
    return-void
.end method

.method synthetic lambda$showSettings$15$org-emulationstation-frontend-sony-Ps4Activity(Landroid/view/View;)V
    .locals 0

    .line 273
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->leaveSettings()V

    return-void
.end method

.method synthetic lambda$showSettings$16$org-emulationstation-frontend-sony-Ps4Activity(ILandroid/view/View;)V
    .locals 0

    .line 285
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->selectSettingsCategory(I)V

    return-void
.end method

.method synthetic lambda$stopOwner$11$org-emulationstation-frontend-sony-Ps4Activity()V
    .locals 5

    .line 193
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->entry:Ljava/lang/Class;

    if-nez v0, :cond_0

    return-void

    :cond_0
    const/4 v1, 0x0

    .line 194
    :try_start_0
    const-string v2, "cancelImport"

    new-array v3, v1, [Ljava/lang/Class;

    new-array v4, v1, [Ljava/lang/Object;

    invoke-static {v0, v2, v3, v4}, Lorg/emulationstation/frontend/sony/Ps4Game;->invoke(Ljava/lang/Class;Ljava/lang/String;[Ljava/lang/Class;[Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 195
    :catch_0
    :try_start_1
    const-string v2, "stop"

    new-array v3, v1, [Ljava/lang/Class;

    new-array v1, v1, [Ljava/lang/Object;

    invoke-static {v0, v2, v3, v1}, Lorg/emulationstation/frontend/sony/Ps4Game;->invoke(Ljava/lang/Class;Ljava/lang/String;[Ljava/lang/Class;[Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_1

    :catch_1
    return-void
.end method

.method synthetic lambda$warning$8$org-emulationstation-frontend-sony-Ps4Activity(Ljava/lang/String;)V
    .locals 1

    .line 170
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_0

    const/4 v0, 0x0

    invoke-static {p0, p1, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object p1

    invoke-virtual {p1}, Landroid/widget/Toast;->show()V

    :cond_0
    return-void
.end method

.method public onBackPressed()V
    .locals 0

    .line 221
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->confirmExit()V

    return-void
.end method

.method public onConfigurationChanged(Landroid/content/res/Configuration;)V
    .locals 0

    .line 238
    invoke-super {p0, p1}, Landroid/app/Activity;->onConfigurationChanged(Landroid/content/res/Configuration;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->updatePhysical()V

    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .locals 7

    .line 57
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 58
    invoke-static {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$ApplicationName;->expected(Landroid/app/Activity;)Z

    move-result p1

    if-nez p1, :cond_0

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->finish()V

    return-void

    .line 59
    :cond_0
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getWindow()Landroid/view/Window;

    move-result-object p1

    const/16 v0, 0x80

    invoke-virtual {p1, v0}, Landroid/view/Window;->addFlags(I)V

    .line 60
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object p1

    const/16 v0, 0x1706

    invoke-virtual {p1, v0}, Landroid/view/View;->setSystemUiVisibility(I)V

    .line 62
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getIntent()Landroid/content/Intent;

    move-result-object p1

    invoke-virtual {p1}, Landroid/content/Intent;->getData()Landroid/net/Uri;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->requested:Landroid/net/Uri;

    .line 63
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getIntent()Landroid/content/Intent;

    move-result-object p1

    const-string v0, "operation"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const-string v0, "settings"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    const/4 v0, 0x1

    const/4 v1, 0x0

    if-nez p1, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->requested:Landroid/net/Uri;

    if-nez p1, :cond_1

    goto :goto_0

    :cond_1
    move p1, v1

    goto :goto_1

    :cond_2
    :goto_0
    move p1, v0

    :goto_1
    iput-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMode:Z

    .line 64
    new-instance p1, Landroid/widget/FrameLayout;

    invoke-direct {p1, p0}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    const/high16 v2, -0x1000000

    invoke-virtual {p1, v2}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->setContentView(Landroid/view/View;)V

    .line 65
    new-instance p1, Landroid/view/TextureView;

    invoke-direct {p1, p0}, Landroid/view/TextureView;-><init>(Landroid/content/Context;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->display:Landroid/view/TextureView;

    invoke-virtual {p1, p0}, Landroid/view/TextureView;->setSurfaceTextureListener(Landroid/view/TextureView$SurfaceTextureListener;)V

    .line 66
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->display:Landroid/view/TextureView;

    new-instance v3, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v4, -0x1

    invoke-direct {v3, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v2, v3}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 67
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps4Touch;

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps4Activity$1;

    invoke-direct {v2, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$1;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-direct {p1, p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Touch;-><init>(Landroid/content/Context;Lorg/emulationstation/frontend/sony/Ps4Touch$Target;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    const/16 v2, 0x8

    .line 73
    invoke-virtual {p1, v2}, Lorg/emulationstation/frontend/sony/Ps4Touch;->setVisibility(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    new-instance v5, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v5, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v3, v5}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 74
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->buildNotice()V

    .line 75
    new-instance p1, Landroid/widget/Button;

    invoke-direct {p1, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    iget-boolean v3, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsMode:Z

    if-eqz v3, :cond_3

    const-string v3, "Voltar"

    goto :goto_2

    :cond_3
    const-string v3, "Sair"

    :goto_2
    invoke-virtual {p1, v3}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/high16 v3, 0x41400000    # 12.0f

    invoke-virtual {p1, v3}, Landroid/widget/Button;->setTextSize(F)V

    invoke-virtual {p1, v1}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 76
    new-instance v3, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda7;

    invoke-direct {v3, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda7;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-virtual {p1, v3}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 77
    new-instance v3, Landroid/widget/FrameLayout$LayoutParams;

    const/16 v4, 0x42

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v4

    const/16 v5, 0x28

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v5

    const/16 v6, 0x35

    invoke-direct {v3, v4, v5, v6}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    .line 78
    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v4

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/sony/Ps4Activity;->dp(I)I

    move-result v2

    invoke-virtual {v3, v1, v4, v2, v1}, Landroid/widget/FrameLayout$LayoutParams;->setMargins(IIII)V

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->layout:Landroid/widget/FrameLayout;

    invoke-virtual {v2, p1, v3}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 79
    const-string p1, "input"

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Landroid/hardware/input/InputManager;

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->input:Landroid/hardware/input/InputManager;

    new-instance v2, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v3

    invoke-direct {v2, v3}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    invoke-virtual {p1, p0, v2}, Landroid/hardware/input/InputManager;->registerInputDeviceListener(Landroid/hardware/input/InputManager$InputDeviceListener;Landroid/os/Handler;)V

    .line 80
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->started:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {p1, v1, v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->compareAndSet(ZZ)Z

    move-result p1

    if-eqz p1, :cond_4

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    new-instance v0, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda8;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps4Activity$$ExternalSyntheticLambda8;-><init>(Lorg/emulationstation/frontend/sony/Ps4Activity;)V

    invoke-interface {p1, v0}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    :cond_4
    return-void
.end method

.method protected onDestroy()V
    .locals 2

    const/4 v0, 0x1

    .line 247
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsLeaving:Z

    iget v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    add-int/2addr v1, v0

    iput v1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->settingsEpoch:I

    .line 248
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->input:Landroid/hardware/input/InputManager;

    if-eqz v0, :cond_0

    invoke-virtual {v0, p0}, Landroid/hardware/input/InputManager;->unregisterInputDeviceListener(Landroid/hardware/input/InputManager$InputDeviceListener;)V

    .line 250
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->worker:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ExecutorService;->shutdown()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->stopper:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ExecutorService;->shutdown()V

    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V

    return-void
.end method

.method public onInputDeviceAdded(I)V
    .locals 0

    .line 243
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->updatePhysical()V

    return-void
.end method

.method public onInputDeviceChanged(I)V
    .locals 0

    .line 244
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->updatePhysical()V

    return-void
.end method

.method public onInputDeviceRemoved(I)V
    .locals 1

    .line 245
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    if-eqz v0, :cond_0

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/sony/Ps4Control;->removed(I)V

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps4Activity;->updatePhysical()V

    return-void
.end method

.method protected onNewIntent(Landroid/content/Intent;)V
    .locals 0

    .line 218
    invoke-super {p0, p1}, Landroid/app/Activity;->onNewIntent(Landroid/content/Intent;)V

    .line 219
    iget-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->running:Z

    if-eqz p1, :cond_0

    const-string p1, "A partida atual continua aberta. Saia dela para trocar de jogo."

    goto :goto_0

    :cond_0
    const-string p1, "O PS4 j\u00e1 est\u00e1 aberto. Volte \u00e0 lista para escolher o jogo."

    :goto_0
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps4Activity;->warning(Ljava/lang/String;)V

    return-void
.end method

.method protected onPause()V
    .locals 1

    .line 237
    invoke-super {p0}, Landroid/app/Activity;->onPause()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->touch:Lorg/emulationstation/frontend/sony/Ps4Touch;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Touch;->clear()V

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->control:Lorg/emulationstation/frontend/sony/Ps4Control;

    if-eqz v0, :cond_1

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps4Control;->neutral()V

    :cond_1
    return-void
.end method

.method public onSurfaceTextureAvailable(Landroid/graphics/SurfaceTexture;II)V
    .locals 0

    .line 225
    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {p2}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result p2

    if-eqz p2, :cond_0

    return-void

    .line 226
    :cond_0
    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->retainedTexture:Landroid/graphics/SurfaceTexture;

    if-nez p2, :cond_1

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->retainedTexture:Landroid/graphics/SurfaceTexture;

    goto :goto_0

    :cond_1
    if-eq p2, p1, :cond_2

    .line 227
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->display:Landroid/view/TextureView;

    invoke-virtual {p1, p2}, Landroid/view/TextureView;->setSurfaceTexture(Landroid/graphics/SurfaceTexture;)V

    .line 228
    :cond_2
    :goto_0
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    monitor-enter p1

    :try_start_0
    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    if-nez p2, :cond_3

    new-instance p2, Landroid/view/Surface;

    iget-object p3, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->retainedTexture:Landroid/graphics/SurfaceTexture;

    invoke-direct {p2, p3}, Landroid/view/Surface;-><init>(Landroid/graphics/SurfaceTexture;)V

    iput-object p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surface:Landroid/view/Surface;

    :cond_3
    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->surfaceLock:Ljava/lang/Object;

    invoke-virtual {p2}, Ljava/lang/Object;->notifyAll()V

    monitor-exit p1

    return-void

    :catchall_0
    move-exception p2

    monitor-exit p1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    throw p2
.end method

.method public onSurfaceTextureDestroyed(Landroid/graphics/SurfaceTexture;)Z
    .locals 1

    .line 234
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->completed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps4Activity;->retainedTexture:Landroid/graphics/SurfaceTexture;

    if-eq v0, p1, :cond_0

    goto :goto_0

    :cond_0
    const/4 p1, 0x0

    goto :goto_1

    :cond_1
    :goto_0
    const/4 p1, 0x1

    :goto_1
    return p1
.end method

.method public onSurfaceTextureSizeChanged(Landroid/graphics/SurfaceTexture;II)V
    .locals 0

    return-void
.end method

.method public onSurfaceTextureUpdated(Landroid/graphics/SurfaceTexture;)V
    .locals 0

    return-void
.end method
