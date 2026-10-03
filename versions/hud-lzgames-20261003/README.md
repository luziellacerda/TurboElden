# HUD LZ Games — SNES e Mega Drive — 03/10/2026

**Estado atual:** HUD R2 compilado e instalado por atualização, SHA256 `6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b` conferido no telefone. Visual das cinco ações aprovado por captura em SNES e Mega. Save manual `.00.gp` do Mega observado; carregar, cancelar/substituir e posição 10 ainda precisam de conferência controlada. Telefone saiu da USB. Não promovido a estável. R1 rejeitada por texto sobreposto; histórico em `history/r1-render-bug`.

## Escopo

Pedido do mantenedor: menu de pausa com identidade LZ Games/Turborama, ações explicadas e opções de salvar/carregar estado. Abrange Snes9x EX+ e MD.emu completos, ambos do upstream `1c12fac5ce49badaadff2e2f210dcc30b89f4943` (1.5.85). Outros emuladores não são modificados.

Base obrigatória: APK `8f494041ca4ae37fbd8becb50a1a7156ea2141e717af41452e5a1a923e0799b0`, com a separação de armazenamento SNES/Mega aprovada pelo usuário. Não usar o candidato `e87a352b`, que compartilhava configurações. Não misturar com a linha de 40 mil jogos.

## Funcionamento

- Menu nativo por reticências, Voltar do Android e ação de menu do controle.
- Continuar: remove modais e chama `EmuApp::showEmulation()`.
- Salvar estado: dez posições manuais, índices reais 0–9; chamada `saveStateWithSlot(slot, true)`. Posição já existente exige confirmação.
- Carregar estado: mostra data local, desativa posições vazias e confirma a substituição do andamento atual. Chama `loadStateWithSlot(slot)`. O slot automático -1 não é usado.
- Configurações: abre as opções e controles originais do respectivo emulador.
- Sair: explica o retorno às plataformas e chama `ApplicationContext::exit()`. Esta função marca o estado Exiting antes de `finish`, fazendo a rotina original gravar memória de backup, opções e autosave conforme configuração. Não usa apenas Activity.finish, kill de processo ou eventos simulados.
- Falha de salvar/carregar mantém a partida pausada e a mensagem original do motor. Retoma somente após sucesso.

`showLastViewFromSystem`, `showSystemActionsViewFromSystem` e `showExitAlert` encaminham ao HUD somente quando há conteúdo carregado. `showUI` não é redirecionada, evitando recursão. `pushAndShowModal` executa a pausa original antes de exibir o menu.

O HUD usa o renderizador, toque, foco, controle e rolagem nativos. Preto/verde com detalhes vermelhos; fontes locais do HUD, sem alterar o tamanho configurado nas opções do emulador. Descrições e confirmações quebram linhas. Não há timer de animação, sobreposição Java ou navegação por coordenadas.

## Pastas e compilação

- Trabalho: `E:\ESTUDO APK\work\station-hud-lzgames-20261003`.
- Fonte original somente leitura: `E:\ESTUDO APK\work\station-snes-explus-20261003\source\emu-ex-plus-alpha-1c12fac5ce49badaadff2e2f210dcc30b89f4943`.
- Fonte modificada: `source` na pasta de trabalho.
- Dependências e SDK ARM64: `deps` e `sdk\android-arm64`.
- Objetos: `native-build`; registros: `logs`.
- Saídas nativas: `libsnes9x_explus.so`, `libmdemu_station.so`.
- APK R2 atual: `TurboStations-SNES-Mega-HUD-LZGames-R2-20261003.apk`, SHA256 `6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b`, 1.910.661.392 bytes.
- APK R1 rejeitado, removido após conferência de hash para liberar espaço de build: `TurboStations-SNES-Mega-HUD-LZGames-20261003.apk`, SHA256 `3d3afc380b109affe5615961b6930ffe7b88f1c96255e8cf39e6e688da66e0f7`, 1.910.652.864 bytes.

Recompilação integral dos dois motores a partir do mesmo fonte identificado anteriormente, agora com o HUD no EmuFramework. Não utiliza offsets, substituição de instruções ou hooks em vtables. Clang 22.1.8, CMake 4.4.2, Ninja e sysroot Android NDK r28c, ARM64 API26 e páginas de 16 KiB.

Dependências do próprio upstream: libc++/libc++abi22.1.0, ogg1.3.6, vorbis1.3.7, FLAC1.5.0, xz5.8.3, libarchive3.8.6; patches originais CRC32/UTF8 preservados. Flags e hashes são registrados nos recibos de compilação.

Receita em árvore limpa:

1. `prepare_native.py`: copia quatro diretórios do upstream e adapta apenas a preparação Windows/CMake.
2. `build_libcxx.py` e `build_cdeps.py`: compila/instala as dependências locais.
3. `native-hud/apply_patch.py <source> --apply`: aplica oito arquivos, verificando antes cinco hashes originais. Inclui os dois fontes Imagine com `Text::drawScaled`, além das três alterações EmuFramework e três novos fontes do HUD.
4. `select_engine.py snes`, depois `build_native.py imagine EmuFramework Snes9x`.
5. `select_engine.py mega`, depois `build_native.py imagine EmuFramework MD.emu`.
6. Conferir as bibliotecas no Android com o probe de carregamento isolado.
7. `package_hud.py --native-finalized`: empacota somente após as saídas estarem finalizadas.

As fases 4/5 são sequenciais. O SDK é compartilhado; cada biblioteca final é copiada antes da troca de namespace. A receita final usa saída intermediária dentro do diretório de cada emulador para evitar que um build incremental confunda a saída do outro. O Mega recompila oito descritores JNI `com/mdimagn/` e o atlas `mdOverlay.png`; SNES mantém `com/imagine/` e `gpOverlay.png`. Os includes do fonte têm prioridade sobre cópias anteriores do SDK.

Adaptações de preparação documentadas: leitura de pkg-config sem shell Linux e com espaços corretamente tratados; geração de cabeçalho via CMake; remoção apenas de `-gz` porque o clang Windows não tem zlib para comprimir informação de debug; avisos de depreciação Android continuam avisos; tabela JNI `static const` em vez de `constexpr` para o tipo JNINativeMethod do NDK28; ligação explícita do caminho que no ZIP original era um symlink de CMake. Nenhuma delas altera regras de emulação ou presets.

## Preservação obrigatória

Todos os DEX, manifesto, recursos visuais, mídia, catálogo, login, downloads e motores de outras plataformas permanecem byte a byte iguais à base. O empacotador confere cada entrada ZIP, a assinatura original e alinhamento. Somente os dois `.so` mudam; fontes/notas públicas são acrescentadas.

As sobrescritas Java reais de `NativeActivity.getFilesDir/getCacheDir/getExternalFilesDir` continuam intactas. Configurações SNES em `files/snes-explus/config`, Mega em `files/mega-explus/config`; sem copiar o antigo arquivo compartilhado. Saves seguem os caminhos e opções nativos já existentes. Atualizar com instalação `-r`, nunca desinstalar ou limpar dados.

## Validação e estado

R1 instalada por atualização em 03/10/2026, hash do `base.apk` conferido e nenhum dado limpo. Na captura posterior `hud-mega-menu.png` (atividade SNES, apesar do nome do arquivo), painel e cartões apareceram, mas os textos se sobrepunham no canto superior esquerdo. A R1 não foi aprovada. O recibo anterior à captura foi preservado em `history/r1-render-bug/device-runtime.json`, junto da fonte R1; os arquivos Imagine adicionais não existiam naquela proposta.

Causa comprovada no código: `Text::draw` redefine a matriz modelView e descartava a transformação externa do HUD. R2 acrescenta `Text::drawScaled`, preserva `draw` na escala 1 e usa coordenadas absolutas/escala explícita em todos os textos, com recortes de cabeçalho e rodapé. A fonte local também tenta acomodar as cinco ações do HUD principal antes de aceitar o tamanho; seletores maiores continuam roláveis. Fontes/preferências globais não mudam. Includes de Imagine do fonte precisam vir antes do SDK antigo.

R2 instalada por atualização e hash conferido. Capturas demonstram HUD legível em ambos os motores e controles próprios do Mega. Novo estado manual `.00.gp` foi encontrado após interação do mantenedor; posição 10, carregamento e cancelamento/substituição não foram comprovados antes da desconexão USB. Retorno ao catálogo autenticado foi observado, sem processo do emulador; a tela retomada pode ser a lista de jogos anterior, não necessariamente o carrossel de plataformas. `hud-build-result-r2.json` registra a montagem; `device-runtime.json` detalha exatamente o que foi ou não conferido. A opção temporária Android `stay_on_while_plugged_in` foi alterada de 0 para 3; a restauração falhou com telefone ausente, portanto restaurar 0 na próxima conexão.

Consulte `evidence/hud-build-result-r2.json` e `evidence/device-runtime.json`, quando presentes, para o APK exato, instalação e resultados reais. A ausência de recibo de aparelho significa que o fluxo ainda não foi conferido nele. Não promover a estável por inferência.

Testes de fonte R2: **21 aprovados**, sendo 18 contratos de ações/slots/lifetime/layout/API real de texto e três guardas do aplicador. O helper C++ efetivamente usado pelo HUD passou 576 cenários de tamanho/fonte/texto. Incluem regressões da transformação em `Text::drawScaled` e tentativa de cinco ações visíveis. Esses testes não substituem observar o renderizador e executar save/load nos jogos.

O probe prova apenas que o Android resolve a biblioteca e sua entrada `ANativeActivity_onCreate`; não abre emulação. Os resultados de menu, continuar, salvar/carregar, configurações e retorno precisam ficar descritos separadamente no recibo do aparelho.
