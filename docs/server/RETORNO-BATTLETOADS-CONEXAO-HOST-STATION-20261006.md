# Battletoads: sala aceita, conexão do anfitrião pendente — 06/10/2026

## Evidência nova de produção

A tentativa observada às18h02min53s de Maceió (`2026-10-06T21:02:53Z`) é **SNES / Battletoads in Battlemaniacs (USA)**. Os dois membros estavam na mesma sala, ambos Pronto. `start` retornou200, geração3, transporte `relay-wss-v1`; o anfitrião recebeu `relay-ticket`200. Uma conexão WSS foi aberta e terminou após60.001,8673ms. Não foi observado `host-listening`; não houve incremento nos bytes encaminhados pelo relay durante a tentativa. O convidado recebeu estado `starting` e continuou no lobby.

Isso localiza a falha entre abertura do motor Android e confirmação de prontidão do anfitrião. Não comprova se o socket nativo não abriu, se o callback JNI não chegou ou se o Binder/processo principal falhou. O servidor não recusou o segundo membro nem o início. **Gameplay em dupla continua sem validação.**

API permanece `a2bb176530fd4d2dfa740da7e934fd84d097404e`, DLL `d181bf97d5b39a334e95144267d6ece3f11d4e659a314d7d16cd2746e1999e13`, PID875574. Não forçar `connecting`, não abrir convidado prematuramente, não mudar autenticação nem allowlist por inferência.

## Captura solicitada ao operador do APK

O usuário informou Samsung da loja e confirmou que conectará por USB **o telefone que abre o jogo** ao PC de produção. Não atribuir os papéis ao modelo ou à licença por suposição. Esta máquina Linux não tem esse Android conectado por ADB.

1. Conferir `adb devices -l` e escolher explicitamente o serial. Registrar modelo, versãoAndroid, pacote instalado e versão do APK. O recibo anterior R41 comprova apenas Samsung SM_A566E/hash`b6b19321ec529945870dc919c3de5f0eba75aa54330d3672227b8e632302b28d` naquela instalação; não prova a versão dos dois telefones agora.
2. **Capturar antes de instalar ou encerrar o jogo**: Activity em primeiro plano e logs `StationRooms`, `RetroArch`, `AndroidRuntime`, no diretório privado `device-evidence`, fora do Git. Não limpar dados/logs, regenerar códigos ou abrir outra sessão pelo processo nativo.
3. Reproduzir uma vez com dois membros Pronto e anfitrião Iniciar. Procurar as fases `launch stage=activity`, `game stage=native-listening`, `game stage=host-listening-ack`, `session-sync`, erros `[Netplay]` e morte do processo principal. Conferir se a Activity é `StationRetroActivity` no processo `:station_netplay`, biblioteca `station_retroarch`, papelhost e porta55435. Os extras/config podem conter segredos: não publicar dumps integrais.
4. Se `native-listening` está ausente, verificar o erro nativo e se o runtime carregado tem os patches de papelhost/client e listener. Se o sinal chega, investigar entrega por ResultReceiver/Binder e a chamada autenticada `host-listening`. Registrar apenas fase/classe/código e resultados, sem sala, apelido, ticket, bearer, senha ou código de acesso.
5. Preservar licença, saves, assinatura, todos motores e fonte congeladaR41. Atualizações são APKsucessor sobre R41, sem desinstalar/limpar. Não aplicar R34 antigo sobre R41.

## Correção em preparação

O túnel atual aguarda exclusivamente o callbackJNI por60s antes de conectar ao TCP local. Está sendo preparado um delta que mantém como fluxo de jogo a primeira conexão TCP real bem-sucedida emloopback; sinaliza a prontidão somente após TCP conectado e WSS aberto. O callback nativo passa a acelerar a espera. O convidado continua aguardando a confirmação autenticada no servidor.

**Neste recibo inicial o delta ainda está em testes e não está compilado/instalado no telefone.** A causa específica do motor e a captura USB permanecem pendentes. Não marcar a partida corrigida. A publicação seguinte anexará fontes, testes e receita concreta do candidato.
