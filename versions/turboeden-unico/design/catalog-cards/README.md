# Cartões de sistemas do catálogo

Este diretório prepara 46 imagens, uma para cada categoria presente no `catalog.json` do APK único. O `manifest.csv` associa cada cartão ao ID estável da categoria, ao nome e à quantidade de jogos no catálogo local.

- 36 cartões são quadros estáticos extraídos dos vídeos do tema `TURBORAMAx` fornecido pelo mantenedor em `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx`.
- 10 cartões foram criados para categorias sem vídeo correspondente: ColecoVision, Famicom Disk System, Game & Watch, Game Gear, Game Boy, Jaguar, Odyssey 2, PC Engine CD, Sufami Turbo e SuperGrafx.

O tema de origem declara autoria **LZ-RETRO-PC-2026** e aponta para [es-theme-PlayStation-X](https://github.com/LZ-RETRO-PC-2026/es-theme-PlayStation-X). Preserve a atribuição ao reutilizar os quadros dos vídeos.

## Estado da integração

Os cartões são recursos de interface. A tela de catálogo Android atual é `GuiStore`, implementada em `libmain.so`. Seu painel **Filtrar por plataforma** desenha botões próprios e não lê as imagens do tema EmulationStation. O tema `TURBORAMAx` usa `formatVersion 7`, enquanto o tema Android incluído no APK usa `formatVersion 4`; copiar seus XMLs diretamente causa incompatibilidades.

Para o fluxo solicitado, o seletor gráfico precisa usar os IDs do `manifest.csv` e, ao escolher uma categoria, aplicar esse ID ao filtro de `GuiStore`. Os métodos nativos relevantes identificados são `GuiStore::openFilterPanel`, `GuiStore::applyFilterChip` e `GuiStore::rebuildVisible`. A tela **Instalados** e o botão **Baixar** já funcionam no APK de catálogo restaurado e devem continuar usando o fluxo nativo existente. Os cartões ainda não são exibidos pelo APK instalado.

O APK de catálogo contém chaves e firmware privados. Nunca o adicione a este repositório.
