# TurboStations R19B — controles e configurações próprios do Nintendo 64

## Estado final conferido em 05/10/2026

**R19B instalada por atualização, com SHA-256 do `base.apk` igual ao candidato.** O recibo de instalação é `evidence/installation-r19b.json`; o campo `installed: false` do recibo de empacotamento registra o instante anterior à instalação e não deve ser usado como estado atual.

O jogo **007 - The World Is Not Enough** abriu pelo JOGAR em `paulscode.android.mupen64plusae.game.GameActivity`, com `CoreService` e os plugins próprios de vídeo, áudio, entrada e RSP. O recorte de inicialização de 15:22:39 a 15:22:41 não contém o fechamento anterior; uma consulta posterior ainda encontrou essa atividade em primeiro plano. A captura local mostrou a tela inicial do jogo. O mantenedor confirmou **controles de toque visíveis e respondendo**, e depois confirmou **menu próprio pelo Voltar do Android e retorno à TurboStations sem novo login**.

A USB caiu depois da captura inicial. Portanto a resposta dos botões e a saída são confirmação do mantenedor, não uma segunda captura ADB. Os controles somem após inatividade conforme o comportamento upstream e reaparecem ao tocar; não foi alterada a preferência no telefone. A entrada específica pela engrenagem é coberta pelos testes de despacho, mas não recebeu conferência visual nesta rodada. Não houve medição de FPS, validação de todos os jogos ou promoção a estável geral. Evidência consolidada: `evidence/n64-device-result.json`.

**Próxima integração deve partir do APK R19B e do overlay `native` desta pasta**, preservando os recursos corrigidos. Não voltar à R19, que ainda tinha o conflito visual. O trabalho visual R20 é separado e ainda não integra esta entrega.

## Revisão R19B após teste real no telefone

R19 `6e6e87a5...` foi instalada e a chamada ao Mupen64Plus AE foi observada. Na primeira abertura real de 007, GalleryActivity fechou com `ClassCastException`: o recurso `n6_appbar_scrolling_view_behavior` ainda nomeava a classe Material do aplicativo principal, incompatível com o CoordinatorLayout isolado do N64. Portanto R19 não é uma versão funcional completa do N64.

R19B corrige **11 referências de classes** nos fontes `resources/res/values/n6_strings.xml` e `n6_styles.xml`: sete comportamentos e quatro estilos com `viewInflaterClass`. O algoritmo reutilizável `merge_resources.py` também foi corrigido para realocar nomes de classes no texto e nos atributos XML. Não modifica recursos de outros emuladores.

A comparação semântica dos **43.618 recursos compilados** comprovou IDs/nomes idênticos e somente essas 11 referências alteradas. Outros **80.125 checks de recursos** passaram. `compiled-resource-tests.json` e `resource-tests.json` registram resultados. O recurso compilado foi reconstruído com apktool/aapt2, sem editar instruções ou substituir strings de outros módulos.

APK final preparado: `E:\ESTUDO APK\work\station-n64-controls-r19-20261005\TurboStations-N64-Controles-R19B-20261005.apk`, SHA256 **`c8fcb15f0951cf5874ac9de2fa2f2e9bfbe26813b7e9ddea5b897355cea4157c`**, 2.036.265.660 bytes. Sobre R18, duas entradas mudam: SO do carrossel e `resources.arsc` (SHA `1e33730bf8fc2b7bd4c6994c2254b2dffb3e44fff8b359e22a51627dde9103dd`); **13.079 entradas preservadas**, incluindo todos os DEX/motores. Assinatura e alinhamento16KiB conferidos. Conferência Android desta revisão final deve ser lida no recibo correspondente, não no primeiro recibo R19.

`fix_n64_resources_r19b.py` cria um projeto temporário de recursos a partir da árvore R15 congelada, aplica as correções e compila. `verify_archive_n64_resources_r19b.py` compara o resultado semanticamente com R18 e arquiva o APK intermediário de recursos em `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-n64-controls-r19-20261005\n64-resources-r19b.apk`. Após a conferência, o projeto temporário de recursos e a duplicata desse APK em E foram removidos para liberar espaço. Fontes finais alteradas, script de importação, `resources.arsc` e recibos permanecem em E. `package_n64_controls_r19b.py` reúne a correção do roteador e esses recursos sobre R18, preservando todos os demais arquivos.

R19 anterior está arquivada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-N64-Controles-R19-20261005.apk`, com hash conferido antes de remover a duplicata em E. Não instalar essa revisão anterior para resolver N64. Detalhes abaixo descrevem a primeira correção nativa, integralmente preservada pela R19B.

## Histórico técnico da primeira correção R19

## Pedido e escopo

Pedido do mantenedor em 05/10/2026: “emulador n64 esta usando menus controles do app quero que use controles do emulador”. O APK já contém o Mupen64Plus AE 3.0.249(beta) completo da R15. Esta entrega corrige seu encaminhamento, sem substituir controles por um desenho da Station nem modificar outro emulador.

Estado inicial deste documento: compilado, assinado e conferido no PC. Instalação e conferência Android são registradas separadamente em `device-evidence`; não inferir que gameplay foi aprovado a partir de testes locais. Não promover a estável sem essa evidência.

## Causa demonstrada no APK

Base exata: R18, SHA256 `a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4`. `libmain.so` SHA256 `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`.

1. `GuiStore::launchItem` resolve o comando por `LibretroPlayer::resolveCore` antes de chamar `LibretroPlayer::run`.
2. Na resolução de um motor incorporado, `resolveCore` extrai o nome e insere o prefixo `lib`. Instruções em `0x2a8e14..0x2a8e64`; a string em `0xc6477` é exatamente `lib`. A chamada a `run` em `0x2335ac` recebe o resultado resolvido.
3. `native_n64.h` da R15 reconhecia `mupen64plus_ae_android.so` e o identificador antigo sem prefixo, mas rejeitava `libmupen64plus_ae_android.so` e `libmupen64plus_next_gles3_libretro_android.so`. Com isso, delegava ao encadeamento antigo. O novo teste reproduz essa divergência e rejeita a versão anterior na primeira verificação.
4. O catálogo Java publica as pastas `nintendo-64` e `nintendo-64--br`. Esses identificadores exatos também estavam ausentes da seleção de comando N64. O ID de opções antigo `mupen64plus_next_gles3` precisava ser encaminhado ao menu próprio.

As instruções, hashes e testes estão em `resolver-evidence.json`, `bundled-prefix.txt`, `resolved-run.txt` e `tests.json`. Essa evidência demonstra os defeitos do despacho; não afirma qual ramo cada sessão anterior no telefone percorreu sem um registro daquela sessão.

## Correção

Único arquivo funcional alterado: `native/native_n64.h`.

- `n64PlatformKey`: nomes e aliases reais do catálogo, incluindo os dois identificadores de pasta e N64 BR.
- `n64Core`: aceita o nome completo do motor, o prefixo real `lib`, caminhos resolvidos e o ID de opções. Extrai o último componente e compara nomes completos; não utiliza correspondência genérica por trecho.
- `n64CommandHook`: usa a mesma identificação de plataforma para gerar `libretro: core=mupen64plus_ae_android.so`, o identificador interno de despacho da ponte Android.
- `n64RunHook`: mantém a chamada já integrada a `N64Bootstrap.launch`. Uma falha explícita de abertura retorna erro e não inicia o motor antigo como alternativa silenciosa.
- `n64SettingsHook`: encaminha as entradas N64 ao painel do Mupen64Plus AE.

Fluxo preservado: catálogo → arquivo instalado → ponte N64 → Splash/Gallery oficiais → GameActivity/CoreService oficiais, nos processos `:n64` / `:n64core`. Controles de toque, perfis, menu, saves e opções vêm do emulador integrado. As adaptações Java e bibliotecas da R15 são preservadas byte a byte; os recursos têm as 11 correções descritas na R19B. Consultar `versions/station-emulators-r15-20261005` para a proveniência e preparação do emulador.

## Testes e preservação

- 240 verificações C++ do código real de despacho: prefixo inserido pelo resolvedor, caminhos, nomes do catálogo, configurações, falha de abertura e delegação das outras plataformas.
- Código antigo rejeitado pelo mesmo teste.
- 3030 verificações de navegação R17 passaram novamente usando o novo conjunto de fontes.
- Android ARM64 compilado com NDK r28c, API26, C++17/O2, alinhamento16KiB.
- SO novo SHA256 `e0f13c18e0f6c4efe8e1d279422f9ed5516bd4f8cc21b7df1cf0ab1406fd248c`.
- APK R19 SHA256 `6e6e87a5befe55324569591a0cd0095c1cb94cb57e8ffea29433cafcdbf96819`, 2.036.266.368 bytes.
- Uma entrada alterada: `lib/arm64-v8a/libturbo_carousel.so`; 13.080 entradas preservadas. Assinatura original e alinhamento conferidos.
- Neo Geo `classes30.dex` continua `0d76beace3c7c427c670dc4cc59d60200d14b11f96b907fe79c8abc3e25d973f`; salas `classes35.dex` continua `8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae`. Station R16 offline/download, mídia, demais motores e navegação R17 continuam intactos.

## Caminhos canônicos e reconstrução

- Fonte/build desta entrega: `E:\ESTUDO APK\work\station-n64-controls-r19-20261005`.
- APK vigente: `TurboStations-N64-Controles-R19B-20261005.apk` nessa pasta. O APK R19 do histórico foi arquivado em G: e não é o candidato corrigido.
- Overlay nativo: quatro arquivos em `native`. Somente `native_n64.h` difere da base; cpp, navegação e download são cópias exatas do overlay R17.
- Demais headers, bibliotecas de ligação e `video720_posters.o`: `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native`. Não usar o cpp antigo de outra revisão como substituto.
- Base R18 preservada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-NeoGeo-Pastas-R18-20261005.apk`. Cópia/igualdade de tamanho e hash foram conferidas antes de remover só a duplicata APK em E. Fontes e recibos R18 permanecem em E.
- SO R17 anterior arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-single-folder-r17-20261005\libturbo_carousel.so`, SHA `4d2b962e09c7924e7b9b14042ee4b43e08d704bedae021131668303ae42fb39d`. Fontes R17 continuam na pasta original de E. Recibos dos dois arquivos estão nesta entrega.

`prepare_n64_controls_r19.py` prepara uma pasta nova; não repetir sobre a montagem atual. `test_build_n64_controls_r19.py` executa testes e compila o SO. `audit_n64_resolver_r19.py` registra a evidência da base exata. `package_n64_controls_r19.py` substitui somente o SO na base R18, alinha, assina e verifica todas as entradas; não sobrescreve um APK existente. `archive_*.py` documentam as operações já concluídas de arquivo, não devem ser repetidos.

Atualizar por `adb install --no-incremental -r --user 0`, sem desinstalar/limpar dados. Não corrigir configuração apenas no telefone: qualquer correção necessária deve entrar na fonte e no APK. Verificar em Android a abertura pelo catálogo e pela engrenagem, controles próprios, retorno sem login e seleção da coleção. Não alterar o servidor nem o contrato de catálogo para corrigir esse despacho.
