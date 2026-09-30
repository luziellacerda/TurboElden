# Reconstrução e caminhos exatos

Fontes ativos: `E:\ESTUDO APK\work\native-carousel\implementation`.
GameCube: subpasta `gamecube-integration`, APK `TurboramaStation-GameCube-Dolphin.apk` (cd1a8a55).
Wii U: subpasta `wiiu-integration`, APK `TurboramaStation-WiiU-Cemu-0.5.apk` (b11f0acc), ainda não instalado.

## Pré-requisitos
Sobrepor estes fontes ao snapshot PS2/PSP f5b3afa. Base binária privada e assinatura original são necessárias; o repositório não contém o C++ integral do frontend. Python3, JDK17, Apktool3.0.3, build-tools35, android.jar34, LLVM e NDK28c. Compilação/temporários em E:.

## GameCube
Usar base PSP exata 3631c668. `intermediate-gamecube` contém os três fontes anteriores ao Wii U; com o mapeamento gc incluído, build_native.py recompila o módulo. Catálogo privado autorizado: cache-atual-catalogo.json; inserir categoria GameCube (Files originais, RequiredPackage/Demo/Mensal preservados, Android=true, R2Pasta=gamecube, AndroidPackage=RequiredPackage, CatalogLabel=roms, Oculta=false) ao final do catálogo original. Resultado: catalog-gamecube.json. Vídeo privado gc.mp4 do tema TURBORAMAx convertido para 720x720 H264 baseline, velocidade 1x e sem áudio em720-gc.mp4. Executar rebuild_catalog_module.py e package.py. O SHA esperado em CatalogData precisa corresponder ao novo JSON; DEX deve ser reassemblado para ordenar a tabela de strings.

## Wii U
Base GameCube exata cd1a8a55. Doador Cemu-0.5.apk e SHA constam no provenance.json. Decodificar em current-decoded. Criar frontend-sparse.apk com AndroidManifest.xml/resources.arsc/res/classes.dex/classes8.dex da base e decodificar em frontend-decoded. Cache framework e temporários E:.

Extrair categoria wiiu do mesmo catálogo privado em source-wiiu.json. `catalog-before.json` é o asset JSON da base. Copiar seus grupos para catalog-wiiu.json, substituindo APENAS Files da categoria wiiu pelos arquivos da fonte autorizada; preservar AndroidPackage e demais campos de acesso. Não publicar esses JSON/CSV.

Executar prepare.py (gera merged, class-map e resource-map) e integrate.py, depois Apktool b merged -> merged-template.apk. Não executar integrate.py duas vezes sobre a mesma árvore modificada; começar novamente por prepare.py. Recolocar snapshot/implementation/native_carousel.cpp e native_wiiu.h, executar build_native.py e wiiu-integration/package.py. Usa classes19 para Cemu, classes20 para bridge, recompila classes8 para hash; demais DEX e motores são conferidos byte a byte.

Os scripts publicados usam TURBORAMA_KEYSTORE, TURBORAMA_KEY_ALIAS, TURBORAMA_STORE_PASSWORD e TURBORAMA_KEY_PASSWORD. Não há valores de assinatura publicados. Scripts ativos locais conservados.

Wii U exige Android11 e Vulkan1.1; checagem restrita ao seu botão. Dados ficam nas subpastas Cemu, com preferências isoladas. Abertura aceita arquivos WUX/WUD/WUA/WUHB/RPX/ELF/ISO e procura RPX em pastas extraídas. As bibliotecas auxiliares têm nomes próprios para preservar PSP. Menus originais Cemu; onQuit fecha sua Activity/processo separado.

## Pendências e instalação
Telefone descarregou e instalação foi adiada pelo mantenedor. Atualizar somente fora de uma partida, mesma assinatura, `adb install -r`, sem apagar dados. Abrir entrada pública `.auth.LoginActivity`; observar configurações Wii U, jogo baixado/extraído e retorno sem novo login. Não classificar como estável antes da avaliação. Imagens/URLs remotas, execução e retorno ainda não conferidos. WUX pode exigir chaves do próprio usuário; nenhuma chave foi obtida ou incluída nesta integração.

Xbox360 foi solicitado depois deste snapshot e ainda não está incorporado.
