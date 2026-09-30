# Atualização PS2 e PSP — em avaliação

Publicado a pedido do mantenedor enquanto testa no aparelho. Não é uma nova versão estável aprovada.

- PS2: ARMSX2 2.7.2, motor e menus oficiais dentro do mesmo APK, processo `:ps2`.
- PSP: PPSSPP 1.20.4, motor e menus oficiais dentro do mesmo APK, processo `:psp`.
- Integração própria compilada. Bibliotecas dos motores incorporadas dos APKs oficiais; não houve reconstrução integral do C++ dos motores.
- Preservados design, Dolphin, Flycast, jogos, saves existentes e sessão. Dados de cada motor separados; migração copia apenas arquivos ausentes.
- APK final instalado por atualização, com hash conferido no aparelho. Abertura das plataformas mantendo login observada.
- PS2: GTA San Andreas observado renderizando; saída para plataformas confirmada pelo usuário e captura. Sem benchmark.
- PSP: abertura de configurações, jogo e retorno ainda pendentes de conferência no momento desta publicação.

[Alterações](ALTERACOES.md) · [Pastas e reconstrução](RESTAURACAO.md) · [Manifesto](MANIFESTO.json)

Base aprovada preservada: tag `estavel-2026-09-30-dolphin-flycast`, commit `3573db1203cee541f2e590d4ed6574e2a23e781c`, APK `55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85`.
O snapshot é um complemento ao snapshot dessa tag: materializar a base e aplicar os arquivos desta pasta. Não contém APK, SO, DEX, BIOS, jogos, saves, mídias privadas, assinatura, capturas nem registros privados do aparelho.
