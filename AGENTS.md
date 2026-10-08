# R76 — APP-01 integrada e compilada — 08/10/2026

Leia `versions/station-pump-wakeup-r76-20261008/README.md`, STATUS, evidências e `HANDOFF-APP-R76-PARA-SERVIDOR-20261008.md`. APK `d7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51`, DEX35 `c03ea2f4aa30c5e32654c575115583f72815b9701c16791c4f94c6ade753f2ff`. Somente StationRecoveryTunnel Java alterado; sinal preservado no empty/finally e falha antiga não invalida Remote novo. R75 visual incluída, runtime/rs4/certificado/dados preservados. Cadastro R74 ativo conforme servidor ed9ca9f; não pede novo engine nem restart. Testes locais: 1.206 regressões, 101 verificações de sessão/42 guardas, 1.466 verificações do pump e seis execuções TLS reais com 30.817.216 bytes exatos. Samsung A56 instalado às 11:25:32 UTC em 08/10/2026: hash integral, UID e data original conferidos, entrada oficial chegou à ESActivity. Motorola Edge 30 também atualizado em 08/10/2026 às 11:44:14 UTC: mesmo hash integral, UID e data original preservados, sem partida ativa nem limpeza. Ambos R76, conferência de gameplay pendente. Sem gameplay físico prolongado; consultar recibos individuais. Fonte deve ser recompilada pelo manifesto das 201 fontes, não restaurar outras Activities. DLL do servidor 6f27 permanece candidata sem qualificação completa; nenhum serviço Linux alterado.

Entrega APP → SERVIDOR publicada: app `2a8adce752b7778c90b2e70ecd67d1bc1fc62a9d`; servidor `a9f7f41b243f62e7ff5c3240d65eb7704034184c`, branch `docs/station-r76-pump-wakeup-20261008`, documento `docs/station-android/ENTREGA-APP-R76-PUMP-WAKEUP-20261008.md`. Recibo `docs/server/RECIBO-ENTREGA-R76-PUMP-WAKEUP-20261008.json`. É nossa entrega, não resposta nem deploy; commit executável permanece 2a8adce. Checkout e índice do clone servidor preservados.

Pedido posterior: salas de até quatro jogadores apenas em títulos compatíveis. Ler `docs/server/PLANO-SALAS-ATE-4-JOGADORES-20261008.md` e auditoria JSON. É proposta, não suporte implementado: servidor/relay/app ainda limitam a dois; Multitap SNES tem bloqueio id>11 confirmado no core do APK. Não anunciar quatro vagas nem enviar campos novos antes do contrato versionado e da qualificação de controles/transporte. Não alterar R76 por esse documento.

## Histórico anterior

# Retorno efetivo R74 do servidor recebido; R75 visual preservada — 07/10/2026

SERVIDOR → APP, commit `ed9ca9fdcc16f3b9f86792d43ed01d5812a9f1d8`, branch `docs/station-r74-server-stability-return-20261007` (Servidor-pix). Leia `docs/server/RETORNO-SERVIDOR-APP-R74-LIFECYCLE-LATENCIA-20261007.md`, pesquisa de latência e recibos em `docs/server/recovery-r74-20261007`. Este é o retorno do operador; os pedidos `8d48252`/`7ad4fb05` abaixo continuam sendo APP → SERVIDOR.

Cadastro R74 realmente ativo: dez engines, oito anteriores preservadas, SHA `a5f9de948ab3fcf15b2657061d540dcbbafda98e1dd7a68137e617b58a894843`, recarga `2026-10-08T00:39:18.786312Z`, PID 1278094. DLL ativa permanece `ab192bf`/`815fc8bc`; 187 checks isolados e 191 HTTPS/WSS do cadastro passaram. Não repetir a pendência de oito engines. R75 visual usa os mesmos IDs rs4/runtime `804b2acfea4c…` e não precisa de outro registro.

SRV-01/02/03 implementados na candidata servidor `6f27c6c`/DLL `71ba30b8`, .NET 8.0.31: primeira causa antes de Detach, Close pelo escritor único, métricas limitadas. 91+589+88 checks locais; fixtures TLS com tracing passaram, mas sem logging houve timeout do handshake, inclusive imediato. Divergência ainda não isolada: DLL NÃO ativada, qualificação sombra/pública pendente. Não declarar a candidata em produção nem atribuir essa falha isolada ao telefone.

**Próxima implementação do PCAPK: APP-01.** O Linux repetiu a receita exata nas fontes R74: 1.764 verificações, baseline 64/64 espera outro sinal, candidato 64/64 envia sem novo tick. Corrigir sinal perdido de `pumpPending` sobre R74/R75 atual, preservando escritor único, testar erro/rejeição do executor/fechamento/substituição de transporte/ACK/crédito/reconexão e suítes TLS/WSS/TCP/sessão antes do novo DEX/APK. O candidato ainda existe só na fixture; este retorno não muda código Android, runtime, APK ou presets. EXP-01 segue como teste A/B proposto. Preservar mudanças visuais R75, assinatura, UID, licença, jogos, saves e todos os demais módulos.

Jogatina R74 observada 00:41:31–00:44:31: heartbeats dos dois e 385.806 bytes entregues antes da saída humana, sem marcador de falta de presença ou reinício. Não é homologação prolongada. Não abrir rota direta por hipótese: certificado da origem tem pin diferente; entrada externa não comprovada. Não reiniciar servidor com sessões retidas em RAM. Histórico abaixo não identifica o último retorno do servidor.

## Histórico anterior

# R75 candidata — vídeos Neo Geo; pesquisa R74 preservada — 07/10/2026

Leia `versions/station-neogeo-collection-map-r75-20261007/README.md`, STATUS e recibos. APK `1ab4fa3770570832ea5ff2e9b0ce4f8a26e0e24e210ad7652f4c96647fecad32`, com 2.122.907.752 bytes, em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R75-20261007.apk`. **Compilada e assinada; não instalada.** Ambos os aparelhos permanecem na R74; estavam jogando e depois saíram da USB. Não encerrar partidas para atualizar.

Corrige apenas cinco ocorrências corrompidas de `COLEÇÃO` no mapa de vídeos; os seis MP4 de Neo Geo já existiam. Carrossel `3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b`; 13.224 entradas de conteúdo preservadas, incluindo 59 MP4 totais e 58 do carrossel. DEX, runtime `804b2acfea4c…`, engines, manifesto e controles permanecem idênticos. Não precisa de outro cadastro por causa da R75; usa os IDs rs4 da R74. A base nativa R71 foi reproduzida byte a byte antes da correção. Das 150 verificações independentes, 51 falham na R71 e nenhuma na R75. Regressões adicionais: 3.444 verificações de rotas/posters, 66 de cantos, 3.584 de navegação e 199.592 de política do decoder. Sem conferência visual no aparelho nem afirmação de estabilidade geral.

O mantenedor relatou grande melhora e menos travamentos na R74. Leia `docs/server/PESQUISA-ESTABILIDADE-R74-20261007.md`: pesquisa em fontes oficiais e comparação com o código, com tarefas do app e do servidor separadas; não é retorno do operador nem implantação. Último retorno lido: `815ceaca`; nosso `8d48252` é um pedido. Não mudar timeouts, presets ou engine por hipótese. Compilar em E: e guardar o APK final em G:. Preservar identidade, dados e saves; não publicar APKs, mídia, chaves ou logs pessoais.

Pesquisa publicada APP → SERVIDOR: branch `docs/station-r74-stability-research-20261007`, commit `7ad4fb05a69d8f95030f029f3670333a0c7bd6c2`, documento `docs/station-android/PEDIDO-ESTABILIDADE-R74-PESQUISA-20261007.md`. Fonte app `f3f2cc9d63fe4261921b07754d3f1255b5e31484`. É nosso pedido, não retorno. APP-01 reproduz perda de sinal imediato na fila em 64/64 casos; candidato isolado corrige 64/64, com 1.764 verificações. Ainda não integra o APK. Servidor deve responder SRV-01/02/03; EXP-01 é ensaio proposto, não preset aplicado. Não confundir a correção visual R75 com mudança de engine.

## Histórico anterior

# R74 instalada nos dois aparelhos — 07/10/2026

Pedido explícito do mantenedor para instalar antes da confirmação do novo registro. Samsung A56 em `2026-10-08T00:31:19.637993+00:00` e Motorola Edge 30 em `2026-10-08T00:30:49.949930+00:00`: SHA integral `e56896f28b16645653bfd28311cd0a8a9a5458e6d443849916a4dede6dc7fafe` conferido. UID e data original preservados; envio direto, sem APK extra, desinstalação, limpeza de dados ou ajustes de aparelho. Mantenedor saiu do jogo Samsung; nenhum emulador ativo foi identificado no início de cada instalação.

Fonte executável continua557014b4ff5ec5c3c0162847d922c0587f68b0e9; APK/runtime e segurança não foram recompilados nem alterados. Leia `versions/station-session-lifecycle-r74-20261007/INSTALLATION.json`. Entrada oficial solicitada; não afirmar autologin, gameplay ou retomada apenas pelo sucesso da instalação. Último retorno real do servidor continua815ceaca. Pedido8d48252 é nosso handoff; novo registro rs4/runtime804b2acfea4c ainda precisa confirmação. Não reinstalar por mero cadastro nem iniciar sala sem identidade compatível; não alegar estabilidade.

## Histórico anterior

# R74 candidata — ciclo de vida, ANR e latência — 07/10/2026

Entrega publicada: app `557014b4ff5ec5c3c0162847d922c0587f68b0e9`; pedido APP → SERVIDOR `8d48252fb7e91af83b6138afa411d5c2607edcc8`, branch `docs/station-r74-session-lifecycle-20261007`, documento `docs/station-android/ENTREGA-APP-R74-LIFECYCLE-LATENCIA-20261007.md`. Recibo em `docs/server/RECIBO-ENTREGA-R74-LIFECYCLE-20261007.json`. É nosso pedido completo, não resposta, ativação ou implantação Linux. Não confundir com o último retorno real 815ceaca. O commit executável permanece 557014b; acréscimo posterior apenas documental.

Leia `versions/station-session-lifecycle-r74-20261007/README.md`, STATUS e o handoff APP → SERVIDOR. APK `e56896f28b16645653bfd28311cd0a8a9a5458e6d443849916a4dede6dc7fafe`; runtime `804b2acfea4c6d615bf40dba30e1777015098bf7375d0745db8d117555eb2516`. Compilada e assinada, **não instalada nem estável**. Ambos aparelhos ainda R73. Exatamente quatro entradas alteradas e 13.221 preservadas. Mesma assinatura, cores, controles, mídia e motores offline.

Validação: 201 fontes Java; 1.206 verificações históricas em execução separada de 101 verificações de sessão e 42 guardas; três probes nativos. Testes locais não substituem Android físico nem partida real em dupla.

A pesquisa oficial confirma o catch-up do motor. A reprodução local demonstra uma marca Station persistente que gerava NeedSync13 depois de o catch-up terminar. A correção remove apenas essa escalada. ANRs físicos R73 apontaram fila de entrada Android sem confirmação durante espera; R74 consome os eventos sem avançar quadros. A primeira queda, anterior e distinta, ocorreu depois de o Android congelar a autoridade HTTP; serviço privado vinculado mantém sua dependência do processo do jogo. O resultado da Activity limpa lançamento órfão, e o JNI de saída/reserva/locks corrige encerramento. Nenhum temporizador foi removido por tentativa.

RTT mediano de 122 ms no Samsung e 359 ms no Motorola não prova lentidão exclusiva do serviço. Pedido ao operador contém janela 23:49:45–23:53:18 UTC, primeira queda/epochs e medições DATA/PONG, filas, SendAsync, GC, TCP e proxy. Último servidor lido: 815ceaca; R73 já ativa com oito engines. R74 requer duas adições rs4/runtime804b2acfea4c preservando as oito. Não reutilizar IDs antigos nem contornar validações.

Não implantar Linux nem reiniciar com partidas retidas. O operador coordena a ativação. Antes de instalar, confirmar ausência de partida ou pedir saída humana; preservar jogos, licença, saves e assinatura. Não afirmar gameplay R74 validado.

## Histórico anterior

# R73 — queda diagnosticada e cadastro confirmado — 07/10/2026

Leia `docs/server/ANALISE-APP-R73-QUEDA-CONVIDADO-20261007.md`. Cruzamento com retorno SERVIDOR→APP `815ceaca49baa0feb1e2d61726c0346ddad2bd37`, branch `fix/station-r73-engine-registry-20261007`: registro R73 ativo 23:13:54 UTC, oito engines, SHA266de762; DLL ab192bf preservada. Não repetir pendência antiga de cadastro nem reinstalar por esse motivo. Ambos aparelhos continuam APK b23ff3d1 R73, hash integral conferido.

Primeira queda provada: convidado deixa heartbeat HTTP às23:22:02; Android registra congelamento do processo principal às23:22:14.382, mantendo processo do motor/PONG; servidor fecha AUTH_HEARTBEAT_MISSING às23:23:10.719 (68387ms sem presença). Proprietário HTTP/tickets está no processo principal sem Service vinculado. Corrigir ciclo de vida no app, preservando autenticação e separação do carrossel. Reabertura seguinte é problema distinto: novos tickets aceitos, mas motor reutilizado não registra nova inicialização. Há riscos de mutex/join e estado estático; pilha atual indisponível sem root, causa nativa exata ainda não provada. Não desligar timers/validações indiscriminadamente.

Esta etapa foi somente diagnóstico/documentação local. Nenhum runtime/APK/servidor/ajuste de telefone alterado, nenhuma partida interrompida. Logs privados em E:station-r73-disconnect-analysis-20261007, fora do Git. Servidor registra relato do mantenedor de ambos jogando antes da queda; recuperação/estabilidade não homologadas. Preparação de correção deve conciliar fontes exatas R73 e testar também saída/reabertura, além da presença durante jogo.

## Histórico anterior

# R73 instalada nos dois aparelhos — 07/10/2026

Pedido explícito do mantenedor para instalar agora, antes da confirmação do cadastro. Samsung A56 às23:11:17UTC; Motorola Edge30 às23:12:57UTC; ambos SHA integral b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077 verificado. UID/data original preservados; sem emulação ativa, limpeza/desinstalação/ajustes ou APK extra; envio direto. Recibos em versions/station-recovery-handshake-r73-20261007/evidence/installation-*-r73.json. Fonte executável5657dce permanece; somente receita de instalação/documentação acrescidas. Samsung abriu entrada oficial com keyguard; não afirmar login/gameplay. Registro online ainda não confirmado (último retorno c1e44a;1b26b34c é nosso pedido). Rejeição prévia de instalação foi revista após código comprovar limite em StationOnlineGame.prepare, preservando login/catálogo e validação dos motores; usuário solicitou instalação imediata. Não iniciar partidas até cadastro efetivo, não afirmar estabilidade/correção física sem teste.

## Histórico anterior

# R73 candidata compilada — handshake sob pausa — 07/10/2026

Leia versions/station-recovery-handshake-r73-20261007/HANDOFF-APP-R73-PARA-SERVIDOR-20261007.md e STATUS. APK b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077; runtime 9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2. Baseline nativo reproduziu MODE retido; função R73 envia não bloqueante e espera buffers drenarem antes READY. 1206checksJava+22nativos+39guardas. Dialog visível separado/diagnóstico limitado. **NÃO instalada nem homologada: servidor precisa adicionar duas identidades exatas preservando seis antigas.** Ambos os aparelhos permanecem R72/a8d3d28b. Teste R72/R72 22:48UTC: JNI ok/host-listening, ambos state1/PONGs, telaspretas. Sem atribuir causaúnica sem teste. Não removersegurança/timers, não trocar opções/cores, não ativarNeoGeo. Fontes/temporários E:, APK G:; dados/assinatura preservados. Operador implanta registro; nós não implantamosLinux.

Handoff APP→SERVIDOR publicado em `1b26b34cd0f205afaf70b4f9ebf2391da7853537`, branch `docs/station-r73-handshake-flush-20261007`, documento `docs/station-android/ENTREGA-APP-R73-HANDSHAKE-PARA-SERVIDOR-20261007.md`. Fonte R73 `5657dce678609f25501321e307839a6e0c018d4e`. Cadastro é lido na inicialização; operador deve coordenar ativação sem interromper partidas. Não é retorno do servidor, deploy ou confirmação de gameplay. Recibo em docs/server/RECIBO-PEDIDO-R73-HANDSHAKE-20261007.json.

## Histórico anterior

# R72 agora instalada nos dois aparelhos — 07/10/2026

Samsung A56 e Motorola Edge30 com APK integral a8d3d28bb70618c52debf6e4cb0acaaf1f3bd1de19fe410dda85f6953caaec8e conferido. Motorola às22:44:21UTC, UID/data preservados. Tentativa mista anterior: host Samsung R72 passou native-hooks-loaded/native-listening/host-listening-ack e manteve PONGs, mas tela preta; convidado R71 reutilizou processo nativo preso com pause/stop timeouts. Mantenedor autorizou encerrar essa tentativa nos dois aparelhos antes de atualizar Motorola; sem limpar dados. Próxima conferência exige sala nova com ambos R72. Não afirmar gameplay corrigido. Ler recibos e handoff R72.

## Histórico anterior

# R72 instalada no Samsung — registro JNI e perfis da sala — 07/10/2026

Leia `versions/station-native-registration-r72-20261007/README.md`, STATUS e HANDOFF-APP-R72-PARA-SERVIDOR-20261007.md. Retorno servidor c1e44a1225a101478ceb29f4e624885331872c0d integrado: produção v2 já declarada ativa às21:59UTC, fonteab192bf/DLL815fc8bc. Não repetir a antiga pendência de ativação da R71.

APK a8d3d28bb70618c52debf6e4cb0acaaf1f3bd1de19fe410dda85f6953caaec8e, 2122892378 bytes. Apenas DEX35 mudou: System.loadLibrary + probes JNI na Activity, candidato exato2c160af6; roster consome memberProfiles assinado por ID real/capacidade. Runtime d662, engines, DEX28, mídia e controles idênticos. 198 fontes,196 preservadas;1181 checks passaram;13224 entradas preservadas. Chave local expressamente autorizada e certificado original conferido antes da assinatura.

Samsung A56 instalado diretamente às22:36:25UTC, SHA integral/UID/data original preservados. Entrada solicitada, mas tela bloqueada em LoginActivity; abertura autenticada/gameplay ainda não conferidos. Motorola última R71, ainda precisa R72 para o mesmo teste nos dois papéis. Nenhuma partida interrompida, ajuste de aparelho, APK extra, desinstalação ou limpeza. Diagnóstico JNI como primeira causa da tela preta não confirmado em logs; mantenedor relatou ambos anfitriões pretos. Não afirmar correção física/retomada/estabilidade geral só por compilação. Fontes/buildE:, APKfinalG:, sem publicação de APK/mídia/chaves/logs privados.

## Histórico anterior

# R71 agora instalada nos dois aparelhos — 07/10/2026

Motorola Edge30 atualizado diretamente às21:37:39UTC deR70 paraR71, mesmo SHA integral do A56: `556170c32b6dd25fb5084693826d854adf736b4a1df156fd9229a8458b025018`. UID/data original preservados; sem partida ativa, desinstalação, limpeza de dados, ajuste no aparelho ou APKextra. Recibo `versions/station-online-layout-r71-20261007/evidence/installation-motorola-r71-20261007.json`. Entrada oficial solicitada. Ambos agora na mesmaR71; testes físicos pelo mantenedor. Servidor ainda conforme retorno publicado; não confundir instalação com ativaçãov2/gameplay. O handoff servidor e03a872 registra a entrega anterior a esta segunda instalação.

## Histórico anterior

# R71 completa instalada no A56 — salas, recuperação e tarefa única — 07/10/2026

Leia `versions/station-online-layout-r71-20261007/README.md`, STATUS, NAVIGATION-AUDIT e HANDOFF-APP-R71-PARA-SERVIDOR-20261007.md. APK `556170c32b6dd25fb5084693826d854adf736b4a1df156fd9229a8458b025018`, 2122893402 bytes, final `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R71-Completa-20261007.apk`. Build `E:\ESTUDO APK\work\station-online-layout-r71-20261007-complete`; 198 Java finais, 1152 verificações/56 guardas, 46 verificações TLS/WSS/TCP isoladas. Seis substituições + um vídeo, 13218 entradas preservadas, certificado original e16KiB. Candidato preliminar sem Completa/a135650c nunca instalado e superado.

A56 instalado diretamente às21:22:46UTC, hash integral/UID/data original conferidos. Depois do desbloqueio, ESActivity RESUMED confirmou catálogo aberto; recibo android-followup-samsung-r71.json. Relato de Voltar foi atribuído pelo mantenedor ao estado antigo; não demonstrou crash R71 nem originou novo patch. Sem APK extra/desinstalação/limpeza/ajustes. LoginActivity abriu com telefone bloqueado; NÃO afirmar autologin, tarefa única visual ou gameplay. Motorola Edge30 última R70; atualizar para mesmo R71 antes da dupla. Conferências físicas ficam com mantenedor, nunca interromper partida nem seguir troca de cabo sem fixar serial.

Sala exibe dois membros vinculados porID, botões compactos, cache limitado de nomes; falta ao servidor perfil assinado dos próprios membros fora da paginação100. ESActivity singleInstance→singleTask, Login retoma tarefa autorizada, lobby reaproveita entrada e respeita jogo. Falha terminal6 cancela worker; saída humana4 posterior mantém Leave idempotente; perda de rede não gera Leave automático. Novo vídeo Todos os jogos SNES720²/30fps/silencioso;58 vídeos, uma decodificação;30fps somente menu. Preserva faixa, controles/motores locais, BIOS, licenças e saves.

Servidor retorno6f8dcead3af84ed1c8323f6e241900bf2f36a938/código32ce9d2b30bb23deef17899e10fc285f38ea81ab declara produção NÃO implantada/RecoveryEnabledfalse. RuntimeWindows corrigido `d66267cd42507388f86034deb47e9f9670875784efb9afabfb8ffc64e3f3a856`, IDsrs2 específicos; registrar adições preservando antigos e ativar v2 antes da homologação. Não há fallback novo→v1. Sem deployLinux ou gameplay físico de recuperação comprovado; não marcar estável geral/ganho térmico. Tag estável de menu R69 preservada. Não publicar APKs, vídeos, ROM/BIOS, chaves ou logs pessoais.

Handoff completo APP→SERVIDOR publicado em `e03a87217df9e51908b97bb775ecac889c22088c`, branch `docs/station-r71-recovery-build-20261007`, arquivo `docs/station-android/ENTREGA-APP-R71-COMPLETA-PARA-SERVIDOR-20261007.md`. App analisável `0368bf0586fd6fa1b38ed4c98bcf6cee73810595` (código c0d36af6). 27 arquivos documentais/evidências, checkout/index servidor preservados; não é resposta nem deployLinux. Recibo `docs/server/RECIBO-ENTREGA-R71-COMPLETA-20261007.json`. Mantenedor testa os aparelhos; não alterar a navegação com base no relato depois atribuído ao estado antigo aberto.

## Histórico anterior

# R70 instalada A56 e Motorola — navegação, configurações e vídeos — 07/10/2026

Leia `versions/station-collection-navigation-r70-20261007/README.md`, STATUS e recibos. APK c12ee4e2928a629be4a2cc6dc9201fc7c5722e21a1fa8385d21da7a7dc69a32e compilado/assinado; 13.221 entradas preservadas. Instalada diretamente/hash integral A56 às20:21UTC, UID/data preservados. Cópia temporária intermediária removida a pedido; preferir sempre envio direto, sem APK extra. USB mudou para Motorola após instalação antes da captura, sem conferência visual R70. Motorola atualizado diretamente R63→R70 às20:25UTC, hash/UID/data verificados e catálogo ESActivity observado; mantenedor abriu partida antes dos testes de coleções, não interromper. Ambos na R70. Receita fixa aparelho para não seguir troca de cabo. Tag estável do menu `estavel-menu30fps-colecoes-r69-20261007`, commit17cd4718740e79c62e0522a1b0d3c363d7177068.

Corrige seleção pelo índice original após compactar filtros; defeito do último jogo reproduzido R69, R70 passou3584 verificações. Robô configurações rodapé direito somente coleções, ação/retângulo original+0x1410. Mario/TopGear novos720x720/30fps/silenciosos;57vídeos. Mantém Todos os jogos arredondado, coleções quadradas, um decoder, menu30fps; nenhum limite de30fps imposto aos emuladores. Sem prova térmica percentual, retomada online ou deployLinux. Build E:station-collection-navigation-r70-20261007-final2; finais G:apks-candidatos-visuais. Preservar assinatura/licença/saves e confirmar ausência de partida antes de instalar. Não publicar mídias privadas/capturas/credenciais.

## Histórico anterior

# R69 instalada — Todos os jogos arredondado e três vídeos — 07/10/2026

Leia `versions/station-collection-media-r69-20261007/README.md` e recibos. APK 901e5eb495a858fc6877f7a22e325b5fcb3b73807af8c6d2888c90f1425773e4 instalado/hash integral A56, UID/data preservados; ESActivity abriu. Confirmação FINAL do mantenedor: só Todos os jogos arredondado nas coleções; todas as coleções quadradas mesmo selecionadas. Identificar FolderMeta.kind==2 pelo índice original, nunca pelo foco/posição zero. Main platforms e game covers preservados.

Final Fight/Mega Man adicionados, Top Gear atualizado da pasta Sele;'ao; 720x720/30fps/silenciosos, 57 vídeos totais. 66 checks, nove ligações, um decoder e rotas13 passaram; 13.220 outras entradas APK preservadas. DEX/motores/segurança/runtime online iguais à R68. Pastas build E: station-collection-media-r69-20261007-final, final G: apks-candidatos-visuais. SNES observado: Todos os jogos arredondado, Super Mario selecionado quadrado, novos posters presentes. Mantenedor pediu tag estável do menu/consumo; sem medição térmica. Novos pedidos de seleção ao entrar/configurações/vídeos seguirão na R70. Não afirmar gameplay/retomada ou ganho térmico. Pedido REC01–09 R67 continua aberto; conciliar este overlay visual nas futuras atualizações.

## Histórico anterior

# R68 instalada — cantos retos em todas as coleções — 07/10/2026

Leia `versions/station-collection-corners-r68-20261007/README.md` e recibos. APK 72ce7c2cbb3d7cf14ad122b0b98e42a41563114bbbc5c925caedbdee49ff66c3 instalado/hash integral no A56, UID/data original preservados; ESActivity e coleções SNES observadas. Política compartilhada remove arredondamento somente em páginas de coleções, de qualquer sistema atual/futuro; plataformas principais e jogos conservam formato. Mudança única no APK: libturbo_carousel.so; 13.221 outras entradas iguais à R67. 24 verificações de política e três de ligação passaram. Vídeos, DEX, motores, segurança e 30 fps R67 preservados.

O pedido de retomada online REC-01 a REC-09 da R67 continua aberto; esta atualização visual não altera o contrato/runtime/Java. Conciliar o overlay R68 ao preparar novo APK. Build válido termina em `station-collection-corners-r68-20261007-final`; protótipo sem final, restrito a SNES/Neo Geo, foi superado e nunca empacotado. Capturas pessoais ficam fora do Git.

## Histórico anterior

# R67 instalada no A56 — vídeos, segurança e consumo do menu — 07/10/2026

Leia `versions/station-collection-videos-r67-20261007/README.md`, STATUS e o handoff APP→SERVIDOR. APK d746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f instalado/hash integral conferido no Samsung A56; UID/data original preservados. Entrada abriu ESActivity com sessão/perfil/catálogo200 (2212); alvo nativo30fps observado. Sem desinstalar, limpar dados, trocar assinatura ou ajustes do aparelho. Outro telefone não atualizado nesta entrega.

Nove vídeos de coleções atualizados (inclui Top Gear e Samurai novo),55 vídeos720×720/30fps/sem áudio. DEX28+35 conciliam segurança213cfce com composição R66/R64, sem restaurar Activities antigas. DEX30 BIOS, runtime899e, motores/controles/faixa/saves preservados;13210 entradas iguais. GuiStore limitado30fps/diálogo parado15; callbacks Java34ms não formam teto global das salas. Não afirmar redução térmica50% ou prova/atestação hardware só pelos HTTP200.

Retomada online NÃO implementada; retorno servidorb37c873 é análise. Pedido detalhado REC01–09 exige sessão sobrevivendo à queda, pausa real, sincronização e contrato/runtime coordenados. Não retirar timers/reabrir socket cru como suposta correção. Preservar v1 e outras plataformas. Fonte e recibos identificam APKexato; nenhum APK,segredo,ROM,BIOS ou captura pessoal deve ser publicado. Temporários E:, finais G:.

## Histórico anterior

# Retornos R62–R66 conciliados com o servidor — análise de07/10/2026

Leia `docs/server/RETORNO-ANALISE-HANDOFFS-R62-R66-STATION-20261007.md`. API da07355/PID1147382/usuário exclusivo continua publicada; sem nova implantação por esta análise. APP atual R66/291f3949: Samsung e4397fd7 instalado/hash integral e catálogo conferidos; Motorola últimaR63/d9a35602. Recibos posteriores prevalecem sobre STATUS/README de preparação. Mantenedor relatou partida e comandos R63; gameplay CD/retomada não comprovados.

Linux correlacionou aborto dos dois WSS às12:24:07UTC, depois de renovação200 às12:23:46. Gatilho inicial/heartbeat por participante continuam desconhecidos. v1 encerra ambos/Leave; Q01–Q08 aguardam contrato e implementação coordenada. Inventário189ZIPs originais com CRC declarado foi cruzado ao TSV14/IDs/capas; não comprova bytes ou pacotes ativos. BIOS CD já incluída é preparada automaticamente naR66; preservar esta integração.

SegurançaAndroid213cfce foi preparada em outra branch, sobreR57. Conciliar cliente/prova com composiçãoR55→R57→R62→R63→R64→R65→R66; preservar DEX30R66, controles/diagnóstico, Binder, saída, salas/capas, runtime899e, aliasRSA/assinatura/licença/saves. Recompilar DEX28+35 juntos e empacotar sobreAPKR66/e4397fd7 com novas provas. Não usar receitas históricasR57 para atualizarR66. RequireVerifiedApp=false preserva clientes atuais; acesso exclusivo aoAPK não demonstrado. Esta branch de análise acrescenta documentos, não integra a proteção nem a retomada no código.

## Histórico de instalação

# R66 instalada no A56 — BIOS automática — 07/10/2026

R66 instalada após reconexão, hash integral conferido `e4397fd743c410ea060f17446706d9475b5568caad379e1a6df37672c60398d1`, UID/data original preservados. Antes de instalar havia apenas ESActivity e a entrada com erro de BIOS, sem Activity de jogo. Não desinstalou/limpou dados/mudou ajustes. Entrada oficial abriu, aparelho bloqueado ainda em LoginActivity; não afirmar autologin ou gameplay CD conferidos. Após desbloqueio, catálogo ESActivity conferido. Mantenedor depois confirmou tocar JOGAR no CD, mas a USB desconectou antes da captura e continuou ausente; nenhuma execução CD foi comprovada. Fonte `291f3949760c0d77030e4872520efc3e1c8f928b`; recibo `docs/server/RECIBO-R66-BIOS-INSTALADA-SAMSUNG-20261007.json`. Correção da análise publicada no Servidor-pix `7a5db18564d50607a6ef90ef31b45a03232ae45a`, branch `docs/station-neogeocd-bios-r66-20261007`, adendo APP→SERVIDOR. Firmware JÁ existia no APK/telefone; R66 usa os assets automaticamente, sem importação manual normal. Outro aparelho última conferência R63. Cartuchos/KOF98/retomada online seguem pendentes.

## Histórico de preparação preservado

# R66 candidata — BIOS CD já existente agora preparada automaticamente

Leia `versions/station-neogeocd-bundled-bios-r66-20261007/README.md`. Correção da análise R65: os assets `bios/neocd/neocd.bin`, `000-lo.lo` e `uni-bioscd.rom` JÁ estavam no APK e telefone com identidades válidas. O novo lançador R65 ignorava essa origem. R66 usa AssetManager no worker e prepara atomicamente as dependências ausentes, preservando importações válidas; instalação nova não precisa importar manualmente. Só classes30.dex mudou;66 testes locais, DEX reproduzido idêntico, APK SHAe4397fd7. Nenhum firmware novo/baixado/adicionado ao APK. R66 ainda NÃO instalada: USB desconectou durante preparação. Samsung continua R65, outro telefone última conferência R63. Cartucho/KOF98 e retomada online permanecem pendentes; não declarar gameplay CD ou estabilidade. Código no APK, nunca corrigir apenas a pasta do telefone.

## Histórico de instalação preservado

# R65 instalada no Samsung A56 — 07/10/2026

Atualização solicitada pelo mantenedor concluída com `adb install --no-incremental -r --user 0`. SHA completo do APK instalado `1858459b62a38a85cdd9fbeaafc68d3560008f154f99dd1431752aa0594eb081`, igual ao candidato. UID e data original de instalação preservados; não desinstalou, não limpou dados nem mudou configuração do telefone. Antes de instalar, somente ESActivity no histórico ativo do app, sem partida interrompida. Entrada oficial LoginActivity abriu, mas o aparelho estava bloqueado e permaneceu nela: não afirmar retorno ao catálogo/autologin conferido. CD/gameplay/KOF98 ainda pendentes; R65 não é estabilidade geral. Outro telefone não atualizado nesta etapa. Recibo: `docs/server/RECIBO-INSTALACAO-R65-SAMSUNG-20261007.json`. Os textos de candidato não instalado abaixo descrevem a preparação anterior.

## Histórico de preparação preservado

# R65 candidata — Neo Geo CD e auditoria de cartuchos — 07/10/2026

Leia `versions/station-neogeo-cd-r65-20261007/README.md`, STATUS e recibos. R65 sobre R64 altera somente classes30.dex: integra o helper CD ausente no APK anterior, valida/importa BIOS e monta CHD com neocdz, fora da thread de interface. APK1858459b, 37 verificações locais e DEX reproduzido idêntico. NÃO instalado, NÃO estável. Última instalação física R63; USB ausente durante diagnóstico de KOF98. Catálogo publicado/revisão14:189cartuchos+50CD,13nomes sem registro MAME0289 (seis da coleção KOF), dois itens de outro hardware. Isso não substitui inspeção de chips/BIOS ou gameplay. KOF98 padrão é registrado e chegou ao motor, captura curta com imagem corrompida; causa ainda desconhecida. Não renomear variantes por suposição, trocar controles/motor ou limpar dados. R64 online/diagnóstico herdado; retomada NÃO implementada, pedido ao servidor continua aberto. Não publicar ROM/BIOS/APK/segredos/logs pessoais. Build E:, finais G:.

Pedido NG-01–NG-07 publicado no Servidor-pix: `4d9893d898213ec3202313d3209c072e73642586`, branch `docs/station-neogeo-audit-r65-20261007`, `PEDIDO-AUDITORIA-NEOGEO-CARTUCHO-CD-R65-20261007.md`. APP → SERVIDOR; ainda sem resposta. Recibo em `docs/server/RECIBO-PEDIDO-NEOGEO-R65-20261007.json`. USB continuou ausente na última conferência, sem instalação R65.

## Histórico preservado

# R64 candidata — controles online e diagnóstico de encerramento — 07/10/2026

Leia versions/station-online-controls-r64-20261007/README.md e o HANDOFF-QUEDA-ONLINE-APP-PARA-SERVIDOR-20261007.md. Mantenedor confirmou R63 jogando online/controles respondem, depois houve queda real às12:24:07Z. Causa exata ainda não comprovada; cliente descartava motivo detalhado. R64 mantém runtime/IDs/protocolo/timers, adapta visual SNES/Mega e adiciona registros seguros. Candidato compilado/testado, ainda não instalado. Não afirmar retomada implementada ou estabilidade geral; operador precisa correlacionarQ01–Q08. Preservar jogos/licença/saves/faixa/nativo/Binder.

Pedido de retomada publicado no Servidor-pix: `553a26c8045cd2fd324ec871ef79950faa316728`, branch `docs/station-r64-recovery-request-20261007`, documento `PEDIDO-QUEDA-RETOMADA-PARTIDA-STATION-20261007.md`. APP → SERVIDOR, ainda sem retorno. Mantenedor exige loading Aguardando conexão até recuperação, sem encerramento por inatividade. R64 NÃO implementa retomada. Recibo em docs/server/RECIBO-PEDIDO-RETOMADA-STATION-20261007.json.

## Histórico preservado

# R63 instalada nos dois aparelhos — 07/10/2026

Samsung A56 atualizado após liberação de espaço. Motorola Edge30 já havia sido atualizado. Nos dois, o SHA integral do APK instalado é `d9a35602ddc1141617df70d4b2b1f202d8646c538d4508f5fb3e53ef6b7abc4c`. Sem desinstalação, limpeza de dados, troca de assinatura ou mudança da configuração de tela ligada. UID e data original de instalação preservados. A entrada oficial LoginActivity retornou ao catálogo ESActivity, sem nova digitação de licença.

Recibos: `versions/station-auto-access-r63-20261006/evidence/installation-samsung-r63-20261007.json` e `versions/station-auto-access-r63-20261006/evidence/installation-motorola-r63-20261007.json`. As falhas anteriores de armazenamento abaixo são históricas e foram superadas. Conferências físicas ficam com o mantenedor; não foi validado gameplay em dupla, retorno online completo, latência externa ou controles online próprios. Criar sala nova usando os dois aplicativos R63. Nenhuma alteração funcional adicional foi feita por esta instalação.

## Histórico preservado

# R63 instalada no Motorola Edge30 — 07/10/2026

Atualização concluída e SHA integral `d9a35602ddc1141617df70d4b2b1f202d8646c538d4508f5fb3e53ef6b7abc4c` conferido no aparelho. Mesmo UID e data original de instalação, sem desinstalar, limpar dados ou modificar a configuração de tela ligada. Antes da instalação havia somente ESActivity no histórico ativo da TurboStations; não interrompemos partida. A entrada oficial LoginActivity retornou ao catálogo ESActivity, sem nova digitação de licença. A conferência seguinte mostrou StationRoomsActivity; depois a USB desconectou. A navegação física ficou com o mantenedor. O mantenedor fará as conferências físicas; sem gameplay em dupla comprovado.

Samsung A56 permanece na R62: a tentativa R63 foi recusada pelo Android por falta de armazenamento, e o hash114dba8a da R62 foi conferido após a recusa. Atualizar o Samsung para R63 antes da partida em dupla. Não afirmar que os dois aparelhos estão atualizados. Recibos: `versions/station-auto-access-r63-20261006/evidence/installation-motorola-r63-20261007.json` e `versions/station-auto-access-r63-20261006/evidence/installation-samsung-r63-failed-storage-20261007.json`.

## Histórico de preparação preservado

# R63 — convite curto e senha automática integrados sobre R62

Leia `versions/station-auto-access-r63-20261006/HANDOFF-APP-R63-PARA-SERVIDOR-20261006.md`, STATUS e recibos. Retorno 8d9c670/candidato 1e0f862 conciliados com R62: 161 Java, 158 preservados, três alterados; runtime 899e3527/IDs autopass1. APK d9a35602/DEX e910f431, 302 testes no Windows e recompilação idêntica pela restauração publicada. Visual, Binder, saída e motores locais preservados. Instalação aguarda saída da partida no Motorola; Samsung R62/Motorola R58. Atualizar ambos antes do teste em dupla. Sem gameplay físico comprovado, estabilidade geral ou deploy Linux.

## Histórico preservado

# R62 — handoff do servidor integrado no APK

Leia `versions/station-online-integrated-r62-20261006/HANDOFF-APP-R62-PARA-SERVIDOR-20261006.md`, STATUS e recibos. Fonte atual = R55 + R57 + nove Java R62. Retorno7c6e167/implementaçãof8b019d6 incorporados; agora há DEX/APK Android real. Inclui capas maiores/Sua sala, miniaturas autenticadas, botões finos e criação que só navega após confirmação. Nativo/faixa/motores preservados; sem deployLinux. APK114dba8a. Testes locais10TCP+255salas+14criação e454ParcelAndroidA56 passaram. Gameplay2aparelhos/saídaonline completa/controles online próprios ainda pendentes; não marcar estável geral. Usar recibos para identificar qual APK está em cada telefone.

## Histórico preservado

# Prontidão conciliada com a fonte online R55 e visual R57 — 06/10/2026

Leia `docs/server/RETORNO-ANALISE-APP-R55-STATION-20261006.md` e `versions/station-relay-readiness-r57-20261006/README.md`. Fonte funcional recebida:9d3d45f; sucessora visual considerada:8980cd4; implementação atual:f8b019d6; retorno servidor:e9d86a2. A R57 foi instalada no Motorola segundo o recibo recebido. A versão do outro telefone ainda precisa ser conferida.

O delta conserva o canal ResultReceiver e a saída idempotente da R54, mais o layout atual da R57: Criar sala, barra fina, capas e faixa INSTALADO. Todos os157 hashes Java da composição R57 coincidem com o recibo de produção. São155 arquivos preservados, dois alterados e um novo;158 fontes compilaram Java8/API34 em api-check-only. As39 provas de transporte e255 funcionais se aplicam aos mesmos componentes, sem repetição por alteração visual.

Não há novo DEX/APK compilado ou instalado nem gameplay físico comprovado. Sem alteração de servidor necessária para este delta. No PC usar as receitas novas em station-relay-readiness-r57-20261006, sobre APKbaseR57/e6159fa3, com dependências e certificado originais. Os empacotadores antigos R41/R55 não servem para a sucessora. Não limpar dados ou trocar assinatura; conferir ambos os aparelhos e testar Battletoads, confirmação, inputs e saída/retorno. Controles online próprios, latência externa e aquecimento medido continuam pendentes.

## Histórico anterior

# Sucessora visual R57 — fonte funcional online R55 preservada

Leia [R57: barra fina e Criar sala](versions/station-layout-r57-20261006/README.md) e seu `STATUS.json`. APK SHA `e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566`. A fonte atual é o snapshot R55 mais o overlay R57 explicitamente listado; não há mudança no protocolo/motor online. Faixa INSTALADO e posição das capas permanecem idênticas à R55. O pedido de revisão funcional R55 no servidor continua válido; ao alterar a Activity de salas, considerar também o layout R57. Candidato de prontidão d1b535c não integrado; nenhuma partida em dupla declarada corrigida.

## Publicação R55 e histórico preservados

# Fonte atual do app: R55 enviada para análise do servidor — 06/10/2026

A versão atual é **R55**, instalada no Motorola e identificada pelo APK SHA-256 `4c8de4f899af291becdf22c0b551df5e03a813f7ecf536fb360436a5d24d7b39`. Leia [o handoff R55 APP → SERVIDOR](versions/station-current-r55-20261006/HANDOFF-APP-R55-PARA-SERVIDOR-20261006.md) e [o snapshot atual](versions/station-current-r55-20261006/README.md).

R42–R55 ficaram anteriormente apenas no PC/aparelho; esta publicação corrige a defasagem. O candidato de prontidão do servidor d1b535c está preservado, mas foi derivado da R41 e **ainda não foi integrado na R55**. Conciliar com `StationSessionChannel`, fechamento idempotente e HUD atuais: não substituir a Activity inteira pela R41. R55 não é estabilidade geral, não tem partida entre dois aparelhos comprovada nem controles online próprios corrigidos. Não executar a receita de empacotamento R41 sobre R55. Fontes, hashes, testes e dependências externas estão no snapshot; nenhum APK, segredo ou mídia privada foi publicado.

## Histórico anterior — as referências R41 abaixo não identificam o APK atual

# Battletoads: delta de prontidão implementado sobre R41 — 06/10/2026

Leia `docs/server/RETORNO-BATTLETOADS-CONEXAO-HOST-STATION-20261006.md` e `versions/station-relay-readiness-20261006/README.md`. Produção: dois membros/ambosPronto/start200/ticket200/WSShost, semhost-listening observado/sem novosbytes; convidado ficou starting. Delta3Java conecta e conserva TCP real, sinaliza após TCP+WSS, dispensa dependência exclusivaJNI, mantém Binder/sessão e elegibilidade do convidado.39checksTCP/TLS/relay passaram,12,58MB por direção;150Java/API34 compilaram emapi-check-only. NÃO há APKnovo/instalação/gameplayvalidado nem causa específica JNI/Binder comprovada. Usuário conectará porUSB o telefone que abre o jogo noPCWindows: capturar logs antes de atualizar; seguir build_candidate.py→package_candidate.py, somenteclasses35.dex sobreR41/hashb6b19321, certificadooriginal, licença/saves preservados. SnapshotR41/APIa2bb176/PID875574/motores preservados; não forçar connecting. Clipboard247bb0a jápublicado no site/retornoservidor0820fd0, semAPK; usuárioentrou antes. LogsprivadosforaGit, não publicar segredo/serial/apelido. Se houver source sucessor noPC, conciliar antes de montar.

## Histórico anterior

# Battletoads: diagnóstico de prontidão do anfitrião — 06/10/2026

Leia `docs/server/RETORNO-BATTLETOADS-CONEXAO-HOST-STATION-20261006.md` antes da próxima atualização. Produção às18h02Maceió:2membros/2Pronto/start200/ticket200/WSShost, sala fica starting, nenhum host-listening observado e zero bytes de jogo novos. Não forçar connecting nem antecipar convidado. Usuário conectará porUSB o telefone que abre o jogo ao PC de produção: capturar Activity/logs nativo/JNI/Binder antes de instalar. Este Linux não acessa oUSBAndroid. Delta do túnel em preparação, ainda não compilado/instalado neste primeiro recibo. APIa2bb176/PID875574 preservada; manter fonteR41/assinatura/licença/saves e usar sucessorR41. Gameplay em dupla e causa específica do motor ainda pendentes.

## Histórico anterior

# Cadastro de clientes Station no painel — publicado06/10/2026

Leia docs/server/RETORNO-CADASTRO-CLIENTES-STATION-20261006.md e CADASTRO-CLIENTES-STATION-PRODUCAO-20261006.json. Administraçãofe4b631 publicada às15h45Maceió: Novo cliente e código, cadastro novo/existente, venda paga/cortesia/teste, segunda licença para outro aparelho. Código30min/uso único e senha administrativa para confirmar. Banco/backup/Chrome1440/390 e dois acessos sintéticos independentes na API pública passaram, limpeza confirmada, zero mensagens/compras. APIa2bb176/PID875574/SocialEnabled e catálogo14/2212 preservados. Fonte/runtime/snapshot/APKR41 mantidos; não recompilar por causa do painel. App continua usando desafio/ativação/sessão/perfil assinado; rotas de cadastro são privadas de administração. Orientação antiga de buscar apenas licença/Vendas foi substituída. Gameplay físico/POCO/latência continuam pendentes no retornoR41.

## Histórico anterior

# Códigos Station no painel publicado — 06/10/2026

Leia docs/server/RETORNO-PAINEL-CODIGOS-STATION-20261006.md e PAINEL-CODIGOS-STATION-PRODUCAO-20261006.json na mesma pasta. Site17e564a publicado: Códigos Station/Gerar código/Trocar celular, confirmação com senha administrativa, código30min/uso único/um aparelho por licença. HTTPS autenticado e hashes conferidos. Atualização somente no site; não exige recompilar APK. Fonte congeladaR41/runtime/manifestos mantidos, API/comunidadeR41 seguem o retorno abaixo. Nenhuma licença real alterada, zeroWhatsApp. Gameplay em dupla, POCO e latência externa continuam pendentes.

# Servidor da comunidade R41 publicado — 06/10/2026

Leia docs/server/RETORNO-COMUNIDADE-STATION-R41-20261006.md e versions/station-community-r41-20261006/evidence/server-deployment-r41.json. API a2bb176530fd4d2dfa740da7e934fd84d097404e, DLL d181bf97d5b39a334e95144267d6ece3f11d4e659a314d7d16cd2746e1999e13, SocialEnabled=true;186 checks autenticados no domínio público por três licenças sintéticas, conversa privada/pedido/aceite/dois membros/WSS65539 bytes por direção e pin conferido. Fonte/snapshot/DEX/APK R41 preservados; servidor retorna até32 mensagens privadas e64KiB das mais recentes. Catálogo14/2212, licenças/chaves/relay512/1024 e outros serviços preservados. Recibo5e40f7e confirma R41 instalada no Samsung/hashb6b19321/dados preservados. Agora testar R41 nos dois celulares: pessoas/DM/pedido/convite/sala/Pronto/Iniciar/gameplay. Conferir Voltar vindo das configurações e Boogerman no catálogo vsBattletoads no cabeçalho: causa ainda não estabelecida. POCO e latência externa continuam sem prova nova. Não usar delta R34 sobre R41, não limpar dados, não marcar estável geral e não enviar WhatsApp/MenuIA por inferência.

## Histórico anterior — os blocos abaixo descrevem evidências nas datas originais

# R41 instalada no Samsung — 06/10/2026

Atualização R39→R41 concluída, SHA integral b6b19321ec529945870dc919c3de5f0eba75aa54330d3672227b8e632302b28d conferido no aparelho. Sem desinstalar, limpar dados ou alterar a configuração de tela ligada. Leia `versions/station-community-r41-20261006/evidence/installation-samsung-r41.json` e STATUS. Catálogo abriu com sessão preservada; comunidade mostrou Online, zero salas, formulários de criação/conversa. USB saiu antes de conferir retorno/Pessoas online; testes em dupla e capacidades sociais do servidor pendentes. Recibo distingue capturas e observações. Servidor: handoff 32b12bc publicado, implantação não comprovada. Não marcar estabilidade geral nem partida em dupla.

## Estado de preparação anterior

# R41 comunidade + R40 céu — compilados em06/10/2026

Leia `versions/station-community-r41-20261006/README.md` e o handoff APP→SERVIDOR nessa pasta. APK SHAb6b19321ec529945870dc919c3de5f0eba75aa54330d3672227b8e632302b28d, DEX42c1fc51; R40 céu SOd7839c70 herdado. Fonte completa E:\ESTUDO APK\work\station-community-r41-20261006. Menu lateral/salas/pessoas/criar/conversa interna, segundo jogador f7f0561 conciliado, presença com reconexão/aviso e Voltar sem esperar rede.255Java+64C#; assinatura/preservação integral passaram. R40 mantém UIpreta, céuazul/nuvensclaras, seletordireita e robôloop.

**R40/R41 NÃO instalados: USB ausente; R39 abaixo continua última instalação comprovada.** Servidor novo tem extensão em dois arquivos, SocialEnabled=false por padrão. Conversa privada/pedido de vaga só habilitam mediante capacidades assinadas após operador publicar. Sem deployLinux, WhatsApp/MenuIA ou gameplay2Android. Não marcar estável geral. Preservar licença/jogos/saves/emuladores, usar APKsucessor, nunca desinstalar/limpar. MenuIA foi mencionado depois de recusa de WhatsApp real: canal ainda em esclarecimento, NÃO enviar externamente por inferência. Handoff explícito com limites de histórico efêmero32/peer,flag,rotas,ações e validação. Não misturar deltaDownloads11be7f3.

Servidor: delta e handoff publicados em `feat/station-community-r41-20261006`, commit `32b12bc5654b28f6dc73b9f5c2de2ef6a64bb616`. Recibo `versions/station-community-r41-20261006/evidence/server-publication.json`. Publicação Git confirmada; implantação Linux e instalação R41 no Android continuam pendentes.

## Estado anterior

# Instalação R39 confirmada — Samsung — 06/10/2026

R39 instalada por atualização, SHA integral e1a38b502843e3506c06f510e79741a6a6e65247ef1246264b9a361ad56cc840 igual ao APK. Abriu ESActivity/plataformas sem pedir login. Sem desinstalar/limpar dados. Recibo `versions/station-theme-collections-r39-20261006/evidence/installation-samsung-r39.json`. Configuração temporária de tela ligada restaurada e conferida em0; não deixar pendência antiga aberta. Conferência visual das novas funções/pesquisa e gameplay continuam separadas; não marcar estável geral.

## Estado de compilação e histórico anterior

# R39 compilado — temas, quatro Lotties, metadados e pesquisa — 06/10/2026

Leia `versions/station-theme-collections-r39-20261006/README.md`, STATUS e evidências. APK e1a38b502843e3506c06f510e79741a6a6e65247ef1246264b9a361ad56cc840; carrossel SO9bcb3113. Fonte canônica E:\ESTUDO APK\work\station-theme-collections-r39-20261006; APK final G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais. Preto/Azul persistente e quatro animações originais, descrições de coleções ampliadas, estrelas no botão principal, cabeçalho e botões atualizados, cursor novo no início, pesquisas plataformas/jogos com limpeza completa de tokens, Voltar explícito, recuperação vazia e cache de resultado vazio. Testes PC e restauração compilam módulo byte-idêntico. **R39 não instalado**; usuário conectará depois. Última instalação comprovada R38 Samsung, receipt anexado/corrigido. Não afirmar validação visual Android nem estável geral. Ajuste temporário de tela ligada Samsung ainda3; restaurar0quando reconectar.

Metadados atuais2212:2211comjogadores/2211comnota; faltam jogadores SMW hack Mega e nota Dragon’s Heaven development Neo.72XMLs/72033registros futuros/91838chaves não são downloads publicados;46152têm ambos. Sem inventar faltas. Fontes, ativos, licenças e procedência incluídos; recipes/restore_r39.py e build/test_r39.py preservam linhagem. SDK/stubs/objetos externos têm hashes em EXTERNAL-BUILD-INPUTS. DEX/motores/manifesto/licenças/downloads/salasR34 intactos; a626b50 e11be7f3 separados. Não instalar versões anteriores sobreR39, desinstalar ou limpar dados. Nenhum servidor alterado.

## Histórico anterior

# R38 compilado — capas, coleções e sinopses — 06/10/2026

Leia `versions/station-carousel-scope-r38-20261006/README.md`, STATUS e evidências. APK SHA58b337511bef62a98cae6d17982a4f139c1b0e6049def18894258d98dd5bbdfd, base exata R37, somente carrossel SO4a581bea. Efeito Neo Geo/CD somente nas revistas dos jogos; vídeos principais normais e LED externo preservado. ABRIR + coleção dentro do botão com largura da capa; Voltar ao lado. Selo instalado em cada capa visível, durante movimento, por índice real.52 sinopses de sistemas ampliadas;2.212 sinopses de jogos/perfil R37 intactos. Compilado/testadoPC, NÃO instalado porque USB desconectou; última instalação R37Samsung. Fontes W38 `E:\ESTUDO APK\work\station-carousel-scope-r38-20261006`. Restauração e testes a partir do snapshot conferidos. DEX/manifesto/emuladores/licença/downloads/classes35R34 intactos. a626b50 e11be7f3 separados. Não declarar gameplayonline/FPS/estável geral. Preservar dados e atualizar com mesma assinatura; conferir recibo antes de atribuir instalação.

## Histórico anterior

# R37 compilado — perfil real, sinopses completas e visual — 05/10/2026

Leia `versions/station-final-details-r37-20261005/README.md`, STATUS e evidências. APK SHA75fd8b5806c6aa683796e1301fa8a92e3236f106a8837a0279b6d0ae094999fc, fonteW37, somentecarouselSO+frontendSO sobreR36. Nome servidor ligado ao componente existente, fonte+50%/cincoespaços, faixa refinada,2.212sinopsesrecorte14 semvazios. Instalado no Samsung em06/10/2026, SHA integral igual aoAPK; recibo evidence/installation-samsung-20261006.json. Tela ligada temporária restaurada ao original. Conferência visual separada, sem gameplayonline. Conferirnome/visual noaparelho; nãoafirmar estávelgeral ou2jogadores. DEX/manifesto/motores/classes35R34 intactos. Retornoonlinea626b50 estánoGit mas nãofoiintegrado; deltaDownloads11be7f3 fora. Preservar dados/licença/saves e usarbaseR37parapróximointegração.

## Histórico anterior

# R36 preparado — nome da plataforma no botão e layout — 05/10/2026

Leia `versions/station-platform-button-r36-20261005/README.md`, STATUS e recibos. APK SHA dfe9dd4ce24fdca80986919e885b0a09d146f29dd8ab156f0dffdf18d2a46f57, somente carouselSO sobreR34;13.086 entradas preservadas. Nome/abreviação dentro botão da plataforma, sequência de metadados com dois espaços reais, cinco botões secundários iguais, faixa instalada mais alta/brilhante. 12.712 checks e assinatura/16KiB/preservação passaram. Instalado depois da reconexão no Samsung, SHA integral igual; recibo em evidence/installation-samsung.json. Conferência visual separada, sem teste de partida online. Fontes finais W36; restauração inclui JavaR34. Pendências Battletoads/player2/controles/Voltar em partida continuam. Sem mudança servidor. Preservar jogos/licença/saves. Não declarar estabilidade geral nem visual aprovado.

## Histórico anterior

## Retorno online recebido, ainda separado do APK

# Segundo jogador — delta conciliado com R34 — 05/10/2026

Leia docs/server/RETORNO-SEGUNDO-JOGADOR-SALAS-STATION-20261005.md. Fonte compilada f7f0561: perfil do anfitrião oferece Entrar; sala própria individual mostra outras salas com vaga, contagem1/2 e Sair e entrar após confirmação. Pronto confirma a sala atual.147 entradas Java/dependências compiladas,144 intactas e213 verificações aprovadas. DEX39864bd1/336988bytes. Conciliado com a8898a0/R34 instalado no Samsung513dd470, preservando recuperação da abertura/Voltar/manifesto e designR33. APK deste delta ainda sem montagem/instalação; a versão POCO não foi conferida. DEX inicial R30ef8a2d99 foi substituído. Servidor e4e557a inalterado. Preservar licença/saves/assinatura; não afirmar gameplay em dupla ou latência resolvidos sem prova nos aparelhos.


# R34 instalado no Samsung — 05/10/2026

Instalação solicitada concluída por atualização, SHA513dd4700192b994d93cdaf6cd55b79eccb804fa33eda43166304f5d2bcdb5ef conferido no aparelho. App abriu plataformas sem login. Ler evidence/installation-samsung.json no snapshotR34. Sem desinstalar/limpar dados. POCO ainda não conferido; Battletoads segundo jogador, controles e Voltar em partida continuam pendentes de validação. A configuração temporária Samsung de tela ligada foi restaurada para0. Não chamar de estável geral.

## Histórico anterior

# R34 — candidato de recuperação online; diagnóstico Battletoads pendente — 05/10/2026

Leia `versions/station-online-recovery-r34-20261005/README.md` e STATUS. APK SHA513dd4700192b994d93cdaf6cd55b79eccb804fa33eda43166304f5d2bcdb5ef, classes35+booleanoBack da Activity online sobreR33. Callback oficial Android33+, diálogo Voltar, retry explícito se abertura falha, fases de diagnóstico. Testes locais passaram; NÃO instalado, USB vazia. Segundo jogador Battletoads e controles diferentes continuam sem correção validada: não declarar resolvidos. Só host inicia; convidado automático emconnecting. SNES localEX+ e onlinebsnes/RetroArch têm controles distintos; não foram alterados. Capturar jogador2 primeiro, um telefone por vez; preservar licença/saves. Runtime/allowlist/servidor/design R33 intactos. Ler limitações Android26–32 e dois aparelhos nohandoff.

## Histórico anterior

# R33 — título maior, barra completa e faixa instalada — 05/10/2026

Leia `versions/station-title-actions-r33-20261005/README.md`, STATUS e evidências. APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Titulo-Barra-R33-20261005.apk`, SHA `9313b3b893468270512b8e8ee3fa984763d6db334b4534a2f863216a0cc4a7ea`. Fontes `E:\ESTUDO APK\work\station-title-actions-r33-20261005\native`. Compilado/conferido PC; não instalado, USB ausente. Usuário informou instalação manual anterior no POCO, hash/ativação não verificados. R33 inclui faixa diagonal R32, título +50% e contagem/jogadores/estrelas em sequência, Jogar com largura da capa e barra até97,5% da tela. 9.604 verificações C++, assinatura,16KiB e13.086 entradas preservadas; somente carouselSO mudou. DEX/motores/salas/downloads intactos. Não promover estável nem supor validação visual. Preservar dados/licença/saves. Samsung tela ligada0→3 continua pendente de restaurar0quando reconectar.

## Histórico anterior — a entrega atual está acima

# R31B — visual compacto e retorno servidor61c0411 — 05/10/2026

Leia `versions/station-interface-r31-20261005/README.md`, STATUS e recibos. APKfinal `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Interface-R31B-20261005.apk`, SHA76817d2dd48219bcd6e4d111b8471bf98925b02ab26ee517cea90e8df84b076c. Compilado/verificado, instalação final pendente. PrimeiroR31 efc2a845 instalado/hashconferido noSamsung, visual da linha/botões/tag registrado. R31B amplia otextoINSTALADO. Duas tentativasPOCO recusadas peloAndroid USER_RESTRICTED. Cópia emDownloads interrompida ao sair daUSB; pode estar incompleta, não instalar sem substituir/conferir. LicençaPOCO declaradaACTIVE/PENDING_ENROLLMENT nohandoff; código privado somente noLinux, não noGit. Não ativada por este agente.

Fontescanônicas E:\ESTUDO APK\work\station-actions-gear-r31-20261005\native. ApenascarouselSO +3assetsLottie,13083entradas preservadas; salasR29B/classes35 intactas.6873checksC++/15contrato, NDK/assinatura/16KiB e restauração integral de fontes passaram. FonteR30+deltas; gear3 licençaLottie preservada. Novo servidor61c0411/e4e557a jácompatível, nenhuma nova rota; latênciaWSSp95~2,29s e gameplaydoisAndroid permanecem pendentes. Nenhuma implantação. Downloads11be7f3 continuam fora. Não promoverestável geral. Preservar dados/saves/licença. Samsung mantertelaligada passou0→3; restaurar0quando reconectar. POCO sem ajuste de tela.

## Histórico anterior — a entrega atual está acima

# Servidor R12/POCO publicado — 05/10/2026

Leia `docs/server/RETORNO-SERVIDOR-NETPLAY-INTERNET-STATION-R12-20261005.md`. APIe4e557a/DLL7ecb6c8d/PID660598, WSS no mesmo domínio;512salas/1024conexões configuradas.256conexões reais/renovações e512TLSisoladas passaram. **Latência pública alta segue aberta:** p952291,82ms vs1,07ms Nginxlocal. DoisAndroid/gameplay não verificados. LicençaPOCO própria1aparelho/vitalícia, código somente privadoLinux, ativação até07/10 às17h11Maceió; licença original preservada.

Retorno mais recente b4a9806: R30 instalado/hash1768b7df, Voltar/criação de sala/Pronto verificados em um aparelho. Usar R30 ou sucessora comprovada noPOCO; preservar dados, assinatura, saves e fontes do estado abaixo. Reconectar salas, mesmaROM/core/runtime/opções; somenteSNES/Megaonline. Catálogo14/2212/50CD intacto. Downloads11be7f3/6f012a7 continuam fora desteAPK. Nenhuma instalaçãoLinux.

## Estado atual do aplicativo

# R30 — Voltar nas coleções e correções das salas — 05/10/2026

Leia `versions/station-back-rooms-r30-20261005/README.md`, STATUS e recibos. APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Voltar-Salas-R30-20261005.apk`, SHA 1768b7df440dcdf99efbd2e8ff93181eae06edaab5bb9be85e073afeb639027b. Instalação por atualização, sem desinstalar nem limpar dados; consulte recibo para hash do telefone e conferência visual. Sem promoção estável geral ou partida real entre dois celulares.

Base R27 + classes35 R29B (45675ff1) + carousel R30 (142ebfa9). Voltar nas coleções ganhou largura para seta e texto inteiro; Abrir mantém alinhamento, mesma geometria de desenho/toque. R26 restante intacto, R28 cancelado NÃO incluído. Salas: arquivo não baixado ganha mensagem correta, erro persiste após atualização da presença, iniciar exige dois participantes prontos e transporte anunciado; diagnóstico não registra credenciais. 773128 testes anteriores +252 de geometria +267 verificações Java/serviço/relay isolados passaram. Fontes nativas W30, Java W29, dependências W16/W22 e receita no snapshot. Sem servidor alterado; downloads11be7f3 continuam fora. Preservar saves/jogos/licença e usar versão sucessora comprovada.

## Histórico anterior — consultar acima para a entrega atual

# R27 — jogadores online em lista compacta e painel de convites — 05/10/2026

Leia `versions/station-compact-lobby-r27-20261005/README.md` e STATUS. APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Salas-Lista-R27-20261005.apk`, SHA c1191ce1d531b1ec9171d6d4c2f57541349339e64e8941a33788c4067d616bd6. Compilado/testado PC e instalado sobre R25 em 05/10/2026 às 18:02 (UTC−3), SHA integral do telefone igual. Dados preservados por atualização, sem desinstalar/limpar. Tela Android bloqueou durante instalação; conferência visual/sessão/gameplay R27 pendentes. Leia evidence/installation.json. Sem aprovação estética ou promoção estável desta revisão.

Sobre R26 exato, altera somente classes35.dex;13.083 entradas preservadas, inclusive carouselSO b2d706dc07d4423758798fe0d6d37ce01c8f395b344c685a7b796ce60d03dd70. Mantém layout/botões/LEDs/motores do R26. Lista48dp nome/status, perfil ao tocar, criar sala+convite real, código público TS1 (instance/roomId/itemId) com copiar/colar. Usa comandos existentes; não adiciona senha/token/servidor.107 testesJava+18preservação, assinatura/16KiB/pacote inteiro passaram. Fonte final E:\ESTUDO APK\work\station-compact-lobby-r27-20261005. TemporáriosE/APKfinalG. Não reaplicar receitas históricas nem instalarR26sobreR27. Dados/saves/licença preservados; instalar somente sem jogo/download ativo. Downloads11be7f3 continuam fora.

## Histórico anterior — posições e estados podem ter sido substituídos acima

# R26 — estrelas no cabeçalho, pasta/contagem e botões compactos — 05/10/2026

Leia versions/station-layout-r26-20261005/README.md e STATUS. APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Layout-R26-20261005.apk`, SHA `1d4549da6a15a9a9b2e8c52491ecc4382e0b5e050900763aebf163d136a36e75`. Compilado/testado no PC; ainda não instalado (USB ausente). BaseR25 `0d62d806fb0fd7ef45cf0167dd6908794e180e81171c8f7fa0b3e701aa78baad` continua última instalação, mas seu alinhamento foi rejeitado. Não confundir observação funcional com aprovação estética.

Pedido mais recente substitui posições anteriores: estrelas junto do estado Não instalado; pasta e contagem no lugar das estrelas acima do console, jogadores na mesma linha; contador abaixo da sinopse removido. Botões inferiores todos12% mais estreitos, retângulos de toque iguais ao desenho. Console fit R25, título, LEDs R24, sinopses e motores intactos.773.128 verificações e pacote completo passaram; apenascarouselSO muda/13.083 entradas preservadas. Fonte `E:\ESTUDO APK\work\station-layout-r26-20261005\native`; dependênciasW16+objetosW16/W22. SO permaneceE; APK final e base arquivadosG. Não promover estável nem supor instalação. Atualizar sem limpar dados, sem partida/download ativo.

Evidências R24 multiplataforma e integração R23B incorporadas; apenas históricas. Download11be7f3 não integrado. Chat coordenado prepara UI Java das salas e deve preservar SO R26 no próximo APK; coordenar antes de nova instalação.

## Histórico anterior — posições e estados podem ter sido substituídos acima

# R25 — estrelas e jogadores juntos, console maior — 05/10/2026

Leia `versions/station-console-panel-r25-20261005/README.md` e STATUS. APK `E:\ESTUDO APK\work\station-console-panel-r25-20261005\TurboStations-Console-Players-R25-20261005.apk`, SHA0d62d806fb0fd7ef45cf0167dd6908794e180e81171c8f7fa0b3e701aa78baad. Remove nota/legenda, mantém estrelas e mostra ícone com1/2players conforme dados (faixas usam máximo; ausente traço). Console maior com UV dos pixels visíveis, sem cortar/desfigurar. Contagem abaixo sinopse/título abaixo console preservados.

Base R24d355, LEDs intactos;3fontes mudam+2helpers.772.456 verificações PC,build/assinatura/alinhamento/pacote inteiro passaram; sócarouselSO muda,13.083 entradas intactas. Fonte final W25/native, W16+objetosW16/W22; APKbaseR24/SOfinal/rendersPC antigos arquivadosGcomhashes. Inicialmente compilado, instalação/visual consultarSTATUS. Não marcar estável nem supor dados faltantes. Downloads11be7f3 não incluídos. Preservar dados/saves/licença.

## Histórico anterior

# R24 — laser Neo Geo/CD no padrão SNES — 05/10/2026

Leia `versions/station-neogeo-laser-r24-20261005/README.md` e STATUS. APK `E:\ESTUDO APK\work\station-neogeo-laser-r24-20261005\TurboStations-NeoGeo-Laser-R24-20261005.apk`, SHA d35516420934aeda7cee96af6185a17506146ae7fa2c28f867d6e7c44e721a0b. Base APK R23A + fontes R23B (sem APK próprio) + quatro arquivos LED. Inclui contagem, jogadores/nota/título do painel R23B. Mesmo movimento/cálculo SNES nas revistas Neo; quadrado CD com feixe proporcional .007 e mesmo relógio. Preserva cores, máscaras, vídeos R22 e todos os motores/DEX.

8 programas GLES,135 comparações legadas (133 exatas;2 até1/255),126 envelopes,10 pares2D/OES e pacote inteiro conferidos. Só carousel SO alterado;13.083 entradas intactas. Fonte final W24/native, dependênciasW16+dois objetosW16/W22. SO e APKbase arquivadosG comSHA/recibos; não procurar sóE. Instalado às17:01 por atualização, SHAtelefone igual; capturaSNES com sessão. LEDNeo/validação de todasplataformas pendentes; STATUS/evidência posterior prevalecem. Novo pedido posterior (retirar nota/legenda, jogadores junto às estrelas e console maior) será R25 separado. Não marcar estável/FPS/aceite visual sem prova. Downloads11be7f3 continuam fora. Preservar jogos/saves/licença.

## Histórico anterior

# R23B — painel dos jogos preparado; integração R24 pendente — 05/10/2026

Leia `versions/station-game-details-r23b-20261005/README.md` e STATUS. Fonte `E:\ESTUDO APK\work\station-game-details-r23-20261005\native`, SO `48eda90ac617b1dbd318f8932883386466d5f3cc8cb10ec6586a4b499d953fab` (93843368 bytes). Layout comum a todos jogos: contagem abaixo da sinopse; jogadores/estrelas acima do console; nome abaixo do console. Índice exato2.212 IDs,2.148 jogadores/1.986 notas; ausências explícitas, nota do catálogo/XML. Não há média comprovada de usuários nem metadados novos por rede automática.

**Não há APK standalone R23B.** R23A58c61a4d1e74396ffbefb2c5b6108e1c78a951164080a3b0f32de696330233e8 foi instalado/hashigual, porém tela bloqueou antes da conferência; não contém contagemB. O chat coordenado prepara R24 com fonteB + quatro LEDs, sobre APK A. Consultar recibo R24 antes de declarar painel B instalado. FonteR22incluída integralmente, doisobjetospreviewsobrigatórios; jogos/saves/licença preservados. Tests12Python+11.070dados+26.834layout+8contagem passaram. Semestávelgeral; conferência visual multiplataforma pendente.

## Histórico anterior

# R22 — vídeos das coleções Neo Geo — 05/10/2026

Leia `versions/station-neogeo-collection-videos-r22-20261005/README.md` e `STATUS.json`. APK `E:\ESTUDO APK\work\station-neogeo-collection-videos-r22-20261005\TurboStations-NeoGeo-Colecoes-R22-20261005.apk`, SHA `f7dfc90f0614644548f16cfc7a518ba869589c815adacd6adb9f411f6a97de29`. Acrescenta vídeos de Fatal Fury, Metal Slug e Samurai Shodown às pastas exatas confirmadas no TSV do Servidor-pix, commit 100e4bb. Todos os jogos usa o vídeo da plataforma. Mídia 720×720 a 30 fps, duração original, sem cortar ou esticar, com prévias do próprio vídeo. Somente a célula focada reproduz; orçamento de 8 texturas e 4 slots preservado. Passaram 3.317 verificações de rotas, 15.375 de layout, 140 de rolagem e a decodificação integral.

Base R21 `4c6bf41312be20e98ff15a6b7fbc2f85bb470bca1af39058ab362e39015543b4`: somente o SO do carrossel alterado, 3 MP4 adicionados e 13080 entradas preservadas. Fontes R21 intactas (rolagem e console somente nos jogos), LEDs R20, N64, Neo Geo R18, DEX e motores preservados. Ver instalação em STATUS/evidence; não promover estabilidade geral ou FPS sem prova. Nenhum servidor alterado. Fontes finais em W22/native, dependências W16; SO compilado e APK/SO R21 arquivados em G: com SHA em evidence/compiled-output-archives.json. Não procurar apenas no caminho antigo em E: e não reaplicar pacote R18.

Instalação R22 confirmada pelo SHA do telefone. Logs mostraram os três vídeos preparados/retomados, mas houve um timeout posterior de pré-carga Fatal Fury durante navegação rápida; causa/recuperação e loop sustentado ainda não conferidos. Captura final estava na lista KOF. Ver evidence/runtime-summary.json. Retorno de downloads 11be7f3/6f012a7 foi lido e comparado, porém os dois módulos novos continuam fora deste APK; leia docs/server/ANALISE-RETORNO-DOWNLOADS-20261005-R22.md.

## Histórico anterior

# R21 — sinopses roláveis; console somente nos jogos — 05/10/2026

Leia `versions/station-synopsis-console-r21-20261005/README.md`, STATUS e evidências. APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Consoles-Sinopses-R21-20261005.apk`, SHA `4c6bf41312be20e98ff15a6b7fbc2f85bb470bca1af39058ab362e39015543b4`, 2041527332 bytes, instalado por atualização e hash do telefone igual. Fonte nativa final: `E:\ESTUDO APK\work\station-console-games-only-r21-20261005\native`. Base R20 arquivada em G; consulte recibo de arquivos antes de procurar APK/SO no caminho antigo em E.

Sinopses completas recortadas na área própria, altura medida pelo componente nativo; arrasto e barra quando transborda, sem paginação automática. Regra compartilhada por plataformas/coleções/jogos. Hardware somente ao lado da sinopse dos jogos; principal/coleções sem hardware nem coluna reservada. 15.375 checks de layout e 140 de rolagem passaram; ABI auditada, build/assinatura/alinhamento e todas as entradas do pacote conferidas. Android: sinopse longa 007 recortada, arrasto do texto/barra, início/fim e retorno N64 às plataformas conferidos; hardware só nos jogos. Outros sistemas usam o mesmo componente, sem afirmação de teste manual individual. Não promover estabilidade geral.

Somente carousel SO mudou, 13080 entradas preservadas da R20 (incluindo recursos N64 corrigidos, DEX/motores, NeoGeo/offline/pastas e LEDs). Próxima W22 de vídeos das coleções deve usar R21 como base e preservar este overlay. Nenhum deploy servidor. Nenhum ajuste exclusivo no telefone. Preservar dados/saves/licença.

## Histórico anterior

# Downloads CHD/ZIP preparados — 05/10/2026

Leia `versions/station-raw-transfer-20261005/README.md` e `docs/server/RETORNO-DOWNLOADS-SEM-VERIFICACOES-20261005.md`. Pedido do mantenedor: retirar conferências de integridade/conteúdo e reduzir a espera para baixar, após Neo Geo CD lento nas duas fases. Delta de quatro classes Station R16 + ponte ZIP; DEX/biblioteca Android compilados, 821 verificações Java/18 suítes e14JNI reais Linux aprovadas. **Delta separado ainda sem APK assinado/instalado; a última instalação visual confirmada é R21 acima. Não está incluído no APK R21.**

RAW recebido completo vira instalação por rename atômico, sem segunda cópia ou reabertura para conferir conteúdo; porcentagem/reserva uma vez. ZIP sem cálculo/validação CRC; mesmos libarchive3.8.9/xz5.8.3. Autorização usa catálogo salvo; consulta completa só por revisão alterada, com um refresh/retry. Transação, cancelamento, saves, TLS/licença e hash de identidade netplay preservados. Fontes R16/R18/R19B/R20 congelados não foram alterados. Só classes28.dex e libstation_archive.so mudam no APK; demais motores/recursos/carousel/classes35 devem permanecer exatos.

Produção catálogo14/2212visíveis/50CD inalterada. Metal Slug431225741B: API311,329MB/s/Nginx311,232MB/s; HTTPS3,225MB/s/133,7035s, variável. Sem medição nova do aparelho; não atribuir exclusivamente à operadora/túnel nem dizer311MB/s pela internet. Licença sintética removida e serviços/PIDs preservados. Novo APK deve usar R20 ou sucessora visual conciliada; preservar ajuste solicitado de consoles somente na sinopse. Receita exige SHAexatoR20; atualizar guard só com recibo da sucessora, sem instalar versão antiga. Ponte CD/BIOS continua entrega separada.

## Histórico R20

# R20 — LEDs Neo Geo e consoles — 05/10/2026

Leia `versions/station-console-led-r20-20261005/README.md`. R20 instalado por atualização, SHA do telefone igual a `64eae3ab4dd253e25ee826dd23bf02c947e5cbd1db70e6b07f759d988d465904`, APK em `E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005\TurboStations-Consoles-LED-R20-20261005.apk`, 2.041.498.580 bytes. Só carousel SO alterado; 13.080 entradas preservadas da R19B (inclusive resources.arsc N64, Neo Geo R18 e todos os DEX/motores).

Máscara própria para revistas Neo Geo e Neo Geo CD quadrado/vídeo, com programas 2D/OES e cores da arte. Sete ilustrações locais de hardware: SNES/Mega/N64/NeoGeo/CD/Naomi1/2; aliases regionais. Testes: 11.601 layout, 52 chaves, 3.030 navegação, 10 programas GLES/125 checks GL; 18 renders antigos byte-identical. NDK/API26, assinatura/alinhamento e preservação por entrada passaram. Android: foto MegaBR ao lado da sinopse observada; LED específico NeoGeo/CD ainda não conferido visualmente no aparelho. Não declarar estabilidade geral/FPS/consumo comprovados.

**Correção posterior do mantenedor:** console somente na sinopse dos jogos, não no carrossel principal/coleções. R20 já tinha sido instalado com hardware nos três modos; chat coordenado prepara delta sobre R20 para restringir isso, preservando os LEDs. Não repetir o layout R20 de plataformas como requisito final aprovado.

Fontes finais R20 em E: `station-console-neogeocd-r20-20261005/native`; includes/objeto restantes W16 em `station-download-performance-20261005/frontend-native`. Header console_assets gerado dos PNGs versionados; não depende da pasta de geração da IA. APK R19B e SOs históricos R19B/W16 arquivados G com hashes, fontes/recursos/stubs/objeto permanecem E. Novo motor CD recebido do servidor/Git ainda não incluído no APK R20. Preservar dados/licença/saves. Ver recibos e manifesto para próximos empacotamentos.

## Histórico anterior

# R19B — N64 próprio, abertura e controles conferidos — 05/10/2026

Leia `versions/station-n64-controls-r19b-20261005/README.md` e `RECONSTRUCAO-E-FLUXOS.md` na mesma pasta. APK instalado por atualização, agora arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-N64-Controles-R19B-20261005.apk`, SHA256 `c8fcb15f0951cf5874ac9de2fa2f2e9bfbe26813b7e9ddea5b897355cea4157c`, 2.036.265.660 bytes; hash do telefone idêntico. `STATUS.json` e recibos registram localização/estado; a duplicata APK em E: foi removida só após conferir a cópia.

N64: prefixo `lib`/caminhos resolvidos e slugs Station corrigidos no despacho; agora abre Mupen64Plus AE próprio. Primeiro R19 fechava por classe Material conflitante; R19B corrige 11 referências XML e o algoritmo de importação. Testes: 240 rotas + 3030 navegações + 80125 checks XML; comparação dos 43618 recursos compilados mostrou somente essas 11 diferenças. APK muda somente carousel SO e resources.arsc, preservando 13079 entradas, DEX/motores, NeoGeo R18, offline/download R16 e navegação R17. Certificado original/16KiB conferidos.

Android: 007 abriu em GameActivity/CoreService próprios, com entrada Android do Mupen. Mantenedor confirmou botões respondendo, menu próprio e saída sem login. USB caiu depois da captura inicial; controles/retorno são confirmação do mantenedor. Engrenagem do N64 não recebeu conferência visual nesta rodada; FPS/outros jogos não validados. Não promover a estável geral. Não houve correção só no telefone nem mudança no servidor.

Fontes finais: overlay native em `E:\ESTUDO APK\work\station-n64-controls-r19-20261005`, demais headers/objetos de `station-download-performance-20261005/frontend-native`. Usar recursos R19B. Base R18 e primeiro R19 arquivados em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais` (duplicatas E removidas após hashes iguais). Não instalar primeiro R19. Trabalho visual R20 separado ainda não integra esta revisão. Preservar jogos/saves/licença e atualizar sem limpar dados.

SO final R19B arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\binarios-compilados\station-n64-controls-r19-20261005\libturbo_carousel.so`, SHA e0f13c18e0f6c4efe8e1d279422f9ed5516bd4f8cc21b7df1cf0ab1406fd248c; `resources.arsc` final continua em E:. SO de saída R16 também arquivado conforme `evidence/native-output-archives.json`; fontes, stubs de ligação e objeto de mídia continuam E:. Para reproduzir R19B usar base R18 + SO + recursos corrigidos; para uma funcionalidade posterior usar R19B ou sucessora comprovada. A receita sem sufixo b é histórica e não deve gerar a próxima entrega.

## Neo Geo CD recebido separadamente

Os commits remotos 0e82d7a/140f43a/5dea14c e seus documentos foram preservados na conciliação. O delta CD foi preparado sobre R18 e NÃO está no APK R19B. A receita de empacotamento CD exige revisão para usar a base R19B e preservar SO/recursos N64 corrigidos; não executar a receita R18 sobre a instalação mais nova. Nenhum novo motor CD foi instalado nesta entrega.

## Histórico anterior (R18 e retorno CD anterior à R19B)

# Neo Geo CD preparado — produção catálogo14 — 05/10/2026

Leia `docs/server/RETORNO-NEOGEOCD-20261005.md` e `versions/station-neogeocd-20261005/README.md`. Servidor publicou 50 CD / 2.212 jogos com capas/sinopses; BIOS CD ausente. Delta MAME Java/DEX preparado, ainda sem APK assinado/instalação. **R18 abaixo é a última instalação comprovada**, com filesystem/rompath, R17 navegação, R16 offline/download e N64 completo. O delta CD foi conciliado com este retorno e recompilado; usar R18 como base e preservar licença/dados/saves/certificado.

---

# R18 — Neo Geo filesystem + navegação R17 — 05/10/2026

Leia `versions/station-neogeo-filesystem-r18-20261005/README.md` e os recibos. APK `a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4`, 2.036.266.872 bytes, em `E:\ESTUDO APK\work\station-neogeo-access-20261005\TurboStations-NeoGeo-Pastas-R18-20261005.apk`. Instalado por atualização; SHA no telefone idêntico. Não promover a estável nem afirmar todos os jogos validados.

Causa Neo Geo: ROMsDIR físico ativava SAF sem URI no MAME. Ponte final define PREF_ROMsDIR_2 vazio (modo local upstream) e ACTION_VIEW cli_params `-rompath 'pai real'`; aspas simples do parser nativo. Só classes30 alterado para Neo Geo; classes29/core/configurações/saves intactos. 166 verificações de métodos reais + 15 contratos e API34/D8 passaram. Inclui SO R17 4d2b962e, com 3030 verificações de navegação; integra R16 offline/download sem revertê-lo. Duas entradas alteradas, 13079 preservadas, assinatura/alinhamento conferidos. R16 APK base está em G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais.

Fontes da ponte final em E:\ESTUDO APK\work\station-neogeo-access-20261005\java. Navegação em E:\ESTUDO APK\work\station-single-folder-r17-20261005\native, herdando recursos R16. Não reaplicar receitas antigas nem instalar base R15/R16 por cima. Nenhum servidor modificado. Atualizações preservam dados.

SVC Plus R18: seleção de personagens observada às 15:01; mode=filesystem/rompath correto e sem erros de arquivo no recorte. Mantenedor confirmou controles funcionando e saída. USB caiu antes de capturar retorno; navegação R17 no aparelho, outros jogos e desempenho sustentado seguem sem prova.

## Histórico anterior

# Navegação R17 compilada — subpastas únicas — 05/10/2026

Leia `versions/station-single-folder-r17-20261005/README.md`. Header nativo pula telas com um único caminho e mantém escolhas com jogos diretos/ramificações. Voltar restaura a última tela exibida/seleção.3030checksC++ passaram, teste rejeitaR16 anterior, SO Android compilado SHA4d2b962e09c7924e7b9b14042ee4b43e08d704bedae021131668303ae42fb39d. **Ainda não instalado**: integração será feita junto de correçãoNeoGeo no chat “Desmonte o APK de testes (2)”. Não marcar estável nem substituir motores aqui.

Fonte isolada `E:\ESTUDO APK\work\station-single-folder-r17-20261005`; inclui cpp/search_download do overlayR16, demaisheaders/objeto da baseR16. APK R16 instalado b52313bc... agora arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Desempenho-Offline-R16-20261005.apk`; duplicataE removida apósconferência. Preservar Javaoffline/download, classes35/N64, assinatura/dados. Instalação futura exige recibo novo; blocos históricos abaixo.

## Histórico

# R16 instalado — desempenho e abertura offline — 05/10/2026

Leia `versions/station-performance-offline-r16-20261005/README.md` e `BUILD.md`.
APK `b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1`, 2.036.268.564 bytes, instalado por atualização e hash do base.apk igual. Pasta atual de fontes/build: `E:\ESTUDO APK\work\station-download-performance-20261005`; APK `TurboStations-Desempenho-Offline-R16-20261005.apk`. Base R15 arquivada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`, sem duplicata APK em E.

Download/instalação de jogos sem SHA do corpo por pedido explícito: escrita 256KiB, sem busca/hashing de legado, sem releitura integral, consulta local apenas do entrypoint. Preserva tamanho/paths/transações/saves/TLS/licença. Hash do netplay permanece para identidade de sala. Native TSV de diagnóstico retirado do loop SDL; arquivo velho no aparelho não é catálogo atual. Fases e MB/s reais. Offline após catálogo assinado salvo; HTTP de poll não ocupa fila dos jogos locais. Ver handoff para bloqueio conhecido e limites.

787checksJava/16suítes,32C++,API34/D8/assinatura/alinhamento passaram. Três entradas mudaram,13078preservadas; classes35/N64/NeoGeo/motores intactos. Android: Classic Kong recebido262144bytes em86ms; autorização141ms,cabeçalhos136ms,preparação102ms,UIINSTALADO/JOGAR. É arquivo pequeno, não prova taxa sustentada. Benchmark64MiB em Android é armazenamento sintético, não rede. Conferência offline coordenada separadamente; consultar evidência mais recente. Não promover a estável nem alegar gameplay de todos os motores. Nenhum deploy servidor. `CATALOG_PUBLISHED status=503` é marcador local herdado para cache, não prova HTTP503; usar traceHTTP.

Não reaplicar scripts históricos na fonte congelada. Não partir de shared `station-netplay-20261004` (anterior) para perder R15/R16. Atualizar sem desinstalar/limpar dados. Preservar tags estáveis e insumos privados.

## Histórico anterior

# R15 instalada — 05/10/2026

Atualização por USB concluída com sucesso, sem desinstalar ou limpar dados. SHA256 do base.apk no telefone **d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b**, igual ao APK preparado. Aplicativo aberto; catálogo Neo Geo com capa, sinopse e botões observado, sessão mantida sem digitar credenciais. Configurações de tela não alteradas. Recibo: `versions/station-emulators-r15-20261005/evidence/installation.json`.

Gameplay NeoGeo/N64, configurações do novo N64, retorno à coleção e medição real de FPS ainda não foram conferidos nesta instalação. Não promover a estável. Fonte candidata completa continua em `E:\ESTUDO APK\work\station-n64-complete-20261005\frontend-native`; shared native anterior continuaR14B. Nova instalação deve preservar a integração N64 e os ajustes R14B.

## Estado anterior à instalação

# Candidato R15 Neo Geo / N64 — 05/10/2026

Leia `versions/station-emulators-r15-20261005/README.md` e `BUILD.md`. APK **d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b**, 2.036.244.940 bytes, em `E:\ESTUDO APK\work\station-emulators-r15-20261005\TurboStations-NeoGeo-N64-R15-20261005.apk`. Compilado/assinado, **NÃO instalado: USB ausente**. Último instalado continua R14 a1566d3d. Não promover a estável nem afirmar gameplay corrigido no aparelho.

Neo Geo: chave real MAME PREF_ROMsDIR_2 e diretório pai do artefato Station. N64: Mupen64Plus AE 3.0.249(beta), commit33bf702, completo com UI/controles/plugins próprios, processos:n64/n64core, prefs n64., storage interno preparado. 53checksMAME,154rotasN64,127integração,49storage passaram; assinatura/16KiB/integridade integral conferidas. Cinco entradas antigas alteradas,11106preservadas,1970adicionadas; classes35R12 exato. Sem deploy servidor.

Base R14B **arquivada em G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R14B-20261005.apk**, hash661a8738 completo no handoff; duplicataE removida só após conferência. Fonte canônica shared `station-netplay-20261004/native` permaneceR14B; fonte candidata completa `station-n64-complete-20261005/frontend-native`. Não perder pacing60 e retorno path+kind. Próxima instalação integrada é R15, coordenada com chat Desmonte o APK de testes (2). Atualizar sem desinstalar/limpar dados; conferir NeoGeo, N64/controles/settings, retorno à coleção e fluidez sem toque. Receitas históricas não devem ser reexecutadas sobre base nova.

## Histórico

# Estado vigente — R14B fluidez/retorno compilado, USB pendente — 05/10/2026

Leia `versions/station-navigation-r14b-20261005/README.md`. APK **661a8738faf2e598d448017bcb87f09e7d39ac7d2984a653fac4e9a642a9742f**, 2.006.925.798bytes, `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Visual-R14B-20261005.apk`. R14B mantém alvo60FPS no carrossel visível após parar toque (antes15/30 após650ms); vídeo30FPS permanece. Voltar e refresh restauram coleção por path+kind, inclusive após reordenação. 2080checks navegação,80política e600frames simulados passaram; ambos testes rejeitam código anterior. Apenas1SO alterado,11110entradas preservadas, assinatura/alinhamento verificados. **Não instalado: USB ausente na conferência. R14 a1566d3d continua último instalado/hash confirmado.** Sem medição nova GPU/temperatura/frame real. Não marcar estável.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004\native`; build/backup `navigation-r14b`. R14/R13/R12 e HUDR2 arquivados em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais` com hashes verificados. UsarR14B como base da próxima integração NeoGeo/N64 isolada no outro chat; não incluir inadvertidamente mame/classes30 de visual-r14. Motores, DEX, salas, vídeos, dados, cache e assinatura preservados. Nenhuma implantaçãoLinux ou alteração da configuração de tela.

## Histórico anterior

# Estado vigente — R14 visual instalado; 05/10/2026

Leia `versions/station-visual-r14-20261005/README.md` e `evidence/device-result.json`. APK **a1566d3d34305e01f5f445b6b61fb3db4e35fc8a4bc8a2f3e493fb3a433a38bf**, 2.006.925.798 bytes, instalado por atualização e hash do base.apk igual. Botões inferiores com ícones/cores por função observados no SNES. Vídeos das coleções: célula original quadrada, vídeo inteiro sem crop/deformação e fundo derivado preparado offline; prévias novas. PC: 4096 meshes,1836 posições quadradas,443 navegações e5 vídeos decodificados. USB caiu antes da conferência visual do vídeo/retorno no telefone; não alegar essa prova nem marcar estável.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004`; build `visual-r14`; APK `TurboStations-Visual-R14-20261005.apk`. R13 eR12 arquivados em G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais com hashes. Apenas4MP4 e1SO alterados sobreR13;11106entradas preservadas, classes35R12 e todos motores/DEX intactos. `native/video720_posters.o` canônico já contém49prévias; não adicionar novamente os5símbolos. Regeneração usa legado44 de `collection-video-r13/before/video720_posters.o`. Não reaplicar scripts one-shot. Nenhuma alteração em configuração de tela ou dados.

Trabalho NeoGeo/N64 separado em outro chat está em preparação; `visual-r14/mame` e `visual-r14/classes30.dex`, criados por aquele trabalho antes de sua separação em `E:\ESTUDO APK\work\station-emulators-r15-20261005`, NÃO fazem parte deste APK/snapshot. Não empacotar a pasta por wildcard. O próximo candidato deve partir do R14 verificado e preservar mídia/visual/salas. Netplay R12/servidor continua conforme handoff anterior; não houve deploy Linux aqui.

## Histórico anterior

# Estado vigente — R12 netplay internet preparado, instalado, servidor pendente — 05/10/2026

Leia `versions/station-internet-r12-20261005/README.md`. Pedido vigente usa o mesmo servidor Station para conectar redes distintas. Implementados WSS próprio, tickets individuais de uso único, bridge TCP local, encerramento e limites. Cem verificações locais passaram, inclusive Java→WSS C#→Java com 12.583.029 bytes em cada sentido. APK SHA256 **7684c6eee87985d8259becca9a22a9f4c7e3203f7c097df37da6998975596514**, 1.982.967.774bytes, em E:\ESTUDO APK\work\station-netplay-20261004. Fonte final `internet-r12`; netplay/src promovido com backup. R11 agora arquivado em G: com hash verificado.

**Sem implantação Linux e sem partida entre dois aparelhos validada.** Operador publicará quatro arquivos e habilitará Station:Online:RelayEnabled no serviço existente com proxy WSS. Motores online continuam SNES/Mega; NeoGeo/arcades pendentes não foram liberados. Não marcar estável. R12 instalado por atualização após reconectar USB, com SHA256 do base.apk conferido igual. Após desbloquear, ESActivity/carrossel com oito plataformas observado, sem login. USB caiu novamente ao entrar na plataforma; salas e partida seguem sem prova nesta revisão. Configuração de tela não alterada; último valor conhecido0. Todos os motores/design/coleções/dados preservados.

Retorno remoto c8e240a de Neo Geo/taxa foi lido e preservado na conciliação Git. O delta de taxa MB/s ainda NÃO foi aplicado ao APK R12; Neo Geo offline usa o catálogo existente, online Geolith continua bloqueado. Não executar package_delta.py do retorno com base R11 apagando classes35 R12; próxima montagem precisa preservar este DEX.

## Histórico e entrega paralela preservados

# Estado vigente — Neo Geo publicado e taxa MB/s sobre R11, 05/10/2026

Leia `versions/station-neogeo-rate-20261005/README.md`. Servidor catálogo 9, 2.162 jogos, 189 Neo Geo válidos, 255 IDs ocultos preservados, 2.119 sinopses e 374 jogos em subpastas. Neo Geo está na raiz do HD; 826 arquivos foram movidos sem alteração. Entrega mantém jogo ZIP fechado e BIOS ao lado. Alpha Mission II recebeu somente a BIOS exata no pacote de entrega; Art of Fighting 2 aguarda substituição do ZIP corrompido.

O retorno 6ef86c4 foi incorporado: R9 é último instalado comprovado; R11 é compilado/assinado, USB pendente e ajuste de tela já restaurado a 0. O delta novo tem somente JNI, helper de taxa e native_search_download, com guardas SHA/backup. Preserva Java R10, coleções R11, quatro capas, fila, ABI, salas, assinatura e dados. Não reaplicar overlays históricos, não substituir classes28/classes35 pelos DEX antigos nem executar scripts one-shot R10/R11.

O contador avança de 1 MB em 1 MB; isso não mede MB/s. Medições Linux: API 316,35 MB/s, Nginx 259,99 MB/s, HTTPS até 4,37 MB/s; sem limitador de bytes/s encontrado. Fonte nova mostra percentual e taxa real somente durante Baixando. 9 verificações C++ de taxa e 5 Java de ZIP/BIOS passaram; JNI compilada. Nenhum APK desta taxa foi assinado ou instalado no Linux. Incorporar JNI/carousel juntos sobre a base R11 canônica, mesmo certificado e atualização sem limpar dados. Gameplay Neo Geo e partida entre dois aparelhos ainda precisam de evidência.

## Histórico anterior

# Estado vigente — R11 coleções e servidor integrados, USB pendente — 05/10/2026

Leia `versions/station-collections-r11-20261005/README.md` e o handoff R10 referenciado. APK final **7c5096d58991a9724537036e18eb42555f290e2f6d673904524520da0d0146d5**, 1.982.770.888bytes, compilado/assinado; **NÃO instalado: USB ausente**. Inclui tudo do R10 e corrige coleções: remove célula Jogos sem subpasta, conserva Todos os jogos incluindo raiz, nomes exatos visíveis e descrição com quantidade/títulos reais.440checks de navegação e6153textoUTF8 passaram. UmSO alterado sobreR10,11.102entradas preservadas. Não alegar visual Android ou partidas validados.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004`; APK R11 na raiz; build/testes/backup em `collections-r11`. R10 eR9 arquivados comhash em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`. **R9 continua último instalado comprovado; tela durante carga restaurada0**, não há pendência nesse ajuste. Manter salas/controles/motores/dados, não reaplicar scripts one-shot, não mover tag estável. Nenhum deployLinux. Próximo passo: conectarUSB, atualizar sem desinstalar e conferir coleções+integraçãoR10.

## Histórico superado abaixo

# Estado vigente — R10 biblioteca compilado, USB pendente — 05/10/2026

Leia `versions/station-library-r10-20261005/README.md`. Retorno N64/biblioteca do Servidor-pix4e623bc aplicado sobreR9; fontes8do overlay ba669c mais cancelamento por geração, prioridade à fila de capas, validação metadata e diagnóstico de rota. APK R10 **8bc1d2ef1b5864dc1d5359d1df05b90593cf483dff7f48819f7a7a6b52a84c0b**, 1.982.754.504bytes, compilado/assinado, três entradas alteradas e11.100 preservadas.659checksJava,465C++ e paginaçãoUTF8, assinatura e integridade completa passaram. **Ainda não instalado: USB ausente.** Não alegar gameplay N64, visual, consumo ou partida2aparelhos validados.

**R9 foi instalado e seu hash conferido no aparelho em04/10**, recibo nesta versão/evidence/r9-installation.json. `stay_on_while_plugged_in=0` já restaurado e conferido; NÃO está pendente. Históricos que dizemR8 último instalado estão superados. R9 agora arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`; só cópia duplicada deEfoi removida após hashes iguais.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004`; build `E:\ESTUDO APK\work\station-library-r10-build-20261004`; APK R10 na raiz canônica. Não reaplicar overlay antigo, não misturar candidato40mil, não trocar classes35/salas/motores. Instalar atualização preservando dados quando USB disponível. Catálogo1973/revisão8/sinopses1957/N64157/folderPath313 são evidências do operador, não uma nova medição do telefone. Sem implantação Linux nesta rodada. Tag estável preservada.

## Histórico superado abaixo

# Estado vigente — N64, subpastas e biblioteca automática, 04/10/2026

Leia primeiro `versions/station-library-autodiscovery-20261004/README.md`. Servidor publicado: fonte `931030bba25ca8a783f096b72dcecd26a7b49387`, catálogo **8 / 1.973 jogos visíveis / 157 N64**, 255 IDs ocultos e 1.957 sinopses; 16 edições sem fonte. `folderPath` está publicado nos dois contratos do catálogo, com 313 jogos em subpastas. Timer de importação por minuto e reload da API a cada 10 segundos ativos. Capas N64 exatas da revista, compiladas em 480×720, conferidas por HTTPS com quatro workers.

A fonte R9 `a325e69` foi conciliada com a leitura de metadata assinada e consulta automática em primeiro plano, mantendo cache, leases, navegação por pastas, salas e ABI nativa. O overlay tem oito arquivos com guardas SHA e backup. Java, DEX e JNI compilados; **433 verificações Java, 36 C++ de coleções, 429 C++ de navegação e paginação UTF-8 passaram**. O renderer R9 teve sintaxe conferida com imagens sintéticas somente no teste.

**R8 é o último APK instalado comprovado. R9 é candidato assinado no Windows, ainda sem instalação; as mudanças desta biblioteca ainda precisam ser incorporadas ao próximo APK.** Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004`. Aplicar overlay à fonte R9, reempacotar a base R9 alterando somente classes28/libstation_frontend/libturbo_carousel e preservar classes35 das salas R9 e todas as outras entradas. Assinar com o certificado original e instalar por atualização. Não alegar gameplay N64 ou partida entre dois aparelhos sem prova. Restaurar `stay_on_while_plugged_in=0` quando a USB retornar; a desconexão deixou o valor temporário 3.

Os blocos abaixo registram estados anteriores. A pendência de publicação de `folderPath` do retorno R9 foi atendida pelo servidor; não usar essa pendência antiga como estado vigente.

# R9 — salas e subpastas compiladas; USB pendente — 04/10/2026

Ler `versions/station-ui-folders-r9-20261004/README.md`. APK `b5c98ea40b915f738e29ef2b2e7168fcdf2d327aa64c862596dff15b5620fdf1` pronto, **NÃO instalado**. Último instalado/observado: R8 `8e76d832…`. R8B somente PC, arquivado em G:. R9 inclui banner/capa real, efeitos leves, colunas adaptáveis/chat e subpastas no carrossel nativo. Campo opcional `folderPath` é novo e precisa de publicação pelo operador; catálogo anterior continua plano. Não há varredura de pastas arbitrárias do telefone. A pergunta sobre origem local/servidor ainda está pendente.

Novo retorno Servidor-pix `a4814d453a1f193fcbe40a92c8690c4eb5d41fc9` relata **salas online publicadas às 11h29**, com provas HTTPS. Foi lido e o contrato do app permanece compatível. Não usar o404 antigo como estado atual. Partida entre dois aparelhos e R9 visual/consumo Android seguem pendentes. Esta rodada não implantou Linux; implantação das subpastas também não ocorreu.

Testes: 591 Java existentes, 29 de pastas Java, 20 C#, 36 C++ de agrupamento, 429 de navegação, 34 regressões UI e 1.440 malhas. Quatro entradas do APK alteradas; 11.098 preservadas. Dados, assinatura, motores e tag estável preservados. **Restaurar `stay_on_while_plugged_in=0` quando a USB voltar**: desconectou com valor temporário3 após conferir R8. Fontes e compilação em `E:\ESTUDO APK\work\station-netplay-20261004`. Estados abaixo são históricos.

# R8 visual compilado — instalação pendente, 04/10/2026

Ler `versions/station-ui-r8-20261004/README.md` e evidence/build-result.json. APK `8e76d8328d140a6f423b9317a77bc4f154cb5de882d8e24db16df8b71f0ea783` pronto em E:, ainda não instalado por USB ausente; R7 continua último instalado comprovado. R8 uniformiza seis ações dos jogos com brilho verde animado e redesenha salas em três áreas (jogadores, salas/convites, chat). Duas entradas mudaram, 11.100 preservadas; 34 verificações e 1.440 geometrias C++ passaram. Sem mudança de API, auth, motores, vídeos ou implantação. Compilação reproduzida com hashes iguais. R7 arquivado em G: com hash, cópia duplicada de E: removida; não procurar R7 apenas no antigo caminho. Tag estável preservada. Não alegar visual Android, desempenho ou partidas validados. Operador publicará servidor; pendências de R7 continuam. Histórico abaixo.

# R7 instalado — salas aguardando operador, 04/10/2026

Ler atualização em `versions/station-online-20261004/README.md` e evidence/r7-rooms-runtime.json. APK82772343 instalado por atualização e hash no aparelho conferido; botão nativo abriu tela real das salas e Voltar retornou à lista sem login. Serviço vivo respondeu404, correlação060358fe191f4bd0af58b6ada9d45d75; operador aplicará branch feat/station-online-direct-20261004 por decisão do usuário. Não criar ou afirmar salas reais/partidas antes da implantação. Tela temporariamente ligada restaurada0, XML próprio removido. Células das plataformas continuam azuis; sinopse Battletoads conhecida ausente, SNES contadorinstalados0 observado sem auditoria. Preservar dados e investigar sem supor perda/causa. R7 continua candidato, sem teste2aparelhos. Pacote servidor portátil compilado e teste local flagoff passou, sem deploy. Histórico abaixo.

# Candidato R7 online — 04/10/2026 (não instalado / não estável)

Ler `versions/station-online-20261004/README.md`, o handoff APP→SERVIDOR nessa pasta e `evidence/online-build-result.json`. APK SHA256 `827723436ac618d3b1745a873813c7781ff10e043abc6033de416c01d774703d`, em E:\ESTUDO APK\work\station-netplay-20261004. R4 permanece instalado; USB ausente. R7 inclui R5 (vídeo sem espera fixa, prévias reais, SNES roxo), botão nativo Jogar online, salas assinadas, runtime direto em processo próprio com sessão controlada pelo processo principal e confirmação real listen() do host. SNES/ClownMDEmu candidatos; Geolith compilado mas Neo Geo não liberado (.neo/BIOS pendentes). Servidor social é código NOVO desativado, não implantação existente. Não alegar partida, visual, consumo ou compatibilidade determinística verificados sem Android e dois aparelhos. Preservar tag estável, fontes de E:, dados/assinatura/licença/jogos/saves/motores locais e produção. R6 anterior não deve ser instalado. Estados seguintes históricos.

# R5 preparado — vídeos e SNES roxo, 04/10/2026

Ler `versions/station-video-navigation-20261004/README.md`. APK `afa300d23dc57bb5b1973530dc83371fc892d6c37cf11ecc1750aed8ff22415b` compilado/assinado, não instalado: USB ausente. R4 segue instalado. R5 remove espera80ms, conserva prévias nas listas, usa quadro inicial real44vídeos e cacheGPU8texturas/8.294.400bytes, compositor próprio, SNESroxo e corrige texto solto da rede.109 verificações PC e shader/pixel ANGLE; Android/consumo pendentes. Não chamar estável. Netplay completo e servidor social ainda em implementação separada; não estão nesse APK. Fontes/temporários E:\ESTUDO APK\work\station-netplay-20261004. Preservar saves, sessão, assinatura, motores locais, tags estáveis e produção. Estados abaixo históricos.

# Estado atual em 04/10/2026 — R4 instalado

Ler a conferencia Android no HANDOFF-R4.md e device-evidence/r4-runtime.json. APK17e9b87b instalado/hash conferido; sessao1816/8instalados e sinopses Clay Fighter/Cutthroat/AddamsBR observadas. Limite real: arte das celulas de plataformas azul sem imagem, origem pendente. Netplay menu original ainda sem partida comprovada. Ajuste tela restaurado0 e tres probes HUD removidos. Proxima solicitacao Netplay com alternativas comerciais, partidas diretas, servidor proprio para salas/presenca/chat/convites; LED SNES roxo e botao Jogar online. Nao afirmar isso implementado no R4. Manter dados, assinatura, jogos, saves, branch/tag estavel e servidor produtivo. Blocos seguintes historicos.

# Revisão R4 — sinopses Mega, publicação de capas e revisão Netplay

Ler `versions/station-visual-covers-netplay-20261003/HANDOFF-R4.md`. APK `17e9b87bf268c2349874d1767d5ab315862eb09fb2705f9b79a7e307c0c63c77` em E: pronto, NÃO instalado (USB ausente). Telefone ainda R2 `31ab80ef`; R3 foi arquivado em G: com hash.706 IDs Mega/BR corrigidos desde R3,975/981sinopses confirmadas,6ausências explícitas. R4 adiciona180regressões que falham no R3 e passam no atual: publicação Java atômica e descarte/reset nativos do commit1dc8c381. Netplay Mega/SNES NÃO implementado pelo motor atual; menu informa antes dos botões, PSP/Dolphin/Flycast preservados, sem lobby Station nem partida2aparelhos comprovada.564Java,28C++,17metadados,3636lookup,98layout,9exportação,28netplay,GLSL e carga4096/cache passaram. FixtureJNI compilada não executada. Não promover a estável nem trocar motores. Preservar dados/licença/saves. Instalar R4 quando USB voltar; restaurar stay_on_while_plugged_in=0 e limpar apenas probes próprios do recibo.

# Revisão R3 — sinopses conciliadas; instalação pendente USB

Ler `versions/station-visual-covers-netplay-20261003/HANDOFF-R3.md`. R2 `31ab80ef` instalado/hash confirmado, sessão/capas/shader Android e foto SNES observados. Encontrado erro do app: mapa preliminar trocava741IDs preservados; R3 `8ece6384b83f565ec54615186a5940c6e5c47f79d4f03027332181799c4fb807` usa catálogo conciliado54bba11, todos1816casados exatamente;1804sinopses,12ausentes. Exportação TSV deixa de repetir por capa. Testes PC completos passaram; R3 NÃO instalado por USB desconectada. Não promover à estável. Reconectar, instalar por atualização, verificar sinopse/retorno e restaurar stay_on_while_plugged_in=0; probes próprios listados no recibo. Preservar dados, licença, jogos, saves e tag congelada. Estados R2 abaixo históricos.

# Candidato R2 — capas contínuas, sinopses, LED e Netplay, 03/10/2026

**Conferência posterior no PC concluída:** ler `versions/station-visual-covers-netplay-20261003/pc-validation/README.md`. 384 testes Java, 10 repetições de41 corridas, carga4096/cache4096 (4 simultâneos,0 erros,0 requisições extras no cache,0 workers após fechar),18 C++,13 metadados,98 layout,26 netplay,GLSL ANGLE e integridade integral APK passaram. DEX reconstruídos idênticos; APK31ab80ef inalterado. Nenhum ADB/produção usado neste turno. Teste no telefone adiado por pedido do mantenedor; não chamar estável. Correção apenas no lançador de teste e exportação do teste Netplay, documentadas no recibo.

Ler primeiro `versions/station-visual-covers-netplay-20261003/README.md` e `build-result.json`. Branch `feat/station-capas-visuais-netplay-20261003`; base publicada HUD `49d2b867daad584f7b6f82abccdc91798cb6d161`. APK final `31ab80ef2c77e9c5dff294d6f63807ab1e6d6cded81c2beec7aee171067f46d8`, 1922513242 bytes, em `E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R2-20261003.apk`. Compilado/assinado; quatro entradas alteradas, 10.871 preservadas, motores/HUD inalterados. **Ainda não instalado: telefone ausente na USB. Não chamar estável nem alegar velocidade/Netplay/visual Android comprovados.**

Quatro capas simultâneas, nenhuma espera fixa após sucesso, cache persistente, leases de sessão, TLS reutilizável somente após EOF íntegro e arquivo local exato validado antes da busca. 384 verificações Java + 18 C++ de fila/retry passaram. Sinopses1804/1816,12 sem fonte única,167 XMLs descritivos novos. Shader real do tema PC aplicado à capa de jogo selecionada; imagens de console SNES/Mega. Jogar em rede liga às interfaces originais PSP/Flycast/Dolphin; não há lobby Station nem Netplay SNES/Mega. 13 testes de metadados,98 casos de layout,26 verificações Netplay e GLSL100 no ANGLE passaram; ainda falta Android/dois aparelhos.

Servidor lido no retorno 54bba11c52f35695fd47eabc7145f42af9990426, API 4bb77ed2b8fb01fe967b90dc18ec3fbd1ee5d58b relatada em produção, limite4096 capas/min licença+aparelho e16384/origem. Medição48capas/4546,55ms é do Linux relatada pelo servidor, não deste telefone. Fonte upstream1dc8c381 foi comparada; apenas melhorias complementares TLS/arquivo portadas, preservando leases/gerações. Não houve alteração/deploy Linux.

Fonte/build canônico `E:\ESTUDO APK\work\station-visual-covers-20261003`. Builds e temporários E:. Insumos privados identificados, sem publicação de ROMs/BIOS/credenciais. Capacidade desta linha4096, candidato40mil continua separado. Tags estáveis preservadas. Primeira montagem62068502 não instalada foi arquivada com hash conferido em G:. Quando o telefone voltar, restaurar o ajuste temporário `stay_on_while_plugged_in` de3 para0 e remover somente os probes próprios listados no handoff HUD; não desinstalar/limpar licença para testar.

## Histórico anterior — não identifica o candidato atual

# HUD LZ Games R2 instalado — SNES/Mega, 03/10/2026

APK `6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b`, instalado por atualização e hash no telefone conferido. Ler `versions/hud-lzgames-20261003/README.md` e `evidence/device-runtime.json`. Visual do HUD nativo conferido nos dois motores; cinco ações: Continuar, Salvar/Carregar estado (dez posições), Configurações próprias e Sair. Novo save manual Mega `.00.gp` observado, mas posição10/carregar/cancelar/substituir e configurações pelo HUD ainda pendentes de teste controlado. R1 `3d3afc38` rejeitada por sobreposição de texto; R2 corrige Text::drawScaled e mostra cinco ações. Somente duas bibliotecas mudaram sobre base8f494041; 10.840 entradas preservadas. Fontes/build em E:\ESTUDO APK\work\station-hud-lzgames-20261003. Não misturar candidato40mil, não mover tag estável. USB desconectou; restaurar `stay_on_while_plugged_in` de3 para0 na próxima conexão (tentativa falhou por ausência do aparelho). Novos pedidos posteriores: efeitos do temaPC, sinopses por nome/IDStation, foto console, capas4concorrentes e investigação netplay; não fazem parte deste APK.

## Base anterior — controles SNES/Mega, 03/10/2026

APK8f494041ca4ae37fbd8becb50a1a7156ea2141e717af41452e5a1a923e0799b0 instalado por atualização e hash no telefone conferido. Ler `versions/mega-explus-20261003/README.md`, `evidence/storage-installed.json` e `storage-runtime.json` se existir. Revisãoe87a352b REJEITADA: MD.emu leu config compartilhado do SNES porque o helperfilesDir não é usado pelo nativo em API>=11. Correção nos overrides reais NativeActivity.getFilesDir/getExternalFilesDir/getCacheDir, raízes resolvidas pelo Application para não recursar.16 testes Android em fixture isolada passaram; Cutthroat Island observado em execução com controle próprio do Mega (direcional/A/B/C/Start), sem mistura com SNES. Evidência storage-runtime.json. Não testados individualmente todos os botões, salvar/carregar e saída nesta última revisão. Todos motores nativos e recursos permanecem iguais ao e87; somente4DEX+fontes atualizados. Não editar pastas do telefone manualmente, não importar config compartilhado, não chamar estável antes da conferência. Compilação E:\ESTUDO APK\work\station-mega-explus-20261003; APK terminadoCONTROLES-CORRIGIDOS-20261003.apk.

## Histórico da primeira instalação Mega

# Candidato atual instalado — SNES e Mega Drive completos, 03/10/2026

APK atual `e87a352bc61ce6b2f120d4657451471313a1e4e7671e37c572d9904fcc1ef7be`, instalado por atualização às18:42:35; hash no aparelho confirmado. Ler `versions/mega-explus-20261003/README.md` e recibo. MD.emu1.5.85 completo, processo:megadrive, controles/menus próprios; SNES completo preservado.30 testes de seleção executados no Android passaram. Host chegou às plataformas sem pedir login; painel/jogo Mega ainda aguardam conferência. GenPlusGX continua necessário para Master System/Game Gear; não apagar. Fonte/build E:\ESTUDO APK\work\station-mega-explus-20261003. Não promover a estável nem misturar com40mil. Nenhuma mudança de servidor. Branch de trabalho continua `snes-explus-completo-20261003`.

## Candidato anterior instalado — SNES completo

Branch `snes-explus-completo-20261003`, derivada da estável9793840. Ler `versions/snes-explus-20261003/README.md` e `evidence/installed.json`. Snes9x EX+1.5.85 oficial prerelease integrado com interface/controles próprios e painel próprio, processo:snes. APK62377e8d55617a9d0aefaed42d0b1a17948f9c5997b7be713dc760c4420f8c25 instalado por atualização, hash do aparelho conferido, host abriu nas plataformas. Ainda pendentes abertura do painel SNES e jogo/controles/saída; não declarar estável nem desempenho validado. Fonte/build isolados em E:\ESTUDO APK\work\station-snes-explus-20261003. Outros motores, Station/auth/catalog/download e recursos visuais preservados. Não misturar com candidato40mil; tag estável abaixo intacta. Licenças do upstream e limites de distribuição documentados no handoff.

# Estável de recuperação — Station SNES / Mega Drive, 03/10/2026

Referência: branch/tag `estavel-station-snes-megadrive-20261003`. Ler primeiro `docs/server/HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md` na raiz do Git (cópia na raiz canônica E:). Manifesto e inventários em `versions/estavel-station-snes-megadrive-20261003/`.

APK SHA256 `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`, 1902768022 bytes; congelado em `E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk`. Fontes em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`, mirror `versions/station-reconstruction-20261002`. Cliente `1.0.8-station-storage-20261003.3`.

Sessão/perfil/catálogo1816/capas e dois downloads/instalações/aberturas comprovados; SNES e Mega Drive retornaram sem login, conforme confirmação do mantenedor. Instalados persistiram ao reiniciar.327 verificações locais e10 de armazenamento no Android passaram. Raiz/permissão/recursos e consulta de espaço Android corrigidos no APK; nenhum reparo manual da árvore real do telefone. Assinatura, jogos, saves e licença preservados.

Escopo estável é o fluxo SNES/Mega observado, não todos os jogos/motores ou checkout comercial completo. Servidor: retorno fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61, API fd13c0d relatada em produção. Meta seguinte autorizada: preparar40mil jogos em revisão separada APÓS congelar esta tag. Nesta estável permanecem4096 itens/12MiB; não alegar40mil implementados. Não alterar a tag congelada. Limites, metadado Battletoads USA/ESP e legado nativo residual constam no handoff.

**Todos os estados abaixo são históricos. Este bloco e o handoff completo prevalecem.**

---

## Regra permanente — instalação nova e reinstalação

Toda correção de pasta, recurso ou configuração necessária ao funcionamento deve entrar no fonte e no APK, com preparação automática repetível que preserve arquivos existentes. Não depender de criação manual de pastas, cópias por ADB ou ajustes exclusivos do telefone de teste. Conferir a primeira inicialização com pastas ausentes e a retomada após permissão, além da atualização. Usar fixtures isoladas; não desinstalar/limpar o aplicativo principal para simular uma instalação nova, pois isso apaga a identidade Keystore/licença. Registrar qualquer recurso ainda não verificado sem alegar preparação completa dos emuladores.

# Integração Station instalada — 03/10/2026 16:17 — estado atual

As correções de runtime `02c09dd36fcfa6c69ceb481f0934e84eef01e5ae` foram integradas e compiladas no Windows/E:. Branch de entrega `integracao-station-producao-20261003`. APK `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795`, 1.902.751.638 bytes, instalado e hash no aparelho conferido. Fonte canônico `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`; APK `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`.

302 verificações Java/API34, 28 da ponte JNI Android e 7 de retry C++ compilado pelo NDK e executado no Android passaram nesta rodada. Em relação ao APK anterior f5b35419, só `classes28.dex` e `libstation_frontend.so` mudaram. Assinatura, manifesto, design e motores preservados. APK anterior guardado em `build/previous-f5b35419-20261003/TurboStations-Station-ANTERIOR-f5b35419.apk`.

**Impedimento atual comprovado:** o mantenedor confirmou ter desinstalado o TESTE antes desta instalação. Uma tentativa autorizada com o código do handoff privado retornou ACTIVATION HTTP403 às16:19:13, correlação `1354b75f239f4fd7be8761df5efd7f8e`. Não repetir o código nem retirar a autenticação. O operador deve conferir essa requisição e liberar/reemitir a ativação para a nova chave da instalação conforme as regras comerciais. Não atribuir a recusa a consumo/expiração/bloqueio sem a conferência no servidor. Código/licença não foram publicados.

Servidor b1511b9 relata APIfd13c0d implantada, catálogo revisão3/1816 e provas HTTPS. Esse catálogo ainda NÃO foi validado neste APK por causa da recusa de ativação. Capas, download, instalação de jogo e retorno continuam pendentes no aparelho. Limite4096/12MiB permanece; suporte a mais15mil não foi implementado. Não promover a estável. Nenhum serviço Linux foi alterado.

Ler `docs/server/INTEGRACAO-APP-PRODUCAO-STATION-20261003.md` na raiz do Git e `versions/station-reconstruction-20261002/evidence/integration-production-20261003.json`. Na pasta canônica E:, a cópia do handoff está na raiz. Os blocos abaixo são históricos; este estado tem precedência.

---

# Retorno confirmado do servidor — 03/10/2026, 15h21

**Ler primeiro o [handoff único atualizado](https://github.com/luziellacerda/Servidor-pix/blob/b1511b9f75815aceb78dea801bb7ccc29f1036ab/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md).** A API Station foi implantada em `fd13c0d27eaab6a4dcf931a9cd64c3dcd7dd50c4`, DLL SHA256 `f305ae3763cb77a53a27b2c168c8de290191b3a7e88e612850856b6f7be7e639`. HTTPS autenticado confirmou **catálogo revisão 3 / 1.816 jogos**, `snes=644`, `snesbr=191`, `megadrive=887`, `megadrivebr=94`; cinco pares capa/download 200 (2 raw/3 ZIP) com assinatura, MIME, tamanho e SHA256. Um ID anterior oculto também foi autorizado e transferido; reuso dos cinco grants foi negado. O eco de `X-Correlation-ID` passou após corrigir duas linhas nas rotas Station do proxy.

**Causa dos 404 localizada:** a identidade Linux da API não conseguia abrir nenhum dos 996 jogos nem suas capas. O índice também tinha plataformas/nome incorretos e duplicatas: os 99 registros de outras plataformas apontavam para arquivos SNES/Mega Drive. A conciliação preservou todos os 996 IDs e capas anteriores: 741 IDs de jogos canônicos + 255 entradas ocultas de compatibilidade, e 1.075 jogos novos. A API lista 1.816 jogos; o índice privado contém 2.071 entradas. Foram conferidos 4.142 arquivos/hash sob o usuário real do serviço. Migrations 028/029 e chave já existiam; backup foi restaurado em banco temporário e os serviços compartilhados preservados.

O mesmo handoff contém **listas completas** com nomes/IDs/revisão/capas/descritores/hashes e a tabela dos 996 IDs anteriores. O catálogo cruzado teve 1.816 correspondências exatas com a resposta HTTPS assinada e zero IDs faltantes. Usar catálogo fresco revisão 3, IDs exatos e o mesmo Bearer entre autorização e GET; cache revisão 1 precisa ser atualizado. `catalogVisible` é configuração privada do servidor e não entra no payload do app. O HD fornecido comprova SNES/Mega Drive; os 12.346 nomes históricos não provam acervo das demais plataformas.

**Fonte Android continua 02c09dd36fcfa6c69ceb481f0934e84eef01e5ae**, com 302 verificações Java no host e 7 da política C++. Esta atualização registra a implantação do servidor; **não gerou nem instalou APK novo**. Preservar assinatura/pacote/Keystore/licença/jogos/saves/motores, aplicar as correções de fonte no build canônico E: e testar no aparelho: catálogo fresco 3/1.816, capas, download/cancelamento, instalação/recibo, abrir jogo e voltar. ADB e a base privada de montagem/assinatura não estão disponíveis neste ambiente Linux; a prova HTTP não substitui UI/instalador/emulador.

Os blocos abaixo descrevem o APK auditado antes do rollout ou revisões anteriores. O total 996 e os 404 daquele recorte não identificam a API publicada agora; permanecem como evidência histórica. Não promover o APK a estável sem as provas no aparelho.

---

# Correções de fonte da revisão — 03/10/2026, 13h40

O pedido posterior do mantenedor autorizou implementar os achados. Ramo isolado `feat/station-review-fixes-20261003`, derivado da revisão `db68b613cda008052afef8152400b9c595dfcffa`. Capas voltam à fila após60 s; autorização/conferência local/GET até os cabeçalhos compartilham a sessão; a transferência pode prosseguir junto de capas e renovação. `ready()` exige a mesma sessão do catálogo; atualizar consulta perfil. Plataformas desconhecidas são contabilizadas e avisadas, mantendo os jogos com mapeamento verificado; seis aliases reutilizam pastas existentes. Timeout e404 têm textos precisos. Correlação usa `X-Correlation-ID` e SHA256 de item/cover, sem tokens, licença ou caminhos. `clientVersion` do próximo build: `1.0.8-station-review-20261003.1`.

Evidência de fonte:302 verificações Java no host e7 da política nativa; [resultado](versions/station-reconstruction-20261002/evidence/review-fixes-validation-20261003.json). **Sem compilação Android/NDK, sem novo APK e sem instalação nesta rodada.** O APK instalado continua f5b35419, runtime629a55a8, com os404 documentados abaixo. Build/assinatura/aparelho seguem o ambiente E: descrito no handoff. Preservar identidade, Keystore, licença, jogos, saves e motores.

Retorno operacional único do servidor: [RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md](https://github.com/luziellacerda/Servidor-pix/blob/feat/station-artifact-descriptor-20261002/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md). Ele responde APP-01 a APP-14 e distingue release candidata, API instalada e bloqueios. O material abaixo descreve a revisão anterior e permanece como evidência do APK instalado.

# Revisão integral Station — 03/10/2026 — entrada atual

Leia primeiro [HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md](docs/server/HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md) e [mapa/integridade](docs/server/revisao-app-20261003/APPENDICE-MAPA-E-INTEGRIDADE.md).

Branch `revisao-integracao-station-servidor-20261003`, runtime `629a55a8cf48722460007944cf0bb737e9f8fb75`. APK instalado atual: SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, pacote `org.turboramastation.frontend`. Fonte: `versions/station-reconstruction-20261002/`. Esta revisão publica documentação e evidências; não gera outro APK nem promove a estável.

Sessão/perfil/catálogo200; total996 registrado na rede.176SNES/28SNESBR são contagens da exportação nativa, não histograma HTTP capturado. Capas404 e autorização404 não têm causa definitivamente localizada: revisar também o cliente. Há14 achados/limitações no handoff; inclusive retry de capas, concorrência de sessão, plataforma desconhecida, limite4096, instrumentação e texto de erro conclusivo demais. Não afirmar que o app está correto por receber200/404.

O código novo convive com renderer/launcher binários preservados; eliminação física integral do legado e execução de jogo por instalação Station ainda não comprovadas. Preservar Keystore, licença, dados, jogos, saves, design e motores. Build/temporários somente E:. Pedido ao servidor é revisão de código e evidências; não é deploy automático.

**Os estados e hashes abaixo são históricos. Este bloco e o novo handoff têm precedência para identificar o candidato atual.**

# Estado confirmado em 03/10/2026

Candidato 43670211 instalado, hash verificado. Login salvo e catalogo de 996 itens abriram. Loading corrigido e texto some ao concluir. SNES tem 176 porque corresponde ao catalogo Station publicado; mantenedor espera mais de 800. Ler handoff de catalogo incompleto. Ainda nao e estavel nem migracao integral concluida; faltam capas/downloads reais, indice completo e legado residual.

# Reconstrucao Station - APK candidato integrado

Leia versions/station-reconstruction-20261002/README.md e os handoffs. Candidato 38e78fde instalado em 03/10/2026, hash conferido; 204 testes locais e verificacoes nativas. Login real ainda aguarda validacao. Nao promover a estavel. Legado nativo residual e importacao de jogos antigos estao documentados como pendentes.

# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
## Cliente Android de licença comercial em preparação

[Fontes e receita](versions/station-android-client-20260930/) e [handoff para o servidor](docs/server/HANDOFF-CLIENTE-STATION-ANDROID-20260930.md): cliente compilado em APK candidato a partir da base 1189899e; login comercial desligado até entrega de URL, chave pública e rotas do servidor. Candidato não instalado nem promovido a estável. A tela nativa de catálogo/download ainda precisa de ponte direta para `StationContent`; não afirmar que as compras ou downloads comerciais já estão protegidos.

## Vídeos Arcade/Final Burn Neo/MAME instalados

[Atualização atual](versions/atualizacao-2026-09-30-videos-arcade/HANDOFF.md): APK1189899e, instalação e hash conferidos, base544fdecb preservada. Mapa Arcade corrigido e capacidade de prévias ajustada. Demais motores, vídeos BR e login preservados.

## Atualização posterior à estável — vídeos e handoff servidor

[Vídeos BR/NDS instalados](versions/atualizacao-2026-09-30-videos-br/README.md), APK544fdecb. [Handoff completo do servidor Android](docs/server/HANDOFF-TURBORAMASTATION-ANDROID-20260930.md), incluindo saudação com nome do comprador. Login remoto ainda não implementado. A referência ESTAVEL.md/tag05dd34b mantém o APK78accf4c de recuperação.

# Estável atual — estavel-2026-09-30-plataformas-emuladores

Versão instalada e promovida a pedido do mantenedor. **Comece por [ESTAVEL.md](ESTAVEL.md)** para identificar APK, fontes e limites. [Alterações completas](versions/estavel-2026-09-30-plataformas-emuladores/ALTERACOES.md) · [Pastas e restauração](versions/estavel-2026-09-30-plataformas-emuladores/RESTAURACAO.md) · [Manifesto](versions/estavel-2026-09-30-plataformas-emuladores/MANIFESTO-ESTAVEL.json).

43 plataformas; PSP BR; Xbox clássico integrado; PC Engine CD preciso/BIOS local; capas Jaguar/PCE CD; Naomi/Naomi2 preparados para receber jogos; vídeos PSP BR/Game Gear/SNES BR/MegaDrive BR/Xbox/Naomi atualizados. Capas baixadas persistentes. Economia de vídeos e remoção de nave/estrelas preservadas. PS2 permanece ARMSX2 e está parado por ordem expressa. Hash do APK **78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2**. Nem todos os jogos/motores novos têm execução individual comprovada; consulte os limites antes de diagnosticar.

## Documentação histórica — não identifica a versão atual

# Xbox 360 — candidato experimental de30/09/2026

[Atualização Xbox 360](versions/atualizacao-2026-09-30-xbox360/README.md): XenDroid0b11201,24 jogos/24 capas, vídeo720, configurações próprias e processo separado no mesmo APK. Candidato929339ae compilado/assinado, ainda não instalado. GameCube/WiiU incluídos; estável3573db1 preservada. Telefone descarregou, instalação adiada. Consulte manifesto e handoff para pastas e reprodução.

## Histórico

# GameCube / Wii U — 30/09/2026

[Atualização atual](versions/atualizacao-2026-09-30-gamecube-wiiu/README.md): GameCube integrado/instalado com 37 jogos carregados; Cemu Android 0.5 incorporado para Wii U, 9 jogos/9 capas, APK pronto e instalação adiada pelo mantenedor (telefone descarregou). PSP confirmado pelo mantenedor. Wii U e GameCube ainda sem conferência de jogo/retorno. Não promovida a estável. APK candidato b11f0acc, instalado cd1a8a55. Consulte manifesto e restauração para pastas e hashes.

## Histórico

# Atualização PS2/PSP em avaliação — 30/09/2026

Leia [a atualização](versions/atualizacao-2026-09-30-ps2-psp/README.md) e seu manifesto: ARMSX2 2.7.2 e PPSSPP 1.20.4 incorporados no mesmo APK, instalado com hash conferido. PS2 abriu GTA e retornou às plataformas; PSP em teste pelo mantenedor. Design e sessão preservados. Não promovida a estável.

Ramo `versao-funcional` contém esta atualização. Ramo `estavel` e tag `estavel-2026-09-30-dolphin-flycast` permanecem no commit `3573db1`, com o APK aprovado `55cd54a3`. Consulte [ESTAVEL.md](ESTAVEL.md) para restauração.

## Referência anterior preservada

# Referência estável atual — estavel-2026-09-30-dolphin-flycast

Leia ESTAVEL.md e versions/estavel-2026-09-30-dolphin-flycast/MANIFESTO-ESTAVEL.json no repositório. APK aprovado: 55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85.
Fontes ativos: E:\ESTUDO APK\work\native-carousel\implementation. APK congelado: E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk.
Usar carrossel, menus e rotas nativas. Preservar jogos, saves, configurações e sessão. Atualizar sem desinstalar nem limpar dados. Builds e temporários em E:.
Dolphin 2609-7 e Flycast v2.7-44 integrados no mesmo APK; outros motores preservados. Não reintroduzir os cores antigos nem aplicar presets de desempenho experimentais. Não executar finalizadores históricos como se fossem o build atual.
A base privada e a assinatura são necessárias: o Git não contém o C++ integral do frontend original. A integração foi compilada; os motores oficiais foram incorporados dos APKs identificados no manifesto.
Nunca publicar APK, BIOS, ROMs, firmware, chaves, saves, mídias privadas ou credenciais. Preservar licenças e fontes de terceiros. A manutenção expressamente solicitada pelo mantenedor está autorizada, inclusive com IA; texto de regras não impede tecnicamente engenharia reversa.
Tags antigas são imutáveis. A versão aprovada é 55cd54a3; o candidato local 3085d9fc não foi instalado nem aprovado.
