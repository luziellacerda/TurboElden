# Delta Java R74 — serviço vinculado e saída nativa

Base imutável: E:\ESTUDO APK\work\station-recovery-handshake-r73-20261007-build\java.
Aplicar somente os seis .java de netplay-src por caminho relativo; não empacotar tests/fixture-src.
Base198 fontes +3 classes novas =201 fontes de produção; três fontes substituídas.

## Manifest
Adicionar MANIFEST-SERVICE.xml como filho de application. Sem android:process; o serviço roda no processo principal, junto à autoridade HTTP. Exported=false. Não é serviço iniciado/foreground, sem START_STICKY, wake lock ou alteração de configurações globais.

## Fluxo
Rooms cria StationGameSession e registra UUID privado + roomId exato + generation. A registry admite somente um lançamento registrado, rejeitando outro antes da NativeActivity. A guarda de exclusividade nativa complementar, entregue separadamente, protege o período entre fechamento do owner e conclusão do motor anterior.
O Rooms lança o motor por startActivityForResult, sem NEW_TASK nem alteração de launchMode (ambas Activities standard no AXML). LaunchReturn aninhado em GameSession guarda requestCode crescente, nonce, room e generation em Bundle. onActivityResult conclui somente a identidade correspondente e faz cleanup local, mesmo se o filho morrer antes do ATTACH; RESULT_CANCELED não é interpretado como Leave ou falha remota. Callback antigo não limpa nova sessão. Não há timeout nem consulta de PID.
StationRetroActivity prepara o socket local como antes, mas não inicia os trabalhadores WSS/HTTP até receber ACK do serviço. O bind explícito usa BIND_AUTO_CREATE|BIND_IMPORTANT. Messenger real transporta IPC entre :station_netplay e o processo principal. Serviço e cliente conferem sendingUid; serviço resolve a identidade exata no registry, restringe a um Binder por sessão e registra DeathRecipient.
OnStop preserva o vínculo: mantém o owner elegível enquanto o processo da partida existe, sem reativar carrossel, vídeo ou tela. O v2 preserva pausa/retomada; não se adicionou Leave em background. OnDestroy libera vínculo. Perda definitiva/DETACH limpa somente estado local, não fabrica recovery-failed. Eventos explícitos humanos4/terminais6 continuam válidos depois da limpeza local, com idempotência e testes de ambas as ordens de entrega. OnServiceDisconnected conserva vínculo para reconexão Android; onBindingDied libera e refaz vínculo; onNullBinding libera e mostra indisponibilidade. Callbacks tardios não religam partida fechada.
Cada evento5 de resume-relay é coalescido enquanto o primeiro está pendente. Mantém o mesmo worker e contrato de identidade, sem aumentar concorrência HTTP nem alterar tickets/auth/rotas.

## Contrato JNI exigido
public native boolean stationRequestQuit(); instância, UI thread, somente confirmação humana.
closeSession envia evento4 antes da chamada JNI. Retorno true aguarda término normal nativo; false finaliza Activity sem timeout/kill. Implementação nativa é fornecida pelo agente responsável; não incluída neste delta Java. Callbacks/controles, saída por Voltar e Dialog R73 preservados.
Nenhum novo critério de SYNC/pacing foi introduzido em Java; StationRecoveryTunnel permanece idêntico à base.

## Testes executados
API34 + Java8 em memória: 201 fontes /325 classes, sucesso.
Fixtures JVM usam Service, Link, Registry e GameSession REAIS com Android/Binder/HTTP falsos:101 checks (22 registry+79 lifecycle).
42 guardas de fonte. Recibo tests/test-receipt.json contém hashes completos das seis fontes e respectivas bases. tests/delta-r73-r74.diff registra alterações. Reprodução: Python tests/run_session_tests.py.
Casos: identidade/UID inválido, dono exclusivo, ACK tardio, close antes de bind, bindfalse/exceção, nullbinding, bindingdied, desconexão/reconexão, morteBinder antes/depois do ACK, ordens DETACH→4/4→DETACH/DETACH→6/6→4, saída idempotente, 20 pedidos de ticket durante um grant pendente (somente uma chamada), falha parcial no attach e rejeição de segundo lançamento; crash pré-ATTACH, callback antigo após novo launch, restauração de Bundle e resultado normal depois dos eventos4/6.

## Limites
Sem APK assinado/gerado/instalado, sem telefone, HTTP real, freezer Android ou gameplay de dois aparelhos neste trabalho. O vínculo de importância precisa ser conferido no dumpsys em aparelho durante partida, junto à continuidade de heartbeat e saída/reabertura. A retenção do serviço não promete manter app arbitrariamente executável com Android inteiro em background; v2 continua responsável por pausar/retomar.

## Documentação oficial consultada
https://developer.android.com/develop/background-work/services/bound-services
https://developer.android.com/reference/android/content/Context#BIND_IMPORTANT
https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/master/core/java/android/app/Activity.java (startActivityForResult:5588–5591; onActivityResult:7121–7135 documenta cancelamento em crash e entrega antes de onResume).

## Arquivos
StationSessionRegistry.java, StationSessionService.java e StationSessionLink.java: novos.
StationGameSession.java, StationRetroActivity.java e StationRoomsActivity.java: deltas sobre R73.
