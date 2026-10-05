# R10 — integração do retorno N64/biblioteca, APP → SERVIDOR

## Estado e destinatário

Entrega do cliente Android para o operador do **Servidor-pix** e próximos mantenedores do **TurboStations**. Data de conclusão do APK: **05/10/2026**. O nome dos arquivos mantém `20261004`, data de início desta revisão.

**APK R10 compilado, assinado e conferido no PC; instalação R10 e execução Android pendentes por USB ausente.** Não promover a estável nem atribuir resultados de produção aos testes sintéticos. Nenhum serviço Linux, índice, conta, licença ou jogo real foi alterado nesta rodada.

Correção de histórico: **R9 foi instalado** por atualização e seu hash foi confirmado no aparelho em 04/10/2026. `stay_on_while_plugged_in` foi restaurado para **0**, com leitura confirmada. As afirmações anteriores de R8 como último instalado e de restauração pendente foram superadas pelo recibo `evidence/r9-installation.json`.

## Fontes de autoridade

- Retorno lido no Servidor-pix: commit **4e623bcbeaed3ee03d8a1767f66319e67659463d**, branch `feat/station-artifact-descriptor-20261002` (também alcançado pelos ramos library-autodiscovery e online-direct).
- Documento: `docs/station-android/RETORNO-SERVIDOR-N64-BIBLIOTECA-20261004.md`, acompanhado de `BIBLIOTECA-AUTOMATICA-STATION-20261004.md`.
- Implementação fornecida pelo servidor no TurboElden: **ba669c27418341c7f232a644317881779ddd3bf3**, integrada por fast-forward ao ramo `feat/station-capas-visuais-netplay-20261003`.
- Base visual R9: **a325e6986e5432871a0b8f22168e4e8e16868eff**.
- Fonte Android canônica: `E:\ESTUDO APK\work\station-netplay-20261004`, alias `E:\StationNetplayWork`.
- Build R10: `E:\ESTUDO APK\work\station-library-r10-build-20261004`.
- Evidências privadas locais: `E:\ESTUDO APK\work\station-netplay-20261004\library-r10`.
- Backup dos oito arquivos anteriores ao overlay: `library-r10\before`; não reaplicar o overlay do servidor sobre as correções R10.

## O que o servidor relatou como publicado

Estas são evidências do operador documentadas no retorno, **não uma nova medição do Android**:

- API fonte `931030bba25ca8a783f096b72dcecd26a7b49387`; DLL SHA256 `0b3f5da385216d216fb55220789f55c40b8eb304b7b1a4759cc154b1aa3f3ab0`.
- Serviço `turborama-station-api.service`, executável `/opt/turborama-station-folders-20261004-931030b/TurboRamaSuiteOnlineServer.dll`.
- Índice `/mnt/DADOS/turbostation-library-auto-20261004/index.json`.
- Revisão **8**, **1.973 jogos visíveis**: SNES644, SNESBR191, Mega887, MegaBR94 e N64157. Há255IDs internos ocultos por compatibilidade, e996IDs originais preservados.
- **1.957 sinopses**,16edições sem fonte; **313 jogos com folderPath**.
- N64:156ZIPs e1alternativa RAW `.rom`; capas480×720 derivadas das artes exatas. Quatro downloads simultâneos de capas conferidos no Linux.
- Importação automática por minuto, duas observações estáveis, recarga do índice pela API a cada10s. Esses tempos são do servidor, independentes da consulta Android.
- Salas já publicadas segundo retorno. O antigo404 das salas não representa o estado atual relatado.

## Contrato implementado no app

Base existente `https://app.lzgames.com.br`, mesma sessão, pin e assinatura; não foi acrescentado domínio, CDN, URL de ROM ou caminho de disco ao cliente.

| Operação | Contrato e função |
|---|---|
| Catálogo | `StationApi.catalogSnapshot` solicita **GET /v1/station/catalog?metadata=1**; `StationHttp` permite exatamente a variante; `StationClient` verifica o envelope no domínio `TurboRamaStationAndroid/catalog/v1` antes do parser. |
| Identidade | `itemId`, `name`, `platform`, `revision`, `coverId` continuam obrigatórios. IDs existentes não são reconstruídos por nomes. |
| Subpastas | `folderPath` opcional, array de até8segmentos/80unidadesUTF16. Ausência mantém catálogo plano. Pasta é apresentação, nunca destino arbitrário de download. |
| Sinopse | `metadata.description`, máximo2000unidadesUTF16, permite tab/nova linha e rejeita NUL, demais controles e surrogates inválidos. Outros campos: developer/publisher/genre80, players/releaseDate40. Metadados ausentes aceitos; tipo presente inválido rejeitado. |
| Cache | `StationCatalog.localPayload` conserva os seis campos de metadata e folderPath. Catálogo antigo sem metadata continua legível. Limite de corpo64MiB, capacidade desta linha4096itens; candidato40mil não foi mesclado. |
| Capas | **GET /v1/station/covers/{coverId}**, bytes autenticados, quatro workers existentes, cache persistente e leases preservados. Sem espera fixa entre sucessos. |
| Download | **POST /v1/station/downloads/authorize** pelo itemId/revision atual; **GET /v1/station/artifacts/{grantId}** com concessão assinada. Descritor, bytes/hash, formato e launchPath continuam nos módulos existentes. Sem novo caminho alternativo de download. |
| Perfil/login | Fluxo existente de ativação, sessão e perfil preservado. Nenhum código de ativação ou segredo foi publicado. |

## Fluxo automático e correções complementares

`StationFrontend.configure` prepara armazenamento e publica a biblioteca já autenticada. `startCatalogPoll` agenda a primeira consulta em5s e as seguintes em60s. Não é um atraso da fila de capas.

O tick só entra na fila de comandos com app em primeiro plano, configurado, autorizado, sem download nem capas pendentes. As mesmas condições são conferidas novamente quando a tarefa começa, para não usar um estado antigo da fila.

`StationCatalogPoll` mantém um ticket por geração e somente uma consulta em andamento. Ao esconder o app, `stopCatalogPoll` cancela o timer e a requisição por `StationApi.Cancellation`. Uma tarefa da geração anterior não publica depois de esconder/mostrar rapidamente. O ticket é liberado no término e também quando o executor recusa uma tarefa. O helper não mantém seu monitor durante tráfego de rede.

`StationCoordinator.refresh` verifica cancelamento antes de aceitar a nova biblioteca autorizada. Se revisão e nome do perfil forem iguais, o polling não chama `publishCurrent`: não republica o catálogo nativo nem cancela/recomeça capas. Revisão diferente ou nome alterado produz publicação pelo mecanismo atômico existente. Erros comuns de rede mantêm a biblioteca corrente; erro de sessão válido usa a mensagem de reentrada existente. Catálogo grande e internet lenta ainda podem consumir tempo de rede: não há promessa de latência zero.

`StationDiagnostics.route` foi corrigido para classificar a consulta com `?metadata=1` como CATALOG, mantendo consultas desconhecidas fora dessa classificação. A versão fornecida pelo servidor classificava essa variante como REQUEST_FAILED mesmo quando válida.

## Caminho nativo da sinopse e N64

Cada linha publicada tem itemId, nome, label da plataforma, pasta canônica, coverId, caminho instalado verificado, folderKey e sinopse, separados por NUL. JNI aceita a oitava coluna opcional, pagina com `station_synopsis_pages.hpp` sem cortar UTF-8 e guarda no slot de string antes reservado em `Item`. ABI0xe8 e offsets existentes permanecem.

`native_info.h` prioriza a sinopse recebida do servidor e usa o complemento empacotado por ID quando ela está vazia. A chegada de cada capa não reinicia a paginação do texto. `developer`, `publisher`, `genre`, `players` e `releaseDate` ficam no modelo/cache; esta entrega não adiciona novas caixas visuais para esses campos.

N64 já era uma integração do app: `n64` → `Nintendo 64` → pasta `nintendo-64` → core `mupen64plus_next_gles3`. Esta revisão permite receber a biblioteca/sinopses do novo catálogo; não troca o core. N64 não é acrescentado aos motores elegíveis para partidas online. Salas mantêm `classes35.dex` exato do R9; partida real entre dois aparelhos continua sem evidência.

## APK, assinatura e preservação

- APK: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Biblioteca-N64-Sinopses-R10-20261004.apk`.
- SHA256 **8bc1d2ef1b5864dc1d5359d1df05b90593cf483dff7f48819f7a7a6b52a84c0b**;1.982.754.504bytes.
- Pacote `org.turboramastation.frontend`; certificado **7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825**.
- Base R9 arquivada e revalidada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Salas-Subpastas-R9-20261004.apk`, SHA256 **b5c98ea40b915f738e29ef2b2e7168fcdf2d327aa64c862596dff15b5620fdf1**. Somente sua cópia idêntica em E: foi removida para liberar espaço.
- Exatamente três entradas alteradas: `classes28.dex`, `lib/arm64-v8a/libstation_frontend.so`, `lib/arm64-v8a/libturbo_carousel.so`.
- **11.100 entradas preservadas**, comparadas por SHA256, nomes e tipo de compressão; nenhuma entrada de conteúdo adicionada ou removida. Arte/vídeos reais usados no renderer; nada sintético no APK.
- Salas `classes35.dex`: **0b9847c71cecd46eecdbd8681579296778a41e765d13dbed00e7aa2bb72bb8d4**.
- Assinatura e alinhamento16KiB conferidos. Não houve desinstalação nem limpeza de dados nesta rodada. Tags estáveis anteriores não foram movidas.

## Reproduzir e auditar

O diretório desta entrega contém os11arquivos runtime alterados desde R9, testes, scripts e `source-manifest.json`. É um delta: a base completa canônica contém headers, arte, objetos e módulos já existentes. Não reconstruir usando arquivos vazios no lugar desses insumos.

1. Conferir fontes pelos hashes do manifesto. No PC já estão aplicadas; não repetir `implement_station_r10.py` sobre a mesma árvore.
2. Rodar `station/run_tests.py` com `STATION_BUILD_DIR` em uma pasta de E: e dependência JSON existente. Suite Java659checks/API34Java8.
3. Builder `build_modules.py --work-root "E:\ESTUDO APK\work\station-netplay-20261004" --sdk "G:\Android\Sdk" --ndk "E:\TurboEdenEngine\android-ndk-r28c" --output "E:\ESTUDO APK\work\station-library-r10-build-20261004" --android-api 34 --build-tools 34.0.0 --jdk "C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin" --build-carousel`. A pasta de saída deve ser nova; não sobrescrever o build entregue.
4. `package_station_library_r10.py` documenta o empacotamento exato. É deliberadamente protegido contra sobrescrever APK/temporários existentes. Usa base R9 verificada, mesmos três módulos e certificado original, valida cada entrada.
5. Instalar somente quando o aparelho estiver disponível e fora de uma partida: `adb install --no-incremental -r --user 0 <APK R10>`. Não desinstalar, não limpar armazenamento, não editar pastas/configurações manualmente para fazer o teste passar.

Os scripts de teste C++ requerem os fixtures `station_collection_test.cpp` e `station_folder_navigation_test.cpp`, copiados nesta entrega em `tests/`. Ajustar seus caminhos locais se executar fora do workspace original; compilam contra headers reais da árvore canônica. Evidências têm resultados e hashes, não credenciais.

## Testes executados nesta revisão

- **659 checks Java**:33novos ciclo de vida/revisão/metadata/diagnóstico;6N64/sinopse/cache;29pastas;591regressões existentes de arquivos, protocolo, sessão/cache, publicação, instalador, fechamento, bootstrap, transporte online e concorrência de capas.
- Compilação de todas as fontes Android/API34 com bytecodeJava8; DEXAPI26.
- **36 checks C++ coleções**, **429 navegação**, teste de páginas por palavra/UTF-8.
- JNIarm64 com libc++estática, renderer real com headers/objetos do projeto, módulos16KiB.
- Assinatura/apkalign e comparação de todos os conteúdos do APK contra R9.

Os testes usam fixtures sintéticos identificados. Não significam download de jogos reais, medição de aquecimento ou demonstração de sincronismo Netplay.

## Pendências reais e próximo responsável

**No Android, após conectar:** confirmar instalação/hash, sessão mantida, catálogo recebido/revisão/contagens, sinopse de N64 e fallback, capas em sequência, entrada/volta de subpastas, download ZIP/RAW de item autorizado, abertura real, controles/saves/retorno e salas R9. Não fixar1.973 como limite visual: o servidor pode já ter uma revisão maior.

**Operador do servidor:** não há nova rota obrigatória criada por esta entrega. Preservar contrato publicado e disponibilizar registros de catálogo/capa/download com IDs/correlação se houver falha no aparelho. Para conferir autodiscovery ponta a ponta, publicar um item autorizado pela rotina oficial e observar revisão nova no cliente; não duplicar IDs nem alterar arquivos apenas no telefone. Novas plataformas ainda precisam de mapeamento/motor no app; novos jogos/pastas das plataformas existentes vêm do índice sem novo APK.

**Não comprovado ainda:** instalação R10, desempenho/visual dessa revisão no telefone, downloads N64 reais e partida entre dois aparelhos. O código e o APK estão prontos; essas evidências não foram inventadas para encerrar o handoff.
