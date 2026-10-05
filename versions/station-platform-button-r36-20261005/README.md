## Instalação posterior nesta entrega

R36 instalada no Samsung por atualização; SHA integral no aparelho igual ao APK. Nenhuma desinstalação ou limpeza de dados. Recibo em evidence/installation-samsung.json. A ausência de USB registrada abaixo é histórica e foi resolvida após o mantenedor reconectar. Validação visual, quando disponível, está registrada separadamente; não confundir instalação com teste de partida online.

# R36 — nome da plataforma no botão e ajustes finais de layout

## Estado comprovado

APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R36-20261005.apk`, SHA-256 `dfe9dd4ce24fdca80986919e885b0a09d146f29dd8ab156f0dffdf18d2a46f57`, 2.053.900.392 bytes. Pacote `org.turboramastation.frontend`; certificado original preservado. Fonte canônica `E:\ESTUDO APK\work\station-platform-button-r36-20261005\native`.

Compilação Android e 12.712 verificações C++ passaram. Assinatura, alinhamento16KiB, todos os arquivos e preservação do pacote conferidos. Não instalado: ADB sem aparelhos durante esta entrega. Último instalado e hash conferido foi R34 no Samsung; não afirmar R36 validado visualmente ou estável geral. O ajuste temporário anterior de tela ligada no Samsung já foi restaurado para0.

## Pedidos incluídos juntos

1. Na raiz de plataformas, o nome do sistema fica dentro do botão antes chamado ABRIR. O nome ao lado foi removido. Mede o nome completo com a fonte real do botão; só abrevia se ultrapassa a área. 52 aliases explícitos, entre eles SNES/N64/PS2, e cinco variantes BR preservadas. Nomes desconhecidos longos recebem reticências UTF-8. Coleções conservam ABRIR e o nome da coleção. Identificadores do catálogo, rotas e toque não mudam.
2. Nome do jogo, ícone de pasta/contagem, ícone/jogadores e estrelas seguem em sequência. Cada intervalo entre grupos corresponde à largura real de dois espaços na fonte nativa; ícone/valor têm um espaço. Escala1,05 preserva aumento50%. Nomes grandes são truncados sem reduzir a fonte. Não há colunas percentuais reservando vazios. Sinopse mantém rolagem e limite da área.
3. Jogar/Baixar mantém a largura da capa focada. Os outros cinco botões têm largura idêntica, com cinco intervalos iguais de0,9% da tela. Barra ocupa2,5%–97,5%; os mesmos retângulos controlam desenho/toque. Cores, ícones e ações preservados.
4. Faixa INSTALADO mais próxima do canto: alcance diagonal0,38 da largura da capa, antes0,61. Efeito de brilho com núcleo visível, ciclo2,6s. Usa o relógio nativo já existente, sem thread, vídeo ou timer novo. Só aparece no jogo selecionado instalado.

## Mapa do código

- `station_platform_button_label.h`: comparador tolerante a caixa/espaço final e aliases. Variantes BR não são confundidas com principal.
- `native_info.h`: mede largura real, monta sequência, limita nomes por busca binária UTF-8, prepara/cacheia texto da plataforma. `preparePlatformActionLabel` mede o TextComponent do botão em+0xe00, escala0,92. Atualização reage à seleção/modo/resolução/revisão.
- `native_carousel.cpp`: render aplica texto preparado somente à raiz; mantém ABRIR nas coleções e suprime título duplicado da plataforma.
- `station_bottom_action_layout.h`: geometria única dos botões.
- `station_game_meta_row.h`: posição sequencial derivada da largura medida; rejeita área insuficiente sem desenhar componente em posição antiga.
- `native_installed_tag.h`: posição e brilho da faixa.

Medição auditada contra libmain SHA62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6. GuiComponent::setSize em0x2771d8 com0/0 ativa largura automática do TextComponent; largura fica em+0x54. Font::sizeText em0x2e7fa4 soma inclusive espaços finais. Não foi chamada calculateExtent diretamente, pois retorna string por ABI diferente. Fonte/uppercase são os componentes reais do app. Testes geométricos e revisão estática não substituem visual no aparelho.

## Base e preservação

Base exata R34 SHA513dd4700192b994d93cdaf6cd55b79eccb804fa33eda43166304f5d2bcdb5ef. Somente lib/arm64-v8a/libturbo_carousel.so mudou;13.086 entradas preservadas. classes35.dex R34 SHA0db040a6b3406e744053c63467ed0f26e3582928ef5b84ecb9e360603ce870f6 e manifesto com callback Voltar mantidos. R35 intermediário não foi instalado; R36 contém todos seus ajustes mais o pedido do botão e a proteção contra retângulo vazio.

Nenhuma mudança no servidor, licenças, downloads ou emuladores. Falha real do segundo jogador Battletoads, controles online distintos e validação Voltar em partida continuam pendências R34. Não declarar corrigidos por esta entrega visual. Delta downloads11be7f3 continua fora.

## Restaurar e recompilar sem perder mudanças

Este snapshot contém seis fontes alterados/novos sobreR34. `python recipes/restore_r36.py E:\NOVO_DIRETORIO` restaura R33, aplica JavaR34 e nativoR36 e confere todos os hashes de SOURCE-MANIFEST. Diretório precisa ser novo. Não restaura APK binário nem modifica telefone/servidor.

Copiar receitas, testes e evidence/native-build-input.json para o workspace de compilação; ajustar caminhos de entrada/saída no recibo antes de executar build_r36.py. O comando exato e hashes constam em evidence/native-build.json. Dependências externas: W16 frontend-native com stubs/headers/video720_posters.o e W22 neogeo_previews.o uma vez cada; NDKr28c API26, LLVM host, JDK17/build-tools35. Não executar receitas dentro do Git sem adaptar workspace. package_r36.py exige baseR34 exata, mantém certificado e recusa sobrescrever candidato. APK/keystore/objetos externos não entram no Git.

Instalar com atualização preservando dados, sem desinstalar/limpar: adb install --no-incremental -r --user 0. Antes conferir que não há partida/download ativo. Validar nome completo/abreviado/BR ao trocar plataforma, coleção ABRIR, títulos curtos/longos, grupos em sequência, seis botões, faixa instalada e retorno. Não alterar somente arquivos do telefone.
