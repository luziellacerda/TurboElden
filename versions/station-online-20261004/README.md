# TurboStations — candidato R7, vídeo e salas online, 04/10/2026

## Atualização: instalado e tela das salas conferida

R7 foi instalado por atualização em 04/10/2026, SHA256 do APK no aparelho conferido. Botão nativo **Jogar online** abriu StationRoomsActivity; apelido, jogadores, salas e chat apareceram. **Voltar** retornou ao catálogo sem login. Ajuste temporário de tela restaurado para 0, XML de inspeção removido. Evidências: `evidence/r7-installed.json` e `evidence/r7-rooms-runtime.json`.

A chamada real do telefone recebeu **404**, correlação `060358fe191f4bd0af58b6ada9d45d75`. As duas rotas públicas também responderam404 sem autenticação. O operador do servidor aplicará o handoff do Git, conforme resposta do mantenedor. **Criar sala, convites, entrega de chat e partida ainda não foram verificados no serviço vivo.** Não chamar o candidato de estável.

A observação das plataformas confirmou que as células ainda ficam azuis; o candidato R5/R7 não deve ser descrito como correção visual comprovada. As capas dos jogos e o botão novo apareceram na lista SNES. A contagem de instalados apareceu0 nessa lista; não foi auditada a origem nesta conferência e nenhum jogo foi apagado.

## Estado registrado na compilação (anterior à instalação)

APK: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Online-Candidato-R7-20261004.apk`.
SHA256: `827723436ac618d3b1745a873813c7781ff10e043abc6033de416c01d774703d`.
Tamanho: **1.982.721.652 bytes**. Certificado preservado: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
Pacote `org.turboramastation.frontend`. ClientVersion de transporte ainda `1.0.8-station-covers-20261003.5`; não identifica sozinho este APK. Usar SHA256 e recibo.

**Compilado, assinado, alinhado 16 KiB e conferido no PC. Não instalado, não estável.** USB ausente na última consulta; R4 continua sendo o último instalado conhecido. Servidor online novo não foi publicado em produção. Nenhuma partida entre dois aparelhos foi demonstrada. Não converter compilação em alegação de compatibilidade ou desempenho.

Fontes, temporários e motores: `E:\ESTUDO APK\work\station-netplay-20261004` (junction `E:\StationNetplayWork`). Código público: `versions/station-online-20261004`. Base R5 arquivada em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`; R6 anterior arquivado e superado. Não instalar R6. Tag estável `estavel-station-snes-megadrive-20261003` preservada.

## Pedidos atendidos no candidato

| Pedido | Implementação | Limite real |
|---|---|---|
| Retirar espera ao navegar nos vídeos | R5 incorporado: removida espera fixa de 80 ms; 44 primeiros quadros reais; prévias preservadas ao abrir listas/menus; cache de 8 texturas RGB565 (8.294.400 bytes) | Latência física de disco/decoder permanece; medir Android. O problema visual azul observado em R4 ainda precisa ser reconferido no aparelho |
| Vídeo central em loop normal | MP4 e controle Java anteriores preservados, 720p, 1×, foco a 30 FPS; não reativadas nave/estrelas | Prévias laterais são quadros dos próprios vídeos; não são novas fotos |
| SNES roxo | SNES e SNESBR `A855F7FF`, núcleo `F3E8FFFF` | Conferir visual no aparelho |
| Botão Jogar online | Sexta ação nativa, ID real do jogo selecionado → JNI → sala | Toque implementado; navegação do botão novo por controle físico ainda não validada |
| Lista de online, convites, salas e chat | Novas telas + presença nas plataformas; API autenticada e assinada, chat por sala, bloqueio temporário de contato, paginação | Exige habilitação do código novo no servidor; não há chat global, mensagens persistentes ou moderação administrativa nova |
| Partida direta | RetroArch 1.22.2 em `:station_netplay`, sem anúncio/relay público; host abre socket antes de liberar convidado | CGNAT/NAT podem impedir conexão direta. Dois aparelhos, sincronismo e ROMs ainda precisam de homologação |
| SNES e Mega online com alternativas comerciais | bsnes-mercury Performance GPLv3 e ClownMDEmu AGPLv3 compilados e integrados com controles oficiais distintos | Não substituem os motores locais; condições de distribuição de código/licença continuam aplicáveis |
| Neo Geo/arcades | Geolith BSD compilado e incluído, mas recusado antes de criar sala | Exige `.neo` e BIOS. ZIPs do catálogo não são presumidos compatíveis. CPS/MAME/FBNeo e demais arcades não foram integrados ao transporte novo |
| Sinopses/capas/efeito do tema | R4 preservado: 1.804/1.816 sinopses conciliadas, correção Mega/BR, shader do tema, fotos SNES/Mega, 4 capas simultâneas sem pausa após sucesso e cache persistente | 12 sinopses sem fonte única; não inventadas. Não há foto de todo console ou metadados de jogos ainda ausentes do catálogo |

## Fluxo de código

1. `native/native_netplay.h`: ação direta da célula selecionada, ID em item de stride `0xe8`; não injeta cliques. `native_skin.h` distribui seis áreas mantendo as cinco ações originais.
2. `StationNetplayActivity.launchGame` passa o ID para `StationRoomsActivity`. Interfaces próprias PSP/Dolphin/Flycast são preservadas; a sala nova ainda não as lança automaticamente.
3. `StationOnlineClient` usa `StationAndroid`/`StationSessions.Lease`/`StationApi.online`. Exatamente duas rotas novas são permitidas. Assinatura RSA-PSS, sessão/aparelho/produto/requestId e tamanho são verificados antes de usar a resposta.
4. `StationOnlineGame` resolve recibo real da instalação pelo itemId, confere arquivo, SHA256 de ROM, motor, runtime e opções. Não busca pastas arbitrárias nem aceita URL de ROM na sala.
5. `StationRetroLaunch` escreve configuração privada e handoff de uso único/60 s. Copia overlays oficiais distintos SNES/Mega; mantém saves online por sala separados dos saves locais.
6. `StationRetroActivity` carrega o runtime nativo no processo dedicado. O guard mínimo em `YuzuApplication` evita inicializar outros motores nesse processo. Não abre outra sessão Station.
7. `StationGameSession`, no processo principal, recebe eventos privados de ciclo de vida via `ResultReceiver`/Binder e mantém a sessão autenticada existente. Ao esconder, cancela timers/requisições; ao sair, encerra a sala. Morte do processo principal causa expiração da presença, não cria uma segunda autoridade de sessão.
8. Após `listen()` bem-sucedido no RetroArch, callback JNI → Binder → `host-listening`. O servidor muda `starting` para `connecting`; só então o convidado abre o motor. `connecting` não significa jogo sincronizado. Sem confirmação do host, encerra `starting` após 30 s.
9. Ao voltar, a sala anterior é encerrada antes de reentrar, evitando reabrir o jogo automaticamente. A configuração com senha da sala é apagada na saída normal.

## Fontes oficiais e licenças

Pins completos em `evidence/upstream-pins.json`; submódulos do Clown em `evidence/clown-submodules.json`.

- RetroArch: `69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576`, GPLv3.
- bsnes-mercury: `79d7f9de218b6ffa65a80bbdc5828532bc239232`, GPLv3.
- ClownMDEmu: `d43c2708b0a31c285ce16724b6c4a2e92af07346`, AGPLv3.
- Geolith: `194024931935eff2092e36fc4f8e53e62ed11097`, BSD-3-Clause.
- Controles: libretro/common-overlays `42c21b99889468a8e77fd7f002229ec16e2f9fa2`, CC-BY-4.0, arquivos e atribuição incluídos.

Referências: [Netplay](https://docs.libretro.com/guides/netplay-getting-started/), [protocolo](https://docs.libretro.com/development/retroarch/netplay/), [bsnes-mercury](https://docs.libretro.com/library/bsnes_mercury_performance/), [ClownMDEmu](https://docs.libretro.com/library/clownmdemu/), [Geolith](https://docs.libretro.com/library/geolith/).

Não foram acrescentados ROMs ou BIOS. As alternativas novas não certificam as licenças dos motores locais anteriormente incluídos. Antes de distribuir comercialmente, resolver os componentes anteriores com restrições comerciais e cumprir as licenças de todos os novos componentes.

## Evidências e riscos restantes

- **591** verificações Java da integração Station, incluindo 27 de resposta online; **39** domínio .NET; **37** HTTP real em Kestrel local com identidade sintética.
- **231** regras de fonte/recursos/layout e **6** checks executáveis de revisão/reinício; **109** verificações R5 e shader/pixel real em ANGLE/Windows.
- Quatro ELF AArch64 e exports necessários conferidos; LOADs com alinhamento mínimo 16 KiB. Compilação RetroArch em NDK r28c tem avisos upstream registrados, não foi declarada livre de avisos.
- APK: cinco entradas existentes alteradas, **11.045 preservadas**, novas entradas listadas no recibo, sem classes DEX duplicadas; ZIP completo conferido por hash.
- Base APK privada e chave local não são publicadas. O packager usa certificado de teste preservado, não certificação de publicação em loja.
- Não comprovado: execução destes quatro ELF no Android, determinismo entre pares, jitter/reconexão real, efeito térmico, controles/UX da sala em todos os tamanhos, carregamento instantâneo de vídeo ou API nova em produção.

## Próxima execução correta

1. Operador do servidor lê **HANDOFF-APP-PARA-SERVIDOR-ONLINE-20261004.md**, confere serviço/artefato real e homologa a nova branch com flag desligada. Não substituir endpoints de login/capas/downloads.
2. Implantação exige alvo/artefato/retorno concretos e autorização; o trabalho atual não reiniciou serviços nem alterou Linux/DB.
3. Com USB disponível e aplicativo nas plataformas, atualizar por `adb install --no-incremental -r --user 0` no APK exato. Nunca desinstalar ou limpar dados.
4. Conferir plataformas/vídeo para ambos os lados, listas/retorno, capas e download local, SNES/Mega/controles/HUD/saves sem regressão. O aviso de serviço online desligado é esperado antes da implantação.
5. Homologar duas licenças/aparelhos: mesmo arquivo/motor/opções, convites, chat, pronto, host listen, conexão, controles, saída, perda de rede e retorno autenticado; testar Wi-Fi e conexão externa alcançável separadamente.
6. Só após evidência real considerar estabilidade. Não mover a tag de recuperação atual nem descrever Neo Geo/CPS como prontos.
