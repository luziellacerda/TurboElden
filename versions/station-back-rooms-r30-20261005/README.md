# R30 — Voltar nas coleções e diagnóstico das salas

## Entrega e fontes canônicas

Data: 05/10/2026. Pacote `org.turboramastation.frontend`; classes Java `org.emulationstation.frontend`. Não mudar identidade/assinatura nem desinstalar para atualizar.

APK final: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Voltar-Salas-R30-20261005.apk`.

- APK SHA-256: `1768b7df440dcdf99efbd2e8ff93181eae06edaab5bb9be85e073afeb639027b`, 2.053.858.040 bytes.
- Certificado: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
- Native: `E:\ESTUDO APK\work\station-back-button-r30-20261005\native`.
- SO: `142ebfa99724a311893708cb295af9c2cfecaee6ee51c8c6ec6d47e3b3267c5f`.
- Java completo: `E:\ESTUDO APK\work\station-room-diagnostics-r29-20261005\netplay-src` e `dependency-src`.
- `classes35.dex`: `45675ff1b72c76bc6d388f6fa6f016a55cc1d06c4fbec09689ab4654dde3e9f1`.

Instalado em 05/10/2026 às 18:39:35 (UTC−3); SHA completo do APK instalado igual. Atualização `-r --no-incremental --user 0`, sem desinstalação/limpeza. Aplicativo abriu já conectado; 32 instalados continuaram indicados. Não foi feita comparação binária de todos os saves. Não promover a estabilidade geral ou declarar multiplayer real aprovado.

## Encadeamento exato

R27 `c1191ce1d531b1ec9171d6d4c2f57541349339e64e8941a33788c4067d616bd6` → R29B `76c8799d3d094a8d4186395897d73c3cb327a60476fd4d28f6d55783692228d5` (somente classes35) → R30 (somente carousel SO). Cada etapa preservou integralmente 13.083 outras entradas; assinatura, recursos N64, motores, mídias, arquivos de licença e configuração foram preservados. R29 intermediário foi substituído pelo B e não instalado. R28 foi cancelado e não integra esta entrega. Downloads 11be7f3 permanecem fora deste APK.

## Causa e correção de Voltar

Na seleção de coleções, o R26 alocava 66% da largura da célula para Abrir e 31% para Voltar, aplicando depois a redução geral de 12%. A seta reserva 0,98 da altura do botão; a margem final reserva 0,16. O espaço restante para seis letras causava quebra `VOLT` / `AR`, reproduzida na captura do mantenedor e no aparelho.

`stationCollectionAction` agora distribui 52% para Abrir e 45% para Voltar, intervalo inicial de 3%, mantendo a redução interna de 12%. Altura, cores, ícones e rotas existentes continuam. `layoutSkin` usa o mesmo retângulo para desenho, rótulo e toque. Somente coleções aplicam essa redistribuição; a ação das plataformas e as seis ações dos jogos mantêm a geometria anterior. Não foi criado overlay nem navegação por coordenadas dentro do APK.

No telefone: Voltar apareceu inteiro e alinhado; toque retornou às plataformas sem login; reabertura do SNES mostrou as coleções; Abrir entrou em Todos os jogos. Capturas locais e hashes constam em `evidence/device/runtime.json`. Coordenadas ADB foram usadas somente para o teste manual automatizado no aparelho.

## Salas — causas demonstradas e código alterado

1. **Arquivo não baixado:** a função existente `StationFrontend.installedPathForItem` lançava IOException com orientação local. O fallback `StationOnlineClient.message` a transformava em erro genérico de conexão. `StationOnlineGame.installedRom` traduz somente os estados locais conhecidos para `Unavailable`, rejeita arquivo ausente/symlink e preserva os demais controles de integridade/compatibilidade. Não expõe caminho/token no texto.
2. **Começar antes dos requisitos:** R27 oferecia Iniciar mesmo com um único participante. O servidor recusava corretamente com `STATION_ONLINE_NOT_READY`. `StationRoomStartState` calcula a disponibilidade a partir do snapshot assinado: host, sala waiting, dois membros diferentes, ambos prontos e `relay-wss-v1` anunciado. A interface desativa o botão e explica a etapa pendente; valida novamente na confirmação. O servidor continua sendo a autoridade.
3. **Mensagem apagada pela presença:** `StationRoomFeedback` conserva o erro até a próxima ação/reconexão. Atualizações do snapshot não o substituem por uma mensagem genérica de convite.
4. **Diagnóstico:** `StationRoomsActivity.recordFailure` registra somente classe da exceção, código validado, status HTTP e stack de métodos/linhas limitado. Não registra mensagens arbitrárias, corpos, tokens, códigos de licença ou URLs. Falha do poll muda o estado visual para Reconectar.

Arquivos existentes alterados: `StationOnlineGame.java`, `StationRoomsActivity.java`. Novos: `StationRoomStartState.java`, `StationRoomFeedback.java`. Das 144 fontes anteriores de produção/dependências, 142 permaneceram intactas; o build final reúne 146 fontes.

## Aparelho e limites das provas

- R29B: jogo não instalado passou a mostrar “Baixe este jogo primeiro…”; a orientação persistiu após atualizações da presença. Reconectar e Voltar ao catálogo funcionaram.
- R30: Battletoads instalado criou sala real; Estou pronto virou Cancelar confirmação e o membro apareceu Pronto; Iniciar permaneceu desativado com uma pessoa. Nenhuma partida foi forçada.
- Antes da atualização: perfil próprio, código TS1 e Sair da sala haviam sido exercitados no R27. Não atribuir essas capturas ao R30.
- Houve mudança de tela durante a última conferência; a captura posterior mostrou coleções. Não é prova de que o gesto de rolagem fechou a sala. Os registros novos mostraram `STATION_ONLINE_ENTER_REQUIRED` no poll, também observado ao sair/offline. Não foi capturada exceção de crash atual.
- Um erro genérico em sala já criada havia aparecido no R27. A causa exata daquele evento não ficou comprovada. A instrumentação do R29B/R30 foi adicionada para distinguir erro local, API, timeout ou mudança da instância. Não afirmar que todos os erros de rede foram resolvidos.
- Durante a observação do R29B, o servidor anunciou temporariamente 143 usuários com nomes `Load host/guest`; depois voltou a 2/1. Isso é apenas observação, não prova de autoria ou de número real de jogadores. Nenhum convite/chat foi enviado a esses usuários.
- Um único celular disponível. Convite aceito por outro aparelho, gameplay, sincronismo, retorno da partida em dupla e transferência relay real em produção não foram comprovados. Exigem dois clientes/licenças e a rede real. Não apresentar os testes abaixo como substituição dessa validação.

## Servidor consultado, sem implantação

Clone existente: `E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002`. Fetch de todos os ramos, sem alterar checkout ou clonar.

- `feat/station-online-direct-20261004`: `11be7f3a725d236439be820dd0a3e6c517e771f5`.
- `feat/station-netplay-internet-r12-20261005`: `d358e5f4d127a607bdf0c1ce3e4f4c2b4eaa7504`.
- Implementação relay consultada: `0037a0f5bf20734bac25cd2497158b06bed0bc58`.

Lidos `RETORNO-SERVIDOR-ONLINE-STATION-20261004.md` e `HANDOFF-APP-SERVIDOR-NETPLAY-INTERNET-R12-20261005.md`; o segundo é pedido do app, não resposta de implantação. O snapshot real anunciou transporte relay (a confirmação de conexão internet apareceu no R27). Isso não prova binário/proxy implantado nem transferência entre celulares. Não foi feito deploy, mudança no banco, reinício ou chamada administrativa.

## Testes executados

| Escopo | Resultado | Limite |
|---|---:|---|
| Helpers reais Java de estado/arquivo/mensagem | 60 checks | Stubs Android/frontend |
| Modelos/código de convite/reducer herdados | 107 checks | JVM local |
| Serviço C# de sala/chat/convite | 39 checks | Identidades sintéticas, isolado |
| Rotas HTTP assinadas | 37 checks | Kestrel local |
| TLS WSS/tickets/revogação | 17 checks | Serviço local, certificado de teste |
| Java de produção ↔ relay C# | 7 checks | Endpoints TCP sintéticos |
| Layout R26 preservado | 773.128 checks | Geometria/C++ no PC |
| Largura/toque Voltar R30 | 252 checks | 36 tamanhos/proporções |

O teste de túnel transferiu 12.583.029 bytes em cada direção, mais 50 comandos curtos ordenados, recusou pin incorreto e conferiu fechamento. Não executou jogo Android. Compilação Java8/API34, D8 mínimo26, NDK/API26, assinatura e alinhamento16KiB passaram. Todos os conteúdos do pacote foram comparados por hash com a base de cada etapa.

## Reproduzir sem regredir

1. Este snapshot guarda os seis arquivos alterados/novos, com manifesto de **todos** os fontes finais. Os arquivos restantes vêm dos snapshots completos `station-layout-r26-20261005/native` e `station-compact-lobby-r27-20261005/{netplay-src,dependency-src}`. `recipes/restore_back_rooms_r30.py E:\caminho-novo` combina as bases e os deltas e exige todos os hashes finais iguais. Depois distribuir Java para W29 e native para W30; não executar receitas históricas sobre diretórios já publicados. Essa forma evita duplicar o cabeçalho gerado de consoles de 19 MB no C: sem espaço e mantém a reconstrução exata.
2. Para Java: `build_room_diagnostics_r29.py final`. Usa JDK17, Android34, D8 e API compile-time `station-library-r10-build-20261004/station-client.jar`. Os fontes e hashes do jar de saída/DEX estão no recibo.
3. `test_room_diagnostics_r29.py` espera testes em `room-r29/` e `lobby-r27/` junto da receita; neste snapshot estão em `tests/`. Copiar esses dois arquivos para as pastas esperadas antes de executar, ou ajustar somente os caminhos da receita. O runner relay usa a fixture compilada e fontes da revisão `internet-r12`, documentada na versão correspondente do Git.
4. Native: `build_back_button_r30.py`, com os dois testes em sua pasta. A entrada `evidence/native/native-build.json` contém o comando NDK exato; inclui headers/stubs de W16 e **uma cópia** de cada objeto `video720_posters.o` (W16) e `neogeo_previews.o` (W22). Preservar ambos, sem duplicar símbolos/mídias.
5. `package_room_diagnostics_r29.py` recria R29B sobre R27 exato; `package_back_button_r30.py` gera R30 sobre R29B exato. Não sobrescrever APK existente. Gates de SHA/certificado/preservação são obrigatórios. Temporários E:, resultado G:.
6. Atualizar somente sem emulação/download ativo, com `adb install --no-incremental -r --user 0`. Comparar SHA completo no aparelho. Nunca limpar dados para “corrigir” uma atualização.

Os binários APK/SO e mídias privadas não são publicados no Git; as pastas locais, hashes, receitas, fontes e recibos identificam exatamente os insumos. A documentação R27/R26/W16/W22 permanece necessária para bibliotecas/objetos preservados. A opção temporária manter tela ligada durante carga deve ser restaurada ao valor original 0 ao terminar; recibo separado informa o estado efetivo.
