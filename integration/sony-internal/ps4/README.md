# PS4 interno — R131

Este owner usa o runtime Bionic real de Bachata S4 0.2.4 dentro do instalador local TurboStations. Não instala nem abre outro aplicativo. É exclusivamente offline. Jogos, saves, licenças e os motores existentes não são migrados por este módulo.

## Entrada e isolamento

| Elemento | Contrato |
|---|---|
| Application | `org.emulationstation.frontend.sony.Ps4Application`, criada pelo factory antes dos inicializadores nativos da Station |
| Activity | `org.emulationstation.frontend.sony.Ps4Activity`, privada, `singleTask`, processo `:station_ps4` |
| Jogo | `ACTION_VIEW` e URI `content:` validada pelo launcher; sem URI abre a preparação/informação interna |
| Nova solicitação | Preserva a sessão atual; não inicia outro motor nem troca a partida em andamento |
| Requisitos | Android 12/API31 ou mais recente, ARM64 e GPU compatível com o motor |

O bootstrap `org.emulationstation.ps4child.Ps4NativeEntry` pertence a um classloader filho. Somente os namespaces `org.libsdl.app`, `com.bachatas4.android.runtime` e `org.emulationstation.ps4child` são carregados primeiro pelo filho. As APIs Android e classes Station continuam no pai.

`owner.dex` contém as 67 declarações JNI SDL3 exatas e o adaptador de runtime/importação. O DEX completo do aplicativo estrangeiro, Hilt e seus recursos não são incorporados. `System.load` ocorre no bootstrap filho, com paths absolutos e a ordem de dependências conferida pelo manifest. A `libc++_shared.so` privada é a do PS4; nenhuma biblioteca raiz dos demais emuladores é sobrescrita.

## Preparação automática

`StationSonyAssets.prepare` verifica o manifest assinado pelo pin local da composição e prepara os arquivos privados. `Ps4Runtime` confere as 397 entradas do archive oficial, tamanhos e SHA256, rejeita caminhos externos/duplicatas/arquivos inesperados, promove uma staging atomicamente e mantém os arquivos não executáveis e somente leitura. O cache é novamente conferido por SHA256 no worker antes do uso. Nenhuma extração ou hash roda na UI ou por frame.

O runtime direto usa `NativeRuntimeBridge.run(Surface,false,argv,environment,cwd,-1)`. Os argumentos observados no upstream são `--override-root`, `--bachata-storage-root` e `--bachata-socket`. HOME, TMPDIR, XDG_CACHE_HOME, MESA_SHADER_CACHE_DIR e BACHATA_ALSA_SOCKET apontam para pastas privadas preparadas automaticamente. A rota Bionic não carrega o host GLIBC, X server ou Vortek.

Não há uma operação de pausa/rebind no bridge 0.2.4. O host mantém a mesma Surface/SurfaceTexture por meio do contrato Android de TextureView; retirar a View não dispara um `stop` automático nem um JNI SDL inventado. Sair/Back confirmado solicita o encerramento real. A liberação dos transportes e da Surface ocorre após o retorno nativo; somente o processo PS4 termina. Retenção ao bloquear/voltar ainda exige conferência física.

## Jogos e controles

Um PKG real passa por `nativeProbe` e `nativeExtract` oficiais. A importação acontece uma vez, em staging privada, com o passcode padrão upstream de 32 zeros. O material RSA comum do importador foi autorizado expressamente pelo mantenedor somente no APK local e permanece privado. Nenhum array, conta ou licença pessoal pertence ao Git.

Antes da promoção, o owner valida `eboot.bin` legível e `sce_sys/param.sfo`, obtendo o título e TITLE_ID reais. O nome do arquivo e amostras DEMO não são usados como prova de jogo. Um pacote inválido, incompleto ou que exija uma chave própria retorna erro explícito. Não há marcação falsa de prontidão ou configuração manual substituindo uma importação que falhou.

USB/Bluetooth seguem os eventos Android de gamepad/joystick: quatro slots, máscaras PS4 reais, eixos, deadzones, gatilhos e hat. Os snapshots BACHATA/1 são enviados por AF_UNIX privado, com sequência crescente e fila limitada/coalescida. O toque usa direcional, dois analógicos e botões PS4 estáticos; fica oculto ao conectar um controle físico. Seus eixos são separados dos eixos físicos. Foco perdido e desconexão enviam estado neutro.

O áudio implementa o protocolo binário BACHATA_ALSA_SOCKET: header de cinco bytes, Prepare4, PCM5 e Close0. AudioTrack e conversões de PCM ficam nos workers, com limites de payload e encerramento único. Não existe polling da UI para áudio ou controle.

## Artefatos e reprodução

| Artefato | SHA256 |
|---|---|
| APK oficial 0.2.4 | `4077b0d0b80e354c71eff1ce2c003f122449ac266eb27a6ac26744d3f9809a08` |
| DEX oficial inspeccionado | `0b33b62b7663370587fbcf1b14fdb54ba97990d9e7e205f50c8cbf976be56052` |
| owner.dex, 12.304 bytes | `6e10f4636be39a84cb4daefd0bc7968dd72cd2d56b1e3f33542ed6a38870dd81` |
| Runtime nativo | `5159ebdf1aa34713217e3598a0c084aa04ce59d623152fdbab501d293957c06a` |
| Importador PKG | `9e28ee2bc4b4909634a34402e3aa79c03300ed99327eb79c09e080a1995dc0ff` |
| libc++ privada | `8fed70ee5cf18534beebe28b525af8e422d08de3a241ccd3db7856f47048eda0` |
| Archive runtime, 110.834.547 bytes | `bfead069a93b6838dd0ce8f27021b0fe81a9f402e809de925cee86939724e87e` |

`recipe/build_owner.py` confere o APK/DEX oficial, regenera e compara as declarações JNI, compila Java8/API31/D8 e produz os arquivos privados `owner-derivation.json` e `derived.json`. O recibo contém hashes de fontes, receita, ferramentas e resultado. A composição consome `derived.json`; binários e material PKG não entram no repositório. O manifesto final da composição é a autoridade dos pins e do inventário empacotado.

## Evidência e limites

A compilação Java/D8 do filho passou. O root recompilou os hosts combinados após a revisão de lifecycle/input. Isso não é execução Android de um PKG nem validação de gameplay, Bluetooth/USB, áudio, retorno de background, estabilidade, FPS ou aquecimento. Não foi operado telefone ou servidor por este subtrabalho.

As árvores oficiais disponíveis fornecem core e protocolos, mas não contêm os módulos Android Gradle, C++ do bridge JNI ou CMake da versão nativa exata. Por isso os binários oficiais permanecem preservados, sem alegar reconstrução nativa integral. Jogos/firmware de console não são distribuídos por este módulo e compatibilidade universal não é prometida.

Fontes primárias: [release oficial](https://github.com/JICA98/Bachata-S4/releases/tag/v0.2.4), [metadados de fontes](https://github.com/JICA98/Bachata-S4/blob/edd2a74399a292552cc31e451fbb78713b6448a7/release-metadata/source-links.json), [core e protocolos](https://github.com/zenithblue-oss/shadps4-arm64/tree/be6bc2e9c60799e071dd2fafa6216e8d80ec619c), [notices do runtime](https://github.com/zenithblue-oss/shadps4-arm64/blob/be6bc2e9c60799e071dd2fafa6216e8d80ec619c/NOTICE.android-runtime.md), [TextureView](https://developer.android.com/reference/android/view/TextureView#setSurfaceTexture(android.graphics.SurfaceTexture)), [propriedade do FD em LocalServerSocket](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/master/core/java/android/net/LocalServerSocket.java). Core GPL-2.0-or-later e demais notices upstream devem acompanhar a entrega correspondente.
