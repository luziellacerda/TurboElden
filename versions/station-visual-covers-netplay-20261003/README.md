# TurboStations — capas contínuas, sinopses, efeitos e Netplay

Handoff técnico da entrega de 03/10/2026. Este documento descreve o aplicativo Android TurboStations e sua ligação com o canal Station. O serviço Turborama/Suite Windows não foi alterado.

## Conferência posterior no PC

Bateria completa repetida e ensaio de 4.096 pedidos de capa simulados aprovados, sem acessar telefone ou sessão de produção. [Relatório detalhado](pc-validation/README.md) e [recibo](pc-validation/PC-TEST-RESULT.json). APK R2 e seus componentes permanecem com os mesmos hashes.

## 1. Estado e referências obrigatórias

| Referência | Identificação |
| --- | --- |
| Branch desta entrega | `feat/station-capas-visuais-netplay-20261003` |
| Base publicada antes desta entrega | Commit `49d2b867daad584f7b6f82abccdc91798cb6d161`, branch `snes-explus-completo-20261003` |
| APK base HUD LZ Games R2 | SHA-256 `6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b` |
| Pasta canônica de compilação | `E:\ESTUDO APK\work\station-visual-covers-20261003` |
| Fontes publicadas | Esta pasta `versions/station-visual-covers-netplay-20261003` |
| Pacote preservado | `org.turboramastation.frontend` |
| Servidor: retorno lido | Commit `54bba11c52f35695fd47eabc7145f42af9990426` do Servidor-pix |
| API que o retorno informa em produção | Commit `4bb77ed2b8fb01fe967b90dc18ec3fbd1ee5d58b` |
| Fonte de otimização enviada pela equipe do servidor | Commit `1dc8c381e49e60ccbe0f84c97dcfe5be3e1d85f3` do TurboElden |

**Estado final:** APK R2 compilado, assinado e conferido. Arquivo: `E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R2-20261003.apk`; **1,922,513,242 bytes**, SHA-256 **`31ab80ef2c77e9c5dff294d6f63807ab1e6d6cded81c2beec7aee171067f46d8`**. Quatro entradas existentes foram alteradas conforme a lista planejada, 10.871 foram preservadas byte a byte e não há classes duplicadas. O manifesto preserva todas as declarações anteriores e acrescenta somente duas Activities internas, sem novas permissões. A assinatura original e o alinhamento de 16 KiB foram conferidos. O recibo `build-result.json` identifica esta montagem; não usar os recibos da primeira montagem como se fossem R2.

A primeira montagem, identificada pelo prefixo de hash `62068502`, foi arquivada e verificada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`; consultar `archived-visual-r1.json`. Ela não representa o R2.

O telefone não estava disponível na USB para instalar e conferir esta entrega. Compilação e testes locais não comprovam velocidade no telefone, imagem final no driver Android ou uma partida Netplay entre dois aparelhos. Esta revisão ainda não foi promovida à referência estável de recuperação.

A base HUD já instalada tinha os menus próprios de SNES/Mega e o HUD LZ Games. Esta entrega preserva os motores e o HUD. A confirmação anterior de um novo arquivo de save manual do Mega não substitui testes controlados de carregar, cancelar e substituir cada posição.

## 2. Mapa de arquivos e responsabilidades

| Local | Responsabilidade |
| --- | --- |
| `station/src/java/org/emulationstation/frontend/station/` | Protocolo Station, sessões, catálogo, cache, fila de capas, download e instalação |
| `station/src/native/station_frontend.cpp` | Ponte JNI do catálogo e agenda de capas no thread SDL |
| `station/src/native/station_cover_plan.hpp` | Prioridades visíveis seguidas dos demais jogos da mesma plataforma e pasta |
| `station/src/native/station_cover_retry.hpp` | Repetição por imagem e suspensão da busca antecipada após 429 |
| `native/native_carousel.cpp`, `native/native_settings.h` | Integração do carrossel existente e entrada nativa “Jogar em rede” |
| `native/native_magazine.h`, `native/magazine_shader.h` | Efeito de luz e brilho da capa selecionada |
| `native/premium-magazine-led-android.glsl` | Fonte GLSL adaptada do efeito real do tema do PC |
| `native/native_info.h`, `native/station_game_infos.h` | Consulta de sinopse pelo identificador exato do item Station |
| `native/station_info_layout.h`, `native/native_console.h` | Distribuição do texto e ilustração do console à direita |
| `assets/station-metadata/` | Metadados XML saneados, índice das sinopses e lista das ausências |
| `assets/turbo-console/` | Ilustrações locais de SNES e Mega Drive |
| `netplay/src/`, `netplay/native_netplay.h` | Ponte para interfaces reais de rede dos motores |
| `build/` | Receitas de montagem/exportação; não contém todos os insumos privados |
| `evidence/` | Recibos, proveniência, contagens, testes e auditorias |
| `PRIVATE-BUILD-INPUTS.json` | Insumos locais grandes/privados que não devem ser presumidos presentes no Git |

As classes Java históricas continuam sob `org.emulationstation.frontend`; isso não muda o pacote instalado. A reconstrução usa o renderer e os lançadores binários preservados. O repositório não deve ser descrito como fonte C++ integral de todo o frontend original.

## 3. Caminho completo: tela → catálogo → capa → jogo

```text
Login Station / licença salva / chave Android Keystore
  → StationSessions → StationCoordinator
  → perfil e catálogo autenticados/assinados
  → StationPublication → StationFrontend.publishCatalog
  → station_frontend.cpp → renderer/carrossel nativo existente

Capa solicitada pelo carrossel
  → prioridades visíveis + restante da plataforma selecionada
  → até 4 operações nativas pendentes
  → StationCoverQueue, 4 workers reais
  → StationCoordinator.acquireItem + lease da sessão
  → StationCoverStore: cache privado ou GET autenticado
  → arquivo validado/publicado atomicamente
  → publishCoverResult → Inbox JNI → thread SDL → textura

Baixar
  → StationDownloads → autorização assinada do item/revisão
  → descritor de instalação → busca local conferida ou GET de uso único
  → tamanho + SHA-256 → instalação segura → recibo e launchPath
  → Jogar → motor já integrado → retorno às plataformas
```

### Contrato HTTP usado pelo aplicativo

Origem do canal comercial: `https://app.lzgames.com.br`. A classe `StationConfig` permanece a autoridade de host, pin TLS e chave pública; não duplicar valores em classes de apresentação.

| Método e rota | Uso e regra |
| --- | --- |
| `POST /v1/station/activations/challenge` e `/activations/complete` | Primeira ativação com código emitido pelo servidor e prova do aparelho |
| `POST /v1/station/challenges` e `/sessions` | Sessão usando a licença salva e a chave privada do Android Keystore |
| `GET /v1/station/me` | Perfil/nome do comprador, validado pelo cliente |
| `GET /v1/station/catalog` | Envelope assinado; `itemId`, `name`, `platform`, revisão do item e `coverId` |
| `GET /v1/station/covers/{coverId}` | Bytes da capa com Bearer; identidade vem do catálogo |
| `POST /v1/station/downloads/authorize` | Autoriza o `itemId`; devolve grant assinado, `itemRevision` e `artifact` |
| `GET /v1/station/artifacts/{grantId}` | Bytes do jogo, mesmo vínculo de sessão, um uso e 60 segundos para consumir o grant |

O cliente verifica `{keyId,payload,signature}` e RSA-PSS/SHA-256 antes de aceitar perfil, catálogo ou descritor. A identidade do aparelho é derivada da chave pública do Keystore. Não usar MAC/IMEI nem trocar a licença `STA-` pelo código de ativação. Bearer e grant não são persistidos nem publicados no Git.

O download não recebe URL de Miami, Sambox, CDN ou caminho Linux. Não inserir `/drawers`, `/v1/suite/*`, parâmetros `?e=`/`?s=` ou fallback por URL antiga neste fluxo. Recursos de rede próprios dos emuladores têm finalidade separada.

No Linux, o retorno registra HTTPS público → túnel/Cloudflare → Nginx → API Station em `127.0.0.1:5192`. O APK utiliza somente a origem HTTPS pública. Este trabalho não reiniciou nem publicou serviços Linux.

## 4. Capas: concorrência, cache e sessão

### Sucesso sem espera artificial

`StationCoverQueue` possui quatro workers de IO, fila limitada e deduplicação por item. A ponte nativa mantém no máximo quatro pedidos pendentes. Cada conclusão libera uma vaga; o preenchimento continua no próximo ciclo do frontend. Não se espera o lote inteiro e não há intervalo fixo de 2,1 segundos entre sucessos.

O plano começa pelas prioridades que o renderer está mostrando e continua pelos demais itens da **mesma plataforma e pasta**, em ordem. Isso mantém as listas BR separadas mesmo quando compartilham a pasta de instalação. Não inicia automaticamente uma varredura de todas as plataformas do catálogo.

“Zero espera” significa ausência de atraso deliberado depois de sucesso. Rede, verificação de imagem, armazenamento e próximo ciclo da tela ainda levam tempo. A checagem de um segundo do plano esgotado/repetições não cadencia imagens bem-sucedidas.

### Cache persistente

O arquivo fica em `noBackupFilesDir/station-v2/covers/<coverId>-<revision>.img`. A identidade inclui a revisão do **item**. Uma capa válida da mesma revisão é lida do disco sem novo HTTP. O conteúdo é validado e a substituição usa o escritor atômico existente. Somente pedidos da mesma chave são serializados; capas diferentes não compartilham um bloqueio durante a transferência.

No servidor, editar os bytes de uma capa exige elevar a revisão do item ou fornecer outro `coverId`. Manter o mesmo par enquanto muda a imagem deixa o cache antigo legitimamente reutilizável. O app não deve “resolver” isso apagando todas as capas a cada abertura.

### Renovação segura de sessão

O servidor invalida sessões anteriores ao renovar. `StationSessions.Lease` conta usuários ativos e impede a rotação do Bearer enquanto perfil/catálogo, capas ou a janela de autorização do jogo ainda o utilizam.

Para um jogo, a lease cobre autorização, conferência do arquivo local e aceitação dos cabeçalhos do GET que consome o grant. Depois, o corpo pode continuar em streaming enquanto outras operações usam a sessão. Fechar a lease antes da invalidação sincronizada evita a inversão de bloqueios examinada na revisão. Uma recusa tardia só limpa a sessão rejeitada correspondente; não invalida uma sessão mais nova.

### Troca de catálogo e ciclo de vida

Cada tarefa de capa registra uma geração. `images.invalidate()` antecede a publicação do catálogo novo; resultados da geração anterior viram cancelamento sem caminho de imagem. A publicação de resultados é ordenada para não perder a liberação de vagas.

Ocultar o frontend cancela tarefas ativas e enfileiradas e desativa novos pedidos nativos. Ao retornar, capas canceladas podem ser solicitadas novamente imediatamente. A fila e o plano não mantêm downloads especulativos enquanto o frontend está oculto.

### Política de erros

| Resultado | Comportamento |
| --- | --- |
| Sucesso/cache | Sem pausa programada |
| Cancelamento/segundo plano | Sem penalidade de erro; pode retomar |
| Falha transitória | Repetição após 2 segundos |
| HTTP 404 | Somente aquela capa aguarda 60 segundos; outras continuam |
| HTTP 429 | Respeita `Retry-After` em segundos ou data HTTP; ausência/inválido usa 60 segundos, limite de 24 horas |
| Sessão negada | Invalida apenas a sessão correspondente e exige recuperação autenticada |

Durante 429, a busca antecipada fora da área visível é suspensa; pedidos visíveis limitados ainda podem encontrar cache local. O sucesso de outra transferência não encurta a suspensão exigida pelo servidor. Não há repetição infinita ocupando os quatro workers durante o prazo.

### Integração adicional do retorno mais recente

O commit de cliente `1dc8c381e49e60ccbe0f84c97dcfe5be3e1d85f3` foi cruzado com esta implementação. A montagem R2 incorpora as melhorias complementares sem substituir as leases, o tratamento de `Retry-After`, a geração ou o plano da plataforma:

- Reuso da conexão TLS quando o corpo HTTP foi consumido por inteiro. Leitura incompleta, erro ou cancelamento continuam desconectando. Pin, certificado, hostname, bloqueio de redirect, tamanho e hash permanecem exigidos.
- Conferir primeiro o arquivo local de nome exato, sempre por tamanho e SHA-256, antes da busca mais ampla por candidatos. Não declarar um arquivo instalado por nome ou existência apenas.

Essas duas alterações estão implementadas e compiladas no componente R2. `StationTransferReuseTest` acrescentou 16 verificações, elevando o conjunto Java de 368 para **384**. A busca conserva os oito candidatos máximos, orçamento de hash, recusa de links e cancelamento. A prova é local; a economia de conexões no telefone ainda depende de medição.

## 5. O que o servidor comprovou

Fonte primária lida: [retorno único do Servidor-pix no commit 54bba11](https://github.com/luziellacerda/Servidor-pix/blob/54bba11c52f35695fd47eabc7145f42af9990426/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md).

O retorno declara API `4bb77ed2b8fb01fe967b90dc18ec3fbd1ee5d58b`, DLL SHA-256 `b08f8313651a10de008d35545ff13569c5a360fb42ee792ad37f2647bd9d107e`, catálogo revisão 4 com 1.816 jogos públicos e quatro plataformas. Todas as capas públicas são originais de `media/revista`, 480 × 720: 1.815 JPEG e um PNG. A otimização não muda IDs, capas ou jogos.

| Limite/prova relatada | Resultado |
| --- | --- |
| Capas por licença/aparelho autenticados | 4.096 pedidos/minuto |
| Capas por origem, agregado | 16.384 pedidos/minuto |
| Ativação, sessão, autorização e artefatos | Limites anteriores de 30 pedidos/minuto por rota/origem |
| Produção HTTPS, cliente de teste Linux | 48 capas; 6.458.397 bytes; 4.546,55 ms; quatro simultâneas; 48 respostas 200 com bytes exatos |
| Jogos verificados pelo servidor | Nove downloads 200 íntegros; nove reutilizações do grant recusadas com 404 |

Esses limites contam pedidos, não bytes por segundo. A medição é do Linux informado pelo operador. **Não é medição da USB, do telefone, de FPS, temperatura ou consumo.** O app não garante a mesma duração em qualquer rede. Não confundir o limite de 4.096 pedidos/minuto com capacidade de catálogo.

## 6. Sinopses e XML: identidade exata

`prepare_visual_metadata.py` lê o mapa `catalogo-candidato-cruzado-20261003.tsv` do servidor e as fontes XML locais. O mapa tem SHA-256 `d030cbecc3a9e406cde24bba9583ec2f8e0920df6b65acb623e8d91c3350de46`. A ligação inicial exige **itemId do servidor + XML/plataforma de origem + posição da entrada + nome exato**. Não se usa aproximação de título para relacionar um jogo a outro.

| Plataforma | Itens mapeados |
| --- | ---: |
| `snes` | 644 |
| `snesbr` | 191 |
| `megadrive` | 887 |
| `megadrivebr` | 94 |
| Total | 1.816 |

Foram importados 180 arquivos-fonte, correspondentes a 167 XMLs únicos; 20 caminhos do inventário não existiam e nenhum XML lido era inválido. Os 36 XMLs legados já presentes em `assets/turbo-game-info/` são preservados byte a byte. Os novos XMLs do APK contêm somente campos descritivos, sem URLs antigas ou caminhos locais. O manifesto da origem e os hashes ficam em `assets/station-metadata/xml-manifest.json` e `evidence/xml-source-inventory.json`.

O resultado atual tem **1.804 sinopses para 1.816 itens**. Foram recuperadas 29 descrições adicionais por identidade local exata e descrição única. Restam 12 itens: seis sem correspondência exata disponível e seis com descrições conflitantes. Eles mostram mensagem de indisponibilidade; nenhuma sinopse foi inventada.

| Plataforma | Sinopses pendentes |
| --- | --- |
| Mega Drive | Battletoads-Double Dragon (USA); Columns III (USA); Lethal-wedding; Sonic The Hedgehog 3 (USA); Tetris |
| Mega Drive BR | Sonic Hedgehog 3D Blast (BR) |
| SNES | Battletoads in Battlemaniacs (USA); Mario Paint; Rise of the Robots; Samurai Shodown; Street Fighter Alpha 2; World Heroes 2 |

Identificadores e provas individuais estão em `assets/station-metadata/missing-station-synopses.json` e `evidence/missing-synopses-exact-search.json`. A tabela compilada `station_game_infos.h` fica ordenada por `itemId` para busca binária. Itens `station_` não caem em busca legada por título. A paginação de 9,5 segundos reinicia somente quando a sinopse selecionada muda; a chegada de um lote de capas não reinicia continuamente a primeira página.

## 7. Efeito real do tema do PC e ilustração do console

Origem do shader: `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\premium-magazine-led.glsl`, SHA-256 `0c6637dc33a83bf38cf1f92691bbbf0a4963f75113c9f0199d63805365634d43`.

Foram mantidas as equações de leitura dos pixels, regiões emissoras, cor e reflexo do shader do PC. A adaptação GLES100 acrescenta precisão inteira explícita e retorno antecipado quando a máscara emissora já é zero. O tempo usa relógio monotônico convertido em unidades equivalentes a 60 Hz; isso não obriga o menu a renderizar a 60 FPS. O limite anterior de 15 FPS em repouso permanece.

`drawMagazineCover` aplica o efeito apenas à capa de jogo selecionada. Reutiliza textura, geometria, transparência e chamada de desenho nativos; não cria sobreposição Java nem outro ciclo de renderização. O LED das plataformas continua usando seu mapeamento existente. Nave e estrelas não foram reativadas.

A auditoria do renderer confirma que a chamada original de triângulos não troca o programa GLSL; os novos programas restauram o estado original após desenhar. Os atributos, stride e offsets constam em `evidence/renderer-program-audit.json`. Falha de compilação do shader é registrada e o desenho original continua disponível.

As ilustrações de SNES e Mega Drive aparecem à direita da sinopse na tela dos jogos. São imagens **geradas para esta entrega**, não fotografias históricas. Cada família utiliza uma textura RGBA de 512 × 512, reaproveitada pela lista BR; as duas totalizam 2 MiB de pixels quando carregadas. Proporção e transparência são preservadas. Em tela estreita/retrato, o layout usa o espaço para o texto e oculta a ilustração. Não há imagens de console implementadas para todas as demais plataformas.

### Origem das ilustrações geradas

Foi usada a ferramenta integrada `image_gen`. `evidence/console-assets-provenance.json` registra os arquivos originais, hashes, dimensões e transformação para textura. Os pedidos visuais podem ser resumidos assim, **sem representar transcrição literal dos prompts**:

- SNES: ilustração fotorealista de produto em estúdio, console original cinza com detalhes roxos e controle, recorte transparente.
- Mega Drive: ilustração fotorealista de produto em estúdio, Mega Drive 1 preto com controle de três botões, recorte transparente.

Arquivos finais: `E:\ESTUDO APK\work\station-visual-covers-20261003\assets\turbo-console\snes.png` e `E:\ESTUDO APK\work\station-visual-covers-20261003\assets\turbo-console\megadrive.png`. Cópias publicadas em `assets/turbo-console/` nesta versão. Esses assets representam os consoles para a interface; não constituem fotografias documentais.

## 8. Netplay: opções reais e limites

Entrada: **Configurações → Jogar em rede**. O cabeçalho chama `openStationNetplay()`. A ponte retorna sucesso depois que o Android aceita abrir a Activity; então o painel é fechado e vídeo/música do frontend são pausados. As duas Activities novas são internas, `exported=false`; a preparação Dolphin usa o processo `:dolphin` e o bootstrap existente.

| Motor preservado | Ação implementada | Limite |
| --- | --- | --- |
| PPSSPP 1.20.4 | Abre suas configurações pela rota existente `PspBootstrap.launch(activity, "", true)` e orienta Rede/WLAN, ad hoc/relay | O modo multiplayer depende do jogo, lobby e configuração original; não existe sala Station criada automaticamente |
| Flycast v2.7-44 | Abre configurações originais por `FlycastBootstrap.launch(activity, "", true)`; orienta GGPO/Native/DCNet conforme suporte | Os modos suportam conjuntos diferentes de jogos; não equivale a prometer rede para todo Dreamcast/Naomi |
| Dolphin 2609-7 | Prepara biblioteca e abre a Activity original `NetplaySetupActivity` | Exige jogos compatíveis, versões/configurações adequadas e conexão; partida entre dois aparelhos ainda não conferida |
| Snes9x EX+ 1.5.85 e MD.emu 1.5.85 | Tela informa indisponibilidade de Netplay nos motores atuais | Não foram substituídos; nenhum botão promete SNES/Mega online |

No Dolphin, `StationFrontend.installedPathsFor("gamecube"/"wii")` roda fora da UI, exige catálogo autorizado e consulta recibos de instalação verificados. Não varre pastas presumidas nem faz HTTP. Ausência de inicialização é erro explícito; retorno vazio significa nenhum jogo instalado verificado.

Os caminhos são entregues em snapshot privado limitado, evitando arrays grandes no Binder. No processo Dolphin, a preparação aguarda `DirectoryInitialization.areDolphinDirectoriesReady`, preserva os diretórios já existentes de `GameFileCache`, acrescenta os pais dos launchPaths válidos, grava `NativeConfig.save(1)` e usa `GameFileCacheManager.startLoad/startRescan`. Só depois abre a interface real de criar/entrar. Métodos/classes foram conferidos no fonte e no DEX integrado, inclusive nomes que sobreviveram ao R8.

O snapshot admite até 40 mil caminhos como limite defensivo do arquivo; **isso não aumenta o limite de catálogo deste APK**. Não contém tokens. Fica em `files/station-netplay/dolphin-*.paths`, permite recriação da Activity e é removido ao finalizar. O preparo não abre telas se o app estiver oculto, e seus callbacks param em `onStop`/`onDestroy`. Nenhum serviço de polling foi adicionado à tela principal.

Não foram implementados presença de usuários Station, convite, matchmaking ou servidor de partidas Station. O servidor de licenças não recebe credenciais de rede dos emuladores. Para oferecer salas entre clientes Station, será necessário contrato próprio de presença/convite, identificação da versão/ROM e conexão efetiva com cada motor; uma lista de usuários sozinha não realiza Netplay.

Fontes primárias: [PPSSPP multiplayer](https://www.ppsspp.org/docs/multiplayer/quickstart/), [configuração de partidas PPSSPP](https://www.ppsspp.org/docs/multiplayer/how-to-play/), [Dolphin 2609 e Android Netplay](https://dolphin-emu.org/blog/2026/09/24/dolphin-progress-report-release-2609/), [implementação Android Dolphin](https://github.com/dolphin-emu/dolphin/pull/14647), [opções do Flycast](https://github.com/flyinghead/flycast/blob/master/core/cfg/option.cpp), [funcionalidades pendentes Emu EX+](https://github.com/Rakashazi/emu-ex-plus-alpha/issues/330).

## 9. Build, insumos privados e preservação

Executar builds e temporários na pasta canônica **E:**. Não compilar diretamente sobre o checkout publicado, não copiar fontes de candidatos históricos por semelhança de nome e não substituir a estável congelada.

A `.gitattributes` desta pasta desativa a conversão automática de quebras de linha para preservar os bytes dos fontes e assets referenciados pelos recibos SHA-256. Os XMLs publicados são as cópias descritivas saneadas, sem URLs comerciais antigas; os originais completos permanecem no computador.

Pré-requisitos locais: Python 3, JDK 17, Android API 34, D8 min API 26, build-tools 35, NDK r28c/Clang para arm64 e os insumos registrados em `PRIVATE-BUILD-INPUTS.json`. A receita conserva alinhamento de 16 KiB. APK base, assinatura, ROMs, BIOS, firmware, chaves e recursos privados não são entregues por este README.

Sequência dos componentes:

1. Conferir o hash do APK base HUD R2 e os hashes das fontes/insumos.
2. Preparar metadados com `prepare_visual_metadata.py` e ilustrações com `prepare_console_assets.py`, usando fontes locais conferidas. O script de metadados depende também de `audit_missing_synopses.py` da pasta canônica.
3. Rodar `test_visual_metadata.py` e a conferência de layout C++. O teste ANGLE fica em `test_shader_angle.py` na pasta canônica.
4. Compilar/testar Station com `station/run_tests.py`, `station/build_frontend.py` e `station/build_module.py`; conferir os recibos atuais, especialmente após integrar o retorno do servidor.
5. Compilar/testar as classes novas por `netplay/build_netplay.py` e `netplay/test_contracts.py`.
6. Conferir a integração e o manifesto. `build/prepare_visual_delivery.py` é a preparação de uma árvore limpa e exige marcadores únicos; não reaplicá-la cegamente sobre fontes já integradas. `build/finalize_netplay_manifest.py` mantém as Activities efetivas; compilar o manifesto com `build/build_visual_delivery.py manifest`. O projeto de recursos é copiado de `E:\ESTUDO APK\work\station-mega-explus-20261003\manifest-decoded`; o framework apktool está em `E:\ESTUDO APK\work\station-snes-explus-20261003\framework`. Ambos são insumos locais da receita. A validação final usa `build/verify_visual_manifest.py`.
7. Compilar o carrossel por `build/build_visual_delivery.py native`; empacotar com a ação `package` somente quando os componentes e o manifesto estiverem prontos. A receita recusa sobrescrever uma saída existente.
8. Conferir assinatura, alinhamento, classes duplicadas, inventário ZIP e `build-result.json`. A exportação para o Git usa `build/export_visual_delivery.py`; não publica insumos privados.

Substituições previstas sobre o APK base: `classes28.dex`, `lib/arm64-v8a/libstation_frontend.so`, `lib/arm64-v8a/libturbo_carousel.so` e `AndroidManifest.xml`. O Netplay entra em novo DEX, **`classes35.dex` na base examinada**. Metadados/ilustrações são assets novos; os assets anteriores e bibliotecas de emulação devem permanecer byte a byte. A receita verifica todas as entradas preservadas e recusa mudanças fora da lista prevista.

Componentes R2 já concluídos, sem confundir seus hashes com o hash do APK:

| Componente | SHA-256 |
| --- | --- |
| `station/build/classes28.dex`, 142.428 bytes | `4ebf1507b278779aa8cb4cdea16e20697827968643d7172de5c49a852371855f` |
| `libstation_frontend.so` | `4da25d5bc91d74628944b6a8ec1d8b5fdc31c7dff8314852b05164a164676ed2` |
| `libturbo_carousel.so` recompilada | `5edea19f156568d8801a80104b36fc4f7e060e81d55badc473e874a437546b30` |
| DEX novo de Netplay | `25952f2de2682e639cc565a0fdc8451fad60b9c49a4704cd41b393899e0c56ba` |

Os cabeçalhos grandes listados em `PRIVATE-BUILD-INPUTS.json` continuam locais; `console_assets.h` pode ser regenerado dos PNGs publicados. O Git mais um SDK não basta para reconstruir o APK inteiro sem a base e os insumos identificados. Não remover o GenPlusGX por ter integrado MD.emu: Master System/Game Gear ainda dependem das rotas existentes.

Instalar posteriormente por atualização com a mesma assinatura, preservando dados. Não desinstalar nem limpar a identidade do Keystore para fazer um teste. Correções de pasta, recursos e configuração devem estar no código/primeira inicialização, nunca apenas no telefone de teste.

## 10. Evidências e alcance dos testes

| Evidência | O que foi comprovado |
| --- | --- |
| `evidence/station-test-results.json` | 384 verificações locais R2: 368 anteriores de arquivos/protocolo/catálogo/armazenamento/instalação/sessão/concorrência + 16 de reaproveitamento TLS e arquivo local exato |
| `evidence/station-cover-delivery-result.json` | Quatro workers, zero atraso após sucesso, cache, políticas e hashes dos componentes; 18 verificações C++ de planejamento/retry |
| `evidence/cover-concurrency-independent-review.json` | Revisão independente dos bloqueios, geração, 429 e preservação da sessão |
| `evidence/metadata-build-result.json` | 1.816 identidades exatas, 1.804 descrições e 12 ausências |
| `evidence/visual-implementation-result.json` | 13 testes Python e 98 casos de layout C++ aprovados; conferir hashes atuais |
| `evidence/shader-angle-validation.json` | Compilação/link dos dois shaders reais GLES100 e programa de prova de FrameCount no Windows ANGLE, sem janela |
| `evidence/shader-integer-precision-review.json` | Precisão do contador inteiro e adaptação móvel |
| `evidence/transfer-reuse-independent-review.json` | Revisão independente dos dois portes de conexão/arquivo, sem novo defeito comprovado |
| `evidence/renderer-program-audit.json` | Compatibilidade do desenho de triângulos, atributos e restauração do programa |
| `evidence/netplay-test-result.json` | 14 verificações executáveis de caminhos/snapshot e 12 contratos de APIs do doador/fonte |
| `evidence/netplay-build-result.json` | Compilação das novas classes; não comprova uma partida |
| `build-result.json` canônico | APK efetivamente montado, mudanças previstas, assinatura/alinhamento e integridade do inventário |

O ANGLE utilizado no Windows informa EGL 1.5 e OpenGL ES 3.0; os fontes compilados são GLSL ES 1.00. Houve aviso do tradutor HLSL sobre `f_region`; a análise registrou retorno inicializado nos ramos GLSL e atribuição de `activeMagazineModel` antes das chamadas. Não houve falha de link. O teste aritmético de FrameCount conferiu 0, 32.767, 65.535 e 1.000.000 com `glError=0`. Isso não substitui compilação/desenho no driver do telefone.

## 11. Aceite pendente no telefone

Após conectar a depuração autorizada e deixar o app fora de uma partida:

1. Conferir hash/assinatura da instalação R2, abrir sem perder a licença e registrar revisão/contagem do catálogo real.
2. Abrir SNES e Mega, observar quatro capas simultâneas e continuidade sem outros toques; rolar nos dois sentidos e separar primeira carga de cache quente.
3. Sair/voltar e conferir cache sem novo download das mesmas revisões. Atualizar o catálogo durante transferências e verificar que capa antiga não aparece no item novo.
4. Conferir os LEDs, a capa retangular do jogo, texto abaixo/ao lado conforme layout e a ilustração do console; registrar erros GLSL e resposta visual do driver.
5. Conferir sinopse de identidade conhecida, paginação enquanto outras capas chegam e mensagem dos itens ainda sem descrição.
6. Baixar jogo pequeno, cancelar um download, repetir com novo grant, instalar, abrir, sair e confirmar instalado/licença preservados. Conferir arquivo local reutilizado por hash.
7. Abrir Jogar em rede; conferir PSP/Flycast nas configurações originais e Dolphin com seus jogos instalados. Confirmar retorno sem novo login e sem frontend trabalhando em segundo plano.
8. Para declarar Netplay funcionando, realizar uma partida em dois dispositivos com jogo/versões compatíveis e registrar motor, versão, modo de conexão, início, controles e saída.

Ainda existe a pendência histórica de restaurar `stay_on_while_plugged_in` de `3` para `0`, caso permaneça no valor temporário quando o aparelho retornar. Não alegar restauração enquanto estiver sem USB.

## 12. Como adicionar plataformas, jogos e metadados depois

### Plataforma e jogos

1. Confirmar no servidor os arquivos reais, plataforma canônica, `itemId`, `coverId`, revisão, capa revista e descritor completo. Preservar IDs existentes. Não usar o nome exibido como caminho ou chave.
2. Conferir `StationPlatforms` e o mapa nativo: alias, pasta, extensões, launchPath e motor integrado. Plataforma desconhecida deve continuar explícita como não suportada; nunca cair em outra pasta por aproximação.
3. Conferir preparação repetível do motor, recursos permitidos, interface/controles próprios, processo, início pelo botão Jogar e retorno ao frontend. Incluir o necessário no APK para instalação nova.
4. No servidor, validar índice efetivo, permissões do usuário do serviço, capa autenticada 200, grant assinado, bytes/tamanho/hash reais e uso único. Só então publicar catálogo que anuncie os novos jogos.
5. No app, testar publicação, busca dentro da plataforma, cache de capas, download/cancelamento/instalação/remoção, abrir jogo e voltar. Registrar o primeiro par `itemId`/`coverId` e correlação que falhar; não atribuir a causa por suposição.

### Sinopses e ilustrações

1. Obter o mapa exato de origem das entradas novas e os XMLs reais. Atualizar explicitamente `LABELS`/mapa quando houver nova plataforma.
2. Gerar `station-synopses.json` e `station_game_infos.h`, verificando unicidade de `itemId`, ordinal/nome da origem e descrição. Se houver versões contraditórias, resolver com origem comprovada antes de associar.
3. Regerar inventário e relatório de ausências; incluir somente campos descritivos no APK.
4. Para nova ilustração de console, incluir asset com proveniência, regenerar `console_assets.h`, mapear família em `stationConsoleIndex` e conferir proporção/layout. Compartilhar textura entre variantes regionais somente quando for o mesmo aparelho.
5. Para outro desenho de revista, acrescentar modelo/máscara do shader a partir da imagem real e teste de pixels; não alterar IDs/revisões comerciais para ajustar apresentação.

### Netplay

1. Confirmar suporte no motor Android efetivamente integrado e sua versão; presença de um arquivo antigo de rede na árvore não comprova suporte ativo.
2. Usar API/Activity original demonstrada no APK, com preparação real de biblioteca e ciclo de vida. Métodos removidos pelo R8 não são rotas válidas.
3. Explicar ao usuário quais modos/jogos funcionam; não oferecer botão vazio nem simular sala.
4. Se forem necessárias salas Station, produzir contrato próprio de presença/convites e compatibilidade, sem reutilizar Bearer/grants comerciais como credencial de pares.
5. Conferir em dois dispositivos antes de anunciar suporte operacional.

### Capacidade

Esta linha permanece limitada a **4.096 itens por catálogo e 12 MiB no envelope**. A meta separada de 40 mil jogos não foi incorporada aqui. Para ampliar, alterar de forma coordenada contrato/paginação assinada, parser Java, limites JNI, mapas de retry/Inbox, publicação, memória, cache e testes de escala. Não basta elevar uma constante ou o orçamento de requisições de capas.

## 13. Limitações observadas que devem acompanhar esta entrega

- Telefone indisponível na USB: sem prova de instalação, renderização, throughput ou consumo desta revisão.
- Doze sinopses ainda sem fonte única comprovada; vinte caminhos XML do inventário estavam ausentes.
- Ilustrações de console implementadas somente para as famílias SNES/Mega; catálogo comercial atual contém essas quatro listas regionais.
- SNES EX+ e MD.emu atuais não oferecem Netplay integrado. PSP/Flycast/Dolphin usam interfaces originais, sem lobby Station.
- Não houve partida Netplay entre dois aparelhos nem revisão de todos os jogos/motores.
- O limite de catálogo continua 4.096; a mudança de limite por minuto no servidor não implementa 40 mil jogos.
- A montagem depende de base assinada e insumos privados identificados. O renderer original continua binário preservado.
- Recibos da primeira montagem não devem ser usados para certificar código R2 alterado depois deles. O recibo final e a exportação devem ser atualizados juntos.

Essas lacunas são de escopo ou conferência registrados. Nenhuma delas autoriza inventar rotas, associar capas/sinopses por aproximação, desligar validação de assinatura/hash ou reparar apenas a instalação do telefone.
