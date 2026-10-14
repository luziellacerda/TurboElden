# R149 — reparo pontual do Dolphin ao abrir GameCube offline

A R149 é candidata assinada sobre a R148. A referência estável continua R143.
O código e a receita de reconstrução estão no commit
`ef5d00b189a4a57bb2044e297b2f1b9b4fa90ce0`, em
`integration/dolphin-onpause-r149/recipe`. A R149 foi instalada e testada no
A56, mas ainda não concluiu uma partida física nem foi cadastrada no servidor.

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
`LinkageError` no trecho conferido.

## Teste físico GameCube no A56

The Wind Waker foi aberto pela rota de jogar sozinho na R149. O Dolphin chegou
à sua própria tela de emulação e exibiu o aviso **“The disc could not be read
(at 0x55e3c040 - 0x55e3c060)”**. O erro anterior de ligação de
`EmulationActivity.onPause()` não reapareceu na tentativa capturada. Isso
confirma que o motor passou pelo ponto que antes impedia sua abertura, mas **não
confirma jogo funcional**: a partida ficou bloqueada pela leitura da mídia.
Após o aviso, o usuário saiu do jogo e confirmou que o TurboStations voltou
normalmente à lista de jogos, sem travar. Esse retorno valida a saída nessa
tentativa; não valida a execução da partida, que segue bloqueada pela mídia.

O item do catálogo `station_12b835c9539b4800a6bb29ca00a25f94` aponta um
arquivo `.iso` de 546.776.387 bytes e SHA-256
`3106a01516f59854a55fd6343da8b0f489ca8cfc523f300bb1913d7f1c602a2f`.
O arquivo baixado no A56 coincide com esse hash. O início do intervalo que o
Dolphin não conseguiu ler corresponde a 1.440.989.248 bytes, além do tamanho
do arquivo anunciado. Seu identificador interno `GZLE01` também não corresponde
à edição “Europe” indicada no nome do catálogo. Esses dados apontam para a
necessidade de auditar o artefato e os metadados na origem; a igualdade de hash
mostra consistência com o catálogo, **não** que a imagem seja íntegra ou
reproduzível. O resumo sanitizado está em
`evidence/WINDWAKER-A56-MIDIA-20261014.json`; captura e registro completos
permanecem privados no workspace e no backup
`F:\TurboStations-Backup-Completo-20261011\desenvolvimento\R149-dolphin-onpause-20261014-provas\teste-fisico-a56`.

Antes de alterar outra lógica do aplicativo, verificar no servidor a imagem
original com um leitor/validador de GameCube, conferir tamanho e edição,
substituir ou corrigir o artefato se necessário, atualizar revisão e SHA do
catálogo, baixar novamente no A56 e repetir o teste offline. A R149 continua
candidata; não foi promovida a estável nem liberada ao consumidor.

O teste GameCube **offline** não depende de registrar o kit. Para partidas
online, o servidor precisa cadastrar o kit R149 correspondente com baseline
protegido fresco e registro aditivo sob `scan.lock`; não reaplicar R141 ou o
controle de banda como parte desta correção. Registro no servidor e teste de
partida online seguem pendentes. Não promover esta candidata ao consumidor.
