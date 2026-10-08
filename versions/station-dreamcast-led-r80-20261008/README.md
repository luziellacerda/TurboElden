# Dreamcast — backup de efeito para uso futuro

**Estado posterior confirmado pelo mantenedor:** as capas do aplicativo são diferentes desta referência. O usuário pediu guardar o efeito pronto como backup para quando decidir usar esse estilo. Arquivado; não incorporar automaticamente ao próximo APK. As medições abaixo validam somente as 26 artes locais usadas na preparação.

Pedido do mantenedor: mapear a arte das capas do Dreamcast e aplicar o mesmo movimento LED usado nos jogos do Super Nintendo enquanto o servidor prepara o multiplayer.

## Entrega

O perfil Dreamcast foi implementado e a biblioteca ARM64 foi compilada. Não foi gerado nem instalado outro APK nesta etapa. Os dois instaladores atuais continuam R76 (referência de dois jogadores) e R79 (teste de até quatro), no backup único indicado por `release-channels/ACTIVE.json`.

Este perfil é uma referência para uso futuro mediante novo pedido e conferência das capas. Não sobrescrever os APKs existentes nem recuperar receitas antigas para montá-lo. A dependência de ativação/perfis multiplayer v3 continua conforme o handoff R79; o efeito não altera a conexão.

## Mapeamento e comportamento

- Perfil específico Dreamcast, reconhecido pela chave da plataforma sem depender de maiúsculas/minúsculas.
- Coordenadas da arte original 1024 × 1536: seis barras laterais, lâmpadas dos cantos, duas barras do cabeçalho, indicador laranja e lâmpadas/ícones do rodapé.
- Máscara geométrica combinada com a cor dos pixels. Azul e laranja da moldura são preservados; títulos, espirais e ilustração central ficam fora do efeito.
- Reconhecimento da moldura por quatro barras azuis, luz laranja, separador escuro e chassi branco. Uma capa sem essa moldura permanece intacta.
- Mesmo movimento, velocidade, cauda e halo de 2/5 pixels de referência do SNES, usando o relógio existente.
- Somente a capa selecionada na lista de jogos. Guardas de plataformas, coleções, vídeos e modais foram preservadas.
- Sem novas threads, decodificadores, leitura de tela para CPU, textura auxiliar ou ciclo de renderização. A política de 30 fps dos menus/15 fps em diálogo parado permanece intacta. O jogo emulado não usa essa política de menu.

## Evidências

Foram medidos os 26 PNG locais de Dreamcast em `G:\TURBORAMA\RetroBat\roms\dreamcast\media\images`, incluindo a textura reduzida BOX 262 × 393. São 26 artes locais, não uma auditoria das 243 capas do catálogo remoto.

Os testes executam o GLSL pelo ANGLE no PC. O contexto solicitado é GLES2, com shaders GLSL ES 1.00; o driver informa OpenGL ES 3.0. Isso não comprova desempenho térmico nem aparência em um GPU Android.

- 52 combinações de capa/resolução com animação; assinatura da moldura reconhecida integralmente.
- Nenhum pixel da área central do jogo ou fora da máscara ampliada do halo modificado; alpha preservado.
- 90 comparações dos perfis SNES/Mega Drive/N64/Neo Geo iguais byte a byte à R79.
- 24 controles sem moldura preservados; 126 comparações do movimento iguais ao SNES; 12 verificações de alpha/tint com erro máximo de arredondamento de 1/255.
- O carrossel R79 foi reproduzido byte a byte antes de compilar a mudança. Ver `evidence/build.json` e os recibos ANGLE.

## Fontes e compilação

Entradas canônicas: `test-up-to-4-players-r79/carousel-inputs` do backup único. Somente `native_magazine.h`, `premium-magazine-led-android.glsl` e o header GLSL correspondente mudam. `native/dreamcast_led.glsl` contém o trecho autoral do novo perfil; `recipes/prepare.py` recompõe os três arquivos a partir da base exata.

Trabalho/saída: `E:\ESTUDO APK\work\station-dreamcast-led-r80-20261008`.
Biblioteca: `libturbo_carousel-dreamcast.so`, SHA-256 `bfd8601f1c44e80dac0f30c345ab02c40a4f971e3ce206eb98b12afc117e1f3e`.

`recipes/build.py` confere as entradas congeladas, recompila o baseline quando necessário e compila o candidato. Não altera Java, motores, manifestos, controles, saves, cadastro de engines, assinatura ou servidor.

As prévias são leituras reais da GPU, armazenadas localmente em E:. Nenhuma capa, ROM, BIOS, imagem privada ou APK faz parte desta entrega Git.
