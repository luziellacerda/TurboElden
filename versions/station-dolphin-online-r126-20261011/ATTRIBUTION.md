# Atribuição e fontes

Esta integração altera uma variante do Dolphin e mantém as fontes originais do projeto como referência fixada. Dolphin é software GPL-2.0-or-later. Os novos arquivos nativos conservam esse identificador SPDX.

- Fonte oficial Dolphin: https://github.com/dolphin-emu/dolphin/tree/5102a0339c2177575378107b76541e47cc52122d
- Licença do Dolphin: https://github.com/dolphin-emu/dolphin/blob/5102a0339c2177575378107b76541e47cc52122d/COPYING
- Dependências originais e pins: `recipe/dependencies.lock.json`; as licenças permanecem nos caminhos correspondentes dos arquivos de fontes obtidos pela receita. Não se atribui a licença do Dolphin a todos os terceiros.
- Guia oficial NetPlay: https://dolphin-emu.org/docs/guides/netplay-guide/

O adaptador Station está em `native/` e `java/`; as transformações reproduzíveis estão em `recipe/` e `patches/`. A entrega não publica APK, binários, mídia, jogos ou BIOS. A receita usa o clone existente sem mudar seu checkout e reconstrói somente a variante online. A biblioteca normal do aplicativo é preservada.

N64 permanece na integração R125, cujo upstream, modificações, plugins e identidades estão em `../station-mupen-online-r125-20261011/`. Não confundir o NetPlay e o código de emulação originais de cada projeto com uma substituição de desenho de controles.
