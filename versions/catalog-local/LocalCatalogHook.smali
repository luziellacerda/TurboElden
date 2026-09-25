.method private static tryLocalCatalog(Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/HttpBridge$Request;)Z
    .locals 4

    invoke-static {p0, p1}, Lorg/emulationstation/frontend/catalog/CatalogData;->matches(Ljava/lang/String;Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :not_local

    :try_start_local
    iget-boolean v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->cancelled:Z
    if-nez v0, :cancelled_local
    invoke-static {}, Lorg/libsdl/app/SDL;->getContext()Landroid/content/Context;
    move-result-object v0
    invoke-static {v0}, Lorg/emulationstation/frontend/catalog/LocalCatalog;->read(Landroid/content/Context;)[B
    move-result-object v0
    iget-boolean v1, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->cancelled:Z
    if-nez v1, :cancelled_local
    iput-object v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->content:[B
    array-length v1, v0
    int-to-long v1, v1
    iput-wide v1, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->total:J
    iget-object v3, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->downloadedBytes:Ljava/util/concurrent/atomic/AtomicLong;
    invoke-virtual {v3, v1, v2}, Ljava/util/concurrent/atomic/AtomicLong;->set(J)V
    const/4 v0, 0x1
    iput-boolean v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->downloadOk:Z
    iput v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->status:I
    :try_end_local
    .catch Ljava/lang/Exception; {:try_start_local .. :try_end_local} :failed_local
    goto :handled_local

    :failed_local
    move-exception v0
    const-string v0, "Falha ao ler catalogo local. Reinstale a atualizacao sem limpar dados."
    iput-object v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->error:Ljava/lang/String;
    const/4 v0, 0x2
    iput v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->status:I
    goto :handled_local

    :cancelled_local
    const-string v0, "Leitura do catalogo local cancelada."
    iput-object v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->error:Ljava/lang/String;
    const/4 v0, 0x2
    iput v0, p2, Lorg/emulationstation/frontend/HttpBridge$Request;->status:I

    :handled_local
    const/4 v0, 0x1
    return v0

    :not_local
    const/4 v0, 0x0
    return v0
.end method
