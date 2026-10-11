# Online compacto — R123

Base: R122. Alterações restritas a `StationRoomsActivity.java` e `StationActionButton.java`.

## Fluxo e proteção

| Etapa | Apresentação | Autoridade preservada |
| --- | --- | --- |
| Escolher jogo | Catálogo e capa existentes | O identificador continua sendo o do item escolhido. |
| Criar sala | O nome permanece no cabeçalho principal; o corpo não repete outro título grande. | `createRoom` continua obtendo somente perfis verificados. |
| Modo e quantidade | Opções com largura natural, agrupadas; face visual de 32 dp dentro de alvo de 48 dp. Resumo curto; instruções completas por toque. | Mesmos perfis, seleção, quantidades permitidas e validação de contexto. |
| Preparação e criação | Mantém os estados de conferência/criação. | Mesmos `prepareRoom`, `sameRoomSetupProfile`, `createVerifiedRoom` e confirmação da resposta. |
| Aceitar entrada em sala | A confirmação humana continua existindo. Ações agrupadas, sem marca/sinopse repetidas no painel. | `join` e `joinConfirmed` permanecem idênticos; não sai de uma sala antes de preparar e verificar a nova. |
| Sua sala | Jogo no cabeçalho principal, ocupação e nomes/posição/prontidão continuam visíveis. Sem título/sinopse repetidos. Ações lado a lado; quebra de linha somente quando não couberem. | Mesmo `ready`, `leave`, conversa, convite e autorização de anfitrião. |
| Iniciar | Um único botão. A segunda tela “Tudo pronto para jogar” foi retirada. | Antes do comando, valida prontidão, identidade da sala exibida e transporte; valida novamente no executor. |

O botão Iniciar captura o fingerprint do **snapshot usado para construir aquele botão**. O executor lê o estado atual, usa `StationRoomStartState.reason`, confere o fingerprint e o transporte disponível, e somente então envia o mesmo comando `start` com `roomId`, `generation` e `transport`.

O fingerprint conserva, na mesma ordem, `instance`, `roomId`, `itemId`, `generation`, `profileId`, `profileSha256`, `capacity` e `roster`. Acrescenta `hostId`, `recoveryProtocol`, `members` e `ready` para detectar alterações em salas legadas sem `roster`. Isso é uma proteção local do que foi exibido; não modifica o protocolo, o payload, a assinatura ou a decisão do serviço.

`action()` ainda marca `busy` sincronamente, antes de enfileirar o trabalho. O segundo toque durante a mesma solicitação não envia outro início. Os participantes, quantidades permitidas, slots distintos, P1, prontidão e disponibilidade de transporte continuam sendo validados pela classe original e pelo serviço.

Quando uma solicitação falha, o callback que ainda pertence à Activity ativa e ao mesmo `epoch` limpa `busy` e reavalia `updateStartState()`. Isso reabilita Iniciar se a sala continua válida, sem aguardar outra revisão do polling. A mensagem original de erro permanece em `status`; não há repetição automática da solicitação, mudança de rede ou de timeout. Callbacks antigos ou após a saída continuam sendo ignorados.

## Apresentação

- Menu esquerdo sem cabeçalhos de agrupamento/margens repetidos; os alvos continuam em 48 dp.
- Navegação usa um seletor próprio: nenhum estado desenha uma caixa preenchida. Seleção usa texto/ícone ciano e marcador de 2 × 14 dp; foco/pressionado usam marcador branco. Desabilitado continua com texto atenuado e fundo transparente. O tint é removido após a troca do background.
- Na sala, os nomes usam 14 sp, até duas linhas, sem reservar uma segunda linha vazia para nomes curtos. Papéis, nomes e prontidão continuam vindos do mesmo `StationRoomRoster`.
- O agrupador de ações mede texto/ícone/padding reais durante layout. Cada alvo tem 48 dp de altura e largura mínima de 48 dp quando a área útil comporta isso. O excesso passa para outra linha; os botões não são esticados por toda a largura.
- A mensagem de prontidão só ocupa altura quando existe espera, preparação ou solicitação em andamento. O estado permitido do botão continua sendo calculado sempre.
- Um aviso idêntico ao status global não é repetido acima das ações. Mensagens distintas, erro, preparação e motivo acessível do botão Iniciar permanecem.
- Detalhes/instruções não foram apagados: ficam disponíveis por toque em “Sua sala” e no resumo da configuração.
- Chips de modo/quantidade mantêm 12 dp de respiro lateral, reaplicado depois de `setBackground`, pois o Android adota o padding do drawable ao trocá-lo. A altura do resumo é natural, até três linhas; a área não recebe `weight=1` nem `fillViewport`.

Não foi prometida ausência universal de rolagem: cinco participantes, fonte ampliada ou janela muito estreita podem precisar dela para manter informações e alvos acessíveis. A redução elimina conteúdo repetido e barras de ação vazias; não esconde jogadores para caber.

## Código preservado

Os métodos de criação, preparação, entrada, comandos, lançamento, lifecycle e reuso das capas foram comparados à R122. Também permanecem idênticos os arquivos `StationRoomStartState`, `StationRoomState`, `StationRoomRoster`, `StationOnlineClient`, `StationOnlineGame`, `StationRetroLaunch`, `StationOnlineCoverView`, `StationCreateGameCard`, `StationFlowPanel`, `StationCoverLayout` e `StationRoomArtwork`.

Sem alteração de motores, controle, saves, slots, transporte, autenticação, API, cache de capas, TextureView, shaders, decodificação, vídeos, 30 fps ou gates de economia. Nenhum timer/animação contínua foi acrescentado.

## Evidência

Receita: `tests/verify_room_compact_r123.py`. Recibo: `evidence/room-compact-r123.json`.

- **3.203 casos / 23.202 verificações**: execução host de corpos reais de `startRoom`, `action`, `command`, `failure`, `roomConfirmationKey`, `roomControlLayout` e `StationRoomStartState`; callbacks reais da sala com stubs mínimos de UI.
- **332 casos / 1.640 verificações de drawable/padding**: corpos reais de `applyFace`, `navigationFace`, `choiceFace` e `applyChoiceFace` com stubs que registram seletores, cores, geometria e ordem de aplicação. Os estados da navegação não contêm preenchimento, e 128 reaplicações de chips conservam o padding.
- **100 guardas de fonte**: preservação comparada à R122 e de 17 corpos críticos exatos da fonte R123 inicialmente instalada, SHA256 `780a0bfa3580fc761ad1289bdf36f84dbf53188afd28065030806fe576a0ef44`.
- **Duas classes reais compiladas** contra Android API 34 e dependências da R122; hashes no recibo.

Cobertura: início válido em v1/v2/v3, capacidades permitidas, prontidão, anfitrião, slots/IDs inválidos, transporte indisponível, snapshot alterado antes do clique ou antes do executor, legado sem roster, double tap, ready/leave/conversa e agrupamento de até cinco ações em larguras diversas. Falha sintética no comando verifica a reabilitação de Iniciar, preservação da mensagem de erro e rejeição de callbacks com `epoch` antigo ou Activity inativa.

Esses resultados não são teste de janela/layout Android, toque, controlador físico, rede, temperatura ou gameplay. A apresentação e o fluxo nos aparelhos permanecem para conferência. O reparo da falha restringe-se à reavaliação da UI após limpar `busy`; polling e lifecycle continuam como na R122. Não há atribuição desse reparo aos ANRs anteriores.

## Correção após a conferência do aparelho

A primeira instalação R123 mostrou chips com textos encostados nas bordas, resumo ocupando espaço vazio e quatro caixas preenchidas na navegação. O padding era aplicado antes do background; o resumo estava em um ScrollView com altura ponderada e `fillViewport=true`. Essas duas relações foram corrigidas diretamente.

A cor das caixas correspondia à face desabilitada do seletor anterior, mas a captura/hierarquia consultada não prova quem propagou esse estado. Não se atribuiu o problema a APK antigo ou DEX duplicado: a conferência independente encontrou uma única definição das classes e o hash instalado correto. O novo ramo da navegação é transparente também nos estados desabilitado e pressionado; a correção não depende da hipótese sobre a propagação do estado.

As capturas privadas não foram publicadas. Os testes de drawables verificam comandos de desenho e ordem do padding, sem substituir a conferência dos pixels no aparelho atualizado.
