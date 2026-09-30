.class public final Lorg/emulationstation/frontend/NativeCarouselBack;
.super Ljava/lang/Object;
.implements Landroid/window/OnBackInvokedCallback;
.field private static callback:Lorg/emulationstation/frontend/NativeCarouselBack;
.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method
.method public static install(Landroid/app/Activity;)V
    .locals 3
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I
    const/16 v1, 0x21
    if-lt v0, v1, :done
    sget-object v1, Lorg/emulationstation/frontend/NativeCarouselBack;->callback:Lorg/emulationstation/frontend/NativeCarouselBack;
    if-nez v1, :register
    new-instance v1, Lorg/emulationstation/frontend/NativeCarouselBack;
    invoke-direct {v1}, Lorg/emulationstation/frontend/NativeCarouselBack;-><init>()V
    sput-object v1, Lorg/emulationstation/frontend/NativeCarouselBack;->callback:Lorg/emulationstation/frontend/NativeCarouselBack;
    :register
    invoke-virtual {p0}, Landroid/app/Activity;->getOnBackInvokedDispatcher()Landroid/window/OnBackInvokedDispatcher;
    move-result-object v0
    const/4 v2, 0x0
    invoke-interface {v0, v2, v1}, Landroid/window/OnBackInvokedDispatcher;->registerOnBackInvokedCallback(ILandroid/window/OnBackInvokedCallback;)V
    :done
    return-void
.end method
.method public onBackInvoked()V
    .locals 2
    const-string v0, "TurboCarousel"
    const-string v1, "Android Back dispatched to native carousel"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    const/4 v0, 0x4
    invoke-static {v0}, Lorg/libsdl/app/SDLActivity;->onNativeKeyDown(I)V
    invoke-static {v0}, Lorg/libsdl/app/SDLActivity;->onNativeKeyUp(I)V
    return-void
.end method
