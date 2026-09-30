# Arcade, Final Burn Neo e MAME — atualização 30/09/2026

APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk
SHA256: 1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7
Base preservada: F:\Turborama-build-archive\TurboramaStation-videos-br-544fdecb.apk / 544fdecbc512a128827b392dcc96461573db9a16c09dc343bc3d958749980b81
Instalação concluída com Success e hash do APK no telefone conferido em installed.json. Dados preservados. Reprodução visual ainda não conferida após a atualização.

## Mudanças

- Arcade: corrigido mapeamento que usava MAME; agora usa ARCADE.mp4 da pasta caratulas indicada.
- Final Burn Neo: fbneo.mp4 recomposto no asset720-fbneo.mp4.
- MAME: mame.mp4 recomposto no asset720-mame.mp4.
- Todos convertidos a720x720/30fps, H264 baseline, duração original preservada à precisão de um quadro, sem áudio, velocidade1x e loop. Mantida reprodução somente na célula principal.
- Limite de prévias: native_system_video720.h tinha40 registros fixos; após esgotar, video720CanStart recusava novas mídias. Agora a capacidade acompanha o número de entradas do mapa (44 nesta revisão), que é um limite superior dos vídeos únicos. Texturas continuam criadas sob demanda; número de players e renderização permanecem iguais. A causa foi identificada por leitura do código, não reproduzida em ensaio no aparelho.
- Vídeos BR/NDS/Game Gear anteriores, catálogo, todos os DEX, motores e login preservados e comparados com a base. Não implementa login do servidor. Não altera PS2.

## Fontes e recuperação

Fontes ativos: pasta pai, system_video720_assets.h e native_system_video720.h. Mapas anteriores nesta pasta com sufixo.before.h. Receita update_videos.py exige hash544fdecb como entrada e ferramentas emE. Temporários compilados emE.

O módulo compilado da revisão anterior foi arquivado em F:/Turborama-build-archive/libturbo_carousel-videos-br-df579112.so para liberar espaço emE; também continua contido integralmente no APK de recuperação544fdecb. Não confundir com o novo módulo a302bddd desta pasta.

build-result.json documenta a comparação de entradas e os hashes de origem/saída de cada vídeo. Para restaurar, atualizar com o APK-base preservado, sem desinstalar ou limpar dados. Estável78accf4c/tag05dd34b permanece preservada.
