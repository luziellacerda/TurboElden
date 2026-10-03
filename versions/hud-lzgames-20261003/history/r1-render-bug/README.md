# R1 — histórico da falha de desenho

APK instalado: `3d3afc380b109affe5615961b6930ffe7b88f1c96255e8cf39e6e688da66e0f7`, 1.910.652.864 bytes. Não aprovado como estável.

Esta pasta preserva somente arquivos pequenos da revisão anterior: `EmuFramework/src/gui/StationHudView.cc` (SHA256 `004801c255dfcffe1f5491bdaf362582acadd5bf9b84ae294c8a091e565cd38c`) e o recibo `device-runtime.json` capturado antes da conferência visual. O recibo ainda declara os testes pendentes; não é evidência de aprovação.

Na captura posterior `E:\ESTUDO APK\work\station-hud-lzgames-20261003\hud-mega-menu.png`, painel/cartões estavam posicionados, mas textos se sobrepunham no canto superior esquerdo e as linhas não mostravam o texto corretamente. Apesar do nome da captura, a atividade observada era SNES.

Causa no fonte: `Text::draw` substituía a matriz modelView configurada pelo HUD, que fornecia posições locais. A revisão R2 usa posição absoluta e a nova API `drawScaled`, responsável pela matriz completa.

**Ausência preservada:** a cópia `native-hud` da R1 não continha `imagine/include/imagine/gfx/GfxText.hh` nem `imagine/src/gfx/common/GfxText.cc`; usava esses arquivos originais do upstream. Nenhum arquivo vazio foi criado para representá-los. Os fontes novos de Imagine pertencem somente à R2 em `../../native-hud`. Nenhum APK, biblioteca ou captura grande foi duplicado neste histórico.
