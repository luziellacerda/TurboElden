# Estado aprovado — 30/09/2026

Esta versão substitui os estados intermediários registrados abaixo. O usuário confirmou funcionamento e pediu publicação como estável. APK final SHA256: 55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85. Tag: estavel-2026-09-30-dolphin-flycast.
Dolphin: configurações abriram; usuário confirmou jogo Wii e retorno sem login. Flycast: Sonic funcionando conforme usuário; retorno nativo e fundo observados; correção de toque aprovada com “tudo ok”. Não houve benchmark prolongado nem validação de todos os jogos. BIOS ficam privadas. O candidato posterior 3085d9fc não foi instalado e não integra esta entrega.

## Registro histórico da implementação (estados e pendências abaixo são da época)

# Flycast integrado à TurboramaStation

## Estado atual

Consultar STATUS.md, build-result.json e installed.json antes de agir. Revisão retorno-rapido instalada às10:22:03, SHA25655cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85. Fila nativa de toques e ativação no pressionamento, aguardando confirmação de toque único. Fundo/BIOS/retorno já observados nas revisões anteriores; não transferir evidência de desempenho para esta revisão.

## Pastas e base exata

- Raiz de implementação: E:\ESTUDO APK\work\native-carousel\implementation
- Integração e temporários: raiz\flycast-integration
- APK atual: raiz\TurboramaStation-Flycast-v2.7-44-retorno-rapido.apk; anteriores turborama.apk, menu-bios.apk e v2.7-44.apk preservados.
- Base obrigatória: raiz\TurboramaStation-Dolphin-2609-7.apk
- SHA256 da base: 5bce795e714ce943d887dd127bfb28c501b8fc55b2f748520348c705ed30dc03
- Fontes anteriores do módulo: flycast-integration\before
- A base contém o Dolphin 2609-7 já incorporado, cujo jogo/retorno sem login foram confirmados pelo usuário. NÃO voltar à base antiga de pesquisa ou ao APK estável histórico para trabalhar no Flycast.

## Atualização BIOS e imagem de disco — 30/09/2026

O usuário pediu explicitamente BIOS após a primeira abertura de jogo falhar. O frontend enviou Resident Evil - Code - Veronica (USA) (Disc 2) (Track 2).bin, 1.589.952 bytes. No diretório Dreamcast não há descritor nem outras faixas de Resident Evil. O Flycast oficial classifica .bin como Naomi (core/emulator.cpp getGamePlatform), gerando erro de BIOS Naomi; isso não prova que Resident Evil seja arcade.

BIOS encontradas localmente em D:\TurboRoms\roms\bios\bios\dc. Foram incorporadas dc_boot.bin, dc_flash.bin, naomi.zip, naomi2.zip, awbios.zip, hod2bios.zip, f355bios.zip e airlbios.zip. f355dlx.zip veio do asset mame2003-plus já existente na base. Total9. dc_boot MD5 e10c53c2f8b90bab96ead2d368858623 corresponde à referência local flycast_libretro.info. Naomi inclui epr-21576h/epr-21577h/epr-21578h com os CRCs definidos pelo código oficial; naomi2/awbios contêm os arquivos próprios.

- Fontes exatas e hashes locais: bios-sources-private.json. NÃO publicar BIOS no Git.
- Cópia de trabalho E: flycast-integration/bios-assets. Arquivos empacotados em assets/flycast-bios. Manifest sem caminhos locais em assets/flycast-integration/bios-manifest.json.
- FlycastBootstrap.installBundledBios roda após migrate() retornar, inclusive quando o marker da migração já existe. A migração tem prioridade para preservar BIOS/flash/saves anteriores. Copia somente destino ausente para Android/data/org.emulationstation.frontend/files/Flycast/data; arquivo temporário + rename, sem sobrescrever arquivos/saves existentes. Nada baixado da web.
- resolveGame recusa arquivo inexistente e faixa .bin/.raw em /dreamcast/ sem descritor correspondente. Se há GDI/CUE/CHD/CDI do mesmo disco, resolve para ele; se há mais de um, pede seleção explícita. Valida referências de GDI/CUE antes de iniciar. Não tenta transformar áudio em jogo, não fabrica GDI e não modifica catálogo/downloads.
- Mensagem específica retorna pelo UiString nativo usando getLastLaunchError. Falha de validação não abre o motor e não pausa vídeo/música do frontend.
- Novo APK: TurboramaStation-Flycast-v2.7-44-menu-bios.apk. Hash/instalação em build-result.json e installed.json; não pressupor instalação antes do respectivo registro.
- Antes das alterações: before-bios preserva fontes e resultados, APK original v2.7-44 permanece no caminho anterior.
- Recompilar integrate.py (bridge DEX), build_native.py (mensagem/roteamento) e package.py; recursos doador inalterados permitem reutilizar merged-template.apk. Rebuild completo segue os passos originais.
- Evidência do erro: game-first-attempt-logcat.txt e current-before-bios.png. Jogo não iniciou nessa tentativa. Sonic Adventure CHD abriu e retomou emulação às09:54:44 e09:56:15; usuário confirmou funcionando. Consultar sonic-confirmation.json e sonic-user-confirmed-logcat.txt. Desempenho não medido.

## Botão nativo de retorno — 30/09/2026

- Pedido do usuário: botão para voltar ao menu na tela do Flycast; depois continuar as BIOS. Android upstream não oferece Exit no cabeçalho da lista principal.
- native_bridge.c troca somente a chamada ImGui::Text do título GAMES por ImGui::Button("VOLTAR AO MENU") verde. Usa foco/toque/controle nativos. Sem Java overlay, coordenadas ou cliques simulados.
- Chamada restrita a GuiState::Main(4) e retorno exato base+0xafad84; outras chamadas encaminhadas a TextV preservando varargs.
- Slot ImGui::Text em0x1190e18, módulo oficial e36e9df2d. integrate.py confere SHA256 fixado em navigation-abi.json; runtime valida função exportada, instruções, string GAMES e slot antes de modificar. Slot em GNU_RELRO; proteção read-only restaurada após troca.
- init é chamado em activityReady antes da superfície. Botão usa dc_exit oficial; finishAffinity já é redirecionado a Activity.finish para preservar tarefa/login da TurboramaStation.
- Compilar integrate.py e package.py. Recursos/DEX13 não mudaram; merged-template.apk continua válido. build_native.py já foi executado para a guarda de discos antes deste botão.
- Backups em before-return-button. Botão observado visualmente; toque e retorno ao frontend registrados às10:07:56. Evidências em menu-bios-observation.json e native-return-*.

## Fundo Turborama do menu — 30/09/2026

Pedido posterior ao retorno/BIOS confirmados: identidade Turborama no plano de fundo da biblioteca Flycast. native_bridge.c acrescenta desenho ImGui nativo estático (preto/verde, wordmark TURBORAMA, detalhes vermelhos e legenda Dreamcast/Naomi/Atomiswave), atrás dos itens. Sem vídeo, Java overlay, texturas externas, temporizador ou alteração das regras/controles.

Intercepta também BeginChild(unsigned,...), somente no retorno0xafb0d4 da biblioteca principal e GuiState::Main(4). Executa BeginChild original primeiro e desenha no drawlist do filho; respeita recorte e dimensões do próprio painel. Outros filhos/estados não são desenhados. Os dois slots estão na mesma página GNU_RELRO; hash/instruções/ponteiros validados. Métodos nativos de texto/linhas/gradiente exportados pelo binário oficial. Não roda desenho do fundo durante emulação.

Backup da revisão botão+BIOS confirmada: before-turborama-background. APK anterior menu-bios.apk/f4551cc0 preservado. Nova saída TurboramaStation-Flycast-v2.7-44-turborama.apk. Consultar build-result.json/installed.json: compilação e teste visual não são equivalentes. Recompilar integrate.py e package.py, reutilizando merged-template.apk e libturbo_carousel.so atuais. Botão/BIOS e demais motores permanecem.

## Correção do toque no retorno — 30/09/2026

Usuário relatou vários toques/lag no botão. Registros10:16 mostram quatro pares de toque entregues antes da ativação; após reconhecer às10:16:20.861, finish às20.862 e frontend resumed às20.895. As coordenadas dos primeiros toques não foram inspecionadas; os registros sozinhos não provam que todos acertaram o botão. Fonte oficial gui.cpp310..330 só amostra mouseButtons a cada quadro, portanto um down/up entre quadros pode desaparecer. Evidência/inferência em return-delay-analysis.json e return-delay-before-logcat.txt.

native_bridge.c registra wrapper JNI para InputDeviceManager.touchMouseEvent(III)V. Sempre encaminha ao JNI oficial; na biblioteca Main(4) preserva transições reais em fila protegida. Lê coordenadas já transformadas pelo código original. Hook do AddMouseButtonEvent no ponto gui_newFrame/leftbutton consome fila no renderer usando APIs oficiais ImGui. Coalesce movimento, não press/release. Eventos com mais de2s descartados; fila limpa fora da biblioteca. Não calcula áreas clicáveis nem simula toques; hit-test/foco ficam no ImGui. Controles durante jogo continuam no JNI original.

Retorno agora usa ButtonEx com PressedOnClick(1<<4), acionando no início do toque e com trava de uma saída por Activity. Label VOLTANDO... enquanto finish é processado. Mantém dc_exit/Activity.finish e o fundo Turborama. Configurações e emulação não passam pela fila da biblioteca.

Slots/ABI fixados em navigation-abi.json: AddMouseButtonEvent0x118fc10, caller0xafaadc; coordenadas originais0x3896798/79c. RegisterNatives restrito ao processo Flycast. Proteção RELRO restaurada. Compilar integrate.py com -mno-outline-atomics (biblioteca auxiliar sem runtime compiler-rt), depois package.py. Não precisa reexecutar apktool/build_native: DEX e libturbo_carousel preservados.

APK novo: TurboramaStation-Flycast-v2.7-44-retorno-rapido.apk; hash/instalação e confirmação por uso nos registros. Backup anterior before-return-touch-fix; APK turborama.apk/1f6e63da intacto. Não afirmar retorno no primeiro toque até observação manual. Não rodar testes/toques automatizados.

## Proveniência

- Repositório: https://github.com/flyinghead/flycast
- Fonte local: flycast-integration\source
- Commit: e36e9df2dcc1487acdb1dc7725766f1f5ba029b5
- Versão Android oficial: v2.7-44-ge36e9df2d, versionCode3395, minSDK21, target36.
- Compilação oficial do ramo master de 28/09/2026, selecionada no índice do site oficial https://flyinghead.github.io/flycast-builds/.
- APK oficial: https://flycast-builds.s3.fr-par.scw.cloud/android/heads/master-e36e9df2dcc1487acdb1dc7725766f1f5ba029b5/flycast-release.apk
- SHA256 oficial: d590819a7282a6487b0411356dfec0af839ca598c3b3dc57d57d0930bda1d5aa
- A versão estável 2.7 também foi baixada para comparação, mas NÃO é o motor utilizado. O Flycast separado do aparelho já era posterior, 2.7-11-g149e651d2/versionCode3320.
- Motor C++ e UI reaproveitados do binário oficial. Integração compilada localmente. Não afirmar recompilação integral do motor.
- LICENSE GPL-2.0-or-later, proveniência e fontes da integração incluídos em assets/flycast-integration. Direitos de terceiros preservados.

## Arquitetura

1. native_flycast.h incluído após native_dolphin.h. Oito destinos do vetor de hooks agora entram nos wrappers Flycast. Se não for Flycast, delegam aos wrappers Dolphin, que preservam a rota original dos outros motores.
2. Hooks: run 0x2a9718 (UiString por x8), needsFreshProcess 0x2a89a8, isBundledCore 0x2a87d8, isCoreInstalled 0x18b098, isAssetPackInstalled 0x18aaf0, getAssetPack 0x18a8a8, CoreOptions::loadDefinitions 0x2a6850, GuiStore::selectSettingsTab 0x2228f8. Nenhum trampoline de instruções.
3. Identificadores com flycast/Flycast/reicast vão ao FlycastBootstrap.launch. Dreamcast/Atomiswave no catálogo atual; mesma rota atenderá outro sistema cujo identificador use este core. Não adicionar plataformas inventadas.
4. resolveCore original retorna nome de biblioteca pelo isBundledCore sem exigir arquivo. run intercepta esse identificador. Não restaurar libretro antigo.
5. NativeGLActivity original do Flycast no processo :flycast, exported=false. Recebe ACTION_VIEW com Uri do caminho absoluto para abrir jogo pela API oficial JNIdc.setGameUri; sem file:// exposto e sem coordenadas.
6. YuzuApplication mantém inicialização original no processo principal e o desvio Dolphin existente. Adicionado retorno antecipado no processo :flycast, com delegado Emulator anexado à Application real.
7. JNI com/flycast/emulator e com/google/androidgamesdk preservados. AndroidX isolado como tflycast; outras dependências tflycast/shaded. Stubs de plataforma Android mantêm nomes reais e são deduplicados contra TODOS os DEX da base. 6223 classes do doador, 1280 recursos prefixados tf_, novos IDs sem mudar IDs existentes.
8. classes13.dex = doador isolado; classes14.dex = ponte Java. classes2..12, incluindo Dolphin, byte idênticos à base. classes.dex alterado apenas no bootstrap.
9. libflycast.so e libswappy.so incorporados. Helpers exclusivos: libfile_redirecf_hook.so, libfsl_alloc_hook.so, libfhok_impl.so, libflyc_hook.so. SONAME/strings de nomes alterados com comprimento constante; não alterar libmain.so, libc++ ou helpers dos outros motores.
10. Configurações abertas pelo símbolo oficial exportado gui_setState(GuiState::Settings=3), chamado pelo pequeno libturbo_flycast.so APÓS initEnvironment e ANTES de iniciar a superfície de renderização. Endereço não fixado; dlsym pelo nome _Z12gui_setState8GuiState. O nome JNIdc.guiOpenSettings é enganoso: abre/fecha PAUSA durante jogo e não abre Configurações na tela inicial, por isso não é usado para esta entrada.
11. Monitor de retorno das configurações consulta a função JNI original guiIsContentBrowser, a cada250ms, só encerra quando voltar à tela principal e Activity estiver em foco. Nenhum clique simulado.
12. Menus do jogo/controles do Flycast preservados. Fechar jogo pode levar à lista interna do Flycast; Voltar na lista ou Sair encerra a Activity. finishAffinity foi sobrescrito para finalizar só o Flycast e preservar a tarefa/sessão da TurboramaStation. NÃO afirmar retorno automático às plataformas no botão Fechar jogo antes de observar.
13. Renderização, vídeo e música do frontend pausam por sua rotina existente ao abrir o motor; retorno segue ciclo Android/SDL. Sem ajuste forçado de desempenho ou resolução.

## Dados e remoção do antigo

- Usuário: Android/data/org.emulationstation.frontend/files/Flycast
- Dados nativos: subpasta data; emu.cfg no diretório Flycast.
- Internos: files/Flycast; cache: cache/Flycast. Exportar/importar pelo menu oficial usa somente essa árvore, não a árvore dos outros emuladores.
- SharedPreferences próprio flycast_preferences. home_directory aponta à nova árvore inicial e respeita escolha posterior do usuário.
- Fontes legadas: EmulationStation/.emulationstation/saves/reicast, bios/dc e bios/dc/data.
- Copia APENAS arquivos conhecidos de BIOS/suporte local, VMU, nvmem/nvmem2/eeprom. Nenhum download de BIOS. Nunca sobrescreve destino existente nem apaga origem. Grava arquivo temporário e renomeia ao concluir. Marker .turborama-legacy-copy-v1 após conclusão.
- VMUs por jogo: formato legado nome.A1.bin convertido para nome_vmu_save_A1.bin. VMU compartilhada permanece compartilhada se encontrada sem VMU por jogo; emu.cfg inicial apenas nesse caso recebe PerGameVmu=no. Nenhum preset de velocidade/resolução.
- Shaders, save states e configurações Libretro não importados automaticamente; ficam preservados na origem. Não prometer compatibilidade entre save states.
- No aparelho, saves/reicast continha ggx15.zip.nvmem e nvmem2. Configurações/dados do Flycast separado não foram lidos via run-as nem alterados.
- O core antigo NÃO estava no APK base. Era arquivo baixado na pasta cores. A inicialização principal remove apenas flycast_libretro_android.so e libflycast_libretro_android.so nas duas pastas conhecidas: files/cores e EmulationStation/.emulationstation/cores.
- Backup PC: previous-libretro.so, SHA256 d8cadd791074a47e2b737a395f00401e8df05e8c565c33fd65ad95703ca88f4b. Não empacotar novamente. A rota antiga permanece desativada mesmo se remoção física falhar.
- device-catalog.json é evidência privada local, não publicar.

## Reprodução

Scripts em flycast-integration:
1. prepare.py — copia frontend-decoded para merged, isola classes/recursos do current-decoded. Reexecutar reseta as modificações do doador; sempre rodar integrate.py em seguida.
2. integrate.py — modifica bootstrap/armazenamento/entrada de configurações; compila java/org/emulationstation/frontend/FlycastBootstrap.java para bridge-dex; compila native_bridge.c.
3. native_patch.py — registra include/wrappers no native_carousel.cpp. Backups em before.
4. Compilar raiz/build_native.py. Log native-build.log.
5. Apktool b merged -p framework -o merged-template.apk, com java.io.tmpdir=flycast-integration/tmp. Log build.log.
6. package.py — sobrepõe recursos/classes1/13/14 e bibliotecas novas na BASE DOLPHIN; zipalign16, mesma chave de assinatura, conferência de preservação. Saída e hash em build-result.json; log package.log.
7. Captura fresca preinstall.png + tela/Activity comprovando fora de partida. install.py --catalog-confirmed. Nunca desinstalar/limpar dados. Rejeita NativeGLActivity/EmulationActivity ativa; ESActivity também pode hospedar jogo Libretro e exige screenshot.

Ferramentas: C:\Python314\python.exe; JDK17 Adoptium; apktool_3.0.3.jar em E:\ESTUDO APK\TurboRetroEmu-build\tools; build-tools35 em android-build-tools\35.0.0\android-15; NDKr28c em E:\TurboEdenEngine. Scripts já contêm caminhos exatos. ADB local workspace/work/android-tools/platform-tools/adb.exe, ADB_USB_LEGACY=1, aparelho [identificador do aparelho omitido].

## Pendências e limites

Botão nativo, nove BIOS e retorno ao catálogo com login foram confirmados. Abertura/retomada de emulação registrada; não houve medição de desempenho prolongado ou conferência de todos os jogos. Resident Evil baixado é faixa isolada e continua incompleto. Não baixar conteúdo ou fabricar descritor. Não executar toques automatizados. Git estável de29/09 permanece intacto; não promover/publicar sem pedido específico. Não incluir BIOS/ROMs/dados privados no repositório.
