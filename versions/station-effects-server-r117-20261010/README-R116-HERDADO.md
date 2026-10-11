# R116 — capas sequenciais, prioridade visível e diagnóstico de cache

A R116 está compilada, assinada e instalada no Motorola Edge 30 e no Samsung A56. Ela reúne a base funcional R99, as otimizações de renderização posteriores, vídeos locais, preparação inicial de recursos e capas, publicação progressiva e LED incremental. A mudança específica R115 → R116 organiza a leitura de capas do carrossel, online e central de downloads em uma fila compartilhada, dá prioridade à capa em uso e conclui o cache em segundo plano.

O documento [ALTERACOES-DETALHADAS.md](ALTERACOES-DETALHADAS.md) descreve a trajetória integrada, os sete arquivos alterados, o comportamento das filas, cache, rede, lifecycle, LEDs, compilação, instalações e limites da conferência. O estado legível por ferramentas está em [STATUS.json](STATUS.json).

## Problemas tratados e alcance da conclusão

O mantenedor relatou congelamento ao abrir uma lista de jogos e, no online, uma capa já visível com a interface parada até o início do LED. A inspeção do código confirmou caminhos independentes de leitura e decodificação de capas concorrendo com a publicação visual e a preparação do efeito. A R115 já havia dividido a publicação e o campo LED em parcelas; a R116 reúne os consumidores Java de capas e impede que a conclusão opcional do cache dispute a fila com a capa selecionada.

Isso confirma a contenção no código e explica por que os reparos precisam ser integrados. A janela física disponível não prova que essa era a causa exclusiva de todos os congelamentos relatados, nem valida o primeiro quadro online.

## Comportamento atual

- Na preparação inicial, indexa o cache persistido e executa um passe remoto limitado a 64 tentativas ou 20 segundos.
- Publica imediatamente a capa selecionada e revela os vizinhos em uma janela de até nove itens, um por pulso de 80 ms; essa regra é herdada da R115.
- Após publicar o catálogo, agenda somente uma capa fria de cada vez. O arquivo concluído é gravado atomicamente na identidade exata `coverId+revision`.
- Capa selecionada e capa principal online passam à frente do passe opcional. A capa principal pode promover uma miniatura pendente preservando callbacks.
- Carrossel, artwork online e artwork da central compartilham a fila de IO; os bitmaps Java são decodificados nela. O renderer nativo continua com sua publicação progressiva, sem reconstruir a lista inteira por caminho recebido.
- O plano opcional pausa com o carrossel. Pedidos explícitos da tela online continuam admitidos quando `ESActivity` está pausada.
- A central mantém um cache de bitmaps limitado a 8 MiB e cancela handles e tentativas atrasadas ao fechar. O download dos arquivos de jogos usa seu executor próprio.
- Offline, erro transitório, 401, 403 ou 404 encerram o passe opcional atual. Uma nova abertura/publicação forma um novo passe com as faltas restantes. Em 429, respeita `Retry-After` e permite uma única retomada por passe.

## Cache legado seguro e diagnosticável

Uma capa antiga só pode ser reutilizada com revisão exata em `station-covers/revisions.tsv`, arquivo privado regular, tamanho limitado e assinatura PNG/JPEG/GIF/WebP. Os caminhos privados aceitos são os dois roots Android de `no_backup` já usados pela R115. Não há dependência de `/files` nem confiança no nome de arquivo sozinho.

A R116 acrescenta contadores agregados sobre tabela ausente ou inválida, revisões faltantes ou divergentes, arquivos rejeitados e aceitos. IDs, nomes de arquivo e caminhos privados não entram nesse diagnóstico. `canonicalMissing` significa falta no cache canônico; não comprova a existência de imagem legada.

## LEDs, vídeos e cadência

O LED incremental da R115 permanece: a capa base fica visível enquanto um campo candidato separado produz até quatro linhas por quadro. O campo nativo usa RGBA16F; o online usa RGBA8. Somente o campo completo e ainda compatível é publicado, com restauração do estado GL e retorno ao shader direto em falha. A qualidade e os parâmetros visuais não foram alterados pela R116.

Os 58 vídeos de sistemas e coleções continuam locais no APK, abertos pelo `AssetManager`, sem sincronizador de vídeo remoto ativo. Os menus mantêm 30 fps; essa cadência pertence ao menu e não altera o relógio dos emuladores. O robô continua em loop enquanto visível e com foco, e o fundo online é a imagem estática de ondas herdada.

## Artefato e integridade

| Campo | Valor |
| --- | --- |
| Base executável exata | R115 |
| SHA-256 da base | `290b9e237c8ad158aac443ce5c11959004f7a28ab4844c4c3453721a288f0dcc` |
| SHA-256 R116 | `3c5fb1cb84330b4cea635152e65b7498bf6baf15192371789945fcaf861226c1` |
| Tamanho | 2.218.343.816 bytes |
| Java | 226 fontes; sete alteradas desde R115 |
| Entradas diferentes no APK | `classes28.dex`, `classes35.dex` |
| Demais entradas | byte a byte idênticas à R115 |
| Assinatura e alinhamento | v2/v3 e 16 KiB aprovados |

APK local: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R116-20261010.apk`

Build local: `E:\ESTUDO APK\work\station-legacy-cover-diagnostics-r116-20261010\compiled-final`

Fonte: `versions/station-legacy-cover-diagnostics-r116-20261010`

O pacote final é identificado por [evidence/package.json](evidence/package.json). Os manifestos Java e de entradas nativas identificam os conteúdos da compilação. A receita exige o APK privado da base e as ferramentas locais; os binários, mídias e chave de assinatura não fazem parte da publicação Git. O snapshot nativo identifica o conteúdo herdado e não é uma árvore completa para recompilar o frontend original.

## Instalações confirmadas

Todos os horários abaixo são os horários locais retornados pelos aparelhos, sem conversão ou atribuição a UTC.

| Aparelho | Instalação original preservada | Atualização R116 |
| --- | --- | --- |
| Motorola Edge 30 | 06/10/2026 17:12:33 | primeira atualização 10/10/2026 19:45:48; reinstalação solicitada 20:02:32 |
| Samsung A56 SM-A566E | 03/10/2026 16:17:03 | 10/10/2026 20:21:43 |

O hash integral instalado coincide com o APK R116 nos dois aparelhos. A atualização foi direta, preservando o diretório existente, jogos, saves e licença, sem desinstalação ou limpeza. Não foi copiado um APK extra para o armazenamento compartilhado. Recibos: [Motorola](evidence/installation-motorola-r116.json), [reinstalação Motorola](evidence/reinstallation-motorola-r116.json) e [Samsung](evidence/installation-samsung-r116.json).

## Verificações existentes

Compilação conjunta de 226 fontes Java e quatro fixtures; 72 verificações da fila, 23 de diagnóstico agregado, 20 do marcador de recursos, 54 de cache e 26 do caminho nativo de capas passaram. Assinatura, certificado, alinhamento, delta de pacote e manifestos foram conferidos. A revisão independente da R116 não deixou P0/P1 aberto no escopo revisado.

No Motorola, o preindex terminou em 1.569 ms e publicou 2.327 capas quentes de 3.685 itens; 1.358 faltas foram agendadas para conclusão sequencial. O passe inicial baixou 64 capas em 15.231 ms. Esses números registram aquela abertura, não a conclusão integral do catálogo. O diretório legado não existia no aparelho e o reaproveitamento físico de legado não foi exercitado.

Na lista SNES, em 500 ms estavam visíveis a capa principal, textos e cinco miniaturas. A sexta apareceu até 2,5 segundos. Durante a conclusão em segundo plano, um swipe atualizou a seleção e a capa principal em cerca de 550 ms. O LED permaneceu ativo; não foi observado FATAL nem ANR nessa janela.

## Limites da validação

A instalação foi comprovada nos dois aparelhos; o recorte físico de carregamento progressivo é do Motorola. O primeiro quadro online, retorno entre telas, fechamento da central durante decode, rede ausente e resposta 429 ainda não foram conferidos fisicamente na R116. A abertura automatizada da Activity online não foi conclusiva porque ela não é exportada, o APK não é depurável e os toques tentados não ativaram a tela.

Não houve gameplay R116 ou ensaio térmico prolongado. Esta publicação registra uma versão instalada com validação parcial; não constitui promoção automática a estável nem promessa de ganho térmico. Evidências antigas dentro da pasta estão identificadas como herdadas e não substituem os recibos R116.
