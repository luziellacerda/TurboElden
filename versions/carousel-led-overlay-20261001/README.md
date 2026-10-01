# Carrossel — LED colorido e overlay cinza 01/10/2026

Atualização de código nativo do carrossel principal de sistemas. Ramo `versao-funcional`. O ramo `estavel` e a tag `estavel-2026-09-30-cemu-052` permanecem no commit `f6d7c04`. Cemu 0.5.2, PS2 ARMSX2, FBNeo e o APK estável `7ce3fab3` ficam intactos.

## Pedido

Manter o LED colorido que percorre o aro das células. Remover o overlay cinza transparente que passava na frente da arte, só nas células do carrossel principal de sistemas. O mantenedor confirmou que o overlay foi removido.

## Código

- `premium-selection-laser-android.glsl`: `head`/`tail`/`hot` permanecem. O núcleo do LED usa a cor da célula (`hue*1.38`). Fragmentos com `sd < 1.20*scale` são descartados para o LED ficar fora da arte.
- `native_laser.h`: faixa oca do laser com inset `radius+6*scale`.
- `native_skin.h`: ignora o contorno nativo `0x228714` e os fills aditivos `src==4 dst==1` em `mappingCover`.
- `native_formation.h`: ignora a faixa aditiva nativa de 6 vértices e outros aditivos em `mappingCover`.
- `native_action_motion.h`: ABRIR estático no carrossel de sistemas.
- `laser-user-overrides.json`: paleta em dois tons (Naomi 2/Model 2 vermelho+azul; Vita branco+azul; DS branco+vermelho; N64/N64 BR amarelo+branco).
- `prepare_laser.py`, `build_native.py`, `rebuild_laser_colors.py`: compilam `libturbo_carousel.so` e enxertam só esse módulo no APK TESTE.

APK, `.so`, vídeos, BIOS, ROMs, chaves e catálogo de jogos não entram no Git.

## TESTE local (fora do Git)

- Pacote: `org.turboramastation.frontend`
- APK: `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk`
- SHA-256: `a03ea6b108637d82f09105765beb0ed9aa28a7571813935ab651f241ffe4f2c8`
- Módulo nativo SHA-256: `523eb3b3c87c53834ea172091aa2c9826874e7a3956077b1269069901283da24`
- Fontes ativos: `E:\ESTUDO APK\work\native-carousel\implementation`

## Reprodução

A partir da pasta de fontes ativos: `python build_native.py` e em seguida `python rebuild_laser_colors.py`. O enxerto troca somente `lib/arm64-v8a/libturbo_carousel.so` e confere o hash do APK estável Cemu 0.5.2.
