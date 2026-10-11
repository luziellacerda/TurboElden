# R118 — alterações detalhadas do visual e da preparação gráfica

## Base e estado desta entrega

A R118 parte da fonte R117 publicada no commit `129ee9db892a327f720df8ae4f8e8a5ffab3f7ee`. A base privada da receita é o APK R117 SHA-256 `fce3be2821abcb89da05b18370a36dadc0a78f1f5f8381ccbc8a0ba2c2645372`. A fonte desta entrega está em `versions/station-visual-refinement-r118-20261010`; ramo previsto `fix/station-visual-refinement-r118-20261010`.

Este documento descreve as fontes congeladas. **Compilação, assinatura e instalação direta no Motorola concluídas. SHA integral instalado, UID/data/instalação original conferidos. Conferência visual completa, térmica e gameplay ainda pendentes.** Os recibos novos e `STATUS.json` devem registrar o resultado efetivo de cada etapa. A descrição R117 foi preservada em `ALTERACOES-R117-HERDADAS.md`.

São 230 fontes Java e 123 entradas de fontes/inputs nativos identificadas na preparação. A contagem não significa que todos esses arquivos foram modificados. Não houve leitura adicional de handoff, mudança de contrato, novo motor online, implantação ou reinício do servidor nesta revisão visual.

## 1. Menu online com cores compatíveis com as ondas

Arquivo: `java/netplay-src/org/emulationstation/frontend/netplay/StationRoomsActivity.java`.

- Superfícies azul-marinho e destaques ciano. O campo existente `green` passa a conter `0xff7ad9f1`; texto principal `0xfff1f6ff` e texto secundário `0xffa7b7cf`.
- `styleAction` harmoniza ações primárias, secundárias e de saída, com estados desabilitado, pressionado e foco. A ação de saída continua distinta.
- `styleNavigation` trata a navegação selecionada sem modificar as seções ou seus callbacks.
- `pill`, `card`, `panel` e `field` usam a mesma família de cores. Participantes, conversa, modo e quantidade de jogadores acompanham esses tons.
- Modais continuam opacos para leitura; telas que já não tinham moldura externa continuam sem ela. A marca de apresentação dos diálogos passa a ser TURBOSTATIONS / JOGAR ONLINE.

Alvos de toque de 48 dp, ícones semânticos, ordem das ações, visibilidade por estado e habilitação por capacidade foram preservados. Não foi adicionado ciclo de animação nem tarefa de rede para produzir essas cores. Botões e renderers de capa continuam sendo os componentes existentes.

## 2. Capa de “Estou pronto” com a mesma viewport de Criar/Modo

Arquivo: `StationRoomsActivity.java`, principalmente `roomViewportHeight`, a montagem de `ownRoomCard` em `paint` e o observador de tamanho de `middlePanel`.

Antes, Sua sala/Estou pronto usava `StationCreateGameCard` com altura de conteúdo (`WRAP_CONTENT`, `-2`), dependente dos textos, participantes e ações. Criar sala e Modo já usavam `setViewportBounded(true)` com a altura útil do painel.

Agora, Sua sala/Estou pronto também usa `setViewportBounded(true)` e a altura útil do painel. A política é a mesma de `StationCreateGameCard`/`StationCoverLayout` na preparação:

```text
gap = 12 dp
larguraPreferida = screenHeight × 0,790 × 0,828
larguraDisponível = min(larguraPreferida, W − 220 dp − gap)
larguraDaCapa = min(H × aspectoDaCapa, larguraDisponível)
alturaDaCapa = min(H, larguraDaCapa / aspectoDaCapa)
```

W e H representam o espaço útil do painel; limites mínimos e arredondamentos continuam nos componentes existentes. Não é imposto um número fixo de pixels a todos os aparelhos. O observador de layout atualiza a altura quando o painel muda de tamanho.

Informações e controles de prontidão ficam em um `ScrollView` dentro da coluna de ações. Uma sala com mais participantes pode mostrar todo o conteúdo sem determinar o tamanho da capa. Bitmap, `StationOnlineCoverView`, aspecto real, mapa da plataforma e LED vêm do mesmo motor/cache. Essa mudança não cria arte ou tabela de LEDs.

## 3. Explicações de uso sem referências técnicas

Arquivo: `StationRoomsActivity.java`, métodos `playGuidance`, `onlineNotice`, `showGameDetails`, `roomExplanation`, `roomSetupDescription`, `renderRoomSetup` e `renderHeroPlayerInfo`.

O filtro atua na apresentação de explicações de modo, instruções de participação, Como jogar, informações de jogadores e avisos relacionados. Remove URLs e frases de referência ao Git/GitHub, handoff, repositório, commit e outros termos internos. Cabeçalhos de fontes técnicas são omitidos; as fontes do perfil deixam de ser listadas na seleção do modo.

O filtro não é aplicado globalmente ao helper `text`. Nomes dos jogos, sinopses do catálogo, nomes/apelidos dos jogadores, códigos de convite e mensagens de conversa permanecem intactos. Um nome de jogo com HTTP, por exemplo, não passa pelo filtro de instruções.

`profileInfo`, `roomGameInfo`, `displayHelp`, os perfis assinados e seus campos `instructions`/`sources` continuam como antes. A limpeza ocorre depois da validação, no ponto de exibição. Capacidades, quantidades permitidas, `profileId`, hashes, identidade da edição e aprovação do motor não são removidos ou reinterpretados para habilitar uma ação.

`onlineNotice` mantém avisos úteis e troca “servidor” por “serviço online”. Conteúdo formado somente por referência técnica recebe uma explicação curta de indisponibilidade ou falha da ação. A falta de suporte da sessão continua impedindo o início e sendo informada explicitamente.

Instruções práticas, como escolher batalha e atribuir controles aos participantes, continuam disponíveis. Criar, Entrar, Pronto, Iniciar, Sair, convite e conversa mantêm os mesmos comandos.

SHA-256 da fonte online final: `ec78f2fb1f1de5bd244b968bc560f60721357f1e832e88758044a11d54ce0ab3`.

## 4. Região do LED pronta antes das parcelas de halo

| Arquivo | Preparação alterada |
|---|---|
| `native/d0/premium-magazine-led-android.glsl` | Uniforme `magazineRegionOnly` e saída da região geométrica sem a busca pesada dos emissores |
| `native/d0/magazine_shader.h` | Representação embutida do shader nativo com esse caminho |
| `native/d0/native_magazine_field.h` | Inicialização geométrica integral do candidato antes da publicação progressiva |
| `java/netplay-src/org/emulationstation/frontend/netplay/StationCoverLightingShader.java` | Caminho equivalente no shader online, com a disposição de canais usada por esse renderer |
| `java/netplay-src/org/emulationstation/frontend/netplay/StationOnlineCoverView.java` | Passagem geométrica no worker EGL existente; depois, retomada das parcelas pesadas |

O campo candidato recebe a região completa em uma primeira passagem geométrica. Emissores e halo continuam incrementais: **quatro linhas por quadro e 16 amostras**. O objetivo é evitar que a região que controla a recoloração da arte exista apenas nas linhas já concluídas, alterando a cor durante a preparação.

Essa passagem não executa as 16 buscas de halo para toda a textura. A iluminação termina suas parcelas no mesmo fluxo; ganho, relógio, rastro, halo e equações da cor final não recebem novo preset. Transparência do letterboxing e separação entre campo ativo e candidato continuam respeitadas.

Custo da primeira passagem no GPU e aparência resultante ainda precisam ser observados no aparelho. Não existe medição R118 que comprove a eliminação de um atraso físico de oito segundos, menor consumo ou redução de temperatura.

## 5. Ondas como padrão e opções somente nas Configurações

| Arquivo | Alteração |
|---|---|
| `java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java` | WAVES como padrão e migração única `background_default_r118` |
| `java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPanel.java` | Duas colunas em paisagem com largura mínima de 520 dp |
| `native/d0/native_graphics.h` | Fallback inicial do snapshot com efeitos ativos e Ondas |
| `native/d0/native_graphics_ui.h` | Botão rápido removido: desenho sem trabalho e toque retorna false |

A migração usa o arquivo de preferências R117. Céu legado muda para Ondas uma única vez; chave geral, controles individuais e fundo desligado são preservados. Após a migração, uma escolha explícita de Céu permanece e não é substituída na próxima abertura.

Configurações → EFEITOS mantém a chave geral e as seis escolhas: LEDs, vídeos do carrossel, fundo animado, ícones/Lotties, efeitos das células e transições. Ondas, Céu e Sem fundo continuam selecionáveis. Desligar a chave geral conserva as escolhas individuais. O botão geral não é mais desenhado nem captura toques no carrossel principal.

## 6. Loading inicial preto, barra e percentual

Arquivos: `frontend/station_frontend.cpp`, `native/d0/native_carousel.cpp` e `native/d0/native_skin.h`.

`StationLoading_draw` usa superfície preta, barra e percentual. A interpolação visual é limitada pelo trabalho concluído informado pela preparação; não inventa progresso por tempo decorrido. Em caso de falha, permanece um aviso curto de carregamento.

Durante a preparação inicial:

- O fundo retorna antes de preparar/desenhar shaders ou imagens decorativas.
- Cabeçalho, avatar, ícones e ações decorativas não são desenhados nesse estado.
- O pós-render do carrossel retorna antes dos efeitos adicionais.
- O prewarm dos programas LED espera a saída do loading inicial.

Esses bloqueios não mudam preparação do catálogo, fila de capas, preload limitado ou cache persistente. A preparação necessária continua; o trabalho decorativo listado fica suspenso.

## 7. Preservação da R117

Fila única de IO/decode de capas, prioridade visível, cache por revisão, continuação sequencial, cancelamento e retomada de lifecycle permanecem. Vídeos continuam locais, com uma passagem e retenção dois quadros antes do fim. Vídeos desligados mantêm a apresentação estática disponível.

Menus continuam a 30 FPS; emuladores mantêm suas taxas. Controles, motores, registro online, assinatura/autenticação, ordem dos estados, paginação independente, recuperação de consultas, downloads e dados de licença/jogos/saves não são alterados pelo pedido visual.

## 8. Compilação, evidências e pendências

Compilação completa: **concluída**, duas DEX e duas bibliotecas UI, recibo `evidence/build-r118.json`. Assinatura v2/v3 com certificado original e alinhamento 16 KiB conferidos em `evidence/package-r118.json`; SHA-256 final `960b62397fdff20491a5b842dcab0451fade5d786beb84c40e6a9d91ae456e42`, 2.217.033.096 bytes. Apenas quatro entradas UI mudaram; 13.543 outras entradas são byte idênticas à base R117, além de engines.json preservado. Compilações Java isoladas das fontes modificadas verificam a compilação; não são testes de comportamento, shader ou gameplay.

Receita `build.py` e argumentos `recipes/build-r118-arguments.json`: base R117 exata, duas DEX e duas bibliotecas UI recompiladas, demais entradas preservadas, mesma assinatura e alinhamento 16 KiB. Resultados posteriores devem constar em `evidence/build-r118.json`, `evidence/package-r118.json` e recibo de instalação correspondente.

Nenhum teste novo foi criado ou executado nesta revisão. Arquivos/recibos R117/R116 copiados da base são históricos; não validam R118 nem cedem suas contagens a este candidato.

Conferências físicas pendentes: cores e legibilidade online; capa em Criar/Modo/Sua sala; preparação do LED ao trocar capa e entrar no online; loading preto; migração única do fundo e aba EFEITOS. Medição térmica e gameplay R118 continuam pendentes. Não houve promoção a estável.

Publicação: fontes, receitas, manifestos e recibos agregados. APK, mídias/artes privadas, objetos privados, credenciais, capturas e dados pessoais permanecem locais.

## Instalação desta entrega

R118 instalada diretamente no Motorola Edge30 em 11/10/2026 às 01:26 UTC, sem APK extra no telefone e sem desinstalação/limpeza. SHA integral `960b62397fdff20491a5b842dcab0451fade5d786beb84c40e6a9d91ae456e42` conferido; UID, diretório de dados e primeira instalação preservados. Recibo `evidence/installation-motorola-r118.json`. Samsung não atualizado nesta entrega.

Leitura posterior à instalação confirmou ESActivity/carrossel autenticado com Ondas e ausência do atalho geral de efeitos. Somente observação da tela, sem alternar configurações, criar sala, iniciar gameplay ou medir desempenho. Recibo `evidence/post-install-observation-r118.json`; captura privada excluída do Git. Não valida a formação temporal do LED nem as telas de prontidão.
