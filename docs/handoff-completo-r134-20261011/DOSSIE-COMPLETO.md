# Dossiê completo do TurboStations e handoff de manutenção

Aplicativo R134, auditoria online, servidor e entrega ao consumidor.

**Fonte executável:** 4f9039eb9ce13907ce043870bfe1f6e294888556. **APK R134:** f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2.

O relato de carregamento com três jogadores e de pedido para fechar o app está registrado na auditoria atual. Correções em fonte não equivalem a uma nova instalação homologada.

## 1 Estado consolidado e operação

### 1.1 Objetivo e modo de leitura

Este dossiê registra a composição técnica do TurboStations R134 e entrega o contexto necessário para o proprietário, o próximo agente de manutenção e o operador do servidor. Ele relaciona código, contratos, emuladores, interface, arquivos, autenticação, downloads, multiplayer, receitas de reprodução e evidência física. As duas instalações USB solicitadas foram concluídas antes da montagem final deste documento.

A unidade de referência é o APK exato identificado por SHA256, associado ao commit executável, congelamento de fontes e identidade de runtime. Um nome R134, uma data de arquivo, um README, uma resposta de disponibilidade ou o limite teórico de jogadores não identificam sozinhos uma entrega autorizada. A leitura começa pelo estado consolidado e segue para os capítulos de serviços, frontend e motores offline e multiplayer.

O escopo detalhado é o comportamento observável no código e nos recibos consultados. Binários de terceiros, fontes originais não localizadas, jogos específicos não testados e estados de produção sem resposta assinada continuam com limites expressos. O documento registra essas lacunas em vez de preencher detalhes por suposição. A presença de um recurso implementado não significa sua homologação física universal.

Os anexos técnicos contêm o inventário completo de nomes, tamanhos e hashes das entradas do APK, os registros das bibliotecas e DEX, o mapa de fontes produtivas congeladas, os índices de consulta e os dois recibos desta operação. Os hashes das entradas vêm dos mapas integrais de verificação final; não foram recalculados nesta montagem documental. O SHA integral do APK instalado foi conferido pelo instalador em cada telefone.


### 1.2 Identidade da entrega R134

A R134 é composta sobre o donor R133 assinado. As alterações permitidas são as páginas agrupadas de efeitos gráficos, as configurações dos owners PS3 e PS4 e os dois rótulos de configuração Sony no carrossel. A mudança de compartilhados exige renovar as identidades de PSX, N64, GameCube e Wii. Seus cores, opções, perfis de controle e protocolo permanecem vinculados às provas de preservação.

A conferência final registra sete substituições, zero adições e 13.853 entradas preservadas. Os 38 DEX fora dos dois escopos são byte idênticos. No DEX28, o delta é limitado à família StationGraphicsPanel. No DEX40, o delta é limitado às famílias Ps3Activity e Ps4Activity e classes internas geradas. As classes externas às famílias permitidas foram comparadas por projeção byte a byte. Manifest, resources, assets Sony, biblioteca frontend, vídeos e política de loop permanecem preservados.

O certificado original foi aceito pelo Android nas duas atualizações. O pacote foi verificado com assinatura APK v2 e v3 e alinhamento de 16 KiB. Manter esse certificado e identidade é necessário para atualizar sem romper a instalação existente; nenhuma chave ou senha de assinatura faz parte deste dossiê.

| Elemento | Valor verificado |
| --- | --- |
| Revisão | R134 |
| Pacote Android | org.turboramastation.frontend |
| Entrada pública | org.emulationstation.frontend.auth.LoginActivity |
| Frontend | org.emulationstation.frontend.ESActivity |
| Fonte executável | 4f9039eb9ce13907ce043870bfe1f6e294888556 |
| APK SHA256 | f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2 |
| APK bytes | 2714991631 |
| APK no backup | F:\TurboStations-Backup-Completo-20261011\desenvolvimento\TurboStations-Premium-R134-20261011.apk |
| Certificado SHA256 | 7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825 |
| Congelamento SHA256 | 7b9eead9ecd79d1582647b1b41d45158a36627ba6b8231663a3fa87067a97af0 |
| Identidade de runtime SHA256 | 2d6fc1c1933b4dc88aa09192138b8564b5f0b743461faa7580896b8339b2067f |
| Donor R133 SHA256 | 945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112 |
| Escopos aprovados | graphics-settings-grouped-pages, sony-emulator-settings-and-return, native-sony-settings-action-labels |
| Entradas ZIP | 13860 |
| DEX principais e asset PS4 | 40 principais + 1 em assets |
| Entradas de bibliotecas nativas | 166 |


### 1.3 Instalação USB concluída nos dois telefones

O Edge 30 e o Samsung A56 foram atualizados individualmente pelo USB com o mesmo arquivo R134. A seleção do aparelho foi explícita e a operação não escolheu automaticamente outro destino. O estado inicial de cada telefone foi conferido para impedir a atualização enquanto houvesse emulador, jogo, painel desconhecido ou serviço de download ativo.

O instalador resolveu os ponteiros do projeto, do backup único e de desenvolvimento ATUAL; conferiu o APK real, os recibos, as fontes congeladas, os payloads, o certificado original e o alinhamento. A atualização usou instalação direta por streaming para o usuário Android 0, sem cópia extra de APK no telefone. Após a atualização, leu o SHA256 integral da instalação e comparou com a R134.

UID, firstInstallTime e dataDir permaneceram iguais. Não houve desinstalação, limpeza de dados, troca de identidade de assinatura, instalação de emuladores externos, remoção de tarefas, force stop ou alteração de configurações Android nesta operação. Esses controles documentam preservação da identidade e diretório; não representam comparação byte a byte de cada save e de todo o conteúdo privado do aplicativo.

A entrada pública foi solicitada e o frontend foi observado nos dois aparelhos. Esta operação comprova instalação e abertura. Não valida nova autenticação, catálogo produtivo atual, download real, criação de sala, controles físicos, partida entre os dois telefones, firmware consumido por jogo, temperatura ou estabilidade. Os recibos registram esses estados como não validados.

| Aparelho | Conclusão local UTC menos 3 | Resultado |
| --- | --- | --- |
| motorola edge 30 | 11/10/2026 20:18:33 | R134 instalada e SHA integral igual; dados e UID preservados; frontend observado |
| SM-A566E | 11/10/2026 20:23:26 | R134 instalada e SHA integral igual; dados e UID preservados; frontend observado |

- Recibo Edge 30 outputs/instalacao-r134-edge30.json. APK anterior R133 SHA256 945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112.
- Recibo Samsung A56 outputs/instalacao-r134-samsung-a56.json. APK anterior SHA256 3c5fb1cb84330b4cea635152e65b7498bf6baf15192371789945fcaf861226c1. A revisão anterior não foi inferida apenas pelo nome.

### 1.4 Repositórios fontes e ponteiros de autoridade

O repositório do aplicativo é https://github.com/luziellacerda/TurboElden. A fonte executável consultada é o commit 4f9039eb9ce13907ce043870bfe1f6e294888556, no ramo fix/station-settings-refinement-r134-20261011. O ramo padrão versao-funcional permaneceu em documentação anterior de 02/10/2026 durante a consulta. Ler o ramo padrão sem ref explícito pode omitir os módulos recentes.

O repositório do servidor é https://github.com/luziellacerda/Servidor-pix. O retorno real consultado permanece a6b58e9beb12eb564c1b58d9d4c32ed3e7513861 no ramo feat/station-r128-aplicado-20261011. A entrega documental R133 existe no ramo docs/station-r133-final-console-modes-20261011, commit 524d2ebff08353fda62aacbc5f05f9248ba69b7c. Essa publicação do pedido e dos recibos não é retorno de ativação dos novos motores.

O checkout atual utilizado para verificar e instalar está em C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git. Seu HEAD é o commit R134. Há recibos e auditorias locais não versionados e alterações de auditoria preservadas de outras operações; este trabalho não os modificou. A árvore pública copiada em F:/TurboStations-Backup-Completo-20261011/fontes/TurboElden termina nos conteúdos R133 e não possui todas as novas receitas R134.

Os ponteiros de seleção lidos foram work/CURRENT-LOCAL-ARTIFACTS.json do projeto de origem, F:/TurboStations-Backup-Completo-20261011/CURRENT-LOCAL-ARTIFACTS.json e desenvolvimento/ATUAL.json. Eles concordam em R134, APK, SHA, bytes, fonte e assembly. Seus campos de instalação ainda retratam o momento anterior às atualizações: lastInstalled R133 e candidato R134 installed=false. Os dois recibos novos deste dossiê são posteriores. Não substituir a verdade física recente por um booleano de preparo anterior.

Também há defasagem documental conhecida: README do ramo recente começa em R127; release-channels/ACTIVE.json resume R130; ONLINE-SYSTEMS.json resume R131; AGENTS começa em R133. Esses arquivos continuam úteis para regras e história, mas não prevalecem sobre a conciliação do pacote R134 e recibos recentes. Referências stable-2p R76 e test-4p R95 são canais históricos identificados por hash, não promoção automática da R134 a estável.


### 1.5 Arquitetura da composição e cadeia de proveniência

O aplicativo reúne frontend nativo, clientes Java de serviços, apresentação e pontes, owners e processos de emulação e bibliotecas oficiais ou preservadas. O carrossel usa libturbo_carousel.so; libstation_frontend.so fornece a ponte que permanece idêntica na R134. Java publica catálogo e estados, autoriza operações e encaminha comandos para as rotas conhecidas. Os motores mantêm suas opções e mecanismos próprios de renderização, áudio, input e armazenamento.

A composição recente inclui o snapshot completo R124, N64 R125, Dolphin R126, PSX normal R127, a preparação Sony local R129 e menus e loop R130. R131 corrigida incorporou owners Sony internos. R132 acrescentou preparação de shaders durante loading, fichas Sony e migração limitada do caminho Switch. R133 acrescentou fotos PSP, PS3 e PS4. R134 muda o painel de efeitos e configurações reais Sony. Cada camada exige seu donor, freeze e receipts; copiar uma Activity ou receita histórica inteira pode reverter mudanças de camadas posteriores.

As bibliotecas Sony são assets privados extraídos para diretórios isolados e usam processos próprios. O owner PS4 usa classloader filho e namespaces isolados de SDL 3 e bibliotecas para evitar colisão com o frontend e outros motores. A existência de um mesmo basename em lib/arm64-v8a e assets/sony não implica intercambialidade.

O inventário deste APK contém 166 entradas terminadas em .so, incluindo assets Sony, 40 partições DEX principais e um owner.dex PS4 em assets. O nome de uma biblioteca prova presença no pacote, não sua execução por todo comando, compatibilidade de todos os jogos ou capacidade de multiplayer. O apêndice relaciona cada biblioteca com tamanho e SHA do mapa final; o anexo completo conserva todas as 13860 entradas ZIP.


### 1.6 Reprodução assinatura e preparação do pacote

O objetivo de reprodução é obter bytes ligados às fontes e dependências exatas, sem alterar a entrega instalada por tentativa histórica. A receita atual está em integration/settings-refinement-r134/recipe. O donor obrigatório R133 tem SHA256 945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112 e 2.714.971.151 bytes. Os donors anteriores R132, R131 corrigida e R130 continuam relevantes para reconstruir a cadeia; não apagá-los por nome ou data.

build_java_payloads.py verifica ferramentas e classpaths fixados por hash, usa JDK 17, Android 34, D8/build-tools35, stubs Android de lambda e Apktool3.0.3. Compila somente os três fontes produtivos R134: StationGraphicsPanel, Ps3Activity e Ps4Activity. As famílias de DEX e classes externas são verificadas antes e depois da montagem, incluindo preservação de inicializadores estáticos explícitos do donor.

patch_settings_labels.py altera somente duas C-strings Sony de mesmo tamanho na biblioteca do carrossel. A inversão deve recuperar o binário original inteiro e manter ELF64/AArch64, segmentos LOAD e alinhamento de 16 KiB. O agregado confere fontes, classpaths, escopos de DEX, três payloads e inversão. A identidade de runtime deriva os quatro IDs finais dos compartilhados e conserva cores, opções e perfis.

assemble_apk.py monta as sete substituições sem adições. verified-final.json liga o arquivo assinado ao congelamento e à identidade e registra mapas integrais de entradas. tooling/release/compile_current.py resolve a seleção explícita e tooling/release/install_current.py verifica a entrega antes de operar no telefone. As receitas inferiores que só produzem payloads não são prova de APK final ou instalação.

A árvore de assembly utilizada é G:\StationNormalOwnersR127\settings-refinement-r134\assembly. Os recibos principais são verified-final.json, source-freeze.json, identity/runtime-identity.json e payload-receipt.json da revisão. As ferramentas preservadas estão no backup F:/TurboStations-Backup-Completo-20261011/ferramentas. Chaves, senha do certificado, APKs e conteúdo Sony ficam no canal privado local. Não incluir esses bytes em commits públicos.

Esta operação instalou o APK já criado e verificado; não recompilou a R134 nem qualificou uma reconstrução integral feita só com o backup F. A cópia de fontes F ainda R133 e os mapas locais R134 exigem conciliação para declarar o backup atual plenamente reproduzível. Guardar o checkout, os donors e os inputs vinculados pelos hashes até essa conferência específica.


### 1.7 Procedimento operacional para futuras instalações

A autorização recebida nesta conversa cobre a atualização dos dois aparelhos conectados individualmente. Para uma operação futura, identificar modelo e serial USB explicitamente, confirmar autorização ADB e usuário Android 0 e verificar os caminhos do pacote existente. O modelo informado por adb devices pode trocar espaços e hífens por sublinhado; a comparação efetiva deve usar ro.product.model.

Antes de atualizar, conferir Activities reais e serviços ativos. Se houver jogo, emulador, download ou painel desconhecido, o usuário deve sair ou aguardar. Não encerrar processos para satisfazer a atualização. Ler o SHA integral anterior; quando não estiver nos históricos explícitos, usar o SHA observado como baseline esperado. Não desinstalar nem limpar dados para resolver incompatibilidade de assinatura ou armazenamento.

Resolver e conferir novamente o candidato, recibos e fonte após o preflight demorado, imediatamente antes da instalação. Atualizar por streaming com a assinatura original. Conferir o SHA integral no telefone, UID, firstInstallTime e dataDir e salvar recibo próprio. Solicitar entrada pelo Login público, observar o frontend de forma delimitada e registrar authentication-pending se a entrada exigir ação humana.

O fallback de Gallery histórica é limitado a um retry da entrada pública após nova verificação de ociosidade. Não restaurar Activities antigas nem remover tarefas para forçar navegação. Split APK, pacote não instalado, outro usuário, assinatura diferente ou layout inesperado exigem tratamento revisado; o instalador atual não transforma esses casos em instalação limpa automática.


### 1.8 Proteção de dados e limites do handoff

Este dossiê pode conter nomes de endpoints públicos, contratos, namespaces, caminhos de trabalho e hashes técnicos. Não contém senha de assinatura, chave privada, bearer, código pessoal de ativação, identidade de usuário, serial USB, BIOS, firmware, jogo, save, mídia privada ou dump bruto de sessão. Os dois recibos foram produzidos pelo instalador sem serial ou dados de sessão pessoal.

Os anexos documentais extraídos não substituem o kit privado original de implantação do servidor. O operador precisa dos recibos e binários originais byte exatos, perfis e autorização administrativa de produção descritos no capítulo online. Campos sanitizados, aliases, manifests públicos e fontes citadas servem para compreensão e verificação, não para fabricar atestação ou aprovar uma sala recusada.

Os servidores produtivos não foram modificados por esta tarefa. Não houve deploy, restart, cadastro de engine, mudança de licença ou consulta autenticada comercial. As URLs descritas são evidência de código e contratos lidos; não representam teste de disponibilidade realizado durante a instalação. Não remover guardas, assinatura ou aprovação específica para fazer um botão online parecer habilitado.


### 1.9 Qualificação restante e plano de aceite

A R134 está instalada nos dois aparelhos e abre o frontend. O próximo teste funcional deve registrar o APK exato de cada participante e o resultado, com data e limites. Conferir navegação, busca, efeitos, capas, loop somente no herói de plataforma, central de downloads, preservação dos jogos e retorno. Conferir configurações Sony e persistência antes de atribuir qualquer efeito a um jogo real.

Para gameplay offline, testar um título autorizado por motor e formato e registrar renderização, áudio, controle por toque, controle físico, saves, pausa, retorno e reapertura. Para Sony, firmware preparado e owner aberto não bastam: ISO ou PKG real, importação e execução precisam de evidência específica. Para Switch, rota corrigida não comprova boot do título.

Para multiplayer, obter snapshot v3 assinado fresco que aprove os IDs R134, conteúdo, modo, quantidade e perfis exatos. Criar sala nova com os dois aplicativos atualizados, observar prontidão, início, inputs de cada slot, pausa e reconexão, encerramento humano e retorno. Quatro ou cinco aparelhos exigem cenário separado. O ledger preparado e os testes de transporte no PC não comprovam essa execução física.

Para desempenho, medir no mesmo aparelho e cenário tempo de abertura, uso de memória, frame pacing, temperaturas, energia e duração. O menu limitado a 30 fps, a ausência de um novo timer e a preparação durante loading não demonstram redução térmica. Os resultados históricos permanecem atribuídos à revisão em que foram feitos e não se tornam automaticamente resultados da R134.


## 2 Auditoria atual e operação para entrega ao consumidor

### 2.1 Incidentes relatados e estado para entrega ao consumidor

Após a instalação da R134 nos dois aparelhos, o proprietário relatou que uma partida com três participantes permanecia carregando e que, ao sair de uma partida online, o celular pedia para fechar o aplicativo. Esses relatos passam a compor o estado operacional atual. A instalação com SHA correto e a abertura do frontend não homologam o multiplayer.

A revisão atual foi realizada sem acesso USB aos telefones. O jogo, plataforma, etapa exata de carregamento, horário da ocorrência, APK do terceiro participante e texto do diálogo não foram identificados. O relato de fechar o aplicativo é compatível com falha de resposta, mas a classificação como ANR requer o registro do Android; uma exceção ou falha nativa exige outra evidência.

A entrega comercial do online deve aguardar a correção dos defeitos comprovados no código, a aplicação administrativa dos motores exatos quando exigida e a execução do aceite físico por edição, modo e quantidade de jogadores. Os achados estáticos não permitem afirmar que o defeito relatado no telefone foi resolvido.


### 2.2 Mapa de responsabilidades do aplicativo completo

LoginActivity e StationLogin conduzem ativação e sessão autenticada; StationApi verifica TLS, prova de requisição e envelope assinado. StationFrontend e as pontes Java e JNI publicam a biblioteca para o carrossel. O frontend nativo apresenta hierarquia, pesquisa, capas, vídeos, efeitos e ações de jogo.

A central de downloads obtém grants assinados e acompanha a fila. StationInstaller e StationArchive instalam transacionalmente os formatos suportados e usam recibos para remoção. A biblioteca local e o catálogo remoto têm responsabilidades diferentes: indisponibilidade de sessão não apaga jogos instalados nem autoriza qualquer novo download.

Os resolvedores offline escolhem owners por plataforma, formato e configuração. Online acrescenta identidade de conteúdo, engine e runtime, perfil de controle, modo aprovado, slots e sala assinada antes de lançar o owner. Os processos de Sony seguem exclusivos do offline. Os owners normais N64, Dolphin e PSX não podem ser substituídos por um core genérico por conveniência de cadastro.

Os capítulos de serviços, frontend e motores e multiplayer apresentam as funções, campos persistidos e condições de cada domínio. O índice java-methods.json dá arquivo, classe, assinatura e linhas das declarações disponíveis. Os índices de DEX e bibliotecas apresentam a presença dos módulos compilados que não têm fonte completa disponível.

| Domínio | Entrada ou responsável | Condição de operação |
| --- | --- | --- |
| Identidade e catálogo | LoginActivity, StationLogin, StationApi | Sessão e respostas assinadas; licença e identidade de dispositivo |
| Biblioteca e apresentação | StationFrontend, libstation_frontend, libturbo_carousel | Publicação atual e lifecycle; cache e mídia com limites |
| Downloads e instalação | DownloadService, StationDownload*, StationInstaller, StationArchive | Grant vigente, fila, instalação transacional e recibos |
| Offline | Resolvedores e owners de cada plataforma | Arquivo/formato e dependências reais do motor |
| Lobby online | StationRoomsActivity e StationOnlineClient | Edição, engine, modo, capacidade e roster assinados |
| Partida e reconexão | StationGameSession e StationMultiplayerSession/Tunnel | Binding, geração, epoch, ACK/READY e recuperação v3 |
| Encerramento | Owner Activity, sessão humana e leave | Autorização humana, recursos encerrados e confirmação da sala |


### 2.3 Índice de fontes e funções e limites de reconstrução

O parser de sintaxe do JDK indexou 281 fontes Java e 3.650 declarações de métodos, construtores e métodos de classes anônimas; 97 são declarações native. Isso permite localizar uma função com precisão e buscar suas chamadas. Expressões lambda não são tratadas como métodos independentes pelo índice. A indexação não executa o código nem resolve semanticamente as APIs Android.

A composição parte de 234 arquivos R124 e aplica os overlays R125, R126, PSX, hosts Sony e menus R134. O índice mantém a origem de cada arquivo. Transformações de bytecode posteriores, como StationFrontend, StationSinglePassVideo720 e SwitchConfigPatcher, estão descritas pelas receitas e não são apresentadas como Java integral reconstruído.

O índice adicional de todas as 41 entradas DEX do APK, lidas e conferidas pelos hashes de cada entrada, enumera 51.615 definições de classes e 311.866 definições de métodos; 2.001 são declarações nativas. São 40 partições principais e o owner.dex PS4 em assets. dex-defined-methods.json.gz contém seus descriptors, partição e flags. Esse inventário cobre as assinaturas definidas nos DEX, incluindo componentes de terceiros; não exporta instruções, corpos de métodos ou constantes arbitrárias e não reconstrói a implementação nativa.

integration-build-source-index.json registra caminho, tamanho e SHA256 de 209 arquivos de integração e compilação presentes antes da nova correção de lifecycle. Os arquivos da correção têm seu próprio recibo. As 40 partições DEX principais, o owner.dex PS4 em assets, 166 entradas de bibliotecas nativas e 13.860 entradas do APK estão integralmente enumerados nos anexos do pacote R134.

O loop C++ original do LibretroPlayer e alguns componentes de terceiros não têm fonte exata localizada. O repasse registra essa dependência por hash, interface e limitação. O repositório público sozinho não reproduz o APK de 2,7 GB: donors, classpaths, materiais privados e assinatura original continuam sendo inputs obrigatórios identificados pelas receitas.


### 2.4 Fluxo de partida de três e pontos de confirmação

No transporte v3, três jogadores formam dois links entre o host e os convidados. Cada link tem dois attachments, totalizando quatro conexões. O estado Playing depende de HELLO, confirmação de pausa e READY no epoch atual em todas as conexões, com as janelas Pending zeradas. Uma conexão WebSocket aberta ou um PING não confirma consumo pelo motor.

A implementação do servidor consultada não estabelece um prazo global para concluir starting ou synchronizing. O heartbeat de presença e o PING podem manter a sala enquanto uma conexão não chega a READY. Os timeouts de inatividade do transporte e de presença disparam recuperação, conservando a sala; não constituem um pedido humano de sair.

O operador deve localizar a etapa que falta em cada uma das quatro conexões. Registrar apenas geração, epoch, slot, estado HELLO/PAUSED/READY, offsets accepted/delivered/Pending e categoria de erro redigida. Não colocar ticket, requestProof, Authorization, conteúdo do jogo, nomes pessoais ou IPs nos recibos públicos.

A quantidade três precisa estar aprovada para a edição e modo selecionados. O teto teórico quatro não autoriza qualquer partida com três. PSX standard-2p-v1 e a política efetiva Mega de duas portas não devem oferecer três; SNES exige o perfil multitap e modo correspondente; N64/GameCube/Wii exigem os vínculos finais específicos e as contagens permitidas.


### 2.5 Coleta de diagnóstico sem USB

Para identificar o diálogo, o suporte pode receber uma foto enviada voluntariamente pelo usuário com dados pessoais removidos, junto do modelo, versão Android, versão/hash do aplicativo quando disponível, jogo/edição/plataforma, quantidade de jogadores e ação que precedeu a falha. Uma foto identifica a mensagem; não identifica sozinha a thread bloqueada.

No servidor, correlacionar o horário e um identificador de suporte redigido com os estados de cada attachment e o resultado dos comandos start, ticket, resume e leave. Registrar 409 com sua categoria exata. O recebimento HTTP de leave não substitui a confirmação de que a sala foi encerrada ou o participante foi removido.

No Android API 30 ou superior, uma futura coleta dentro do próprio aplicativo pode consultar ActivityManager.getHistoricalProcessExitReasons e ApplicationExitInfo. REASON_ANR e getTraceInputStream podem oferecer a pilha; a disponibilidade do trace não é garantida. A R134 não foi alterada nesta revisão para coletar ou enviar esses dados automaticamente. Qualquer exportação deve permanecer local e exigir ação explícita do usuário.

O watchdog ou a instrumentação devem servir ao diagnóstico. Não matar automaticamente o app, descartar saves ou fingir READY para remover o carregamento. Antes de publicar um novo APK, a coleta precisa de limites de tamanho, retenção curta, redação e uma validação para assegurar que não registra licença, ticket, caminhos pessoais ou conteúdo dos jogos.

- [Diagnóstico de ANRs Android](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs).
- [ApplicationExitInfo e traces](https://developer.android.com/reference/android/app/ApplicationExitInfo).

### 2.6 Operação de saída e invariantes de dados

A saída nasce da ação humana no painel ou botão de retorno confirmado. A UI marca a intenção e permanece responsiva enquanto os recursos são encerrados. A sessão precisa cancelar requests e transporte, sinalizar o owner para sair, observar o encerramento dos workers e somente então retornar ou reabrir o frontend. Uma resposta tardia de sessão antiga deve ser ignorada por geração e identidade.

Não executar esperas de término de threads, bloqueio de sockets ou fechamento nativo demorado segurando um monitor usado pelo callback do transporte. Operações em workers também precisam de ordem de locks e cancelamento válidos; mover a espera para outro executor sem acordar o motor não comprova encerramento.

A notificação leave precisa manter o mesmo roomId do pedido humano. Uma rejeição explícita por geração stale admite buscar snapshot atual, confirmar a mesma sala e repetir de forma limitada com a nova geração. Erro de rede ambíguo não autoriza uma mutação cega; uma nova sala nunca deve receber a saída destinada à anterior.

Os saves online isolados, arquivos offline e recibos locais permanecem distintos. O encerramento não limpa dados da instalação, não troca o certificado e não copia estado online de sessão para o save offline. Remoção de jogo deve seguir a transação e recibo do instalador, preservando arquivos não registrados.


### 2.7 Qualificação do produto e regressões obrigatórias

O aceite abaixo define o que o responsável deve comprovar na candidata com APK e identidade exatos. Os ensaios de concorrência e contratos executados no computador são registrados no relatório da correção. As linhas de aceite físico permanecem pendentes até serem executadas nos aparelhos, sem confundir teste de preparação com jogo real.

Qualificar host e convidado nas duas posições e repetir em três participantes no mesmo conteúdo e modo aprovado. A aprovação de um jogo e uma edição não se estende automaticamente a todas as ROMs, BIOS, cores, modos ou perfis de controle da plataforma.

| Cenário | Resultado exigido | Gate |
| --- | --- | --- |
| Ativar e abrir | Erros de licença/sessão claros; catálogo assinado e navegação respondem | Serviços |
| Sessão expirada e offline | Renovação delimitada; biblioteca instalada preservada | Serviços |
| Download pausar/retomar/cancelar | Uma transferência; novos grants; sem arquivo parcial publicado | Instalação |
| Arquivo/ZIP inválido e armazenamento cheio | Falha transacional explicada e sem apagar jogo existente | Instalação |
| Remover e reinstalar jogo | Somente arquivos registrados; saves e arquivos desconhecidos preservados | Instalação |
| Abrir cada owner offline | Formato, dependências, toque, gamepad, áudio e save reais | Offline |
| PS3 ISO e PS4 PKG reais | Bootstrap, importação e gameplay distintos; retorno responsivo | Sony offline |
| Criar/entrar com 2 jogadores | Roster/slots corretos, todos READY e frames sincronizados | Online |
| Criar/entrar com 3 jogadores | 2 links e 4 attachments aptos; modo/count aprovado | Online |
| Capacidade/mode não permitido | Recusa antes do owner; mensagem útil | Online |
| Conteúdo/core/runtime/profile diferente | Recusa explícita, sem remover guardas | Online |
| Wi-Fi cai e volta | Pausa global, epoch monotônico, replay/ACK e READY corretos | Recovery |
| Um convidado demora a READY | Diagnóstico do attachment; saída humana continua responsiva | Recovery |
| Background, retorno, tela gira | Sem worker duplicado nem COMMIT de geração antiga | Lifecycle |
| Host sai em starting/playing/recovery | Sem ANR; cleanup comprovado; sala confirma encerramento | Saída |
| Convidado sai em starting/playing/recovery | Sem ANR; demais recebem estado real de recovery/saída | Saída |
| Generation muda antes de leave | Snapshot fresco; mesma sala; retry delimitado | Saída |
| Entrar novamente após sair | Sem link/socket/thread de sessão anterior; novas identidades | Regressão |
| Jogo offline após online | Input/áudio/save/config offline preservados | Regressão |
| 20 ciclos entrar/sair por owner | Sem aumento continuado de recursos; sem deadlock/ANR | Estabilidade |
| Carrossel e efeitos após retorno | 30fps dos menus, capas/cache/vídeos/economia preservados | Regressão |
| Aparelho com pouca memória/rede lenta | Erro/espera explicados, interface e saída utilizáveis | Consumidor |


### 2.8 Compilação reprodução e promoção de candidata

A fonte executável da instalação continua 4f9039eb9ce13907ce043870bfe1f6e294888556, APK R134 SHA256 f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2. A revisão de lifecycle acrescenta um overlay separado e testes. Ela não modifica as fontes congeladas das versões históricas nem transforma os recibos R134 em prova de um APK novo.

Para um novo APK, compilar os payloads do overlay com API Android e classpaths exatos, restringir as famílias de DEX, conferir as classes fora do escopo, recompor o pacote, renovar os runtime IDs afetados pelo bundle, assinar com o certificado original e verificar mapas de entradas, assinatura e alinhamento 16 KiB. Depois conciliar ponteiros, kit e registrador do servidor com os novos hashes.

A publicação de fontes e build recipes é suficiente para revisar a correção, mas a candidata só pode ser instalada e homologada depois da montagem assinada e das verificações completas. O pedido atual proíbe usar USB; nenhuma instalação da candidata é realizada por esta revisão. R134 instalada e overlay proposto são estados separados.

A atualização do servidor exige recebimento do kit privado byte exato, preservação dos baselines atuais, autenticação administrativa nativa, transação de cadastro e resposta assinada fresca do multiplayer. Os handoffs R134 e o suplemento do incidente devem ser devolvidos com uma única matriz de aprovados/recusados e recibos reais. Não reiniciar serviços ou aplicar scripts históricos por ler o Git.


### 2.9 Pacote público e transferência do conhecimento

O pacote público reúne handoff completo em Word e Markdown, capítulos estruturados, inventários de funções/arquivos/DEX/bibliotecas, receitas de indexação e geração do dossiê, evidências públicas R134, matriz de modos por edição e relatório de auditoria com fontes e resultados de testes. O consumidor e o operador têm necessidades diferentes: o operador recebe contratos e gates; a interface do consumidor deve apresentar resultado e ação útil em linguagem simples.

APKs, bibliotecas compiladas, jogos, firmware, BIOS, mídias e chaves de assinatura continuam no canal privado indicado pelas receitas. O pacote público contém seus hashes técnicos e requisitos. Um recibo público sanitizado não substitui o recibo original para o registrador. O servidor precisa confirmar o recebimento dos originais antes da aplicação.

O responsável que assumir a manutenção deve começar pelo README do handoff completo, ler estado atual e incidente, localizar a função no índice, usar o commit explícito e confirmar no STATUS se o artefato é fonte, payload, APK assinado, instalado ou homologado. A branch padrão antiga e rótulos de versão isolados não selecionam o APK atual.


## 3 Serviços comerciais arquivos e contratos HTTP

### 3.1 Serviços comerciais: recorte da fonte e cadeia efetiva R134

A análise desta parte usa o HEAD publicado 4f9039eb9ce13907ce043870bfe1f6e294888556 e o snapshot Java completo da R124 como fonte herdada dos serviços. A R134 muda somente a família StationGraphicsPanel em DEX28, Ps3Activity/Ps4Activity em DEX40, dois textos do carrossel e as identidades dos quatro motores vinculados ao bundle. Licença, transporte HTTP, sessões, catálogo, perfil, fila, instalador e armazenamento conservam o comportamento anterior. A publicação da R134 tem sete substituições e zero adições ao donor R133; preservação de classes e entradas não é uma nova execução física de todos esses fluxos. [SV01, SV02, SV38]

StationFrontend precisa ser lido junto com o delta herdado de integration/local-sony-demos/recipe/patch_frontend.py. Esse delta modifica publishCurrent, start, remove e cover para acrescentar linhas visuais DEMO Sony e impedir que elas sejam tratadas como jogos comerciais, downloads ou capas de rede. O restante dos serviços abaixo permanece representado pelo snapshot completo. As amostras não alteram o catálogo assinado, não fornecem jogo real e não concedem capacidade online. [SV03]

Há quatro numerações diferentes que precisam ser registradas separadamente: revisão de pacote R134; clientVersion enviado pela API; schemaVersion dos envelopes; e multiplayerVersion/capability. O StationConfig herdado ainda declara clientVersion 1.0.8-station-performance-offline-r16-20261005. Portanto esse campo legado sozinho não identifica o APK R134. Os recibos de pacote, seu hash e a cadeia de fontes identificam a entrega; o perfil comercial usa domínios v1, enquanto o contrato multiplayer atual exige versão 3. [SV05, SV06, SV39]

Nesta análise não foram executadas chamadas ao serviço produtivo, novas ativações, downloads reais ou alterações de licença. O inventário descreve o que o cliente implementa e as condições verificadas no código. Os recibos de instalação dos dois aparelhos, compilados pelo responsável pela entrega, devem integrar outra seção do dossiê; a presença de um APK instalado não certifica catálogo atual, acesso online, download de um título, estabilidade ou gameplay. [SV01, SV02]


### 3.2 Organização dos componentes e responsabilidades

StationAndroid é a composição central no processo principal: resolve o diretório no_backup do Android, cria o relógio monotônico, o dispositivo criptográfico, o transportador HTTP, o dono de sessões, o catálogo privado, o cache de capas e o coordenador. Login e frontend recebem os mesmos objetos. Essa composição reduz o risco de autorizar um jogo com uma sessão e baixar seus cabeçalhos com outra sessão independente. As operações que fazem IO são encaminhadas para trabalhadores, não para a thread que desenha a tela. [SV04, SV10, SV11, SV16]

Os dados comerciais e seus caminhos privados são escolhidos pelo aplicativo. O modelo StationCatalog não armazena URLs de download; o grant e a allowlist do transporte determinam a rota. Um endereço arbitrário vindo de metadado, nome de arquivo, capa ou manifesto não é seguido. O instalador recebe dados através do leitor nativo, mas é o código Java que valida caminhos, limites e publicação. Essa divisão é importante para rastrear responsabilidades quando ocorrer erro de catálogo, transferência ou preparação. [SV05, SV07, SV14, SV24, SV25]

| Componente | Responsabilidade | Consumidor/efeito |
| --- | --- | --- |
| StationApi + StationHttp + StationProtocol | Contrato tipado, contexto, assinatura e única saída HTTP comercial | Ativação, perfil, catálogo, capas, grants, mídia e comandos online |
| StationCrypto + StationRequestProof | Identidade do aparelho e prova de cada requisição negociada | Keystore e vínculo entre método/rota/corpo/credencial |
| StationSessions + StationCoordinator | Dono de sessão, licença, biblioteca e decisões de invalidação | Entrada do usuário, catálogo local e operações autenticadas |
| StationCatalogStore + StationCatalog | Persistência do envelope assinado e modelo de biblioteca | Restauração offline e catálogo por revisão/ID |
| StationFrontend + StationPublication | Publicação dos dados Java para o carrossel nativo | Instalado, ação Baixar/Jogar/Apagar, metadados e capa |
| StationDownloads + StationInstaller + StationArchive | Fila, autorização, transferência, extração e commit | Um jogo fica executável somente após recibo comprometido |
| StationCoverStore + StationCoverQueue | Cache, IO, decode, prioridade e recuperação de capas | Carrossel, sala e central de downloads |
| StationCarouselMedia + StationMediaStore | Atualização e retenção dos clipes de menu | Renderização consome arquivos locais validados |
| StationStorage + StationBundledFiles + StationResourceBundle | Pastas, teste de escrita e recursos empacotados | Primeira inicialização, reparo de ausentes e mudança de bundle |
| LoginActivity + StationTaskNavigation | Entrada, permissão de armazenamento e reuso de tarefa | Frontend e retorno ao jogo sem criar tela duplicada |


### 3.3 Identidade do aparelho, HTTPS e envelope assinado

A identidade principal é uma chave RSA de 2048 bits gerada no Android Keystore. A chave privada não é exportada pelo cliente; o identificador do aparelho é Base64URL do SHA256 da chave pública codificada em SPKI. O alias principal é preservado nas atualizações. A assinatura principal usa RSA-PSS com SHA256, MGF1-SHA256 e salt de 32 bytes. A licença é vinculada a essa identidade e não a um número digitado de aparelho ou ao nome exibido na interface. Remover os dados ou desinstalar pode apagar a identidade, por isso os recibos de atualização conferem preservação da instalação. [SV04, SV08]

StationHttp aceita apenas a origem pública https://app.lzgames.com.br com HTTPS, sem credenciais de URL, query, fragmento ou path na origem. A validação do certificado do sistema e do hostname permanece habilitada; adicionalmente o cliente compara o SHA256 da chave pública do certificado de folha com o pin configurado. Os valores do pin e das chaves não são reproduzidos neste documento. Redirecionamentos HTTP e qualquer cabeçalho Location são recusados, mesmo que apontem a outro recurso no mesmo domínio. [SV07, SV39]

Respostas de controle chegam como JSON application/json com envelope {keyId,payload,signature}. Payload e assinatura usam Base64URL canônico sem padding. O cliente exige o keyId configurado, verifica a assinatura RSA-PSS e depois examina schemaVersion=1, domain, productId, applicationId e deviceId. Com sessão ativa, também exige licenseId e sessionId exatos. Para catálogo salvo aceita um sessionId histórico com formato válido, preservando licença e aparelho. JSON UTF8 malformado, esquema/contexto divergente, assinatura inválida ou corpo acima do limite interrompem a operação antes da publicação. [SV05, SV06]

Ativação e sessão negociam prova de requisição. O modo pode ser none, rsa-pss-v1 ou ec-p256-v1, conforme a oferta assinada do servidor e as condições do cliente. O modo EC usa chave secundária P256 atestada; o cliente não permite alegar verifiedApp se a negociação não terminou em ec-p256-v1. Se o servidor exige aplicativo verificado e a atestação não puder ser preparada, a abertura falha. Quando o servidor permite fallback, o código aceita a negociação RSA prevista. Essa flexibilidade está no contrato; não é um bypass criado para esta revisão. [SV05, SV08, SV09]

A prova X-Station-Request-Proof liga uma assinatura ao método HTTP, destino completo com query, hash do corpo, hash da credencial, timestamp derivado do tempo do servidor e nonce aleatório. Isso difere de calcular hash de ROM. A forma textual é v1.timestamp.nonce.signature, sem expor o bearer em logs ou no documento. O tempo de sessão usa elapsedRealtime; a prova combina serverTime assinado com tempo monotônico decorrido. A chave de requisições secundária pode ser reutilizada quando desafio/cadeia continuam válidos, e falha na preparação adia nova tentativa por uma hora. [SV08, SV09]

| Contrato/limite | Valor observado no cliente |
| --- | --- |
| Connect timeout / read timeout | 10 segundos / 30 segundos |
| Corpo geral de requisição/erro/resposta curta | 8192 bytes |
| POST activations/complete e sessions | Até 65536 bytes no transporte para envelope/cadeia |
| Cadeia de atestação | 2–6 certificados; até 8192 bytes/certificado; total codificado até 49152 |
| Cabeçalhos | Authorization: Bearer quando há sessão; X-Station-Request-Proof quando negociado; X-Correlation-ID gerado; Accept-Encoding: identity |
| Encoding/resposta | Content-Encoding ausente ou identity; outros encodings recusados |
| Status de sucesso do contrato | 200; outros status passam pela classificação de falha |


### 3.4 Endpoints comerciais de ativação, sessão e perfil

Todos os caminhos desta tabela são relativos à base pública https://app.lzgames.com.br. Os nomes de campos são os do código, e os identificadores variáveis são esquemas, não valores de credenciais. Os quatro POSTs de ativação/sessão não usam uma sessão bearer prévia; autenticam a continuidade com desafio, nonce e assinatura do dispositivo. A identidade comum de requisição inclui schemaVersion, domain, productId, applicationId, deviceId, clientVersion, deviceManufacturer, deviceModel e androidSdk. Fabricante/modelo são dados técnicos enviados pela implementação; dados de aparelhos particulares não foram incluídos aqui. [SV05, SV06, SV07]

ActivationCode, accessToken, grantId e tickets são tratados como tokens Base64URL canônicos de 32 bytes. LicenseId admite de 6 a 64 caracteres alfanuméricos, hífen e underscore. ChallengeId e sessionId exigem 64 dígitos hexadecimais minúsculos. O cliente não aceita uma senha comercial livre ou valor arbitrário com a intenção de substituir o código emitido. O campo visual recebe o nome de senha de acesso, mas o método StationApi.activate confirma o formato e executa ativação de licença. [SV05, SV06, SV12]

Desafios têm expiresInSeconds exato 60; a sessão retorna expiresInSeconds exato 180 e sua vigência é contada no relógio monotônico do cliente. A abertura verifica challengeId/nonce/licenseId retornados antes de aceitar accessToken. Não há regra local de duração vitalícia ou quantidade de aparelhos inferida da interface: essas regras são decisões do servidor/licença. A leitura do cliente permite documentar o contrato, sem declarar uma licença particular ativa, expirada, consumida ou liberada. [SV05, SV10]

| Método e rota | Requisição | Resposta e validação |
| --- | --- | --- |
| POST /v1/station/activations/challenge | Identidade com domain request-activation-challenge/v1, activationCode e devicePublicKey | Envelope domínio activation-challenge/v1; challengeId, nonce, expiresInSeconds=60 e security opcional |
| POST /v1/station/activations/complete | Envelope do dispositivo: payload/signature; payload activate/v1 com código, chave, desafio, nonce e campos de segurança; atestação quando preparada | Envelope activated/v1; challengeId e nonce exatos; licenseId com formato válido |
| POST /v1/station/challenges | Identidade request-session-challenge/v1 com licenseId | Envelope session-challenge/v1; mesma licença, challengeId, nonce, TTL60 e security |
| POST /v1/station/sessions | Envelope do dispositivo com payload open-session/v1, licença/desafio/nonce e segurança negociada | Envelope session/v1; mesma licença/desafio/nonce; sessionId, accessToken, TTL180; requestProof, verifiedApp e serverTime consistentes |
| GET /v1/station/me | Bearer válido e proof quando negociado; sem corpo | Envelope profile/v1; profileVersion positivo e displayName plain text até 80 caracteres |


### 3.5 Tela de acesso, opção Manter conectado e perfil

A tela LoginActivity apresenta campo único, botão ENTRAR, estado da consulta e opção Manter conectado. O campo é de linha única, limitado a 128 caracteres, não salva o texto em estado da Activity e bloqueia autofill; o código é limpo ao iniciar a consulta. Se há licença salva, o campo informa que o acesso já está guardado. Manter conectado é uma preferência local station-login-ui/rememberAccess, com padrão true, que controla a entrada automática ao reabrir. Desmarcar não equivale a revogar a licença nem apagar o arquivo da identidade. [SV12, SV13]

StationLogin executa operações num trabalhador com no máximo uma consulta ativa e fila limitada a quatro tarefas. Callbacks voltam à thread principal somente se a consulta não foi cancelada e a Activity continua válida. A interface impede submissão duplicada enquanto authenticating/opening; ao pausar/destruir, cancela o trabalho associado conforme o lifecycle. O acesso salvo pode entrar sem digitação quando a biblioteca autorizada/cacheada está disponível. Não há fluxo de senha de usuário, cadastro de email, recuperação de senha ou compra/Pix nesta tela examinada. [SV12, SV13]

O nome que aparece no cabeçalho vem de displayName autenticado por GET me. StationCoordinator grava uma cópia por proprietário licença+aparelho e também uma string local consumida pelo cabeçalho nativo. Esse nome é somente apresentação: não cria sessão nem autoriza download. ProfileVersion é validado como inteiro positivo, mas o modelo desta função expõe o nome, não um editor de dados cadastrais. Se o servidor devolve especificamente 503/STATION_PROFILE_NOT_READY, o coordenador pode reutilizar o nome salvo; outros 503 não recebem automaticamente o mesmo tratamento. [SV05, SV11]

Os textos de falha distinguem acesso não autorizado401/403, excesso de tentativas429, indisponibilidade503, código inválido e conexão não confirmada. O texto429 de login recomenda aguardar um minuto; isso não significa que a tela executa retry automático após 60 segundos. Em caso de ausência de internet, o erro da API informa que jogos instalados continuam disponíveis. A política offline só consegue satisfazer esse fluxo quando já há a licença e um catálogo local íntegro compatível. [SV05, SV13]


### 3.6 Sessão compartilhada, concorrência e renovação

StationSessions é o único dono do bearer comercial e nunca o persiste em disco. A licença salva fica em station-license-id.txt dentro de no_backup, e é escrita imediatamente depois de a ativação assinada retornar. Isso evita perder uma licença recém-ativada porque um código de uso único já foi consumido e a abertura seguinte falhou. A sessão só é aceita depois da confirmação de StationApi.openSession. Na retomada de processo, o ID salvo e a identidade Keystore reabrem a sessão quando uma operação online precisa dela. [SV04, SV10]

Session.needsRenewal retorna true nos 15 segundos anteriores ao vencimento de 180 segundos. acquire obtém um Lease e incrementa o número de consumidores. Ativar ou substituir sessão aguarda os leases terminarem, com cancelamento verificável, para não girar a credencial enquanto autorização e GET autenticados dependem da mesma sessão. A fila mantém o lease entre acquireItem, authorize e os cabeçalhos do artefato, liberando-o antes de transferir todo o corpo. Assim uma transferência longa pode coexistir com renovação/capas depois de o servidor aceitar os cabeçalhos. [SV05, SV10, SV11, SV19]

StationCoordinator mantém a biblioteca e a sessão que autorizaram aquele catálogo. Se uma operação recebe uma sessão diferente da autorizada, recarrega o catálogo antes de localizar o item e continuar; um item que sumiu após renovação é recusado. Falha401/403 invalida a sessão rejeitada; uma resposta atrasada de bearer antigo não derruba a sessão mais recente. Esse controle é diferente de reabrir login a cada retorno de jogo, e explica por que biblioteca local e token online têm ciclos independentes. [SV10, SV11]

O coordenador oferece logout que limpa biblioteca/sessão em memória, sem um endpoint de revogação remoto nesse método. O arquivo de licença não é apagado por esse código. Portanto logout não deve ser confundido com desativar comercialmente o aparelho, reembolsar compra ou liberar vaga de licença. O estado no servidor e uma nova sessão autenticada continuam sendo a autoridade para ações online. [SV10, SV11]


### 3.7 Biblioteca offline e negação persistente de licença/aparelho

Quando o código de entrada está vazio e existe licença salva, StationCoordinator.login tenta primeiro o catálogo local. StationCatalogStore identifica esse cache pelo SHA256 do par licenseId+deviceId. O envelope inteiro é preservado; restauração verifica assinatura da autoridade, produto, aplicação, aparelho e licença. SessionId histórico deve manter o formato válido, mas não cria uma sessão nova. Esse caminho devolve Library.cached=true e um nome salvo. Sua finalidade é leitura e execução de conteúdo já instalado após ativação. [SV05, SV11, SV15]

ready verifica a existência da biblioteca, e não a vigência do bearer. Vencer180 segundos de sessão online não fecha sozinho a coleção local. Capas já cacheadas e paths de jogos comprovados por recibo podem continuar disponíveis sem rede. Baixar uma capa ausente, autorizar artefato ou executar comandos sociais precisa de conectividade e sessão. O cache de catálogo não contém URLs nem concede um Grant; ver um item offline não significa que seu arquivo já foi instalado ou pode ser obtido offline. [SV05, SV11, SV16, SV17]

Há uma diferença concreta entre recusar sessão e negar licença/aparelho. sessionDenied cobre401 e403. licenseDenied cobre apenas 403 com STATION_LICENSE_DENIED ou STATION_DEVICE_DENIED. Nessas duas negações explícitas, o coordenador zera a biblioteca e StationCatalogStore grava marcador .blocked do proprietário. Na reabertura offline esse marcador impede a restauração do catálogo. Se falhar gravar o bloqueio, o código tenta remover o catálogo para não persistir acesso contrário à recusa conhecida. [SV05, SV11, SV15]

Um catálogo fresco autenticado pode reparar cache inválido e retirar o marcador após autorização aceita. A revisão recebida não pode ser inferior à revisão já salva. A fallback de catálogo por serviço indisponível é específica a 503/STATION_CATALOG_NOT_READY e usa envelope salvo validado para a sessão; qualquer 503 genérico, assinatura incorreta ou resposta de outra licença não é incorporado. No percurso de login após erro de cache, somente uma resposta autenticada pode reconstruir os dados. [SV11, SV15]

| Condição | Resultado implementado |
| --- | --- |
| Primeiro uso sem licença/cache e sem rede | Exige ativação/consulta válida; não fabrica biblioteca local |
| Ativado, licença e catálogo íntegros, sem internet | Biblioteca restaurada; jogos instalados podem ser apresentados/abertos |
| Bearer expirado com biblioteca local | ready permanece verdadeiro; nova operação online renova a sessão |
| Capa/artefato ausente offline | Aguarda conexão ou falha apropriada; cache não gera bytes inexistentes |
| 401/403 de sessão sem código explícito de negação | Sessão rejeitada é invalidada; não deduz revogação permanente |
| 403 LICENSE_DENIED/DEVICE_DENIED | Biblioteca bloqueada e marcador persistente impede restauração offline |
| Nova resposta autenticada de catálogo aceita | Repara cache e remove bloqueio daquele proprietário |


### 3.8 Endpoints de catálogo, capas, autorização e artefatos

A lista comercial é solicitada por GET /v1/station/catalog?metadata=1; o transporte também admite a forma sem query por compatibilidade, mas catalogSnapshot escolhe metadata=1. Há bearer e proof quando a sessão os exige. A resposta é envelope catalog/v1 com revisão e array items. Todo item é identificado por itemId e coverId, não pelo nome visual. O autorizador recebe itemId e a API compara itemRevision assinada com a revisão que o coordenador espera. Isso impede instalar silenciosamente outra revisão do conteúdo por simples coincidência de título. [SV05, SV06, SV07, SV14]

A autorização retorna grant de uso único para GET artifacts. O cliente liga o grant à própria sessão, ao item e ao descritor; TTL60 é contado desde o início da autorização e conferido antes do GET. O servidor consome o grant antes de devolver os cabeçalhos, e o cliente também o marca consumido com AtomicBoolean antes da troca. Mesmo uma conexão que cai depois do consumo não torna o grant reutilizável. A próxima tentativa completa deve obter autorização nova. [SV05, SV19]

Capas e arquivos grandes não passam pelo envelope JSON durante o corpo de transferência. A confiança vem da sessão/prova, HTTPS e contrato anterior; capa exige assinatura de formato de imagem/MIME compatível e validação de decode. Artefato exige MIME application/octet-stream e Content-Length exato do descritor. O hash sha256 continua sendo exigido como metadado do descritor, mas a política de instalação não calcula o SHA integral da ROM no download. Isso deve constar claramente para não transformar presença de campo hash em alegação de conteúdo byte a byte verificado. [SV05, SV24, SV26]

| Método e rota | Requisição/identidade | Resposta/limite |
| --- | --- | --- |
| GET /v1/station/catalog?metadata=1 | Bearer válido + proof; sem corpo | Envelope catalog/v1; revisão/items; corpo máximo 64 MiB; parser máximo 4096 itens |
| GET /v1/station/covers/{coverId} | coverId 8–64 alfanuméricos/hífen/underscore; bearer + proof | PNG/JPEG/GIF/WebP com MIME compatível; corpo até 5 MiB |
| POST /v1/station/downloads/authorize | Identidade domain request-download/v1 com itemId; bearer + proof | Envelope download-grant/v1; itemId/itemRevision, grantId, expiresInSeconds=60, artifact |
| GET /v1/station/artifacts/{grantId} | Token de grant de 32 bytes Base64URL; mesma sessão + proof; GET único | application/octet-stream; Content-Length exato; transferência limitada ao tamanho autorizado |


### 3.9 Catálogo, coleções, busca e apresentação de metadados

StationCatalog.fromVerifiedPayload é chamado depois da verificação do envelope. Revision e revision de item precisam ser inteiros positivos; IDs duplicados causam falha. Nome e plataforma são texto simples até 120 caracteres, IDs de biblioteca têm8–64 caracteres. O modelo não executa HTML e rejeita controles inadequados/UTF16 inválido. MAX_ITEMS é4096, e o envelope pode ocupar até 64 MiB. Esses limites pertencem ao cliente examinado e não comprovam suporte a 40mil títulos numa única resposta. [SV05, SV06, SV14]

FolderPath permite até oito segmentos de até 80 caracteres, sem vazio, ponto, dotdot ou separadores de caminho no nome. Representa coleções/folders do catálogo; a chave da coleção é a união com slash. Metadados opcionais incluem descrição, desenvolvedor, distribuidora, gênero, jogadores e data de lançamento. Descrição tem limite 2000 caracteres e admite newline/tab; os campos simples possuem limites menores. Ausência de metadado é representada como vazio e não é substituída por informação inventada. A informação textual players não equivale a aprovação online de edição/conteúdo/owner/modo. [SV14]

contentSha256 e contentIdentityScheme, quando presentes, descrevem identidade do conteúdo. Os esquemas especiais aceitos nesse parser são cue-set-v1 e wiiu-set-v1, condicionados a digest válido. O multiplayer pode fazer validações adicionais sobre conteúdo/owner, tratadas em outra seção. O catálogo comercial diz qual item é oferecido; não certifica que o aparelho suporta executar toda ROM daquela plataforma, nem que há modo online aprovado. [SV14, SV02]

StationFrontend publica uma linha do item com ID, nome, label/pasta da plataforma, coverId, path inicial instalado ou vazio, folderKey, descrição, revisão e capa quente quando já comprovada. A marca de instalado decorre do recibo do StationInstaller, não de varrer todas as pastas arbitrárias por nome. Platforms.resolve precisa reconhecer a plataforma; entradas sem mapeamento são contabilizadas/avisadas. A busca nativa preservada atualiza resultados enquanto o usuário digita, trata busca vazia e sobrepõe o editor ao carrossel/sinopse. A interface fornece contexto instalado e ações baixar/jogar/apagar, conforme conteúdo e estados. [SV16, SV25, SV40]

| Elemento | Limite/condição no modelo |
| --- | --- |
| Número de itens / corpo assinado | 4096 /64 MiB |
| IDs de item/capa | 8–64; [A-Za-z0-9_-], únicos por item |
| Nome/plataforma | Texto simples até 120 caracteres |
| FolderPath | Até8 segmentos de até 80; sem .,..,/ ou barra invertida |
| Descrição | Até2000; controles limitados a newline/tab |
| Developer/publisher/genre | Até80 caracteres por campo |
| Players/releaseDate | Até40 caracteres por campo |
| Scheme de identidade composto | cue-set-v1 ou wiiu-set-v1 com contentSha256 válido |


### 3.10 Atualização do catálogo e conciliação com o foreground

A biblioteca tem refresh explícito e um polling automático de primeiro plano. StationFrontend inicia a primeira consulta após5 segundos e mantém intervalo fixo de 60 segundos. mayPoll exige foreground, configuração pronta, StationAndroid disponível, rede indicada, biblioteca autorizada, zero trabalhos ativos de download e zero trabalhos ativos da fila de capas. Assim consulta de catálogo não compete automaticamente com a instalação/capa em andamento. Pausa de Activity cancela a geração de refresh e preserva quando a próxima consulta ficará devida. [SV16]

A consulta automática roda num trabalhador próprio do catálogo. Quando a nova revisão ou displayName difere, a publicação é agendada para a fila de comandos do frontend, ainda protegida pelo Ticket/generation. Um resultado atrasado de tela já pausada não publica sobre a tela atual. Se a revisão/nome permanecer igual, o código evita reconstrução visual desnecessária. O refresh autenticado consulta também perfil, portanto não é só uma troca de array de ROMs. [SV11, SV16]

Esse mecanismo atualiza dados comerciais, não instala outro APK e não promove build a estável. O código não apresenta nessa trilha um endpoint de auto update do aplicativo. A versão comercial de catálogo efetivamente disponível deve ser confirmada por resposta assinada nova; matrizes documentais, aliases históricos e recibos de revisão anterior não substituem essa resposta. Políticas de rollback e bloqueio local são parte da persistência, e não prova de que uma alteração recente já foi publicada pelo servidor. [SV02, SV15, SV16]


### 3.11 Capas persistentes, legado exato e fila de prioridade

StationCoverStore grava imagens por coverId+revision no diretório privado station-v2/covers. A mesma capa/revisão recebe lock por chave; o cache pode devolver path sem nova rede quando sua identidade/validação ainda é válida. O provedor ExistingCoverCache oferece reuso do cache legado somente quando comprova a revisão e o tipo/firma de imagem esperados. Não é busca genérica por título em qualquer pasta. A pré-indexação registra tamanho/data/estado de validação, reduzindo a necessidade de recalcular hash ou decode completo em toda publicação. [SV17]

A validação de imagem reconhece PNG, JPEG, GIF e WebP por bytes iniciais, compara MIME e verifica dimensões. StationAndroid recusa width/height ausentes, menores que1 ou maiores que8192; decodifica amostra reduzida em vez de aceitar arquivo que apenas tenha uma extensão. A camada de central de downloads reduz capas para até 256 no lado maior e mantém cache de bitmaps com orçamento de 8 MiB. Corromper uma capa cacheada não autoriza conteúdo nem é corrigido mudando a licença; cache visual e licença têm donos distintos. [SV04, SV17, SV21, SV26]

StationCoverQueue tem um trabalhador global de IO/decode, fila ativa limitada a nove tarefas e geração vinculada à publicação. Pedidos visíveis têm prioridade sobre completar cache em background; capas de sala/UI passam pelo mesmo trabalhador, com opção de alta prioridade. Prefetch do catálogo admite no máximo 4096 identidades. Pausar o frontend cancela a geração/pedidos conforme lifecycle, e uma capa entregue após a tela destruir não deve voltar a anexar bitmap àquela superfície. [SV18, SV21]

Falha404 coloca aquela capa/revisão em espera de 60 segundos. 429 bloqueia consultas do store até Retry-After ou60 segundos quando o header falta. A fila e a central têm seus próprios atrasos de reconsulta e cleanup; a central libera loading para tentar novamente após30 segundos quando falha decode/carga. Esses intervalos não são promessa de que uma imagem ausente aparecerá ao vencer o relógio: ela só poderá ser obtida se o servidor a disponibilizar e a sessão autorizar. [SV17, SV18, SV21]


### 3.12 Fila de downloads: estados, interface e persistência

StationDownloads mantém uma transferência por vez num ScheduledThreadPoolExecutor de um trabalhador. Cada jogo tem estados QUEUED, AUTHORIZING, DOWNLOADING, PREPARING, WAITING, PAUSED, ERROR, COMPLETE e CANCELLED. Até 32 jogos podem ficar não terminais; histórico em memória é aparado para 48 linhas quando novos jogos entram. Uma solicitação duplicada não cria download concorrente do mesmo item que já está em execução/fila. Estado terminal não é igual a pendente de pausa; pausados continuam na contagem de trabalhos ativos, mas não fazem requisições. [SV19]

A central exibe capa, nome/plataforma, estado, barra, bytes, velocidade, tempo decorrido e restante estimado; atualiza as linhas uma vez por segundo somente enquanto aberta. Durante DOWNLOADING a barra usa networkDone/networkTotal; na preparação usa progresso composto. Velocidade é medição de bytes recebidos no trecho de rede e o restante é cálculo baseado nela; não é garantia de duração. Os botões PAUSAR/CONTINUAR/TENTAR DE NOVO e CANCELAR têm layout horizontal adaptado à largura. Preparação final desabilita pausa para proteger publicação transacional. [SV21]

O aviso no carrossel mostra quantidade ativa; quando só há histórico, a API downloadNoticeCount fornece estado para VER. Fechar a central não cancela o trabalho. Cancelar exige confirmação com MANTER ou CANCELAR, remove a tentativa e impede retorno automático daquele trabalho; jogos/saves já instalados continuam. Ao destruir/parar a Activity, a central encerra tick, diálogos, requisições e bitmaps de apresentação, não o gerenciador de downloads. [SV16, SV21, SV22]

A persistência pending-downloads-v1 guarda somente itemId e estado Q/P, com limite de arquivo de 16384 bytes. Erros são persistidos como pausados para exigir ação; trabalhos concluídos/cancelados não são gravados. Ao abrir de novo, restorePending verifica cada item no catálogo autorizado, limita a 32 e não restaura IDs que desapareceram. Não é persistência de bytes parciais nem histórico completo de sessões. close cancela tentativas, espera trabalhador, drena o journal e encerra para não perder a escolha de pausa na nova instância. [SV19]


### 3.13 Recuperação, pausa e condições de retry

Cada tentativa de download adquire o item na biblioteca atual, obtém grant novo, verifica espaço, cria diretório transfer- próprio, abre os cabeçalhos autenticados, transfere e prepara. Se a rede cair, o finally fecha a transferência e remove o artefato/diretório temporário daquela tentativa. Pausar interrompe a conexão e guarda PAUSED; continuar agenda novo ciclo. A transferência volta do byte zero, pois o cliente não negocia Range e o grant anterior já foi consumido. A central informa que a retomada pode reiniciar o arquivo. [SV05, SV19, SV21]

StationDownloadRetry considera transitórias as respostas408,429,500,502,503 e504, além de Offline, ArtifactNetworkFailure, SocketException, SocketTimeoutException, UnknownHostException e EOFException. A espera base cresce 2, 4, 8, 16 e 30 segundos, com teto de 30; Retry-After pode elevar até uma hora nessa política. Não existe limite de tentativas que cancela automaticamente por essas falhas transitórias. NetworkCallback pode antecipar trabalhos WAITING/Aguardando conexão quando a rede volta. [SV19, SV20, SV36]

Falhas TLS de handshake, certificado ou peer não são transitórias para essa fila, mesmo quando aparecem dentro da cadeia de causas. Recusa401/403,404 permanente, descritor incompatível, plataforma sem suporte, falta de espaço e outros erros não listados tornam ERROR e exigem ação explícita. Há mensagem específica para artefato ainda não publicado, item ausente no catálogo e acesso não autorizado. Repetir automaticamente grant consumido, remover TLS ou tratar qualquer403 como queda de rede violaria o comportamento existente. [SV05, SV19, SV20]

Uma falha de autenticação passa ao coordenador; negação explícita de licença pode remover a biblioteca e solicitar login. Falha de instalação preserva o jogo previamente comprometido. Uninstall recusa agir sobre item cujo trabalho ainda está não terminal/running, pedindo cancelar antes. Essas condições evitam disputar os arquivos durante a preparação e separam retry de rede, ação de usuário e remoção de jogo. [SV11, SV19, SV25]

| Evento | Tratamento |
| --- | --- |
| Queda de rede/EOF/timeout elegível | WAITING; espera e novo grant; arquivo reinicia |
| 408/429/500/502/503/504 | Retry com crescimento2→30s e Retry-After até 1 h |
| PAUSAR | Cancela tentativa/conexão; preserva estadoP; sem nova consulta atéContinuar |
| CANCELAR | Cancela/remover trabalho; não agenda retorno automático |
| PREPARING | Pausa desabilitada; cancelamento segue guarda transacional |
| TLS/certificado inválido | Não entra no retry transitório |
| 401/403/404 ou erro local permanente | ERROR/mensagem; ação explícita e invalidação quando aplicável |


### 3.14 Serviço Android, notificação e uso de energia dos downloads

DownloadService é criado como foreground service somente quando existem trabalhos ativos. A notificação fica no canal Downloads com importância baixa, ongoing e onlyAlertOnce; agrega progresso e abre LoginActivity com reordenamento para chegar à tarefa existente. Para múltiplos trabalhos, o título mostra quantidade de jogos. O corpo acompanha o último estado/nome agregado; não é uma notificação de cada ROM separada. Atualização é limitada a uma por segundo. [SV23]

O serviço possui PARTIAL_WAKE_LOCK sem referência múltipla e só o mantém quando algum estado/mensagem corresponde a Baixando, Preparando ou Aguardando autorização. Pausa, espera de conexão/servidor e fila parada liberam o bloqueio, ainda que o trabalho permaneça pendente no gerenciador. O acquire tem limite de seis horas e a destruição libera qualquer wake lock retido. Não há Wi-Fi performance lock nem polling ocioso nesse serviço. Esse desenho mostra condição de energia, mas não substitui medição de bateria ou temperatura. [SV23]

O retorno do serviço é START_NOT_STICKY. Não é um scheduler externo que promete sobreviver indefinidamente a encerramento de processo, restrições do Android ou reinício do aparelho. A recuperação comprovada pelo código é reconstituir Q/P quando o aplicativo abre e prepara StationDownloads novamente, preservando IDs autorizados. Assim instalação do APK, existência de notificação e persistência de fila precisam ser avaliadas em situações distintas. [SV19, SV23]


### 3.15 Descritor do jogo, extração e commit transacional

StationArtifact exige fileName, sizeBytes, sha256, format, launchPath, expandedSizeBytes e fileCount no grant assinado. Tamanhos são inteiros positivos: teto de artefato de 1 TiB, expandido de 4 TiB, até 100000 arquivos. São limites defensivos de formato; não afirmam que um telefone tenha espaço ou capacidade prática nesses valores. Formatos aceitos: raw, zip, rar e7z. RAW deve ser um arquivo único, launchPath igual a fileName, size/expanded iguais e não usar extensão de compactador; arquivos compactados precisam da extensão correspondente e assinatura inicial de formato concordante. [SV24, SV25, SV26]

Caminhos são relativos, sem barra invertida/colon, sem segmento vazio, ponto ou dotdot. Instalador verifica pais contra symlink antes de tocar os descendentes. ManifestSink normaliza nomes NFC/case para rejeitar aliases duplicados em armazenamento potencialmente sem distinção de maiúsculas; admite até 200000 membros incluindo diretórios. Tamanho/contagem efetiva não pode exceder o descritor assinado. Cada membro precisa terminar com o número anunciado de bytes; extração incompleta, arquivo inicial ausente/vazio ou referências de acompanhante inválidas impedem o commit. [SV24, SV25]

Para CUE/M3U, o arquivo inicial é lido limitado a 1 MiB e cada referência deve apontar a arquivo presente dentro do content da transação. CUE precisa de diretiva FILE reconhecida; M3U ignora linha vazia/comentário e exige pelo menos uma referência. Isso não permite usar uma playlist para escapar ao diretório ou declarar conteúdo incompleto como instalado. O decoder nativo libstation_archive entrega membros a Sink e não escolhe os paths finais sozinho. [SV25]

Instalação cria roms/.station-v2/{pastaPlataforma}/{itemId}/install-*/content, escreve manifest.json e publica o mesmo manifesto em station-v2/installs/{itemId}.json privado. O ponteiro privado atômico é o commit exclusivo. A geração anterior permanece intacta quando uma atualização falha; finalmente limpa somente a árvore install- criada pela tentativa não comprometida. StationFiles usa arquivo temporário no mesmo diretório, escrita buffer de 256 KiB, leitura de 64 KiB, fsync e rename atômico. [SV25, SV26]

A política solicitada pelo mantenedor desliga SHA do conteúdo dos jogos em replaceArtifact e install. O descritor continua contendo SHA sintaticamente válido; checagem de TLS/contexto/tamanho/formato/caminhos/transação permanece. O snapshot atual copia RAW para content, apesar de documentação histórica mencionar um caminho por rename; o dossiê descreve o código preservado e não promete essa otimização. Mídias de menu seguem outra política e efetivamente verificam SHA, explicada adiante. [SV24, SV25, SV26]


### 3.16 Detecção de instalado, exclusão de jogo e preservação de saves

find não varre a árvore inteira por título e não calcula hash de todos os companheiros toda vez que o usuário volta à coleção. Lê recibo privado válido schema 1/itemId, confirma pasta da plataforma, descritor, contagem de arquivos e entrada inicial listada uma única vez; então confere se o arquivo inicial continua regular e com o tamanho salvo. Retorna Installed com revisão, plataforma e launchPath. Se path desapareceu ou tamanho mudou, não o considera executável. Isso reduz custo de retorno, mas não é verificação integral de cada byte e cada acompanhante após instalação. [SV25]

StationFrontend.installedPathsFor resolve jogos da biblioteca por plataforma em background; installedPathForItem exige item autorizado e recibo encontrado. O método que oferece path para criar/entrar em sala produz mensagem Baixe o jogo antes se ele não existir. Apenas visibilidade no catálogo não satisfaz a condição de arquivo pronto. Para DEMOs Sony, o delta herdado bloqueia ações de download/remoção/capa de rede e a Activity proprietária rejeita usar a amostra como arquivo de jogo. [SV03, SV16, SV25]

Uninstall publica tombstone removing=true, enumera somente paths do recibo e remove arquivos pertencentes à instalação; diretórios só são retirados quando vazios. Dados desconhecidos não são apagados recursivamente. Se o usuário ou emulador colocou arquivo adicional/saves dentro do content, esse arquivo permanece. A marca de remoção permite reexecutar após interrupção. A rotina não equivale a limpar todos os saves nem resetar o emulador e mantém uma geração que não pôde ser removida por conteúdo extra. [SV25]

A camada comercial não implementa neste recorte sincronização de save em nuvem, backup periódico de partidas ou conversão universal entre motores. Salvar/carregar, pasta e formato de save pertencem ao owner de cada emulador e às regras de sessão multiplayer. A preservação de arquivos no uninstall e de dados Android na atualização protege esses dados, mas não demonstra que todos os comandos de save/load funcionem em todos os motores R134. Essa qualificação exige teste do motor e título pertinente. [SV01, SV02, SV25]


### 3.17 Armazenamento, permissão inicial e recursos do pacote

LoginActivity só abre frontend depois de acesso confirmado e permissão de armazenamento. Android 30+ usa a condição isExternalStorageManager e abre ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION para o pacote; versões anteriores pedem WRITE_EXTERNAL_STORAGE. Se o Android não oferece a tela, o aplicativo orienta permitir nas configurações e voltar. storageReturned revalida a permissão e retoma entrada/preparação, sem exigir criação manual das pastas para corrigir a instalação de teste. [SV12]

StationStorage.prepareRoot exige caminho absoluto escolhido pelo aplicativo. Busca ancestral existente, resolve raiz canônica do sistema e cria descendentes com as guardas do instalador. Faz arquivo de prova e remove-o para verificar escrita real; não confia apenas em flag de permissão ou resultado de mkdir. Aceita alias do sistema somente ao resolver a raiz, não em path vindo do catálogo ou ZIP. Conflito de arquivo no lugar da pasta, acesso negado ou falha de preparação recebem mensagens próprias, preservando arquivos existentes. [SV27]

Espaço para transferir é conferido com File.getUsableSpace, pois Files.getFileStore é problemático no armazenamento compartilhado Android deste fluxo. A fila exige sizeBytes+expandedSizeBytes+256 MiB antes de baixar; o instalador exige expandedSizeBytes+256 MiB no proprietário antes de preparar. Para RAW isso inclui orçamento para corpo e cópia transacional; para compactado considera staging e extração. São margens de segurança codificadas, não medição de espaço real no aparelho do leitor. [SV19, SV25, SV27]

StationResourceBundle usa BUNDLE_ID de conteúdo e marcador .installed-version. Bundle atual e marcador numérico legado reparam arquivos ausentes/vazios; uma revisão nova do bundle substitui os paths empacotados e conserva adições do usuário. StationBundledFiles recusa nomes de filho inseguro, symlink/conflicto de tipo e profundidade acima32, escreve em temporário e move. Arquivos adicionais fora do bundle não são removidos. Esta política descreve recursos fornecidos pelo APK; não distribui automaticamente todo firmware/BIOS imaginável. [SV28, SV29]

no_backup guarda licença/catálogo/perfil/capas/recibos e mídia do próprio app; staging/conteúdo de jogos ficam sob a raiz de ROMs .station-v2. Essa separação ajuda a explicar por que limpeza de dados do app pode perder identidade e recibos mesmo quando ROMs ainda existem no armazenamento compartilhado. A presença dos arquivos sozinha não recompõe automaticamente a autoridade comercial; não há scan arbitrário que substitua o catálogo/recibo com o nome da ROM. [SV04, SV16, SV25, SV27]

| Categoria | Organização lógica/controle |
| --- | --- |
| Identidade/ID de licença | Android Keystore e no_backup/station-license-id.txt |
| Catálogo por proprietário | no_backup/station-v2/catalog/{hashLicençaAparelho}.json e .blocked |
| Perfil | no_backup/station-v2/profiles/{hashLicençaAparelho}.json; string de display separada |
| Capas | no_backup/station-v2/covers por ID/revisão e cache legado comprovado |
| Recibos instalados | no_backup/station-v2/installs/{itemId}.json |
| Fila/staging | {raizROMs}/.station-v2/staging e pending-downloads-v1 |
| Conteúdo do jogo | {raizROMs}/.station-v2/{plataforma}/{itemId}/install-*/content |
| Mídia de menu | no_backup/station-v2/menu-media, installed.json e arquivo imutável {sha256}.mp4 |
| Recursos empacotados | Raiz de recursos com marcador .installed-version; reparo por bundle |


### 3.18 Vídeos de menu: contrato remoto e operação local

StationMediaCatalog descreve clipes imutáveis sem URL arbitrária. GET /v1/station/media/catalog?requestId={32hex} retorna envelope domínio TurboRamaStationAndroid/media-catalog/v1 e o mesmo requestId. Revision positiva, items e cada entrada precisam satisfazer asset,sha256,sizeBytes,contentType,width,height,fps,audioTracks. Asset só pode seguir turbo-system-videos/720-{nome}.mp4; hash tem64hex. O cliente aceita1–128 itens, envelope até 256 KiB, no máximo 32 MiB por arquivo e256 MiB total. Dimensões720×720,30fps e zero faixas de áudio fazem parte do contrato. [SV05, SV30]

GET /v1/station/media/files/{sha256} usa sessão/proof e devolve video/mp4 com tamanho exato. StationMediaStore calcula/verifica SHA na publicação, diferente da política das ROMs. A validação local com MediaExtractor exige uma única faixa H264/AVC 720×720,30fps e sem áudio. O índice instalado.json só muda após arquivo/hash/codec passarem e cancelamento não ter ocorrido. Uma atualização inválida deixa o ponteiro do clipe anterior disponível; coleta remove somente .mp4 imutáveis do cache que não estão no índice. [SV05, SV31, SV32]

StationCarouselMedia realiza prefetch num trabalhador, um clipe por vez, somente com menu em foreground, biblioteca pronta, rede e nenhum download de jogo ativo. A seleção preferida é atendida antes dos clipes faltantes da lista. Catálogo é renovado após cinco minutos; revisão inferior é recusada. Ao pausar o menu, a transferência é suspensa. O renderer consome arquivo local e não aguarda HTTP na thread de desenho. Falhas adiam normalmente 60 s, respeitam Retry-After até uma hora e404 limpa a lista em memória para reconsulta; mídia local continua. [SV32]

Existência dessas classes/rotas não comprova publicação recente de todos os clipes. A linha atual conserva os vídeos locais e loop do carrossel; o último retorno documental servidor citado em R134 ainda informa covers.published=false em outro escopo e não substitui prova assinada fresca de mídia. Para diagnosticar vídeo, deve-se distinguir asset local do APK, clipe remoto validado em menu-media e autorização/publicação efetiva. Não confundir mídia de menu com áudio/music de emulação ou vídeo de gameplay. [SV02, SV30, SV31, SV32]

| Método/rota | Contrato e condições |
| --- | --- |
| GET /v1/station/media/catalog?requestId={32hex} | Bearer/proof; resposta assinada media-catalog/v1 com requestId exato; até 256 KiB |
| GET /v1/station/media/files/{64hex} | Bearer/proof; video/mp4, tamanho exato; SHA/codec validados antes de publicar |
| Entradas | asset,sha256,sizeBytes,contentType=video/mp4,width=720,height=720,fps=30,audioTracks=0 |
| Orçamentos | 1–128 clipes;32 MiB por clipe;256 MiB catálogo; reserva32 MiB na publicação |


### 3.19 Fronteira com social e multiplayer: v1 e v3 coexistem

StationApi também transporta os comandos online. POST /v1/station/online/command e /online/events recebem requestId UUID canônico, JSON até 8192 bytes e resposta assinada até 524288 bytes no domínio TurboRamaStationAndroid/online/v1. O cliente compara requestId devolvido e schemaVersion=1 da snapshot. Essas rotas dão acesso ao contrato social, mas não tornam o snapshot legado de engines uma prova suficiente para os quatro owners atuais. [SV05, SV07, SV02]

POST /v1/station/online/multiplayer/command usa a mesma origem, sessão, assinatura e namespace de URL. O resultado precisa conter schemaVersion=1, multiplayerVersion=3 e capability=station-multiplayer.v3. Caso contrário StationApi recusa Unsupported multiplayer snapshot. Portanto v3 não implica URL /v3 nem muda os domínios comerciais de ativação/perfil/catálogo; trata da capacidade/semântica multiplayer. A matriz, approvals, engines e modos são detalhados na seção específica de multiplayer. [SV05, SV02]

A prova para GET /v1/station/online/multiplayer/relay é gerada vinculada ao ticket de uso único; modo none é recusado nesse método. O relay WebSocket tem transportador específico fora da allowlist HTTP comercial ordinária. StationApi não entrega bearer bruto à interface de jogo; entrega proof/ticket pelo contrato. A prova antiga para /online/relay também existe para compatibilidade do sistema online anterior. A presença desses helpers não substitui tickets assinados recentes nem valida jogo entre aparelhos. [SV05, SV09]

A R134 preserva validações de licença/transporte e os perfis/modos dos outros motores; renovar identidades de quatro owners por shared bundle não é uma nova aprovação comercial de todo título. O último retorno real citado pela documentação ainda revisa R129 e não confirma ativação dos motores finais. Handoff de fontes e ledger preparados são pedidos/insumos, não resposta ativa. Este recorte não promove um engine somente porque o endpoint está implementado. [SV02]

| Rota | Requisitos da camada API |
| --- | --- |
| POST /v1/station/online/command | UUID requestId; request<=8 KiB; response<=512 KiB; snapshot schemaVersion1 |
| POST /v1/station/online/events | Mesmo contrato assinado; uso de eventos conforme cliente social |
| POST /v1/station/online/multiplayer/command | Schema1 + multiplayerVersion3 + capability station-multiplayer.v3 |
| GET /v1/station/online/relay | Proof de ticket específico para transporte legado; não GET permitido no HTTP comercial |
| GET /v1/station/online/multiplayer/relay | Proof obrigatório com ticket; transporte dedicado; não bearer exposto ao consumidor |


### 3.20 Retorno às telas, lifecycle e prevenção de duplicação

Depois de acesso e permissão aprovados, LoginActivity tenta resumeExistingTask antes de criar ESActivity. StationTaskPolicy considera somente tarefas pertencentes ao pacote e em execução. Prioriza jogo registrado/Activity de emulação, depois frontend, e por fim lobby legado que pode sobreviver a atualização. StationTaskNavigation move a tarefa à frente e não remove tarefas, mata processo ou envia comandos de servidor. Esse comportamento evita que uma notificação de download abra login sobre um jogo já rodando. [SV12, SV33, SV34]

A abertura de Rooms/Netplay pelo roteador aceita somente componentes internos conhecidos e impede duas chamadas pendentes iguais na mesma tarefa. Se existe jogo em execução, mantém essa tarefa acima do lobby. ReorderToFront/SingleTop reaproveitam a Activity. pendingTarget é limpo quando a Activity chega ou a abertura é recusada. A política de seleção de item também exige snapshot conhecido, ausência de sala, launching=false e returning=false. Essas guardas de navegação são separadas da autoridade de iniciar uma partida. [SV33, SV34]

Voltar no login envia o usuário à HOME do Android; Voltar na central fecha o diálogo e deixa o download. Voltar dos emuladores segue o owner e as Activity/processos específicos. As alterações R134 asseguram retorno persistente das configurações Sony e drenagem de gravações humanas, descritas em sua seção. Um caminho de retorno observado em uma versão anterior de um motor não prova todos os caminhos de save, pause, crash ou Android de outros aparelhos. [SV12, SV21, SV02, SV33]


### 3.21 Diagnóstico, erros de contrato e limites da evidência

StationDiagnostics registra eventos, status, contagens e tempos de autorização/cabeçalhos/download/instalação. X-Correlation-ID é criado como UUID sem hífens pelo cliente e o trace usa esse valor gerado, não texto arbitrário do servidor. Identidades de item/capa são tags SHA256 e revisão; diagnóstico não escreve bearer, activationCode, licenseId pessoal ou path de jogo nesse mecanismo. Falha de observador é capturada para não quebrar a operação principal. Dados pessoais/seriais/capturas/valores de credencial não foram copiados para o dossiê. [SV07, SV35]

A API aceita sucesso200 e classifica as demais respostas com status e code seguro. Corpo de erro fica limitado a 8192 bytes e só copia code se segue STATION_[A-Z0-9_]{1,80}; mensagens/arbitrary payload não são exibidos integralmente. Categorias específicas incluem ITEM_NOT_FOUND, COVER_NOT_FOUND, GRANT_NOT_FOUND e ARTIFACT_NOT_READY. O código de erro é lido sobre TLS, enquanto as respostas aceitas de controle precisam do envelope assinado; não é correto assumir que todo JSON de erro tem a mesma assinatura do catálogo. [SV05, SV35]

Retry-After aceita segundos numéricos ou data HTTP estrita em GMT; seu parser limita1 segundo a 24 horas. Políticas de download e mídia impõem teto próprio de uma hora; store de capas usa o valor conforme seu bloqueio. Um header inválido cai em zero e a política usa espera padrão. Essa diferença evita confundir o parser genérico com a espera efetiva de cada serviço. [SV20, SV32, SV36]

Há provas históricas isoladas do modelo R90, incluindo 641 verificações de recuperação, pause/cancelamento,403 e persistência; R124 publicou fontes completas e preservou downloads/licença. Essas provas qualificam aquela implementação/ambiente sintético na data registrada. A R134 preserva o código, mas instalação em dois aparelhos não reexecuta automaticamente os 641 casos nem prova corte de internet físico, performance comercial prolongada, tempo de download de todos os formatos, primeira inicialização sem pastas, todos os BIOS ou save/load de cada motor. [SV02, SV37, SV38]

As questões em aberto no fim desta parte são lacunas de qualificação, não autorização para remover verificações. Os caminhos e endpoints permitem investigação focada: correlacionar status/código, confirmar revisão assinada, separar download e install, identificar cache visual e observar o jogo exato. O limite demonstrado deve acompanhar qualquer declaração de funcionamento, mantendo fonte/pacote instalado/resposta ativa e execução física como evidências distintas. [SV01, SV02, SV35]


## 4 Frontend controles e emuladores offline

### 4.1 Escopo da leitura do frontend e dos motores offline

Esta parte do dossiê descreve o comportamento implementado do TurboStations Android e a proveniência das suas rotas offline na fonte 4f9039eb9ce13907ce043870bfe1f6e294888556, revisão R134. A leitura considera a composição explícita de R134 sobre R133, R132, R131 corrigida e os módulos preservados da R124 e anteriores. O repositório utiliza fontes congeladas e receitas de transformação delimitadas: a existência de um arquivo histórico não significa que ele seja a fonte escolhida pelo instalador atual. Os exemplos de métodos e processos abaixo apontam para os componentes efetivamente documentados pela cadeia de preservação.

A expressão implementado significa que há código, contrato de lançamento ou evidência estática correspondente. Componente presente significa classe, biblioteca ou recurso identificado no pacote auditado. Instalado significa atualização Android acompanhada de recibo do APK exato. Navegação observada significa uma tela vista em uma sessão delimitada. Gameplay validado exigiria executar o título e conferir renderização, controles, som, saída e demais condições pertinentes. Essas categorias têm resultados próprios e não devem ser fundidas. O estado final dos dois aparelhos deve ser lido no capítulo de instalação produzido durante esta tarefa.

A matriz histórica R120 fornece 50 plataformas canônicas, 78 chaves aceitas pelo catálogo e 43 perfis originais de fallback. A R131 acrescenta os owners internos PS3 e PS4, que são apresentados separadamente porque não pertencem às 50 linhas daquela matriz. A R134 preserva motores, bibliotecas, firmware/importador, vídeos, cache, LEDs e protocolos, alterando o painel gráfico e as famílias Ps3Activity/Ps4Activity. Não há fundamento para declarar todos os jogos, todos os controles ou todos os dispositivos compatíveis apenas pela existência dessas rotas.

- Referências: [OFF01], [OFF02], [OFF03], [OFF04].

### 4.2 Biblioteca, hierarquia e publicação do catálogo

O frontend apresenta uma hierarquia de plataformas, coleções/subpastas e jogos. O modelo nativo agrupa os sistemas por fabricante e prepara uma linha de plataforma a partir dos jogos publicados. Entrar em uma plataforma abre suas coleções ou lista de jogos; a navegação por pastas usa caminho e tipo, distinguindo o item agregado Todos os jogos das coleções reais. O retorno usa o contexto atual para voltar ao nível anterior. No nível de plataformas, Jogar/Baixar é apresentado como Abrir e ações próprias de um jogo, como Apagar ou Saves, são suprimidas pela camada de apresentação.

StationFrontend publica cada linha com itemId, nome, rótulo da plataforma, pasta canônica, coverId, caminho de lançamento instalado, chave da coleção, descrição, revisão e eventual caminho de capa previamente preparado. O mapeamento StationPlatforms é explícito; não deduz o destino de uma string arbitrária. Uma plataforma desconhecida gera aviso de suporte e não recebe uma pasta inventada. Aliases brasileiros preservam os mesmos motores e, quando aplicável, as pastas existentes: megadrive--br, super-nintendo--br e nintendo-64--br têm regras próprias, enquanto PSP BR compartilha a pasta psp.

StationCoordinator administra a biblioteca e mantém o catálogo assinado em cache. No acesso sem novo código, pode restaurar um envelope local válido ligado à licença salva e ao dispositivo; uma sessão recém-autenticada continua necessária para operações que pedem autorização remota. A biblioteca em cache é identificada como tal. Atualizar a lista faz a renovação pelo serviço e substitui o catálogo autorizado. O frontend também possui atualização automática em trabalhador separado: primeira tentativa após cinco segundos e intervalo de sessenta segundos, condicionados a foreground, configuração, disponibilidade da API, autorização e ausência de downloads e trabalho de capas ativos.

A consulta de um jogo instalado é feita pelo recibo da instalação correspondente, não por uma varredura indiscriminada de pastas ROM. installedPathsFor filtra a plataforma mapeada; installedPathForItem exige o identificador selecionado e retorna erro se não houver instalação reconhecida. A abertura de uma sala utiliza essa regra para exigir que o jogo seja baixado antes. O caminho publicado para o renderer é o arquivo inicial reconhecido, enquanto a seleção do motor offline continua sendo responsabilidade do resolvedor de comandos.

- Referências: [OFF05], [OFF06], [OFF07].

### 4.3 Pesquisa, ficha e ações do usuário

A pesquisa respeita o contexto em que foi aberta: plataformas, coleções ou jogos. A camada nativa mantém o campo de entrada, teclado e resultados do GuiStore original, acrescentando apresentação e ações de recuperação. Limpar pesquisa remove o filtro; Ver resultados fecha a edição para mostrar a lista; Editar pesquisa retorna ao campo quando a busca está vazia. Há mensagens específicas para nenhuma plataforma, nenhuma coleção e nenhum jogo encontrado. As caixas usadas pelo desenho e pelo toque/controle são as mesmas, evitando que a aparência e a área clicável sejam calculadas por regras diferentes.

A ficha do item apresenta título, capa, descrição ou sinopse, contagens, informação de jogadores e classificação. A escolha da sinopse combina o texto recebido do servidor com informações locais e correções específicas de edição; quando não há informação, mostra Sinopse ainda não localizada para esta edição. A ausência de classificação aparece como SEM NOTA. Texto que ultrapassa a altura disponível tem área de rolagem; isso não deve ser confundido com atualização da capacidade online. A indicação textual de jogadores é descritiva, enquanto criar uma sala continua dependendo do contrato específico do jogo, conteúdo e modo.

As ações de jogo disponíveis no contexto original incluem baixar/jogar, online, saves, apagar, atualizar e voltar. A barra nativa tem ícones vetoriais e estados de foco, desabilitado e confirmação. Baixar recebe cor própria; a apresentação não cria uma segunda rotina de transferência. O pedido de apagar é encaminhado à implementação de instalação por recibo. No contexto de plataforma ou coleção, o botão Abrir substitui a ação de jogo e navega para o conteúdo. A faixa INSTALADO depende da reconciliação do recibo com o arquivo inicial e não garante que o emulador tenha executado esse título.

A revisão R133 acrescenta fotografias estáticas de PSP, PS3 e PS4 ao painel ao lado da sinopse. A arte de hardware é um recurso de apresentação separado da ficha de plataforma, da rota do emulador e da elegibilidade online. O código desenha uma quad no contexto SDL/GL existente, com ajuste proporcional e limites alfa. O nome de uma plataforma na tabela visual, como PlayStation 5, também não é prova de um motor correspondente: a matriz de lançamento e os componentes reais devem ser consultados.

- Referências: [OFF08], [OFF09], [OFF10].

### 4.4 Painel de efeitos gráficos da R134

A R134 organiza o painel Efeitos gráficos em quatro páginas: Fundo, Carrossel, Luzes e Ícones. O cabeçalho mantém Efeitos gerais e Voltar. Em telas largas, a navegação fica numa coluna lateral; em telas estreitas, as quatro categorias ficam numa faixa horizontal. A decisão de layout considera orientação e largura em dp. A área de opções é rolável e apenas a página ativa permanece visível. Há estados de foco, seleção e descrições acessíveis para os controles. As mudanças são salvas automaticamente nas preferências existentes, sem criar um ciclo de animação ou consulta periódica para navegar entre categorias.

Fundo oferece Ondas, Céu e Sem fundo, além de Movimento do fundo. Carrossel oferece Reta, Diagonal e De lado, Vídeos do carrossel e Com loop/Sem loop para o vídeo principal. Luzes contém LEDs das capas e Efeitos das células. Ícones contém Ícones e Lotties e Transições. O total é de seis efeitos independentes: LED, vídeo, movimento do fundo, ícones, efeitos das células e transições. A mudança do estilo do carrossel usa uma preferência separada da máscara de efeitos; a escolha não é codificada como mais um bit de iluminação.

Efeitos gerais desliga a máscara efetiva sem apagar as escolhas individuais. Ao reativar, as opções salvas voltam a determinar os efeitos. O estilo de fundo também é preservado quando o movimento é desligado. StationGraphicsPreferences usa um estado imutável com máscara individual, masterDisabled, modo de fundo e revisão. Os anúncios são entregues na thread principal e consolidados para evitar notificações redundantes. A ponte JNI recebe estado e revisão numa publicação coerente, impedindo que o renderer combine partes de escolhas distintas.

Esses controles afetam a apresentação dos menus. Não mudam o núcleo do emulador, os mapeamentos de input, o frame rate do jogo ou o perfil multiplayer. Economia significa supressão de efeitos implementada na UI, mas o valor de consumo ou temperatura não foi medido por essa implementação. A R134 conserva a política de vídeos e o limitador de apresentação herdados; mudar a divisão em páginas não demonstra ganho físico de bateria, latência ou estabilidade.

- Referências: [OFF11], [OFF12].

### 4.5 Geometria do carrossel e limite de apresentação

Reta é a formação padrão. Diagonal aplica uma geometria alternativa às células que não estão selecionadas, mantendo o pipeline de MVP e os mecanismos existentes de picking e recorte. De lado inverte a orientação e pode mostrar a capa principal com dez vizinhas, sem duplicatas. A revisão R123 ampliou as prioridades apenas nesse modo até a janela necessária; os modos Reta e Diagonal continuam com a formação anterior. O renderer mantém a capa selecionada como referência e não utiliza um novo shader, FBO ou decoder apenas para transformar a geometria.

Na R124, o orçamento de frames retidos dos vídeos acompanha os itens únicos visíveis. Reta e Diagonal mantêm oito frames. De lado admite de oito até treze conforme a janela e a transição, descartando frames que saem do conjunto quando o orçamento diminui. A política corrige células sem imagem que ocorriam com o limite antigo de oito. Onze frames representam aproximadamente 2,97 MiB adicionais de pixels em relação ao orçamento anterior; o teto transitório de treze representa cerca de 4,94 MiB adicionais. Esses números são estimativas de buffers do formato previsto, não memória residente total do driver.

O limite de trinta fps se aplica aos menus/apresentação. O código mantém vídeos locais de 720 por 720 e trinta quadros por segundo, frames adjacentes retidos e um único decoder focado. Não se deve ler esse limite como travamento de todos os jogos em trinta fps. A configuração Frame limit do PS3 e a VBlank do PS4 pertencem aos próprios motores, com semântica diferente. A documentação da R131 explicita que a composição Sony não impõe o limite do carrossel ao gameplay.

Existe evidência física histórica da R124 mostrando a capa principal e dez pequenas no carrossel De lado, sem célula vazia naquela captura. Isso qualifica uma observação delimitada da apresentação e não a reprodução contínua de todos os vídeos, todos os temas ou todas as transições. Os testes HOST e de política exercitam geometria e orçamento, porém não executam GPU Android, codec, gesto físico, fonte ampliada ou consumo.

- Referências: [OFF13], [OFF14].

### 4.6 Capas, filas, cache e concorrência

A fila de capas é global para o frontend. StationCoverQueue possui um trabalhador de IO/decodificação; pedidos visíveis têm prioridade sobre a passagem opcional de preenchimento do cache. Downloads de jogos têm um trabalhador independente. O estado de preparação do catálogo evita competição entre a publicação inicial e os pedidos visíveis. Sair de foreground cancela gerações obsoletas; uma capa de uma publicação anterior não deve entrar numa lista substituída. Erros são classificados em cancelamento, falha transitória, ausente, limite de taxa e autorização negada, com tratamento de nova tentativa coerente.

O cache canônico guarda identidades coverId/revisão e pode reconhecer cache legado permitido. O legado exige revisão exata, arquivo privado regular, tamanho limitado e assinatura de imagem válida; o caminho é revalidado por tipo, tamanho e mtime antes de nova publicação. A operação evita copiar em massa arquivos já persistidos. StationFrontend constrói o conjunto de identidades esperado e aquece o cache antes da publicação quando pertinente. Uma geração, a biblioteca correspondente e o estado foreground são conferidos repetidamente para interromper trabalho desatualizado.

A preparação herdada limita a passagem inicial de misses a sessenta e quatro tentativas ou vinte segundos. Falha de rede, autenticação ou rate limit encerra essa passagem; o catálogo continua com os sucessos disponíveis. Uma instalação vazia com milhares de capas pode precisar de mais de uma abertura para completar o cache. A publicação é progressiva: capa selecionada imediata, janela atual delimitada e uma vizinha por pulso de oitenta milissegundos. No estilo De lado, a política posterior de prioridades considera a janela expandida; não deve ser descrita como uma publicação simultânea das milhares de capas.

Na central de downloads, os thumbnails têm cache de bitmap próprio limitado a oito MiB e decodificação reduzida para até 256 pixels na maior dimensão. A fila de capa compartilhada realiza a leitura/decodificação fora da UI. Ao fechar o painel, handles, callbacks, retries e imagens são liberados. O frontend nativo limita as filas de inbox de capas e jobs a 4096 identidades; exceder o limite gera falha explícita. O valor é um teto defensivo da ponte, não uma garantia de que qualquer catálogo de tamanho arbitrário possa ser publicado.

- Referências: [OFF05], [OFF15], [OFF16], [OFF17].

### 4.7 LEDs, estado GL e cache de campos

A iluminação da capa selecionada mantém o classificador da arte e o kernel de emissores/halos do pipeline herdado. O trabalho estático caro é preparado num campo RGBA16F; animação, paleta, ganho e composição continuam no shader de desenho. Há um destino candidato separado do campo completo. A preparação incremental cria quatro linhas por quadro, e somente um candidato completo com a mesma chave é promovido. Mudança de seleção, identidade, revisão de upload, modelo, viewport ou contexto invalida a preparação correspondente.

O cache de campos completos conserva até três entradas no mesmo contexto e limita seus pixels acumulados a oito MiB. O cálculo nominal é largura vezes altura vezes oito bytes. Uma entrada maior que esse teto não entra no conjunto salvo. O reaproveitamento exige correspondência de textura fonte, identidade, modelo, tamanho e viewport. Upload ou destruição da textura de origem invalida os campos associados antes de eventual reutilização do número GLuint. Nomes GL de um contexto antigo não são apagados através de um contexto novo, pois o driver pode ter reutilizado o mesmo identificador para outro objeto.

Cada fatia restaura os estados de framebuffer, viewport, scissor, buffers, texturas, samplers, programas e máscaras de escrita pertinentes ao pipeline. O destino incompleto não substitui a capa original: o usuário continua vendo a arte enquanto o campo é produzido. Se o caminho otimizado não está disponível ou a preparação não conclui, o desenho usa os fallbacks herdados. O cache é uma otimização, não um novo requisito de funcionamento nem uma promessa de qualidade diferente.

Quatro linhas por quadro podem fazer a preparação inicial da iluminação de capas de 1024–1536 pixels levar cerca de 8,5–12,8 segundos segundo a estimativa documentada da R115. Esse tempo não equivale a bloquear a UI durante toda a preparação. Também não prova ausência de pausas do driver, custo GL constante ou redução térmica. O orçamento precisa ser relacionado com medição no aparelho para qualquer alteração; a R134 apenas conserva esse comportamento e reorganiza os controles que o habilitam.

- Referências: [OFF16], [OFF18].

### 4.8 Loading e preparação dos shaders

A R132 introduz uma barreira na fase inicial do GuiStore. Primeiro deve ser desenhado um frame preto de loading; só então a atualização seguinte tenta preparar os programas existentes no contexto SDL/GL que fará o desenho dos menus. Não existe criação de um contexto trabalhador concorrente para essa compilação. O owner e o contexto são parte do estado da preparação. Se mudarem, o estado deve ser reavaliado; a regra de efeitos desligados também é mantida.

O progresso final depende de dois marcos reais: publicação do catálogo nativo e preparação gráfica. O cálculo acrescenta essas duas unidades ao total de itens e só mostra conclusão real quando ambos estão satisfeitos. O frame terminal de loading deve ser desenhado antes de avançar para o menu e para o tratamento de capas/boas-vindas. Se o catálogo falhar, o fluxo original de erro continua disponível; o código não apresenta cem por cento como sucesso de uma publicação que não ocorreu.

A tentativa de compilação de shader pode ser rejeitada pelo driver. Nesse caso, a rotina considera a tentativa encerrada e mantém o fallback anterior em vez de repetir indefinidamente o loading. A composição exige os exports emparelhados StationLoading_graphicsReady e StationLoading_stage e verifica o ABI/GOT original antes de instalar o hook. Essa verificação evita aplicar os offsets a uma biblioteca diferente sem reconhecer o contexto binário.

Preparar mais cedo muda quando o custo acontece. O código não demonstra redução do tempo total de compilação, não acrescenta cache binário de programas e não prova menor consumo. Loading, cache de capas, preparo de emulador Sony e importação de jogo são etapas distintas; a extração Sony só começa no worker do owner solicitado e não vira uma tarefa obrigatória executada a cada frame do carrossel.

- Referências: [OFF19], [OFF20].

### 4.9 Vídeos locais, decoder e ciclo de vida

StationSinglePassVideo720 mantém sessões com SurfaceTexture, Surface, estado de visibilidade, frame pronto e indicadores de conclusão. O MediaPlayer pertence exclusivamente ao HandlerThread StationVideoOnce. A consulta dos codecs aceita hardware AVC compatível com 720×720 a trinta fps; se não houver decoder apropriado, a capacidade fica zero e as artes/posters herdados permanecem como alternativa. Quatro slots são estrutura de controle, não quatro players ativos: uma nova sessão chama stopAll e o decoder focado é único.

A rotina de ciclo de vida reconhece a ESActivity do frontend. Resume de outra Activity, pause/stop/destroy do frontend e mudança de foreground encerram as sessões pertinentes. Um watchdog detecta sessão sem desenho recente, primeiro frame que não chegou e entrega de frames interrompida. Os limites documentados são três segundos sem desenho, quinze segundos para primeiro frame e quatro segundos de atraso de entrega quando o vídeo está visível e preparado; a checagem é agendada no worker, fora do loop de desenho da UI.

Na política de reprodução única, o player busca um frame aproximadamente dois quadros antes do fim e o renderer conserva essa imagem. Seek tem limite de espera e, se falhar, o frame anterior é mantido. A R130 adiciona a preferência persistente de loop e o parâmetro de escopo da plataforma. No fim de um vídeo de plataforma visível, busca o começo e reinicia o mesmo player/Surface/decoder, sem nova preparação ou nova leitura do asset. Coleções continuam reprodução única, mesmo quando o usuário escolhe Com loop.

Desabilitar vídeos, ativar economia, esconder a sessão ou retirar sua posse impede reinício indevido. Frames retidos de miniaturas são recursos separados do player e ficam sujeitos ao orçamento visível de oito a treze da R124. Mudança de contexto remove a possibilidade de reutilizar handles incompatíveis. Esses mecanismos reduzem duplicações desnecessárias e delimitam recursos, mas codec, GL, travamentos, tempo de retorno e funcionamento contínuo precisam de observação física para serem declarados estáveis.

- Referências: [OFF21], [OFF22], [OFF14].

### 4.10 Resolução de comandos e leitura da matriz de 50 plataformas

A resolução offline passa pelos hooks N64, Mega e o conjunto de comandos de GameCube/demais sistemas, antes do XML original. Quando o XML não possui uma chave, o resolvedor procura um perfil original pela pasta e depois pelo nome, usando a normalização prevista naquele consumidor. A comparação dos hooks tem regras distintas, por isso a R120 precisou reconhecer explicitamente megadrive--br, super-nintendo--br e pc-engine-cd. A ausência de comando no XML, isoladamente, não significa ausência de rota.

Alguns comandos têm a forma libretro: core=<identificador>, porém o identificador é interceptado e abre um emulador Android próprio. N64, Dolphin, MAME, PPSSPP, ARMSX2, Flycast e outros não devem ser descritos automaticamente como cores executados no LibretroPlayer apenas porque esse texto aparece no comando. A matriz registra o bootstrap, a cadeia de Activity e o processo onde a emulação realmente ocorre. As famílias sem interceptação usam o LibretroPlayer original no processo principal.

A tabela a seguir reproduz as cinquenta linhas canônicas auditadas com motor, pasta e processo. A coluna Família remete à tabela de condições que detalha Android, formatos realmente conferidos, opções e controles. Em todas as linhas, a comprovação principal é estática e herdada pela preservação posterior; instalada no aparelho descreve o pacote inteiro e não cinquenta gameplays. Oito dependências ausentes são um achado histórico do Motorola consultado na R120 e não uma afirmação sobre a situação atual dos dois aparelhos sem nova leitura dos diretórios.

O registro completo de nomes/aliases, bibliotecas e class_defs é launch-matrix-r120.json. Ele registra 146 verificações HOST das seis funções reais de seleção de comando, com zero falhas e trinta e sete passagens ao fallback original. Strings e resolvedor XML foram mocks delimitados nesse harness; ele não executou ABI ARM64, JNI, GPU, assets, BIOS ou jogo. A R126 acrescenta uma auditoria estática de 51.818 verificações, igualmente sem gameplay, e os recibos R134 confirmam a preservação das bibliotecas dos motores offline.

| Plataforma / pasta | Motor | Processo | Família / condição |
| --- | --- | --- | --- |
| 3ds / 3ds | LibretroPlayer: azahar | principal | L1 · componentes/rota auditados; jogo pendente |
| Arcade / arcade | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| Atomiswave / atomiswave | Flycast Android | :flycast | F1 · componentes/rota auditados; jogo pendente |
| Dreamcast / dreamcast | Flycast Android | :flycast | F1 · componentes/rota auditados; jogo pendente |
| GameCube / gamecube | Dolphin Android | :dolphin | D1 · componentes/rota auditados; jogo pendente |
| Gameboy / gameboy | LibretroPlayer: gambatte | principal | L1 · componentes/rota auditados; jogo pendente |
| Gameboy Color / gameboy-color | LibretroPlayer: gambatte | principal | L1 · componentes/rota auditados; jogo pendente |
| Gba / gba | LibretroPlayer: mgba | principal | L1 · componentes/rota auditados; jogo pendente |
| Master System / master-system | LibretroPlayer: genesis_plus_gx | principal | L1 · componentes/rota auditados; jogo pendente |
| MegaDrive / megadrive | MD.emu EX+ | :megadrive | E1 · componentes/rota auditados; jogo pendente |
| MegaDrive - BR / megadrive--br | MD.emu EX+ | :megadrive | E1 · componentes/rota auditados; jogo pendente |
| Neo Geo / neo-geo | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| Neo Geo CD / neo-geo-cd | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| Nintendinho / nintendinho | LibretroPlayer: fceumm | principal | L1 · componentes/rota auditados; jogo pendente |
| Nintendo 64 / nintendo-64 | Mupen64Plus AE | :n64 → :n64core | N1 · componentes/rota auditados; jogo pendente |
| Nintendo 64 - BR / nintendo-64--br | Mupen64Plus AE | :n64 → :n64core | N1 · componentes/rota auditados; jogo pendente |
| Nintendo DS / nintendo-ds | LibretroPlayer: melonds | principal | L1 · dependência ausente na observação R120 |
| Odyssey 2 / odyssey-2 | LibretroPlayer: o2em | principal | L1 · dependência ausente na observação R120 |
| PSP / psp | PPSSPP Android | :psp | P1 · componentes/rota auditados; jogo pendente |
| Pc Engine / pc-engine | LibretroPlayer: mednafen_pce_fast | principal | L1 · componentes/rota auditados; jogo pendente |
| Pc Engine cd / pc-engine-cd | LibretroPlayer: mednafen_pce | principal | L1 · componentes/rota auditados; jogo pendente |
| Playstation 1 / psx | LibretroPlayer: pcsx_rearmed | principal | L1 · componentes/rota auditados; jogo pendente |
| Playstation 2 / ps2 | ARMSX2 Android | :ps2 | P2 · componentes/rota auditados; jogo pendente |
| Playstation 2 - BR / ps2br | ARMSX2 Android | :ps2 | P2 · componentes/rota auditados; jogo pendente |
| Psp - BR / psp | PPSSPP Android | :psp | P1 · componentes/rota auditados; jogo pendente |
| Psvita / psvita | Vita3K Android | :psvita | V1 · componentes/rota auditados; jogo pendente |
| Super Nintendo / super-nintendo | Snes9x EX+ | :snes | E1 · componentes/rota auditados; jogo pendente |
| Super Nintendo - BR / super-nintendo--br | Snes9x EX+ | :snes | E1 · componentes/rota auditados; jogo pendente |
| Switch / switch | Yuzu Android (unchanged) | principal | S1 · rota package corrigida; jogo pendente |
| atari2600 / atari2600 | LibretroPlayer: stella | principal | L1 · dependência ausente na observação R120 |
| atari7800 / atari7800 | LibretroPlayer: prosystem | principal | L1 · dependência ausente na observação R120 |
| colecovision / colecovision | LibretroPlayer: bluemsx | principal | L1 · dependência ausente na observação R120 |
| cps1 / cps1 | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| cps2 / cps2 | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| cps3 / cps3 | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| fbneo / fbneo | LibretroPlayer: fbneo | principal | L1 · dependência ausente na observação R120 |
| fds / fds | LibretroPlayer: fceumm | principal | L1 · componentes/rota auditados; jogo pendente |
| gameandwatch / gameandwatch | LibretroPlayer: gw | principal | L1 · dependência ausente na observação R120 |
| gamegear / gamegear | LibretroPlayer: genesis_plus_gx | principal | L1 · componentes/rota auditados; jogo pendente |
| jaguar / jaguar | LibretroPlayer: virtualjaguar | principal | L1 · dependência ausente na observação R120 |
| mame / mame | MAME 4droid Current | :mame | M1 · componentes/rota auditados; jogo pendente |
| naomi / naomi | Flycast Android | :flycast | F1 · componentes/rota auditados; jogo pendente |
| naomi2 / naomi2 | Flycast Android | :flycast | F1 · componentes/rota auditados; jogo pendente |
| saturn / saturn | Saturn integrado | :saturn | T1 · componentes/rota auditados; jogo pendente |
| sega32x / sega32x | LibretroPlayer: picodrive | principal | L1 · componentes/rota auditados; jogo pendente |
| supergrafx / supergrafx | LibretroPlayer: mednafen_supergrafx | principal | L1 · componentes/rota auditados; jogo pendente |
| wii / wii | Dolphin Android | :dolphin | D1 · componentes/rota auditados; jogo pendente |
| wiiu / wiiu | Cemu Android | :wiiu | W1 · componentes/rota auditados; jogo pendente |
| xbox / xbox | x1box/xemu | :xbox → :xboxemu | X1 · componentes/rota auditados; jogo pendente |
| xbox360 / xbox360 | Xendroid | :xbox360 → :xbox360emu | X2 · componentes/rota auditados; jogo pendente |

| Família | Exemplo de despacho / biblioteca |
| --- | --- |
| L1 | Fallback → LibretroPlayer::run em ESActivity; lib<core>_libretro_android.so. |
| E1 | megaCommandHook/SNES → com.mdimagn.BaseActivity ou com.imagine.BaseActivity; libs próprias EX+. |
| N1 | n64CommandHook → N64Bootstrap → GameActivity/CoreService; libmupen64plus-core.so. |
| D1 | gamecubeCommandHook → DolphinEntryActivity/EmulationActivity; libdolp.so. |
| M1 | mameCore → MameBootstrap/MameEntryActivity → MAME 4droid; libMAME4droid.so + JNI. |
| F1 | identificador flycast interceptado → NativeGLActivity; libflycast.so + libturbo_flycast.so. |
| P1 | identificador PPSSPP interceptado → PpssppActivity; libppsspp_jni.so. |
| P2 | native_ps2 → Ps2Bootstrap → com.armsx2.Main; emucore16k/4k. |
| V1 | VitaEntryActivity → org.vita3k.emulator.Emulator; libVita3K.so. |
| S1 | ACTION_VIEW → BootstrapActivity → Yuzu EmulationActivity; libyuzu-android.so. |
| T1 | native_saturn → SaturnActivity; libturbo_saturn.so. |
| W1 | WiiUEntryActivity → Cemu EmulationActivity; libCemuAndroid.so. |
| X1 | XboxEntryActivity → x1box.MainActivity; libxemu.so. |
| X2 | Xbox360Entry/GameEntry → XenDroid EmulatorHostActivity; libe.so. |

- Referências: [OFF03], [OFF27], [OFF02].

### 4.11 Condições dos motores offline e limites de inventário

Os formatos mencionados abaixo são aqueles explicitamente documentados pela ponte ou contrato local lido. Não se presume que a lista geral de extensões de um projeto upstream atual descreva o binário exato incorporado. Para várias famílias LibretroPlayer e wrappers legados, esta janela de auditoria não consolidou uma lista completa de extensões ou o minSdk de cada componente; isso é registrado como não conferido. ARM64 e capacidade gráfica apropriada continuam condições do conjunto nativo, mas não são uma garantia de performance de cada título.

A identificação de versão vem dos recibos de proveniência e dos commits correspondentes. Há motores preservados de APKs oficiais e módulos recompilados: Flycast, PSP, PS2, Vita, Cemu e XenDroid incluem binários cuja reconstrução integral não é alegada pelos recibos; Saturn registra reconstrução a partir da fonte correspondente. O LibretroPlayer possui binário normal preservado cuja fonte C++ exata do loop não foi localizada na auditoria. Isso é relevante para alterar overlays, pauses ou comportamentos internos: a disponibilidade de um projeto com nome semelhante não autoriza tratá-lo como fonte equivalente.

N64 usa o conjunto oficial Mupen64Plus AE 3.0.249 beta, commit 33bf7021, mínimo API 28 documentado, plugins e preferências separados. Dolphin usa a integração 2609-7 e commit 5102a033 na documentação das rotas online/controle, com Android e formato offline completo não requalificados neste dossiê. PPSSPP tem proveniência 1.20.4; ARMSX2 2.7.2; Flycast v2.7-44-ge36e9df2d; Vita3K build 4115/a366df69; Yaba Sanshiro 1.20.46; Cemu 0.5.2 e XenDroid0b11201, os dois últimos explicitamente experimentais.

A tela de configuração de cada família segue o owner correspondente quando há rota documentada. O frontend não fornece automaticamente todas as opções de todos os motores num painel único. A R134 altera apenas o painel gráfico e as configurações dos owners Sony internos. Escolha de renderer, driver, resolução, frame skip, perfis e saves dos demais emuladores foi preservada; sua aparência e efeito físico dependem dos componentes existentes e precisam ser conferidos no próprio motor.

| Família | Versão / requisito comprovado | Conteúdo / configurações / controles |
| --- | --- | --- |
| L1 · LibretroPlayer | Binário normal preservado; ABI ARM64. MinSdk e lista completa de extensões por core não consolidados. | Cores individuais da matriz; host é ESActivity/LibretroPlayer. PSX normal possui duas portas no caminho auditado; não importar capacidades Multitap/analógico por nome de core. API de ocultação universal do touch não comprovada. |
| E1 · SNES/Mega EX+ | Snes9x EX+ e MD.emu EX+; fonte EX+ correspondente disponível. Versão comercial exata e minSdk não fixados nesta matriz. | Menu, input, save states/saves e preferências próprios preservados. VController AUTO possui hotplug e respeita ON/OFF manual; a detecção também considera teclado. Extensões offline completas não requalificadas. |
| N1 · N64 | Mupen64Plus AE 3.0.249 beta, commit 33bf7021; Android 9/API 28. | ROM_PATH real; formatos registrados N64 incluem n64/z64/v64, mas lista offline completa/archives não requalificada aqui. Menu oficial vídeo/áudio/input/perfis e saves; touch/input próprios. :n64 e :n64core. |
| D1 · GameCube/Wii | Dolphin2609-7, commit 5102a033; pacote ARM64 preservado. MinSdk offline não consolidado. | Arquivo local enviado ao owner Dolphin. Registro do bundle usa iso/gcz/wbfs/rvz; isso não substitui auditoria de todos os formatos offline. Configurações originais, touch e portas próprios; adaptação transitória Dolphin da R120. |
| M1 · MAME/Neo Geo | MAME 4droid Current 1.41.2, MAME 0.289; minSdk não consolidado nesta leitura. | Cartucho ZIP permanece comprimido para o MAME; conteúdo e BIOS devem corresponder ao driver/parent. CD: CHD v5 autônomo, BIOS específica e driver CDZ. Menus/controles próprios; hide pode depender da primeira entrada. |
| F1 · Flycast | v2.7-44-ge36e9df2d, commit e36e9df2; binário oficial preservado. | Dreamcast/Atomiswave/Naomi/Naomi2, bibliotecas e BIOS/configuração por hardware. MinSdk/formato completo não consolidado. VGamepad/timer têm gaps de supressão e hitTest; não foi aplicado conserto universal. |
| P1 · PSP | PPSSPP 1.20.4 oficial preservado; minSdk do componente não consolidado. | URI/arquivo enviado ao PPSSPP, menu próprio. Lista offline de formatos não extraída nesta janela. ShowTouchControls é persistente e TouchButtonHideSeconds é inatividade; presença física não prova restauração automática. |
| P2 · PS2 | ARMSX2 2.7.2; artefato legacy armv8.0-sdk26. SDK26 do artefato não é mínimo efetivo comprovado de todo TurboStations. | Owner com.armsx2.Main e emucore4k/16k preservados. BIOS/configuração/licenças permanecem privadas quando aplicáveis. Formatos e overlay precisam ser conciliados com DEX exato; referência upstream isolada não basta. |
| V1 · Vita | Vita3K build 4115, engine_commit a366df69, binário preservado. | Instalação/importação/configuração do owner Vita; dependências de jogo/firmware e formato completo não requalificados. hideOverlayWhenControllerConnected default true e restauração no último disconnect documentados. |
| S1 · Switch | Yuzu integrado; biblioteca idêntica às referências R76/R119. Versão de release textual/minSdk não fixados aqui. | Bootstrap/action/URI/MIME/content preservados; assets/keys e firmware privados mantidos. Novos caminhos roms/switch; legado exato só migra quando ausente/vazio. Overlay de presença do motor preservado; gameplay pendente. |
| T1 · Saturn | Yaba Sanshiro 1.20.46 Android; recompilado de fonte correspondente. | SaturnActivity/Pad separa input físico e toque. Opção touch manual; sem listener de presença no wrapper auditado. MinSdk, BIOS e formato offline completo não requalificados. |
| W1 · Wii U | Cemu Android 0.5.2; binário oficial preservado; experimental. | Cemu EmulationActivity e InputOverlaySurfaceView/StateFlow; callbacks de input próprios. Lista offline de formatos, conteúdo/keys e minSdk não consolidados. Auto-hide por presença não confirmado no gate do StateFlow. |
| X1 · Xbox clássico | x1box/xemu, libs preservadas; versão textual/minSdk não fixados nesta matriz. | Wrapper MainActivity, processos interface/emulação distintos. Dependências de firmware/disco/storage do owner precisam ser válidas; lista de formatos não consolidada. Detecção/hide existentes não excluem virtual na fonte inspecionada. |
| X2 · Xbox360 | XenDroid0b11201 oficial preservado; experimental. | XenDroid EmulatorHostActivity/Compose, processos distintos. show_touch_overlay manual persistente; presença transitória não comprovada. Formatos/minSdk e compatibilidade de jogos não consolidados. |
| Y3 · PS3 interno | aPS3e 2.43; Android 9/API 28, ARM64; :station_ps3. | Launcher direto ISO; owner também reconhece pasta de jogo válida. Firmware automático do pacote local; ISO criptografado pode exigir chave própria. Config18 campos+touch, input físico e Surface próprios. |
| Y4 · PS4 interno | BachataS4 0.2.4; Android 12/API 31, ARM64 e GPU compatível; :station_ps4. | Launcher direto PKG; probe/extract oficiais e biblioteca privada. Importação precisa de conteúdo válido e, quando necessário, chave própria. Config11 campos+touch. Bridge sem pause/rebind e retorno background físico pendente. |

- Referências: [OFF28], [OFF29], [OFF30].

### 4.12 N64, Dolphin e separação dos owners

N64 incorpora interface, controles, áudio, vídeo, perfis, saves, núcleo e plugins do Mupen64Plus AE. O lançamento normal parte do arquivo instalado e passa pela ponte N64Bootstrap e entrada oficial antes de GameActivity/CoreService. O parâmetro de caminho utiliza a chave real ROM_PATH. A ponte de configurações abre o menu público do upstream e não simula coordenadas. A interface fica no processo :n64 e core em :n64core; arquivos internos, cache, arquivos externos privados e SharedPreferences n64.* evitam compartilhar estado com SNES, Mega e frontend.

Na primeira preparação N64, o armazenamento de dados de jogo é interno; uma escolha posterior válida é mantida. Assets oficiais de mupen64plus_data são preparados pela rotina existente. A saída de GameActivity informa resultado à Gallery; a ponte retorna à ESActivity com CLEAR_TOP|SINGLE_TOP e encerra somente seu processo de interface conforme a cadeia documentada. O núcleo segue o encerramento oficial. Isso não autoriza matar uma partida para conferir cadastro, firmware ou existência de biblioteca.

Dolphin usa Activity e superfície próprias em :dolphin. O adaptador de presença da R120 é restrito à Activity exata EmulationActivity e à classe InputOverlay. Reconhece dispositivo não virtual com máscara completa GAMEPAD ou JOYSTICK, guarda a visibilidade original, envia ACTION_CANCEL, libera os overrides virtuais e usa INVISIBLE para preservar geometria. Ao remover o último controle, reconstrói o layout de toque pela API pública e restaura o estado anterior. Não grava preferências e não altera GameSurface nem mapeamento físico.

A configuração nativa do Dolphin, suas portas de GameCube/Wii e o renderer pertencem ao emulador. O runtime online real acrescentado na R126 usa as APIs oficiais, mas não transforma toda função offline em capacidade de sala. Os cinquenta motores não foram migrados universalmente para o mesmo owner online. As integrações de N64/Dolphin são exemplos de owners específicos preservados, e a elegibilidade por jogo/modo é tratada no capítulo multiplayer.

- Referências: [OFF29], [OFF30], [OFF31].

### 4.13 MAME, Neo Geo e BIOS CD automática

MAME 4droid Current 1.41.2/MAME 0.289 recebe as rotas Arcade, MAME, CPS1/2/3, Neo Geo e Neo Geo CD. Cartuchos usam o ZIP interno do conjunto e rompath apontando para o pai real do arquivo instalado, incluindo gerações de coleções. O contêiner da transferência e o ZIP do conjunto são camadas diferentes. A correção histórica do bootstrap substituiu a chave de pasta errada e passou a localizar a BIOS junto ao conteúdo existente. A preferência e os saves válidos do MAME são conservados.

Neo Geo CD na integração lida aceita CHD v5 autônomo. A identificação da plataforma é feita pelos ancestrais canônicos neo-geo-cd/neogeocd, não por uma palavra no nome do jogo. CUE/BIN/ISO, CHD com pai e seletor de múltiplos discos não foram acrescentados nessa correção. O lançador valida cabeçalho e dependências e abre o driver CDZ com -cdrom; conferir o cabeçalho não é validar todos os setores de um disco. A BIOS CD é distinta da BIOS de cartucho.

A R66 liga a preparação aos recursos que já estavam incluídos no APK. Primeiro reutiliza as dependências válidas privadas ou ao lado do disco; se faltar algo, lê os assets conhecidos, confere tamanho/CRC/SHA-1 e prepara os arquivos atomicamente no worker. Reabertura válida evita releitura e regravação. Importação manual permanece alternativa quando necessária, mas não é requisito normal do APK que já traz essas dependências. Este dossiê registra somente o comportamento e as referências; não reproduz bytes de BIOS.

A auditoria do catálogo histórico identificou nomes não registrados no MAME 0.289, variantes/hacks com conjuntos próprios e dois itens classificados como Neo Geo que pertencem a outro hardware. Uma abertura histórica de KOF98 apresentou corrupção verde/branca na captura curta, sem causa isolada. A correção da BIOS CD não resolve automaticamente cartuchos, driver, gráficos ou online. Os 66 testes locais da R66 exercitaram preparação e preservação com cabeçalho CHD sintético; não qualificaram gameplay, áudio ou controles de todos os títulos.

- Referências: [OFF26], [OFF32], [OFF33].

### 4.14 Controles físicos, toque e gaps por família

O Android distingue teclado, mouse, remoto DPAD, dispositivo virtual e fontes GAMEPAD/JOYSTICK. Reconhecer um dispositivo não prova todos os botões, eixos, slots ou modalidades de Bluetooth/USB. A R120 produziu uma auditoria por owner e acrescentou apenas a supressão transitória do touch do Dolphin. Não há adaptação universal no frontend que esconda toda superfície ou que desligue todos os overlays com a mesma chamada. O código dos cores Libretro não controla necessariamente a UI Android do host que os executa.

SNES/Mega EX+ já possuem AUTO em VController e recebem hotplug, mas a condição de presença também inclui teclado; escolhas manuais ON/OFF permanecem. Switch possui estado overlayHiddenByPhysicalController e restauração quando a própria camada o havia ocultado. Vita possui hideOverlayWhenControllerConnected e recuperação depois do último disconnect. O wrapper Xbox clássico inspecionado enumera presença e restaura o touch, embora sua regra não exclua virtual. Esses comportamentos são achados de fonte/rotas, não testes físicos completos nesta leitura.

Flycast possui show/hide e timer, mas hitTest não depende da mesma visibilidade e o delegate pode reabrir; N64 oculta por entrada e timer sem getter que identifique a propriedade da supressão; PPSSPP possui preferência persistente e opacidade por inatividade; MAME registra efetivamente alguns controles pela primeira entrada. PS2 tem divergências entre a superfície decoded e referências upstream. Cemu usa StateFlow para overlay, XenDroid usa opção Compose manual e Saturn usa toque manual sem listener de presença no wrapper lido. Chamar um setter isolado pode ser revertido pelo owner ou interferir no input.

O adaptador Dolphin passou 68 testes isolados com stubs, incluindo dois controles, último disconnect, mil callbacks de layout sem release repetido, pause/destroy e falha de ponte. Esses testes não exercitam JNI real, latência, botão BSP-D3, pareamento, eixos ou gameplay. PS3/PS4 têm detecção própria de presença e máscaras/eixos no owner interno, mas sua resposta física completa permanece uma tarefa de validação. Slots online têm autoridade própria e não podem ser deduzidos do número do InputDevice.

- Referências: [OFF31], [OFF34], [OFF35].

### 4.15 PS3 interno: bootstrap, firmware, jogo e retorno

PS3 usa aPS3e 2.43 em :station_ps3, com mínimo Android 9/API 28 e ARM64 verificados pela ponte. StationSonyComponentFactory preserva a factory delegada e escolhe o dispatcher interno, de modo que a rota atual não depende de instalar ou abrir outro aplicativo. O worker prepara o módulo fixado por manifest, confere arquivos e bibliotecas, vincula as pastas privadas e executa o importador nativo do firmware autorizado presente no pacote local. Um marcador só não basta: sucesso do importador e arquivos reais de flash são condições do sistema preparado.

O launcher Station aceita ISO para a abertura direta e valida URI content/file, extensão e disponibilidade; amostras DEMO e arquivos vazios são rejeitados. Ps3Activity também tem caminho para pasta com executável válido, mas essa capacidade interna não significa que o catálogo Station ofereça importação universal de pastas. ISO usa um descriptor para metadados e outro descriptor novo para playback, com propriedade transferida ao JNI. Quando há criptografia, a chave válida do próprio jogo precisa ser fornecida pela rota que a requer. Título/serial vêm da leitura real do motor, não do nome da capa.

A interface de jogo utiliza SurfaceView, touch próprio e eventos físicos. O worker configura a Surface, executa boot e usa pause/resume quando o ciclo de vida exige; mudança de tamanho é encaminhada ao motor. Perder a Surface libera estados de input e pausa a sessão apropriada. Há confirmação humana para sair da partida e retorno ao frontend. Um pedido novo respeita a instância singleTask e não deve criar uma segunda emulação simultânea por mera preparação.

A R131 corrigida teve instalação/abertura do frontend e telas de preparo PS3/PS4 observadas. PS3 confirmou importação inicial e reuso do firmware; PS4 superou o erro antigo ClassLoader. A evidência qualifica bootstrap e telas, sem leitura independente dos arquivos privados e sem jogo ISO/PKG real iniciado. As configurações posteriores R134 não são fisicamente validadas por uma observação anterior R131. Firmware incluído, JNI carregado, configuração salva e gameplay são estados diferentes.

- Referências: [OFF36], [OFF37], [OFF38].

### 4.16 PS3 R134: inventário completo das opções

A tela PS3 R134 tem categorias Imagem, Áudio, Processamento e Sistema, Voltar persistente e retorno disponível durante a preparação. São dezoito campos nativos, dezesseis editáveis e dois de leitura, mais a preferência de controles de toque. O cabeçalho informa que alterações valem no próximo jogo. Valores são carregados com aenu.emulator.Emulator.Config.openFile/load e gravados por save/closeText no YAML do owner, seguido de publicação atômica; o frontend não cria equivalentes fictícios com chaves próprias.

Renderizador e Compilação de shaders ficam somente para leitura. Os nomes de enum do XML publicado divergem do padrão do binário2.43 e o código não converte esses valores por inferência. Resolução, aspecto, limite de quadros e decodificadores usam a enumeração fixada pelo contrato. Valores numéricos têm faixa explícita. Um valor ausente ou tipo incompatível fica indisponível na UI, em vez de receber um padrão fabricado e ser automaticamente regravado.

A troca de categoria incrementa um epoch e descarta callbacks que pertencem à página anterior, Activity fechada ou saída em curso. O gate de submissão e destroy foi revisado para impedir trabalho posterior ao fechamento do executor. Uma gravação humana já enfileirada termina antes de Voltar completar o retorno. A preferência de toque usa SharedPreferences do owner e continua condicionada à presença do controle físico. A existência do campo e da gravação não prova que um título físico consumiu a alteração ou ganhou desempenho.

A tabela reúne as chaves exatas, opções e intervalos expostos. O limite de quadros PS3, a escala de resolução e número de threads são escolhas do motor; alterá-los pode afetar compatibilidade e qualidade de modo específico ao jogo. Os rótulos em português simplificam a navegação, mas não alteram a semântica das chaves. Nenhum desses campos habilita PS3 online.

| Categoria | Campo nativo / rótulo | Opções / faixa / condição |
| --- | --- | --- |
| Imagem | Video\|Renderer · Renderizador | Somente leitura; divergência enum XML/binário impede conversão inferida. |
| Imagem | Video\|Resolution · Resolução | 1920x1080,1920x1080i,1280x720,720x480,720x480i,720x576,720x576i,1600x1080,1440x1080,1280x1080,960x1080. |
| Imagem | Video\|Resolution Scale · Escala | 25–800%. |
| Imagem | Video\|Aspect ratio · Proporção | 4:3 ou16:9. |
| Imagem | Video\|Frame limit · Limite de quadros | Off,30,50,60,120,Display,Auto,PS3 Native,Infinite. |
| Imagem | Video\|Shader Mode · Compilação de shaders | Somente leitura pelo conflito de enums da fonte publicada. |
| Imagem | Video\|Write Color Buffers | Booleano. |
| Imagem | Video\|Strict Rendering Mode | Booleano. |
| Áudio | Audio\|Master Volume | 0–200%. |
| Áudio | Audio\|Enable Buffering | Booleano. |
| Áudio | Audio\|Enable Time Stretching | Booleano. |
| Processamento | Core\|PPU Decoder | Interpreter(static), Recompiler(LLVM). |
| Processamento | Core\|SPU Decoder | Interpreter(static), Interpreter(dynamic), Recompiler(ASMJIT), Recompiler(LLVM). |
| Processamento | Core\|PPU Threads | 1–8. |
| Processamento | Core\|Preferred SPU Threads | 0–6. |
| Processamento | Core\|Max LLVM Compile Threads | 0–12. |
| Processamento | Core\|LLVM Precompilation | Booleano. |
| Sistema | Miscellaneous\|Show trophy popups | Booleano. |
| Sistema | Controles de toque | Preferência própria; mantém condição de ausência de controle físico. |

- Referências: [OFF39], [OFF40].

### 4.17 PS4 interno: runtime, PKG, vídeo, áudio e input

PS4 usa Bachata S4 0.2.4 em :station_ps4, Activity privada singleTask e mínimo Android 12/API 31 com ARM64. O bootstrap filho carrega apenas namespaces SDL 3/runtime/entrada próprios antes do pai; classes Android e Station permanecem no classloader principal. Bibliotecas e libc++ privadas não substituem as raízes dos outros motores. O módulo derivado contém as declarações JNI conferidas, e o pacote estrangeiro completo com sua UI/Hilt não foi incorporado.

A preparação confere manifest e archive oficiais, caminhos, duplicatas, tamanhos e hashes dos assets; promove uma staging atomicamente e revalida cache no worker. Os arquivos de configuração, HOME/XDG, cache de shaders e sessões pertencem ao armazenamento privado do PS4. Um PKG real passa por probe/extract oficiais, em staging de biblioteca, com validação de eboot.bin e sce_sys/param.sfo antes da promoção. TITLE_ID e título vêm do SFO. Importação inválida ou conteúdo que requer chave própria resulta em erro explícito; DEMO não é importação válida.

Ps4Activity usa TextureView/Surface. O bridge0.2.4 não oferece pausa/rebind: o owner retém a mesma SurfaceTexture ao destacar a View e não inventa uma chamada SDL para pausar. Ao voltar, reaproveita o producer quando previsto. Sair/Back confirmado solicita stop real, neutraliza input e libera transportes/Surface depois do retorno nativo, encerrando somente o processo PS4. Retorno de background ainda exige teste físico; retenção implementada não é garantia de estabilidade.

Input físico/toque usa máscaras PS4, quatro slots, analógicos, hat, gatilhos e deadzones através de AF_UNIX privado e snapshots sequenciados com fila limitada/coalescida. A camada de toque é ocultada quando há controle físico e suas fontes são separadas dos eixos físicos. Perda de foco/desconexão neutraliza o estado. Áudio implementa BACHATA_ALSA_SOCKET com preparação, PCM e fechamento, usando AudioTrack/conversões nos workers e limites de payload. A documentação não qualifica Bluetooth, áudio ou gameplay de PKG real apenas por essa implementação.

- Referências: [OFF41], [OFF42], [OFF43].

### 4.18 PS4 R134: inventário completo e persistência das opções

PS4 R134 divide suas opções em Imagem, Desempenho, Sistema e Áudio. São onze campos nativos, oito editáveis e três para leitura, mais controles de toque. O contrato vem do catálogo runtime-settings/shadps4.json do artefato oficial0.2.4 e do leitor/writer correspondente. O arquivo que o motor consome é ps4/storage/.local/share/shadPS4/config.json, relativo ao armazenamento privado do owner. HOME e XDG são definidos antes de carregar bibliotecas para que a configuração da tela e a execução usem a mesma raiz.

Abrir Configurações não cria o JSON e não regrava padrões. Se uma chave não existe, a UI mostra o padrão documentado para aquele campo; ao editar, apenas a chave escolhida é atualizada. Seções/chaves desconhecidas são preservadas. A leitura e escrita recusam arquivo ou payload maior que 512 KiB, tipos incompatíveis e seção não objeto. AtomicFile preserva o arquivo anterior se a gravação falhar. Nenhum backend de áudio, faixa numérica ou driver é inventado quando o contrato primário não o demonstrou.

Enquadramento e modo de apresentação usam enumeração real; os booleanos permitem canal de cor, HDR, FSR, RCAS, afinidade de núcleos e cache de pipelines. VBlank, idioma e backend de áudio são de leitura porque limites/enumeração ou escrita segura não foram expostos com comprovação suficiente. O controle de toque pertence à preferência do owner, não ao JSON nativo. Valores e chaves estão reunidos na tabela abaixo, sem implicar que todas as combinações funcionam na GPU dos aparelhos.

A fonte definitiva corrige um callback que podia submeter trabalho depois da destruição da tela. settingsActive considera destruição, finishing, leaving e shutdown; o epoch é invalidado antes de encerrar o worker. Voltar marca saída e enfileira finish depois das gravações humanas já solicitadas. A mudança não encerra um jogo nativo em andamento por simples callback de settings. O consumo da configuração pelo jogo, os efeitos físicos e a navegação completa R134 dependem dos recibos de validação específicos.

| Categoria | Chave nativa / rótulo | Opções / padrão documentado / condição |
| --- | --- | --- |
| Imagem | GPU.display_mode · Enquadramento | Fit,Stretch,Crop; padrão Fit. |
| Imagem | GPU.present_rb_swap · Corrigir canais de cor | Booleano; padrão false. |
| Imagem | GPU.hdr_allowed · Permitir HDR | Booleano; padrão false. |
| Imagem | GPU.fsr_enabled · Filtro FSR | Booleano; padrão false. |
| Imagem | GPU.rcas_enabled · Nitidez RCAS | Booleano; padrão true. |
| Imagem | GPU.present_mode · Apresentação | Immediate,Mailbox,Fifo,FifoRelaxed; padrão Mailbox. |
| Desempenho | General.big_core_affinity | Booleano; padrão false. |
| Desempenho | Vulkan.pipeline_cache_enabled | Booleano; padrão false. |
| Desempenho | GPU.vblank_frequency | Somente leitura; padrão documentado60. |
| Sistema | General.console_language | Somente leitura; padrão documentado1. |
| Áudio | Audio.audio_backend | Somente leitura; padrão do motor quando ausente. |
| Sistema | Controles de toque | Preferência própria do owner; não grava chave fictícia no JSON. |

- Referências: [OFF44], [OFF40], [OFF02].

### 4.19 Saves, retorno ao frontend e condição operacional

O TurboStations preserva a assinatura e os dados de uma atualização Android para manter licenças, instalação e armazenamento de jogos. Essa operação de pacote é diferente da opção Apagar jogo. O instalador só conhece seus arquivos de conteúdo pelo recibo; saves e preferências são administrados pelos emuladores. Não há prova nesta leitura de uma camada universal que converta save states entre MAME, EX+, Dolphin, N64, LibretroPlayer, Yuzu, Sony e os demais owners.

Cada família tem seu retorno. N64 possui resultado oficial Gallery/GameActivity e ponte de volta à ESActivity; MAME usa a rota para plataformas e encerra seu processo apenas após ação humana; os owners Sony têm Voltar para configurações e confirmação de saída para jogo. Em processos separados, encerrar a Activity e encerrar o core não são a mesma operação. As fontes preservadas não autorizam apresentar toda saída como identicamente implementada ou fisicamente validada.

PS3 conserva config custom_cfg por serial quando existe; PS4 mantém biblioteca importada e armazenamento interno privado sem mover saves de outros motores. O dispatcher Sony recusa DEMOs e valida o jogo real antes de enviar ao owner. Ao receber pedido novo com uma sessão já aberta, os owners mantêm a sessão atual ou pedem retorno ao catálogo, em vez de iniciar outra emulação simultânea. Controles devem ser neutralizados na pausa/saída conforme a implementação específica para evitar input preso.

A condição de operação para instalar, revisar ou comparar versões é não interromper uma partida/download. O guard da instalação verifica esse estado e o recibo mantém APK integral, UID e data de instalação para conferir continuidade. Este dossiê não inclui ROMs, BIOS, firmware, chaves, tokens, seriais, capturas privadas ou logs pessoais. As referências são código/contratos e recibos agregados; material binário local autorizado continua em seu destino privado.

- Referências: [OFF25], [OFF29], [OFF38], [OFF41], [OFF45].

### 4.20 Pontos ainda abertos na qualificação offline

A abrangência do catálogo é maior que a qualificação física disponível. Os cinquenta comandos auditados e os dois owners Sony descrevem intenção de lançamento; para cada título permanecem relevantes formato aceito pelo binário exato, dependências de conteúdo, integridade, BIOS/firmware, capacidade gráfica, preferências, controles e retorno. Nas oito famílias com dependência ausente na observação histórica, a informação precisa ser atualizada por uma leitura atual dos aparelhos antes de afirmar disponibilidade.

O dossiê não consolida um minSdk e uma whitelist completa de extensões para todas as famílias antigas. Não preencher essas lacunas com requisitos de uma release recente upstream: vários motores têm binários preservados e wrappers com políticas próprias. O inventário registra explicitamente API 28 N64/PS3, API 31 PS4 e proveniência SDK26 do artefato ARMSX2, distinguindo requisito do motor e requisito efetivo do pacote. A matriz é completa quanto às cinquenta linhas auditadas; o detalhamento de compatibilidade não é declarado completo quando a evidência não o permite.

Os testes isolados de filas, geometria, lifecycle, config, ABI e composição verificam riscos específicos. Eles não medem rendimento de GPU, consumo, aquecimento, resposta Bluetooth, áudio contínuo, estabilidade de emulação ou todas as combinações de configuração. Instalar o APK atual em dois aparelhos e observar o frontend acrescenta evidência de instalação/abertura, mas não transforma o pacote em release estável universal nem qualifica quatro jogadores ou todos os motores.

Para uma validação operacional completa de um motor, selecionar um título instalado real, conferir boot, imagem/som, controles físicos e toque, pausa/background quando houver API, retorno e persistência de saves. Para settings Sony, conferir que o arquivo muda somente a chave escolhida e que o motor consome a alteração no próximo lançamento. Para render/menu, medir primeira entrada, mudanças rápidas, contexto recriado, tempo do LED e memória. Qualquer alegação térmica precisa de medição física separada.

- Referências: [OFF02], [OFF03], [OFF31], [OFF40].

## 5 Multiplayer servidor e handoff de ativação

### 5.1 Online: versão efetiva e limites desta leitura

Este capítulo descreve a composição R134, fonte executável 4f9039eb9ce13907ce043870bfe1f6e294888556, APK SHA-256 f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2, 2.714.991.631 bytes. A mudança R134 concentra-se no painel de efeitos e configurações PS3/PS4. A composição conserva os emuladores, cores, controles, opções, autenticação e protocolo online; renova quatro identidades porque o fingerprint incorpora compartilhados do pacote. Um ID da R133 não representa a R134, embora o core continue igual. [ON-01, ON-02]

As fontes online são uma composição explícita: a base Java completa da R124, o overlay N64 R125, o overlay Dolphin R126 e o overlay PSX em integration/psx-online. A receita compile_java.py verifica hashes das fontes congeladas antes de compor as classes. A R134 preserva as classes online; DEX28 só permite StationGraphicsPanel, DEX40 só permite Ps3Activity/Ps4Activity e classes internas. Não escolher uma Activity histórica pela data do arquivo. [ON-03]

Há seis estados a registrar separadamente: código implementado; pacote compilado/assinado/verificado; instalação do APK exato; preparo do kit e dos perfis; aplicação protegida no servidor; partida física validada. O recibo de instalação mais recente e a seção de instalação consolidada deste dossiê prevalecem sobre o installed=false dos documentos de preparação. Nenhuma instalação autoriza inferir autenticação, ativação do servidor, gameplay, controles ou temperatura. Os valores técnicos abaixo não incluem token, licença, chave privada, senha, serial de aparelho ou conteúdo de jogo.


### 5.2 Inventário de endpoints consumidos pelo aplicativo

O contrato Android usa rotas relativas à raiz /v1/station/. O domínio/hostname configurado não concede autoridade por si só: o cliente verifica o envelope assinado e os vínculos esperados. A tabela descreve método, finalidade e condição de consumo. As rotas C# de autenticação/biblioteca e online foram lidas no commit servidor a6b58e9; as duas rotas de mídia estão implementadas no cliente, mas não foram encontradas nessa árvore de servidor examinada. Essa ausência não é diagnóstico de uma requisição de produção, que não foi executada. [ON-04, ON-05, ON-06]

As rotas /ready são telemetria administrativa local. /ready/station/online exige conexão loopback; diagnostics também verifica Host local e rejeita cabeçalhos de encaminhamento. Não usá-las como endpoint público nem como prova de aprovação de um jogo. HTTP 200, PONG, serverReady ou presença de uma biblioteca também não substituem um snapshot multiplayer v3 assinado para o conteúdo e engine atuais.

| Método e rota | Função real | Condição/resultado |
| --- | --- | --- |
| POST /v1/station/activations/challenge | Desafio para ativar acesso por código | Identidade de produto/app/aparelho; resposta activation-challenge/v1; prazo de 60 s |
| POST /v1/station/activations/complete | Concluir ativação assinada pelo aparelho | Mesmo challengeId/nonce/código/chave; resposta activated/v1 |
| POST /v1/station/challenges | Desafio de sessão para licença/aparelho autorizado | Resposta session-challenge/v1; prazo de 60 s |
| POST /v1/station/sessions | Abrir sessão autenticada | Envelope do aparelho; resposta session/v1; validade de 180 s |
| GET /v1/station/me | Nome de exibição/perfil | Bearer+prova quando negociada; profile/v1 |
| GET /v1/station/catalog?metadata=1 | Catálogo assinado e metadados | catalog/v1; cache não cria autorização |
| GET /v1/station/covers/{coverId} | Bytes da capa autorizada | Autenticação e ID válido; MIME/tamanho limitados no cliente |
| POST /v1/station/downloads/authorize | Grant para um item do catálogo | request-download/v1; resposta download-grant/v1 |
| GET /v1/station/artifacts/{grantId} | Consumir grant e transmitir artefato | Mesmo aparelho/licença/sessão; bytes/tamanho/hash do descriptor |
| POST /v1/station/online/command | Presença/social e sala legada | enter/heartbeat/chat privado/bloqueio; envelope online/v1 |
| POST /v1/station/online/events | Eventos/presença por revisão | requestId/instance/revision/page; espera limitada |
| GET /v1/station/online/relay | Relay histórico v1 ou recovery v2 | Upgrade WSS; StationRelay ticket; subprotocolo correto |
| POST /v1/station/online/multiplayer/command | Salas/perfis/controle multiplayer v3 | 12 ações; Bearer+prova; snapshot multiplayerVersion 3 |
| GET /v1/station/online/multiplayer/relay | DATA e barreira v3 por ligação | WSS station-stream.v3; ticket uso único/prova/lease atual |
| GET /v1/station/media/catalog?requestId=... | Contrato cliente de vídeos de menu remotos | media-catalog/v1 assinado; servidor atual não confirmado |
| GET /v1/station/media/files/{sha256} | Contrato cliente de MP4 imutável | Hash/tamanho/MIME e geometria esperados; servidor não confirmado |
| GET /ready/station/online | Métricas agregadas administrativas | Somente loopback; não aprova edição/modo |
| GET /ready/station/online/diagnostics | Diagnóstico recovery administrativo | Host/IP locais, sem forwarding; não público |


### 5.3 Ativação, sessão, assinatura e prova de posse

O produto/applicationId do protocolo é TURBORAMA_STATION_ANDROID. O prefixo dos domínios é TurboRamaStationAndroid/. A ativação começa com schemaVersion 1, domínio request-activation-challenge/v1, deviceId, clientVersion, fabricante/modelo/SDK e activationCode/devicePublicKey. O servidor verifica o acesso e produz desafio assinado contendo challengeId, nonce e capacidades de segurança. A conclusão leva o mesmo desafio, a identidade e a assinatura do aparelho; o servidor confere código, chave e gerações de ativação/revogação. Esses campos são identidades operacionais privadas, e só seus nomes integram este documento. [ON-04]

A sessão usa licença já ativada e deviceId autorizado, challenge de 60 s e envelope open-session/v1. A resposta tem sessionId, accessToken, expiresInSeconds=180, requestProof, verifiedApp e serverTime. O cliente verifica licença, dispositivo, challengeId/nonce, domínio, sessão e prazo antes de usar o token. StationSessions controla leases/renovação; uma aquisição de sessão dentro de outra lease é evitada no discovery multiplayer porque pode bloquear renovação. Sessão expirada ou negada requer renovar/revalidar o acesso; não repetir uma mutação de sala às cegas. [ON-05]

O envelope da autoridade contém keyId, payload e signature. O cliente exige a autoridade pinada e RSA-PSS/SHA-256, MGF1-SHA256 e salt de 32 bytes; a assinatura cobre os bytes do payload, não uma representação JSON reformatada. Após verificar, confere schemaVersion 1, domínio, productId/applicationId, deviceId e, com sessão, licenseId/sessionId. O requestId retornado tem de coincidir com o comando emitido. O domínio externo online/v1 continua correto na API multiplayer: a versão 3 é confirmada também por multiplayerVersion=3 e capability=station-multiplayer.v3. [ON-05]

A prova HTTP usa X-Station-Request-Proof e domínio TurboRamaStationAndroid/request/v1. Canonical: domínio, método, target, SHA-256 do corpo, hash da credencial, timestamp e nonce, cada um separado por LF e com LF final. Header: v1.timestamp.nonce.signature. A janela de timestamp é ±90 s; nonce de 16 bytes Base64URL canônico é registrado somente depois da verificação criptográfica. RSA-PSS exige 2.048 bits / assinatura de 256 bytes; ECDSA exige curva P-256 e DER. Reuso de nonce é recusado; o cache padrão limita 262.144 nonces. A prova não lê ROM nem assina cada quadro de jogo. [ON-07]

A prova protege Bearer nas chamadas HTTP e ticket no upgrade GET WSS. Tickets não devem estar em query string nem logs. Os endpoints v3 proíbem query, verificam o token, reautenticam antes da resposta assinada e revogam a presença se o acesso deixou de valer durante a espera. O relay reautoriza licença/dispositivo periodicamente. Não fabricar chave, PKEXEC_UID, sessão ou resultado de assinatura para contornar uma recusa.


### 5.4 Catálogo, capas, downloads e mídia: autorização distinta de multiplayer

O catálogo assinado apresenta jogos e metadados. O descritor de instalação chega no grant assinado de downloads/authorize. O cache local é dado de apresentação: restoreLocalCatalog verifica assinatura e propriedade da instalação, mas não cria Session nem Grant. Para criar/entrar em sala, o app precisa de classificação v3 fresca, arquivo instalado e identidade exata do conteúdo. Nome, quantidade descritiva de jogadores, capa ou item visível não são permissões de multiplayer. [ON-05, ON-08]

downloads/authorize recebe itemId com identidade request-download/v1. O servidor resolve o artefato atual, sela o vínculo privado com licença/dispositivo/sessão/item/grant e devolve grantId, itemRevision, descriptor e validade de 60 s. artifacts/{grantId} confere Bearer, identidade, revisão/hash/tamanho/caminho protegido e consome o grant antes de transmitir. Não é URL pública de ROM, nem credencial reaproveitável para outro aparelho. No app o grant vale para o descriptor original e o download respeita limite local, staging, cancelamento e confirmação de tamanho, formato e descritor assinado antes da instalação; o SHA integral do corpo da ROM não é calculado nesse fluxo. [ON-04, ON-05]

O cliente limita catálogo a 64 MiB e capa a 5 MiB. Para mídia remota aceita no máximo 128 entradas, JSON de 256 KiB, arquivo de 32 MiB e total de 256 MiB; asset precisa corresponder a turbo-system-videos/720-...mp4, hash SHA-256 válido, video/mp4, 720×720, 30 fps, zero áudio. Não segue URL/caminho fornecido pelo servidor. Vídeos locais continuam no pacote. Essa implementação cliente não demonstra que o servidor de mídia tenha sido publicado. O retorno de capas e o registro de modos online são publicações independentes.


### 5.5 Lobby, presença e funções sociais

A Activity de salas conserva apelido em preferências station-online-profile; o campo admite 24 caracteres e impede entrada vazia. enter confirma presença, heartbeat ocorre a cada20 s, e o contrato legado anuncia expiração60 s. As telas têm Salas/Sua sala, Pessoas, Criar e Conversa. Pessoas mostra disponíveis/em sala, pesquisa local da página, paginação e perfil; as salas mostram capa, título, anfitrião, ocupação e estado. As leituras de eventos/snapshot são canceláveis; polling v3 é único e sequencial. [ON-09, ON-10]

O social legado fornece direct-chat-v1, join-request-v1, short-invite-v1 e own-room-member-profiles-v1 conforme habilitação. Conversa privada usa peerId, chat da sala usa roomId; limite 500 caracteres sem controles/quebras de linha e espaçamento mínimo 1 s. Há rascunho por conversa e aviso de mensagem recebida; o cliente não promete histórico permanente. Servidor mantém até 32 mensagens privadas por participante e até 50 no chat legado; v3 mantém até 32 ou64 KiB na sala. [ON-06]

Bloquear exige confirmação humana. O servidor limita 128 bloqueios, oculta o jogador, remove conversas/convites/pedidos entre envolvidos e encerra a sala compartilhada conforme a autoridade social. O bloqueio aceito é propagado ao hub v3 sob AdmissionGate. A perda de rede não é comando block, leave ou offline; não se deve confundir transporte desconectado com saída autorizada. Não foram encontrados fluxo de denúncia, lista persistente de amigos ou desbloqueio nessa interface atual.

| Operação social/legada | Condição | Disponibilidade no fluxo atual |
| --- | --- | --- |
| enter / heartbeat / offline | Presença por licença+dispositivo; apelido validado | Base social do lobby |
| direct-chat / block | Capacidade social, peer existente, bloqueio/limites | Conversa privada/bloqueio quando aceitos |
| chat | Membro da sala | V3 direciona ao endpoint multiplayer |
| create / join / ready / start / leave | Identidade e estado da sala | V3 direciona ao endpoint multiplayer |
| invite / dismiss-invite | Sala legada aguardando e vaga; convite60 s | Histórico; não oferecido no multiplayer v3 |
| request-join / accept-request / dismiss-request | Capacidade join-request-v1; anfitrião responde | Histórico; recusado no multiplayer v3 |
| resolve-code | Código curto ou locator histórico validado | Histórico; código v3 em preparação |
| host-listening / relay-ticket / resume-relay / recovery-failed | Transporte/geração legados | Contrato v1/v2 histórico |


### 5.6 Convites: evitar confusão entre código histórico e v3

O app contém parser/gerador de código curto de 8 caracteres e locator TS1 legado. No fluxo antigo, o anfitrião copia um código enquanto há vaga; resolve-code obtém locator assinado e o convidado valida instance/room/item antes de preparar arquivos. Convites diretos têm60 s; limites 10 enviados por anfitrião e20 recebidos pelo jogador. Pedidos para jogar têm60 s, até 5 enviados por jogador e20 por sala. Essas funções são reais no contrato social legado, mas não estão liberadas pela modalidade v3 atual. [ON-06, ON-09]

StationOnlineClient.compose remove join-request-v1 e zera roomCapabilities ao apresentar o multiplayer. StationRoomsActivity oculta inviteNavigation quando multiplayerEnabled; invitePlayer orienta conversar e entrar pela lista; showRoomCode recusa recoveryProtocol station-stream.v3. call recusa request-join/accept-request/dismiss-request/invite/dismiss-invite quando a ação pertence à sala v3. A ficha de perfil pode conter ações históricas, mas a guarda funcional prevalece. O sucessor deve preservar essa distinção na UI e no handoff, sem anunciar convites v3 com base em R63/R41. [ON-09, ON-10]


### 5.7 Schema e operações do comando multiplayer v3

StationMultiplayerCommand é JSON estrito com action/requestId; campos opcionais roomId,itemId,contentSha256,engineId,coreSha256,runtimeSha256,profileId,profileSha256,capacity,generation,linkId,value,nickname,text,clientMaximumPlayers,page,roomPageSize. Propriedades duplicadas são recusadas; profundidade máxima 16 e corpo máximo 8.192 bytes. O timeout do endpoint é 15 s. O cliente anuncia clientMaximumPlayers=5, página da sala e roomPageSize=32; o servidor admite capacidade de cliente 2..5, página 0..40 e tamanho 32 ou 100. [ON-11]

São12 ações aceitas, listadas abaixo. UUID formato D é obrigatório; reuso do requestId só é idempotente quando o fingerprint do comando é idêntico. Mudança do corpo com mesmo ID retorna REQUEST_REUSED. O servidor conserva 64 recibos por participante e limita20 ações por segundo. Uma mutação é enviada uma vez; backoff automático fica restrito às leituras. create/join não podem coexistir com membership legado; o gate compartilhado impede dupla admissão. [ON-12]

O snapshot contém schemaVersion 1, multiplayerVersion 3, capability,selfId, instance, revision, serverTimeMs, status, profiles, profileCount, classification, platformPolicy, serverPlatforms, paginação, totalRooms, rooms, room, ticket. Os profiles retornados são filtrados por item e capacidade do cliente, até 32 por item. platformPolicy apresenta teto, topology host-star, trusted-manifest, profileReloadWithoutRestart e availability; esses indicadores não substituem approved e identidade exata. [ON-12]

| Ação | Campos/efeito | Guardas principais |
| --- | --- | --- |
| capabilities / snapshot | Consulta perfis/capacidade/salas | Sessão e resposta assinadas; não cria autorização implícita |
| heartbeat | Renova presença multiplayer | Identidade atual |
| create | Identidade completa + capacity | Perfil approved/catálogo/hash; sem sala; limite 100 salas |
| join | roomId + generation + identidade | Vaga, esperando, sem bloqueio; perfil igual; sem sala |
| ready | roomId/generation/value | Membro, sem partida; perfil continua válido |
| start | roomId/generation | Só anfitrião; todos prontos; quantidade permitida |
| leave | roomId/generation | Saída humana/membro; host ou partida encerra sala |
| chat | roomId/generation/text | Membro;500 caracteres; mínimo 1 s |
| ticket | roomId/generation/linkId + identidade | Partida iniciada; prova; ligação própria; sem attachment |
| resume | Mesmo vínculo do ticket para recuperação | Estado recuperável e membership atual |
| failed | roomId/generation | Partida iniciada; marca stream irrecuperável |


### 5.8 Perfis aprovados, canonical e posições

StationMultiplayerProfile vincula itemId, contentSha256, platform, engineId, coreSha256, runtimeSha256, profileId, profileSha256, maximumPlayers, approved, controllerProfile, mode, allowedPlayerCounts e opcionais modeTitle/instructions/sources. A chave administrativa inclui todos os hashes/IDs: uma aprovação de outro core, edição, runtime ou owner não serve. approved deve ser true; as contagens precisam ser distintas, crescentes e incluir maximumPlayers quando este é ≥2. Perfil single-player usa maximumPlayers=1 e allowedPlayerCounts vazio, apresentando classificação sem criar sala. [ON-08, ON-12]

O servidor valida até 50.000 perfis e até 32 por item, sources HTTPS sem userinfo, até 8 fontes/instruções, títulos de 80 caracteres, instruções de 500 e fontes de 512. A política de plataforma é outro limite, aplicado tanto na carga quanto na admissão. O cadastro exige objetos/controller configuration; o array de nomes controllerProfiles do asset Android não é um registro administrativo equivalente. [ON-12]

Canonical do perfil é UTF-8 compacto, ordem exata schemaVersion/controllerProfile/devices/coreOptions, sem BOM nem LF final depois do JSON. coreOptions é string com sua própria ordem e LF final preservados. profileSha256 é SHA-256 desses bytes. O app recomputa o hash e exige correspondência; inserir espaço, normalizar escape/LF ou trocar opções pode invalidar o perfil. standard-2p-v1 usa devices=[1,1], direct-four-ports-v1 usa devices=[1,1,1,1]; Dolphin tem nomes próprios de quatro portas. [ON-08, ON-13]

O roster tem peerId,nickname,slot,ready. Host é slot1; convidados recebem posições2..5 conforme capacidade. Uma mudança pré-jogo recompõe posições e desmarca prontidão, incrementando generation; start incrementa novamente e congela links. Cada participante controla somente seu slot autenticado. O mask Java usa bit(slot−1); Dolphin nativo usa bits1..4 e recebe conversão <<1. Quatro entradas no driver não são aprovação de um modo de quatro pessoas. PSX current owner aceita somente duas portas humanas Standard.


### 5.9 Identidades técnicas finais R134

A tabela fixa o par exato core/runtime dos quatro motores renovados. O core é a implementação emulada; runtime é a adaptação/fingerprint ligado à composição do pacote. GameCube/Wii compartilham biblioteca e runtime, mas têm engineId e controllerProfile próprios. O kit privado inclui seis bibliotecas únicas: PCSX core+runtime PSX, core+runtime N64, core+runtime Dolphin. Há 20 dependências conferidas no manifesto. Não substituir runtime marker por uma biblioteca histórica ou usar o ID R133 no APK R134. [ON-02, ON-13]

Todos os quatro têm launchReady=true e recoveryProtocol=station-stream.v3 no asset local. Isso significa que o seletor cliente tem rota preparada, não que o servidor a aceite. O status implementado continua peer-gameplay-pending. O hash original do recibo de identidade R134 é 2d6fc1c1933b4dc88aa09192138b8564b5f0b743461faa7580896b8339b2067f; source-freeze 7b9eead9ecd79d1582647b1b41d45158a36627ba6b8231663a3fa87067a97af0. As cópias públicas sanitizadas permitem auditoria, não implantação.

| Plataforma / backend / perfil | Engine ID R134 | Core SHA-256 | Runtime SHA-256 |
| --- | --- | --- | --- |
| PSX / psx-player-station-v1 / standard-2p-v1 | pcsx-rearmed-ff81ed17-player-v3-69ac2b703f03 | e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9 | 69ac2b703f03826c8f7203b296665c6f2cc34cb944af7c3f758d9033116cade3 |
| N64 / mupen64plus-ae-station-v1 / direct-four-ports-v1 | mupen64plus-ae-33bf7021-n64-v3-5f56099c433f | fe6e810a1c7fc50a494b50b1dccf581b84385667191c0cbcd235d585a0703dd8 | 5f56099c433f29514c864d1eeea2995e3f52b0d15d76eaf125c4f4346a9d6e87 |
| GameCube / dolphin-station-v1 / dolphin-gamecube-four-ports-v1 | dolphin-5102a033-gamecube-v3-9c87e2ec4c79 | f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d | 9c87e2ec4c798ab1f42130326855d0171617501ee513dfefa74241b3665e38ad |
| Wii / dolphin-station-v1 / dolphin-wii-remotes-four-v1 | dolphin-5102a033-wii-v3-9c87e2ec4c79 | f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d | 9c87e2ec4c798ab1f42130326855d0171617501ee513dfefa74241b3665e38ad |

| Plataforma | Bibliotecas principais / extensões | Teto e política |
| --- | --- | --- |
| PSX | libpcsx_rearmed_libretro_android.so + libstation_psx_online.so; pbp,chd,cue | 2; HLE por edição; CUE=cue-set-v1 |
| N64 | libstation_mupen64plus_core.so + libstation_mupen64plus_runtime.so; z64,n64,v64,rom | 4; modo exato; launch-file-v1 |
| GameCube | libstation_dolphin_online.so + libstation_dolphin_runtime.so; iso,gcm,gcz,ciso,wia,rvz | 4; GameINI/opções sincronizados |
| Wii | Mesmas bibliotecas Dolphin; iso,gcz,ciso,wbfs,wia,rvz | 4; Wiimotes emulados; acessórios por perfil |


### 5.10 Preparo local, criação, entrada e arranque

Antes de criar/entrar, StationOnlineGame consulta classificação fresca por item, lê engine local launchReady/v3 e confere perfil/canonical. O jogo deve estar instalado e pertencer ao catálogo carregado; symlink ou arquivo ausente é recusado. Hash de conteúdo precisa coincidir com o aprovado; bibliotecas locais são conferidas por SHA. Para PSX CUE a identidade inclui todos os tracks no conjunto; CHD/PBP e demais rotas usam arquivo de lançamento. A confirmação da sala é revalidada depois da resposta. [ON-08]

Ao criar, o usuário vê modos e contagens permitidos, resumo/instruções e volta antes da confirmação. O client revalida setupContext para impedir confirmar escolhas de uma sala/edição que mudou. Ao entrar em outra sala, trata a saída anterior de forma explícita, prepara a edição correta e exige room/generation e membership reconhecidos. Não se escolhe o primeiro profile de uma lista ambígua. A regra de ocultar two-player genérico quando há modos documentados evita que descrição antiga substitua uma escolha específica. [ON-09]

Iniciar usa StationRoomStartState: anfitrião, todos prontos, contagem aprovada, roomConfirmationKey e transporte anunciado. O worker revalida as condições novamente antes de mandar start. A resposta contém links host-star e generation atual; host obtém ticket de cada link, convidado somente do próprio. Ticket e sala precisam ter identidade/geração concordantes. O descriptor privado de lançamento é preparado para Mupen/Dolphin/PSX/RetroArch conforme backend e consumido uma vez. O app recusa N64/Dolphin históricos quando a rota não corresponde ao emulador normal integrado. [ON-09]

Abertura da Activity não é prova de gameplay: ainda existem bootstrap do owner, registro dos slots, estado inicial, pausa real e barreira global. Diretórios/saves online são novos por sessão; não reaproveitar saves normais ou prefs offline como opções silenciosas. Revalidar em sala nova com APK exato em todos os participantes após alteração de engine, em vez de tentar reciclar sala congelada de outra revisão.


### 5.11 WSS v3, tickets e formato externo TSR3

A topologia é estrela: cada convidado tem um link autenticado com o host, dois attachments e duas janelas FIFO independentes. Não existe rota convidado↔convidado. GET multiplayer/relay exige upgrade WebSocket, station-stream.v3, nenhuma query e Authorization StationRelay seguido do ticket canônico de 32 bytes. O ticket dura 60 s, tem path/protocol/linkId/ownerSlot/hostSide/windowBytes/epoch e é consumido ao criar attachment. Não é grant de download. Lease associa identidade, room/generation/link/slot/prova; qualquer alteração invalida o uso. [ON-11, ON-12, ON-14]

TSR3 preserva o formato de recovery v2 com magic distinto. Header24 bytes: magic TSR3 nos bytes 0..3, type no byte 4, zeros reservados nos bytes 5..7, offset int64 big-endian nos bytes 8..15, value int64 big-endian nos bytes 16..23. DATA carrega1..16.384 bytes e value0; controles têm só header. Offset/value são não negativos e o parser impede overflow. O relay não interpreta SN64,DPL1,PXL1: esses protocolos internos são bytes opacos no DATA. [ON-14]

Cada direção retém 256 KiB de replay; limite global padrão 32 MiB compartilhado com recovery, configurável entre 512 KiB e 128 MiB. start reserva númeroLinks×2×256 KiB; falta de orçamento retorna REPLAY_FULL antes de iniciar. A janela guarda bytes até confirmação de consumo pelo destino, não até o envio WSS. Replays antigos idênticos não entregam input duas vezes; sobreposição parcial, bytes divergentes, salto de offset ou janela cheia são recusados. O consumidor nativo precisa confirmar cópia/consumo real antes de ACK externo. [ON-14]

| Tipo TSR3 | Código | Semântica |
| --- | --- | --- |
| HELLO | 1 | Primeiro frame; posições locais de aceito/entregue para replay |
| WELCOME | 2 | Primeira confirmação de watermarks |
| DATA | 3 | Bytes internos opacos com offset |
| ACK | 4 | Destino confirma consumo; value0 |
| ACCEPTED | 5 | Servidor informa accepted/delivered |
| STATE | 6 | Epoch e estado global; não é snapshot de core |
| PAUSED | 7 | Participante confirma pausa real no epoch |
| READY | 8 | Pausa confirmada+watermark exato+filas drenadas |
| PING / PONG | 9 / 10 | Saúde do transporte; não prova core rodando |
| SUSPEND | 11 | Lifecycle/foco solicita pausa global |
| FOREGROUND | 12 | Retira suspensão do participante |
| NEED_SYNC | 13 | Solicita novo epoch quando necessário |


### 5.12 Pausa, recuperação e falhas: barreira global

TSR3 inicia em epoch 1 e estado Waiting=0. Depois que todas as conexões apresentam HELLO e PAUSED do epoch atual, sem participantes suspensos, passa a Synchronizing=1; somente todas as confirmações READY e todas as janelas com Pending=0 permitem Playing=2. Unrecoverable=3 é terminal para aquela execução. Desconexão incrementa epoch e revoga Paused/Ready. Novos bytes aceitos invalidam readiness apenas do link afetado; replay duplicado sem avanço não fabrica nova invalidação. Estado de core, IO enfileirado e contador de bytes são evidências diferentes. [ON-14]

No app, pausa significa que a thread real do owner/CPU está parada em ponto autorizado, sem avançar um quadro para drenar. O serial local aumenta para cada controle aceito, inclusive mudanças no mesmo epoch. Resume exige epoch e serial mais recentes, autorização global assinada, estado inicial aplicado e filas locais/servidor drenadas. Uma pausa mais nova bloqueia resume antigo. DATA de preparação/estado continua transitando durante a pausa para evitar ciclo READY/EXECUTE. Não liberar a barreira por rendererReady, PONG ou retorno positivo de enqueue. [ON-15, ON-16]

O relay verifica membership e autorização a cada 10 s. PresenceAge ≥ 60 s ou 30 s sem frame recebido fecha o attachment. Autorização indisponível encerra o transporte, e revogação explícita revoga a identidade/sala. Fechar attachment por timeout não é saída humana do emulador: o cliente pausa e mostra recuperação/falha. O writer de WebSocket é único e é aguardado antes de close output. O handshake de fechamento tem 2 s, sem interpretar isso como timeout de gameplay. [ON-14]

No polling somente leitura, falhas transitórias usam 1/2/4/8 s de backoff; Retry-After pode aumentar o intervalo até 60 s. HTTP 401/403, assinatura/vínculo inválido e serviço desabilitado são terminais para essa tentativa. Ações create/join/start/leave não são reexecutadas automaticamente. NativeFail ou protocolo irrecuperável mantém explicação e saída pelo menu. Não há promessa de rollback, restauração silenciosa ou reconstrução do core no meio da sessão. [ON-10]


### 5.13 Nintendo 64: Mupen64Plus AE e SN64/1

N64 online abre GameActivity/CoreService reais do Mupen64Plus AE, com renderer, áudio, menu e controles desse emulador. O core variante Station deriva do upstream 33bf7021549d7873e976884370fbd1a8e7333bc7; biblioteca normal e plugins continuam preservados. Não abre StationRetroActivity. GameActivity/CoreService continuam no processo :n64core. A preparação ocorre fora da UI e assets ausentes de instalação nova são preparados antes de abrir o owner. [ON-15]

Opções fixadas: backend=mupen64plus-ae-station-v1; wire=SN64/1; cpu=cached-interpreter; video=glide64mk2; rsp=hle; rawInput=false; expansionPak=true; countPerOp/countPerOpDen/forceAlignmentOfPiDma=0; randomizeInterrupt=false; inputDelay=2; rollback=false; saves=session-only. O interpretador sincronizável não demonstra desempenho equivalente ao modo normal. As quatro portas disponíveis só são usadas se edição, modo e allowedPlayerCounts autorizarem. [ON-13]

SN64 começa com magic SN64 de 4 bytes e versão 1. Cada frame tem kind 1=TCP ou 2=UDP, tamanho uint16 big-endian e payload. TCP admite 1..16.384 bytes, UDP 1..512 bytes; fila de entrada de 256 KiB produz backpressure. O protocolo interno não aceita ticket, role ou epoch como autoridade: esses vínculos vêm da sessão Station. Não precisa abrir UDP público, pois o TCP/UDP nativo é transportado pelo DATA WSS autenticado. EOF cancela leitura e não gera loop de tentativas. [ON-15]

Cada telefone conserva o gamepad local na porta P1; o transporte associa esse input ao slot de sala. O anfitrião oferece configurações e saves temporários. Nomes de save UTF-8 são limitados e rejeitam separadores, controles, vazio, ponto e ponto-ponto. Preferências, cheats e saves da sessão são isolados. O registro inicial MEMORY=2/raw=0 cobre a fase anterior à anexação do input plugin. Pausa requer confirmação da thread de emulação; perda WSS conserva pausa e solicita reconexão. As 282 verificações JVM e 134 C citadas são testes isolados históricos, não gameplay atual.


### 5.14 GameCube/Wii: Dolphin real e DPL1

Dolphin online usa upstream 2609-7 / 5102a0339c2177575378107b76541e47cc52122d, libstation_dolphin_online.so e quatro hooks próprios. Seleciona a biblioteca antes de DolphinApplication iniciar no processo exclusivo :dolphin; owner normal continua original em lançamento normal. A sessão oficial NetplaySession, GameFile, BootSessionData e EmulationActivity são reutilizados. O host inicia conexão local antes de convidados para preservar PID nativo 1. O boot só ocorre com roster/controller mapping exatos, jogo nos clientes oficiais e autorização da barreira. [ON-16]

As opções de CurrentRun não gravam preferências offline: direct/loopback, UPnP/index/QoS=false, chunkedUploadLimit=false, fixeddelay, padBuffer=5, clientBuffer=1, saveLoad/saveWrite=true, syncAllWii=false, syncCodes/cheats/recordInputs=false, strictSettingsSync=true, golfMode/remoteGbas=false, saves=session-only. settingsPolicy=official-pinned-gameini+host-synchronized-strict-v1: GameINI pinado e serialização oficial sincronizam Core/GFX/SYSCONF. Isso não significa que toda preferência do host recebeu um valor fixo. [ON-13, ON-16]

DPL1 tem 8 bytes de header: magic de 4 bytes, source slot de 1 byte, target slot de 1 byte, payload size uint16 big-endian; depois datagrama ENet UDP de 1..1.392 bytes. Só host↔guest; wrappers preservam fronteiras e simulam endereço loopback. nativeDeliver=1 é cópia validada/enfileirada, não ACK Station. nativeAwaitDelivery do mesmo uniqueId confirma cópia completa na recepção ENet real; só então cabe ACK do offset externo. Filas por link/endpoint são limitadas a 256 KiB e a deduplicação é preservada. [ON-16]

GameCube exige quatro entradas de porta; Wii exige quatro remotes emulados, cada entrada com slot autenticado ou zero. DesiredWiimoteState oficial transporta acessórios Nunchuk/Classic/MotionPlus configurados, sem liberar Wiimotes reais ou GBA remoto. Four Swords Adventures depende de gamecube-gba-link-v1 ausente; Galaxy 1/2 precisam de papel/input co-star não implementado. NativeSuspendTransport congela relógio ENet e pede break, mas pause ACK requer PauseAndLock/CPU idle. Reset real ENet é falha permanente. Somente nativeAuthorizeHumanExit permite teardown; loss/Stop/Disable/Core::Stop automáticos mantêm suspensão.


### 5.15 PlayStation: owner normal, PXL1 e HLE por edição

PSX reutiliza libmain.so / LibretroPlayer original e libpcsx_rearmed_libretro_android.so normal, no processo :station_psx_online, por adaptador ABI pinado. O owner não foi reconstruído de fonte C++ recuperada: o ELF original é conferido por hash/segmentos e o opt-in só atua no processo privado. SDL, renderer, input e áudio pertencem ao Player; não há segundo retro_run em thread de rede. A entrada estática recebe core/ROM absolutos, HOME privado, fonte original conferida por hash e autoriza após descriptor/Binder. [ON-17]

A política combina 59 defaults compilados conferidos com 7 overrides: HLE; analog combo, multitap, frameskip e threads auxiliares DRC/GPU/SPU desabilitados. DRC compilado permanece no seu default. Options incluem ownerSha256=62ad07ba... / coreSha256=e7534aa6... / compiledDefaultsSha256=bcbb221e..., compiled-defaults+explicit-overrides-v1, standard-two-ports-v1, host-authoritative-lockstep-v1, atraso de 4 quadros, owner-thread-snapshot-v1, saves=session-only-fresh e humanExitOnly=true. Aprovação de BIOS real ou perfil PSX RetroArch antigo não migra para HLE atual. Os hashes integrais estão no recibo de identidade, e os de owner/core constam da tabela. [ON-13, ON-17]

PXL1 transporta pacote de até 1.400 bytes, payload de até 1.392 bytes e janela de 256 KiB. Header: magic PXL1, origem/destino autenticados 1/2, tamanho uint16; payload tem kind/versão/protocolo, epoch, stateSerial, frame e corpo. Kinds: Input=1, Frame=2, StateBegin=3, StateChunk=4, StateEnd=5, RequestState=6, Commit=7. MaxState=16 MiB deve coincidir com serializeSize real; FrameWindow=32, ReceiptWindow=512, StandardPadBits=0x3fff. O hash de estado/identidade e o tamanho exatos são verificados antes de o decoder original aplicar o estado. [ON-17]

O owner amostra quadro N para N+4; host reúne slots e define o quadro canônico. ownerComplete só emite compromisso de execução depois de retro_run retornar. copied(uniqueId) é receipt de transporte e permite drenar STATE durante CPU pausada; takeCommit distingue Executed/Superseded/AppliedState/OwnerFailed. IO nunca executa core/aplica snapshot. nativeStatus retorna 20 long com coreReady, failed, pausa/autorização, epoch/serial/frame/state e condições de ACK/state/drained. RendererReady não é CoreReady e nenhum deles sozinho é READY global. [ON-17]

Back/Menu/Guide abrem confirmação. O positivo humano permite encerramento, aguarda transporte/Binder e a Thread SDL real TERMINATED, devolve RESULT e retira somente o processo privado. Null em mSDLThread não prova término; join ocorre em worker. Só as strings Player1Controller/Player2Controller e bool LibretroStretch validados são copiadas para HOME privado. Não copiar saves, BIOS ou opções offline. Todos os 84 PSX atuais continuam HLE por edição pendente, com zero novos aprovados: instalar o owner ou testar ABI não resolve a política de cada jogo.


### 5.16 Rotas históricas e tetos efetivos

A migração universal dos emuladores normais não foi concluída. SNES continua bsnes/runtime RetroArch no online, embora o normal seja Snes9x EX+; Mega Drive continua clownmdemu/runtime RetroArch, com normal MD.emu; CPS/Neo Geo/FBNeo usam FBNeo online; Neo Geo CD usa NeoCD. Essas rotas foram preservadas, inclusive controles e registros compatíveis. N64/Dolphin/PSX são as quatro identidades renovadas, não prova de que PS2, PSP, Switch, Dreamcast, Saturn ou Wii U tenham adaptador Station. [ON-18]

A política servidor lista 17 plataformas capazes de receber dados de cadastro, mas serverReady da plataforma não significa engine/perfil cliente disponível. Teto SNES=5; N64/Dreamcast/GameCube/Wii/Wii U=4; demais=2. Dreamcast/PS2/PSP/Saturn/Sega 32X/Switch/Wii U têm 337 itens sem engine online atual na matriz. PS3/PS4 permanecem exclusivamente offline. Foto de PSP ou anúncio textual de portas não cria rota. A normalização BR une a família, mas conteúdo/edição permanece vinculado ao hash específico. [ON-12, ON-18]

Existem casos de profile megadrive-sega-teamplayer-v1 e megadrive-ea-4way-v1 no código, com devices/opções próprias. Ainda assim a política efetiva de plataforma consultada limita Mega Drive a 2. Não anunciar 4 com base só no case do perfil. snes-multitap-port2-v1 usa [1,257,1,1,1] e pode admitir 5 apenas no modo permitido. Compartilhar um controle por turnos também não comprova duas entradas independentes.


### 5.17 Ledger R134: cobertura, modos preparados e recusas

A auditoria atual confronta 3.940 registros de catálogo 33: 3.685 visíveis / 255 aliases. Mantém 5.176 perfis e 321 modos históricos como baseline, com 78 novos modos/perfis preparados em 44 jogos/edições e identidade R134 final. A preparação usa reviewed-decisions original e validadores oficiais, não regex de título ou teto do console. operatorApplied=false, currentProductionAuthenticatedSnapshotCaptured=false e physicalGameplayValidated=false referem-se ao preparo; devem ser atualizados apenas com provas reais posteriores. [ON-01, ON-19]

Distribuição: N64 66 modos / 33 jogos, GameCube 9/8, Wii 3/3, PSX 0/0. Restam 110 N64 com propostas genéricas de teste, 14 bloqueios documentais/periféricos, 17 jogos individuais documentados, 337 itens sem engine e 84 PSX HLE pendentes. A matriz soma 2.996 registros baseline-current-engine-profile-compatible, 77 classificações individuais de baseline, 6 sem vínculo de modo atual e os demais estados específicos. Compatibilidade documental não é snapshot de produção nem ensaio físico. [ON-19]

Bloqueios nativos concretos incluem Banjo-Tooie japonês por minigame/contagem; Mythologies/Pilotwings pela página de modo/manual; Stadium japonês sem equivalência à edição ocidental; Smash Remix por revisão específica do mod; Turok 2/3 por páginas ilegíveis; Code Veronica X DUB / Disc 1 e 2 por edição GameCube não revista; Terminator 3 por contagem co-op não extraída; Four Swords por link GBA ausente; Epic Mickey 2 por modo/controller; Galaxy 1/2 por co-star. PSX tem 10 achados primários de 26 históricos multiplayer, mas isso não preenche biosPolicy=HLE-per-game-approved e reviewEvidence real. Preservar recusas.

| Escopo R134 | Quantidade | Estado |
| --- | --- | --- |
| Catálogo integral | 3.940 (3.685 visíveis + 255 aliases) | Auditado; não universalmente aprovado |
| Perfis / modos históricos | 5.176 / 321 | Preservados |
| N64 preparados | 33 jogos / 66 modos | Vínculo R134 pronto localmente |
| GameCube preparados | 8 jogos / 9 modos | Vínculo R134 pronto localmente |
| Wii preparados | 3 jogos / 3 modos | Vínculo R134 pronto localmente |
| PSX novos | 0 jogos / 0 modos | 84 edições HLE pendentes |
| Nativos documentais bloqueados | 14 entradas | Sem remover validação |
| Sem engine online cliente | 337 entradas | Sem fallback aprovado |
| Snapshot v3 fresco / operador aplicado | Não capturados no preparo | Prova independente necessária |


### 5.18 GitHub e estado real do servidor

O repositório de serviço é luziellacerda/Servidor-pix. O ref feat/station-r128-aplicado-20261011 foi novamente consultado nesta leitura e permaneceu a6b58e9beb12eb564c1b58d9d4c32ed3e7513861. r128-retorno-servidor-20261011.json ainda revisa fonte R129 cf623c7 e APK 89dd...: privateKitReceived=false, newFinalEnginesActivated=false, scriptsEffectivePublicationConfirmed=false, nativeAdministrativeAuthenticationRequired=true. Os 68 métodos Linux passaram no preparo administrativo; não é ativação. [ON-20]

A entrega do app R133 está publicada em docs/station-r133-final-console-modes-20261011, commit 524d2ebff08353fda62aacbc5f05f9248ba69b7c. DELIVERY.json identifica R133 e serverActivated=false, privateArtifactsPublished=false; parent é a6b58e9. Essa branch é publicação documental do produtor, não retorno de aplicação do servidor. O handoff R134 local pede continuar a mesma branch, substituindo somente identidades/hashes e mantendo contrato e recusas. Não criar outro contrato por nome de revisão. A publicação R134 e os resultados atuais devem ser comprovados pelo responsável, sem inferir de arquivos locais/untracked. [ON-01, ON-21]

O retorno descreve 2.255 vínculos de capas preparados / 2.150 imagens distintas, 278 não resolvidos e covers.published=false. latestProductionBindings lista Mega Drive=331, SNES=671, PSX=28; há 157 N64 no batch preparado. Isso não prova ausência de toda capa local: uma capa N64 foi vista na R132. Preserve capa correta/ambígua e exija revisão/hash/contagens efetivamente publicadas. Captura de capa não autoriza jogo online. A recusa física R132 em Criar sala ocorreu antes de sala/jogo, sem HTTP/envelope bruto: não usar como diagnóstico de produção R134.


### 5.19 Kit privado R134 e recibos públicos

O kit atual preparado está em G:/StationNormalOwnersR127/settings-refinement-r134/server-kit, server-kit-original-receipts e server-kit-tools. server-kit contém seis bibliotecas e três JSONs técnicos; originais conservam runtime/package/source-freeze/engines/profile; tools conserva extratores/geradores pinados. Manifesto público indexa 16 arquivos; modos, 22 inputs/outputs. O recibo privado de preparo do kit tem SHA b46b64a1aac139974eef764ba92b3039545fdee24d81a969dd198403f0c15d1f; modos, d5ca95395a41b28deae5402e6fa200e916184685de869018cbc5612bc4a21b98. [ON-01]

O backup único resolve os inputs em desenvolvimento/reconstrucao-atual/settings-refinement-r134/inputs via INPUT-MAP-R134.json, com originalPath/role → backupRelativePath. Não presumir G: no Linux nem montar folha flat pela aparência dos nomes. Transferir privadamente os originais finais; públicos sanitizados são auditoria e não o par de implantação. Não transmitir APK, ROM, firmware, BIOS, RSA, saves, licenças, sessões, capturas ou logs pessoais. Bibliotecas técnicas do kit exigem o canal autorizado; disponibilidade local não prova recebimento servidor. [ON-01]

Ledger reviewed-decisions SHA 1cde1bfb3e591108263abb3c0bf4d15bd91e22c9f9ffbb4ade41abad8c59aa8b permanece; mode-additions R134 SHA 945ae692f2bbddc40e791cd9cf18a783ac53d142373893b850536715b6622065; prepared-new-profiles SHA de650a99245468beb39f7138f2a602c090196167dc6803bd85e3dd0793230a8f; official-merge-receipt SHA 86fe321c43946be5eb6851c4257f7c916a6f2b67211416a882d7e58e1c05ea66. Esses hashes permitem conferir integridade, mas a prévia não deve sobrescrever perfil ativo. O operador precisa reexecutar contra baseline ativo atual.


### 5.20 Procedimento administrativo protegido para o próximo operador

Esta receita é documental e não foi executada nesta leitura. Antes da preparação, resolver CONFIG ativo, OUTPUT, CATALOG=outputDirectory/index.json, PROFILES=autoOnlineProfiles.registry, ENGINES=autoOnlineProfiles.engineManifest, MODES=autoOnlineProfiles.preparedModes. Os quatro registros protegidos ficam diretamente no mesmo outputDirectory. SERVER_OPERATOR/PROFILES_MODULE devem apontar aos módulos ativos realmente importados; conferir hash/caminho/module.__file__. Não adivinhar diretório Linux ou alterar permissão para permitir escrita. [ON-01]

Com DELIVERY original, ARTIFACTS recebido, TOOLS fixado e PREPARATION fora dos registros ativos, executar build_incoming_manifest.py --runtime-receipt DELIVERY/runtime-final.json --package-receipt DELIVERY/package-final.json --output PREPARATION/incoming-engine-manifest.json --profile-receipt PREPARATION/profile-canonical-receipt.json. requireExplicitEngineModes:true restringe os quatro IDs a modos revisados. O gerador confere par final/canonical, não um snapshot.engines v2. Os placeholders são caminhos reais resolvidos, não literais a executar. [ON-01]

Depois, merge_scoped_modes.py --catalog CATALOG --profiles PROFILES --modes MODES --runtime-receipt DELIVERY/runtime-final.json --profiles-module PROFILES_MODULE --decisions REVIEW_LEDGER --output PREPARATION/prepared-modes-merged.json --audit-json PREPARATION/scoped-mode-audit.json. Helper chama validate_modes/prepare reais; prepare chama validate_manifest e revalida portas/configuração. Preserve 5.176 perfis, 321 modos, engines anteriores e recusas; se baseline mudou, usar o novo e registrar diferença. PSX é excluído de migração automática sem HLE por edição. [ON-01]

Selar candidata absoluta ainda inexistente: SERVER_OPERATOR prepare --catalog CATALOG --profiles PROFILES --current ENGINES --modes MODES --mode-additions PREPARATION/prepared-modes-merged.json --incoming PREPARATION/incoming-engine-manifest.json --artifacts ARTIFACTS --output CANDIDATE. --modes é o ativo original; merge entra somente em --mode-additions. A candidata conserva selos/incoming/engines/profiles/modes e confere bytes reais. Não substituir candidata por JSON editado manualmente. [ON-01]

Aplicar somente com operador humano/autenticação Linux nativa: pkexec python3 -B SERVER_OPERATOR apply --config CONFIG --candidate CANDIDATE. A guarda exige geteuid()==0 e PKEXEC_UID original do operador esperado. Sob scan.lock revalida baselines, selos, binários e publica modos → engines → perfis. Falha restaura os três arquivos byte a byte; baseline alterado interrompe. Alternativa integrada install usa --config --incoming --artifacts --mode-additions --output sob mesma autenticação. Escolher uma rota e não aplicar duas vezes. [ON-01]

StationMultiplayerProfileMonitor verifica a cada 10 s, lê arquivo regular absoluto até 16 MiB, chama ReplaceProfiles e retém último registro válido se falhar. Salas existentes conservam perfil, links e janelas congelados. Hotreload de dados não publica script Python: scanner oneshot importa módulos por execução. Se código ativo divergir, operador coordena timer existente/execução, confere Type/ExecStart/import/hash no processo novo. Não há necessidade demonstrada de reiniciar API por cadastro; nenhum serviço foi operado neste handoff. [ON-22]

Após aplicação, comprovar enter autenticado e capabilities/snapshot em multiplayer/command com UUID novo e identidade R134. Verificar assinatura e licença/dispositivo/sessão/requestId privadamente, capability v3, instance/revision, item/content/engine/core/runtime/profile/canonical/controller/mode/allowedPlayerCounts. Guardar recibo agregado sanitizado da candidata/aplicação/hotreload e informar aprovados/recusados por motivo. Kit recebido, administração aplicada, snapshot fresco e partida física são quatro provas diferentes.

| Ferramenta fixada do servidor a6b58e9 | SHA-256 |
| --- | --- |
| r128/operator/build_incoming_manifest.py | 362bcae9d8915f7f43aac4c48d06b35bdf57efc88d6acb9199aa06e3a0231426 |
| r128/operator/extract_private_server_artifacts.py | 27053b843d763adcf570e859b2c8658e216dbf6f80963b600fa5326958f70ef4 |
| r128/operator/merge_scoped_modes.py | ddac598ca1671e6d682b626866a3b1984eb88c5ff7d677c7b4cd563a6a677783 |
| online-plataformas-20261009/library-tools/station_online_profiles.py | 3d5d5b5563e2a6825ab9e798da80313cdbf2640522bc4dfd6b47e25c7f69eae1 |
| online-plataformas-20261009/library-tools/cadastrar-motor-online-station.py | a3c81e0c379984d6b7736f79ce963c73a3f3250883f6304a32b5c6cfda73a096 |


### 5.21 Erros, evidência física e critérios de aceite

Diagnóstico deve preservar código real e etapa. GAME_UNCLASSIFIED/PROFILE_UNAPPROVED/CAPACITY_UNSUPPORTED indicam ausência de vínculo aprovado exato; não remover validadores. GENERATION_MISMATCH significa que sala mudou: reconsultar e confirmar. NOT_READY exige todos prontos. CLIENT_UPDATE_REQUIRED exige pacote compatível com capacidade do perfil. ALREADY_ATTACHED/TICKET_INVALID exigem lease/ticket novo conforme estado; UNRECOVERABLE não permite fingir resume. HTTP 401/403 revalidam acesso; 503 pode ser serviço desabilitado/ocupado; HTTP 404 isolado não prova engine ausente. Os prefixos completos STATION_MULTIPLAYER_ ou STATION_ONLINE_ devem ser preservados nos recibos. [ON-10, ON-12]

O sucessor deve registrar, por motor e jogo/edição/modo: APK/hash em ambos; resposta assinada validada; slot/controller mapping; core load/estado inicial; READY real; execução/input nos dois; pausa/rede/foco/reconexão; saída humana/retorno e preservação de saves. Testes ABI/JVM/C/loopback, shader/compilação, instalação ou frontend observado não cobrem isso. Nos relatos históricos, R95 foi instalada em dois aparelhos, mas o próprio canal conserva two-device gameplay pending e fourPhoneGameplayQualified=false. Não herdar qualificações para R134. [ON-18]

Não declarar ausência de lag/ANR/aquecimento ou desempenho equivalente sem medições físicas. N64 cached-interpreter e Dolphin delay fixo podem ter custos diferentes; fotos/prewarm/30 fps de menu não medem emulação online. Isolar uptime, tempo de frame, FPS de jogo, memória, temperatura e condições de rede/aparelho numa sessão autorizada. Uma verificação breve pode mostrar arranque, mas não estabilidade prolongada. O estado atual deve ser fechado com evidência mínima clara e limites de alcance.

- Conferir os quatro IDs R134 e o par original runtime/package; não usar R133/R129 ou públicos sanitizados na implantação.
- Registrar recebimento privado, hash das seis bibliotecas e 20 dependências, ledger/selos finais e baselines ativos.
- Aplicar somente pela administração nativa autorizada; guardar recibo e confirmar hotreload sem substituir validação por reinício.
- Capturar/validar capabilities v3 fresco vinculado ao item/content/engine/profile atual; publicar resultado sanitizado sem tokens.
- Manter recusas HLE/edição/acessório e capacidades específicas; nenhuma aprovação derivada só do teto.
- Fazer sala nova com participantes atualizados, confirmar input/execução nos dois e medir recuperação/saída/saves.
- Separar capas/mídia, instalação, autenticação, registro, transporte e gameplay no aceite final.

## 6 Achados provas correções e fronteiras dos emuladores

### 6.1 Saída GameCube/Wii pode bloquear a interface por ciclo Session/transporte

comprovado no código e reproduzido em JVM; causalidade do relato físico não comprovada.

UI closeByHuman mantém Session e tenta transporte.close; callback unrecoverable mantém transporte e tenta Session.fatal. Ordem invertida; ambos BLOCKED. ThreadMXBean identifica os dois threads em deadlock.

Bloco curto Session para autorização/flags; fechar transporte depois de soltar Session; StopEmulation/closeBlocking seguem worker.

overlay corrigido e teste base/fixed passou.

- [versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationDolphinSession.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-dolphin-online-r126-20261011/java/org/emulationstation/frontend/netplay/StationDolphinSession.java#L147) linhas 147, 189, 190
- [integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java#L30) linhas 30, 72

### 6.2 Saída humana rejeitada por geração antiga pode deixar membership remoto ativo

comprovado no cliente e contrato servidor; reproduzido com classes reais do cliente/servidor fixture.

Um Leave usa binding.generation; exceção ignorada e v3 retorno não reemite. Servidor valida Own antes da mutação.

Somente evento4 humano: uma rejeição409/código exato permite snapshot próprio assinado, identidade integral idêntica, geração maior e uma única reemissão com requestId novo. Confirmar alvo ausente.

overlay corrigido e testes de guardas passaram.

Erro rede/timeout não ganha retry automático nem durable intent; sai localmente e registra diagnóstico categórico de saída não confirmada.

- [versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationGameSession.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationGameSession.java#L73) linhas 73, 76
- [integration/psx-online/java/org/emulationstation/frontend/netplay/StationRoomsActivity.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationRoomsActivity.java#L465) linhas 465, 467
- [src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs#L193) linhas 193, 217, 263, 268

### 6.3 Três participantes precisam de dois links/quatro conexões/barreira global completa

condição implementada; causa da partida relatada não comprovada.

Host só roda quando todas épocas/estados/available estão compatíveis. Servidor exige quatro Hello/Paused/Ready e pending0. PING prova conexão, não execução/READY/ACK de owner. Espera pode permanecer indefinidamente se um peer não completar a barreira.

Instrumentar diagnóstico agregado de slots/fase/época/bytes sem credenciais; capturar emulador e estado real de cada owner. Não relaxar gates.

sem mudança de barreira; análise servidor conduzida separadamente.

- [integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java#L40) linhas 40, 54, 55
- [integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerTunnel.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerTunnel.java#L197) linhas 197, 199, 253, 270

### 6.4 NativeActivity aguarda eventos nativos/destruição sem limite

esperas demonstradas; bloqueio físico não reproduzido.

quit atômico+wake looper; callbacks set input/window/state e onDestroy aguardam cond/worker. Wake não interrompe retro_run/GL/audio/save preso.

Obter trace nativo/UI e confirmar ponto antes de mudar teardown; nunca remover waits ou destruir owner em execução por timeout.

sem alteração nativa.

- [versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationRetroActivity.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationRetroActivity.java#L113) linhas 113, 119, 125, 126, 155, 159
- [versions/station-multiplayer-r77-20261008/native/source/frontend/drivers/platform_unix.c](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-multiplayer-r77-20261008/native/source/frontend/drivers/platform_unix.c#L256) linhas 256, 282, 301, 307, 323, 333, 338, 739, 749

### 6.5 Cancelamento HTTP é executado no chamador durante cleanup

abort síncrono demonstrado; latência/ANR não medida.

pause cancela pending; Cancellation.cancel sincronizado chama abort.run; StationHttp conecta abort a disconnect. Se disconnect demora, chamada de UI pode demorar; não existe prova de demora neste ambiente.

Medir/trace primeiro; eventual cancelamento separa publicação da flag e abort fora de monitores sem abrir janela de acesso indevido.

não alterado; cliente congelado preservado.

- [versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationGameSession.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationGameSession.java#L74) linhas 74, 101
- [versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationApi.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationApi.java#L48) linhas 48, 59
- [versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationHttp.java](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationHttp.java#L64) linhas 64, 65

### 6.6 Auditoria adicional da fronteira entre app, online e emulador

Este complemento lê a fonte executável 4f9039eb9ce13907ce043870bfe1f6e294888556 e as fontes herdadas explicitamente pela composição R134. O trabalho foi somente consulta: nenhum USB/ADB, partida, firmware, ROM, aparelho, servidor ou fonte congelada foi alterado. As mudanças preparadas em outro recorte da equipe devem possuir seus próprios testes/recibos; elas não transformam as hipóteses abaixo em falhas reproduzidas no aparelho.

O foco é o trajeto completo: frontend→launcher→owner→core→partida→save→saída→frontend, incluindo autoridade/Binder/transporte nos modos online. Activity fechada, socket fechado, executor interrompido, thread terminada e core descarregado são eventos distintos. A análise identifica quais eventos o código exige e quais ainda precisam de prova. A preservação de um hash não comprova estabilidade de renderização, áudio, input ou encerramento.

Classificações utilizadas: fonte confirmada significa que o trecho foi lido; risco significa consequência plausível da estrutura; hipótese precisa de teste/reprodução; proteção existente significa guard implementado; qualificação física depende de teste do APK exato, título, aparelho e modo. Não foi comprovado neste recorte que todas as bibliotecas preservadas possuem fonte correspondente ou que seus locks internos foram revisados.

- Referências: [RUN01], [RUN25], [RUN39].

### 6.7 Saída online: Retro e callbacks NativeActivity

No owner Retro herdado da R124, a confirmação humana marca humanExit e quitRequested. Antes de chamar o JNI stationRequestQuit, requestHumanExit chama closeSession de forma síncrona. Esse método possui monitor da Activity e fecha multiplayer, recovery e relay. Assim, uma operação de rede que demora pode prender o caminho da UI antes de o owner receber o pedido de quit. O recorte online da equipe analisa os monitores de transporte e o overlay corretivo.

O JNI nativo verifica a Activity exata sob station_activity_mutex. android_app_request_quit grava stationQuitRequested atomicamente e chama ALooper_wake; o caminho evita backpressure do pipe. O input herdado da R74 verifica o flag antes e depois de poll e durante a espera inicial de window. Esse mecanismo já existe e deve ser preservado. Ele acorda o looper, mas não interrompe código de emulação, driver GL, áudio ou gravação que não retorna ao pump.

Os callbacks NativeActivity de input, window, estado da Activity e saveState esperam a confirmação do owner por condition variable sem prazo. A destruição espera destroyed e faz join. O código libera o mutex durante a condition wait e faz join fora dele; por isso não foi identificado um deadlock trivial desse mutex. Continua possível um ANR quando um core/driver demora indefinidamente e a UI está dentro de um callback Android esperando sua resposta.

onRetroArchExit no worker agenda finish na UI; não chama finish diretamente no mutex finalizador nativo. O shutdown final Android usa exit(0) no runtime isolado. A publicação deve distinguir retorno da Activity de término do processo e não apresentar um timeout arbitrário como licença para liberar ANativeWindow ou memória ainda em uso. A melhoria apropriada é retirar trabalho próprio de rede da UI, enviar o quit cedo e registrar a etapa que ainda falta.

| Fronteira | O que o código prova | O que permanece pendente |
| --- | --- | --- |
| UI→transport close→JNI quit | Ordem síncrona e monitor de closeSession. | Contenção do close e responsividade física de Sair. |
| JNI→ALooper | Atomic release/acquire, wake e checks no pump. | Core/driver fora do pump pode não cooperar. |
| Destroy→worker | Condition libera mutex; join fora dele. | Espera sem prazo e garantia física de término. |
| Worker→UI finish | onRetroArchExit agenda a UI. | Conferir resultado da autoridade e catálogo restaurado. |

- Achados RT-01 aRT-03. Referências: [RUN02] 117–159; [RUN03] 241–408, 739–749; [RUN04] 1640–1693.

### 6.8 N64: quit cooperativo, saves isolados e recursos locais

StationN64Bridge atua apenas quando o descriptor de lançamento Station foi consumido e o contexto é reconhecido. A sessão redireciona autoSaveDir, config, SRAM, slotSaveDir e userSaveDir para o diretório privado da sala/geração. Autosave/load automático e import/export do storage offline são bloqueados no contexto online. A partida offline conserva sua rota normal. Isso evita escrever estados online na biblioteca habitual, mas não constitui migração universal de saves.

O quit nativo StationMupenRequestQuit marca quitting e acorda a condição. O gate somente reconhece checkpoint/ACK no thread do emulador; bombeia a rede fora do mutex, reavalia revisão e não dorme após atualização perdida. A receita de transferência usa poll de 20 ms e recv/send não bloqueantes, com check de cancelamento/falha. netplay_stop recusa fechar/free enquanto EXECUTE ainda roda, e o cleanup do owner libera a fila de inputs.

Session.close Java é sincronizado e chamado por onExit/onDestroy. Ele solicita quit, fecha transporte, mux e Binder, interrompe o worker e remove a tela de espera. O mux fecha TCP/UDP/listeners/queues, acorda guestReady e interrompe seus executores; o servidor acorda registro/saves/sendqueues e interrompe senders. Não há awaitTermination dessa família de workers. Fechamento de sockets e shutdownNow são evidências de cancelamento, não prova de término real de todas as threads.

Não foi encontrado no N64 o mesmo ABBA entre monitor Session e transport descrito no Dolphin: fatal/nativeControl N64 não sincronizam Session. Ainda é necessário validar o fechamento comum do transporte, a ordem transport→mux e retorno oficial após o core acabar. O thread principal não deve aguardar a liberação completa de workers sob um monitor de Activity. A confirmação humana deve seguir necessária; falha de rede continua sendo pausa/atenção, nunca STOP automático.

- Achados RT-04 eRT-05. Referências: [RUN05] 35–56, 94–141; [RUN06] 111–124, 216–236; [RUN07] 53–98, 108–135; [RUN08] 95–97; [RUN09] 122–124.

### 6.9 PSX: owner exato, checkpoints e condição de retorno

O caminho PXL1 executa o LibretroPlayer normal preservado e o core PCSX-ReARMed normal, em processo privado. O shim confere hashes/ABI e adapta somente entradas delimitadas. O protocolo não executa retro_run a partir de thread de IO; o checkpoint original concede o fechamento após autorização humana e depois de inFrame/aplicação de estado terminarem. Unload/deinit automáticos são bloqueados até o owner registrar closed.

humanExit marca a ação sob monitor breve e realiza t.close em worker separado. Na sequência, o Binder é fechado na UI, o JNI recebe a autorização humana e o cleanup verifica transport.awaitClosed. Cada espera tem janela de 250 ms e novo agendamento de 50 ms; o ciclo continua até terminar. A Activity captura o thread real do owner e faz join numa thread daemon própria, evitando self-join e espera longa na UI.

A retirada do processo exige quatro condições: ação humana registrada, cleanup de IO/Binder completo, processo PSX privado e owner efetivamente encerrado. O opt-in SDL mantém uma destruição inesperada como falha/pausa, sem chamar o teardown padrão enquanto esses gates faltam. Não se deve relaxar essa proteção para esconder um bloqueio, pois ela impede use-after-free e encerramento de jogo por lifecycle.

Há um limite de disponibilidade: se uma chamada do core, callback, Binder ou IO nunca termina, a saída permanece pendente sem informação de etapa. A fonte C++ completa do LibretroPlayer exato não foi localizada; a leitura presente cobre shim, adaptação, protocolo e gates Java, não todos os locks de render/input/audio do owner binário. A melhoria possível é mostrar estágio/duração e colher diagnóstico agregado, mantendo recuperação adicional como ação humana explícita no processo privado.

- Achados RT-06 eRT-07. Referências: [RUN10] 146–164; [RUN11] 67–96; [RUN12] 182–233; [RUN13] 151–154, 207–214; [RUN14] 264–271; [RUN15] 20–32.

### 6.10 Sony: encerramento, áudio e continuidade da sessão

PS3 R134 mantém operações de superfície e configuração num worker serial. setup_surface/boot/resume/pause/change_surface não são executados como longas esperas na UI. surfaceDestroyed libera inputs e agenda pause+surface null. onDestroy marca closed, neutraliza inputs e enfileira quit após o trabalho existente; depois encerra só o processo :station_ps3 quando há jogo configurado/iniciado. Voltar de settings entra atrás dos saves humanos pendentes. Se uma chamada JNI anterior não retornar, o quit não chega ao início da fila; ainda falta qualificação física com jogo real.

PS4 usa dois executores: o worker de preparo/run/config e stopper para a ação humana cancelImport/stop. O worker de run fecha a sessão no finally, depois de o native run retornar. Dessa forma, superfície/input/áudio não são descartados enquanto a emulação normal ainda os usa. Não há prazo para stop/run. A tela Encerrando pode permanecer aberta quando o owner não coopera; o retorno da UI e fim do processo devem ter provas separadas.

A ponte Bachata S4 0.2.4 não oferece pause/rebind. TextureView retém sua SurfaceTexture ao desanexar; onPause apenas limpa toque e envia estado neutro do controle. Por isso não há fundamento para prometer pausa de execução/som ao mandar o app para background. onDestroy sem ação humana não mata o jogo; se Android destrói a Activity, ainda pode existir runtime ativo sem aquela UI até o processo ser encerrado. É necessária prova de retorno de superfície, áudio, inputs e capacidade de voltar ao catálogo.

Ps4Audio limita 8 workers de streams, valida cabeçalhos/tamanho/tipo/rate, converte para estéreoPCM 16 e escreve AudioTrack de modo bloqueante. release remove o track atomicamente antes de pause/flush/release, evitando dupla liberação. close fecha listener/peers/tracks e chama shutdownNow; Ps4Control acorda queue, fecha sockets e interrompe worker. Não há join/await desses executores. A limpeza é bem delimitada, mas duração do driver e término real não foram medidos. Não mover release de áudio bloqueante para a UI como suposta correção.

- Achados RT-08 aRT-10. Referências: [RUN16] 138–250; [RUN17] 160–177, 236–255, 451–455; [RUN18] 17–22, 61–78, 106–117; [RUN19] 135–160.

### 6.11 Frontend ao entrar e voltar de uma partida

O vídeo do carrossel observa o lifecycle da Activity oficial. Pause/stop/destroy ou Activity diferente do frontend chama stopAll. Cada slot é retirado atomicamente, sua sessão fica inválida, as superfícies são liberadas sob o monitor da Session e o MediaPlayer é liberado no worker próprio. O render também segura esse monitor ao executar updateTexImage/getTransformMatrix. Uma chamada de driver lenta nesse ponto pode prolongar a espera da UI por releaseSurfaces; esse é risco de contenção, ainda não reprodução de ANR.

A camada nativa retira slots somente depois de o JNI aceitar stop; se o JNI está temporariamente indisponível, mantém stopPending e tenta depois. Um GLuint é deletado apenas no contexto em que foi criado. Campos LED/frames retidos possuem identidades de contexto/fonte e são esquecidos na troca de contexto; não são liberados através de um novo contexto com nome numérico reutilizado. Esses guards devem ser preservados em qualquer alteração de saída.

O foreground do frontend incrementa a geração da publicação, cancela warm de capa, suspende prefetch/polling e notifica a presença online. Capas nativas deferidas durante preparação do catálogo são mantidas silenciosas para não criar uma tempestade de retries quando a Activity está pausada. No retorno, as filas admitidas e polling podem retomar. Downloads possuem serviço/worker próprios e podem continuar por opção do usuário; atividade de download em background não deve ser classificada automaticamente como vazamento.

Para certificar o handoff visual é preciso observar ida e volta entre settings, sala e jogo real: catálogo/foco restaurados, um decoder no máximo, nenhum menu áudio sobre a partida, sem textura de contexto antigo, sem callback de capa antiga e sem reentrada de owner. O limite de 30 fps é da apresentação do menu e não limita a emulação. Nem os guards de contexto nem o cancelamento por geração comprovam temperatura, consumo ou FPS físico de jogos.

- Achado RT-11. Referências: [RUN20] 57–60, 173–204; [RUN21] 138–160; [RUN22] 354–404; [RUN23] 243–245; [RUN37] 251–253; [RUN38].

### 6.12 Correções de abrangência do dossiê e limites da fonte

O dossiê anterior cobriu as 50 plataformas canônicas e os dois owners Sony, mas citou sem enumerar os 43 perfis originais de fallback. Esses perfis são extração estática do ELF normal; há seletores para SegaCD, AtariLynx, NeoGeoPocket, WonderSwan, MSX e VirtualBoy além das linhas canônicas. Não são novas plataformas aprovadas pelo StationPlatforms, nem prova de core disponível no APK/aparelho. Sua presença pode atender rotas legadas/normalizadas, mas um catálogo novo com nome sem mapeamento explícito segue sendo recusado.

Também havia requisitos de wrappers antigos marcados como não consolidados. A leitura adicional fixa guards existentes: Vita API 28; Xbox clássico API 29/Android 10, com mensagem X1 BOX 1.2.8; WiiU/Cemu e Xbox360/XenDroid API 30/Android 11 mais feature Vulkan 1.1. Estes são guards de Java preservados na cadeia documental. O mínimo efetivo de todo o pacote e o comportamento final do APK exato precisam ser conferidos no recibo/composição; não usar requisito de release upstream recente para preencher lacunas.

Extensões nos 43 perfis são critérios históricos de seleção e não whitelist validada do binário/launcher atual. Exemplos: o perfil 3DS aponta citra mas o comando canônico usa azahar; o perfil N64 aponta mupen64plus_next mas a rota normal usa Mupen64Plus AE; Switch fallback suyu é substituído pelo bootstrap Yuzu; NeoGeo/Arcade/CPS/NeoCD atuais passam pelo MAME; PCECD atual força mednafen_pce. A revisão não deve restaurar fallback antigo por causa de um nome conhecido.

As oito dependências ausentes na observação Motorola R119/R120 eram melonds, o2em, stella, prosystem, bluemsx, fbneo, gw e virtualjaguar. Esse estado é histórico; ele não foi novamente lido nos aparelhos e não autoriza dizer que continuam ausentes ou estão resolvidas. A matriz consumer mantém essa condição aberta. Nos motores binários preservados, leitura de wrapper/receita/hash é cobertura de fronteira, não auditoria do loop nativo inteiro.

Além dos handoffs de lançamento, a aprovação precisa considerar input e saves por família. EX+ AUTO pode incluir teclado; PPSSPP conserva touch manual; Saturn não tem listener transitório universal; Flycast tem gaps de hitTest/visibilidade; Cemu StateFlow ainda precisa de prova; XenDroid Compose é manual; Xbox wrapper não exclui virtual na fonte lida; LibretroPlayer não tem API de auto-hide universal comprovada. Esses limites já descritos permanecem gates, sem conserto global por suposição.

- Referências: [RUN24], [RUN25], [RUN26], [RUN27] 23–37, [RUN28] 34–36, [RUN29] 20–24, [RUN30] 30.

### 6.13 Inventário dos 43 seletores originais de fallback

A tabela completa mantém os nomes, cores e extensões extraídos do ELF normal. A resolução original tenta comandoXML/hook, depois pasta normalizada e nome normalizado. Os hooks de integração atuais têm precedência. Para todos os perfis abaixo, disponibilidade, dependências, compatibilidade e gameplay não são concedidos pela tabela.

| Perfil | Core original | Aliases do seletor | Extensões históricas |
| --- | --- | --- | --- |
| Nintendo Entertainment System | fceumm | nes famicom fc nintendoentertainmentsystem nintendinho fds famicomdisksystem | .nes .fds .unf .unif .zip |
| Super Nintendo | snes9x | snes sfc superfamicom supernintendo supernes | .smc .sfc .fig .swc .bs .zip |
| Game Boy | gambatte | gb gameboy | .gb .zip |
| Game Boy Color | gambatte | gbc gameboycolor | .gbc .gb .zip |
| Game Boy Advance | mgba | gba gameboyadvance | .gba .zip |
| Nintendo DS | melonds | nds ds nintendods | .nds .zip |
| Mega Drive | genesis_plus_gx | megadrive genesis md segagenesis segamegadrive | .md .gen .smd .bin .sms .zip |
| Master System | genesis_plus_gx | mastersystem sms segamastersystem | .sms .zip |
| Game Gear | genesis_plus_gx | gamegear gg segagamegear | .gg .zip |
| Sega CD | genesis_plus_gx | segacd megacd | .cue .chd .iso .m3u |
| Sega 32X | picodrive | sega32x 32x | .32x .zip |
| PC Engine | mednafen_pce_fast | pcengine pce tg16 turbografx16 turbografx | .pce .zip |
| PC Engine CD | mednafen_pce_fast | pcenginecd tg16cd turbografxcd | .cue .chd .ccd |
| PlayStation | pcsx_rearmed | psx ps1 playstation playstation1 psone | .pbp .cue .chd .bin .iso .img .m3u |
| Neo Geo | fbneo | neogeo | .zip .7z |
| Arcade | fbneo | arcade fbneo fba finalburn | .zip .7z |
| MAME | mame2003_plus | mame mame2003 | .zip |
| Atari 2600 | stella | atari2600 a 2600 | .a 26 .bin .zip |
| Atari 7800 | prosystem | atari7800 a 7800 | .a 78 .bin .zip |
| Atari Lynx | handy | atarilynx lynx | .lnx .zip |
| Neo Geo Pocket | mednafen_ngp | ngp ngpc neogeopocket neogeopocketcolor | .ngp .ngc .zip |
| WonderSwan | mednafen_wswan | wonderswan wsc ws wonderswancolor | .ws .wsc .zip |
| MSX | bluemsx | msx msx1 msx2 | .rom .mx1 .mx2 .dsk .cas .m3u .zip .7z |
| ColecoVision | bluemsx | colecovision coleco | .col .rom .zip |
| Virtual Boy | mednafen_vb | virtualboy vb | .vb .vboy .zip |
| PlayStation 2 | armsx2 | ps2 playstation2 ps2br playstation2br | .iso .chd .cso .zso .bin .elf .gz .mdf .nrg .img .m3u |
| Nintendo Switch | suyu | switch nintendoswitch nsw ns | .nsp .xci .nca .nro |
| CPS-1 | fbalpha2012_cps1 | cps1 capcomcps1 cpsi | .zip .7z |
| CPS-2 | fbalpha2012_cps2 | cps2 capcomcps2 cpsii | .zip .7z |
| CPS-3 | fbalpha2012_cps3 | cps3 capcomcps3 cpsiii | .zip .7z |
| PSP | ppsspp | psp playstationportable | .iso .cso .pbp .chd .elf .prx .zip |
| Nintendo 3DS | citra | 3ds nintendo3ds | .3ds .3dsx .cci .cxi .cia .app .elf .axf |
| Dreamcast | flycast | dreamcast dc | .gdi .cdi .chd .cue .bin .elf .m3u .zip |
| GameCube | dolphin | gamecube gc ngc | .iso .gcm .gcz .ciso .rvz .wbfs .wia .dol .elf .m3u |
| Wii | dolphin | wii nintendowii | .iso .wbfs .rvz .ciso .gcz .wia .wad .dol .elf .m3u |
| Nintendo 64 | mupen64plus_next_gles3 | n64 nintendo64 | .n64 .z64 .v64 .zip |
| Saturn | yabasanshiro | saturn segasaturn ss | .cue .ccd .chd .iso .m3u .zip |
| Neo Geo CD | neocd | neogeocd neocd ngcd neogeocdz | .cue .chd |
| Atomiswave | flycast | atomiswave awave naomi naomi2 | .zip .7z .lst .dat |
| SuperGrafx | mednafen_supergrafx | supergrafx sgx pcenginesupergrafx | .pce .sgx .cue .ccd .chd .zip |
| Game & Watch | gw | gameandwatch gw gamewatch | .mgw |
| Odyssey 2 | o2em | o2em odyssey2 odyssey videopac | .bin .zip |
| Atari Jaguar | virtualjaguar | jaguar atarijaguar | .j64 .jag .rom .abs .cof .bin .prg .zip |

- Referência: [RUN24].

### 6.14 Roteiro consumidor para todas as plataformas canônicas e Sony

A matriz abaixo cobre as 50 linhas do catálogo auditado e os dois owners Sony. Cada linha requer o ciclo G01 no título real e gates adicionais da família. O formato/dependência indicado é condição, não certificado de compatibilidade. Nenhum desses testes físicos foi executado neste recorte. VariaçõesBR devem usar título e recibo próprios mesmo quando compartilham motor.

Registrar APK exato, aparelho/Android, título/edição/conteúdo, modo, input e resultado por etapa. Para catálogo/menu anotar somente evidência necessária; para rede/sala usar logs agregados sem ticket/token/identidade. Um boot incompleto, silêncio, tela preta, erro de dependência ou saída parada deve ficar como resultado próprio, sem mascarar pela instalação do aplicativo.

| Plataforma | Owner / processo | Pré-condição | Controle, save, retorno e gates |
| --- | --- | --- | --- |
| 3ds | LibretroPlayer: azahar · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Arcade | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| Atomiswave | Flycast Android · :flycast | Imagem válida e dependências do hardware; BIOS/saves são específicos DC/Naomi/Atomiswave. | Conferir VGamepad/hotplug, VMU/NVRAM, retorno oficial e reabertura. Gates: G01, G04, G10 |
| Dreamcast | Flycast Android · :flycast | Imagem válida e dependências do hardware; BIOS/saves são específicos DC/Naomi/Atomiswave. | Conferir VGamepad/hotplug, VMU/NVRAM, retorno oficial e reabertura. Gates: G01, G04, G10 |
| GameCube | Dolphin Android · :dolphin | Arquivo real iso/gcz/wbfs/rvz no registro; GC/Wii usam configurações e input próprios. | Conferir portas GC/Wiimote, touch/hotplug e saves; saída humana e retorno. Gates: G01, G02, G04, G09 |
| Gameboy | LibretroPlayer: gambatte · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Gameboy Color | LibretroPlayer: gambatte · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Gba | LibretroPlayer: mgba · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Master System | LibretroPlayer: genesis_plus_gx · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| MegaDrive | MD.emu EX+ · :megadrive | Motor Snes9x ou MD.emu preservado; arquivo e extensão do owner. | AUTO do controle respeita ON/OFF manual; conferir teclado/hotplug, save nativo e state. Gates: G01, G04, G09 |
| MegaDrive - BR | MD.emu EX+ · :megadrive | Motor Snes9x ou MD.emu preservado; arquivo e extensão do owner. | AUTO do controle respeita ON/OFF manual; conferir teclado/hotplug, save nativo e state. Gates: G01, G04, G09 |
| Neo Geo | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| Neo Geo CD | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| Nintendinho | LibretroPlayer: fceumm · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Nintendo 64 | Mupen64Plus AE · :n64 → :n64core | API 28; ROM n64/z64/v64 segundo registro; formato completo do owner deve ser conferido. | Menu oficial, toque+físico, save nativo; no online usar saves isolados e G05. Gates: G01, G02, G05, G09 |
| Nintendo 64 - BR | Mupen64Plus AE · :n64 → :n64core | API 28; ROM n64/z64/v64 segundo registro; formato completo do owner deve ser conferido. | Menu oficial, toque+físico, save nativo; no online usar saves isolados e G05. Gates: G01, G02, G05, G09 |
| Nintendo DS | LibretroPlayer: melonds · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Odyssey 2 | LibretroPlayer: o2em · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| PSP | PPSSPP Android · :psp | Arquivo real enviado ao PPSSPP 1.20.4; extensões do perfil não garantem suporte de cada pacote. | ShowTouchControls manual persistente, menu próprio e memstick; conferir saída sem login novo. Gates: G01, G04, G10 |
| Pc Engine | LibretroPlayer: mednafen_pce_fast · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Pc Engine cd | LibretroPlayer: mednafen_pce · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| Playstation 1 | LibretroPlayer: pcsx_rearmed · main (applicationId) | Core PCSX normal presente na matriz; HLE online só por edição/aprovação e2 portas. | Save state não equivale a save nativo; offline e PXL1 têm storage distinto. Gates: G01, G02, G06, G10 |
| Playstation 2 | ARMSX2 Android · :ps2 | ARMSX2 2.7.2, BIOS/conteúdo validado; SDK26 do artefato não garante mínimo do app. | Renderer/menu/input próprio; conciliar DEX do overlay; save e retorno official. Gates: G01, G04, G10 |
| Playstation 2 - BR | ARMSX2 Android · :ps2 | ARMSX2 2.7.2, BIOS/conteúdo validado; SDK26 do artefato não garante mínimo do app. | Renderer/menu/input próprio; conciliar DEX do overlay; save e retorno official. Gates: G01, G04, G10 |
| Psp - BR | PPSSPP Android · :psp | Arquivo real enviado ao PPSSPP 1.20.4; extensões do perfil não garantem suporte de cada pacote. | ShowTouchControls manual persistente, menu próprio e memstick; conferir saída sem login novo. Gates: G01, G04, G10 |
| Psvita | Vita3K Android · :psvita | Guard de wrapper API 28; instalação/firmware/conteúdo precisam estar preparados. | Touch hide no controle conectado e retorno após última desconexão; conferir save. Gates: G01, G04, G10 |
| Super Nintendo | Snes9x EX+ · :snes | Motor Snes9x ou MD.emu preservado; arquivo e extensão do owner. | AUTO do controle respeita ON/OFF manual; conferir teclado/hotplug, save nativo e state. Gates: G01, G04, G09 |
| Super Nintendo - BR | Snes9x EX+ · :snes | Motor Snes9x ou MD.emu preservado; arquivo e extensão do owner. | AUTO do controle respeita ON/OFF manual; conferir teclado/hotplug, save nativo e state. Gates: G01, G04, G09 |
| Switch | Yuzu Android (unchanged) · main (applicationId) | Bootstrap Android do próprio pacote; conteúdo/keys/firmware privados; novo roms/switch. | Conferir overlay, renderer, save, back e retorno; não mover biblioteca existente. Gates: G01, G04, G10 |
| atari2600 | LibretroPlayer: stella · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| atari7800 | LibretroPlayer: prosystem · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| colecovision | LibretroPlayer: bluemsx · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| cps1 | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| cps2 | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| cps3 | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| fbneo | LibretroPlayer: fbneo · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| fds | LibretroPlayer: fceumm · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| gameandwatch | LibretroPlayer: gw · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| gamegear | LibretroPlayer: genesis_plus_gx · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| jaguar | LibretroPlayer: virtualjaguar · main (applicationId) | Dependência ausente na observação R119/R120: inventário atual precisa ser conferido antes de iniciar. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| mame | MAME 4droid Current · :mame | ROMset/driver/parent/BIOS compatíveis; cartucho ZIP; Neo Geo CD somente CHD v5 autônomo no launcher. | Menu do MAME, toque/físico e save nativo; NeoCD validar BIOS automática e driver CDZ. Gates: G01, G04, G10 |
| naomi | Flycast Android · :flycast | Imagem válida e dependências do hardware; BIOS/saves são específicos DC/Naomi/Atomiswave. | Conferir VGamepad/hotplug, VMU/NVRAM, retorno oficial e reabertura. Gates: G01, G04, G10 |
| naomi2 | Flycast Android · :flycast | Imagem válida e dependências do hardware; BIOS/saves são específicos DC/Naomi/Atomiswave. | Conferir VGamepad/hotplug, VMU/NVRAM, retorno oficial e reabertura. Gates: G01, G04, G10 |
| saturn | Saturn integrado · :saturn | Owner Yaba Sanshiro 1.20.46; BIOS/imagem do formato real. | Touch manual, pad físico separado; nunca releaseAll universal porque afeta físico. Gates: G01, G04, G10 |
| sega32x | LibretroPlayer: picodrive · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| supergrafx | LibretroPlayer: mednafen_supergrafx · main (applicationId) | Core da linha deve existir; conteúdo/BIOS e formato completo dependem do core exato. | Input/menu/saves originais; API universal de touch e cleanup interno não comprovados. Gates: G01, G04, G10 |
| wii | Dolphin Android · :dolphin | Arquivo real iso/gcz/wbfs/rvz no registro; GC/Wii usam configurações e input próprios. | Conferir portas GC/Wiimote, touch/hotplug e saves; saída humana e retorno. Gates: G01, G02, G04, G09 |
| wiiu | Cemu Android · :wiiu | Guard de wrapper API 30+Vulkan 1.1; Cemu 0.5.2 experimental; conteúdo executável/keys válidos. | StateFlow/input overlay próprio; conferir GamePad, save, background, retorno e som. Gates: G01, G04, G10 |
| xbox | x1box/xemu · :xbox → :xboxemu | Guard de wrapper API 29 e X1 BOX 1.2.8; dependências/disco/storage do xemu. | Conferir settings vs game process; input físico/touch, saves, retorno humano. Gates: G01, G04, G10 |
| xbox360 | Xendroid · :xbox360 → :xbox360emu | Guard de wrapper API 30+Vulkan 1.1; XenDroid experimental; conteúdo do owner. | Touch Compose manual; conferir som/render/controller, saves e duas etapas de processo. Gates: G01, G04, G10 |
| PlayStation 3 | aPS3e 2.43 · :station_ps3 | API 28/ARM64; firmware preparado; ISO real ou pasta válida do owner, chave própria quando aplicável. | R134: 18 campos+touch; saída humana→quit worker; conferir save/input/Superfície e próximo boot. Gates G01, G07, G09. |
| PlayStation 4 | Bachata S4 0.2.4 · :station_ps4 | API 31/ARM64/GPU compatível; PKG real preparado na biblioteca privada. | R134: 11 campos+touch;4 slots; background não pausa; stop→fim run→áudio/input/superfície. Gates G01, G07, G08, G09. |

- Referências: [RUN25], [RUN26], [RUN27] 23–37; [RUN28] 34–36; [RUN29] 20–24; [RUN30] 30; [RUN16], [RUN17].

### 6.15 Gates de teste e critério para publicação

Os testes de modelo/concorrência e probes nativos delimitados devem verificar a ordem de cleanup, idempotência e uso correto dos monitores. Eles não substituem os testes consumidor. Uma alteração de lifecycle deve ter allowlist e recibos de origem/composição; conservar assinatura/dados/opções/input/render/saves dos motores e registrar novos IDs de runtime quando compartilhados mudam.

A liberação pode afirmar que a fonte foi corrigida e os testes específicos passaram, se houver essas provas. Instalação, abertura, jogo, servidor e estabilidade física continuam etapas distintas. Não declarar todos os motores aprovados, 4 jogadores estáveis, som/saves perfeitos ou redução térmica pela aprovação de um helper Java. Nenhum timeout deve autorizar apagar dados, matar jogo sem ação humana ou liberar memória ainda em uso.

| Gate | Teste | Resultado mínimo |
| --- | --- | --- |
| G01 · Ciclo consumidor offline por título | Selecionar título real instalado; abrir; conferir imagem/som/toque/controle; gravar save nativo; sair pelo menu humano; voltar ao mesmo catálogo; abrir o mesmo título e conferir save. Repetir no mesmo APK/aparelho sem limpar dados. | Título correto, uma sessão, nenhum input/som preso, retorno responsivo e save persistente. |
| G02 · Sair em todas as fases do owner online | Aplicar confirmação Sair antes do primeiro frame, durante preparação, registro, sincronização, espera de input, partida e pausa nativa. Testar duplo toque/back/menu e sair logo após falha. | Ação humana é idempotente; UI continua respondendo; quit chega ao owner; IO/Binder/owner terminam e autoridade recebe um único encerramento. |
| G03 · NativeActivity e contenção | Atrasar mock de close/callback, core/driver e fim do owner; solicitar pause/window/input/save/destroy; coletar stacks/etapas agregadas sem identidades. | Trabalho próprio de rede não segura UI/monitor de Activity; nenhum uso de memória/janela após liberar; wait real é visível e diagnosticável. |
| G04 · Carrossel e contexto recriado | Entrar/sair rapidamente de jogo, settings, sala e frontend; apagar/recriar contexto GL; alterar vídeos/economia durante retorno; conferir stopAll e contagem de decoder. | Um decoder no máximo, nenhum GLuint velho usado no contexto novo, catálogo/foco restaurados, toque correto e sem áudio do menu sobre a partida. |
| G05 · N64 normal e SN64 | Registro incompleto, espera de save/input, EOF local, fechamento de UDP/TCP, input físico removido e quit humano em cada fase; observar fim de EXECUTE antes de netplay_stop. | Mutex do gate não fica em pump externo; quit desbloqueia transfer/gate; queues/senders/mux terminam e offline não herda diretório online. |
| G06 · PSX normal e PXL1 | Core/HLE aprovado por edição; falha de fonte/ABI/config; native menu pause; destroy sem humano; confirmação humana durante IO/callback preso; liberação de estado após checkpoint. | Nenhum unload/deinit automático, nenhum falso READY/ACK, join fora da UI e retirada só depois de owner+Binder+IO realmente concluídos. |
| G07 · Sony settings e sessão | Alterar um campo R134 e clicar Voltar imediatamente; reabrir; conferir chave desconhecida preservada e mudança consumida pelo motor; iniciar jogo real; background e retorno; sair durante bootstrap/import. | Saves FIFO completos, uma sessão, sem callbacks antigos na nova tela, input neutro, retorno consistente. Preparação/firmware importado é registrada separadamente de gameplay. |
| G08 · PS4 áudio/input e stop | Áudio ativo, 8 streams, stream truncado, socket perdido, WRITE_BLOCKING atrasado e stop simultâneo; hotplug em 4 slots; neutralização em pause/removal. | Sockets fecham, uma release por track, workers terminam, sem som/input residual; superfície liberada só após native run retornar. |
| G09 · Pacote e regressão da composição | Comparar somente entradas autorizadas; source/runtime/engine IDs novos coerentes; DEX fora allowlist e motores/controles/opções/saves byte preservados; compilar tests de concorrência e probes nativos relevantes. | Recibos separados para fonte, pacote, instalado, boot, gameplay e servidor; não promover por mock/status 200/PONG isolado. |
| G10 · Dependências e rotas ausentes | Conferir core/BIOS/firmware/content no APK exato ou diretório permitido atual; apresentar requisito ausente antes de launch; arquivos válidos e inválidos por formato do owner. | Sem falso botão que promete gameplay; o histórico de 8 dependências não é tratado como inventário atual. |

- Referências: [RUN01], [RUN02] 154–159; [RUN03] 326–338; [RUN10] 146–164; [RUN11] 88–96; [RUN16] 186–215.

### 6.16 Servidor auditado: versão, cadeia de evidência e alcance

A auditoria usa o código Servidor-pix a6b58e9beb12eb564c1b58d9d4c32ed3e7513861, da branch feat/station-r128-aplicado-20261011. A branch de documentação docs/station-r133-final-console-modes-20261011 está no HEAD 524d2ebff08353fda62aacbc5f05f9248ba69b7c e conserva esse domínio de runtime. As 117 branches foram enumeradas em duas páginas, incluindo as 17 posteriores ao primeiro lote de 100. Não foi localizado retorno posterior que confirme aplicação do kit R134. A conclusão se limita às fontes e recibos públicos consultados; não houve consulta ao host produtivo ou inferência da configuração efetiva. [SA16-SA19, SA25]

O checkout isolado publication-server tem como base docs R133. A proposta acrescenta uma projeção numérica do estado da barreira para membros e uma suite determinística. Não foram executados comandos de aplicação administrativa, restart, acesso a banco produtivo, USB ou fluxo de licença real. Os testes invocam classes C# reais com identidades fictícias em processo e não constituem gameplay Android nem validação de TLS/WAN. [SA21-SA23]

O URL comercial /v1, schemaVersion=1, domínio de assinatura online/v1, revisão do pacote R134 e multiplayerVersion=3 são identificadores de eixos diferentes. O cliente comercial v1 e os domínios v1/v2 de lobby coexistem com station-multiplayer.v3. Para admitir um jogo v3, exige-se o snapshot próprio com capability e perfil exato. Resposta HTTP 200, PONG ou serverReady de plataforma não bastam. [SA01:236-268, SA07:29-32, SA26]


### 6.17 Falha comprovada de espera com três participantes

Três jogadores significam um host e dois guests. A topologia host-star abre dois links, cada um com um endpoint host e um endpoint guest. Portanto a barreira precisa de quatro attachments de transporte, embora a sala tenha três membros. Cada direção conserva uma janela FIFO de 262144 bytes. A reserva é 2 links × 2 direções × 262144 = 1048576 bytes, exatamente 1 MiB. Confundir três jogadores com três conexões deixa um endpoint esperado sem participação. [SA01:185-191, SA02:17-35]

O servidor só passa de Waiting para Synchronizing quando todos os endpoints esperados estão anexados, com HELLO e PAUSED válidos, e nenhum participante está suspenso. Só passa para Playing quando as quatro flags Ready estão verdadeiras e todas as janelas têm pendingBytes=0. READY exige epoch corrente, confirmação de pausa e watermark Accepted exato da direção. ACK confirma entrega de replay e não substitui READY. O ready=true do lobby não substitui nenhum desses frames. [SA01:182-188, SA02:59-95]

No domínio real foi reproduzido o estado com quatro attachments, HELLO/PAUSED completos, três READY válidos e pending=0: Synchronizing e hasPlayed=false. Avançar 300000 ms no relógio sintético do hub, com heartbeat dos três peers e PING dos quatro endpoints, não inicia a partida. A última READY válida libera Playing. Isso prova uma condição de espera sem prazo global no código; não prova qual aparelho real deixou de emitir READY nem identifica uma ROM como causa. [SA21, SA23]

Watch fecha um attachment quando a lease fica inválida, o heartbeat de controle envelhece ≥60 s, o último frame recebido envelhece ≥30 s ou a autorização não pode ser revalidada. Verifica a cada 10 s e limita a consulta de autorização a 5 s. Se heartbeat e PING continuarem, as verificações de vida não detectam falta de READY nem replay pendente. A sala lógica é conservada para recuperação; o cliente pode manter loading se não apresentar a causa e não confirmar a saída humana. [SA02:149-159]

Os timeouts de 30/90 s do domínio legado não se aplicam automaticamente à barreira multiplayer v3. Um prazo opcional futuro exigiria política explícita de produto e protocolo. Este patch não inicia sem um participante, descarta bytes ou retira alguém por timer. A evidência aponta necessidade de diagnóstico, observação do lado nativo e confirmação de saída, conservando os validadores. [SA06:155-175, SA02:42-95]

| Estado observável | Condição exata | Efeito/limite |
| --- | --- | --- |
| starting | Epoch=1 e stream Waiting após start; anexos/HELLO/PAUSED ainda incompletos. | Roster congelado; ainda não prova gameplay. |
| waiting-reconnect | Stream Waiting em epoch>1, após Pause/detach/suspend. | Perda de rede não remove membros. |
| synchronizing | Todos HELLO+PAUSED, sem suspensos; falta READY ou há replay pendente. | Com tráfego de vida, pode esperar sem prazo global. |
| playing | Todos READY na transição e pending=0. | DATA pode invalidar flags do seu par durante tráfego normal sem sair de Playing. |
| unrecoverable | Falha explícita ou protocolo inválido chama End. | Resume/ticket recusados; leave humano continua disponível. |


### 6.18 Regras de perfil, número de jogadores e ownership

O perfil é identificado por itemId, contentSha256, platform, engineId, coreSha256, runtimeSha256, profileId, profileSha256, controllerProfile, mode e allowedPlayerCounts. Aprovação exige hashes de 64 caracteres hexadecimais, catálogo corrente compatível e entrada Approved. Plataforma ou engineId isolados não identificam um perfil. O teto global é cinco jogadores; a política administrativa limita SNES a 5, N64/Dreamcast/GameCube/Wii/WiiU a 4 e as demais plataformas aceitas a 2. Esses tetos não homologam automaticamente todos os números intermediários. [SA01:76-145, SA04]

Um perfil maximumPlayers=4 com allowedPlayerCounts=[2,4] recusa uma sala de três, mesmo com quatro portas disponíveis. Start revalida a quantidade real de membros; ready revalida a capacidade configurada. Uma sala de capacidade 4 pode iniciar com três presentes somente se 3 estiver explicitamente homologado e os três estiverem prontos. Este método não exige lotação completa. O novo teste configura capacity=3 e allowedPlayerCounts=[2,3,4]. [SA01:126-131,182-192, SA13, SA21]

Create e join exigem que maximumPlayers do perfil caiba no clientMaximumPlayers enviado. O default do comando é 4, e o domínio aceita de 2 a 5. Isso impede ingresso com capacidade de cliente inferior ao máximo do perfil, mesmo em sala menor. A classificação retorna até 32 matches por item e filtra a identidade corrente do catálogo. A listagem pública é paginada: até 100 salas, páginas de 0 a 40 e tamanho 32 ou 100. A ownRoom aparece separadamente. [SA01:151-179,236-257]

Após start, roster e links ficam congelados. O host é autenticado nos seus endpoints e cada guest no próprio link/slot; um guest não acessa o link de outro. Create/join dos domínios legado e v3 compartilham AdmissionGate para evitar duas memberships da mesma identidade. Bloqueio social e revogação são eventos explícitos que podem aposentar a sala; perda de transporte não escolhe saída lógica. [SA01:199-225,270-287, SA03:29-34, SA07:99-104]

| Ações do contrato (12 no total) | Condição/ownership | Limite | Efeito |
| --- | --- | --- | --- |
| snapshot / capabilities | Lê própria sala e catálogo de perfis/plataformas. | Não seleciona mode/core nem aprova conteúdo. | Snapshot assinado pode incluir sala própria fora da página pública. [SA01:236-257] |
| heartbeat | Atualiza Seen, sem mudar membership ou Ready. | Ausência de controle por aproximadamente 60 s pode fechar transport. | PING atualiza LastReceive do socket, não Seen do hub. [SA01:149-159; SA02:149-158] |
| create | Sem sala; capacity homologada; até 100 salas; perfil compatível com clientMaximumPlayers. | Approved/CatalogMatches e IDs/hashes exatos. | Cria waiting, generation=1 e host no slot 1. [SA01:126-145,170-173] |
| join | Sem sala; sala ainda não iniciada e não cheia; generation exata; perfil/bloqueios válidos. | Máximo do perfil deve caber no cliente; slot de 2 a 5. | Bump aumenta generation e limpa ready de todos. [SA01:174-181,218] |
| ready | Own + generation; stream ausente; revalida perfil para a capacidade. | Ready de lobby é diferente de frame READY após start. | Altera o booleano do membro. [SA01:182-184] |
| start | Host + generation; todos prontos; perfil aprovado para o número real presente. | allowedPlayerCounts deve conter 3 para testar três; máximo 4 não basta. | Congela roster/links; reserva 2 × Window por guest; aumenta generation. [SA01:185-192] |
| leave | Own e generation exata, antes de qualquer mudança. | Waiting: guest sai sozinho; host aposenta tudo. Após start: qualquer membro aposenta tudo. | Perda de rede/timeout de attachment não executa leave. [SA01:193,216-225] |
| failed | Own + generation e start realizado. | Falha terminal explícita; sem recuperação fabricada. | End passa para Unrecoverable; saída continua humana. [SA01:194; SA02:50-54] |
| chat | Own + generation; texto de 1 a 500 sem caracteres de controle; uma mensagem/s. | Retém até 32 mensagens ou 65536 bytes. | Operação social não altera prontidão. [SA01:195-198] |
| ticket / resume | Own + generation; perfil exato; started; proof RSA/EC; link autorizado; sem anexo ativo. | Host só acessa seus links; guest, o próprio link/slot. Stream não pode estar Unrecoverable. | Grant one-use de 60 s por attachment; resume não reduz roster. [SA01:199-209,270-287] |

- A tabela tem dez linhas por agrupamento: snapshot/capabilities e ticket/resume compartilham linhas. O código admite 12 ações.
- Nickname, limitado a 40, só é usado sem autoridade social validada. Chat, limitado a 500 caracteres e 32 mensagens/65536 bytes, permanece em memória.
- SNES com cinco jogadores exige o perfil administrativo snes-multitap-port2. O teto global de cinco não amplia outros motores.

### 6.19 Generation, epoch, tickets e saída humana

Generation pertence à composição da sala e aos comandos: começa em 1 e aumenta no join/reordenação e no start. Epoch pertence à sincronização do stream: começa em 1 e aumenta em pausa, detach, suspend, NEEDSYNC ou falha terminal. O snapshot pode conservar generation enquanto epoch muda muitas vezes na recuperação. Esses campos não são intercambiáveis; leave com epoch no lugar de generation não atende Own. [SA01:49,178-191,216-225, SA02:30-54]

Own valida sala existente, membership e generation exata antes de leave. Uma generation antiga recebe 409 STATION_MULTIPLAYER_GENERATION_MISMATCH sem remover o peer; o teste novo confirma a conservação da membership. O evento 4 herdado do cliente fazia uma tentativa com binding.generation e ignorava exceção. Esse caminho permite saída local com sala lógica ainda mantida; não prova que causou o incidente físico. A correção do cliente é preparada separadamente. [SA01:193,216-225, SA21; fonte cliente StationGameSession R124 herdada]

A correção do cliente se restringe à intenção humana de sair: após 409 de generation mismatch, obter snapshot assinado fresco e conferir roomId, recoveryProtocol, itemId, engineId, coreSha256, runtimeSha256, contentSha256, profileId e profileSha256 iguais ao binding anterior, com generation válida. Então enviar leave para a mesma sala com a geração atual. OwnRoom já null confirma saída. Não repetir em outra sala nem por erro 500/rede ambígua com UUID novo sem reconciliação. Esta é a regra do handoff coordenado; não é uma mudança deste patch de servidor. [SA01:263-268, SA03:34-36]

Ticket/resume exige Own atual, identidade completa de jogo/perfil, proof RSA-PSS ou EC-P256, link autorizado e ausência de anexo ativo. O grant dura 60 s e TakeTicket é one-use. A autorização é revalidada antes do upgrade e periodicamente. Revogação efetiva retira membership; indisponibilidade da consulta só encerra attachment para recuperação. O relatório não reproduz valores de tickets, tokens, chaves privadas ou senhas. [SA01:199-209,270-287, SA03:47-56, SA02:149-159]

Leave humano de guest em waiting remove somente esse guest; Bump limpa ready e recompõe slots. Leave do host em waiting ou de qualquer membro após start aposenta toda a sala e limpa ownRoom para todos. A reserva permanece enquanto writers/anexos podem usar as janelas; é liberada após o último Detach, em Unrecoverable e com retirementRequested. Os testes verificam essa sequência e a reserva de 1 MiB. [SA01:219-225, SA02:50-54, SA21]


### 6.20 Patch proposto de diagnóstico numérico, sem alteração de progressão

O patch acrescenta BarrierDiagnostics() a StationMultiplayerStream e room.barrierDiagnostics à ownRoom assinada. A listagem pública recebe null; somente o membro recebe detalhe. Não cria rota pública de inspeção nem logs com identidades. O objeto possui schemaVersion=1, epoch, state, hasPlayed, linkCount, expectedAttachments, attachedConnections, helloCount, pausedCount, readyCount, pendingBytes, suspendedParticipants e waitingReasons. [SA21, SA22]

Attachments contém linkOrdinal sequencial local, hostSide, attached, hello, paused, ready, acceptedBytes, deliveredBytes e pendingBytes. Não inclui IDs de sala/link/peer/licença/dispositivo, tickets, senhas, tokens, payload ou bytes de ROM. Um endpoint ausente não revela ID. Os watermarks separam READY ausente de replay pendente; não identificam por si qual função de núcleo ou UI deixou de responder. [SA22]

WaitingReasons enumera missing-attachment, awaiting-hello, participant-suspended, awaiting-core-pause, awaiting-ready, pending-replay ou unrecoverable. Awaiting-core-pause indica ausência do frame PAUSED, não uma medição de CPU. As razões podem coexistir. Em Playing, a lista fica vazia: DATA invalida ready do par tocado durante tráfego normal sem criar outra barreira, até Pause/NEEDSYNC. ReadyCount abaixo de 4 em Playing não significa falha de sincronização. [SA02:69-95, SA22]

SnapshotWithDiagnostics(bool member) obtém estado, epoch, pending, accepted, delivered, connections, hasPlayed e diagnóstico sob o mesmo lock. A projeção não mistura duas epochs. Nenhum método Attach/Detach/Receive/Next/End/RetireRoom, regra Own, perfil, reserva, timeout ou geração foi relaxado. Snapshot anterior permanece disponível aos consumidores existentes. [SA21, SA22]

A interface pode apresentar contagens e motivo, mas o patch de servidor não redesenha a tela nem força saída. Após homologação, coletar snapshot próprio, distinguir attachment/HELLO/PAUSED/READY de ACK/replay, correlacionar com diagnóstico nativo sanitizado e verificar recuperação. O novo campo é opcional para o cliente até existir prova de deploy da branch. [SA21-SA23]

| Arquivo proposto | Mudança | Alcance |
| --- | --- | --- |
| StationMultiplayerStream.cs | 37 linhas acrescentadas: diagnóstico e snapshot coerente. | Projeção sob lock; mutadores preservados. |
| StationMultiplayer.cs | RoomView usa snapshot coerente e expõe detalhe ao membro. | 3 linhas novas/2 substituídas; comandos preservados. |
| BarrierDiagnosticsChecks.cs | Fixture novo com 29 checks e classes reais. | Identidades sintéticas; relógio determinístico do hub. |
| Checks.cs + StationMultiplayer.Tests.csproj | Inclui e executa o arquivo novo de checks. | Dependências, target framework e flags de produção preservados. |


### 6.21 Validação executada: 29 checks novos e 1452 do domínio

A suite real tests/StationMultiplayer/StationMultiplayer.Tests.csproj foi executada em Release, com as referências reais do servidor e Notifications. Os 29 checks novos foram somados aos existentes: passed=true, checks=1452. A suite de capacidade informou 320 participantes sintéticos, 80 salas, 7864320 bytes bidirecionais e maximumReplayBytes=134217728. Os números descrevem exercícios em processo, sem WAN/TLS, autenticação real de dispositivo ou engine Android. [SA13, SA14, SA21, SA23]

O novo fixture verifica dois links/quatro attachments para três jogadores, isolamento de não membro, epoch coerente, HELLO/PAUSED completos e uma READY ausente com pending=0. Verifica espera após cinco minutos de relógio sintético com heartbeat/PING, última READY liberando Playing, reserva de 1 MiB, leave de generation antiga recebendo 409 sem retirar membro, leave humano aposentando sala e último detach liberando reserva. O relógio avança em 60 passos instantâneos; não houve cinco minutos de observação física. [SA21, SA23]

O segundo fixture entra em Playing, solicita NEEDSYNC, envia 3 bytes e registra pending-replay. DATA novo invalida READY somente do par afetado. READY com watermark antigo não libera a direção. Entrega e ACK drenam a janela, mas o último READY ainda é obrigatório. Também confirma retomada conjunta, failed gerando Unrecoverable explícito e saída/liberação humana. [SA21]

A primeira tentativa de restore encontrou bloqueio de rede NuGet no sandbox, sem falha de código. Npgsql 8.0.6 e as duas dependências Logging/DependencyInjection Abstractions 8.0.0 já estavam no cache local. Um feed temporário fora do checkout permitiu restore bem-sucedido. O csproj final só inclui o teste novo, sem allowtestfixture, troca de pacote ou workaround produtivo. Run com --no-restore terminou com exit=0. [SA23]

A suite HTTP de HttpChecks.cs e testes físicos de três aparelhos não foram executados nesta etapa. Os 1452 checks são do domínio, sem validar a API geral. Ativação exige validadores nativos, resposta v3 fresca assinada e matriz física separada com conteúdo/perfil autorizado. O recibo guarda comandos, scopes e hashes dos arquivos editados; o responsável pelo handoff realiza commit/publicação. [SA15, SA17, SA23]


### 6.22 Serviços comerciais no servidor: elegibilidade, transações e revogação

Este recorte complementa os serviços do cliente com o store real. EligibleDelivery exige product TURBORAMA_STATION_ANDROID, SKU STATION_ANDROID_LIFETIME_1_DEVICE, provisioning=PROVISIONED e condição financeira PAID. FindActivation exige licença ACTIVE, tipo LIFETIME, sem expiração, enrollment=PENDING_ENROLLMENT, maxActiveDevices=1, código não consumido nem expirado, verifier compatível e entrega elegível. O app não autentica por e-mail/senha nesse caminho. Dados de comprador pertencem à compra/produto de origem da licença. [SA11:27-48]

FindDevice exige dispositivo ACTIVE e licença ACTIVE/LIFETIME, sem expiração, BOUND e entrega elegível. FindSession procura digest do Bearer, autorização não expirada e geração corrente de revogação; revalida os vínculos. Sessão existente não preserva acesso após revogação, inelegibilidade financeira ou desativação do dispositivo. Sessão dura 180 s, desafio/grant 60 s; refresh cria nova sessão, sem mudar ownership. [SA11:86-117,333-362; SA09:97-164]

ActivateAsync usa transação SERIALIZABLE e repete somente conflitos de serialização/deadlock, até três tentativas com pequena espera aleatória. Não repete arbitrariamente o corpo da ativação. Licença/desafio/código são travados, consumidos e vinculados atomicamente; replay recebe 409. OpenSession consome desafio e registra sessão em operação transacional. O vínculo de segurança só se fortalece: request-proof e verified-app não aceitam downgrade explícito, recusado com 403. [SA11:120-317,365-384]

Perfil comercial projeta comprador da mesma compra/produto, displayName e profileVersion. Catálogo usa a biblioteca monitorada e jogos/metadados públicos; não inclui grant nem descritor do artefato da autorização posterior. O cache visual não expõe caminhos privados nem concede download. Essa família de rotas não recebe saves Android. [SA09:166-264, SA11:333-362]

O app pode mostrar biblioteca e cache assinado sem rede ou com sessão expirada. Já 403 LICENSE_DENIED/DEVICE_DENIED tem semântica de bloqueio persistente. O 404 mascarado de grant não deve ser convertido em revogação: a mesma resposta reúne diversas causas. Diagnose pelo contexto do pedido, authorize, perfil e sessão. Nenhuma licença produtiva foi consultada nesta autoria. [SA09:266-324, SA26]


### 6.23 Matriz de endpoints comerciais: esquemas, resposta e efeitos

A origem HTTPS pública é a configuração do cliente auditado; os paths/handlers são do head do servidor. Disponibilidade efetiva depende de flags e composição do host. O envelope comum é {keyId, payload, signature}: payload Base64URL contém UTF-8 assinado por RSA-PSS/SHA-256. SchemaVersion=1 e domain delimitam propósito; o cliente verifica identidade/contexto e chaves fixadas. TLS, assinatura de resposta, proof de pedido e token de sessão são verificações distintas. Valores de chaves/pins/tokens não estão publicados. [SA08-SA11, SA26]

A tabela registra nomes de campos, sem montar pedidos com credenciais. Os números são limites/defaults do código auditado ou do cliente citado, sem declarar configuração produtiva. O handler comercial de 10 s não limita toda a transferência; o controle online de 15 s não é deadline da barreira. O JSON detalha errors, auth, cache/retry e efeitos por endpoint. [SA08, SA03]

| Método e caminho | Pedido | Resposta | Autorização/efeito |
| --- | --- | --- | --- |
| POST /v1/station/activations/challenge | schemaVersion=1, domain=TurboRamaStationAndroid/<operação>/v1, productId=applicationId=TURBORAMA_STATION_ANDROID, deviceId canônico derivado da chave, clientVersion, deviceManufacturer, deviceModel e androidSdk; domain request-activation-challenge/v1, activationCode Base64URL de 32 bytes e devicePublicKey SPKI RSA-2048 Base64URL. | Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga activation-challenge/v1: deviceId, challengeId, nonce, expiresInSeconds=60 e security (requestProofVersion, keyAttestation, requireVerifiedApp, keyAttestationChallenge, serverTime). | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Não exige Bearer prévio; verifica código elegível e vínculo público da chave. Insere desafio vinculado à licença/dispositivo candidatos e às gerações de ativação/revogação. Ainda não consome a ativação. |
| POST /v1/station/activations/complete | StationDeviceEnvelope {payload, signature, attestationChain?, keySignature?}. Payload assinado: identidade comum com domain activate/v1, challengeId, nonce, activationCode, devicePublicKey e metadados do cliente. Limite exterior de 65536 bytes e payload decodificado até 8192. | Envelope JSON {keyId, payload, signature}; payload é Base64URL dos bytes UTF-8 assinados RSA-PSS/SHA-256. A carga contém schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga activated/v1: licenseId, deviceId, challengeId, nonce. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Prova do dispositivo RSA-2048 PSS/SHA-256, com assinatura de 256 bytes. Proof/attestation negociados conforme política vigente. A transação consome desafio/código, vincula um dispositivo, muda enrollment para BOUND e registra segurança. Entitlement lifetime de um dispositivo. |
| POST /v1/station/challenges | schemaVersion=1, domain=TurboRamaStationAndroid/<operação>/v1, productId=applicationId=TURBORAMA_STATION_ANDROID, deviceId canônico derivado da chave, clientVersion, deviceManufacturer, deviceModel e androidSdk; domain request-session-challenge/v1 e licenseId. | Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga session-challenge/v1: licenseId, deviceId, challengeId, nonce, expiresInSeconds=60 e security. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Dispositivo deve estar ACTIVE e vinculado a licença elegível BOUND. Não exige Bearer prévio. Insere desafio SESSION ligado à geração de revogação atual; não altera entitlement. |
| POST /v1/station/sessions | StationDeviceEnvelope assinado. Payload com identidade domain open-session/v1, challengeId, nonce, licenseId e metadados do cliente; extensões de segurança conforme negociação. | Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga session/v1: licenseId, deviceId, challengeId, nonce, sessionId, accessToken, expiresInSeconds=180, requestProof, verifiedApp e serverTime. Somente nomes de campos, sem credenciais reais. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Chave já vinculada, prova do desafio e segurança monotônica. Consome desafio e insere digest do accessToken, contexto sessionId e geração de revogação. Flags de request-proof/verifiedApp só fortalecem o vínculo. |
| GET /v1/station/me | Sem corpo. Authorization Bearer de sessão atual. | Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga profile/v1: licenseId, deviceId, sessionId, displayName limitado a 80 caracteres e profileVersion. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Sessão e entitlement elegíveis; perfil pertence ao comprador do mesmo produto/compra. Leitura do perfil no banco; não cria perfil, não edita comprador nem licença. |
| GET /v1/station/catalog?metadata=1 | Bearer. Metadata exatamente 1 acrescenta metadados; ausência retorna o catálogo básico. | Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga catalog/v1: licenseId, deviceId, sessionId, revision e items PublicValue. Contém jogos/metadados públicos; descritor de artefato e grant não chegam nessa resposta. | HTTPS com validação de hostname e pin no cliente; valores de pin/chave não reproduzidos. Sessão Bearer quando indicada; prova de pedido conforme política negociada. Pin TLS e assinatura de resposta são verificações distintas. Sessão elegível e biblioteca atual disponível. Leitura da biblioteca monitorada. Catálogo publicado não é inventário bruto de arquivos do servidor; alterações administrativas ocorrem fora desta rota. |
| GET /v1/station/covers/{coverId} | Bearer e coverId seguro do catálogo; não aceita URL arbitrária. | Blob de capa autorizado, mime/type e Content-Length. A rota usa no-store e nosniff. Não é envelope de grant nem conteúdo de jogo. | HTTPS com validação de hostname e pin no cliente; valores de pin/chave não reproduzidos. Sessão Bearer quando indicada; prova de pedido conforme política negociada. Pin TLS e assinatura de resposta são verificações distintas. Sessão, coverId e orçamento de origem/dispositivo. Leitura de blob. Rate limiter mantém janelas temporárias de contagem; não consome grant de jogo. |
| POST /v1/station/downloads/authorize | schemaVersion=1, domain=TurboRamaStationAndroid/<operação>/v1, productId=applicationId=TURBORAMA_STATION_ANDROID, deviceId canônico derivado da chave, clientVersion, deviceManufacturer, deviceModel e androidSdk; domain request-download/v1, itemId seguro e Bearer atual. | Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga download-grant/v1: licenseId, deviceId, sessionId, itemId, itemRevision, artifact (descritor), grantId e expiresInSeconds=60. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. DeviceId idêntico ao da sessão. O selo vincula licença, dispositivo, sessão, item, revisão, SHA/tamanho declarados e stamp do arquivo. Cria registro one-use de grant com path privado selado. O descritor público do artefato chega aqui, separado do catálogo. |
| GET /v1/station/artifacts/{grantId} | Bearer da mesma sessão e grantId canônico de 32 bytes. O cliente não fornece arquivo ou caminho arbitrário. | Application/octet-stream, Content-Length exato, no-store e nosniff. FileStream sequencial com buffer de 65536 bytes. Não assina cada chunk por envelope. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Grant não consumido/expirado, mesma licença/dispositivo/sessão, selo válido e item/revisão/SHA/tamanho/path/stamp correspondentes. A comparação dos metadados não recalcula todo o SHA durante o GET. UPDATE atômico consumed_at antes do stream. Cliente instala em geração transacional própria; servidor não gerencia save Android. |


### 6.24 Matriz comercial: erros, deadlines, cache e retries

As rotas comerciais compartilham leitura/validação de JSON, rate limiting e handler. Corpo normal admite até 8192 bytes; StationDeviceEnvelope exterior até 65536, com payload decodificado até 8192. JSON deve ser objeto, de profundidade até 16, sem duplicados; identidade exata e metadados de cliente limitados. Disabled retorna 503. O 429 comercial não define Retry-After nesta classe; online define 1. Erros usam schemaVersion/code/message, sem paths privados de artefato. [SA08:140-244, SA09:377-434, SA10:13-21,137-151]

O default por origem é 30 pedidos/minuto por rota, configurável até 65536. MaximumWindows tem default 4096 e faixa de 4096 a 131072. Capas têm orçamento adicional de 4096/minuto por dispositivo e 16384/minuto por origem. Esses números são defaults/limites configuráveis, não medição do host produtivo. Workers e filas limitados no app não determinam a cota ativa do servidor. [SA08:249-307, SA26]

| Endpoint | Erros/recusa | Deadline | Cache e retry |
| --- | --- | --- | --- |
| Desafio de ativação | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR. Código inelegível 403 STATION_ACTIVATION_INVALID; chave/dispositivo inválido 400 STATION_DEVICE_INVALID. | 10 s no handler; desafio 60 s. | Resposta de desafio não é uma licença reutilizável. Sem retry automático genérico no servidor; repetir produz outro desafio, sujeito à quota. |
| Conclusão de ativação | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR. 409 STATION_CHALLENGE_INVALID/CHALLENGE_MISMATCH/ACTIVATION_REPLAY/DEVICE_ALREADY_BOUND/TRANSACTION_CONFLICT; 403 STATION_ACTIVATION_INVALID/PROOF_INVALID/DEVICE_DENIED. | 10 s no handler; desafio deve permanecer válido e não consumido. | Ativação one-use. O store só repete transação serializável em deadlock/serialization, até 3 tentativas. Não repetir conclusão sem reconciliar uma resposta ambígua. |
| Desafio de sessão | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR. LicenseId inválido 400 STATION_LICENSE_INVALID; autorização 403 STATION_DEVICE_DENIED ou STATION_LICENSE_DENIED. | 10 s; desafio 60 s. | Desafio específico, não cache duradouro nem sessão. Novo desafio é necessário depois de expirar/consumir. |
| Abertura de sessão | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR. 409 STATION_CHALLENGE_INVALID/CHALLENGE_MISMATCH; 403 STATION_DEVICE_DENIED/PROOF_INVALID/LICENSE_DENIED/SECURITY_DOWNGRADE_DENIED; 503 STATION_SECURITY_UNAVAILABLE. | 10 s no handler; sessão autorizada 180 s no banco. | Bearer fica em memória no app. Cliente obtém nova sessão próximo da expiração; não prolonga a sessão pelo simples uso. Resposta/carga antiga não contorna revogação. |
| Perfil de comprador | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR. 401 STATION_SESSION_INVALID; 503 STATION_PROFILE_NOT_READY. | 10 s. | Cliente pode preservar projeção assinada conforme cache privado. O código de rota analisado não mostra mutação de nome pelo app. |
| Catálogo comercial | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR.401 STATION_SESSION_INVALID; 503 STATION_CATALOG_NOT_READY. | 10 s. | Cliente conserva catálogo assinado por licença/dispositivo, revisões e capas. Uma resposta de perfil/plataforma antiga não autoriza online. Falha transitória de rede não equivale a revogação. |
| Capas | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR.401 STATION_SESSION_INVALID; 404 STATION_COVER_NOT_FOUND; 503 STATION_CATALOG_NOT_READY; 429 STATION_RATE_LIMITED. | 10 s para operação de capa; escrita usa cancelamento da requisição conforme rota. | Cache privado por revisão no cliente, um worker e fila prioritária. O cliente adia 404 por 60 s e trata 429 com espera. Isso não comprova existência atual no servidor. |
| Autorização de download | Erros de identidade/formato 400; corpo grande 413; serviço desligado 503 STATION_DISABLED; rate limit 429 STATION_RATE_LIMITED; deadline 504 STATION_TIMEOUT; cancelamento do cliente 499; falha inesperada 500 STATION_INTERNAL_ERROR.401 STATION_SESSION_INVALID; 403 STATION_DEVICE_DENIED; 404 STATION_ITEM_NOT_FOUND; 503 STATION_DOWNLOAD_NOT_READY/ARTIFACT_NOT_READY. | 10 s no handler; grant 60 s. | Não reaproveitar grant após uso/expiração/troca de sessão. Retomada do app autoriza novamente e começa arquivo inteiro; rota não negocia Range. |
| Transferência do artefato | 404 STATION_GRANT_NOT_FOUND mascara grant inválido, expiração, consumo, sessão ausente/inválida, identidade diferente, selo inválido ou arquivo/revisão alterado. SuiteExceptions preservam seu status. IO/UnauthorizedAccess antes de enviar cabeçalhos também 404. Abortamento do cliente encerra stream; erro depois de cabeçalhos não vira um JSON completo. | Sem deadline geral de 10 s nessa rota. Abertura/consumo e CopyToAsync recebem RequestAborted; não foi encontrado prazo total de transferência. | Grant é consumido antes da emissão do arquivo. Falha parcial exige novo authorize; sem retomada Range/offset no contrato analisado. Um GET retry com mesmo grant não é equivalente a uma segunda transferência. |


### 6.25 Grants, downloads e armazenamento: garantias e limite do hash

Authorize exige sessão atual e deviceId idêntico ao da sessão. Resolve o artefato privado da biblioteca vigente e sela associated data contendo licença, dispositivo, sessão, item e grant. O corpo selado guarda path privado, revisão, SHA declarado, tamanho e lastWriteUtcTicks. O grant tem 32 bytes aleatórios e validade de 60 s; a resposta assinada leva artifact descriptor, itemRevision e grantId. O descritor não vem no catálogo. [SA09:219-264]

Consume verifica grant canônico, cipher presente, registro válido, Bearer, mesma licença/dispositivo e associação à mesma sessionId. Mudar a sessão não transfere automaticamente o grant. Resolve o artefato e compara path/revisão/SHA declarado/tamanho/mtime ao selo; consome o registro atomicamente antes de transmitir. Essas comparações não recalculam todo o SHA do arquivo por GET. As causas mascaradas recebem 404 GRANT_NOT_FOUND; falha parcial de transferência exige novo grant. [SA09:266-324, SA11:407-434]

A transferência abre FileStream sequencial com buffer de 65536 bytes, verifica tamanho/stamp antes dos headers, informa Content-Length e copia com RequestAborted. O contrato não oferece Range/offset. O cliente reinicia o arquivo inteiro e limita uma transferência, 32 pendentes e histórico de 48. Java instala por gerações privadas e recibos transacionais, remove apenas os arquivos que possui e conserva saves/arquivos desconhecidos. Essas rotas não recebem upload ou restore de saves Android. [SA08:91-137, SA26]

O hash completo de ROM durante download/instalação Java está desativado no snapshot herdado. O descritor assinado e seu SHA continuam como metadados; a publicação exige tamanho/formato/paths seguros. A preparação online é outro fluxo que precisa calcular/comparar a identidade real de conteúdo para o perfil autorizado. O diagnóstico da barreira não altera essas garantias. O dossiê não deve afirmar SHA local de download validado neste caminho atual. [SA26, SA01:126-145]


### 6.26 Matriz multiplayer e legado: contratos, autenticação e limites

Rotas v3 aplicam no-store/nosniff, recusam query, exigem Bearer canônico e proof negociado e assinam snapshot após revalidar sessão. A prova HTTP associa método, path, token e body. Ticket WebSocket assina GET com body vazio e é consumido antes do upgrade. A identidade admitida tem licença/dispositivo elegíveis; ownership não é inferido do nome de usuário nem da senha de conexão externa. [SA03:10-56, SA07:12-22]

O cache de 64 recibos por peer/requestId/fingerprint oferece idempotência ao mesmo UUID e conteúdo. Não torna uma mutação com UUID novo segura após timeout ambíguo. Limites de 20 ações/s e chat de uma mensagem/s recebem 429 e Retry-After=1. Ticket/resume só entregam anexo próprio. As páginas públicas de 32/100, até 100 salas, não revelam connectionPassword, messages ou diagnóstico detalhado ao não membro. [SA01:149-212,235-268, SA03:37]

Lobby social v1, recuperação v2 e multiplayer v3 coexistem. Rotas legadas usam OnlineCommand/EventsRequest e station-relay.v1/station-stream.v2. V3 usa StationMultiplayerCommand e station-stream.v3/TSR3, ainda em URL /v1. Online/v1 no domain de assinatura não distingue relay: capability, multiplayerVersion, recoveryProtocol e binding exato são necessários. Station:Online:Enabled e MultiplayerEnabled devem permitir v3, independentemente das flags legadas RelayEnabled/RecoveryEnabled. [SA01:34,252-268, SA07:25-32,62-107]

| Endpoint | Request/response | Auth/ownership | Timeout/cache/erro |
| --- | --- | --- | --- |
| POST /v1/station/online/multiplayer/command | StationMultiplayerCommand: action, requestId (UUID D); roomId?, itemId?, contentSha256?, engineId?, coreSha256?, runtimeSha256?, profileId?, profileSha256?, capacity (default 0), generation (default 0), linkId?, value (default false), nickname?, text?, clientMaximumPlayers (default 4), page (default 0), roomPageSize (default 100). JSON objeto até 8192 bytes, profundidade 16, sem duplicados; query proibida. Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga online/v1: licenseId, deviceId, sessionId, requestId e snapshot. Snapshot com schemaVersion=1, multiplayerVersion=3, capability=station-multiplayer.v3, instance, revision, selfId, platformPolicy, profiles, rooms, room e ticket. O patch adiciona room.barrierDiagnostics apenas ao membro. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Bearer canônico de 32 bytes, header de 50 caracteres, proof conforme sessão e autenticação antes/depois da ação. AdmissionGate recusa create/join se existir membership legado. Salas, peers, anexos, replay e recibos ficam em memória. Own exige membership e generation exata antes de leave/ready/start/ticket. Só o host inicia; leave de qualquer membro após start aposenta toda a sala. | Controle de 15 s; ticket de 60 s. Peer sem sala pode expirar após 60 s; um membro não é removido apenas por atraso. No-store/nosniff. Cache de 64 recibos por peer: mesmo requestId e fingerprint é idempotente; outro conteúdo recebe 409 REQUEST_REUSED. Limite de 20 ações/s. Erro 500/timeout ambíguo exige reconciliar snapshot antes de mutação com UUID novo. 400 STATION_MULTIPLAYER_* para request/page/action/body/query; 413 BODY_TOO_LARGE; 401 SESSION_INVALID/REQUEST_PROOF_REQUIRED; 403 HOST_REQUIRED/LINK_FORBIDDEN/BLOCKED; 409 GENERATION_MISMATCH/GAME_MISMATCH/NOT_READY/UNRECOVERABLE/ALREADY_*; 429 RATE_LIMIT ou CHAT_RATE_LIMIT com Retry-After1; 503 DISABLED/FULL/REPLAY_FULL; 504 TIMEOUT. |
| GET (WebSocket upgrade) /v1/station/online/multiplayer/relay | Upgrade WebSocket, subprotocol station-stream.v3, sem query. Authorization StationRelay <ticket>, token one-use de 32 bytes, com proof do GET e body vazio. 101 com station-stream.v3 e frames binários TSR3. Erros anteriores ao upgrade usam JSON finito {schemaVersion:1, code, message:code} e Content-Length. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. TakeTicket valida sala/generation/link/slot, assinatura e anexo exclusivo. AuthorizeRelay revalida dispositivo/licença em até 5 s antes do upgrade e durante Watch. Memória limitada: 3 jogadores, 2 links, 4 attachments e reserva de 1048576 bytes. Janela de 262144 bytes por direção; libera reserva após aposentadoria e último detach. | Auth de 5 s; Watch a cada 10 s. Fecha attachment se heartbeat de controle ausente ≥60 s ou frame recebido ausente ≥30 s. Sem prazo global de READY. CloseOutput de até 2 s depois de juntar writer/watch. No-store. Ticket consumido não pode ser reutilizado; resume gera outro. Sala, links e replay persistem na perda de rede. Ausência de tráfego fecha attachment, sem escolher saída humana. 400 STATION_MULTIPLAYER_UPGRADE_REQUIRED/frame inválido; 401 TICKET_INVALID/SESSION_INVALID; 409 ALREADY_ATTACHED/UNRECOVERABLE/proof-watermark errors; 503 DISABLED; 504 TIMEOUT antes de headers. Erro de protocolo depois do upgrade encerra stream em Unrecoverable; erro de transporte pausa para recuperar. |
| POST /v1/station/online/command | OnlineCommand legado: action/requestId e campos opcionais nickname, roomId, peerId, itemId, engineId, contentSha256, optionsSha256, coreSha256, runtimeSha256, address, port, text, value, page, transport, inviteCode, recoveryProtocol e generation, conforme ação. Não substituir por StationMultiplayerCommand. Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga online/v1 com snapshot legado de lobby, pessoas, convites e sala v1/v2. O mesmo domain online/v1 assina v3; snapshot/capability/protocolo distinguem a família. | HTTPS com hostname e pin validados pelo cliente; valores de chaves/pins omitidos. Bearer e prova de pedido quando indicados. TLS e assinatura da resposta são verificações distintas. Sessão e proof negociados. AdmissionGate impede create/join legado de identidade já em v3. Block também afeta a sala multiplayer. Estado social e legacy membership em memória; a coordenação explicitamente impede duas memberships simultâneas da mesma identidade. Mantém operações sociais existentes. | Handler de 15 s. Timeouts legados de lobby de 30/90 s não são prazos da barreira v3. No-store/nosniff; recibos, eventos e revisões do domínio legado. HTTP 200 desse endpoint não demonstra capacidade v3. STATION_ONLINE_DISABLED503, SESSION_INVALID401, BODY_INVALID400/BODY_TOO_LARGE413, erros de ação/autorização/geração do domínio legado,429 Retry-After1,504 STATION_ONLINE_TIMEOUT. |
| POST /v1/station/online/events | EventsRequest {requestId, instance?, revision, page}. Bearer e proof conforme a segurança da sessão. Envelope JSON {keyId, payload, signature}. Payload Base64URL contém bytes UTF-8 assinados por RSA-PSS/SHA-256. A carga inclui schemaVersion/domain/productId/applicationId e a identidade/contexto próprios da operação. Carga online/v1 com requestId e snapshot depois de mudança da revisão ou espera limitada. A sessão é reautenticada após esperar. | HTTPS com validação de hostname e pin no cliente; valores de pin/chave não reproduzidos. Sessão Bearer quando indicada; prova de pedido conforme política negociada. Pin TLS e assinatura de resposta são verificações distintas. Só entrega snapshot novo a sessão ainda válida; revogação revalida no fim. Leitura e presença do domínio legado; entrega não liga motores, não cria grant de ROM. | Espera por evento de até 10 s, dentro do handler de 15 s. no-store; long polling usa instance/revision. Não substitui heartbeat/progresso da barreira v3. 401 SESSION_INVALID; 400 BODY_INVALID; 413 BODY_TOO_LARGE; 429 limitações do hub; 503 ONLINE_DISABLED; 504 ONLINE_TIMEOUT. |
| GET (WebSocket upgrade) /v1/station/online/relay | Authorization StationRelay <ticket> e proof, sem query. Subprotocol station-relay.v1 ou station-stream.v2 conforme lease. Não usa station-stream.v3/TSR3. 101 com o protocolo selecionado; JSON finito se o upgrade for recusado. V1 faz forwarding simples; v2 oferece recuperação de stream entre o par. | HTTPS com validação de hostname e pin no cliente; valores de pin/chave não reproduzidos. Sessão Bearer quando indicada; prova de pedido conforme política negociada. Pin TLS e assinatura de resposta são verificações distintas. Ticket do domínio legado; v2 exige RecoveryEnabled e autorização de relay conforme dispositivo. Domínio legado independente, interoperando no bloqueio de admission. Não compartilha formato de payload v3 por ter /v1 no URL. | Timeouts pertencem ao relay selecionado. Não aplicar as regras de quatro attachments v3 a uma sala de dois endpoints v2. no-store; ticket one-use. Flags legadas e o endpoint antigo não demonstram v3 ativo. 503 STATION_ONLINE_RELAY_DISABLED/STATION_RECOVERY_DISABLED; 400 UPGRADE_REQUIRED; 401 TICKET_INVALID/SESSION_INVALID; 409 STATION_RECOVERY_PROTOCOL_MISMATCH; 504 ONLINE_TIMEOUT. |
| GET local /ready/station/online; /ready/station/online/diagnostics | Operador local. Diagnostics exige Host localhost/IP loopback, remoto loopback e ausência de forwarded headers. Agregados legacy/recovery/multiplayer conforme flags. O diagnostics atual pertence exclusivamente a recovery v2. O novo diagnóstico v3 entra no snapshot assinado do membro, sem nova rota de operador. | Restrição de endereço/host, endpoint interno. Nenhuma consulta a produção foi realizada. Leitura numérica; não altera configurações nem ativa kit. | Leitura local de snapshot; sem promessa de prontidão de jogo ou engineId. No-store. Agregados activeRooms/connections/budget não mostram CPU do núcleo ou vídeo e não liberam títulos por cache. 404 para acesso não autorizado por localidade; 503 quando flags necessárias desligadas. |
| Não mapeado neste head Família de mídia implementada no cliente; sem rota correspondente na árvore aplicada a6b58e9/docs524d2eb | Não declarar contrato produtivo com base apenas no cliente. Não observado: nenhuma chamada produtiva efetuada. | Implementação existente em branch histórica separada não prova composição no host atual. Sem prova de serviço atual publicado/ativo. Deve verificar branch/host/config antes de prometer feature. | Não determinado neste host. Capacidades/caches do cliente não suprem rota ausente no head auditado. A ausência de mapeamento na árvore é gap de composição; não é afirmação de HTTP404 real em produção. |


### 6.27 Kit R134: diferenças de identidade e condições exatas para ativação

O handoff público R133 não deve ser usado como lista final de engineId da R134. A R134 recompôs quatro identidades de engine/core/runtime, preservando a baseline. Mesmo um título com perfil anterior pode deixar de corresponder aos novos binários. Não contornar mismatch com ID legado, core alternativo ou capabilities de cache. Os IDs extraídos do kit R134 são informações públicas de handoff; este relatório não republica os artefatos nativos privados. [SA17, SA18, SA24]

O kit atual deve ser aplicado pelo responsável Linux autorizado, usando o conjunto privado original: ARTIFACTS com seis bibliotecas e três JSON técnicos, DELIVERY com runtime/package congelados, TOOLS na versão exata, private ledger e CANDIDATE como caminho absoluto ainda inexistente. Deve resolver a configuração ativa: outputDirectory, catálogo, índice de registry/engineManifest e preparedModes pertencem ao mesmo conjunto vigente; confirmar também os módulos Python realmente importados e seus hashes. O handoff público sanitizado não substitui o input privado da ativação. [SA17:46-60]

RequireExplicitEngineModes deve permanecer true. Os controllerProfiles administrativos devem ser objetos com schema/controller/devices/coreOptions, e não uma lista de nomes de assets. Exigem UTF-8 canônico, ordem determinística, ausência de BOM/terminador externo e vínculo SHA de perfil. validate_modes, prepare e validate_manifest devem usar os paths/config/ports vigentes e preservar a baseline de 5176 perfis/321 modos e os fluxos Sony/SNES/Mega existentes. PSX com HLE automático continua recusado; presença de arquivo não cria homologação. [SA17:64-85]

A aplicação nativa administrativa exige getuid=0 e PKEXEC_UID original do operador, scan.lock, selos, hashes de baseline e ledger privado. Não se pode forjar variável de ambiente para contornar a validação. A publicação de modes, engines e profiles revalida os arquivos e faz rollback dos bytes originais dos três arquivos se houver falha ou mudança de baseline. Reiniciar a API não substitui consistência. Nenhum desses passos foi executado nesta auditoria. [SA17:92-105]

O ProfileMonitor verifica o arquivo a cada 10 s, exige caminho absoluto regular sem reparse, tamanho máximo de 16 MiB e stamp estável antes de ReplaceProfiles. Registro inválido mantém a última versão válida. Perfis equivalentes preservam os objetos usados pelas salas existentes; o novo registro não muda o binding de uma sala já iniciada. Isso permite reload de dados sem restart da API, mas o scanner Python executa uma vez e seus imports/config precisam ser resolvidos separadamente. [SA01:96-111, SA05:20-65, SA17:102]

O kit descreve 78 modos/44 jogos preparados: N64 66 modos/33 jogos, GameCube 9/8, Wii 3/3. PSX tem zero modos novos confirmados e 84 pendências de HLE. Esses números indicam preparação e recusas, não aplicação produtiva ou gameplay. Depois da aplicação, exigir snapshot fresco assinado station-multiplayer.v3 que corresponda a content/core/runtime/profile/mode/allowedPlayerCounts do título real. ServerReady=true, HTTP 200, PONG, perfil em cache e relay v2 não substituem essa prova. [SA17, SA18, SA24]

O patch numérico é aditivo à API e exige build/deploy separado se o operador quiser receber barrierDiagnostics. Publicar branches de auditoria, documentos e builddocs não ativa o kit de engines nem atualiza o executável produtivo. O campo pode estar ausente até existir deployment confirmado; o cliente deve tratá-lo como opcional. Nesta tarefa foi autorizada publicação de fontes/handoff, sem deploy de servidor. [SA22, SA23]

| Plataforma | Identidade do handoff R133 | Identidade do kit R134 |
| --- | --- | --- |
| PSX | pcsx-rearmed-ff81ed17-player-v3-42e4ca5f2acc | pcsx-rearmed-ff81ed17-player-v3-69ac2b703f03 |
| N64 | mupen64plus-ae-33bf7021-n64-v3-6dd47d4e0092 | mupen64plus-ae-33bf7021-n64-v3-5f56099c433f |
| GameCube | dolphin-5102a033-gamecube-v3-5912af1feeef | dolphin-5102a033-gamecube-v3-9c87e2ec4c79 |
| Wii | dolphin-5102a033-wii-v3-5912af1feeef | dolphin-5102a033-wii-v3-9c87e2ec4c79 |


### 6.28 Matriz obrigatória de homologação em três jogadores

O teste físico deve usar título conhecido, conteúdo identificado e perfil assinado com 3 explicitamente presente em allowedPlayerCounts. Selecionar um modo de máximo 4 jogadores não basta. Os três dispositivos devem usar o mesmo engine/core/runtime/profile e identidade de conteúdo. Os dois guests entram na mesma sala e geração; o host inicia após os três estarem prontos no lobby. Um perfil SNES de três jogadores já homologado pode isolar a barreira enquanto os novos engines N64/GC/Wii estiverem pendentes, sem estender a homologação destes últimos. [SA01:126-192, SA17:108, SA21]

Registrar snapshots próprios sanitizados com geração/epoch/state, quantidade de jogadores e contadores de link/attachments/HELLO/PAUSED/READY/pending/hasPlayed. Não exportar IDs de sala/peer, tokens, senha, serial USB ou caminho de ROM. No start de três jogadores, observar quatro attachments, quatro HELLO/PAUSED/READY e pending zero, depois confirmar execução do jogo, vídeo, áudio e inputs nos três aparelhos. Só a observação física confirma gameplay; contadores e frontend aberto não certificam o núcleo. [SA21-SA23]

Na recuperação, interromper e restabelecer a rede de um guest, alternar foreground/background e produzir replay controlado com input legítimo. A barreira deve pausar globalmente, preservar roster, aumentar epoch, reconstruir anexos com tickets frescos, drenar todas as janelas, receber todos os READY da mesma época e retomar conjuntamente. Nenhum guest deve ser retirado automaticamente para obter Ready. Saída humana de qualquer participante após start deve confirmar ownRoom=null nos três e retorno do aplicativo ao lobby sem ANR.

Provocar leave com geração anterior ao start para confirmar 409 sem saída e validar o helper humano do cliente após snapshot fresco do mesmo binding. Timeout ambíguo exige reconciliar ownRoom antes de outra mutação. Verificar também failed/unrecoverable com saída explícita, recusa de perfil incompatível, manutenção da última classificação válida após arquivo administrativo inválido e indicação de READY ausente sem autoexit. Essa matriz é um requisito pendente; esta auditoria cumpriu somente a parte em processo. [SA01-SA05, SA21-SA23]

| Caso | Critério de aceitação | Evidência a guardar |
| --- | --- | --- |
| Três jogadores: positivo | Quatro READY, pending=0 e gameplay/inputs nos três. | Snapshot próprio, logs numéricos nativos e observação física. |
| Um guest sem READY, com PING | Permanece Synchronizing e mostra awaiting-ready; saída humana funciona. | ready=3, expected=4, pending=0; hasPlayed não pode ser falso positivo. |
| Anexo ausente | Missing-attachment; sem início automático com outro guest. | attached<expected; reconecta ao mesmo link/slot. |
| Replay pendente | ACK drena bytes, mas não libera sem READY atualizado. | pending>0 → 0; epoch coerente e watermark Accepted. |
| Perda de rede / suspensão | Pausa global; recupera com roster constante e play conjunto. | epoch aumenta, tickets one-use frescos; sem leave automático. |
| Leave com generation antiga | 409 conserva sala; retry humano da mesma sala com geração fresca confirma saída. | Generation mismatch, snapshot assinado e ownRoom=null. |
| Saída de host/guest após start | OwnRoom=null para todos; frontend retorna; reserva=0 após detach. | Sem ANR, socket abandonado ou sala lógica fantasma. |
| Falha terminal | Unrecoverable explicado; resume recusado; leave disponível. | Failed/erro de protocolo; sem promessa de recuperação fabricada. |
| Perfil [2,4] versus três | Recusa três por count; sem bypass. | Snapshot exato com quantidade explicitamente aprovada. |
| Baseline/kit administrativo | Validadores atuais, rollback e perfis baseline preservados. | Recibo da aplicação nativa e hashes/config/imports corretos. |


### 6.29 Gaps remanescentes e condições para fechar o handoff

O dossiê anterior descreve mídia/carrossel no cliente, mas a árvore aplicada a6b58e9/docs524d2eb não mapeia as rotas correspondentes. Existe uma branch histórica de mídia separada; isso não prova sua composição no host produtivo nem uma falha HTTP observada. Antes de prometer clips, confirmar a fonte, flags, host e mídia atuais. Nenhum pedido produtivo foi feito para comprovar status. [SA25, SA26]

Este recorte SQL complementa o dossiê de cliente com lifetime de um dispositivo, entitlement pago, fortalecimento monotônico de segurança e masking404 de grants. Rate limiting é configurável: números de código devem ser rotulados como defaults e limites, sem afirmar cota ativa. Catálogo contém jogos/metadados; artifact/grant chegam somente na autorização. Hash declarado e hash local da preparação online permanecem distintos da instalação Java, que omite o SHA completo de ROM. [SA08-SA11, SA26]

Ainda faltam recibo administrativo Linux de aplicação dos IDs R134 atuais, snapshot v3 fresco da API com os mesmos binários/conteúdo e teste físico continuado com três aparelhos. A auditoria não comprova execução de núcleo em cada attachment, causa física da ausência de READY, latência WAN, timeout do proxy TLS nem valores ativos das flags do host. Os 29 checks novos aprovados verificam regras de domínio e precisão do diagnóstico; não substituem esses itens. [SA17, SA21-SA25]

Para publicar, o responsável deve revisar o patch aditivo e documentos, conservar artefatos privados fora dos repositórios, incluir o recibo de 1452 checks com scope correto e criar os commits nas branches autorizadas. Deployment requer autorização operacional e aplicação pelo procedimento nativo do host vigente. Não concluir que o servidor está ativado, que três jogadores estão homologados ou que o loading foi corrigido em produção só porque a fonte compilou e o teste local passou. A entrega acrescenta observabilidade e reproduz a condição bloqueante; a correção de saída humana no cliente é validada separadamente.


## Índices completos

- [Fontes Java e composição](java-source-composition.json)
- [Funções Java e linhas](java-methods.json)
- [Fontes de integração e compilação](integration-build-source-index.json)
- [Todas as entradas do APK](package-entries.json)
- [Bibliotecas](native-libraries.json)
- [DEX](dex-entries.json)

## Fontes consultadas

- **SV01** Regras, cadeia de revisões e separação entre fonte, pacote, instalação, autenticação e execução. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/AGENTS.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/AGENTS.md)
- **SV02** Escopo R134: famílias alteradas e serviços preservados; limites da publicação. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-settings-refinement-r134-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-settings-refinement-r134-20261011/README.md)
- **SV03** Delta efetivo herdado da publicação Java: linhas DEMO e guardas sem rede. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/local-sony-demos/recipe/patch_frontend.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/local-sony-demos/recipe/patch_frontend.py)
- **SV04** Composição dos serviços, armazenamento no_backup, identidade Android e integração do perfil. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationAndroid.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationAndroid.java)
- **SV05** Métodos/rotas, esquemas de ativação/sessão/perfil/catálogo/grants/mídia, assinatura e erros. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationApi.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationApi.java)
- **SV06** Domínios v1, formatos de identificadores, identidade de requisição e limites de corpo. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationProtocol.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationProtocol.java)
- **SV07** Allowlist HTTP, HTTPS/pin, cabeçalhos, timeouts, tamanho de requisições e recusa de redirects. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationHttp.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationHttp.java)
- **SV08** Chaves Keystore RSA2048 e EC P256, atestação, reuso e limites. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCrypto.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCrypto.java)
- **SV09** Prova vinculada a método, destino, corpo, credencial, tempo e nonce. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationRequestProof.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationRequestProof.java)
- **SV10** Licença persistida, sessão em memória, renovação e leases de concorrência. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationSessions.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationSessions.java)
- **SV11** Login, cache offline, perfil, renovação, invalidação e autorização vinculada a catálogo. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoordinator.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoordinator.java)
- **SV12** Interface de acesso, Manter conectado, armazenamento e navegação após login. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/LoginActivity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/LoginActivity.java)
- **SV13** Fila de login, callbacks, autorização e mensagens de erro. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/StationLogin.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/StationLogin.java)
- **SV14** Modelo assinado de itens/metadados/coleções e limite de 4096. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCatalog.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCatalog.java)
- **SV15** Cache privado assinado, monotonicidade de revisão e bloqueio persistente. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCatalogStore.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCatalogStore.java)
- **SV16** Publicação da biblioteca, refresh, polling, downloads, capas e identificação de instalados. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java)
- **SV17** Cache de capas por revisão, pré-indexação, reaproveitamento e falhas 404/429. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverStore.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverStore.java)
- **SV18** Fila única de IO/decode, prioridades, gerações, foreground e prefetch. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java)
- **SV19** Estados, fila, grant novo, pausa/cancelamento/persistência e limite de transferências. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloads.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloads.java)
- **SV20** Classificação e espera de falhas transitórias sem repetir grant consumido. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadRetry.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadRetry.java)
- **SV21** Central atual de downloads, progresso, estimativa, botões e lifecycle. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java)
- **SV22** Avisos e confirmação de cancelamento. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadUi.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadUi.java)
- **SV23** Notificação foreground, bloqueio parcial de energia e ausência de serviço ocioso. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/DownloadService.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/DownloadService.java)
- **SV24** Descritor de artefato, formatos, caminhos e limites de tamanho/contagem. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationArtifact.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationArtifact.java)
- **SV25** Transação, extração, CUE/M3U, recibo, descoberta de instalados e remoção que preserva saves. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationInstaller.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationInstaller.java)
- **SV26** Escrita limitada/atômica, fsync, detecção de tipos e política de hash. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFiles.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFiles.java)
- **SV27** Preparação de raiz canônica, prova de escrita, espaço livre e erros de armazenamento. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationStorage.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationStorage.java)
- **SV28** Revisão do bundle de recursos e política de reparo/substituição. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationResourceBundle.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationResourceBundle.java)
- **SV29** Cópia de recursos empacotados que preserva adições do usuário. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationBundledFiles.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationBundledFiles.java)
- **SV30** Contrato dos vídeos de menu, domínio, dimensões/fps/áudio e limites. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationMediaCatalog.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationMediaCatalog.java)
- **SV31** Cache persistente de mídia por hash, validação e publicação transacional. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationMediaStore.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationMediaStore.java)
- **SV32** Prefetch de mídia, intervalo, prioridade, suspensão e checagem H264. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCarouselMedia.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCarouselMedia.java)
- **SV33** Reuso de tarefas e retorno sem encerrar processos ou tarefas de jogo. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/StationTaskNavigation.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/StationTaskNavigation.java)
- **SV34** Seleção de tarefa pertencente ao pacote e guarda contra abertura durante jogo. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/StationTaskPolicy.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/auth/StationTaskPolicy.java)
- **SV35** Contagens, correlação, categorias de erro e tags de item/capa sem credenciais. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDiagnostics.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDiagnostics.java)
- **SV36** Parsing de Retry-After numérico/data HTTP e limites. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationRetryAfter.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationRetryAfter.java)
- **SV37** Provas históricas isoladas da fila/recuperação; não é nova homologação R134. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-download-center-r90-20261009/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-download-center-r90-20261009/README.md)
- **SV38** Fonte completa R124, classes preservadas e qualificação física limitada. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/README.md)
- **SV39** Base pública, produto/aplicação e clientVersion legado; valores de chaves/pin omitidos. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationConfig.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationConfig.java)
- **SV40** Busca nativa e apresentação enquanto digita; barra de progresso no carrossel. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/native/d0/native_search_download.h — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/native/d0/native_search_download.h)
- **OFF01** Política de composição, preservação e separação das evidências — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/AGENTS.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/AGENTS.md)
- **OFF02** Composição e escopo atual R134 — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-settings-refinement-r134-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-settings-refinement-r134-20261011/README.md)
- **OFF03** 50 plataformas, rotas, processos, componentes e limites — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/evidence/launch-matrix-r120.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/evidence/launch-matrix-r120.json)
- **OFF04** Owners Sony internos e validação R131 — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/README.md)
- **OFF05** Publicação de catálogo, workers, capas, refresh e instalados — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java)
- **OFF06** Mapeamento explícito de plataformas — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationPlatforms.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationPlatforms.java)
- **OFF07** Biblioteca/cache/sessões/autorização — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoordinator.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoordinator.java)
- **OFF08** Modelo, ações, comandos e despacho — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/native/d0/native_carousel.cpp — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/native/d0/native_carousel.cpp)
- **OFF09** Sinopse, contagens, classificação e ficha — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/native/d0/native_info.h — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/native/d0/native_info.h)
- **OFF10** Fotos console, cache e custos nominais — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/console-panel-r133/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/console-panel-r133/README.md)
- **OFF11** Painel gráfico R134 e controles — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/settings-refinement-r134/java/org/emulationstation/frontend/station/StationGraphicsPanel.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/settings-refinement-r134/java/org/emulationstation/frontend/station/StationGraphicsPanel.java)
- **OFF12** Persistência da máscara, fundo e economia — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java)
- **OFF13** Reta/Diagonal/De lado e prioridades — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-carousel-diagonal-online-compact-r123-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-carousel-diagonal-online-compact-r123-20261011/README.md)
- **OFF14** Orçamento de frames e evidência física delimitada — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/README.md)
- **OFF15** Fila única, foreground e preempção de capas — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java)
- **OFF16** Cache progressivo e preparação incremental LED — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-smooth-preload-r115-20261010/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-smooth-preload-r115-20261010/README.md)
- **OFF17** Central, ETA, ações e bitmap cache — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java)
- **OFF18** Cache GL, chave, três entradas e 8MiB — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/native/d0/native_magazine_field.h — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/native/d0/native_magazine_field.h)
- **OFF19** Barreira loading e marcos de progresso — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/startup-cleanup-r132/recipe/patch_loading.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/startup-cleanup-r132/recipe/patch_loading.py)
- **OFF20** Prewarm no SDL/GL e contexto — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/startup-cleanup-r132/recipe/r132_startup_loading.h — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/startup-cleanup-r132/recipe/r132_startup_loading.h)
- **OFF21** Player, decoder e lifecycle baseline — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java)
- **OFF22** Loop persistente e reutilização decoder R130 — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/local-sony-demos/recipe/patch_video_loop.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/local-sony-demos/recipe/patch_video_loop.py)
- **OFF23** Estados, fila, retry, pausa e limpeza da tentativa — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloads.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationDownloads.java)
- **OFF24** Notificação foreground e wake lock — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/DownloadService.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/DownloadService.java)
- **OFF25** Instalação transacional, não hashing ROM e remoção — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationInstaller.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationInstaller.java)
- **OFF26** Neo Geo/MAME, CHD, BIOS, nomes e limites — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-neogeo-cd-r65-20261007/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-neogeo-cd-r65-20261007/README.md)
- **OFF27** Auditoria R126 das rotas/binários preservados — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/audits/station-online-system-engines-20261011/evidence/current-apk-audit.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/audits/station-online-system-engines-20261011/evidence/current-apk-audit.json)
- **OFF28** Proveniência versões de motores — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/audits/station-online-system-engines-20261011/remaining-systems/matrix.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/audits/station-online-system-engines-20261011/remaining-systems/matrix.json)
- **OFF29** Integração normal N64, processos, storage e retorno — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-emulators-r15-20261005/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-emulators-r15-20261005/README.md)
- **OFF30** Dolphin/N64 owners reais e proveniência — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-dolphin-online-r126-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-dolphin-online-r126-20261011/README.md)
- **OFF31** Inventário controle por motor e limites — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/REVIEW-CONTROLLER-VISIBILITY-R120.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/REVIEW-CONTROLLER-VISIBILITY-R120.md)
- **OFF32** Preparação automática das BIOS existentes — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-neogeocd-bundled-bios-r66-20261007/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-neogeocd-bundled-bios-r66-20261007/README.md)
- **OFF33** Recibos e limites das provas CD; diretório de evidências — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-neogeocd-bundled-bios-r66-20261007/evidence — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-neogeocd-bundled-bios-r66-20261007/evidence)
- **OFF34** Adaptador Dolphin completo — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/java/client/src/java/org/emulationstation/frontend/station/StationControllerPresence.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/java/client/src/java/org/emulationstation/frontend/station/StationControllerPresence.java)
- **OFF35** 68 provas isoladas controle — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/evidence/controller-presence-r120.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/evidence/controller-presence-r120.json)
- **OFF36** Contrato PS3 runtime/firmware/input — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps3/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps3/README.md)
- **OFF37** API/ARM64/formatos e despacho interno Sony — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/java/org/emulationstation/frontend/sony/StationSonyLaunchActivity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/java/org/emulationstation/frontend/sony/StationSonyLaunchActivity.java)
- **OFF38** Bootstrap PS3 baseline, jogo e lifecycle — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps3/java/org/emulationstation/frontend/sony/Ps3Activity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps3/java/org/emulationstation/frontend/sony/Ps3Activity.java)
- **OFF39** Configuração PS3 R134 com 18 campos — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps3Activity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps3Activity.java)
- **OFF40** Contrato primário settings, lifecycle e limites — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/settings-refinement-r134/evidence/sony-settings-contract.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/settings-refinement-r134/evidence/sony-settings-contract.json)
- **OFF41** Contrato PS4 runtime/PKG/áudio/input/retorno — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps4/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps4/README.md)
- **OFF42** Owner PS4 baseline — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Activity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Activity.java)
- **OFF43** Importação PKG, staging e SFO — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Game.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Game.java)
- **OFF44** Configuração PS4 R134, JSON e callbacks — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps4Activity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps4Activity.java)
- **OFF45** Guard de instalação e verificação de dados — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/tooling/release/install_current.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/tooling/release/install_current.py)
- **ON-01** Handoff R134 local atual: identidades, kit, ledger e procedimento. Arquivo local em preparação; publicação não presumida. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-settings-refinement-r134-20261011/HANDOFF-APP-R134-PARA-SERVIDOR-20261011.md
- **ON-02** Status R134 e escopo limitado dos deltas. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-settings-refinement-r134-20261011/STATUS.json
- **ON-03** Ordem explícita de composição Java R124/R125/R126/PSX. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/recipe/compile_java.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/recipe/compile_java.py)
- **ON-04** Rotas Station, ativação, sessão e grants efetivamente lidos no GitHub. — src/TurboRamaSuiteOnlineServer/StationEndpoints.cs e StationService.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationEndpoints.cs)
- **ON-05** Cliente HTTP, assinatura, domínios, grants, limites e mídia. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationApi.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationApi.java)
- **ON-06** Operações sociais/legadas, limites, capacidades e endpoints. — src/TurboRamaSuiteOnlineServer/StationOnline.cs e StationOnlineEndpoints.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationOnline.cs)
- **ON-07** Canonical HTTP, timestamp/nonce, criptografia e proteção de replay. — src/TurboRamaSuiteOnlineServer/StationRequestProof.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationRequestProof.cs)
- **ON-08** Engine, conteúdo, preparo e conferência das salas. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/java/org/emulationstation/frontend/netplay/StationOnlineGame.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationOnlineGame.java)
- **ON-09** Lobby, salas, pronto/start, convites guardados e lançamento. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/java/org/emulationstation/frontend/netplay/StationRoomsActivity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationRoomsActivity.java)
- **ON-10** Composição social/v3, requisições, capacidades e retry somente leitura. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineClient.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineClient.java)
- **ON-11** Endpoints POST/WSS, timeout/corpo/cabeçalhos, assinatura e autenticação. — src/TurboRamaSuiteOnlineServer/StationMultiplayerEndpoints.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerEndpoints.cs)
- **ON-12** Schema, 12 ações, aprovação, roster, tickets, limites e snapshot. — src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs e StationMultiplayerPlatformPolicy.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs)
- **ON-13** Recibo original R134: IDs, hashes, opções, extensões e dependências técnicas; sem segredos. — G:/StationNormalOwnersR127/settings-refinement-r134/assembly/identity/runtime-identity.json
- **ON-14** TSR3, replay, barreira, relay, timeouts e autorizações. — src/TurboRamaSuiteOnlineServer/StationMultiplayerStream.cs e StationRecoveryRelay.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerStream.cs)
- **ON-15** Integração Mupen AE, SN64 e alcance dos testes; consultar também java/StationN64Wire.java. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-mupen-online-r125-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-mupen-online-r125-20261011/README.md)
- **ON-16** Dolphin real, DPL1, CurrentRun, ACK/CPU gate e saída humana. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-dolphin-online-r126-20261011/NATIVE-CONTRACT.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-dolphin-online-r126-20261011/NATIVE-CONTRACT.md)
- **ON-17** Owner PSX, ABI, SDL, status e saída; complemento native/StationPsxProtocol.hpp e .cpp. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/ENTRY-CONTRACT.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/ENTRY-CONTRACT.md)
- **ON-18** Auditoria histórica R126 dos demais sistemas; PSX posterior supersede linha PS1; canais ACTIVE históricos. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/audits/station-online-system-engines-20261011/README.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/audits/station-online-system-engines-20261011/README.md)
- **ON-19** Matriz/ledger R134 local e estados auditados; não é snapshot de produção. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/audits/station-r134-online-mode-completion-20261011/summary.json
- **ON-20** Último retorno real a6b58e9 verificado nesta leitura, ainda R129. — docs/station-android/online-plataformas-20261009/r128-retorno-servidor-20261011.json — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/docs/station-android/online-plataformas-20261009/r128-retorno-servidor-20261011.json)
- **ON-21** Entrega documental R133 publicada; não é aplicação servidor. — docs/station-android/r133/DELIVERY.json — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/524d2ebff08353fda62aacbc5f05f9248ba69b7c/docs/station-android/r133/DELIVERY.json)
- **ON-22** Hotreload de 10 s, limite de 16 MiB, último válido e salas congeladas. — src/TurboRamaSuiteOnlineServer/StationMultiplayerProfileMonitor.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerProfileMonitor.cs)
- **RUN01** Instruções de composição, preservação e limites de evidência. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/AGENTS.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/AGENTS.md)
- **RUN02** Saída humana e lifecycle Java Retro herdado. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationRetroActivity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationRetroActivity.java)
- **RUN03** Quit JNI, callbacks NativeActivity e finalização do worker. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-multiplayer-r77-20261008/native/source/frontend/drivers/platform_unix.c — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-multiplayer-r77-20261008/native/source/frontend/drivers/platform_unix.c)
- **RUN04** Leitura do quit no input/poll inicial; fonte herdada do lifecycle. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-session-lifecycle-r74-20261007/native/source/input/drivers/android_input.c — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-session-lifecycle-r74-20261007/native/source/input/drivers/android_input.c)
- **RUN05** Owner normal N64, saves isolados, fechamento e hooks humanos. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Bridge.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Bridge.java)
- **RUN06** Condicional de pausa/quit no thread do emulador. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-mupen-online-r125-20261011/native/n64-station-recovery.c — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-mupen-online-r125-20261011/native/n64-station-recovery.c)
- **RUN07** Receita de I/O cancelável, guards de STOP e descarte seguro dos inputs. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-mupen-online-r125-20261011/native/apply_native_patch.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-mupen-online-r125-20261011/native/apply_native_patch.py)
- **RUN08** Fechamento dos sockets locais, queues e executores N64. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Mux.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Mux.java)
- **RUN09** Espera de registro/saves e cancelamento de senders. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Server.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-mupen-online-r125-20261011/java/org/emulationstation/frontend/netplay/StationN64Server.java)
- **RUN10** Saída humana PSX, IO/Binder cleanup e polling de status. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxSession.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxSession.java)
- **RUN11** Join fora da UI, captura de owner e gate de retirada privada. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxOnlineActivity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxOnlineActivity.java)
- **RUN12** Shim SDL/JNI, autorização humana, waits e renderer deinit. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/native/StationPsxEntry.cpp — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/native/StationPsxEntry.cpp)
- **RUN13** Checkpoint do owner exato e liberação guardada de core. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/native/StationPsxOwner.cpp — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/native/StationPsxOwner.cpp)
- **RUN14** Locks internos do protocolo e estados inFrame/applying. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/native/StationPsxProtocol.cpp — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/native/StationPsxProtocol.cpp)
- **RUN15** Opt-in SDL: onDestroy não mata owner sem gate e inversão exata do patch. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/recipe/patch_sdl_optin.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/recipe/patch_sdl_optin.py)
- **RUN16** R134 PS4: stopper, run, superfície retida, configurações e retorno. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps4Activity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps4Activity.java)
- **RUN17** R134 PS3: worker serial de superfície/config/quit. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps3Activity.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/settings-refinement-r134/java/org/emulationstation/frontend/sony/Ps3Activity.java)
- **RUN18** Áudio local PS4, AudioTrack bloqueante e limpeza idempotente. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Audio.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Audio.java)
- **RUN19** Input local PS4, neutralização, queue e close. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Control.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/sony-internal/ps4/java/org/emulationstation/frontend/sony/Ps4Control.java)
- **RUN20** Lifecycle e exclusão mútua de SurfaceTexture/MediaPlayer. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java)
- **RUN21** Retirada dos slots e handles GL por contexto. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/native/d0/native_system_video720.h — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/native/d0/native_system_video720.h)
- **RUN22** Foreground, gerações e cancelamento das capas. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java)
- **RUN23** Foreground do frontend, capa/polling e publicação. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/java/client/src/java/org/emulationstation/frontend/station/StationFrontend.java)
- **RUN24** 43 perfis de fallback extraídos do ELF original; extensões são seletores. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/evidence/original-launch-profile-table-r120.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/evidence/original-launch-profile-table-r120.json)
- **RUN25** 50 rotas canônicas e inventário histórico de dependências ausentes. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/evidence/launch-matrix-r120.json — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/evidence/launch-matrix-r120.json)
- **RUN26** Diferenças e limitações de toque/hotplug por família. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-game-menu-controller-audit-r120-20261010/REVIEW-CONTROLLER-VISIBILITY-R120.md — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-game-menu-controller-audit-r120-20261010/REVIEW-CONTROLLER-VISIBILITY-R120.md)
- **RUN27** Guard de Android10/X1 BOX1.2.8 e retorno isolado Xbox. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/platform-xbox-pce-refresh/java/org/emulationstation/frontend/XboxBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/platform-xbox-pce-refresh/java/org/emulationstation/frontend/XboxBootstrap.java)
- **RUN28** Guard API30/Vulkan1.1 e seletor executável Cemu preservado. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/wiiu-rar5-fix-20260930/WiiUBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/wiiu-rar5-fix-20260930/WiiUBootstrap.java)
- **RUN29** Guard API30/Vulkan1.1 do XenDroid integrado. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/xbox360-integration/java/org/emulationstation/frontend/Xbox360Bootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/xbox360-integration/java/org/emulationstation/frontend/Xbox360Bootstrap.java)
- **RUN30** Guard API28 do wrapper Vita preservado. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/vita-wiiu-pronto-20261001/VitaBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/vita-wiiu-pronto-20261001/VitaBootstrap.java)
- **RUN31** Owner Dolphin offline e migração só dos saves nativos ausentes. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/dolphin-integration/java/org/emulationstation/frontend/DolphinBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/dolphin-integration/java/org/emulationstation/frontend/DolphinBootstrap.java)
- **RUN32** Retorno Flycast e migração delimitada de BIOS/saves. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/flycast-integration/java/org/emulationstation/frontend/FlycastBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/flycast-integration/java/org/emulationstation/frontend/FlycastBootstrap.java)
- **RUN33** Owner PSP, preferências e cópia dos saves ausentes. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/psp-integration/java/org/emulationstation/frontend/PspBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/psp-integration/java/org/emulationstation/frontend/PspBootstrap.java)
- **RUN34** Owner PS2, finishActivity e monitor de retorno das configurações. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/ps2-integration/java/org/emulationstation/frontend/Ps2Bootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/ps2-integration/java/org/emulationstation/frontend/Ps2Bootstrap.java)
- **RUN35** Wrapper Saturn preservado. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/saturn-modern/java/org/emulationstation/frontend/SaturnBootstrap.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/estavel-2026-09-30-plataformas-emuladores/snapshot/implementation/saturn-modern/java/org/emulationstation/frontend/SaturnBootstrap.java)
- **RUN36** Monitor do transporte comum e awaitClosed. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/integration/psx-online/java/org/emulationstation/frontend/netplay/StationMultiplayerSession.java)
- **RUN37** JNI de foreground/graphics e limites das inboxes. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/frontend/station_frontend.cpp — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/frontend/station_frontend.cpp)
- **RUN38** Identidade dos recursos GL/LED por contexto e liberação. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-video-room-footer-r124-20261011/native/d0/native_magazine_field.h — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-video-room-footer-r124-20261011/native/d0/native_magazine_field.h)
- **RUN39** Composição de fonte herdada e overlays do runtime Retro. — C:/Users/Admin/Documents/Codex/2026-09-28/turboramaemutestes-apk-e-estudo-apk-work/work/TurboElden-git/versions/station-multiplayer-r77-20261008/native/build_native.py — [fonte](https://github.com/luziellacerda/TurboElden/blob/4f9039eb9ce13907ce043870bfe1f6e294888556/versions/station-multiplayer-r77-20261008/native/build_native.py)
- **SA01** Registro de perfis, salas, geração, ownership, ações e tickets. — src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayer.cs)
- **SA02** Barreira global, replay, epochs, recuperação e watchdog. — src/TurboRamaSuiteOnlineServer/StationMultiplayerStream.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerStream.cs)
- **SA03** Rotas HTTP e WebSocket v3, autenticação, envelopes e limites. — src/TurboRamaSuiteOnlineServer/StationMultiplayerEndpoints.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerEndpoints.cs)
- **SA04** Plataformas e tetos administrativos por plataforma. — src/TurboRamaSuiteOnlineServer/StationMultiplayerPlatformPolicy.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerPlatformPolicy.cs)
- **SA05** Reload do registro validado de perfis sem reiniciar API. — src/TurboRamaSuiteOnlineServer/StationMultiplayerProfileMonitor.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationMultiplayerProfileMonitor.cs)
- **SA06** Domínio legado v1/v2, lobby, presença e diferenças de timeout. — src/TurboRamaSuiteOnlineServer/StationOnline.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationOnline.cs)
- **SA07** Rotas legadas, composição das flags v3 e diagnóstico operacional. — src/TurboRamaSuiteOnlineServer/StationOnlineEndpoints.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationOnlineEndpoints.cs)
- **SA08** Rotas comerciais, transferência, rate limit e timeout. — src/TurboRamaSuiteOnlineServer/StationEndpoints.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationEndpoints.cs)
- **SA09** Esquemas de ativação/sessão, perfil, catálogo e grant. — src/TurboRamaSuiteOnlineServer/StationService.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationService.cs)
- **SA10** Identidade comercial, assinatura RSA-PSS e envelope. — src/TurboRamaSuiteOnlineServer/StationProtocol.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationProtocol.cs)
- **SA11** Elegibilidade comercial, transações, revogação e consumo de grants. — src/TurboRamaSuiteOnlineServer/StationStore.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationStore.cs)
- **SA12** Catálogo publicado, metadados, capas e artefatos vinculados. — src/TurboRamaSuiteOnlineServer/StationLibrary.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationLibrary.cs)
- **SA13** Suite real do domínio e casos de allowedPlayerCounts. — tests/StationMultiplayer/Checks.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/tests/StationMultiplayer/Checks.cs)
- **SA14** Carga sintética limitada em processo; 320 participantes e 80 salas. — tests/StationMultiplayer/CapacityChecks.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/tests/StationMultiplayer/CapacityChecks.cs)
- **SA15** Suite HTTP separada, existente e não executada nesta validação. — tests/StationMultiplayer/HttpChecks.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/tests/StationMultiplayer/HttpChecks.cs)
- **SA16** Recibo histórico de preparação sem ativação produtiva. — docs/station-android/online-plataformas-20261009/r128-retorno-servidor-20261011.json — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/docs/station-android/online-plataformas-20261009/r128-retorno-servidor-20261011.json)
- **SA17** Procedimento administrativo nativo e pré-requisitos de aplicação. — docs/station-android/r133/HANDOFF-APP-R133-PARA-SERVIDOR-20261011.md — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/524d2ebff08353fda62aacbc5f05f9248ba69b7c/docs/station-android/r133/HANDOFF-APP-R133-PARA-SERVIDOR-20261011.md)
- **SA18** Delivery público R133 e status de não ativação. — docs/station-android/r133/DELIVERY.json — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/524d2ebff08353fda62aacbc5f05f9248ba69b7c/docs/station-android/r133/DELIVERY.json)
- **SA19** Instruções herdadas e limites de publicação/ativação. — docs/station-android/AGENTS.md — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/docs/station-android/AGENTS.md)
- **SA20** Codec de frames e janelas FIFO reaproveitados por v3. — src/TurboRamaSuiteOnlineServer/StationRecoveryRelay.cs — [fonte](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/src/TurboRamaSuiteOnlineServer/StationRecoveryRelay.cs)
- **SA21** 29 verificações determinísticas novas, com classes reais de hub/stream/replay; será publicado na branch de auditoria pelo responsável. — tests/StationMultiplayer/BarrierDiagnosticsChecks.cs
- **SA22** Diagnóstico numérico opcional, exclusivo de membros e snapshot coerente; não ativa motores nem muda regras de progressão. — src/TurboRamaSuiteOnlineServer/StationMultiplayerStream.cs:59-95; StationMultiplayer.cs:259-269
- **SA23** Recibo da suite real de domínio: 29 checks novos, 1452 totais; sem TLS, WAN, Android ou deploy. — work/server-three-player-validation.json
- **SA24** Comparação dos quatro engineId de R134 com o handoff público R133; artefatos privados não incluídos. — incoming-engine-manifest.json do kit privado R134, identificadores públicos extraídos
- **SA25** Confirmação de heads R128 aplicado a6b e docs R133 524d; não foi localizado recibo posterior de ativação R134. — consulta GitHub branches, páginas 1 e 2, 117 branches — [fonte](https://github.com/luziellacerda/Servidor-pix/branches)
- **SA26** Configuração pública do cliente, transporte HTTPS, identidade, cache e coexistência comercial v1/multiplayer v3. — work/dossier-services.json, fontes SV05/SV06/SV07 e SV39
