# Retorno do carrossel sem descarte visual do vídeo

## Diagnóstico de 29/09/2026

Os registros existentes mostram capacidade declarada de 12 players. O 3DS foi preparado repetidamente às 17:07:52, 17:07:54, 17:07:55 e novamente às 17:08:02, 17:08:04, 17:08:06 e 17:08:08. O código descartava a textura ao sair da janela de dois vizinhos e desenhava um gradiente verde enquanto a preparação assíncrona não terminava. A consulta leu registros existentes; não executou navegação nem teste de arraste.

## Correção

- Retém um quadro decodificado do próprio MP4 em textura 720x720 RGB565 quando o vídeo fica pronto, sai de vista ou precisa ceder seu player. Mantém esse quadro mesmo após a liberação do decodificador.
- Ao voltar, a célula usa exclusivamente a textura do vídeo ao vivo, se pronta, ou seu quadro retido até a retomada. Não há fotos empacotadas, atlas, segunda versão de vídeo ou duas camadas de reprodução.
- Até quatro vizinhos anteriores e dois seguintes entram na pré-carga conforme os slots disponíveis. Visíveis vêm primeiro; anterior e seguinte imediatos precedem os demais. Slots que sobram mantêm players já visitados preparados e pausados.
- O player lembra sua posição e faz busca nessa posição antes de reiniciar. O watchdog de ausência de desenho passa de 900ms a 3s para não descartar players durante pequenas pausas da interface; saída real da Activity continua liberando imediatamente.
- Fundo verde animado removido. Arquivo ausente ou nunca decodificado ainda necessita de carregamento inicial e tem superfície neutra; não afirmar que arquivos faltantes viraram vídeos ou que todos os vídeos já ficam decodificados no primeiro instante.

O cache usa GPU, sem leitura de pixels para CPU nem cópia por quadro. Há uma cópia ao ficar pronto e nas transições. Aloca por clipe visitado, 27 clipes únicos hoje (~26,7 MiB nominais de pixels RGB565; alocação real depende do driver); limite defensivo de 40 entradas. Libera ao sair das plataformas para jogos/modal ou perder o contexto GL. O motor recebe os recursos liberados.

## Arquivos e entrega

Fontes: native_system_video720.h; native_system_video.h; native_formation.h; system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java.
Compilar: build_native.py. Montar: system-videos/build_videos.py. Instalar: system-videos/install_videos.py. Registrar: video-ready-cache/finalize.py.
Saída: TurboramaStation-videos-retorno-pronto.apk.
Fontes/registros anteriores: video-ready-cache/before/.
APK imediatamente anterior: TurboramaStation-led-premium-diagonal.apk, SHA256 3b8bb1fb0f25a40665d7bc6031228c0049d7595022146f940e371a793c01e3fa.

Preservar o LED premium, voo diagonal, vídeos únicos 720p em loop 1x, paleta do usuário, motor estável, login, jogos, saves e regras de navegação. O motor 1.0.8/6727ab7 e o ponto Git estável não mudam. Não afirmar validação visual ou medição de latência a partir de compilação/instalação.
