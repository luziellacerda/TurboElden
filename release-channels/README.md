# Duas versões atuais

O mantenedor pediu um único backup do projeto, somente dois instaladores atuais e limpeza de APKs anteriores/temporários. Histórico de fontes permanece no Git.

| Canal | Versão | Uso |
|---|---|---|
| `stable-2p` | R76 | Referência de dois jogadores escolhida pelo mantenedor. Houve partida física; engasgos anteriores continuam documentados. |
| `test-4p` | R79 | Candidata para até quatro, com a correção das salas e fallback Dreamcast. Depende da ativação v3/perfis do servidor; não homologada em quatro aparelhos. |

Backup único: `G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008`.
O histórico R78 já estava publicado antes da R79. Não confundir R78 com a referência estável de dois jogadores: R78 já herda o motor experimental R77.

## Próxima alteração

Efeito guardado para uso futuro: `PENDING-VISUAL.json` registra o LED Dreamcast em `versions/station-dreamcast-led-r80-20261008` como **arquivado, sem integração automática**. O mantenedor confirmou que as capas atuais são diferentes das 26 artes usadas na referência. O efeito só poderá ser aplicado após novo pedido e conferência da moldura correspondente. Não há APK R80 nem instalação; os dois instaladores continuam R76/R79.

Leia `ACTIVE.json`, escolha explicitamente um canal e use suas fontes completas congeladas. Não selecionar APK por data, procurar a versão com maior número ou recuperar uma Activity de outra revisão.

`rebuild_verified.py` verifica o APK, os 201/209 Java e as dependências do carrossel; com `--build both --output <pasta nova em E:>`, reproduz o DEX e a biblioteca e exige hashes idênticos. Não usa receitas de sobreposição de versões antigas. Ferramentas JDK/SDK/NDK instaladas e chave original foram preservadas; não apagar como temporários.

Para uma alteração futura, partir de uma cópia de trabalho desse canal, registrar nova versão/manifesto e preservar os hashes da referência. As receitas históricas em `versions/` registram compilações passadas; alguns caminhos de APKs nelas foram aposentados pela limpeza autorizada. Instaladores atuais são somente os de `ACTIVE.json`.

Backup inclui os APKs exatos, fontes Java completas, fontes e dependências do carrossel, fontes nativas dos motores, histórico Git e recibos. APKs, objetos, mídia e arquivos locais de assinatura não são enviados ao Git. A chave original e o backup privado preexistente de assinatura permanecem em seus locais protegidos.

Nova conferência R79: no Motorola, capa/nome/plataforma/avaliação de Battletoads e estado Online visíveis; sinopse de Bust-A-Move 4 visível. Cruzamento com revisão 18: 142/243 nomes Dreamcast encontram fallback, 101 permanecem pendentes. Não declarar cobertura integral nem gameplay multiplayer corrigido por essa conferência.

## Conferência final

Backup local conferido, com dois instaladores. As 201/209 fontes Java e ambos os carrosséis foram recompilados a partir das entradas consolidadas e produziram os mesmos DEX/bibliotecas das versões preservadas. Histórico antigo conserva também seis tags anotadas em referências locais arquivadas; não são canais de instalação nem foram publicadas automaticamente. A limpeza removeu 61 APKs anteriores/duplicados e saídas temporárias, preservando os módulos oficiais necessários dos emuladores.
