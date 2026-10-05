# Histórico R13 — substituído pela R14

R13 foi instalado e teve hash conferido em 05/10. A geometria larga foi rejeitada pelo mantenedor e corrigida na [R14](../station-visual-r14-20261005/README.md): células originais quadradas, vídeo inteiro com fundo derivado. Não reconstruir R13 como revisão atual. APK R13 agora arquivado em G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais. Vídeos privados não são publicados no Git; apenas caminhos, filtros, fontes e hashes.

# R13 — coleções em vídeo, sem faixas ou nomes sobre as células

Pedido do mantenedor em 05/10/2026: aplicar a todos os sistemas o fluxo plataforma → Todos os jogos e coleções → jogos da seleção. Remover a faixa preta e o texto sobre cada célula. Usar os vídeos de `C:\Users\Admin\Videos\New folder`; Todos os jogos usa exatamente o vídeo da plataforma principal.

## Mudanças delimitadas

- Removidos a criação e o desenho de `folderLabels` e sua faixa de fundo. O título/sinopse na área de informação permanecem, sem texto novo por cima do vídeo. Os textos que já fazem parte da arte dos vídeos fornecidos não são apagados.
- Carrossel nativo de coleções agora funciona também em plataformas sem subpastas: há a célula Todos os jogos. Subpastas reais continuam vindo do catálogo assinado, por `folderPath`; não foram criadas pastas ou listas fictícias.
- `Todos os jogos` resolve o mesmo asset da plataforma em `systemVideo720Definitions`, sem duplicar vídeo. A entrada no menu de coleções conserva esse player quando é o mesmo vídeo, evitando reiniciar sua preparação.
- Habilitado o mesmo player nativo nas coleções. Apenas a célula principal reproduz, em loop e velocidade1× a30FPS. Laterais usam quadros reais dos vídeos; política de players aquecidos, cache limitado, pausa em configurações/segundo plano/jogo permanecem.
- Cinco vídeos próprios do SNES. Preservados todos os frames na duração original, com conversão para30FPS, sem áudio da trilha concorrendo com o menu. Não há faixa preta adicionada, crop de conteúdo ou nomes sobrepostos. Sampling interno720×720 segue o cache existente; geometria da célula restaura a proporção original16:9 ou1:1. Portanto, vídeos paisagem aparecem em células paisagem e Mario permanece quadrado; isso evita esticar ou cortar a arte.
- Coleções sem vídeo próprio usam o vídeo da plataforma. Nesta pasta não há Final Fight nem Mega Man; não atribuir a elas vídeo de outro jogo. O mecanismo de coleções é geral, mas esses cinco clips estão associados apenas a Super Nintendo e Super Nintendo BR.

## Mapeamento comprovado

Nomes de folderPath conferidos no TSV `docs/station-android/biblioteca-20261004/catalogo-completo.tsv` do servidor4e623bc. O componente usa o nome da folha e só ignora espaços/# externos na correspondência de arte; não renomeia o catálogo nem muda a seleção de jogos.

| Folha da coleção | Arquivo fornecido | Asset novo | Proporção |
|---|---|---|---|
| ## BOMBER MAN ## | ## BOMBER MAN ##.mp4 | 720-collection-snes-bomberman.mp4 | 16:9 |
| ## DONKEY KONG ## | ## DONKEY KONG ##.mp4 | 720-collection-snes-donkeykong.mp4 | 16:9 |
| ## SUPER MARIO ## | ## SUPER MARIO ##.mp4 | 720-collection-snes-mario.mp4 | 1:1 |
| ## TOP GEAR ## | ## TOP GEAR ##.mp4 | 720-collection-snes-topgear.mp4 | 16:9 |
| ## 1 -PT-BR ## | 1 -PT-BR.mp4 | 720-collection-snes-ptbr.mp4 | 16:9 |

Todos sob `assets/turbo-system-videos/`, sem compressão ZIP, porque MediaPlayer usa asset file descriptor. Os originais de C: não foram modificados. `media-manifest.json` registra originais, hashes, derivados, previews e proporções.

## Fontes e reconstrução

Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004\native`.
Build/backup/mídia/testes: `E:\ESTUDO APK\work\station-netplay-20261004\collection-video-r13`.

Arquivos: `native_folders.h` (navegação e resolução de arte), `collection_video_policy.h` (cinco correspondências/proporção), `native_formation.h` (geometria e remoção de labels), `native_info.h` (remoção de textos nas células), `native_carousel.cpp` (pausa não interrompe coleções), `native_system_video720.h` (vídeos das coleções e capacidade de previews), `video720_posters.h` (cinco primeiros frames adicionais).

`implement_collection_video_r13.py` é aplicação inicial com backup e guardas; não repetir em árvore já alterada. `build_test_collection_video_r13.py` compila testes e renderer real com arte original; liga explicitamente o objeto anterior `before/video720_posters.o` e `collection_previews.o`, reproduzindo a ordem usada no APK R13. Para os builders genéricos, o objeto canônico `native/video720_posters.o` também foi consolidado com os cinco previews novos; essa ligação equivalente pode alterar o layout/hash do ELF, sem alteração do código-fonte. Para reconstruí-lo, gerar RGB565720×720 bottom-up do primeiro frame de cada MP4 fornecido na entrega, montar `collection_previews.S` com os caminhos reais e compilar pelo mesmo clang do script; combinar o objeto adicional com o objeto anterior guardado em `before/video720_posters.o` usando `ld.lld -r`, conforme o script de implementação. Não combinar uma segunda vez com um objeto já consolidado. Nenhuma imagem sintética entra no APK.

`package_collection_video_r13.py` parte do APK R12 exato SHA2567684c6eee87985d8259becca9a22a9f4c7e3203f7c097df37da6998975596514. Arquiva R12 em G: conferindo hash antes de remover apenas sua duplicata de E:. Substitui somente libturbo_carousel.so, adiciona cinco MP4s, assina com o certificado original e alinha16KiB. Faz comparação SHA256 de todas as entradas. R12/salas/internet/classes35, motores e demais recursos devem permanecer byte a byte. Não aplicar package_delta.py do retornoNeoGeo com R11 por cima desta revisão.

## Testes e estado

443 verificações da navegação real compilada (IDs/índices originais, raiz, Todos, subpastas, Voltar, catálogo vazio/plano e200atualizações) e105 da correspondência/proporção passaram. Remoção do desenhador de labels conferida. Renderer Android26arm64 compilado. Três warnings de trigraph já existentes nos textos de sinopse, sem erro de compilação; não se referem a este transporte/mídia.

Estado de APK/instalação: consultar evidence/build-result.json e eventual installation.json. Não alegar vídeo/renderização/toque conferidos no telefone sem recibo próprio. R12 foi instalado e seu carrossel observado; a USB caiu durante a continuação da conferência. Tag estável não alterada.

O servidor não precisa de nova rota, schema, importação ou implantação para esses vídeos. Netplay internet entregue em paralelo ao operador no Servidor-pix, branch feat/station-netplay-internet-r12-20261005 / commitd358e5f4d127a607bdf0c1ce3e4f4c2b4eaa7504, segue aguardando publicação e partida real em duas redes. RetornoNeoGeo/taxa c8e240a foi preservado no Git; sua taxa MB/s não faz parte deste delta visual.
