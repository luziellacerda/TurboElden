.class public final Lorg/emulationstation/frontend/sony/Ps3Activity;
.super Landroid/app/Activity;
.source "Ps3Activity.java"

# interfaces
.implements Landroid/view/SurfaceHolder$Callback;
.implements Landroid/hardware/input/InputManager$InputDeviceListener;


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;
    }
.end annotation


# static fields
.field private static final SETTINGS:[Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;


# instance fields
.field private volatile closed:Z

.field private controls:Lorg/emulationstation/frontend/sony/Ps3TouchControls;

.field private exitDialog:Z

.field private volatile gameConfigured:Z

.field private volatile input:Lorg/emulationstation/frontend/sony/Ps3Input;

.field private inputManager:Landroid/hardware/input/InputManager;

.field private volatile owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

.field private volatile prepared:Z

.field private progress:Landroid/widget/TextView;

.field private requestInFlight:Z

.field private volatile resumed:Z

.field private root:Landroid/widget/FrameLayout;

.field private settingsBody:Landroid/widget/LinearLayout;

.field private settingsCategory:I

.field private settingsEpoch:I

.field private settingsLeaving:Z

.field private settingsMessage:Landroid/widget/TextView;

.field private settingsSaving:Z

.field private volatile started:Z

.field private final submissions:Ljava/lang/Object;

.field private surface:Landroid/view/SurfaceView;

.field private final worker:Ljava/util/concurrent/ExecutorService;


# direct methods
.method public static synthetic $r8$lambda$QTDC_ncgmCRsHgPJX8gxvh5qs-Q(Lorg/emulationstation/frontend/sony/Ps3Activity;Ljava/lang/String;)V
    .locals 0

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->showProgress(Ljava/lang/String;)V

    return-void
.end method

.method public static synthetic $r8$lambda$eVqoYDY8ijrEPk7-Uii6vWFyCUo(Lorg/emulationstation/frontend/sony/Ps3Activity;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->showGame()V

    return-void
.end method

.method static constructor <clinit>()V
    .locals 22

    const/16 v0, 0x12

    .line 343
    new-array v0, v0, [Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    new-instance v9, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/4 v7, 0x0

    const/4 v10, 0x0

    new-array v8, v10, [Ljava/lang/String;

    const/4 v2, 0x0

    const/4 v3, 0x0

    const-string v4, "Video|Renderer"

    const-string v5, "Renderizador"

    const/4 v6, 0x0

    move-object v1, v9

    invoke-direct/range {v1 .. v8}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    aput-object v9, v0, v10

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const-string v20, "1280x1080"

    const-string v21, "960x1080"

    const-string v11, "1920x1080"

    const-string v12, "1920x1080i"

    const-string v13, "1280x720"

    const-string v14, "720x480"

    const-string v15, "720x480i"

    const-string v16, "720x576"

    const-string v17, "720x576i"

    const-string v18, "1600x1080"

    const-string v19, "1440x1080"

    filled-new-array/range {v11 .. v21}, [Ljava/lang/String;

    move-result-object v18

    const/4 v12, 0x0

    const/4 v13, 0x1

    const-string v14, "Video|Resolution"

    const-string v15, "Resolu\u00e7\u00e3o"

    const/16 v16, 0x0

    const/16 v17, 0x0

    move-object v11, v1

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x1

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0x320

    new-array v2, v10, [Ljava/lang/String;

    const/4 v13, 0x2

    const-string v14, "Video|Resolution Scale"

    const-string v15, "Escala de resolu\u00e7\u00e3o"

    const/16 v16, 0x19

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x2

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const-string v2, "4:3"

    const-string v3, "16:9"

    filled-new-array {v2, v3}, [Ljava/lang/String;

    move-result-object v18

    const/4 v13, 0x1

    const-string v14, "Video|Aspect ratio"

    const-string v15, "Propor\u00e7\u00e3o da imagem"

    const/16 v16, 0x0

    const/16 v17, 0x0

    move-object v11, v1

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x3

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const-string v18, "PS3 Native"

    const-string v19, "Infinite"

    const-string v11, "Off"

    const-string v12, "30"

    const-string v13, "50"

    const-string v14, "60"

    const-string v15, "120"

    const-string v16, "Display"

    const-string v17, "Auto"

    filled-new-array/range {v11 .. v19}, [Ljava/lang/String;

    move-result-object v18

    const/4 v12, 0x0

    const/4 v13, 0x1

    const-string v14, "Video|Frame limit"

    const-string v15, "Limite de quadros"

    const/16 v16, 0x0

    const/16 v17, 0x0

    move-object v11, v1

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x4

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    new-array v2, v10, [Ljava/lang/String;

    const/4 v13, 0x0

    const-string v14, "Video|Shader Mode"

    const-string v15, "Compila\u00e7\u00e3o de shaders"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x5

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    new-array v2, v10, [Ljava/lang/String;

    const/4 v13, 0x3

    const-string v14, "Video|Write Color Buffers"

    const-string v15, "Gravar buffers de cor"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x6

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    new-array v2, v10, [Ljava/lang/String;

    const-string v14, "Video|Strict Rendering Mode"

    const-string v15, "Renderiza\u00e7\u00e3o estrita"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/4 v2, 0x7

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0xc8

    new-array v2, v10, [Ljava/lang/String;

    const/4 v12, 0x1

    const/4 v13, 0x2

    const-string v14, "Audio|Master Volume"

    const-string v15, "Volume"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0x8

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0x0

    new-array v2, v10, [Ljava/lang/String;

    const/4 v13, 0x3

    const-string v14, "Audio|Enable Buffering"

    const-string v15, "Buffer de \u00e1udio"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0x9

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    new-array v2, v10, [Ljava/lang/String;

    const-string v14, "Audio|Enable Time Stretching"

    const-string v15, "Ajuste de tempo do \u00e1udio"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0xa

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const-string v2, "Interpreter (static)"

    const-string v3, "Recompiler (LLVM)"

    filled-new-array {v2, v3}, [Ljava/lang/String;

    move-result-object v18

    const/4 v12, 0x2

    const/4 v13, 0x1

    const-string v14, "Core|PPU Decoder"

    const-string v15, "Decodificador PPU"

    move-object v11, v1

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v4, 0xb

    aput-object v1, v0, v4

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const-string v4, "Interpreter (dynamic)"

    const-string v5, "Recompiler (ASMJIT)"

    filled-new-array {v2, v4, v5, v3}, [Ljava/lang/String;

    move-result-object v18

    const-string v14, "Core|SPU Decoder"

    const-string v15, "Decodificador SPU"

    move-object v11, v1

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0xc

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0x8

    new-array v2, v10, [Ljava/lang/String;

    const/4 v13, 0x2

    const-string v14, "Core|PPU Threads"

    const-string v15, "Threads PPU"

    const/16 v16, 0x1

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0xd

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0x6

    new-array v2, v10, [Ljava/lang/String;

    const-string v14, "Core|Preferred SPU Threads"

    const-string v15, "Threads SPU preferidas"

    const/16 v16, 0x0

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0xe

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0xc

    new-array v2, v10, [Ljava/lang/String;

    const-string v14, "Core|Max LLVM Compile Threads"

    const-string v15, "Threads de compila\u00e7\u00e3o LLVM"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0xf

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    const/16 v17, 0x0

    new-array v2, v10, [Ljava/lang/String;

    const/4 v13, 0x3

    const-string v14, "Core|LLVM Precompilation"

    const-string v15, "Pr\u00e9-compila\u00e7\u00e3o LLVM"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0x10

    aput-object v1, v0, v2

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    new-array v2, v10, [Ljava/lang/String;

    const/4 v12, 0x3

    const-string v14, "Miscellaneous|Show trophy popups"

    const-string v15, "Avisos de trof\u00e9us"

    move-object v11, v1

    move-object/from16 v18, v2

    invoke-direct/range {v11 .. v18}, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;-><init>(IILjava/lang/String;Ljava/lang/String;II[Ljava/lang/String;)V

    const/16 v2, 0x11

    aput-object v1, v0, v2

    sput-object v0, Lorg/emulationstation/frontend/sony/Ps3Activity;->SETTINGS:[Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    return-void
.end method

.method public constructor <init>()V
    .locals 1

    .line 35
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    .line 36
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda20;

    invoke-direct {v0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda20;-><init>()V

    invoke-static {v0}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor(Ljava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->worker:Ljava/util/concurrent/ExecutorService;

    .line 37
    new-instance v0, Ljava/lang/Object;

    invoke-direct {v0}, Ljava/lang/Object;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->submissions:Ljava/lang/Object;

    const/4 v0, 0x1

    .line 43
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->requestInFlight:Z

    return-void
.end method

.method private activateSurface(Landroid/view/SurfaceHolder;)V
    .locals 1

    .line 161
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda25;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda25;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Landroid/view/SurfaceHolder;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    return-void
.end method

.method private addSetting(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)V
    .locals 5

    .line 381
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->label:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, "   \u00b7   "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->displaySettingValue(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsButton(Ljava/lang/String;Z)Landroid/widget/Button;

    move-result-object v0

    .line 382
    sget-object v2, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v0, v2, v1}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;I)V

    const/16 v2, 0x13

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setGravity(I)V

    const/high16 v2, 0x41500000    # 13.0f

    .line 383
    invoke-virtual {v0, v2}, Landroid/widget/Button;->setTextSize(F)V

    const/4 v2, 0x1

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setSingleLine(Z)V

    sget-object v2, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 384
    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v3, 0x28

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v3

    const/4 v4, -0x1

    invoke-direct {v2, v4, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    const/4 v3, 0x5

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v3

    iput v3, v2, Landroid/widget/LinearLayout$LayoutParams;->bottomMargin:I

    .line 385
    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    invoke-virtual {v3, v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    if-eqz p2, :cond_1

    .line 386
    iget v2, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->kind:I

    if-nez v2, :cond_0

    goto :goto_0

    .line 387
    :cond_0
    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda16;

    invoke-direct {v1, p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda16;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)V

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-void

    .line 386
    :cond_1
    :goto_0
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    const p1, 0x3f3851ec    # 0.72f

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setAlpha(F)V

    return-void
.end method

.method private addTouchSetting()V
    .locals 5

    const/4 v0, 0x0

    .line 425
    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object v1

    const-string v2, "touch"

    const/4 v3, 0x1

    invoke-interface {v1, v2, v3}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v1

    if-eqz v1, :cond_0

    .line 426
    const-string v2, "Ativados"

    goto :goto_0

    :cond_0
    const-string v2, "Desativados"

    :goto_0
    const-string v3, "Controles de toque   \u00b7   "

    invoke-virtual {v3, v2}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-direct {p0, v2, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsButton(Ljava/lang/String;Z)Landroid/widget/Button;

    move-result-object v2

    .line 427
    sget-object v3, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v2, v3, v0}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;I)V

    const/16 v0, 0x13

    invoke-virtual {v2, v0}, Landroid/widget/Button;->setGravity(I)V

    .line 428
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda9;

    invoke-direct {v0, p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda9;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Z)V

    invoke-virtual {v2, v0}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 432
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v3, 0x28

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v3

    const/4 v4, -0x1

    invoke-direct {v1, v4, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v2, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-void
.end method

.method private detach(Landroid/net/Uri;)I
    .locals 4
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 134
    const-string v0, "file"

    invoke-virtual {p1}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    new-instance v0, Ljava/io/File;

    invoke-virtual {p1}, Landroid/net/Uri;->getPath()Ljava/lang/String;

    move-result-object p1

    invoke-direct {v0, p1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    const/high16 p1, 0x10000000

    invoke-static {v0, p1}, Landroid/os/ParcelFileDescriptor;->open(Ljava/io/File;I)Landroid/os/ParcelFileDescriptor;

    move-result-object p1

    goto :goto_0

    .line 135
    :cond_0
    const-string v0, "content"

    invoke-virtual {p1}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_3

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0

    const-string v1, "r"

    invoke-virtual {v0, p1, v1}, Landroid/content/ContentResolver;->openFileDescriptor(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;

    move-result-object p1

    :goto_0
    if-eqz p1, :cond_2

    .line 138
    invoke-virtual {p1}, Landroid/os/ParcelFileDescriptor;->getStatSize()J

    move-result-wide v0

    const-wide/16 v2, 0x0

    cmp-long v0, v0, v2

    if-eqz v0, :cond_1

    .line 139
    invoke-virtual {p1}, Landroid/os/ParcelFileDescriptor;->detachFd()I

    move-result v0

    invoke-virtual {p1}, Landroid/os/ParcelFileDescriptor;->close()V

    return v0

    .line 138
    :cond_1
    invoke-virtual {p1}, Landroid/os/ParcelFileDescriptor;->close()V

    new-instance p1, Ljava/io/IOException;

    const-string v0, "O arquivo PS3 est\u00e1 vazio"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 137
    :cond_2
    new-instance p1, Ljava/io/IOException;

    const-string v0, "N\u00e3o foi poss\u00edvel ler o arquivo PS3"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 136
    :cond_3
    new-instance p1, Ljava/io/IOException;

    const-string v0, "O arquivo precisa estar no armazenamento local"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method private detachPair(Landroid/net/Uri;Landroid/net/Uri;)[I
    .locals 0
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    .line 142
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->detach(Landroid/net/Uri;)I

    move-result p1

    if-nez p2, :cond_0

    const/4 p2, -0x1

    goto :goto_0

    .line 143
    :cond_0
    :try_start_0
    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->detach(Landroid/net/Uri;)I

    move-result p2

    :goto_0
    filled-new-array {p1, p2}, [I

    move-result-object p1
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_1
    .catch Ljava/lang/RuntimeException; {:try_start_0 .. :try_end_0} :catch_0

    return-object p1

    :catch_0
    move-exception p2

    goto :goto_1

    :catch_1
    move-exception p2

    .line 144
    :goto_1
    invoke-static {p1}, Landroid/os/ParcelFileDescriptor;->adoptFd(I)Landroid/os/ParcelFileDescriptor;

    move-result-object p1

    invoke-virtual {p1}, Landroid/os/ParcelFileDescriptor;->close()V

    throw p2
.end method

.method private displaySettingValue(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    if-nez p2, :cond_0

    .line 402
    const-string p1, "Indispon\u00edvel nesta vers\u00e3o"

    return-object p1

    .line 403
    :cond_0
    iget v0, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->kind:I

    const/4 v1, 0x3

    if-ne v0, v1, :cond_3

    const-string p1, "true"

    invoke-virtual {p1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_1

    const-string p2, "Ativado"

    goto :goto_0

    :cond_1
    const-string p1, "false"

    invoke-virtual {p1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_2

    const-string p2, "Desativado"

    :cond_2
    :goto_0
    return-object p2

    .line 404
    :cond_3
    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->tag:Ljava/lang/String;

    const-string v1, "Audio|Master Volume"

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_5

    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->tag:Ljava/lang/String;

    const-string v0, "Video|Resolution Scale"

    invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_4

    goto :goto_1

    :cond_4
    return-object p2

    :cond_5
    :goto_1
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p2, "%"

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    return-object p1
.end method

.method private editSettingsNumber(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)V
    .locals 6

    .line 408
    :try_start_0
    invoke-static {p2}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result p2
    :try_end_0
    .catch Ljava/lang/NumberFormatException; {:try_start_0 .. :try_end_0} :catch_0

    .line 409
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v1, 0x14

    .line 410
    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v2

    const/16 v3, 0xa

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v3

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v1

    const/4 v4, 0x0

    invoke-virtual {v0, v2, v3, v1, v4}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 411
    invoke-static {p2}, Ljava/lang/Integer;->toString(I)Ljava/lang/String;

    move-result-object v1

    const/16 v2, 0xf

    invoke-direct {p0, v1, v2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->text(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 412
    new-instance v2, Landroid/widget/SeekBar;

    invoke-direct {v2, p0}, Landroid/widget/SeekBar;-><init>(Landroid/content/Context;)V

    iget v3, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->maximum:I

    iget v5, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->minimum:I

    sub-int/2addr v3, v5

    invoke-virtual {v2, v3}, Landroid/widget/SeekBar;->setMax(I)V

    .line 413
    iget v3, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->maximum:I

    iget v5, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->minimum:I

    sub-int/2addr v3, v5

    iget v5, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->minimum:I

    sub-int/2addr p2, v5

    invoke-static {v3, p2}, Ljava/lang/Math;->min(II)I

    move-result p2

    invoke-static {v4, p2}, Ljava/lang/Math;->max(II)I

    move-result p2

    invoke-virtual {v2, p2}, Landroid/widget/SeekBar;->setProgress(I)V

    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 414
    new-instance p2, Lorg/emulationstation/frontend/sony/Ps3Activity$1;

    invoke-direct {p2, p0, v1, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$1;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Landroid/widget/TextView;Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;)V

    invoke-virtual {v2, p2}, Landroid/widget/SeekBar;->setOnSeekBarChangeListener(Landroid/widget/SeekBar$OnSeekBarChangeListener;)V

    .line 419
    new-instance p2, Landroid/app/AlertDialog$Builder;

    invoke-direct {p2, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->label:Ljava/lang/String;

    invoke-virtual {p2, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p2

    invoke-virtual {p2, v0}, Landroid/app/AlertDialog$Builder;->setView(Landroid/view/View;)Landroid/app/AlertDialog$Builder;

    move-result-object p2

    const-string v0, "Cancelar"

    const/4 v1, 0x0

    .line 420
    invoke-virtual {p2, v0, v1}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p2

    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda18;

    invoke-direct {v0, p0, p1, v2}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda18;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Landroid/widget/SeekBar;)V

    const-string p1, "Salvar"

    invoke-virtual {p2, p1, v0}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    .line 422
    invoke-virtual {p1}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    :catch_0
    return-void
.end method

.method private execute(Ljava/lang/Runnable;)V
    .locals 3

    .line 258
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->submissions:Ljava/lang/Object;

    monitor-enter v0

    .line 259
    :try_start_0
    iget-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v1, :cond_0

    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    return-void

    .line 261
    :cond_0
    :try_start_1
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->worker:Ljava/util/concurrent/ExecutorService;

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda26;

    invoke-direct {v2, p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda26;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Ljava/lang/Runnable;)V

    invoke-interface {v1, v2}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V
    :try_end_1
    .catch Ljava/util/concurrent/RejectedExecutionException; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_0

    :catch_0
    move-exception p1

    .line 263
    :try_start_2
    iget-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v1, :cond_1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->failure(Ljava/lang/Throwable;)V

    .line 265
    :cond_1
    :goto_0
    monitor-exit v0

    return-void

    :catchall_0
    move-exception p1

    monitor-exit v0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    throw p1
.end method

.method private failure(Ljava/lang/Throwable;)V
    .locals 1

    .line 271
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda2;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda2;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Ljava/lang/Throwable;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method static synthetic lambda$new$0(Ljava/lang/Runnable;)Ljava/lang/Thread;
    .locals 2

    .line 36
    new-instance v0, Ljava/lang/Thread;

    const-string v1, "StationPs3Owner"

    invoke-direct {v0, p0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    return-object v0
.end method

.method private leaveSettings()V
    .locals 2

    .line 452
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-eqz v0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x1

    .line 453
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    iget v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsEpoch:I

    add-int/2addr v1, v0

    iput v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsEpoch:I

    .line 455
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda8;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda8;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private prepareGame(Landroid/content/Intent;)V
    .locals 7
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 96
    const-string v0, "Preparando o jogo\u2026"

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->showProgress(Ljava/lang/String;)V

    .line 97
    const-string v0, "game_path"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x1

    if-eqz v0, :cond_1

    .line 99
    new-instance v2, Ljava/io/File;

    invoke-direct {v2, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->isDirectory()Z

    move-result v2

    if-eqz v2, :cond_1

    .line 100
    new-instance p1, Ljava/io/File;

    invoke-direct {p1, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object p1

    .line 101
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {p1}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v0, p1}, Laenu/aps3e/Emulator;->meta_info_from_dir(Ljava/lang/String;)Laenu/aps3e/Emulator$MetaInfo;

    move-result-object p1

    if-eqz p1, :cond_0

    .line 102
    iget-object v0, p1, Laenu/aps3e/Emulator$MetaInfo;->eboot_path:Ljava/lang/String;

    if-eqz v0, :cond_0

    new-instance v0, Ljava/io/File;

    iget-object v2, p1, Laenu/aps3e/Emulator$MetaInfo;->eboot_path:Ljava/lang/String;

    invoke-direct {v0, v2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->isFile()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 104
    invoke-static {p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->validateMetadata(Laenu/aps3e/Emulator$MetaInfo;)V

    .line 105
    iput-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->gameConfigured:Z

    .line 106
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    iget-object v2, p1, Laenu/aps3e/Emulator$MetaInfo;->eboot_path:Ljava/lang/String;

    invoke-virtual {v0, v2}, Laenu/aps3e/Emulator;->setup_game_path(Ljava/lang/String;)V

    goto/16 :goto_2

    .line 103
    :cond_0
    new-instance p1, Ljava/io/IOException;

    const-string v0, "A pasta n\u00e3o cont\u00e9m um execut\u00e1vel PS3 v\u00e1lido"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 108
    :cond_1
    const-string v2, "game_uri"

    invoke-virtual {p1, v2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    if-nez v2, :cond_2

    .line 109
    invoke-virtual {p1}, Landroid/content/Intent;->getData()Landroid/net/Uri;

    move-result-object v2

    goto :goto_0

    :cond_2
    invoke-static {v2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v2

    :goto_0
    if-nez v2, :cond_3

    if-eqz v0, :cond_3

    .line 110
    new-instance v2, Ljava/io/File;

    invoke-direct {v2, v0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v0

    invoke-static {v0}, Landroid/net/Uri;->fromFile(Ljava/io/File;)Landroid/net/Uri;

    move-result-object v2

    :cond_3
    if-eqz v2, :cond_8

    .line 111
    const-string v0, "content"

    invoke-virtual {v2}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_4

    const-string v0, "file"

    invoke-virtual {v2}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_8

    .line 113
    :cond_4
    const-string v0, "decryption_key_uri"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-nez p1, :cond_5

    const/4 p1, 0x0

    goto :goto_1

    .line 114
    :cond_5
    invoke-static {p1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object p1

    .line 115
    :goto_1
    invoke-direct {p0, v2, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->detachPair(Landroid/net/Uri;Landroid/net/Uri;)[I

    move-result-object v0

    .line 117
    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v3, v3, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    const/4 v4, 0x0

    aget v5, v0, v4

    aget v0, v0, v1

    invoke-virtual {v2}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v3, v5, v0, v6}, Laenu/aps3e/Emulator;->meta_info_from_iso(IILjava/lang/String;)Laenu/aps3e/Emulator$MetaInfo;

    move-result-object v0

    .line 118
    invoke-static {v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->validateMetadata(Laenu/aps3e/Emulator$MetaInfo;)V

    .line 119
    iget-boolean v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v3, :cond_6

    return-void

    .line 120
    :cond_6
    invoke-direct {p0, v2, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->detachPair(Landroid/net/Uri;Landroid/net/Uri;)[I

    move-result-object p1

    .line 121
    iput-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->gameConfigured:Z

    .line 122
    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v3, v3, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {v2}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v2

    aget v4, p1, v4

    aget p1, p1, v1

    invoke-static {v2, v4, p1}, Laenu/emulator/Emulator$Path;->from(Ljava/lang/String;II)Laenu/emulator/Emulator$Path;

    move-result-object p1

    invoke-virtual {v3, p1}, Laenu/aps3e/Emulator;->setup_game_path(Laenu/emulator/Emulator$Path;)V

    move-object p1, v0

    .line 124
    :goto_2
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    iget-object v2, p1, Laenu/aps3e/Emulator$MetaInfo;->serial:Ljava/lang/String;

    invoke-virtual {v0, v2}, Laenu/aps3e/Emulator;->setup_game_id(Ljava/lang/String;)V

    .line 125
    new-instance v0, Ljava/io/File;

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v2, v2, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->userDirectory:Ljava/io/File;

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v4, "config/custom_cfg/"

    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-object p1, p1, Laenu/aps3e/Emulator$MetaInfo;->serial:Ljava/lang/String;

    invoke-virtual {v3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p1, ".yml"

    invoke-virtual {v3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {v0, v2, p1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 126
    invoke-virtual {v0}, Ljava/io/File;->isFile()Z

    move-result p1

    if-eqz p1, :cond_7

    const-string p1, "APS3E_CUSTOM_CONFIG_YAML_PATH"

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    invoke-static {p1, v0, v1}, Laenu/lang/System;->setenv(Ljava/lang/String;Ljava/lang/String;Z)V

    :cond_7
    return-void

    .line 112
    :cond_8
    new-instance p1, Ljava/io/IOException;

    const-string v0, "Selecione um ISO PS3 local"

    invoke-direct {p1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method private saveSettingsEntry(Ljava/lang/String;Ljava/lang/String;)V
    .locals 2

    .line 435
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x1

    .line 436
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    .line 437
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsMessage:Landroid/widget/TextView;

    const-string v1, "Salvando configura\u00e7\u00e3o\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 438
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda29;

    invoke-direct {v0, p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda29;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Ljava/lang/String;Ljava/lang/String;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private selectSettingsCategory(I)V
    .locals 4

    .line 364
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    if-nez v0, :cond_0

    goto :goto_0

    .line 365
    :cond_0
    iput p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsCategory:I

    iget v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsEpoch:I

    add-int/lit8 v1, v1, 0x1

    iput v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsEpoch:I

    .line 366
    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    const-string v2, "Lendo configura\u00e7\u00e3o\u2026"

    const/16 v3, 0xd

    invoke-direct {p0, v2, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->text(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v2

    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 367
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda5;

    invoke-direct {v0, p0, p1, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda5;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;II)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private settingsBackground(II)Landroid/graphics/drawable/GradientDrawable;
    .locals 1

    .line 287
    new-instance v0, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v0}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    .line 288
    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result p1

    int-to-float p1, p1

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    return-object v0
.end method

.method private settingsButton(Ljava/lang/String;Z)Landroid/widget/Button;
    .locals 3

    .line 291
    new-instance v0, Landroid/widget/Button;

    invoke-direct {v0, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 p1, 0x0

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setAllCaps(Z)V

    const/high16 v1, 0x41500000    # 13.0f

    .line 292
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextSize(F)V

    if-eqz p2, :cond_0

    const v1, -0xf9eae3

    goto :goto_0

    :cond_0
    const v1, -0x161107

    :goto_0
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextColor(I)V

    .line 293
    sget-object v1, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    const/4 v2, 0x1

    invoke-virtual {v0, v1, v2}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;I)V

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setMinHeight(I)V

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setMinimumHeight(I)V

    const/16 v1, 0xc

    .line 294
    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v2

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v1

    invoke-virtual {v0, v2, p1, v1, p1}, Landroid/widget/Button;->setPadding(IIII)V

    if-eqz p2, :cond_1

    const p1, -0xaa2d12

    goto :goto_1

    :cond_1
    const p1, -0xe7d9ce

    :goto_1
    const/4 p2, 0x7

    .line 295
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBackground(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object p1

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setBackground(Landroid/graphics/drawable/Drawable;)V

    return-object v0
.end method

.method private settingsDp(I)I
    .locals 1

    int-to-float p1, p1

    .line 284
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr p1, v0

    invoke-static {p1}, Ljava/lang/Math;->round(F)I

    move-result p1

    return p1
.end method

.method private showGame()V
    .locals 4

    .line 148
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_1

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->isFinishing()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    .line 149
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v0}, Landroid/widget/FrameLayout;->removeAllViews()V

    .line 150
    new-instance v0, Landroid/view/SurfaceView;

    invoke-direct {v0, p0}, Landroid/view/SurfaceView;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->surface:Landroid/view/SurfaceView;

    invoke-virtual {v0}, Landroid/view/SurfaceView;->getHolder()Landroid/view/SurfaceHolder;

    move-result-object v0

    invoke-interface {v0, p0}, Landroid/view/SurfaceHolder;->addCallback(Landroid/view/SurfaceHolder$Callback;)V

    .line 151
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->surface:Landroid/view/SurfaceView;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v3, -0x1

    invoke-direct {v2, v3, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 152
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3TouchControls;

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-direct {v0, p0, v1}, Lorg/emulationstation/frontend/sony/Ps3TouchControls;-><init>(Landroid/content/Context;Lorg/emulationstation/frontend/sony/Ps3Input;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->controls:Lorg/emulationstation/frontend/sony/Ps3TouchControls;

    .line 153
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v2, v3, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 154
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->updateControls()V

    :cond_1
    :goto_0
    return-void
.end method

.method private showProgress(Ljava/lang/String;)V
    .locals 1

    .line 268
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda0;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda0;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method private showSettings()V
    .locals 15

    .line 299
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_2

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->isFinishing()Z

    move-result v0

    if-eqz v0, :cond_0

    goto/16 :goto_1

    :cond_0
    const/4 v0, 0x0

    .line 300
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v1}, Landroid/widget/FrameLayout;->removeAllViews()V

    .line 301
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    const v2, -0xd7814b

    invoke-virtual {v1, v2}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    .line 302
    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const/16 v3, 0x10

    .line 303
    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v4

    const/16 v5, 0xa

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v6

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v7

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v8

    invoke-virtual {v1, v4, v6, v7, v8}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 304
    iget-object v4, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    new-instance v6, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v7, -0x1

    invoke-direct {v6, v7, v7}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v4, v1, v6}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 305
    new-instance v4, Landroid/widget/LinearLayout;

    invoke-direct {v4, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    invoke-virtual {v4, v3}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 306
    const-string v3, "\u2039  Voltar"

    invoke-direct {p0, v3, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsButton(Ljava/lang/String;Z)Landroid/widget/Button;

    move-result-object v3

    new-instance v6, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda23;

    invoke-direct {v6, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda23;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {v3, v6}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 307
    new-instance v6, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v8, 0x5e

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v8

    const/16 v9, 0x26

    invoke-direct {p0, v9}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v9

    invoke-direct {v6, v8, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v4, v3, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 308
    const-string v3, "PS3  /  Configura\u00e7\u00f5es"

    const/16 v6, 0x13

    invoke-direct {p0, v3, v6}, Lorg/emulationstation/frontend/sony/Ps3Activity;->text(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v3

    sget-object v8, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-virtual {v3, v8, v2}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;I)V

    const/16 v8, 0xe

    .line 309
    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v8

    invoke-virtual {v3, v8, v0, v0, v0}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v8, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v9, -0x2

    const/high16 v10, 0x3f800000    # 1.0f

    invoke-direct {v8, v0, v9, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v4, v3, v8}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 310
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v8, 0x2c

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v8

    invoke-direct {v3, v7, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v4, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 311
    const-string v3, "Op\u00e7\u00f5es do motor \u00b7 altera\u00e7\u00f5es valem no pr\u00f3ximo jogo"

    const/16 v4, 0xc

    invoke-direct {p0, v3, v4}, Lorg/emulationstation/frontend/sony/Ps3Activity;->text(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object v3

    iput-object v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsMessage:Landroid/widget/TextView;

    const v8, -0x6c5746

    .line 312
    invoke-virtual {v3, v8}, Landroid/widget/TextView;->setTextColor(I)V

    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsMessage:Landroid/widget/TextView;

    const/4 v8, 0x3

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v8

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v5

    invoke-virtual {v3, v0, v8, v0, v5}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 313
    iget-object v3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsMessage:Landroid/widget/TextView;

    invoke-virtual {v1, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 314
    new-instance v3, Landroid/widget/LinearLayout;

    invoke-direct {v3, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    invoke-virtual {v3, v0}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 315
    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v5, v7, v0, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v1, v3, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 316
    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 317
    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v8, 0x8c

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v8

    invoke-direct {v5, v8, v7}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v3, v1, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 318
    const-string v5, "Processamento"

    const-string v8, "Sistema"

    const-string v11, "Imagem"

    const-string v12, "\u00c1udio"

    filled-new-array {v11, v12, v5, v8}, [Ljava/lang/String;

    move-result-object v5

    move v8, v0

    :goto_0
    const/4 v11, 0x4

    if-ge v8, v11, :cond_1

    .line 320
    aget-object v11, v5, v8

    invoke-direct {p0, v11, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsButton(Ljava/lang/String;Z)Landroid/widget/Button;

    move-result-object v11

    .line 321
    invoke-virtual {v11, v6}, Landroid/widget/Button;->setGravity(I)V

    .line 322
    new-instance v12, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda24;

    invoke-direct {v12, p0, v8}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda24;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;I)V

    invoke-virtual {v11, v12}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 323
    new-instance v12, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v13, 0x27

    invoke-direct {p0, v13}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v13

    invoke-direct {v12, v7, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 324
    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v13

    const/4 v14, 0x7

    invoke-direct {p0, v14}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v14

    invoke-virtual {v12, v0, v0, v13, v14}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {v1, v11, v12}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    add-int/lit8 v8, v8, 0x1

    goto :goto_0

    .line 326
    :cond_1
    new-instance v1, Landroid/widget/ScrollView;

    invoke-direct {v1, p0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v1, v0}, Landroid/widget/ScrollView;->setFillViewport(Z)V

    invoke-virtual {v1, v0}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    .line 327
    new-instance v4, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v4, v0, v7, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v3, v1, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 328
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    invoke-virtual {v0, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 329
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v2, v7, v9}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v2}, Landroid/widget/ScrollView;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 330
    iget v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsCategory:I

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->selectSettingsCategory(I)V

    :cond_2
    :goto_1
    return-void
.end method

.method private text(Ljava/lang/String;I)Landroid/widget/TextView;
    .locals 1

    .line 281
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    int-to-float p1, p2

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextSize(F)V

    const p1, -0x161107

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextColor(I)V

    return-object v0
.end method

.method private updateControls()V
    .locals 4

    .line 193
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->controls:Lorg/emulationstation/frontend/sony/Ps3TouchControls;

    if-nez v0, :cond_0

    return-void

    .line 194
    :cond_0
    invoke-static {}, Lorg/emulationstation/frontend/sony/Ps3Input;->physicalControllerPresent()Z

    move-result v0

    const/4 v1, 0x0

    if-nez v0, :cond_1

    invoke-virtual {p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v2, "touch"

    const/4 v3, 0x1

    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0

    if-eqz v0, :cond_1

    goto :goto_0

    :cond_1
    move v3, v1

    :goto_0
    if-nez v3, :cond_2

    .line 195
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->controls:Lorg/emulationstation/frontend/sony/Ps3TouchControls;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps3TouchControls;->release()V

    :cond_2
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->controls:Lorg/emulationstation/frontend/sony/Ps3TouchControls;

    if-eqz v3, :cond_3

    goto :goto_1

    :cond_3
    const/16 v1, 0x8

    :goto_1
    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/sony/Ps3TouchControls;->setVisibility(I)V

    return-void
.end method

.method private static validateMetadata(Laenu/aps3e/Emulator$MetaInfo;)V
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/io/IOException;
        }
    .end annotation

    if-eqz p0, :cond_0

    .line 129
    iget-object v0, p0, Laenu/aps3e/Emulator$MetaInfo;->serial:Ljava/lang/String;

    if-eqz v0, :cond_0

    iget-object p0, p0, Laenu/aps3e/Emulator$MetaInfo;->serial:Ljava/lang/String;

    const-string v0, "[A-Za-z0-9_-]{1,32}"

    invoke-virtual {p0, v0}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result p0

    if-eqz p0, :cond_0

    return-void

    .line 130
    :cond_0
    new-instance p0, Ljava/io/IOException;

    const-string v0, "N\u00e3o foi poss\u00edvel ler o jogo PS3. ISO criptografado exige a chave do pr\u00f3prio jogo"

    invoke-direct {p0, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p0
.end method


# virtual methods
.method public dispatchKeyEvent(Landroid/view/KeyEvent;)Z
    .locals 1

    .line 180
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz v0, :cond_0

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->exitDialog:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/sony/Ps3Input;->key(Landroid/view/KeyEvent;)Z

    move-result v0

    if-eqz v0, :cond_0

    const/4 p1, 0x1

    return p1

    .line 181
    :cond_0
    invoke-super {p0, p1}, Landroid/app/Activity;->dispatchKeyEvent(Landroid/view/KeyEvent;)Z

    move-result p1

    return p1
.end method

.method synthetic lambda$activateSurface$5$org-emulationstation-frontend-sony-Ps3Activity(Landroid/view/SurfaceHolder;)V
    .locals 1

    .line 162
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_2

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->resumed:Z

    if-eqz v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    if-eqz v0, :cond_2

    invoke-interface {p1}, Landroid/view/SurfaceHolder;->getSurface()Landroid/view/Surface;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Surface;->isValid()Z

    move-result v0

    if-nez v0, :cond_0

    goto :goto_0

    .line 164
    :cond_0
    :try_start_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-interface {p1}, Landroid/view/SurfaceHolder;->getSurface()Landroid/view/Surface;

    move-result-object p1

    invoke-virtual {v0, p1}, Laenu/aps3e/Emulator;->setup_surface(Landroid/view/Surface;)V

    .line 165
    iget-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-nez p1, :cond_1

    const/4 p1, 0x1

    iput-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {p1}, Laenu/aps3e/Emulator;->boot()V

    goto :goto_0

    .line 166
    :cond_1
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {p1}, Laenu/aps3e/Emulator;->is_paused()Z

    move-result p1

    if-eqz p1, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {p1}, Laenu/aps3e/Emulator;->resume()V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception p1

    .line 167
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->failure(Ljava/lang/Throwable;)V

    :cond_2
    :goto_0
    return-void
.end method

.method synthetic lambda$addSetting$24$org-emulationstation-frontend-sony-Ps3Activity(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Landroid/content/DialogInterface;I)V
    .locals 1

    .line 396
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez v0, :cond_0

    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->tag:Ljava/lang/String;

    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->values:[Ljava/lang/String;

    aget-object p1, p1, p3

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->saveSettingsEntry(Ljava/lang/String;Ljava/lang/String;)V

    :cond_0
    invoke-interface {p2}, Landroid/content/DialogInterface;->dismiss()V

    return-void
.end method

.method synthetic lambda$addSetting$25$org-emulationstation-frontend-sony-Ps3Activity(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;Landroid/view/View;)V
    .locals 2

    .line 388
    iget-boolean p3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez p3, :cond_6

    iget-boolean p3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    if-eqz p3, :cond_0

    goto :goto_1

    .line 389
    :cond_0
    iget p3, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->kind:I

    const/4 v0, 0x3

    const/4 v1, 0x1

    if-ne p3, v0, :cond_2

    .line 390
    const-string p3, "true"

    invoke-virtual {p3, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p3

    if-nez p3, :cond_1

    const-string p3, "false"

    invoke-virtual {p3, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p3

    if-nez p3, :cond_1

    return-void

    .line 391
    :cond_1
    iget-object p1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->tag:Ljava/lang/String;

    invoke-static {p2}, Ljava/lang/Boolean;->parseBoolean(Ljava/lang/String;)Z

    move-result p2

    xor-int/2addr p2, v1

    invoke-static {p2}, Ljava/lang/Boolean;->toString(Z)Ljava/lang/String;

    move-result-object p2

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->saveSettingsEntry(Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_1

    .line 392
    :cond_2
    iget p3, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->kind:I

    if-ne p3, v1, :cond_5

    const/4 p3, -0x1

    const/4 v0, 0x0

    .line 393
    :goto_0
    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->values:[Ljava/lang/String;

    array-length v1, v1

    if-ge v0, v1, :cond_4

    iget-object v1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->values:[Ljava/lang/String;

    aget-object v1, v1, v0

    invoke-virtual {v1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_3

    move p3, v0

    :cond_3
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 394
    :cond_4
    new-instance p2, Landroid/app/AlertDialog$Builder;

    invoke-direct {p2, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->label:Ljava/lang/String;

    invoke-virtual {p2, v0}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p2

    iget-object v0, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->values:[Ljava/lang/String;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda19;

    invoke-direct {v1, p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda19;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;)V

    .line 395
    invoke-virtual {p2, v0, p3, v1}, Landroid/app/AlertDialog$Builder;->setSingleChoiceItems([Ljava/lang/CharSequence;ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    const-string p2, "Cancelar"

    const/4 p3, 0x0

    .line 397
    invoke-virtual {p1, p2, p3}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    invoke-virtual {p1}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    goto :goto_1

    .line 398
    :cond_5
    iget p3, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->kind:I

    const/4 v0, 0x2

    if-ne p3, v0, :cond_6

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->editSettingsNumber(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)V

    :cond_6
    :goto_1
    return-void
.end method

.method synthetic lambda$addTouchSetting$27$org-emulationstation-frontend-sony-Ps3Activity(ZLandroid/view/View;)V
    .locals 1

    .line 429
    iget-boolean p2, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez p2, :cond_1

    iget-boolean p2, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    if-eqz p2, :cond_0

    goto :goto_0

    :cond_0
    const/4 p2, 0x0

    .line 430
    invoke-virtual {p0, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object p2

    invoke-interface {p2}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object p2

    xor-int/lit8 p1, p1, 0x1

    const-string v0, "touch"

    invoke-interface {p2, v0, p1}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object p1

    invoke-interface {p1}, Landroid/content/SharedPreferences$Editor;->apply()V

    iget p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsCategory:I

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->selectSettingsCategory(I)V

    :cond_1
    :goto_0
    return-void
.end method

.method synthetic lambda$editSettingsNumber$26$org-emulationstation-frontend-sony-Ps3Activity(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Landroid/widget/SeekBar;Landroid/content/DialogInterface;I)V
    .locals 0

    .line 421
    iget-boolean p3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez p3, :cond_0

    iget-boolean p3, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    if-nez p3, :cond_0

    iget-object p3, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->tag:Ljava/lang/String;

    invoke-virtual {p2}, Landroid/widget/SeekBar;->getProgress()I

    move-result p2

    iget p1, p1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->minimum:I

    add-int/2addr p2, p1

    invoke-static {p2}, Ljava/lang/Integer;->toString(I)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p3, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->saveSettingsEntry(Ljava/lang/String;Ljava/lang/String;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$execute$15$org-emulationstation-frontend-sony-Ps3Activity(Ljava/lang/Runnable;)V
    .locals 1

    .line 261
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    invoke-interface {p1}, Ljava/lang/Runnable;->run()V

    :cond_0
    return-void
.end method

.method synthetic lambda$failure$17$org-emulationstation-frontend-sony-Ps3Activity(Landroid/content/DialogInterface;I)V
    .locals 0

    .line 276
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    return-void
.end method

.method synthetic lambda$failure$18$org-emulationstation-frontend-sony-Ps3Activity(Landroid/content/DialogInterface;)V
    .locals 0

    .line 277
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    return-void
.end method

.method synthetic lambda$failure$19$org-emulationstation-frontend-sony-Ps3Activity(Ljava/lang/Throwable;)V
    .locals 2

    .line 272
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_2

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->isFinishing()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    .line 273
    :cond_0
    invoke-virtual {p1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object p1

    .line 274
    new-instance v0, Landroid/app/AlertDialog$Builder;

    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string v1, "PS3"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    if-nez p1, :cond_1

    .line 275
    const-string p1, "N\u00e3o foi poss\u00edvel preparar o motor PS3."

    :cond_1
    invoke-virtual {v0, p1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda27;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda27;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    .line 276
    const-string v1, "Voltar"

    invoke-virtual {p1, v1, v0}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda28;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda28;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    .line 277
    invoke-virtual {p1, v0}, Landroid/app/AlertDialog$Builder;->setOnCancelListener(Landroid/content/DialogInterface$OnCancelListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    invoke-virtual {p1}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    :cond_2
    :goto_0
    return-void
.end method

.method synthetic lambda$leaveSettings$31$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 455
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_0

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    :cond_0
    return-void
.end method

.method synthetic lambda$leaveSettings$32$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 455
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda33;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda33;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method synthetic lambda$onBackPressed$10$org-emulationstation-frontend-sony-Ps3Activity(Landroid/content/DialogInterface;I)V
    .locals 0

    .line 213
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    return-void
.end method

.method synthetic lambda$onBackPressed$11$org-emulationstation-frontend-sony-Ps3Activity(Landroid/content/DialogInterface;)V
    .locals 0

    .line 0
    const/4 p1, 0x0

    .line 214
    iput-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->exitDialog:Z

    return-void
.end method

.method synthetic lambda$onBackPressed$9$org-emulationstation-frontend-sony-Ps3Activity(Landroid/content/DialogInterface;I)V
    .locals 0

    .line 0
    const/4 p1, 0x0

    .line 212
    iput-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->exitDialog:Z

    return-void
.end method

.method synthetic lambda$onCreate$1$org-emulationstation-frontend-sony-Ps3Activity(Landroid/view/View;)V
    .locals 0

    .line 73
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    return-void
.end method

.method synthetic lambda$onCreate$2$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 84
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->showSettings()V

    const/4 v0, 0x0

    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->requestInFlight:Z

    return-void
.end method

.method synthetic lambda$onCreate$3$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 85
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    const/4 v0, -0x1

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->setResult(I)V

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    :cond_0
    return-void
.end method

.method synthetic lambda$onCreate$4$org-emulationstation-frontend-sony-Ps3Activity(Ljava/lang/String;Landroid/content/Intent;)V
    .locals 2

    .line 79
    :try_start_0
    invoke-static {p0}, Lorg/emulationstation/frontend/sony/Ps3Bootstrap;->prepare(Landroid/content/Context;)Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    .line 80
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v0, :cond_0

    return-void

    .line 81
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda13;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda13;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-static {v0, v1}, Lorg/emulationstation/frontend/sony/Ps3Firmware;->ensure(Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;Lorg/emulationstation/frontend/sony/Ps3Firmware$Progress;)V

    .line 82
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v0, :cond_1

    return-void

    :cond_1
    const/4 v0, 0x1

    .line 83
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->prepared:Z

    .line 84
    const-string v0, "settings"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda21;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda21;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void

    .line 85
    :cond_2
    const-string v0, "prepare"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda22;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda22;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void

    .line 86
    :cond_3
    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->prepareGame(Landroid/content/Intent;)V

    .line 87
    iget-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz p1, :cond_4

    return-void

    .line 88
    :cond_4
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Input;

    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object p2, p2, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/sony/Ps3Input;-><init>(Laenu/aps3e/Emulator;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    .line 89
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda15;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda15;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception p1

    .line 90
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->failure(Ljava/lang/Throwable;)V

    :goto_0
    return-void
.end method

.method synthetic lambda$onDestroy$14$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 2

    .line 243
    :try_start_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    if-eqz v0, :cond_0

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {v0}, Laenu/aps3e/Emulator;->quit()V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 245
    :cond_0
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->gameConfigured:Z

    if-eqz v0, :cond_2

    .line 246
    :cond_1
    invoke-static {}, Lorg/emulationstation/frontend/sony/Ps3Bootstrap;->requireProcess()V

    .line 248
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v0

    invoke-static {v0}, Landroid/os/Process;->killProcess(I)V

    :cond_2
    return-void

    :catchall_0
    move-exception v0

    .line 245
    iget-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-nez v1, :cond_3

    iget-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->gameConfigured:Z

    if-eqz v1, :cond_4

    .line 246
    :cond_3
    invoke-static {}, Lorg/emulationstation/frontend/sony/Ps3Bootstrap;->requireProcess()V

    .line 248
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v1

    invoke-static {v1}, Landroid/os/Process;->killProcess(I)V

    .line 250
    :cond_4
    throw v0
.end method

.method synthetic lambda$onNewIntent$12$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 229
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    const/4 v0, -0x1

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->setResult(I)V

    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    :cond_0
    return-void
.end method

.method synthetic lambda$onNewIntent$13$org-emulationstation-frontend-sony-Ps3Activity(Landroid/content/Intent;)V
    .locals 2

    .line 226
    :try_start_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda13;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda13;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-static {v0, v1}, Lorg/emulationstation/frontend/sony/Ps3Firmware;->ensure(Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;Lorg/emulationstation/frontend/sony/Ps3Firmware$Progress;)V

    .line 227
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v0, :cond_0

    return-void

    .line 228
    :cond_0
    const-string v0, "prepare"

    const-string v1, "operation"

    invoke-virtual {p1, v1}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 229
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda14;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda14;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void

    .line 231
    :cond_1
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->prepareGame(Landroid/content/Intent;)V

    iget-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz p1, :cond_2

    return-void

    .line 232
    :cond_2
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Input;

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-direct {p1, v0}, Lorg/emulationstation/frontend/sony/Ps3Input;-><init>(Laenu/aps3e/Emulator;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda15;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda15;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception p1

    .line 233
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->failure(Ljava/lang/Throwable;)V

    :goto_0
    return-void
.end method

.method synthetic lambda$onPause$8$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 200
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {v0}, Laenu/aps3e/Emulator;->pause()V

    :cond_0
    return-void
.end method

.method synthetic lambda$saveSettingsEntry$28$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 2

    .line 0
    const/4 v0, 0x0

    .line 444
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    .line 445
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-eqz v0, :cond_0

    goto :goto_0

    .line 446
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsMessage:Landroid/widget/TextView;

    const-string v1, "Salvo \u00b7 altera\u00e7\u00f5es valem no pr\u00f3ximo jogo"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsCategory:I

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->selectSettingsCategory(I)V

    :cond_1
    :goto_0
    return-void
.end method

.method synthetic lambda$saveSettingsEntry$29$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 1

    .line 0
    const/4 v0, 0x0

    .line 448
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsSaving:Z

    return-void
.end method

.method synthetic lambda$saveSettingsEntry$30$org-emulationstation-frontend-sony-Ps3Activity(Ljava/lang/String;Ljava/lang/String;)V
    .locals 2

    .line 439
    :try_start_0
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->configFile:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Laenu/emulator/Emulator$Config;->openFile(Ljava/lang/String;)Laenu/emulator/Emulator$Config;

    move-result-object v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    .line 440
    :try_start_1
    invoke-virtual {v0, p1, p2}, Laenu/emulator/Emulator$Config;->save(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v0}, Laenu/emulator/Emulator$Config;->closeText()Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_0

    .line 441
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result p2

    if-eqz p2, :cond_0

    .line 442
    iget-object p2, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object p2, p2, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->configFile:Ljava/io/File;

    sget-object v1, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {p1, v1}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object p1

    invoke-static {p2, p1}, Lorg/emulationstation/frontend/sony/Ps3Bootstrap;->writeAtomic(Ljava/io/File;[B)V

    .line 443
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda6;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda6;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    if-eqz v0, :cond_2

    .line 448
    :try_start_2
    invoke-virtual {v0}, Laenu/emulator/Emulator$Config;->close()V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    goto :goto_1

    .line 441
    :cond_0
    :try_start_3
    new-instance p1, Ljava/io/IOException;

    const-string p2, "O motor n\u00e3o retornou a configura\u00e7\u00e3o"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    :catchall_0
    move-exception p1

    if-eqz v0, :cond_1

    .line 439
    :try_start_4
    invoke-virtual {v0}, Laenu/emulator/Emulator$Config;->close()V
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_1

    goto :goto_0

    :catchall_1
    move-exception p2

    :try_start_5
    invoke-virtual {p1, p2}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :cond_1
    :goto_0
    throw p1
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_2

    :catchall_2
    move-exception p1

    .line 448
    new-instance p2, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda7;

    invoke-direct {p2, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda7;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {p0, p2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->failure(Ljava/lang/Throwable;)V

    :cond_2
    :goto_1
    return-void
.end method

.method synthetic lambda$selectSettingsCategory$22$org-emulationstation-frontend-sony-Ps3Activity(II[Ljava/lang/String;)V
    .locals 2

    .line 372
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsLeaving:Z

    if-nez v0, :cond_3

    iget v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsEpoch:I

    if-ne p1, v0, :cond_3

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    if-nez p1, :cond_0

    goto :goto_1

    .line 373
    :cond_0
    invoke-virtual {p1}, Landroid/widget/LinearLayout;->removeAllViews()V

    const/4 p1, 0x0

    .line 374
    :goto_0
    sget-object v0, Lorg/emulationstation/frontend/sony/Ps3Activity;->SETTINGS:[Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    array-length v1, v0

    if-ge p1, v1, :cond_2

    aget-object v1, v0, p1

    iget v1, v1, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->category:I

    if-ne v1, p2, :cond_1

    aget-object v0, v0, p1

    aget-object v1, p3, p1

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->addSetting(Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;Ljava/lang/String;)V

    :cond_1
    add-int/lit8 p1, p1, 0x1

    goto :goto_0

    :cond_2
    const/4 p1, 0x3

    if-ne p2, p1, :cond_3

    .line 375
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->addTouchSetting()V

    :cond_3
    :goto_1
    return-void
.end method

.method synthetic lambda$selectSettingsCategory$23$org-emulationstation-frontend-sony-Ps3Activity(II)V
    .locals 5

    .line 368
    sget-object v0, Lorg/emulationstation/frontend/sony/Ps3Activity;->SETTINGS:[Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    array-length v0, v0

    new-array v0, v0, [Ljava/lang/String;

    .line 369
    :try_start_0
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v1, v1, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->configFile:Ljava/io/File;

    invoke-virtual {v1}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Laenu/emulator/Emulator$Config;->openFile(Ljava/lang/String;)Laenu/emulator/Emulator$Config;

    move-result-object v1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    const/4 v2, 0x0

    .line 370
    :goto_0
    :try_start_1
    sget-object v3, Lorg/emulationstation/frontend/sony/Ps3Activity;->SETTINGS:[Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;

    array-length v4, v3

    if-ge v2, v4, :cond_1

    aget-object v4, v3, v2

    iget v4, v4, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->category:I

    if-ne v4, p1, :cond_0

    aget-object v3, v3, v2

    iget-object v3, v3, Lorg/emulationstation/frontend/sony/Ps3Activity$Setting;->tag:Ljava/lang/String;

    invoke-virtual {v1, v3}, Laenu/emulator/Emulator$Config;->load(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    aput-object v3, v0, v2

    :cond_0
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    .line 371
    :cond_1
    new-instance v2, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda4;

    invoke-direct {v2, p0, p2, p1, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda4;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;II[Ljava/lang/String;)V

    invoke-virtual {p0, v2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    if-eqz v1, :cond_3

    .line 377
    :try_start_2
    invoke-virtual {v1}, Laenu/emulator/Emulator$Config;->close()V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    goto :goto_2

    :catchall_0
    move-exception p1

    if-eqz v1, :cond_2

    .line 369
    :try_start_3
    invoke-virtual {v1}, Laenu/emulator/Emulator$Config;->close()V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    goto :goto_1

    :catchall_1
    move-exception p2

    :try_start_4
    invoke-virtual {p1, p2}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :cond_2
    :goto_1
    throw p1
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_2

    :catchall_2
    move-exception p1

    .line 377
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->failure(Ljava/lang/Throwable;)V

    :cond_3
    :goto_2
    return-void
.end method

.method synthetic lambda$showProgress$16$org-emulationstation-frontend-sony-Ps3Activity(Ljava/lang/String;)V
    .locals 1

    .line 268
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->progress:Landroid/widget/TextView;

    if-eqz v0, :cond_0

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$showSettings$20$org-emulationstation-frontend-sony-Ps3Activity(Landroid/view/View;)V
    .locals 0

    .line 306
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->leaveSettings()V

    return-void
.end method

.method synthetic lambda$showSettings$21$org-emulationstation-frontend-sony-Ps3Activity(ILandroid/view/View;)V
    .locals 0

    .line 322
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->selectSettingsCategory(I)V

    return-void
.end method

.method synthetic lambda$surfaceChanged$6$org-emulationstation-frontend-sony-Ps3Activity(II)V
    .locals 1

    .line 172
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {v0, p1, p2}, Laenu/aps3e/Emulator;->change_surface(II)V

    :cond_0
    return-void
.end method

.method synthetic lambda$surfaceDestroyed$7$org-emulationstation-frontend-sony-Ps3Activity()V
    .locals 2

    .line 177
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    invoke-virtual {v0}, Laenu/aps3e/Emulator;->pause()V

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    iget-object v0, v0, Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;->emulator:Laenu/aps3e/Emulator;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Laenu/aps3e/Emulator;->setup_surface(Landroid/view/Surface;)V

    :cond_0
    return-void
.end method

.method public onBackPressed()V
    .locals 3

    .line 208
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsBody:Landroid/widget/LinearLayout;

    if-eqz v0, :cond_0

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->leaveSettings()V

    goto :goto_0

    :cond_0
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->finish()V

    :goto_0
    return-void

    .line 209
    :cond_1
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->exitDialog:Z

    if-eqz v0, :cond_2

    return-void

    :cond_2
    const/4 v0, 0x1

    .line 210
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->exitDialog:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz v0, :cond_3

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps3Input;->releaseAll()V

    .line 211
    :cond_3
    new-instance v0, Landroid/app/AlertDialog$Builder;

    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string v1, "Sair do jogo?"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "Voltar \u00e0 TurboStations."

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda30;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda30;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    .line 212
    const-string v2, "Continuar"

    invoke-virtual {v0, v2, v1}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda31;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda31;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    .line 213
    const-string v2, "Sair"

    invoke-virtual {v0, v2, v1}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda32;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda32;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    .line 214
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setOnCancelListener(Landroid/content/DialogInterface$OnCancelListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .locals 7

    .line 60
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    invoke-static {}, Lorg/emulationstation/frontend/sony/Ps3Bootstrap;->requireProcess()V

    .line 61
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getWindow()Landroid/view/Window;

    move-result-object p1

    const/16 v0, 0x80

    invoke-virtual {p1, v0}, Landroid/view/Window;->addFlags(I)V

    .line 62
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object p1

    const/16 v0, 0x1006

    invoke-virtual {p1, v0}, Landroid/view/View;->setSystemUiVisibility(I)V

    .line 64
    new-instance p1, Landroid/widget/FrameLayout;

    invoke-direct {p1, p0}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    const/high16 v0, -0x1000000

    invoke-virtual {p1, v0}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->setContentView(Landroid/view/View;)V

    .line 65
    const-string p1, "Preparando PS3\u2026"

    const/16 v0, 0x12

    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->text(Ljava/lang/String;I)Landroid/widget/TextView;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->progress:Landroid/widget/TextView;

    const/16 v0, 0x11

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setGravity(I)V

    .line 66
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->progress:Landroid/widget/TextView;

    new-instance v1, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v2, -0x1

    invoke-direct {v1, v2, v2}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 67
    const-string p1, "input"

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Landroid/hardware/input/InputManager;

    iput-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->inputManager:Landroid/hardware/input/InputManager;

    if-eqz p1, :cond_0

    const/4 v0, 0x0

    .line 68
    invoke-virtual {p1, p0, v0}, Landroid/hardware/input/InputManager;->registerInputDeviceListener(Landroid/hardware/input/InputManager$InputDeviceListener;Landroid/os/Handler;)V

    .line 69
    :cond_0
    invoke-virtual {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->getIntent()Landroid/content/Intent;

    move-result-object p1

    .line 70
    const-string v0, "operation"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 71
    const-string v1, "settings"

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_1

    .line 72
    const-string v1, "\u2039  Voltar"

    const/4 v2, 0x0

    invoke-direct {p0, v1, v2}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsButton(Ljava/lang/String;Z)Landroid/widget/Button;

    move-result-object v1

    .line 73
    new-instance v3, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda11;

    invoke-direct {v3, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda11;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-virtual {v1, v3}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 74
    new-instance v3, Landroid/widget/FrameLayout$LayoutParams;

    const/16 v4, 0x5e

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v4

    const/16 v5, 0x26

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v5

    const/16 v6, 0x33

    invoke-direct {v3, v4, v5, v6}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    const/16 v4, 0x10

    .line 75
    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v4

    const/16 v5, 0xa

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/sony/Ps3Activity;->settingsDp(I)I

    move-result v5

    invoke-virtual {v3, v4, v5, v2, v2}, Landroid/widget/FrameLayout$LayoutParams;->setMargins(IIII)V

    iget-object v2, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v2, v1, v3}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 77
    :cond_1
    new-instance v1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda12;

    invoke-direct {v1, p0, v0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda12;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Ljava/lang/String;Landroid/content/Intent;)V

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    return-void
.end method

.method public onDestroy()V
    .locals 3

    .line 237
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->submissions:Ljava/lang/Object;

    monitor-enter v0

    .line 238
    :try_start_0
    iget-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v1, :cond_2

    const/4 v1, 0x1

    .line 239
    iput-boolean v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    .line 240
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->inputManager:Landroid/hardware/input/InputManager;

    if-eqz v1, :cond_0

    invoke-virtual {v1, p0}, Landroid/hardware/input/InputManager;->unregisterInputDeviceListener(Landroid/hardware/input/InputManager$InputDeviceListener;)V

    .line 241
    :cond_0
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz v1, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/sony/Ps3Input;->releaseAll()V

    .line 242
    :cond_1
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->worker:Ljava/util/concurrent/ExecutorService;

    new-instance v2, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda17;

    invoke-direct {v2, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda17;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-interface {v1, v2}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    .line 252
    iget-object v1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->worker:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v1}, Ljava/util/concurrent/ExecutorService;->shutdown()V

    .line 254
    :cond_2
    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 255
    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V

    return-void

    :catchall_0
    move-exception v1

    .line 254
    :try_start_1
    monitor-exit v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    throw v1
.end method

.method public onGenericMotionEvent(Landroid/view/MotionEvent;)Z
    .locals 1

    .line 184
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz v0, :cond_0

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->exitDialog:Z

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/sony/Ps3Input;->motion(Landroid/view/MotionEvent;)Z

    move-result v0

    if-eqz v0, :cond_0

    const/4 p1, 0x1

    return p1

    .line 185
    :cond_0
    invoke-super {p0, p1}, Landroid/app/Activity;->onGenericMotionEvent(Landroid/view/MotionEvent;)Z

    move-result p1

    return p1
.end method

.method public onInputDeviceAdded(I)V
    .locals 0

    .line 187
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->updateControls()V

    return-void
.end method

.method public onInputDeviceChanged(I)V
    .locals 0

    .line 188
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->updateControls()V

    return-void
.end method

.method public onInputDeviceRemoved(I)V
    .locals 0

    .line 190
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/sony/Ps3Input;->releaseAll()V

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->updateControls()V

    return-void
.end method

.method protected onNewIntent(Landroid/content/Intent;)V
    .locals 2

    .line 217
    invoke-super {p0, p1}, Landroid/app/Activity;->onNewIntent(Landroid/content/Intent;)V

    .line 219
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->gameConfigured:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->requestInFlight:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v0, :cond_0

    goto :goto_0

    .line 220
    :cond_0
    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->setIntent(Landroid/content/Intent;)V

    .line 221
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->owner:Lorg/emulationstation/frontend/sony/Ps3Bootstrap$Ready;

    if-eqz v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->prepared:Z

    if-nez v0, :cond_1

    goto :goto_0

    .line 222
    :cond_1
    const-string v0, "operation"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v1, "settings"

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->showSettings()V

    return-void

    :cond_2
    const/4 v0, 0x1

    .line 223
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->requestInFlight:Z

    .line 224
    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda3;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda3;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;Landroid/content/Intent;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    :cond_3
    :goto_0
    return-void
.end method

.method protected onPause()V
    .locals 1

    const/4 v0, 0x0

    .line 198
    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->resumed:Z

    .line 199
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/sony/Ps3Input;->releaseAll()V

    .line 200
    :cond_0
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->started:Z

    if-eqz v0, :cond_1

    new-instance v0, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda10;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda10;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    .line 201
    :cond_1
    invoke-super {p0}, Landroid/app/Activity;->onPause()V

    return-void
.end method

.method protected onResume()V
    .locals 1

    .line 204
    invoke-super {p0}, Landroid/app/Activity;->onResume()V

    const/4 v0, 0x1

    iput-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->resumed:Z

    invoke-direct {p0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->updateControls()V

    .line 205
    iget-object v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->surface:Landroid/view/SurfaceView;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Landroid/view/SurfaceView;->getHolder()Landroid/view/SurfaceHolder;

    move-result-object v0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/sony/Ps3Activity;->activateSurface(Landroid/view/SurfaceHolder;)V

    :cond_0
    return-void
.end method

.method public surfaceChanged(Landroid/view/SurfaceHolder;III)V
    .locals 0

    .line 171
    iget-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-nez p1, :cond_1

    if-lez p3, :cond_1

    if-gtz p4, :cond_0

    goto :goto_0

    .line 172
    :cond_0
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda1;

    invoke-direct {p1, p0, p3, p4}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda1;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;II)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method public surfaceCreated(Landroid/view/SurfaceHolder;)V
    .locals 1

    .line 157
    iget-boolean v0, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz v0, :cond_0

    return-void

    .line 158
    :cond_0
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->activateSurface(Landroid/view/SurfaceHolder;)V

    return-void
.end method

.method public surfaceDestroyed(Landroid/view/SurfaceHolder;)V
    .locals 0

    .line 175
    iget-boolean p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->closed:Z

    if-eqz p1, :cond_0

    return-void

    .line 176
    :cond_0
    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    if-eqz p1, :cond_1

    iget-object p1, p0, Lorg/emulationstation/frontend/sony/Ps3Activity;->input:Lorg/emulationstation/frontend/sony/Ps3Input;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/sony/Ps3Input;->releaseAll()V

    .line 177
    :cond_1
    new-instance p1, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda34;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/sony/Ps3Activity$$ExternalSyntheticLambda34;-><init>(Lorg/emulationstation/frontend/sony/Ps3Activity;)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/sony/Ps3Activity;->execute(Ljava/lang/Runnable;)V

    return-void
.end method
