# R132 — preparação inicial, sinopses Sony e caminho do Switch

**R132 compilada, assinada, conferida e instalada no Motorola; kit privado preparado. Ativação do servidor ainda pendente.** Fonte executável `56ba83b7fcc5c243ae50052fec9b6f4141e1b5f1`; APK SHA256 `47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20`, 2.711.825.423 bytes. A assinatura original v2/v3 e o alinhamento de 16 KiB foram conferidos. Os recibos públicos preservam os mapas completos de hashes e a proveniência dos originais privados.

## Base e checkpoint

A base é a R131 corrigida: fonte `8503c2e32d7487d3bb31397ba9533dc7e1bfe981`, APK SHA256 `0273ab9ae1b7ef5a061fdcc76c49558db4180bedd10a8100e6d5f764ac2ab175`, 2.711.825.423 bytes. A instalação e o bootstrap Sony documentados nessa base não validam a R132.

Antes das alterações, o checkpoint `8a199d025e9eb338f1973f8e2f8ca975862cdef5`, branch `checkpoint/station-r131-before-cleanup-20261011`, foi confirmado no remoto e no backup completo existente. Mantém-se o único backup e seus inputs necessários, sem apagar dados dos emuladores.

A R132 foi instalada diretamente **somente no Motorola Edge 30** em 11/10/2026 às 20:54:08.764316 UTC. O SHA integral no aparelho corresponde ao APK final; UID/dados e assinatura original foram preservados, sem cópia extra de APK no telefone. O frontend oficial foi observado às 20:54:12.047096 UTC. O [recibo agregado](evidence/installation.json) não contém serial ou sessão pessoal; a sessão autenticada, a medição da preparação nativa, gameplay, controles e consumo térmico são verificações separadas, ainda não concluídas por esse recibo.

Na conferência física posterior, abrir **Criar sala** no jogo N64 selecionado e executar a primeira consulta segura refez capabilities e manteve a mensagem: “Não há modo aprovado para esta edição e o motor instalado. Atualize o aplicativo e o catálogo nos participantes.” A recusa ocorreu antes de criar sala ou abrir o jogo; o bloqueio exige vínculo de edição/conteúdo/modo aprovado com o motor atual. Não foram capturados resposta HTTP ou envelope bruto, portanto não há prova física de HTTP 409 nem identificação do campo específico faltante. A capa selecionada N64 foi exibida localmente. [Observação agregada](evidence/physical-observation.json).

## Alterações delimitadas

1. **Preparação dos shaders no loading inicial.** A preparação ocorre no contexto GL do renderer antes de retirar a barreira de carregamento. O objetivo é antecipar trabalho que aparecia no primeiro uso. Não há medição que comprove menor tempo total de abertura ou redução térmica; transferir o trabalho para o loading não elimina seu custo. O desenho dos efeitos, LEDs, ganho/rastro, limite de 30 fps dos menus, política de vídeos, economia, cache e preload continuam no escopo preservado.
2. **Duas sinopses de plataformas: PS3 e PS4.** Entram no mesmo painel de informações utilizado pelos sistemas Nintendo, por includes overlay explícitos. As fichas existentes, sinopses de jogos/DEMOs e catálogo assinado são preservados. Os textos não prometem compatibilidade de jogos nem alteram capacidades online. Referências factuais: [história do PS3](https://www.playstation.com/pt-br/playstation-history/2007-ps3-ps-vita/) e [história do PS4](https://www.playstation.com/pt-br/playstation-history/2013-ps4-ps-vr/).
3. **Caminho legado do Switch.** A rota `SAMBOX-Vfull/sistema/roms/switch` foi confirmada. A migração é limitada ao valor legado exato quando vazio, usando `roms/switch`; não move nem apaga jogos, saves ou configurações arbitrárias. A recriação contínua da pasta relatada pelo mantenedor não foi reproduzida. A identificação dessa rota não autoriza apagar workspaces necessários de outros motores.

Na observação R132, o caminho canônico do Switch foi encontrado, o diretório SAMBOX legado não estava presente e o frontend havia retomado. Esse estado pontual não prova ausência de recriação futura. A janela de medição foi alterada por navegação/reabertura do usuário: tempo físico de shaders depois do loading, CPU em repouso e temperatura não foram validados.

Receitas novas: `integration/startup-cleanup-r132`. As fontes congeladas R124/R131 não são sobrescritas. O runtime extraído do PS4 foi mantido: a auditoria não comprovou que todos os acessos implícitos de gameplay são dispensáveis.

## Composição conferida do APK

**Sete substituições; zero adições; 13.853 entradas preservadas byte a byte:**

- `classes8.dex`;
- `lib/arm64-v8a/libturbo_carousel.so`;
- `lib/arm64-v8a/libstation_frontend.so`;
- `lib/arm64-v8a/libstation_psx_online.so`;
- `lib/arm64-v8a/libstation_mupen64plus_runtime.so`;
- `lib/arm64-v8a/libstation_dolphin_runtime.so`;
- `assets/station-online/engines.json`.

O DEX8 permite alteração apenas de `Lorg/emulationstation/frontend/switchengine/SwitchConfigPatcher;`. Os conjuntos de classes e as demais classes desse DEX foram preservados. Os **39 outros DEX**, incluindo DEX40 Sony, estão byte idênticos à R131. Firmware/material PKG privado, capas, vídeos, bibliotecas Sony, cores dos emuladores, opções, perfis de controle e capacidades permanecem nos inputs preservados. SNES/Mega Drive mantêm as rotas aprovadas pelo mantenedor; PS3/PS4 seguem exclusivamente offline.

Os quatro marcadores N64/GameCube/Wii/PSX foram renovados porque o bundle compartilhado mudou. Isso não altera o core, o protocolo `station-stream.v3`, o transporte, a autenticação ou a capacidade máxima dos perfis. Os IDs/hashes exatos estão no [STATUS](STATUS.json) e no [manifesto público de hashes do kit](evidence/server-kit-manifest.json); nunca cadastrar IDs históricos como se fossem R132.

## Servidor: uma entrega final

O retorno real lido é `a6b58e9beb12eb564c1b58d9d4c32ed3e7513861` do Servidor-pix. Ele revisou o kit **R129**, declarou autenticação administrativa nativa pendente e não confirmou publicação efetiva dos scripts, recebimento do kit privado ou ativação dos motores finais. Seus testes administrativos isolados não são prova de produção ou gameplay R132.

Nesse mesmo retorno, `covers.published=false`: a preparação incluiu 157 vínculos N64, mas não declarou sua publicação. O campo `latestProductionBindings` enumerou somente Mega Drive (331), SNES (671) e PSX (28). Isso não demonstra ausência de toda capa N64 existente; demonstra que aquela atualização de capas ainda não foi concluída/publicada. O cadastro dos novos motores e a publicação de capas são verificações distintas.

A capa N64 observada no telefone já estava disponível localmente; `covers.published=false` refere-se ao batch do servidor, não à ausência de todas as capas locais. A conferência de um jogo não audita as demais capas.

O [handoff único](HANDOFF-APP-R132-PARA-SERVIDOR-20261011.md) usa o contrato v3 e reúne o cadastro dos quatro motores, modos explicitamente aprovados e confirmação assinada fresca. O kit privado foi preparado com **16 arquivos/seis bibliotecas**. O par original está em `server-kit-original-receipts/runtime-final.json` e `package-final.json`, copiado byte exato dos originais de identidade e verificação: seu vínculo SHA foi conferido. Recibos públicos sanitizados têm proveniência, mas não são o par consumível pelos helpers administrativos. Não reduzir guardas para aceitar um par diferente. O kit ainda não foi recebido/aplicado pelo operador.

## Evidências e limites

- [Estado desta revisão](STATUS.json).
- [Auditoria dos owners/workspaces](../../audits/station-runtime-cleanup-r132-20261011/sandbox-owners.json).
- [Cruzamento dos três retornos reais do servidor](../../audits/station-runtime-cleanup-r132-20261011/server-crosscheck.json).
- [Recibos finais e índice público](evidence/PUBLIC-EVIDENCE.json).
- [Inventário e selos públicos do kit privado](evidence/server-kit-manifest.json).
- [Recusa segura N64 e caminho Switch observados](evidence/physical-observation.json), com hashes dos recibos privados e sem capturas, nomes pessoais ou logs.
- [Template administrativo preparatório](../../audits/station-runtime-cleanup-r132-20261011/r132-server-delivery-template.json), anterior à compilação; seus placeholders não são inputs de implantação. Esta entrega e os recibos finais fornecem as identidades atuais.

A instalação, o frontend oficial, a recusa segura N64 e o estado pontual do caminho Switch estão confirmados somente no Motorola. Bootstrap físico dos jogos, partida real, controles, estabilidade, latência, tempo de preparação após loading, CPU em repouso e consumo térmico ainda não foram validados. Os cinco recibos finais de compilação registram o estado anterior à instalação; os recibos físicos posteriores complementam esse estado sem alterar seus selos. O Git recebe somente fontes, receitas, documentos e recibos agregados; não recebe APK, firmware, BIOS, material RSA, jogos, mídia, licenças, seriais, sessões ou logs pessoais.
