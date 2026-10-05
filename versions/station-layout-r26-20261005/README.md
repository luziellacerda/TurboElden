# R26 — alinhamento do painel e barra inferior compacta

## Pedidos vigentes

O mantenedor rejeitou o alinhamento R25 e definiu: estrelas ao lado de “Não instalado”; no lugar das estrelas anteriores, pasta com quantidade de jogos; jogadores com ícone e “1 player”/“2 players” conforme o dado; todos os botões inferiores mais estreitos.

## Implementação

- Cabeçalho: estado nativo ocupa x=.410W..552W; estrelas em .562W..622W, mesma altura/centro; pesquisa começa em .634W. Texto ajustado apenas quando muda ou quando o layout nativo é reiniciado. Recorte no espaço reservado evita sobreposição com estrelas. Desenho das estrelas ocorre depois do fundo do cabeçalho, usando a matriz nativa, sem novo controle.
- Acima do console: ícone de pasta e contagem real da lista visível (inclusive coleção/filtro) à esquerda; jogadores à direita, alinhados em uma linha. Remove contador duplicado abaixo da sinopse. Um jogador usa uma figura; outros valores usam ícone de grupo. Campo desconhecido conserva traço.
- Console: mantém a escala uniforme máxima e remoção apenas da margem transparente R25. Título permanece centrado abaixo. Sem alteração na arte, UV ou regra de console somente na lista de jogos.
- Barra inferior: largura de cada botão reduzida em 12%, centro/altura preservados, incluindo Abrir, Voltar e Jogar Online. Retângulos de toque e rótulos seguem a largura desenhada. Online usa o mesmo helper no desenho e no toque; ações/rotas não mudam.
- Mantém estrelas com nota real ou vazias quando ausente; não reintroduz nota numérica ou “Nota do catálogo”.

## Fontes e reprodução

Overlay final: `E:\ESTUDO APK\work\station-layout-r26-20261005\native`. Partir dele, com dependências W16 `E:\ESTUDO APK\work\station-download-performance-20261005\frontend-native`. Dois objetos de mídia: W16/video720_posters.o e W22/neogeo_previews.o, exatamente uma vez cada. Comando/hashes completos em evidence/native-build.json.

Muda três fontes existentes do overlay R25: native_info.h, native_carousel.cpp, station_game_panel_layout.h. Importa native_skin.h/native_netplay.h da dependência W16 e modifica só layout/áreas dos botões. Acrescenta station_header_layout.h e station_bottom_action_layout.h. LEDs R24, console fit R25, dados, sinopses, rolagem, vídeos, motores e DEX preservados.

Receitas são guardadas contra sobrescrita; a geração usa os arquivos predecessores incluídos em recipes. O build precisa test_layout_r26.cpp junto do script (copiar de tests). Para reconstruir novamente em outro diretório, ajustar apenas destinos guardados e usar os hashes base documentados; não executar preparação em uma pasta já existente.

## Testes e estado

773.128 verificações C++ passaram: labels, limites/ausências, mesma linha pasta/jogadores, cabeçalho sem sobreposição, 12% de redução de todos os botões e centros preservados, proporções e todos os pixels visíveis das sete artes. Compilação NDK arm64/API26, assinatura e alinhamento16KiB aprovados. APK comparado por todas as entradas: só libturbo_carousel.so muda, 13.083 entradas intactas.

**Compilado; ainda não instalado nem conferido visualmente no aparelho.** USB ausente na última conferência. R25 continua a última instalação confirmada, com visual rejeitado pelo mantenedor. Testes PC não são aceite visual nem prova de estabilidade/FPS. Nenhum servidor alterado; delta download11be7f3 continua separado.

## Artefatos

- APK final: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Layout-R26-20261005.apk`
- SHA256: `1d4549da6a15a9a9b2e8c52491ecc4382e0b5e050900763aebf163d136a36e75`; 2053848592 bytes.
- SO: `E:\ESTUDO APK\work\station-layout-r26-20261005\libturbo_carousel.so`; SHA256 `b2d706dc07d4423758798fe0d6d37ce01c8f395b344c685a7b796ce60d03dd70`.
- APK base R25: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Console-Players-R25-20261005.apk`, hash `0d62d806fb0fd7ef45cf0167dd6908794e180e81171c8f7fa0b3e701aa78baad`.
- Compilação e temporários em E:. Saída assinada em G: por espaço disponível. Apenas o APK concluído R25 foi movido ao backup com hash conferido. Imagens de evidência, testes e fontes permaneceram intactos em E:. O script de limpeza em lote foi rejeitado pela revisão automática e **não foi executado**.

Instalar por atualização, mesmo certificado, dados/saves/licença preservados. Receita exige frontend aberto e hash R25 no aparelho. Não encerrar jogo nem download ativo para instalar.
