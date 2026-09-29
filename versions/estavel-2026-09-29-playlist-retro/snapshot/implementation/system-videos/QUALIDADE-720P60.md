# Pedido atual: 720 × 720 / 60 fps e brilho por sistema

## Conteúdo

35 clipes individuais em 720 × 720 e taxa constante de 60 fps, gerados novamente dos originais, sem ampliar os antigos clipes reduzidos do atlas. As fontes abaixo de 60 fps têm repetição de quadros; não são apresentadas como movimento nativo de 60 quadros diferentes. Cinco clipes sem filmagem do tema usam movimento da arte correta, agora calculado a 60 fps.

## Reprodução nativa

SystemCardVideo720 usa MediaExtractor e MediaCodec por nome de decoder de hardware compatível; não permite decodificação por software nessa camada. Buffer de entrada/saída assíncrono, sem preparar/ler arquivos na thread OpenGL. Timestamps agendam a apresentação dos quadros; ao chegar ao final, volta ao início e mantém a linha de tempo, sem EOS/recriação do codec a cada loop.

No máximo oito clipes únicos visíveis. Instâncias compartilhadas quando duas células usam o mesmo vídeo; prioridade à célula principal. Ao sair da tela, o stream é liberado. Ao abrir jogos, configurações modais ou pausar a Activity, libera todos. O atlas leve continua como transição e compatibilidade para que as outras células nunca precisem voltar a fotos.

O limite é consultado no aparelho com areSizeAndRateSupported e getMaxSupportedInstances, reservando uma instância para o atlas. Esses limites são declarações de capacidade, não medição da taxa sustentada: https://developer.android.com/reference/android/media/MediaCodecInfo.CodecCapabilities#getMaxSupportedInstances(). A fluidez efetiva depende do aparelho, temperatura e carga. Quando faltam recursos, as células afetadas usam o vídeo do atlas em resolução/taxa inferiores; isso não deve ser chamado de 720p/60 real.

A declaração do fabricante no celular conectado informa H.264 até 4096 × 2176, performance point 3840 × 2160 / 60 e até 16 instâncias não seguras. Isso orientou a implementação, mas não substitui medição real. Não foi executado benchmark nesta alteração.

## Brilho da célula principal

Mesmas cores gc-laser-color/gc-accent-b e regras do tema original, 45 chaves no mapa laser-system-colors.json. A célula selecionada resolve a chave do sistema em tempo de execução. O brilho é desenhado depois do vídeo 720p, sem ser coberto por ele; raio externo 11px, contorno fino mais visível, cor mais saturada e ponto luminoso com relógio monotônico. Não troca todas as cores por verde.

## Arquivos

Fontes em E:\ESTUDO APK\work\native-carousel\implementation. Reprodutor: system-videos/java/org/emulationstation/frontend/SystemCardVideo720.java. Integração: native_system_video720.h. Recursos: system-videos/assets/720-*.mp4. Preparação: system-videos/prepare_720.py, depois prepare_laser.py, build_native.py e system-videos/build_videos.py. Entrega: TurboramaStation-videos-720p60.apk. build-result.json e installed.json são os registros finais; enquanto a montagem não termina, consultá-los como revisão anterior.

Base estável, motores, login, ícone, jogos, saves, nave e regras de navegação preservados. A tag Git estável não é movida.
