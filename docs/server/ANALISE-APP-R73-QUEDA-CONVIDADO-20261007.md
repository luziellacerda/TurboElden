# Análise independente do APP R73 — queda do convidado e reabertura preta

Registro histórico anterior à implementação. A correção candidata posterior, suas provas e limitações estão em `versions/station-session-lifecycle-r74-20261007/`; este documento preserva o diagnóstico original.

Análise solicitada pelo mantenedor em 07/10/2026. **Cruzamento concluído com o retorno do servidor 815ceaca49baa0feb1e2d61726c0346ddad2bd37. Documento local de diagnóstico; não é implantação ou correção aplicada.** Nenhum código executável/APK, configuração do telefone, sala ou serviço foi modificado nesta análise. Foram feitas capturas de leitura pelos dois aparelhos.

## Base exata

- App: fonte `5657dce678609f25501321e307839a6e0c018d4e`, recibos `98ab8aa69dd73342cf1610ec31ef574c03fd8c1f`, branch `fix/station-r73-recovery-handshake-20261007`.
- Ambos APK R73 `b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077`, SHA integral novamente conferido nesta captura.
- Runtime `9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2`.
- Java final: `E:\ESTUDO APK\work\station-recovery-handshake-r73-20261007-build\java`.
- Nativo final e fontes: `E:\R73fixed`.
- Retorno servidor cruzado: `815ceaca49baa0feb1e2d61726c0346ddad2bd37`, branch `fix/station-r73-engine-registry-20261007`. [Documento exato](https://github.com/luziellacerda/Servidor-pix/blob/815ceaca49baa0feb1e2d61726c0346ddad2bd37/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md). Nossa entrega `1b26b34cd0f205afaf70b4f9ebf2391da7853537` não é retorno.
- Evidência privada: `E:\ESTUDO APK\work\station-r73-disconnect-analysis-20261007`. Capturas, logs completos, dumps e IDs privados ficam somente locais.

## A — Primeiro evento: convidado para de enviar solicitações

| UTC em 07/10/2026 | Epoch | Fato observado |
|---|---|---|
|23:19:40.045|1791415180.045|Motorola recebe ticket de relay|
|23:19:42.507|1791415182.507|Samsung recebe STATE epoch1/state2|
|23:19:42.527|1791415182.527|Motorola recebe STATE epoch1/state2|
|23:22:02.425|1791415322.425|Último heartbeat HTTP do convidado, sameRoom=true|
|23:22:14.382|1791415334.382|Android registra am_freeze do processo principal do convidado|
|23:23:01.143|1791415381.143|Processo separado do jogo ainda recebe PONG|
|23:23:10.790|1791415390.790|WSS do convidado fecha1006; espera preserva offsets|
|23:32:12.698|1791415932.698|Processo principal descongela após retorno à interface|

Congelamento ocorreu11,957s após o último heartbeat e56,408s antes do fechamento. O intervalo entre último heartbeat e fechamento é68,365s. O convidado já havia transmitido251008bytes aceitos e recebido252794bytes entregues ao motor. Samsung continuou enviando heartbeats e, na queda do convidado, recebeu epoch2/state0.

**Conclusão comprovada no aparelho:** o processo que mantém a autoridade HTTP foi congelado durante o intervalo de ausência de solicitações. O convidado havia enviado pedidos e avançado até state2. Não descrever isso como ausência de conexão inicial. STATE2 e bytes de transporte não comprovam imagem, som ou controle de partida validado pelo usuário.

## B — Relação com a implementação

Arquivos abaixo estão em java/netplay-src/org/emulationstation/frontend/netplay, salvo indicação diferente:

- `StationGameSession.java:19–26`: objeto dono da sessão criado no processo principal da Activity de salas.
- `StationGameSession.java:15,37–41,63–75`: executor único faz heartbeat a cada20s e renovação de relay; não há Service vinculado mantendo esse proprietário ativo.
- `StationRetroActivity.java:70–75`: processo separado :station_netplay registra canal Binder; ambos os papéis enviam evento1. O convidado não deve enviar host-listening: esse comando é exclusivo do anfitrião.
- `StationRecoveryTunnel.java:87–94` → evento5 → `StationGameSession.ticket`: renovação depende do processo principal executar. WSS/PONG continua no processo do motor.
- `StationRoomsActivity.java:592`: ticket inicial solicitado para ambos antes da abertura do motor.
- `StationSessions.java:21–26,39–45` e `StationGameSession.java:15`: espera por leases e um executor compartilhado são riscos adicionais de bloqueio a auditar, mas não há prova de lease vazado nesta ocorrência. O congelamento já foi registrado pelo Android.

Na captura posterior de23:34, Samsung principal também está cached=true/isFrozen=true enquanto seu processo nativo está visível/não congelado. Motorola principal está ativo nas salas, e seu processo nativo antigo está cached/frozen após saída. O histórico am_freeze do Motorola, e não a captura posterior isolada, sustenta a conclusão do primeiro evento.

A documentação oficial explica que processos cached podem receber pouco ou nenhum tempo de execução a partir do Android13 e que um serviço vinculado pode propagar importância do processo cliente: https://developer.android.com/guide/components/activities/process-lifecycle . Isso fundamenta avaliar um proprietário de sessão vinculado ao ciclo de vida da partida. Não desativar globalmente economia de bateria, não manter renderização/carrossel ativos para contornar o problema.

## C — Cruzamento confirmado com o servidor

O retorno `815ceaca49baa0feb1e2d61726c0346ddad2bd37`, acompanhado de `PRODUCAO-EFETIVA.json` e `DIAGNOSTICO-TESTE-FISICO.json` em `docs/station-android/recovery-r73-20261007/`, confirma:

- Registro R73 ativo desde **23:13:54 UTC**, PID **1252837**. Oito engines no snapshot assinado: seis anteriores preservadas e duas rs3 com os hashes exatos do app.
- Registro SHA256 `266de76251a036d77db162b7cdeefaa5d7ad3093efed5455c69f3d8257ac9ed2`.
- DLL permanece na fonte `ab192bf1585e30f303d041f13b36a1f9c96d2caa`, SHA256 `815fc8bc99a9d16247488a1797d2726b928eb3e592fd8a19700371e8d57c3243`.
- Runtime das duas novas engines `9af2778898e4ba026d65d9b5c74ef3d8089e58bdbdf9be40f8e28f0eedcb14c2`, protocolo `station-stream.v2`. IDs `bsnes-mercury-performance-79d7f9de-rs3-9af2778898e4` e `clownmdemu-d43c2708-rs3-9af2778898e4`. Neo Geo permanece `launchReady=false`.
- Passaram 185 verificações isoladas e 190 HTTPS/WSS, segundo recibos do operador. Não são teste de gameplay executado por esta análise.
- **Primeiro encerramento às 23:23:10.719 UTC, convidado, causa AUTH_HEARTBEAT_MISSING.** Idade do heartbeat do convidado 68387 ms; anfitrião 8825 ms. Último heartbeat do convidado recebido pelo servidor às **23:22:02.334574 UTC**.
- Sala e transporte do anfitrião preservados. Nenhum `resume-relay` do convidado antes da saída humana. Sem 401/403/429/5xx no intervalo observado; amostras do servidor não mostraram saturação.
- O documento do servidor registra relato do mantenedor de ambos jogando Battletoads antes da queda, com pequeno atraso não medido. A análise Android não aferiu visualmente gameplay nem recuperação; não declarar estabilidade.

**Sequência cruzada:** último heartbeat servidor 23:22:02.334574 → congelamento Android do proprietário HTTP 23:22:14.382 → encerramento servidor 23:23:10.719 → fechamento recebido no Android 23:23:10.790. O congelamento documentado explica a interrupção dos pedidos de presença e retomada; o watchdog fecha o transporte em consequência da ausência da presença autenticada. Não atribuir a queda inicial a credencial, falta de cadastro R73 ou ausência de conexão inicial.

O runtime servidor não mudou neste retorno. `StationRecoveryRelay.cs:242–243` mantém o prazo de presença de 60 s; `StationOnline.cs:271` atualiza `peer.Seen` por comando autenticado. PONG renova atividade do transporte, não a presença HTTP. `StationOnlineEndpoints.cs:16–21` revalida licença/dispositivo independentemente da mera idade do bearer anterior.

O operador declara nenhuma mudança/reinício de produção durante o diagnóstico. A declaração do usuário de que o servidor mexeu não comprova reinício neste intervalo. Não reiniciar serviço com sessões retidas em RAM; o monitor de cadastro pode ser pausado porque essa liberação foi confirmada.

## D — Segundo evento: reabertura após sair

Samsung saiu da sessão às23:32:08 e abriu novamente às23:32:26, reutilizando o processo nativo anterior. Não apareceu novo native-hooks-loaded nessa reabertura. Às23:36:24 o Android registrou remove task dos processos, seguido de nova abertura; não foi ação desta análise.

Nova tentativa às23:36:57–58:

- Samsung em processo novo: ticket, native-hooks-loaded, native-listening e host-listening-ack. STATEepoch1/state0, nativeStatus9, tx/rx0, heartbeats ativos. Painel Aguardando conexão é compatível com ausência do outro transporte.
- Motorola: novo relay-ticket recebido23:36:58.938 e Activity solicitada23:36:59.059, mas nenhum novo native-hooks-loaded/WSS nessa captura. O processo nativo antigo era reutilizado.

**Não misturar isso com o primeiro congelamento.** Na nova tentativa há solicitação HTTP do convidado; falta evidência de avanço da nova instância nativa. O retorno do servidor confirma, para a tentativa anterior iniciada às 23:32:26.495, ticket do anfitrião aceito, mas ausência de host-listening/anexo v2 até 23:33:29. A tentativa posterior de 23:36:57–59 foi capturada no Android depois desse intervalo; ainda requer correlação do servidor para identificar os anexos dessa nova geração. Não supor alteração do operador: o retorno declara não ter reiniciado ou alterado a produção durante o diagnóstico.

## E — Achados nativos para reprodução controlada

1. `platform_unix.c:265–283`: destruição aguarda sthread_join segurando mutex; a saída do thread também usa esse mutex. Java finish não fornece comando explícito de saída nativa antes de super.finish. APP_CMD_DESTROY tem consumidor, mas não foi encontrado emissor no runtime examinado. É risco concreto de lifecycle/reabertura; sem stack atual não atribuir a tela preta a um ponto exato de bloqueio.
2. `station_recovery.h:15–20`: configure não reinicializa epoch/failed/confirmed estáticos. Reutilizar processo exige tratar estado entre sessões; condição testável, não diagnóstico único da queda.
3. `platform_unix.c:288`: chamada síncrona de shell para /sdcard/switch está presente no ELF realmente compilado. Não foi executado nem examinado o arquivo do telefone por esta análise. O hook fica em onStart, depois do ponto do log JNI, e não explica sozinho a ausência desse log em nova onCreate. Revisar separadamente.

## F — Limites e próximos passos

- debuggerd recusou leitura de pilha por exigir root; nenhuma elevação no aparelho foi feita. Não alterar a segurança para obter o diagnóstico.
- Últimos ANRs do sistema são20:06, anteriores à R73/tentativa atual. Não usá-los como prova desta reabertura.
- Novo handoff lido e cruzado. A liberação R73 está confirmada; o defeito de ciclo de vida HTTP no app precisa ser corrigido. A reinicialização nativa permanece uma investigação separada, sem stack que identifique o ponto exato. Nenhum código executável foi alterado nesta análise.
- Prioridade de solução a avaliar: manter a autoridade HTTP em componente com ciclo de vida reconhecido pelo Android durante a partida; depois conferir encerramento/reabertura nativa sem reaproveitar estado inválido. Preservar pausa, reconexão, identidade, licença, assinatura, saves e controles.
- Não remover indiscriminadamente prazos/validações do servidor para ocultar o congelamento local; não declarar partida recuperada apenas por PONG/estadoOnline.
