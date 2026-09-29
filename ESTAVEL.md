# ESTÁVEL — TurboramaStation com vídeos e playlist retrô

**Versão designada estável pelo mantenedor em 29/09/2026.**

- Ramo: `estavel` (também publicado em `versao-funcional`).
- Tag fixa: `estavel-2026-09-29-playlist-retro`.
- [Snapshot e manifesto](versions/estavel-2026-09-29-playlist-retro/); [restauração completa](versions/estavel-2026-09-29-playlist-retro/RESTAURACAO.md).
- APK: `TurboramaStation-ESTAVEL-playlist-retro.apk`; SHA256 `352d74708adacd4bb3e2e9edc428a4fca6c0836fb81ee4e512cf4b5fb511a049`; 667694649 bytes.
- Motor histórico: 1.0.8, commit `6727ab725f1c4ac9afdd0382cc7d4ae5d3ff8eb3`. Esse commit identifica o motor; a nova tag identifica a entrega atual.

## O que foi congelado

Carrossel nativo e rotas existentes, vídeos únicos 720p em loop/velocidade normal, pré-carga e quadro retido para retorno, LED intenso nas cores de cada plataforma, F-16 com câmera traseira/voo diagonal e nuvens/estrelas alinhadas, login/ícone/menus atuais. Playlist de 18 músicas locais de Donkey Kong, Super Mario World e Rock n’ Roll Racing, com um player e controle nativo Música de fundo. Código prevê pausa/liberação ao entrar na emulação.

36 plataformas ativas; 27 vídeos cobrem 29 delas. Sete ainda sem vídeo: Atari 7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx. Motor e DEX originais preservados; não contém os experimentos anteriores de emulação/FPS/shaders.

## Pastas exatas

| Uso | Caminho |
|---|---|
| Fontes ativos e compilação | `E:\ESTUDO APK\work\native-carousel\implementation` |
| APK congelado de retorno | `E:\ESTUDO APK\estaveis\2026-09-29-playlist-retro\TurboramaStation-ESTAVEL-playlist-retro.apk` |
| APK instalado, saída original | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-playlist-retro.apk` |
| Perfil ativo | `E:\ESTUDO APK\work\native-carousel\implementation\stable-design\active-profile.json` |
| Handoff local | `E:\ESTUDO APK\work\native-carousel\HANDOFF-IMPLEMENTACAO-CARROSSEL-NATIVO.md` |
| Fonte nativa e shaders | `implementation/native_carousel.cpp`, `implementation/native_*.h`, `implementation/space3d/` |
| Vídeos/player/montagem | `E:\ESTUDO APK\work\native-carousel\implementation\system-videos` |
| Playlist e MP3 privados | `E:\ESTUDO APK\work\native-carousel\implementation\retro-playlist` |
| LED atual | `E:\ESTUDO APK\work\native-carousel\implementation\premium-selection-laser-android.glsl` e `native_laser.h` |
| Snapshot no Git | `versions/estavel-2026-09-29-playlist-retro/snapshot/implementation/` |
| Checkout usado | `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git` |

## Recuperação e evidências

600 arquivos de fontes, recursos e documentação preservados, com SHA256 no manifesto. Cabeçalhos grandes em gzip recuperável. APK/MP3/MP4, chaves, firmware, ROMs, saves e credenciais ficam locais. As licenças/fontes de terceiros foram mantidos. Clone sozinho não recompila o frontend original completo: dependências privadas e ferramentas estão descritas na restauração.

Instalado em 2026-09-29T17:37:29.280278, com Success e hash conferido. Publicação a pedido do usuário; não houve novo teste visual, reprodução de áudio ou medição de FPS. 60fps refere-se à codificação dos vídeos, não a desempenho garantido.

A referência anterior `estavel-2026-09-29-camera-traseira`, commit `95d244bcea95647236bea335c41b46afe15674bf`, e seu APK congelado foram preservados. Não mover tags antigas nem restaurar outro APK apenas porque o nome contém “estável”. Atualizar sem desinstalar/limpar dados.
