# R96 — controles Bluetooth Android

Base integral: R95. Esta revisão altera somente a configuração dos controles usados pelo motor RetroArch da TurboStations.

## BSP-D3

O BSP-D3 deve ser ligado com **X + HOME**, que ativa o modo HID padrão do Android. O modo **A + HOME** pertence ao ShootingPlus e envia mapeamentos de toque, por isso não oferece comandos confiáveis aos emuladores.

O perfil `assets/station-online/autoconfig/android/BSP-D3.cfg` reconhece os nomes `BSP-D3`, `D3` e `ShanWan D3`. Ele configura direcional, dois analógicos, A/B/X/Y, LB/RB, LT/RT, L3/R3, START e SELECT.

## Outros controles

Foram incorporados os 218 perfis Android do projeto oficial `libretro/retroarch-joypad-autoconfig` no commit `f3b62b847ed21939b668b897b18bbc1defbaae05`. A licença e a origem acompanham os arquivos.

O motor agora:

- carrega automaticamente o perfil correspondente ao nome e aos identificadores do controle;
- aceita até 16 dispositivos detectados, respeitando o limite real de cada jogo;
- mantém o controle na mesma porta quando o Bluetooth reconecta;
- conserva o toque e o controle virtual existentes.

Salas, servidor, catálogo, downloads, vídeos, capas, efeitos e emuladores não foram modificados nesta revisão.

## Artefato

APK: `TurboStations-Premium-R96-20261009.apk`

SHA-256: `64a71268b77196ef2f3c064eb0a1d24e1ef75cc3be9f4bcd9cfcb064ce6d5f24`

Assinatura: mesmo certificado das versões instaladas, SHA-256 `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
