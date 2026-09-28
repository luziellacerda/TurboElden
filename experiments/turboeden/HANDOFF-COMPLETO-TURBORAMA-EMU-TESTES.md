# Handoff completo — TurboramaEmuTestes / Eden

**Atualizado:** 2026-09-28  
**Status:** handoff reavaliado contra o APK desmontado, a APK remontada e os repositórios Git. A APK de teste foi remontada, alinhada, assinada e validada estaticamente; não foi instalada nem executada em aparelho.

**Continuação:** foi criada uma variante de teste com o nome visível **TurboEden** e package ID próprio. Consulte [o handoff dessa variante](HANDOFF-TURBOEDEN.md). Este documento mantém o nome original para preservar a identificação e os hashes da APK examinada.

## Resumo executivo

O arquivo chamado `TurboramaEmuTestes.apk` é, pelos metadados internos, o **Eden**, um emulador de Nintendo Switch. Não é o TurboRetroEmu/EmulationStation. O pacote contém um motor nativo principal (`libyuzu-android.so`) para ARM64, integrado à interface Android por JNI. Isso é um único emulador de Switch, não um conjunto de “cores” Libretro para vários sistemas.

A APK remontada preserva o pacote, a versão e as sete bibliotecas nativas originais. A assinatura foi substituída por uma chave debug local. O DEX e os recursos foram reempacotados; a equivalência em execução ainda não está demonstrada. A revisão identificou [o código-fonte público do Eden v0.2.1](https://github.com/eden-emulator/mirror/tree/v0.2.1), possivelmente correspondente ao identificador `1f6734c`. Isso corrige a conclusão anterior de que faltava o projeto C++.

## Resposta: temos todos os cores?

Não no sentido de uma coleção de cores de múltiplos consoles. Este APK inclui o runtime nativo do Eden/Yuzu e seus componentes Android de suporte. O principal é `libyuzu-android.so`; o DEX contém a interface Android e as chamadas para o motor.

As outras seis bibliotecas não são seis cores de emulação. Há uma camada de validação Vulkan, suporte AndroidX e bibliotecas auxiliares de hooks. Os nomes sugerem alguns papéis, mas o funcionamento interno completo não foi estabelecido apenas pelo nome do arquivo.

O APK inclui o motor, mas não inclui jogos, firmware ou chaves de descriptografia. Esses insumos precisam ser dumps próprios do usuário. O guia do Eden lista firmware, keys e jogos obtidos do próprio console como pré-requisitos: [Quick Start do Eden](https://github.com/eden-emulator/mirror/blob/master/docs/user/QuickStart.md).

## Identificação e integridade do original

| Campo | Valor observado |
|---|---|
| Arquivo de entrada | `E:\ESTUDO APK\work\TurboramaEmuTestes.apk` |
| Tamanho | 24.970.363 bytes |
| SHA-256 | `BEFBF70B1A05715811FE092EF9CF71E6F1C1672008A6C5CAA31D633E99615668` |
| Pacote | `dev.eden.eden_emulator` |
| Nome / versão | `Eden` / `1f6734c` |
| versionCode | `32873047` |
| minSdk / targetSdk | 24 / 36 |
| Arquitetura nativa presente | `arm64-v8a` |
| DEX | `classes.dex` (um arquivo, 4.948.756 bytes) |
| Requisito do manifesto | Vulkan obrigatório; touchscreen e gamepad opcionais |

O nome externo do APK é apenas um nome de arquivo. Os metadados do manifesto identificam Eden/Yuzu.

O certificado de assinatura do APK original tem SHA-256 `7fca26483b2d1b3dc3e6d9bb836e2fee18f09dc644353befd2fce8606bd2a40a`. Esse digest é diferente do certificado debug da APK de teste.

## Inventário das bibliotecas nativas

| Biblioteca ARM64 | Tamanho | Interpretação sustentada pela evidência |
|---|---:|---|
| `libyuzu-android.so` | 35.518.648 bytes | Motor de emulação principal. A interface Java declara métodos JNI para iniciar/parar emulação, consultar firmware e keys, aplicar configurações e conectar superfície gráfica. |
| `libVkLayer_khronos_validation.so` | 24.616.200 bytes | Biblioteca de camada de validação Khronos para Vulkan, conforme o nome. Não é outro emulador. |
| `libhook_impl.so` | 272.424 bytes | Biblioteca auxiliar de hooks; finalidade interna completa não confirmada só pelo nome. |
| `libandroidx.graphics.path.so` | 10.096 bytes | Componente gráfico AndroidX. |
| `libgsl_alloc_hook.so` | 4.312 bytes | O nome indica hook ligado a alocação de memória; finalidade interna não confirmada só pelo nome. |
| `libmain_hook.so` | 4.216 bytes | Hook auxiliar; detalhes não confirmados só pelo nome. |
| `libfile_redirect_hook.so` | 4.000 bytes | O nome indica redirecionamento de arquivos; detalhes não confirmados só pelo nome. |

Na APK remontada, comparei cada `.so` com a entrada correspondente do original: **7 de 7 bibliotecas ARM64 são byte a byte idênticas**. Também há os perfis `assets/dexopt/baseline.prof` e `baseline.profm`. Não encontrei jogos, firmware ou `prod.keys` nos assets extraídos.

## Como o aplicativo funciona — auditoria de funções

O fluxo reconstruído pelas classes Android e pelas assinaturas JNI é:

1. `YuzuApplication.onCreate` inicializa utilitários de armazenamento, controles, tempo de jogo, parâmetros do driver GPU e canais de notificação. `MainActivity.onCreate` monta a interface, inicializa o multiplayer e direciona ao assistente inicial quando necessário.
2. `SetupFragment` conduz a configuração inicial. O código consulta presença de keys e firmware e exige ao menos uma pasta de jogos para concluir o preparo. Os arquivos externos são selecionados pelo Android; o APK não os fornece.
3. `GamesViewModel` e `GameHelper` consultam pastas configuradas, percorrem arquivos e montam a biblioteca. O código inclui leitura de contêineres de conteúdo externo, inclusive extensões `nsp` e `xci`.
4. Ao abrir um título, `EmulationFragment` escolhe configurações globais ou específicas do jogo, prepara driver e conteúdo associado e solicita uma sessão para o caminho do jogo. `EmulationActivity` administra eventos de controle, sensores, pausa, retorno e troca/saída. A superfície Android é entregue ao código nativo.
5. `NativeLibrary` carrega `libyuzu-android.so` via `System.loadLibrary("yuzu-android")`. As chamadas JNI incluem `initializeSystem`, `initializeGpuDriver`, `applySettings`, `run(path, programIndex, frontendInitiated)`, `surfaceChanged`, `pauseEmulation`, `unpauseEmulation` e `stopEmulation`. O manifesto exige Vulkan; só há binários ARM64 neste APK.

| Área | Evidência concreta no programa desmontado | Alcance da conclusão |
|---|---|---|
| Primeira configuração e arquivos | `SetupFragment`, `NativeLibrary.areKeysPresent`, `isFirmwareAvailable`, `installKeys`, `installFileToNand` | Fluxos de seleção, checagem e instalação presentes; importação real não ensaiada. |
| Biblioteca de jogos | `GamesViewModel`, `GameHelper.getGames`, `NativeConfig.getGameDirs`, `GameHelper.mountGameFolderContent` | Varredura de pastas e conteúdo externo presente; reconhecimento de cada formato não testado. |
| Sessão de emulação | `EmulationFragment.finishGameSetup`, `EmulationActivity`, `NativeLibrary.run`, `surfaceChanged`, `stopEmulation` | Encadeamento Android → JNI confirmado; execução de jogo não testada. |
| Configurações por jogo | `NativeConfig.initializePerGameConfig` e `reloadGlobalConfig` chamados em `EmulationFragment` | Seleção entre perfil do jogo e configuração global presente. |
| GPU e driver customizado | `GpuDriverHelper.initializeDriverParameters` passa diretórios de hook, driver e redirecionamento a `NativeLibrary.initializeGpuDriver` | Preparação e interface presentes; compatibilidade do driver depende do dispositivo. |
| Entrada e interface em jogo | `InputHandler`, `InputOverlay`, métodos de superfície, sensores e teclado em `EmulationActivity`/`NativeLibrary` | Suporte de interface para gamepad/toque e ciclo de vida presente; mapeamentos físicos não ensaiados. |
| Conteúdo adicional | JNI `getPatchesForFile`, `installFileToNand`, `removeDLC`, `removeUpdate`, `removeMod`, `verifyGameContents` | Interface para patches, DLC, updates e mods presente; cada operação depende do conteúdo e do motor nativo. |
| Usuários e saves | JNI `createUser`, `setCurrentUser`, `getAllUsers`, `getSavePath`; `ProfileManagerFragment` | Gerência de perfis e acesso a saves presentes. |
| Amiibo | `EmulationFragment.showAmiiboDialog`, JNI `loadAmiibo`, `getVirtualAmiiboState` | Fluxo virtual no app presente; leitura NFC/dispositivo não validada. |
| Multiplayer | `NetPlayManager` declara criar/entrar/sair de sala, listar salas públicas, chat e moderação; `MainActivity` chama `initMultiplayer` | Interface e chamadas nativas presentes; conectividade/servidores não testados. |
| Atualizador | `NativeLibrary.checkForUpdate`, `isUpdateCheckerEnabled`; `MainActivity.downloadAndInstallUpdate`; `APKInstaller` | Verificação/instalação condicionais implementadas; endpoint e funcionamento atual não validados. |
| Diagnóstico e desempenho | JNI `getPerfStats`, `getShadersBuilding`, `playTimeManager*`, `getCpuSummary`, `getVulkanApiVersion` | Telemetria, tempo jogado e identificação do dispositivo expostos à interface. |

Esta é uma auditoria funcional por subsistemas e pontos de entrada. O APK contém milhares de métodos de terceiros e código C++ compilado; não houve execução ou prova formal de cada método interno. As 107 falhas de JADX exigem conferir em Smali qualquer detalhe decisivo de uma função que ele não conseguiu reconstruir.

A documentação atual recomenda ARM64, Vulkan, pelo menos 8 GB de RAM e atenção ao aquecimento; compatibilidade depende muito do SoC, GPU e driver. Adreno tende a ter melhor suporte segundo o guia upstream. Isso é orientação atual do projeto, não uma garantia para a build `1f6734c`; releases mais novas podem exigir Vulkan mais recente do que a declaração mínima deste APK. Consulte [arquiteturas e Android](https://github.com/eden-emulator/mirror/blob/master/docs/user/Architectures.md) e [releases do Eden](https://git.eden-emu.dev/eden-emu/eden/releases).

## Reconstrução e validações realizadas

- **Apktool 3.0.3:** decodificou manifesto, recursos, assets, bibliotecas, Smali e arquivos desconhecidos; remontou os 4.540 arquivos Smali em DEX.
- **JADX 1.5.6:** gerou 3.135 arquivos Java para inspeção. Reportou 107 erros. Trate o Java gerado como aproximação de leitura, não como fonte perfeita nem como fonte usada para recompilar.
- **Compilação:** feita de Smali e recursos Apktool, sem usar o Java aproximado de JADX como fonte. O DEX binário final difere do original, portanto a recompilação não prova equivalência de comportamento.
- **Comparação Smali após nova decodificação da APK de teste:** 4.540 classes presentes nos dois lados; 4.533 arquivos Smali idênticos e sete com diferença apenas na declaração explícita/implícita de valores padrão (`false`/`null`) de campos de bibliotecas AndroidX/Kotlin. Isso sustenta boa preservação estrutural do código Dalvik, com o limite de não ter ensaio em execução.
- **Comparação do pacote ZIP:** 1.262 entradas de arquivo no original e 1.265 na APK de teste; 109 entradas com mesmo nome e bytes iguais, 218 com mesmo nome e bytes diferentes, 935 nomes só no original e 938 só na APK de teste. Boa parte dos nomes de recursos mudou no processo Apktool; os dois assets e as sete bibliotecas nativas mantiveram seus bytes. Não trate a saída como reprodução binária do APK original.
- **Integridade da saída:** alinhamento ZIP verificado; assinatura APK v2 e v3 verificada; `aapt` confirmou pacote, versão e SDK; sete bibliotecas nativas comparadas sem alterações.
- **Ainda não feito:** instalação em dispositivo, inicialização visual do app, teste de GPU/Vulkan em aparelho, execução de um jogo ou teste de desempenho/compatibilidade.

### APK recompilada de teste

Arquivo entregue: `outputs\TurboramaEmuTestes-recompilado-assinado-teste.apk`  
Tamanho: 25.352.997 bytes  
SHA-256: `EF1AE37F9D32C6AEB899F08AC5203A70AE001517A5701A8A4CF21D21C9911C89`

Certificado usado: `Android Debug` local; fingerprint SHA-256 `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

Como a assinatura mudou, esta APK não atualiza por cima de outra instalação `dev.eden.eden_emulator` assinada com chave diferente. Para instalar como teste, faça backup dos dados da instalação anterior antes de removê-la. A assinatura debug não representa a chave de publicação original.

## Materiais locais

- APK original: `E:\ESTUDO APK\work\TurboramaEmuTestes.apk`
- Saída Apktool: `E:\ESTUDO APK\work\desmontado\TurboramaEmuTestes\apktool`
- Saída Java aproximada JADX: `E:\ESTUDO APK\work\desmontado\TurboramaEmuTestes\jadx`
- Build e intermediários: `E:\ESTUDO APK\work\desmontado\TurboramaEmuTestes\build`
- APK assinada de teste: `E:\ESTUDO APK\work\desmontado\TurboramaEmuTestes\build\TurboramaEmuTestes-recompilado-assinado-teste.apk`
- Cópia entregue pelo workspace: `outputs\TurboramaEmuTestes-recompilado-assinado-teste.apk`

## Relação com o repositório TurboElden

O branch `versao-funcional` de [TurboElden](https://github.com/luziellacerda/TurboElden/tree/versao-funcional) documenta outro aplicativo: pacote `org.emulationstation.frontend`, baseado em EmulationStation/SDL/Libretro. O APK desta tarefa é `dev.eden.eden_emulator`, baseado em Eden/Yuzu. Os fontes e arquivos do TurboElden não completam os cores nem reconstroem este motor.

## Código-fonte do Eden e correspondência de versão

Existe [tag público `v0.2.1` do Eden](https://github.com/eden-emulator/mirror/tree/v0.2.1), com projeto C++/CMake, aplicativo Android/Gradle, Kotlin e JNI sob `src/android`. A [release oficial v0.2.1](https://git.eden-emu.dev/eden-emu/eden/releases/tag/v0.2.1) aponta para commit `58c1e20ee5` e oferece builds Android. Um [relato no rastreador do Eden](https://github.com/eden-emulator/Issue-Reports/issues/671) associa explicitamente o build ID Android `1f6734c` à tag `v0.2.1`. Essa é uma correspondência forte para escolher a fonte de trabalho, mas **não foi comparado o hash deste APK ao binário oficial da release nem demonstrado que cada arquivo da APK deriva exatamente dessa tag**. Não se deve chamar o código recuperado por JADX de fonte original.

Para uma reconstrução de projeto editável, a base correta é o checkout de `v0.2.1` do Eden, mantendo dependências, submódulos, versões de NDK/CMake/Gradle e opções de build daquela revisão. A desmontagem deste APK ajuda a comparar manifesto, recursos, chamadas JNI e bibliotecas da distribuição específica. O Git TurboElden continua sendo referência de outro produto, não uma fonte intercambiável.

## Pendências e próximo ensaio

- Comparar este APK com o APK Android oficial da release `v0.2.1` por hash e por inventário de conteúdo, para determinar variante e eventuais modificações.
- Obter checkout completo da tag, dependências e ambiente de build compatível caso o objetivo seja recompilar **a partir de fonte editável**. Isso ainda não foi executado; a APK entregue é a remontagem do APK existente.
- Validar instalação, abertura, importação de dados próprios e execução de um título em aparelho ARM64 com Vulkan. Registrar SoC, GPU, driver, Android, Vulkan e logs da sessão.
- Se precisar atualizar uma instalação existente sem desinstalar, é necessária a chave de assinatura original; a chave debug local não substitui essa identidade.

**Conclusão prática:** o handoff anterior acertava a identificação como Eden, a ausência de cores Libretro e a validação estática da APK de teste. Ele errava ao afirmar que não existia o código-fonte C++ correspondente e exagerava a fidelidade da recompilação. Esta revisão corrige esses pontos, amplia o mapa funcional e separa evidência estática de comportamento ainda não testado.
