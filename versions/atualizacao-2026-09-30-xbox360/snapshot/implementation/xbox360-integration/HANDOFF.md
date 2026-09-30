# Xbox 360 — candidato experimental, não instalado

## Estado de 30/09/2026
APK: `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Xbox360-XenDroid-0b11201.apk`
SHA256: `929339aeb74a3460cc44f2ec4cc0aa461dca581c2c75dd30b8ace4a52ff9c7a1`
Tamanho: 983124339 bytes. Módulo nativo: `577c907f62d612af37dea5f8d78e0ea2e5d8a47fca975411171602c78840ca17`.
Base exata Wii U: `b11f0acce6bb553c2f13e2a6846bc1e4f0189050a2a3ab69d962fe7972e2d7d5`. Inclui GameCube e Wii U anteriores.
XenDroid oficial tag XenDroid-0b11201: https://github.com/rfandango/XenDroid/releases/tag/XenDroid-0b11201.
Integração Java/nativa compilada; motor upstream incorporado do APK publicado, não recompilado integralmente.
Assinatura conferida. Todos os motores anteriores e classes2–20, exceto catálogo classes8, byte idênticos à base.
NÃO instalado; jogo, controles, configurações, retorno e desempenho NÃO observados. Telefone descarregou; instalação adiada pelo usuário. Não pedir conexão repetidamente.
Instalado continua GameCube cd1a8a55. Estável Git3573db1/APK55cd54a3 preservada. GameCube/WiiU publicados anteriormente em67b23340.

## Catálogo e visual
24 jogos e24 capas provenientes do mesmo cache local autorizado, indicado pelos documentos de H:\ARQUIVOS DLL SAMBOX. source-xbox360.json privado; catalog-xbox360.json adiciona categoria xbox360 ao final, mantendo todas as categorias anteriores. Permissões ESPECIAL/Demo/Mensal preservadas e mapeadas para Android. Links remotos não verificados, nenhum jogo baixado.
Vídeo xbox360.mp4 do tema TURBORAMAx/_theme_inc/images/caratulas convertido para720x720/60fps, velocidade1x, sem áudio. Mesmo player/cache/loop nativo. Sinopse portuguesa de xbox360.xml e LED pelo mapeamento do tema. Nenhuma tela Java substitui o carrossel.
CatalogData recebeu SHA256 novo em smali e DEX8 foi reassemblado corretamente.

## Rotas e processos
native_xbox360.h antecede WiiU -> PSP -> PS2 -> Flycast -> Dolphin, delegando todas as outras plataformas.
findLaunchCommand xbox360 retorna libretro: core=xendroid_android.so, interceptado pela ponte Java; não existe tentativa de carregar esse nome como core Libretro.
Configurações nativas ganham Xbox 360; entrada abre menus originais XenDroid.
classes21: motor/interface e dependências realocadas tx360cor. classes22: três classes da ponte.
Processo :xbox360 para menus e :xbox360emu para jogo. MainAliveService executa no processo principal mantendo o frontend conforme upstream. Saída original encerra só o processo de emulação. Mesma tarefa Android; retorno real ainda não observado.
YuzuApplication despacha initProcess antes dos outros motores, apenas nos processos Xbox. Inicialização original Application.attachBaseContext/onCreate preservada. Dados/cache/preferências isolados em Xbox360/xbox360_.
Jogo recebe game_uri com caminho absoluto. Ponte resolve ISO/XEX/ZAR/STFS e diretório com default.xex. Após extração, seleção pelo resolvedor nativo antigo ainda requer observação no aparelho.
JNI xendroid preservado. Bibliotecas auxiliares renomeadas e referências ajustadas, inclusive libX360V-Tools-shared.so para evitar colisão com outro motor. Nenhuma biblioteca anterior sobrescrita.
Android11+/Vulkan1.1 como condição mínima da ponte, não garantia de compatibilidade. Projeto experimental com limitações de hardware/jogos; não prometer desempenho universal. Configurações originais permanecem escolhidas pelo usuário. Atualizador original upstream não foi redesenhado; futuras trocas de motor devem ocorrer pelo build integrado.
Vídeo e música frontend pausados no despacho; retomada usa mecanismos existentes.

## Pastas e reprodução
Fonte ativa: `E:\ESTUDO APK\work\native-carousel\implementation`. Integração: `E:\ESTUDO APK\work\native-carousel\implementation\xbox360-integration`. Temporários e builds somente E:.
1. Base Wii U exata; frontend-sparse.apk guarda manifest/resources/res/classes.dex/classes8.dex e frontend-decoded sua decodificação.
2. XenDroid_Release_0b11201.apk vem da release; current-decoded contém a decodificação. base-classes.json inclui toda base Wii U.
3. prepare.py mescla recursos/manifest/classes21/libs. integrate.py aplica inicialização/dados/hash e compila ponte Java. Executar integrate.py uma única vez por árvore criada por prepare.py.
4. Apktool3.0.3 compila merged para merged-template.apk. build_native.py compila libturbo_carousel.so com NDK28c/Clang. package.py monta e assina APK usando a chave local, conferindo preservação de motores, DEX e catálogo.
5. Para instalar depois: usuário fora do jogo, adb install -r; nunca desinstalar nem limpar dados. Abrir .auth.LoginActivity. Conferir plataformas, configurações Xbox, jogo e retorno logado.
Backups do estado anterior em xbox360-integration/before. Não executar preparadores históricos que regeneram mapeamentos antigos e removem GameCube/Xbox360.
Git recebe somente fontes, licenças e documentação; APK, URLs privadas do catálogo, vídeos, ROMs, BIOS, chaves e assinatura ficam locais. Base privada continua necessária, Git não contém o C++ integral original do frontend.
PSX Resident Evil permanece uma pendência separada, sem alteração nesta entrega.
