# TurboStations R20 — consoles e LED Neo Geo

## Escopo e autoridade

Pedido do mantenedor em 05/10/2026: restaurar consoles ao lado das sinopses e mapear as luzes da arte Neo Geo como feito no SNES/Mega. Ao distinguir capa de jogo e imagem quadrada do Neo Geo CD, confirmou **“Nas duas”**.

Esta revisão altera somente a apresentação nativa. O motor Neo Geo CD recebido separadamente no Git não foi incluído. Não executar receitas antigas sobre este APK. Base exata R19B com N64 próprio corrigido, mantendo acesso Neo Geo R18, pastas R17 e transferências/offline R16.

**Orientação posterior do mantenedor no chat coordenado:** console não deve ficar no carrossel principal. R20 já estava instalado quando essa correção de escopo chegou. O chat “Desmonte o APK de testes” prepara um delta separado para restringir o hardware à sinopse dos jogos, preservando os LEDs desta revisão. Não tratar a exibição de hardware nas plataformas/coleções da R20 como layout final aprovado.

## Identidades e pastas

| Item | Identificação |
| --- | --- |
| Trabalho / temporários | `E:\ESTUDO APK\work\station-console-neogeocd-r20-20261005` |
| APK | `TurboStations-Consoles-LED-R20-20261005.apk` |
| SHA-256 APK | `64eae3ab4dd253e25ee826dd23bf02c947e5cbd1db70e6b07f759d988d465904` |
| Tamanho | 2.041.498.580 bytes |
| SO final | `f87a5f6c9ef5bda4083f2bdf94eca49840e71aeed9da530c57549e3be0f10630` — 90.546.824 bytes |
| Base APK R19B | `c8fcb15f0951cf5874ac9de2fa2f2e9bfbe26813b7e9ddea5b897355cea4157c` |
| Base arquivada | `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-N64-Controles-R19B-20261005.apk` |
| Dados alterados no APK | Somente `lib/arm64-v8a/libturbo_carousel.so` |
| Preservação | 13.080 entradas conferidas individualmente; DEX, resources.arsc e motores iguais à R19B |
| Certificado | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| Alinhamento | 16 KiB conferido após assinatura |

`build-result.json` registra o instante do empacotamento; instalação posterior tem recibo próprio. Não declarar estável nem confundir prova de GPU no PC com aprovação no Android.

**Instalado por atualização em 05/10/2026**, hash do `base.apk` idêntico. Launcher retornou à `ESActivity` sem login. A captura local `screen-154420.png` mostrou a plataforma Mega Drive BR com a foto do console ao lado da sinopse. Os logs registraram navegação por plataformas, sem erro GL no recorte. Essa captura não certifica ainda o LED Neo Geo/CD no aparelho; validação adicional foi transferida ao chat coordenado junto com o ajuste de escopo acima.

## Causa das fotos ausentes

O código anterior embutia somente SNES e Mega Drive. Além disso, `native_info.h` zerava a chave nas plataformas/coleções e `native_console.h` recusava `systemsMode`. O servidor exporta o label da plataforma; não foi demonstrado defeito de download das fotos.

Agora cada tela entrega a chave correta:

1. Plataformas: label do item selecionado.
2. Coleções: `folderPlatform` do menu existente.
3. Jogos: label do catálogo do item selecionado.
4. `station_console_keys.h` liga labels e aliases explícitos à família local.
5. `stationInfoLayout` reserva coluna direita quando existe imagem e há espaço. Título e navegação permanecem no fluxo anterior.
6. A textura RGBA é enviada à GPU uma vez por família/contexto. O desenho preserva proporção, alfa e estados GL; não há requisição HTTP nem decoder de imagem em runtime.

Famílias nesta revisão: **SNES, Mega Drive, Nintendo 64, Neo Geo, Neo Geo CD, Naomi e Naomi 2**. Listas BR reutilizam o hardware correspondente. Não afirmar cobertura dos 50 mapeamentos históricos: plataformas fora dessas famílias ainda precisam de arte própria. Retrato ou área insuficiente conserva a largura de texto, sem foto.

As sete texturas 512×512 totalizam 7.340.032 bytes RGBA embutidos; uploads são feitos sob demanda, com máximo de sete texturas deste conjunto. Acrescentam cinco imagens em relação à base, sem adicionar processamento quando o frontend está escondido. Não houve medição de GPU/consumo no telefone nesta fase.

## LED das revistas Neo Geo

Fontes reais locais: `G:\Capas-TurboRama\Capas-TurboRama-NeoGeo\svcplus.png` e `G:\TURBORAMA\RetroBat\roms\neogeo\media\revista\aof.png`, 1024×1536. A arte de jogo Neo Geo CD independente não foi localizada; o label CD pode usar o mesmo modelo somente se a assinatura da imagem coincidir.

O modelo 3 entra antes dos modelos SNES/Mega/N64. A máscara medida cobre trilhos superiores, linhas COLLECTION, duas barras ARCADE, quatro lâmpadas circulares, trilhos laterais, linha do selo e pictogramas inferiores. Não recolore logotipos, texto, estrelas do selo ou efeitos da arte do jogo. Mantém as cores impressas de cada emissor.

O reconhecimento exige quatro amostras azuis, barra âmbar e separador escuro. Pontos refinados com leituras reais da GPU: `(240,14)`, `(790,14)`, `(34,406)`, `(991,406)`, âmbar `(942,125)` e separador `(512,208)`. Thresholds preservados. Foram conferidos original e textura 262×393. Imagens sem assinatura retornam intactas.

Há varredura luminosa e o mesmo brilho de contorno da arte usado nos modelos anteriores. A prova de zero pixels fora da moldura refere-se **somente ao LED**, isolando a varredura branca de contorno que é intencional e pode atuar na imagem. Não confundir essas duas medidas.

## LED do Neo Geo CD quadrado / vídeo

O PNG de referência é `_theme_inc\images\caratulas\neogeocd.png` do TURBORAMAx2, 1254×1254. O asset efetivo `turbo-system-videos/720-neogeocd.mp4` foi confirmado contra um frame real do vídeo incluído no aplicativo. Não foi substituído vídeo.

Mapa em coordenadas da arte: contorno azul/laranja, anéis das setas e quatro pictogramas inferiores. Indicadores/dots inferiores são explicitamente excluídos. O brilho usa curva suave sem criar blocos brancos saturados.

`native_system_video720.h` escolhe o shader apenas no card focado com o asset exato. Variantes sampler2D (quadro retido) e samplerExternalOES (vídeo) usam a mesma função. A matriz SurfaceTexture transforma a amostra de vídeo; a máscara segue UV canônico. O quadro retido continua bottom-first como na base. O shader usa **uma amostra de textura por pixel**. Mesmos players, cache, 30 fps e um draw; nenhuma camada/vídeo adicional. Sem efeito nos vizinhos, menus modais ou emulação escondendo frontend.

## Testes e limites

- 11.601 verificações de layout C++17: dimensões, retrato, falta de arte e limites; sem avisos.
- 52 verificações de chaves, aliases e seleção exclusiva do asset.
- 3.030 verificações da navegação R17 preservada.
- NDK r28c arm64/API26 compilado e linkado. Três avisos antigos de trigraph em sinopses foram conservados; nenhum aviso novo deste delta.
- ANGLE/RTX 2060 no PC: dez programas GLES100 compilados/linkados e 125 consultas sem erro GL.
- 18 renderizações dos modelos 0/1/2 idênticas byte a byte à W16; o corpo legado do shader permanece idêntico.
- Cinco controles sem assinatura intactos; assinatura Neo Geo >0,85 nas duas artes em resolução original e 262×393.
- LED isolado não altera pixels fora da moldura/margem medida; imagem quadrada preserva todos os dots, anima os quatro pictogramas e não cria pixels brancos saturados nos frames 0/60/120.
- OES e 2D produziram os mesmos pixels nas referências. O teste OES usa EGLImage no PC, não MediaPlayer Android.
- Instrumentação GLSL contou 15–20 leituras na revista, uma no quadrado; isso não mede cache/GPU/FPS do celular.

Relatório final: `evidence/led-final.json`. Prévias completas arquivadas, com todos os hashes, em `G:\BAKUP SISTEMA APP 03-10-2026\evidencias-visuais\station-console-neogeocd-r20-20261005\angle-20261005-153629`. `preview-archive.json` registra os caminhos anteriores e atuais. Não publicar capas privadas de jogos nem APK/ROM/BIOS em Git.

## Reconstrução

1. Ler este snapshot e a R19B. Manter sua base APK exata; não usar R18 nem o primeiro R19.
2. Base dos headers/objeto: `station-download-performance-20261005/frontend-native` (W16). Preservar `video720_posters.o`, `libc.so`, `libdl.so`, `liblog.so` e demais inputs.
3. Sobrepor todos os arquivos de `native/` desta revisão. `native_carousel.cpp`, `native_folders.h`, `native_n64.h` e `native_search_download.h` são bytes da R19; os recursos N64 corrigidos são herdados do APK R19B.
4. Se necessário, gerar `console_assets.h` a partir dos sete PNGs publicados com `generate_console_header.py`. Não depender da pasta de imagens temporárias da IA.
5. Executar receita de build nativo e testes em E:. Comando completo e hashes em `native-build.json`. A versão portable do teste GL está em `tests/angle/` e depende das artes privadas locais identificadas nos manifests.
6. Empacotar somente o SO com `package_console_led_r20.py`. Conferir SHA da base, de cada entrada preservada, certificado e alinhamento. A receita exige espaço para unsigned+signed.
7. Instalar via `adb install --no-incremental -r --user 0`. Só com frontend seguro, sem partida em outro processo. Não desinstalar, não limpar dados, não aplicar correção manual no telefone.
8. Conferir hash de `base.apk`, abrir pelo launcher público e registrar validação visual com estado explícito.

Recibos de espaço: APK R19B e SOs históricos R19B/W16 foram copiados para G:, hashes/tamanhos conferidos antes de remover somente duplicatas E:. Fontes, recursos N64 e objetos de ligação ficaram em E:. Os caminhos atuais estão em `r19b-archive.json` e `native-output-archives.json`.

## Origem das ilustrações dos consoles

SNES/Mega existentes foram mantidos. N64, Neo Geo e CD foram extraídos visualmente dos cards fornecidos usando **ImageGen integrado**; Naomi 1/2 usam como referência o hardware inferior esquerdo dos respectivos vídeos. São ilustrações derivadas por geração, não fotografias documentais. Os PNGs definitivos pertencem ao projeto em `assets/turbo-console/`; imagem fonte, transformação e hashes constam em `console-assets.json`.

Prompt usado para N64/Neo Geo/CD: isolar apenas console e controle da referência, preservar forma/material/perspectiva/marcações, remover fundo, piso, grade, bordas, legendas, setas, ícones e adaptador; objeto completo, margem transparente, iluminação neutra e alfa real. Para Naomi/Naomi2: isolar somente a caixa de hardware cinza do canto inferior esquerdo, preservando forma e logo; remover gabinete, disco, caixas, pedestal e fundo. Conversão posterior limitada a RGBA e redução proporcional para 512px.
