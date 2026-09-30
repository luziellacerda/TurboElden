# Alterações

## PS2

- Substituição do core Libretro antigo por ARMSX2 oficial 2.7.2 (ARM64, Android 8+, suporte oficial a páginas 4k/16k).
- Remoção do antigo `libarmsx2_libretro_android.so` do pacote. Backup local preservado.
- Rotas nativas do frontend passam a chamar `Ps2Bootstrap`; biblioteca e classes isoladas para coexistirem com os outros motores.
- Menus oficiais de configuração, inicialização direta do jogo e retorno à tarefa da TurboramaStation.
- Diretórios PS2 próprios. BIOS locais existentes e memory cards copiados somente quando o destino está ausente; originais preservados. Nenhum download de BIOS.
- Sem presets de desempenho forçados. Configuração e salvamento realizados pelo próprio motor.
- Classes anteriores 2–14 e demais bibliotecas preservadas byte a byte, exceto módulo de integração do frontend.

## PSP

- PPSSPP oficial 1.20.4 com classes JNI originais, dependências e recursos com nomes separados, processo `:psp`.
- Rotas nativas passam a chamar `PspBootstrap`. O motor integrado aparece como disponível, dispensando o antigo core baixado.
- Inicialização de configurações por `--gamesettings`; jogo por `--pause-menu-exit` e caminho do arquivo.
- Diretórios internos, externos e cache próprios. Memstick em `Android/data/org.emulationstation.frontend/files/PPSSPP/memstick`.
- Cópia de SAVEDATA, PPSSPP_STATE, CHEATS e NAND legados apenas quando ausentes. Configurações antigas não são convertidas. Compatibilidade dos save states não presumida.
- Remoção dos nomes conhecidos do core PSP antigo nas pastas de cores somente na primeira inicialização do novo PSP. Backup privado no PC. Firmware HLE do próprio PPSSPP; sem BIOS adicional.
- Pausa dos vídeos das plataformas e da música ao iniciar a emulação. Retorno usa fechamento oficial da Activity preservando a tarefa do frontend.
- Classes anteriores 2–16 e demais bibliotecas preservadas byte a byte, exceto módulo de integração do frontend.

## Estado observado

O APK final foi instalado sem desinstalar ou limpar dados; SHA256 do pacote no aparelho corresponde ao manifesto. Login e plataformas observados após instalação. PS2 abriu GTA San Andreas e retornou às plataformas. PSP em teste pelo mantenedor, sem confirmação de jogo/retorno nesta publicação. Não há medição de FPS ou aprovação geral de todos os jogos.
