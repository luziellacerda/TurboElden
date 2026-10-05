# R34 — recuperação de abertura online e Voltar Android

## Estado e impedimentos

Relato: Battletoads SNES, segundo jogador não entra, somente anfitrião tem Iniciar, controles mudam online, Voltar do telefone não responde. Usuário dispõe de uma conexão USB por vez: conferir primeiro jogador2, depois1 se necessário. **Nenhum aparelho apareceu conectado nesta etapa. Não há causa comprovada para a falha inicial do segundo jogador. Não declarar partida corrigida nem controles iguais.**

APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Salas-Retorno-R34-20261005.apk`, SHA `513dd4700192b994d93cdaf6cd55b79eccb804fa33eda43166304f5d2bcdb5ef`, 2053907144 bytes. Compilado, assinado e conferido no PC; NÃO instalado/testado em Android. Base R33 `9313b3b893468270512b8e8ee3fa984763d6db334b4534a2f863216a0cc4a7ea`. Apenas classes35.dex e um booleano de manifesto mudam.13.085 entradas preservadas, incluindo design/faixa R33, todos motores, servidor/auth/downloads. Runtime online `22ee3f67e4a5abf4625c2776928a8011a14c5ae0568d74d9576f4b49a9514905` e identidades de compatibilidade do servidor intactos. Não exige nova allowlist de motor.

## Achados confirmados no código

1. `StationRoomsActivity` só dá Iniciar ao host. Isso corresponde ao contrato: após ambos Pronto, host inicia; convidado abre automaticamente quando servidor passa a connecting. R34 explica isso ao convidado e mantém a regra; não libera start sem autorização.
2. O campo launchKey era registrado antes de pedir ticket/preparar/abrir Activity. Em erro continuava igual, bloqueando novas tentativas daquela geração. R34 oferece **Tentar abrir a partida novamente** quando a tentativa falha. É explícito; não dispara ciclos automáticos. Mantém proteção contra duplicatas. Não é prova de que esse foi o erro inicial do aparelho.
3. A Activity online tinha enableOnBackInvokedCallback=false e só onBackPressed. O runtime NativeActivity lê e consome eventos nativos. R34 habilita o callback oficial nessa única Activity e registra OnBackInvokedCallback no Android33+, removendo-o ao destruir. Confirmação Continuar/Voltar às salas, sem diálogos duplicados; dispatchKeyEvent/onBackPressed mantidos para eventos Java. **Caminho nativo em Android26–32 e funcionamento nos aparelhos ainda precisam validação**; não alegar correção universal.
4. SNES local usa Snes9x EX+; online usa bsnes-mercury/RetroArch com assets station-online/overlays/gamepads/flat/snes.cfg. Isso explica os controles diferentes. **R34 não muda motores nem controles**. Para conservar o arranjo que o usuário quer, ler primeiro o perfil/estado real do SNES local e adaptar/testar a interface online; não trocar core sem revisar o protocolo, compatibilidade e autorização do servidor.

## Funções e diagnóstico

StationLaunchPolicy extrai elegibilidade host/guest por estado e chave roomId:generation; testada em JVM. StationRoomsActivity mostra orientação ao convidado, adiciona recuperação explícita e repinta erro sem perder mensagem. StationGameSession registra sucesso de host-listening e classe/código de falhas da sessão; StationRetroActivity registra listener nativo e saída. Logs de fases em StationRooms, sem senhas/tickets/bearer/ROM/conteúdo de chat. Capturar a falha de jogador2 com esses registros e relacionar ticket/Activity/listener/ack. Não confundir sala pronta com handshake RetroArch concluído.

## Testes realizados

60 verificações de estado/feedback/arquivo e107 de convites/presença/ordenação;15 novas da política de abertura;7 contratos de fonte da recuperação/Voltar. Transporte isolado:39serviço,37HTTP,7túnelJava e17TLS, incluindo12.583.029bytes em cada direção. Identidades sintéticas e endpoints TCP de teste, **sem duas emulações Android nem servidor de produção**. Java8/API34, DEXmin26 compilaram. Assinatura e alinhamento16KiB passaram; todas entradas do APK comparadas. Manifesto validado por receita: só4bytes do booleano dessa Activity mudam. Esses testes não cobrem a falha de Battletoads no aparelho.

## Reprodução e fontes

Workspace `E:\ESTUDO APK\work\station-online-recovery-r34-20261005`. Restaurar delta sobre R33 usando SOURCE-MANIFEST.json; native/dep-src inalterados. Fontes completos de trabalho em netplay-src/dependency-src. Copiar receitas para a raiz do workspace (não executar diretamente de recipes no Git), testes para tests. Ordem: build_r34.py → prepare_manifest_r34.py → testes → package_r34.py. Arquivos de APK/SO/keystore/SDK não versionados. Build precisa station-client.jar de station-library-r10-build, Android34/JDK17/D8; testes JSONjar e serviço isolado R12 nos caminhos registrados. APKbase permanece G, temporáriosE.

## Próxima ação

Conectar o telefone do jogador2 com erro/sala aberta. Capturar versão/hash, Activity e logs antes de instalar; preservar saves/licença. Se houver partida, solicitar saída antes da atualização. Conferir mesmo jogo/edição/runtime dos dois; jogo do anfitrião pode continuar sem USB. Não alterar servidor ou liberar códigos de erro por suposição. Instalar somente como correção candidata. Ausência de erro em teste isolado não é comprovação de gameplay.

Referências: Android OnBackInvokedDispatcher https://developer.android.com/reference/android/window/OnBackInvokedDispatcher ; protocolo netplay https://docs.libretro.com/development/retroarch/netplay/ . Código upstream local RetroArch69a4f0ea1e8a confirma fila nativa; offline EX+ e overlay online verificados no projeto.
