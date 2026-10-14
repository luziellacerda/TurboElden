.class final Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;
.super Ljava/lang/Object;
.source "StationMultiplayerSession.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x12
    name = "Channel"
.end annotation


# instance fields
.field at:J

.field final guestSlot:I

.field final id:Ljava/lang/String;

.field ready:Z

.field running:Z

.field serial:J

.field sync:Z

.field final synthetic this$0:Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;

.field final tunnel:Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel;


# direct methods
.method constructor <init>(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;Lorg/json/JSONObject;I)V
    .locals 19
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    move-object/from16 v0, p0

    move-object/from16 v1, p1

    move-object/from16 v2, p2

    .line 17
    iput-object v1, v0, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;->this$0:Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;

    invoke-direct/range {p0 .. p0}, Ljava/lang/Object;-><init>()V

    const-wide/16 v3, -0x1

    .line 16
    iput-wide v3, v0, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;->at:J

    const-string v3, "linkId"

    .line 18
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    iput-object v3, v0, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;->id:Ljava/lang/String;

    const-string v4, "guestSlot"

    invoke-virtual {v2, v4}, Lorg/json/JSONObject;->getInt(Ljava/lang/String;)I

    move-result v4

    iput v4, v0, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;->guestSlot:I

    const-string v5, "ticket"

    .line 19
    invoke-virtual {v2, v5}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v2

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$000(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Z

    move-result v6

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$100(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)I

    move-result v7

    invoke-static {v2, v3, v6, v7}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->checkTicket(Lorg/json/JSONObject;Ljava/lang/String;ZI)V

    .line 20
    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$200(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Lorg/emulationstation/frontend/netplay/StationMultiplayerEndpoint$Factory;

    move-result-object v3

    const/4 v6, 0x1

    if-nez v3, :cond_0

    const/4 v3, 0x0

    goto :goto_1

    :cond_0
    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$200(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Lorg/emulationstation/frontend/netplay/StationMultiplayerEndpoint$Factory;

    move-result-object v3

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$100(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)I

    move-result v7

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$000(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Z

    move-result v8

    if-eqz v8, :cond_1

    move v8, v4

    goto :goto_0

    :cond_1
    move v8, v6

    :goto_0
    invoke-interface {v3, v7, v8}, Lorg/emulationstation/frontend/netplay/StationMultiplayerEndpoint$Factory;->create(II)Lorg/emulationstation/frontend/netplay/StationMultiplayerEndpoint;

    move-result-object v3

    .line 21
    :goto_1
    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$200(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Lorg/emulationstation/frontend/netplay/StationMultiplayerEndpoint$Factory;

    move-result-object v7

    if-eqz v7, :cond_3

    if-eqz v3, :cond_2

    goto :goto_2

    :cond_2
    new-instance v1, Ljava/io/IOException;

    const-string v2, "NATIVE_ENDPOINT"

    invoke-direct {v1, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 22
    :cond_3
    :goto_2
    new-instance v15, Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel;

    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationRelayTls;->multiplayerEndpoint()Ljava/net/URI;

    move-result-object v8

    invoke-virtual {v2, v5}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v9

    const-string v5, "requestProof"

    invoke-virtual {v2, v5}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    const-string v5, "windowBytes"

    invoke-virtual {v2, v5}, Lorg/json/JSONObject;->getInt(Ljava/lang/String;)I

    move-result v11

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$000(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Z

    move-result v12

    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationRelayTls;->createMultiplayer()Ljavax/net/ssl/SSLSocketFactory;

    move-result-object v14

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel$1;

    invoke-direct {v2, v0, v1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel$1;-><init>(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)V

    .line 31
    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$100(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)I

    move-result v17

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$000(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Z

    move-result v5

    if-eqz v5, :cond_4

    move/from16 v18, v4

    goto :goto_3

    :cond_4
    move/from16 v18, v6

    :goto_3
    move-object v7, v15

    move/from16 v13, p3

    move-object v4, v15

    move-object v15, v2

    move-object/from16 v16, v3

    invoke-direct/range {v7 .. v18}, Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel;-><init>(Ljava/net/URI;Ljava/lang/String;Ljava/lang/String;IZILjavax/net/ssl/SSLSocketFactory;Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel$Listener;Lorg/emulationstation/frontend/netplay/StationMultiplayerEndpoint;II)V

    iput-object v4, v0, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;->tunnel:Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel;

    .line 32
    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->access$000(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)Z

    move-result v2

    if-eqz v2, :cond_5

    if-nez v3, :cond_5

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel$2;

    invoke-direct {v2, v0, v1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel$2;-><init>(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession$Channel;Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;)V

    invoke-virtual {v4, v2}, Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel;->socketBinding(Lorg/emulationstation/frontend/netplay/StationMultiplayerTunnel$SocketBinding;)V

    :cond_5
    return-void
.end method
