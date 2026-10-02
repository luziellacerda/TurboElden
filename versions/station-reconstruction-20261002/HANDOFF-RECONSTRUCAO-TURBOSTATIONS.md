# Handoff técnico da reconstrução TurboStations

## Estado atual

Este documento orienta a continuação do APK TESTE `org.turboramastation.frontend`. O cliente Station foi reconstruído em fonte Java, compilado para Android e testado localmente. **O login foi conectado ao cliente nos fontes e compilado. A ligação do catálogo nativo e o empacotamento em um APK novo continuam pendentes. O APK atual ainda contém as conexões antigas.**

A reconstrução está em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`. Os fontes novos ficam em `src\java\org\emulationstation\frontend\station`. A biblioteca compilada fica em `build\station-client.aar`; `build\dex\classes.dex` contém somente esse módulo. Não instalar esse DEX isolado nem simplesmente anexá-lo ao APK: isso manteria os dois clientes e não atenderia à substituição solicitada.

## Escopo e autorização

O mantenedor autorizou descompilar o que for necessário, recriar o código indisponível e criar/executar testes locais. O trabalho é somente no TurboStations. Os outros aplicativos Turborama e o servidor não foram modificados. As compilações, ferramentas e temporários desta reconstrução estão em E:.

## Fontes de verdade

| Evidência | Identificação |
| --- | --- |
| APK de entrada | `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk` |
| SHA256 da entrada | `d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b` |
| Tamanho da entrada | 1.898.675.776 bytes |
| Código das rotas Station | Servidor-pix `origin/feat/station-library-grant-20261002`, `b1159c9` |
| Última auditoria de produção consultada | Servidor-pix `origin/docs/auditoria-producao-station-20261002`, `07b4cab` |
| Identificadores de plataformas no catálogo vivo documentado | Handoff do servidor `ac86942`, oito plataformas e 996 itens |
| Git do aplicativo | Local `34d53ae`, remoto `versao-funcional` `0544607`, conforme auditoria inicial |

Todos os ramos do servidor foram atualizados para leitura com fetch nesta rodada. A auditoria 07b4cab relata 48 respostas 404 de capa, nenhuma capa 200 e nenhuma transferência completa de jogo comprovada. Esses números são do documento do servidor; não são novas medições feitas por este cliente.

O código do servidor, e não uma descrição antiga do handoff, confirmou: challengeId e sessionId são 64 caracteres hexadecimais; nonce, token e grant são Base64URL canônicos de 32 bytes; os erros usam a propriedade `code`.

## Componentes reconstruídos

| Fonte | Responsabilidade implementada |
| --- | --- |
| `StationApi` | Ativação, prova assinada pelo aparelho, abertura de sessão, perfil, catálogo, capa, autorização e download para área temporária. Confere assinatura RSA PSS, domínio, produto, aplicação, aparelho, licença, sessão e correspondência do challenge. |
| `StationHttp` | HTTPS com confiança do Android, verificação de hostname e pin SPKI. Somente as rotas Station enumeradas; sem redirects, sem fallback e sem URLs fornecidas pelo catálogo. Fecha conexão em sucesso, falha ou cancelamento. |
| `StationCrypto` | Reutiliza o alias Android Keystore `turborama.station.device.v1`. A chave privada não é exportada. |
| `StationSessions` | Um proprietário da sessão, token somente em memória, renovação sob demanda 15 segundos antes da validade de 180 segundos. Reutiliza `no_backup/station-license-id.txt`. Nenhum polling periódico. |
| `StationCatalog` | Modelo imutável com os cinco campos reais do servidor. Não fabrica URL nem extensão. Limite de 4096 itens, conforme StationLibrary. |
| `StationCatalogStore` | Guarda o envelope assinado de maneira atômica; releitura verifica assinatura e identidade. Cache é dado de exibição e exige uma sessão válida; nunca concede login. Rejeita queda de revisão. |
| `StationCoverStore` | Cache persistente por coverId e revisão, reaproveitamento de arquivo validado, limite entre requisições, espera após 429 e supressão temporária de 404 repetido. Não baixa capas no construtor. |
| `ExistingCoverCache` | Migração somente de leitura do cache anterior `station-covers/revisions.tsv` e imagens cuja revisão confere. Não apaga o arquivo anterior. |
| `StationFiles` | Arquivo parcial exclusivo, validação de tamanho, SHA256 calculado, hash esperado quando fornecido, sincronização e publicação atômica. Erro ou cancelamento preserva o destino anterior. |
| `StationPlatforms` | 50 mapeamentos locais comprovados e oito aliases do catálogo documentado no servidor. Plataforma desconhecida não vira pasta por aproximação. |
| `StationAndroid` | Composição real das dependências Android; valida dimensões e decodificação de capas com BitmapFactory. |
| `StationCoordinator` | Coordena o login, perfil, catálogo, cache, capas e autorização; negação da licença retira a autorização da interface. |
| `auth/LoginActivity` e `auth/StationLogin` | Layout atual ligado ao controlador, consulta fora da thread visual, retomada da licença salva, cancelamento ao destruir a tela e retirada da senha local nos fontes reconstruídos. |

O limite do envelope de catálogo foi elevado para 12 MiB para acomodar os 4096 itens máximos com textos Unicode escapados e Base64URL; capas continuam limitadas a 5 MiB, conforme servidor. O catálogo vivo documentado de 996 itens não é o limite contratual.

A busca estática no fonte novo não encontrou Squareweb, Miami, drawers, LocalPassword, LocalCatalog, GameDownload ou `station.invalid`. Isso comprova a ausência no **módulo novo**, não a retirada desses componentes do APK atual.

## Testes e limites da evidência

`build/test-results.json` registra os resultados e hashes dos fontes. A última execução completou:

- 19 verificações de gravação, integridade, cancelamento e preservação do destino.
- 68 verificações de protocolo e catálogo, com autoridade RSA criada somente para os testes.
- 36 verificações de sessão, cache, migração de capas e mapeamento de pastas.
- 19 verificações de integração entre login, perfil, catálogo, capas, renovação e bloqueio.
- Compilação contra Android API 34 em bytecode Java 8.
- Geração de DEX com API mínima 26 e biblioteca AAR.

Total: **142 verificações locais**. As respostas dos testes são controladas em memória e seguem os campos lidos no servidor. Isso não é teste autenticado contra produção. O caminho BitmapFactory foi compilado, mas não executado no Android nesta rodada. Não houve medição de desempenho de GPU ou alteração dos emuladores.

O telefone voltou à USB durante a rodada. O pacote instalado informa versão `1.0.8-turboeden-unico`, código 11, última atualização em 02/10/2026 às 16:47:06 e cerca de 2,9 GiB livres. O Android recusou `run-as` porque o pacote não é depurável; dados privados não foram lidos. Nenhum APK foi instalado nem jogo encerrado nesta rodada.

## Recuperação nativa

Foi analisada uma cópia exata de `libmain.so` do APK de entrada, SHA256 `a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8`. Ghidra produziu 455 saídas de funções, incluindo thunks, sem falhas de descompilação. Isso é pseudocódigo de análise, **não o projeto C++ original nem fonte diretamente recompilável**.

Os arquivos estão em `decompiled`, com `functions.tsv` e `references.tsv`. O projeto Ghidra e os logs foram preservados. Os endereços da saída Ghidra têm base de imagem 0x100000 adicionada; para confrontar com `native_carousel.cpp`, subtrair essa base.

Foram recuperadas as responsabilidades de CatalogService, CatalogItem, GuiStore, LicenseService, TelemetryService e ponte HTTP. O renderer e os motores continuam no binário original. `native_carousel.cpp` também depende de endereços e layout desse binário; recompilar somente esse arquivo não recompila GuiStore.

### Dados recuperados para orientar o código novo

`CatalogItem` ocupa 0xe8 bytes no arm64 analisado. Os campos string observados ficam em: id 0x00, nome 0x18, URL de jogo antiga 0x30, URL de capa antiga 0x48, rótulo de plataforma 0x60, pasta 0x78, nome de arquivo 0x90, caminho local 0xb0 e capa local 0xc8. Há flag de instalação em 0xa8. Os bytes finais 0xe0 a 0xe2 participam do estado de capa; seus significados individuais ainda precisam ser fechados antes de reproduzir o layout em código.

`CatalogService` ocupa 0x138 bytes. Foram observados estado em 0x50, vetor de itens em 0x88, revisão em 0xa8, contagem de instalados em 0xb0, vetor pendente em 0xd0, pedidos de capas em 0xe8, prioridade de capas em 0x100 e downloads ativos em 0x120.

| Função original | Endereço sem a base Ghidra | Uso na reconstrução |
| --- | --- | --- |
| refresh | 0x18f790 | Substituir origem do catálogo por snapshot Station direto |
| parseItems | 0x1904f0 | Eliminar leitura de gavetas e URLs antigas |
| adoptItems | 0x192778 | Publicação do catálogo para a interface |
| updateCovers | 0x192f10 | Conectar coverId ao caminho local validado |
| updateDownloads | 0x193cfc | Estado de transferência e instalação |
| applyPendingCatalog | 0x194924 | Momento seguro para trocar o modelo mostrado |
| refreshInstalledState | 0x194a60 | Reconciliar jogos existentes sem confundir parcial com instalado |
| startDownload | 0x1961ec | Autorizar itemId e instalar artefato confirmado |
| cancelDownload | 0x196a2c | Cancelar a operação e limpar somente seus temporários |
| uninstall | 0x196cd4 | Remover arquivos pertencentes ao jogo sem atingir saves |

A função antiga updateDownloads usa a existência do caminho para marcar instalação, inclusive após falha. O novo instalador deverá publicar um registro somente depois de validar e finalizar os arquivos. A troca do catálogo também deve manter o ponto seguro usado por GuiStore para não invalidar seleção, texturas ou downloads ativos.

## O que falta no aplicativo

1. Recriar o serviço nativo de catálogo e conectar suas ações ao cliente tipado, preservando o renderer e o design. A descompilação recuperou informações para isso; essa integração ainda não está implementada.
2. Empacotar a nova LoginActivity e ligar os controles de entrada/retorno da ESActivity ao mesmo proprietário da sessão. O login novo está compilado e conectado ao controlador nos fontes; LocalPassword e AuthSession antigos ainda estão no APK não alterado.
3. Implementar instalação e manifesto de arquivos com o descritor confirmado pelo servidor. O método atual novo `downloadToStaging` deliberadamente só baixa bytes; ele não cria entrada falsa em gamelist nem marca um jogo como instalado.
4. Remover as classes antigas e suas referências, os caminhos de rede de CatalogService, LicenseService e TelemetryService que pertencem ao frontend antigo. As conexões próprias dos motores devem ser auditadas separadamente.
5. Construir o APK completo, verificar classes e bibliotecas, testar no aparelho login, catálogo, capa, baixar, cancelar, jogar, apagar e voltar. Só então avaliar estabilidade.

## Dependências do servidor

O documento `HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md` descreve as informações ainda necessárias. O servidor entrega o jogo com Content-Length e tipo genérico, mas não fornece nome, formato ou hash assinado. Não existe fundamento para salvar todos os jogos como ZIP. Capas válidas também precisam responder 200 no índice do Linux.

## Reprodução e arquivos de build

Usar `prepare_test_dependency.py`, `run_tests.py` e `build_module.py`, nessa ordem. A dependência JSON de testes está fixada por SHA256 em `tools/json-dependency.json`; no Android é usado org.json da plataforma. Os scripts de edição de execução única na raiz são histórico da reconstrução e não fazem parte do build.

A máquina usa JDK 17, Python em `C:\Python314`, SDK em `G:\Android\Sdk` e D8 em `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar`. Nenhuma ferramenta foi instalada globalmente nesta rodada. Ghidra e JDK 25 portáteis estão em `tools`, com seus hashes em `tools-manifest.json`.

Não promover esta etapa como versão estável. O resultado entregue aqui é um módulo compilado e testado localmente, com integração do APK ainda pendente.

## Publicação do handoff no servidor

A pedido do mantenedor, o handoff foi publicado no Servidor-pix no commit `6a8fb3663ba40a53e4179f799e756b71a7398a8e`, ramo `docs/cliente-reconstruido-station-20261002`, arquivo `docs/station-android/HANDOFF-CLIENTE-RECONSTRUIDO-STATION-20261002.md`. Nenhum serviço do Linux foi alterado. A publicação contém o estado anterior à integração do login, com 123 verificações; este documento registra a etapa posterior com 142.
