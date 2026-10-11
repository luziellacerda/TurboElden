# R125 — N64 com Mupen64Plus AE real

Base exata: R124, fonte `08cf0947538da796a9534d211467ecfefb4884e8` e APK `aeeb2f8167a442db5a58b990cf6d45b613fab42b1e7a9bbc0bf3214b260420c4`. A R125 é uma candidata de integração; não é uma promoção de estabilidade.

## Implementado

- N64 online abre a **GameActivity/CoreService do Mupen64Plus AE**, com seu renderizador, áudio, menus e controles. Não abre a NativeActivity do RetroArch nem troca somente a aparência do controle.
- Variante exclusiva `libstation_mupen64plus_core.so`, derivada do upstream AE `33bf7021549d7873e976884370fbd1a8e7333bc7`. A biblioteca e os plugins do N64 normal permanecem byte idênticos.
- O protocolo nativo TCP/UDP v1 do Mupen trafega pelo envelope interno SN64/1 nos links Station WSS v3 autenticados existentes. Não exige abrir UDP público.
- Cada telefone conserva seu controle local na porta P1 do emulador; o transporte nativo associa esse controle ao slot autenticado da sala. O anfitrião fornece configurações, saves temporários e entradas para até quatro slots aprovados.
- Diretórios, preferences, cheats e saves da sessão são isolados. O conteúdo normal não é sobrescrito. Assets do Mupen ausentes em instalação nova são preparados no worker antes da GameActivity.
- A pausa é confirmada pela thread real de emulação, sem avançar quadros. DATA de preparação continua fluindo durante a pausa, evitando ciclo entre registro/EXECUTE/READY.
- Perda de WSS mantém o emulador pausado e solicita reconexão. Só uma saída humana validada autoriza desligamento. Falha irreversível mantém explicação e saída pelo menu; não se promete rollback.
- O registro inicial oferece MEMORY=2/raw=0 antes de o input plugin estar anexado; corrigida a oferta global ainda zerada. Leituras TCP canceláveis não entram em loop ao receber EOF.

## Preservação e pacote

O pacote final altera apenas `AndroidManifest.xml`, `classes35.dex`, `classes36.dex`, `assets/station-online/engines.json` e adiciona as duas bibliotecas Station do N64. **13.544 entradas restantes conferidas por SHA-256**, incluindo carrossel, LEDs, cache/preload, loading, vídeos locais, opções de economia, outros emuladores, mídia e runtime anterior. Mesma assinatura, alinhamento de bibliotecas em 16 KiB. A Activity nova é privada e fica no processo principal; GameActivity/CoreService continuam em `:n64core`.

APK final: `TurboStations-Premium-R125-20261011.apk`, 2.217.741.887 bytes, SHA-256 `a3ed815c01fdb0bd06a3a2485991fe8d19a51c63fee0e9255a45ecd8a9b6d4a5`. Instalador permanece local, fora do Git. Ver `evidence/package-final.json`.

## Evidências e limites

- 282 verificações JVM do protocolo: 2/3/4 slots, fragmentação, saves, nomes UTF-8, filas, backpressure e cancelamento.
- 134 verificações C e 36 guardas de geração, incluindo registro antes do input plugin. Core completo recompilado de 79 fontes; sem reutilizar objetos antigos.
- Compilação Java/D8 de 190 fontes. Auditoria independente de 20 assinaturas de hooks, AXML reversível, 830 assets e ciclo READY. Ver `evidence/n64-final-independent-audit.json`.
- Compilação, assinatura e preservação do APK foram verificadas. **Nenhum gameplay físico da R125, ativação do servidor, desempenho do interpretador ou estabilidade térmica foi confirmado.** R124 instalada não foi interrompida nesta entrega.

## Registro e continuidade

O novo engine/perfil/hashes exigem cadastro próprio; não reutilizar o perfil do ParaLLEl nem alias de hashes. Ver `HANDOFF-N64-R125-PARA-SERVIDOR.md` e `native/RUNTIME-IDENTITY.json`. Salas novas somente depois de a resposta assinada refletir o cadastro correto.

A R125 modifica a rota N64. A adaptação real do Dolphin para GameCube/Wii está separada em R126 e ainda não integra este APK. As outras rotas online históricas não foram declaradas convertidas.

## Reproduzir

Receitas em `recipes/`: compilação Java sobre manifesto R124, patch condicional de sete arquivos smali, compilação completa do core, congelamento de identidade, runtime de proveniência, montagem com lista explícita de mudanças e conferência final. São exigidos o APK base exato e os arquivos upstream/dependências hash conferidos. Não executar receitas históricas de preparação que restaurem Activities antigas.

Fonte do protocolo Mupen: [API oficial NetPlay](https://github.com/mupen64plus/mupen64plus-core/blob/master/doc/emuwiki-api-doc/Mupen64Plus-v2.0-Netplay-API.mediawiki). Core/patches mantêm atribuição GPL-2.0-or-later; upstream e licenças estão vinculados na receita nativa.
