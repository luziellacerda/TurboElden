# R139 — recursos da Activity e propriedade JNI

Overlay mínimo sobre a fonte nativa R138, SHA-256 `e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2`. A fonte candidata é `native/source/frontend/drivers/platform_unix.c`, SHA-256 `24420118e5ce94376b077051084a84d4c52f152d00b9e2330333896bced798fb`. Este registro qualifica a fonte e testes locais; compilação Android, assinatura, instalação e aceite físico são estados separados.

## Falhas corrigidas

`android_app_create()` usava mutex, condição e estado salvo sem conferir a alocação. Falha na criação do worker deixava a interface esperando `running` para sempre, sem thread que pudesse sinalizar. Falha no pipe também perdia mutex e condição. A candidata confere cada recurso antes do uso, libera somente o que adquiriu e retorna `NULL` sem esperar/join quando nenhum worker foi criado. A `ANativeActivity_onCreate()` libera sua reserva e pede o fechamento da nova Activity na falha. O handshake normal com o worker continua igual.

A R138 criava uma chave TLS por lançamento e não a reutilizava/liberava; a referência estática era substituída. Seu destructor também dependia de `g_android->activity`, embora outras threads possam terminar depois da Activity. A R139 cria uma única chave do processo, guardando uma `JavaVM` estável. Falha de criação impede a thread nativa de começar; uma tentativa posterior pode repetir a inicialização. Outra VM é recusada. A chave não é apagada enquanto algum destructor pode usá-la. `StationRetroActivity` carrega a biblioteca com `System.loadLibrary`, mantendo a biblioteca vinculada ao class loader.

O getter mantém a exigência de contexto ativo (`g_android`) e consulta `GetEnv` para a thread atual. Uma thread já anexada por Java/outro proprietário recebe seu próprio `JNIEnv` e não recebe uma nova obrigação de detach. Somente um `AttachCurrentThread` realizado pelo helper é registrado na chave TLS, com `JavaVM*`. Falha no registro desfaz somente esse attach recém-criado. O destructor recebe a VM estável e desanexa sua própria thread, mesmo depois de `g_android` ser limpo; não guarda `JNIEnv` de outra thread nem usa Activity liberada.

Um mutex exclusivo de TLS protege inicialização e snapshot de VM/chave. O getter solta esse mutex antes de qualquer chamada à VM. Reutilizar `station_activity_mutex` criaria inversão com `android_app_destroy` (app mutex → getter) e `stationRequestQuit` (Activity mutex → app mutex); por isso esses monitores permanecem separados.

## Escopo verificável

O único arquivo produtivo é `frontend/drivers/platform_unix.c`. A receita modifica `android_app_create`, `jni_thread_getenv`, `jni_thread_destruct` e os dois ramos necessários de `ANativeActivity_onCreate`; acrescenta um helper e as declarações da chave/VM/mutex. A inversão das substituições deve reproduzir a fonte R138 byte a byte. As fontes históricas ficam intactas.

Runloop, FPS, frequência dos timers, áudio/vídeo, recuperação, sockets, READY/ACK, roster, cores, opções e capacidades mantêm seus bytes anteriores. Esta mudança evita falhas de recursos e ownership; nenhum teste daqui mede temperatura, uso real de CPU ou desempenho Android.

## Reprodução

Gerar uma saída nova a partir da R138 pinada:

```text
python recipe/patch_resource_lifecycle.py CAMINHO_R138/platform_unix.c --output CAMINHO_NOVO/platform_unix.c
```

A receita recusa outra fonte base e não sobrescreve uma saída existente. Uma saída dentro do repositório deve ficar somente neste overlay nativo novo. Para os testes Windows, fornecer compilador Clang, diretório de trabalho absoluto, novo e fora do repositório, e recibo JSON novo:

```text
python recipe/test_resource_lifecycle.py CAMINHO_R138/platform_unix.c --compiler CAMINHO_CLANG/clang.exe --work DIRETORIO_TESTES --receipt CAMINHO_RECIBO.json
```

`tests/resource_tls_harness.c.in` contém fixtures das bordas Android/JNI/alocação/FD e do handshake de worker. As quatro funções produtivas e o helper são extraídos sem edição. Mutexes, threads e callbacks FLS de término de thread são eventos reais no Windows. Um wait/null inválido da base é registrado antes de travar/crashar o host.

`evidence/native-resource-tests.json` registra 24 cenários da candidata: seis falhas de recursos e a falha inicial da chave; sucesso; recuperação após falha de chave; 100 lançamentos; criação concorrente em 32 threads; 640 consultas em threads Java/nativas; destructor depois de limpar `g_android`; Attach/GetEnv/setspecific falhando; VM divergente ou ausente; ausência de contexto ativo; quatro combinações de estado salvo presente/ausente e tamanho zero/positivo. Chamadas da VM reentram no helper para conferir que seu mutex já foi solto.

`evidence/recipe-path-guards.json` registra oito recusas de argumentos que tentariam reaproveitar pasta/recibo ou escrever em fontes históricas. Nenhuma dessas chamadas cria saídas, e os cinco inputs protegidos permanecem exatos. Os testes de TLS/alocação não procuram USB nem abrem conexões externas.

Na base, 100 lançamentos criaram 100 chaves; na candidata, uma. As 16 threads Java não foram desanexadas pela candidata; as 16 threads nativas anexadas pelo helper tiveram detach na própria thread. Cada falha de startup da candidata termina com zero alocações/FDs da fixture, reserva liberada e uma solicitação de fechamento. A base reproduz a espera sem worker, campos inválidos e vazamento de recursos. O handshake Android e a concorrência com drivers reais ainda exigem teste físico.

## Integração do pacote

Usar a árvore correspondente exata R138, aplicar somente este arquivo e compilar pelas flags/NDK vigentes. Conferir a base reconstruída e o diff do manifesto de todas as fontes. Um runtime final diferente exige identidade real, cadastro e recibo do pacote conforme o contrato existente. Preservar certificado, dados, jogos e saves; repetir início/saída e a operação online nos aparelhos. Não publicar esta fonte como APK instalado sem seus recibos próprios.
