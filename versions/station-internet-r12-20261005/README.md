> Atualização: R12 instalado por atualização após reconexão USB; SHA256 integral no telefone confirmado. Servidor ainda sem deploy e partida entre dois aparelhos não verificada. Retorno remoto c8e240a (Neo Geo offline/taxa MB/s) conciliado no Git; seu delta de taxa ainda não integra este APK. Na próxima montagem, preservar classes35 R12; não voltar ao DEX R11.

> Atualização: R12 instalado por atualização após reconexão USB; hash integral no telefone confirmado. Tela estava apagada/bloqueada e foi solicitado desbloqueio. Servidor ainda sem deploy e partida entre dois aparelhos não verificada. Retorno remoto c8e240a (Neo Geo offline/taxa MB/s) conciliado no Git; seu delta de taxa ainda não integra este APK. Na próxima montagem, preservar classes35 R12; não voltar ao DEX R11.

# APP â†’ SERVIDOR â€” Netplay pela internet no mesmo Station â€” R12, 05/10/2026

DestinatÃ¡rio: operador do **Servidor-pix**. Este Ã© cÃ³digo e pedido de publicaÃ§Ã£o do APP, nÃ£o retorno do servidor nem prova de produÃ§Ã£o. Pedido vigente do mantenedor: jogadores em redes distintas, usando o mesmo servidor que jÃ¡ atende a Station. Substitui a restriÃ§Ã£o anterior de conexÃ£o direta. NÃ£o usar lobby, relay ou conta pÃºblicos do RetroArch.

## Estado e autoridade

- App parte de R11 / TurboElden `6ef86c4cfd8302c0673c784856f25cf673d261ca`; preserva coleÃ§Ãµes, nomes, sinopses, catÃ¡logo, capas e emuladores locais.
- Servidor parte exatamente de `4e623bcbeaed3ee03d8a1767f66319e67659463d`, branch `feat/station-online-direct-20261004`. Preserva `StationLibraryMonitor` e consulta ao catÃ¡logo vigente; nÃ£o substituir por fonte anterior sem monitor.
- APK novo: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Netplay-Internet-R12-20261005.apk`. Hash, tamanho, certificado e comparaÃ§Ã£o integral em `evidence/build-result.json` no app.
- Fonte/build canÃ´nicos: `E:\ESTUDO APK\work\station-netplay-20261004\internet-r12`. App Java tambÃ©m promovido para `netplay\src`, com backup anterior em `internet-r12\before-netplay-src`. Novas dependÃªncias estÃ£o em `internet-r12\dependency-src`.
- Servidor completo compilado isoladamente em `internet-r12\server-full`. Nenhuma alteraÃ§Ã£o foi implantada em Linux. Checkout do clone do servidor preservado; a nova branch contÃ©m quatro arquivos de produÃ§Ã£o e documentaÃ§Ã£o/testes aditivos.
- R9 Ã© o Ãºltimo instalado comprovado. O aparelho voltou Ã  USB nas plataformas (84% de bateria, ~12 GiB livres), mas desconectou durante a instalaÃ§Ã£o R12; ADB devolveu falha e a conferÃªncia seguinte nÃ£o encontrou dispositivo. Estado do pacote apÃ³s a tentativa e hash no aparelho ainda precisam ser conferidos. NÃ£o foi alterada a configuraÃ§Ã£o de tela. R10/R11/R12 nÃ£o foram validados em Android nesta rodada. R11 foi arquivado em G: com SHA256 integral antes de remover a cÃ³pia idÃªntica de E:. Tag estÃ¡vel preservada.

## Desenho implementado

Dois celulares iniciam conexÃµes **WSS na porta HTTPS do mesmo domÃ­nio Station**, usando o mesmo certificado/pin do app. O servidor associa somente dois integrantes da mesma sala. O fluxo TCP do RetroArch passa por essas conexÃµes em ordem. NÃ£o hÃ¡ IP pÃºblico do jogador, encaminhamento de porta no roteador, descoberta LAN obrigatÃ³ria, UPnP ou retransmissor pÃºblico.

Isso permite atravessar redes com NAT/CGNAT quando ambas permitem saÃ­da WSS para o domÃ­nio Station. NÃ£o promete acesso em rede que bloqueia esse domÃ­nio/WebSocket, nem ausÃªncia de latÃªncia, compatibilidade de todos os motores, ou continuaÃ§Ã£o transparente ao trocar Wi-Fi por dados mÃ³veis. Troca/perda de conexÃ£o encerra a partida; criar uma nova sala para reconectar. ReinÃ­cio do servidor tambÃ©m encerra salas, pois o estado continua em memÃ³ria.

## Contrato exato e sequÃªncia

As rotas existentes `/v1/station/online/command` e `/v1/station/online/events` continuam autenticadas por Bearer, assinadas RSA-PSS, vinculadas Ã  sessÃ£o/aparelho/licenÃ§a/requestId. As verificaÃ§Ãµes existentes de nÃºcleo/runtime/conteÃºdo/opÃ§Ãµes permanecem obrigatÃ³rias.

1. `snapshot.transports` acrescenta `relay-wss-v1` somente quando a configuraÃ§Ã£o permite. Flag ausente/desligada publica apenas `direct`. App novo informa atualizaÃ§Ã£o pendente quando nÃ£o hÃ¡ relay; nÃ£o pede IP nem anuncia sucesso fictÃ­cio.
2. Criar/entrar/confirmar presenÃ§a seguem os comandos atuais. Ambos precisam da mesma ROM instalada, nÃºcleo, runtime e opÃ§Ãµes aceitos pelo registro.
3. Host envia `start` com `roomId` e `transport: "relay-wss-v1"`. EndereÃ§o/porta do telefone nÃ£o sÃ£o solicitados. O servidor valida dois integrantes prontos, passa a `starting` e incrementa generation.
4. Host envia `relay-ticket` com `roomId`. A resposta assinada contÃ©m `snapshot.room.relay = {path:"/v1/station/online/relay",protocol:"station-relay.v1",ticket:...,expiresInSeconds:...}`. Token aleatÃ³rio de 32 bytes, base64url sem padding (43 caracteres), 60 s e uso Ãºnico, reservado ao prÃ³prio integrante. NÃ£o aparece para o colega ou visitante. Refazer o comando com novo requestId antes do uso substitui o ticket anterior.
5. Host prepara o runtime nativo. Seu bridge inicia WSS e aguarda callback real `onNetplayListening`. Depois conecta TCP local `127.0.0.1:55435`. O sinal `host-listening` segue via Binder para o processo principal autenticado.
6. Servidor passa a `connecting`, **sem incrementar generation no modo relay**, preservando o ticket do host. Convidado solicita seu prÃ³prio ticket e abre runtime. O bridge convidado aceita conexÃ£o nativa em porta local efÃªmera e encaminha os bytes por WSS.
7. Rota nova `GET /v1/station/online/relay`, upgrade WebSocket, subprotocolo `station-relay.v1`, header `Authorization: StationRelay <ticket>`. Sem query string. NÃ£o recebe URL, host ou porta de destino do usuÃ¡rio. Consome ticket antes de aceitar e associa sala, geraÃ§Ã£o, participante e papel. SÃ³ aceita mensagens binÃ¡rias.
8. A partida usa o protocolo TCP original RetroArch, senha aleatÃ³ria original da sala e validaÃ§Ãµes do motor. Servidor nÃ£o interpreta comandos da ROM nem executa emulaÃ§Ã£o. `connecting` continua significando conexÃ£o em preparaÃ§Ã£o; nÃ£o Ã© prova de sincronismo/gameplay.
9. `StationGameSession` conserva heartbeat autenticado a cada 20 s enquanto o jogo estÃ¡ visÃ­vel, usando a sessÃ£o do processo principal. `onStop` fecha o tÃºnel; `onDestroy` encerra a participaÃ§Ã£o. Falha/saÃ­da de um lado aborta os dois sockets e remove a sala. NÃ£o existe conexÃ£o silenciosa infinita no fundo.

## Arquivos e funÃ§Ãµes

| Arquivo | Responsabilidade |
|---|---|
| StationRoomsActivity.java | Descobre transportes, confirma jogo pela internet, start e solicitaÃ§Ã£o do ticket; mantÃ©m visual/salas/chat existentes |
| StationRetroLaunch.java | Valida descritor assinado, prepara arquivo privado de lanÃ§amento de uso Ãºnico, overlays e configuraÃ§Ã£o nativa |
| StationRetroActivity.java | Cria/fecha bridge; repassa porta local ao runtime antes de iniciar; callback real do host e avisos de conexÃ£o |
| StationRelayTunnel.java | WebSocket upstream, TCP local, preservaÃ§Ã£o da ordem, backpressure, fechamento e limites; sem APIs Android na implementaÃ§Ã£o do fluxo |
| StationRelayTls.java | Mesmo BASE_URL HTTPS â†’ WSS; trust store do Android, hostname e SPKI SHA256 existentes; sem trust-all |
| StationOnlineClient.java | Mensagens dos novos erros do servidor |
| StationOnline.cs | Flag, transportes, tickets, vÃ­nculo Ã  sala/geraÃ§Ã£o, consumo Ãºnico, heartbeat e revogaÃ§Ã£o |
| StationRelay.cs | Pareamento exclusivamente de dois membros; cÃ³pia binÃ¡ria com buffers limitados e encerramento conjunto |
| StationOnlineEndpoints.cs | Upgrade autenticado por ticket, subprotocolo, rejeiÃ§Ãµes, duraÃ§Ã£o do request e liberaÃ§Ã£o da sala |
| StationOnlineRegistration.cs | DI/flag; preserva catÃ¡logo atualizado pelo monitor e autenticaÃ§Ã£o existentes |

NÃ£o modificar manifesto, assinatura, base da API, pin, chave de assinatura de respostas, IDs de jogos, banco ou catÃ¡logo para ativar relay. NÃ£o trocar os motores locais SNES/Mega. O registro online existente deve continuar com os hashes exatos atuais: nenhum nÃºcleo/runtime nativo mudou neste APK.

## Limites e seguranÃ§a operacionais

- AtÃ© 128 pares simultÃ¢neos nesta implementaÃ§Ã£o, dois sockets por sala; capacidade real depende de CPU/rede/proxy e precisa de teste de carga do operador.
- Buffer servidor de 32 KiB por direÃ§Ã£o, escrita aguardada; sem fila ilimitada. Limite de 8 MiB/s por direÃ§Ã£o por sala com backpressure, sem descartar bytes nem derrubar a conexÃ£o por uma rajada de estado inicial.
- Fila cliente limitada por backpressure em torno de 256 KiB mais um bloco; leitura local de 16 KiB; WebSocket com limite de mensagem 64 KiB e payload esperado atÃ© 32 KiB.
- Pareamento aguarda no mÃ¡ximo 60 s. `starting` relay no hub expira em 90 s; conexÃ£o ao upstream/endpoint local tem limites prÃ³prios. Ping cliente 20 s e keepalive servidor 20 s.
- Watch de vÃ­nculo Ã  sala a cada 2 s. RevogaÃ§Ã£o explÃ­cita no hub interrompe no prÃ³ximo watch. RevogaÃ§Ã£o na base impede novos comandos/heartbeats vÃ¡lidos; presenÃ§a expira em atÃ© 60 s desde o Ãºltimo heartbeat vÃ¡lido, mais o watch. NÃ£o alegar bloqueio instantÃ¢neo de um socket jÃ¡ aberto por alteraÃ§Ã£o isolada no banco.
- Token nÃ£o vai na URL nem nos logs. Configurar proxy para nÃ£o registrar Authorization ou corpo da resposta assinada. NÃ£o publicar arquivos de fixture com tokens, certificados privados, sessÃµes ou cÃ³digos reais.
- Continua uma Ãºnica instÃ¢ncia autoritativa das salas. MÃºltiplos workers/rÃ©plicas sem afinidade/estado compartilhado nÃ£o sÃ£o suportados; nÃ£o ativar escalonamento horizontal aleatÃ³rio.
- Transporte WSS tem TLS atÃ© o servidor. NÃ£o afirmar criptografia ponta a ponta entre os telefones; o relay vÃª os bytes transitÃ³rios, nÃ£o os grava.

## PublicaÃ§Ã£o pelo operador, no serviÃ§o jÃ¡ existente

1. Comparar a branch com o serviÃ§o realmente ativo e conciliar quatro arquivos com quaisquer mudanÃ§as posteriores a 4e623bc. NÃ£o trocar todo o servidor por este snapshot antigo. Confirmar chamadas existentes de AddStationOnline/MapStationOnline no Program e preservar monitor/biblioteca/serviÃ§os compartilhados.
2. Compilar/testar em ambiente isolado .NET 8. NÃ£o hÃ¡ migration, banco novo, credencial pÃºblica ou serviÃ§o adicional requerido. Manter registro de motores e configuraÃ§Ãµes atuais.
3. A configuraÃ§Ã£o nova Ã© `Station:Online:RelayEnabled` (variÃ¡vel de ambiente `Station__Online__RelayEnabled`). **PadrÃ£o false**. `Station:Online:Enabled` tambÃ©m precisa estar true. Publicar primeiro desativado e validar regressÃµes do serviÃ§o.
4. No mesmo domÃ­nio HTTPS do app e upstream atualmente usado pelas rotas Station, permitir upgrade WebSocket **somente** em `/v1/station/online/relay`; preservar Authorization e Sec-WebSocket-Protocol, HTTP/1.1 upstream, Upgrade/Connection adequados; nÃ£o cachear/bufferizar. Timeout inativo deve comportar keepalive de 20 s, por exemplo acima de 60 s. NÃ£o presumir caminho de arquivo nginx, nome de container/unidade ou endereÃ§o upstream: usar os efetivamente ativos documentados pelo operador.
5. Se existir Cloudflare na rota, habilitar WebSockets e conferir regras WAF sem retirar proteÃ§Ã£o das outras rotas. NÃ£o mudar DNS, pin/certificado ou expor uma porta do emulador na internet. O app usa o mesmo host/porta configurado no Station.
6. Habilitar RelayEnabled e reiniciar controladamente **o serviÃ§o correto** segundo o procedimento operacional vigente. Flag Ã© lida tambÃ©m na construÃ§Ã£o do hub: trocar somente o valor em arquivo sem recriar processo nÃ£o atualiza capacidades do hub.
7. Verificar via sessÃ£o de homologaÃ§Ã£o: transports, resposta assinada relay-ticket, upgrade101, binÃ¡rio nos dois sentidos, rejeiÃ§Ã£o de token expirado/reusado/integrante externo, saÃ­da, revogaÃ§Ã£o e zero pares apÃ³s encerrar. NÃ£o incluir segredos no retorno.
8. Instalar o APK por atualizaÃ§Ã£o preservando dados, licenÃ§a, saves e assinatura. Testar dois celulares com o mesmo jogo/nÃºcleo, um Wi-Fi e outro rede mÃ³vel; depois Wi-Fi de operadoras distintas. Confirmar interaÃ§Ã£o dos dois jogadores, tempo/Ã¡udio/sincronismo, controles e retorno Ã s salas/plataformas. NÃ£o basta ver sala/lista/101.
9. Rollback: desligar RelayEnabled e reiniciar o serviÃ§o (as partidas ativas encerram); app informa indisponibilidade, jogo local continua. NÃ£o remover catÃ¡logo, dados, licenÃ§as ou publicar a revisÃ£o como estÃ¡vel antes da homologaÃ§Ã£o.

## Provas locais entregues

100 verificaÃ§Ãµes: 39 regressÃµes de salas/chat/convites; 37 HTTP com assinatura RSA-PSS real e autenticaÃ§Ã£o sintÃ©tica; 17 integraÃ§Ã£o de rotas TLS/tickets/flags/limpeza/revogaÃ§Ã£o; 7 bridge Java real contra relay C# real. Transferidos 12.583.029 bytes em cada sentido e 50 comandos pequenos ordenados, conferidos byte a byte. Teste de pin incorreto rejeitado. Grande rajada nÃ£o encerra mais a sessÃ£o. Testes rodam em loopback com certificado confiado sÃ³ pela fixture e identidades artificiais, sem banco ou usuÃ¡rios de produÃ§Ã£o.

Android Java API34/Java8 e DEX mÃ­nimo26 compilados; servidor completo Release net8.0 compilado. ComparaÃ§Ã£o integral do APK em evidence. Isso nÃ£o comprova GPU/consumo Android, partida determinÃ­stica, latÃªncia externa, proxy vivo ou redes mÃ³veis.

Motores habilitados nesta linha: SNES bsnes-mercury Performance e Mega ClownMDEmu. Neo Geo permanece bloqueado por preparaÃ§Ã£o .neo/BIOS pendente; CPS/MAME/FBNeo e outros arcades nÃ£o se tornam compatÃ­veis por existir relay. Manter licenÃ§as/fontes correspondentes jÃ¡ documentadas. NÃ£o prometer todos os sistemas.

## DependÃªncias e reproduÃ§Ã£o

Java-WebSocket 1.6.0 e SLF4J API 2.0.13, licenÃ§as MIT incluÃ­das no APK. Fontes upstream e hashes estÃ£o em dependencies/sources.json. Os 124 fontes foram realocados para `org.emulationstation.frontend.relay.ws` e `.relay.log` para evitar colisÃµes com os emuladores integrados. Sem outra mudanÃ§a algorÃ­tmica upstream. Fontes realocados completos acompanham esta entrega, dispensando busca incerta de versÃµes.

No workspace canÃ´nico E:, `build_station_internet_app.py` compila os 141 fontes usando station-client.jar produzido pelo R10, SDK34, JDK17 e D8. `run_station_relay_tests.py` compila servidor e testes isolados; requer as fixtures prÃ©vias server/Program.cs e HttpTests.cs, tambÃ©m copiadas na entrega. `package_station_internet_r12.py` usa R11 exato, altera somente classes35.dex, inclui trÃªs arquivos de licenÃ§a/proveniÃªncia, alinha 16 KiB, assina com certificado original e compara todas as entradas. NÃ£o reaplicar scripts one-shot em artefato existente: revisar guardas e recibos; nÃ£o apagar o APK estÃ¡vel.

ReferÃªncias primÃ¡rias: [protocolo RetroArch](https://docs.libretro.com/development/retroarch/netplay/), [conectividade Netplay](https://docs.libretro.com/guides/netplay-getting-started/), [ASP.NET WebSockets](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/websockets?view=aspnetcore-8.0), [Cloudflare WebSockets](https://developers.cloudflare.com/network/websockets/), [Java-WebSocket](https://github.com/TooTallNate/Java-WebSocket).

## Retorno solicitado ao servidor

Publicar **RETORNO-SERVIDOR-NETPLAY-INTERNET-STATION-R12-20261005.md** respondendo: commit/DLL efetivos e hashes; flags; instÃ¢ncia/serviÃ§o/upstream/proxy efetivos (sem segredos); confirmaÃ§Ã£o de contratos/catÃ¡logo preservados; resultados dos testes HTTPS/WSS; capacidade/limites/telemetria; decisÃ£o de publicaÃ§Ã£o ou impedimento comprovado; prova de dois aparelhos/redes quando disponÃ­vel. Distinguir teste local, homologaÃ§Ã£o, produÃ§Ã£o e aparelho. NÃ£o chamar este prÃ³prio handoff de retorno nem preencher dados nÃ£o medidos.

## Artefato exato desta entrega

APK SHA256 `7684c6eee87985d8259becca9a22a9f4c7e3203f7c097df37da6998975596514`, 1.982.967.774 bytes. Somente `classes35.dex` alterado, trÃªs arquivos de licenÃ§a/proveniÃªncia adicionados e 11.102 entradas preservadas. Certificado original e alinhamento16KiB conferidos.
