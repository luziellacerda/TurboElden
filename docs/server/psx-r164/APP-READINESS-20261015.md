# PSX online na R164 — diagnóstico do app para o servidor

**Estado em 15/10/2026:** esta é uma análise de prontidão, sem alteração no APK ou nas políticas de jogos. A revisão estável em dois jogadores N64 é `estavel-station-r164-20261015`; o APK R164 tem SHA-256 `903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210`.

## O que já existe no APK R164

- A fonte de verdade é `assets/station-online/engines.json` **dentro do APK assinado**, não o `integration/psx-online/profile.json` histórico da R127. O registro PSX instalado tem `launchReady=true`, backend `psx-player-station-v1` e `engineId=pcsx-rearmed-ff81ed17-player-v3-1b315b86b4a7`.
- O caminho online usa o PCSX-ReARMed `libpcsx_rearmed_libretro_android.so` com o owner original `libmain.so` e o adaptador opcional `libstation_psx_online.so` no protocolo PXL1/v3. Não é uma troca para o netplay padrão do RetroArch e não altera a rota offline.
- A política atual exige HLE, duas portas Standard, exatamente dois jogadores, sem Multitap, analógico, arma de luz ou threads GPU/SPU/dynarec. O lançamento confere o perfil assinado da edição, o conteúdo e as opções antes de autorizar a partida.
- O `server-return.json` da R164 confirma `serverApplied=true`, o `engineId` PSX acima cadastrado e `psxHleApprovalsAdded=0`. Portanto a ausência de jogos aprovados no ledger do servidor é o bloqueio imediato de uma sala PSX; o retorno não demonstra ausência de motor no app.

## Trabalho necessário antes de qualquer novo APK

1. Qualificar **uma edição exata** de jogo PSX com modo para dois jogadores e HLE no servidor. Vincular o `itemId`, hash integral do conteúdo, motor R164, core, runtime, perfil de controle `standard-2p-v1`, modo e capacidade `[2]`. Devolver capability assinada e a razão explícita para qualquer recusa. Não liberar jogos por plataforma inteira.
2. Para `.cue`, exigir o conjunto CUE **e todas as tracks referenciadas**, com a identidade `cue-set-v1` do fluxo vigente; um hash só do CUE não comprova os dados que o core lê. Conferir o mesmo conteúdo nos dois aparelhos.
3. Com A56 e g52 na mesma R164, testar criação e entrada na sala, primeiro quadro, imagem, som, controles independentes, sincronismo, saída humana e retorno à sala. Registrar falha concreta e logs sanitizados se houver. Medir o tempo de hash/arranque em CHD e CUE antes de mudar desempenho.
4. Somente se esses testes indicarem defeito do app, preparar correção delimitada. Mudança no DEX ou no adaptador exige novo APK, novos IDs e novo cadastro de motor/perfis; não recompilar por hipótese.

O PCSX-ReARMed oficial informa que a BIOS HLE reduz compatibilidade e pode produzir tela preta em certas edições; a aprovação HLE precisa ser por jogo. Também informa que Multitap requer jogo compatível e pode deixar os controles sem resposta quando o jogo não o espera. A documentação de netplay do Libretro exige core/conteúdo idênticos e comportamento determinístico; essa regra orienta a validação, mas não prova o PXL1 próprio do TurboStations. Fontes: [PCSX-ReARMed](https://docs.libretro.com/library/pcsx_rearmed/) e [Netplay Libretro](https://docs.libretro.com/development/retroarch/netplay/).

## Limites preservados

- A integração PSX atual é ARM64/API 28+ e de dois jogadores. Três ou mais exigem evolução do adaptador e perfis por jogo; a opção Multitap do core, sozinha, não amplia a capacidade do app.
- O worker de sessão PSX nasce na Activity e se encerra na saída humana pelo código atual. Isso é prova de escopo, não teste físico de consumo ou limpeza; registrar processo e serviço após sair.
- Não ativar Turbo CD nem leitura antecipada do disco inteiro como atalho de latência. A documentação do core adverte risco de crash no primeiro caso e cerca de 750 MB extras de RAM no segundo.

Referências locais: `integration/psx-online/ENTRY-CONTRACT.md`, `integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxLaunch.java`, `integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxSession.java`, `docs/server/r164/STABLE-BASELINE-20261015.md` e [retorno R164 do servidor](https://github.com/luziellacerda/Servidor-pix/blob/fix/station-r164-server-20261015/docs/station-android/r164/server-return.json).
