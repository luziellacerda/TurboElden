# TurboramaStation — versão estável atual

**Tag: `estavel-2026-09-30-dolphin-flycast`** — publicada a pedido do mantenedor em 30/09/2026, após aprovação do APK instalado. Ramos de referência: `estavel` e `versao-funcional`. Tags anteriores permanecem preservadas.

## Identificação obrigatória

- APK: `TurboramaStation-ESTAVEL-dolphin-flycast.apk`
- SHA256: `55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85`
- Tamanho: **738.069.339 bytes**.
- APK congelado: `E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk`.
- Fontes ativos: `E:\ESTUDO APK\work\native-carousel\implementation`.
- Snapshot Git: [`versions/estavel-2026-09-30-dolphin-flycast`](versions/estavel-2026-09-30-dolphin-flycast/).

## O que está nesta versão

Dolphin 2609-7 e Flycast v2.7-44 integrados no mesmo APK, menus oficiais, migração preservando saves, retorno mantendo o login, BIOS locais provisionadas sem sobrescrever arquivos existentes, fundo Turborama e correção do botão Voltar que exigia vários toques. Inclui melhorias do botão Abrir, pesquisa, avisos de download, carregamento e saída do PS2. Carrossel, vídeos 720p, LED por plataforma, F-16 e playlist preservados.

- [Descrição completa das alterações e verificações](versions/estavel-2026-09-30-dolphin-flycast/ALTERACOES.md).
- [Pastas, dependências e ordem para restaurar/compilar](versions/estavel-2026-09-30-dolphin-flycast/RESTAURACAO.md).
- [Inventário verificável dos fontes e identificação dos motores](versions/estavel-2026-09-30-dolphin-flycast/MANIFESTO-ESTAVEL.json).

## Limites da referência

O pacote instalado foi identificado e aprovado; o candidato posterior `3085d9fc` está excluído. Wii e Sonic foram confirmados pelo usuário, assim como retorno sem login; isso não certifica todos os jogos ou desempenho em todos os aparelhos.

APK, BIOS, ROMs, saves, assinatura, credenciais e mídias privadas ficam locais. O Git contém fontes da integração e recursos revisados; depende das bases binárias identificadas, pois o C++ integral do frontend original não está disponível. Os motores oficiais não foram recompilados integralmente do C++; a integração foi compilada. Restaurar com atualização preservando dados, nunca desinstalar/limpar dados.
