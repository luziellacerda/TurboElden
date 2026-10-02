# Vita3K 4115 no TESTE — 02/10/2026

Pedido do mantenedor: atualizar o motor do PS Vita para o oficial mais novo; descrever tudo no Git. Ramo `versao-funcional`. Cemu 0.5.2 estável, ARMSX2, FBNeo e o APK `7ce3fab3` intactos.

Arquivos `.PUP`, APK, `.so`, BIOS, ROMs, `keys.txt` e catálogo **não entram neste Git**.

## O que mudou no TESTE

O TESTE estava no Vita3K **4103** (`e6ac4272`), o ponto documentado em 01/10 com firmware 3.74 no APK. O contínuo oficial Android em 02/10 17:02 é o **build 4115**, commit `a366df69` (renderer/gl honra `hashless-texture-cache`, PR #4163).

O Java do doador 4115 é **byte-idêntico** ao 4103 (`classes.dex` SHA-256 `b80d41d5c544264647408db068affeec4d856c2c8059709a311853d11d649f42`). JNI igual: 128 exports Java, 67 SDL, 53 NativeLib. Libs auxiliares e assets iguais. Só `libVita3K.so` muda (28040968 → 28034048).

`rebuild_vita_engine.py` aplica os mesmos deslocamentos ELF da integração (`org/libsdl/` → `org/vtsdlx/`, nomes das libs hook) e troca só o `.so` no APK TESTE. `classes23.dex`, `classes24.dex` (VitaEntry + firmware 3.74) e `libturbo_vita_jni.so` ficam iguais.

Doador oficial: [Vita3K-builds 4115](https://github.com/Vita3K/Vita3K-builds/releases/tag/4115)  
`vita3k-4115-a366df69-android.apk` SHA-256 `b9c7cf96dcc2d5bb0286dbf29676ea6ce4b556bc030b0d7c90ef27db8d8963dc`.

## O que permanece

- Firmware oficial **3.74** no APK (`assets/psvita-firmware/`), copiado na abertura para `files/psvita/setup/`. 3.74 é o último firmware oficial da Vita.
- Avatar T no cabeçalho (`profile_mockup.png`).
- `keys.txt` do Wii U **fora do APK e deste Git**. No aparelho: `files/Cemu/keys.txt` (cópia em `EmulationStation/bios/wiiu/`). `WiiUEntryActivity.ensureKeys()` copia se o arquivo do Cemu estiver ausente ou menor que 1024 bytes.
- Cemu 0.5.2 estável SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`.

## TESTE local (fora do Git)

- Pacote: `org.turboramastation.frontend`
- APK: `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk`
- SHA-256: `0e7974e1a324c4aabfb475d1fa9081f4307efd52ca099323bcafdd852694478b` (1 898 657 898 bytes)
- `libVita3K.so` relocado: `a133ff7e5397ae09d863e9583c37a5070024f0bc226630ae4a1fc40e77fed8db`
- `classes24.dex`: `972ae20692a0297a735cc7a24d957396950a20b9ff00d6fadb63f03949d142af` (igual ao 01/10)
- Assinado debug.keystore, esquemas v2 e v3

## Reprodução

Doador 4115 em `platform-media-refresh/psvita/vita3k-4115.apk`, APK TESTE no hash 01/10 `5090cb83…` (T + 3.74):

```
python rebuild_vita_engine.py
```

O script recusa PUP inesperado e recusa `keys.txt` no ZIP. Confirma Cemu 0.5.2 `7ce3fab3…`.

## Notas de aparelho (02/10)

- Backup completo local: `G:\BAKUP SISTEMA APP 02-10-2026` (TESTE 01/10 `5090cb83…`, estável Cemu, Git, esteira). Fora deste repositório.
- **Wii U tela preta no POCO** (2412DPC0AG, Mali-G720 / MT6899): o Cemu abre o título, o áudio sobe, o shader cache grava; o Vulkan não tem `VK_FORMAT_BC1`…`BC5`. Cemu Android nesta build é Vulkan. Mali Dimensity em geral não expõe BCn. No Galaxy A56 (Xclipse) a imagem aparece. Driver customizado na Mali não cria BCn.
- **PS Vita “sem jogos” depois de instalar:** firmware 3.74 aplicado (`os0/kd`, `sa0` fontes, `vs0` sistema). `ux0/app` vazia. Log Vita3K: `Install app before patch`. O RAR vira ZIP pela primeira pasta com `sce_sys/param.sfo`; se o patch (`CATEGORY gp`) vem antes do jogo (`gd`), o Vita3K recusa o update sem o título base e a lista fica vazia. O 4115 não muda esse instalador.

## Linha do tempo deste dia

1. Restaurar TESTE ao GitHub `6454ea4` (T + 3.74, motor 4103, keys fora do APK) e instalar no A56.
2. Backup `G:\BAKUP SISTEMA APP 02-10-2026`.
3. Atualizar só `libVita3K.so` 4103 → 4115; firmware, Java e keys como no GitHub.
