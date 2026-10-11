# R126 — N64, GameCube e Wii com seus emuladores próprios no online

APK compilado, assinado e verificado em 11/10/2026. GameCube e Wii abrem o **Dolphin real**, com a Activity, o renderer, a entrada de controles e o NetPlay nativo do Dolphin. Nintendo 64 mantém o **Mupen64Plus AE real** integrado na R125. Essas três rotas não abrem StationRetroActivity nem utilizam o core do RetroArch.

Esta entrega é candidata: instalação, registro efetivo no servidor e gameplay nos aparelhos ainda não foram confirmados. As demais rotas online históricas permanecem como estavam; não estão todas convertidas para seus emuladores normais. Consulte a auditoria de sistemas e não anuncie uma migração universal.

## Artefato verificado

| Campo | Valor |
|---|---|
| APK local | `TurboStations-Premium-R126-20261011.apk` |
| SHA-256 | `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d` |
| Bytes | 2.233.970.789 |
| Certificado | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| Assinaturas / alinhamento | v2 e v3 verificadas / 16 KiB |
| Base exata | R125, `a3ed815c01fdb0bd06a3a2485991fe8d19a51c63fee0e9255a45ecd8a9b6d4a5` |
| Preservação | 13.544 entradas byte idênticas à R125; seis substituições e seis adições |

O recibo [package-final-r126.json](evidence/package-final-r126.json) foi produzido por comparação integral das entradas e pelas ferramentas reais de assinatura/alinhamento. Os vídeos locais, recursos, bibliotecas do carrossel, shaders/LED, economia, cache, preload, loading e limite de 30 fps dos menus foram preservados. As bibliotecas dos emuladores do modo normal permanecem idênticas.

## Fontes e contrato

- [ALTERACOES-DETALHADAS.md](ALTERACOES-DETALHADAS.md): implementação e preservação.
- [NATIVE-CONTRACT.md](NATIVE-CONTRACT.md): barreiras reais, ACK, opções, controles e saída humana.
- `java/`: lançamento, seleção de biblioteca/processo, sessão, perfil e endpoint.
- `native/`, `patches/`: adaptador e alterações da variante online do Dolphin.
- `recipe/`: fontes fixadas, dependências, transformação de DEX/manifesto, compilação, identidades e montagem.
- `tests/`, `evidence/`: provas isoladas e recibos; não são gameplay.
- [HANDOFF-R126-PARA-SERVIDOR.md](HANDOFF-R126-PARA-SERVIDOR.md): entrega consolidada das três identidades finais.

A R126 atualiza também o marcador de proveniência N64 porque ele incorpora o DEX/manifesto integrado. O core, plugins, hooks N64 e seu perfil foram preservados. **Não cadastrar o marcador intermediário R125 para este APK**; usar os três registros finais da R126.

## Compilação e limites

Dolphin upstream `2609-7`, commit `5102a0339c2177575378107b76541e47cc52122d`; NDK r28c/Clang 19, CMake 4.4.2, Ninja, Android API24/arm64-v8a. A receita lê o clone já existente, cria um arquivo de fontes isolado e usa 25 submódulos Android fixados e três dependências aninhadas. Não cria clone nem muda checkout. Java usa JDK17/D8 e a base exata R124 mais os deltas R125/R126.

São quatro portas emuladas disponíveis; o jogo, sua edição e o modo autenticado determinam se a sala aceita dois, três ou quatro participantes. Não ampliar a capacidade de todos os jogos. No Wii, a serialização oficial transporta o estado do Wiimote emulado e seus acessórios configurados; isso não comprova compatibilidade física de cada jogo ou controle.

A CPU N64 utiliza cached-interpreter para a sincronização nativa; equivalência de desempenho com o modo normal não foi medida. Dolphin usa sincronização de opções do anfitrião e GameINI fixado. Não prometer ausência de lag, aquecimento, ANR ou perda de sincronismo antes das medições físicas.

Binários, APK, jogos, BIOS, saves, chaves, capturas, logs pessoais e identificadores de aparelhos permanecem fora do Git. Não desinstalar, limpar dados, trocar assinatura, interromper partida/download ou reiniciar o servidor por consequência deste handoff.
