# Alterações detalhadas da R116 — 10/10/2026

A R116 é a versão instalada nos dois aparelhos e preparada para publicação no ramo `fix/station-cover-sequential-r116-20261010`. Ela contém a evolução de renderização e carregamento feita após a restauração da R99. O delta executável específico da R116 sobre a R115 contém sete alterações Java e substitui apenas `classes28.dex` e `classes35.dex` no APK. A R116 não altera as bibliotecas nativas, o protocolo de partida ou o cadastro de motores do servidor.

## 1. Base e trajetória integrada

A base funcional adotada foi a R99, em `versions/station-server-integration-r99-20261009`. A R100 de modo leve foi rejeitada pelo mantenedor e não é a base desta publicação. As mudanças posteriores foram conciliadas sobre a fonte atual, preservando o funcionamento da R99. As etapas abaixo já estavam integradas na R115 e são heranças da R116, não sete correções adicionais feitas nesta revisão.

| Etapa herdada | Problema e comportamento integrado |
| --- | --- |
| R99 | Base de integração do servidor, menus online, controles, catálogo, downloads, emuladores e runtime usados pela sequência posterior. A identificação dos motores pertence à base e não recebe novo runtime pela R116. |
| R101/R102 | Reduzem recomposição repetida de textos e layout quando texto, seleção, dimensões e revisão permanecem iguais. A ponte do nome de perfil permite ler a revisão e copiar somente quando muda. As chaves de texto/layout preservam métricas, tamanhos e o visual pedido. O menu usa espera SDL em cadência de 30 fps, sem espera ocupada. |
| R103/R104 | Limitam o trabalho do shader ao suporte conservador da iluminação e omitem amostras comprovadamente incapazes de mudar o resultado. O núcleo condicional preserva emissor, halos de oito direções em 2 px e oito em 5 px, cor, ganho, velocidade e rastro. |
| R105/R106 | Transferem a classificação constante da moldura para os quatro vértices, primeiro no carrossel e depois na capa online. Consultam a capacidade de textura no vertex shader e mantêm retorno ao caminho direto em falha. |
| R107–R109 | Integram o campo estático da capa online, evitando refazer máscara e halos em cada quadro. O campo online atual é RGBA8. O fundo online atual é uma imagem estática de ondas desenhada quando muda o tamanho; não possui relógio, thread de animação ou invalidação periódica. O robô continua em loop quando visível e com foco. |
| R110 | Calcula o campo nativo RGBA16F e reutiliza seus componentes estáticos; o envelope animado continua dinâmico. Invalida o campo em criação, descarte e atualização da textura, inclusive quando o driver recicla o identificador GL. Um vídeo concluído passa a desenhar o quadro retido sem reabrir o decoder. |
| R111 | Recoloca os 58 vídeos de sistemas/coleções no caminho local: `AssetManager.openFd`. Remove a inicialização e os ticks do sincronizador remoto de vídeo. As classes remotas permanecem para compatibilidade, mas ficam inertes. O cache remoto de capas continua ativo. |
| R112 | Troca o marcador de instalação baseado em `lastUpdateTime` por uma identidade SHA-256 do conteúdo dos recursos. Uma atualização com o mesmo conteúdo deixa de recopiar os 199 recursos, 81.660.567 bytes, antes do primeiro quadro. Preserva arquivos extras do usuário e a regra de BIOS `replaceExisting=false`. |
| R113 | Persiste a prova de capa validada por identidade, revisão, tamanho e mtime; permite publicar seu caminho antes da solicitação assíncrona do renderer. O parser nativo aceita o campo opcional de caminho mantendo o layout binário de catálogo. |
| R114 | Indexa as capas durante `PREPARANDO SUA BIBLIOTECA`, com uma varredura limitada de cache privado e revisão exata. O índice distingue prova estrutural de validação completa e evita consulta individual repetida durante a publicação. |
| R115 | Usa diretamente o legado com revisão exata quando hard link não existe; limita o passe inicial a 64 tentativas/20 segundos. Mantém o mapa completo privado e publica a capa selecionada imediatamente, até nove itens visíveis e um vizinho por pulso de 80 ms. Divide a geração do campo LED em quatro linhas por quadro e mantém a capa base visível. |

As pastas históricas registram o estado de cada etapa no momento em que ela foi preparada. Um `compiled=false` herdado ou um recibo R112 não descreve o estado final da R116. A identificação do artefato atual é feita por `STATUS.json`, `evidence/package.json` e pelos recibos de instalação R116.

As heranças de renderização têm verificação estrutural e medições pontuais documentadas nas respectivas etapas. A publicação R116 não transforma essas medições em ensaio térmico controlado da versão atual.

## 2. Os dois congelamentos e o vínculo observado no código

O primeiro relato foi a entrada numa lista de jogos com várias imagens aparecendo ao mesmo tempo e a interface azul ou congelada. O segundo foi a tela online exibir a capa base e permanecer parada até começar o LED.

Havia duas fontes de contenção no caminho examinado: preparação/publicação de muitas capas junto com a entrada no sistema e consumidores de artwork que executavam leitura/decodificação em filas próprias. A geração do campo LED também havia sido monolítica antes da R115. Mesmo com o campo incremental, filas independentes de artwork ainda podiam competir pelo disco, decodificação e entrega de imagens.

A R115 tratou a publicação e o LED por parcelas. A R116 organiza a admissão dos consumidores restantes de capas, concede a prioridade ao que o usuário está vendo e só usa o intervalo disponível para completar o cache. A relação entre esses trabalhos é comprovada no código. O recorte físico da R116 demonstra carregamento progressivo e resposta à seleção no Motorola; não prova uma causa exclusiva para todos os congelamentos anteriores nem mede o primeiro quadro online.

## 3. Sete arquivos alterados na R116

Os caminhos desta tabela são relativos ao diretório `java/` desta versão. O manifesto contém 226 fontes de produção e identifica exatamente as sete diferenças contra a R115.

| Arquivo | Mudança específica R116 |
| --- | --- |
| `client/src/java/org/emulationstation/frontend/station/ExistingCoverCache.java` | Acrescenta diagnóstico agregado do cache histórico. Separa tabela/diretório ausente, tabela inválida, IDs/revisões conflitantes, revisão ausente/diferente, imagem ausente, arquivo rejeitado e aceito. Conserva validação fechada de identidade/revisão e não escreve IDs/caminhos no diagnóstico. |
| `client/src/java/org/emulationstation/frontend/station/StationCoverQueue.java` | Implementa a fila global com um worker e fila curta de nove entradas, trabalho explícito de artwork, prioridade da capa principal, conclusão opcional sequencial, cancelamento, geração do catálogo e retenção de pedidos durante preparação. Trata 429 com uma retomada limitada e mantém contadores agregados por passe. |
| `client/src/java/org/emulationstation/frontend/station/StationCoverStore.java` | Expõe os dados agregados de diagnóstico do legado e a recuperação das identidades frias à preparação atual. Mantém cache canônico exato, validação de imagem, persistência atômica, provas v1/v2 e uso direto do legado validado. |
| `client/src/java/org/emulationstation/frontend/station/StationDownloadPanel.java` | Passa a resolver caminho e decodificar artwork pela fila comum. Limita o cache de bitmaps a 8 MiB. Ao fechar, cancela handles, tentativas atrasadas e callbacks de lifecycle, e libera o cache. Pausar/continuar/cancelar e os arquivos de jogo seguem nos executores próprios. |
| `client/src/java/org/emulationstation/frontend/station/StationFrontend.java` | Torna a fila comum dona dos pedidos de capa, interrompe a geração anterior antes da preparação síncrona, publica o catálogo e entrega as faltas ao passe opcional. Expõe `coverWork`, registra diagnóstico agregado e preserva as regras de foreground/cancelamento. |
| `netplay-src/org/emulationstation/frontend/netplay/StationRoomArtwork.java` | Remove a fila própria de IO/decode e usa `coverWork`. A capa principal promove um pedido de miniatura com a mesma chave, conserva callbacks e invalida a tentativa antiga. Mantém cache de 8 MiB, amostragem/dimensões existentes e cancelamento por epoch da tela. |
| `netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java` | Solicita a capa principal e a capa do fluxo de entrada como alta prioridade. Mantém pedidos de miniatura em prioridade normal e o vínculo entre callbacks, item solicitado, epoch e Activity ativa. |

A fila Java serializa a resolução do caminho, IO remoto/local e `BitmapFactory` das telas Java. A decodificação e o upload de textura do renderer nativo continuam no caminho próprio do renderer, governados pela janela/revelação herdada. Não existe alegação de que operações GL executem no worker Java de capas.

## 4. Ordem de trabalho e lifecycle

### Preparação inicial

Antes do passe inicial, `quiesceForCatalog()` cancela a geração antiga, suspende novas admissões e espera o IO anterior sair, com limite de cinco segundos no worker de catálogo. A espera não ocorre na thread de UI. Esse limite evita deixar uma preparação nova presa indefinidamente por um transporte que não termina; em falha, o caminho de liberação da preparação permanece no `finally`.

O passe inicial herdado lê as provas/indexa o cache e tenta as faltas uma por vez. Termina por 64 tentativas ou 20 segundos, e também termina diante de falha de sessão/rede/limite de taxa. Esse teto permite abrir o catálogo mesmo quando há milhares de capas frias. Capas já persistidas com a identidade exata são puladas.

Pedidos nativos que chegam durante a preparação ficam retidos por identidade. Eles não recebem cancelamento a cada quadro. Na publicação, são rebaseados para a nova geração e retomam quando o carrossel volta ao primeiro plano. Pedidos explícitos de artwork também esperam a liberação da preparação, evitando um segundo IO paralelo.

### Depois da publicação

As identidades frias são deduplicadas e formam um plano limitado a 4.096 itens. O plano não publica milhares de tarefas no executor: admite uma tarefa opcional, espera terminar e só então admite a próxima.

Uma solicitação visível cancela a tarefa opcional corrente e recoloca a falta para depois. A capa principal online entra antes de miniaturas e substitui uma capa principal anterior obsoleta. A seleção nativa pode deslocar artwork opcional da central quando a fila está cheia, preservando pedidos visíveis nativos existentes.

O plano frio continua guardado se o catálogo terminar de publicar enquanto a `ESActivity` está pausada. Sua execução só retoma no foreground do carrossel. Uma tela online aberta pode continuar solicitando sua própria capa: `ESActivity` pausada não equivale a Activity online encerrada. Cada tela é responsável por cancelar seus handles ao parar ou fechar.

A conclusão bem-sucedida persiste o arquivo. Sair do app ou reiniciar o processo não perde os sucessos já gravados; uma abertura/publicação futura reconstrói o plano com as faltas atuais. A persistência não significa conservar um pedido cancelado em memória nem continuar IO opcional durante gameplay.

## 5. Cache, revisão e comportamento de rede

O nome canônico é `<coverId>-<revision>.img` em `station-v2/covers`. O ledger v1 representa validação completa; o índice v2 distingue validação completa `V` da prova estrutural `M`. Um arquivo inexistente, divergente, de tamanho inválido ou assinatura recusada permanece frio. Um arquivo estruturalmente aceito em cache privado não constitui garantia contra corrupção profunda futura: o renderer não oferece callback de falha de textura para autorreparo integral.

O legado é o formato confirmado `station-covers/revisions.tsv`, com `coverId<TAB>itemRevision` e uma imagem de extensão permitida. Os roots aceitos são `/data/data/org.turboramastation.frontend/no_backup/` e `/data/user/0/org.turboramastation.frontend/no_backup/`. Revisão divergente, tabela ausente, conflito ou arquivo não regular recusam reaproveitamento. Quando hard link não é possível, o caminho privado validado pode ser usado diretamente, sem copiar os bytes em massa.

A capa baixada passa pela validação de imagem e pela troca atômica existentes. A mesma identidade já concluída é reutilizada; uma revisão nova exige sua própria validação/arquivo. Isso permite reutilização offline do que já existe, sem prometer a capa de um jogo nunca baixado.

| Resultado do passe opcional | Comportamento |
| --- | --- |
| sucesso | persiste e avança para a próxima falta quando não existe trabalho visível |
| cancelamento por prioridade/lifecycle | guarda a identidade pendente e aguarda a condição de retomada |
| offline ou falha transitória | encerra o passe atual; outra abertura/publicação monta um novo plano |
| 401/403 | encerra o passe atual sem contornar sessão ou autenticação |
| 404 | encerra o passe atual, evitando varrer milhares de respostas ausentes |
| 429 | usa `Retry-After`, com espera limitada, e permite uma única retomada; repetição encerra o passe |

A política acima é da conclusão opcional de capas. Ela não cancela download de jogo nem encerra partida online. O download de jogos mantém persistência, pausa/cancelamento e recuperação de rede no executor próprio já integrado.

## 6. LED incremental e qualidade visual

A R116 não muda o shader ou o campo da R115. Os programas são pré-compilados no contexto GL do carrossel durante o loading. Ao selecionar uma capa, a imagem base aparece; um destino candidato separado produz no máximo quatro linhas por quadro. O nativo usa RGBA16F; o online usa RGBA8. O campo pronto substitui o confirmado somente se contexto, imagem/textura, revisão, modelo, viewport e dimensões continuarem compatíveis.

Troca de seleção/upload ou perda do contexto invalida o candidato. O estado GL modificado é restaurado em cada parcela. No online, a textura do efeito só recebe alpha após a conclusão, mantendo o `ImageView` base visível enquanto o efeito é preparado. Falha de shader, alocação, FBO ou capacidade mantém o caminho direto equivalente já existente.

Essa divisão evita exigir um único cálculo completo antes de voltar a desenhar a interface. Ainda pode haver espera até o LED ficar pronto. A quota de quatro linhas foi conservada por causa do custo por linha observado; não foi aumentada sem medição de frame pacing. Na R115 física, a conclusão online registrada levou aproximadamente 7.058 ms; esse valor é histórico e não uma medição online R116.

Regiões, halos, relógio, brilho, cores, velocidade e rastro mantêm os parâmetros anteriores. Os menus usam 30 fps por uma regra restrita ao `GuiStore` e às animações de menu. Os emuladores e o runtime de partida têm relógios próprios; esta regra não limita gameplay a 30 fps.

## 7. Compilação, identidade e dependências

Fonte local:
`C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git\versions\station-legacy-cover-diagnostics-r116-20261010`

Build:
`E:\ESTUDO APK\work\station-legacy-cover-diagnostics-r116-20261010\compiled-final`

APK final:
`G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R116-20261010.apk`

| Conteúdo | SHA-256 |
| --- | --- |
| APK R115 exato usado como base | `290b9e237c8ad158aac443ce5c11959004f7a28ab4844c4c3453721a288f0dcc` |
| APK R116, 2.218.343.816 bytes | `3c5fb1cb84330b4cea635152e65b7498bf6baf15192371789945fcaf861226c1` |
| `classes28.dex` R116 | `9ed018fcef4eb01fd4ef7d609a93cda592ce2b56792f772f62bc71277db79566` |
| `classes35.dex` R116 | `f48bdfaa466f031cff8a5bf127764218f01d111fb01e9e8ad22764feb3394d0d` |
| `libstation_frontend.so`, preservada | `3c9d6bfba6ef08ad4909c6e1338c7a2ccd5cf46f9bf0c9bf895910093d3c8b1e` |
| `libturbo_carousel.so`, preservada | `8b774382c71b18100fb2e70bd9d553307cabe615fcb6aaecc3047bb612d4b3a5` |
| `libstation_retroarch.so`, preservada | `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc` |
| Certificado de assinatura | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |

Assinatura v2/v3 e alinhamento de 16 KiB passaram. Todas as entradas de conteúdo fora dos dois DEX alterados são byte a byte idênticas à R115. O runtime online preservado não requer nova identidade de motor por consequência desta publicação.

`JAVA-SOURCE-MANIFEST.json` identifica 226 fontes atuais. `JAVA-SOURCE-MANIFEST-R115.json` é a referência local exata para conferir as sete diferenças sem exigir a pasta-fonte R115 no computador. A receita continua exigindo o APK privado R115 de hash exato, Android SDK, JDK, ferramentas de build e a assinatura local compatível. A chave de assinatura não é publicada.

`CAROUSEL-INPUT-MANIFEST.json` e o snapshot parcial nativo identificam a herança; não oferecem o código completo do frontend original nem um build nativo autossuficiente. A receita R116 recompila Java e preserva os binários nativos da base exata.

A publicação inclui fontes, receitas apropriadas, manifestos, testes e recibos sanitizados. Cinco receitas de medição `measure_motorola_*.py` são omitidas por conter identificação privada de aparelho. Capturas PNG, mídias, fixtures geradas de imagens, logs pessoais, APKs, ROMs, BIOS, licenças e chaves não são publicados.

## 8. Verificações realizadas

| Verificação existente | Resultado e alcance |
| --- | --- |
| compilação conjunta | 226 fontes Java de produção e quatro fixtures compiladas |
| fila global | `PASS 72 one-lane cover prefetch checks`: admissão, prioridade, plano sequencial, cancelamento e lifecycle em modelo isolado |
| diagnóstico de legado | `PASS 23 aggregate legacy-cover diagnostics checks` |
| marcador de recursos | `PASS 20 resource bundle marker checks`, herança R112 |
| cache/preindex | `PASS 54 cover warm-start checks; legacy-direct=executed` |
| caminho nativo de capa | `PASS 26 native warm-cover checks`, herança preservada |
| manifestos/delta | 226 fontes, sete diferenças R115 → R116; apenas dois DEX diferentes no APK |
| pacote | assinatura v2/v3, certificado e alinhamento 16 KiB aprovados |
| revisão de fonte | nenhum P0/P1 aberto no escopo R116 revisto após ajustes de lifecycle, prioridade e limpeza |

Os testes isolados validam os contratos e condições descritos, não equivalem a gameplay Android nem medição térmica. A fixture executou o caminho direto de legado no host; no aparelho medido o diretório legado estava ausente.

## 9. Instalação e conferência física

As atualizações foram feitas diretamente com substituição do pacote existente. Os horários abaixo são os valores locais informados pelo Android, sem atribuição a UTC.

| Aparelho | Instalação original | R116 |
| --- | --- | --- |
| Motorola Edge 30 | 06/10/2026 17:12:33 preservado | 10/10/2026 19:45:48; reinstalação explicitamente solicitada às 20:02:32 |
| Samsung A56 SM-A566E | 03/10/2026 16:17:03 preservado | 10/10/2026 20:21:43 |

Os dois reproduziram o SHA-256 integral do APK final. Diretório e dados existentes foram preservados, sem desinstalação ou limpeza. Nenhum APK adicional foi deixado no armazenamento compartilhado. A abertura do launcher foi aceita nos recibos de reinstalação Motorola e instalação Samsung. Os recibos não afirmam gameplay.

Na primeira abertura Motorola R116, o preindex leu 2.266 entradas, aceitou 2.264 e rejeitou zero em 1.569 ms. Registrou `canonicalMissing=1422`, `legacyDirect=0`, `legacyMissed=1422` e `tableStatus=directory-missing`. Esse diagnóstico comprova ausência do diretório de legado no aparelho observado; não há 1.422 imagens antigas comprovadas.

O passe inicial encontrou 3.685 identidades, 491 já prontas e 64 baixadas antes do limite, encerrando com `stopped=true` após 15.231 ms. A publicação produziu 3.685 itens com 2.327 capas quentes e agendou 1.358 faltas para o passe sequencial. O número agendado não significa que todas concluíram nessa janela.

Na lista SNES, a captura em 500 ms já mostrava capa principal, textos e cinco miniaturas; a sexta estava visível até 2,5 s. Um swipe durante o passe opcional trocou o jogo e atualizou sua capa principal em cerca de 550 ms. Os LEDs permaneceram visíveis e não foram observados FATAL ou ANR nessa janela. A configuração temporária de tela ligada foi restaurada ao terminar a conferência.

## 10. Limitações explícitas da entrega

A instalação/hash estão confirmados nos dois aparelhos. A prova física de carregamento progressivo pertence ao Motorola e cobre primeira abertura e lista/carrossel SNES. Não houve validação física equivalente do Samsung após instalar.

O primeiro quadro online não foi acionado de forma confiável pela automação: a Activity não é exportada, o APK não é depurável e os toques tentados não abriram a tela. Permanecem sem prova física R116 a promoção da capa online, o retorno online → carrossel, corridas de lifecycle, fechar a central durante decode, offline/429 e o reaproveitamento de cache legado num aparelho que realmente o possua.

Não há gameplay em dupla R116, ensaio prolongado de estabilidade nem comparação térmica controlada. A R116 está instalada e pronta para teste, com verificações locais concluídas e validação física parcial. A publicação não altera os canais históricos de estável de dois jogadores e testes de quatro jogadores nem promove automaticamente esta versão a estável.
