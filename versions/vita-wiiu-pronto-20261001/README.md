# PS Vita e Wii U prontos na abertura — 01/10/2026

Pedido do mantenedor: o emulador de PS Vita pedia instalações depois de abrir e tinha que já estar pronto; o Wii U precisava do `keys.txt` já instalado. Ramo `versao-funcional`. O ramo `estavel` e a tag `estavel-2026-09-30-cemu-052` permanecem em `f6d7c04`. Cemu 0.5.2 estável, ARMSX2, FBNeo e o APK `7ce3fab3` ficam intactos.

Firmware PUP, `keys.txt`, APK, `.so`, BIOS, ROMs e catálogo de jogos **não entram neste Git**.

## PS Vita (Vita3K)

Abrir o Vita caía na tela **Install Firmware** do Vita3K (`Skip for now` / `Open Library`), mesmo depois do firmware 3.74 aplicado. Essa tela é a rota `initial_setup` do próprio Vita3K.

Código em `VitaEntryActivity.java`:

1. `ensureReady()` inicializa o Vita3K, aplica os três PUPs oficiais 3.74 que já estejam no aparelho, chama `prepareFrontend`, cria o usuário **Jogador** se não houver nenhum.
2. Grava `SharedPreferences` `vita3k_app` → `initial_setup_completed=true`. Com isso o Vita3K abre a biblioteca (`apps_list`) e não o assistente.
3. Se o firmware ainda estiver incompleto, a Turborama permanece na tela dela. Não abre o instalador do Vita3K.

Os PUPs ficam só no aparelho, pasta `Android/data/<pacote>/files/psvita/setup/`:

| Arquivo | Tamanho | SHA-256 (identificação do pacote oficial 3.74) |
|---|---|---|
| `PSVita-3.74-preinstalled.PUP` | 128 798 720 | `339d1439eb329cfbd1a936f0a1563458e0555ef52975486b2844e24b6049e33e` |
| `PSVita-3.74-main.PUP` | 133 834 240 | `6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf` |
| `PSVita-3.74-fonts.PUP` | 56 778 752 | `c3c03fc7363dd573d90e5157629bf11551f434b283cc898d9ffc71dd716b791c` |

Máscara nativa: bit 0 pré-instalado, bit 1 principal, bit 2 fontes. Pronto para uso exige bits 1 e 2 (máscara 6). A busca também olha `EmulationStation/bios/psvita`, `Turborama/firmware/psvita` e `Download`.

`rebuild_vita_ready.py` recompila a ponte e troca só `classes24.dex` no APK TESTE.

## Wii U (Cemu 0.5.2)

O Cemu Android lê `keys.txt` na raiz da pasta de dados: `Android/data/<pacote>/files/Cemu/keys.txt`. No TESTE essa pasta tinha um stub de 277 bytes (4 linhas). Sem as chaves de disco, WUD/WUX não abre.

Código em `WiiUEntryActivity.java`:

- `ensureKeys()` na abertura (jogo e configurações).
- Se `Cemu/keys.txt` já tiver pelo menos 1024 bytes, não mexe.
- Se faltar ou estiver vazio, copia de pastas do dono no aparelho: `EmulationStation/bios/wiiu/keys.txt`, `Turborama/firmware/wiiu/keys.txt`, `Download/keys.txt`, `files/Cemu/keys.txt`.

O arquivo de chaves usado no aparelho foi o gist público indicado pelo mantenedor, copiado só para o storage do app. **Não está neste repositório.** No Samsung TESTE ficou com 449 507 bytes e 5 388 linhas de chave, na pasta do Cemu e em `EmulationStation/bios/wiiu/`.

`rebuild_wiiu_keys.py` recompila a ponte e troca só `classes20.dex` no APK TESTE.

## TESTE local (fora do Git)

- Pacote: `org.turboramastation.frontend`
- APK: `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk`
- SHA-256 do APK após o enxerto Wii U: `f53fa49ad4a10f3c75b5fb5636138987f877282d21a29d6da81c6bc058ab6fe6`
- Fontes ativos: `E:\ESTUDO APK\work\native-carousel\implementation`

## Reprodução

A partir da pasta de fontes ativos:

1. Colocar os três PUPs 3.74 em `emulator-completion/firmware/` (local) e, no aparelho, em `files/psvita/setup/`.
2. Colocar `keys.txt` no aparelho em `files/Cemu/` ou `EmulationStation/bios/wiiu/`.
3. `python rebuild_vita_ready.py`
4. `python rebuild_wiiu_keys.py`

Os scripts recusam PUP/`keys.txt` dentro do APK e conferem o hash do Cemu 0.5.2 estável `7ce3fab3…`.
