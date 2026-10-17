# Auditoria separada: saída do anfitrião N64

Esta análise não faz parte do APK R162 de vídeo. O relato físico foi: o anfitrião saiu e outro aparelho permaneceu na tela preta sem aviso. A captura R161 salva antes da saída não prova se o pedido `leave` chegou ao servidor; nenhum log posterior dos dois aparelhos foi incluído nela.

## Caminho atual

1. A saída humana no N64 envia evento 4 ao processo principal (`StationN64Bridge.Session.humanExit`). O processo principal fecha o dono da sessão e cria uma tarefa avulsa que chama `StationHumanDeparture.leave` uma vez (`StationGameSession.event(4)`). Se a chamada falha, só grava `game stage=human-leave-unconfirmed`; não há nova tentativa nem heartbeat desse anfitrião.
2. Se o servidor aceita `leave`, `StationMultiplayer.Leave` retira a sala e chama `RetireRoom`. `StationMultiplayerStream.End` marca estado irrecuperável, desperta os escritores e imediatamente cancela o token de todos os sockets. Como o escritor usa esse mesmo token, o frame terminal `STATE=3` pode nunca sair. O convidado trata o fechamento do WSS como perda temporária e exibe espera genérica (`StationMultiplayerTunnel.lost`).
3. O processo principal do convidado consulta a autoridade a cada 20 segundos (`StationGameSession.sync`). Quando não vê mais a sala, envia evento terminal 102 e encerra a sessão. O N64 transforma isso em `fatal("N64_AUTHORITY")`, que mostra um aviso genérico apenas se a Activity estiver visível. Não há motivo específico “o anfitrião saiu”.
4. Se o `leave` do anfitrião **não** chega ao servidor, a desconexão do socket só pausa o stream. O heartbeat do convidado mantém sua própria presença e pode continuar vendo a sala em `waiting-reconnect` sem prazo de encerramento baseado na ausência do anfitrião. O código proíbe corretamente converter uma perda de rede isolada em saída humana, mas precisa de uma forma confiável de concluir a saída explicitamente solicitada.

## Correção delimitada, após estabilizar o vídeo

- **Servidor:** quando `RetireRoom` decorre de um `leave` confirmado, dar ao escritor único uma janela curta e limitada para transmitir `STATE=3` antes de cancelar os sockets. Testar que o convidado recebe o estado terminal em vez de apenas `onClose`, e que conexões lentas ainda são fechadas no prazo. Isso melhora o aviso imediato sem mudar a política de recuperação para perda de rede.
- **Aplicativo:** no evento 4, conservar o mesmo `requestId` para uma repetição limitada do `leave` quando o transporte falhar; o servidor já possui recibos idempotentes por `requestId`. Depois de resposta incerta, consultar a própria sala e continuar apenas se a identidade/generation corresponder, sem sair de uma sala nova. Registrar confirmação ou falha final para diagnóstico. Considerar uma mensagem explícita de anfitrião ausente somente após evidência autoritativa de sala encerrada.
- **Prova física:** capturar do convidado o `event=socket-close`, `event=state`, o resultado do heartbeat e o aviso na tela por pelo menos 25 segundos após a saída, e do anfitrião o registro `human-leave-unconfirmed` ou a confirmação do servidor. Não publicar IDs de sala, tokens nem registros brutos.

Um ajuste exclusivo no servidor pode fazer o cliente atual mostrar seu aviso **genérico** rapidamente quando o `leave` foi confirmado. A confiabilidade da entrega de `leave` e uma mensagem específica de saída exigem também alteração do aplicativo. Não misturar estas mudanças no candidato R162 de vídeo.
