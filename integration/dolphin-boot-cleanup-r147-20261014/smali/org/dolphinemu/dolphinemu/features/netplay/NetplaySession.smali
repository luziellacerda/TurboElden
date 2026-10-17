.class public final Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;
.super Ljava/lang/Object;
.source "r8-map-id-9a4222011a6d8b0648219e033bcbee74eb4d973334d19b9766cacf6ca23ae0d2"


# instance fields
.field public final _chatMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _connectionErrors:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

.field public final _connectionLost:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

.field public final _controllerMapping:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _desyncMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _fatalTraversalError:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

.field public final _game:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

.field public final _hostInputAuthorityEnabled:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _launchGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

.field public final _messages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _padBuffer:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _players:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field public final _saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

.field public final _stopGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

.field public final _traversalState:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

.field private bootSessionDataPointer:J

.field public final chatMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

.field public final connectionErrors:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

.field public final connectionLost:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

.field public final controllerMapping:Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;

.field public final desyncMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

.field public final fatalTraversalError:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

.field public final game:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

.field public final gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlyStateFlow;

.field public final hostInputAuthorityEnabled:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

.field public volatile isClosed:Z

.field public final launchGame:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

.field public final messages:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

.field private netPlayClientPointer:J

.field private netPlayServerPointer:J

.field private netPlayUICallbacksPointer:J

.field public final nickName$delegate:Ltdolphin/shaded/kotlin/SynchronizedLazyImpl;

.field public final onClosed:Lorg/dolphinemu/dolphinemu/model/TaskViewModel$$ExternalSyntheticLambda0;

.field public final padBuffer:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

.field public final players:Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;

.field public final saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlyStateFlow;

.field public final sessionScope:Ltdolphin/shaded/kotlinx/coroutines/internal/ContextScope;

.field public final stopGame:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

.field public final traversalState:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;


# direct methods
.method public constructor <init>(Lorg/dolphinemu/dolphinemu/model/TaskViewModel$$ExternalSyntheticLambda0;)V
    .locals 9

    .line 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 2
    .line 3
    .line 4
    iput-object p1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->onClosed:Lorg/dolphinemu/dolphinemu/model/TaskViewModel$$ExternalSyntheticLambda0;

    .line 5
    .line 6
    sget-object p1, Lorg/dolphinemu/dolphinemu/services/GameFileCacheManager;->gameFiles:Ltdolphin/lifecycle/MutableLiveData;

    .line 7
    .line 8
    invoke-virtual {p1}, Ltdolphin/lifecycle/MutableLiveData;->getValue()Ljava/lang/Object;

    .line 9
    .line 10
    .line 11
    move-result-object p1

    .line 12
    check-cast p1, [Lorg/dolphinemu/dolphinemu/model/GameFile;

    .line 13
    .line 14
    const/4 v0, 0x0

    .line 15
    if-nez p1, :cond_0

    .line 16
    .line 17
    new-array p1, v0, [Lorg/dolphinemu/dolphinemu/model/GameFile;

    .line 18
    .line 19
    :cond_0
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeCreateUICallbacks([Lorg/dolphinemu/dolphinemu/model/GameFile;)J

    .line 20
    .line 21
    .line 22
    move-result-wide v1

    .line 23
    iput-wide v1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayUICallbacksPointer:J

    .line 24
    .line 25
    invoke-static {}, Ltdolphin/shaded/kotlinx/coroutines/JobKt;->SupervisorJob$default()Ltdolphin/shaded/kotlinx/coroutines/SupervisorJobImpl;

    .line 26
    .line 27
    .line 28
    move-result-object p1

    .line 29
    invoke-static {p1}, Ltdolphin/shaded/kotlinx/coroutines/JobKt;->CoroutineScope(Ltdolphin/shaded/kotlin/coroutines/CoroutineContext;)Ltdolphin/shaded/kotlinx/coroutines/internal/ContextScope;

    .line 30
    .line 31
    .line 32
    move-result-object p1

    .line 33
    iput-object p1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->sessionScope:Ltdolphin/shaded/kotlinx/coroutines/internal/ContextScope;

    .line 34
    .line 35
    new-instance p1, Ltdolphin/shaded/coil/ImageLoader$Builder$$ExternalSyntheticLambda2;

    .line 36
    .line 37
    const/16 v1, 0x13

    .line 38
    .line 39
    invoke-direct {p1, v1}, Ltdolphin/shaded/coil/ImageLoader$Builder$$ExternalSyntheticLambda2;-><init>(I)V

    .line 40
    .line 41
    .line 42
    new-instance v1, Ltdolphin/shaded/kotlin/SynchronizedLazyImpl;

    .line 43
    .line 44
    invoke-direct {v1, p1}, Ltdolphin/shaded/kotlin/SynchronizedLazyImpl;-><init>(Ltdolphin/shaded/kotlin/jvm/functions/Function0;)V

    .line 45
    .line 46
    .line 47
    iput-object v1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nickName$delegate:Ltdolphin/shaded/kotlin/SynchronizedLazyImpl;

    .line 48
    .line 49
    const/4 p1, -0x1

    .line 50
    const/4 v1, 0x6

    .line 51
    const/4 v2, 0x0

    .line 52
    invoke-static {p1, v1, v2}, Ltdolphin/shaded/kotlinx/coroutines/channels/ChannelKt;->Channel$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 53
    .line 54
    .line 55
    move-result-object v3

    .line 56
    iput-object v3, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_launchGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 57
    .line 58
    new-instance v4, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 59
    .line 60
    invoke-direct {v4, v3}, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/channels/Channel;)V

    .line 61
    .line 62
    .line 63
    iput-object v4, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->launchGame:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 64
    .line 65
    invoke-static {p1, v1, v2}, Ltdolphin/shaded/kotlinx/coroutines/channels/ChannelKt;->Channel$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 66
    .line 67
    .line 68
    move-result-object v3

    .line 69
    iput-object v3, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_stopGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 70
    .line 71
    new-instance v4, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 72
    .line 73
    invoke-direct {v4, v3}, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/channels/Channel;)V

    .line 74
    .line 75
    .line 76
    iput-object v4, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->stopGame:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 77
    .line 78
    invoke-static {p1, v1, v2}, Ltdolphin/shaded/kotlinx/coroutines/channels/ChannelKt;->Channel$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 79
    .line 80
    .line 81
    move-result-object v3

    .line 82
    iput-object v3, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_connectionLost:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 83
    .line 84
    new-instance v4, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 85
    .line 86
    invoke-direct {v4, v3}, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/channels/Channel;)V

    .line 87
    .line 88
    .line 89
    iput-object v4, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->connectionLost:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 90
    .line 91
    const/4 v3, -0x2

    .line 92
    invoke-static {v3, v1, v2}, Ltdolphin/shaded/kotlinx/coroutines/channels/ChannelKt;->Channel$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 93
    .line 94
    .line 95
    move-result-object v3

    .line 96
    iput-object v3, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_connectionErrors:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 97
    .line 98
    new-instance v4, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 99
    .line 100
    invoke-direct {v4, v3}, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/channels/Channel;)V

    .line 101
    .line 102
    .line 103
    iput-object v4, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->connectionErrors:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 104
    .line 105
    const/4 v3, 0x2

    .line 106
    sget-object v4, Ltdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;->DROP_OLDEST:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;

    .line 107
    .line 108
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 109
    .line 110
    .line 111
    move-result-object v5

    .line 112
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_messages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 113
    .line 114
    new-instance v6, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 115
    .line 116
    invoke-direct {v6, v5}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 117
    .line 118
    .line 119
    iput-object v6, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->messages:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 120
    .line 121
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 122
    .line 123
    .line 124
    move-result-object v5

    .line 125
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_players:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 126
    .line 127
    new-instance v6, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 128
    .line 129
    invoke-direct {v6, v5}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 130
    .line 131
    .line 132
    invoke-static {v6}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->distinctUntilChanged(Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;)Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;

    .line 133
    .line 134
    .line 135
    move-result-object v5

    .line 136
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->players:Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;

    .line 137
    .line 138
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 139
    .line 140
    .line 141
    move-result-object v5

    .line 142
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_controllerMapping:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 143
    .line 144
    new-instance v6, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 145
    .line 146
    invoke-direct {v6, v5}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 147
    .line 148
    .line 149
    invoke-static {v6}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->distinctUntilChanged(Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;)Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;

    .line 150
    .line 151
    .line 152
    move-result-object v5

    .line 153
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->controllerMapping:Ltdolphin/shaded/kotlinx/coroutines/flow/Flow;

    .line 154
    .line 155
    const/16 v5, 0x20

    .line 156
    .line 157
    const/4 v6, 0x1

    .line 158
    invoke-static {v5, v6, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 159
    .line 160
    .line 161
    move-result-object v7

    .line 162
    iput-object v7, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_chatMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 163
    .line 164
    new-instance v8, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 165
    .line 166
    invoke-direct {v8, v7}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 167
    .line 168
    .line 169
    iput-object v8, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->chatMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 170
    .line 171
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 172
    .line 173
    .line 174
    move-result-object v7

    .line 175
    iput-object v7, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_game:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 176
    .line 177
    new-instance v8, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 178
    .line 179
    invoke-direct {v8, v7}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 180
    .line 181
    .line 182
    iput-object v8, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->game:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 183
    .line 184
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 185
    .line 186
    .line 187
    move-result-object v7

    .line 188
    iput-object v7, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_hostInputAuthorityEnabled:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 189
    .line 190
    new-instance v8, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 191
    .line 192
    invoke-direct {v8, v7}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 193
    .line 194
    .line 195
    iput-object v8, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->hostInputAuthorityEnabled:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 196
    .line 197
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 198
    .line 199
    .line 200
    move-result-object v7

    .line 201
    iput-object v7, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_padBuffer:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 202
    .line 203
    new-instance v8, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 204
    .line 205
    invoke-direct {v8, v7}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 206
    .line 207
    .line 208
    iput-object v8, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->padBuffer:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 209
    .line 210
    invoke-static {v5, v6, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 211
    .line 212
    .line 213
    move-result-object v5

    .line 214
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_desyncMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 215
    .line 216
    new-instance v6, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 217
    .line 218
    invoke-direct {v6, v5}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 219
    .line 220
    .line 221
    iput-object v6, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->desyncMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 222
    .line 223
    invoke-static {v2}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableStateFlow(Ljava/lang/Object;)Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 224
    .line 225
    .line 226
    move-result-object v5

    .line 227
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 228
    .line 229
    invoke-static {v5}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->asStateFlow(Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;)Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlyStateFlow;

    .line 230
    .line 231
    .line 232
    move-result-object v5

    .line 233
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlyStateFlow;

    .line 234
    .line 235
    invoke-static {v2}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableStateFlow(Ljava/lang/Object;)Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 236
    .line 237
    .line 238
    move-result-object v5

    .line 239
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 240
    .line 241
    invoke-static {v5}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->asStateFlow(Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;)Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlyStateFlow;

    .line 242
    .line 243
    .line 244
    move-result-object v5

    .line 245
    iput-object v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlyStateFlow;

    .line 246
    .line 247
    invoke-static {v0, v3, v4}, Ltdolphin/shaded/kotlinx/coroutines/flow/FlowKt;->MutableSharedFlow$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 248
    .line 249
    .line 250
    move-result-object v0

    .line 251
    iput-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_traversalState:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 252
    .line 253
    new-instance v3, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 254
    .line 255
    invoke-direct {v3, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;)V

    .line 256
    .line 257
    .line 258
    iput-object v3, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->traversalState:Ltdolphin/shaded/kotlinx/coroutines/flow/ReadonlySharedFlow;

    .line 259
    .line 260
    invoke-static {p1, v1, v2}, Ltdolphin/shaded/kotlinx/coroutines/channels/ChannelKt;->Channel$default(IILtdolphin/shaded/kotlinx/coroutines/channels/BufferOverflow;)Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 261
    .line 262
    .line 263
    move-result-object p1

    .line 264
    iput-object p1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_fatalTraversalError:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 265
    .line 266
    new-instance v0, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 267
    .line 268
    invoke-direct {v0, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;-><init>(Ltdolphin/shaded/kotlinx/coroutines/channels/Channel;)V

    .line 269
    .line 270
    .line 271
    iput-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->fatalTraversalError:Ltdolphin/shaded/kotlinx/coroutines/flow/ChannelAsFlow;

    .line 272
    .line 273
    return-void
.end method

.method public static final synthetic access$getNetPlayClientPointer$p(Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;)J
    .locals 2

    .line 1
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayClientPointer:J

    .line 2
    .line 3
    return-wide v0
.end method

.method public static final synthetic access$getNetPlayServerPointer$p(Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;)J
    .locals 2

    .line 1
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayServerPointer:J

    .line 2
    .line 3
    return-wide v0
.end method

.method public static final synthetic access$nativeHost(Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;)J
    .locals 2

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeHost()J

    .line 2
    .line 3
    .line 4
    move-result-wide v0

    .line 5
    return-wide v0
.end method

.method public static final synthetic access$nativeJoin(Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;)J
    .locals 2

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeJoin()J

    .line 2
    .line 3
    .line 4
    move-result-wide v0

    .line 5
    return-wide v0
.end method

.method public static final synthetic access$setNetPlayClientPointer$p(Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;J)V
    .locals 0

    .line 1
    iput-wide p1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayClientPointer:J

    .line 2
    .line 3
    return-void
.end method

.method public static final synthetic access$setNetPlayServerPointer$p(Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;J)V
    .locals 0

    .line 1
    iput-wide p1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayServerPointer:J

    .line 2
    .line 3
    return-void
.end method

.method private final native nativeAdjustClientPadBufferSize(I)V
.end method

.method private final native nativeAdjustServerPadBufferSize(I)V
.end method

.method private final native nativeChangeGame(Lorg/dolphinemu/dolphinemu/model/GameFile;)V
.end method

.method private final native nativeCreateUICallbacks([Lorg/dolphinemu/dolphinemu/model/GameFile;)J
.end method

.method private final native nativeDoAllPlayersHaveGame()Z
.end method

.method private final native nativeGetExternalIpAddress()Ljava/lang/String;
.end method

.method private final native nativeGetPadMapping()[I
.end method

.method private final native nativeGetPort()I
.end method

.method private final native nativeGetWiimoteMapping()[I
.end method

.method private final native nativeHost()J
.end method

.method private final native nativeJoin()J
.end method

.method private final native nativeReconnectTraversal()V
.end method

.method private final native nativeReleaseBootSessionData(J)V
.end method

.method private final native nativeReleaseClient(J)V
.end method

.method private final native nativeReleaseServer(J)V
.end method

.method private final native nativeReleaseUICallbacks(J)V
.end method

.method private final native nativeSendMessage(Ljava/lang/String;)V
.end method

.method private final native nativeSetHostInputAuthority(Z)V
.end method

.method private final native nativeSetPadMapping([I)V
.end method

.method private final native nativeSetWiimoteMapping([I)V
.end method

.method private final native nativeStartGame()V
.end method


# virtual methods
.method public final adjustClientPadBufferSize(I)V
    .locals 0

    .line 1
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeAdjustClientPadBufferSize(I)V

    .line 2
    .line 3
    .line 4
    return-void
.end method

.method public final adjustServerPadBufferSize(I)V
    .locals 0

    .line 1
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeAdjustServerPadBufferSize(I)V

    .line 2
    .line 3
    .line 4
    return-void
.end method

.method public final changeGame(Lorg/dolphinemu/dolphinemu/model/GameFile;)V
    .locals 0

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeChangeGame(Lorg/dolphinemu/dolphinemu/model/GameFile;)V

    .line 5
    .line 6
    .line 7
    return-void
.end method

.method public final declared-synchronized closeBlocking()V
    .locals 2

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->allowClose(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    .line 1
    :cond_0
    monitor-enter p0

    .line 2
    :try_start_0
    iget-boolean v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->isClosed:Z
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 3
    .line 4
    if-eqz v0, :cond_1

    .line 5
    .line 6
    monitor-exit p0

    .line 7
    return-void

    .line 8
    :cond_1
    const/4 v0, 0x1

    .line 9
    :try_start_1
    iput-boolean v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->isClosed:Z

    .line 10
    .line 11
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->sessionScope:Ltdolphin/shaded/kotlinx/coroutines/internal/ContextScope;

    .line 12
    .line 13
    const/4 v1, 0x0

    .line 14
    invoke-static {v0, v1}, Ltdolphin/shaded/kotlinx/coroutines/JobKt;->cancel(Ltdolphin/shaded/kotlinx/coroutines/CoroutineScope;Ljava/util/concurrent/CancellationException;)V

    .line 15
    .line 16
    .line 17
    invoke-virtual {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->releaseNativeResources()V

    .line 18
    .line 19
    .line 20
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->onClosed:Lorg/dolphinemu/dolphinemu/model/TaskViewModel$$ExternalSyntheticLambda0;

    .line 21
    .line 22
    invoke-virtual {v0, p0}, Lorg/dolphinemu/dolphinemu/model/TaskViewModel$$ExternalSyntheticLambda0;->invoke(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 23
    .line 24
    .line 25
    monitor-exit p0

    .line 26
    return-void

    .line 27
    :catchall_0
    move-exception v0

    .line 28
    :try_start_2
    monitor-exit p0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 29
    throw v0
.end method

.method public final consumeBootSessionData()J
    .locals 6

    const-class v4, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;

    monitor-enter v4

    :station_boot_lock_start
    .line 1
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->bootSessionDataPointer:J

    .line 2
    .line 3
    const-wide/16 v2, 0x0

    .line 4
    .line 5
    iput-wide v2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->bootSessionDataPointer:J

    .line 6
    .line 7
    goto :station_boot_return
    :station_boot_lock_end
    .catchall {:station_boot_lock_start .. :station_boot_lock_end} :station_boot_lock_catch

    :station_boot_return
    monitor-exit v4

    return-wide v0

    :station_boot_lock_catch
    move-exception v5

    monitor-exit v4

    throw v5
.end method

.method public final doAllPlayersHaveGame()Z
    .locals 0

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeDoAllPlayersHaveGame()Z

    .line 2
    .line 3
    .line 4
    move-result p0

    .line 5
    return p0
.end method

.method public final finalize()V
    .locals 0

    .line 1
    invoke-virtual {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->releaseNativeResources()V

    .line 2
    .line 3
    .line 4
    return-void
.end method

.method public final getExternalIpAddress()Ljava/lang/String;
    .locals 0

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeGetExternalIpAddress()Ljava/lang/String;

    .line 2
    .line 3
    .line 4
    move-result-object p0

    .line 5
    return-object p0
.end method

.method public final getPort()I
    .locals 0

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeGetPort()I

    .line 2
    .line 3
    .line 4
    move-result p0

    .line 5
    return p0
.end method

.method public final isHosting()Z
    .locals 4

    .line 1
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayServerPointer:J

    .line 2
    .line 3
    const-wide/16 v2, 0x0

    .line 4
    .line 5
    cmp-long p0, v0, v2

    .line 6
    .line 7
    if-eqz p0, :cond_0

    .line 8
    .line 9
    const/4 p0, 0x1

    .line 10
    return p0

    .line 11
    :cond_0
    const/4 p0, 0x0

    .line 12
    return p0
.end method

.method public final isLaunching()Z
    .locals 6

    const-class v4, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;

    monitor-enter v4

    :station_boot_lock_start
    .line 1
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->bootSessionDataPointer:J

    .line 2
    .line 3
    const-wide/16 v2, 0x0

    .line 4
    .line 5
    cmp-long p0, v0, v2

    .line 6
    .line 7
    if-eqz p0, :cond_0

    .line 8
    .line 9
    const/4 p0, 0x1

    .line 10
    goto :station_boot_return

    .line 11
    :cond_0
    const/4 p0, 0x0

    .line 12
    goto :station_boot_return
    :station_boot_lock_end
    .catchall {:station_boot_lock_start .. :station_boot_lock_end} :station_boot_lock_catch

    :station_boot_return
    monitor-exit v4

    return p0

    :station_boot_lock_catch
    move-exception v5

    monitor-exit v4

    throw v5
.end method

.method public final onAbortGameDigest()V
    .locals 1

    .line 1
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 2
    .line 3
    const/4 v0, 0x0

    .line 4
    invoke-virtual {p0, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->setValue(Ljava/lang/Object;)V

    .line 5
    .line 6
    .line 7
    return-void
.end method

.method public final onBootGame(Ljava/lang/String;J)V
    .locals 8

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    const-class v1, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;

    const-wide/16 v2, 0x0

    const/4 v4, 0x0

    monitor-enter v1

    :station_boot_offer_start
    iget-boolean v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->isClosed:Z

    iget-wide v5, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->bootSessionDataPointer:J

    if-nez v0, :station_boot_offer_closed

    cmp-long v0, v5, p2

    if-eqz v0, :station_boot_offer_same

    move-wide v2, v5

    :station_boot_offer_same
    iput-wide p2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->bootSessionDataPointer:J

    const/4 v4, 0x1

    goto :station_boot_offer_end

    :station_boot_offer_closed
    cmp-long v0, v5, p2

    if-eqz v0, :station_boot_offer_end

    move-wide v2, p2

    :station_boot_offer_end
    .catchall {:station_boot_offer_start .. :station_boot_offer_end} :station_boot_offer_catch
    monitor-exit v1

    const-wide/16 v5, 0x0

    cmp-long v0, v2, v5

    if-eqz v0, :station_boot_offer_released

    invoke-direct {p0, v2, v3}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeReleaseBootSessionData(J)V

    :station_boot_offer_released
    if-nez v4, :station_boot_offer_dispatch

    return-void

    :station_boot_offer_catch
    move-exception v7

    monitor-exit v1

    throw v7

    :station_boot_offer_dispatch

    invoke-static {p0, p1}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->onBootGame(Ljava/lang/Object;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_0

    return-void

    .line 5
    .line 6
    :cond_0
    iget-object p2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_stopGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 7
    .line 8
    invoke-virtual {p2}, Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;->tryReceive-PtdJZtk()Ljava/lang/Object;

    .line 9
    .line 10
    .line 11
    move-result-object p2

    .line 12
    instance-of p2, p2, Ltdolphin/shaded/kotlinx/coroutines/channels/ChannelResult$Failed;

    .line 13
    .line 14
    if-eqz p2, :cond_0

    .line 15
    .line 16
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_launchGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 17
    .line 18
    invoke-interface {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/channels/SendChannel;->trySend-JP2dKIU(Ljava/lang/Object;)Ljava/lang/Object;

    .line 19
    .line 20
    .line 21
    return-void
.end method

.method public final onChatMessageReceived(Ljava/lang/String;)V
    .locals 0

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_chatMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 5
    .line 6
    invoke-virtual {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 7
    .line 8
    .line 9
    return-void
.end method

.method public final onConnectionError(Ljava/lang/String;)V
    .locals 1

    invoke-static {p0, p1}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->onConnectionError(Ljava/lang/Object;Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_0

    return-void

    .line 1
    :cond_0
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_connectionErrors:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 5
    .line 6
    invoke-interface {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/channels/SendChannel;->trySend-JP2dKIU(Ljava/lang/Object;)Ljava/lang/Object;

    .line 7
    .line 8
    .line 9
    return-void
.end method

.method public final onConnectionLost()V
    .locals 1

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->onConnectionLost(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    return-void

    .line 1
    :cond_0
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_connectionLost:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 2
    .line 3
    sget-object v0, Ltdolphin/shaded/kotlin/Unit;->INSTANCE:Ltdolphin/shaded/kotlin/Unit;

    .line 4
    .line 5
    invoke-interface {p0, v0}, Ltdolphin/shaded/kotlinx/coroutines/channels/SendChannel;->trySend-JP2dKIU(Ljava/lang/Object;)Ljava/lang/Object;

    .line 6
    .line 7
    .line 8
    return-void
.end method

.method public final onDesync(ILjava/lang/String;)V
    .locals 1

    .line 1
    invoke-virtual {p2}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    new-instance v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/NetplayMessage$Desync;

    .line 5
    .line 6
    invoke-direct {v0, p1, p2}, Lorg/dolphinemu/dolphinemu/features/netplay/model/NetplayMessage$Desync;-><init>(ILjava/lang/String;)V

    .line 7
    .line 8
    .line 9
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_desyncMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 10
    .line 11
    invoke-virtual {p0, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 12
    .line 13
    .line 14
    return-void
.end method

.method public final onGameChanged(Ljava/lang/String;)V
    .locals 0

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_game:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 5
    .line 6
    invoke-virtual {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 7
    .line 8
    .line 9
    return-void
.end method

.method public final onHideChunkedProgressDialog()V
    .locals 1

    .line 1
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 2
    .line 3
    const/4 v0, 0x0

    .line 4
    invoke-virtual {p0, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->setValue(Ljava/lang/Object;)V

    .line 5
    .line 6
    .line 7
    return-void
.end method

.method public final onHostInputAuthorityChanged(Z)V
    .locals 0

    .line 1
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_hostInputAuthorityEnabled:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 2
    .line 3
    invoke-static {p1}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    .line 4
    .line 5
    .line 6
    move-result-object p1

    .line 7
    invoke-virtual {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 8
    .line 9
    .line 10
    return-void
.end method

.method public final onPadBufferChanged(I)V
    .locals 2

    .line 1
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_hostInputAuthorityEnabled:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 2
    .line 3
    invoke-virtual {v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->getReplayCache()Ljava/util/List;

    .line 4
    .line 5
    .line 6
    move-result-object v0

    .line 7
    invoke-static {v0}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->firstOrNull(Ljava/util/List;)Ljava/lang/Object;

    .line 8
    .line 9
    .line 10
    move-result-object v0

    .line 11
    sget-object v1, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;

    .line 12
    .line 13
    invoke-static {v0, v1}, Ltdolphin/shaded/kotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 14
    .line 15
    .line 16
    move-result v0

    .line 17
    if-eqz v0, :cond_0

    .line 18
    .line 19
    return-void

    .line 20
    :cond_0
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_padBuffer:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 21
    .line 22
    invoke-static {p1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    .line 23
    .line 24
    .line 25
    move-result-object p1

    .line 26
    invoke-virtual {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 27
    .line 28
    .line 29
    return-void
.end method

.method public final onSetChunkedProgress(IJ)V
    .locals 6

    .line 1
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 2
    .line 3
    invoke-virtual {p0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->getValue()Ljava/lang/Object;

    .line 4
    .line 5
    .line 6
    move-result-object v0

    .line 7
    check-cast v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;

    .line 8
    .line 9
    if-eqz v0, :cond_2

    .line 10
    .line 11
    iget-object v1, v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;->playerProgresses:Ljava/util/List;

    .line 12
    .line 13
    new-instance v2, Ljava/util/ArrayList;

    .line 14
    .line 15
    const/16 v3, 0xa

    .line 16
    .line 17
    invoke-static {v1, v3}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 18
    .line 19
    .line 20
    move-result v3

    .line 21
    invoke-direct {v2, v3}, Ljava/util/ArrayList;-><init>(I)V

    .line 22
    .line 23
    .line 24
    invoke-interface {v1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 25
    .line 26
    .line 27
    move-result-object v1

    .line 28
    :goto_0
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    .line 29
    .line 30
    .line 31
    move-result v3

    .line 32
    if-eqz v3, :cond_1

    .line 33
    .line 34
    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 35
    .line 36
    .line 37
    move-result-object v3

    .line 38
    check-cast v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;

    .line 39
    .line 40
    iget v4, v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;->playerId:I

    .line 41
    .line 42
    if-ne v4, p1, :cond_0

    .line 43
    .line 44
    iget-object v3, v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;->name:Ljava/lang/String;

    .line 45
    .line 46
    new-instance v5, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;

    .line 47
    .line 48
    invoke-direct {v5, p2, p3, v3, v4}, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;-><init>(JLjava/lang/String;I)V

    .line 49
    .line 50
    .line 51
    move-object v3, v5

    .line 52
    :cond_0
    invoke-virtual {v2, v3}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 53
    .line 54
    .line 55
    goto :goto_0

    .line 56
    :cond_1
    iget-object p1, v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;->title:Ljava/lang/String;

    .line 57
    .line 58
    iget-wide p2, v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;->totalSize:J

    .line 59
    .line 60
    new-instance v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;

    .line 61
    .line 62
    invoke-direct {v0, p1, p2, p3, v2}, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;-><init>(Ljava/lang/String;JLjava/util/List;)V

    .line 63
    .line 64
    .line 65
    goto :goto_1

    .line 66
    :cond_2
    const/4 v0, 0x0

    .line 67
    :goto_1
    invoke-virtual {p0, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->setValue(Ljava/lang/Object;)V

    .line 68
    .line 69
    .line 70
    return-void
.end method

.method public final onSetGameDigestProgress(II)V
    .locals 6

    .line 1
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 2
    .line 3
    invoke-virtual {p0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->getValue()Ljava/lang/Object;

    .line 4
    .line 5
    .line 6
    move-result-object v0

    .line 7
    check-cast v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;

    .line 8
    .line 9
    if-nez v0, :cond_0

    .line 10
    .line 11
    return-void

    .line 12
    :cond_0
    iget-object v1, v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;->playerProgresses:Ljava/util/List;

    .line 13
    .line 14
    new-instance v2, Ljava/util/ArrayList;

    .line 15
    .line 16
    const/16 v3, 0xa

    .line 17
    .line 18
    invoke-static {v1, v3}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 19
    .line 20
    .line 21
    move-result v3

    .line 22
    invoke-direct {v2, v3}, Ljava/util/ArrayList;-><init>(I)V

    .line 23
    .line 24
    .line 25
    invoke-interface {v1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 26
    .line 27
    .line 28
    move-result-object v1

    .line 29
    :goto_0
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    .line 30
    .line 31
    .line 32
    move-result v3

    .line 33
    const/4 v4, 0x0

    .line 34
    if-eqz v3, :cond_2

    .line 35
    .line 36
    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 37
    .line 38
    .line 39
    move-result-object v3

    .line 40
    check-cast v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 41
    .line 42
    iget v5, v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;->playerId:I

    .line 43
    .line 44
    if-ne v5, p1, :cond_1

    .line 45
    .line 46
    const/16 v5, 0xb

    .line 47
    .line 48
    invoke-static {v3, p2, v4, v5}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;->copy$default(Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;ILjava/lang/String;I)Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 49
    .line 50
    .line 51
    move-result-object v3

    .line 52
    :cond_1
    invoke-virtual {v2, v3}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 53
    .line 54
    .line 55
    goto :goto_0

    .line 56
    :cond_2
    const/4 p1, 0x5

    .line 57
    invoke-static {v0, v2, v4, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;->copy$default(Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;Ljava/util/ArrayList;Ljava/lang/Boolean;I)Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;

    .line 58
    .line 59
    .line 60
    move-result-object p1

    .line 61
    invoke-virtual {p0, v4, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->updateState(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 62
    .line 63
    .line 64
    return-void
.end method

.method public final onSetGameDigestResult(ILjava/lang/String;)V
    .locals 7

    .line 1
    invoke-virtual {p2}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 5
    .line 6
    invoke-virtual {p0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->getValue()Ljava/lang/Object;

    .line 7
    .line 8
    .line 9
    move-result-object v0

    .line 10
    check-cast v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;

    .line 11
    .line 12
    if-nez v0, :cond_0

    .line 13
    .line 14
    return-void

    .line 15
    :cond_0
    iget-object v1, v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;->playerProgresses:Ljava/util/List;

    .line 16
    .line 17
    new-instance v2, Ljava/util/ArrayList;

    .line 18
    .line 19
    const/16 v3, 0xa

    .line 20
    .line 21
    invoke-static {v1, v3}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 22
    .line 23
    .line 24
    move-result v4

    .line 25
    invoke-direct {v2, v4}, Ljava/util/ArrayList;-><init>(I)V

    .line 26
    .line 27
    .line 28
    invoke-interface {v1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 29
    .line 30
    .line 31
    move-result-object v1

    .line 32
    :goto_0
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    .line 33
    .line 34
    .line 35
    move-result v4

    .line 36
    const/4 v5, 0x0

    .line 37
    if-eqz v4, :cond_2

    .line 38
    .line 39
    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 40
    .line 41
    .line 42
    move-result-object v4

    .line 43
    check-cast v4, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 44
    .line 45
    iget v6, v4, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;->playerId:I

    .line 46
    .line 47
    if-ne v6, p1, :cond_1

    .line 48
    .line 49
    const/4 v6, 0x7

    .line 50
    invoke-static {v4, v5, p2, v6}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;->copy$default(Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;ILjava/lang/String;I)Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 51
    .line 52
    .line 53
    move-result-object v4

    .line 54
    :cond_1
    invoke-virtual {v2, v4}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 55
    .line 56
    .line 57
    goto :goto_0

    .line 58
    :cond_2
    const/4 p1, 0x5

    .line 59
    const/4 p2, 0x0

    .line 60
    invoke-static {v0, v2, p2, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;->copy$default(Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;Ljava/util/ArrayList;Ljava/lang/Boolean;I)Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;

    .line 61
    .line 62
    .line 63
    move-result-object p1

    .line 64
    iget-object v0, p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;->playerProgresses:Ljava/util/List;

    .line 65
    .line 66
    invoke-interface {v0}, Ljava/util/Collection;->isEmpty()Z

    .line 67
    .line 68
    .line 69
    move-result v1

    .line 70
    if-eqz v1, :cond_3

    .line 71
    .line 72
    goto :goto_2

    .line 73
    :cond_3
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 74
    .line 75
    .line 76
    move-result-object v1

    .line 77
    :goto_1
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    .line 78
    .line 79
    .line 80
    move-result v2

    .line 81
    if-eqz v2, :cond_4

    .line 82
    .line 83
    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 84
    .line 85
    .line 86
    move-result-object v2

    .line 87
    check-cast v2, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 88
    .line 89
    iget-object v2, v2, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;->result:Ljava/lang/String;

    .line 90
    .line 91
    if-eqz v2, :cond_7

    .line 92
    .line 93
    goto :goto_1

    .line 94
    :cond_4
    :goto_2
    new-instance v1, Ljava/util/ArrayList;

    .line 95
    .line 96
    invoke-static {v0, v3}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 97
    .line 98
    .line 99
    move-result v2

    .line 100
    invoke-direct {v1, v2}, Ljava/util/ArrayList;-><init>(I)V

    .line 101
    .line 102
    .line 103
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 104
    .line 105
    .line 106
    move-result-object v0

    .line 107
    :goto_3
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    .line 108
    .line 109
    .line 110
    move-result v2

    .line 111
    if-eqz v2, :cond_5

    .line 112
    .line 113
    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 114
    .line 115
    .line 116
    move-result-object v2

    .line 117
    check-cast v2, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 118
    .line 119
    iget-object v2, v2, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;->result:Ljava/lang/String;

    .line 120
    .line 121
    invoke-virtual {v1, v2}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 122
    .line 123
    .line 124
    goto :goto_3

    .line 125
    :cond_5
    new-instance v0, Ljava/util/LinkedHashSet;

    .line 126
    .line 127
    invoke-direct {v0, v1}, Ljava/util/LinkedHashSet;-><init>(Ljava/util/Collection;)V

    .line 128
    .line 129
    .line 130
    invoke-static {v0}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->toList(Ljava/lang/Iterable;)Ljava/util/List;

    .line 131
    .line 132
    .line 133
    move-result-object v0

    .line 134
    invoke-interface {v0}, Ljava/util/List;->size()I

    .line 135
    .line 136
    .line 137
    move-result v0

    .line 138
    const/4 v1, 0x1

    .line 139
    if-ne v0, v1, :cond_6

    .line 140
    .line 141
    move v5, v1

    .line 142
    :cond_6
    invoke-static {v5}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    .line 143
    .line 144
    .line 145
    move-result-object v0

    .line 146
    const/4 v1, 0x3

    .line 147
    invoke-static {p1, p2, v0, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;->copy$default(Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;Ljava/util/ArrayList;Ljava/lang/Boolean;I)Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;

    .line 148
    .line 149
    .line 150
    move-result-object p1

    .line 151
    :cond_7
    invoke-virtual {p0, p2, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->updateState(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 152
    .line 153
    .line 154
    return-void
.end method

.method public final onShowChunkedProgressDialog(Ljava/lang/String;J[I)V
    .locals 9

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    invoke-virtual {p4}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 5
    .line 6
    .line 7
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_players:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 8
    .line 9
    invoke-virtual {v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->getReplayCache()Ljava/util/List;

    .line 10
    .line 11
    .line 12
    move-result-object v0

    .line 13
    invoke-static {v0}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->firstOrNull(Ljava/util/List;)Ljava/lang/Object;

    .line 14
    .line 15
    .line 16
    move-result-object v0

    .line 17
    check-cast v0, Ljava/util/List;

    .line 18
    .line 19
    new-instance v1, Ljava/util/ArrayList;

    .line 20
    .line 21
    array-length v2, p4

    .line 22
    invoke-direct {v1, v2}, Ljava/util/ArrayList;-><init>(I)V

    .line 23
    .line 24
    .line 25
    array-length v2, p4

    .line 26
    const/4 v3, 0x0

    .line 27
    :goto_0
    const/4 v4, 0x0

    .line 28
    if-ge v3, v2, :cond_4

    .line 29
    .line 30
    aget v5, p4, v3

    .line 31
    .line 32
    if-eqz v0, :cond_2

    .line 33
    .line 34
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 35
    .line 36
    .line 37
    move-result-object v6

    .line 38
    :cond_0
    invoke-interface {v6}, Ljava/util/Iterator;->hasNext()Z

    .line 39
    .line 40
    .line 41
    move-result v7

    .line 42
    if-eqz v7, :cond_1

    .line 43
    .line 44
    invoke-interface {v6}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 45
    .line 46
    .line 47
    move-result-object v7

    .line 48
    move-object v8, v7

    .line 49
    check-cast v8, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 50
    .line 51
    invoke-virtual {v8}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getPid()I

    .line 52
    .line 53
    .line 54
    move-result v8

    .line 55
    if-ne v8, v5, :cond_0

    .line 56
    .line 57
    move-object v4, v7

    .line 58
    :cond_1
    check-cast v4, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 59
    .line 60
    if-eqz v4, :cond_2

    .line 61
    .line 62
    invoke-virtual {v4}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getName()Ljava/lang/String;

    .line 63
    .line 64
    .line 65
    move-result-object v4

    .line 66
    if-nez v4, :cond_3

    .line 67
    .line 68
    :cond_2
    const-string v4, "Invalid Player ID"

    .line 69
    .line 70
    :cond_3
    new-instance v6, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;

    .line 71
    .line 72
    const-wide/16 v7, 0x0

    .line 73
    .line 74
    invoke-direct {v6, v7, v8, v4, v5}, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress$PlayerProgress;-><init>(JLjava/lang/String;I)V

    .line 75
    .line 76
    .line 77
    invoke-virtual {v1, v6}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 78
    .line 79
    .line 80
    add-int/lit8 v3, v3, 0x1

    .line 81
    .line 82
    goto :goto_0

    .line 83
    :cond_4
    new-instance p4, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;

    .line 84
    .line 85
    invoke-direct {p4, p1, p2, p3, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/SaveTransferProgress;-><init>(Ljava/lang/String;JLjava/util/List;)V

    .line 86
    .line 87
    .line 88
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_saveTransferProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 89
    .line 90
    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 91
    .line 92
    .line 93
    invoke-virtual {p0, v4, p4}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->updateState(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 94
    .line 95
    .line 96
    return-void
.end method

.method public final onShowGameDigestDialog(Ljava/lang/String;)V
    .locals 7

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_players:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 5
    .line 6
    invoke-virtual {v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->getReplayCache()Ljava/util/List;

    .line 7
    .line 8
    .line 9
    move-result-object v0

    .line 10
    invoke-static {v0}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->firstOrNull(Ljava/util/List;)Ljava/lang/Object;

    .line 11
    .line 12
    .line 13
    move-result-object v0

    .line 14
    check-cast v0, Ljava/util/List;

    .line 15
    .line 16
    const/4 v1, 0x0

    .line 17
    if-eqz v0, :cond_0

    .line 18
    .line 19
    new-instance v2, Ljava/util/ArrayList;

    .line 20
    .line 21
    const/16 v3, 0xa

    .line 22
    .line 23
    invoke-static {v0, v3}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 24
    .line 25
    .line 26
    move-result v3

    .line 27
    invoke-direct {v2, v3}, Ljava/util/ArrayList;-><init>(I)V

    .line 28
    .line 29
    .line 30
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 31
    .line 32
    .line 33
    move-result-object v0

    .line 34
    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    .line 35
    .line 36
    .line 37
    move-result v3

    .line 38
    if-eqz v3, :cond_1

    .line 39
    .line 40
    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 41
    .line 42
    .line 43
    move-result-object v3

    .line 44
    check-cast v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 45
    .line 46
    new-instance v4, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;

    .line 47
    .line 48
    invoke-virtual {v3}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getPid()I

    .line 49
    .line 50
    .line 51
    move-result v5

    .line 52
    invoke-virtual {v3}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getName()Ljava/lang/String;

    .line 53
    .line 54
    .line 55
    move-result-object v3

    .line 56
    const/4 v6, 0x0

    .line 57
    invoke-direct {v4, v5, v6, v3, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress$PlayerProgress;-><init>(IILjava/lang/String;Ljava/lang/String;)V

    .line 58
    .line 59
    .line 60
    invoke-virtual {v2, v4}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 61
    .line 62
    .line 63
    goto :goto_0

    .line 64
    :cond_0
    sget-object v2, Ltdolphin/shaded/kotlin/collections/EmptyList;->INSTANCE:Ltdolphin/shaded/kotlin/collections/EmptyList;

    .line 65
    .line 66
    :cond_1
    new-instance v0, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;

    .line 67
    .line 68
    invoke-direct {v0, p1, v2, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/GameDigestProgress;-><init>(Ljava/lang/String;Ljava/util/List;Ljava/lang/Boolean;)V

    .line 69
    .line 70
    .line 71
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_gameDigestProgress:Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;

    .line 72
    .line 73
    invoke-virtual {p0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 74
    .line 75
    .line 76
    invoke-virtual {p0, v1, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/StateFlowImpl;->updateState(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 77
    .line 78
    .line 79
    return-void
.end method

.method public final onStopGame()V
    .locals 1

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->onNativeStop(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    return-void

    .line 1
    :cond_0
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_stopGame:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 2
    .line 3
    sget-object v0, Ltdolphin/shaded/kotlin/Unit;->INSTANCE:Ltdolphin/shaded/kotlin/Unit;

    .line 4
    .line 5
    invoke-interface {p0, v0}, Ltdolphin/shaded/kotlinx/coroutines/channels/SendChannel;->trySend-JP2dKIU(Ljava/lang/Object;)Ljava/lang/Object;

    .line 6
    .line 7
    .line 8
    return-void
.end method

.method public final onTraversalStateChanged(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 1
    if-eqz p1, :cond_2

    .line 2
    .line 3
    const/4 v0, 0x1

    .line 4
    if-eq p1, v0, :cond_1

    .line 5
    .line 6
    const/4 p2, 0x2

    .line 7
    if-eq p1, p2, :cond_0

    .line 8
    .line 9
    goto :goto_1

    .line 10
    :cond_0
    new-instance p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Failure;

    .line 11
    .line 12
    invoke-virtual {p4}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 13
    .line 14
    .line 15
    invoke-direct {p1, p4}, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Failure;-><init>(Ljava/lang/String;)V

    .line 16
    .line 17
    .line 18
    goto :goto_0

    .line 19
    :cond_1
    new-instance p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Connected;

    .line 20
    .line 21
    invoke-virtual {p2}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 22
    .line 23
    .line 24
    invoke-virtual {p3}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 25
    .line 26
    .line 27
    invoke-direct {p1, p2, p3}, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Connected;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    .line 28
    .line 29
    .line 30
    goto :goto_0

    .line 31
    :cond_2
    sget-object p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Connecting;->INSTANCE:Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Connecting;

    .line 32
    .line 33
    :goto_0
    iget-object p2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_traversalState:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 34
    .line 35
    invoke-virtual {p2, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 36
    .line 37
    .line 38
    const-string p1, "BadHost"

    .line 39
    .line 40
    invoke-static {p4, p1}, Ltdolphin/shaded/kotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 41
    .line 42
    .line 43
    move-result p1

    .line 44
    if-nez p1, :cond_4

    .line 45
    .line 46
    const-string p1, "VersionTooOld"

    .line 47
    .line 48
    invoke-static {p4, p1}, Ltdolphin/shaded/kotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    .line 49
    .line 50
    .line 51
    move-result p1

    .line 52
    if-eqz p1, :cond_3

    .line 53
    .line 54
    goto :goto_2

    .line 55
    :cond_3
    :goto_1
    return-void

    .line 56
    :cond_4
    :goto_2
    new-instance p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Failure;

    .line 57
    .line 58
    invoke-direct {p1, p4}, Lorg/dolphinemu/dolphinemu/features/netplay/model/TraversalState$Failure;-><init>(Ljava/lang/String;)V

    .line 59
    .line 60
    .line 61
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_fatalTraversalError:Ltdolphin/shaded/kotlinx/coroutines/channels/BufferedChannel;

    .line 62
    .line 63
    invoke-interface {p0, p1}, Ltdolphin/shaded/kotlinx/coroutines/channels/SendChannel;->trySend-JP2dKIU(Ljava/lang/Object;)Ljava/lang/Object;

    .line 64
    .line 65
    .line 66
    return-void
.end method

.method public final onUpdate([Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;)V
    .locals 10

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    invoke-static {p1}, Ltdolphin/shaded/kotlin/collections/ArraysKt;->toList([Ljava/lang/Object;)Ljava/util/List;

    .line 5
    .line 6
    .line 7
    move-result-object p1

    .line 8
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_players:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 9
    .line 10
    invoke-virtual {v0, p1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 11
    .line 12
    .line 13
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeGetPadMapping()[I

    .line 14
    .line 15
    .line 16
    move-result-object v0

    .line 17
    new-instance v1, Ljava/util/ArrayList;

    .line 18
    .line 19
    array-length v2, v0

    .line 20
    invoke-direct {v1, v2}, Ljava/util/ArrayList;-><init>(I)V

    .line 21
    .line 22
    .line 23
    array-length v2, v0

    .line 24
    const/4 v3, 0x0

    .line 25
    move v4, v3

    .line 26
    :goto_0
    const/4 v5, 0x0

    .line 27
    if-ge v4, v2, :cond_2

    .line 28
    .line 29
    aget v6, v0, v4

    .line 30
    .line 31
    invoke-interface {p1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 32
    .line 33
    .line 34
    move-result-object v7

    .line 35
    :cond_0
    invoke-interface {v7}, Ljava/util/Iterator;->hasNext()Z

    .line 36
    .line 37
    .line 38
    move-result v8

    .line 39
    if-eqz v8, :cond_1

    .line 40
    .line 41
    invoke-interface {v7}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 42
    .line 43
    .line 44
    move-result-object v8

    .line 45
    move-object v9, v8

    .line 46
    check-cast v9, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 47
    .line 48
    invoke-virtual {v9}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getPid()I

    .line 49
    .line 50
    .line 51
    move-result v9

    .line 52
    if-ne v9, v6, :cond_0

    .line 53
    .line 54
    move-object v5, v8

    .line 55
    :cond_1
    check-cast v5, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 56
    .line 57
    invoke-virtual {v1, v5}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 58
    .line 59
    .line 60
    add-int/lit8 v4, v4, 0x1

    .line 61
    .line 62
    goto :goto_0

    .line 63
    :cond_2
    invoke-static {v1}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->toList(Ljava/lang/Iterable;)Ljava/util/List;

    .line 64
    .line 65
    .line 66
    move-result-object v0

    .line 67
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeGetWiimoteMapping()[I

    .line 68
    .line 69
    .line 70
    move-result-object v1

    .line 71
    new-instance v2, Ljava/util/ArrayList;

    .line 72
    .line 73
    array-length v4, v1

    .line 74
    invoke-direct {v2, v4}, Ljava/util/ArrayList;-><init>(I)V

    .line 75
    .line 76
    .line 77
    array-length v4, v1

    .line 78
    :goto_1
    if-ge v3, v4, :cond_5

    .line 79
    .line 80
    aget v6, v1, v3

    .line 81
    .line 82
    invoke-interface {p1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 83
    .line 84
    .line 85
    move-result-object v7

    .line 86
    :cond_3
    invoke-interface {v7}, Ljava/util/Iterator;->hasNext()Z

    .line 87
    .line 88
    .line 89
    move-result v8

    .line 90
    if-eqz v8, :cond_4

    .line 91
    .line 92
    invoke-interface {v7}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 93
    .line 94
    .line 95
    move-result-object v8

    .line 96
    move-object v9, v8

    .line 97
    check-cast v9, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 98
    .line 99
    invoke-virtual {v9}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getPid()I

    .line 100
    .line 101
    .line 102
    move-result v9

    .line 103
    if-ne v9, v6, :cond_3

    .line 104
    .line 105
    goto :goto_2

    .line 106
    :cond_4
    move-object v8, v5

    .line 107
    :goto_2
    check-cast v8, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 108
    .line 109
    invoke-virtual {v2, v8}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 110
    .line 111
    .line 112
    add-int/lit8 v3, v3, 0x1

    .line 113
    .line 114
    goto :goto_1

    .line 115
    :cond_5
    invoke-static {v2}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->toList(Ljava/lang/Iterable;)Ljava/util/List;

    .line 116
    .line 117
    .line 118
    move-result-object p1

    .line 119
    new-instance v1, Lorg/dolphinemu/dolphinemu/features/netplay/model/ControllerMapping;

    .line 120
    .line 121
    invoke-direct {v1, v0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/ControllerMapping;-><init>(Ljava/util/List;Ljava/util/List;)V

    .line 122
    .line 123
    .line 124
    iget-object p0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_controllerMapping:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 125
    .line 126
    invoke-virtual {p0, v1}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 127
    .line 128
    .line 129
    return-void
.end method

.method public final reconnectTraversal()V
    .locals 0

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeReconnectTraversal()V

    .line 2
    .line 3
    .line 4
    return-void
.end method

.method public final releaseNativeResources()V
    .locals 5

    invoke-static {p0}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->allowClose(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    .line 1
    :cond_0
    invoke-virtual {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->consumeBootSessionData()J

    move-result-wide v0

    .line 2
    .line 3
    const-wide/16 v2, 0x0

    .line 4
    .line 5
    cmp-long v4, v0, v2

    .line 6
    .line 7
    if-eqz v4, :cond_1

    .line 8
    .line 9


    .line 10
    .line 11
    invoke-direct {p0, v0, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeReleaseBootSessionData(J)V

    .line 12
    .line 13
    .line 14
    :cond_1
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayClientPointer:J

    .line 15
    .line 16
    cmp-long v4, v0, v2

    .line 17
    .line 18
    if-eqz v4, :cond_2

    .line 19
    .line 20
    iput-wide v2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayClientPointer:J

    .line 21
    .line 22
    invoke-direct {p0, v0, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeReleaseClient(J)V

    .line 23
    .line 24
    .line 25
    :cond_2
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayServerPointer:J

    .line 26
    .line 27
    cmp-long v4, v0, v2

    .line 28
    .line 29
    if-eqz v4, :cond_3

    .line 30
    .line 31
    iput-wide v2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayServerPointer:J

    .line 32
    .line 33
    invoke-direct {p0, v0, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeReleaseServer(J)V

    .line 34
    .line 35
    .line 36
    :cond_3
    iget-wide v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayUICallbacksPointer:J

    .line 37
    .line 38
    cmp-long v4, v0, v2

    .line 39
    .line 40
    if-eqz v4, :cond_4

    .line 41
    .line 42
    iput-wide v2, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->netPlayUICallbacksPointer:J

    .line 43
    .line 44
    invoke-direct {p0, v0, v1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeReleaseUICallbacks(J)V

    .line 45
    .line 46
    .line 47
    :cond_4
    return-void
.end method

.method public final sendMessage(Ljava/lang/String;)V
    .locals 2

    .line 1
    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    .line 2
    .line 3
    .line 4
    iget-object v0, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nickName$delegate:Ltdolphin/shaded/kotlin/SynchronizedLazyImpl;

    .line 5
    .line 6
    invoke-virtual {v0}, Ltdolphin/shaded/kotlin/SynchronizedLazyImpl;->getValue()Ljava/lang/Object;

    .line 7
    .line 8
    .line 9
    move-result-object v0

    .line 10
    check-cast v0, Ljava/lang/String;

    .line 11
    .line 12
    new-instance v1, Ljava/lang/StringBuilder;

    .line 13
    .line 14
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    .line 15
    .line 16
    .line 17
    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 18
    .line 19
    .line 20
    const-string v0, ": "

    .line 21
    .line 22
    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 23
    .line 24
    .line 25
    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 26
    .line 27
    .line 28
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    .line 29
    .line 30
    .line 31
    move-result-object v0

    .line 32
    iget-object v1, p0, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->_chatMessages:Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;

    .line 33
    .line 34
    invoke-virtual {v1, v0}, Ltdolphin/shaded/kotlinx/coroutines/flow/SharedFlowImpl;->tryEmit(Ljava/lang/Object;)Z

    .line 35
    .line 36
    .line 37
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeSendMessage(Ljava/lang/String;)V

    .line 38
    .line 39
    .line 40
    return-void
.end method

.method public final setControllerMapping(Lorg/dolphinemu/dolphinemu/features/netplay/model/ControllerMapping;)V
    .locals 5

    .line 1
    iget-object v0, p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/ControllerMapping;->gamecubePorts:Ljava/util/List;

    .line 2
    .line 3
    new-instance v1, Ljava/util/ArrayList;

    .line 4
    .line 5
    const/16 v2, 0xa

    .line 6
    .line 7
    invoke-static {v0, v2}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 8
    .line 9
    .line 10
    move-result v3

    .line 11
    invoke-direct {v1, v3}, Ljava/util/ArrayList;-><init>(I)V

    .line 12
    .line 13
    .line 14
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 15
    .line 16
    .line 17
    move-result-object v0

    .line 18
    :goto_0
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    .line 19
    .line 20
    .line 21
    move-result v3

    .line 22
    const/4 v4, 0x0

    .line 23
    if-eqz v3, :cond_1

    .line 24
    .line 25
    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 26
    .line 27
    .line 28
    move-result-object v3

    .line 29
    check-cast v3, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 30
    .line 31
    if-eqz v3, :cond_0

    .line 32
    .line 33
    invoke-virtual {v3}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getPid()I

    .line 34
    .line 35
    .line 36
    move-result v4

    .line 37
    :cond_0
    invoke-static {v4}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    .line 38
    .line 39
    .line 40
    move-result-object v3

    .line 41
    invoke-virtual {v1, v3}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 42
    .line 43
    .line 44
    goto :goto_0

    .line 45
    :cond_1
    invoke-static {v1}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->toIntArray(Ljava/util/ArrayList;)[I

    .line 46
    .line 47
    .line 48
    move-result-object v0

    .line 49
    invoke-direct {p0, v0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeSetPadMapping([I)V

    .line 50
    .line 51
    .line 52
    iget-object p1, p1, Lorg/dolphinemu/dolphinemu/features/netplay/model/ControllerMapping;->wiiRemotes:Ljava/util/List;

    .line 53
    .line 54
    new-instance v0, Ljava/util/ArrayList;

    .line 55
    .line 56
    invoke-static {p1, v2}, Ltdolphin/shaded/kotlin/collections/CollectionsKt__IterablesKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    .line 57
    .line 58
    .line 59
    move-result v1

    .line 60
    invoke-direct {v0, v1}, Ljava/util/ArrayList;-><init>(I)V

    .line 61
    .line 62
    .line 63
    invoke-interface {p1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    .line 64
    .line 65
    .line 66
    move-result-object p1

    .line 67
    :goto_1
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z

    .line 68
    .line 69
    .line 70
    move-result v1

    .line 71
    if-eqz v1, :cond_3

    .line 72
    .line 73
    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    .line 74
    .line 75
    .line 76
    move-result-object v1

    .line 77
    check-cast v1, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;

    .line 78
    .line 79
    if-eqz v1, :cond_2

    .line 80
    .line 81
    invoke-virtual {v1}, Lorg/dolphinemu/dolphinemu/features/netplay/model/Player;->getPid()I

    .line 82
    .line 83
    .line 84
    move-result v1

    .line 85
    goto :goto_2

    .line 86
    :cond_2
    move v1, v4

    .line 87
    :goto_2
    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    .line 88
    .line 89
    .line 90
    move-result-object v1

    .line 91
    invoke-virtual {v0, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 92
    .line 93
    .line 94
    goto :goto_1

    .line 95
    :cond_3
    invoke-static {v0}, Ltdolphin/shaded/kotlin/collections/CollectionsKt;->toIntArray(Ljava/util/ArrayList;)[I

    .line 96
    .line 97
    .line 98
    move-result-object p1

    .line 99
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeSetWiimoteMapping([I)V

    .line 100
    .line 101
    .line 102
    return-void
.end method

.method public final setHostInputAuthority(Z)V
    .locals 0

    .line 1
    invoke-direct {p0, p1}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeSetHostInputAuthority(Z)V

    .line 2
    .line 3
    .line 4
    return-void
.end method

.method public final startGame()V
    .locals 0

    .line 1
    invoke-direct {p0}, Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;->nativeStartGame()V

    .line 2
    .line 3
    .line 4
    return-void
.end method
