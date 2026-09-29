# Restaurar estavel-2026-09-29-playlist-retro

## Retorno exato ao APK publicado como referência

APK privado congelado: `E:\ESTUDO APK\estaveis\2026-09-29-playlist-retro\TurboramaStation-ESTAVEL-playlist-retro.apk`.
SHA256: `352d74708adacd4bb3e2e9edc428a4fca6c0836fb81ee4e512cf4b5fb511a049`; 667694649 bytes. Compare antes de instalar. A publicação não recompilou nem reinstalou o app.
Saia normalmente de qualquer emulação; atualize com a mesma assinatura usando `adb install -r CAMINHO_DO_APK`. Nunca desinstale nem limpe dados. O APK privado não está no Git porque inclui dados e músicas que não foram autorizados para distribuição pública.

## Recuperar fontes

Na pasta desta versão, execute `python restaurar_fontes.py --destino "E:\ESTUDO APK\restaurados\estavel-2026-09-29-playlist-retro"` em uma pasta NOVA. O script confere hashes e descomprime os cabeçalhos originais. Não altera o aparelho. O resultado fica em `implementation` dentro do destino.

## Compilar esta integração

O clone não contém o C++ completo original do frontend/motores. A compilação depende da base privada. Para reproduzir o ambiente atual, preserve os fontes ativos antes de restaurar no caminho `E:\ESTUDO APK\work\native-carousel\implementation`; vários scripts usam caminhos absolutos. Para usar outra pasta, adapte explicitamente os caminhos E: dos scripts antes de compilar; não misture snapshots.

1. Base de montagem: `E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira\TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk`, SHA256 `54681d24d4ae912c0d081b276064264f95ad5e1d41e4e2851d2daa87169c4257`. É a entrega camera-traseira anterior. Base histórica original: `stable-reference-audit/original-1.0.8-alignment-preserved.apk`, SHA256 `5cd234d0ac57aa6f1b260db6278087b7d961c671385ecf47871570bc00e78814`.
2. Vídeos privados: copiar os 27 `720-*.mp4` locais para `system-videos/assets/`, conferindo videos-manifest.json. Originais em `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas`. A regeneração usa prepare_720.py e imageio-ffmpeg; preserve duração/velocidade. Nova codificação pode gerar hashes distintos e exige nova revisão do manifesto.
3. Música privada: copiar as 18 faixas `track-01.mp3` a `track-18.mp3` de `E:\ESTUDO APK\work\native-carousel\implementation\retro-playlist\assets` para a mesma pasta relativa restaurada. Fontes em `C:\Users\Admin\Music\LinkSom\SNES`. Conferir tamanho/SHA no manifesto sanitizado; nenhum MP3 foi publicado. playlist.json foi incluído.
4. Ferramentas: Python 3.14 (`C:\Python314\python.exe`), clang/LLD em `C:\Program Files\LLVM\bin`, NDK `E:\TurboEdenEngine\android-ndk-r28c`, JDK17 `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot`, Android SDK `G:\Android\Sdk\platforms\android-34\android.jar`, build tools `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15`. Modelo usa bibliotecas Python locais conforme prepare_f16.py. Tema original TURBORAMAx em G: é dependência de prepare_laser.py; mapeamento, cores e shader gerado estão preservados.
5. Assinatura privada original em `C:\Users\Admin\.android\debug.keystore`; não publicar. Ausência/assinatura diferente impede atualizar preservando o pacote instalado.
6. Executar `build_native.py`, depois `system-videos/build_videos.py`. Saída `TurboramaStation-playlist-retro.apk`. O segundo script acrescenta os dois helpers Java em classes9.dex e mídias; preserva motores e DEX originais. Só libturbo_carousel.so é substituída na base.

Não execute package_apk.py, scripts flight-rear-view ou finalizadores de revisões antigas para produzir esta entrega. São histórico; podem gerar outro APK ou sobrescrever o perfil atual. Installer local depende de auditoria do aparelho e não foi publicado neste snapshot; use instalação de atualização como descrito acima.

## Limites conhecidos

Sete plataformas ativas sem arquivo de vídeo; não foram criados substitutos. Arquivos nunca decodificados precisam de carregamento inicial. Cache é limitado pelo hardware. Designação estável solicitada pelo mantenedor; compilação, assinatura e instalação/hash já registrados, sem nova conferência de áudio/visual/FPS nesta publicação. Backup criptografado de 15:39 é anterior aos vídeos/playlist e não representa esta revisão.
