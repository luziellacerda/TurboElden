# Pastas exatas, restauração e reconstrução

## Identificação

| Conteúdo | Local |
| --- | --- |
| APK estável exato | `E:\ESTUDO APK\estaveis\2026-09-30-plataformas-emuladores\TurboramaStation-ESTAVEL-plataformas-emuladores.apk` |
| SHA256 | `78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2` |
| APK de trabalho (pode mudar em tarefas futuras) | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk` |
| Fontes atuais | `E:\ESTUDO APK\work\native-carousel\implementation` |
| Integração desta revisão | `E:\ESTUDO APK\work\native-carousel\implementation\platform-xbox-pce-refresh` |
| PSP BR/Game Gear finais | `E:\ESTUDO APK\work\native-carousel\implementation\platform-xbox-pce-refresh\final-videos` |
| Backup anterior à integração | `F:\Turborama-build-archive\TurboramaStation-before-NetherSX2-ca5556ac.apk` |
| Backup antes dos dois vídeos finais | `F:\Turborama-build-archive\TurboramaStation-platforms-a59a07af.apk` |
| Estável anterior preservada | `E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk` |
| Vídeos do mantenedor | `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas` |

## Restaurar no telefone

Fora de uma partida, instalar o APK congelado com a mesma assinatura por atualização (`adb install -r`). Nunca desinstalar ou limpar dados para restaurar. Entrada pública: `org.emulationstation.frontend/.auth.LoginActivity`; a própria aplicação recupera a sessão. Confirmar o hash do `base.apk` instalado. Não confundir esse APK com o arquivo de trabalho, que pode receber revisões futuras.

## Fontes publicados

O snapshot contém as fontes próprias ativas, headers incluídos pelo módulo nativo, pontes Java, scripts e mapas de integração, patches e referências de upstream. Arquivos grandes podem estar em gzip e são materializados por `restaurar_fontes.py`. O manifesto registra SHA256 original e armazenado de cada arquivo.

O C++ integral do frontend original não está disponível; o APK base privado e as bibliotecas oficiais identificadas são necessários. O Git sozinho não gera um APK completo. O snapshot não inclui APK/DEX/SO, catálogos de download privados, BIOS/firmware/ROMs, saves, chave de assinatura, vídeos/músicas privados nem dumps do telefone. Os arquivos doadores oficiais e licenças são identificados nos metadados; respeitar suas licenças.

## Compilar a revisão final

1. Trabalhar em uma pasta nova em E:. Materializar `snapshot/implementation`, mantendo os fontes originais preservados.
2. A receita final `platform-xbox-pce-refresh/final-videos/finish_platform_videos.py` foi executada sobre a base privada **a59a07af9360b360131062e1c2f75224256f5926c75547aaabd074133912db4e**. Ela espera o mapeamento anterior do PSP BR e ausência do Game Gear; para repeti-la, usar `system_video720_assets.before.h` no local correto antes da execução. Não executá-la sobre a saída final nem remover os guards.
3. A base a59a07af veio da receita `package_platform_xbox_pce.py` sobre a base **ca5556ac81e96e49d67ac0134533604908dd5122351c898ac2125d03a223cee7**. Preparar doador X1 BOX 1.2.8, recursos/namespace, catálogo privado e pontes antes de empacotar. Os scripts preparatórios não são idempotentes: `prepare_xbox_classic.py`, `merge_xbox.py`, `finish_xbox_merge.py`, `prepare_refresh_catalog.py`, `apply_refresh_sources.py`, montagem do template e pacote, com os ajustes registrados no handoff.
4. Preservar o catálogo privado `E:\ESTUDO APK\work\native-carousel\implementation\platform-xbox-pce-refresh\catalog-refresh.json`, SHA256 **c449e137b3fd351bbfee9c660e2afa1f44bd87c21b8418d00fd930e933422dbb**, e os dois identificadores desse hash no DEX8. Não restaurar catálogo antigo de Vita/GameCube/Saturn isoladamente.
5. Ferramentas locais: Python3; JDK17; Apktool3.0.3 em `E:\ESTUDO APK\TurboRetroEmu-build\tools`; build-tools35 em `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15`; android.jar34 em `G:\Android\Sdk\platforms\android-34`; LLVM em `C:\Program Files\LLVM`; NDKr28c em `E:\TurboEdenEngine\android-ndk-r28c`. Temporários em E:.
6. O módulo atual foi compilado diretamente por Clang com target aarch64-linux-android26, `-shared -fPIC -nostdlib`, alinhamento16KB, C++17/O2, sem exceções/RTTI. Os arquivos `libc.so`, `libdl.so`, `liblog.so` da pasta P são stubs de link; nunca os incluir no APK.
7. Os scripts públicos parametrizam assinatura por `TURBORAMA_KEYSTORE`, `TURBORAMA_KEY_ALIAS`, `TURBORAMA_STORE_PASSWORD` e `TURBORAMA_KEY_PASSWORD`. Essa parametrização é uma adaptação da cópia pública, registrada no manifesto. Nenhuma chave é publicada.
8. O pacote final deve preservar todos os DEX, catálogo e motores da base a59a07af; somente o módulo do carrossel, os dois vídeos finais e fontes anexos foram alterados. Conferir entradas, assinatura e zipalign. Uma reconstrução pode gerar hash diferente por metadados/assinatura; não alegar identidade sem conferir.

## Material dos outros motores

`dolphin-integration`, `flycast-integration`, `ps2-integration`, `psp-integration`, `wiiu-integration`, `xbox360-integration`, `platform-media-refresh/psvita`, `emulator-completion` e `saturn-modern` guardam as receitas/patches relevantes. Os scripts são históricos e exigem suas bases exatas; não executá-los em sequência sobre o APK atual sem planejar a reconstrução. O módulo final em `native_carousel.cpp` é a cadeia atual de rotas. PS2 não deve ser retomado sem novo pedido expresso.

## Receber jogos Naomi

Manter categorias `naomi` e `naomi2` e suas pastas. Inserir no catálogo autorizado os IDs, títulos, arquivos, capas, URLs e permissões reais; atualizar a identificação do catálogo pelo fluxo existente. Ambos chamam Flycast. Não criar Naomi3 nem links por suposição.
