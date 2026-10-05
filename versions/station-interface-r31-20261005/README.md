# R31B — ações compactas, informações e etiqueta de instalado

## Estado exato em 05/10/2026

Pacote `org.turboramastation.frontend`, classes `org.emulationstation.frontend`, assinatura original preservada. Trabalho apenas TurboStations Android. Temporários/fontes na unidade E; APKs na G. Nenhum serviço Linux modificado.

- **Candidato final R31B**: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Interface-R31B-20261005.apk`.
- SHA256 `76817d2dd48219bcd6e4d111b8471bf98925b02ab26ee517cea90e8df84b076c`, 2.053.910.613 bytes.
- SO `4e72c4072d43fbd3e7bf9353b51c1728226b91deb6ece02b688eac095970039f`.
- Fontes: `E:\ESTUDO APK\work\station-actions-gear-r31-20261005\native`.
- Base exata R30: SHA `1768b7df440dcdf99efbd2e8ff93181eae06edaab5bb9be85e073afeb639027b`; commit `b4a980632ac75d837863aa2b558d6bc7655d6648`.
- Java das salas permanece R29B, classes35 `45675ff1b72c76bc6d388f6fa6f016a55cc1d06c4fbec09689ab4654dde3e9f1`.
- Certificado `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

O primeiro candidato R31, `efc2a84593b9a6ecc0a25f59dcff1257b703e7fd4c761e8cd99d532b2431104b`, foi instalado no Samsung em 05/10 às19h14min37s (UTC−3), por atualização com dados. O SHA completo do telefone confere. Captura mostrou sessão mantida,34 instalados, selo no Battletoads, botões alinhados e metadados em uma linha. A USB saiu antes dos testes seguintes.

**R31B amplia somente o texto INSTALADO dentro da etiqueta. Consulte STATUS e os recibos posteriores para saber se já foi instalado. Não tratar a prova visual de R31 como prova visual de R31B.** Não houve desinstalação/limpeza; não foi comparado cada save individualmente.

O mantenedor informou que conectará o POCO para instalar/ativar. Até a primeira documentação desta revisão ele ainda não apareceu na USB. A opção temporária de manter a tela ligada durante carga no Samsung mudou de0 para3; a restauração ficou pendente porque a USB foi retirada. Não repetir essa alteração no POCO sem registrar seu valor inicial.

## Mudanças e funções

### Ações inferiores

`stationBottomGameAction` é a fonte única de retângulos para desenho e toque. Seis larguras em unidades da altura:3,3 /4,45 /3 /3,2 /3,7 /3,1; intervalo0,16 da altura. Grupo começa em2,5% da largura, encolhe somente se exceder95% da tela. Ordem: Jogar/Baixar, Jogar online, Saves, Apagar, Atualizar, Voltar. Os cinco botões nativos e o botão online usam esse helper. Textos alinhados à esquerda depois do ícone; cores, efeitos de borda e rotas mantidos. Fundo inferior acompanha apenas o grupo compacto. A largura corrigida do Voltar nas coleções R30 continua.

### Linha acima da sinopse

`stationGameMetaRow` distribui nome, ícone/quantidade de jogos, ícone/jogadores e cinco estrelas na mesma linha. `updateSystemInfo` avança o início da sinopse e do console em5,4% da altura, reservando uma linha de4%. Texto restante continua completo e rolável com recorte; nenhum parágrafo foi removido. Título deixa a posição antiga abaixo do console; estrelas deixam o cabeçalho global. Nome muito longo diminui e, se necessário, recebe reticências em limite UTF-8 sem alterar o nome no catálogo.

Quantidade = número de itens da lista visível/filtrada; jogadores e nota vêm de `StationGameDetails` pelo ID exato. Número ausente aparece como traço; nota ausente mantém estrelas neutras. Não foram inventadas médias, avaliações de compradores ou número de jogadores. Plataformas/coleções mantêm suas sinopses e títulos anteriores. Console permanece somente nos jogos.

### Etiqueta pendurada

`drawInstalledTag` consulta o estado instalado do item selecionado no catálogo nativo a cada desenho. Renderiza apenas no modo jogos, sem modal e após carregamento do catálogo. Acompanha a posição animada da célula selecionada e some durante deslocamentos maiores. Ao baixar/apagar, o estado original do catálogo controla a etiqueta.

Referência do mantenedor: etiqueta de ofertas com ponta, furo e laço. Arte nativa verde/preta, detalhe vermelho, inclinação8°, ilhós, laço Bézier e brilho limitado ao interior. Texto INSTALADO na mesma matriz da arte; R31B aumenta e centraliza a palavra. Geometria desenhada no loop visível existente, sem bitmap gerado, worker, vídeo ou temporizador extra. Não é fita sobre todas as capas e não marca jogo não instalado.

### Engrenagem Lottie

Fonte exata: [Gear3 por Giovana Pontes](https://lottiefiles.com/pt/free-animation/gear-3-oz2ZcDdYz1). JSON original SHA `9c6b8546fbe7e11d6e31d140c5342227f40a54e3d575a71fb915decdf6177eb7`,29,97fps/90frames. Dois contornos, cor originalB78E31 e easing original. Curvas amostradas em962+194 vértices;90 amostras de rotação. Padding da composição aparado para ocupar o espaço do ícone atual.

`GuiStore::drawGear(float,float,float,unsigned)`, símbolo0x221854, relocação0x3c14a0 confirmada no libmain `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`. Hook apenas quando `skinTop`; demais usos encaminham ao original. Troca o desenho antigo e mantém área de toque/ação. Não é sobreposição Android nem substituição global de glifos. JSON/crédito/licença incluídos em `assets/turborama-ui/`. [Lottie Simple License](https://lottiefiles.com/page/license) permanece aplicável à animação e derivados, sem substituir por restrições do projeto.

## Retorno do servidor — lido e cruzado

Commit completo `61c0411d0a306f348f48647b466a05a3d0f78733`, ramos `feat/station-poco-online-20261005`, `feat/station-online-direct-20261004`, `feat/station-netplay-internet-r12-20261005` e `feat/station-artifact-descriptor-20261002`.

[Retorno exato](https://github.com/luziellacerda/Servidor-pix/blob/61c0411d0a306f348f48647b466a05a3d0f78733/docs/station-android/RETORNO-SERVIDOR-NETPLAY-INTERNET-STATION-R12-20261005.md). Clone existente consultado com fetch explícito, sem checkout/clone/implantação.

Servidor declara fonte `e4e557a985ac5bead24885149c8650a5bb2dfae8`, DLL `7ecb6c8d94c5ab42c26638b5f9bdf7ffd0e70f99e047463ee5293af34f7bdcf5`, relay privado em `wss://app.lzgames.com.br/v1/station/online/relay`,512salas/1.024conexões configuradas. Catálogo14/2.212visíveis. SNES/SNESBR/Mega/MegaBR autorizados online; não habilitar outros motores por suposição.

`evidence/server-crosscheck.json` registra15 conferências de fonte: UUIDrequestId, sessão por lease, instance/revision, heartbeat20s, transporte anunciado, ticket por participante, caminho/subprotocolo/header, pin/TLS, TCP_NODELAY, callback real host-listening e fechamento. Tudo já presente no cliente R30/R29B. **O retorno não exige novas rotas, host, chave, porta ou DEX no APK.** Mantivemos exatamente o cliente que o servidor reconciliou.

O próprio retorno ainda deixa aberto o atraso público: p95WSS2.291,82ms com256conexões, contraAPI0,83ms/Nginxlocal1,07ms. Uma sala também apresentou p95de2.176,15ms. São medições do operadorLinux; não foram repetidas aqui e não identificam a causa única. Partida real em doisAndroid, duasredes e baixa latência continuam pendentes. Não anunciar256jogadores responsivos, estabilidade geral ou correção de lag por esta mudança visual.

### POCO e ativação

O handoff declara licença própria POCO ACTIVE/PENDING_ENROLLMENT, vitalícia/um aparelho, primeiro código válido até07/10/2026às17h11min33America/Maceio. Isso é estado documentado do servidor, não uma ativação efetuada nesta estação. **O Git não contém o código**: arquivo privado `/home/lz-servidor/LICENCA-POCO-STATION-20261005.txt` no Linux, permissão0600. Nenhum código/token foi copiado para este snapshot. Não confundir ID da licença com código de ativação nem reutilizar a licença Samsung.

O operador deve disponibilizar o código ao mantenedor ou arquivo local autorizado; digitá-lo no login após instalar o APK final. Primeiro vínculo exige sessão real do Keystore do POCO. Manter assinatura, jogos e dados quando houver instalação existente. O conector remoto estava offline e o painel por browser não pôde ser inicializado nesta estação; nenhuma concessão administrativa nova foi executada.

Depois: mesmo APK e mesma edição/ROM/core/opções em ambos, salas → Reconectar → criar/convidar/entrar → dois Pronto → iniciar. Confirmar controles dos dois, sincronismo, áudio, saída e sessão. Nunca consumir a licença POCO por um cliente sintético.

## Testes e reprodução

6.873 verificações C++ passaram:42 tamanhos/proporções, retângulos de ações/metadados, separação da sinopse, larguraVoltar,962pontos e90framesLottie. Compilação NDK/API26 passou. Assinatura original e alinhamento16KiB passaram. Comparação integral: apenas `libturbo_carousel.so` alterado,3assetsLottie adicionados,13.083 entradas antigas preservadas inclusive todos os DEX/motores.

`recipes/restore_r31.py E:\diretorio-novo` reconstrói fontes exatas pela baseR30 + estes deltas e compara todos os hashes. A baseR30 derivaR26/R27 conforme sua receita, nunca R28. Dependências nativas continuam W16 `station-download-performance-20261005/frontend-native`, mais os objetos únicos `video720_posters.o` (W16) e `neogeo_previews.o` (W22). Não duplicar objetos/mídias.

Build: scripts em `recipes`, testes em `tests`, recibos em `evidence`. `build_r31.py` usa `native-build-input.json`; `package_r31.py` exige APK R30 exato e recusa sobrescrever resultado. Alterar caminhos para diretório novo de saída antes de reproduzir; nenhum binário grande ou mídia privada foi incluído no Git. `prepare_r31.py` e `finalize_source_r31.py` são receitas históricas de geração da primeira variante: **não executá-las sobre fontes finais**, pois substituiriam os ajustes finais de texto/tag. Os fontes publicados e o manifesto são a autoridade.

Atualizar com `adb install --no-incremental -r --user 0` somente após identificar aparelho e sair de jogo/download. Conferir SHA completo no aparelho. Não desinstalar, limpar dados ou trocar assinatura para contornar erro.

Delta de downloads11be7f3/6f012a7 continua separado e fora deste APK; não foi exigido pelo novo contrato de salas. Não anunciar sua integração. Esta entrega não modifica autenticação, firmware, BIOS, catálogo, motores ou política de verificação de downloads.

## POCO — tentativa de instalação posterior

O POCO2412DPC0AG apareceu na USB. A primeira leitura encontrou APK antigo SHA438010ddd716b67731c59462caebb6e163d216ed99a1e8b9a347ddd6b1a2c4ac (WiiU/01–02outubro); antes da instalação o pacote deixou de constar em `pm list packages`. O agente não desinstalou nem limpou dados. Não atribuir autoria à remoção. A instalação doR31B às19h25–19h27 foi recusada peloAndroid com INSTALL_FAILED_USER_RESTRICTED/Install canceled by user. Foi solicitado ao mantenedor desbloquear e habilitar Instalar viaUSB. Também houve INJECT_EVENTS negado ao tentar acordar a tela; não houve tentativa de contornar essa restrição. Recibo preservado. Ativação ainda não realizada.

A restauração de todas as fontes nativas/Java pelo script publicado passou e conferiu todos os hashes doSOURCE-MANIFEST. Os6873testes deR31 não substituem gameplay Android.

## Encerramento da rodada no POCO

A segunda tentativa (19h28–19h30) também retornou INSTALL_FAILED_USER_RESTRICTED. Foi iniciada cópia para `/sdcard/Download/TurboStations-Interface-R31B-20261005.apk`, para instalação manual com confirmação do Android. A transferência falhou com `25473-byte write failed` e o aparelho deixou de aparecer na USB. Essa cópia no telefone pode estar incompleta: conferir tamanho/SHA ou substituir pelo APK íntegro do PC antes de instalar. Não confundir arquivo em Downloads com aplicativo instalado.

Nenhuma ativação POCO foi realizada. Não houve desinstalação, limpeza ou desativação de restrições por este agente. Samsung permanece no primeiro candidato R31, POCO sem instalação final comprovada. A configuração temporária manter tela ligada no Samsung ainda precisa voltar de3 para0 quando reconectar. O POCO não teve essa configuração alterada.

A restauração completa dos fontes pelo script publicado passou, conferindo todos os hashes. O retorno61c0411 foi lido integralmente, além de15 conferências estáticas no cliente. Teste de gameplay em dois aparelhos e baixa latência pública continuam pendentes.
