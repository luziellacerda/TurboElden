# TurboEden — APK experimental

Esta pasta registra uma **variante de teste** do APK `TurboramaEmuTestes.apk`, identificado internamente como Eden/Yuzu. Ela é separada do frontend EmulationStation/Libretro documentado na raiz deste repositório. O nome **TurboEden** aparece na interface e no Android package ID; a biblioteca C++ compilada ainda é a da distribuição original. Portanto, esta edição **não é um aplicativo inteiramente reescrito como TurboElden** e não reúne os cores Libretro do outro projeto.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| [`TurboEden-teste-assinado.apk`](TurboEden-teste-assinado.apk) | APK ARM64 de teste, assinada com certificado Android Debug local. |
| [`TurboEden-TV-banner.png`](TurboEden-TV-banner.png) | Banner com o nome visível TurboEden. |
| [`branding.patch`](branding.patch) | Mudanças textuais no manifesto, em Smali e nas strings da saída Apktool 3.0.3. O banner é fornecido separadamente. |
| [`HANDOFF-TURBOEDEN.md`](HANDOFF-TURBOEDEN.md) | Mudanças, verificações e limites da variante. |
| [`HANDOFF-COMPLETO-TURBORAMA-EMU-TESTES.md`](HANDOFF-COMPLETO-TURBORAMA-EMU-TESTES.md) | Auditoria funcional e procedência do APK original. |

## Identificação e integridade

- Package ID: `dev.turboeden.turboeden_emulator`.
- Nome exibido: `TurboEden`.
- APK: 25.369.381 bytes; SHA-256 `2D40E60CC58E1AEECCEB176868F9FCC344E111E90FEC354EBECBD113255CD342`.
- APK original estudado: SHA-256 `BEFBF70B1A05715811FE092EF9CF71E6F1C1672008A6C5CAA31D633E99615668`.
- Sete bibliotecas nativas ARM64 byte a byte iguais às do APK original.
- Alinhamento ZIP e assinatura APK v2/v3 verificados. Instalação e execução em aparelho ainda não testadas.

## Como reproduzir a mudança textual

Desmonte o APK original identificado acima com Apktool 3.0.3. Na pasta resultante, aplique `branding.patch` com `git apply` e substitua `res/drawable-xhdpi/tv_banner.png` pelo arquivo desta pasta. Remonte com Apktool, alinhe com `zipalign` e assine com uma chave de testes. A saída precisa de validação em aparelho ARM64/Vulkan. A chave de assinatura não faz parte desta publicação.

O APK original não inclui jogos, firmware nem chaves de console. Os nomes internos do código nativo e os links oficiais do projeto de origem foram preservados. A [tag pública v0.2.1 do Eden](https://github.com/eden-emulator/mirror/tree/v0.2.1) é uma referência de investigação para recompilação integral, mas ainda não há comparação binária que confirme a correspondência exata com este APK específico. Os direitos e avisos do projeto de origem permanecem aplicáveis.
