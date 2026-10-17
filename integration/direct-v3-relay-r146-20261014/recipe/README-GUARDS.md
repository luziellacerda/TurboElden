# R146 — rota direta v3: receitas privadas para revisão

Esta preparação não compila nem monta produto antes de copiar o escopo para
`integration/direct-v3-relay-r146-20261014` e congelar um novo commit completo.
O ponto estável R143 e a candidata visual R145 ficam preservados.

## Base e alterações autorizadas

Base exata R145 `275f31b34145eb77c457b1a9c09bbff4034cc28a990b74121b0b1fd4573c5df0`,
2.715.057.167 bytes, fonte `25d10b2322d2e5687c9dfacc71a826c3955fad5d`.
Prova assinada parent `524b9a0bb0d9827cf76abb27377d69bfebd6d792b758674e6bb52ad024b9b2d2`.
Os 36 arquivos produtivos parent são conferidos no disco e no Git congelado.

DEX35 recebe exclusivamente `multiplayerEndpoint()`, uma nova fábrica TLS
`createMultiplayer()` e a troca de uma invocação no construtor de Channel.
São duas classes de 608; 606 classes, todos os outros métodos, campos e
inicializadores permanecem. A nova fábrica clona a fábrica existente,
alterando apenas o nome e o pin aprovado para a rota direta.

A construção parte do DEX R145 real, não de Activities/Session Java históricos.
Decodificação após montagem deve recuperar integralmente as duas classes por
inversão. Os mapas de métodos precisam coincidir com o escopo exato, incluindo
somente um método novo e nenhum campo/classe/remoção novo.

As outras 39 partições DEX e o carrossel nativo permanecem byte exatos.
Não há `--native` ou `--native-receipt` nas receitas desta etapa.
O ajuste de boot Dolphin estudado separadamente não integra a R146.

## Identidade e pacote

Somente DEX35 muda no payload completo de 345 entradas. As quatro identidades
independentes são renovadas usando as três implementações de marcador já
aprovadas, cujas fontes, ferramentas e políticas originais são guardadas.
Nove descritores RetroArch e oito IDs ativos permanecem. Cores, controles,
opções, HLE, cadastro por jogo, ticket/proof, READY/ACK e saída permanecem.

Cinco entradas do APK mudam: DEX35, engines.json e três wrappers de identidade.
13.855 de 13.860 entradas são preservadas, com zero adições ou remoções.
A verificação final relê todos os hashes, identidades canônicas, políticas,
exports/dependências/SONAME dos wrappers, certificado original, v2/v3 e 16 KiB.

`common.source_map()` e `build_dex.source_map()` usam a mesma closure:
arquivos `.py`, `.java`, `.smali`, `.txt`, `.json` em recipe/java/tests/evidence.
`route-scope.json` é a declaração executável pinada. README/PROPOSED-SCOPE
na raiz são documentação no Git e não são consumidos como código.

## Interfaces para o mantenedor

- DEX: `build_dex.py --base --jdk-bin --apktool --out --source-commit`.
- Identidade: `build_identity.py --base --dex-dir --dex-receipt --ndk --out --source-commit`.
- Montagem: `assemble_apk.py --base --dex-dir --dex-receipt --identity --out --source-commit`.
- Final: `verify_apk.py --base --apk --receipt --dex-dir --dex-receipt --java --apksigner --zipalign --out`.

Identidade, montagem e final aceitam `--parent-proof`, cujo default é a prova
R145 em E:. O hash esperado continua obrigatório mesmo ao recuperar em outra
unidade. Outputs produtivos ficam somente em
`E:/StationDirectV3RelayR146-20261014`; commit novo completo é obrigatório.
O APK unsigned se chama `TurboStations-Premium-R146-relay-v3-unsigned.apk`.

Os testes host usam certificados sintéticos e não demonstram handshake ou
gameplay físicos. Depois de assinado, ainda serão necessários o kit correspondente
às identidades finais e testes autorizados dos aparelhos. Nenhuma implantação,
instalação, aprovação HLE nova ou correção total de multiplayer é inferida pelo build.
