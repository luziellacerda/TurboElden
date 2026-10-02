# Avatar T e firmware Vita 3.74 no TESTE — 01/10/2026

Pedido do mantenedor: tirar o ícone roxo com S do cabeçalho e, sem foto, mostrar T; os componentes oficiais 3.74 do PS Vita têm que ir no aplicativo na instalação. Ramo `versao-funcional`. Cemu 0.5.2 estável, ARMSX2, FBNeo e o APK `7ce3fab3` intactos.

Arquivos `.PUP`, APK, `.so`, BIOS, ROMs, `keys.txt` e catálogo **não entram neste Git**.

## Avatar do jogador

O círculo ao lado de JOGADOR usava `assets/resources/profile_mockup.png` (S roxo da Sambox). Sem foto de usuário (`profile_*.png` vazio), o nativo mostra esse arquivo.

Substituição: T verde da Turborama (traço vermelho, fundo preto, anel circular), gerado por `make_profile_t.py` a partir do ícone aprovado `turborama-icon-v2`. `rebuild_profile_icon.py` troca só esse PNG no APK TESTE.

SHA-256 do PNG novo: `eb0fccbb5cebb5d2c110b48c7c0719eee36ceaf0d69f25f2a56512daee82d6f2`.  
Cópia em tempo de execução: `/sdcard/EmulationStation/.emulationstation/resources/profile_mockup.png`.

Com foto escolhida pelo jogador, a foto continua na frente.

## PS Vita — componentes 3.74 no APK TESTE

O Vita3K pedia componentes, firmware e fontes porque a pasta `files/psvita/setup/` no Samsung estava vazia. Os três PUPs oficiais 3.74 passam a ir **dentro do APK TESTE**, pasta `assets/psvita-firmware/`, sem compressão (o AssetManager lê arquivo grande).

`VitaEntryActivity.stageFirmwareFromAssets()` copia os três para `files/psvita/setup/` na primeira abertura. Em seguida `installFirmware` aplica no Vita3K, cria o usuário Jogador e grava `vita3k_app` / `initial_setup_completed=true`.

| Arquivo | Tamanho | SHA-256 |
|---|---|---|
| `PSVita-3.74-preinstalled.PUP` | 128 798 720 | `339d1439eb329cfbd1a936f0a1563458e0555ef52975486b2844e24b6049e33e` |
| `PSVita-3.74-main.PUP` | 133 834 240 | `6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf` |
| `PSVita-3.74-fonts.PUP` | 56 778 752 | `c3c03fc7363dd573d90e5157629bf11551f434b283cc898d9ffc71dd716b791c` |

Máscara nativa: bit 0 componentes, bit 1 firmware, bit 2 fontes. Pronto exige bits 1 e 2 (máscara 6). `rebuild_vita_ready.py` enxerta `classes24.dex` e os três assets; recusa qualquer outro `.PUP`; confirma o hash do Cemu 0.5.2 estável.

Os PUPs continuam fora deste repositório. O script lê `emulator-completion/firmware/` na máquina de build.

## TESTE local (fora do Git)

- Pacote: `org.turboramastation.frontend`
- APK: `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk`
- SHA-256 após o T: `be9b8125d56e704f256714e8a11812037c3eb95edf35dffacdcf259c1302fa83`
- SHA-256 após firmware no APK: `5090cb83e0d69957e22227b748848ce112c8aa302361cc71b5f336937fbfc7f5` (1 898 651 065 bytes)
- `classes24.dex`: `972ae20692a0297a735cc7a24d957396950a20b9ff00d6fadb63f03949d142af`

## Reprodução

Na pasta de fontes ativos, com os três PUPs em `emulator-completion/firmware/`:

1. `python brand-login/make_profile_t.py`
2. `python rebuild_profile_icon.py`
3. `python rebuild_vita_ready.py`

O script de Vita recusa PUP inesperado e confirma Cemu 0.5.2 `7ce3fab3…`.
