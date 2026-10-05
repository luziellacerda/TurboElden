# TurboStations — abertura offline após ativação — 05/10/2026

## Atualização: R16 instalado e abertura offline conferida

APK conjunto `TurboStations-Desempenho-Offline-R16-20261005.apk`, SHA256 `b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1`, instalado por atualização e hash do base.apk conferido. A suíte conjunta passou **787 verificações em 16 suítes**. O estado abaixo descreve também a preparação isolada histórica; a entrega vigente é o R16 integrado em `E:\ESTUDO APK\work\station-download-performance-20261005`.

Em 05/10, 17:35 e 17:37 UTC, com Wi-Fi e dados móveis desabilitados e `Active default network: none`, o processo foi encerrado na biblioteca (nenhum emulador ativo) e o launcher foi aberto novamente. ESActivity retomou em 0,666s e 0,717s, respectivamente; isso é tempo até Activity retomada, **não tempo de toda a mídia pronta**. Catálogo local de **2162 itens** publicado, `CATALOG_CACHE status=0`, **zero rastros HTTP** e nenhum `CATALOG_NETWORK`. Na primeira captura após4s havia placeholders; na segunda, após12s ainda sem rede, as artes das plataformas/SNES e sinopse estavam visíveis normalmente. Não confundir a tag histórica `CATALOG_PUBLISHED status=503` (flag de cache) com resposta HTTP; não houve requisição.

Wi-Fi=1, dados móveis=1 e modo avião=0 foram restaurados e conferidos nas duas tentativas. Tela, licença, jogos e saves preservados. Nenhum comando de navegação ou início de jogo foi enviado. **Gameplay e capa de jogo offline no aparelho não foram conferidos**; o teste PC comprova resolução de jogo instalado e cache de capa sem rede. Abertura offline real do aplicativo e catálogo está confirmada. Não promover toda a versão a estável por este teste.

Evidências: `E:\ESTUDO APK\work\station-offline-access-20261005\device-check\result.json`, `offline-logcat.txt`, `offline.png`; primeira tentativa preservada em `device-check\first-boot`. A imagem final foi inspecionada. USB liberada para o outro chat após a conferência; ele reúne fonte, handoff e recibos no Git.

## Pedido e estado

Pedido do mantenedor: depois de registrado e liberado pelo servidor, abrir o sistema sem precisar estar online. Implementação preparada e testada no PC em `E:\ESTUDO APK\work\station-offline-access-20261005\client`. Não é novo contrato de licença emitido pelo servidor: é a política local do produto, solicitada pelo mantenedor, usando a evidência assinada já recebida do servidor. Não inventar campos de validade/offline, rotas ou tokens.

R15 instalado anteriormente: `d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b`. Este delta ainda não é APK instalado. Será unido à otimização de download de `station-download-performance-20261005` no R16. Não sobrepor seu Api/Files/Downloads/Installer nem os nativos N64/R14B. Não instalar o DEX offline isolado sobre o pacote combinado sem recompilar a união.

## Problema comprovado

Antes, `StationCoordinator.ready()` dependia de `StationSessions.peek()` e de um bearer ainda válido. `StationSessions.get()` abria nova sessão quando expirava, inclusive para entrar e ler capas já salvas. A sessão Station dura 180 segundos (renovação aos 165s); ela regula requisições ao servidor, mas não deve expulsar o comprador da biblioteca local. `login()` sempre consultava sessão/perfil/catálogo antes de abrir.

Contrato lido no clone existente do Servidor-pix, fonte `41837c695b880323441002d837c35b850f942cc3`, `src/TurboRamaSuiteOnlineServer/StationService.cs`: `catalog/v1` é assinado e contém productId, applicationId, licenseId, deviceId e sessionId; não contém accessToken ou prazo de autorização offline. `STATION_LICENSE_DENIED` e `STATION_DEVICE_DENIED` são negativas explícitas 403; `STATION_SESSION_INVALID` é 401 e não equivale sozinho à revogação da compra. Isto é leitura de código, não comprovação de implantação Linux.

## Caminho executável

1. `LoginActivity` mantém o fluxo visual e o checkbox Manter conectado. `StationLogin.begin` chama o coordenador em worker.
2. Sem novo código informado, `StationCoordinator.login` lê o licenseId salvo e tenta `StationCatalogStore.readLocal` **antes de qualquer HTTP**.
3. `StationApi.restoreLocalCatalog` confere RSA-PSS da autoridade fixada, keyId, schema, domínio catalog/v1, produto, applicationId, deviceId da chave atual no Android Keystore, licenseId e formato do sessionId histórico. Usa os bytes assinados existentes. Não cria Session nem Grant, não prolonga bearer e não persiste senha/token.
4. Catálogo íntegro + dono correto + nenhuma negativa persistida permitem biblioteca local imediatamente. Nome vem do perfil local do mesmo dono; ausência do nome não inventa comprador. Jogos são encontrados pelos recibos existentes. Capas pela chave coverId/revision existentes.
5. Sem cache válido (primeira instalação, cache corrompido, chave/aparelho diferente), permanece necessária uma consulta autenticada. Um licenseId avulso não libera o app. O primeiro catálogo precisa ter sido recebido com sucesso uma vez. Desinstalação/limpeza continua removendo dados privados e pode exigir nova ativação conforme o servidor.
6. `ready()` passa a representar biblioteca local já autorizada, independente do relógio e do bearer. Não existe prazo local artificial de dias. Jogos instalados abrem pela rota já existente, sem sessão online.
7. `StationCoordinator.cover` consulta `covers.cached` antes de adquirir lease. O cache preserva exclusão por imagem, conferência de revisão, validação de imagem e importação do cache anterior. Cache miss ainda usa o servidor; nenhuma capa inexistente é inventada.
8. `StationHttp.available` recebe conectividade Android (permissão ACCESS_NETWORK_STATE já consta no manifesto R15). `StationApi.exchange` falha imediatamente sem rede; primeira ativação, grants, capas ausentes e salas continuam exigindo conexão. Wifi conectado com servidor inacessível também não impede o boot local. TLS/pin/assinaturas/expiração e uso único dos grants permanecem.
9. Consulta automática do catálogo exige rede e primeiro plano; HTTP ocorre no próprio worker de poll após a abertura local. Somente a publicação do resultado entra na fila de comandos que resolve jogos instalados; um servidor lento não ocupa essa fila. Cancelamento/geração continuam descartando resultados antigos. Falha de conexão/503 mantém a biblioteca. Expiração/401 remove sessão online, preservando acesso local. Refresh manual informa falha sem apagar biblioteca.
10. Negativas explícitas de licença/aparelho recebidas pelo coordenador em catálogo/perfil/capa/download ou criação de sessão bloqueiam a biblioteca e gravam `<owner>.blocked`. O marcador impede restaurar o cache após reiniciar offline. Só catálogo novo autenticado remove o marcador. Falha ao gravar marcador tenta remover o cache daquele dono e falha fechada. Rejeição tardia de bearer antigo não derruba sessão mais nova.

## Limites reais

- Servidor não pode comunicar revogação a um aparelho desconectado. Sem rede, vale a última liberação conhecida; bloqueio só passa a ser conhecido ao consultar o servidor.
- A assinatura do catálogo prova que aquele conteúdo foi emitido para a instalação/licença. Ela não é um novo certificado de autorização offline emitido pelo servidor, nem prova de status remoto atual.
- Os módulos de salas mantêm suas autorizações online. Falhas opcionais de presença não fecham o catálogo; o poll do catálogo/fluxos do coordenador verificam a licença quando conectados. Nenhuma alteração em classes35/netplay ou em sua identificação de ROM foi feita aqui.
- Capas e jogos não baixados exigem internet. Vídeos/assets já empacotados permanecem locais.
- Não alterou servidor, APK instalado, telefone, emuladores, controles, saves, design, performance nativa ou configuração de tela.

## Arquivos

- `StationApi`: transporte disponível/offline, classificação precisa da negativa de licença, restauração assinada local com dono exato; rotas existentes preservadas.
- `StationSessions`: leitura validada do licenseId existente, sem novo bearer persistido.
- `StationCatalogStore`: leitura local, marcador de bloqueio por dono e liberação só após resposta autenticada nova.
- `StationCoordinator`: entrada local, vida útil independente da sessão, capa local antes de lease, tratamento das negativas.
- `StationCoverStore`: cache-only por imagem antes de sessão, mesma trava por chave.
- `StationHttp`/`StationAndroid`: verificação rápida da conectividade existente.
- `StationFrontend`: poll automático só quando há rede, aviso de negativa real.
- `StationLogin`: mensagem explícita para operação que exige conexão.

## Evidência PC e integração

`client/build/test-results.json`: **707 verificações** em 15 suítes, incluindo **48 casos offline**; compilação Android API34/bytecode Java8 passou. O teste novo usa assinaturas RSA reais de fixture, não servidor produtivo. Comprova boot offline sem requisições, ano offline/relógio reiniciado, capa persistente, jogo instalado resolvido, falta de capa, servidor indisponível, 401, bloqueio 403 antes/depois da sessão, bloqueio após reinício, reaprovação, cancelamento, assinatura/dono/autoridade alterados e ausência de bearer persistido. Um teste mantém a resposta de perfil parada em barreira enquanto outro worker lê acesso local, capa e recibo sem esperar a rede. Regressões de quatro capas/leases/grants/cancelamento/publicação também passaram.

Módulo offline isolado final compilado: DEX SHA256 `cd92ebc4b1193c805687018a0eb3380b6e2a9c84ebe44a11e4c281b201c3c92d`, 154520 bytes. É apenas evidência de compilação; **o DEX da união com downloads será diferente**.

`offline-delta.patch` SHA256 `02b9f583d0560e34c17cba7be432d9ca0b6f3817b09cfc4234354e84865d5ec1` contém apenas diferenças funcionais, sem confundir normalização CRLF com alteração. `offline-delta.json` identifica bases/resultados iniciais. Aplicar em seguida `offline-refresh-followup.patch` SHA256 `f28f3c6939c5378a6885dfcefb3acddfe99129a67f366cd4eec59dd1e0f512fd` (Frontend e teste offline; antes/depois em `offline-refresh-followup.json`). Mesclar sobre client R16 preservando seus arquivos e executar novamente a suíte conjunta. Reempacotar a base R15 preservando classes35/R12, todos motores (incluindo N64 completo), assinatura, mídia e dados.

Conferência Android pendente: atualizar sem desinstalar; abrir uma vez normalmente; retornar às plataformas e fechar o app; desabilitar temporariamente as conexões com estado registrado; abrir novamente; conferir nome, catálogo/capa já salvos, abrir jogo instalado e voltar; restaurar exatamente as conexões originais. Não testar com revogação real de cliente. Não marcar estável antes da conferência.
