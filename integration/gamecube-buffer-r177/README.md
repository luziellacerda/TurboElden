# R177: GameCube com buffer de oito quadros

Pedido do proprietário: manter a base que registrou 44–45 FPS antes do ensaio
CPU da R174 e testar oito quadros, como a ideia que ajudou no PSX. R176 já
restaurou classes35.dex e os núcleos exatos da R173; esta candidata conserva
essa CPU normal e altera somente o buffer de entrada GameCube, de cinco para
oito, no CurrentRun. Não é frameskip nem aumento garantido de FPS.

NativeConfigure mantém a política original. Em seguida o helper define
Dolphin/NetPlay/BufferSize=8 no layer4 e confere Active3 antes de nativeConnect.
O nativeHost oficial lê esse valor e transmite o mesmo alvo aos convidados.
BufferSizeClient=1 e Wii=5 permanecem. As opções assinadas, o hash do perfil,
a validação do launcher e o cadastro acompanham o valor real.

A receita preserva cada instrução existente fora de três classes e acrescenta
um helper. Mantém39DEX, todos os núcleos reais e13.855 entradas do APK.
Os quatro IDs de runtime são renovados por vincular todo o APK; isso não muda
as decisões, ROMs, limites de jogadores nem o PSX estável de oito quadros.
A R172 estável e suas tags são imutáveis. Prova física ainda pendente.

Referências primárias: [buffer do Dolphin](https://dolphin-emu.org/docs/guides/netplay-guide/)
e [configuração da versão fixada](https://github.com/dolphin-emu/dolphin/blob/5102a0339c2177575378107b76541e47cc52122d/Source/Core/Core/Config/NetplaySettings.cpp).
