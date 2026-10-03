# HUD nativo LZ Games / Turborama — proposta de fonte

**Estado R2:** revisão de fonte pronta, com compilação Android em andamento pelo responsável. Ainda não instalada nem conferida no aparelho. A R1 foi compilada e instalada, mas falhou visualmente: os textos ficaram sobrepostos no canto superior esquerdo. Não promover esta revisão a estável apenas pelos testes de fonte.

**Revisão responsiva e de desenho concluída nos fontes:** usa fontes próprias, medidas completas e regiões limitadas à janela. Agora a chamada `Text::drawScaled` controla posição absoluta e escala; `Text::draw` original descartava a transformação anterior do chamador. O HUD principal tenta acomodar as cinco ações antes de aceitar o tamanho local da fonte, mantendo rolagem quando necessária. Todos os **21 testes** passaram: 18 contratos e três guardas do aplicador, incluindo compilação do helper C++ de layout real em **576 combinações**. Não há falha esperada desativando regressão. Esses testes não comprovam renderização Android.

## Base e destino

- Upstream: `Rakashazi/emu-ex-plus-alpha`, commit `1c12fac5ce49badaadff2e2f210dcc30b89f4943`.
- Aplica-se ao framework compartilhado pelas compilações completas **Snes9x EX+** e **MD.emu**.
- O patch adiciona uma interface nativa do framework, liga ações semânticas e acrescenta `Text::drawScaled` ao Imagine, preservando a assinatura de `draw` e seu comportamento na escala 1. Não troca controles, núcleo, arquivos de estado, caminhos ou configurações do usuário.
- Manter os avisos GPL e disponibilizar fontes correspondentes da revisão distribuída. Não alterar avisos/licenças dos motores.

## Interface

Fundo preto, cartões em verde escuro, foco verde vivo, detalhe vermelho na saída. Cabeçalho `LZ GAMES / TURBORAMA`, subtítulo `JOGO PAUSADO` e explicações em cada opção:

1. **Continuar jogo:** fecha apenas os modais e retoma a emulação.
2. **Salvar estado:** mostra dez posições, grava na posição escolhida e confirma qualquer substituição, mesmo se a configuração antiga dispensava a confirmação.
3. **Carregar estado:** mostra os estados existentes e suas datas; posições vazias ficam inativas. Pede confirmação antes de perder o andamento atual.
4. **Configurações:** abre a raiz original do emulador, mantendo vídeo/áudio/controles e demais recursos originais.
5. **Sair do jogo:** confirma retorno às plataformas e informa que a gravação automática depende das opções do emulador.

As posições visíveis 1–10 mapeiam explicitamente para slots nativos 0–9. Cada callback captura o slot nativo escolhido, sem usar o índice do item destacado. A chamada `setStateSlot` só acontece depois de salvar/carregar com sucesso. Falhas ficam no menu pausado e utilizam a mensagem de erro original.

**Voltar/Back:** no HUD principal retoma o jogo; nos seletores e na confirmação apenas cancela. A confirmação começa focada em Cancelar. Toque, controle físico, foco e rolagem usam `TableView` e os eventos do próprio motor.

## Ligações exatas

| Entrada | Código original | Alteração |
|---|---|---|
| Reticências nativas / Back mapeado | `AppKeyCode::openMenu` → `EmuApp::showLastViewFromSystem` | Abre HUD se há conteúdo carregado |
| Botão de ações / gamepad | `AppKeyCode::openSystemActions` → `showSystemActionsViewFromSystem` | Abre o mesmo HUD |
| Botão explicitamente mapeado para sair | `AppKeyCode::exitApp` | Chama `showExitAlert`; com jogo abre HUD |
| Back na raiz nativa com jogo | `EmuApp::showExitAlert` | Abre HUD |
| Pausa | `EmuViewController::pushAndShowModal` → `showUI(false)` | Usa a rotina original para parar thread/áudio |
| Retomada | `popModalViews()` → `showEmulation()` | Reset de entrada e retomada originais |
| Gravação | `saveStateWithSlot(slot, true)` | Caminho, formato e mensagens originais |
| Leitura | `loadStateWithSlot(slot)` | Valida acesso/formato pelo motor original |
| Saída | `ApplicationContext::exit()` | Marca a atividade como saindo antes de `finish()` |

A saída original passa por `onStop` → `dispatchOnExit(backgrounded=false)` → `EmuApp::closeSystem` → `EmuSystem::closeRuntimeSystem`: salva autosave conforme opções, opções da sessão e memória de backup. A ponte Android já integrada deve continuar trazendo as plataformas. **Não substituir isso por `killProcess`, por `finish()` sozinho ou por fechamento do conteúdo que deixa o menu original aberto.**

Não interceptar `showUI()` globalmente: é usado tanto para pausas quanto para abrir configurações e construir modais; isso causaria recursão ou bloquearia as opções originais.

## Aplicação

Usar uma **cópia de trabalho isolada** do upstream. `apply_patch.py` verifica SHA-256 dos cinco arquivos existentes antes de preparar qualquer alteração. Sem `--apply`, apenas valida e imprime os hashes previstos:

```text
python apply_patch.py CAMINHO_DA_COPIA_UPSTREAM
python apply_patch.py CAMINHO_DA_COPIA_UPSTREAM --apply
```

O plano contém **oito arquivos**: cinco existentes modificados (`EmuFramework/src/EmuApp.cc`, `EmuFramework/src/EmuInput.cc`, `EmuFramework/src/CMakeLists.txt`, `imagine/include/imagine/gfx/GfxText.hh` e `imagine/src/gfx/common/GfxText.cc`) e três novos (`StationHudView.hh`, `StationHudView.cc` e `StationHudLayout.hh`). Os dois fontes Imagine completos nesta pasta correspondem à revisão corrigida; não omiti-los no build. Includes do fonte devem ter prioridade sobre cabeçalhos do SDK de uma compilação anterior.

## Correção de desenho R2

A R1 passava posição local para `Text::draw` após transformar o modelo. A implementação original de `draw` redefine `modelView`, eliminando essa transformação. R2 passa coordenadas absolutas a `drawScaled`, que aplica a escala na mesma matriz que posiciona os glifos e alinha usando o tamanho escalado. Cabeçalho e rodapé usam recortes explícitos. A API antiga continua disponível, com escala 1.

Ajuste adicional: o laço de fonte exige espaço para `min(5, quantidade de ações)` antes de aceitar o tamanho. Os seletores com onze linhas continuam roláveis. A fonte global do emulador não muda. Captura e resultados reais de toque/controle, salvar/carregar e saída continuam necessários após instalar a R2.

## Compilação: requisitos comprovados no upstream

- `EmuFramework/CMakeLists.txt`: CMake >= 4.1, módulos C++.
- `imagine/doc/INSTALL`: ambiente oficialmente suportado Linux/macOS, Clang >= 21.
- `.github/workflows/build.yml`: compila com NDK `r30-beta1`, JDK 21 e dependências do bundle.
- `imagine/doc/INSTALL-Android`: API 36, NDK 29 indicado na documentação; CI é a receita exata mais recente deste commit.
- Recompilar Imagine/EmuFramework + SNES e MD em arm64, sem recompilar os demais emuladores da TurboStations.
- Manter renomeação da biblioteca, processo, assets e isolamento `NativeActivity.internalDataPath` da integração já corrigida. No MD, preservar renomeação de `gpOverlay.png` para o arquivo exclusivo aplicado na integração existente.

## Conferências obrigatórias antes de distribuir

- Compilar ambos os motores; esta proposta não afirma que a compilação passou.
- Toque nas reticências, Back Android e menu do controle abrem HUD sem executar opções ocultas.
- Navegar por toque e controle; voltar de confirmação/seletores não sai do jogo.
- Salvar slot vazio; substituir após confirmação; cancelar substituição; carregar estado existente e tentar posição vazia; confirmar que SNES/MD continuam isolados.
- Continuar, configurações e voltar ao jogo mantêm controles próprios e som corretos.
- Sair: plataformas sem login; processo do emulador encerrado; jogos/dados preservados.
- Não validar apenas por captura: comparar arquivos de estado antes/depois e reabrir o jogo para conferir persistência.
- Avaliar alturas/fonte e rolagem em tela estreita e paisagem; o HUD é nativo, sem temporizador ou animação adicional.
