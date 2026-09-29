# Playlist retrô do menu — 29/09/2026

Pedido: músicas de Donkey Kong, Super Mario e Rock n’ Roll Racing em playlist. O usuário informou que já estavam neste computador e pediu para procurar. Encontradas em C:/Users/Admin/Music/LinkSom/SNES. Usados 18 MP3 originais, sem downloads, conversão ou alteração de velocidade. Fontes/hashes em playlist-manifest.json; somente títulos e caminhos internos entram no manifesto do APK.

## Funcionamento

Um único MediaPlayer de áudio, separado dos decodificadores dos vídeos, lê cada arquivo como fluxo. Ordem intercalada abaixo; ao terminar volta à primeira faixa. Não muda a música a cada troca de plataforma. Guarda faixa e posição ao sair e retoma ao voltar. Volume de fundo inicial 32% do volume de mídia; botões de volume do Android controlam a saída.

Reutiliza a opção nativa MUSICA DE FUNDO (StoreMusic) para ligar/desligar. Ativada uma única vez na primeira execução desta função, conforme pedido, marcada por RetroPlaylistReady; escolhas posteriores do usuário são respeitadas. As opções do emulador não mudam.

Hook verificado por símbolos/relocação do binário base: GuiStore::updateMusic em 0x2170d0 / GOT 0x3c1328. O WAV antigo em GuiStore+0x230 é parado apenas para evitar música simultânea; efeitos sonoros de navegação continuam originais. Não há UI Java ou sobreposição nova.

Entrada em jogo chama suspensão antes da rota original de launchItem. Activity pausada libera player/foco; perda do foco de áudio pausa ou encerra conforme Android. Um heartbeat do menu também libera o áudio se GuiStore parar de atualizar. Durante a emulação não fica player decodificando nem temporizador periódico de música. Não afirmar consumo zero absoluto ou desempenho medido.

## Reprodução e publicação

Arquivos foram fornecidos localmente pelo mantenedor para esta edição privada. Não publicar as faixas em Git ou serviços externos. Não foram pesquisados nem baixados arquivos de terceiros.

## Compilação

Fontes: native_retro_music.h, native_carousel.cpp e system-videos/java/org/emulationstation/frontend/MenuRetroMusic.java. O mesmo classes9.dex contém o helper de vídeo existente e o novo helper de música; DEX originais da base não são alterados.
Compilar: build_native.py; montar: system-videos/build_videos.py; instalar: system-videos/install_videos.py; registrar: retro-playlist/finalize.py.
APK: TurboramaStation-playlist-retro.apk.
Anterior: TurboramaStation-led-intenso.apk, SHA256 83e713ee772e7f543772342eab43122a03f38293e8e350932ee3ca9bdce5f630.

Preservar motor estável, LED intenso, cache de vídeos ao retornar, nave diagonal e jogos/saves. Compilação/instalação não equivalem a teste de reprodução, pausa ou volume no aparelho.

## Ordem da playlist

1. Donkey Kong Country — Title Theme
2. Super Mario World — Overworld
3. Rock n’ Roll Racing — Bad to the Bone
4. Donkey Kong Country 2 — Brambles
5. Super Mario World — Athletic
6. Rock n’ Roll Racing — Paranoid
7. Donkey Kong Country 2 — Enchanted Wood
8. Super Mario World — Swimming
9. Rock n’ Roll Racing — Highway Star
10. Donkey Kong Country 2 — Ship Deck
11. Super Mario World — Underground
12. Rock n’ Roll Racing — Peter Gunn
13. Donkey Kong Country 2 — Mine
14. Super Mario World — Special World
15. Rock n’ Roll Racing — Born to Be Wild
16. Donkey Kong Country 2 — Swamp
17. Super Mario World — Title
18. Donkey Kong Country 2 — Jungle
