# R137 — retorno da partida quando o motor nativo já terminou

## Motivo e escopo

No teste físico de Super Mario Kart no moto g52, o núcleo SNES foi selecionado, mas não confirmou prontidão (`nativeStatus=-1`, sem READY), apesar de PONG do túnel. O usuário tocou em “Sair da partida”; `closeSession()` completou, porém a Activity ficou aberta. A thread nativa de inicialização já havia terminado, e o retorno de `stationRequestQuit()` impediu o `finish()` Android. Ver [captura do incidente](../../audits/station-r137-super-mario-kart-exit-live-20261012/README.md).

A [receita de R137](../../integration/online-exit-r137/recipe/) substitui somente o retorno após `stationRequestQuit()` aceito por um desvio para o `finish()` que já existia. Continua enviando quit ao motor e leave humano ao proprietário da sessão. `closeSession()` é idempotente. Não altera espera, sincronização, servidor, controles, perfis, limites ou mídia. A origem do `nativeStatus=-1` continua pendente; esta versão evita que a saída dependa de uma thread de emulação já encerrada.

## Compilação e identidade

Donor R136 final assinado: SHA-256 `fd14c522f51e717a636febf1ab9dee1970217339f37880421238eb2f30ce7b05`. O DEX35 R136 `84b8aa3935a8e84eb69f8f7cc45885ac693e38bf1f26cfb07b811d3df60b8c05` foi recomposto como `dd6ea401376aafcba86518038fa2589c3d626c076cdcfc21252efca1a93ab6a9`; as 608 classes foram verificadas, 607 com projeção idêntica, apenas `StationRetroActivity` diferente. O APK preserva as outras 13.855 entradas e substitui DEX35, `engines.json` e três marcadores de runtime por exigência do vínculo de identidade. Assinatura original v2/v3, alinhamento 16 KiB e hashes de todas as entradas foram conferidos.

APK R137 assinado: SHA-256 `fe4bc08fbc1f36d2790831f6bcd9593204ec0a032ca0d3a42c1cd385bc272719`, 2.714.991.631 bytes. Ele foi instalado no moto g52 em 12/10/2026 às 02:54 (America/Fortaleza), após fechar o aplicativo preso com autorização do usuário. O recibo comprova hash integral do APK instalado, mesmo UID, data original de instalação e diretório de dados preservados; a tela inicial abriu. O binário e a chave ficam no backup privado; o Git contém receita e [recibos sanitizados](evidence/).

| Plataforma | ID vinculado à R137 |
| --- | --- |
| PSX | `pcsx-rearmed-ff81ed17-player-v3-c26d8836df25` |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-2f248cfcdc9e` |
| GameCube | `dolphin-5102a033-gamecube-v3-2e0b36222097` |
| Wii | `dolphin-5102a033-wii-v3-2e0b36222097` |

Esses IDs ainda exigem kit privado original, cadastro confirmado e resposta assinada fresca no servidor. A R137 não deve ser misturada com R135/R136 na mesma partida. O handoff correspondente está em `docs/station-android/r137/README.md` no repositório do servidor.

## Teste físico de saída

O usuário viu a tela de salas depois de “Sair”, e o log registrou `session-ended` às 02:56:17 e `native-activity-returned` às 02:56:19. A inspeção posterior do tombstone revelou que o processo nativo **abortou às 02:56:18 dentro de `stationRequestQuit()`**, antes de o desvio Java para `finish()` ser executado. `ALooper_wake` tentou usar um descritor inválido após o fim da thread de emulação. O retorno visual resultou da morte do processo privado, portanto **não valida a correção R137**. Não houve novo ANR, mas houve crash nativo. O jogo ainda carregava com `nativeStatus=-1`. Log bruto local SHA-256 `46a8aee86338b9f85d45d07be05cb55fb041ff98543739dbacba701841e8a61b`; tombstone SHA-256 `f49ff669755ea4ae1129374e83f99d2c057d7b8cb48c94036e2c2a1a339d0e75`.

## Aceite pendente

Corrigir primeiro o uso do looper nativo depois que a thread termina e validar saída sem crash. Repetir a saída em falha real de sinal no anfitrião e convidado. Depois, diagnosticar e corrigir o motivo do fim precoce do runloop para Top Gear 3000 e Super Mario Kart, registrar o resultado do servidor e comprovar gameplay de 2, 3 e 4 jogadores nas edições apropriadas. Errata R138: a fonte correspondente ao runtime instalado já suporta cinco posições; cinco ainda depende de teste físico e de um jogo cujo modo aprove cinco. Não homologar o catálogo inteiro com esta correção de saída.
