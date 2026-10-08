# Duas versões atuais

O mantenedor pediu um único backup do projeto, somente dois instaladores atuais e limpeza de APKs anteriores/temporários. Histórico de fontes permanece no Git.

| Canal | Versão | Uso |
|---|---|---|
| `stable-2p` | R76 | Referência de dois jogadores escolhida pelo mantenedor. Houve partida física; engasgos anteriores continuam documentados. |
| `test-4p` | R81 | Candidata para até quatro, com correções de descoberta e apresentação dos perfis individuais/multiplayer. Depende da ativação v3 e de perfis exatos aprovados, inclusive para salas de duas pessoas. Não instalada nem homologada em quatro aparelhos. |

Backup único: `G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008`.

Leia `ACTIVE.json`, escolha explicitamente um canal e use suas fontes completas congeladas. Não selecionar APK por data, procurar a versão com maior número ou recuperar uma Activity de outra revisão. A R81 substitui somente o instalador de teste R79; a referência estável permanece R76.

## Efeito arquivado

`PENDING-VISUAL.json` registra o LED Dreamcast em `versions/station-dreamcast-led-r80-20261008` como **arquivado, sem integração automática**. O mantenedor confirmou que as capas atuais são diferentes das 26 artes usadas na referência. O efeito só poderá ser aplicado após novo pedido e conferência da moldura correspondente. Não há APK R80 nem instalação; o efeito não foi incorporado à R81.

## Fontes e reprodução

`rebuild_verified.py` verifica o APK, os 201/209 Java e as dependências do carrossel; com `--build both --output <pasta nova em E:>`, reproduz o DEX e a biblioteca e exige hashes idênticos. Não usa receitas de sobreposição de versões antigas. Ferramentas JDK/SDK/NDK instaladas e chave original foram preservadas; não apagar como temporários.

Para uma alteração futura, partir de uma cópia de trabalho do canal escolhido, registrar nova versão/manifesto e preservar os hashes da referência. As receitas históricas em `versions/` registram compilações passadas; alguns caminhos de APKs nelas foram aposentados pela limpeza autorizada. Instaladores atuais são somente os de `ACTIVE.json`.

Backup inclui os APKs exatos, fontes Java completas, fontes e dependências do carrossel, fontes nativas dos motores, histórico Git e recibos. APKs, objetos, mídia e arquivos locais de assinatura não são enviados ao Git. A chave original e o backup privado preexistente de assinatura permanecem em seus locais protegidos.

## Conferência da R81

As 209 fontes Java da R81 foram compiladas e seus DEX conferidos com o pacote assinado. Somente `classes35.dex` mudou em relação à R79; os 13.225 demais arquivos do pacote e os 59 vídeos foram preservados. Runtime, cores, engines e carrossel permanecem idênticos à R79. A consolidação confere as fontes, entradas e binários por hash, sem recompilar receitas históricas.

O APK R81 ainda não foi instalado. Últimas instalações comprovadas: Motorola R79 e Samsung R78. Os testes locais não qualificam gameplay Android, quatro aparelhos ou estabilidade WAN. Produção permanece v2, sem perfis reais v3 aprovados. A publicação do catálogo 19 já permite receber as sinopses pelo fluxo vigente; não depende deste APK.

Na conferência anterior da R79 no Motorola, capa/nome/plataforma/avaliação de Battletoads e estado Online estavam visíveis, assim como a sinopse de Bust-A-Move 4. Isso não demonstra a ativação das novas salas.

O recibo `versions/station-online-readiness-r81-20261008/evidence/consolidation.json` registra a substituição do canal, a preservação da referência R76 e do efeito arquivado e a remoção das duas cópias aposentadas após verificar o backup completo.

## Limpeza pendente

A R81 foi copiada e verificada. A pasta R79 e o APK temporário R81 em E: estão preservados enquanto a autorização para removê-los é resolvida. ACTIVE.json seleciona R76/R81; há temporariamente três APKs no backup. O recibo de consolidação registra esta pendência.
