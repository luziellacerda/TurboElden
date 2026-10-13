.class public final Lorg/emulationstation/frontend/netplay/StationRoomsActivity;
.super Landroid/app/Activity;
.source "StationRoomsActivity.java"

# interfaces
.implements Lorg/emulationstation/frontend/station/StationGraphicsPreferences$Listener;


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;,
        Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;,
        Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;,
        Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoiceAdapter;,
        Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;
    }
.end annotation


# static fields
.field private static final TECHNICAL_COPY:Ljava/util/regex/Pattern;


# instance fields
.field private volatile active:Z

.field private artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

.field private busy:Z

.field private chat:Landroid/widget/EditText;

.field private chatActions:Landroid/widget/LinearLayout;

.field private chatHint:Landroid/widget/TextView;

.field private chatScroll:Landroid/widget/ScrollView;

.field private chatTitle:Landroid/widget/TextView;

.field private choose:Landroid/widget/Button;

.field private volatile client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

.field private codeDialog:Landroid/app/Dialog;

.field private final commands:Ljava/util/concurrent/ExecutorService;

.field private connection:Landroid/widget/TextView;

.field private conversationName:Ljava/lang/String;

.field private conversationPeer:Ljava/lang/String;

.field private create:Landroid/widget/Button;

.field private createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

.field private createGame:Landroid/widget/TextView;

.field private createInfo:Landroid/widget/TextView;

.field private createMessage:Landroid/widget/TextView;

.field private createOverview:Landroid/widget/LinearLayout;

.field private createPanel:Landroid/widget/LinearLayout;

.field private createSetup:Landroid/widget/LinearLayout;

.field private createSynopsis:Landroid/widget/TextView;

.field private creating:Z

.field private final desiredRoomRows:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Landroid/view/View;",
            ">;"
        }
    .end annotation
.end field

.field private final drafts:Ljava/util/Map;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private volatile epoch:I

.field private final events:Ljava/util/concurrent/ExecutorService;

.field private final feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

.field private gamePlatform:Landroid/widget/TextView;

.field private graphics:Lorg/emulationstation/frontend/station/StationGraphicsPreferences;

.field private graphicsStage:Landroid/widget/FrameLayout;

.field private final green:I

.field private headerMetadata:Lorg/json/JSONObject;

.field private headerPlayers:Landroid/widget/TextView;

.field private headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

.field private heroBitmap:Landroid/graphics/Bitmap;

.field private heroCover:Landroid/widget/ImageView;

.field private heroEpoch:I

.field private heroFactDetail:Ljava/lang/String;

.field private heroFactSummary:Ljava/lang/String;

.field private heroOnlineDetail:Ljava/lang/String;

.field private heroOnlinePlayers:Ljava/lang/String;

.field private heroRequestId:Ljava/lang/String;

.field private heroSymbol:Lorg/emulationstation/frontend/netplay/StationLobbyIcon;

.field private heroSynopsis:Ljava/lang/String;

.field private hyperspace:Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

.field private inboxNotice:Landroid/widget/TextView;

.field private inspectedName:Ljava/lang/String;

.field private inspectedPeer:Ljava/lang/String;

.field private inviteNavigation:Landroid/widget/Button;

.field private lastMessageId:Ljava/lang/String;

.field private launchKey:Ljava/lang/String;

.field private launching:Z

.field private leave:Landroid/widget/Button;

.field private leftPanel:Landroid/widget/LinearLayout;

.field private messages:Landroid/widget/LinearLayout;

.field private middlePanel:Landroid/widget/LinearLayout;

.field private final multiplayerEvents:Ljava/util/concurrent/ScheduledExecutorService;

.field private volatile multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

.field private volatile multiplayerPollEpoch:I

.field private multiplayerPolling:Ljava/util/concurrent/ScheduledFuture;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/concurrent/ScheduledFuture<",
            "*>;"
        }
    .end annotation
.end field

.field private final muted:I

.field private narrow:Z

.field private final nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

.field private navChat:Landroid/widget/Button;

.field private navCreate:Landroid/widget/Button;

.field private navPeople:Landroid/widget/Button;

.field private navRooms:Landroid/widget/Button;

.field private nickname:Landroid/widget/EditText;

.field private ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

.field private ownRoomCoverItem:Ljava/lang/String;

.field private ownRoomFooter:Landroid/widget/LinearLayout;

.field private volatile page:I

.field private painted:J

.field private paintedMessages:I

.field private paintedPage:I

.field private paintedRoom:Ljava/lang/String;

.field private paintedRoomPage:I

.field private peerFeedback:Ljava/lang/String;

.field private peerScroll:Landroid/widget/ScrollView;

.field private peerTitle:Landroid/widget/TextView;

.field private peers:Landroid/widget/LinearLayout;

.field private pendingName:Ljava/lang/String;

.field private pendingNavigation:Landroid/content/Intent;

.field private pendingPeer:Ljava/lang/String;

.field private playerSearch:Landroid/widget/EditText;

.field private playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

.field private polling:Ljava/util/concurrent/Future;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/concurrent/Future<",
            "*>;"
        }
    .end annotation
.end field

.field private prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

.field private profileEpoch:I

.field private profileRequestId:Ljava/lang/String;

.field private ready:Landroid/widget/Button;

.field private final requests:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Lorg/emulationstation/frontend/station/StationApi$Cancellation;",
            ">;"
        }
    .end annotation
.end field

.field private retry:Landroid/widget/Button;

.field private returningFromGame:Z

.field private returningRecovery:Z

.field private rightPanel:Landroid/widget/LinearLayout;

.field private volatile roomPage:I

.field private roomReadiness:Landroid/widget/TextView;

.field private final roomRows:Ljava/util/Map;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;",
            ">;"
        }
    .end annotation
.end field

.field private roomScroll:Landroid/widget/ScrollView;

.field private roomTitle:Landroid/widget/TextView;

.field private rooms:Landroid/widget/LinearLayout;

.field private final roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

.field private section:I

.field private final seenMessages:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private selectedItem:Ljava/lang/String;

.field private send:Landroid/widget/Button;

.field private setupBack:Landroid/widget/Button;

.field private setupCapacity:I

.field private setupConfirm:Landroid/widget/Button;

.field private setupContext:Ljava/lang/String;

.field private final setupCountLabels:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Landroid/widget/TextView;",
            ">;"
        }
    .end annotation
.end field

.field private setupCounts:Landroid/widget/LinearLayout;

.field private setupDescription:Landroid/widget/TextView;

.field private final setupModeLabels:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Landroid/widget/TextView;",
            ">;"
        }
    .end annotation
.end field

.field private setupModes:Landroid/widget/LinearLayout;

.field private setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

.field private final setupProfiles:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;",
            ">;"
        }
    .end annotation
.end field

.field private start:Landroid/widget/Button;

.field private final state:Lorg/emulationstation/frontend/netplay/StationRoomState;

.field private status:Landroid/widget/TextView;

.field private subtitle:Landroid/widget/TextView;

.field private title:Landroid/widget/TextView;

.field private final usedRoomRows:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private waves:Lorg/emulationstation/frontend/station/StationWaveBackground;

.field private final white:I


# direct methods
.method static constructor <clinit>()V
    .locals 1

    const-string v0, "(?iu)\\b(?:github|gitlab|bitbucket|git|handoff|commit|reposit[o\u00f3]rio|branch|sha256|sha-256|endpoint|runtime|dex|dll|servidor)\\b|^\\s*(?:fontes(?: do modo)?|refer[e\u00ea]ncias|suporte confirmado na documenta[c\u00e7][a\u00e3]o)\\s*[:\\s]"

    .line 237
    invoke-static {v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;

    move-result-object v0

    sput-object v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->TECHNICAL_COPY:Ljava/util/regex/Pattern;

    return-void
.end method

.method public constructor <init>()V
    .locals 3

    .line 19
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    .line 20
    invoke-static {}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor()Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->commands:Ljava/util/concurrent/ExecutorService;

    .line 21
    invoke-static {}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor()Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->events:Ljava/util/concurrent/ExecutorService;

    .line 22
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-direct {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    .line 23
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    invoke-direct {v0}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    .line 24
    new-instance v0, Ljava/util/HashSet;

    invoke-direct {v0}, Ljava/util/HashSet;-><init>()V

    invoke-static {v0}, Ljava/util/Collections;->synchronizedSet(Ljava/util/Set;)Ljava/util/Set;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    .line 27
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    invoke-direct {v0}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;-><init>()V

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    const-string v0, ""

    .line 28
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchKey:Ljava/lang/String;

    .line 30
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedRoom:Ljava/lang/String;

    .line 32
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->lastMessageId:Ljava/lang/String;

    .line 35
    new-instance v1, Ljava/util/ArrayList;

    invoke-direct {v1}, Ljava/util/ArrayList;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    .line 36
    new-instance v1, Ljava/util/ArrayList;

    invoke-direct {v1}, Ljava/util/ArrayList;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeLabels:Ljava/util/List;

    new-instance v1, Ljava/util/ArrayList;

    invoke-direct {v1}, Ljava/util/ArrayList;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCountLabels:Ljava/util/List;

    .line 37
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    .line 38
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCoverItem:Ljava/lang/String;

    .line 45
    new-instance v1, Ljava/util/LinkedHashMap;

    invoke-direct {v1}, Ljava/util/LinkedHashMap;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    .line 46
    new-instance v1, Ljava/util/ArrayList;

    invoke-direct {v1}, Ljava/util/ArrayList;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    .line 47
    new-instance v1, Ljava/util/HashSet;

    invoke-direct {v1}, Ljava/util/HashSet;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    .line 48
    new-instance v1, Ljava/util/HashMap;

    invoke-direct {v1}, Ljava/util/HashMap;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->drafts:Ljava/util/Map;

    .line 49
    new-instance v1, Ljava/util/LinkedHashSet;

    invoke-direct {v1}, Ljava/util/LinkedHashSet;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->seenMessages:Ljava/util/Set;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingName:Ljava/lang/String;

    .line 51
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-direct {v1}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;-><init>()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    .line 53
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedPeer:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedName:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    .line 55
    invoke-static {}, Ljava/util/concurrent/Executors;->newSingleThreadScheduledExecutor()Ljava/util/concurrent/ScheduledExecutorService;

    move-result-object v1

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerEvents:Ljava/util/concurrent/ScheduledExecutorService;

    const-wide/16 v1, -0x1

    .line 59
    iput-wide v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    const/4 v1, -0x1

    iput v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedPage:I

    iput v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedRoomPage:I

    .line 60
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    iput v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroEpoch:I

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileRequestId:Ljava/lang/String;

    iput v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileEpoch:I

    .line 61
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactSummary:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactDetail:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlineDetail:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlinePlayers:Ljava/lang/String;

    .line 62
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroSynopsis:Ljava/lang/String;

    const v0, -0xb92401

    .line 64
    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->green:I

    const v0, -0x100a01

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->white:I

    const v0, -0x554736

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->muted:I

    return-void
.end method

.method static synthetic access$000(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)Lorg/emulationstation/frontend/netplay/StationRoomState;
    .locals 0

    .line 19
    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    return-object p0
.end method

.method static synthetic access$100(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V
    .locals 0

    .line 19
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderPlayers(Lorg/json/JSONObject;)V

    return-void
.end method

.method static synthetic access$1000(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;)V
    .locals 0

    .line 19
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->invitePlayer(Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$1100(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;)V
    .locals 0

    .line 19
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->joinPlayer(Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$1200(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V
    .locals 0

    .line 19
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showRoomCode()V

    return-void
.end method

.method static synthetic access$1300(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;)V
    .locals 0

    .line 19
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->confirmBlock(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$200(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;F)I
    .locals 0

    .line 19
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p0

    return p0
.end method

.method static synthetic access$300(I[III)[I
    .locals 0

    .line 19
    invoke-static {p0, p1, p2, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomControlLayout(I[III)[I

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$400(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)Landroid/widget/LinearLayout;
    .locals 0

    .line 19
    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    return-object p0
.end method

.method static synthetic access$500(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V
    .locals 0

    .line 19
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateOwnRoomHeight()V

    return-void
.end method

.method static synthetic access$600(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)Landroid/widget/LinearLayout;
    .locals 0

    .line 19
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$700(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)Landroid/widget/LinearLayout;
    .locals 0

    .line 19
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$800(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;
    .locals 0

    .line 19
    invoke-direct {p0, p1, p2, p3, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$900(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)Lorg/emulationstation/frontend/netplay/StationRoomArtwork;
    .locals 0

    .line 19
    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    return-object p0
.end method

.method private action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V
    .locals 1

    const/4 v0, 0x0

    .line 546
    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    return-void
.end method

.method private action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V
    .locals 8

    .line 547
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x1

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->begin()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateRoomSetupEnabled()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    iget v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    new-instance v5, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-direct {v5}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;-><init>()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v5}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    .line 548
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->commands:Ljava/util/concurrent/ExecutorService;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda23;

    move-object v2, v1

    move-object v3, p0

    move-object v4, p1

    move-object v7, p2

    invoke-direct/range {v2 .. v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda23;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Lorg/emulationstation/frontend/station/StationApi$Cancellation;ILjava/lang/Runnable;)V

    invoke-interface {v0, v1}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private actionLine(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;
    .locals 4

    .line 356
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v2, 0x42400000    # 48.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    const/4 v3, -0x1

    invoke-direct {v1, v3, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-object v0
.end method

.method private addSynopsis(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/String;)V
    .locals 3

    .line 292
    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->synopsisFor(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const/16 v1, 0xc

    const v2, -0x554736

    invoke-direct {p0, p1, v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    invoke-virtual {v0, p3}, Landroid/widget/TextView;->setMaxLines(I)V

    sget-object v1, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    const/high16 v1, 0x3f800000    # 1.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    int-to-float v2, v2

    invoke-virtual {v0, v2, v1}, Landroid/widget/TextView;->setLineSpacing(FF)V

    .line 293
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda79;

    invoke-direct {v1, p0, p2, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda79;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    const/4 v0, 0x2

    if-gt p3, v0, :cond_0

    const/16 p3, 0xb

    const v0, -0xb92401

    const-string v1, "Ver detalhes"

    .line 294
    invoke-direct {p0, p1, v1, p3, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    const/high16 p3, 0x40400000    # 3.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    const/high16 v0, 0x40e00000    # 7.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/4 v1, 0x0

    invoke-virtual {p1, v1, p3, v1, v0}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance p3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda80;

    invoke-direct {p3, p0, p2, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda80;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {p1, p3}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    :cond_0
    return-void
.end method

.method private applyChoiceFace(Landroid/widget/TextView;Z)V
    .locals 2

    .line 624
    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choiceFace(Z)Landroid/graphics/drawable/Drawable;

    move-result-object p2

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setBackground(Landroid/graphics/drawable/Drawable;)V

    const/high16 p2, 0x41400000    # 12.0f

    .line 627
    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/4 v1, 0x0

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p2

    invoke-virtual {p1, v0, v1, p2, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    return-void
.end method

.method private applyGraphics()V
    .locals 5

    .line 407
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->graphics:Lorg/emulationstation/frontend/station/StationGraphicsPreferences;

    if-nez v0, :cond_0

    return-void

    .line 408
    :cond_0
    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationGraphicsPreferences;->effectiveBackgroundMode()I

    move-result v0

    .line 409
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->hyperspace:Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

    const/4 v2, 0x0

    const/16 v3, 0x8

    if-eqz v1, :cond_2

    if-nez v0, :cond_1

    move v4, v2

    goto :goto_0

    :cond_1
    move v4, v3

    :goto_0
    invoke-virtual {v1, v4}, Lorg/emulationstation/frontend/netplay/StationHyperspaceView;->setVisibility(I)V

    .line 410
    :cond_2
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->waves:Lorg/emulationstation/frontend/station/StationWaveBackground;

    if-eqz v1, :cond_4

    const/4 v4, 0x1

    if-ne v0, v4, :cond_3

    goto :goto_1

    :cond_3
    move v2, v3

    :goto_1
    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/station/StationWaveBackground;->setVisibility(I)V

    .line 411
    :cond_4
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->graphicsStage:Landroid/widget/FrameLayout;

    if-eqz v0, :cond_5

    const v1, -0xd7814b

    invoke-virtual {v0, v1}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    :cond_5
    return-void
.end method

.method private applyPendingNavigation(Lorg/json/JSONObject;)V
    .locals 8

    .line 71
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingNavigation:Landroid/content/Intent;

    if-eqz v0, :cond_3

    if-eqz p1, :cond_3

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v1, :cond_3

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    if-eqz v1, :cond_0

    goto :goto_1

    :cond_0
    const/4 v1, 0x0

    .line 72
    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingNavigation:Landroid/content/Intent;

    const-string v2, "station.itemId"

    .line 73
    invoke-virtual {v0, v2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    if-eqz v2, :cond_2

    const-string v3, "room"

    .line 74
    invoke-virtual {p1, v3}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v3

    const/4 v4, 0x0

    const/4 v5, 0x1

    if-eqz v3, :cond_1

    move v3, v5

    goto :goto_0

    :cond_1
    move v3, v4

    :goto_0
    iget-boolean v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    iget-boolean v7, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    invoke-static {v5, v3, v6, v7}, Lorg/emulationstation/frontend/auth/StationTaskPolicy;->canSelectItem(ZZZZ)Z

    move-result v3

    if-eqz v3, :cond_2

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-nez v3, :cond_2

    .line 75
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    :cond_2
    const-string v1, "station.peerId"

    .line 77
    invoke-virtual {v0, v1}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_3

    .line 78
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_3

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-virtual {v1, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;->resolveName(Lorg/json/JSONObject;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->openConversation(Ljava/lang/String;Ljava/lang/String;)V

    :cond_3
    :goto_1
    return-void
.end method

.method private beginMultiplayerDiscovery(Lorg/emulationstation/frontend/netplay/StationOnlineClient;I)V
    .locals 3

    .line 487
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_1

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p2, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq v0, p1, :cond_0

    goto :goto_0

    .line 488
    :cond_0
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    .line 489
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerEvents:Ljava/util/concurrent/ScheduledExecutorService;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda66;

    invoke-direct {v2, p0, p2, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda66;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;IILorg/emulationstation/frontend/netplay/StationOnlineClient;)V

    const-wide/16 p1, 0x0

    sget-object v0, Ljava/util/concurrent/TimeUnit;->MILLISECONDS:Ljava/util/concurrent/TimeUnit;

    invoke-interface {v1, v2, p1, p2, v0}, Ljava/util/concurrent/ScheduledExecutorService;->schedule(Ljava/lang/Runnable;JLjava/util/concurrent/TimeUnit;)Ljava/util/concurrent/ScheduledFuture;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPolling:Ljava/util/concurrent/ScheduledFuture;

    :cond_1
    :goto_0
    return-void
.end method

.method private beginRoomRows()V
    .locals 2

    .line 304
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    invoke-interface {v0}, Ljava/util/Set;->clear()V

    const/4 v0, 0x0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    const-string v1, ""

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCoverItem:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->start:Landroid/widget/Button;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomReadiness:Landroid/widget/TextView;

    return-void
.end method

.method private bg(II)Landroid/graphics/drawable/GradientDrawable;
    .locals 1

    .line 89
    new-instance v0, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v0}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    const/high16 p1, 0x40800000    # 4.0f

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p1

    int-to-float p1, p1

    invoke-virtual {v0, p1}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    const/high16 p1, 0x3f800000    # 1.0f

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p1

    invoke-virtual {v0, p1, p2}, Landroid/graphics/drawable/GradientDrawable;->setStroke(II)V

    return-object v0
.end method

.method private bindHeroCover()V
    .locals 4

    .line 297
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz v0, :cond_0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->coverPlatform(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setPlatform(Ljava/lang/String;)V

    .line 298
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz v0, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCoverItem:Ljava/lang/String;

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->coverPlatform(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setPlatform(Ljava/lang/String;)V

    .line 299
    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroCover:Landroid/widget/ImageView;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroBitmap:Landroid/graphics/Bitmap;

    invoke-virtual {v0, v1}, Landroid/widget/ImageView;->setImageBitmap(Landroid/graphics/Bitmap;)V

    .line 300
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    const/4 v1, 0x0

    if-eqz v0, :cond_3

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_2

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroBitmap:Landroid/graphics/Bitmap;

    goto :goto_0

    :cond_2
    move-object v2, v1

    :goto_0
    invoke-virtual {v0, v2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    .line 301
    :cond_3
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz v0, :cond_5

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCoverItem:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_4

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroBitmap:Landroid/graphics/Bitmap;

    :cond_4
    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    :cond_5
    return-void
.end method

.method private bold(Landroid/widget/TextView;)V
    .locals 2

    const-string v0, "sans-serif-condensed"

    const/4 v1, 0x1

    .line 94
    invoke-static {v0, v1}, Landroid/graphics/Typeface;->create(Ljava/lang/String;I)Landroid/graphics/Typeface;

    move-result-object v0

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    return-void
.end method

.method private build()V
    .locals 16

    move-object/from16 v6, p0

    .line 139
    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    const v1, -0xf9f7f3

    invoke-virtual {v0, v1}, Landroid/view/Window;->setStatusBarColor(I)V

    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0, v1}, Landroid/view/Window;->setNavigationBarColor(I)V

    .line 140
    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const/16 v1, 0x1006

    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V

    .line 141
    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    const/16 v1, 0x10

    invoke-virtual {v0, v1}, Landroid/view/Window;->setSoftInputMode(I)V

    .line 142
    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getConfiguration()Landroid/content/res/Configuration;

    move-result-object v0

    iget v0, v0, Landroid/content/res/Configuration;->screenWidthDp:I

    const/16 v2, 0x2f8

    const/4 v7, 0x1

    const/4 v8, 0x0

    if-ge v0, v2, :cond_0

    move v0, v7

    goto :goto_0

    :cond_0
    move v0, v8

    :goto_0
    iput-boolean v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->narrow:Z

    .line 143
    new-instance v0, Landroid/widget/FrameLayout;

    invoke-direct {v0, v6}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->graphicsStage:Landroid/widget/FrameLayout;

    const v2, -0xd7814b

    invoke-virtual {v0, v2}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationHyperspaceView;-><init>(Landroid/content/Context;)V

    iput-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->hyperspace:Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

    .line 144
    new-instance v3, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v4, -0x1

    invoke-direct {v3, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v2, v3}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 145
    new-instance v2, Lorg/emulationstation/frontend/station/StationWaveBackground;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/station/StationWaveBackground;-><init>(Landroid/content/Context;)V

    iput-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->waves:Lorg/emulationstation/frontend/station/StationWaveBackground;

    const/16 v3, 0x8

    invoke-virtual {v2, v3}, Lorg/emulationstation/frontend/station/StationWaveBackground;->setVisibility(I)V

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->waves:Lorg/emulationstation/frontend/station/StationWaveBackground;

    new-instance v5, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v5, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v2, v5}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyGraphics()V

    .line 146
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v2

    new-instance v5, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v5, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v2, v5}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-virtual {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setContentView(Landroid/view/View;)V

    .line 147
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    const/high16 v5, 0x41200000    # 10.0f

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v11

    const/high16 v12, 0x41000000    # 8.0f

    invoke-direct {v6, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    invoke-virtual {v0, v9, v10, v11, v13}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const v9, -0x6f9f7f3

    invoke-virtual {v0, v9}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    .line 148
    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    iget-boolean v10, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->narrow:Z

    if-eqz v10, :cond_1

    const/high16 v10, 0x43160000    # 150.0f

    goto :goto_1

    :cond_1
    const/high16 v10, 0x43280000    # 168.0f

    :goto_1
    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-direct {v9, v10, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v0, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const-string v9, "JOGAR ONLINE"

    const/16 v10, 0x12

    const v11, -0x100a01

    .line 150
    invoke-direct {v6, v0, v9, v10, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v9

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const v13, 0x3d23d70a    # 0.04f

    invoke-virtual {v9, v13}, Landroid/widget/TextView;->setLetterSpacing(F)V

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    const/high16 v14, 0x40000000    # 2.0f

    invoke-direct {v6, v14}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v14

    const/high16 v15, 0x40c00000    # 6.0f

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-virtual {v9, v13, v14, v8, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 151
    new-instance v1, Landroid/widget/EditText;

    invoke-direct {v1, v6}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    const-string v9, "Seu nome online"

    invoke-direct {v6, v1, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->field(Landroid/widget/EditText;Ljava/lang/String;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    const/4 v9, 0x0

    invoke-virtual {v1, v9}, Landroid/widget/EditText;->setBackground(Landroid/graphics/drawable/Drawable;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    const/high16 v13, 0x41300000    # 11.0f

    invoke-virtual {v1, v13}, Landroid/widget/EditText;->setTextSize(F)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v14

    invoke-virtual {v1, v13, v8, v14, v8}, Landroid/widget/EditText;->setPadding(IIII)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    invoke-virtual {v1, v7}, Landroid/widget/EditText;->setSingleLine(Z)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    new-array v13, v7, [Landroid/text/InputFilter;

    new-instance v14, Landroid/text/InputFilter$LengthFilter;

    const/16 v10, 0x18

    invoke-direct {v14, v10}, Landroid/text/InputFilter$LengthFilter;-><init>(I)V

    aput-object v14, v13, v8

    invoke-virtual {v1, v13}, Landroid/widget/EditText;->setFilters([Landroid/text/InputFilter;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    const-string v10, "station-online-profile"

    invoke-virtual {v6, v10, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v10

    const-string v13, "nickname"

    const-string v14, "Jogador"

    invoke-interface {v10, v13, v14}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    invoke-virtual {v1, v10}, Landroid/widget/EditText;->setText(Ljava/lang/CharSequence;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    new-instance v10, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v13, 0x42300000    # 44.0f

    invoke-direct {v6, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    invoke-direct {v10, v4, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v10}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 152
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    const-string v10, "Seu nome online. Use Reconectar para atualizar."

    invoke-virtual {v1, v10}, Landroid/widget/EditText;->setContentDescription(Ljava/lang/CharSequence;)V

    const-string v1, "\u25cb  Conectando"

    const/16 v10, 0xb

    const v13, -0x554736

    .line 153
    invoke-direct {v6, v0, v1, v10, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->connection:Landroid/widget/TextView;

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v14

    const/high16 v10, 0x40800000    # 4.0f

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v11

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v12

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-virtual {v1, v14, v11, v12, v3}, Landroid/widget/TextView;->setPadding(IIII)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->connection:Landroid/widget/TextView;

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 154
    new-instance v1, Landroid/widget/ScrollView;

    invoke-direct {v1, v6}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v1, v8}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v3

    new-instance v11, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v12, -0x2

    invoke-direct {v11, v4, v12}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v3, v11}, Landroid/widget/ScrollView;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance v11, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v14, 0x3f800000    # 1.0f

    invoke-direct {v11, v4, v8, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v0, v1, v11}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 155
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda29;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda29;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v11, "Salas"

    invoke-direct {v6, v3, v11, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navRooms:Landroid/widget/Button;

    invoke-direct {v6, v1, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 156
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda35;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda35;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v11, "Pessoas"

    invoke-direct {v6, v3, v11, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navPeople:Landroid/widget/Button;

    invoke-direct {v6, v1, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 157
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda36;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda36;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v11, "Criar sala"

    invoke-direct {v6, v3, v11, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navCreate:Landroid/widget/Button;

    const/4 v11, 0x2

    invoke-direct {v6, v1, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 158
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda37;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda37;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v9, "Conversas"

    invoke-direct {v6, v3, v9, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navChat:Landroid/widget/Button;

    const/4 v9, 0x3

    invoke-direct {v6, v1, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 159
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navRooms:Landroid/widget/Button;

    iget-object v9, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navPeople:Landroid/widget/Button;

    iget-object v7, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navCreate:Landroid/widget/Button;

    iget-object v12, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navChat:Landroid/widget/Button;

    filled-new-array {v1, v9, v7, v12}, [Landroid/widget/Button;

    move-result-object v1

    move v7, v8

    :goto_2
    const/4 v9, 0x4

    if-ge v7, v9, :cond_2

    aget-object v9, v1, v7

    const/16 v12, 0x13

    invoke-virtual {v9, v12}, Landroid/widget/Button;->setGravity(I)V

    const/high16 v12, 0x41400000    # 12.0f

    invoke-virtual {v9, v12}, Landroid/widget/Button;->setTextSize(F)V

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v12

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v11

    invoke-virtual {v9, v12, v8, v11, v8}, Landroid/widget/Button;->setPadding(IIII)V

    add-int/lit8 v7, v7, 0x1

    const/4 v11, 0x2

    goto :goto_2

    :cond_2
    const-string v1, "LZ GAMES \u00b7 COMUNIDADE"

    const/16 v7, 0x8

    .line 161
    invoke-direct {v6, v3, v1, v7, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    const v7, 0x3da3d70a    # 0.08f

    invoke-virtual {v1, v7}, Landroid/widget/TextView;->setLetterSpacing(F)V

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v7

    const/high16 v9, 0x40000000    # 2.0f

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-virtual {v1, v7, v9, v8, v10}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 162
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda38;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda38;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v7, "Usar convite"

    invoke-direct {v6, v3, v7, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inviteNavigation:Landroid/widget/Button;

    const/4 v7, 0x4

    invoke-direct {v6, v1, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 163
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda39;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda39;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v7, "Reconectar"

    invoke-direct {v6, v3, v7, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->retry:Landroid/widget/Button;

    const/4 v3, 0x5

    invoke-direct {v6, v1, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 164
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda40;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda40;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v3, "Voltar"

    invoke-direct {v6, v0, v3, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v0

    const/4 v1, 0x6

    invoke-direct {v6, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    .line 165
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v7

    const/high16 v0, 0x41600000    # 14.0f

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    const/high16 v3, 0x41600000    # 14.0f

    invoke-direct {v6, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    const/high16 v9, 0x41000000    # 8.0f

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-virtual {v7, v0, v1, v3, v10}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    new-instance v0, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v0, v8, v4, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v2, v7, v0}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 166
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v2, 0x42800000    # 64.0f

    invoke-direct {v6, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-direct {v1, v4, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v7, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 167
    new-instance v1, Landroid/widget/FrameLayout;

    invoke-direct {v1, v6}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v3, 0x42000000    # 32.0f

    invoke-direct {v6, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    const/high16 v9, 0x42200000    # 40.0f

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-direct {v2, v3, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationLobbyIcon;

    const/4 v3, 0x2

    invoke-direct {v2, v6, v3}, Lorg/emulationstation/frontend/netplay/StationLobbyIcon;-><init>(Landroid/content/Context;I)V

    iput-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroSymbol:Lorg/emulationstation/frontend/netplay/StationLobbyIcon;

    new-instance v3, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v3, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v2, v3}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance v2, Landroid/widget/ImageView;

    invoke-direct {v2, v6}, Landroid/widget/ImageView;-><init>(Landroid/content/Context;)V

    iput-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroCover:Landroid/widget/ImageView;

    sget-object v3, Landroid/widget/ImageView$ScaleType;->FIT_CENTER:Landroid/widget/ImageView$ScaleType;

    invoke-virtual {v2, v3}, Landroid/widget/ImageView;->setScaleType(Landroid/widget/ImageView$ScaleType;)V

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroCover:Landroid/widget/ImageView;

    new-instance v3, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v3, v4, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v2, v3}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 168
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v1

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v3, -0x2

    invoke-direct {v2, v8, v3, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    const/high16 v3, 0x41400000    # 12.0f

    invoke-direct {v6, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    const/high16 v9, 0x41400000    # 12.0f

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v2, v3, v8, v9, v8}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const-string v0, "PARTIDAS ONLINE"

    const/16 v2, 0xa

    const v3, -0xb92401

    .line 170
    invoke-direct {v6, v0, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->title:Landroid/widget/TextView;

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->title:Landroid/widget/TextView;

    const v9, 0x3dcccccd    # 0.1f

    invoke-virtual {v0, v9}, Landroid/widget/TextView;->setLetterSpacing(F)V

    .line 171
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->title:Landroid/widget/TextView;

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v10, 0x41800000    # 16.0f

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-direct {v9, v4, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 172
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    if-nez v0, :cond_3

    const-string v0, "Escolha uma sala ou converse com algu\u00e9m"

    goto :goto_3

    :cond_3
    const-string v0, "Preparando seu jogo\u2026"

    :goto_3
    const v9, -0x100a01

    const/16 v10, 0x12

    invoke-direct {v6, v0, v10, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    const/4 v9, 0x1

    invoke-virtual {v0, v9}, Landroid/widget/TextView;->setSingleLine(Z)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    sget-object v9, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v0, v9}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 173
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v10, 0x41c00000    # 24.0f

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-direct {v9, v4, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 174
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v10, 0x41c00000    # 24.0f

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-direct {v9, v4, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 175
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationGameRatingView;-><init>(Landroid/content/Context;)V

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v9, 0x42b40000    # 90.0f

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    const/high16 v10, 0x41c00000    # 24.0f

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-direct {v1, v9, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v1, v8, v8, v9, v8}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    iget-object v9, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    invoke-virtual {v0, v9, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const-string v1, "\u2014"

    .line 176
    invoke-direct {v6, v1, v2, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    const/16 v9, 0x10

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setGravity(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    const/4 v9, 0x1

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setSingleLine(Z)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    sget-object v10, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v1, v10}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    new-instance v10, Lorg/emulationstation/frontend/netplay/StationSocialIcon;

    const/high16 v11, 0x41700000    # 15.0f

    invoke-direct {v6, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v11

    invoke-direct {v10, v9, v11, v3}, Lorg/emulationstation/frontend/netplay/StationSocialIcon;-><init>(III)V

    const/4 v9, 0x0

    invoke-virtual {v1, v10, v9, v9, v9}, Landroid/widget/TextView;->setCompoundDrawablesWithIntrinsicBounds(Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    const/high16 v9, 0x40a00000    # 5.0f

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setCompoundDrawablePadding(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v9, v8, v4, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v0, v1, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const-string v1, ""

    .line 177
    invoke-direct {v6, v1, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    const/4 v9, 0x1

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setSingleLine(Z)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    sget-object v9, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    const/16 v9, 0x10

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setGravity(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v1, v9, v8, v8, v8}, Landroid/widget/TextView;->setPadding(IIII)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v9, v8, v4, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v0, v1, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 178
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v1, v4, v8, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    iput v5, v1, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    invoke-virtual {v7, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const v1, 0x3ee147ae    # 0.44f

    .line 179
    invoke-direct {v6, v0, v1, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->panel(Landroid/widget/LinearLayout;FZ)Landroid/widget/LinearLayout;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->leftPanel:Landroid/widget/LinearLayout;

    const v1, 0x3ee147ae    # 0.44f

    invoke-direct {v6, v0, v1, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->panel(Landroid/widget/LinearLayout;FZ)Landroid/widget/LinearLayout;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    const v1, 0x3ee147ae    # 0.44f

    invoke-direct {v6, v0, v1, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->panel(Landroid/widget/LinearLayout;FZ)Landroid/widget/LinearLayout;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createPanel:Landroid/widget/LinearLayout;

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v1, v5, v8, v9, v8}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const v1, 0x3f0f5c29    # 0.56f

    invoke-direct {v6, v0, v1, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->panel(Landroid/widget/LinearLayout;FZ)Landroid/widget/LinearLayout;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    .line 180
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda41;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda41;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addOnLayoutChangeListener(Landroid/view/View$OnLayoutChangeListener;)V

    .line 181
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->leftPanel:Landroid/widget/LinearLayout;

    const-string v1, "PESSOAS ONLINE"

    const/16 v5, 0xc

    invoke-direct {v6, v0, v1, v5, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerTitle:Landroid/widget/TextView;

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    .line 182
    new-instance v0, Landroid/widget/EditText;

    invoke-direct {v0, v6}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSearch:Landroid/widget/EditText;

    const-string v1, "Buscar nesta p\u00e1gina"

    invoke-direct {v6, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->field(Landroid/widget/EditText;Ljava/lang/String;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSearch:Landroid/widget/EditText;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/EditText;->setSingleLine(Z)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSearch:Landroid/widget/EditText;

    new-array v9, v1, [Landroid/text/InputFilter;

    new-instance v1, Landroid/text/InputFilter$LengthFilter;

    const/16 v10, 0x30

    invoke-direct {v1, v10}, Landroid/text/InputFilter$LengthFilter;-><init>(I)V

    aput-object v1, v9, v8

    invoke-virtual {v0, v9}, Landroid/widget/EditText;->setFilters([Landroid/text/InputFilter;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->leftPanel:Landroid/widget/LinearLayout;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSearch:Landroid/widget/EditText;

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v10, 0x42400000    # 48.0f

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v11

    invoke-direct {v9, v4, v11}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 183
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->leftPanel:Landroid/widget/LinearLayout;

    invoke-direct {v6, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->scroll(Landroid/widget/LinearLayout;Landroid/widget/LinearLayout;)Landroid/widget/ScrollView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerScroll:Landroid/widget/ScrollView;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    .line 184
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSearch:Landroid/widget/EditText;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$1;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$1;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/EditText;->addTextChangedListener(Landroid/text/TextWatcher;)V

    .line 185
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    const-string v1, "VER SALAS"

    invoke-direct {v6, v0, v1, v5, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomTitle:Landroid/widget/TextView;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setVisibility(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v0, v1, v8, v9, v8}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    invoke-direct {v6, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->scroll(Landroid/widget/LinearLayout;Landroid/widget/LinearLayout;)Landroid/widget/ScrollView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomScroll:Landroid/widget/ScrollView;

    invoke-virtual {v0, v8, v8, v8, v8}, Landroid/widget/ScrollView;->setPadding(IIII)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomScroll:Landroid/widget/ScrollView;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    .line 186
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createPanel:Landroid/widget/LinearLayout;

    invoke-virtual {v0, v8}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createPanel:Landroid/widget/LinearLayout;

    invoke-virtual {v0, v8, v8, v8, v8}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 187
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-direct {v0, v6}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;-><init>(Landroid/content/Context;)V

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setViewportBounded(Z)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createPanel:Landroid/widget/LinearLayout;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v9, v4, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 188
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->actions:Landroid/widget/LinearLayout;

    const-string v1, "Jogo n\u00e3o selecionado"

    const v9, -0x100a01

    const/16 v11, 0x12

    .line 189
    invoke-direct {v6, v0, v1, v11, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    invoke-direct {v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    const/4 v9, 0x2

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setMaxLines(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    sget-object v11, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v1, v11}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 190
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    const/16 v11, 0x8

    invoke-virtual {v1, v11}, Landroid/widget/TextView;->setVisibility(I)V

    .line 191
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    const/16 v11, 0xe

    const/4 v3, 0x1

    const/16 v12, 0x12

    invoke-virtual {v1, v11, v12, v3, v9}, Landroid/widget/TextView;->setAutoSizeTextTypeUniformWithConfiguration(IIII)V

    .line 192
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v4, v8, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v0, v1, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 193
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    const-string v3, "Sinopse indispon\u00edvel no momento."

    invoke-direct {v6, v1, v3, v5, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSynopsis:Landroid/widget/TextView;

    invoke-virtual {v1, v9}, Landroid/widget/TextView;->setMaxLines(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSynopsis:Landroid/widget/TextView;

    sget-object v3, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 194
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSynopsis:Landroid/widget/TextView;

    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda42;

    invoke-direct {v3, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda42;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 195
    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->pending()Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v1

    iget-object v1, v1, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->detail:Ljava/lang/String;

    invoke-direct {v6, v1, v5, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    const/16 v3, 0x30

    invoke-virtual {v1, v3}, Landroid/widget/TextView;->setGravity(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-virtual {v1, v8, v3, v8, v9}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 196
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    const/4 v3, 0x2

    const/4 v9, 0x1

    invoke-virtual {v1, v2, v5, v9, v3}, Landroid/widget/TextView;->setAutoSizeTextTypeUniformWithConfiguration(IIII)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    sget-object v2, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 197
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v4, v8, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v1, v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 198
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda43;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda43;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 199
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    const-string v2, "Todos precisam da mesma edi\u00e7\u00e3o do jogo."

    const/16 v3, 0xb

    invoke-direct {v6, v1, v2, v3, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    const/4 v2, 0x2

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setMaxLines(I)V

    .line 200
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v1

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-direct {v3, v4, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v1, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 201
    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda30;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda30;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v3, "Escolher jogo"

    invoke-direct {v6, v1, v3, v2, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v2

    iput-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    invoke-direct {v6, v2, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    invoke-direct {v6, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->compactCreateAction(Landroid/widget/Button;)V

    .line 202
    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {v2, v8, v3, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    const/high16 v3, 0x41000000    # 8.0f

    invoke-direct {v6, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    iput v9, v2, Landroid/widget/LinearLayout$LayoutParams;->rightMargin:I

    iget-object v3, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    invoke-virtual {v3, v2}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    .line 203
    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda31;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda31;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v3, "Criar sala"

    const/4 v9, 0x1

    invoke-direct {v6, v1, v3, v2, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const/4 v2, 0x2

    invoke-direct {v6, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    invoke-direct {v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->compactCreateAction(Landroid/widget/Button;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {v2, v8, v3, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    invoke-virtual {v1, v8}, Landroid/widget/Button;->setEnabled(Z)V

    .line 204
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    const-string v2, ""

    invoke-direct {v6, v1, v2, v5, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    const/4 v2, 0x3

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setMaxLines(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    sget-object v2, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    const/16 v2, 0x8

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setVisibility(I)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setAccessibilityLiveRegion(I)V

    .line 205
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda32;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda32;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 206
    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->buildRoomSetup(Landroid/widget/LinearLayout;)V

    .line 207
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    const-string v1, "Suas conversas"

    const/16 v2, 0x11

    const v3, -0x100a01

    invoke-direct {v6, v0, v1, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatTitle:Landroid/widget/TextView;

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    const-string v1, "Selecione uma pessoa ou entre em uma sala"

    const/16 v2, 0xb

    invoke-direct {v6, v0, v1, v2, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatHint:Landroid/widget/TextView;

    .line 208
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    const-string v1, ""

    const v2, -0xb92401

    invoke-direct {v6, v0, v1, v5, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inboxNotice:Landroid/widget/TextView;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setVisibility(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inboxNotice:Landroid/widget/TextView;

    const/high16 v1, 0x41000000    # 8.0f

    invoke-direct {v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-direct {v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-virtual {v0, v8, v2, v8, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inboxNotice:Landroid/widget/TextView;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda33;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda33;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 209
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatActions:Landroid/widget/LinearLayout;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v3, -0x2

    invoke-direct {v2, v4, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    invoke-direct {v6, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->scroll(Landroid/widget/LinearLayout;Landroid/widget/LinearLayout;)Landroid/widget/ScrollView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    .line 210
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v1

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v2, v4, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance v0, Landroid/widget/EditText;

    invoke-direct {v0, v6}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    const-string v2, "Sua mensagem"

    invoke-direct {v6, v0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->field(Landroid/widget/EditText;Ljava/lang/String;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    const/4 v2, 0x3

    invoke-virtual {v0, v2}, Landroid/widget/EditText;->setMaxLines(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    const/16 v2, 0x4001

    invoke-virtual {v0, v2}, Landroid/widget/EditText;->setInputType(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    const/4 v2, 0x1

    new-array v3, v2, [Landroid/text/InputFilter;

    new-instance v2, Landroid/text/InputFilter$LengthFilter;

    const/16 v4, 0x1f4

    invoke-direct {v2, v4}, Landroid/text/InputFilter$LengthFilter;-><init>(I)V

    aput-object v2, v3, v8

    invoke-virtual {v0, v3}, Landroid/widget/EditText;->setFilters([Landroid/text/InputFilter;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    const-string v2, "Escrever mensagem"

    invoke-virtual {v0, v2}, Landroid/widget/EditText;->setContentDescription(Ljava/lang/CharSequence;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v3, 0x42380000    # 46.0f

    invoke-direct {v6, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {v2, v8, v3, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v1, v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const-string v2, ""

    const/16 v3, 0x30

    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda34;

    invoke-direct {v4, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda34;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const/4 v5, 0x1

    move-object/from16 v0, p0

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inline(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->send:Landroid/widget/Button;

    const/16 v1, 0xb

    invoke-direct {v6, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigationIcon(Landroid/widget/Button;I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->send:Landroid/widget/Button;

    const/16 v2, 0x11

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setGravity(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->send:Landroid/widget/Button;

    const-string v2, "Enviar mensagem"

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setContentDescription(Ljava/lang/CharSequence;)V

    const-string v0, "Conectando com sua sess\u00e3o\u2026"

    .line 211
    invoke-direct {v6, v7, v0, v1, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const/4 v1, 0x2

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setMaxLines(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setAccessibilityLiveRegion(I)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadingLobby()V

    invoke-direct {v6, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    .line 212
    invoke-virtual/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getIntent()Landroid/content/Intent;

    move-result-object v0

    const-string v1, "station.peerId"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    if-eqz v0, :cond_4

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    const-string v0, "Jogador"

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    const/4 v0, 0x3

    iput v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    invoke-direct {v6, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    :cond_4
    return-void
.end method

.method private buildRoomSetup(Landroid/widget/LinearLayout;)V
    .locals 7

    .line 578
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v2, 0x3f800000    # 1.0f

    const/4 v3, -0x1

    const/4 v4, 0x0

    invoke-direct {v1, v3, v4, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 579
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    const-string v0, "Partida"

    const/16 v1, 0xb

    const v2, -0xb92401

    invoke-direct {p0, p1, v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/high16 v0, 0x40400000    # 3.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/high16 v5, 0x40000000    # 2.0f

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-virtual {p1, v4, v0, v4, v6}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 580
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomControls(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModes:Landroid/widget/LinearLayout;

    .line 581
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    const-string v0, "Jogadores"

    invoke-direct {p0, p1, v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/high16 v0, 0x40800000    # 4.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {p1, v4, v1, v4, v2}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 582
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomControls(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCounts:Landroid/widget/LinearLayout;

    const/16 p1, 0xc

    const v1, -0x554736

    const-string v2, ""

    .line 583
    invoke-direct {p0, v2, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    const/16 v1, 0x30

    invoke-virtual {p1, v1}, Landroid/widget/TextView;->setGravity(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    const/high16 v1, 0x40a00000    # 5.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    invoke-virtual {p1, v4, v1, v4, v0}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 584
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    const/4 v0, 0x3

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setMaxLines(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    sget-object v0, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 585
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    const-string v0, "Resumo da partida. Toque para ver como jogar."

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setContentDescription(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda99;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda99;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 586
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    const/4 v0, 0x1

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setAccessibilityLiveRegion(I)V

    .line 587
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v2, -0x2

    invoke-direct {v1, v3, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 588
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomControls(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object p1

    const-string v2, "Voltar"

    const/4 v3, 0x6

    .line 589
    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda100;

    invoke-direct {v5, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda100;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    move-object v0, p0

    move-object v1, p1

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupBack:Landroid/widget/Button;

    const-string v2, "Criar sala"

    const/16 v3, 0x8

    const/4 v4, 0x1

    .line 590
    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda101;

    invoke-direct {v5, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda101;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    move-object v0, p0

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupConfirm:Landroid/widget/Button;

    return-void
.end method

.method private button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;
    .locals 2

    .line 102
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationActionButton;

    invoke-direct {v0, p0, p2, p4}, Lorg/emulationstation/frontend/netplay/StationActionButton;-><init>(Landroid/content/Context;Ljava/lang/String;Z)V

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationActionButton;->compactAppearance()V

    invoke-direct {p0, v0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleAction(Landroid/widget/Button;I)V

    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 p4, 0x42400000    # 48.0f

    invoke-direct {p0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p4

    const/4 v1, -0x1

    invoke-direct {p2, v1, p4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda46;

    invoke-direct {p1, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda46;-><init>(Ljava/lang/Runnable;)V

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-object v0
.end method

.method private cancelAll()V
    .locals 3

    .line 457
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->polling:Ljava/util/concurrent/Future;

    if-eqz v0, :cond_0

    const/4 v1, 0x1

    invoke-interface {v0, v1}, Ljava/util/concurrent/Future;->cancel(Z)Z

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    monitor-enter v0

    :try_start_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v1}, Ljava/util/Set;->iterator()Ljava/util/Iterator;

    move-result-object v1

    :goto_0
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_1

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancel()V

    goto :goto_0

    :cond_1
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v1}, Ljava/util/Set;->clear()V

    monitor-exit v0

    return-void

    :catchall_0
    move-exception v1

    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    throw v1
.end method

.method private card(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;
    .locals 5

    .line 117
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    const/high16 v1, 0x41400000    # 12.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    const/high16 v3, 0x41100000    # 9.0f

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-virtual {v0, v2, v4, v1, v3}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const v1, -0xdeae0d2

    const v2, -0xcfbda8

    invoke-direct {p0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v2, -0x1

    const/4 v3, -0x2

    invoke-direct {v1, v2, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    const/high16 v2, 0x41000000    # 8.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    const/4 v3, 0x0

    invoke-virtual {v1, v3, v3, v3, v2}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-object v0
.end method

.method private choiceFace(Z)Landroid/graphics/drawable/Drawable;
    .locals 8

    .line 616
    new-instance v1, Landroid/graphics/drawable/StateListDrawable;

    invoke-direct {v1}, Landroid/graphics/drawable/StateListDrawable;-><init>()V

    const v0, -0xe4ceb0

    const v2, -0xeae0d2

    if-eqz p1, :cond_0

    move v3, v0

    goto :goto_0

    :cond_0
    move v3, v2

    :goto_0
    const v4, -0x100a01

    .line 617
    invoke-direct {p0, v3, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v3

    const/high16 v5, 0x40000000    # 2.0f

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    invoke-virtual {v3, v5, v4}, Landroid/graphics/drawable/GradientDrawable;->setStroke(II)V

    const v5, -0x101009e

    .line 618
    filled-new-array {v5}, [I

    move-result-object v5

    const v6, -0xefe8de

    const v7, -0xddcfbc

    invoke-direct {p0, v6, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v6

    invoke-virtual {v1, v5, v6}, Landroid/graphics/drawable/StateListDrawable;->addState([ILandroid/graphics/drawable/Drawable;)V

    const v5, 0x10100a7

    .line 619
    filled-new-array {v5}, [I

    move-result-object v5

    const v6, -0xcea455

    invoke-direct {p0, v6, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v4

    invoke-virtual {v1, v5, v4}, Landroid/graphics/drawable/StateListDrawable;->addState([ILandroid/graphics/drawable/Drawable;)V

    const v4, 0x101009c

    .line 620
    filled-new-array {v4}, [I

    move-result-object v4

    invoke-virtual {v1, v4, v3}, Landroid/graphics/drawable/StateListDrawable;->addState([ILandroid/graphics/drawable/Drawable;)V

    const/4 v3, 0x0

    new-array v3, v3, [I

    if-eqz p1, :cond_1

    goto :goto_1

    :cond_1
    move v0, v2

    :goto_1
    if-eqz p1, :cond_2

    const p1, -0xb92401

    goto :goto_2

    :cond_2
    const p1, -0xcfbda8

    .line 621
    :goto_2
    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object p1

    invoke-virtual {v1, v3, p1}, Landroid/graphics/drawable/StateListDrawable;->addState([ILandroid/graphics/drawable/Drawable;)V

    new-instance p1, Landroid/graphics/drawable/InsetDrawable;

    const/4 v2, 0x0

    const/high16 v0, 0x41000000    # 8.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    const/4 v4, 0x0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    move-object v0, p1

    invoke-direct/range {v0 .. v5}, Landroid/graphics/drawable/InsetDrawable;-><init>(Landroid/graphics/drawable/Drawable;IIII)V

    return-object p1
.end method

.method private chooseGame()V
    .locals 9

    .line 433
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_7

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_7

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-eqz v0, :cond_0

    goto/16 :goto_3

    .line 434
    :cond_0
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    new-instance v1, Ljava/util/ArrayList;

    invoke-direct {v1}, Ljava/util/ArrayList;-><init>()V

    .line 435
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v2, v2, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->app:Lorg/emulationstation/frontend/station/StationAndroid;

    iget-object v2, v2, Lorg/emulationstation/frontend/station/StationAndroid;->coordinator:Lorg/emulationstation/frontend/station/StationCoordinator;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/station/StationCoordinator;->current()Lorg/emulationstation/frontend/station/StationCoordinator$Library;

    move-result-object v2

    if-nez v2, :cond_1

    return-void

    .line 436
    :cond_1
    iget-object v2, v2, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;

    iget-object v2, v2, Lorg/emulationstation/frontend/station/StationCatalog;->items:Ljava/util/List;

    invoke-interface {v2}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :catch_0
    :cond_2
    :goto_0
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_4

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Lorg/emulationstation/frontend/station/StationCatalog$Item;

    :try_start_0
    iget-object v4, v3, Lorg/emulationstation/frontend/station/StationCatalog$Item;->platform:Ljava/lang/String;

    invoke-static {v4}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->platform(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    iget-object v5, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v5}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v5

    const-string v6, "engines"

    invoke-virtual {v5, v6}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v5

    const/4 v6, 0x0

    :goto_1
    if-eqz v5, :cond_2

    invoke-virtual {v5}, Lorg/json/JSONArray;->length()I

    move-result v7

    if-ge v6, v7, :cond_2

    invoke-virtual {v5, v6}, Lorg/json/JSONArray;->getJSONObject(I)Lorg/json/JSONObject;

    move-result-object v7

    const-string v8, "platform"

    invoke-virtual {v7, v8}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v7

    invoke-virtual {v4, v7}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v7

    if-eqz v7, :cond_3

    invoke-virtual {v0, v3}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v5, v3, Lorg/emulationstation/frontend/station/StationCatalog$Item;->name:Ljava/lang/String;

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v5, "  \u00b7  "

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v3, v3, Lorg/emulationstation/frontend/station/StationCatalog$Item;->platform:Ljava/lang/String;

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v3}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :cond_3
    add-int/lit8 v6, v6, 0x1

    goto :goto_1

    .line 437
    :cond_4
    invoke-virtual {v0}, Ljava/util/ArrayList;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_5

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Nenhum motor liberado para os jogos deste cat\u00e1logo."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_5
    const-string v1, "Escolher jogo"

    const-string v2, "Busque uma edi\u00e7\u00e3o do cat\u00e1logo. Baixe o jogo antes de criar sua sala."

    .line 438
    invoke-direct {p0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codePanel(Ljava/lang/String;Ljava/lang/String;)Landroid/widget/LinearLayout;

    move-result-object v1

    new-instance v2, Landroid/widget/EditText;

    invoke-direct {v2, p0}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    const-string v3, "Buscar jogo"

    invoke-direct {p0, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->field(Landroid/widget/EditText;Ljava/lang/String;)V

    const/4 v3, 0x1

    invoke-virtual {v2, v3}, Landroid/widget/EditText;->setSingleLine(Z)V

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 439
    new-instance v3, Landroid/widget/ListView;

    invoke-direct {v3, p0}, Landroid/widget/ListView;-><init>(Landroid/content/Context;)V

    new-instance v4, Ljava/util/ArrayList;

    invoke-direct {v4}, Ljava/util/ArrayList;-><init>()V

    invoke-virtual {v0}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_2
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_6

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Lorg/emulationstation/frontend/station/StationCatalog$Item;

    new-instance v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;-><init>(Lorg/emulationstation/frontend/station/StationCatalog$Item;)V

    invoke-virtual {v4, v6}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    goto :goto_2

    :cond_6
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoiceAdapter;

    invoke-direct {v0, p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoiceAdapter;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/util/List;)V

    invoke-virtual {v3, v0}, Landroid/widget/ListView;->setAdapter(Landroid/widget/ListAdapter;)V

    new-instance v4, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v5, 0x432a0000    # 170.0f

    invoke-direct {p0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    const/4 v6, -0x1

    invoke-direct {v4, v6, v5}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v3, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 440
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$2;

    invoke-direct {v1, p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$2;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Landroid/widget/ArrayAdapter;)V

    invoke-virtual {v2, v1}, Landroid/widget/EditText;->addTextChangedListener(Landroid/text/TextWatcher;)V

    .line 441
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda102;

    invoke-direct {v1, p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda102;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Landroid/widget/ArrayAdapter;)V

    invoke-virtual {v3, v1}, Landroid/widget/ListView;->setOnItemClickListener(Landroid/widget/AdapterView$OnItemClickListener;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayCodePanel()V

    :cond_7
    :goto_3
    return-void
.end method

.method private clearHeroCover()V
    .locals 2

    .line 219
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroCover:Landroid/widget/ImageView;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/ImageView;->setImageDrawable(Landroid/graphics/drawable/Drawable;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz v0, :cond_0

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz v0, :cond_1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    .line 220
    :cond_1
    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroBitmap:Landroid/graphics/Bitmap;

    return-void
.end method

.method private clearRoomRows()V
    .locals 3

    .line 346
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    invoke-interface {v0}, Ljava/util/Map;->values()Ljava/util/Collection;

    move-result-object v0

    invoke-interface {v0}, Ljava/util/Collection;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    const/4 v2, 0x0

    if-eqz v1, :cond_0

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;

    iget-object v1, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->display:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    goto :goto_0

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    invoke-interface {v0}, Ljava/util/Map;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    invoke-interface {v0}, Ljava/util/Set;->clear()V

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    const-string v0, ""

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCoverItem:Ljava/lang/String;

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    return-void
.end method

.method private clearRoomSetup()V
    .locals 3

    .line 612
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    const/4 v0, 0x0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    const/4 v0, 0x0

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    const-string v1, ""

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    .line 613
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    if-eqz v1, :cond_0

    const/16 v2, 0x8

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->setVisibility(I)V

    :cond_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    if-eqz v1, :cond_1

    invoke-virtual {v1, v0}, Landroid/widget/LinearLayout;->setVisibility(I)V

    :cond_1
    return-void
.end method

.method private closeSheets()V
    .locals 2

    .line 869
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    const/4 v1, 0x0

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->dismiss()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    if-eqz v0, :cond_1

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    :cond_1
    const-string v0, ""

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedPeer:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedName:Ljava/lang/String;

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    return-void
.end method

.method private codePanel(Ljava/lang/String;Ljava/lang/String;)Landroid/widget/LinearLayout;
    .locals 1

    .line 913
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->currentCoverItem()Ljava/lang/String;

    move-result-object v0

    invoke-direct {p0, p1, p2, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codePanel(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Landroid/widget/LinearLayout;

    move-result-object p1

    return-object p1
.end method

.method private codePanel(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Landroid/widget/LinearLayout;
    .locals 1

    const/4 v0, 0x0

    .line 914
    invoke-direct {p0, p1, p2, p3, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codePanel(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;

    move-result-object p1

    return-object p1
.end method

.method private codePanel(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;
    .locals 5

    .line 916
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    :cond_0
    new-instance v0, Landroid/app/Dialog;

    invoke-direct {v0, p0}, Landroid/app/Dialog;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/app/Dialog;->requestWindowFeature(I)Z

    .line 917
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationFlowPanel;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationFlowPanel;-><init>(Landroid/content/Context;)V

    const v1, -0xefe8de

    if-eqz p4, :cond_1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationFlowPanel;->setBackgroundColor(I)V

    goto :goto_0

    :cond_1
    const v2, -0xcfbda8

    invoke-direct {p0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationFlowPanel;->setBackground(Landroid/graphics/drawable/Drawable;)V

    :goto_0
    iget-object v1, v0, Lorg/emulationstation/frontend/netplay/StationFlowPanel;->content:Landroid/widget/LinearLayout;

    .line 918
    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->coverPlatform(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v2}, Lorg/emulationstation/frontend/netplay/StationFlowPanel;->setPlatform(Ljava/lang/String;)V

    if-eqz p3, :cond_3

    .line 919
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-nez v2, :cond_2

    const-string v2, "jogo selecionado"

    goto :goto_1

    :cond_2
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v2, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    :goto_1
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda78;

    invoke-direct {v4, v0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda78;-><init>(Lorg/emulationstation/frontend/netplay/StationFlowPanel;Ljava/lang/String;)V

    const/16 v2, 0x600

    invoke-virtual {v3, p3, v2, v4}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->loadHero(Ljava/lang/String;ILorg/emulationstation/frontend/netplay/StationRoomArtwork$Callback;)V

    :cond_3
    if-nez p4, :cond_4

    const/16 v2, 0xa

    const v3, -0xb92401

    const-string v4, "TURBOSTATIONS  /  JOGAR ONLINE"

    .line 920
    invoke-direct {p0, v1, v4, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    const v3, 0x3dcccccd    # 0.1f

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setLetterSpacing(F)V

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    :cond_4
    if-eqz p4, :cond_5

    const/16 v2, 0x12

    goto :goto_2

    :cond_5
    const/16 v2, 0x16

    :goto_2
    const v3, -0x100a01

    .line 921
    invoke-direct {p0, v1, p1, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/16 p1, 0xc

    const v2, -0x554736

    invoke-direct {p0, v1, p2, p1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    if-eqz p3, :cond_6

    if-nez p4, :cond_6

    const/4 p1, 0x2

    invoke-direct {p0, v1, p3, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->addSynopsis(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/String;)V

    .line 922
    :cond_6
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {p1, v0}, Landroid/app/Dialog;->setContentView(Landroid/view/View;)V

    return-object v1
.end method

.method private command(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V
    .locals 10

    .line 755
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v6

    if-nez v6, :cond_0

    const-string v0, ""

    goto :goto_0

    :cond_0
    const-string v0, "roomId"

    invoke-virtual {v6, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    :goto_0
    move-object v5, v0

    if-nez v6, :cond_1

    const-wide/16 v0, 0x0

    goto :goto_1

    :cond_1
    const-string v0, "generation"

    invoke-virtual {v6, v0}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v0

    :goto_1
    move-wide v7, v0

    .line 756
    new-instance v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda21;

    move-object v0, v9

    move-object v1, p0

    move-object v2, p1

    move-object v3, p2

    move-object v4, p3

    invoke-direct/range {v0 .. v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda21;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;Ljava/lang/String;Lorg/json/JSONObject;J)V

    invoke-direct {p0, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V

    return-void
.end method

.method private compactCreateAction(Landroid/widget/Button;)V
    .locals 2

    .line 215
    move-object v0, p1

    check-cast v0, Lorg/emulationstation/frontend/netplay/StationActionButton;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationActionButton;->compactAppearance()V

    .line 216
    invoke-virtual {p1}, Landroid/widget/Button;->getLayoutParams()Landroid/view/ViewGroup$LayoutParams;

    move-result-object v0

    check-cast v0, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v1, 0x42400000    # 48.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    iput v1, v0, Landroid/widget/LinearLayout$LayoutParams;->height:I

    const/4 v1, 0x0

    iput v1, v0, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    iput v1, v0, Landroid/widget/LinearLayout$LayoutParams;->bottomMargin:I

    invoke-virtual {p1, v0}, Landroid/widget/Button;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    return-void
.end method

.method private composer(Z)V
    .locals 1

    .line 128
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    invoke-virtual {v0, p1}, Landroid/widget/EditText;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->send:Landroid/widget/Button;

    invoke-virtual {v0, p1}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    if-eqz p1, :cond_0

    const-string p1, "Escreva para sua sala\u2026"

    goto :goto_0

    :cond_0
    const-string p1, "Entre em uma sala"

    :goto_0
    invoke-virtual {v0, p1}, Landroid/widget/EditText;->setHint(Ljava/lang/CharSequence;)V

    return-void
.end method

.method private confirmBlock(Ljava/lang/String;Ljava/lang/String;)V
    .locals 2

    .line 910
    new-instance v0, Ljava/lang/StringBuilder;

    const-string v1, "Bloquear "

    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p2, "?"

    invoke-virtual {v0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p2

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda53;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda53;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;)V

    const-string p1, "Oculta este jogador enquanto estiver online e encerra uma sala compartilhada."

    const-string v1, "Bloquear"

    invoke-direct {p0, p2, p1, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->confirmWithCover(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;)V

    return-void
.end method

.method private confirmRoomSetup()V
    .locals 3

    .line 679
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_3

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-nez v0, :cond_0

    goto :goto_1

    .line 680
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v0

    if-nez v0, :cond_1

    goto :goto_0

    .line 681
    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    invoke-direct {p0, v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepareRoom(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;ILjava/lang/String;)V

    return-void

    .line 680
    :cond_2
    :goto_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    const-string v0, "A sele\u00e7\u00e3o mudou. Confira novamente o jogo e os participantes."

    const/4 v1, 0x1

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    :cond_3
    :goto_1
    return-void
.end method

.method private confirmWithCover(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;)V
    .locals 6

    .line 444
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->currentCoverItem()Ljava/lang/String;

    move-result-object v5

    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    move-object v3, p3

    move-object v4, p4

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->confirmWithCover(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;)V

    return-void
.end method

.method private confirmWithCover(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;)V
    .locals 6

    const/4 v0, 0x1

    .line 447
    invoke-direct {p0, p1, p2, p5, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codePanel(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;

    move-result-object p1

    .line 448
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomControls(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object p1

    .line 449
    invoke-static {p3}, Lorg/emulationstation/frontend/netplay/StationActionButton;->iconForLabel(Ljava/lang/String;)I

    move-result v3

    const/4 v4, 0x1

    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda50;

    invoke-direct {v5, p0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda50;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/Runnable;)V

    move-object v0, p0

    move-object v1, p1

    move-object v2, p3

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    const-string v2, "Cancelar"

    const/16 v3, 0xc

    const/4 v4, 0x0

    .line 450
    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda51;

    invoke-direct {v5, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda51;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayCodePanel()V

    return-void
.end method

.method private connect()V
    .locals 5

    .line 458
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-nez v0, :cond_0

    return-void

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    const/4 v1, 0x1

    add-int/2addr v0, v1

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->stopMultiplayerPoll()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->cancelAll()V

    const/4 v0, 0x0

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    invoke-virtual {v2, v1}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const-string v2, "Criar sala"

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->begin()V

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/netplay/StationRoomState;->reset()V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;->reset()V

    const-wide/16 v2, -0x1

    iput-wide v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    const/4 v2, 0x0

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    const-string v2, ""

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchKey:Ljava/lang/String;

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadingLobby()V

    .line 459
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname:Landroid/widget/EditText;

    invoke-virtual {v2}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-eqz v3, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Escolha seu apelido para entrar."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_1
    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getPreferences(I)Landroid/content/SharedPreferences;

    move-result-object v3

    invoke-interface {v3}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v3

    const-string v4, "nickname"

    invoke-interface {v3, v4, v2}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v3

    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V

    const-string v3, "station-online-profile"

    invoke-virtual {p0, v3, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v3

    invoke-interface {v3}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v3

    invoke-interface {v3, v4, v2}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v3

    invoke-interface {v3}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 460
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v4, "Consultando jogadores e salas\u2026"

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    invoke-virtual {v3, v0}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->events:Ljava/util/concurrent/ExecutorService;

    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda47;

    invoke-direct {v3, p0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda47;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;)V

    invoke-interface {v0, v3}, Ljava/util/concurrent/ExecutorService;->submit(Ljava/lang/Runnable;)Ljava/util/concurrent/Future;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->polling:Ljava/util/concurrent/Future;

    return-void
.end method

.method private static contains(Lorg/json/JSONArray;Ljava/lang/String;)Z
    .locals 3

    const/4 v0, 0x0

    if-eqz p0, :cond_1

    move v1, v0

    .line 1042
    :goto_0
    invoke-virtual {p0}, Lorg/json/JSONArray;->length()I

    move-result v2

    if-ge v1, v2, :cond_1

    invoke-virtual {p0, v1}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_0

    const/4 p0, 0x1

    return p0

    :cond_0
    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_1
    return v0
.end method

.method private coverPlatform(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    const-string v0, ""

    .line 223
    :try_start_0
    invoke-static {p0}, Lorg/emulationstation/frontend/station/StationAndroid;->get(Landroid/content/Context;)Lorg/emulationstation/frontend/station/StationAndroid;

    move-result-object v1

    iget-object v1, v1, Lorg/emulationstation/frontend/station/StationAndroid;->coordinator:Lorg/emulationstation/frontend/station/StationCoordinator;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/station/StationCoordinator;->current()Lorg/emulationstation/frontend/station/StationCoordinator$Library;

    move-result-object v1

    if-nez v1, :cond_0

    const/4 p1, 0x0

    goto :goto_0

    .line 224
    :cond_0
    iget-object v1, v1, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;

    invoke-virtual {v1, p1}, Lorg/emulationstation/frontend/station/StationCatalog;->find(Ljava/lang/String;)Lorg/emulationstation/frontend/station/StationCatalog$Item;

    move-result-object p1

    :goto_0
    if-nez p1, :cond_1

    goto :goto_1

    :cond_1
    iget-object v0, p1, Lorg/emulationstation/frontend/station/StationCatalog$Item;->platform:Ljava/lang/String;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    :goto_1
    return-object v0
.end method

.method private createRoom()V
    .locals 5

    .line 684
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_3

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_3

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_0

    goto :goto_0

    .line 685
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    const/4 v1, 0x1

    if-nez v0, :cond_1

    const-string v0, "Escolha um jogo antes de criar a sala."

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    return-void

    .line 686
    :cond_1
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_2

    const-string v0, "Saia da sala atual antes de criar outra."

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    return-void

    .line 687
    :cond_2
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object v1

    new-instance v2, Ljava/util/ArrayList;

    invoke-direct {v2}, Ljava/util/ArrayList;-><init>()V

    .line 688
    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda1;

    invoke-direct {v3, p0, v2, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda1;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/util/List;Ljava/lang/String;)V

    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda2;

    invoke-direct {v4, p0, v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda2;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Ljava/util/List;)V

    invoke-direct {p0, v3, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    :cond_3
    :goto_0
    return-void
.end method

.method private createVerifiedRoom(Lorg/emulationstation/frontend/netplay/StationOnlineGame;I)V
    .locals 3

    .line 717
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_1

    iget-object v0, p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->itemId:Ljava/lang/String;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    iget-object v0, p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->multiplayerProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-virtual {v0, p2}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v0

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x1

    .line 718
    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const-string v2, "Criando\u2026"

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const-string v0, "Confirmando sua sala\u2026"

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    .line 719
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda44;

    invoke-direct {v0, p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda44;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationOnlineGame;I)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda45;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda45;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private currentCoverItem()Ljava/lang/String;
    .locals 3

    .line 912
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v2, 0x2

    if-eq v1, v2, :cond_1

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    const-string v1, "itemId"

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    goto :goto_1

    :cond_1
    :goto_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    :goto_1
    return-object v0
.end method

.method private deliver(Lorg/json/JSONObject;I)V
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 534
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_2

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-eq p2, v0, :cond_0

    goto :goto_0

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->accept(Lorg/json/JSONObject;)Z

    move-result v0

    if-nez v0, :cond_1

    return-void

    :cond_1
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda94;

    invoke-direct {v0, p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda94;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILorg/json/JSONObject;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    :cond_2
    :goto_0
    return-void
.end method

.method private discardPreparedLaunch(ZZZLjava/lang/String;)V
    .locals 0

    if-eqz p1, :cond_0

    .line 1097
    invoke-static {p0, p4}, Lorg/emulationstation/frontend/netplay/StationN64Launch;->discard(Landroid/content/Context;Ljava/lang/String;)V

    goto :goto_0

    :cond_0
    if-eqz p2, :cond_1

    invoke-static {p0, p4}, Lorg/emulationstation/frontend/netplay/StationDolphinLaunch;->discard(Landroid/content/Context;Ljava/lang/String;)V

    goto :goto_0

    :cond_1
    if-eqz p3, :cond_2

    invoke-static {p0, p4}, Lorg/emulationstation/frontend/netplay/StationPsxLaunch;->discard(Landroid/content/Context;Ljava/lang/String;)V

    goto :goto_0

    :cond_2
    invoke-static {p0, p4}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->discard(Landroid/content/Context;Ljava/lang/String;)V

    :goto_0
    return-void
.end method

.method private displayCodePanel()V
    .locals 6

    .line 925
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->show()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->getWindow()Landroid/view/Window;

    move-result-object v0

    if-nez v0, :cond_0

    return-void

    :cond_0
    const v1, 0x106000d

    .line 926
    invoke-virtual {v0, v1}, Landroid/view/Window;->setBackgroundDrawableResource(I)V

    const/4 v1, 0x2

    invoke-virtual {v0, v1}, Landroid/view/Window;->addFlags(I)V

    .line 927
    invoke-virtual {v0}, Landroid/view/Window;->getAttributes()Landroid/view/WindowManager$LayoutParams;

    move-result-object v1

    const/high16 v2, 0x44390000    # 740.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v3

    invoke-virtual {v3}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v3

    iget v3, v3, Landroid/util/DisplayMetrics;->widthPixels:I

    const/high16 v4, 0x41c00000    # 24.0f

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    sub-int/2addr v3, v5

    invoke-static {v2, v3}, Ljava/lang/Math;->min(II)I

    move-result v2

    iput v2, v1, Landroid/view/WindowManager$LayoutParams;->width:I

    const/high16 v2, 0x43dc0000    # 440.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v3

    invoke-virtual {v3}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v3

    iget v3, v3, Landroid/util/DisplayMetrics;->heightPixels:I

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    sub-int/2addr v3, v4

    invoke-static {v2, v3}, Ljava/lang/Math;->min(II)I

    move-result v2

    iput v2, v1, Landroid/view/WindowManager$LayoutParams;->height:I

    const v2, 0x3f3851ec    # 0.72f

    iput v2, v1, Landroid/view/WindowManager$LayoutParams;->dimAmount:F

    const/16 v2, 0x11

    iput v2, v1, Landroid/view/WindowManager$LayoutParams;->gravity:I

    invoke-virtual {v0, v1}, Landroid/view/Window;->setAttributes(Landroid/view/WindowManager$LayoutParams;)V

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v1

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getWindow()Landroid/view/Window;

    move-result-object v2

    invoke-virtual {v2}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v2

    invoke-virtual {v2}, Landroid/view/View;->getSystemUiVisibility()I

    move-result v2

    invoke-virtual {v1, v2}, Landroid/view/View;->setSystemUiVisibility(I)V

    const/16 v1, 0x10

    .line 928
    invoke-virtual {v0, v1}, Landroid/view/Window;->setSoftInputMode(I)V

    return-void
.end method

.method private static displayHelp(Lorg/json/JSONObject;Ljava/lang/String;)[Ljava/lang/String;
    .locals 2

    const-string v0, "sources"

    .line 561
    :try_start_0
    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    const/16 v1, 0x200

    goto :goto_0

    :cond_0
    const/16 v1, 0x1f4

    :goto_0
    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    invoke-static {p0, p1, v1, v0}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->help(Lorg/json/JSONObject;Ljava/lang/String;IZ)[Ljava/lang/String;

    move-result-object p0
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    return-object p0

    :catch_0
    const/4 p0, 0x0

    new-array p0, p0, [Ljava/lang/String;

    return-object p0
.end method

.method private dp(F)I
    .locals 1

    .line 88
    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr v0, p1

    const/high16 p1, 0x3f000000    # 0.5f

    add-float/2addr v0, p1

    float-to-int p1, v0

    return p1
.end method

.method private empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 7

    .line 121
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object p2

    const/16 v0, 0x11

    invoke-virtual {p2, v0}, Landroid/widget/LinearLayout;->setGravity(I)V

    const/high16 v1, 0x41200000    # 10.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-virtual {p2, v2, v3, v4, v1}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v2, -0x1

    invoke-direct {v1, v2, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, p2, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 122
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    if-eq p1, v1, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    if-ne p1, v1, :cond_0

    goto :goto_0

    :cond_0
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationLobbyIcon;

    const/4 v2, 0x1

    invoke-direct {v1, p0, v2}, Lorg/emulationstation/frontend/netplay/StationLobbyIcon;-><init>(Landroid/content/Context;I)V

    goto :goto_2

    :cond_1
    :goto_0
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationLottieIllustration;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    if-ne p1, v2, :cond_2

    const-string v2, "dialog"

    goto :goto_1

    :cond_2
    const-string v2, "online-robot"

    :goto_1
    invoke-direct {v1, p0, v2}, Lorg/emulationstation/frontend/netplay/StationLottieIllustration;-><init>(Landroid/content/Context;Ljava/lang/String;)V

    :goto_2
    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    const/high16 v4, 0x42900000    # 72.0f

    const/high16 v5, 0x42e00000    # 112.0f

    if-ne p1, v3, :cond_3

    move v3, v4

    goto :goto_3

    :cond_3
    move v3, v5

    :goto_3
    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    iget-object v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    if-ne p1, v6, :cond_4

    goto :goto_4

    :cond_4
    move v4, v5

    :goto_4
    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p1

    invoke-direct {v2, v3, p1}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p2, v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const/16 p1, 0xe

    const v1, -0x100a01

    .line 123
    invoke-direct {p0, p2, p3, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setGravity(I)V

    const/high16 p3, 0x41500000    # 13.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    const/high16 v1, 0x40c00000    # 6.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    const/4 v2, 0x0

    invoke-virtual {p1, v2, p3, v2, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/16 p1, 0xc

    const p3, -0x554736

    .line 124
    invoke-direct {p0, p2, p4, p1, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setGravity(I)V

    const/high16 p2, 0x40000000    # 2.0f

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p2

    int-to-float p2, p2

    const/high16 p3, 0x3f800000    # 1.0f

    invoke-virtual {p1, p2, p3}, Landroid/widget/TextView;->setLineSpacing(FF)V

    return-void
.end method

.method private enterCodeDialog()V
    .locals 7

    .line 942
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-eqz v0, :cond_0

    return-void

    :cond_0
    const-string v0, "Entrar por c\u00f3digo"

    const-string v1, "Digite ou cole o convite de 8 caracteres. Convites antigos tamb\u00e9m s\u00e3o aceitos."

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codePanel(Ljava/lang/String;Ljava/lang/String;)Landroid/widget/LinearLayout;

    move-result-object v0

    .line 943
    new-instance v1, Landroid/widget/EditText;

    invoke-direct {v1, p0}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    const-string v2, "7KPM-4XRT"

    invoke-direct {p0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->field(Landroid/widget/EditText;Ljava/lang/String;)V

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/widget/EditText;->setSingleLine(Z)V

    const/high16 v3, 0x41400000    # 12.0f

    invoke-virtual {v1, v3}, Landroid/widget/EditText;->setTextSize(F)V

    new-array v3, v2, [Landroid/text/InputFilter;

    new-instance v4, Landroid/text/InputFilter$LengthFilter;

    const/16 v5, 0xa0

    invoke-direct {v4, v5}, Landroid/text/InputFilter$LengthFilter;-><init>(I)V

    const/4 v5, 0x0

    aput-object v4, v3, v5

    invoke-virtual {v1, v3}, Landroid/widget/EditText;->setFilters([Landroid/text/InputFilter;)V

    const v3, 0x80001

    invoke-virtual {v1, v3}, Landroid/widget/EditText;->setInputType(I)V

    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v4, 0x42400000    # 48.0f

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    const/4 v6, -0x1

    invoke-direct {v3, v6, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const/16 v3, 0xc

    const v4, -0x105268

    const-string v6, ""

    .line 944
    invoke-direct {p0, v0, v6, v3, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v3

    const/16 v4, 0x8

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setVisibility(I)V

    invoke-virtual {v3, v2}, Landroid/widget/TextView;->setAccessibilityLiveRegion(I)V

    .line 945
    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda76;

    invoke-direct {v4, p0, v1, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda76;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Landroid/widget/EditText;Landroid/widget/TextView;)V

    const-string v1, "Entrar na sala"

    invoke-direct {p0, v0, v1, v4, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v1

    .line 961
    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->compactCreateAction(Landroid/widget/Button;)V

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda77;

    invoke-direct {v1, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda77;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v2, "Cancelar"

    invoke-direct {p0, v0, v2, v1, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->compactCreateAction(Landroid/widget/Button;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayCodePanel()V

    return-void
.end method

.method private exitRooms()V
    .locals 6

    .line 1104
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_2

    const-string v1, "station-online-profile"

    const/4 v2, 0x0

    .line 1106
    invoke-virtual {p0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v1

    const-string v2, "station-stream.v3"

    const-string v3, "recoveryProtocol"

    .line 1107
    invoke-virtual {v0, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_1

    const-string v2, "roomId"

    .line 1108
    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    const-string v3, "generation"

    invoke-virtual {v0, v3}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v3

    const-string v5, "recoveryProtocol"

    invoke-virtual {v0, v5}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v2, v3, v4, v0}, Lorg/emulationstation/frontend/netplay/StationRoomLeaveIntent;->human(Ljava/lang/String;JLjava/lang/String;)Lorg/emulationstation/frontend/netplay/StationRoomLeaveIntent;

    move-result-object v0

    .line 1109
    const-class v2, Lorg/emulationstation/frontend/netplay/StationRoomLeaveIntent;

    monitor-enter v2

    :try_start_0
    invoke-interface {v1}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v3, "leaveMultiplayerIntent"

    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationRoomLeaveIntent;->encoded:Ljava/lang/String;

    invoke-interface {v1, v3, v0}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v1, "leaveOnCatalog"

    invoke-interface {v0, v1}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->commit()Z

    move-result v0

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "N\u00e3o foi poss\u00edvel registrar a sa\u00edda. Tente novamente."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    monitor-exit v2

    return-void

    :cond_0
    monitor-exit v2

    goto :goto_0

    :catchall_0
    move-exception v0

    monitor-exit v2
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    throw v0

    .line 1110
    :cond_1
    invoke-interface {v1}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v1, "leaveOnCatalog"

    const/4 v2, 0x1

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 1112
    :cond_2
    :goto_0
    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->finish()V

    return-void
.end method

.method private failure(Ljava/lang/Throwable;I)V
    .locals 1

    .line 544
    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->recordFailure(Ljava/lang/Throwable;)V

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda62;

    invoke-direct {v0, p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda62;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/Throwable;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method private field(Landroid/widget/EditText;Ljava/lang/String;)V
    .locals 4

    const/high16 v0, 0x41500000    # 13.0f

    .line 126
    invoke-virtual {p1, v0}, Landroid/widget/EditText;->setTextSize(F)V

    const v0, -0x100a01

    invoke-virtual {p1, v0}, Landroid/widget/EditText;->setTextColor(I)V

    const v0, -0x554736

    invoke-virtual {p1, v0}, Landroid/widget/EditText;->setHintTextColor(I)V

    const/high16 v0, 0x41400000    # 12.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    const/high16 v2, 0x41000000    # 8.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {p1, v1, v3, v0, v2}, Landroid/widget/EditText;->setPadding(IIII)V

    const v0, -0xf5ead9

    const v1, -0xd3bc9f

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v0

    invoke-virtual {p1, v0}, Landroid/widget/EditText;->setBackground(Landroid/graphics/drawable/Drawable;)V

    invoke-virtual {p1, p2}, Landroid/widget/EditText;->setHint(Ljava/lang/CharSequence;)V

    return-void
.end method

.method private static findRoom(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;
    .locals 3

    const-string v0, "rooms"

    .line 1043
    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object p0

    if-eqz p0, :cond_1

    const/4 v0, 0x0

    :goto_0
    invoke-virtual {p0}, Lorg/json/JSONArray;->length()I

    move-result v1

    if-ge v0, v1, :cond_1

    invoke-virtual {p0, v0}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v1

    if-eqz v1, :cond_0

    const-string v2, "roomId"

    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_0

    return-object v1

    :cond_0
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    :cond_1
    const/4 p0, 0x0

    return-object p0
.end method

.method private inline(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/Runnable;Z)Landroid/widget/Button;
    .locals 3

    .line 109
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/16 v2, 0x30

    invoke-static {v2, p3}, Ljava/lang/Math;->max(II)I

    move-result p3

    int-to-float p3, p3

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    const/4 v2, -0x2

    invoke-direct {v1, p3, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    const/high16 p3, 0x41000000    # 8.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    const/4 v2, 0x0

    invoke-virtual {v1, p3, v2, v2, v2}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-direct {p0, v0, p2, p4, p5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object p1

    return-object p1
.end method

.method private invitePlayer(Ljava/lang/String;)V
    .locals 3

    .line 890
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-boolean v0, v0, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-eqz v0, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v0, "Converse com o jogador e pe\u00e7a para entrar pela lista de salas. O convite desta modalidade ainda est\u00e1 em prepara\u00e7\u00e3o."

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    .line 891
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedName:Ljava/lang/String;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-static {v0, p1, v1, v2}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->read(Lorg/json/JSONObject;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationPlayerModel;

    move-result-object v0

    .line 892
    iget-boolean v1, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->canInvite:Z

    if-eqz v1, :cond_2

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-eqz v1, :cond_1

    goto :goto_0

    :cond_1
    const-string v1, "Preparando seu convite\u2026"

    .line 893
    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    .line 894
    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda109;

    invoke-direct {v2, p0, p1, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda109;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationPlayerModel;I)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda110;

    invoke-direct {p1, p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda110;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationPlayerModel;)V

    invoke-direct {p0, v2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    return-void

    .line 892
    :cond_2
    :goto_0
    iget-object p1, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->reason:Ljava/lang/String;

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    return-void
.end method

.method private join(Ljava/lang/String;Ljava/lang/String;)V
    .locals 11

    .line 725
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_6

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-eqz v0, :cond_0

    goto/16 :goto_1

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_1

    const/4 v1, 0x0

    goto :goto_0

    :cond_1
    const-string v1, "room"

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    .line 726
    :goto_0
    invoke-static {v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->findRoom(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v7

    if-nez v7, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string p2, "A sala mudou. Atualize a lista antes de entrar."

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_2
    if-nez v1, :cond_3

    const-string v1, "Entrar nesta sala?"

    .line 727
    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v2

    const-string v3, "Aceitar e entrar"

    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda95;

    invoke-direct {v4, p0, p1, p2, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda95;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Lorg/json/JSONObject;)V

    move-object v0, p0

    move-object v5, p2

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->confirmWithCover(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;)V

    return-void

    :cond_3
    const-string v2, "roomId"

    .line 728
    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {p1, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_4

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string p2, "Voc\u00ea j\u00e1 est\u00e1 nesta sala. Marque Estou pronto para confirmar sua participa\u00e7\u00e3o."

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    .line 729
    :cond_4
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->soloWaitingRoom(Lorg/json/JSONObject;)Z

    move-result v0

    if-nez v0, :cond_5

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string p2, "Saia da sala atual antes de entrar em outra."

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    .line 730
    :cond_5
    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    const-string v1, "Entrar na outra sala?"

    .line 731
    new-instance v0, Ljava/lang/StringBuilder;

    const-string v2, "Voc\u00ea est\u00e1 sozinho na sua sala. Ela ser\u00e1 encerrada para voc\u00ea entrar na sala de outro jogador. Estou pronto confirma a participa\u00e7\u00e3o; n\u00e3o muda de sala.\n\n"

    invoke-direct {v0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v8

    const-string v9, "Sair e entrar"

    new-instance v10, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda96;

    move-object v2, v10

    move-object v3, p0

    move-object v4, p1

    move-object v5, p2

    invoke-direct/range {v2 .. v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda96;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lorg/json/JSONObject;)V

    move-object v0, p0

    move-object v2, v8

    move-object v3, v9

    move-object v4, v10

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->confirmWithCover(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Runnable;Ljava/lang/String;)V

    :cond_6
    :goto_1
    return-void
.end method

.method private joinCode(Ljava/lang/String;)V
    .locals 2

    .line 970
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Localizando a sala\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    .line 971
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda103;

    invoke-direct {v1, p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda103;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;I)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda104;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda104;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct {p0, v1, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    return-void
.end method

.method private joinConfirmed(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;)V
    .locals 11

    move-object v9, p0

    .line 734
    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Conferindo se os jogos s\u00e3o id\u00eanticos\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget v8, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    .line 735
    new-instance v10, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda63;

    move-object v0, v10

    move-object v1, p0

    move-object v2, p2

    move-object/from16 v3, p6

    move-object v4, p1

    move-wide v5, p4

    move-object v7, p3

    invoke-direct/range {v0 .. v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda63;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;I)V

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda64;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda64;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct {p0, v10, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    return-void
.end method

.method private joinPlayer(Ljava/lang/String;)V
    .locals 3

    .line 904
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedName:Ljava/lang/String;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-static {v0, p1, v1, v2}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->read(Lorg/json/JSONObject;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationPlayerModel;

    move-result-object p1

    .line 905
    iget-boolean v0, p1, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->canJoin:Z

    if-eqz v0, :cond_2

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-eqz v0, :cond_0

    goto :goto_1

    .line 906
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "join-request-v1"

    invoke-static {v0, v1}, Lorg/emulationstation/frontend/netplay/StationSocial;->supports(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_1

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda92;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda92;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationPlayerModel;)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda93;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda93;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    goto :goto_0

    .line 907
    :cond_1
    iget-object v0, p1, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->joinRoomId:Ljava/lang/String;

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->joinItemId:Ljava/lang/String;

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->join(Ljava/lang/String;Ljava/lang/String;)V

    :goto_0
    return-void

    .line 905
    :cond_2
    :goto_1
    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->reason:Ljava/lang/String;

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    return-void
.end method

.method private label(Ljava/lang/String;II)Landroid/widget/TextView;
    .locals 1

    .line 92
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    int-to-float p1, p2

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setTextSize(F)V

    invoke-virtual {v0, p3}, Landroid/widget/TextView;->setTextColor(I)V

    const-string p1, "kern"

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setFontFeatureSettings(Ljava/lang/String;)V

    const/4 p1, 0x0

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setIncludeFontPadding(Z)V

    return-object v0
.end method

.method static synthetic lambda$button$0(Ljava/lang/Runnable;Landroid/view/View;)V
    .locals 0

    .line 102
    invoke-interface {p0}, Ljava/lang/Runnable;->run()V

    return-void
.end method

.method static synthetic lambda$codePanel$90(Lorg/emulationstation/frontend/netplay/StationFlowPanel;Ljava/lang/String;Landroid/graphics/Bitmap;)V
    .locals 0

    .line 919
    invoke-virtual {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationFlowPanel;->setCover(Landroid/graphics/Bitmap;Ljava/lang/String;)V

    return-void
.end method

.method static synthetic lambda$navButton$1(Ljava/lang/Runnable;Landroid/view/View;)V
    .locals 0

    .line 106
    invoke-interface {p0}, Ljava/lang/Runnable;->run()V

    return-void
.end method

.method static synthetic lambda$roomAction$23(Ljava/lang/Runnable;Landroid/view/View;)V
    .locals 0

    .line 401
    invoke-interface {p0}, Ljava/lang/Runnable;->run()V

    return-void
.end method

.method private launch(Lorg/json/JSONObject;Lorg/json/JSONObject;)V
    .locals 8

    .line 1079
    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationLaunchPolicy;->key(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v1, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;->pending()Z

    move-result v1

    if-nez v1, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchKey:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    goto :goto_0

    :cond_0
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchKey:Ljava/lang/String;

    const/4 v0, 0x1

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    iget v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    new-instance v5, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-direct {v5}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;-><init>()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v5}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Conectando a partida online\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    new-instance v0, Ljava/lang/StringBuilder;

    const-string v1, "launch stage=prepare room="

    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    const-string v1, "roomId"

    invoke-virtual {p1, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, " generation="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, "generation"

    invoke-virtual {p1, v1}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v1

    invoke-virtual {v0, v1, v2}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    const-string v1, " host="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v1, "selfId"

    invoke-virtual {p2, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const-string v2, "hostId"

    invoke-virtual {p1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    const-string v1, "StationRooms"

    invoke-static {v1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 1080
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->commands:Ljava/util/concurrent/ExecutorService;

    new-instance v7, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda58;

    move-object v1, v7

    move-object v2, p0

    move-object v3, p1

    move-object v4, p2

    invoke-direct/range {v1 .. v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda58;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;I)V

    invoke-interface {v0, v7}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private launchFailure(Ljava/lang/Throwable;I)V
    .locals 1

    .line 1099
    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->recordFailure(Ljava/lang/Throwable;)V

    .line 1100
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda67;

    invoke-direct {v0, p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda67;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/Throwable;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method

.method private loadHero()V
    .locals 5

    .line 1001
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v2, 0x2

    if-eq v1, v2, :cond_1

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    const-string v1, "itemId"

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    goto :goto_1

    :cond_1
    :goto_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    .line 1002
    :goto_1
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v1, :cond_6

    if-eqz v0, :cond_6

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_2

    goto :goto_2

    .line 1003
    :cond_2
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_3

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroEpoch:I

    iget v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v1, v2, :cond_3

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHeroProfile(Ljava/lang/String;)V

    return-void

    .line 1004
    :cond_3
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    iput v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroEpoch:I

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    .line 1005
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->synopsisFor(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroSynopsis:Ljava/lang/String;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSynopsis:Landroid/widget/TextView;

    if-eqz v3, :cond_4

    invoke-virtual {v3, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_4
    const-string v2, ""

    .line 1006
    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactSummary:Ljava/lang/String;

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactDetail:Ljava/lang/String;

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlineDetail:Ljava/lang/String;

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlinePlayers:Ljava/lang/String;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    const/4 v4, -0x1

    invoke-virtual {v3, v4}, Lorg/emulationstation/frontend/netplay/StationGameRatingView;->setRating(I)V

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    const-string v4, "Jogadores a confirmar"

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    if-eqz v3, :cond_5

    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->pending()Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v4

    iget-object v4, v4, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->detail:Ljava/lang/String;

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_5
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    invoke-virtual {v3, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearHeroCover()V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroSymbol:Lorg/emulationstation/frontend/netplay/StationLobbyIcon;

    const/4 v3, 0x0

    invoke-virtual {v2, v3}, Lorg/emulationstation/frontend/netplay/StationLobbyIcon;->setVisibility(I)V

    .line 1007
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda74;

    invoke-direct {v3, p0, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda74;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;)V

    const/16 v4, 0x600

    invoke-virtual {v2, v0, v4, v3}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->loadHero(Ljava/lang/String;ILorg/emulationstation/frontend/netplay/StationRoomArtwork$Callback;)V

    .line 1008
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->commands:Ljava/util/concurrent/ExecutorService;

    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda75;

    invoke-direct {v3, p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda75;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;I)V

    invoke-interface {v2, v3}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    .line 1019
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHeroProfile(Ljava/lang/String;)V

    :cond_6
    :goto_2
    return-void
.end method

.method private loadHeroProfile(Ljava/lang/String;)V
    .locals 3

    .line 1028
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-boolean v0, v0, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileRequestId:Ljava/lang/String;

    invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileEpoch:I

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, v1, :cond_0

    goto :goto_0

    .line 1029
    :cond_0
    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileRequestId:Ljava/lang/String;

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileEpoch:I

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    .line 1030
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->commands:Ljava/util/concurrent/ExecutorService;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda98;

    invoke-direct {v2, p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda98;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;I)V

    invoke-interface {v1, v2}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    :cond_1
    :goto_0
    return-void
.end method

.method private loadingLobby()V
    .locals 5

    .line 130
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->closeSheets()V

    const-string v0, "Conectando"

    const/4 v1, 0x0

    .line 131
    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setConnection(Ljava/lang/String;Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerTitle:Landroid/widget/TextView;

    const-string v2, "JOGADORES"

    invoke-virtual {v0, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomTitle:Landroid/widget/TextView;

    const-string v2, "SALAS DISPON\u00cdVEIS"

    invoke-virtual {v0, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomRows()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    .line 132
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    const-string v2, "Buscando jogadores"

    const-string v3, "A lista aparece assim que a conex\u00e3o for confirmada."

    const-string v4, "\u2026"

    invoke-direct {p0, v0, v4, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    const-string v2, "Abrindo o lobby"

    const-string v3, "Preparando suas salas e seus convites."

    invoke-direct {p0, v0, v4, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    const-string v2, "Conversa da sala"

    const-string v3, "Entre em uma partida para conversar com outro jogador."

    const-string v4, "\u2197"

    invoke-direct {p0, v0, v4, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->composer(Z)V

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    return-void
.end method

.method private navButton(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;)Landroid/widget/Button;
    .locals 3

    .line 105
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationActionButton;

    const/4 v1, 0x0

    invoke-direct {v0, p0, p2, v1}, Lorg/emulationstation/frontend/netplay/StationActionButton;-><init>(Landroid/content/Context;Ljava/lang/String;Z)V

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationActionButton;->compactAppearance()V

    const/high16 p2, 0x41400000    # 12.0f

    invoke-virtual {v0, p2}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setTextSize(F)V

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleNavigation(Landroid/widget/Button;Z)V

    .line 106
    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v1, 0x42400000    # 48.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    const/4 v2, -0x1

    invoke-direct {p2, v2, v1}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda60;

    invoke-direct {p1, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda60;-><init>(Ljava/lang/Runnable;)V

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-object v0
.end method

.method private navigate(I)V
    .locals 2

    const/4 v0, 0x2

    if-eq p1, v0, :cond_0

    .line 414
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    :cond_0
    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    const/4 v1, 0x1

    if-eqz v0, :cond_1

    move v0, v1

    goto :goto_0

    :cond_1
    const/4 v0, 0x0

    :goto_0
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_4

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_4

    .line 415
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_2

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_2

    if-nez p1, :cond_2

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    if-eqz v0, :cond_2

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    neg-int p1, p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pageRooms(I)V

    goto :goto_1

    .line 416
    :cond_2
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_3

    if-ne p1, v1, :cond_3

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    if-eqz p1, :cond_3

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    neg-int p1, p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pagePeers(I)V

    goto :goto_1

    :cond_3
    const-wide/16 v0, -0x1

    .line 417
    iput-wide v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paint(Lorg/json/JSONObject;)V

    :cond_4
    :goto_1
    return-void
.end method

.method private navigationIcon(Landroid/widget/Button;I)V
    .locals 0

    .line 403
    check-cast p1, Lorg/emulationstation/frontend/netplay/StationActionButton;

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setActionIcon(I)V

    return-void
.end method

.method private navigationSection(Landroid/widget/LinearLayout;Ljava/lang/String;)V
    .locals 4

    const/16 v0, 0x9

    const v1, -0x554736

    .line 113
    invoke-direct {p0, p2, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p2

    const v0, 0x3df5c28f    # 0.12f

    invoke-virtual {p2, v0}, Landroid/widget/TextView;->setLetterSpacing(F)V

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/high16 v0, 0x41200000    # 10.0f

    .line 114
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/high16 v2, 0x40a00000    # 5.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    const/4 v3, 0x0

    invoke-virtual {p2, v1, v0, v3, v2}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v0, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v1, -0x1

    const/4 v2, -0x2

    invoke-direct {v0, v1, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, p2, v0}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-void
.end method

.method private nickname(Lorg/json/JSONObject;Ljava/lang/String;)Ljava/lang/String;
    .locals 1

    .line 765
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-virtual {v0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;->resolveName(Lorg/json/JSONObject;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    return-object p1
.end method

.method private static onlineNotice(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    if-eqz p0, :cond_4

    .line 255
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_1

    :cond_0
    const-string v0, "(?iu)\\bservidor(?:\\s+(?:Station|PIX))?\\b"

    const-string v1, "servi\u00e7o online"

    .line 256
    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playGuidance(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 257
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_1

    return-object v0

    .line 258
    :cond_1
    sget-object v0, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {p0, v0}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object p0

    const-string v0, "ativa\u00e7\u00e3o"

    .line 259
    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    if-nez v0, :cond_3

    const-string v0, "aguarda"

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    if-nez v0, :cond_3

    const-string v0, "pending"

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v0

    if-nez v0, :cond_3

    const-string v0, "unavailable"

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result p0

    if-eqz p0, :cond_2

    goto :goto_0

    :cond_2
    const-string p0, "N\u00e3o foi poss\u00edvel concluir esta a\u00e7\u00e3o. Confira sua conex\u00e3o e tente novamente."

    return-object p0

    :cond_3
    :goto_0
    const-string p0, "Este modo online ainda n\u00e3o est\u00e1 dispon\u00edvel nesta sess\u00e3o. Aguarde a ativa\u00e7\u00e3o desta op\u00e7\u00e3o."

    return-object p0

    :cond_4
    :goto_1
    const-string p0, ""

    return-object p0
.end method

.method private openConversation(Ljava/lang/String;Ljava/lang/String;)V
    .locals 3

    .line 829
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->drafts:Ljava/util/Map;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    invoke-virtual {v2}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-interface {v0, v1, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    const-string p2, ""

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->lastMessageId:Ljava/lang/String;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingName:Ljava/lang/String;

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->drafts:Ljava/util/Map;

    invoke-interface {v1, p1}, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_1

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->drafts:Ljava/util/Map;

    invoke-interface {p2, p1}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    move-object p2, p1

    check-cast p2, Ljava/lang/CharSequence;

    :cond_1
    invoke-virtual {v0, p2}, Landroid/widget/EditText;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-eqz p1, :cond_2

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->dismiss()V

    :cond_2
    const/4 p1, 0x3

    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_3

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderConversation(Lorg/json/JSONObject;)V

    :cond_3
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_4

    const/4 p1, 0x1

    goto :goto_0

    :cond_4
    const/4 p1, 0x0

    :goto_0
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    return-void
.end method

.method private ownRoomGuide(Landroid/widget/LinearLayout;Lorg/json/JSONObject;)V
    .locals 8

    const-string v0, "SOBRE O JOGO"

    const/16 v1, 0x9

    const v2, -0xb92401

    .line 349
    invoke-direct {p0, p1, v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const v1, 0x3da3d70a    # 0.08f

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setLetterSpacing(F)V

    const/high16 v1, 0x41400000    # 12.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    const/high16 v3, 0x40800000    # 4.0f

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    const/4 v5, 0x0

    invoke-virtual {v0, v5, v1, v5, v4}, Landroid/widget/TextView;->setPadding(IIII)V

    const-string v0, "itemId"

    .line 350
    invoke-virtual {p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->synopsisFor(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const/16 v1, 0xc

    const v4, -0x554736

    invoke-direct {p0, p1, v0, v1, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    const/high16 v1, 0x41000000    # 8.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-virtual {v0, v5, v5, v5, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    const/4 v1, 0x4

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setMaxLines(I)V

    sget-object v1, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    const/high16 v1, 0x40000000    # 2.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    int-to-float v4, v4

    const/high16 v6, 0x3f800000    # 1.0f

    invoke-virtual {v0, v4, v6}, Landroid/widget/TextView;->setLineSpacing(FF)V

    .line 351
    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda19;

    invoke-direct {v4, p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda19;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    invoke-virtual {v0, v4}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    const-string v0, "state"

    .line 352
    invoke-virtual {p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v4, "waiting"

    invoke-virtual {v4, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    const-string v0, "Marque Estou pronto. Quando todos confirmarem, o anfitri\u00e3o inicia a partida."

    goto :goto_0

    :cond_0
    const-string v0, "Use Conversa para falar com os jogadores. Sair deixa esta sala."

    :goto_0
    const v4, -0x100a01

    const/16 v7, 0xb

    .line 353
    invoke-direct {p0, p1, v0, v7, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-virtual {v0, v5, v5, v5, v3}, Landroid/widget/TextView;->setPadding(IIII)V

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    int-to-float v1, v1

    invoke-virtual {v0, v1, v6}, Landroid/widget/TextView;->setLineSpacing(FF)V

    const-string v0, "Ver sinopse completa e como jogar"

    .line 354
    invoke-direct {p0, p1, v0, v7, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    const/high16 v0, 0x40400000    # 3.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/high16 v1, 0x40e00000    # 7.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-virtual {p1, v5, v0, v5, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda20;

    invoke-direct {v0, p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda20;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-void
.end method

.method private static ownRoomHeight(III)I
    .locals 1

    const/4 v0, 0x0

    .line 267
    invoke-static {v0, p0}, Ljava/lang/Math;->max(II)I

    move-result p0

    invoke-static {v0, p1}, Ljava/lang/Math;->max(II)I

    move-result p1

    invoke-static {v0, p2}, Ljava/lang/Math;->max(II)I

    move-result p2

    add-int/2addr p1, p2

    invoke-static {p0, p1}, Ljava/lang/Math;->max(II)I

    move-result p0

    return p0
.end method

.method private ownRoomRequiredHeight()I
    .locals 5

    .line 270
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    const/4 v1, 0x0

    if-eqz v0, :cond_3

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->getPaddingTop()I

    move-result v0

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-virtual {v2}, Landroid/widget/LinearLayout;->getPaddingBottom()I

    move-result v2

    add-int/2addr v0, v2

    :goto_0
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-virtual {v2}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result v2

    if-ge v1, v2, :cond_2

    .line 271
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-virtual {v2, v1}, Landroid/widget/LinearLayout;->getChildAt(I)Landroid/view/View;

    move-result-object v2

    invoke-virtual {v2}, Landroid/view/View;->getVisibility()I

    move-result v3

    const/16 v4, 0x8

    if-ne v3, v4, :cond_0

    goto :goto_2

    .line 272
    :cond_0
    instance-of v3, v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;

    if-eqz v3, :cond_1

    check-cast v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;->requiredHeight()I

    move-result v2

    goto :goto_1

    :cond_1
    invoke-virtual {v2}, Landroid/view/View;->getMeasuredHeight()I

    move-result v2

    :goto_1
    add-int/2addr v0, v2

    :goto_2
    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_2
    move v1, v0

    .line 274
    :cond_3
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomViewportHeight()I

    move-result v0

    const/high16 v2, 0x42c00000    # 96.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-static {v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomHeight(III)I

    move-result v0

    return v0
.end method

.method private pagePeers(I)V
    .locals 1

    .line 1053
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    add-int/2addr v0, p1

    const/16 p1, 0x28

    invoke-static {p1, v0}, Ljava/lang/Math;->min(II)I

    move-result p1

    const/4 v0, 0x0

    invoke-static {v0, p1}, Ljava/lang/Math;->max(II)I

    move-result p1

    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->setPeerPage(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-boolean p1, p1, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-nez p1, :cond_1

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->setRoomPage(I)V

    :cond_1
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v0, "Consultando esta p\u00e1gina de pessoas\u2026"

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda24;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda24;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V

    :cond_2
    :goto_0
    return-void
.end method

.method private pageRooms(I)V
    .locals 7

    .line 1054
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    add-int/2addr v0, p1

    const/16 p1, 0x28

    invoke-static {p1, v0}, Ljava/lang/Math;->min(II)I

    move-result p1

    const/4 v0, 0x0

    invoke-static {v0, p1}, Ljava/lang/Math;->max(II)I

    move-result p1

    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->setRoomPage(I)V

    iget v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    .line 1055
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v0, "Consultando esta p\u00e1gina de salas\u2026"

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 1056
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-boolean p1, p1, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-eqz p1, :cond_1

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->stopMultiplayerPoll()V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const/4 v4, 0x0

    const-wide/16 v5, 0x0

    move-object v1, p0

    invoke-direct/range {v1 .. v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->scheduleMultiplayerPoll(Lorg/emulationstation/frontend/netplay/StationOnlineClient;IIJ)V

    goto :goto_0

    .line 1057
    :cond_1
    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->setPeerPage(I)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda61;

    invoke-direct {p1, p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda61;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V

    :cond_2
    :goto_0
    return-void
.end method

.method private paint(Lorg/json/JSONObject;)V
    .locals 32

    move-object/from16 v6, p0

    move-object/from16 v7, p1

    .line 784
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_29

    const-string v1, "revision"

    invoke-virtual {v7, v1}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v2

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v4

    cmp-long v0, v2, v4

    if-ltz v0, :cond_29

    const-string v0, "peerPage"

    const-string v8, "page"

    invoke-virtual {v7, v8}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v2

    invoke-virtual {v7, v0, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v0

    iget v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    if-ne v0, v2, :cond_29

    invoke-virtual {v7, v8}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v0

    const-string v9, "roomPage"

    invoke-virtual {v7, v9, v0}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v0

    iget v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    if-eq v0, v2, :cond_0

    goto/16 :goto_1d

    .line 785
    :cond_0
    invoke-virtual {v7, v1}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v2

    iget-wide v4, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    cmp-long v0, v2, v4

    if-nez v0, :cond_1

    iget v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    iget v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedPage:I

    if-ne v0, v2, :cond_1

    iget v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    iget v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedRoomPage:I

    if-ne v0, v2, :cond_1

    return-void

    :cond_1
    invoke-virtual {v7, v1}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v0

    iput-wide v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    iget v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    iput v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedPage:I

    iget v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    iput v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paintedRoomPage:I

    .line 786
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-virtual {v0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;->observe(Lorg/json/JSONObject;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inviteNavigation:Landroid/widget/Button;

    const/4 v10, 0x0

    if-eqz v0, :cond_3

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v1, :cond_2

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-boolean v1, v1, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-eqz v1, :cond_2

    const/16 v1, 0x8

    goto :goto_0

    :cond_2
    move v1, v10

    :goto_0
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setVisibility(I)V

    .line 787
    :cond_3
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    iget-boolean v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    const/4 v11, 0x1

    if-nez v1, :cond_4

    iget-boolean v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v1, :cond_4

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v1

    if-nez v1, :cond_4

    move v1, v11

    goto :goto_1

    :cond_4
    move v1, v10

    :goto_1
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    const-string v0, "Online"

    invoke-direct {v6, v0, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setConnection(Ljava/lang/String;Z)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    iget-boolean v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    invoke-virtual {v1, v7, v2}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->text(Lorg/json/JSONObject;Z)Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->onlineNotice(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 788
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    if-eqz v0, :cond_5

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->getVisibility()I

    move-result v0

    if-nez v0, :cond_5

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_5

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    const-string v0, "As op\u00e7\u00f5es da sala mudaram. Confira o jogo antes de criar."

    invoke-direct {v6, v0, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    .line 789
    :cond_5
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    .line 790
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomScroll:Landroid/widget/ScrollView;

    invoke-virtual {v0}, Landroid/widget/ScrollView;->getScrollY()I

    move-result v12

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerScroll:Landroid/widget/ScrollView;

    invoke-virtual {v0}, Landroid/widget/ScrollView;->getScrollY()I

    move-result v13

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->beginRoomRows()V

    invoke-direct/range {p0 .. p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderPlayers(Lorg/json/JSONObject;)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    const-string v14, "room"

    .line 791
    invoke-virtual {v7, v14}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v15

    const-string v0, "selfId"

    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomTitle:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "SALAS  \u00b7  "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    const-string v2, "totalRooms"

    invoke-virtual {v7, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const-string v0, "invites"

    .line 792
    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v4

    const-string v2, "fromPeerId"

    const-string v1, "itemId"

    if-eqz v4, :cond_7

    move v3, v10

    :goto_2
    invoke-virtual {v4}, Lorg/json/JSONArray;->length()I

    move-result v0

    if-ge v3, v0, :cond_7

    invoke-virtual {v4, v3}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_6

    move-object/from16 v19, v4

    move/from16 v20, v12

    goto :goto_3

    :cond_6
    const-string v11, "inviteId"

    invoke-virtual {v0, v11}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v11

    move-object/from16 v19, v4

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    move/from16 v20, v12

    const-string v12, "invite"

    invoke-direct {v6, v12, v11, v4, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomCoverCard(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;

    move-result-object v4

    const-string v11, "CONVITE RECEBIDO"

    const v10, -0xb92401

    const/16 v12, 0xa

    invoke-direct {v6, v4, v11, v12, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v11

    invoke-direct {v6, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    new-instance v10, Ljava/lang/StringBuilder;

    invoke-direct {v10}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v11

    invoke-direct {v6, v7, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname(Lorg/json/JSONObject;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v11

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v11, "  \u00b7  "

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v11, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v12

    invoke-virtual {v11, v12}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v11

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v10}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v10

    const/16 v11, 0xe

    const v12, -0x100a01

    invoke-direct {v6, v4, v10, v11, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    const-string v11, "Todos precisam da mesma edi\u00e7\u00e3o do jogo."

    const/4 v12, 0x2

    invoke-direct {v6, v4, v10, v12, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->addSynopsis(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/String;)V

    new-instance v10, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda3;

    invoke-direct {v10, v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda3;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    const-string v11, "Aceitar e entrar"

    const/4 v12, 0x1

    invoke-direct {v6, v4, v11, v10, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    new-instance v10, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda10;

    invoke-direct {v10, v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda10;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    const-string v0, "Agora n\u00e3o"

    const/4 v11, 0x0

    invoke-direct {v6, v4, v0, v10, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    :goto_3
    add-int/lit8 v3, v3, 0x1

    move-object/from16 v4, v19

    move/from16 v12, v20

    const/4 v10, 0x0

    goto/16 :goto_2

    :cond_7
    move-object/from16 v19, v4

    move/from16 v20, v12

    const-string v0, "joinRequests"

    .line 793
    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v0

    if-eqz v0, :cond_9

    const/4 v3, 0x0

    :goto_4
    invoke-virtual {v0}, Lorg/json/JSONArray;->length()I

    move-result v4

    if-ge v3, v4, :cond_9

    invoke-virtual {v0, v3}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v4

    if-nez v4, :cond_8

    move-object/from16 v21, v0

    goto :goto_5

    :cond_8
    iget-object v10, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->card(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v10

    iget-object v11, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v11, v10}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    const-string v11, "PEDIDO PARA JOGAR"

    move-object/from16 v21, v0

    const v0, -0xb92401

    const/16 v12, 0xa

    invoke-direct {v6, v10, v11, v12, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v11

    invoke-direct {v6, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    invoke-virtual {v4, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-direct {v6, v7, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname(Lorg/json/JSONObject;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const/16 v11, 0xf

    const v12, -0x100a01

    invoke-direct {v6, v10, v0, v11, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda11;

    invoke-direct {v0, v6, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda11;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    const-string v11, "Aceitar pedido"

    const/4 v12, 0x1

    invoke-direct {v6, v10, v11, v0, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda12;

    invoke-direct {v0, v6, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda12;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    const-string v4, "Recusar"

    const/4 v11, 0x0

    invoke-direct {v6, v10, v4, v0, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    :goto_5
    add-int/lit8 v3, v3, 0x1

    move-object/from16 v0, v21

    goto :goto_4

    :cond_9
    const-string v10, "hostId"

    const-string v11, "recoveryProtocol"

    const-string v12, "station-stream.v3"

    const-string v4, "state"

    const-string v3, "waiting"

    const-string v0, "roomId"

    if-eqz v15, :cond_12

    move-object/from16 v22, v2

    .line 795
    invoke-virtual {v15, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    move-object/from16 v23, v0

    invoke-virtual {v15, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    move/from16 v24, v13

    const-string v13, "own"

    move-object/from16 v25, v9

    const/4 v9, 0x1

    invoke-direct {v6, v13, v2, v0, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomCoverCard(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;

    move-result-object v0

    .line 796
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v2

    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v13, 0x41a00000    # 20.0f

    invoke-direct {v6, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    move-object/from16 v26, v8

    const/4 v8, -0x1

    invoke-direct {v9, v8, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v2, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const-string v9, "SUA SALA"

    const v8, -0xb92401

    const/16 v13, 0xa

    .line 797
    invoke-direct {v6, v9, v13, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v9

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const v8, 0x3df5c28f    # 0.12f

    invoke-virtual {v9, v8}, Landroid/widget/TextView;->setLetterSpacing(F)V

    new-instance v8, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v13, 0x3f800000    # 1.0f

    move-object/from16 v27, v14

    const/4 v14, -0x2

    move-object/from16 v28, v12

    const/4 v12, 0x0

    invoke-direct {v8, v12, v14, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v2, v9, v8}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 798
    new-instance v2, Ljava/lang/StringBuilder;

    const-string v8, "Sua sala. "

    invoke-direct {v2, v8}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-object v8, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v15, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v12

    invoke-virtual {v8, v12}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v8

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v8, ". Toque para ver os detalhes e como jogar."

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v9, v2}, Landroid/widget/TextView;->setContentDescription(Ljava/lang/CharSequence;)V

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda13;

    invoke-direct {v2, v6, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda13;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    invoke-virtual {v9, v2}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 799
    invoke-static {v15, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomInfo(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;

    move-result-object v2

    iget-object v2, v2, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->summary:Ljava/lang/String;

    const/16 v8, 0xb

    const v9, -0xb92401

    invoke-direct {v6, v0, v2, v8, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    const/high16 v8, 0x40800000    # 4.0f

    invoke-direct {v6, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    const/4 v12, 0x0

    invoke-virtual {v2, v12, v12, v12, v9}, Landroid/widget/TextView;->setPadding(IIII)V

    const/4 v9, 0x2

    invoke-virtual {v2, v9}, Landroid/widget/TextView;->setMaxLines(I)V

    .line 800
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v2

    new-instance v12, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v13, -0x1

    invoke-direct {v12, v13, v14}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v2, v12}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    invoke-direct {v6, v2, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderParticipants(Landroid/widget/LinearLayout;Lorg/json/JSONObject;)V

    const-string v2, "ready"

    .line 801
    invoke-virtual {v15, v2}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v2

    const-string v12, ""

    const/16 v13, 0xb

    const v14, -0x554736

    .line 802
    invoke-direct {v6, v0, v12, v13, v14}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v12

    iput-object v12, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomReadiness:Landroid/widget/TextView;

    invoke-direct {v6, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    invoke-direct {v6, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v8

    const/4 v9, 0x0

    invoke-virtual {v12, v9, v13, v9, v8}, Landroid/widget/TextView;->setPadding(IIII)V

    iget-object v8, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomReadiness:Landroid/widget/TextView;

    const/4 v9, 0x1

    invoke-virtual {v8, v9}, Landroid/widget/TextView;->setAccessibilityLiveRegion(I)V

    .line 803
    invoke-direct {v6, v0, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomGuide(Landroid/widget/LinearLayout;Lorg/json/JSONObject;)V

    .line 804
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomControls(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v8

    .line 805
    invoke-virtual {v15, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_d

    .line 806
    invoke-static {v2, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->contains(Lorg/json/JSONArray;Ljava/lang/String;)Z

    move-result v9

    if-eqz v9, :cond_a

    const-string v0, "Desmarcar"

    goto :goto_6

    :cond_a
    const-string v0, "Estou pronto"

    :goto_6
    move-object v12, v0

    if-eqz v9, :cond_b

    const/16 v0, 0xe

    goto :goto_7

    :cond_b
    const/4 v0, 0x7

    :goto_7
    move v13, v0

    xor-int/lit8 v17, v9, 0x1

    .line 807
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda14;

    invoke-direct {v0, v6, v2, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda14;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONArray;Ljava/lang/String;)V

    move v2, v14

    move-object/from16 v29, v23

    move-object v14, v0

    move-object/from16 v0, p0

    move-object/from16 v30, v1

    move-object v1, v8

    move-object/from16 v31, v22

    move-object v2, v12

    move-object v12, v3

    move v3, v13

    move-object v13, v4

    move/from16 v4, v17

    move-object v7, v5

    move-object v5, v14

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ready:Landroid/widget/Button;

    if-eqz v9, :cond_c

    const-string v1, "Desmarcar sua confirma\u00e7\u00e3o"

    goto :goto_8

    :cond_c
    const-string v1, "Confirmar que voc\u00ea est\u00e1 pronto para jogar"

    .line 808
    :goto_8
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setContentDescription(Ljava/lang/CharSequence;)V

    goto :goto_9

    :cond_d
    move-object/from16 v30, v1

    move-object v12, v3

    move-object v13, v4

    move-object v7, v5

    move-object/from16 v31, v22

    move-object/from16 v29, v23

    .line 810
    :goto_9
    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomConfirmationKey(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    .line 811
    invoke-virtual {v15, v13}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v12, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_e

    invoke-virtual {v15, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v7, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_e

    const-string v2, "Iniciar"

    const/16 v3, 0x8

    const/4 v4, 0x1

    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda15;

    invoke-direct {v5, v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda15;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;)V

    move-object/from16 v0, p0

    move-object v1, v8

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v0

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->start:Landroid/widget/Button;

    :cond_e
    const-string v2, "Sair"

    const/16 v3, 0x9

    const/4 v4, 0x2

    .line 812
    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda16;

    invoke-direct {v5, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda16;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    move-object/from16 v0, p0

    move-object v1, v8

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    move-result-object v0

    const-string v1, "Sair da sala atual"

    .line 813
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setContentDescription(Ljava/lang/CharSequence;)V

    const-string v2, "Conversa"

    const/4 v3, 0x3

    const/4 v4, 0x0

    .line 814
    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda17;

    invoke-direct {v5, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda17;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    move-object/from16 v0, p0

    move-object v1, v8

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    .line 815
    invoke-virtual {v15, v11}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    move-object/from16 v9, v28

    invoke-virtual {v9, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_f

    invoke-static/range {p1 .. p1}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->shareable(Lorg/json/JSONObject;)Z

    move-result v0

    if-eqz v0, :cond_f

    const-string v2, "Convidar"

    const/4 v3, 0x4

    const/4 v4, 0x0

    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda18;

    invoke-direct {v5, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda18;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    move-object/from16 v0, p0

    move-object v1, v8

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    .line 816
    :cond_f
    invoke-virtual {v15, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v7, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    invoke-static {v15, v0}, Lorg/emulationstation/frontend/netplay/StationLaunchPolicy;->eligible(Lorg/json/JSONObject;Z)Z

    move-result v0

    if-eqz v0, :cond_11

    iget-boolean v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_10

    invoke-static {v15}, Lorg/emulationstation/frontend/netplay/StationLaunchPolicy;->key(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchKey:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_10

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->actionLine(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v1

    const-string v2, "Abrir partida"

    const/16 v3, 0x8

    const/4 v4, 0x1

    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda4;

    move-object v8, v7

    move-object/from16 v7, p1

    invoke-direct {v5, v6, v15, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda4;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;Lorg/json/JSONObject;)V

    move-object/from16 v0, p0

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;

    goto :goto_a

    :cond_10
    move-object v8, v7

    move-object/from16 v7, p1

    invoke-direct {v6, v15, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launch(Lorg/json/JSONObject;Lorg/json/JSONObject;)V

    goto :goto_a

    :cond_11
    move-object v8, v7

    move-object/from16 v7, p1

    goto :goto_a

    :cond_12
    move-object/from16 v29, v0

    move-object/from16 v30, v1

    move-object/from16 v31, v2

    move-object/from16 v26, v8

    move-object/from16 v25, v9

    move-object v9, v12

    move/from16 v24, v13

    move-object/from16 v27, v14

    move-object v12, v3

    move-object v13, v4

    move-object v8, v5

    :goto_a
    const-string v0, "rooms"

    .line 819
    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v0

    const/4 v1, 0x0

    const/4 v2, 0x0

    :goto_b
    if-eqz v0, :cond_1c

    .line 820
    invoke-virtual {v0}, Lorg/json/JSONArray;->length()I

    move-result v3

    if-ge v1, v3, :cond_1c

    invoke-virtual {v0, v1}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v3

    if-eqz v3, :cond_1b

    move-object/from16 v4, v29

    if-eqz v15, :cond_13

    invoke-virtual {v15, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v5, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_13

    move-object/from16 v16, v0

    move-object/from16 v17, v15

    goto/16 :goto_12

    :cond_13
    add-int/lit8 v2, v2, 0x1

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    move-object/from16 v16, v0

    move-object/from16 v14, v30

    invoke-virtual {v3, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    move/from16 v18, v2

    move-object/from16 v17, v15

    move-object/from16 v15, v27

    const/4 v2, 0x0

    invoke-direct {v6, v15, v5, v0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomCoverCard(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;

    move-result-object v0

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v3, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v2, v5}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    const/16 v5, 0xf

    const v15, -0x100a01

    invoke-direct {v6, v0, v2, v5, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    invoke-direct {v6, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-direct {v6, v7, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nickname(Lorg/json/JSONObject;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v5, "  \u00b7  "

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {v3, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomInfo(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;

    move-result-object v5

    iget-object v5, v5, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->summary:Ljava/lang/String;

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    const/16 v5, 0xc

    const v15, -0x554736

    invoke-direct {v6, v0, v2, v5, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    invoke-virtual {v3, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-direct {v6, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v5

    const/4 v15, 0x2

    invoke-direct {v6, v0, v2, v15, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->addSynopsis(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/String;)V

    invoke-static {v3, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomInfo(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;

    move-result-object v2

    invoke-virtual {v3, v11}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v9, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_14

    iget-boolean v5, v2, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->confirmed:Z

    if-eqz v5, :cond_15

    iget-boolean v5, v2, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->acceptingPlayers:Z

    if-eqz v5, :cond_15

    iget v2, v2, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->vacancies:I

    if-lez v2, :cond_15

    goto :goto_c

    :cond_14
    invoke-virtual {v3, v13}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v12, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_15

    const-string v2, "players"

    invoke-virtual {v3, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v2

    const-string v5, "maximumPlayers"

    invoke-virtual {v3, v5, v15}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v5

    const-string v15, "capacity"

    invoke-virtual {v3, v15, v5}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v5

    if-ge v2, v5, :cond_15

    :goto_c
    const/4 v2, 0x1

    goto :goto_d

    :cond_15
    const/4 v2, 0x0

    :goto_d
    if-eqz v2, :cond_1a

    invoke-virtual {v3, v11}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v9, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-nez v2, :cond_16

    const-string v2, "join-request-v1"

    invoke-static {v7, v2}, Lorg/emulationstation/frontend/netplay/StationSocial;->supports(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_16

    const/4 v2, 0x1

    goto :goto_e

    :cond_16
    const/4 v2, 0x0

    :goto_e
    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-static {v7, v5}, Lorg/emulationstation/frontend/netplay/StationSocial;->requested(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v5

    if-eqz v5, :cond_17

    const-string v5, "Pedido enviado"

    goto :goto_f

    :cond_17
    if-eqz v2, :cond_18

    const-string v5, "Pedir para jogar"

    goto :goto_f

    :cond_18
    const-string v5, "Entrar na sala"

    :goto_f
    new-instance v15, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda5;

    invoke-direct {v15, v6, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda5;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ZLorg/json/JSONObject;)V

    const/4 v2, 0x1

    invoke-direct {v6, v0, v5, v15, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v0

    iget-boolean v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v2, :cond_19

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-static {v7, v2}, Lorg/emulationstation/frontend/netplay/StationSocial;->requested(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_19

    const/4 v2, 0x1

    goto :goto_10

    :cond_19
    const/4 v2, 0x0

    :goto_10
    invoke-virtual {v0, v2}, Landroid/widget/Button;->setEnabled(Z)V

    const v5, -0x554736

    goto :goto_11

    :cond_1a
    const-string v2, "Partida em andamento ou sala completa"

    const/16 v3, 0xc

    const v5, -0x554736

    invoke-direct {v6, v0, v2, v3, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    :goto_11
    move/from16 v2, v18

    goto :goto_13

    :cond_1b
    move-object/from16 v16, v0

    move-object/from16 v17, v15

    move-object/from16 v4, v29

    :goto_12
    move-object/from16 v14, v30

    const v5, -0x554736

    :goto_13
    add-int/lit8 v1, v1, 0x1

    move-object/from16 v29, v4

    move-object/from16 v30, v14

    move-object/from16 v0, v16

    move-object/from16 v15, v17

    goto/16 :goto_b

    :cond_1c
    move-object/from16 v17, v15

    if-nez v2, :cond_1f

    if-nez v17, :cond_1f

    if-eqz v19, :cond_1e

    .line 821
    invoke-virtual/range {v19 .. v19}, Lorg/json/JSONArray;->length()I

    move-result v0

    if-nez v0, :cond_1d

    goto :goto_14

    :cond_1d
    move-object/from16 v0, v26

    const/4 v3, 0x1

    goto :goto_16

    :cond_1e
    :goto_14
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    const-string v1, "Ainda n\u00e3o h\u00e1 salas aqui"

    const-string v2, "Crie a primeira sala ou procure pessoas online para combinar uma partida."

    const-string v3, "+"

    invoke-direct {v6, v0, v3, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v1}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result v2

    const/4 v3, 0x1

    sub-int/2addr v2, v3

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->getChildAt(I)Landroid/view/View;

    move-result-object v1

    invoke-interface {v0, v1}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_15

    :cond_1f
    const/4 v3, 0x1

    :goto_15
    move-object/from16 v0, v26

    .line 822
    :goto_16
    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v0

    move-object/from16 v1, v25

    invoke-virtual {v7, v1, v0}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v0

    if-lez v0, :cond_20

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda6;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda6;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v4, "\u2190 P\u00e1gina anterior"

    const/4 v5, 0x0

    invoke-direct {v6, v1, v4, v2, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v1

    invoke-interface {v0, v1}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    :cond_20
    const-string v0, "nextRoomPage"

    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_21

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda7;

    invoke-direct {v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda7;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v4, "Mais salas \u2192"

    const/4 v11, 0x0

    invoke-direct {v6, v1, v4, v2, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v1

    invoke-interface {v0, v1}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_17

    :cond_21
    const/4 v11, 0x0

    .line 823
    :goto_17
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->reconcileRoomRows()V

    const-string v0, "directMessages"

    .line 824
    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v0

    if-eqz v0, :cond_27

    move v1, v11

    :goto_18
    invoke-virtual {v0}, Lorg/json/JSONArray;->length()I

    move-result v2

    if-ge v1, v2, :cond_27

    invoke-virtual {v0, v1}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v2

    if-eqz v2, :cond_25

    const-string v4, "toPeerId"

    invoke-virtual {v2, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v8, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-nez v4, :cond_22

    goto :goto_1b

    :cond_22
    const-string v4, "messageId"

    invoke-virtual {v2, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    iget-object v5, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->seenMessages:Ljava/util/Set;

    invoke-interface {v5, v4}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v5

    if-nez v5, :cond_23

    iget-object v5, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    move-object/from16 v9, v31

    invoke-virtual {v2, v9}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    invoke-virtual {v5, v10}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-nez v5, :cond_24

    invoke-virtual {v2, v9}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    iput-object v5, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    const-string v5, "nickname"

    const-string v10, "Jogador"

    invoke-virtual {v2, v5, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    iput-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingName:Ljava/lang/String;

    goto :goto_19

    :cond_23
    move-object/from16 v9, v31

    :cond_24
    :goto_19
    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->seenMessages:Ljava/util/Set;

    invoke-interface {v2, v4}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    :goto_1a
    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->seenMessages:Ljava/util/Set;

    invoke-interface {v2}, Ljava/util/Set;->size()I

    move-result v2

    const/16 v4, 0x80

    if-le v2, v4, :cond_26

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->seenMessages:Ljava/util/Set;

    invoke-interface {v2}, Ljava/util/Set;->iterator()Ljava/util/Iterator;

    move-result-object v4

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    invoke-interface {v2, v4}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    goto :goto_1a

    :cond_25
    :goto_1b
    move-object/from16 v9, v31

    :cond_26
    add-int/lit8 v1, v1, 0x1

    move-object/from16 v31, v9

    goto :goto_18

    .line 825
    :cond_27
    invoke-direct/range {p0 .. p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderConversation(Lorg/json/JSONObject;)V

    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateStartState()V

    if-eqz v17, :cond_28

    move v10, v3

    goto :goto_1c

    :cond_28
    move v10, v11

    :goto_1c
    invoke-direct {v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerScroll:Landroid/widget/ScrollView;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda8;

    move/from16 v2, v24

    invoke-direct {v1, v6, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda8;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->post(Ljava/lang/Runnable;)Z

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomScroll:Landroid/widget/ScrollView;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda9;

    move/from16 v2, v20

    invoke-direct {v1, v6, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda9;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->post(Ljava/lang/Runnable;)Z

    :cond_29
    :goto_1d
    return-void
.end method

.method private panel(Landroid/widget/LinearLayout;FZ)Landroid/widget/LinearLayout;
    .locals 5

    .line 118
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v0

    const/high16 v1, 0x41000000    # 8.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    const/high16 v3, 0x40c00000    # 6.0f

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-virtual {v0, v2, v4, v1, v3}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    const/4 v2, -0x1

    if-eqz p3, :cond_0

    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v3, 0x438c0000    # 280.0f

    invoke-direct {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {p2, v2, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    goto :goto_0

    :cond_0
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v3, v1, v2, p2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    move-object p2, v3

    :goto_0
    const/high16 v2, 0x41200000    # 10.0f

    if-eqz p3, :cond_1

    move v3, v1

    goto :goto_1

    :cond_1
    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    :goto_1
    if-eqz p3, :cond_2

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    goto :goto_2

    :cond_2
    move p3, v1

    :goto_2
    invoke-virtual {p2, v1, v1, v3, p3}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {p1, v0, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-object v0
.end method

.method private pill(Ljava/lang/String;I)Landroid/widget/TextView;
    .locals 3

    const/16 v0, 0xa

    .line 116
    invoke-direct {p0, p1, v0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/4 p2, 0x1

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setSingleLine(Z)V

    const/16 p2, 0x11

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setGravity(I)V

    const/high16 p2, 0x41100000    # 9.0f

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/high16 v1, 0x40a00000    # 5.0f

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p2

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-virtual {p1, v0, v2, p2, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    const p2, -0xeed8c5

    const v0, -0xd6b8a2

    invoke-direct {p0, p2, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object p2

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setBackground(Landroid/graphics/drawable/Drawable;)V

    return-object p1
.end method

.method private static playGuidance(Ljava/lang/String;)Ljava/lang/String;
    .locals 11

    const-string v0, ""

    if-eqz p0, :cond_8

    .line 239
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_0

    goto/16 :goto_4

    .line 240
    :cond_0
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "\\r?\\n"

    .line 241
    invoke-virtual {p0, v2}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0

    array-length v2, p0

    const/4 v3, 0x0

    move v4, v3

    :goto_0
    if-ge v4, v2, :cond_7

    aget-object v5, p0, v4

    const-string v6, "\\[([^\\]]+)\\]\\((?:https?://|www\\.)[^\\s)]+\\)"

    const-string v7, "$1"

    .line 242
    invoke-virtual {v5, v6, v7}, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    const-string v6, "(?i)(?:https?://|www\\.)[^\\s]+"

    .line 243
    invoke-virtual {v5, v6, v0}, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v5

    .line 244
    invoke-virtual {v5}, Ljava/lang/String;->isEmpty()Z

    move-result v6

    if-eqz v6, :cond_1

    goto :goto_3

    .line 245
    :cond_1
    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    const-string v7, "(?<=[.!?;])\\s+"

    .line 246
    invoke-virtual {v5, v7}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v5

    array-length v7, v5

    move v8, v3

    :goto_1
    if-ge v8, v7, :cond_4

    aget-object v9, v5, v8

    .line 247
    sget-object v10, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->TECHNICAL_COPY:Ljava/util/regex/Pattern;

    invoke-virtual {v10, v9}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v10

    invoke-virtual {v10}, Ljava/util/regex/Matcher;->find()Z

    move-result v10

    if-eqz v10, :cond_2

    goto :goto_2

    .line 248
    :cond_2
    invoke-virtual {v6}, Ljava/lang/StringBuilder;->length()I

    move-result v10

    if-lez v10, :cond_3

    const/16 v10, 0x20

    invoke-virtual {v6, v10}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    :cond_3
    invoke-virtual {v9}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v9

    invoke-virtual {v6, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    :goto_2
    add-int/lit8 v8, v8, 0x1

    goto :goto_1

    .line 250
    :cond_4
    invoke-virtual {v6}, Ljava/lang/StringBuilder;->length()I

    move-result v5

    if-lez v5, :cond_6

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->length()I

    move-result v5

    if-lez v5, :cond_5

    const/16 v5, 0xa

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    :cond_5
    invoke-virtual {v1, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/CharSequence;)Ljava/lang/StringBuilder;

    :cond_6
    :goto_3
    add-int/lit8 v4, v4, 0x1

    goto :goto_0

    .line 252
    :cond_7
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_8
    :goto_4
    return-object v0
.end method

.method private prepareRoom(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;ILjava/lang/String;)V
    .locals 8

    .line 701
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v0, :cond_2

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_2

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_0

    goto :goto_0

    .line 702
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    if-eqz v0, :cond_2

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_2

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v0

    if-nez v0, :cond_1

    goto :goto_0

    .line 703
    :cond_1
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    const/4 v0, 0x1

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const-string v1, "Conferindo\u2026"

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const/4 v0, 0x0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    .line 704
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupConfirm:Landroid/widget/Button;

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "Conferindo a edi\u00e7\u00e3o, o modo e os "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, p2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, " jogadores selecionados\u2026"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 705
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda56;

    invoke-direct {v0, p0, v3, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda56;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)V

    new-instance v7, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda57;

    move-object v1, v7

    move-object v2, p0

    move-object v4, p3

    move-object v5, p1

    move v6, p2

    invoke-direct/range {v1 .. v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda57;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;I)V

    invoke-direct {p0, v0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    :cond_2
    :goto_0
    return-void
.end method

.method private static profileInfo(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;
    .locals 5

    .line 554
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->maximumPlayers:I

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->mode:Ljava/lang/String;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->controllerProfile:Ljava/lang/String;

    const/4 v4, 0x1

    invoke-static {v4, v0, v1, v2, v3}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->fromVerifiedProfile(ZI[ILjava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->modeTitle:Ljava/lang/String;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->instructions:[Ljava/lang/String;

    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->sources:[Ljava/lang/String;

    invoke-virtual {v0, v1, v2, p0}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->withHelp(Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object p0

    return-object p0
.end method

.method private readPoll(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    const/4 v0, 0x0

    .line 1046
    :goto_0
    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v1, :cond_1

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v1, p2, :cond_1

    .line 1047
    invoke-virtual {p3}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->check()V

    .line 1048
    :try_start_0
    invoke-interface {p1, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;->run(Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    return-object p1

    :catch_0
    move-exception v1

    .line 1049
    invoke-virtual {p3}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->check()V

    add-int/lit8 v0, v0, 0x1

    invoke-static {v1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->pollRetryDelay(Ljava/lang/Throwable;I)J

    move-result-wide v2

    const-wide/16 v4, 0x0

    cmp-long v4, v2, v4

    if-ltz v4, :cond_0

    invoke-static {v2, v3}, Ljava/lang/Thread;->sleep(J)V

    invoke-virtual {p3}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->check()V

    goto :goto_0

    :cond_0
    throw v1

    .line 1051
    :cond_1
    new-instance p1, Ljava/io/InterruptedIOException;

    const-string p2, "Read poll cancelled by lifecycle"

    invoke-direct {p1, p2}, Ljava/io/InterruptedIOException;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method private reconcileRoomRows()V
    .locals 5

    .line 337
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    invoke-interface {v0}, Ljava/util/Map;->entrySet()Ljava/util/Set;

    move-result-object v0

    invoke-interface {v0}, Ljava/util/Set;->iterator()Ljava/util/Iterator;

    move-result-object v0

    .line 338
    :cond_0
    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_1

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/util/Map$Entry;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    invoke-interface {v1}, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;

    move-result-object v3

    invoke-interface {v2, v3}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v2

    if-nez v2, :cond_0

    invoke-interface {v1}, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;

    iget-object v1, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->display:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    const/4 v2, 0x0

    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    invoke-interface {v0}, Ljava/util/Iterator;->remove()V

    goto :goto_0

    .line 339
    :cond_1
    new-instance v0, Ljava/util/IdentityHashMap;

    invoke-direct {v0}, Ljava/util/IdentityHashMap;-><init>()V

    invoke-static {v0}, Ljava/util/Collections;->newSetFromMap(Ljava/util/Map;)Ljava/util/Set;

    move-result-object v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v0, v1}, Ljava/util/Set;->addAll(Ljava/util/Collection;)Z

    .line 340
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v1}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result v1

    const/4 v2, 0x1

    sub-int/2addr v1, v2

    :goto_1
    if-ltz v1, :cond_3

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v3, v1}, Landroid/widget/LinearLayout;->getChildAt(I)Landroid/view/View;

    move-result-object v3

    invoke-interface {v0, v3}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v3

    if-nez v3, :cond_2

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v3, v1}, Landroid/widget/LinearLayout;->removeViewAt(I)V

    :cond_2
    add-int/lit8 v1, v1, -0x1

    goto :goto_1

    .line 341
    :cond_3
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->size()I

    move-result v1

    const/4 v3, 0x0

    if-ne v0, v1, :cond_4

    move v0, v2

    goto :goto_2

    :cond_4
    move v0, v3

    :goto_2
    move v1, v3

    :goto_3
    if-eqz v0, :cond_6

    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v4}, Ljava/util/List;->size()I

    move-result v4

    if-ge v1, v4, :cond_6

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->getChildAt(I)Landroid/view/View;

    move-result-object v0

    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v4, v1}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v4

    if-ne v0, v4, :cond_5

    move v0, v2

    goto :goto_4

    :cond_5
    move v0, v3

    :goto_4
    add-int/lit8 v1, v1, 0x1

    goto :goto_3

    :cond_6
    if-nez v0, :cond_7

    .line 343
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_5
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_7

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/view/View;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-virtual {v2, v1}, Landroid/widget/LinearLayout;->bringChildToFront(Landroid/view/View;)V

    goto :goto_5

    .line 344
    :cond_7
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    invoke-interface {v0}, Ljava/util/Set;->clear()V

    return-void
.end method

.method private static recordFailure(Ljava/lang/Throwable;)V
    .locals 7

    .line 536
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const/4 v1, 0x0

    move v2, v1

    :goto_0
    if-eqz p0, :cond_2

    const/4 v3, 0x3

    if-ge v2, v3, :cond_2

    const-string v3, " type="

    .line 538
    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/Class;->getName()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 539
    instance-of v3, p0, Lorg/emulationstation/frontend/station/StationApi$Failure;

    if-eqz v3, :cond_0

    move-object v3, p0

    check-cast v3, Lorg/emulationstation/frontend/station/StationApi$Failure;

    const-string v4, " http="

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget v4, v3, Lorg/emulationstation/frontend/station/StationApi$Failure;->status:I

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    iget-object v4, v3, Lorg/emulationstation/frontend/station/StationApi$Failure;->code:Ljava/lang/String;

    if-eqz v4, :cond_0

    iget-object v4, v3, Lorg/emulationstation/frontend/station/StationApi$Failure;->code:Ljava/lang/String;

    const-string v5, "[A-Z0-9_]{1,80}"

    invoke-virtual {v4, v5}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v4

    if-eqz v4, :cond_0

    const-string v4, " code="

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v3, v3, Lorg/emulationstation/frontend/station/StationApi$Failure;->code:Ljava/lang/String;

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 540
    :cond_0
    invoke-virtual {p0}, Ljava/lang/Throwable;->getStackTrace()[Ljava/lang/StackTraceElement;

    move-result-object v3

    move v4, v1

    :goto_1
    array-length v5, v3

    const/16 v6, 0x8

    invoke-static {v5, v6}, Ljava/lang/Math;->min(II)I

    move-result v5

    if-ge v4, v5, :cond_1

    const-string v5, " at="

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    aget-object v5, v3, v4

    invoke-virtual {v5}, Ljava/lang/StackTraceElement;->getClassName()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/16 v5, 0x2e

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    aget-object v5, v3, v4

    invoke-virtual {v5}, Ljava/lang/StackTraceElement;->getMethodName()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/16 v5, 0x3a

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;

    aget-object v5, v3, v4

    invoke-virtual {v5}, Ljava/lang/StackTraceElement;->getLineNumber()I

    move-result v5

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    add-int/lit8 v4, v4, 0x1

    goto :goto_1

    :cond_1
    add-int/lit8 v2, v2, 0x1

    .line 537
    invoke-virtual {p0}, Ljava/lang/Throwable;->getCause()Ljava/lang/Throwable;

    move-result-object p0

    goto :goto_0

    :cond_2
    const-string p0, "StationRooms"

    .line 542
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {p0, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method

.method private refreshPlayerSheet()V
    .locals 11

    .line 882
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-eqz v0, :cond_7

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_7

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedPeer:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_0

    goto/16 :goto_5

    .line 883
    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedPeer:Ljava/lang/String;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedName:Ljava/lang/String;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-static {v0, v1, v2, v3}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->read(Lorg/json/JSONObject;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationPlayerModel;

    move-result-object v0

    .line 884
    iget-object v1, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->ownedRoom:Lorg/json/JSONObject;

    if-nez v1, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    goto :goto_0

    :cond_1
    iget-object v1, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->ownedRoom:Lorg/json/JSONObject;

    const-string v2, "itemId"

    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 885
    :goto_0
    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->roomItemId:Ljava/lang/String;

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    const-string v3, ""

    if-eqz v2, :cond_2

    move-object v6, v3

    goto :goto_1

    :cond_2
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v5, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->roomItemId:Ljava/lang/String;

    invoke-virtual {v2, v5}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    move-object v6, v2

    :goto_1
    if-nez v1, :cond_3

    const-string v1, "Jogo n\u00e3o selecionado"

    goto :goto_2

    :cond_3
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v2, v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    :goto_2
    move-object v7, v1

    iget-boolean v8, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    iget-object v9, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "join-request-v1"

    invoke-static {v1, v2}, Lorg/emulationstation/frontend/netplay/StationSocial;->supports(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v10

    move-object v5, v0

    invoke-virtual/range {v4 .. v10}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->render(Lorg/emulationstation/frontend/netplay/StationPlayerModel;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Z)V

    iget-object v1, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->roomItemId:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_4

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    goto :goto_3

    :cond_4
    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->roomItemId:Ljava/lang/String;

    :goto_3
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    const/4 v2, 0x0

    if-eqz v0, :cond_6

    .line 886
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v4

    if-eqz v4, :cond_5

    goto :goto_4

    .line 887
    :cond_5
    iget-object v3, v1, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->coverItem:Ljava/lang/String;

    invoke-virtual {v0, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-nez v3, :cond_7

    iput-object v0, v1, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->coverItem:Ljava/lang/String;

    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->setCover(Landroid/graphics/Bitmap;)V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda73;

    invoke-direct {v3, p0, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda73;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationPlayerSheet;Ljava/lang/String;)V

    const/16 v1, 0x100

    invoke-virtual {v2, v0, v1, v3}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->load(Ljava/lang/String;ILorg/emulationstation/frontend/netplay/StationRoomArtwork$Callback;)V

    goto :goto_5

    .line 886
    :cond_6
    :goto_4
    iput-object v3, v1, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->coverItem:Ljava/lang/String;

    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->setCover(Landroid/graphics/Bitmap;)V

    :cond_7
    :goto_5
    return-void
.end method

.method private renderConversation(Lorg/json/JSONObject;)V
    .locals 18

    move-object/from16 v6, p0

    move-object/from16 v7, p1

    const-string v8, "utcMs"

    .line 832
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inboxNotice:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingName:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, " \u2022 nova mensagem  \u203a"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inboxNotice:Landroid/widget/TextView;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_0

    const/16 v1, 0x8

    goto :goto_0

    :cond_0
    const/4 v1, 0x0

    :goto_0
    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setVisibility(I)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navChat:Landroid/widget/Button;

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_1

    const-string v1, "Conversas"

    goto :goto_1

    :cond_1
    const-string v1, "Nova mensagem"

    :goto_1
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 833
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    invoke-virtual {v0}, Landroid/widget/ScrollView;->getScrollY()I

    move-result v10

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->getHeight()I

    move-result v0

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    invoke-virtual {v1}, Landroid/widget/ScrollView;->getHeight()I

    move-result v1

    sub-int/2addr v0, v1

    sub-int/2addr v0, v10

    const/high16 v1, 0x42800000    # 64.0f

    invoke-direct {v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    const/4 v11, 0x1

    if-ge v0, v1, :cond_2

    move v12, v11

    goto :goto_2

    :cond_2
    const/4 v12, 0x0

    :goto_2
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatActions:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    const-string v0, "room"

    invoke-virtual {v7, v0}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "selfId"

    invoke-virtual {v7, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v13

    .line 834
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    const-string v14, "Jogador"

    const-string v15, "nickname"

    const-string v5, "\u2026"

    if-nez v1, :cond_b

    .line 835
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    invoke-static {v7, v0}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->peer(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_3

    invoke-virtual {v0, v15, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    iput-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    :cond_3
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatTitle:Landroid/widget/TextView;

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatHint:Landroid/widget/TextView;

    if-nez v0, :cond_4

    const-string v0, "Presen\u00e7a n\u00e3o confirmada nesta p\u00e1gina"

    goto :goto_3

    :cond_4
    const-string v2, "status"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v2, "in-room"

    invoke-virtual {v2, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_5

    const-string v0, "Em uma sala"

    goto :goto_3

    :cond_5
    const-string v0, "Online no aplicativo"

    :goto_3
    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 836
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatActions:Landroid/widget/LinearLayout;

    const-string v2, "Perfil / convite"

    const/16 v3, 0x91

    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda26;

    invoke-direct {v4, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda26;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const/16 v16, 0x0

    move-object/from16 v0, p0

    move-object v9, v5

    move/from16 v5, v16

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inline(Landroid/widget/LinearLayout;Ljava/lang/String;ILjava/lang/Runnable;Z)Landroid/widget/Button;

    const-string v0, "direct-chat-v1"

    .line 837
    invoke-static {v7, v0}, Lorg/emulationstation/frontend/netplay/StationSocial;->supports(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_6

    iget-boolean v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v1, :cond_6

    move v1, v11

    goto :goto_4

    :cond_6
    const/4 v1, 0x0

    :goto_4
    invoke-direct {v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->composer(Z)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    if-eqz v0, :cond_7

    const-string v2, "Mensagem privada\u2026"

    goto :goto_5

    :cond_7
    const-string v2, "Conversa privada aguardando ativa\u00e7\u00e3o"

    :goto_5
    invoke-virtual {v1, v2}, Landroid/widget/EditText;->setHint(Ljava/lang/CharSequence;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    invoke-static {v7, v1}, Lorg/emulationstation/frontend/netplay/StationSocial;->messages(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v1

    iget v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v3, 0x3

    if-ne v2, v3, :cond_9

    const/4 v2, 0x0

    :goto_6
    invoke-virtual {v1}, Lorg/json/JSONArray;->length()I

    move-result v3

    if-ge v2, v3, :cond_9

    invoke-virtual {v1, v2}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v3

    if-eqz v3, :cond_8

    const-string v4, "toPeerId"

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v13, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_8

    const-string v4, "messageId"

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-static {v3}, Lorg/emulationstation/frontend/netplay/StationPresence;->markRead(Ljava/lang/String;)V

    :cond_8
    add-int/lit8 v2, v2, 0x1

    goto :goto_6

    :cond_9
    if-nez v0, :cond_a

    .line 838
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    const-string v2, "Conversa privada em prepara\u00e7\u00e3o"

    const-string v3, "Combine a partida pela conversa da sala enquanto esta op\u00e7\u00e3o n\u00e3o estiver dispon\u00edvel."

    invoke-direct {v6, v0, v9, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_7

    .line 839
    :cond_a
    invoke-virtual {v1}, Lorg/json/JSONArray;->length()I

    move-result v0

    if-nez v0, :cond_d

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    new-instance v2, Ljava/lang/StringBuilder;

    const-string v3, "Combine um jogo com "

    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-object v3, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, ". As mensagens ficam dispon\u00edveis enquanto a presen\u00e7a estiver ativa."

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    const-string v3, "Comece a conversa"

    invoke-direct {v6, v0, v9, v3, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_7

    :cond_b
    move-object v9, v5

    if-eqz v0, :cond_e

    .line 840
    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatTitle:Landroid/widget/TextView;

    const-string v2, "Conversa da sala"

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatHint:Landroid/widget/TextView;

    iget-object v2, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v3, "itemId"

    invoke-virtual {v0, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const-string v1, "messages"

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v1

    iget-boolean v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    xor-int/2addr v0, v11

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->composer(Z)V

    if-eqz v1, :cond_c

    invoke-virtual {v1}, Lorg/json/JSONArray;->length()I

    move-result v0

    if-nez v0, :cond_d

    :cond_c
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    const-string v2, "Diga ol\u00e1"

    const-string v3, "Combine a partida com os participantes da sala."

    invoke-direct {v6, v0, v9, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    :cond_d
    :goto_7
    const/4 v0, 0x0

    goto :goto_8

    .line 841
    :cond_e
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatTitle:Landroid/widget/TextView;

    const-string v1, "Suas conversas"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatHint:Landroid/widget/TextView;

    const-string v1, "Pessoas online \u00b7 convites \u00b7 partidas"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/4 v0, 0x0

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->composer(Z)V

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    const-string v2, "Jogue junto"

    const-string v3, "Abra Pessoas online e toque em um nome para conversar ou convidar."

    invoke-direct {v6, v1, v9, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    const/4 v1, 0x0

    :goto_8
    move v2, v0

    :goto_9
    if-eqz v1, :cond_17

    .line 842
    invoke-virtual {v1}, Lorg/json/JSONArray;->length()I

    move-result v3

    if-ge v2, v3, :cond_17

    invoke-virtual {v1, v2}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v3

    if-nez v3, :cond_f

    move-object/from16 v17, v13

    goto/16 :goto_11

    :cond_f
    const-string v4, "fromPeerId"

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v13, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4

    iget-object v5, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->messages:Landroid/widget/LinearLayout;

    invoke-direct {v6, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->card(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v5

    invoke-virtual {v5}, Landroid/widget/LinearLayout;->getLayoutParams()Landroid/view/ViewGroup$LayoutParams;

    move-result-object v7

    check-cast v7, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v9, 0x41f00000    # 30.0f

    if-eqz v4, :cond_10

    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v16

    move/from16 v0, v16

    :cond_10
    const/high16 v11, 0x40400000    # 3.0f

    invoke-direct {v6, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v11

    if-eqz v4, :cond_11

    move-object/from16 v17, v13

    const/4 v9, 0x0

    goto :goto_a

    :cond_11
    invoke-direct {v6, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    move-object/from16 v17, v13

    :goto_a
    const/high16 v13, 0x40e00000    # 7.0f

    invoke-direct {v6, v13}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v13

    invoke-virtual {v7, v0, v11, v9, v13}, Landroid/widget/LinearLayout$LayoutParams;->setMargins(IIII)V

    invoke-virtual {v5, v7}, Landroid/widget/LinearLayout;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    if-eqz v4, :cond_12

    const v0, -0xedc3ab

    goto :goto_b

    :cond_12
    const v0, -0xe8dac5

    :goto_b
    if-eqz v4, :cond_13

    const v7, -0xdba889

    goto :goto_c

    :cond_13
    const v7, -0xd2bfa5

    :goto_c
    invoke-direct {v6, v0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v0

    invoke-virtual {v5, v0}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    if-eqz v4, :cond_14

    const-string v0, "Voc\u00ea"

    goto :goto_d

    :cond_14
    invoke-virtual {v3, v15, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    :goto_d
    if-eqz v4, :cond_15

    const v4, -0xb92401

    goto :goto_e

    :cond_15
    const v4, -0x5b371f

    :goto_e
    const/16 v7, 0xb

    invoke-direct {v6, v5, v0, v7, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    invoke-direct {v6, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const-string v0, "text"

    invoke-virtual {v3, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const/16 v4, 0xe

    const v7, -0x100a01

    invoke-direct {v6, v5, v0, v4, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    const/4 v4, 0x1

    invoke-virtual {v0, v4}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    const/high16 v4, 0x40000000    # 2.0f

    invoke-direct {v6, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    int-to-float v4, v4

    const/high16 v7, 0x3f800000    # 1.0f

    invoke-virtual {v0, v4, v7}, Landroid/widget/TextView;->setLineSpacing(FF)V

    const-string v0, "utc"

    invoke-virtual {v3, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    :try_start_0
    invoke-virtual {v3, v8}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v4

    if-eqz v4, :cond_16

    invoke-virtual {v3, v8}, Lorg/json/JSONObject;->getLong(Ljava/lang/String;)J

    move-result-wide v3

    invoke-static {v3, v4}, Ljava/time/Instant;->ofEpochMilli(J)Ljava/time/Instant;

    move-result-object v0

    invoke-static {}, Ljava/time/ZoneId;->systemDefault()Ljava/time/ZoneId;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/time/Instant;->atZone(Ljava/time/ZoneId;)Ljava/time/ZonedDateTime;

    move-result-object v0

    goto :goto_f

    :cond_16
    invoke-static {v0}, Ljava/time/OffsetDateTime;->parse(Ljava/lang/CharSequence;)Ljava/time/OffsetDateTime;

    move-result-object v0

    invoke-static {}, Ljava/time/ZoneId;->systemDefault()Ljava/time/ZoneId;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/time/OffsetDateTime;->atZoneSameInstant(Ljava/time/ZoneId;)Ljava/time/ZonedDateTime;

    move-result-object v0

    :goto_f
    const-string v3, "HH:mm"

    invoke-static {v3}, Ljava/time/format/DateTimeFormatter;->ofPattern(Ljava/lang/String;)Ljava/time/format/DateTimeFormatter;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/time/ZonedDateTime;->format(Ljava/time/format/DateTimeFormatter;)Ljava/lang/String;

    move-result-object v0
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_10

    :catch_0
    const-string v0, ""

    :goto_10
    const/16 v3, 0xa

    const v4, -0x554736

    invoke-direct {v6, v5, v0, v3, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v0

    const/4 v3, 0x5

    invoke-virtual {v0, v3}, Landroid/widget/TextView;->setGravity(I)V

    :goto_11
    add-int/lit8 v2, v2, 0x1

    move-object/from16 v13, v17

    const/4 v0, 0x0

    const/4 v11, 0x1

    goto/16 :goto_9

    .line 843
    :cond_17
    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationSocial;->last(Lorg/json/JSONArray;)Ljava/lang/String;

    move-result-object v0

    iget-object v1, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->lastMessageId:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    const/4 v2, 0x1

    xor-int/2addr v1, v2

    iput-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->lastMessageId:Ljava/lang/String;

    if-eqz v1, :cond_18

    if-eqz v12, :cond_18

    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda27;

    invoke-direct {v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda27;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    goto :goto_12

    :cond_18
    iget-object v0, v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda28;

    invoke-direct {v1, v6, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda28;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    :goto_12
    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->post(Ljava/lang/Runnable;)Z

    return-void
.end method

.method private renderHeroPlayerInfo()V
    .locals 6

    .line 1022
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactSummary:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    const-string v1, "Online: "

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlinePlayers:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_0

    const-string v0, "Jogadores a confirmar"

    goto :goto_0

    :cond_0
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlinePlayers:Ljava/lang/String;

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    goto :goto_0

    :cond_1
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactSummary:Ljava/lang/String;

    .line 1023
    :goto_0
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    invoke-virtual {v2, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerPlayers:Landroid/widget/TextView;

    invoke-virtual {v2, v0}, Landroid/widget/TextView;->setContentDescription(Ljava/lang/CharSequence;)V

    .line 1024
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactDetail:Ljava/lang/String;

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playGuidance(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlineDetail:Ljava/lang/String;

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-eqz v2, :cond_2

    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->pending()Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v2

    iget-object v2, v2, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->detail:Ljava/lang/String;

    goto :goto_1

    :cond_2
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlineDetail:Ljava/lang/String;

    invoke-static {v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->onlineNotice(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 1025
    :goto_1
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    if-eqz v3, :cond_4

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v5

    if-eqz v5, :cond_3

    const-string v0, ""

    goto :goto_2

    :cond_3
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v5, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v0, "\n\n"

    invoke-virtual {v5, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :goto_2
    invoke-virtual {v4, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v3, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_4
    return-void
.end method

.method private renderParticipants(Landroid/widget/LinearLayout;Lorg/json/JSONObject;)V
    .locals 13

    .line 768
    invoke-virtual {p1}, Landroid/widget/LinearLayout;->removeAllViews()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    const/16 v1, 0x30

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setGravity(I)V

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v3, -0x1

    const/4 v4, -0x2

    invoke-direct {v2, v3, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 769
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-virtual {v2, p2}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;->rows(Lorg/json/JSONObject;)Ljava/util/List;

    move-result-object p2

    const/4 v2, 0x0

    move v5, v2

    .line 770
    :goto_0
    invoke-interface {p2}, Ljava/util/List;->size()I

    move-result v6

    if-ge v5, v6, :cond_b

    if-lez v5, :cond_0

    .line 771
    rem-int/lit8 v6, v5, 0x2

    if-nez v6, :cond_0

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v0

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setGravity(I)V

    new-instance v6, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v6, v3, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 772
    :cond_0
    invoke-interface {p2, v5}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v6

    check-cast v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v7

    const/high16 v8, 0x40000000    # 2.0f

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-virtual {v7, v2, v9, v2, v10}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 773
    new-instance v9, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v10, 0x3f800000    # 1.0f

    invoke-direct {v9, v2, v4, v10}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    rem-int/lit8 v10, v5, 0x2

    if-nez v10, :cond_1

    move v10, v2

    goto :goto_1

    :cond_1
    const/high16 v10, 0x41400000    # 12.0f

    invoke-direct {p0, v10}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    :goto_1
    iput v10, v9, Landroid/widget/LinearLayout$LayoutParams;->leftMargin:I

    invoke-virtual {v0, v7, v9}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 774
    new-instance v9, Ljava/lang/StringBuilder;

    const-string v10, "P"

    invoke-direct {v9, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget v10, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->position:I

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v10, " \u00b7 "

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-boolean v10, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->occupied:Z

    if-eqz v10, :cond_4

    iget-boolean v10, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->host:Z

    if-eqz v10, :cond_2

    const-string v10, "ANFITRI\u00c3O"

    goto :goto_2

    :cond_2
    const-string v10, "CONVIDADO"

    :goto_2
    iget-boolean v11, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->self:Z

    if-eqz v11, :cond_3

    const-string v11, " \u00b7 VOC\u00ca"

    goto :goto_3

    :cond_3
    const-string v11, ""

    :goto_3
    invoke-virtual {v10, v11}, Ljava/lang/String;->concat(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    goto :goto_4

    :cond_4
    const-string v10, "VAGA DISPON\u00cdVEL"

    :goto_4
    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v9}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    const/16 v10, 0x9

    const v11, -0x554736

    invoke-direct {p0, v7, v9, v10, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v9

    const v10, 0x3d23d70a    # 0.04f

    invoke-virtual {v9, v10}, Landroid/widget/TextView;->setLetterSpacing(F)V

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v10

    invoke-virtual {v9, v2, v2, v2, v10}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 775
    iget-object v9, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->name:Ljava/lang/String;

    const/16 v10, 0xe

    const v11, -0x100a01

    invoke-direct {p0, v7, v9, v10, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v9

    invoke-direct {p0, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/4 v10, 0x2

    invoke-virtual {v9, v10}, Landroid/widget/TextView;->setMaxLines(I)V

    sget-object v10, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v9, v10}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    invoke-direct {p0, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v8

    invoke-virtual {v9, v2, v2, v2, v8}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 776
    iget-boolean v8, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->occupied:Z

    if-eqz v8, :cond_5

    new-instance v8, Ljava/lang/StringBuilder;

    const-string v10, "Participante: "

    invoke-direct {v8, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-object v10, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->name:Ljava/lang/String;

    invoke-virtual {v8, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v8}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v8

    goto :goto_5

    :cond_5
    const-string v8, "Aguardando outro jogador"

    :goto_5
    invoke-virtual {v9, v8}, Landroid/widget/TextView;->setContentDescription(Ljava/lang/CharSequence;)V

    .line 777
    iget-boolean v8, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->occupied:Z

    if-nez v8, :cond_6

    const-string v8, "Aguardando convite"

    goto :goto_6

    :cond_6
    iget-boolean v8, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->ready:Z

    if-eqz v8, :cond_7

    const-string v8, "Pronto"

    goto :goto_6

    :cond_7
    const-string v8, "Ainda n\u00e3o confirmou"

    .line 778
    :goto_6
    iget-boolean v9, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->ready:Z

    const v10, -0x872151

    const v11, -0x1a3b89

    if-eqz v9, :cond_8

    move v9, v10

    goto :goto_7

    :cond_8
    move v9, v11

    :goto_7
    const/16 v12, 0xa

    invoke-direct {p0, v7, v8, v12, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v7

    invoke-virtual {v7, v2, v2, v2, v2}, Landroid/widget/TextView;->setPadding(IIII)V

    const/4 v8, 0x1

    invoke-virtual {v7, v8}, Landroid/widget/TextView;->setSingleLine(Z)V

    sget-object v9, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v7, v9}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 779
    new-instance v9, Lorg/emulationstation/frontend/netplay/StationSocialIcon;

    iget-boolean v12, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->ready:Z

    if-eqz v12, :cond_9

    const/4 v8, 0x7

    :cond_9
    const/high16 v12, 0x41500000    # 13.0f

    invoke-direct {p0, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v12

    iget-boolean v6, v6, Lorg/emulationstation/frontend/netplay/StationRoomRoster$Row;->ready:Z

    if-eqz v6, :cond_a

    goto :goto_8

    :cond_a
    move v10, v11

    :goto_8
    invoke-direct {v9, v8, v12, v10}, Lorg/emulationstation/frontend/netplay/StationSocialIcon;-><init>(III)V

    const/4 v6, 0x0

    invoke-virtual {v7, v9, v6, v6, v6}, Landroid/widget/TextView;->setCompoundDrawablesWithIntrinsicBounds(Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;)V

    const/high16 v6, 0x40800000    # 4.0f

    invoke-direct {p0, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-virtual {v7, v6}, Landroid/widget/TextView;->setCompoundDrawablePadding(I)V

    add-int/lit8 v5, v5, 0x1

    goto/16 :goto_0

    :cond_b
    return-void
.end method

.method private renderPlayers(Lorg/json/JSONObject;)V
    .locals 17

    move-object/from16 v0, p0

    move-object/from16 v1, p1

    .line 848
    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    invoke-virtual {v2}, Landroid/widget/LinearLayout;->removeAllViews()V

    const-string v2, "peers"

    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v2

    const-string v3, "selfId"

    invoke-virtual {v1, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    .line 849
    iget-object v4, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSearch:Landroid/widget/EditText;

    invoke-virtual {v4}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v4

    sget-object v5, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v4, v5}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v4

    .line 850
    iget-object v5, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerTitle:Landroid/widget/TextView;

    new-instance v6, Ljava/lang/StringBuilder;

    const-string v7, "ONLINE  \u00b7  "

    invoke-direct {v6, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    const-string v7, "totalPeers"

    invoke-virtual {v1, v7}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v7

    invoke-virtual {v6, v7}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v6}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/4 v6, 0x0

    if-eqz v2, :cond_9

    move v7, v6

    move v8, v7

    .line 851
    :goto_0
    invoke-virtual {v2}, Lorg/json/JSONArray;->length()I

    move-result v9

    if-ge v7, v9, :cond_a

    .line 852
    invoke-virtual {v2, v7}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v9

    if-nez v9, :cond_0

    goto :goto_1

    :cond_0
    const-string v10, "peerId"

    invoke-virtual {v9, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    const-string v11, "nickname"

    const-string v12, "Jogador"

    invoke-virtual {v9, v11, v12}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v11

    .line 853
    sget-object v12, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v11, v12}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v12

    invoke-virtual {v12, v4}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v12

    if-nez v12, :cond_1

    :goto_1
    move-object/from16 v16, v2

    goto/16 :goto_6

    :cond_1
    add-int/lit8 v8, v8, 0x1

    .line 854
    invoke-virtual {v3, v10}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v12

    const-string v13, "online"

    const-string v14, "status"

    invoke-virtual {v9, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v15

    invoke-virtual {v13, v15}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v13

    const-string v15, "in-room"

    invoke-virtual {v9, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v9

    invoke-virtual {v15, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v9

    .line 855
    invoke-direct/range {p0 .. p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->row()Landroid/widget/LinearLayout;

    move-result-object v14

    const/high16 v15, 0x40800000    # 4.0f

    invoke-direct {v0, v15}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v15

    const/high16 v5, 0x40a00000    # 5.0f

    invoke-direct {v0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    invoke-virtual {v14, v15, v6, v5, v6}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 856
    invoke-direct {v0, v6, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v5

    .line 857
    new-instance v15, Landroid/graphics/drawable/RippleDrawable;

    const v16, 0x327ad9f1

    invoke-static/range {v16 .. v16}, Landroid/content/res/ColorStateList;->valueOf(I)Landroid/content/res/ColorStateList;

    move-result-object v6

    move-object/from16 v16, v2

    const/4 v2, 0x0

    invoke-direct {v15, v6, v5, v2}, Landroid/graphics/drawable/RippleDrawable;-><init>(Landroid/content/res/ColorStateList;Landroid/graphics/drawable/Drawable;Landroid/graphics/drawable/Drawable;)V

    invoke-virtual {v14, v15}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    const/4 v2, 0x1

    .line 858
    invoke-virtual {v14, v2}, Landroid/widget/LinearLayout;->setFocusable(Z)V

    invoke-virtual {v14, v2}, Landroid/widget/LinearLayout;->setClickable(Z)V

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v5, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    if-eqz v12, :cond_2

    const-string v6, ", voc\u00ea"

    goto :goto_2

    :cond_2
    if-eqz v13, :cond_3

    const-string v6, ", dispon\u00edvel"

    goto :goto_2

    :cond_3
    if-eqz v9, :cond_4

    const-string v6, ", em uma sala"

    goto :goto_2

    :cond_4
    const-string v6, ", status n\u00e3o informado"

    :goto_2
    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v6, ", abrir perfil"

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v14, v5}, Landroid/widget/LinearLayout;->setContentDescription(Ljava/lang/CharSequence;)V

    if-eqz v13, :cond_5

    const v5, -0xb92401

    goto :goto_3

    :cond_5
    if-eqz v9, :cond_6

    const v5, -0x284789

    goto :goto_3

    :cond_6
    const v5, -0x554736

    :goto_3
    const-string v6, "\u25cf"

    const/16 v9, 0x9

    .line 859
    invoke-direct {v0, v6, v9, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v5

    const/16 v6, 0x11

    invoke-virtual {v5, v6}, Landroid/widget/TextView;->setGravity(I)V

    new-instance v6, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v9, 0x41a00000    # 20.0f

    invoke-direct {v0, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    const/4 v13, -0x1

    invoke-direct {v6, v9, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v14, v5, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    const/16 v5, 0xe

    const v6, -0x100a01

    .line 860
    invoke-direct {v0, v11, v5, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v5

    invoke-virtual {v5, v2}, Landroid/widget/TextView;->setSingleLine(Z)V

    sget-object v2, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {v5, v2}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v6, -0x2

    const/high16 v9, 0x3f800000    # 1.0f

    const/4 v15, 0x0

    invoke-direct {v2, v15, v6, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v14, v5, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    if-eqz v12, :cond_7

    const-string v2, "voc\u00ea"

    goto :goto_4

    :cond_7
    const-string v2, "\u203a"

    :goto_4
    if-eqz v12, :cond_8

    const/16 v5, 0xa

    goto :goto_5

    :cond_8
    const/16 v5, 0x16

    :goto_5
    const v6, -0x554736

    .line 861
    invoke-direct {v0, v2, v5, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    const/16 v5, 0x15

    invoke-virtual {v2, v5}, Landroid/widget/TextView;->setGravity(I)V

    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v6, 0x42180000    # 38.0f

    invoke-direct {v0, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-direct {v5, v6, v13}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v14, v2, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 862
    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v6, 0x42400000    # 48.0f

    invoke-direct {v0, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-direct {v5, v13, v6}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v14, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda81;

    invoke-direct {v2, v0, v12, v10, v11}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda81;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ZLjava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v14, v2}, Landroid/widget/LinearLayout;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 863
    new-instance v2, Landroid/view/View;

    invoke-direct {v2, v0}, Landroid/view/View;-><init>(Landroid/content/Context;)V

    const v5, -0xdbcab3

    invoke-virtual {v2, v5}, Landroid/view/View;->setBackgroundColor(I)V

    iget-object v5, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    new-instance v6, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v0, v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v9

    invoke-direct {v6, v13, v9}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v5, v2, v6}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    :goto_6
    add-int/lit8 v7, v7, 0x1

    move-object/from16 v2, v16

    const/4 v6, 0x0

    goto/16 :goto_0

    :cond_9
    const/4 v8, 0x0

    :cond_a
    if-nez v8, :cond_c

    .line 865
    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    invoke-virtual {v4}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-eqz v3, :cond_b

    const-string v3, "Nenhum jogador nesta p\u00e1gina."

    goto :goto_7

    :cond_b
    const-string v3, "Nenhum nome encontrado nesta p\u00e1gina."

    :goto_7
    const/16 v4, 0xc

    const v5, -0x554736

    invoke-direct {v0, v2, v3, v4, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    const/high16 v3, 0x41000000    # 8.0f

    invoke-direct {v0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    const/high16 v5, 0x41900000    # 18.0f

    invoke-direct {v0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-direct {v0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {v0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    invoke-virtual {v2, v4, v6, v3, v5}, Landroid/widget/TextView;->setPadding(IIII)V

    :cond_c
    const-string v2, "page"

    .line 866
    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v2

    const-string v3, "peerPage"

    invoke-virtual {v1, v3, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v2

    if-lez v2, :cond_d

    iget-object v2, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda82;

    invoke-direct {v3, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda82;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v4, "\u2190 P\u00e1gina anterior"

    const/4 v5, 0x0

    invoke-direct {v0, v2, v4, v3, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    goto :goto_8

    :cond_d
    const/4 v5, 0x0

    :goto_8
    const-string v2, "nextPeerPage"

    .line 867
    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z

    move-result v1

    if-nez v1, :cond_e

    iget-object v1, v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda83;

    invoke-direct {v2, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda83;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const-string v3, "Pr\u00f3xima p\u00e1gina \u2192"

    invoke-direct {v0, v1, v3, v2, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    :cond_e
    return-void
.end method

.method private renderRoomSetup()V
    .locals 8

    .line 668
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-nez v0, :cond_0

    return-void

    :cond_0
    const/4 v0, 0x0

    move v1, v0

    .line 669
    :goto_0
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeLabels:Ljava/util/List;

    invoke-interface {v2}, Ljava/util/List;->size()I

    move-result v2

    const v3, -0xb92401

    const v4, -0x554736

    const/4 v5, 0x1

    if-ge v1, v2, :cond_3

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeLabels:Ljava/util/List;

    invoke-interface {v2, v1}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroid/widget/TextView;

    iget-object v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v6, v1}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v6

    iget-object v7, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-ne v6, v7, :cond_1

    goto :goto_1

    :cond_1
    move v5, v0

    :goto_1
    if-eqz v5, :cond_2

    goto :goto_2

    :cond_2
    move v3, v4

    :goto_2
    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextColor(I)V

    invoke-virtual {v2, v5}, Landroid/widget/TextView;->setSelected(Z)V

    invoke-direct {p0, v2, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyChoiceFace(Landroid/widget/TextView;Z)V

    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_3
    move v1, v0

    .line 670
    :goto_3
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCountLabels:Ljava/util/List;

    invoke-interface {v2}, Ljava/util/List;->size()I

    move-result v2

    if-ge v1, v2, :cond_6

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCountLabels:Ljava/util/List;

    invoke-interface {v2, v1}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroid/widget/TextView;

    iget-object v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    iget-object v6, v6, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    aget v6, v6, v1

    iget v7, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    if-ne v6, v7, :cond_4

    move v6, v5

    goto :goto_4

    :cond_4
    move v6, v0

    :goto_4
    if-eqz v6, :cond_5

    move v7, v3

    goto :goto_5

    :cond_5
    move v7, v4

    :goto_5
    invoke-virtual {v2, v7}, Landroid/widget/TextView;->setTextColor(I)V

    invoke-virtual {v2, v6}, Landroid/widget/TextView;->setSelected(Z)V

    invoke-direct {p0, v2, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyChoiceFace(Landroid/widget/TextView;Z)V

    add-int/lit8 v1, v1, 0x1

    goto :goto_3

    .line 671
    :cond_6
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupDescription:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, " jogadores \u00b7 "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-static {v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeName(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "\nToque para ver como jogar."

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupConfirm:Landroid/widget/Button;

    const-string v1, "Criar sala"

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupConfirm:Landroid/widget/Button;

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "Criar sala para "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, " jogadores"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setContentDescription(Ljava/lang/CharSequence;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateRoomSetupEnabled()V

    return-void
.end method

.method private room()Lorg/json/JSONObject;
    .locals 2

    .line 550
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_0

    const/4 v0, 0x0

    goto :goto_0

    :cond_0
    const-string v1, "room"

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    :goto_0
    return-object v0
.end method

.method private roomAction(Landroid/widget/LinearLayout;Ljava/lang/String;IILjava/lang/Runnable;)Landroid/widget/Button;
    .locals 2

    .line 399
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationActionButton;

    invoke-direct {v0, p0, p2, p4, p3}, Lorg/emulationstation/frontend/netplay/StationActionButton;-><init>(Landroid/content/Context;Ljava/lang/String;II)V

    invoke-direct {p0, v0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleAction(Landroid/widget/Button;I)V

    .line 400
    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 p3, 0x42400000    # 48.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    const/high16 p4, 0x3f800000    # 1.0f

    const/4 v1, 0x0

    invoke-direct {p2, v1, p3, p4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {p1}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result p3

    if-nez p3, :cond_0

    move p3, v1

    goto :goto_0

    :cond_0
    const/high16 p3, 0x41000000    # 8.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    :goto_0
    iput p3, p2, Landroid/widget/LinearLayout$LayoutParams;->leftMargin:I

    .line 401
    invoke-virtual {p1, v0, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda91;

    invoke-direct {p1, p5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda91;-><init>(Ljava/lang/Runnable;)V

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez p1, :cond_1

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez p1, :cond_1

    const/4 v1, 0x1

    :cond_1
    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setEnabled(Z)V

    return-object v0
.end method

.method private static roomConfirmationKey(Lorg/json/JSONObject;)Ljava/lang/String;
    .locals 4

    if-nez p0, :cond_0

    const/4 v0, 0x0

    goto :goto_0

    :cond_0
    const-string v0, "room"

    .line 1059
    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    :goto_0
    if-nez v0, :cond_1

    const-string p0, ""

    goto/16 :goto_1

    :cond_1
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "instance"

    invoke-virtual {p0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p0, "/"

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "roomId"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "itemId"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "generation"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v2

    invoke-virtual {v1, v2, v3}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "profileId"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "profileSha256"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "capacity"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "roster"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v2

    invoke-static {v2}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "hostId"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "recoveryProtocol"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "members"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v2

    invoke-static {v2}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p0, "ready"

    invoke-virtual {v0, p0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object p0

    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    :goto_1
    return-object p0
.end method

.method private static roomControlLayout(I[III)[I
    .locals 8

    const/4 v0, 0x0

    .line 359
    invoke-static {v0, p0}, Ljava/lang/Math;->max(II)I

    move-result p0

    array-length v1, p1

    mul-int/lit8 v1, v1, 0x4

    new-array v1, v1, [I

    move v2, v0

    move v3, v2

    move v4, v3

    .line 360
    :goto_0
    array-length v5, p1

    if-ge v2, v5, :cond_3

    .line 361
    aget v5, p1, v2

    if-gtz v5, :cond_0

    goto :goto_2

    .line 362
    :cond_0
    invoke-static {p2, v5}, Ljava/lang/Math;->max(II)I

    move-result v5

    invoke-static {p0, v5}, Ljava/lang/Math;->min(II)I

    move-result v5

    if-lez v3, :cond_1

    add-int v6, v3, p3

    add-int/2addr v6, v5

    if-le v6, p0, :cond_1

    add-int v3, p2, p3

    add-int/2addr v4, v3

    move v3, v0

    goto :goto_1

    :cond_1
    if-lez v3, :cond_2

    add-int/2addr v3, p3

    :cond_2
    :goto_1
    mul-int/lit8 v6, v2, 0x4

    .line 365
    aput v3, v1, v6

    add-int/lit8 v7, v6, 0x1

    aput v4, v1, v7

    add-int/lit8 v7, v6, 0x2

    aput v5, v1, v7

    add-int/lit8 v6, v6, 0x3

    aput p2, v1, v6

    add-int/2addr v3, v5

    :goto_2
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    :cond_3
    return-object v1
.end method

.method private roomControls(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;
    .locals 4

    .line 397
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    new-instance v1, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v2, -0x1

    const/4 v3, -0x2

    invoke-direct {v1, v2, v3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-object v0
.end method

.method private roomCoverCard(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)Landroid/widget/LinearLayout;
    .locals 9

    .line 306
    invoke-static {p1, p2, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRowKey(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const/4 p2, 0x1

    move-object v0, p1

    move v1, p2

    .line 307
    :goto_0
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    invoke-interface {v2, v0}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_0

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "#"

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    add-int/2addr v1, p2

    goto :goto_0

    .line 308
    :cond_0
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->usedRoomRows:Ljava/util/Set;

    invoke-interface {p1, v0}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    invoke-interface {p1, v0}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;

    if-nez p1, :cond_2

    .line 310
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-direct {p1, p0, p2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;-><init>(Landroid/content/Context;Z)V

    const/4 v1, -0x2

    const/high16 v2, 0x41000000    # 8.0f

    const/4 v3, -0x1

    if-eqz p4, :cond_1

    .line 312
    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setViewportBounded(Z)V

    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomViewportHeight()I

    move-result v6

    invoke-direct {v5, v3, v6}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v4, p1, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 315
    new-instance v4, Landroid/widget/ScrollView;

    invoke-direct {v4, p0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    invoke-virtual {v4, p2}, Landroid/widget/ScrollView;->setFillViewport(Z)V

    const/4 v5, 0x0

    invoke-virtual {v4, v5}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    iget-object v6, p1, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->actions:Landroid/widget/LinearLayout;

    new-instance v7, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v8, 0x3f800000    # 1.0f

    invoke-direct {v7, v3, v5, v8}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {v6, v4, v7}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 316
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v6

    const/high16 v7, 0x40c00000    # 6.0f

    invoke-direct {p0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v7

    invoke-virtual {v6, v5, v5, v7, v5}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    new-instance v7, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v7, v3, v1}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v4, v6, v7}, Landroid/widget/ScrollView;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 317
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->vertical()Landroid/widget/LinearLayout;

    move-result-object v4

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {v4, v5, v2, v5, v5}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    iget-object v2, p1, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->actions:Landroid/widget/LinearLayout;

    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v5, v3, v1}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v4, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 318
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda48;

    invoke-direct {v1, p0, p1, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda48;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationCreateGameCard;Landroid/widget/LinearLayout;)V

    invoke-virtual {v4, v1}, Landroid/widget/LinearLayout;->addOnLayoutChangeListener(Landroid/view/View$OnLayoutChangeListener;)V

    move-object v1, v4

    move-object v4, p1

    goto :goto_1

    .line 320
    :cond_1
    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->card(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v4

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    const/high16 v6, 0x40000000    # 2.0f

    invoke-direct {p0, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v7

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-direct {p0, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-virtual {v4, v5, v7, v2, v6}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    new-instance v2, Landroid/widget/LinearLayout$LayoutParams;

    invoke-direct {v2, v3, v1}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v4, p1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    iget-object v6, p1, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->actions:Landroid/widget/LinearLayout;

    const/4 v1, 0x0

    .line 322
    :goto_1
    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;

    invoke-direct {v2, v4, p1, v6, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;-><init>(Landroid/view/View;Lorg/emulationstation/frontend/netplay/StationCreateGameCard;Landroid/widget/LinearLayout;Landroid/widget/LinearLayout;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    invoke-interface {p1, v0, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    move-object p1, v2

    .line 324
    :cond_2
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->desiredRoomRows:Ljava/util/List;

    iget-object v2, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->root:Landroid/view/View;

    invoke-interface {v1, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->content:Landroid/widget/LinearLayout;

    invoke-virtual {v1}, Landroid/widget/LinearLayout;->removeAllViews()V

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->footer:Landroid/widget/LinearLayout;

    if-eqz v1, :cond_3

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->footer:Landroid/widget/LinearLayout;

    invoke-virtual {v1}, Landroid/widget/LinearLayout;->removeAllViews()V

    :cond_3
    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->display:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v2, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setGameName(Ljava/lang/String;)V

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->display:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->coverPlatform(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setPlatform(Ljava/lang/String;)V

    if-eqz p4, :cond_4

    .line 326
    iget-object p2, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->display:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    iput-object p3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCoverItem:Ljava/lang/String;

    iget-object p2, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->footer:Landroid/widget/LinearLayout;

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    .line 327
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateOwnRoomHeight()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bindHeroCover()V

    goto :goto_2

    .line 328
    :cond_4
    iget-boolean p4, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->loading:Z

    if-nez p4, :cond_5

    iget-boolean p4, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->loaded:Z

    if-nez p4, :cond_5

    .line 331
    iput-boolean p2, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->loading:Z

    .line 332
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    new-instance p4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda49;

    invoke-direct {p4, p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda49;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;)V

    const/16 v0, 0x600

    invoke-virtual {p2, p3, v0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->load(Ljava/lang/String;ILorg/emulationstation/frontend/netplay/StationRoomArtwork$Callback;)V

    .line 334
    :cond_5
    :goto_2
    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->content:Landroid/widget/LinearLayout;

    return-object p1
.end method

.method private roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;
    .locals 5

    .line 570
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, ""

    if-nez v0, :cond_0

    move-object v0, v1

    goto :goto_0

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    const-string v2, "selfId"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    :goto_0
    invoke-static {p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomInfo(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;

    move-result-object v0

    .line 571
    new-instance v2, Ljava/lang/StringBuilder;

    iget-object v3, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->detail:Ljava/lang/String;

    invoke-static {v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playGuidance(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-boolean v3, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->confirmed:Z

    if-nez v3, :cond_1

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    return-object p1

    :cond_1
    const-string v3, "\n\n"

    .line 572
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;->positions:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_1
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_3

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Position;

    iget-object v4, v3, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Position;->label:Ljava/lang/String;

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v4, " \u00b7 "

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v4, v3, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Position;->name:Ljava/lang/String;

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-boolean v3, v3, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Position;->self:Z

    if-eqz v3, :cond_2

    const-string v3, " (voc\u00ea)"

    goto :goto_2

    :cond_2
    move-object v3, v1

    :goto_2
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, "\n"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    goto :goto_1

    :cond_3
    const-string v0, "instructions"

    .line 573
    invoke-static {p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayHelp(Lorg/json/JSONObject;Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    array-length v0, v0

    if-nez v0, :cond_4

    const-string v0, "mode"

    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v1, "battle-single"

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_4

    const-string v0, "controllerProfile"

    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const-string v0, "snes-multitap-port2-v1"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_4

    const-string p1, "\nNo jogo, escolha BATTLE GAME \u2192 Single Match e marque MAN nos controles dos participantes. As vagas desta sala s\u00e3o para Batalha; confira o limite da campanha na descri\u00e7\u00e3o do modo."

    invoke-virtual {v2, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    :cond_4
    const-string p1, "\nTodos precisam da mesma edi\u00e7\u00e3o do jogo. Cada participante controla apenas sua posi\u00e7\u00e3o e pode usar sua pr\u00f3pria rede."

    .line 574
    invoke-virtual {v2, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    return-object p1
.end method

.method private static roomGameInfo(Lorg/json/JSONObject;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;
    .locals 5

    if-eqz p0, :cond_3

    const-string v0, "recoveryProtocol"

    .line 556
    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v1, "station-stream.v3"

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    goto :goto_2

    :cond_0
    const-string v0, "allowedPlayerCounts"

    .line 557
    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v0

    const/4 v1, 0x0

    if-nez v0, :cond_1

    move v2, v1

    goto :goto_0

    :cond_1
    invoke-virtual {v0}, Lorg/json/JSONArray;->length()I

    move-result v2

    :goto_0
    new-array v3, v2, [I

    :goto_1
    if-ge v1, v2, :cond_2

    invoke-virtual {v0, v1}, Lorg/json/JSONArray;->optInt(I)I

    move-result v4

    aput v4, v3, v1

    add-int/lit8 v1, v1, 0x1

    goto :goto_1

    :cond_2
    const-string v0, "maximumPlayers"

    .line 558
    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v0

    const-string v1, "mode"

    invoke-virtual {p0, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const-string v2, "controllerProfile"

    invoke-virtual {p0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    const/4 v4, 0x1

    invoke-static {v4, v0, v3, v1, v2}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->fromVerifiedProfile(ZI[ILjava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v0

    const-string v1, "modeTitle"

    const-string v2, ""

    invoke-virtual {p0, v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const-string v2, "instructions"

    invoke-static {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayHelp(Lorg/json/JSONObject;Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v2

    const-string v3, "sources"

    invoke-static {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayHelp(Lorg/json/JSONObject;Ljava/lang/String;)[Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, v1, v2, p0}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->withHelp(Ljava/lang/String;[Ljava/lang/String;[Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object p0

    return-object p0

    .line 556
    :cond_3
    :goto_2
    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->pending()Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object p0

    return-object p0
.end method

.method private static roomInfo(Lorg/json/JSONObject;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;
    .locals 14

    .line 565
    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomGameInfo(Lorg/json/JSONObject;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v0

    if-nez p0, :cond_0

    const/4 v1, 0x0

    goto :goto_0

    :cond_0
    const-string v1, "roster"

    invoke-virtual {p0, v1}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v1

    :goto_0
    const/4 v2, 0x0

    if-nez v1, :cond_1

    move v3, v2

    goto :goto_1

    :cond_1
    invoke-virtual {v1}, Lorg/json/JSONArray;->length()I

    move-result v3

    :goto_1
    new-array v4, v3, [Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Participant;

    move v5, v2

    :goto_2
    if-ge v5, v3, :cond_3

    .line 566
    invoke-virtual {v1, v5}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v6

    if-eqz v6, :cond_2

    new-instance v13, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Participant;

    const-string v7, "slot"

    invoke-virtual {v6, v7}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result v8

    const-string v7, "peerId"

    invoke-virtual {v6, v7}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v9

    const-string v10, "nickname"

    invoke-virtual {v6, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    const-string v11, "ready"

    invoke-virtual {v6, v11}, Lorg/json/JSONObject;->optBoolean(Ljava/lang/String;)Z

    move-result v11

    invoke-virtual {v6, v7}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {p1, v6}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v12

    move-object v7, v13

    invoke-direct/range {v7 .. v12}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Participant;-><init>(ILjava/lang/String;Ljava/lang/String;ZZ)V

    aput-object v13, v4, v5

    :cond_2
    add-int/lit8 v5, v5, 0x1

    goto :goto_2

    :cond_3
    if-nez p0, :cond_4

    move p1, v2

    goto :goto_3

    :cond_4
    const-string p1, "capacity"

    .line 567
    invoke-virtual {p0, p1}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;)I

    move-result p1

    :goto_3
    if-eqz p0, :cond_5

    const-string v1, "state"

    invoke-virtual {p0, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    const-string v1, "waiting"

    invoke-virtual {v1, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_5

    const/4 v2, 0x1

    :cond_5
    invoke-virtual {v0, p1, v2, v4}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->forRoom(IZ[Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$Participant;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo$RoomInfo;

    move-result-object p0

    return-object p0
.end method

.method private roomLayout(Z)V
    .locals 6

    const/4 v0, 0x0

    if-eqz p1, :cond_0

    .line 992
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    invoke-virtual {v1, v0}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    invoke-virtual {v1, v0, v0, v0, v0}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    goto :goto_0

    .line 993
    :cond_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    invoke-virtual {v1, v0}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    const/high16 v2, 0x40c00000    # 6.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v3

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {v1, v3, v0, v2, v0}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 994
    :goto_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navRooms:Landroid/widget/Button;

    if-eqz p1, :cond_1

    const-string p1, "Sua sala"

    goto :goto_1

    :cond_1
    const-string p1, "Salas"

    :goto_1
    invoke-virtual {v1, p1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 995
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->leftPanel:Landroid/widget/LinearLayout;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/16 v2, 0x8

    const/4 v3, 0x1

    if-ne v1, v3, :cond_2

    move v1, v0

    goto :goto_2

    :cond_2
    move v1, v2

    :goto_2
    invoke-virtual {p1, v1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    if-nez v1, :cond_3

    move v1, v0

    goto :goto_3

    :cond_3
    move v1, v2

    :goto_3
    invoke-virtual {p1, v1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createPanel:Landroid/widget/LinearLayout;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v4, 0x2

    if-ne v1, v4, :cond_4

    move v1, v0

    goto :goto_4

    :cond_4
    move v1, v2

    :goto_4
    invoke-virtual {p1, v1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    .line 996
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rightPanel:Landroid/widget/LinearLayout;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v5, 0x3

    if-ne v1, v5, :cond_5

    move v2, v0

    :cond_5
    invoke-virtual {p1, v2}, Landroid/widget/LinearLayout;->setVisibility(I)V

    .line 997
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navRooms:Landroid/widget/Button;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    if-nez v1, :cond_6

    move v1, v3

    goto :goto_5

    :cond_6
    move v1, v0

    :goto_5
    invoke-direct {p0, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleNavigation(Landroid/widget/Button;Z)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navPeople:Landroid/widget/Button;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    if-ne v1, v3, :cond_7

    move v1, v3

    goto :goto_6

    :cond_7
    move v1, v0

    :goto_6
    invoke-direct {p0, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleNavigation(Landroid/widget/Button;Z)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navCreate:Landroid/widget/Button;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    if-ne v1, v4, :cond_8

    move v1, v3

    goto :goto_7

    :cond_8
    move v1, v0

    :goto_7
    invoke-direct {p0, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleNavigation(Landroid/widget/Button;Z)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navChat:Landroid/widget/Button;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    if-ne v1, v5, :cond_9

    move v0, v3

    :cond_9
    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->styleNavigation(Landroid/widget/Button;Z)V

    .line 998
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    if-eqz p1, :cond_c

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    if-nez v0, :cond_a

    const-string v0, "Jogo n\u00e3o selecionado"

    goto :goto_8

    :cond_a
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-nez v0, :cond_b

    const-string v0, "Carregando jogo\u2026"

    goto :goto_8

    :cond_b
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    :goto_8
    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    invoke-virtual {v0}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-interface {v0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setGameName(Ljava/lang/String;)V

    :cond_c
    return-void
.end method

.method private static roomRowKey(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    .line 303
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p0, ":"

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method private roomSetupContext()Ljava/lang/String;
    .locals 4

    .line 607
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_1

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v1

    if-nez v1, :cond_1

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    if-nez v1, :cond_0

    goto :goto_0

    .line 609
    :cond_0
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, "/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, "instance"

    invoke-virtual {v0, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "engines"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v0

    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    :cond_1
    :goto_0
    const-string v0, ""

    return-object v0
.end method

.method private static roomSetupDescription(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;I)Ljava/lang/String;
    .locals 8

    if-eqz p0, :cond_7

    .line 655
    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v0

    if-nez v0, :cond_0

    goto/16 :goto_4

    .line 656
    :cond_0
    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileInfo(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v0

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "Sala para "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    .line 657
    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v2, " jogadores: voc\u00ea (P1) e "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    add-int/lit8 v2, p1, -0x1

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const/4 v2, 0x2

    if-ne p1, v2, :cond_1

    const-string v2, " convidado."

    goto :goto_0

    :cond_1
    const-string v2, " convidados."

    :goto_0
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "\n"

    .line 658
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeName(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, ". "

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 659
    iget-boolean v4, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->modeConfirmed:Z

    if-eqz v4, :cond_2

    iget-object v4, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->participationLabel:Ljava/lang/String;

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    goto :goto_1

    :cond_2
    const-string v3, "A forma de participa\u00e7\u00e3o segue o modo selecionado no jogo. "

    .line 660
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 661
    :goto_1
    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->controlsLabel:Ljava/lang/String;

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v0, "."

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 662
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->instructions:[Ljava/lang/String;

    array-length v3, v0

    const/4 v4, 0x0

    move v5, v4

    :goto_2
    if-ge v4, v3, :cond_4

    aget-object v6, v0, v4

    invoke-static {v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playGuidance(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/String;->isEmpty()Z

    move-result v7

    if-nez v7, :cond_3

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/4 v5, 0x1

    :cond_3
    add-int/lit8 v4, v4, 0x1

    goto :goto_2

    :cond_4
    if-nez v5, :cond_5

    const-string v0, "battle-single"

    .line 663
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->mode:Ljava/lang/String;

    invoke-virtual {v0, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_5

    const-string v0, "snes-multitap-port2-v1"

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->controllerProfile:Ljava/lang/String;

    invoke-virtual {v0, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_5

    const-string p0, "\nNo jogo, escolha Battle Game \u2192 Single Match e marque MAN nos "

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string p0, " controles dos participantes."

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    goto :goto_3

    :cond_5
    if-nez v5, :cond_6

    const-string v0, "battle-team"

    .line 664
    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->mode:Ljava/lang/String;

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_6

    const-string p0, "\nConfigure os "

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string p0, " participantes e as equipes no menu de batalha do jogo."

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    :cond_6
    :goto_3
    const-string p0, "\nTodos precisam da mesma edi\u00e7\u00e3o instalada. Cada pessoa controla a pr\u00f3pria posi\u00e7\u00e3o."

    .line 665
    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0

    :cond_7
    :goto_4
    const-string p0, "Escolha uma quantidade permitida para este modo."

    return-object p0
.end method

.method private roomViewportHeight()I
    .locals 3

    .line 263
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->middlePanel:Landroid/widget/LinearLayout;

    if-nez v0, :cond_0

    const/4 v0, 0x0

    goto :goto_0

    :cond_0
    invoke-virtual {v0}, Landroid/widget/LinearLayout;->getHeight()I

    move-result v0

    :goto_0
    if-lez v0, :cond_1

    goto :goto_1

    :cond_1
    const/high16 v0, 0x43340000    # 180.0f

    .line 264
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    invoke-virtual {v1}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v1

    iget v1, v1, Landroid/util/DisplayMetrics;->heightPixels:I

    const/high16 v2, 0x42b40000    # 90.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    sub-int/2addr v1, v2

    invoke-static {v0, v1}, Ljava/lang/Math;->max(II)I

    move-result v0

    :goto_1
    return v0
.end method

.method private row()Landroid/widget/LinearLayout;
    .locals 2

    .line 91
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/16 v1, 0x10

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setGravity(I)V

    return-object v0
.end method

.method private static sameRoomSetupProfile(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Z
    .locals 2

    if-eqz p0, :cond_0

    if-eqz p1, :cond_0

    .line 694
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->itemId:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->itemId:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->contentSha256:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->contentSha256:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->engineId:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->engineId:Ljava/lang/String;

    .line 695
    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->coreSha256:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->coreSha256:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->runtimeSha256:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->runtimeSha256:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->profileId:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->profileId:Ljava/lang/String;

    .line 696
    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->profileSha256:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->profileSha256:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->mode:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->mode:Ljava/lang/String;

    .line 697
    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->controllerProfile:Ljava/lang/String;

    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->controllerProfile:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->maximumPlayers:I

    iget v1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->maximumPlayers:I

    if-ne v0, v1, :cond_0

    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    .line 698
    invoke-static {p0, p1}, Ljava/util/Arrays;->equals([I[I)Z

    move-result p0

    if-eqz p0, :cond_0

    const/4 p0, 0x1

    goto :goto_0

    :cond_0
    const/4 p0, 0x0

    :goto_0
    return p0
.end method

.method private scheduleMultiplayerPoll(Lorg/emulationstation/frontend/netplay/StationOnlineClient;IIJ)V
    .locals 8

    .line 515
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_1

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p2, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq v0, p1, :cond_0

    goto :goto_0

    .line 516
    :cond_0
    iget v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    .line 517
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerEvents:Ljava/util/concurrent/ScheduledExecutorService;

    new-instance v7, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda69;

    move-object v1, v7

    move-object v2, p0

    move v3, p2

    move-object v5, p1

    move v6, p3

    invoke-direct/range {v1 .. v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda69;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;IILorg/emulationstation/frontend/netplay/StationOnlineClient;I)V

    const-wide/16 p1, 0x0

    .line 532
    invoke-static {p1, p2, p4, p5}, Ljava/lang/Math;->max(JJ)J

    move-result-wide p1

    sget-object p3, Ljava/util/concurrent/TimeUnit;->MILLISECONDS:Ljava/util/concurrent/TimeUnit;

    .line 517
    invoke-interface {v0, v7, p1, p2, p3}, Ljava/util/concurrent/ScheduledExecutorService;->schedule(Ljava/lang/Runnable;JLjava/util/concurrent/TimeUnit;)Ljava/util/concurrent/ScheduledFuture;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPolling:Ljava/util/concurrent/ScheduledFuture;

    :cond_1
    :goto_0
    return-void
.end method

.method private scroll(Landroid/widget/LinearLayout;Landroid/widget/LinearLayout;)Landroid/widget/ScrollView;
    .locals 5

    .line 119
    new-instance v0, Landroid/widget/ScrollView;

    invoke-direct {v0, p0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->setFillViewport(Z)V

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->setClipToPadding(Z)V

    const/high16 v2, 0x41200000    # 10.0f

    invoke-direct {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v2

    invoke-virtual {v0, v1, v2, v1, v1}, Landroid/widget/ScrollView;->setPadding(IIII)V

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->setVerticalScrollBarEnabled(Z)V

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v3, -0x2

    const/4 v4, -0x1

    invoke-direct {v2, v4, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, p2, v2}, Landroid/widget/ScrollView;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    new-instance p2, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v2, 0x3f800000    # 1.0f

    invoke-direct {p2, v4, v1, v2}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    invoke-virtual {p1, v0, p2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-object v0
.end method

.method private selectRoomMode(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)V
    .locals 7

    .line 648
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v0, p1}, Ljava/util/List;->contains(Ljava/lang/Object;)Z

    move-result v0

    const/4 v1, 0x1

    if-eqz v0, :cond_4

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    goto :goto_2

    .line 649
    :cond_0
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v2

    const/4 v3, 0x0

    if-eqz v2, :cond_1

    goto :goto_0

    :cond_1
    const/4 v0, 0x2

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v2

    if-eqz v2, :cond_2

    goto :goto_0

    :cond_2
    iget-object v0, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    aget v0, v0, v3

    :goto_0
    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    .line 650
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCounts:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCountLabels:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    .line 651
    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    array-length v0, p1

    :goto_1
    if-ge v3, v0, :cond_3

    aget v2, p1, v3

    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCounts:Landroid/widget/LinearLayout;

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v5, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v6, " jogadores"

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    new-instance v6, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda25;

    invoke-direct {v6, p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda25;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-direct {p0, v4, v5, v1, v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupChoice(Landroid/widget/LinearLayout;Ljava/lang/String;ZLjava/lang/Runnable;)Landroid/widget/TextView;

    move-result-object v2

    iget-object v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCountLabels:Ljava/util/List;

    invoke-interface {v4, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    add-int/lit8 v3, v3, 0x1

    goto :goto_1

    .line 652
    :cond_3
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderRoomSetup()V

    return-void

    .line 648
    :cond_4
    :goto_2
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    const-string p1, "A sele\u00e7\u00e3o mudou. Confira o jogo e escolha a partida novamente."

    invoke-direct {p0, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    return-void
.end method

.method private sendChat()V
    .locals 5

    .line 759
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    invoke-virtual {v0}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v2

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_4

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-eqz v3, :cond_0

    goto :goto_1

    .line 760
    :cond_0
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-eqz v3, :cond_1

    if-nez v2, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Escolha uma pessoa ou entre em uma sala."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    .line 761
    :cond_1
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_2

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v3}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v3

    const-string v4, "direct-chat-v1"

    invoke-static {v3, v4}, Lorg/emulationstation/frontend/netplay/StationSocial;->supports(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v3

    if-nez v3, :cond_2

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "A conversa privada ainda n\u00e3o est\u00e1 dispon\u00edvel nesta sess\u00e3o."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_2
    if-nez v2, :cond_3

    const-string v2, ""

    goto :goto_0

    :cond_3
    const-string v3, "roomId"

    .line 762
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 763
    :goto_0
    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda54;

    invoke-direct {v3, p0, v1, v0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda54;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda55;

    invoke-direct {v2, p0, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda55;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;)V

    invoke-direct {p0, v3, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Ljava/lang/Runnable;)V

    :cond_4
    :goto_1
    return-void
.end method

.method private static separateRoomNotice(Ljava/lang/String;Ljava/lang/String;)Z
    .locals 1

    if-eqz p0, :cond_1

    .line 1061
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_1

    if-eqz p1, :cond_0

    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p1}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_1

    :cond_0
    const/4 p0, 0x1

    goto :goto_0

    :cond_1
    const/4 p0, 0x0

    :goto_0
    return p0
.end method

.method private setConnection(Ljava/lang/String;Z)V
    .locals 3

    .line 127
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->connection:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    if-eqz p2, :cond_0

    const-string v2, "\u25cf  "

    goto :goto_0

    :cond_0
    const-string v2, "\u25cb  "

    :goto_0
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->connection:Landroid/widget/TextView;

    if-eqz p2, :cond_1

    const p2, -0xb92401

    goto :goto_1

    :cond_1
    const p2, -0x554736

    :goto_1
    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setTextColor(I)V

    return-void
.end method

.method private setupChoice(Landroid/widget/LinearLayout;Ljava/lang/String;ZLjava/lang/Runnable;)Landroid/widget/TextView;
    .locals 3

    const/16 v0, 0xc

    const v1, -0x100a01

    .line 630
    invoke-direct {p0, p2, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p2

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/16 v0, 0x11

    invoke-virtual {p2, v0}, Landroid/widget/TextView;->setGravity(I)V

    const/high16 v0, 0x41400000    # 12.0f

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v1

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v0

    const/4 v2, 0x0

    invoke-virtual {p2, v1, v2, v0, v2}, Landroid/widget/TextView;->setPadding(IIII)V

    const/4 v0, 0x1

    .line 631
    invoke-virtual {p2, v0}, Landroid/widget/TextView;->setSingleLine(Z)V

    invoke-virtual {p2, v0}, Landroid/widget/TextView;->setFocusable(Z)V

    invoke-virtual {p2, v0}, Landroid/widget/TextView;->setClickable(Z)V

    .line 632
    sget-object v0, Landroid/text/TextUtils$TruncateAt;->END:Landroid/text/TextUtils$TruncateAt;

    invoke-virtual {p2, v0}, Landroid/widget/TextView;->setEllipsize(Landroid/text/TextUtils$TruncateAt;)V

    .line 633
    new-instance v0, Landroid/widget/LinearLayout$LayoutParams;

    if-eqz p3, :cond_0

    goto :goto_0

    :cond_0
    const/4 v2, -0x2

    :goto_0
    if-eqz p3, :cond_1

    const/high16 p3, 0x3f800000    # 1.0f

    goto :goto_1

    :cond_1
    const/4 p3, 0x0

    :goto_1
    const/4 v1, -0x1

    invoke-direct {v0, v2, v1, p3}, Landroid/widget/LinearLayout$LayoutParams;-><init>(IIF)V

    const/high16 p3, 0x40a00000    # 5.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    iput p3, v0, Landroid/widget/LinearLayout$LayoutParams;->rightMargin:I

    invoke-virtual {p1, p2, v0}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 634
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda97;

    invoke-direct {p1, p0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda97;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/Runnable;)V

    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-object p2
.end method

.method private static setupModeName(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Ljava/lang/String;
    .locals 2

    .line 593
    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileInfo(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v0

    iget-boolean v1, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->modeConfirmed:Z

    if-eqz v1, :cond_0

    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->modeLabel:Ljava/lang/String;

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playGuidance(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_0

    return-object v0

    .line 594
    :cond_0
    iget-object p0, p0, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->mode:Ljava/lang/String;

    invoke-virtual {p0}, Ljava/lang/String;->hashCode()I

    invoke-virtual {p0}, Ljava/lang/String;->hashCode()I

    move-result v0

    const/4 v1, -0x1

    sparse-switch v0, :sswitch_data_0

    goto/16 :goto_0

    :sswitch_0
    const-string v0, "vs-race"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_1

    goto :goto_0

    :cond_1
    const/4 v1, 0x7

    goto :goto_0

    :sswitch_1
    const-string v0, "two-player-b"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_2

    goto :goto_0

    :cond_2
    const/4 v1, 0x6

    goto :goto_0

    :sswitch_2
    const-string v0, "two-player-a"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_3

    goto :goto_0

    :cond_3
    const/4 v1, 0x5

    goto :goto_0

    :sswitch_3
    const-string v0, "match-multitap"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_4

    goto :goto_0

    :cond_4
    const/4 v1, 0x4

    goto :goto_0

    :sswitch_4
    const-string v0, "adventure-coop"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_5

    goto :goto_0

    :cond_5
    const/4 v1, 0x3

    goto :goto_0

    :sswitch_5
    const-string v0, "championship-2p"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_6

    goto :goto_0

    :cond_6
    const/4 v1, 0x2

    goto :goto_0

    :sswitch_6
    const-string v0, "normal"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_7

    goto :goto_0

    :cond_7
    const/4 v1, 0x1

    goto :goto_0

    :sswitch_7
    const-string v0, "two-player"

    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_8

    goto :goto_0

    :cond_8
    const/4 v1, 0x0

    :goto_0
    packed-switch v1, :pswitch_data_0

    const-string p0, "Modo aprovado"

    return-object p0

    :pswitch_0
    const-string p0, "Corrida entre jogadores"

    return-object p0

    :pswitch_1
    const-string p0, "Dois jogadores \u00b7 modo B"

    return-object p0

    :pswitch_2
    const-string p0, "Dois jogadores \u00b7 modo A"

    return-object p0

    :pswitch_3
    const-string p0, "Partida em grupo"

    return-object p0

    :pswitch_4
    const-string p0, "Aventura cooperativa"

    return-object p0

    :pswitch_5
    const-string p0, "Campeonato para dois"

    return-object p0

    :pswitch_6
    const-string p0, "Modo normal"

    return-object p0

    :pswitch_7
    const-string p0, "Partida para dois"

    return-object p0

    nop

    :sswitch_data_0
    .sparse-switch
        -0x468faa7e -> :sswitch_7
        -0x3df94319 -> :sswitch_6
        -0x1a4840da -> :sswitch_5
        -0x17a83c16 -> :sswitch_4
        0x10da8ad2 -> :sswitch_3
        0x1eb102d6 -> :sswitch_2
        0x1eb102d7 -> :sswitch_1
        0x290c0be1 -> :sswitch_0
    .end sparse-switch

    :pswitch_data_0
    .packed-switch 0x0
        :pswitch_7
        :pswitch_6
        :pswitch_5
        :pswitch_4
        :pswitch_3
        :pswitch_2
        :pswitch_1
        :pswitch_0
    .end packed-switch
.end method

.method private showCreateMessage(Ljava/lang/String;Z)V
    .locals 2

    .line 552
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->onlineNotice(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    if-eqz p2, :cond_0

    const p2, -0xb4f5e

    goto :goto_0

    :cond_0
    const p2, -0xb92401

    :goto_0
    invoke-virtual {v0, p2}, Landroid/widget/TextView;->setTextColor(I)V

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result p1

    if-eqz p1, :cond_1

    const/16 p1, 0x8

    goto :goto_1

    :cond_1
    const/4 p1, 0x0

    :goto_1
    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setVisibility(I)V

    return-void
.end method

.method private showGameDetails(Ljava/lang/String;Ljava/lang/String;)V
    .locals 3

    .line 287
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eqz v0, :cond_1

    if-nez p1, :cond_0

    goto :goto_0

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    goto :goto_1

    :cond_1
    :goto_0
    const-string v0, "Informa\u00e7\u00f5es do jogo"

    .line 288
    :goto_1
    invoke-static {p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playGuidance(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->synopsisFor(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p2}, Ljava/lang/String;->isEmpty()Z

    move-result p1

    if-eqz p1, :cond_2

    const-string p1, ""

    goto :goto_2

    :cond_2
    new-instance p1, Ljava/lang/StringBuilder;

    const-string v2, "\n\nComo jogar\n"

    invoke-direct {p1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    :goto_2
    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    .line 289
    new-instance p2, Landroid/app/AlertDialog$Builder;

    invoke-direct {p2, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    invoke-virtual {p2, v0}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p2

    invoke-virtual {p2, p1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    const-string p2, "Fechar"

    const/4 v0, 0x0

    invoke-virtual {p1, p2, v0}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    invoke-virtual {p1}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    return-void
.end method

.method private showPlayer(Ljava/lang/String;Ljava/lang/String;)V
    .locals 2

    .line 871
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->dismiss()V

    :cond_0
    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedPeer:Ljava/lang/String;

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedName:Ljava/lang/String;

    const-string v0, ""

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    .line 872
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$3;

    invoke-direct {v1, p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$3;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;)V

    invoke-direct {v0, p0, v1}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;-><init>(Landroid/app/Activity;Lorg/emulationstation/frontend/netplay/StationPlayerSheet$Actions;)V

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    .line 878
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda22;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda22;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->setOnDismissListener(Landroid/content/DialogInterface$OnDismissListener;)V

    .line 879
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->show()V

    return-void
.end method

.method private showRoomCode()V
    .locals 8

    const-string v0, "inviteCode"

    .line 931
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v1

    if-eqz v1, :cond_0

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "recoveryProtocol"

    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const-string v2, "station-stream.v3"

    invoke-virtual {v2, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v1, "Entre nesta partida pela lista de salas. O c\u00f3digo desta modalidade ainda est\u00e1 em prepara\u00e7\u00e3o."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    .line 932
    :cond_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v1

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->shareable(Lorg/json/JSONObject;)Z

    move-result v2

    if-nez v2, :cond_1

    const-string v0, "O c\u00f3digo est\u00e1 dispon\u00edvel quando sua sala tem uma vaga e aguarda jogadores."

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_1
    const-string v2, "room"

    .line 933
    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v2

    .line 934
    :try_start_0
    invoke-virtual {v2, v0}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v3
    :try_end_0
    .catch Ljava/lang/IllegalArgumentException; {:try_start_0 .. :try_end_0} :catch_0

    const-string v4, "itemId"

    if-eqz v3, :cond_2

    :try_start_1
    invoke-virtual {v2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->display(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    goto :goto_0

    :cond_2
    const-string v0, "instance"

    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v1, "roomId"

    invoke-virtual {v2, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v2, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-static {v0, v1, v3}, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->encode(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0
    :try_end_1
    .catch Ljava/lang/IllegalArgumentException; {:try_start_1 .. :try_end_1} :catch_0

    .line 935
    :goto_0
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v2, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v3, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "\nCompartilhe com outro jogador. "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "TS1:"

    invoke-virtual {v0, v2}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v3

    if-eqz v3, :cond_3

    const-string v3, "Ele cola o convite em C\u00f3digo de convite."

    goto :goto_1

    :cond_3
    const-string v3, "Ele digita ou cola os 8 caracteres em C\u00f3digo de convite."

    :goto_1
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v3, " A senha da partida \u00e9 autom\u00e1tica ap\u00f3s atualizar o app."

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const-string v3, "C\u00f3digo da sua sala"

    invoke-direct {p0, v3, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codePanel(Ljava/lang/String;Ljava/lang/String;)Landroid/widget/LinearLayout;

    move-result-object v1

    .line 936
    invoke-virtual {v0, v2}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_4

    const/16 v2, 0xc

    goto :goto_2

    :cond_4
    const/16 v2, 0x1a

    :goto_2
    const v3, -0x100a01

    invoke-direct {p0, v1, v0, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object v2

    sget-object v3, Landroid/graphics/Typeface;->MONOSPACE:Landroid/graphics/Typeface;

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    const/4 v3, 0x1

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextIsSelectable(Z)V

    const/high16 v4, 0x41400000    # 12.0f

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v5

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v6

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v7

    invoke-direct {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result v4

    invoke-virtual {v2, v5, v6, v7, v4}, Landroid/widget/TextView;->setPadding(IIII)V

    const v4, -0xf8eddd

    const v5, -0xd3b99c

    invoke-direct {p0, v4, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bg(II)Landroid/graphics/drawable/GradientDrawable;

    move-result-object v4

    invoke-virtual {v2, v4}, Landroid/widget/TextView;->setBackground(Landroid/graphics/drawable/Drawable;)V

    const/16 v2, 0xb

    const v4, -0x554736

    const-string v5, "V\u00e1lido enquanto esta sala existir e tiver uma vaga. O outro jogador precisa da mesma edi\u00e7\u00e3o instalada."

    .line 937
    invoke-direct {p0, v1, v5, v2, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;

    .line 938
    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda111;

    invoke-direct {v2, p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda111;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;)V

    const-string v0, "Copiar c\u00f3digo"

    invoke-direct {p0, v1, v0, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v0

    .line 939
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->compactCreateAction(Landroid/widget/Button;)V

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda112;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda112;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    const/4 v2, 0x0

    const-string v3, "Fechar"

    invoke-direct {p0, v1, v3, v0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->button(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/Runnable;Z)Landroid/widget/Button;

    move-result-object v0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->compactCreateAction(Landroid/widget/Button;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->displayCodePanel()V

    return-void

    :catch_0
    move-exception v0

    .line 934
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    invoke-virtual {v0}, Ljava/lang/IllegalArgumentException;->getMessage()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void
.end method

.method private showRoomSetup(Ljava/util/List;)V
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/List<",
            "Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;",
            ">;)V"
        }
    .end annotation

    .line 637
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v0, p1}, Ljava/util/List;->addAll(Ljava/util/Collection;)Z

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {p1}, Ljava/util/List;->isEmpty()Z

    move-result p1

    if-nez p1, :cond_5

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result p1

    if-eqz p1, :cond_0

    goto/16 :goto_3

    .line 638
    :cond_0
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModes:Landroid/widget/LinearLayout;

    invoke-virtual {p1}, Landroid/widget/LinearLayout;->removeAllViews()V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeLabels:Ljava/util/List;

    invoke-interface {p1}, Ljava/util/List;->clear()V

    const/4 p1, 0x0

    move v0, p1

    .line 639
    :goto_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->size()I

    move-result v1

    if-ge v0, v1, :cond_4

    .line 640
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v1, v0}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeName(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Ljava/lang/String;

    move-result-object v2

    .line 641
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v3}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v3

    move v4, p1

    :cond_1
    :goto_1
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_2

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-static {v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeName(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v2, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_1

    add-int/lit8 v4, v4, 0x1

    goto :goto_1

    .line 642
    :cond_2
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const/4 v2, 0x1

    if-le v4, v2, :cond_3

    new-instance v2, Ljava/lang/StringBuilder;

    const-string v4, " \u00b7 op\u00e7\u00e3o "

    invoke-direct {v2, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    add-int/lit8 v4, v0, 0x1

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    goto :goto_2

    :cond_3
    const-string v2, ""

    :goto_2
    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    .line 643
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModes:Landroid/widget/LinearLayout;

    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda89;

    invoke-direct {v4, p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda89;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)V

    invoke-direct {p0, v3, v2, p1, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupChoice(Landroid/widget/LinearLayout;Ljava/lang/String;ZLjava/lang/Runnable;)Landroid/widget/TextView;

    move-result-object v1

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setContentDescription(Ljava/lang/CharSequence;)V

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeLabels:Ljava/util/List;

    invoke-interface {v2, v1}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 645
    :cond_4
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createOverview:Landroid/widget/LinearLayout;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    invoke-virtual {v0, p1}, Landroid/widget/LinearLayout;->setVisibility(I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfiles:Ljava/util/List;

    invoke-interface {v0, p1}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectRoomMode(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)V

    :cond_5
    :goto_3
    return-void
.end method

.method private socialAction(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 827
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda87;

    invoke-direct {v0, p0, p1, p2, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda87;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V

    return-void
.end method

.method private startRoom(Ljava/lang/String;)V
    .locals 3

    .line 1070
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomStartState;->reason(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v1

    .line 1071
    iget-boolean v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v2, :cond_7

    iget-boolean v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-eqz v2, :cond_0

    goto :goto_2

    .line 1072
    :cond_0
    iget-boolean v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v2, :cond_5

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-nez v2, :cond_1

    goto :goto_1

    .line 1073
    :cond_1
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomConfirmationKey(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p1, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v0, "A sala mudou. Confira os participantes antes de iniciar."

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_2
    if-nez v0, :cond_3

    const/4 v1, 0x0

    goto :goto_0

    :cond_3
    const-string v1, "transports"

    .line 1075
    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v1

    .line 1076
    :goto_0
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomStartState;->transport(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->contains(Lorg/json/JSONArray;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_4

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v0, "A partida online ainda n\u00e3o est\u00e1 dispon\u00edvel nesta sess\u00e3o. Aguarde a ativa\u00e7\u00e3o desta op\u00e7\u00e3o; os jogos locais continuam dispon\u00edveis."

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    .line 1077
    :cond_4
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda90;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda90;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Ljava/lang/String;)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V

    return-void

    .line 1072
    :cond_5
    :goto_1
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_6

    const-string v1, "Aguarde a solicita\u00e7\u00e3o atual terminar."

    :cond_6
    invoke-virtual {p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->fail(Ljava/lang/String;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v1

    iget-boolean v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    invoke-virtual {v0, v1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->text(Lorg/json/JSONObject;Z)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->onlineNotice(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_7
    :goto_2
    return-void
.end method

.method private declared-synchronized stopMultiplayerPoll()V
    .locals 2

    monitor-enter p0

    .line 80
    :try_start_0
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    const/4 v1, 0x1

    add-int/2addr v0, v1

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPolling:Ljava/util/concurrent/ScheduledFuture;

    if-eqz v0, :cond_0

    invoke-interface {v0, v1}, Ljava/util/concurrent/ScheduledFuture;->cancel(Z)Z

    const/4 v0, 0x0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPolling:Ljava/util/concurrent/ScheduledFuture;

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-eqz v0, :cond_1

    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancel()V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    :cond_1
    monitor-exit p0

    return-void

    :catchall_0
    move-exception v0

    monitor-exit p0

    throw v0
.end method

.method private styleAction(Landroid/widget/Button;I)V
    .locals 0

    const/4 p2, 0x0

    .line 98
    invoke-virtual {p1, p2}, Landroid/widget/Button;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V

    const/high16 p2, 0x41500000    # 13.0f

    invoke-virtual {p1, p2}, Landroid/widget/Button;->setTextSize(F)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bold(Landroid/widget/TextView;)V

    const/4 p2, 0x1

    .line 99
    invoke-virtual {p1, p2}, Landroid/widget/Button;->setFocusable(Z)V

    const/4 p2, 0x0

    invoke-virtual {p1, p2}, Landroid/widget/Button;->setFocusableInTouchMode(Z)V

    return-void
.end method

.method private styleNavigation(Landroid/widget/Button;Z)V
    .locals 1

    const/4 v0, 0x0

    .line 988
    invoke-virtual {p1, v0}, Landroid/widget/Button;->setBackgroundTintList(Landroid/content/res/ColorStateList;)V

    .line 989
    check-cast p1, Lorg/emulationstation/frontend/netplay/StationActionButton;

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationActionButton;->setNavigationSelected(Z)V

    return-void
.end method

.method private static supportsShortInvite(Lorg/json/JSONObject;)Z
    .locals 4

    const-string v0, "roomCapabilities"

    .line 965
    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object p0

    const/4 v0, 0x0

    move v1, v0

    :goto_0
    if-eqz p0, :cond_1

    .line 966
    invoke-virtual {p0}, Lorg/json/JSONArray;->length()I

    move-result v2

    if-ge v1, v2, :cond_1

    const-string v2, "short-invite-v1"

    invoke-virtual {p0, v1}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_0

    const/4 p0, 0x1

    return p0

    :cond_0
    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_1
    return v0
.end method

.method private synopsisFor(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    .line 229
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-nez v0, :cond_0

    const/4 v0, 0x0

    goto :goto_0

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v0, v0, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->app:Lorg/emulationstation/frontend/station/StationAndroid;

    iget-object v0, v0, Lorg/emulationstation/frontend/station/StationAndroid;->coordinator:Lorg/emulationstation/frontend/station/StationCoordinator;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationCoordinator;->current()Lorg/emulationstation/frontend/station/StationCoordinator$Library;

    move-result-object v0

    :goto_0
    const-string v1, "Sinopse indispon\u00edvel no momento."

    if-eqz v0, :cond_5

    if-nez p1, :cond_1

    goto :goto_2

    .line 231
    :cond_1
    iget-object v0, v0, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/station/StationCatalog;->find(Ljava/lang/String;)Lorg/emulationstation/frontend/station/StationCatalog$Item;

    move-result-object p1

    if-nez p1, :cond_2

    return-object v1

    .line 233
    :cond_2
    iget-object v0, p1, Lorg/emulationstation/frontend/station/StationCatalog$Item;->description:Ljava/lang/String;

    if-nez v0, :cond_3

    const-string p1, ""

    goto :goto_1

    :cond_3
    iget-object p1, p1, Lorg/emulationstation/frontend/station/StationCatalog$Item;->description:Ljava/lang/String;

    invoke-virtual {p1}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object p1

    .line 234
    :goto_1
    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_4

    const-string p1, "Sinopse ainda n\u00e3o cadastrada."

    :cond_4
    return-object p1

    :cond_5
    :goto_2
    return-object v1
.end method

.method private text(Landroid/widget/LinearLayout;Ljava/lang/String;II)Landroid/widget/TextView;
    .locals 1

    .line 93
    invoke-direct {p0, p2, p3, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->label(Ljava/lang/String;II)Landroid/widget/TextView;

    move-result-object p2

    const/high16 p3, 0x40a00000    # 5.0f

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p4

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->dp(F)I

    move-result p3

    const/4 v0, 0x0

    invoke-virtual {p2, v0, p4, v0, p3}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance p3, Landroid/widget/LinearLayout$LayoutParams;

    const/4 p4, -0x1

    const/4 v0, -0x2

    invoke-direct {p3, p4, v0}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {p1, p2, p3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-object p2
.end method

.method private unavailableLobby()V
    .locals 5

    const-string v0, "Indispon\u00edvel"

    const/4 v1, 0x0

    .line 135
    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setConnection(Ljava/lang/String;Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->removeAllViews()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomRows()V

    .line 136
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peers:Landroid/widget/LinearLayout;

    const-string v2, "Conex\u00e3o pendente"

    const-string v3, "Os jogadores aparecem quando o servi\u00e7o estiver dispon\u00edvel."

    const-string v4, "\u25cb"

    invoke-direct {p0, v0, v4, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->rooms:Landroid/widget/LinearLayout;

    const-string v2, "Salas indispon\u00edveis"

    const-string v3, "N\u00e3o foi poss\u00edvel conectar agora. Use Reconectar para tentar novamente."

    const-string v4, "!"

    invoke-direct {p0, v0, v4, v2, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->empty(Landroid/widget/LinearLayout;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    invoke-direct {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->composer(Z)V

    return-void
.end method

.method private updateOwnRoomHeight()V
    .locals 4

    .line 279
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz v0, :cond_5

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    if-eqz v0, :cond_5

    invoke-virtual {v0}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result v0

    if-nez v0, :cond_0

    goto :goto_3

    :cond_0
    const/4 v0, 0x0

    .line 280
    :goto_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-virtual {v1}, Landroid/widget/LinearLayout;->getChildCount()I

    move-result v1

    if-ge v0, v1, :cond_4

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    invoke-virtual {v1, v0}, Landroid/widget/LinearLayout;->getChildAt(I)Landroid/view/View;

    move-result-object v1

    invoke-virtual {v1}, Landroid/view/View;->getVisibility()I

    move-result v2

    const/16 v3, 0x8

    if-ne v2, v3, :cond_1

    goto :goto_2

    .line 281
    :cond_1
    instance-of v2, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;

    if-eqz v2, :cond_2

    check-cast v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;

    invoke-virtual {v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomControls;->hasMeasuredActions()Z

    move-result v1

    if-nez v1, :cond_3

    goto :goto_1

    :cond_2
    invoke-virtual {v1}, Landroid/view/View;->getMeasuredHeight()I

    move-result v1

    if-nez v1, :cond_3

    :goto_1
    return-void

    :cond_3
    :goto_2
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 283
    :cond_4
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->getLayoutParams()Landroid/view/ViewGroup$LayoutParams;

    move-result-object v0

    check-cast v0, Landroid/widget/LinearLayout$LayoutParams;

    .line 284
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomRequiredHeight()I

    move-result v1

    iget v2, v0, Landroid/widget/LinearLayout$LayoutParams;->height:I

    if-eq v2, v1, :cond_5

    iput v1, v0, Landroid/widget/LinearLayout$LayoutParams;->height:I

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-virtual {v1, v0}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setLayoutParams(Landroid/view/ViewGroup$LayoutParams;)V

    :cond_5
    :goto_3
    return-void
.end method

.method private updateRoomSetupEnabled()V
    .locals 5

    .line 674
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupConfirm:Landroid/widget/Button;

    if-nez v0, :cond_0

    return-void

    :cond_0
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    const/4 v1, 0x1

    const/4 v2, 0x0

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-eqz v0, :cond_1

    iget v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    invoke-virtual {v0, v3}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result v0

    if-eqz v0, :cond_1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupContext:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    move v0, v1

    goto :goto_0

    :cond_1
    move v0, v2

    .line 675
    :goto_0
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupConfirm:Landroid/widget/Button;

    invoke-virtual {v3, v0}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupBack:Landroid/widget/Button;

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v3, :cond_2

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v3, :cond_2

    move v3, v1

    goto :goto_1

    :cond_2
    move v3, v2

    :goto_1
    invoke-virtual {v0, v3}, Landroid/widget/Button;->setEnabled(Z)V

    .line 676
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupModeLabels:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_2
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_4

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Landroid/widget/TextView;

    iget-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v4, :cond_3

    iget-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v4, :cond_3

    move v4, v1

    goto :goto_3

    :cond_3
    move v4, v2

    :goto_3
    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setEnabled(Z)V

    goto :goto_2

    :cond_4
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCountLabels:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_4
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_6

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Landroid/widget/TextView;

    iget-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v4, :cond_5

    iget-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v4, :cond_5

    move v4, v1

    goto :goto_5

    :cond_5
    move v4, v2

    :goto_5
    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setEnabled(Z)V

    goto :goto_4

    :cond_6
    return-void
.end method

.method private updateStartState()V
    .locals 6

    .line 1064
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomStartState;->reason(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    .line 1065
    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    const/4 v2, 0x0

    if-nez v1, :cond_0

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v1, :cond_0

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_0

    const/4 v1, 0x1

    goto :goto_0

    :cond_0
    move v1, v2

    .line 1066
    :goto_0
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->start:Landroid/widget/Button;

    if-eqz v3, :cond_2

    invoke-virtual {v3, v1}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->start:Landroid/widget/Button;

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v4, "Iniciar partida"

    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v4

    if-eqz v4, :cond_1

    const-string v4, ""

    goto :goto_1

    :cond_1
    new-instance v4, Ljava/lang/StringBuilder;

    const-string v5, ": "

    invoke-direct {v4, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v4, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    :goto_1
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v3}, Landroid/widget/Button;->setContentDescription(Ljava/lang/CharSequence;)V

    .line 1067
    :cond_2
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomReadiness:Landroid/widget/TextView;

    if-eqz v1, :cond_7

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-eqz v3, :cond_3

    const-string v0, "Confirmando sua solicita\u00e7\u00e3o\u2026"

    goto :goto_2

    :cond_3
    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-eqz v3, :cond_4

    const-string v0, "Preparando a partida\u2026"

    :cond_4
    :goto_2
    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomReadiness:Landroid/widget/TextView;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    if-nez v3, :cond_5

    const/4 v3, 0x0

    goto :goto_3

    :cond_5
    invoke-virtual {v3}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;

    move-result-object v3

    invoke-interface {v3}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v3

    :goto_3
    invoke-static {v0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->separateRoomNotice(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_6

    goto :goto_4

    :cond_6
    const/16 v2, 0x8

    :goto_4
    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setVisibility(I)V

    :cond_7
    return-void
.end method

.method private vertical()Landroid/widget/LinearLayout;
    .locals 2

    .line 90
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setOrientation(I)V

    return-object v0
.end method


# virtual methods
.method synthetic lambda$action$38$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/Runnable;)V
    .locals 3

    .line 548
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_3

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_3

    const/4 p1, 0x0

    iput-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v2

    invoke-virtual {v1, v2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->text(Lorg/json/JSONObject;Z)Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->onlineNotice(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateStartState()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v1

    if-nez v1, :cond_0

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v1, :cond_0

    const/4 p1, 0x1

    :cond_0
    invoke-virtual {v0, p1}, Landroid/widget/Button;->setEnabled(Z)V

    if-eqz p2, :cond_1

    invoke-interface {p2}, Ljava/lang/Runnable;->run()V

    :cond_1
    const-wide/16 p1, -0x1

    iput-wide p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paint(Lorg/json/JSONObject;)V

    :cond_2
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateRoomSetupEnabled()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    :cond_3
    return-void
.end method

.method synthetic lambda$action$39$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;Lorg/emulationstation/frontend/station/StationApi$Cancellation;ILjava/lang/Runnable;)V
    .locals 0

    .line 548
    :try_start_0
    invoke-interface {p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;->run(Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda72;

    invoke-direct {p1, p0, p3, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda72;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/Runnable;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception p1

    goto :goto_1

    :catch_0
    move-exception p1

    :try_start_1
    invoke-virtual {p2}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancelled()Z

    move-result p4

    if-nez p4, :cond_0

    invoke-direct {p0, p1, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->failure(Ljava/lang/Throwable;I)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    :cond_0
    :goto_0
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p1, p2}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    return-void

    :goto_1
    iget-object p3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p3, p2}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    throw p1
.end method

.method synthetic lambda$addSynopsis$17$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Landroid/view/View;)V
    .locals 0

    .line 293
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$addSynopsis$18$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Landroid/view/View;)V
    .locals 0

    .line 294
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$beginMultiplayerDiscovery$31$org-emulationstation-frontend-netplay-StationRoomsActivity(IILorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;)V
    .locals 6

    .line 504
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_2

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p1, :cond_2

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    if-ne p2, v0, :cond_2

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq p2, p3, :cond_0

    goto :goto_0

    .line 505
    :cond_0
    iget-boolean p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez p2, :cond_1

    iget-boolean p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    if-nez p2, :cond_1

    invoke-virtual {p4}, Ljava/lang/String;->isEmpty()Z

    move-result p2

    xor-int/lit8 p2, p2, 0x1

    invoke-direct {p0, p4, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    .line 506
    :cond_1
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    .line 507
    iget-boolean p2, p3, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-eqz p2, :cond_2

    const/4 v3, 0x0

    const-wide/16 v4, 0x3e8

    move-object v0, p0

    move-object v1, p3

    move v2, p1

    .line 508
    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->scheduleMultiplayerPoll(Lorg/emulationstation/frontend/netplay/StationOnlineClient;IIJ)V

    :cond_2
    :goto_0
    return-void
.end method

.method synthetic lambda$beginMultiplayerDiscovery$32$org-emulationstation-frontend-netplay-StationRoomsActivity(IILorg/emulationstation/frontend/netplay/StationOnlineClient;)V
    .locals 10

    .line 490
    new-instance v0, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-direct {v0}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;-><init>()V

    .line 491
    monitor-enter p0

    :try_start_0
    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v1, :cond_a

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v1, p1, :cond_a

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    if-ne p2, v1, :cond_a

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq v1, p3, :cond_0

    goto/16 :goto_4

    :cond_0
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v1, v0}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    monitor-exit p0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    const-string v1, ""

    const/4 v2, 0x0

    .line 494
    :try_start_1
    invoke-virtual {p3, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->discoverMultiplayer(Lorg/emulationstation/frontend/station/StationApi$Cancellation;)V

    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->check()V

    .line 495
    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v3, :cond_3

    iget v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v3, p1, :cond_3

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq v3, p3, :cond_1

    goto :goto_0

    .line 496
    :cond_1
    invoke-virtual {p3, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->compose(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object v3

    invoke-direct {p0, v3, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V

    .line 497
    iget-boolean v3, p3, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerEnabled:Z

    if-eqz v3, :cond_2

    const-string v1, ""
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 501
    :cond_2
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v3, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne v3, v0, :cond_6

    goto :goto_1

    :cond_3
    :goto_0
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p1, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne p1, v0, :cond_4

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_4
    return-void

    :catchall_0
    move-exception p1

    goto :goto_3

    :catch_0
    move-exception v1

    .line 499
    :try_start_2
    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancelled()Z

    move-result v3

    if-nez v3, :cond_7

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v3, :cond_7

    iget v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-eq v3, p1, :cond_5

    goto :goto_2

    .line 500
    :cond_5
    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->recordFailure(Ljava/lang/Throwable;)V

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v1
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 501
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v3, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne v3, v0, :cond_6

    :goto_1
    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_6
    move-object v9, v1

    .line 503
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda65;

    move-object v4, v0

    move-object v5, p0

    move v6, p1

    move v7, p2

    move-object v8, p3

    invoke-direct/range {v4 .. v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda65;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;IILorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void

    .line 501
    :cond_7
    :goto_2
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p1, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne p1, v0, :cond_8

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_8
    return-void

    :goto_3
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p2, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne p2, v0, :cond_9

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_9
    throw p1

    .line 491
    :cond_a
    :goto_4
    :try_start_3
    monitor-exit p0

    return-void

    :catchall_1
    move-exception p1

    monitor-exit p0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    throw p1
.end method

.method synthetic lambda$build$10$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/view/View;)V
    .locals 1

    .line 194
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->currentCoverItem()Ljava/lang/String;

    move-result-object p1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    if-nez v0, :cond_0

    const-string v0, ""

    goto :goto_0

    :cond_0
    invoke-virtual {v0}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-interface {v0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v0

    :goto_0
    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$build$11$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/view/View;)V
    .locals 1

    .line 198
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->currentCoverItem()Ljava/lang/String;

    move-result-object p1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createInfo:Landroid/widget/TextView;

    invoke-virtual {v0}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-interface {v0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$build$12$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 201
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chooseGame()V

    return-void
.end method

.method synthetic lambda$build$13$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 203
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createRoom()V

    return-void
.end method

.method synthetic lambda$build$14$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/view/View;)V
    .locals 2

    .line 205
    new-instance p1, Landroid/app/AlertDialog$Builder;

    invoke-direct {p1, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string v0, "Criar sala"

    invoke-virtual {p1, v0}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createMessage:Landroid/widget/TextView;

    invoke-virtual {v0}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-virtual {p1, v0}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    const-string v0, "Fechar"

    const/4 v1, 0x0

    invoke-virtual {p1, v0, v1}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p1

    invoke-virtual {p1}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    return-void
.end method

.method synthetic lambda$build$15$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/view/View;)V
    .locals 1

    .line 208
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result p1

    if-nez p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingName:Ljava/lang/String;

    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->openConversation(Ljava/lang/String;Ljava/lang/String;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$build$16$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 210
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->sendChat()V

    return-void
.end method

.method synthetic lambda$build$2$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, 0x0

    .line 155
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    return-void
.end method

.method synthetic lambda$build$3$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, 0x1

    .line 156
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    return-void
.end method

.method synthetic lambda$build$4$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, 0x2

    .line 157
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    return-void
.end method

.method synthetic lambda$build$5$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 2

    .line 158
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingPeer:Ljava/lang/String;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingName:Ljava/lang/String;

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->openConversation(Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_0

    :cond_0
    const/4 v0, 0x3

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    :goto_0
    return-void
.end method

.method synthetic lambda$build$6$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 162
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->enterCodeDialog()V

    return-void
.end method

.method synthetic lambda$build$7$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 163
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->connect()V

    return-void
.end method

.method synthetic lambda$build$8$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 164
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->exitRooms()V

    return-void
.end method

.method synthetic lambda$build$9$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/view/View;IIIIIIII)V
    .locals 0

    .line 180
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-eqz p1, :cond_1

    sub-int/2addr p5, p3

    sub-int/2addr p9, p7

    if-ne p5, p9, :cond_0

    sub-int/2addr p4, p2

    sub-int/2addr p8, p6

    if-eq p4, p8, :cond_1

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateOwnRoomHeight()V

    :cond_1
    return-void
.end method

.method synthetic lambda$buildRoomSetup$40$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/view/View;)V
    .locals 2

    .line 585
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-eqz p1, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    iget v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    invoke-static {p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupDescription(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;I)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$buildRoomSetup$41$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 589
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    return-void
.end method

.method synthetic lambda$buildRoomSetup$42$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 590
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->confirmRoomSetup()V

    return-void
.end method

.method synthetic lambda$chooseGame$24$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/widget/ArrayAdapter;Landroid/widget/AdapterView;Landroid/view/View;IJ)V
    .locals 0

    .line 441
    invoke-virtual {p1, p4}, Landroid/widget/ArrayAdapter;->getItem(I)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;

    if-nez p1, :cond_0

    return-void

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    iget-object p2, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;->item:Lorg/emulationstation/frontend/station/StationCatalog$Item;

    iget-object p2, p2, Lorg/emulationstation/frontend/station/StationCatalog$Item;->itemId:Ljava/lang/String;

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createGame:Landroid/widget/TextView;

    iget-object p3, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;->item:Lorg/emulationstation/frontend/station/StationCatalog$Item;

    iget-object p3, p3, Lorg/emulationstation/frontend/station/StationCatalog$Item;->name:Ljava/lang/String;

    invoke-virtual {p2, p3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    iget-object p3, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;->item:Lorg/emulationstation/frontend/station/StationCatalog$Item;

    iget-object p3, p3, Lorg/emulationstation/frontend/station/StationCatalog$Item;->name:Ljava/lang/String;

    invoke-virtual {p2, p3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {p2}, Landroid/app/Dialog;->dismiss()V

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$GameChoice;->item:Lorg/emulationstation/frontend/station/StationCatalog$Item;

    iget-object p1, p1, Lorg/emulationstation/frontend/station/StationCatalog$Item;->name:Ljava/lang/String;

    invoke-virtual {p2, p1}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setGameName(Ljava/lang/String;)V

    const-string p1, ""

    const/4 p2, 0x0

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    return-void
.end method

.method synthetic lambda$command$56$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;Ljava/lang/String;Lorg/json/JSONObject;JLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 0
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 756
    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p2, :cond_0

    invoke-virtual {p1, p2, p3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    :cond_0
    invoke-virtual {p4}, Ljava/lang/String;->isEmpty()Z

    move-result p2

    if-nez p2, :cond_1

    const-string p2, "roomId"

    invoke-virtual {p1, p2, p4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    const-string p2, "recoveryProtocol"

    invoke-virtual {p5, p2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    const-string p3, "station-stream.v3"

    invoke-virtual {p3, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-eqz p2, :cond_1

    const-string p2, "generation"

    invoke-virtual {p1, p2, p6, p7}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;

    :cond_1
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const/4 p3, 0x0

    invoke-virtual {p2, p1, p3, p8}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$confirmBlock$89$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;)V
    .locals 2

    .line 910
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->dismiss()V

    :cond_0
    const-string v0, "block"

    const-string v1, "peerId"

    invoke-direct {p0, v0, v1, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->command(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V

    return-void
.end method

.method synthetic lambda$confirmWithCover$25$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/Runnable;)V
    .locals 1

    .line 449
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    invoke-interface {p1}, Ljava/lang/Runnable;->run()V

    return-void
.end method

.method synthetic lambda$confirmWithCover$26$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 450
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    return-void
.end method

.method synthetic lambda$connect$27$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 1

    .line 464
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_1

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p1, :cond_1

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_0

    const/4 p1, 0x1

    goto :goto_0

    :cond_0
    const/4 p1, 0x0

    :goto_0
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomLayout(Z)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    :cond_1
    return-void
.end method

.method synthetic lambda$connect$28$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 1

    .line 479
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p1, :cond_0

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez p1, :cond_0

    const-string p1, "Aguardando conex\u00e3o"

    const/4 v0, 0x0

    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setConnection(Ljava/lang/String;Z)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    const-string v0, "A consulta ser\u00e1 retomada quando a conex\u00e3o voltar."

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$connect$29$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 1

    .line 483
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p1, :cond_0

    const-string p1, "Reconectar"

    const/4 v0, 0x0

    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setConnection(Ljava/lang/String;Z)V

    :cond_0
    return-void
.end method

.method synthetic lambda$connect$30$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;)V
    .locals 11

    .line 0
    const-string v0, "generation"

    const-string v1, "roomId"

    .line 461
    new-instance v2, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-direct {v2}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;-><init>()V

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v3, v2}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    .line 463
    :try_start_0
    new-instance v3, Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-direct {v3, p0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;-><init>(Landroid/content/Context;)V

    iput-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    invoke-virtual {v3, v4}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->setPeerPage(I)V

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomPage:I

    invoke-virtual {v3, v4}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->setRoomPage(I)V

    .line 464
    new-instance v3, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda84;

    invoke-direct {v3, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda84;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-virtual {p0, v3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 465
    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    const/4 v4, 0x0

    if-eqz v3, :cond_1

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningRecovery:Z
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_2
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-nez v3, :cond_1

    :try_start_1
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v5, "leave"

    invoke-static {v5}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v5

    invoke-virtual {v3, v5, v4, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    :try_end_1
    .catch Lorg/emulationstation/frontend/station/StationApi$Failure; {:try_start_1 .. :try_end_1} :catch_0
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_2
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto :goto_0

    :catch_0
    move-exception v3

    :try_start_2
    iget-object v5, v3, Lorg/emulationstation/frontend/station/StationApi$Failure;->code:Ljava/lang/String;

    const-string v6, "STATION_ONLINE_ENTER_REQUIRED"

    invoke-virtual {v5, v6}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_0

    :goto_0
    iput-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    goto :goto_1

    :cond_0
    throw v3

    .line 466
    :cond_1
    :goto_1
    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v5, "enter"

    invoke-static {v5}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v5

    const-string v6, "nickname"

    invoke-virtual {v5, v6, p2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p2

    invoke-virtual {v3, p2, v4, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    .line 467
    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    if-eqz v3, :cond_3

    iget-boolean v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningRecovery:Z

    if-eqz v3, :cond_3

    const-string v3, "room"

    invoke-virtual {p2, v3}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v3

    if-eqz v3, :cond_2

    const-string v5, "relay-wss-v2"

    const-string v6, "transport"

    invoke-virtual {v3, v6}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v6}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_2

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v5, "recovery-failed"

    invoke-static {v5}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v5

    invoke-virtual {v3, v1}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v1, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v1

    invoke-virtual {v3, v0}, Lorg/json/JSONObject;->getLong(Ljava/lang/String;)J

    move-result-wide v5

    invoke-virtual {v1, v0, v5, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;

    move-result-object v0

    invoke-virtual {p2, v0, v4, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    :cond_2
    iput-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    iput-boolean v4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningRecovery:Z

    .line 469
    :cond_3
    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->beginMultiplayerDiscovery(Lorg/emulationstation/frontend/netplay/StationOnlineClient;I)V

    .line 470
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v0

    :goto_2
    move v3, v4

    .line 471
    :goto_3
    iget-boolean v5, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v5, :cond_8

    iget v5, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v5, p1, :cond_8

    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/Thread;->isInterrupted()Z

    move-result v5

    if-nez v5, :cond_8

    .line 472
    iget-object v5, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v5}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v5
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    if-eqz v5, :cond_4

    move-object p2, v5

    .line 474
    :cond_4
    :try_start_3
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v5

    sub-long/2addr v5, v0

    const-wide/16 v7, 0x4e20

    cmp-long v5, v5, v7

    if-ltz v5, :cond_5

    iget-object v5, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v6, "heartbeat"

    invoke-static {v6}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v6

    invoke-virtual {v5, v6, v4, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v0

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V

    .line 475
    :cond_5
    iget-object v5, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget v6, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->page:I

    invoke-virtual {v5, p2, v6, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->events(Lorg/json/JSONObject;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V
    :try_end_3
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_1
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    goto :goto_2

    :catch_1
    move-exception v5

    .line 477
    :try_start_4
    invoke-virtual {v2}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->check()V

    const/4 v6, 0x1

    add-int/2addr v3, v6

    invoke-static {v5, v3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->pollRetryDelay(Ljava/lang/Throwable;I)J

    move-result-wide v7

    const-wide/16 v9, 0x0

    cmp-long v9, v7, v9

    if-ltz v9, :cond_7

    if-ne v3, v6, :cond_6

    .line 478
    invoke-static {v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->recordFailure(Ljava/lang/Throwable;)V

    .line 479
    :cond_6
    new-instance v5, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda85;

    invoke-direct {v5, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda85;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-virtual {p0, v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 480
    invoke-static {v7, v8}, Ljava/lang/Thread;->sleep(J)V

    invoke-virtual {v2}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->check()V

    goto :goto_3

    .line 477
    :cond_7
    throw v5
    :try_end_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_2
    .catchall {:try_start_4 .. :try_end_4} :catchall_0

    :catchall_0
    move-exception p1

    goto :goto_4

    :catch_2
    move-exception p2

    .line 483
    :try_start_5
    invoke-virtual {v2}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancelled()Z

    move-result v0

    if-nez v0, :cond_8

    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda86;

    invoke-direct {v0, p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda86;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;I)V

    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->failure(Ljava/lang/Throwable;I)V
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_0

    :cond_8
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p1, v2}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    return-void

    :goto_4
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p2, v2}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    throw p1
.end method

.method synthetic lambda$createRoom$46$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/util/List;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 688
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-static {p0, v0, p2, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->profiles(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/util/List;

    move-result-object p2

    invoke-interface {p1, p2}, Ljava/util/List;->addAll(Ljava/util/Collection;)Z

    invoke-interface {p1}, Ljava/util/List;->isEmpty()Z

    move-result p1

    if-nez p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const/4 p2, 0x0

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->compose(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1

    :cond_0
    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->unavailable()Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    move-result-object p1

    throw p1
.end method

.method synthetic lambda$createRoom$47$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Ljava/util/List;)V
    .locals 1

    .line 689
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_1

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz p1, :cond_1

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v0, 0x2

    if-ne p1, v0, :cond_1

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-nez p1, :cond_0

    goto :goto_0

    :cond_0
    const-string p1, ""

    const/4 p2, 0x0

    .line 690
    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    invoke-direct {p0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showRoomSetup(Ljava/util/List;)V

    :cond_1
    :goto_0
    return-void
.end method

.method synthetic lambda$createVerifiedRoom$50$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationOnlineGame;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 719
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "create"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    invoke-virtual {p1, v1}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->fields(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "capacity"

    invoke-virtual {v1, v2, p2}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    move-result-object p2

    const/4 v1, 0x0

    invoke-virtual {v0, p2, v1, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    .line 720
    iget-object p3, p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->itemId:Ljava/lang/String;

    invoke-static {p2, p3}, Lorg/emulationstation/frontend/netplay/StationRoomCreation;->confirmed(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result p3

    if-eqz p3, :cond_0

    const-string p3, "room"

    .line 721
    invoke-virtual {p2, p3}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p3

    invoke-virtual {p1, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    return-object p2

    .line 720
    :cond_0
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string p2, "A cria\u00e7\u00e3o da sala n\u00e3o foi confirmada. Reconecte para conferir."

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method synthetic lambda$createVerifiedRoom$51$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 3

    .line 0
    const/4 v0, 0x0

    .line 722
    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const-string v2, "Criar sala"

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const-string v1, ""

    iput-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    invoke-direct {p0, v1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    return-void
.end method

.method synthetic lambda$deliver$36$org-emulationstation-frontend-netplay-StationRoomsActivity(ILorg/json/JSONObject;)V
    .locals 1

    .line 534
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roster:Lorg/emulationstation/frontend/netplay/StationRoomRoster;

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomRoster;->observe(Lorg/json/JSONObject;)V

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paint(Lorg/json/JSONObject;)V

    invoke-direct {p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyPendingNavigation(Lorg/json/JSONObject;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$enterCodeDialog$93$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/widget/EditText;Landroid/widget/TextView;)V
    .locals 3

    .line 946
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    .line 948
    :try_start_0
    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez v1, :cond_5

    if-eqz v0, :cond_4

    .line 949
    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v1, :cond_4

    const-string v1, "room"

    .line 950
    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    if-nez v1, :cond_3

    .line 951
    invoke-virtual {p1}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->parse(Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationInvitationCode;

    move-result-object p1

    .line 952
    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->shortCode:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_1

    .line 953
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->supportsShortInvite(Lorg/json/JSONObject;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 954
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->shortCode:Ljava/lang/String;

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->joinCode(Ljava/lang/String;)V

    goto :goto_0

    .line 953
    :cond_0
    new-instance p1, Ljava/lang/IllegalArgumentException;

    const-string v0, "Os convites curtos ainda n\u00e3o est\u00e3o dispon\u00edveis nesta sess\u00e3o."

    invoke-direct {p1, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 956
    :cond_1
    iget-object v1, p1, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->instance:Ljava/lang/String;

    const-string v2, "instance"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    .line 957
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    iget-object v0, p1, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->roomId:Ljava/lang/String;

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->itemId:Ljava/lang/String;

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->join(Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_0

    .line 956
    :cond_2
    new-instance p1, Ljava/lang/IllegalArgumentException;

    const-string v0, "Este c\u00f3digo expirou ap\u00f3s a atualiza\u00e7\u00e3o das salas. Pe\u00e7a um novo convite."

    invoke-direct {p1, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 950
    :cond_3
    new-instance p1, Ljava/lang/IllegalArgumentException;

    const-string v0, "Saia da sala atual antes de usar outro c\u00f3digo."

    invoke-direct {p1, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 949
    :cond_4
    new-instance p1, Ljava/lang/IllegalArgumentException;

    const-string v0, "Conecte-se ao lobby antes de entrar."

    invoke-direct {p1, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 948
    :cond_5
    new-instance p1, Ljava/lang/IllegalArgumentException;

    const-string v0, "Aguarde a a\u00e7\u00e3o atual terminar."

    invoke-direct {p1, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1
    :try_end_0
    .catch Ljava/lang/IllegalArgumentException; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    move-exception p1

    .line 959
    invoke-virtual {p1}, Ljava/lang/IllegalArgumentException;->getMessage()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/4 p1, 0x0

    invoke-virtual {p2, p1}, Landroid/widget/TextView;->setVisibility(I)V

    :goto_0
    return-void
.end method

.method synthetic lambda$enterCodeDialog$94$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 961
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    return-void
.end method

.method synthetic lambda$failure$37$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/Throwable;)V
    .locals 4

    .line 544
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_5

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_5

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createSetup:Landroid/widget/LinearLayout;

    if-eqz p1, :cond_0

    invoke-virtual {p1}, Landroid/widget/LinearLayout;->getVisibility()I

    move-result p1

    if-nez p1, :cond_0

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    :cond_0
    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    const/4 v0, 0x1

    const/4 v1, 0x0

    if-eqz p1, :cond_1

    iput-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    invoke-virtual {p1, v0}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const-string v2, "Criar sala"

    invoke-virtual {p1, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    invoke-static {p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    :cond_1
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    invoke-static {p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p1, v2}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->fail(Ljava/lang/String;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v3}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v3

    invoke-virtual {v2, v3, v1}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->text(Lorg/json/JSONObject;Z)Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->onlineNotice(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p1, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    if-nez p1, :cond_2

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->unavailableLobby()V

    :cond_2
    iput-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateStartState()V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->retry:Landroid/widget/Button;

    invoke-virtual {p1, v0}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v2}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v2

    if-eqz v2, :cond_3

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v2

    if-nez v2, :cond_3

    iget-boolean v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez v2, :cond_3

    goto :goto_0

    :cond_3
    move v0, v1

    :goto_0
    invoke-virtual {p1, v0}, Landroid/widget/Button;->setEnabled(Z)V

    invoke-static {p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_4

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderConversation(Lorg/json/JSONObject;)V

    :cond_4
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    :cond_5
    return-void
.end method

.method synthetic lambda$invitePlayer$85$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationPlayerModel;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 4
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 895
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    iget-object p2, p2, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->name:Ljava/lang/String;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-static {v0, p1, p2, v1}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->read(Lorg/json/JSONObject;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationPlayerModel;

    move-result-object p2

    .line 896
    iget-boolean v1, p2, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->canInvite:Z

    if-eqz v1, :cond_2

    const-string p2, "room"

    .line 897
    invoke-virtual {v0, p2}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const/4 v2, 0x0

    if-nez v1, :cond_0

    .line 898
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-static {p0, v1, v3, v0, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    const-string v3, "create"

    invoke-static {v3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v3

    invoke-virtual {v1, v3}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->fields(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object v1

    invoke-virtual {v0, v1, v2, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object v0

    invoke-direct {p0, v0, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V

    invoke-virtual {v0, p2}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    :cond_0
    if-eqz v1, :cond_1

    .line 900
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string p3, "invite"

    invoke-static {p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p3

    const-string v0, "roomId"

    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p3, v0, v1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p3

    const-string v0, "peerId"

    invoke-virtual {p3, v0, p1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p1

    invoke-virtual {p2, p1, v2, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1

    .line 899
    :cond_1
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Missing created room"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 896
    :cond_2
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    iget-object p2, p2, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->reason:Ljava/lang/String;

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method synthetic lambda$invitePlayer$86$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationPlayerModel;)V
    .locals 3

    .line 0
    const-string v0, "Convite enviado. O jogador tem 60 segundos para aceitar."

    .line 901
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "Convite enviado para "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->name:Ljava/lang/String;

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p1, "."

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void
.end method

.method synthetic lambda$join$52$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Lorg/json/JSONObject;)V
    .locals 7

    .line 0
    const/4 v3, 0x0

    const-string v0, "generation"

    .line 727
    invoke-virtual {p3, v0}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v4

    const-string v0, "profileId"

    invoke-virtual {p3, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    invoke-direct/range {v0 .. v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->joinConfirmed(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;)V

    return-void
.end method

.method synthetic lambda$join$53$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lorg/json/JSONObject;)V
    .locals 8

    .line 0
    const-string v0, "generation"

    .line 731
    invoke-virtual {p4, v0}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v5

    const-string v0, "profileId"

    invoke-virtual {p4, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v7

    move-object v1, p0

    move-object v2, p1

    move-object v3, p2

    move-object v4, p3

    invoke-direct/range {v1 .. v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->joinConfirmed(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;)V

    return-void
.end method

.method synthetic lambda$joinCode$95$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;)V
    .locals 1

    .line 978
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p1, :cond_0

    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v0, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    :cond_0
    return-void
.end method

.method synthetic lambda$joinCode$96$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 5
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 972
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->room()Lorg/json/JSONObject;

    move-result-object v0

    if-nez v0, :cond_1

    .line 973
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "resolve-code"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "inviteCode"

    invoke-virtual {v1, v2, p1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p1

    const/4 v1, 0x0

    invoke-virtual {v0, p1, v1, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    const-string v0, "resolvedRoom"

    .line 974
    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    const-string v2, "roomId"

    .line 975
    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    const-string v4, "itemId"

    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v4, "instance"

    .line 977
    invoke-virtual {p1, v4}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-static {v4, v3, v0}, Lorg/emulationstation/frontend/netplay/StationInvitationCode;->encode(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    .line 978
    new-instance v4, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda0;

    invoke-direct {v4, p0, p2, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda0;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;)V

    invoke-virtual {p0, v4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 979
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-static {p0, p2, v0, p1, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    move-result-object p1

    .line 980
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v0, "join"

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    invoke-virtual {v0, v2, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v0

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->fields(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object v0

    invoke-virtual {p2, v0, v1, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    const-string p3, "room"

    .line 981
    invoke-virtual {p2, p3}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p3

    if-eqz p3, :cond_0

    .line 982
    invoke-virtual {p3, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    const-string v0, "selfId"

    invoke-virtual {p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {p3, v0}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->member(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 983
    invoke-virtual {p1, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    return-object p2

    .line 982
    :cond_0
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Room join not acknowledged"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 972
    :cond_1
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string p2, "Saia da sala atual antes de usar outro convite."

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method synthetic lambda$joinCode$97$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 984
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->dismiss()V

    :cond_0
    const-string v0, ""

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    const/4 v0, 0x0

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    return-void
.end method

.method synthetic lambda$joinConfirmed$54$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 737
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v3

    move-object v0, p0

    move-object v2, p1

    move-object v4, p8

    move-object v5, p2

    invoke-static/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    move-result-object p1

    .line 738
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v0, p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayerRoom(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    if-eqz v0, :cond_5

    const-string v1, "generation"

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v2

    cmp-long v2, v2, p4

    if-nez v2, :cond_5

    const-string v2, "profileId"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {p2, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-eqz p2, :cond_5

    invoke-virtual {p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    .line 739
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p2}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p2

    const/4 v0, 0x0

    const-string v2, "room"

    if-nez p2, :cond_0

    move-object v3, v0

    goto :goto_0

    :cond_0
    invoke-virtual {p2, v2}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v3

    :goto_0
    const/4 v4, 0x0

    const-string v5, "roomId"

    if-eqz v3, :cond_3

    if-eqz p6, :cond_2

    .line 741
    invoke-virtual {v3, v5}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {p6, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_2

    invoke-static {p2}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->soloWaitingRoom(Lorg/json/JSONObject;)Z

    move-result p2

    if-eqz p2, :cond_2

    .line 743
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v3, "leave"

    invoke-static {v3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v3

    invoke-virtual {v3, v5, p6}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p6

    invoke-virtual {p2, p6, v4, p8}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    .line 744
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    invoke-direct {p0, p2, p7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V

    .line 745
    invoke-virtual {p2, v2}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p2

    if-nez p2, :cond_1

    goto :goto_1

    :cond_1
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Room leave not acknowledged"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 742
    :cond_2
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string p2, "Sua sala mudou. Atualize a lista antes de entrar em outra."

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1

    .line 747
    :cond_3
    :goto_1
    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string p6, "join"

    invoke-static {p6}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p6

    invoke-virtual {p6, v5, p3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p6

    invoke-virtual {p6, v1, p4, p5}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;

    move-result-object p4

    invoke-virtual {p1, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->fields(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object p4

    invoke-virtual {p2, p4, v4, p8}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p2

    .line 748
    invoke-virtual {p2, v2}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p4

    if-eqz p4, :cond_4

    .line 749
    invoke-virtual {p4, v5}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p5

    invoke-virtual {p3, p5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p3

    if-eqz p3, :cond_4

    const-string p3, "selfId"

    invoke-virtual {p2, p3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p3

    invoke-static {p4, p3}, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->member(Lorg/json/JSONObject;Ljava/lang/String;)Z

    move-result p3

    if-eqz p3, :cond_4

    .line 751
    invoke-virtual {p1, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    return-object p2

    .line 750
    :cond_4
    new-instance p1, Ljava/io/IOException;

    const-string p2, "Room join not acknowledged"

    invoke-direct {p1, p2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 738
    :cond_5
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string p2, "A sala mudou. Confira novamente as vagas e o modo."

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method synthetic lambda$joinConfirmed$55$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 752
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->dismiss()V

    :cond_0
    return-void
.end method

.method synthetic lambda$joinPlayer$87$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationPlayerModel;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 906
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "request-join"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "roomId"

    iget-object p1, p1, Lorg/emulationstation/frontend/netplay/StationPlayerModel;->joinRoomId:Ljava/lang/String;

    invoke-virtual {v1, v2, p1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p1

    const/4 v1, 0x0

    invoke-virtual {v0, p1, v1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$joinPlayer$88$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const-string v0, "Pedido enviado. Aguarde o convite do anfitri\u00e3o."

    .line 906
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerFeedback:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->refreshPlayerSheet()V

    return-void
.end method

.method synthetic lambda$launch$110$org-emulationstation-frontend-netplay-StationRoomsActivity(ILorg/json/JSONObject;ZZZLjava/lang/String;)V
    .locals 18

    .line 0
    move-object/from16 v1, p0

    move/from16 v2, p1

    move-object/from16 v3, p2

    move/from16 v4, p3

    move/from16 v5, p4

    move/from16 v6, p5

    move-object/from16 v7, p6

    const-string v8, "station-stream.v3"

    const-string v9, "generation"

    const-string v10, "station-stream.v2"

    const-string v11, "roomId"

    const-string v12, "recoveryProtocol"

    .line 1095
    iget-boolean v0, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_9

    iget v0, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v2, v0, :cond_9

    const/4 v0, 0x1

    iput-boolean v0, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    const-string v13, "relay-wss-v2"

    const-string v14, "transport"

    invoke-virtual {v3, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v15

    invoke-virtual {v13, v15}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v13

    if-nez v13, :cond_1

    const-string v13, "relay-wss-v3"

    invoke-virtual {v3, v14}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v13, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v13

    if-eqz v13, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    :cond_1
    :goto_0
    iput-boolean v0, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningRecovery:Z

    const/16 v16, 0x0

    :try_start_0
    new-instance v0, Landroid/content/Intent;

    if-eqz v4, :cond_2

    const-class v17, Lorg/emulationstation/frontend/netplay/StationN64Activity;

    :goto_1
    move-object/from16 v15, v17

    goto :goto_2

    :cond_2
    if-eqz v5, :cond_3

    const-class v17, Lorg/emulationstation/frontend/netplay/StationDolphinActivity;

    goto :goto_1

    :cond_3
    if-eqz v6, :cond_4

    const-class v17, Lorg/emulationstation/frontend/netplay/StationPsxOnlineActivity;

    goto :goto_1

    :cond_4
    const-class v17, Lorg/emulationstation/frontend/netplay/StationRetroActivity;

    goto :goto_1

    :goto_2
    invoke-direct {v0, v1, v15}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const-string v15, "station.launch"

    invoke-virtual {v0, v15, v7}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v0

    invoke-static {v1, v3, v0}, Lorg/emulationstation/frontend/netplay/StationGameSession;->attach(Landroid/content/Context;Lorg/json/JSONObject;Landroid/content/Intent;)Landroid/content/Intent;

    move-result-object v15
    :try_end_0
    .catch Ljava/lang/RuntimeException; {:try_start_0 .. :try_end_0} :catch_1

    :try_start_1
    const-string v0, "StationRooms"

    const-string v13, "launch stage=activity"

    invoke-static {v0, v13}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    iget-object v0, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    invoke-virtual {v3, v11}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v13

    invoke-virtual {v3, v12}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v10, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    if-nez v14, :cond_6

    invoke-virtual {v3, v12}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v8, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    if-eqz v14, :cond_5

    goto :goto_3

    :cond_5
    const-wide/16 v4, 0x0

    goto :goto_4

    :cond_6
    :goto_3
    const-wide/16 v4, -0x1

    invoke-virtual {v3, v9, v4, v5}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v16

    move-wide/from16 v4, v16

    :goto_4
    invoke-virtual {v0, v15, v13, v4, v5}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;->prepare(Landroid/content/Intent;Ljava/lang/String;J)I

    move-result v0

    invoke-virtual {v1, v15, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->startActivityForResult(Landroid/content/Intent;I)V
    :try_end_1
    .catch Ljava/lang/RuntimeException; {:try_start_1 .. :try_end_1} :catch_0

    goto :goto_8

    :catch_0
    move-exception v0

    goto :goto_5

    :catch_1
    move-exception v0

    move-object/from16 v15, v16

    :goto_5
    invoke-virtual {v3, v11}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v3, v12}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v10, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-nez v5, :cond_8

    invoke-virtual {v3, v12}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v8, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_7

    goto :goto_6

    :cond_7
    const-wide/16 v13, 0x0

    goto :goto_7

    :cond_8
    :goto_6
    const-wide/16 v10, -0x1

    invoke-virtual {v3, v9, v10, v11}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v13

    :goto_7
    invoke-static {v15, v4, v13, v14}, Lorg/emulationstation/frontend/netplay/StationGameSession;->discardLaunch(Landroid/content/Intent;Ljava/lang/String;J)V

    iget-object v3, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    invoke-virtual {v3, v15}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;->abort(Landroid/content/Intent;)V

    const/4 v3, 0x0

    iput-boolean v3, v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    move/from16 v3, p3

    move/from16 v4, p4

    invoke-direct {v1, v3, v4, v6, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->discardPreparedLaunch(ZZZLjava/lang/String;)V

    invoke-direct {v1, v0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchFailure(Ljava/lang/Throwable;I)V

    goto :goto_8

    :cond_9
    move v3, v4

    move v4, v5

    invoke-direct {v1, v3, v4, v6, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->discardPreparedLaunch(ZZZLjava/lang/String;)V

    :goto_8
    return-void
.end method

.method synthetic lambda$launch$111$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;I)V
    .locals 21

    .line 0
    move-object/from16 v9, p0

    move-object/from16 v0, p1

    move-object/from16 v1, p2

    move-object/from16 v10, p3

    const-string v2, "linkId"

    const-string v3, "ticket"

    const-string v4, "transport"

    .line 1080
    :try_start_0
    iget-object v5, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    if-nez v5, :cond_0

    iget-object v5, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v6, "itemId"

    invoke-virtual {v0, v6}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-static {v9, v5, v6, v1, v10}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    move-result-object v5

    :cond_0
    const-string v6, "station-stream.v3"

    const-string v7, "recoveryProtocol"

    .line 1081
    invoke-virtual {v0, v7}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v7

    invoke-virtual {v6, v7}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v6
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_1
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    const-string v7, "room"

    const/4 v8, 0x0

    const-string v11, "roomId"

    const-string v12, "generation"

    if-eqz v6, :cond_5

    .line 1082
    :try_start_1
    invoke-virtual {v5, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    const-string v4, "links"

    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->getJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v4

    new-instance v6, Lorg/json/JSONArray;

    invoke-direct {v6}, Lorg/json/JSONArray;-><init>()V

    const-string v13, "selfId"

    invoke-virtual {v1, v13}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v13

    const-string v14, "hostId"

    invoke-virtual {v0, v14}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v13, v14}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    .line 1083
    :goto_0
    invoke-virtual {v4}, Lorg/json/JSONArray;->length()I

    move-result v15

    if-ge v8, v15, :cond_4

    invoke-virtual {v4, v8}, Lorg/json/JSONArray;->getJSONObject(I)Lorg/json/JSONObject;

    move-result-object v15
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    if-nez v14, :cond_1

    move-object/from16 v16, v4

    :try_start_2
    const-string v4, "guestPeerId"

    invoke-virtual {v15, v4}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v13, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v4
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_1
    .catchall {:try_start_2 .. :try_end_2} :catchall_1

    if-nez v4, :cond_2

    move-object/from16 v17, v13

    move/from16 v18, v14

    move v14, v8

    goto :goto_1

    :cond_1
    move-object/from16 v16, v4

    .line 1084
    :cond_2
    :try_start_3
    iget-object v4, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    move-object/from16 v17, v13

    invoke-static {v3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v13

    invoke-virtual {v5, v13}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->fields(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object v13

    move/from16 v18, v14

    invoke-virtual {v0, v11}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v13, v11, v14}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v13

    move v14, v8

    invoke-virtual {v0, v12}, Lorg/json/JSONObject;->getLong(Ljava/lang/String;)J

    move-result-wide v8

    invoke-virtual {v13, v12, v8, v9}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;

    move-result-object v8

    invoke-virtual {v15, v2}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v9

    invoke-virtual {v8, v2, v9}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v8

    invoke-virtual {v4, v8, v10}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->multiplayer(Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object v4

    .line 1085
    invoke-virtual {v4, v7}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v8

    invoke-virtual {v5, v8}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    invoke-virtual {v8, v12}, Lorg/json/JSONObject;->getLong(Ljava/lang/String;)J

    move-result-wide v8

    invoke-virtual {v0, v12}, Lorg/json/JSONObject;->getLong(Ljava/lang/String;)J

    move-result-wide v19

    cmp-long v8, v8, v19

    if-nez v8, :cond_3

    .line 1086
    invoke-virtual {v4, v3}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v4

    invoke-virtual {v15, v2}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v8

    invoke-static {v4, v8}, Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;->checkTicket(Lorg/json/JSONObject;Ljava/lang/String;)V

    .line 1087
    new-instance v8, Lorg/json/JSONObject;

    invoke-virtual {v15}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v9

    invoke-direct {v8, v9}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v4

    invoke-virtual {v6, v4}, Lorg/json/JSONArray;->put(Ljava/lang/Object;)Lorg/json/JSONArray;

    :goto_1
    add-int/lit8 v8, v14, 0x1

    move-object/from16 v9, p0

    move-object/from16 v4, v16

    move-object/from16 v13, v17

    move/from16 v14, v18

    goto/16 :goto_0

    .line 1085
    :cond_3
    new-instance v0, Ljava/io/IOException;

    const-string v1, "Generation changed"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 1089
    :cond_4
    new-instance v2, Lorg/json/JSONObject;

    invoke-virtual/range {p1 .. p1}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-direct {v2, v3}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    const-string v3, "launchLinks"

    invoke-virtual {v2, v3, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v2

    move-object/from16 v9, p0

    goto :goto_3

    :cond_5
    const-string v2, "relay-wss-v1"

    .line 1090
    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2
    :try_end_3
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_0
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    const-string v3, "relay-wss-v2"

    if-nez v2, :cond_7

    :try_start_4
    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v3, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_6

    goto :goto_2

    :cond_6
    move-object/from16 v9, p0

    move-object v2, v0

    goto :goto_3

    :cond_7
    :goto_2
    const-string v2, "relay-ticket"

    invoke-static {v2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v2

    invoke-virtual {v0, v11}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v2, v11, v6}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v2

    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_8

    invoke-virtual {v5, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->fields(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object v3

    invoke-virtual {v0, v12}, Lorg/json/JSONObject;->getLong(Ljava/lang/String;)J

    move-result-wide v13

    invoke-virtual {v3, v12, v13, v14}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;
    :try_end_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_0
    .catchall {:try_start_4 .. :try_end_4} :catchall_0

    :cond_8
    move-object/from16 v9, p0

    :try_start_5
    iget-object v3, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-virtual {v3, v2, v8, v10}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object v2

    invoke-virtual {v2, v7}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v2

    const-string v3, "StationRooms"

    const-string v4, "launch stage=relay-ticket-received"

    invoke-static {v3, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 1091
    :goto_3
    invoke-virtual {v5, v2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->verifyRoom(Lorg/json/JSONObject;)V

    const-string v3, "mupen64plus-ae-station-v1"

    iget-object v4, v5, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->backend:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v6

    const-string v3, "dolphin-station-v1"

    iget-object v4, v5, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->backend:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v7

    const-string v3, "psx-player-station-v1"

    iget-object v4, v5, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->backend:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v8

    const-string v3, "n64"

    .line 1092
    iget-object v4, v5, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->platform:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_a

    if-eqz v6, :cond_9

    goto :goto_4

    :cond_9
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string v1, "Esta sala usa uma edi\u00e7\u00e3o anterior. Atualize os participantes e crie uma nova sala para usar o emulador Nintendo 64 do aplicativo."

    invoke-direct {v0, v1}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_a
    :goto_4
    const-string v3, "gamecube"

    .line 1093
    iget-object v4, v5, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->platform:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-nez v3, :cond_b

    const-string v3, "wii"

    iget-object v4, v5, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->platform:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_c

    :cond_b
    if-eqz v7, :cond_10

    :cond_c
    if-eqz v6, :cond_d

    .line 1094
    invoke-static {v9, v5, v2, v1, v10}, Lorg/emulationstation/frontend/netplay/StationN64Launch;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;

    move-result-object v1

    :goto_5
    move-object v11, v1

    goto :goto_6

    :cond_d
    if-eqz v7, :cond_e

    invoke-static {v9, v5, v2, v1, v10}, Lorg/emulationstation/frontend/netplay/StationDolphinLaunch;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;

    move-result-object v1

    goto :goto_5

    :cond_e
    if-eqz v8, :cond_f

    invoke-static {v9, v5, v2, v1, v10}, Lorg/emulationstation/frontend/netplay/StationPsxLaunch;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;

    move-result-object v1

    goto :goto_5

    :cond_f
    invoke-static {v9, v5, v2, v1, v10}, Lorg/emulationstation/frontend/netplay/StationRetroLaunch;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;

    move-result-object v1

    goto :goto_5

    .line 1095
    :goto_6
    new-instance v12, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda68;

    move-object v1, v12

    move-object/from16 v2, p0

    move/from16 v3, p4

    move-object/from16 v4, p1

    move v5, v6

    move v6, v7

    move v7, v8

    move-object v8, v11

    invoke-direct/range {v1 .. v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda68;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILorg/json/JSONObject;ZZZLjava/lang/String;)V

    invoke-virtual {v9, v12}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    goto :goto_8

    .line 1093
    :cond_10
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string v1, "Atualize os participantes e crie uma nova sala para usar o Dolphin do aplicativo."

    invoke-direct {v0, v1}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_5
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_5} :catch_1
    .catchall {:try_start_5 .. :try_end_5} :catchall_1

    :catchall_0
    move-exception v0

    move-object/from16 v9, p0

    goto :goto_9

    :catch_0
    move-exception v0

    move-object/from16 v9, p0

    goto :goto_7

    :catchall_1
    move-exception v0

    goto :goto_9

    :catch_1
    move-exception v0

    :goto_7
    move/from16 v1, p4

    .line 1095
    :try_start_6
    invoke-direct {v9, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchFailure(Ljava/lang/Throwable;I)V
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_1

    :goto_8
    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v10}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    return-void

    :goto_9
    iget-object v1, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v1, v10}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    throw v0
.end method

.method synthetic lambda$launchFailure$112$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/Throwable;)V
    .locals 1

    .line 1100
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_0

    const/4 p1, 0x0

    iput-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    iput-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->feedback:Lorg/emulationstation/frontend/netplay/StationRoomFeedback;

    invoke-static {p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomFeedback;->fail(Ljava/lang/String;)V

    const-wide/16 p1, -0x1

    iput-wide p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->painted:J

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p1, :cond_0

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->paint(Lorg/json/JSONObject;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$loadHero$100$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;Lorg/emulationstation/frontend/netplay/StationHeaderMetadata;)V
    .locals 1

    .line 1016
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    iget p2, p3, Lorg/emulationstation/frontend/netplay/StationHeaderMetadata;->rating:I

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationGameRatingView;->setRating(I)V

    :cond_0
    return-void
.end method

.method synthetic lambda$loadHero$101$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;I)V
    .locals 9

    .line 1010
    :try_start_0
    invoke-static {p0}, Lorg/emulationstation/frontend/station/StationAndroid;->get(Landroid/content/Context;)Lorg/emulationstation/frontend/station/StationAndroid;

    move-result-object v0

    iget-object v0, v0, Lorg/emulationstation/frontend/station/StationAndroid;->coordinator:Lorg/emulationstation/frontend/station/StationCoordinator;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationCoordinator;->current()Lorg/emulationstation/frontend/station/StationCoordinator$Library;

    move-result-object v0

    if-nez v0, :cond_0

    const/4 v0, 0x0

    goto :goto_0

    :cond_0
    iget-object v0, v0, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;

    invoke-virtual {v0, p1}, Lorg/emulationstation/frontend/station/StationCatalog;->find(Ljava/lang/String;)Lorg/emulationstation/frontend/station/StationCatalog$Item;

    move-result-object v0

    :goto_0
    if-nez v0, :cond_1

    return-void

    .line 1011
    :cond_1
    iget-object v5, v0, Lorg/emulationstation/frontend/station/StationCatalog$Item;->name:Ljava/lang/String;

    iget-object v6, v0, Lorg/emulationstation/frontend/station/StationCatalog$Item;->platform:Ljava/lang/String;

    .line 1012
    invoke-static {v0}, Lorg/emulationstation/frontend/station/StationGamePlayerFacts;->forItem(Lorg/emulationstation/frontend/station/StationCatalog$Item;)Lorg/emulationstation/frontend/station/StationGamePlayerFacts$Fact;

    move-result-object v7

    .line 1013
    new-instance v8, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda107;

    move-object v1, v8

    move-object v2, p0

    move v3, p2

    move-object v4, p1

    invoke-direct/range {v1 .. v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda107;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationGamePlayerFacts$Fact;)V

    invoke-virtual {p0, v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 1014
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerMetadata:Lorg/json/JSONObject;

    if-nez v1, :cond_3

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getAssets()Landroid/content/res/AssetManager;

    move-result-object v1

    const-string v2, "station-ui-r43/game-metadata.json"

    invoke-virtual {v1, v2}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object v1
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    :try_start_1
    new-instance v2, Lorg/json/JSONObject;

    new-instance v3, Ljava/lang/String;

    const/high16 v4, 0x80000

    invoke-static {v1, v4}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->read(Ljava/io/InputStream;I)[B

    move-result-object v4

    sget-object v5, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v3, v4, v5}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V

    invoke-direct {v2, v3}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    iput-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerMetadata:Lorg/json/JSONObject;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    if-eqz v1, :cond_3

    :try_start_2
    invoke-virtual {v1}, Ljava/io/InputStream;->close()V
    :try_end_2
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_0

    goto :goto_2

    :catchall_0
    move-exception p1

    if-eqz v1, :cond_2

    :try_start_3
    invoke-virtual {v1}, Ljava/io/InputStream;->close()V
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

    .line 1015
    :cond_3
    :goto_2
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerMetadata:Lorg/json/JSONObject;

    iget-object v2, v0, Lorg/emulationstation/frontend/station/StationCatalog$Item;->itemId:Ljava/lang/String;

    iget-object v0, v0, Lorg/emulationstation/frontend/station/StationCatalog$Item;->players:Ljava/lang/String;

    invoke-static {v1, v2, v0}, Lorg/emulationstation/frontend/netplay/StationHeaderMetadata;->lookup(Lorg/json/JSONObject;Ljava/lang/String;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationHeaderMetadata;

    move-result-object v0

    .line 1016
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda108;

    invoke-direct {v1, p0, p2, p1, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda108;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;Lorg/emulationstation/frontend/netplay/StationHeaderMetadata;)V

    invoke-virtual {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_0

    goto :goto_3

    :catch_0
    const-string p1, "StationOnline"

    const-string p2, "Selected game metadata unavailable"

    .line 1017
    invoke-static {p1, p2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    :goto_3
    return-void
.end method

.method synthetic lambda$loadHero$98$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;Landroid/graphics/Bitmap;)V
    .locals 1

    .line 1007
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_1

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_1

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_1

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->isDestroyed()Z

    move-result p1

    if-nez p1, :cond_1

    iput-object p3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroBitmap:Landroid/graphics/Bitmap;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->bindHeroCover()V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroSymbol:Lorg/emulationstation/frontend/netplay/StationLobbyIcon;

    if-nez p3, :cond_0

    const/4 p2, 0x0

    goto :goto_0

    :cond_0
    const/16 p2, 0x8

    :goto_0
    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationLobbyIcon;->setVisibility(I)V

    :cond_1
    return-void
.end method

.method synthetic lambda$loadHero$99$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationGamePlayerFacts$Fact;)V
    .locals 1

    .line 1013
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_2

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_2

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->subtitle:Landroid/widget/TextView;

    invoke-virtual {p1, p3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->gamePlatform:Landroid/widget/TextView;

    invoke-virtual {p1, p4}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const-string p1, ""

    if-nez p5, :cond_0

    move-object p2, p1

    goto :goto_0

    :cond_0
    iget-object p2, p5, Lorg/emulationstation/frontend/station/StationGamePlayerFacts$Fact;->summary:Ljava/lang/String;

    :goto_0
    iput-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactSummary:Ljava/lang/String;

    if-nez p5, :cond_1

    goto :goto_1

    :cond_1
    iget-object p1, p5, Lorg/emulationstation/frontend/station/StationGamePlayerFacts$Fact;->detail:Ljava/lang/String;

    :goto_1
    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroFactDetail:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderHeroPlayerInfo()V

    :cond_2
    return-void
.end method

.method synthetic lambda$loadHeroProfile$102$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 1037
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_0

    iput-object p3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlinePlayers:Ljava/lang/String;

    iput-object p4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlineDetail:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderHeroPlayerInfo()V

    :cond_0
    return-void
.end method

.method synthetic lambda$loadHeroProfile$103$org-emulationstation-frontend-netplay-StationRoomsActivity(ILjava/lang/String;Ljava/lang/Exception;)V
    .locals 1

    .line 1038
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne p1, v0, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroRequestId:Ljava/lang/String;

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_0

    invoke-static {p3}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->heroOnlineDetail:Ljava/lang/String;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderHeroPlayerInfo()V

    :cond_0
    return-void
.end method

.method synthetic lambda$loadHeroProfile$104$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;I)V
    .locals 11

    .line 1031
    new-instance v0, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-direct {v0}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;-><init>()V

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v1, v0}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    .line 1033
    :try_start_0
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    invoke-static {p0, v1, p1, v0}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->classifications(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/util/List;

    move-result-object v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    new-instance v4, Ljava/util/TreeSet;

    invoke-direct {v4}, Ljava/util/TreeSet;-><init>()V

    .line 1034
    invoke-interface {v1}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v5

    :goto_0
    invoke-interface {v5}, Ljava/util/Iterator;->hasNext()Z

    move-result v6

    const/4 v7, 0x0

    const/4 v8, 0x1

    if-eqz v6, :cond_3

    invoke-interface {v5}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v6

    check-cast v6, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    invoke-static {v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->profileInfo(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v9

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->length()I

    move-result v10

    if-lez v10, :cond_0

    const-string v10, "\n"

    invoke-virtual {v3, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    :cond_0
    iget-boolean v10, v9, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->singlePlayerConfirmed:Z

    if-eqz v10, :cond_1

    invoke-static {v8}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v8

    invoke-interface {v4, v8}, Ljava/util/SortedSet;->add(Ljava/lang/Object;)Z

    :cond_1
    iget-object v6, v6, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->allowed:[I

    array-length v8, v6

    :goto_1
    if-ge v7, v8, :cond_2

    aget v10, v6, v7

    invoke-static {v10}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v10

    invoke-interface {v4, v10}, Ljava/util/SortedSet;->add(Ljava/lang/Object;)Z

    add-int/lit8 v7, v7, 0x1

    goto :goto_1

    :cond_2
    iget-object v6, v9, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->detail:Ljava/lang/String;

    invoke-virtual {v3, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    goto :goto_0

    .line 1035
    :cond_3
    invoke-virtual {v2, v7}, Ljava/lang/StringBuilder;->setLength(I)V

    invoke-interface {v4}, Ljava/util/SortedSet;->iterator()Ljava/util/Iterator;

    move-result-object v5

    :goto_2
    invoke-interface {v5}, Ljava/util/Iterator;->hasNext()Z

    move-result v6

    if-eqz v6, :cond_5

    invoke-interface {v5}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v6

    check-cast v6, Ljava/lang/Integer;

    invoke-virtual {v6}, Ljava/lang/Integer;->intValue()I

    move-result v6

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->length()I

    move-result v7

    if-lez v7, :cond_4

    const-string v7, ", "

    invoke-virtual {v2, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    :cond_4
    invoke-virtual {v2, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    goto :goto_2

    :cond_5
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->length()I

    move-result v5

    if-lez v5, :cond_8

    invoke-interface {v4}, Ljava/util/SortedSet;->size()I

    move-result v5

    if-ne v5, v8, :cond_6

    invoke-static {v8}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v5

    invoke-interface {v4, v5}, Ljava/util/SortedSet;->contains(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_6

    const-string v4, " jogador"

    goto :goto_3

    :cond_6
    const-string v4, " jogadores"

    :goto_3
    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-interface {v1}, Ljava/util/List;->size()I

    move-result v4

    if-le v4, v8, :cond_7

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, " \u00b7 "

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-interface {v1}, Ljava/util/List;->size()I

    move-result v1

    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v1, " modos"

    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    goto :goto_4

    :cond_7
    const-string v1, ""

    :goto_4
    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 1036
    :cond_8
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->length()I

    move-result v1

    if-nez v1, :cond_9

    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->pending()Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v1

    iget-object v1, v1, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->capacityLabel:Ljava/lang/String;

    goto :goto_5

    :cond_9
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    :goto_5
    move-object v8, v1

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->length()I

    move-result v1

    if-nez v1, :cond_a

    invoke-static {}, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->pending()Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;

    move-result-object v1

    iget-object v1, v1, Lorg/emulationstation/frontend/netplay/StationGamePlayerInfo;->detail:Ljava/lang/String;

    goto :goto_6

    :cond_a
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    :goto_6
    move-object v9, v1

    .line 1037
    new-instance v1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda105;

    move-object v4, v1

    move-object v5, p0

    move v6, p2

    move-object v7, p1

    invoke-direct/range {v4 .. v9}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda105;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {p0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_7

    :catchall_0
    move-exception p1

    goto :goto_8

    :catch_0
    move-exception v1

    .line 1038
    :try_start_1
    invoke-virtual {v0}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancelled()Z

    move-result v2

    if-nez v2, :cond_b

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->recordFailure(Ljava/lang/Throwable;)V

    :cond_b
    new-instance v2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda106;

    invoke-direct {v2, p0, p2, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda106;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILjava/lang/String;Ljava/lang/Exception;)V

    invoke-virtual {p0, v2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 1039
    :goto_7
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p1, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    return-void

    :goto_8
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {p2, v0}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    throw p1
.end method

.method synthetic lambda$ownRoomGuide$21$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;Landroid/view/View;)V
    .locals 0

    .line 0
    const-string p2, "itemId"

    .line 351
    invoke-virtual {p1, p2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$ownRoomGuide$22$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;Landroid/view/View;)V
    .locals 0

    .line 0
    const-string p2, "itemId"

    .line 354
    invoke-virtual {p1, p2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$pagePeers$105$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 1053
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "heartbeat"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2, p1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$pagePeers$106$org-emulationstation-frontend-netplay-StationRoomsActivity(ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 1053
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda59;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda59;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct {p0, v0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->readPoll(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$pageRooms$107$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 1057
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "heartbeat"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2, p1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$pageRooms$108$org-emulationstation-frontend-netplay-StationRoomsActivity(ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 1057
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda88;

    invoke-direct {v0, p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda88;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;)V

    invoke-direct {p0, v0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->readPoll(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;ILorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$paint$59$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;)V
    .locals 2

    .line 0
    const-string v0, ""

    .line 792
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    const-string v0, "roomId"

    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    const-string v1, "itemId"

    invoke-virtual {p1, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->join(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$paint$60$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;)V
    .locals 2

    .line 0
    const-string v0, "inviteId"

    .line 792
    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const-string v0, "dismiss-invite"

    const-string v1, "text"

    invoke-direct {p0, v0, v1, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->command(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V

    return-void
.end method

.method synthetic lambda$paint$61$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;)V
    .locals 2

    .line 0
    const-string v0, "requestId"

    .line 793
    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const-string v0, "accept-request"

    const/4 v1, 0x0

    invoke-direct {p0, v0, v1, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->socialAction(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$paint$62$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;)V
    .locals 2

    .line 0
    const-string v0, "requestId"

    .line 793
    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const-string v0, "dismiss-request"

    const/4 v1, 0x0

    invoke-direct {p0, v0, v1, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->socialAction(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$paint$63$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;Landroid/view/View;)V
    .locals 0

    .line 0
    const-string p2, "itemId"

    .line 798
    invoke-virtual {p1, p2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomExplanation(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p2, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showGameDetails(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$paint$64$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONArray;Ljava/lang/String;)V
    .locals 1

    .line 807
    invoke-static {p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->contains(Lorg/json/JSONArray;Ljava/lang/String;)Z

    move-result p1

    xor-int/lit8 p1, p1, 0x1

    invoke-static {p1}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object p1

    const-string p2, "ready"

    const-string v0, "value"

    invoke-direct {p0, p2, v0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->command(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V

    return-void
.end method

.method synthetic lambda$paint$65$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;)V
    .locals 0

    .line 811
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->startRoom(Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$paint$66$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 2

    .line 0
    const-string v0, "leave"

    const/4 v1, 0x0

    .line 812
    invoke-direct {p0, v0, v1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->command(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;)V

    return-void
.end method

.method synthetic lambda$paint$67$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const-string v0, ""

    .line 814
    invoke-direct {p0, v0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->openConversation(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$paint$68$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 0

    .line 815
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showRoomCode()V

    return-void
.end method

.method synthetic lambda$paint$69$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;Lorg/json/JSONObject;)V
    .locals 1

    .line 0
    const-string v0, ""

    .line 816
    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launchKey:Ljava/lang/String;

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launch(Lorg/json/JSONObject;Lorg/json/JSONObject;)V

    return-void
.end method

.method synthetic lambda$paint$70$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 820
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "request-join"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "roomId"

    invoke-virtual {p1, v2}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v1, v2, p1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p1

    const/4 v1, 0x0

    invoke-virtual {v0, p1, v1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$paint$71$org-emulationstation-frontend-netplay-StationRoomsActivity(ZLorg/json/JSONObject;)V
    .locals 1

    .line 0
    if-eqz p1, :cond_0

    .line 820
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda52;

    invoke-direct {p1, p0, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda52;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;Lorg/json/JSONObject;)V

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->action(Lorg/emulationstation/frontend/netplay/StationRoomsActivity$Work;)V

    goto :goto_0

    :cond_0
    const-string p1, "roomId"

    invoke-virtual {p2, p1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const-string v0, "itemId"

    invoke-virtual {p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    invoke-direct {p0, p1, p2}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->join(Ljava/lang/String;Ljava/lang/String;)V

    :goto_0
    return-void
.end method

.method synthetic lambda$paint$72$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, -0x1

    .line 822
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pageRooms(I)V

    return-void
.end method

.method synthetic lambda$paint$73$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, 0x1

    .line 822
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pageRooms(I)V

    return-void
.end method

.method synthetic lambda$paint$74$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 2

    .line 825
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->peerScroll:Landroid/widget/ScrollView;

    const/4 v1, 0x0

    invoke-virtual {v0, v1, p1}, Landroid/widget/ScrollView;->scrollTo(II)V

    return-void
.end method

.method synthetic lambda$paint$75$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 2

    .line 825
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomScroll:Landroid/widget/ScrollView;

    const/4 v1, 0x0

    invoke-virtual {v0, v1, p1}, Landroid/widget/ScrollView;->scrollTo(II)V

    return-void
.end method

.method synthetic lambda$prepareRoom$48$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 705
    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v3

    iget-object v5, p2, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->profileId:Ljava/lang/String;

    move-object v0, p0

    move-object v2, p1

    move-object v4, p3

    invoke-static/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;Ljava/lang/String;)Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    move-result-object p1

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const/4 p2, 0x0

    invoke-virtual {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->compose(Lorg/json/JSONObject;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$prepareRoom$49$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;I)V
    .locals 3

    .line 0
    const/4 v0, 0x0

    .line 706
    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->choose:Landroid/widget/Button;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->create:Landroid/widget/Button;

    const-string v2, "Criar sala"

    invoke-virtual {v0, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 707
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->prepared:Lorg/emulationstation/frontend/netplay/StationOnlineGame;

    if-eqz v0, :cond_3

    .line 708
    iget-object v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    invoke-virtual {p1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomSetupContext()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    if-ne p1, p3, :cond_3

    iget p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    if-eq p1, p4, :cond_0

    goto :goto_1

    .line 709
    :cond_0
    iget-object p1, v0, Lorg/emulationstation/frontend/netplay/StationOnlineGame;->multiplayerProfile:Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;

    .line 710
    invoke-static {p3, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->sameRoomSetupProfile(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)Z

    move-result p2

    if-eqz p2, :cond_2

    invoke-virtual {p1, p4}, Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;->permits(I)Z

    move-result p1

    if-nez p1, :cond_1

    goto :goto_0

    .line 713
    :cond_1
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    invoke-direct {p0, v0, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->createVerifiedRoom(Lorg/emulationstation/frontend/netplay/StationOnlineGame;I)V

    return-void

    .line 711
    :cond_2
    :goto_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    const-string p1, "As op\u00e7\u00f5es desta partida foram atualizadas. Escolha novamente o modo e os jogadores."

    invoke-direct {p0, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    return-void

    .line 708
    :cond_3
    :goto_1
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomSetup()V

    const-string p1, "A sele\u00e7\u00e3o mudou. Confira novamente o jogo e os participantes."

    invoke-direct {p0, p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    return-void
.end method

.method synthetic lambda$refreshPlayerSheet$84$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationPlayerSheet;Ljava/lang/String;Landroid/graphics/Bitmap;)V
    .locals 1

    .line 887
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-ne p1, v0, :cond_0

    iget-object v0, p1, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->coverItem:Ljava/lang/String;

    invoke-virtual {p2, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-eqz p2, :cond_0

    invoke-virtual {p1, p3}, Lorg/emulationstation/frontend/netplay/StationPlayerSheet;->setCover(Landroid/graphics/Bitmap;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$renderConversation$77$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 2

    .line 836
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    iget-object v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationName:Ljava/lang/String;

    invoke-direct {p0, v0, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showPlayer(Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method synthetic lambda$renderConversation$78$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 2

    .line 843
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    const/16 v1, 0x82

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->fullScroll(I)Z

    return-void
.end method

.method synthetic lambda$renderConversation$79$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 2

    .line 843
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chatScroll:Landroid/widget/ScrollView;

    const/4 v1, 0x0

    invoke-virtual {v0, v1, p1}, Landroid/widget/ScrollView;->scrollTo(II)V

    return-void
.end method

.method synthetic lambda$renderPlayers$80$org-emulationstation-frontend-netplay-StationRoomsActivity(ZLjava/lang/String;Ljava/lang/String;Landroid/view/View;)V
    .locals 0

    .line 0
    if-nez p1, :cond_0

    .line 862
    invoke-direct {p0, p2, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->openConversation(Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_0

    :cond_0
    invoke-direct {p0, p2, p3}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showPlayer(Ljava/lang/String;Ljava/lang/String;)V

    :goto_0
    return-void
.end method

.method synthetic lambda$renderPlayers$81$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, -0x1

    .line 866
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pagePeers(I)V

    return-void
.end method

.method synthetic lambda$renderPlayers$82$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 0
    const/4 v0, 0x1

    .line 867
    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pagePeers(I)V

    return-void
.end method

.method synthetic lambda$roomCoverCard$19$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationCreateGameCard;Landroid/widget/LinearLayout;Landroid/view/View;IIIIIIII)V
    .locals 0

    .line 318
    iget-object p3, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomCard:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    if-ne p3, p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->ownRoomFooter:Landroid/widget/LinearLayout;

    if-ne p1, p2, :cond_0

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->updateOwnRoomHeight()V

    :cond_0
    return-void
.end method

.method synthetic lambda$roomCoverCard$20$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;Landroid/graphics/Bitmap;)V
    .locals 1

    .line 332
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomRows:Ljava/util/Map;

    invoke-interface {v0, p1}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    if-ne p1, p2, :cond_1

    const/4 p1, 0x0

    iput-boolean p1, p2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->loading:Z

    if-eqz p3, :cond_0

    const/4 p1, 0x1

    :cond_0
    iput-boolean p1, p2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->loaded:Z

    iget-object p1, p2, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$RoomRow;->display:Lorg/emulationstation/frontend/netplay/StationCreateGameCard;

    invoke-virtual {p1, p3}, Lorg/emulationstation/frontend/netplay/StationCreateGameCard;->setCover(Landroid/graphics/Bitmap;)V

    :cond_1
    return-void
.end method

.method synthetic lambda$scheduleMultiplayerPoll$33$org-emulationstation-frontend-netplay-StationRoomsActivity(ILorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Z)V
    .locals 1

    .line 528
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-ne p1, p2, :cond_0

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez p1, :cond_0

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->creating:Z

    if-nez p1, :cond_0

    invoke-direct {p0, p3, p4}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->showCreateMessage(Ljava/lang/String;Z)V

    if-eqz p4, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->status:Landroid/widget/TextView;

    invoke-virtual {p1, p3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_0
    return-void
.end method

.method synthetic lambda$scheduleMultiplayerPoll$34$org-emulationstation-frontend-netplay-StationRoomsActivity(JIILorg/emulationstation/frontend/netplay/StationOnlineClient;I)V
    .locals 6

    .line 0
    const-wide/16 v0, 0x0

    cmp-long v0, p1, v0

    if-ltz v0, :cond_0

    .line 531
    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, p3, :cond_0

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    if-ne p4, v0, :cond_0

    iget-object p4, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-ne p4, p5, :cond_0

    move-object v0, p0

    move-object v1, p5

    move v2, p3

    move v3, p6

    move-wide v4, p1

    invoke-direct/range {v0 .. v5}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->scheduleMultiplayerPoll(Lorg/emulationstation/frontend/netplay/StationOnlineClient;IIJ)V

    :cond_0
    return-void
.end method

.method synthetic lambda$scheduleMultiplayerPoll$35$org-emulationstation-frontend-netplay-StationRoomsActivity(IILorg/emulationstation/frontend/netplay/StationOnlineClient;I)V
    .locals 16

    .line 0
    move-object/from16 v9, p0

    move/from16 v7, p1

    move/from16 v8, p2

    move-object/from16 v10, p3

    .line 518
    iget-boolean v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_c

    iget v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, v7, :cond_c

    iget v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    if-ne v8, v0, :cond_c

    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq v0, v10, :cond_0

    goto/16 :goto_5

    .line 519
    :cond_0
    new-instance v11, Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    invoke-direct {v11}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;-><init>()V

    .line 520
    monitor-enter p0

    :try_start_0
    iget-boolean v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v0, :cond_b

    iget v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-ne v0, v7, :cond_b

    iget v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollEpoch:I

    if-ne v8, v0, :cond_b

    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    if-eq v0, v10, :cond_1

    goto/16 :goto_4

    :cond_1
    iput-object v11, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v11}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    monitor-exit p0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    const/4 v1, 0x0

    const/4 v12, 0x0

    .line 522
    :try_start_1
    invoke-virtual {v10, v11}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->pollMultiplayer(Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object v0

    invoke-direct {v9, v0, v7}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->deliver(Lorg/json/JSONObject;I)V
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 529
    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v11}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne v0, v11, :cond_2

    iput-object v12, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_2
    const-wide/16 v2, 0x3e8

    move v13, v1

    move-wide v3, v2

    goto :goto_1

    :catchall_0
    move-exception v0

    goto/16 :goto_3

    :catch_0
    move-exception v0

    .line 524
    :try_start_2
    invoke-virtual {v11}, Lorg/emulationstation/frontend/station/StationApi$Cancellation;->cancelled()Z

    move-result v2

    if-nez v2, :cond_8

    iget-boolean v2, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz v2, :cond_8

    iget v2, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    if-eq v2, v7, :cond_3

    goto :goto_2

    :cond_3
    const/4 v2, 0x1

    add-int/lit8 v13, p4, 0x1

    .line 525
    invoke-static {v0, v13}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->pollRetryDelay(Ljava/lang/Throwable;I)J

    move-result-wide v14

    const-wide/16 v3, 0x0

    if-eq v13, v2, :cond_4

    cmp-long v5, v14, v3

    if-gez v5, :cond_5

    .line 526
    :cond_4
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->recordFailure(Ljava/lang/Throwable;)V

    :cond_5
    cmp-long v3, v14, v3

    if-gez v3, :cond_6

    move v6, v2

    goto :goto_0

    :cond_6
    move v6, v1

    .line 527
    :goto_0
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->message(Ljava/lang/Throwable;)Ljava/lang/String;

    move-result-object v5

    .line 528
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda70;

    move-object v1, v0

    move-object/from16 v2, p0

    move/from16 v3, p1

    move-object/from16 v4, p3

    invoke-direct/range {v1 .. v6}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda70;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;ILorg/emulationstation/frontend/netplay/StationOnlineClient;Ljava/lang/String;Z)V

    invoke-virtual {v9, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 529
    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v11}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne v0, v11, :cond_7

    iput-object v12, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_7
    move-wide v3, v14

    .line 531
    :goto_1
    new-instance v0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda71;

    move-object v1, v0

    move-object/from16 v2, p0

    move/from16 v5, p1

    move/from16 v6, p2

    move-object/from16 v7, p3

    move v8, v13

    invoke-direct/range {v1 .. v8}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity$$ExternalSyntheticLambda71;-><init>(Lorg/emulationstation/frontend/netplay/StationRoomsActivity;JIILorg/emulationstation/frontend/netplay/StationOnlineClient;I)V

    invoke-virtual {v9, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void

    .line 529
    :cond_8
    :goto_2
    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v0, v11}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object v0, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne v0, v11, :cond_9

    iput-object v12, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_9
    return-void

    :goto_3
    iget-object v1, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->requests:Ljava/util/Set;

    invoke-interface {v1, v11}, Ljava/util/Set;->remove(Ljava/lang/Object;)Z

    iget-object v1, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    if-ne v1, v11, :cond_a

    iput-object v12, v9, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerPollCancellation:Lorg/emulationstation/frontend/station/StationApi$Cancellation;

    :cond_a
    throw v0

    .line 520
    :cond_b
    :goto_4
    :try_start_3
    monitor-exit p0

    return-void

    :catchall_1
    move-exception v0

    monitor-exit p0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    throw v0

    :cond_c
    :goto_5
    return-void
.end method

.method synthetic lambda$selectRoomMode$45$org-emulationstation-frontend-netplay-StationRoomsActivity(I)V
    .locals 0

    .line 651
    iput p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setupCapacity:I

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderRoomSetup()V

    return-void
.end method

.method synthetic lambda$sendChat$57$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 2
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 763
    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_0

    const-string v0, "chat"

    goto :goto_0

    :cond_0
    const-string v0, "direct-chat"

    :goto_0
    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "text"

    invoke-virtual {v0, v1, p2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object p2

    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_1

    const-string p1, "roomId"

    invoke-virtual {p2, p1, p3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    goto :goto_1

    :cond_1
    const-string p3, "peerId"

    invoke-virtual {p2, p3, p1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    :goto_1
    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const/4 p3, 0x0

    invoke-virtual {p1, p2, p3, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$sendChat$58$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 763
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->conversationPeer:Ljava/lang/String;

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    invoke-virtual {v0}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-eqz p2, :cond_0

    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->chat:Landroid/widget/EditText;

    const-string v0, ""

    invoke-virtual {p2, v0}, Landroid/widget/EditText;->setText(Ljava/lang/CharSequence;)V

    :cond_0
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->drafts:Ljava/util/Map;

    invoke-interface {p2, p1}, Ljava/util/Map;->remove(Ljava/lang/Object;)Ljava/lang/Object;

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->renderConversation(Lorg/json/JSONObject;)V

    return-void
.end method

.method synthetic lambda$setupChoice$43$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/Runnable;Landroid/view/View;)V
    .locals 0

    .line 634
    iget-boolean p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->busy:Z

    if-nez p2, :cond_0

    iget-boolean p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->launching:Z

    if-nez p2, :cond_0

    invoke-interface {p1}, Ljava/lang/Runnable;->run()V

    :cond_0
    return-void
.end method

.method synthetic lambda$showPlayer$83$org-emulationstation-frontend-netplay-StationRoomsActivity(Landroid/content/DialogInterface;)V
    .locals 1

    .line 878
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    if-ne v0, p1, :cond_0

    const/4 p1, 0x0

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->playerSheet:Lorg/emulationstation/frontend/netplay/StationPlayerSheet;

    const-string p1, ""

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->inspectedPeer:Ljava/lang/String;

    :cond_0
    return-void
.end method

.method synthetic lambda$showRoomCode$91$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;)V
    .locals 2

    .line 0
    const-string v0, "clipboard"

    .line 938
    invoke-virtual {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/content/ClipboardManager;

    if-eqz v0, :cond_0

    const-string v1, "Convite TurboStations"

    invoke-static {v1, p1}, Landroid/content/ClipData;->newPlainText(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Landroid/content/ClipData;

    move-result-object p1

    invoke-virtual {v0, p1}, Landroid/content/ClipboardManager;->setPrimaryClip(Landroid/content/ClipData;)V

    const-string p1, "C\u00f3digo copiado"

    const/4 v0, 0x0

    invoke-static {p0, p1, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object p1

    invoke-virtual {p1}, Landroid/widget/Toast;->show()V

    :cond_0
    return-void
.end method

.method synthetic lambda$showRoomCode$92$org-emulationstation-frontend-netplay-StationRoomsActivity()V
    .locals 1

    .line 939
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->codeDialog:Landroid/app/Dialog;

    invoke-virtual {v0}, Landroid/app/Dialog;->dismiss()V

    return-void
.end method

.method synthetic lambda$showRoomSetup$44$org-emulationstation-frontend-netplay-StationRoomsActivity(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)V
    .locals 0

    .line 643
    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectRoomMode(Lorg/emulationstation/frontend/netplay/StationMultiplayerProfile;)V

    return-void
.end method

.method synthetic lambda$socialAction$76$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 1
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 827
    invoke-static {p1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p1

    if-eqz p2, :cond_0

    const-string v0, "peerId"

    invoke-virtual {p1, v0, p2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    :cond_0
    if-eqz p3, :cond_1

    const-string p2, "text"

    invoke-virtual {p1, p2, p3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    :cond_1
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const/4 p3, 0x0

    invoke-virtual {p2, p1, p3, p4}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1
.end method

.method synthetic lambda$startRoom$109$org-emulationstation-frontend-netplay-StationRoomsActivity(Ljava/lang/String;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;
    .locals 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 1077
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object v0

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomStartState;->reason(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-eqz v2, :cond_2

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->roomConfirmationKey(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p1, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_1

    const-string p1, "transports"

    invoke-virtual {v0, p1}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object p1

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomStartState;->transport(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v1

    invoke-static {p1, v1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->contains(Lorg/json/JSONArray;Ljava/lang/String;)Z

    move-result p1

    if-eqz p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->client:Lorg/emulationstation/frontend/netplay/StationOnlineClient;

    const-string v1, "start"

    invoke-static {v1}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->command(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "room"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v3

    const-string v4, "roomId"

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v4, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v1

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v2

    const-string v3, "generation"

    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;)J

    move-result-wide v4

    invoke-virtual {v1, v3, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "transport"

    invoke-static {v0}, Lorg/emulationstation/frontend/netplay/StationRoomStartState;->transport(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v2, v0}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v0

    const/4 v1, 0x0

    invoke-virtual {p1, v0, v1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineClient;->call(Lorg/json/JSONObject;ZLorg/emulationstation/frontend/station/StationApi$Cancellation;)Lorg/json/JSONObject;

    move-result-object p1

    return-object p1

    :cond_0
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string p2, "A conex\u00e3o da sala aguarda ativa\u00e7\u00e3o."

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1

    :cond_1
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    const-string p2, "A sala mudou. Confira os participantes antes de iniciar."

    invoke-direct {p1, p2}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1

    :cond_2
    new-instance p1, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;

    invoke-direct {p1, v1}, Lorg/emulationstation/frontend/netplay/StationOnlineGame$Unavailable;-><init>(Ljava/lang/String;)V

    throw p1
.end method

.method protected onActivityResult(IILandroid/content/Intent;)V
    .locals 0

    .line 83
    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;->onActivityResult(IILandroid/content/Intent;)V

    .line 86
    iget-object p2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    invoke-virtual {p2, p1}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;->completed(I)Z

    move-result p1

    if-eqz p1, :cond_0

    const-string p1, "StationRooms"

    const-string p2, "game stage=native-activity-returned"

    invoke-static {p1, p2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    :cond_0
    return-void
.end method

.method public onBackPressed()V
    .locals 2

    .line 1114
    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->section:I

    const/4 v1, 0x3

    if-ne v0, v1, :cond_0

    const/4 v0, 0x1

    invoke-direct {p0, v0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->navigate(I)V

    return-void

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->exitRooms()V

    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .locals 3

    .line 65
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    invoke-static {p0}, Lorg/emulationstation/frontend/station/StationGraphicsPreferences;->get(Landroid/content/Context;)Lorg/emulationstation/frontend/station/StationGraphicsPreferences;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->graphics:Lorg/emulationstation/frontend/station/StationGraphicsPreferences;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    if-nez p1, :cond_0

    const/4 v1, 0x0

    goto :goto_0

    :cond_0
    const-string v1, "station.nativeReturn"

    invoke-virtual {p1, v1}, Landroid/os/Bundle;->getBundle(Ljava/lang/String;)Landroid/os/Bundle;

    move-result-object v1

    :goto_0
    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;->restore(Landroid/os/Bundle;)V

    invoke-static {p0}, Lorg/emulationstation/frontend/auth/StationTaskNavigation;->arrived(Landroid/app/Activity;)V

    invoke-virtual {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->getIntent()Landroid/content/Intent;

    move-result-object v0

    const-string v1, "station.itemId"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    iput-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->selectedItem:Ljava/lang/String;

    const/4 v0, 0x1

    const/4 v1, 0x0

    if-eqz p1, :cond_1

    const-string v2, "returning"

    invoke-virtual {p1, v2}, Landroid/os/Bundle;->getBoolean(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_1

    move v2, v0

    goto :goto_1

    :cond_1
    move v2, v1

    :goto_1
    iput-boolean v2, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    if-eqz p1, :cond_2

    const-string v2, "returningRecovery"

    invoke-virtual {p1, v2}, Landroid/os/Bundle;->getBoolean(Ljava/lang/String;)Z

    move-result p1

    if-eqz p1, :cond_2

    goto :goto_2

    :cond_2
    move v0, v1

    :goto_2
    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningRecovery:Z

    new-instance p1, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    invoke-direct {p1, p0}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;-><init>(Landroid/content/Context;)V

    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->build()V

    return-void
.end method

.method protected onDestroy()V
    .locals 1

    .line 456
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->commands:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->events:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearHeroCover()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->clearRoomRows()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->close()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->multiplayerEvents:Ljava/util/concurrent/ScheduledExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ScheduledExecutorService;->shutdownNow()Ljava/util/List;

    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V

    return-void
.end method

.method public onGraphicsChanged(Lorg/emulationstation/frontend/station/StationGraphicsPreferences$State;)V
    .locals 0

    .line 413
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyGraphics()V

    return-void
.end method

.method protected onNewIntent(Landroid/content/Intent;)V
    .locals 0

    .line 67
    invoke-super {p0, p1}, Landroid/app/Activity;->onNewIntent(Landroid/content/Intent;)V

    invoke-virtual {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->setIntent(Landroid/content/Intent;)V

    invoke-static {p0}, Lorg/emulationstation/frontend/auth/StationTaskNavigation;->arrived(Landroid/app/Activity;)V

    .line 68
    iput-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->pendingNavigation:Landroid/content/Intent;

    iget-boolean p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    if-eqz p1, :cond_0

    iget-object p1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->state:Lorg/emulationstation/frontend/netplay/StationRoomState;

    invoke-virtual {p1}, Lorg/emulationstation/frontend/netplay/StationRoomState;->get()Lorg/json/JSONObject;

    move-result-object p1

    invoke-direct {p0, p1}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyPendingNavigation(Lorg/json/JSONObject;)V

    :cond_0
    return-void
.end method

.method protected onPause()V
    .locals 2

    .line 405
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->hyperspace:Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

    const/4 v1, 0x0

    if-eqz v0, :cond_0

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationHyperspaceView;->setResumed(Z)V

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    if-eqz v0, :cond_1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationGameRatingView;->setResumed(Z)V

    :cond_1
    invoke-super {p0}, Landroid/app/Activity;->onPause()V

    return-void
.end method

.method protected onResume()V
    .locals 2

    .line 404
    invoke-super {p0}, Landroid/app/Activity;->onResume()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->hyperspace:Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

    const/4 v1, 0x1

    if-eqz v0, :cond_0

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationHyperspaceView;->setResumed(Z)V

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    if-eqz v0, :cond_1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationGameRatingView;->setResumed(Z)V

    :cond_1
    return-void
.end method

.method public onSaveInstanceState(Landroid/os/Bundle;)V
    .locals 2

    const-string v0, "returning"

    .line 81
    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    invoke-virtual {p1, v0, v1}, Landroid/os/Bundle;->putBoolean(Ljava/lang/String;Z)V

    const-string v0, "returningRecovery"

    iget-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningRecovery:Z

    invoke-virtual {p1, v0, v1}, Landroid/os/Bundle;->putBoolean(Ljava/lang/String;Z)V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->nativeReturn:Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationGameSession$LaunchReturn;->save()Landroid/os/Bundle;

    move-result-object v0

    const-string v1, "station.nativeReturn"

    invoke-virtual {p1, v1, v0}, Landroid/os/Bundle;->putBundle(Ljava/lang/String;Landroid/os/Bundle;)V

    invoke-super {p0, p1}, Landroid/app/Activity;->onSaveInstanceState(Landroid/os/Bundle;)V

    return-void
.end method

.method protected onStart()V
    .locals 1

    .line 454
    invoke-super {p0}, Landroid/app/Activity;->onStart()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->graphics:Lorg/emulationstation/frontend/station/StationGraphicsPreferences;

    invoke-virtual {v0, p0}, Lorg/emulationstation/frontend/station/StationGraphicsPreferences;->addListener(Lorg/emulationstation/frontend/station/StationGraphicsPreferences$Listener;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->applyGraphics()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->start()V

    const/4 v0, 0x0

    invoke-static {p0, v0}, Lorg/emulationstation/frontend/netplay/StationPresence;->foreground(Landroid/content/Context;Z)V

    const/4 v0, 0x1

    iput-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    iget-boolean v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->returningFromGame:Z

    if-eqz v0, :cond_0

    invoke-static {p0}, Lorg/emulationstation/frontend/auth/StationTaskNavigation;->gameReturned(Landroid/app/Activity;)V

    :cond_0
    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->connect()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->loadHero()V

    return-void
.end method

.method protected onStop()V
    .locals 2

    .line 455
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->graphics:Lorg/emulationstation/frontend/station/StationGraphicsPreferences;

    invoke-virtual {v0, p0}, Lorg/emulationstation/frontend/station/StationGraphicsPreferences;->removeListener(Lorg/emulationstation/frontend/station/StationGraphicsPreferences$Listener;)V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->stopMultiplayerPoll()V

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->hyperspace:Lorg/emulationstation/frontend/netplay/StationHyperspaceView;

    const/4 v1, 0x0

    if-eqz v0, :cond_0

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationHyperspaceView;->setResumed(Z)V

    :cond_0
    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->headerRating:Lorg/emulationstation/frontend/netplay/StationGameRatingView;

    if-eqz v0, :cond_1

    invoke-virtual {v0, v1}, Lorg/emulationstation/frontend/netplay/StationGameRatingView;->setResumed(Z)V

    :cond_1
    iput-boolean v1, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->active:Z

    iget v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    add-int/lit8 v0, v0, 0x1

    iput v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->epoch:I

    iget-object v0, p0, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->artwork:Lorg/emulationstation/frontend/netplay/StationRoomArtwork;

    invoke-virtual {v0}, Lorg/emulationstation/frontend/netplay/StationRoomArtwork;->stop()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->cancelAll()V

    invoke-direct {p0}, Lorg/emulationstation/frontend/netplay/StationRoomsActivity;->closeSheets()V

    invoke-super {p0}, Landroid/app/Activity;->onStop()V

    return-void
.end method
