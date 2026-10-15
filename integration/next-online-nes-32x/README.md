# Próxima integração online: NES primeiro, Sega 32X depois

Esta pasta é uma preparação **fora do APK R169**. Ela não registra motores, não libera salas, não liga serviços e não altera PSX, N64 ou o motor offline. O objetivo é impedir que a presença de um core offline seja confundida com uma partida online funcional.

## Estado verificado no R169

O preflight leu o APK assinado R169 e o registro efetivo `assets/station-online/engines.json` (13 entradas):

| Plataforma | Core offline original | SHA-256 atual | Descritores online v3 |
| --- | --- | --- | ---: |
| Nintendinho (`nintendinho`) | `libfceumm_libretro_android.so` | `38659530f800032ed6ed46ea0cdf167a38326e0ecd9afa09a3c08130020d85af` | 0 |
| Sega 32X (`sega32x`) | `libpicodrive_libretro_android.so` | `92d28b94fd9381a9dea670e57d58a0f3252a99d0ffde8d310add41f81f90a4fd` | 0 |

Os dois hashes são iguais aos da auditoria R126 em `audits/station-online-system-engines-20261011/remaining-systems/matrix.json`; assim, a prova histórica dos nove exports Libretro vale para esses bytes. Ela **não** prova estado serializável útil, determinismo, multiplayer ou desempenho. O binário `libstation_retroarch.so` também está no APK, mas o seu loop de emulação pertence ao RetroArch; ele não está encaixado no `LibretroPlayer` normal dessas duas plataformas. Consulte `remaining-systems/README.md`, seção “Famílias cujo modo normal já é LibretroPlayer”.

`StationOnlineGame.engine()` só seleciona uma entrada `launchReady=true` com `station-stream.v3` (`integration/psx-online/java/.../StationOnlineGame.java:20-27`). Sem ela, o fluxo para antes do jogo. Mesmo com uma entrada adicionada, `StationRoomsActivity:1091-1095` enviaria backend não reconhecido a `StationRetroLaunch/StationRetroActivity`; isso usa o runtime RetroArch, e não comprova o owner normal. O source histórico da Activity em `versions/station-video-room-footer-r124-20261011/java/netplay-src/.../StationRetroActivity.java` mostra a separação. Não colocar `launchReady=true` apenas porque o ELF existe.

## Menor implementação NES segura

1. **Fixar o doador exato.** Localizar fonte correspondente ao FCEUmm de SHA acima, licença e opções efetivamente compiladas. O APK oferece o binário e a auditoria de ABI, mas esta revisão não encontrou a árvore fonte exata em `E:\StationNetplayWork\upstream`. Conferir também a resolução canônica `nintendinho` no DEX da próxima base e os formatos de ROM realmente publicados. Não reutilizar a política FDS: disco e gravação exigem perfil próprio.
2. **Provar o owner normal.** Criar uma variante online opt-in do `LibretroPlayer` em processo privado, com o mesmo core FCEUmm e os callbacks de vídeo, áudio e controle normais. Inspirar-se nas guardas de hash e ciclo do owner PSX (`integration/psx-online/ENTRY-CONTRACT.md`, `native/StationPsxOwner.hpp`), sem mexer na implementação PSX. O bridge NES deve ser instalado antes do `run` somente para uma sessão autorizada e removido ao encerrar. A rota offline continua byte idêntica.
3. **Implementar sincronização real.** No owner, amostrar inputs dos dois pads, confirmar pausa por epoch/serial no checkpoint de `retro_run`, validar `retro_serialize_size`, `retro_serialize` e `retro_unserialize` no jogo real, e só confirmar ACK após execução/aplicação. IO/rede não executa o core; perda de conexão mantém espera recuperável e saída humana fecha apenas a sessão privada. Avaliar se o transporte `station-stream.v3` e a coordenação `StationMultiplayerSession` existentes atendem este core. Não introduzir protocolo paralelo.
4. **Ligar cliente somente após o bridge.** Acrescentar backend NES explícito à whitelist de `StationOnlineGame.runtime()`, `StationNesLaunch`, Activity privada/Manifest e ramo de `StationRoomsActivity`. O descritor novo deve carregar hashes finais do core, runtime, dependências, opções e esquema de identidade do conteúdo. Manter a entrada indisponível até essas verificações passarem. Limite inicial: apenas modo de dois pads comprovado; Four Score fica separado.
5. **Cadastrar modos por edição no servidor.** Para cada jogo NES realmente multiplayer, exigir `itemId`, hash/edição, modo, dois lugares, controles/opções e identidade do motor assinado. Jogo individual recebe classificação explícita sem sala. O cadastro vem depois do APK final/kit exatos e da consulta pública autenticada. Não aprovar todas as ROMs por nome ou pelo teto da plataforma.
6. **Provar em etapas.** Usar ROM de teste legal ou própria para carga/120 quadros/estado/inputs em dois processos; depois dois telefones com o mesmo APK para primeiro quadro, som, controle independente, pausa/reconexão, saída do anfitrião e ausência de serviço órfão. Medir CPU e memória antes de anunciar suporte. Repetir a sequência para PicoDrive/32X após a NES; Mega Drive existente permanece intocado.

## Preflight reproduzível

```text
python -B integration/next-online-nes-32x/audit_offline_candidates.py --apk CAMINHO_DO_APK_R169
```

Ele lê somente os três itens pequenos do ZIP, compara os cores com a auditoria de hashes e informa a ausência de descritores. Não extrai APK, ROM, saves ou credenciais. O resultado da R169 foi: duas bibliotecas offline pinadas, zero descritores online NES/32X, `releaseReady=false` para ambas. O relatório local não é prova de gameplay.

## Bloqueios atuais

- Fonte exata dos dois cores offline e configuração de build ainda não fixadas nesta fase.
- Não existe bridge online no owner `LibretroPlayer` para NES ou 32X, nem prova de checkpoint/estado/inputs de dois aparelhos.
- Não existem descritores online, perfis de modo por edição ou prova pública assinada para esses motores.
- RetroArch online separado não equivale automaticamente à integração do motor normal, e um segundo pad não equivale a cabo/link de outras famílias.

Até resolver os bloqueios, o comportamento correto é negar a sala NES/32X com explicação, sem consumo em segundo plano.
