.method public onBackPressed()V
    .locals 1
    const/4 v0, 0x4
    invoke-static {v0}, Lorg/libsdl/app/SDLActivity;->onNativeKeyDown(I)V
    invoke-static {v0}, Lorg/libsdl/app/SDLActivity;->onNativeKeyUp(I)V
    return-void
.end method

.method public dispatchKeyEvent(Landroid/view/KeyEvent;)Z
    .locals 2
    invoke-virtual {p1}, Landroid/view/KeyEvent;->getKeyCode()I
    move-result v0
    const/4 v1, 0x4
    if-ne v0, v1, :normal_key
    invoke-virtual {p1}, Landroid/view/KeyEvent;->getAction()I
    move-result v0
    if-nez v0, :key_up
    invoke-static {v1}, Lorg/libsdl/app/SDLActivity;->onNativeKeyDown(I)V
    goto :handled_back
    :key_up
    const/4 v1, 0x1
    if-ne v0, v1, :handled_back
    const/4 v1, 0x4
    invoke-static {v1}, Lorg/libsdl/app/SDLActivity;->onNativeKeyUp(I)V
    :handled_back
    const/4 v0, 0x1
    return v0
    :normal_key
    invoke-super {p0, p1}, Lorg/libsdl/app/SDLActivity;->dispatchKeyEvent(Landroid/view/KeyEvent;)Z
    move-result v0
    return v0
.end method
