# R149 — reparo pontual do Dolphin ao abrir GameCube offline

A R149 é candidata assinada sobre a R148. A referência estável continua R143.
O código e a receita de reconstrução estão no commit
`ef5d00b189a4a57bb2044e297b2f1b9b4fa90ce0`, em
`integration/dolphin-onpause-r149/recipe`. A R149 ainda não foi validada em
partida física nem cadastrada no servidor.

## Causa comprovada

No A56, The Legend of Zelda: The Wind Waker mostrava “Não foi possível preparar
o Dolphin. Volte e tente novamente.” A captura registrou `LinkageError` antes
de iniciar a emulação: `EmulationActivity.onPause()` tentava sobrescrever
`FragmentActivity.onPause()` declarado `final`. Isso surgiu na integração
online R126 e também está presente nas candidatas R128, R134, R143 e R148;
não foi introduzido pelos ajustes visuais recentes.

O DEX10 da R149 remove somente o atributo `final` do método base e torna
`public` o método filho. Corpo de ambos os métodos, chamada de pausa online,
cadeia de herança e demais bytes de código foram preservados. O DEX10 tem o
mesmo tamanho e a inversão do patch reproduz exatamente a entrada R148.
SHA-256 DEX10 final:
`1f1b285af161fbf85573c081bee3bc6e4c95f90485d8d405ae064b86feb9144e`.

## APK e kit

O APK assinado tem SHA-256
`698e8a7914cc7be2facc00e6701ff1f3533fa13f763358b51578a35d25c2741e`
e 2.715.089.935 bytes. Certificado original, esquemas v2/v3 e alinhamento de
16 KiB foram conferidos. Das 13.860 entradas, só cinco mudam: `classes10.dex`,
`assets/station-online/engines.json` e os três marcadores de motores
independentes. As outras 13.855 entradas, inclusive os demais 39 DEX,
`libturbo_carousel.so`, lógica de download, rota online, controles, CPU/JIT,
GameCube core e os ajustes de tela R148, são idênticas.

O kit privado R149, guardado no backup F:, tem SHA-256
`ed95ba61c92285937014a91e86b1dd7dd0a6928e10a9d063132973244e4eb5ec`
e 12.181.272 bytes. Contém seis ELF, vinte dependências e 78 modos revisados
(66 N64, nove GameCube, três Wii), sem nova aprovação PS1 HLE. O kit R148
anterior não cadastra os quatro IDs novos da R149. Consulte `STATUS.json` para
esses IDs, hashes e estados exatos.

## Estado de implantação

O backup do APK, kit e provas foi concluído, conforme
`outputs/recibo-backup-r149-dolphin-onpause.json` no workspace. A primeira
tentativa de atualização por USB no A56 em 14/10 falhou por espaço insuficiente;
o recibo está em `evidence/INSTALACAO-A56-20261014.json`. Na segunda passagem,
o instalador aguardou o desbloqueio do aparelho e não iniciou a instalação;
veja `evidence/INSTALACAO-A56-AGUARDOU-DESBLOQUEIO-20261014.json`.

Após o desbloqueio, a terceira passagem instalou a R149 no A56 com resultado
`SUCCESS` e conferiu no aparelho o SHA-256 do APK instalado, igual ao pacote
assinado acima. A atualização solicitou preservação de dados, sem desinstalação,
limpeza ou downgrade; o recibo sanitizado está em
`evidence/INSTALACAO-A56-SUCESSO-20261014.json`. O campo `appLaunched=false`
desse recibo se refere ao instante de conclusão do instalador. Depois disso,
o aplicativo foi aberto: `ESActivity` permaneceu em primeiro plano e os
registros mostraram carregamento de capas, sem `FATAL EXCEPTION` ou
`LinkageError` no trecho conferido. Ainda falta testar The Wind Waker offline
no aparelho para confirmar o reparo em jogo real. A instalação, sozinha, não
promove a candidata a estável.

O teste GameCube **offline** não depende de registrar o kit. Para partidas
online, o servidor precisa cadastrar o kit R149 correspondente com baseline
protegido fresco e registro aditivo sob `scan.lock`; não reaplicar R141 ou o
controle de banda como parte desta correção. Registro no servidor e teste de
partida online seguem pendentes. Não promover esta candidata ao consumidor.
