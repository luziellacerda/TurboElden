# Handoff técnico de continuidade — Station estável SNES / Mega Drive

## 1. Leitura obrigatória e alcance

**Destinatários:** equipe Android TurboStations e equipe backend/operacional Servidor-pix. Este documento fecha o fluxo de conteúdo observado em 03/10/2026 e define a continuidade. Não é ordem de implantação no Linux nem autorização para modificar outros produtos Turborama. A publicação foi solicitada pelo mantenedor como **estável SNES e Mega Drive**.

Referência Git: branch e tag `estavel-station-snes-megadrive-20261003`. O commit da tag identifica juntos os fontes, correções, inventários, evidências e este documento. O manifesto é [MANIFESTO-ESTAVEL.json](../../versions/estavel-station-snes-megadrive-20261003/MANIFESTO-ESTAVEL.json); a recuperação é [RESTAURACAO.md](../../versions/estavel-station-snes-megadrive-20261003/RESTAURACAO.md).

O fluxo comprovado é: **sessão → perfil → catálogo → capa → autorizar → transferir → conferir hash → extrair → registrar → jogar → voltar com login preservado**. Foram instalados e abertos Battletoads in Battlemaniacs (SNES) e Cutthroat Island (Mega Drive). O mantenedor confirmou o retorno normal de ambos; o app mostrou dois instalados após reinício. Isso não comprova todos os 1.816 jogos, todos os motores, todos os celulares ou o painel comercial completo.

**Regra permanente:** consertos necessários à instalação devem existir no fonte e no APK. Não criar pastas/copiar recursos no telefone como solução exclusiva. Não desinstalar nem limpar dados para diagnosticar: isso elimina a chave privada Android e exige transferência oficial de licença. Preparação automática deve ser repetível e preservar jogos, saves, BIOS existentes e identidade.

### Ordem das autoridades

1. Este documento + manifesto/evidências desta tag para o APK atual.
2. Fonte em `versions/station-reconstruction-20261002/`, mesmo conteúdo canônico de `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`.
3. [Retorno do servidor no commit exato fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61](https://github.com/luziellacerda/Servidor-pix/blob/fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md), branch `feat/station-artifact-descriptor-20261002`.
4. Handoffs anteriores são história, não identificação da versão instalada. Em particular, 996 itens, 176 SNES, os 404 antigos, o APK `fa3bc844…` e a ativação pendente não descrevem o resultado atual.

O retorno fa7a10c ainda pede testes do APK antigo. As provas abaixo atualizam essas pendências do lado Android; o servidor não foi alterado nesta entrega. Dados do serviço Linux aqui são **relato identificado do operador no Git**, enquanto as provas do telefone foram obtidas no aparelho.

## 2. Identidade congelada e pastas

| Objeto | Identificação exata |
|---|---|
| Pacote instalado | `org.turboramastation.frontend` — TESTE, separado do outro app |
| Namespace Java | `org.emulationstation.frontend` — não renomear por aparência |
| versionName / versionCode | `1.0.8-turboeden-unico` / `11` |
| clientVersion do protocolo | `1.0.8-station-storage-20261003.3` |
| APK SHA256 | `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17` |
| APK tamanho | `1902768022` bytes |
| Certificado SHA256 | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| APK congelado | `E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk` |
| Saída original de build | `E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build\apk\TurboStations-Station-CANDIDATO-20261003.apk` — o nome histórico não muda seus bytes |
| Fonte e build canônicos | `E:\ESTUDO APK\work\turbostations-reconstruction-20261002` |
| Mirror de fonte no Git | `versions/station-reconstruction-20261002` |
| Repo local app | `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git` |
| Clone existente do servidor | `E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002` — ler refs, não clonar outro nem trocar checkout |
| Base privada de empacotamento | `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk` |
| SHA256 da base | `d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b` |
| SHA256 libmain de entrada | `a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8` |
| Build temporário | Somente `E:`; `temp`, `build`, `tool-home` dentro da pasta canônica |

**O Git não contém APK, ROM, BIOS, firmware, saves, mídia privada, códigos de ativação ou chave de assinatura.** Contém os fontes disponíveis, scripts, contratos, hashes e provas sanitizadas. A base privada, as ferramentas e a assinatura já existente são dependências reais. Não declarar que este repo recompila todos os motores desde seus fontes originais.

## 3. Inventários rastreáveis entregues juntos

Na pasta [da versão](../../versions/estavel-station-snes-megadrive-20261003/):

- `INVENTARIO-FONTES.json`: caminhos, tamanhos e SHA256 de todos os arquivos de `src`, `tests`, scripts Python de montagem e contratos auxiliares presentes no módulo. Marca scripts de build; os demais scripts de edição são históricos.
- `FUNCOES-JAVA-COMPILADAS.txt`: saída integral de `javap -p -s` das classes do projeto presentes em `station-client.jar`, incluindo métodos privados, construtores, classes internas e descritores JVM. É um índice dos métodos efetivamente compilados, não uma lista adivinhada a partir dos nomes.
- `MAPA-FUNCOES-FONTE.md`: declarações Java/nativas com arquivo e linha para localização; ler os corpos no fonte. O índice compilado é a autoridade para assinaturas Java.
- `MAPA-PLATAFORMAS.json`: todos os nomes/aliases exatos, rótulos e pastas lidos de `StationPlatforms.java`. Mapeamento não significa acervo publicado nem motor homologado.
- `VINCULOS-NATIVOS.json`: os 32 endereços da base vinculados às funções reconstruídas. Só valem para a libmain com hash acima.
- `INVENTARIO-APK.json`: nome, tamanho e SHA256 de **cada entrada** do APK entregue, incluindo motores e recursos preservados; não contém seus bytes.
- `EVIDENCIAS-FLUXO.json`: resultados do aparelho, descritores dos dois jogos, correlações HTTP e limites dos testes.
- `MANIFESTO-ESTAVEL.json`: identidade do APK/base/servidor, dependências e escopo.

Não há fonte completo recuperado para cada função do renderer/launcher original. O inventário do APK identifica esses binários, e o mapa nativo delimita exatamente a parte substituída. Funções internas de bibliotecas de terceiros preservadas devem ser analisadas no projeto/versionamento correspondente antes de alterá-las.

## 4. Percurso completo no aplicativo

```text
LoginActivity + StationLogin
  → StationAndroid (composição única / Keystore / no_backup)
  → StationSessions.activate ou get
  → StationCoordinator.login (perfil + catálogo autenticado)
  → permissão de arquivos concedida → ESActivity existente
  → StationFrontend.configure → StationStorage.prepareRoot
  → StationInstaller + StationDownloads
  → StationPublication / JNI publishCatalog
  → StationCatalog_* em libstation_frontend.so
  → GuiStore/carrossel nativo existente

Capa visível → fila nativa → StationFrontend.cover
  → StationCoordinator.cover → StationCoverStore → cache ou GET autenticado
  → JNI publishCover(caminho local) → CoverImage/textura nativa

BAIXAR(itemId) → StationCatalog_start → StationFrontend.start
  → StationDownloads → authorize(itemId, revisão do catálogo)
  → reuso local por hash ou GET /artifacts/{grantId}
  → StationFiles (tamanho/hash) → StationInstaller (extração/manifesto)
  → recibo privado atômico → JNI publishJob(result=1, launchPath)
  → JOGAR → launcher/motor existente com o caminho real do recibo
  → saída normal do motor → reconciliação dos instalados → catálogo
```

Não existe reconstrução de URL de jogo a partir do título, pasta, slug ou CDN. `launchPath` é dado do descritor assinado. O carrossel recebe um caminho local de capa: o antigo truque `station.invalid` não é o transporte desta reconstrução.

### Mapa funcional por arquivo

Prefixo abaixo: `src/java/org/emulationstation/frontend/` no módulo.

| Arquivo/classe | Responsabilidade e conexão |
|---|---|
| `auth/LoginActivity` | Interface de entrada, opção Manter conectado, transição após acesso a arquivos; não inicia o frontend antes da permissão necessária. |
| `auth/StationLogin` | Adaptação da UI ao cliente comercial; usa ativação/licença e erros do serviço. |
| `station/StationAndroid` | Singleton do contexto Android; monta transporte, chave, sessão, caches e coordenador. Usa `getNoBackupFilesDir`. |
| `StationConfig` | Host HTTPS, pin TLS, chave pública/keyId da autoridade, produto, aplicação, clientVersion. Sem segredo de servidor. |
| `StationCrypto` | Chave privada do dispositivo no Android Keystore e assinatura da prova; preservar alias. |
| `StationProtocol` | Constantes de domínio, identidade, Base64URL canônico e limites do protocolo. |
| `StationHttp` | Nove rotas permitidas, HTTPS/hostname/certificado/pin, sem redirect/Location, correlação, timeout, cancelamento. |
| `StationApi` | Ativar, abrir sessão, perfil, catálogo, capa, autorizar e abrir/consumir stream; verifica envelopes, identidade, revisão, TTL e descritor. |
| `StationSessions` | Persiste apenas licenseId verificado, obtém/renova sessão em memória; não armazena código nem Bearer. |
| `StationCoordinator` | Dono da sessão do catálogo; login/refresh/cover/authorize/ready/logout; invalida acesso recusado. |
| `StationCatalog` | Interpretação tipada de itens, IDs, nomes, revisão, duplicidade, quantidade. |
| `StationCatalogStore` | Cache do envelope assinado vinculado ao proprietário; restauração verificada, não banco de URLs. |
| `StationCoverStore` | Cache persistente ID+revisão, validação, intervalo de pedidos e retentativa de indisponibilidade. |
| `ExistingCoverCache` | Reuso de capas anteriores somente conforme identidade/revisão verificável. |
| `StationPlatforms` | Tabela explícita plataforma→rótulo→pasta; desconhecido gera erro/aviso, sem inferência de slug. |
| `StationPublication` | Linhas publicadas para a ABI nativa; mantém os itens suportados e informa os desconhecidos. |
| `StationFrontend` | JNI, pools limitados, configuração da raiz, publicação, início/cancelamento/exclusão e ciclo foreground. |
| `StationDownloads` | Fila limitada de instalações; mesma sessão entre autorização e cabeçalhos GET; progresso e resultados. |
| `StationArtifact` | Valida os sete campos obrigatórios do descritor e limites; não escolhe um executável por aproximação. |
| `StationFiles` | Escrita temporária, contagem/hash, validação de bytes de imagem e substituição segura. |
| `StationExistingArtifact` | Procura limitada por tamanho/hash assinados nos diretórios anteriores autorizados. Nome igual sozinho não serve. |
| `StationInstaller` | Geração instalada, extração, launchPath, recibo, conferência, exclusão somente de arquivos pertencentes ao jogo. |
| `StationArchive` | Ponte Java para a extração libarchive do APK. |
| `StationStorage` | Cria raiz confiável ausente, resolve aliases de raiz do Android, confere escrita/links e consulta espaço compatível com Android. |
| `StationBundledFiles` | Copia assets com limites, arquivo temporário e reparo de ausentes/vazios, preservando arquivos existentes conforme política. |
| `AssetInstaller` | Prepara `bios` e `resources` reais do APK. Retira a dependência inexistente `packs/Dolphin.zip`. |
| `DownloadService` | Serviço Android de acompanhamento de transferência; consulta atividade dos trabalhos. Não é download paralelo antigo. |
| `StationDiagnostics` | Eventos e correlações sanitizados; hashes dos IDs, revisão, código HTTP e contagens. |

### Parte nativa

`src/native/station_frontend.cpp` implementa os serviços `StationCatalog_*`, `StationLicense_*`, `StationStats_*`, `StationCore_request`, `StationLoading_draw` e callbacks JNI. `station_catalog_abi.hpp` define os layouts que o renderer espera (string 24 bytes, item `0xe8`, catálogo `0x138`, progresso 48 bytes), com verificações estáticas. `station_cover_retry.hpp` contém a política de retorno à fila. `station_archive.c` liga libarchive à validação/extrator Java.

`link_native_services.py` substitui os corpos dos 32 serviços mapeados por chamadas diretas às implementações novas, preservando os endereços do renderer e seus símbolos. Ele recusa outra base por SHA256; não transportar os endereços para um APK diferente. As demais rotinas antigas ainda presentes no ELF não foram todas eliminadas. Não chamar isso de fonte C++ integral refeito.

`StationCore_request` não volta a baixar cores de endpoints antigos: se o motor necessário não está no APK, é preciso integrá-lo no build. Estatísticas do frontend reconstruídas mantêm comportamento local, sem reintroduzir a telemetria antiga. Redes próprias de emuladores não estão certificadas por esta revisão de conteúdo Station.

## 5. Contrato HTTP exato

Único host comercial do cliente: **`https://app.lzgames.com.br`**, prefixo **`/v1/station/`**, porta443. Não usar `/drawers`, HMAC Squareweb, Miami, Sambox, `?e=`, `?s=`, 5190, 5191 ou caminho físico Linux no telefone.

| Método e rota | Entrada/condição | Saída consumida / método Java |
|---|---|---|
| POST `activations/challenge` | Identidade `request-activation-challenge`, activationCode, devicePublicKey | Envelope `activation-challenge`, challengeId, nonce, TTL60; `activate`. |
| POST `activations/complete` | Envelope assinado pelo dispositivo, payload `activate`, mesmo código/challenge/nonce/chave | Envelope `activated`, licenseId; `activate`. |
| POST `challenges` | Identidade `request-session-challenge`, licenseId | Envelope `session-challenge`, nonce/challengeId, TTL60; `openSession`. |
| POST `sessions` | Envelope assinado pelo dispositivo, payload `open-session`, licença/challenge/nonce | Envelope `session`, sessionId, accessToken, TTL180; `openSession`. |
| GET `me` | Bearer da sessão | Envelope `profile`, displayName, profileVersion; `profile`. |
| GET `catalog` | Bearer da sessão | Envelope `catalog`, revision, items; `catalogSnapshot`. |
| GET `covers/{coverId}` | Bearer + ID exato | Bytes de imagem MIME compatível; `cover`. |
| POST `downloads/authorize` | Bearer + identidade `request-download` + itemId | Envelope `download-grant`, grantId, itemId, itemRevision, artifact, TTL60; `authorize`. |
| GET `artifacts/{grantId}` | **Mesmo Bearer** usado no grant, um uso | HTTP200, octet-stream, Content-Length exato, bytes do artefato; `openArtifact`. |

Os nomes abreviados de domínio da tabela têm o prefixo/sufixo de `StationProtocol`: `TurboRamaStationAndroid/<nome>/v1`. Não escrever requests à mão copiando só essa tabela: os campos de identidade e a serialização reais são `StationProtocol.identity`, `StationApi.identity`, `envelope` e os DTOs do servidor.

Cada resposta JSON autenticada é `{keyId,payload,signature}`. `payload` e `signature` são Base64URL canônico sem padding; a assinatura RSA-PSS/SHA256 verifica os **bytes exatos** de payload, não JSON reserializado. MGF1 SHA256, sal32, trailer1. Depois validar schemaVersion1, domain, productId, applicationId, deviceId, e vínculo licenseId/sessionId quando aplicável. Produto/aplicação: `TURBORAMA_STATION_ANDROID`.

Autoridade pública e pin estão em `StationConfig`, com keyId `06b41b778041d81b5b86a115a031418e0c4b0b2bd24ec8b340e62eaa82fb5268` e pin TLS SPKI `13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7`. São valores públicos. Rotação de chave/certificado exige plano conjunto e novo cliente se mudar o pin; não retirar a validação para fazer uma conexão passar.

`STA-` seguido de32 hexadecimais maiúsculos é **licenseId**, não activationCode. Código/token/grant usam32 bytes Base64URL. `deviceId` é SHA256 do SPKI público da chave Keystore, Base64URL. MAC/IMEI não são o vínculo de licença. Uma reinstalação com chave nova não pode reutilizar automaticamente uma matrícula consumida: usar transferência oficial pelo operador, preservar auditoria e entregar novo código por canal privado.

### Descritor obrigatório do artefato

`artifact = { fileName, sizeBytes, sha256, format, launchPath, expandedSizeBytes, fileCount }`.

- `format`: `raw`, `zip`, `rar` ou `7z`; inspecionar bytes e conteúdo. Extensão não é prova.
- `sha256`: do **arquivo transferido inteiro**, antes da extração. `sizeBytes`: mesmo arquivo.
- `launchPath`: caminho relativo exato dentro da instalação. Deve existir após extrair; para CUE, conferir arquivos referenciados. Nunca inferir `.rom`, `.iso` ou primeiro arquivo do pacote.
- `expandedSizeBytes`/`fileCount`: conferidos durante a extração. Raw tem um arquivo e tamanho correspondente.
- `itemRevision`: deve ser igual à revisão do item do catálogo que autorizou a operação. Divergência pede atualização, não instalação aproximada.

O servidor consome o grant antes de entregar o stream. Não usar Range, downloads segmentados, seguir redirect ou repetir o mesmo GET após falha. Nova tentativa requer autorização nova. 60s é o prazo para consumir o grant, não uma promessa de baixar um jogo grande em60s.

## 6. Cache, filas, armazenamento e ciclo de vida

Dados privados partem de `Context.getNoBackupFilesDir()`: `station-license-id.txt`, `station-v2/catalog`, `station-v2/covers`, `station-v2/profiles`, `station-v2/installs`. Nome de apresentação é derivado do perfil autenticado, não digitado como licença. A opção Manter conectado controla entrada automática com licença salva e chave, sem salvar senha/código.

Capas ficam em `<coverId>-<revision>.img`. Arquivo válido persiste e evita nova transferência. A validação inclui formato, MIME, limite5MiB, dimensões até8192, decodificação Android. Há cache limitado de metadados, intervalo de2100ms entre pedidos e espera60s para 404/429. A fila de imagens Java tem um worker/capacidade32; o nativo limita os pedidos pendentes a4 e prioridades a64. Ao esconder o frontend, pedidos de capas são cancelados. Isso não equivale a baixar as40mil capas antecipadamente.

`StationCoordinator` mantém a autorização do catálogo na mesma sessão. Autorização, busca por arquivo já baixado e abertura do GET até seus cabeçalhos são serializadas no mesmo owner; o corpo do download segue fora desse bloqueio. Busca local acima de5s obtém novo grant. `ready()` não aceita uma sessão trocada sem catálogo correspondente. Erros de autenticação invalidam o acesso; cache assinado é apoio de exibição com sessão válida, não liberação offline ilimitada.

Raiz Android observada: `/storage/emulated/0/EmulationStation/roms`. `StationStorage.prepareRoot` recebe a raiz escolhida pelo app, resolve os aliases da raiz do sistema e cria descendentes ausentes. Recusa conflito/links nos descendentes e faz prova de escrita. `File.getUsableSpace()` é a consulta compatível; não reintroduzir `Files.getFileStore` no Android.

Instalação:

```text
roms/.station-v2/staging/transfer-*/artifact
roms/.station-v2/<pasta-plataforma>/<itemId>/install-*/content/<launchPath>
no_backup/station-v2/installs/<itemId>.json
```

A área de transferência pertence à raiz ROM compartilhada controlada pelo app, não ao sandbox `no_backup`. A identidade/licença/recibo permanecem privados. Antes da rede reservar tamanho transferido + expandido +256MiB; antes da extração conferir espaço novamente. Limites de caminhos/arquivos, links, duplicatas, traversal e expansão são aplicados no instalador. Arquivo parcial nunca recebe recibo de instalado. O recibo é o último compromisso da operação; instalação anterior íntegra permanece em falha/cancelamento.

`find` confere recibo, plataforma, caminho e tamanhos dos arquivos. Uma revisão nova no servidor não sobrescreve automaticamente um jogo já instalado: não há política completa de atualização automática de ROM. `uninstall` usa arquivos registrados na geração do jogo e preserva desconhecidos/saves; não apagar toda a pasta da plataforma. Cancelamento e exclusão têm testes locais; não foram repetidos visualmente em todos os jogos nesta entrega.

`AssetInstaller`: `bios` preserva arquivos não vazios; recursos são atualizados por `lastUpdateTime` e reparados se ausentes/vazios mesmo com marcador atual. Não tenta mais instalar `packs/Dolphin.zip`, que não existe na base integrada. A atualização restaurou199 recursos e0 BIOS porque as BIOS existentes foram preservadas.

## 7. Servidor: implementação e operação identificadas

Referência de código/handoff: fa7a10c completo citado acima. Release API declarada em produção pelo operador: **`fd13c0d27eaab6a4dcf931a9cd64c3dcd7dd50c4`**. DLL SHA256 **`f305ae3763cb77a53a27b2c168c8de290191b3a7e88e612850856b6f7be7e639`**. Índice SHA256 **`5b460a6f9866e30a5a5b4dad24652c512b1187b3df01244e6af9308ae6b18342`**.

Serviço `turborama-station-api.service`; ExecStart declarado `/usr/bin/dotnet /opt/turborama-station-20261003-fd13c0d/TurboRamaSuiteOnlineServer.dll`; WorkingDirectory da mesma release; drop-in `zz-station-rev3-20261003.conf`. Caminho público: Cloudflare → túnel → nginx → API5192 loopback. Suite5190, gateway5191 e helper administrativo temporário5194 não são rotas de conteúdo do app.

| Fonte Servidor-pix | Responsabilidade para a próxima equipe |
|---|---|
| `src/TurboRamaSuiteOnlineServer/Program.cs` | Feature flag/composição, `Station:LibraryIndexFile`, `Station:DownloadKeyFile`, `Station:ActivationPepperFile`; carrega índice na inicialização e monta serviço. |
| `StationEndpoints.cs` no mesmo diretório | Nove endpoints, leitura/limites JSON, Bearer, corpo de imagem/artefato, códigos HTTP, limiter. |
| `StationProtocol.cs` | DTOs, domínios, identidade e validação de protocolo. |
| `StationService.cs` | Licença/dispositivo/sessão, perfil/catálogo, autorização e consumo do grant. |
| `StationLibrary.cs` | Índice privado, visibilidade, descritor, integridade dos arquivos, capas e correspondência do arquivo autorizado. |
| `StationStore.cs` | Persistência e operações transacionais da licença/dispositivo/challenge/sessão/grant. |
| `StationRequestDiagnostics.cs` | `X-Correlation-ID` e registro sanitizado da requisição. |
| `src/TurboRamaSuiteAdminServer/StationAdminEndpoints.cs` | Administração Station: bloqueio/desbloqueio, transferência/revogação conforme contrato. |
| `src/TurboRamaSuiteAdminServer/StationCommerceEndpoints.cs` | Provisionamento comercial idempotente e produto/SKU. Não certificar checkout real sem prova do operador. |
| `migrations/suite/028_station_android.up.sql` | Produto, dispositivo, desafios, sessões, projeção de cliente e verificador de ativação. |
| `migrations/suite/029_station_download_grants.up.sql` | Grants de download. Conferir ledger antes de qualquer aplicação. |

Prefixar links de leitura por `https://github.com/luziellacerda/Servidor-pix/blob/fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61/` e o caminho da tabela. O fonte completo nesses links é a autoridade de funções internas/SQL; este app não contém uma segunda implementação do backend.

Produto `TURBORAMA_STATION_ANDROID`; SKU `STATION_ANDROID_LIFETIME_1_DEVICE`. Tabelas `suite.station_devices`, `station_challenges`, `station_sessions`, `station_customer_projection`, `station_download_grants`, ledger `suite.schema_migrations`. Os segredos de pepper/chaves, licenseIds reais e caminhos privados de mídia não vão para Git. Não confundir pepper Station com o de outro serviço.

### Índice que realmente alimenta o catálogo

`Station:LibraryIndexFile` é lido na composição do serviço. O código observado não implementa recarga automática ao editar o JSON. Operador deve obter o caminho da configuração **efetiva**, validar índice/arquivos como o usuário real do serviço e planejar publicação/reinício controlado da Station. Não supor o caminho a partir do nome de uma pasta, nem reiniciar outros serviços.

Raiz JSON: revisão e array `items`. Cada registro privado: `itemId`, `name`, `platform`, `revision`, `coverId`, `filePath`, `coverPath`, `catalogVisible` opcional (padrão true), `artifact`. Os dois caminhos são internos Linux; não retornam no catálogo público. O parser permite registro sem descritor, mas a autorização exige descritor e o cliente o recusa se ausente.

O servidor valida tamanho/hash/formato do artefato e mantém tamanho/mtime para detectar alteração. Capas precisam ser legíveis, formato/MIME válido e≤5MiB. Um coverId compartilhado deve ter mesmo caminho **e revisão**. Troca de bytes exige revisão nova do item ou coverId novo; não há coverRevision separado. Conteúdo aprovado deve ficar imutável durante grants ativos.

## 8. Catálogo atual e contagem sem ambiguidades

| platform recebido | Rótulo nativo | Pasta nativa | Jogos públicos revisão3 |
|---|---|---|---:|
| `snes` | Super Nintendo | `super-nintendo` | 644 |
| `snesbr` | Super Nintendo - BR | `super-nintendo--br` | 191 |
| `megadrive` | MegaDrive | `megadrive` | 887 |
| `megadrivebr` | MegaDrive - BR | `megadrive--br` | 94 |
| **Total** | **SNES835 / Mega981** | | **1816** |

As contagens por plataforma acima são do retorno/TSV/HTTPS do servidor; o Android registrou1816 da rede e1816 publicados, zero plataforma desconhecida. Não converter uma contagem de exportação nativa antiga em histograma HTTP atual.

Índice privado:2071 registros =1816 visíveis +255 de compatibilidade ocultos. Os996 IDs anteriores foram preservados (741 canônicos +255 ocultos);1075 jogos novos completam1816. Os99 registros antigos atribuídos a outras plataformas apontavam para SNES/Mega e não demonstravam acervo dessas plataformas. Naomi/Naomi2 podem aparecer como células preparadas sem jogos a pedido anterior; não são jogos inventados pelo servidor.

Listas integrais já estão no Servidor-pix, `docs/station-android/`:

- `catalogo-conciliado-jogos-capas-downloads-20261003.tsv`, SHA256 `bcd8bce18ac48f9eef4c506b071e559de1a3465d3e6892e9ff3538b7c1f9f39a`.
- `compatibilidade-ids-publicados-20261003.tsv`, SHA256 `07736677fd290da1359be4d30057e2ccf004dc90e1286f58940588ce969c336d`.

O mapa completo de aliases do cliente está entregue em JSON. Atenção: `PSP` e `Psp - BR` compartilham pasta `psp`; `Master System ` tem espaço final no nome histórico. Não normalizar rótulos/pastas por conta própria. Sistemas ocultados anteriormente não devem reaparecer só porque têm mapeamento de compatibilidade.

## 9. Correções e provas desta entrega

### Falhas localizadas

1. **Raiz ausente:** `toRealPath` antes de criar `roms` gerava `NoSuchFileException`. Permissão/recursos também eram iniciados cedo demais. Correção em `StationStorage`, `StationFrontend`, `LoginActivity`, `StationBundledFiles`, `AssetInstaller` e montagem DEX.
2. **Baixar sem transferência:** autorização200 seguida de falha local, sem GET. Prova isolada Android: `Files.getFileStore(...).getUsableSpace()` lança `SecurityException:getFileStore` em armazenamento compartilhado e privado. `File.getUsableSpace()` retornou16409522176. Correção nas duas verificações de espaço (`StationDownloads` e `StationInstaller`) via `StationStorage.usableBytes`.
3. **Ativação após desinstalação:** servidor diagnosticou chave antiga/código consumido e fez transferência oficial às16h47; novo código privado foi usado e ativação200 ocorreu às16h52. A revisão atual preservou essa matrícula. Não publicar nem tentar reutilizar códigos históricos.

### Rastreamento real, hora local UTC-03

| Momento | Operação | Resultado/evidência |
|---|---|---|
| 17:20:39 | Atualização APK | Instalada sem desinstalar, SHA no telefone igual ao manifesto. |
| 17:20:57 | Sessão/perfil/catálogo |200;1816 da rede e publicados. |
| 17:21:11 | SNES authorize |200, correlação `d55b3d11a91c440cb16d82a3dc2f9040`. |
| 17:21:11–12 | SNES artifact |200, correlação `96068ccaac1f42b2b6401b3090722491`;670452 bytes ZIP. |
| 17:21:12.237 | SNES instalação |`INSTALL_FINISHED`,1719028 bytes processados (download+extração). |
| 17:21:15 | SNES execução |Core carregou ROM e imagem apareceu; retorno pelo menu confirmado pelo mantenedor. |
| 17:21:43 | Mega authorize |200, correlação `e88520d765cf40548390a7d26e55c912`. |
| 17:21:43–44 | Mega artifact |200, correlação `facb2b4f378a414292c8910845b689d3`;885336 bytes ZIP. |
| 17:21:44 | Mega instalação |`INSTALL_FINISHED`,2982488 bytes processados. |
| Após reinício do processo | Persistência |Acesso retomado, catálogo fresco e `INSTALADOS(2)`, botão Jogar. |
| 17:28:33 | Mega execução repetida |ROM2097152 bytes; logo SEGA e introdução de Cutthroat Island visíveis. Retorno sem login confirmado pelo mantenedor na sequência. |

SNES itemId `826da6daebe9edbebffb3721f83abf12`, itemTag `8aacde0a1c31dc997b24907ab39fc171ce4e69760f475f16bbf31ebffd2e6fc8`, revisão3, ZIP SHA256 `cd3a1292fdb5953ca414dd6a74ac0aa1886b2d132fce4c804e79d5e25ea029f6`, expandido1048576/1 arquivo. O catálogo/ZIP diz USA, mas launchPath assinado é **`Battletoads in Battlemaniacs (ESP) (NTSC).smc`**. Isso é divergência de metadado/acervo para o operador revisar; o app não renomeia a ROM nem altera o descritor.

Mega itemId `ce3f245960b94e064f027ffd8aefe466`, itemTag `57b4daeda099521434572bee6e2f1a0d14ec8ce75316ea603ee56f9a0f71318d`, revisão3, ZIP SHA256 `5c18e99d2ec819ea207e0d5cef1513c1845c8417121022c047d216d4ef140124`, launchPath **`Cutthroat Island (USA, Europe).md`**, expandido2097152/1 arquivo.

327 verificações locais e compilação Java8/API34 passaram;10 verificações de raiz/espaço/aliases/preservação no Android passaram. A rodada anterior da mesma ponte nativa teve28 verificações JNI e7 de retry C++ no aparelho; não contar essas35 como repetidas nesta última troca de Java. Comparado ao APK `fa3bc844…`, mudaram classes5/classes28 e assinatura; manifesto/motores/design preservados.10803 entradas da base preservadas conferidas; nenhum tipo Java duplicado novo. As fixtures Android foram removidas e a opção temporária de manter tela ligada voltou ao valor original0.

### O que ainda não está certificado

- Matriz completa de emuladores, desempenho prolongado, todos os modelos Android e todas as ROMs.
- Negar/conceder permissão manualmente em todas as telas; a lógica tem testes isolados e retomada implementada.
- Fluxo comercial real de compra/provedor/painel de bloqueio/transferência ponta a ponta. Backend relata testes específicos, não certificado global.
- Cancelar/excluir/offline visualmente nesta rodada completa; existem testes locais, mas não apagar jogos do mantenedor para fabricar uma prova.
- Remoção física de todas as rotinas antigas dos binários preservados.
- Catálogo de40mil; limites atuais descritos na seção12.

## 10. Diagnóstico reproduzível: localizar a primeira divergência

Registrar sempre: SHA do APK, clientVersion, commit do servidor, revisão de índice efetivo, horário/fuso, itemId, coverId, revisão do item e correlação. Nunca enviar Bearer, grant, ativação, licença de cliente ou caminho privado em logs públicos.

1. **UI:** obter ID da seleção real; não usar só nome ou posição da célula.
2. **Catálogo:** conferir envelope assinado e item exato; distinguir catálogo da rede de cache/exportação.
3. **Mapeamento:** `StationPlatforms.resolve`, `StationPublication` e aviso de desconhecidos. Comparar contagens recebidas/publicadas.
4. **HTTP:** `StationService` logcat fornece evento/status/count e trace com correlation/itemTag/coverTag/revision. Tag é SHA256 UTF8 do ID para cruzar sem revelar identificadores pessoais.
5. **Servidor:** usar a mesma `X-Correlation-ID`; proxy deve encaminhá-la. API/índice/UID efetivos devem ser comprovados, não presumidos de um arquivo do checkout.
6. **Arquivo:** operador abrir/hashar ROM e capa como usuário do serviço; conferir tamanho/mtime/descritor.404 pode ser ausência/permissão/vínculo, conforme código; status isolado não localiza a causa.
7. **Transferência:** houve GET? Só AUTHORIZE200 e INSTALL_FAILED local não é prova de erro no servidor. Conferir cabeçalhos, bytes/hash e falha de espaço/extrator.
8. **Instalação:** recibo, arquivos da geração e launchPath. Ausência de recibo não é instalação concluída.
9. **Emulador:** core correto, formato aceito, arquivos auxiliares/BIOS e log de abertura. Download200 não prova compatibilidade de jogo.
10. **Retorno:** sair pelo menu normal, conferir sessão e instalado após reabrir.

| Erro | Verificação correta |
|---|---|
|401/403 |Sessão/licença/dispositivo; não retirar autenticação nem repetir ativação consumida. |
|404 `STATION_COVER_NOT_FOUND` |ID do catálogo, índice efetivo e leitura de capa; retentativa limitada. |
|404 `STATION_ITEM_NOT_FOUND` |ID selecionado vs índice ativo; atualizar catálogo e cruzar correlação. |
|404 `STATION_GRANT_NOT_FOUND` |Grant consumido/expirado/vínculo diferente/arquivo inacessível conforme código; nova autorização, sem replay GET. |
|503 `STATION_ARTIFACT_NOT_READY` |Descritor ausente ou arquivo divergente; corrigir conteúdo/índice no servidor. |
|429 |Espera e limite de consultas; servidor atualmente30/IP/rota/minuto. |
|Falha antes do GET |Permissão, raiz, espaço, busca local e exceção Android. |
|Arquivo recebido mas não instalado |Hash/tamanho/formato/launchPath, expansão e limites. Não pular essas validações. |

## 11. Adicionar jogos: procedimento para o servidor

Para plataforma já mapeada e formato já aceito, normalmente o APK não muda: o operador amplia o **índice Station efetivo**. Não basta pôr uma URL em XML/TSV antigo ou editar `/drawers`.

1. Inventariar o arquivo real e sua origem autorizada; definir plataforma exata e nome correto. Escolher itemId estável sem reciclar ID de outro jogo. Preservar todos os IDs/coverIds já publicados e entradas de compatibilidade.
2. Inspecionar o arquivo, calcular tamanho/SHA256, formato, launchPath exato, contagem e expansão. Pacotes multimídia precisam de escolha explícita do executável/CUE/RPX correto, sem primeiro arquivo automático arbitrário.
3. Preparar capa real de formato suportado≤5MiB; definir coverId. Conferir mapeamento e revisão compartilhada se reutilizada.
4. Criar registros no índice privado com caminhos Linux e descritor; incrementar revisões necessárias. Nome de catálogo deve refletir o idioma/região do arquivo; corrigir o caso Battletoads acima sem quebrar IDs.
5. Conferir limites atuais antes de publicar: total de entradas privadas inclui ocultas. Validar tudo sob a identidade real da API, não root. Arquivos e diretórios precisam permitir travessia/leitura; conteúdo estável/imutável.
6. Usar as ferramentas já existentes em `docs/station-android/scripts/`: `inventario-somente-leitura.sh`, `cruzar-indice-catalogo.py`, `conciliar-indices-station.py`, `preparar-indice-artefatos.py`, `gerar-catalogo-midia.py`, `materializar-conteudo-station.py`, `exportar-indice-efetivo.py`, `exportar-catalogo-assinado.py`, `verificar-http-release-station.py`. Ler os argumentos e contratos reais de cada arquivo no commit do servidor; não executar scripts históricos de deploy com defaults antigos.
7. Homologar índice+API juntos com licença de teste autorizada: assinatura, contagem/histograma, preservação dos IDs, capa200, autorização, stream hash/tamanho, segundo uso404, cancelamento/novo grant. Guardar evidência sanitizada.
8. Operador planeja backup/retorno, configuração e publicação controlada só da Station. O índice é carregado no startup; edição em disco sozinha não comprova catálogo vivo atualizado.
9. Android atualizar catálogo, conferir novo item, capa persistente, baixar/instalar/abrir/voltar e reabrir instalado. Não reemitir licença por simples adição de jogos.

Resposta mínima que a equipe do servidor deve publicar: commit/release/DLL, hash e revisão do índice efetivo, contagens públicas e privadas por plataforma, IDs novos e preservados, prova de leitura sob UID real, IDs/correlações de capa+descritor+bytes/hash, serviço/configuração ativos, backup/retorno, pendências específicas. Não enviar apenas “servidor OK”.

## 12. Adicionar sistemas e alcançar 40 mil jogos

**Meta solicitada pelo mantenedor:40.000 jogos. Não implementada nesta versão estável.** Limites atuais do código: servidor `StationLibrary.MaximumItems=4096` sobre todas as entradas privadas; cliente até4096 itens públicos e envelope de catálogo até12MiB. O índice atual ocupa2071 entradas privadas. Aumentar um número só no cliente não habilita40mil no servidor nem resolve memória/latência.

Para um sistema novo, entregar conjuntamente:

1. `platform` exato do servidor e alias explícito em `StationPlatforms`; label/folder conferidos na configuração nativa.
2. Inventário real ROM/capa/descritores. Vídeo/célula não comprovam jogos disponíveis.
3. Motor integrado, comando/atividade/ABI, formatos e BIOS/recursos que precisa; fonte/versão/licença da integração. Rota do launcher e retorno devem existir, sem abrir um emulador antigo por engano.
4. Tema/vídeo/LED mapeados para a mesma plataforma, preservando um vídeo ativo na célula principal e pausa fora do frontend. Não reintroduzir nave/estrelas removidas nem regressão de consumo.
5. Preparação automática de pastas/recursos no APK, preservação de jogos/saves/licença. Testes de fixture para instalação limpa e retomada de permissão; jamais depender de ajuste ADB.
6. Prova real de baixar, extrair, instalar, jogar, controlar, sair e retomar. Anunciar separadamente mapeamento pronto, motor integrado e jogo homologado.

### Trabalho conjunto necessário para40mil

Esta seção é requisito de engenharia, **não contrato HTTP já existente**. A API atual não tem cursor/pageSize/paginação; não enviar campos inventados ao endpoint vivo.

- Servidor e Android devem acordar e publicar contrato versionado de paginação/snapshot, revisão consistente entre páginas, ordenação estável, cursor/expiração, filtros por plataforma e limites de resposta. Escolher nomes/campos no handoff assinado pela equipe responsável antes de codificar chamadas.
- Determinar política dos IDs ocultos/compatibilidade separada da quantidade pública.40mil públicos podem exigir mais de40mil privados; não eliminar compatibilidade para caber no limite.
- Android deve montar/persistir catálogo incremental com índice por plataforma/item, atualização atômica de snapshot e UI progressiva. Não alocar simultaneamente JSON gigante, cópias JNI,40mil bitmaps e texturas.
- Capas sob demanda das células visíveis e vizinhas, cache de disco limitado com política explícita, pedidos e decodificação limitados. Não baixar todas ao abrir.
- Manter vínculo de sessão/assinatura, autorização por item/revisão e download independente de paginação. Renovação de sessão não pode perder seleção ou invalidar um GET já aberto.
- Medir com40mil itens válidos e volume de compatibilidade adicional: memória Java/nativa/GPU, tempo de primeira tela, troca de plataforma, pesquisa local, paginação cancelada/retomada, cache, espaço, processo em segundo plano. Conteúdo sintético prova capacidade, não acervo real.
- Homologar contrato antigo/novo e retorno de versão; não substituir esta tag estável antes da conferência no aparelho. O próximo handoff deve registrar exatamente o contrato acordado e as medidas, sem afirmar suporte por simples aumento de constante.

## 13. Build e recuperação sem misturar versões

Pré-requisitos usados: Python `C:\Python314\python.exe`; JDK17 em `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin`; SDK API34 em `G:\Android\Sdk`; build-tools35 em `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15`; NDKr28c em `E:\TurboEdenEngine\android-ndk-r28c`; CMake/Ninja descritos em `build_archive.py`; ferramentas JSON/apktool/LIEF conforme scripts/manifests do módulo. Preservar keystore de assinatura existente no ambiente, não publicar/copiar para o repo.

Receita de reconstrução do módulo, **executar na pasta canônica E:** e parar em qualquer falha:

```powershell
$env:TEMP = 'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\temp'
$env:TMP = $env:TEMP
$env:ANDROID_USER_HOME = 'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tool-home'
Set-Location -LiteralPath 'E:\ESTUDO APK\work\turbostations-reconstruction-20261002'
& 'C:\Python314\python.exe' .\prepare_test_dependency.py
& 'C:\Python314\python.exe' .\run_tests.py
& 'C:\Python314\python.exe' .\build_module.py
& 'C:\Python314\python.exe' .\prepare_dex_input.py
& 'C:\Python314\python.exe' .\build_archive.py
& 'C:\Python314\python.exe' .\build_frontend.py
& 'C:\Python314\python.exe' .\link_native_services.py
& 'C:\Python314\python.exe' .\build_app_dex.py
& 'C:\Python314\python.exe' .\package_apk.py
```

PowerShell não para automaticamente cada comando nativo em código de saída não zero: o operador deve conferir `$LASTEXITCODE` após cada etapa. Não usar essa lista como execução cega. Scripts de edição `add_*`, `refine_*`, `integrate_*` e finalizadores históricos não são parte desta receita. Se faltarem ferramentas privadas/base/assinatura, informar a dependência; não trocar hashes/inputs para contornar a trava.

O empacotador substitui `classes5/6/8/28.dex` e `libmain/libstation_frontend/libstation_archive.so`, adiciona avisos de licença das dependências, remove `assets/turboretro/catalog.json`, preserva manifesto/design/motores e verifica duplicatas/classes antigas. Zipalign16KiB e assinatura igual à base são conferidos. Cada empacotamento novo é candidato; relatório inicial do script não é aceite de aparelho. O APK congelado é a reprodução **exata em bytes** desta entrega; rebuild pode gerar metadados ZIP/assinatura diferentes e precisa de novo hash/validação.

Instalação de atualização, com jogo encerrado normalmente:

```powershell
& 'G:\Android\Sdk\platform-tools\adb.exe' install --no-incremental -r --user 0 'E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk'
```

Conferir espaço, dispositivo alvo, SHA antes/depois, certificado e pacote. Não usar `uninstall`, `pm clear` ou restaurar dados/Keystore de outro aparelho. Restauração de APK não restaura automaticamente uma licença cuja chave foi apagada. Não promover APK de outro produto/assinatura pelo nome parecido.

## 14. Encerramento para a equipe do servidor e próxima implementação

**Fechado no Android com esta entrega:** acesso real após transferência oficial, nome/perfil, catálogo revision3/1816, capas200 e persistência, descritor assinado, dois ZIP transferidos/hash conferido, instalação automática, abertura SNES/Mega, retorno sem login e instalados após reinício. As duas falhas locais de pasta/espaço foram corrigidas no APK, sem reparo manual da árvore real do telefone.

**Não executar novamente:** migrações028/029, criação de chave, reemissão de código, troca de catálogo ou restart só porque um handoff histórico dizia pendente. Conferir evidência atual antes de cada ação.

**Próxima etapa acordada em escopo:** ampliar sistemas e jogos, preservando esta base.40mil é a capacidade-alvo solicitada; exige trabalho conjunto da seção12. Para jogos em sistemas existentes dentro dos limites, seguir seção11. Para sistema novo, entregar o conjunto completo da seção12. Divergência de idioma do Battletoads é questão objetiva de conteúdo que o operador deve revisar sem alterar IDs arbitrariamente.

Toda futura entrega deve atualizar manifesto, fontes e evidências no mesmo commit de integração, com responsável e resultado: código escrito, build concluído, servidor publicado, teste isolado e aparelho são estados distintos. Ausência de prova deve ser escrita como pendência, nunca preenchida com suposição.
