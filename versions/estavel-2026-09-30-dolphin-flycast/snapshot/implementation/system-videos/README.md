# Estado atual — playlist retrô integrada ao menu

Instalado em 2026-09-29T17:37:29.280278; Success e hash no aparelho confirmados.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-playlist-retro.apk
SHA256: 352d74708adacd4bb3e2e9edc428a4fca6c0836fb81ee4e512cf4b5fb511a049

Playlist de 18 faixas locais de Donkey Kong Country, Donkey Kong Country 2, Super Mario World e cinco faixas de Rock n’ Roll Racing. Encontradas em C:/Users/Admin/Music/LinkSom/SNES por pedido do mantenedor. MP3 originais preservados, sem downloads ou recodificação, 70,2 MiB. Não publicar as faixas em Git/serviços externos. Manifesto de fontes/hashes privado: retro-playlist/playlist-manifest.json; somente títulos e caminhos internos vão ao APK.

Um único player de áudio transmite uma faixa por vez, em ordem intercalada e repetição da lista. Guarda faixa/posição para retomar. Reutiliza o controle nativo MUSICA DE FUNDO/StoreMusic; ativa uma vez ao instalar a função (marcador RetroPlaylistReady) e respeita escolhas posteriores. Volume de fundo 32% do volume de mídia; botões de volume Android controlam a saída. A alteração solicitada de música não altera opções do emulador.

O WAV antigo é parado para evitar duas músicas simultâneas; efeitos de navegação permanecem. Suspensão antes de launchItem, callbacks de pausa da Activity, foco de áudio Android e ausência de heartbeat do menu interrompem/liberam o player. Sem UI Java/sobreposição; Java apenas reproduz áudio. Enquanto há emulação não se mantém o player decodificando ou watchdog periódico de música.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Novos: native_retro_music.h e system-videos/java/org/emulationstation/frontend/MenuRetroMusic.java. Integração em native_carousel.cpp: relocação verificada de GuiStore::updateMusic 0x2170d0 (GOT 0x3c1328), lançamento mantém a rota original. classes9.dex reúne helpers de vídeo/música, mantendo DEX originais da base.
Arquivos/ordem: retro-playlist/README.md e playlist-manifest.json; MP3 em retro-playlist/assets/.
Compilar: build_native.py; montar: system-videos/build_videos.py; instalar: system-videos/install_videos.py; registrar: retro-playlist/finalize.py.
Registros em system-videos/ e cópias em retro-playlist/. Fontes anteriores em retro-playlist/before/.
APK anterior: TurboramaStation-led-intenso.apk, SHA256 83e713ee772e7f543772342eab43122a03f38293e8e350932ee3ca9bdce5f630.

Preservados: LED intenso, quadro do vídeo retido ao retornar, pré-carga dos vizinhos, vídeos únicos 720p/loop 1x, voo diagonal, motor estável 1.0.8/6727ab7, jogos/saves e navegação. Sete plataformas ativas ainda não têm vídeo na pasta caratulas; não inventar substitutos.
Compilação, assinatura e instalação confirmadas. Não houve novo teste de reprodução, troca de faixa, volume ou pausa na emulação; não afirmar essas verificações nem aprovação do usuário. Ativação nativa da preferência ocorre na execução do menu e não foi lida de volta no aparelho.
Git estável preservado: commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira do TurboElden. Não publicado/promovido a estável. Backup criptografado anterior permanece pré-vídeos; gerador atualizado, não executado nesta entrega.

## Histórico substituído pelo estado acima

# Estado atual — LED intenso na célula em evidência

Instalado em 2026-09-29T17:23:55.455586; instalação Success e hash no aparelho confirmados.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-led-intenso.apk
SHA256: 83e713ee772e7f543772342eab43122a03f38293e8e350932ee3ca9bdce5f630

Pedido atendido no código: brilho do foco aumentado. Contorno com opacidade base 0,72 (antes 0,34), núcleo mais definido, ponto luminoso maior, halo de cor mais forte e cauda mais longa. Foco entra em 75% e chega a 100% em 120ms. Mantidas as cores exatas do usuário, percurso dos cantos e volta em 3,8s. Uma faixa nativa de 10 vértices, sem novas texturas, players ou passes. Centro do vídeo livre.

Preservados: cache do próprio quadro de vídeo ao voltar, pré-carga de até quatro anteriores/dois seguintes conforme capacidade, vídeos únicos 720p em loop 1x, LED por sistema, voo diagonal com nuvens/estrelas, motor estável 1.0.8/6727ab7, jogos, saves, configurações e regras de navegação. Detalhes e limites do vídeo continuam em video-ready-cache/ENTREGA.md; sete plataformas ativas continuam sem arquivo de vídeo na pasta indicada. Não inventar substitutos nem prometer que todos os 36 sistemas estejam decodificados no primeiro instante.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Alteração visual: premium-selection-laser-android.glsl e native_laser.h. prepare_laser.py incorpora o shader editável em laser_assets.h durante build_native.py.
Compilar: build_native.py; montar: system-videos/build_videos.py; instalar: system-videos/install_videos.py; registrar: led-brightness/finalize.py.
Detalhes: led-brightness/README.md. Fontes e registros anteriores: led-brightness/before/.
Registros atuais em system-videos/ e cópias em led-brightness/.
APK anterior: TurboramaStation-videos-retorno-pronto.apk, SHA256 bff401319cd120530ce429c7ca6415881acdcb0460e0eba6f8845c247ab07e41.

Compilação, assinatura e instalação confirmadas; sem nova conferência visual ou medição de FPS. Não afirmar aprovação do usuário. Atualização sem desinstalar, limpar dados ou alterar configurações.
Git estável preservado: commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira do TurboElden. Não publicado ou promovido a estável. Backup criptografado anterior permanece pré-vídeos; gerador atualizado, não executado nesta entrega.

## Histórico substituído pelo estado acima

# Estado atual — quadro do vídeo preservado ao voltar pelo carrossel

Instalado em 2026-09-29T17:17:23.624822; Success e hash do APK instalado confirmados.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-videos-retorno-pronto.apk
SHA256: bff401319cd120530ce429c7ca6415881acdcb0460e0eba6f8845c247ab07e41

Correção do quadro verde: um quadro 720x720 do próprio vídeo é retido na GPU quando fica pronto, sai de vista ou precisa liberar seu decodificador. O quadro sobrevive ao descarte do player enquanto o carrossel está aberto. Ao retornar, cada célula desenha a textura ao vivo OU seu quadro retido enquanto a reprodução retoma. Nenhuma foto, atlas ou segunda versão de vídeo foi adicionada. O player guarda a posição e busca essa posição antes de iniciar novamente. O fundo verde animado foi removido.

Pré-carga: até quatro anteriores e dois seguintes, conforme limite de 12 players e capacidade declarada do aparelho. Visíveis primeiro; anterior e seguinte imediatos; demais anteriores; próximo restante. Slots livres mantêm players já visitados pausados e preparados. O cache contém um quadro RGB565 por clipe visitado: 27 clipes existentes, ~26,7 MiB nominais de pixels, limite defensivo de 40 entradas. Não há cópia de pixels para CPU nem cópia contínua por quadro. Jogar/abrir outra tela libera os recursos; callbacks da Activity liberam players e a perda do contexto GL invalida texturas.

Limite real: vídeo nunca decodificado ainda precisa do carregamento inicial. Arquivos ausentes não viram vídeos. Não prometer que todos os 36 sistemas estão decodificados ao abrir nem que hardware abaixo da capacidade necessária reproduz todos simultaneamente. O quadro retido pode ficar parado durante a preparação; permanece sendo o próprio vídeo, sem substituição por fotos de capas.

Preservados: LED premium, nave/estrelas/nuvens na diagonal, cores explícitas, vídeo único 720p/60 codificados em loop 1x, fontes da pasta caratulas indicada, motor estável 1.0.8/6727ab7, login, ícone, navegação e regras dos jogos. Instalação sem desinstalar, limpar dados ou alterar configurações; jogos e saves preservados.

Ausentes na pasta de vídeos: Atari7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx (7 da lista ativa); sufami também ausente no mapa ampliado. Não inventar substitutos. 27 clipes cobrem 32 chaves / 29 plataformas ativas.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Alterados: native_system_video720.h, native_system_video.h, native_formation.h e system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java.
Diagnóstico e detalhes: video-ready-cache/README.md. Fontes e registros anteriores: video-ready-cache/before/.
Montagem: build_native.py; system-videos/build_videos.py. Instalação: system-videos/install_videos.py. Registro: video-ready-cache/finalize.py.
Registros desta entrega em system-videos/ e cópias em video-ready-cache/.
APK anterior: TurboramaStation-led-premium-diagonal.apk, SHA256 3b8bb1fb0f25a40665d7bc6031228c0049d7595022146f940e371a793c01e3fa.

Compilação, assinatura e instalação confirmadas. Diagnóstico leu logs existentes, que mostraram vídeos reabrindo. Não foi feito teste de arraste ou medição de latência após a correção; não afirmar validação visual ou aprovação do usuário.
Git estável preservado: TurboElden commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira. Esta revisão não foi publicada/promovida a estável. Backup criptografado anterior continua pré-vídeos; gerador atualizado, não executado nesta entrega.

## Histórico substituído pelo estado acima

# Estado atual — LED premium e voo diagonal integrado

Instalado em 2026-09-29T17:05:26.689695; instalação Success e SHA256 no aparelho confirmados.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-led-premium-diagonal.apk
SHA256: 3b8bb1fb0f25a40665d7bc6031228c0049d7595022146f940e371a793c01e3fa

LED nativo da célula principal: linha fina, núcleo luminoso, cauda gradual e halo externo suave. Percurso por comprimento real dos cantos arredondados, com volta em 3,8s e movimento contínuo entre seleções. Uma faixa geométrica de 10 vértices; sem textura/vídeo adicional, framebuffer ou blur extra. Centro do vídeo livre. Paleta explícita do usuário preservada, incluindo Switch azul/vermelho e CPS2 amarelo/azul. Jogos continuam com cantos retos.

Voo: corrigido sinal da guinada na câmera traseira, que virava o nariz contra o deslocamento lateral. Nave, estrelas e nuvens usam uma inclinação diagonal comum de 0,50 rad (~28,65 graus), ponto de fuga (0,84; 0,20), e avanço constante. Projeção das estrelas compartilha focal 2,9 e avanço 0,9 unidades/s com as nuvens. Profundidade relativa moderada; aproximação e afastamento alinhados ao ponto de fuga. Nave inteira e escape rotacionados juntos sem esticar. Vista por trás, curvas e turbina volumétrica preservadas. Sem rajadas de aceleração.

Pré-carga anterior preservada: dois cartões anteriores e dois seguintes ao intervalo visível preparados conforme capacidade declarada do aparelho, limite de 12 clipes únicos; prioridade dos visíveis e anteriores. Fora da tela ficam pausados com textura/quadro, retomam a mesma instância e são liberados fora da vizinhança, ao abrir emulação/modal ou pausar a Activity. Não afirmar cache de todos os sistemas.

Vídeos únicos 720p/60 codificados em velocidade normal 1x, loop nativo. Só fontes da pasta caratulas indicada pelo usuário; sem atlas ou segunda reprodução. 27 clipes cobrem 32 chaves, 29 das 36 plataformas ativas. Continuam sem vídeo: Atari7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx; sufami também não tem fonte no mapa ampliado. A resposta SIM não identificou arquivos; não inventar substitutos.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
LED: premium-selection-laser-android.glsl (agora fonte editável), native_laser.h, prepare_laser.py e laser-user-overrides.json. build_native.py gera laser_assets.h automaticamente.
Voo/atmosfera: native_flight.h, native_space.h, native_space3d.h e space3d/clouds.frag; escape continua em space3d/plume.frag.
Detalhes e cópias anteriores: premium-led/README.md e premium-led/before/.
Compilar: build_native.py; montar: system-videos/build_videos.py; instalar: system-videos/install_videos.py; finalizar: premium-led/finalize.py.
Registros atuais em system-videos/ e cópias em premium-led/.
APK imediatamente anterior: TurboramaStation-nave-video-cache.apk, SHA256 d7bf29b5c5498d948994cc4d2ce9e6e9ce3647b8e4d9eac4651823d5a39c30e6.

Motor estável 1.0.8/6727ab7, DEX originais, login, ícone, catálogo, navegação e regras de jogos/saves preservados. Apenas a biblioteca visual nativa e os acréscimos de vídeos já existentes diferem da base congelada. Instalado sem desinstalar, limpar dados ou alterar configurações.
Não houve teste visual novo ou medição de FPS/latência; não afirmar aprovação visual, desempenho medido ou resolução perceptiva confirmada.
Git estável preservado: TurboElden commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira. Esta revisão não foi publicada nem promovida a estável. Backup criptografado anterior continua pré-vídeos; gerador atualizado, não executado nesta entrega.

## Histórico substituído pelo estado acima

# Estado atual — nave com profundidade e vídeos vizinhos preparados

Instalado em 2026-09-29T16:56:44.582074; Success e hash do APK no celular confirmados.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-nave-video-cache.apk
SHA256: d7bf29b5c5498d948994cc4d2ce9e6e9ce3647b8e4d9eac4651823d5a39c30e6

Pedidos incorporados: a nave percorre a tela em curvas, aproxima-se/afasta-se com translação 3D e variação de tamanho em perspectiva. Inclinação acompanha as curvas e o motor tem resposta gradual. Escape com bordas difusas, turbulência transportada, cauda irregular e menor opacidade. A nave usa alvo de 60Hz, a atmosfera mantém 30Hz e velocidade constante. Detalhes em flight-cinematic/README.md.

Dois cartões anteriores e dois seguintes ao intervalo visível ficam preparados quando a capacidade do aparelho permite; prioridade para os visíveis e os anteriores. Fora da tela, pausam mantendo player, textura e primeiro quadro. Ao voltarem, retomam a mesma instância sem reabrir arquivo, preparar codec ou reiniciar. Limite de 12 clipes únicos, conforme capacidade declarada. Libera fora da janela de vizinhança, ao abrir jogos/configuração modal ou pausar Activity. Não afirmar cache de todos os 36 sistemas.

Preservados: vídeo único 720p/60 codificados em velocidade normal 1× e loop; fontes exclusivamente da pasta caratulas indicada; paleta exata do usuário (inclui Switch azul/vermelho e CPS2 amarelo/azul); navegação, motor estável, jogos/saves/configurações. Não há atlas nem segunda versão de vídeo.

Continuam ausentes sete vídeos da lista ativa de 36: Atari7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx. Sufami também não tem arquivo no mapa ampliado. Não inventar ou usar vídeo de outra pasta sem nova instrução. 27 clipes atendem 32 chaves (29 ativas).

Compilação/assinatura e instalação confirmadas. Não houve novo teste visual, benchmark de FPS ou medição de latência nesta entrega. Aparência e fluidez precisam de conferência no aparelho; não afirmar aprovação do usuário.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Voo/escape: native_flight.h, native_space3d.h e space3d/scene-common.glsl + plume.frag.
Cache: native_system_video720.h e system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java.
Montar: build_native.py e system-videos/build_videos.py.
Instalar: system-videos/install_videos.py, preserva dados e recusa emulação ativa.
Finalizar: flight-cinematic/finalize.py. Registros: system-videos/build-result.json e installed.json, copiados em flight-cinematic/.
Fontes anteriores em flight-cinematic/before. APK imediatamente anterior: TurboramaStation-videos-720-unico.apk, SHA256 6cbbb5d4203c2bb4c525a11861bb530ff2fd92805869169d3e185d8837c97e3c.

Estável Git preservada: TurboElden, commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira. Motor 1.0.8/6727ab7 intocado. APK congelado em E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira. Esta entrega não foi publicada ou promovida a estável. O backup criptografado anterior ainda não inclui estas revisões, embora seu gerador esteja atualizado.

## Histórico substituído pelo estado acima

# Estado atual — vídeo único 720p, velocidade normal, cores do usuário

Instalação confirmada em 2026-09-29T16:42:14.495659; Success e hash do APK no aparelho conferido.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-videos-720-unico.apk
SHA256: 6cbbb5d4203c2bb4c525a11861bb530ff2fd92805869169d3e185d8837c97e3c

Somente um vídeo 720p por célula. Loop nativo do Android, velocidade 1.0, pitch 1.0. Arquivos convertidos a 60fps preservando a duração e velocidade originais; quadros repetidos quando a fonte tem taxa inferior. Não afirmar 60fps sustentados nem movimento novo.

O atlas, a versão leve, a camada duplicada e a implementação manual de EOF/timestamps foram retirados do APK. MediaPlayer prepara de forma assíncrona e controla a repetição do mesmo arquivo. Apenas clipes visíveis ficam ativos; liberados ao sair, entrar nos jogos ou abrir modal. Diagnóstico anterior mostrou duas reproduções ativas; não reintroduzir essa arquitetura rejeitada.

Usar EXCLUSIVAMENTE os vídeos de G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas. Foram encontrados 27 vídeos aplicáveis / 32 chaves, 29 das 36 plataformas ativas. Ausentes: Atari7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx; sufami também está sem arquivo no mapa ampliado, mas não na lista ativa de 36. Não há fotos animadas ou vídeos de outra pasta no APK. A resposta "SIM" do usuário não forneceu os arquivos faltantes; isso permanece pendente. Manter os sistemas no catálogo, sem inventar vídeos.

LED conforme ordem explícita: PSP azul; Switch azul/vermelho; Wii branco; Atari marrom; Atomiswave verde; CPS1 verde; CPS2 amarelo/azul; CPS3 azul; Dreamcast laranja; GBA roxo; MAME/Arcade azul; Master System vermelho; Nintendo64 amarelo; NDS branco. Outros mantêm cores do tema. Fonte da regra: laser-user-overrides.json. Duas cores são aplicadas no contorno esquerdo/direito, sem trocar o vídeo.

Motores/DEX originais/login/ícone idênticos à base estável congelada. Jogos, saves, configurações e nave preservados. Sem novo teste visual, de loop ou benchmark no aparelho após esta correção; compilar/instalar não prova esses resultados.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Preparar vídeos: system-videos/prepare_720.py (restringe à pasta indicada).
Gerar cores: prepare_laser.py (aplica overrides do usuário).
Compilar: build_native.py; empacotar: system-videos/build_videos.py.
Instalar: system-videos/install_videos.py, recusa emulação ativa.
Detalhes: system-videos/CORRECAO-VIDEO-UNICO.md e CORES-SOLICITADAS.md.
Registros: system-videos/build-result.json e installed.json.

Git estável intocado: TurboElden, commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira; motor 1.0.8/6727ab7. APK de retorno privado em E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira. Esta correção não foi publicada ou promovida a estável. Revisão duplicada rejeitada preservada em system-videos/revisions/720-dual-rejected.

O backup criptografado anterior ainda é pré-vídeos; seu gerador foi atualizado com novos fontes/paleta, mas não foi executado novamente.

## Histórico substituído

# Entrega atual: vídeos 720p/60 e brilho por sistema

Instalada em 2026-09-29T16:25:02.645281, com Success e hash do APK instalado confirmado.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-videos-720p60.apk
SHA256: 81ccb3c681469e77fccfb1a9ebc9e842eef81aebd46a92b0c30c507dce3d3bad

35 vídeos individuais 720 × 720 / 60fps para todas as células visíveis. Hardware-only MediaCodec, até oito streams visíveis, limite consultado no aparelho e atlas leve preservado durante preparação/falta de recursos. Vídeos de fonte com menos quadros repetem quadros ao converter para 60fps; não afirmar 60 movimentos diferentes por segundo. Cinco vídeos continuam sendo animações da arte, documentadas no manifesto.

Brilho da célula principal conforme mapa real do tema: 45 chaves, cor saturada, contorno/halo mais vivo, desenhado acima dos vídeos. Sem alterar posição/movimento da nave desta rodada, motores, DEX originais, login, ícone ou dados. Sem benchmark nem conferência visual desta entrega; não afirmar FPS sustentado ou aprovação do usuário. Detalhes em QUALIDADE-720P60.md.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
Preparação: system-videos/prepare_720.py, prepare_laser.py, build_native.py, system-videos/build_videos.py. Reprodução: native_system_video720.h + system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java. Instalar: system-videos/install_videos.py (recusa emulação ativa). Registros: system-videos/build-result.json e installed.json.

Git estável intacto: TurboElden, commit 95d244bcea95647236bea335c41b46afe15674bf, tag estavel-2026-09-29-camera-traseira. Referência privada congelada em E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira. Esta revisão não foi publicada/promovida a estável. Motor 1.0.8/6727ab7 permanece byte a byte idêntico.

Revisão anterior de atlas: TurboramaStation-videos-todas-celulas.apk / 215ae541d61cc0e411ef1452639e0714db2014f8c31319dee6aad1b24df336ee. Registros anteriores em revisions/atlas-18fps. O último backup criptografado é anterior aos vídeos; o script de backup foi atualizado, mas não foi executado novamente nesta entrega.

## Histórico anterior — substituído pelo estado acima

## Entrega instalada

E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-videos-todas-celulas.apk

SHA256 `215ae541d61cc0e411ef1452639e0714db2014f8c31319dee6aad1b24df336ee`. Instalação confirmada em 2026-09-29T16:13:13.153287. Sem conferência visual ou benchmark.

# Vídeos simultâneos no carrossel nativo

## Pedido atual

Todas as células de plataformas visíveis reproduzem em loop, inclusive as laterais e durante a troca de seleção. Usa o carrossel nativo e suas ações reais. Fotos de jogos continuam como antes.

## Implementação

- 40 identificadores existentes mapeados para 35 clipes. O catálogo continua decidindo quais plataformas existem; este mapa não adiciona plataformas.
- Atlas 7 x 5: um único vídeo combinado decodificado em uma SurfaceTexture externa. O desenho de cada célula nativa recorta o quadrado correspondente, conservando cantos arredondados, toque e destaque luminoso.
- Loop de 24 segundos, silencioso, 18 fps. Versão HD 1680 x 1200 e leve 1120 x 800, escolhidas por capacidade de decodificação e indicador de pouca memória. O MediaPlayer seleciona o decoder; a disponibilidade de hardware é consultada previamente.
- Preparação assíncrona. Nenhuma leitura de arquivo ou cópia de bitmap por quadro. O stream não reinicia a cada seleção.
- Interrompe ao entrar nos jogos, abrir modal ou pausar/sair da Activity; libera player e superfícies. Portanto o atlas não permanece decodificando durante emulação.
- Enquanto prepara, mostra gradiente verde animado, sem substituir as células por fotos. Falhas são registradas e há retentativa espaçada. Aparelhos sem suporte adequado podem permanecer nesse estado: não prometer compatibilidade universal nem ausência de travamentos.
- Cinco sistemas não tinham MP4 correspondente nos dois temas pesquisados: gamegear, jaguar, pcenginecd, sufami e supergrafx. Seus clipes usam movimento de câmera sobre a arte correta. Não são filmagens originais do tema; origem e hashes estão em videos-manifest.json.

## Nave

Câmera traseira elevada para mostrar as asas; marca TURBORAMA maior e separada em cada asa. Deslocamento diagonal suave guiado pelo mesmo comando da inclinação. Centro mais abaixo na região inferior da sinopse; sem órbita, teleporte ou aceleração das nuvens/estrelas.

## Pastas e montagem

- Fontes: E:\ESTUDO APK\work\native-carousel\implementation
- Originais: G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas; vídeos complementares em _theme_inc/videos/tela1.
- Atlas: system-videos/assets/atlas-hd.mp4 e atlas-lite.mp4.
- Preparar: C:\Python314\python.exe system-videos/prepare_atlas.py.
- Compilar: C:\Python314\python.exe build_native.py.
- Empacotar sobre o APK estável congelado: C:\Python314\python.exe system-videos/build_videos.py.
- Instalar preservando dados: C:\Python314\python.exe system-videos/install_videos.py; recusa emulação ativa.
- Entrega: TurboramaStation-videos-todas-celulas.apk. Hash e integridade em build-result.json, instalação em installed.json. Sem prova visual ou medição de desempenho até haver registro específico.
- A tentativa anterior focada só na célula central foi rejeitada e está documentada em revisions/focus-only; não usá-la como conclusão deste pedido.

## Estável preservada

Git TurboElden, commit 95d244bcea95647236bea335c41b46afe15674bf; ramo estavel e tag estavel-2026-09-29-camera-traseira. Motor histórico 1.0.8/6727ab7. APK congelado em E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira. Esta revisão de vídeos NÃO move essa tag.

## Referências técnicas

- https://developer.android.com/reference/android/graphics/SurfaceTexture
- https://developer.android.com/media/platform/mediaplayer/state-resources
- https://developer.android.com/reference/android/media/MediaCodecInfo
