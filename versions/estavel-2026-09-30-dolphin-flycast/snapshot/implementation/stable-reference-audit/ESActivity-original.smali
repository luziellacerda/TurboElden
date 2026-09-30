.class public Lorg/emulationstation/frontend/ESActivity;
.super Lorg/libsdl/app/SDLActivity;
.source "ESActivity.java"


# static fields
.field private static final HOME_DIR_NAME:Ljava/lang/String; = "EmulationStation"

.field private static final PROFILE_IMAGE_PREFIX:Ljava/lang/String; = "profile_"

.field private static final PROFILE_IMAGE_SIZE:I = 0x200

.field static final PROFILE_PICK_CANCELLED:I = 0x3

.field static final PROFILE_PICK_IDLE:I = 0x0

.field static final PROFILE_PICK_PICKING:I = 0x1

.field static final PROFILE_PICK_SAVED:I = 0x2

.field private static final REQUEST_LEGACY_STORAGE:I = 0x1092

.field private static final REQUEST_NOTIFICATIONS:I = 0x1093

.field private static final REQUEST_PROFILE_IMAGE:I = 0x1094

.field public static final TAG:Ljava/lang/String; = "EmulationStation"

.field private static sInstance:Lorg/emulationstation/frontend/ESActivity;

.field private static sNotificationsRequested:Z

.field private static volatile sProfilePickState:I

.field private static sStorageRequested:Z


# direct methods
.method static bridge synthetic -$$Nest$mstartStorageRequest(Lorg/emulationstation/frontend/ESActivity;)V
    .locals 0

    invoke-direct {p0}, Lorg/emulationstation/frontend/ESActivity;->startStorageRequest()V

    return-void
.end method

.method static bridge synthetic -$$Nest$sfgetsInstance()Lorg/emulationstation/frontend/ESActivity;
    .locals 1

    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    return-object v0
.end method

.method static bridge synthetic -$$Nest$sfputsProfilePickState(I)V
    .locals 0

    sput p0, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    return-void
.end method

.method static bridge synthetic -$$Nest$smsaveProfileImage(Landroid/net/Uri;)Z
    .locals 0

    invoke-static {p0}, Lorg/emulationstation/frontend/ESActivity;->saveProfileImage(Landroid/net/Uri;)Z

    move-result p0

    return p0
.end method

.method static constructor <clinit>()V
    .locals 1

    .line 47
    const/4 v0, 0x0

    sput v0, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 29
    invoke-direct {p0}, Lorg/libsdl/app/SDLActivity;-><init>()V

    return-void
.end method

.method public static clearProfileImage()V
    .locals 7

    .line 181
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getAppContext()Landroid/content/Context;

    move-result-object v0

    .line 182
    .local v0, "context":Landroid/content/Context;
    if-nez v0, :cond_0

    .line 183
    return-void

    .line 185
    :cond_0
    invoke-virtual {v0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->listFiles()[Ljava/io/File;

    move-result-object v1

    .line 186
    .local v1, "files":[Ljava/io/File;
    if-nez v1, :cond_1

    .line 187
    return-void

    .line 189
    :cond_1
    array-length v2, v1

    const/4 v3, 0x0

    :goto_0
    if-ge v3, v2, :cond_3

    aget-object v4, v1, v3

    .line 191
    .local v4, "file":Ljava/io/File;
    invoke-virtual {v4}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v5

    const-string v6, "profile_"

    invoke-virtual {v5, v6}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v5

    if-eqz v5, :cond_2

    .line 192
    invoke-virtual {v4}, Ljava/io/File;->delete()Z

    .line 189
    .end local v4    # "file":Ljava/io/File;
    :cond_2
    add-int/lit8 v3, v3, 0x1

    goto :goto_0

    .line 194
    :cond_3
    return-void
.end method

.method private static collectFiles(Ljava/io/File;Ljava/util/List;)V
    .locals 6
    .param p0, "dir"    # Ljava/io/File;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/io/File;",
            "Ljava/util/List<",
            "Ljava/io/File;",
            ">;)V"
        }
    .end annotation

    .line 665
    .local p1, "out":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    invoke-virtual {p0}, Ljava/io/File;->listFiles()[Ljava/io/File;

    move-result-object v0

    .line 666
    .local v0, "entries":[Ljava/io/File;
    if-nez v0, :cond_0

    .line 667
    return-void

    .line 669
    :cond_0
    invoke-static {v0}, Ljava/util/Arrays;->sort([Ljava/lang/Object;)V

    .line 670
    array-length v1, v0

    const/4 v2, 0x0

    :goto_0
    if-ge v2, v1, :cond_3

    aget-object v3, v0, v2

    .line 672
    .local v3, "entry":Ljava/io/File;
    invoke-virtual {v3}, Ljava/io/File;->isDirectory()Z

    move-result v4

    if-eqz v4, :cond_1

    .line 673
    invoke-static {v3, p1}, Lorg/emulationstation/frontend/ESActivity;->collectFiles(Ljava/io/File;Ljava/util/List;)V

    goto :goto_1

    .line 674
    :cond_1
    invoke-virtual {v3}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v4

    const-string v5, ".extracted"

    invoke-virtual {v4, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-nez v4, :cond_2

    .line 675
    invoke-interface {p1, v3}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 670
    .end local v3    # "entry":Ljava/io/File;
    :cond_2
    :goto_1
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    .line 677
    :cond_3
    return-void
.end method

.method private static deleteTree(Ljava/io/File;)V
    .locals 4
    .param p0, "file"    # Ljava/io/File;

    .line 681
    if-eqz p0, :cond_2

    invoke-virtual {p0}, Ljava/io/File;->exists()Z

    move-result v0

    if-nez v0, :cond_0

    goto :goto_1

    .line 684
    :cond_0
    invoke-virtual {p0}, Ljava/io/File;->listFiles()[Ljava/io/File;

    move-result-object v0

    .line 685
    .local v0, "entries":[Ljava/io/File;
    if-eqz v0, :cond_1

    .line 686
    array-length v1, v0

    const/4 v2, 0x0

    :goto_0
    if-ge v2, v1, :cond_1

    aget-object v3, v0, v2

    .line 687
    .local v3, "entry":Ljava/io/File;
    invoke-static {v3}, Lorg/emulationstation/frontend/ESActivity;->deleteTree(Ljava/io/File;)V

    .line 686
    .end local v3    # "entry":Ljava/io/File;
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    .line 689
    :cond_1
    invoke-virtual {p0}, Ljava/io/File;->delete()Z

    .line 690
    return-void

    .line 682
    .end local v0    # "entries":[Ljava/io/File;
    :cond_2
    :goto_1
    return-void
.end method

.method public static extractRom(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .locals 24
    .param p0, "zipPath"    # Ljava/lang/String;
    .param p1, "extensions"    # Ljava/lang/String;
    .param p2, "destDir"    # Ljava/lang/String;

    .line 533
    move-object/from16 v1, p0

    const-string v2, ""

    const-string v3, "EmulationStation"

    new-instance v0, Ljava/io/File;

    invoke-direct {v0, v1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    move-object v4, v0

    .line 534
    .local v4, "zipFile":Ljava/io/File;
    invoke-virtual {v4}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v0

    .line 535
    .local v0, "stem":Ljava/lang/String;
    const/16 v5, 0x2e

    invoke-virtual {v0, v5}, Ljava/lang/String;->lastIndexOf(I)I

    move-result v5

    .line 536
    .local v5, "dot":I
    const/4 v6, 0x0

    if-lez v5, :cond_0

    .line 537
    invoke-virtual {v0, v6, v5}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v0

    move-object v7, v0

    goto :goto_0

    .line 536
    :cond_0
    move-object v7, v0

    .line 539
    .end local v0    # "stem":Ljava/lang/String;
    .local v7, "stem":Ljava/lang/String;
    :goto_0
    new-instance v0, Ljava/io/File;

    move-object/from16 v8, p2

    invoke-direct {v0, v8, v7}, Ljava/io/File;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    move-object v9, v0

    .line 540
    .local v9, "folder":Ljava/io/File;
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    move-object v10, v0

    .line 541
    .local v10, "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    invoke-virtual/range {p1 .. p1}, Ljava/lang/String;->toLowerCase()Ljava/lang/String;

    move-result-object v0

    const-string v11, "\\|"

    invoke-virtual {v0, v11}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    array-length v11, v0

    move v12, v6

    :goto_1
    if-ge v12, v11, :cond_2

    aget-object v13, v0, v12

    .line 543
    .local v13, "ext":Ljava/lang/String;
    invoke-virtual {v13}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v13

    .line 544
    invoke-virtual {v13}, Ljava/lang/String;->isEmpty()Z

    move-result v14

    if-nez v14, :cond_1

    const-string v14, "zip"

    invoke-virtual {v13, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    if-nez v14, :cond_1

    const-string v14, "7z"

    invoke-virtual {v13, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    if-nez v14, :cond_1

    .line 545
    invoke-interface {v10, v13}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 541
    .end local v13    # "ext":Ljava/lang/String;
    :cond_1
    add-int/lit8 v12, v12, 0x1

    goto :goto_1

    .line 551
    :cond_2
    :try_start_0
    new-instance v0, Ljava/io/File;

    const-string v11, ".extracted"

    invoke-direct {v0, v9, v11}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    move-object v11, v0

    .line 552
    .local v11, "marker":Ljava/io/File;
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v4}, Ljava/io/File;->length()J

    move-result-wide v12

    invoke-virtual {v0, v12, v13}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v12, ":"

    invoke-virtual {v0, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v4}, Ljava/io/File;->lastModified()J

    move-result-wide v12

    invoke-virtual {v0, v12, v13}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    move-object v12, v0

    .line 554
    .local v12, "stamp":Ljava/lang/String;
    const/4 v13, 0x0

    .line 555
    .local v13, "fresh":Z
    invoke-virtual {v11}, Ljava/io/File;->isFile()Z

    move-result v0
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_4

    if-eqz v0, :cond_3

    .line 557
    :try_start_1
    new-instance v0, Ljava/io/BufferedReader;

    new-instance v14, Ljava/io/FileReader;

    invoke-direct {v14, v11}, Ljava/io/FileReader;-><init>(Ljava/io/File;)V

    invoke-direct {v0, v14}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0

    move-object v14, v0

    .line 558
    .local v14, "reader":Ljava/io/BufferedReader;
    :try_start_2
    invoke-virtual {v14}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v12, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    move v13, v0

    .line 559
    :try_start_3
    invoke-virtual {v14}, Ljava/io/BufferedReader;->close()V

    goto :goto_2

    :catchall_0
    move-exception v0

    invoke-virtual {v14}, Ljava/io/BufferedReader;->close()V

    .end local v4    # "zipFile":Ljava/io/File;
    .end local v5    # "dot":I
    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0
    :try_end_3
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_0

    .line 655
    .end local v11    # "marker":Ljava/io/File;
    .end local v12    # "stamp":Ljava/lang/String;
    .end local v13    # "fresh":Z
    .end local v14    # "reader":Ljava/io/BufferedReader;
    .restart local v4    # "zipFile":Ljava/io/File;
    .restart local v5    # "dot":I
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :catch_0
    move-exception v0

    move-object/from16 v17, v2

    move-object/from16 v19, v4

    move/from16 v21, v5

    move-object/from16 v2, p1

    goto/16 :goto_11

    .line 562
    .restart local v11    # "marker":Ljava/io/File;
    .restart local v12    # "stamp":Ljava/lang/String;
    .restart local v13    # "fresh":Z
    :cond_3
    :goto_2
    if-nez v13, :cond_c

    .line 564
    :try_start_4
    invoke-static {v9}, Lorg/emulationstation/frontend/ESActivity;->deleteTree(Ljava/io/File;)V

    .line 565
    invoke-virtual {v9}, Ljava/io/File;->mkdirs()Z

    move-result v0
    :try_end_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_4

    const-string v14, "could not create "

    if-eqz v0, :cond_b

    .line 568
    :try_start_5
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v9}, Ljava/io/File;->getCanonicalPath()Ljava/lang/String;

    move-result-object v15

    invoke-virtual {v0, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    sget-object v15, Ljava/io/File;->separator:Ljava/lang/String;

    invoke-virtual {v0, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    move-object v15, v0

    .line 570
    .local v15, "rootPath":Ljava/lang/String;
    invoke-virtual {v4}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->toLowerCase()Ljava/lang/String;

    move-result-object v0

    const-string v6, ".7z"

    invoke-virtual {v0, v6}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v0
    :try_end_5
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_5} :catch_4

    if-eqz v0, :cond_4

    .line 572
    :try_start_6
    invoke-static {v4, v9, v15}, Lorg/emulationstation/frontend/ESActivity;->extractSevenZip(Ljava/io/File;Ljava/io/File;Ljava/lang/String;)V
    :try_end_6
    .catch Ljava/lang/Exception; {:try_start_6 .. :try_end_6} :catch_0

    move-object/from16 v17, v2

    move-object/from16 v19, v4

    move/from16 v21, v5

    goto/16 :goto_7

    .line 576
    :cond_4
    :try_start_7
    new-instance v0, Ljava/util/zip/ZipInputStream;

    new-instance v6, Ljava/io/BufferedInputStream;
    :try_end_7
    .catch Ljava/lang/Exception; {:try_start_7 .. :try_end_7} :catch_4

    move-object/from16 v17, v2

    :try_start_8
    new-instance v2, Ljava/io/FileInputStream;

    invoke-direct {v2, v4}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V

    invoke-direct {v6, v2}, Ljava/io/BufferedInputStream;-><init>(Ljava/io/InputStream;)V

    invoke-direct {v0, v6}, Ljava/util/zip/ZipInputStream;-><init>(Ljava/io/InputStream;)V
    :try_end_8
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_8} :catch_1

    move-object v2, v0

    .line 580
    .local v2, "zip":Ljava/util/zip/ZipInputStream;
    const/high16 v0, 0x40000

    :try_start_9
    new-array v0, v0, [B

    move-object v6, v0

    .line 582
    .local v6, "buffer":[B
    :goto_3
    invoke-virtual {v2}, Ljava/util/zip/ZipInputStream;->getNextEntry()Ljava/util/zip/ZipEntry;

    move-result-object v0

    move-object/from16 v18, v0

    .local v18, "entry":Ljava/util/zip/ZipEntry;
    if-eqz v0, :cond_a

    .line 584
    new-instance v0, Ljava/io/File;
    :try_end_9
    .catchall {:try_start_9 .. :try_end_9} :catchall_a

    move-object/from16 v19, v4

    .end local v4    # "zipFile":Ljava/io/File;
    .local v19, "zipFile":Ljava/io/File;
    :try_start_a
    invoke-virtual/range {v18 .. v18}, Ljava/util/zip/ZipEntry;->getName()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v0, v9, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v0

    move-object v4, v0

    .line 585
    .local v4, "target":Ljava/io/File;
    invoke-virtual {v4}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0, v15}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_9

    .line 588
    invoke-virtual/range {v18 .. v18}, Ljava/util/zip/ZipEntry;->isDirectory()Z

    move-result v0
    :try_end_a
    .catchall {:try_start_a .. :try_end_a} :catchall_8

    if-eqz v0, :cond_5

    .line 590
    :try_start_b
    invoke-virtual {v4}, Ljava/io/File;->mkdirs()Z
    :try_end_b
    .catchall {:try_start_b .. :try_end_b} :catchall_1

    .line 591
    move-object/from16 v4, v19

    goto :goto_3

    .line 613
    .end local v4    # "target":Ljava/io/File;
    .end local v6    # "buffer":[B
    .end local v18    # "entry":Ljava/util/zip/ZipEntry;
    :catchall_1
    move-exception v0

    move-object/from16 v23, v2

    move/from16 v21, v5

    goto/16 :goto_8

    .line 594
    .restart local v4    # "target":Ljava/io/File;
    .restart local v6    # "buffer":[B
    .restart local v18    # "entry":Ljava/util/zip/ZipEntry;
    :cond_5
    :try_start_c
    invoke-virtual {v4}, Ljava/io/File;->getParentFile()Ljava/io/File;

    move-result-object v0
    :try_end_c
    .catchall {:try_start_c .. :try_end_c} :catchall_8

    move-object/from16 v20, v0

    .line 595
    .local v20, "parent":Ljava/io/File;
    if-eqz v20, :cond_7

    :try_start_d
    invoke-virtual/range {v20 .. v20}, Ljava/io/File;->exists()Z

    move-result v0

    if-nez v0, :cond_7

    invoke-virtual/range {v20 .. v20}, Ljava/io/File;->mkdirs()Z

    move-result v0

    if-eqz v0, :cond_6

    move/from16 v21, v5

    move-object/from16 v5, v20

    goto :goto_4

    .line 596
    :cond_6
    new-instance v0, Ljava/lang/Exception;
    :try_end_d
    .catchall {:try_start_d .. :try_end_d} :catchall_3

    move/from16 v21, v5

    .end local v5    # "dot":I
    .local v21, "dot":I
    :try_start_e
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v5, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    move-object/from16 v14, v20

    .end local v20    # "parent":Ljava/io/File;
    .local v14, "parent":Ljava/io/File;
    invoke-virtual {v5, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-direct {v0, v5}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    .end local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local v11    # "marker":Ljava/io/File;
    .end local v12    # "stamp":Ljava/lang/String;
    .end local v13    # "fresh":Z
    .end local v15    # "rootPath":Ljava/lang/String;
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0
    :try_end_e
    .catchall {:try_start_e .. :try_end_e} :catchall_2

    .line 613
    .end local v4    # "target":Ljava/io/File;
    .end local v6    # "buffer":[B
    .end local v14    # "parent":Ljava/io/File;
    .end local v18    # "entry":Ljava/util/zip/ZipEntry;
    .restart local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local v11    # "marker":Ljava/io/File;
    .restart local v12    # "stamp":Ljava/lang/String;
    .restart local v13    # "fresh":Z
    .restart local v15    # "rootPath":Ljava/lang/String;
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :catchall_2
    move-exception v0

    move-object/from16 v23, v2

    goto/16 :goto_8

    .end local v21    # "dot":I
    .restart local v5    # "dot":I
    :catchall_3
    move-exception v0

    move/from16 v21, v5

    move-object/from16 v23, v2

    .end local v5    # "dot":I
    .restart local v21    # "dot":I
    goto/16 :goto_8

    .line 595
    .end local v21    # "dot":I
    .restart local v4    # "target":Ljava/io/File;
    .restart local v5    # "dot":I
    .restart local v6    # "buffer":[B
    .restart local v18    # "entry":Ljava/util/zip/ZipEntry;
    .restart local v20    # "parent":Ljava/io/File;
    :cond_7
    move/from16 v21, v5

    move-object/from16 v5, v20

    .line 598
    .end local v20    # "parent":Ljava/io/File;
    .local v5, "parent":Ljava/io/File;
    .restart local v21    # "dot":I
    :goto_4
    :try_start_f
    new-instance v0, Ljava/io/FileOutputStream;

    invoke-direct {v0, v4}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_f
    .catchall {:try_start_f .. :try_end_f} :catchall_6

    move-object/from16 v20, v0

    .line 602
    .local v20, "out":Ljava/io/OutputStream;
    :goto_5
    :try_start_10
    invoke-virtual {v2, v6}, Ljava/util/zip/ZipInputStream;->read([B)I

    move-result v0
    :try_end_10
    .catchall {:try_start_10 .. :try_end_10} :catchall_5

    move/from16 v22, v0

    .local v22, "read":I
    if-lez v0, :cond_8

    .line 603
    move-object/from16 v23, v2

    move-object/from16 v2, v20

    move/from16 v0, v22

    move-object/from16 v20, v4

    const/4 v4, 0x0

    .end local v4    # "target":Ljava/io/File;
    .end local v22    # "read":I
    .local v0, "read":I
    .local v2, "out":Ljava/io/OutputStream;
    .local v20, "target":Ljava/io/File;
    .local v23, "zip":Ljava/util/zip/ZipInputStream;
    :try_start_11
    invoke-virtual {v2, v6, v4, v0}, Ljava/io/OutputStream;->write([BII)V
    :try_end_11
    .catchall {:try_start_11 .. :try_end_11} :catchall_4

    move-object/from16 v4, v20

    move-object/from16 v20, v2

    move-object/from16 v2, v23

    goto :goto_5

    .line 607
    .end local v0    # "read":I
    :catchall_4
    move-exception v0

    goto :goto_6

    .line 602
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .local v2, "zip":Ljava/util/zip/ZipInputStream;
    .restart local v4    # "target":Ljava/io/File;
    .local v20, "out":Ljava/io/OutputStream;
    .restart local v22    # "read":I
    :cond_8
    move-object/from16 v23, v2

    move-object/from16 v2, v20

    move/from16 v0, v22

    move-object/from16 v20, v4

    .line 607
    .end local v4    # "target":Ljava/io/File;
    .end local v22    # "read":I
    .local v2, "out":Ljava/io/OutputStream;
    .local v20, "target":Ljava/io/File;
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    :try_start_12
    invoke-virtual {v2}, Ljava/io/OutputStream;->close()V

    .line 608
    nop

    .line 609
    .end local v2    # "out":Ljava/io/OutputStream;
    .end local v5    # "parent":Ljava/io/File;
    .end local v20    # "target":Ljava/io/File;
    move-object/from16 v4, v19

    move/from16 v5, v21

    move-object/from16 v2, v23

    goto/16 :goto_3

    .line 607
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .local v2, "zip":Ljava/util/zip/ZipInputStream;
    .restart local v4    # "target":Ljava/io/File;
    .restart local v5    # "parent":Ljava/io/File;
    .local v20, "out":Ljava/io/OutputStream;
    :catchall_5
    move-exception v0

    move-object/from16 v23, v2

    move-object/from16 v2, v20

    move-object/from16 v20, v4

    .end local v4    # "target":Ljava/io/File;
    .local v2, "out":Ljava/io/OutputStream;
    .local v20, "target":Ljava/io/File;
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    :goto_6
    invoke-virtual {v2}, Ljava/io/OutputStream;->close()V

    .line 608
    nop

    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local v11    # "marker":Ljava/io/File;
    .end local v12    # "stamp":Ljava/lang/String;
    .end local v13    # "fresh":Z
    .end local v15    # "rootPath":Ljava/lang/String;
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0

    .line 613
    .end local v5    # "parent":Ljava/io/File;
    .end local v6    # "buffer":[B
    .end local v18    # "entry":Ljava/util/zip/ZipEntry;
    .end local v20    # "target":Ljava/io/File;
    .local v2, "zip":Ljava/util/zip/ZipInputStream;
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local v11    # "marker":Ljava/io/File;
    .restart local v12    # "stamp":Ljava/lang/String;
    .restart local v13    # "fresh":Z
    .restart local v15    # "rootPath":Ljava/lang/String;
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :catchall_6
    move-exception v0

    move-object/from16 v23, v2

    .end local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    goto :goto_8

    .line 586
    .end local v21    # "dot":I
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v4    # "target":Ljava/io/File;
    .local v5, "dot":I
    .restart local v6    # "buffer":[B
    .restart local v18    # "entry":Ljava/util/zip/ZipEntry;
    :cond_9
    move-object/from16 v23, v2

    move-object/from16 v20, v4

    move/from16 v21, v5

    .end local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .end local v4    # "target":Ljava/io/File;
    .end local v5    # "dot":I
    .restart local v20    # "target":Ljava/io/File;
    .restart local v21    # "dot":I
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    new-instance v0, Ljava/lang/Exception;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "zip entry escapes the folder: "

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual/range {v18 .. v18}, Ljava/util/zip/ZipEntry;->getName()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v0, v2}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local v11    # "marker":Ljava/io/File;
    .end local v12    # "stamp":Ljava/lang/String;
    .end local v13    # "fresh":Z
    .end local v15    # "rootPath":Ljava/lang/String;
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0
    :try_end_12
    .catchall {:try_start_12 .. :try_end_12} :catchall_7

    .line 613
    .end local v6    # "buffer":[B
    .end local v18    # "entry":Ljava/util/zip/ZipEntry;
    .end local v20    # "target":Ljava/io/File;
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local v11    # "marker":Ljava/io/File;
    .restart local v12    # "stamp":Ljava/lang/String;
    .restart local v13    # "fresh":Z
    .restart local v15    # "rootPath":Ljava/lang/String;
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :catchall_7
    move-exception v0

    goto :goto_8

    .end local v21    # "dot":I
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v5    # "dot":I
    :catchall_8
    move-exception v0

    move-object/from16 v23, v2

    move/from16 v21, v5

    .end local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .end local v5    # "dot":I
    .restart local v21    # "dot":I
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    goto :goto_8

    .line 582
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .local v4, "zipFile":Ljava/io/File;
    .restart local v5    # "dot":I
    .restart local v6    # "buffer":[B
    .restart local v18    # "entry":Ljava/util/zip/ZipEntry;
    :cond_a
    move-object/from16 v23, v2

    move-object/from16 v19, v4

    move/from16 v21, v5

    .line 613
    .end local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .end local v4    # "zipFile":Ljava/io/File;
    .end local v5    # "dot":I
    .end local v6    # "buffer":[B
    .end local v18    # "entry":Ljava/util/zip/ZipEntry;
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    :try_start_13
    invoke-virtual/range {v23 .. v23}, Ljava/util/zip/ZipInputStream;->close()V

    .line 614
    nop

    .line 617
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    :goto_7
    new-instance v0, Ljava/io/FileWriter;

    invoke-direct {v0, v11}, Ljava/io/FileWriter;-><init>(Ljava/io/File;)V
    :try_end_13
    .catch Ljava/lang/Exception; {:try_start_13 .. :try_end_13} :catch_3

    move-object v2, v0

    .line 618
    .local v2, "writer":Ljava/io/Writer;
    :try_start_14
    invoke-virtual {v2, v12}, Ljava/io/Writer;->write(Ljava/lang/String;)V
    :try_end_14
    .catchall {:try_start_14 .. :try_end_14} :catchall_9

    .line 619
    :try_start_15
    invoke-virtual {v2}, Ljava/io/Writer;->close()V

    goto :goto_9

    :catchall_9
    move-exception v0

    invoke-virtual {v2}, Ljava/io/Writer;->close()V

    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0

    .line 613
    .local v2, "zip":Ljava/util/zip/ZipInputStream;
    .restart local v4    # "zipFile":Ljava/io/File;
    .restart local v5    # "dot":I
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :catchall_a
    move-exception v0

    move-object/from16 v23, v2

    move-object/from16 v19, v4

    move/from16 v21, v5

    .end local v2    # "zip":Ljava/util/zip/ZipInputStream;
    .end local v4    # "zipFile":Ljava/io/File;
    .end local v5    # "dot":I
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    .restart local v23    # "zip":Ljava/util/zip/ZipInputStream;
    :goto_8
    invoke-virtual/range {v23 .. v23}, Ljava/util/zip/ZipInputStream;->close()V

    .line 614
    nop

    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0

    .line 655
    .end local v11    # "marker":Ljava/io/File;
    .end local v12    # "stamp":Ljava/lang/String;
    .end local v13    # "fresh":Z
    .end local v15    # "rootPath":Ljava/lang/String;
    .end local v23    # "zip":Ljava/util/zip/ZipInputStream;
    .restart local v4    # "zipFile":Ljava/io/File;
    .restart local v5    # "dot":I
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :catch_1
    move-exception v0

    goto/16 :goto_10

    .line 566
    .restart local v11    # "marker":Ljava/io/File;
    .restart local v12    # "stamp":Ljava/lang/String;
    .restart local v13    # "fresh":Z
    :cond_b
    move-object/from16 v17, v2

    move-object/from16 v19, v4

    move/from16 v21, v5

    .end local v4    # "zipFile":Ljava/io/File;
    .end local v5    # "dot":I
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    new-instance v0, Ljava/lang/Exception;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v0, v2}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    .end local v7    # "stem":Ljava/lang/String;
    .end local v9    # "folder":Ljava/io/File;
    .end local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .end local p0    # "zipPath":Ljava/lang/String;
    .end local p1    # "extensions":Ljava/lang/String;
    .end local p2    # "destDir":Ljava/lang/String;
    throw v0

    .line 562
    .restart local v4    # "zipFile":Ljava/io/File;
    .restart local v5    # "dot":I
    .restart local v7    # "stem":Ljava/lang/String;
    .restart local v9    # "folder":Ljava/io/File;
    .restart local v10    # "wanted":Ljava/util/List;, "Ljava/util/List<Ljava/lang/String;>;"
    .restart local p0    # "zipPath":Ljava/lang/String;
    .restart local p1    # "extensions":Ljava/lang/String;
    .restart local p2    # "destDir":Ljava/lang/String;
    :cond_c
    move-object/from16 v17, v2

    move-object/from16 v19, v4

    move/from16 v21, v5

    .line 624
    .end local v4    # "zipFile":Ljava/io/File;
    .end local v5    # "dot":I
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    :goto_9
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    .line 625
    .local v0, "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    invoke-static {v9, v0}, Lorg/emulationstation/frontend/ESActivity;->collectFiles(Ljava/io/File;Ljava/util/List;)V

    .line 627
    const/4 v2, 0x4

    new-array v2, v2, [Ljava/lang/String;

    const-string v4, "m3u"

    const/16 v16, 0x0

    aput-object v4, v2, v16

    const-string v4, "cue"

    const/4 v5, 0x1

    aput-object v4, v2, v5

    const-string v4, "gdi"

    const/4 v5, 0x2

    aput-object v4, v2, v5

    const-string v4, "ccd"

    const/4 v5, 0x3

    aput-object v4, v2, v5

    .line 628
    .local v2, "playlists":[Ljava/lang/String;
    array-length v4, v2
    :try_end_15
    .catch Ljava/lang/Exception; {:try_start_15 .. :try_end_15} :catch_3

    move/from16 v6, v16

    :goto_a
    const-string v5, "."

    if-ge v6, v4, :cond_10

    :try_start_16
    aget-object v14, v2, v6

    .line 630
    .local v14, "ext":Ljava/lang/String;
    invoke-interface {v10}, Ljava/util/List;->isEmpty()Z

    move-result v15

    if-nez v15, :cond_d

    invoke-interface {v10, v14}, Ljava/util/List;->contains(Ljava/lang/Object;)Z

    move-result v15

    if-nez v15, :cond_d

    .line 631
    move-object/from16 v20, v0

    move-object/from16 v18, v2

    goto :goto_c

    .line 633
    :cond_d
    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v15

    :goto_b
    invoke-interface {v15}, Ljava/util/Iterator;->hasNext()Z

    move-result v16

    if-eqz v16, :cond_f

    invoke-interface {v15}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v16

    check-cast v16, Ljava/io/File;

    .line 634
    .local v16, "file":Ljava/io/File;
    invoke-virtual/range {v16 .. v16}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v18

    move-object/from16 v20, v0

    .end local v0    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .local v20, "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    invoke-virtual/range {v18 .. v18}, Ljava/lang/String;->toLowerCase()Ljava/lang/String;

    move-result-object v0

    move-object/from16 v18, v2

    .end local v2    # "playlists":[Ljava/lang/String;
    .local v18, "playlists":[Ljava/lang/String;
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v2}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_e

    .line 635
    invoke-virtual/range {v16 .. v16}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    return-object v0

    .line 634
    :cond_e
    move-object/from16 v2, v18

    move-object/from16 v0, v20

    .end local v16    # "file":Ljava/io/File;
    goto :goto_b

    .line 633
    .end local v18    # "playlists":[Ljava/lang/String;
    .end local v20    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .restart local v0    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .restart local v2    # "playlists":[Ljava/lang/String;
    :cond_f
    move-object/from16 v20, v0

    move-object/from16 v18, v2

    .line 628
    .end local v0    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .end local v2    # "playlists":[Ljava/lang/String;
    .end local v14    # "ext":Ljava/lang/String;
    .restart local v18    # "playlists":[Ljava/lang/String;
    .restart local v20    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    :goto_c
    add-int/lit8 v6, v6, 0x1

    move-object/from16 v2, v18

    move-object/from16 v0, v20

    goto :goto_a

    .line 638
    .end local v18    # "playlists":[Ljava/lang/String;
    .end local v20    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .restart local v0    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .restart local v2    # "playlists":[Ljava/lang/String;
    :cond_10
    move-object/from16 v20, v0

    move-object/from16 v18, v2

    .end local v0    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    .end local v2    # "playlists":[Ljava/lang/String;
    .restart local v18    # "playlists":[Ljava/lang/String;
    .restart local v20    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    invoke-interface {v10}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_d
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_13

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/String;

    .line 640
    .local v2, "ext":Ljava/lang/String;
    invoke-interface/range {v20 .. v20}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v4

    :goto_e
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v6

    if-eqz v6, :cond_12

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v6

    check-cast v6, Ljava/io/File;

    .line 641
    .local v6, "file":Ljava/io/File;
    invoke-virtual {v6}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v14}, Ljava/lang/String;->toLowerCase()Ljava/lang/String;

    move-result-object v14

    new-instance v15, Ljava/lang/StringBuilder;

    invoke-direct {v15}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v15, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v15

    invoke-virtual {v15, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v15

    invoke-virtual {v15}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v15

    invoke-virtual {v14, v15}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v14

    if-eqz v14, :cond_11

    .line 642
    invoke-virtual {v6}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    return-object v0

    .line 641
    .end local v6    # "file":Ljava/io/File;
    :cond_11
    goto :goto_e

    .line 643
    .end local v2    # "ext":Ljava/lang/String;
    :cond_12
    goto :goto_d

    .line 645
    :cond_13
    invoke-interface/range {v20 .. v20}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_f
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_16

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/io/File;

    .line 647
    .local v2, "file":Ljava/io/File;
    invoke-virtual {v2}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v4

    .line 648
    .local v4, "name":Ljava/lang/String;
    invoke-virtual {v4, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v6

    if-nez v6, :cond_15

    invoke-interface {v10}, Ljava/util/List;->isEmpty()Z

    move-result v6

    if-nez v6, :cond_14

    const-string v6, "*"

    invoke-interface {v10, v6}, Ljava/util/List;->contains(Ljava/lang/Object;)Z

    move-result v6

    if-eqz v6, :cond_15

    .line 649
    :cond_14
    invoke-virtual {v2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    return-object v0

    .line 650
    .end local v2    # "file":Ljava/io/File;
    .end local v4    # "name":Ljava/lang/String;
    :cond_15
    goto :goto_f

    .line 652
    :cond_16
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "No file matching "

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0
    :try_end_16
    .catch Ljava/lang/Exception; {:try_start_16 .. :try_end_16} :catch_3

    move-object/from16 v2, p1

    :try_start_17
    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v4, " inside "

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v3, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_17
    .catch Ljava/lang/Exception; {:try_start_17 .. :try_end_17} :catch_2

    .line 653
    return-object v17

    .line 655
    .end local v11    # "marker":Ljava/io/File;
    .end local v12    # "stamp":Ljava/lang/String;
    .end local v13    # "fresh":Z
    .end local v18    # "playlists":[Ljava/lang/String;
    .end local v20    # "files":Ljava/util/List;, "Ljava/util/List<Ljava/io/File;>;"
    :catch_2
    move-exception v0

    goto :goto_11

    :catch_3
    move-exception v0

    move-object/from16 v2, p1

    goto :goto_11

    .end local v19    # "zipFile":Ljava/io/File;
    .end local v21    # "dot":I
    .local v4, "zipFile":Ljava/io/File;
    .restart local v5    # "dot":I
    :catch_4
    move-exception v0

    move-object/from16 v17, v2

    :goto_10
    move-object/from16 v19, v4

    move/from16 v21, v5

    move-object/from16 v2, p1

    .line 657
    .end local v4    # "zipFile":Ljava/io/File;
    .end local v5    # "dot":I
    .local v0, "e":Ljava/lang/Exception;
    .restart local v19    # "zipFile":Ljava/io/File;
    .restart local v21    # "dot":I
    :goto_11
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "Could not extract "

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-static {v3, v4, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 658
    invoke-static {v9}, Lorg/emulationstation/frontend/ESActivity;->deleteTree(Ljava/io/File;)V

    .line 659
    return-object v17
.end method

.method private static extractSevenZip(Ljava/io/File;Ljava/io/File;Ljava/lang/String;)V
    .locals 8
    .param p0, "archive"    # Ljava/io/File;
    .param p1, "folder"    # Ljava/io/File;
    .param p2, "rootPath"    # Ljava/lang/String;
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 488
    new-instance v0, Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;

    invoke-direct {v0, p0}, Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;-><init>(Ljava/io/File;)V

    .line 494
    .local v0, "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    const/high16 v1, 0x40000

    :try_start_0
    new-array v1, v1, [B

    .line 496
    .local v1, "buffer":[B
    :goto_0
    invoke-virtual {v0}, Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;->getNextEntry()Lorg/apache/commons/compress/archivers/sevenz/SevenZArchiveEntry;

    move-result-object v2

    move-object v3, v2

    .local v3, "entry":Lorg/apache/commons/compress/archivers/sevenz/SevenZArchiveEntry;
    if-eqz v2, :cond_5

    .line 498
    new-instance v2, Ljava/io/File;

    invoke-virtual {v3}, Lorg/apache/commons/compress/archivers/sevenz/SevenZArchiveEntry;->getName()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v2, p1, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v2

    .line 499
    .local v2, "target":Ljava/io/File;
    invoke-virtual {v2}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v4, p2}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v4

    if-eqz v4, :cond_4

    .line 502
    invoke-virtual {v3}, Lorg/apache/commons/compress/archivers/sevenz/SevenZArchiveEntry;->isDirectory()Z

    move-result v4

    if-eqz v4, :cond_0

    .line 504
    invoke-virtual {v2}, Ljava/io/File;->mkdirs()Z

    .line 505
    goto :goto_0

    .line 508
    :cond_0
    invoke-virtual {v2}, Ljava/io/File;->getParentFile()Ljava/io/File;

    move-result-object v4

    .line 509
    .local v4, "parent":Ljava/io/File;
    if-eqz v4, :cond_2

    invoke-virtual {v4}, Ljava/io/File;->exists()Z

    move-result v5

    if-nez v5, :cond_2

    invoke-virtual {v4}, Ljava/io/File;->mkdirs()Z

    move-result v5

    if-eqz v5, :cond_1

    goto :goto_1

    .line 510
    :cond_1
    new-instance v5, Ljava/lang/Exception;

    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    const-string v7, "could not create "

    invoke-virtual {v6, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-direct {v5, v6}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    .end local v0    # "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    .end local p0    # "archive":Ljava/io/File;
    .end local p1    # "folder":Ljava/io/File;
    .end local p2    # "rootPath":Ljava/lang/String;
    throw v5

    .line 512
    .restart local v0    # "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    .restart local p0    # "archive":Ljava/io/File;
    .restart local p1    # "folder":Ljava/io/File;
    .restart local p2    # "rootPath":Ljava/lang/String;
    :cond_2
    :goto_1
    new-instance v5, Ljava/io/FileOutputStream;

    invoke-direct {v5, v2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    .line 516
    .local v5, "out":Ljava/io/OutputStream;
    :goto_2
    :try_start_1
    invoke-virtual {v0, v1}, Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;->read([B)I

    move-result v6

    move v7, v6

    .local v7, "read":I
    if-lez v6, :cond_3

    .line 517
    const/4 v6, 0x0

    invoke-virtual {v5, v1, v6, v7}, Ljava/io/OutputStream;->write([BII)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_2

    .line 521
    .end local v7    # "read":I
    :cond_3
    :try_start_2
    invoke-virtual {v5}, Ljava/io/OutputStream;->close()V

    .line 522
    nop

    .line 523
    .end local v2    # "target":Ljava/io/File;
    .end local v4    # "parent":Ljava/io/File;
    .end local v5    # "out":Ljava/io/OutputStream;
    goto :goto_0

    .line 521
    .restart local v2    # "target":Ljava/io/File;
    .restart local v4    # "parent":Ljava/io/File;
    .restart local v5    # "out":Ljava/io/OutputStream;
    :catchall_0
    move-exception v6

    invoke-virtual {v5}, Ljava/io/OutputStream;->close()V

    .line 522
    nop

    .end local v0    # "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    .end local p0    # "archive":Ljava/io/File;
    .end local p1    # "folder":Ljava/io/File;
    .end local p2    # "rootPath":Ljava/lang/String;
    throw v6

    .line 500
    .end local v4    # "parent":Ljava/io/File;
    .end local v5    # "out":Ljava/io/OutputStream;
    .restart local v0    # "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    .restart local p0    # "archive":Ljava/io/File;
    .restart local p1    # "folder":Ljava/io/File;
    .restart local p2    # "rootPath":Ljava/lang/String;
    :cond_4
    new-instance v4, Ljava/lang/Exception;

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "7z entry escapes the folder: "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v3}, Lorg/apache/commons/compress/archivers/sevenz/SevenZArchiveEntry;->getName()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-direct {v4, v5}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    .end local v0    # "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    .end local p0    # "archive":Ljava/io/File;
    .end local p1    # "folder":Ljava/io/File;
    .end local p2    # "rootPath":Ljava/lang/String;
    throw v4
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_1

    .line 527
    .end local v1    # "buffer":[B
    .end local v2    # "target":Ljava/io/File;
    .end local v3    # "entry":Lorg/apache/commons/compress/archivers/sevenz/SevenZArchiveEntry;
    .restart local v0    # "seven":Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;
    .restart local p0    # "archive":Ljava/io/File;
    .restart local p1    # "folder":Ljava/io/File;
    .restart local p2    # "rootPath":Ljava/lang/String;
    :cond_5
    invoke-virtual {v0}, Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;->close()V

    .line 528
    nop

    .line 529
    return-void

    .line 527
    :catchall_1
    move-exception v1

    invoke-virtual {v0}, Lorg/apache/commons/compress/archivers/sevenz/SevenZFile;->close()V

    .line 528
    throw v1
.end method

.method public static finishApp()V
    .locals 2

    .line 789
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 790
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    if-nez v0, :cond_0

    .line 791
    return-void

    .line 793
    :cond_0
    new-instance v1, Lorg/emulationstation/frontend/ESActivity$5;

    invoke-direct {v1, v0}, Lorg/emulationstation/frontend/ESActivity$5;-><init>(Lorg/emulationstation/frontend/ESActivity;)V

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/ESActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 800
    return-void
.end method

.method static getAppContext()Landroid/content/Context;
    .locals 1

    .line 57
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    if-eqz v0, :cond_0

    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/ESActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    :goto_0
    return-object v0
.end method

.method public static getCoresDir()Ljava/lang/String;
    .locals 5

    .line 694
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 695
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    const-string v1, ""

    if-nez v0, :cond_0

    .line 696
    return-object v1

    .line 698
    :cond_0
    new-instance v2, Ljava/io/File;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/ESActivity;->getFilesDir()Ljava/io/File;

    move-result-object v3

    const-string v4, "cores"

    invoke-direct {v2, v3, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 700
    .local v2, "dir":Ljava/io/File;
    invoke-virtual {v2}, Ljava/io/File;->exists()Z

    move-result v3

    if-nez v3, :cond_1

    invoke-virtual {v2}, Ljava/io/File;->mkdirs()Z

    move-result v3

    if-nez v3, :cond_1

    .line 702
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Could not create "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    const-string v4, "EmulationStation"

    invoke-static {v4, v3}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 703
    return-object v1

    .line 706
    :cond_1
    invoke-virtual {v2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v1

    return-object v1
.end method

.method public static getHardwareId()Ljava/lang/String;
    .locals 11

    .line 71
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getAppContext()Landroid/content/Context;

    move-result-object v0

    .line 72
    .local v0, "context":Landroid/content/Context;
    const-string v1, ""

    if-nez v0, :cond_0

    .line 73
    return-object v1

    .line 75
    :cond_0
    invoke-virtual {v0}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v2

    const-string v3, "android_id"

    invoke-static {v2, v3}, Landroid/provider/Settings$Secure;->getString(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 76
    .local v2, "id":Ljava/lang/String;
    if-eqz v2, :cond_3

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-eqz v3, :cond_1

    goto :goto_1

    .line 81
    :cond_1
    :try_start_0
    const-string v3, "SHA-256"

    invoke-static {v3}, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;

    move-result-object v3

    .line 82
    .local v3, "digest":Ljava/security/MessageDigest;
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "WayOs:"

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    const-string v5, "UTF-8"

    invoke-virtual {v4, v5}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object v4

    invoke-virtual {v3, v4}, Ljava/security/MessageDigest;->digest([B)[B

    move-result-object v4

    .line 84
    .local v4, "hash":[B
    new-instance v5, Ljava/lang/StringBuilder;

    array-length v6, v4

    mul-int/lit8 v6, v6, 0x2

    invoke-direct {v5, v6}, Ljava/lang/StringBuilder;-><init>(I)V

    .line 85
    .local v5, "hex":Ljava/lang/StringBuilder;
    array-length v6, v4

    const/4 v7, 0x0

    :goto_0
    if-ge v7, v6, :cond_2

    aget-byte v8, v4, v7

    .line 86
    .local v8, "b":B
    const-string v9, "%02x"

    and-int/lit16 v10, v8, 0xff

    invoke-static {v10}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v10

    filled-new-array {v10}, [Ljava/lang/Object;

    move-result-object v10

    invoke-static {v9, v10}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v9

    invoke-virtual {v5, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 85
    nop

    .end local v8    # "b":B
    add-int/lit8 v7, v7, 0x1

    goto :goto_0

    .line 88
    :cond_2
    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    return-object v1

    .line 90
    .end local v3    # "digest":Ljava/security/MessageDigest;
    .end local v4    # "hash":[B
    .end local v5    # "hex":Ljava/lang/StringBuilder;
    :catch_0
    move-exception v3

    .line 92
    .local v3, "e":Ljava/lang/Exception;
    const-string v4, "EmulationStation"

    const-string v5, "Could not hash the hardware id"

    invoke-static {v4, v5, v3}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 93
    return-object v1

    .line 77
    .end local v3    # "e":Ljava/lang/Exception;
    :cond_3
    :goto_1
    return-object v1
.end method

.method private static getHomeDir()Ljava/io/File;
    .locals 3

    .line 455
    new-instance v0, Ljava/io/File;

    invoke-static {}, Landroid/os/Environment;->getExternalStorageDirectory()Ljava/io/File;

    move-result-object v1

    const-string v2, "EmulationStation"

    invoke-direct {v0, v1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    return-object v0
.end method

.method public static getProfileImagePath()Ljava/lang/String;
    .locals 2

    .line 174
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->newestProfileImage()Ljava/io/File;

    move-result-object v0

    .line 175
    .local v0, "newest":Ljava/io/File;
    if-eqz v0, :cond_0

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v1

    goto :goto_0

    :cond_0
    const-string v1, ""

    :goto_0
    return-object v1
.end method

.method public static getProfilePickState()I
    .locals 1

    .line 163
    sget v0, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    return v0
.end method

.method public static getStorageRoot()Ljava/lang/String;
    .locals 1

    .line 465
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getHomeDir()Ljava/io/File;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public static hasStorageAccess()Z
    .locals 4

    .line 711
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 712
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    const/4 v1, 0x0

    if-nez v0, :cond_0

    .line 713
    return v1

    .line 715
    :cond_0
    sget v2, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v3, 0x1e

    if-lt v2, v3, :cond_1

    .line 716
    invoke-static {}, Landroid/os/Environment;->isExternalStorageManager()Z

    move-result v1

    return v1

    .line 718
    :cond_1
    const-string v2, "android.permission.WRITE_EXTERNAL_STORAGE"

    invoke-virtual {v0, v2}, Lorg/emulationstation/frontend/ESActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v2

    if-nez v2, :cond_2

    const/4 v1, 0x1

    :cond_2
    return v1
.end method

.method public static hideLoadingOverlay()V
    .locals 1

    .line 108
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    invoke-static {v0}, Lorg/emulationstation/frontend/LoadingOverlay;->hide(Landroid/app/Activity;)V

    .line 109
    return-void
.end method

.method private hideSystemUi()V
    .locals 2

    .line 444
    invoke-virtual {p0}, Lorg/emulationstation/frontend/ESActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const/16 v1, 0x1706

    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V

    .line 451
    return-void
.end method

.method public static installResources()V
    .locals 2

    .line 780
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 781
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    if-nez v0, :cond_0

    .line 782
    return-void

    .line 784
    :cond_0
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getHomeDir()Ljava/io/File;

    move-result-object v1

    invoke-static {v0, v1}, Lorg/emulationstation/frontend/AssetInstaller;->installIfNeeded(Landroid/content/Context;Ljava/io/File;)V

    invoke-static {v0, v1}, Lorg/emulationstation/frontend/switchengine/TurboEdenBridge;->prepare(Landroid/content/Context;Ljava/io/File;)V

    .line 785
    return-void
.end method

.method private static newestProfileImage()Ljava/io/File;
    .locals 10

    .line 198
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getAppContext()Landroid/content/Context;

    move-result-object v0

    .line 199
    .local v0, "context":Landroid/content/Context;
    if-nez v0, :cond_0

    .line 200
    const/4 v1, 0x0

    return-object v1

    .line 202
    :cond_0
    invoke-virtual {v0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->listFiles()[Ljava/io/File;

    move-result-object v1

    .line 203
    .local v1, "files":[Ljava/io/File;
    const/4 v2, 0x0

    .line 205
    .local v2, "newest":Ljava/io/File;
    if-eqz v1, :cond_3

    .line 207
    array-length v3, v1

    const/4 v4, 0x0

    :goto_0
    if-ge v4, v3, :cond_3

    aget-object v5, v1, v4

    .line 209
    .local v5, "file":Ljava/io/File;
    invoke-virtual {v5}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v6

    const-string v7, "profile_"

    invoke-virtual {v6, v7}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v6

    if-eqz v6, :cond_2

    invoke-virtual {v5}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v6

    const-string v7, ".png"

    invoke-virtual {v6, v7}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v6

    if-eqz v6, :cond_2

    if-eqz v2, :cond_1

    .line 210
    invoke-virtual {v5}, Ljava/io/File;->lastModified()J

    move-result-wide v6

    invoke-virtual {v2}, Ljava/io/File;->lastModified()J

    move-result-wide v8

    cmp-long v6, v6, v8

    if-lez v6, :cond_2

    .line 212
    :cond_1
    move-object v2, v5

    .line 207
    .end local v5    # "file":Ljava/io/File;
    :cond_2
    add-int/lit8 v4, v4, 0x1

    goto :goto_0

    .line 217
    :cond_3
    return-object v2
.end method

.method public static pickProfileImage()V
    .locals 2

    .line 122
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 123
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    if-nez v0, :cond_0

    .line 125
    const/4 v1, 0x3

    sput v1, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    .line 126
    return-void

    .line 129
    :cond_0
    const/4 v1, 0x1

    sput v1, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    .line 131
    new-instance v1, Lorg/emulationstation/frontend/ESActivity$1;

    invoke-direct {v1, v0}, Lorg/emulationstation/frontend/ESActivity$1;-><init>(Lorg/emulationstation/frontend/ESActivity;)V

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/ESActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 159
    return-void
.end method

.method static requestNotificationPermission()V
    .locals 2

    .line 352
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x21

    if-lt v0, v1, :cond_2

    sget-boolean v0, Lorg/emulationstation/frontend/ESActivity;->sNotificationsRequested:Z

    if-nez v0, :cond_2

    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    if-nez v0, :cond_0

    goto :goto_0

    .line 355
    :cond_0
    const/4 v0, 0x1

    sput-boolean v0, Lorg/emulationstation/frontend/ESActivity;->sNotificationsRequested:Z

    .line 357
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    const-string v1, "android.permission.POST_NOTIFICATIONS"

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/ESActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_1

    .line 358
    return-void

    .line 360
    :cond_1
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    new-instance v1, Lorg/emulationstation/frontend/ESActivity$3;

    invoke-direct {v1}, Lorg/emulationstation/frontend/ESActivity$3;-><init>()V

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/ESActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 367
    return-void

    .line 353
    :cond_2
    :goto_0
    return-void
.end method

.method public static requestStorageAccess()V
    .locals 2

    .line 724
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 725
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    if-eqz v0, :cond_1

    sget-boolean v1, Lorg/emulationstation/frontend/ESActivity;->sStorageRequested:Z

    if-eqz v1, :cond_0

    goto :goto_0

    .line 728
    :cond_0
    const/4 v1, 0x1

    sput-boolean v1, Lorg/emulationstation/frontend/ESActivity;->sStorageRequested:Z

    .line 730
    new-instance v1, Lorg/emulationstation/frontend/ESActivity$4;

    invoke-direct {v1, v0}, Lorg/emulationstation/frontend/ESActivity$4;-><init>(Lorg/emulationstation/frontend/ESActivity;)V

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/ESActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 737
    return-void

    .line 726
    :cond_1
    :goto_0
    return-void
.end method

.method public static resetProfilePickState()V
    .locals 1

    .line 168
    const/4 v0, 0x0

    sput v0, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    .line 169
    return-void
.end method

.method public static restartApp()V
    .locals 2

    .line 809
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 810
    .local v0, "activity":Lorg/emulationstation/frontend/ESActivity;
    if-nez v0, :cond_0

    .line 811
    return-void

    .line 813
    :cond_0
    new-instance v1, Lorg/emulationstation/frontend/ESActivity$6;

    invoke-direct {v1, v0}, Lorg/emulationstation/frontend/ESActivity$6;-><init>(Lorg/emulationstation/frontend/ESActivity;)V

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/ESActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 825
    return-void
.end method

.method private static saveProfileImage(Landroid/net/Uri;)Z
    .locals 22
    .param p0, "uri"    # Landroid/net/Uri;

    .line 253
    move-object/from16 v1, p0

    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getAppContext()Landroid/content/Context;

    move-result-object v2

    .line 254
    .local v2, "context":Landroid/content/Context;
    const/4 v3, 0x0

    if-nez v2, :cond_0

    .line 255
    return v3

    .line 259
    :cond_0
    :try_start_0
    invoke-virtual {v2}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0

    move-object v4, v0

    .line 262
    .local v4, "resolver":Landroid/content/ContentResolver;
    new-instance v0, Landroid/graphics/BitmapFactory$Options;

    invoke-direct {v0}, Landroid/graphics/BitmapFactory$Options;-><init>()V

    move-object v5, v0

    .line 263
    .local v5, "bounds":Landroid/graphics/BitmapFactory$Options;
    const/4 v0, 0x1

    iput-boolean v0, v5, Landroid/graphics/BitmapFactory$Options;->inJustDecodeBounds:Z

    .line 264
    invoke-virtual {v4, v1}, Landroid/content/ContentResolver;->openInputStream(Landroid/net/Uri;)Ljava/io/InputStream;

    move-result-object v6

    .line 265
    .local v6, "probe":Ljava/io/InputStream;
    const/4 v7, 0x0

    invoke-static {v6, v7, v5}, Landroid/graphics/BitmapFactory;->decodeStream(Ljava/io/InputStream;Landroid/graphics/Rect;Landroid/graphics/BitmapFactory$Options;)Landroid/graphics/Bitmap;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_5

    .line 266
    if-eqz v6, :cond_1

    .line 267
    :try_start_1
    invoke-virtual {v6}, Ljava/io/InputStream;->close()V
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0

    goto :goto_0

    .line 338
    .end local v4    # "resolver":Landroid/content/ContentResolver;
    .end local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .end local v6    # "probe":Ljava/io/InputStream;
    :catch_0
    move-exception v0

    move-object/from16 v17, v2

    move/from16 v18, v3

    goto/16 :goto_6

    .line 269
    .restart local v4    # "resolver":Landroid/content/ContentResolver;
    .restart local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .restart local v6    # "probe":Ljava/io/InputStream;
    :cond_1
    :goto_0
    :try_start_2
    iget v8, v5, Landroid/graphics/BitmapFactory$Options;->outWidth:I

    if-lez v8, :cond_a

    iget v8, v5, Landroid/graphics/BitmapFactory$Options;->outHeight:I

    if-gtz v8, :cond_2

    move-object/from16 v17, v2

    move/from16 v18, v3

    move-object/from16 v20, v4

    move-object/from16 v21, v5

    goto/16 :goto_5

    .line 272
    :cond_2
    const/4 v8, 0x1

    .line 273
    .local v8, "sample":I
    :goto_1
    iget v9, v5, Landroid/graphics/BitmapFactory$Options;->outWidth:I

    iget v10, v5, Landroid/graphics/BitmapFactory$Options;->outHeight:I

    invoke-static {v9, v10}, Ljava/lang/Math;->min(II)I

    move-result v9

    mul-int/lit8 v10, v8, 0x2

    div-int/2addr v9, v10

    const/16 v10, 0x200

    if-lt v9, v10, :cond_3

    .line 274
    mul-int/lit8 v8, v8, 0x2

    goto :goto_1

    .line 276
    :cond_3
    new-instance v9, Landroid/graphics/BitmapFactory$Options;

    invoke-direct {v9}, Landroid/graphics/BitmapFactory$Options;-><init>()V

    .line 277
    .local v9, "options":Landroid/graphics/BitmapFactory$Options;
    iput v8, v9, Landroid/graphics/BitmapFactory$Options;->inSampleSize:I

    .line 278
    invoke-virtual {v4, v1}, Landroid/content/ContentResolver;->openInputStream(Landroid/net/Uri;)Ljava/io/InputStream;

    move-result-object v10

    .line 279
    .local v10, "in":Ljava/io/InputStream;
    invoke-static {v10, v7, v9}, Landroid/graphics/BitmapFactory;->decodeStream(Ljava/io/InputStream;Landroid/graphics/Rect;Landroid/graphics/BitmapFactory$Options;)Landroid/graphics/Bitmap;

    move-result-object v7
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_5

    move-object v11, v7

    .line 280
    .local v11, "bitmap":Landroid/graphics/Bitmap;
    if-eqz v10, :cond_4

    .line 281
    :try_start_3
    invoke-virtual {v10}, Ljava/io/InputStream;->close()V
    :try_end_3
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_0

    .line 283
    :cond_4
    if-nez v11, :cond_5

    .line 284
    return v3

    .line 286
    :cond_5
    const/4 v7, 0x0

    .line 289
    .local v7, "rotation":I
    :try_start_4
    invoke-virtual {v4, v1}, Landroid/content/ContentResolver;->openInputStream(Landroid/net/Uri;)Ljava/io/InputStream;

    move-result-object v12

    .line 290
    .local v12, "exifIn":Ljava/io/InputStream;
    if-eqz v12, :cond_6

    .line 292
    new-instance v13, Landroid/media/ExifInterface;

    invoke-direct {v13, v12}, Landroid/media/ExifInterface;-><init>(Ljava/io/InputStream;)V

    .line 293
    .local v13, "exif":Landroid/media/ExifInterface;
    const-string v14, "Orientation"

    invoke-virtual {v13, v14, v0}, Landroid/media/ExifInterface;->getAttributeInt(Ljava/lang/String;I)I

    move-result v0

    sparse-switch v0, :sswitch_data_0

    goto :goto_2

    .line 297
    :sswitch_0
    const/16 v7, 0x10e

    goto :goto_2

    .line 295
    :sswitch_1
    const/16 v7, 0x5a

    goto :goto_2

    .line 296
    :sswitch_2
    const/16 v7, 0xb4

    .line 300
    :goto_2
    invoke-virtual {v12}, Ljava/io/InputStream;->close()V
    :try_end_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_1

    goto :goto_3

    .line 303
    .end local v12    # "exifIn":Ljava/io/InputStream;
    .end local v13    # "exif":Landroid/media/ExifInterface;
    :catch_1
    move-exception v0

    :cond_6
    :goto_3
    nop

    .line 305
    :try_start_5
    invoke-virtual {v11}, Landroid/graphics/Bitmap;->getWidth()I

    move-result v0

    invoke-virtual {v11}, Landroid/graphics/Bitmap;->getHeight()I

    move-result v12

    invoke-static {v0, v12}, Ljava/lang/Math;->min(II)I

    move-result v14

    .line 306
    .local v14, "side":I
    invoke-virtual {v11}, Landroid/graphics/Bitmap;->getWidth()I

    move-result v0

    sub-int/2addr v0, v14

    div-int/lit8 v12, v0, 0x2

    .line 307
    .local v12, "left":I
    invoke-virtual {v11}, Landroid/graphics/Bitmap;->getHeight()I

    move-result v0

    sub-int/2addr v0, v14

    div-int/lit8 v13, v0, 0x2

    .line 309
    .local v13, "top":I
    new-instance v16, Landroid/graphics/Matrix;

    invoke-direct/range {v16 .. v16}, Landroid/graphics/Matrix;-><init>()V
    :try_end_5
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_5} :catch_5

    move-object/from16 v0, v16

    .line 310
    .local v0, "matrix":Landroid/graphics/Matrix;
    const/high16 v15, 0x44000000    # 512.0f

    move/from16 v18, v3

    int-to-float v3, v14

    div-float v3, v15, v3

    .line 311
    .local v3, "scale":F
    :try_start_6
    invoke-virtual {v0, v3, v3}, Landroid/graphics/Matrix;->postScale(FF)Z
    :try_end_6
    .catch Ljava/lang/Exception; {:try_start_6 .. :try_end_6} :catch_4

    .line 312
    if-eqz v7, :cond_7

    .line 313
    int-to-float v15, v7

    :try_start_7
    invoke-virtual {v0, v15}, Landroid/graphics/Matrix;->postRotate(F)Z
    :try_end_7
    .catch Ljava/lang/Exception; {:try_start_7 .. :try_end_7} :catch_2

    goto :goto_4

    .line 338
    .end local v0    # "matrix":Landroid/graphics/Matrix;
    .end local v3    # "scale":F
    .end local v4    # "resolver":Landroid/content/ContentResolver;
    .end local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .end local v6    # "probe":Ljava/io/InputStream;
    .end local v7    # "rotation":I
    .end local v8    # "sample":I
    .end local v9    # "options":Landroid/graphics/BitmapFactory$Options;
    .end local v10    # "in":Ljava/io/InputStream;
    .end local v11    # "bitmap":Landroid/graphics/Bitmap;
    .end local v12    # "left":I
    .end local v13    # "top":I
    .end local v14    # "side":I
    :catch_2
    move-exception v0

    move-object/from16 v17, v2

    goto/16 :goto_6

    .line 315
    .restart local v0    # "matrix":Landroid/graphics/Matrix;
    .restart local v3    # "scale":F
    .restart local v4    # "resolver":Landroid/content/ContentResolver;
    .restart local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .restart local v6    # "probe":Ljava/io/InputStream;
    .restart local v7    # "rotation":I
    .restart local v8    # "sample":I
    .restart local v9    # "options":Landroid/graphics/BitmapFactory$Options;
    .restart local v10    # "in":Ljava/io/InputStream;
    .restart local v11    # "bitmap":Landroid/graphics/Bitmap;
    .restart local v12    # "left":I
    .restart local v13    # "top":I
    .restart local v14    # "side":I
    :cond_7
    :goto_4
    const/16 v17, 0x1

    move v15, v14

    move-object/from16 v16, v0

    .end local v0    # "matrix":Landroid/graphics/Matrix;
    .local v16, "matrix":Landroid/graphics/Matrix;
    :try_start_8
    invoke-static/range {v11 .. v17}, Landroid/graphics/Bitmap;->createBitmap(Landroid/graphics/Bitmap;IIIILandroid/graphics/Matrix;Z)Landroid/graphics/Bitmap;

    move-result-object v0
    :try_end_8
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_8} :catch_4

    .line 316
    .local v0, "square":Landroid/graphics/Bitmap;
    if-eq v0, v11, :cond_8

    .line 317
    :try_start_9
    invoke-virtual {v11}, Landroid/graphics/Bitmap;->recycle()V
    :try_end_9
    .catch Ljava/lang/Exception; {:try_start_9 .. :try_end_9} :catch_2

    .line 319
    :cond_8
    :try_start_a
    invoke-virtual {v2}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v15

    .line 320
    .local v15, "dir":Ljava/io/File;
    new-instance v1, Ljava/io/File;
    :try_end_a
    .catch Ljava/lang/Exception; {:try_start_a .. :try_end_a} :catch_4

    move-object/from16 v17, v2

    .end local v2    # "context":Landroid/content/Context;
    .local v17, "context":Landroid/content/Context;
    :try_start_b
    const-string v2, "profile.tmp"

    invoke-direct {v1, v15, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 321
    .local v1, "temp":Ljava/io/File;
    new-instance v2, Ljava/io/File;

    move/from16 v19, v3

    .end local v3    # "scale":F
    .local v19, "scale":F
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v20, v4

    .end local v4    # "resolver":Landroid/content/ContentResolver;
    .local v20, "resolver":Landroid/content/ContentResolver;
    const-string v4, "profile_"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    move-object/from16 v21, v5

    .end local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .local v21, "bounds":Landroid/graphics/BitmapFactory$Options;
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    invoke-virtual {v3, v4, v5}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, ".png"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-direct {v2, v15, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 323
    .local v2, "target":Ljava/io/File;
    new-instance v3, Ljava/io/FileOutputStream;

    invoke-direct {v3, v1}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    .line 324
    .local v3, "out":Ljava/io/FileOutputStream;
    sget-object v4, Landroid/graphics/Bitmap$CompressFormat;->PNG:Landroid/graphics/Bitmap$CompressFormat;

    const/16 v5, 0x64

    invoke-virtual {v0, v4, v5, v3}, Landroid/graphics/Bitmap;->compress(Landroid/graphics/Bitmap$CompressFormat;ILjava/io/OutputStream;)Z

    move-result v4

    .line 325
    .local v4, "written":Z
    invoke-virtual {v3}, Ljava/io/FileOutputStream;->close()V

    .line 326
    invoke-virtual {v0}, Landroid/graphics/Bitmap;->recycle()V

    .line 328
    if-nez v4, :cond_9

    .line 330
    invoke-virtual {v1}, Ljava/io/File;->delete()Z

    .line 331
    return v18

    .line 335
    :cond_9
    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->clearProfileImage()V

    .line 336
    invoke-virtual {v1, v2}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    move-result v5
    :try_end_b
    .catch Ljava/lang/Exception; {:try_start_b .. :try_end_b} :catch_3

    return v5

    .line 338
    .end local v0    # "square":Landroid/graphics/Bitmap;
    .end local v1    # "temp":Ljava/io/File;
    .end local v2    # "target":Ljava/io/File;
    .end local v3    # "out":Ljava/io/FileOutputStream;
    .end local v4    # "written":Z
    .end local v6    # "probe":Ljava/io/InputStream;
    .end local v7    # "rotation":I
    .end local v8    # "sample":I
    .end local v9    # "options":Landroid/graphics/BitmapFactory$Options;
    .end local v10    # "in":Ljava/io/InputStream;
    .end local v11    # "bitmap":Landroid/graphics/Bitmap;
    .end local v12    # "left":I
    .end local v13    # "top":I
    .end local v14    # "side":I
    .end local v15    # "dir":Ljava/io/File;
    .end local v16    # "matrix":Landroid/graphics/Matrix;
    .end local v19    # "scale":F
    .end local v20    # "resolver":Landroid/content/ContentResolver;
    .end local v21    # "bounds":Landroid/graphics/BitmapFactory$Options;
    :catch_3
    move-exception v0

    goto :goto_6

    .end local v17    # "context":Landroid/content/Context;
    .local v2, "context":Landroid/content/Context;
    :catch_4
    move-exception v0

    move-object/from16 v17, v2

    goto :goto_6

    .line 269
    .local v4, "resolver":Landroid/content/ContentResolver;
    .restart local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .restart local v6    # "probe":Ljava/io/InputStream;
    :cond_a
    move-object/from16 v17, v2

    move/from16 v18, v3

    move-object/from16 v20, v4

    move-object/from16 v21, v5

    .line 270
    .end local v2    # "context":Landroid/content/Context;
    .end local v4    # "resolver":Landroid/content/ContentResolver;
    .end local v5    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .restart local v17    # "context":Landroid/content/Context;
    .restart local v20    # "resolver":Landroid/content/ContentResolver;
    .restart local v21    # "bounds":Landroid/graphics/BitmapFactory$Options;
    :goto_5
    return v18

    .line 338
    .end local v6    # "probe":Ljava/io/InputStream;
    .end local v17    # "context":Landroid/content/Context;
    .end local v20    # "resolver":Landroid/content/ContentResolver;
    .end local v21    # "bounds":Landroid/graphics/BitmapFactory$Options;
    .restart local v2    # "context":Landroid/content/Context;
    :catch_5
    move-exception v0

    move-object/from16 v17, v2

    move/from16 v18, v3

    .line 340
    .end local v2    # "context":Landroid/content/Context;
    .local v0, "e":Ljava/lang/Exception;
    .restart local v17    # "context":Landroid/content/Context;
    :goto_6
    const-string v1, "EmulationStation"

    const-string v2, "Could not save the profile image"

    invoke-static {v1, v2, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 341
    return v18

    nop

    :sswitch_data_0
    .sparse-switch
        0x3 -> :sswitch_2
        0x6 -> :sswitch_1
        0x8 -> :sswitch_0
    .end sparse-switch
.end method

.method public static showLoadingOverlay(Ljava/lang/String;)V
    .locals 1
    .param p0, "name"    # Ljava/lang/String;

    .line 103
    sget-object v0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    invoke-static {v0, p0}, Lorg/emulationstation/frontend/LoadingOverlay;->show(Landroid/app/Activity;Ljava/lang/String;)V

    .line 104
    return-void
.end method

.method private startStorageRequest()V
    .locals 4

    .line 741
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1e

    if-ge v0, v1, :cond_0

    .line 743
    const/4 v0, 0x2

    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "android.permission.READ_EXTERNAL_STORAGE"

    aput-object v2, v0, v1

    const/4 v1, 0x1

    const-string v2, "android.permission.WRITE_EXTERNAL_STORAGE"

    aput-object v2, v0, v1

    const/16 v1, 0x1092

    invoke-virtual {p0, v0, v1}, Lorg/emulationstation/frontend/ESActivity;->requestPermissions([Ljava/lang/String;I)V

    .line 747
    return-void

    .line 754
    :cond_0
    :try_start_0
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    .line 755
    .local v0, "intent":Landroid/content/Intent;
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "package:"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {p0}, Lorg/emulationstation/frontend/ESActivity;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setData(Landroid/net/Uri;)Landroid/content/Intent;

    .line 756
    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/ESActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 770
    .end local v0    # "intent":Landroid/content/Intent;
    goto :goto_0

    .line 758
    :catch_0
    move-exception v0

    .line 760
    .local v0, "e":Ljava/lang/Exception;
    const-string v1, "Could not open the per-app storage settings, falling back to the full list"

    const-string v2, "EmulationStation"

    invoke-static {v2, v1, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 764
    :try_start_1
    new-instance v1, Landroid/content/Intent;

    const-string v3, "android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION"

    invoke-direct {v1, v3}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v1}, Lorg/emulationstation/frontend/ESActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_1

    .line 769
    goto :goto_0

    .line 766
    :catch_1
    move-exception v1

    .line 768
    .local v1, "fallbackError":Ljava/lang/Exception;
    const-string v3, "No way to ask for storage access on this device"

    invoke-static {v2, v3, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 771
    .end local v0    # "e":Ljava/lang/Exception;
    .end local v1    # "fallbackError":Ljava/lang/Exception;
    :goto_0
    return-void
.end method


# virtual methods
.method protected getArguments()[Ljava/lang/String;
    .locals 3

    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getHomeDir()Ljava/io/File;

    move-result-object v0

    invoke-static {p0, v0}, Lorg/emulationstation/frontend/theme/ThemeInstaller;->prepare(Landroid/content/Context;Ljava/io/File;)V

    invoke-static {p0, v0}, Lorg/emulationstation/frontend/switchengine/TurboEdenBridge;->prepare(Landroid/content/Context;Ljava/io/File;)V

    .line 384
    const/4 v0, 0x2

    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "--home"

    aput-object v2, v0, v1

    invoke-static {}, Lorg/emulationstation/frontend/ESActivity;->getHomeDir()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v1

    const/4 v2, 0x1

    aput-object v1, v0, v2

    return-object v0
.end method

.method protected getLibraries()[Ljava/lang/String;
    .locals 3

    .line 376
    const/4 v0, 0x2

    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "SDL2"

    aput-object v2, v0, v1

    const/4 v1, 0x1

    const-string v2, "main"

    aput-object v2, v0, v1

    return-object v0
.end method

.method protected onActivityResult(IILandroid/content/Intent;)V
    .locals 4
    .param p1, "requestCode"    # I
    .param p2, "resultCode"    # I
    .param p3, "data"    # Landroid/content/Intent;

    .line 223
    const/16 v0, 0x1094

    if-eq p1, v0, :cond_0

    .line 225
    invoke-super {p0, p1, p2, p3}, Lorg/libsdl/app/SDLActivity;->onActivityResult(IILandroid/content/Intent;)V

    .line 226
    return-void

    .line 229
    :cond_0
    const/4 v0, -0x1

    if-ne p2, v0, :cond_1

    if-eqz p3, :cond_1

    invoke-virtual {p3}, Landroid/content/Intent;->getData()Landroid/net/Uri;

    move-result-object v0

    goto :goto_0

    :cond_1
    const/4 v0, 0x0

    .line 230
    .local v0, "uri":Landroid/net/Uri;
    :goto_0
    if-nez v0, :cond_2

    .line 232
    const/4 v1, 0x3

    sput v1, Lorg/emulationstation/frontend/ESActivity;->sProfilePickState:I

    .line 233
    return-void

    .line 237
    :cond_2
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lorg/emulationstation/frontend/ESActivity$2;

    invoke-direct {v2, p0, v0}, Lorg/emulationstation/frontend/ESActivity$2;-><init>(Lorg/emulationstation/frontend/ESActivity;Landroid/net/Uri;)V

    const-string v3, "ProfileImage"

    invoke-direct {v1, v2, v3}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 243
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    .line 244
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2
    .param p1, "savedInstanceState"    # Landroid/os/Bundle;

    .line 390
    sput-object p0, Lorg/emulationstation/frontend/ESActivity;->sInstance:Lorg/emulationstation/frontend/ESActivity;

    .line 397
    new-instance v0, Landroid/os/StrictMode$VmPolicy$Builder;

    invoke-direct {v0}, Landroid/os/StrictMode$VmPolicy$Builder;-><init>()V

    invoke-virtual {v0}, Landroid/os/StrictMode$VmPolicy$Builder;->build()Landroid/os/StrictMode$VmPolicy;

    move-result-object v0

    invoke-static {v0}, Landroid/os/StrictMode;->setVmPolicy(Landroid/os/StrictMode$VmPolicy;)V

    .line 399
    invoke-super {p0, p1}, Lorg/libsdl/app/SDLActivity;->onCreate(Landroid/os/Bundle;)V

    .line 401
    invoke-virtual {p0}, Lorg/emulationstation/frontend/ESActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    const/16 v1, 0x80

    invoke-virtual {v0, v1}, Landroid/view/Window;->addFlags(I)V

    .line 403
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1c

    if-lt v0, v1, :cond_0

    .line 404
    invoke-virtual {p0}, Lorg/emulationstation/frontend/ESActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getAttributes()Landroid/view/WindowManager$LayoutParams;

    move-result-object v0

    const/4 v1, 0x1

    iput v1, v0, Landroid/view/WindowManager$LayoutParams;->layoutInDisplayCutoutMode:I

    .line 407
    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/ESActivity;->hideSystemUi()V

    .line 408
    return-void
.end method

.method protected onDestroy()V
    .locals 2

    .line 423
    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onDestroy()V

    .line 431
    invoke-static {}, Lorg/emulationstation/frontend/HttpBridge;->activeFileDownloads()Lorg/emulationstation/frontend/HttpBridge$DownloadSnapshot;

    move-result-object v0

    iget v0, v0, Lorg/emulationstation/frontend/HttpBridge$DownloadSnapshot;->count:I

    const-string v1, "EmulationStation"

    if-nez v0, :cond_0

    .line 433
    const-string v0, "Activity destroyed with nothing downloading - ending the process"

    invoke-static {v1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 434
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v0

    invoke-static {v0}, Landroid/os/Process;->killProcess(I)V

    goto :goto_0

    .line 438
    :cond_0
    const-string v0, "Activity destroyed with a download running - keeping the process for it"

    invoke-static {v1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 440
    :goto_0
    return-void
.end method

.method protected onResume()V
    .locals 0

    invoke-super {p0}, Lorg/libsdl/app/SDLActivity;->onResume()V

    invoke-static {p0}, Lorg/emulationstation/frontend/auth/LoginActivity;->ensureAuthorized(Landroid/app/Activity;)V

    return-void
.end method

.method public onWindowFocusChanged(Z)V
    .locals 0
    .param p1, "hasFocus"    # Z

    .line 413
    invoke-super {p0, p1}, Lorg/libsdl/app/SDLActivity;->onWindowFocusChanged(Z)V

    .line 416
    if-eqz p1, :cond_0

    .line 417
    invoke-direct {p0}, Lorg/emulationstation/frontend/ESActivity;->hideSystemUi()V

    .line 418
    :cond_0
    return-void
.end method
