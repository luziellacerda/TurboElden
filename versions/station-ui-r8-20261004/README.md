## Atualização posterior — R8 instalado, R9 candidato

R8 `8e76d832…` foi instalado e teve hash do APK no aparelho conferido. Seis botões verdes e salas foram observados; serviço apareceu indisponível. USB caiu antes de conferir Voltar. R8B, somente no PC, corrigiu a métrica da fonte online. A melhoria posterior está em `../station-ui-folders-r9-20261004/README.md`; R9 ainda não instalado. Restaurar ajuste temporário de tela para 0 na próxima USB. Textos abaixo registram a preparação anterior e não prevalecem sobre este estado.

# TurboStations R8 — barra de ações e salas

## Estado real em 04/10/2026

**Compilado e conferido no PC; instalação e visual Android pendentes de USB.** Última instalação comprovada continua sendo R7. Não promover esta revisão a estável nem declarar partida online testada. O operador aplicará o servidor conforme o handoff R7; esta revisão não publica serviços.

APK local: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Salas-Botoes-R8-20261004.apk`.

- SHA256: `8e76d8328d140a6f423b9317a77bc4f154cb5de882d8e24db16df8b71f0ea783`.
- Tamanho: 1.982.738.120 bytes.
- Pacote: `org.turboramastation.frontend`.
- Certificado preservado: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
- Base R7: `827723436ac618d3b1745a873813c7781ff10e043abc6033de416c01d774703d`.
- R7 arquivado com hash conferido em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Online-Candidato-R7-20261004.apk`; a cópia duplicada em E: foi removida para liberar espaço. A estável de recuperação permanece intocada.

## Pedidos atendidos na fonte e no APK

### Barra dentro dos jogos

As seis ações **Baixar/Jogar, Jogar online, Saves, Apagar, Atualizar e Voltar** usam o mesmo desenho nativo: verde em degradê, cantos arredondados, texto branco centralizado na mesma escala, contorno luminoso e faixa de luz diagonal dentro do botão. Saves/Apagar continuam com aparência reduzida quando indisponíveis. A indicação de confirmação de exclusão preserva o contorno vermelho e o foco mantém realce próprio.

`native_game_actions.h` contém o desenho compartilhado. `native_skin.h` o chama para as cinco ações antigas; `native_netplay.h` o chama para Jogar online. A função de toque de Jogar online e o despacho JNI não mudaram. Não foram alterados retângulos de toque, ordem, regras de download/instalação/exclusão ou os controles de plataformas. **ABRIR das plataformas permanece no desenho anterior.**

O efeito usa o relógio monotônico e os frames existentes do GuiStore: 286 vértices por face, sem novos timers, threads, texturas ou decodificadores. A política de FPS do menu não foi alterada. Consumo e fluidez no telefone ainda não foram medidos nesta revisão.

### Tela das salas

`StationRoomsActivity` ganhou cabeçalho compacto, estado da conexão, contexto do jogo, apelido, Criar sala, Reconectar e Voltar. Em paisagem, três áreas separam jogadores, salas/convites e chat. Em largura inferior a 600 dp, os painéis ficam empilhados em uma área rolável.

- Jogadores: avatar com inicial, nome, identificação de você, convite para o anfitrião e menu de contato para bloquear.
- Salas: cartões com nome real do catálogo, ocupação informada pelo servidor, convite, entrada, confirmações e saída.
- Chat: área própria com autor e mensagem, posição preservada, rolagem para novas mensagens; envio desativado fora de uma sala.
- Conexão: apresentação explícita para carregamento, serviço indisponível e lista vazia. Não há jogadores, salas ou números de demonstração.
- `StationActionButton` fornece degradê, borda, resposta ao toque, estado desativado e animação de brilho. Apenas **Criar sala** habilita animação contínua, enquanto estiver anexado, visível, habilitado e com foco da janela. A animação é cancelada ao perder foco, esconder ou desmontar a tela. Os cartões de uma lista longa não criam animações contínuas.

## Preservação e testes

Somente duas entradas existentes mudaram: `classes35.dex` e `lib/arm64-v8a/libturbo_carousel.so`. Um novo recibo foi adicionado em `assets/station-ui-r8/BUILD-NOTICE.json`. **11.100 entradas preservadas**, conferidas por SHA256 individual, sem entradas ZIP duplicadas. Assinatura e alinhamento de 16 KiB conferidos. Vídeos mantêm armazenamento sem compressão.

34 verificações de fonte e execução passaram. O teste C++ executou o desenho nativo real em 1.440 combinações de tamanho, tempo, posição e estado, conferindo limites, cor, movimento, clipping e dimensões nulas. Comparações de código confirmaram preservação das ações, entrega de snapshots, paginação, preparação/lançamento de partida, chat e saída. Compilação repetida de ambos os componentes produziu exatamente os hashes já empacotados.

Nenhuma rota, assinatura de requisição, sessão, catálogo, download, motor local, biblioteca online, manifesto ou mídia foi alterada. Não há alteração do contrato do servidor: continua o handoff de `versions/station-online-20261004/HANDOFF-APP-PARA-SERVIDOR-ONLINE-20261004.md`. A última observação autenticada R7 recebeu 404 nas salas; isso é histórico do aparelho, não prova do estado atual da implantação do operador.

## Fonte e reprodução

Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004`. Esta pasta de Git fornece os arquivos substitutos sobre a fonte R7, documentada em `versions/station-online-20261004` (código `dd6aff172761f40c9b8eea2d3e2c1c34a0c79034`, evidência posterior `0cdc1f3e4b8473fdbbd3d1b207b60e157b19baf6`). As imagens e objetos grandes continuam nos insumos locais verificados da mesma base.

1. Aplicar os três headers de `native/` e os dois Java de `netplay/src/` na árvore canônica correspondente. Preservar todos os demais arquivos R7.
2. Copiar `netplay/build_ui_r8.py` para a pasta canônica `netplay`. Ele compila em `netplay/build-r8` e usa `station/build/station-client.jar` da base.
3. Executar `scripts/build_station_ui_r8.py` com Python. Compila pelo Clang/NDK r28c, JDK17 e Android34 já instalados. Temporários e logs em E:.
4. Executar `scripts/test_station_ui_r8.py` a partir do workspace original. O teste usa `work/TurboElden-git/versions/station-online-20261004` como referência das fontes preservadas.
5. `scripts/package_station_ui_r8.py` exige o SHA exato do APK R7 arquivado e destino R8 inexistente. Faz montagem completa, alinhamento, assinatura e comparação integral de entradas. Não sobrepor o APK final sem arquivá-lo com hash.
6. Instalar somente por atualização, com o aparelho nas plataformas: `adb install --no-incremental -r --user 0 <APK>`. Não desinstalar, limpar dados, trocar a chave ou copiar configuração manualmente para o telefone.

## Conferência Android ainda necessária

Abrir uma plataforma, observar as seis ações e o movimento da luz, abrir Jogar online, conferir dimensões/textos/estados da tela nova e voltar ao catálogo sem novo login. Conferir a navegação por controle físico separadamente. Quando o operador liberar o serviço, validar salas, convite, chat e partida com dois aparelhos; a alteração visual não substitui essa homologação.

Pendências anteriores permanecem registradas no handoff R7 (incluindo células azuis das plataformas). Esta alteração não declara corrigidos problemas fora do desenho dos botões e da tela das salas.
