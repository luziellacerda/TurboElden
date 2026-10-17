.method private static prepareSnesMultitap(Lorg/emulationstation/frontend/netplay/StationOnlineGame;Ljava/io/File;Ljava/lang/StringBuilder;I)V
    .locals 8

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->multiplayerProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-eqz v0, :cond_2

    const-string v1, "snes"

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->platform:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_2

    const-string v1, "snes-multitap-port2-v1"

    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->controllerProfile:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_2

    new-instance v1, Ljava/io/File;

    const-string v2, "input-devices"

    invoke-direct {v1, p1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    new-instance v2, Ljava/io/File;

    const-string v3, "bsnes-mercury"

    invoke-direct {v2, v1, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->isDirectory()Z

    move-result v3

    if-nez v3, :cond_0

    invoke-virtual {v2}, Ljava/io/File;->mkdirs()Z

    move-result v3

    if-nez v3, :cond_0

    new-instance v3, Ljava/io/IOException;

    const-string v4, "Cannot create room controller directory"

    invoke-direct {v3, v4}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v3

    :cond_0
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const/4 v4, 0x1

    :goto_0
    const/16 v5, 0x10

    if-gt v4, v5, :cond_1

    new-instance v5, Ljava/lang/StringBuilder;

    const-string v6, "input_libretro_device_p"

    invoke-direct {v5, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v0, v4, p3}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->deviceForSlot(II)I

    move-result v6

    invoke-static {v6}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;

    move-result-object v6

    invoke-static {v3, v5, v6}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->set(Ljava/lang/StringBuilder;Ljava/lang/String;Ljava/lang/String;)V

    add-int/lit8 v4, v4, 0x1

    goto :goto_0

    :cond_1
    new-instance v4, Ljava/io/File;

    const-string v5, "bsnes-mercury.rmp"

    invoke-direct {v4, v2, v5}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v4, v3}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->write(Ljava/io/File;Ljava/lang/String;)V

    const-string v2, "input_remapping_directory"

    invoke-virtual {v1}, Ljava/io/File;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {p2, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->set(Ljava/lang/StringBuilder;Ljava/lang/String;Ljava/lang/String;)V

    const-string v2, "input_remap_sort_by_controller_enable"

    const-string v3, "false"

    invoke-static {p2, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->set(Ljava/lang/StringBuilder;Ljava/lang/String;Ljava/lang/String;)V

    const-string v2, "notification_show_remap_load"

    invoke-static {p2, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->set(Ljava/lang/StringBuilder;Ljava/lang/String;Ljava/lang/String;)V

    const-string v2, "auto_remaps_enable = \"false\"\n"

    invoke-virtual {p2, v2}, Ljava/lang/StringBuilder;->indexOf(Ljava/lang/String;)I

    move-result v4

    if-ltz v4, :flag_missing

    invoke-virtual {v2}, Ljava/lang/String;->length()I

    move-result v5

    add-int/2addr v5, v4

    const-string v3, "auto_remaps_enable = \"true\"\n"

    invoke-virtual {p2, v4, v5, v3}, Ljava/lang/StringBuilder;->replace(IILjava/lang/String;)Ljava/lang/StringBuilder;

    goto :cond_2

    :flag_missing
    new-instance v2, Ljava/io/IOException;

    const-string v3, "Missing room remap policy"

    invoke-direct {v2, v3}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v2

    :cond_2
    return-void
.end method
