## Instruções posteriores incorporadas

Usar só os MP4 da pasta caratulas expressamente indicada. 27 arquivos encontrados, mapeados para 32 chaves existentes (29 presentes na lista atual de 36). Removidos complementos de outras pastas e clipes gerados a partir de fotos. Faltam arquivos para 7 plataformas atualmente exibidas; também sufami no mapa ampliado. A resposta "SIM" não informou os nomes nem adicionou os arquivos: não a interpretar como autorização para inventar ou substituir vídeos.

Velocidade explícita 1.0, pitch 1.0, loop nativo. Paleta exata em CORES-SOLICITADAS.md e ../laser-user-overrides.json. Cores duplas no Switch e CPS 2. Compilar as alterações em conjunto.

# Correção solicitada: somente o vídeo 720p

O usuário relatou que começava um vídeo, trocava para outro e parava. Os registros da revisão 81ccb3c confirmaram dois caminhos ativos: atlas MediaPlayer e camada 720p MediaCodec. Essa alternância foi rejeitada. Não reintroduzir resolução alternativa nem duas camadas de vídeo por célula.

Alterações:
- Removido o atlas do desenho, da inicialização Java e dos assets empacotados. O antigo SystemCardVideo.java é histórico e não entra no DEX atual.
- native_system_video.h contém apenas utilitários JNI/GL; native_system_video720.h desenha uma única fonte para cada célula.
- 35 arquivos 720 × 720 / 60fps continuam os mesmos; nenhum arquivo de resolução reduzida é incluído. Taxa codificada não equivale a medição de 60fps sustentados.
- Um MediaPlayer por clipe único visível, SurfaceTexture compartilhada entre células que reutilizam o mesmo clipe. setLooping(true), preparação assíncrona e relógio de reprodução administrado pelo Android. Removida a reimplementação manual de timestamps/EOF com MediaCodec.
- Ao sair da tela, abrir jogos/configuração modal ou pausar a Activity, libera os players. Falhas tentam recuperar a mesma fonte 720p; nunca mudam para outro vídeo. Enquanto o primeiro quadro prepara, há apenas fundo animado de carregamento.
- Brilho colorido por sistema, nave e motor estável preservados.

Fontes: E:\ESTUDO APK\work\native-carousel\implementation.
APK alvo: TurboramaStation-videos-720-unico.apk.
Montagem: build_native.py e system-videos/build_videos.py.
Instalação: system-videos/install_videos.py; preserva dados e recusa emulação ativa.
Registros finais: build-result.json, installed.json. Revisão rejeitada guardada em revisions/720-dual-rejected.

A captura duplicate-video-screen.png e os registros duplicate-video-log.txt são diagnóstico anterior à correção, não validação da versão nova. Não afirmar verificação visual, loop validado no aparelho ou benchmark se isso não foi realizado.
