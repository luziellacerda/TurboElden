# R131 — PS3 e PS4 internos, exclusivamente offline

Base exata: APK R130 `d227b0af17600bf99ec097857bf182f6e7989f8ddc3b68b63e17c81f69eb30ad`. A integração acrescenta owners próprios ao mesmo APK; a ponte externa R130 permanece byte idêntica, mas a factory instancia o dispatcher interno no lugar dela. Não é necessário instalar nem abrir os aplicativos externos aPS3e/Bachata.

## Preparação automática

- PS3: core oficial aPS3e2.43, JNI real e processo privado `:station_ps3`. Firmware Sony4.93 em `assets/sony/ps3/upstream/PS3UPDAT.PUP`, por autorização humana específica, exclusivamente no APK local. O worker confere o arquivo e executa o importador nativo. Somente importação bem-sucedida e arquivos reais permitem declarar o sistema preparado.
- PS4: runtime oficial BachataS4 0.2.4, processo privado `:station_ps4`, Surface Android e importador PKG real. O DEX JNI SDL3 vive em assets e em classloader isolado; não substitui o SDL da Station. O material comum do importador PKG foi autorizado para o APK local e não é uma conta/licença pessoal.
- Configurações Sony abrem os owners internos e preparam seus arquivos automaticamente. Nenhum downloader de firmware, wizard externo ou configuração manual obrigatória foi acrescentado.
- PS3 abre ISO; PS4 importa PKG uma vez para armazenamento privado, com dados SFO reais. Conteúdo criptografado ainda precisa da chave válida do próprio jogo quando o motor a exigir. DEMOs não são jogos.

Os binários oficiais, firmware, material PKG, jogos e outputs de compilação não entram no Git. As receitas recebem inputs privados fixados por hash. A versão completa das interfaces Android oficiais não foi reconstruída: estes owners são fontes próprias mínimas sobre os artefatos nativos exatos. Consulte os contratos e atribuições de cada motor.

## Preservação da R130

Todos os39 DEX existentes, resources.arsc, libturbo_carousel, vídeos, capas, LEDs, economia, cache/preload, limites dos menus, controles, cores e opções dos outros emuladores são conferidos contra o APK R130. A extração Sony começa somente no worker do owner solicitado. Não adiciona tarefa de preparação ao carrossel nem impõe30fps ao gameplay.

A montagem admite exatamente cinco substituições: Manifest, engines.json e os três marcadores de identidade PSX/N64/Dolphin. Acrescenta classes40.dex e299 entradas Sony. Os quatro IDs online existentes precisam acompanhar o novo bundle compartilhado; seus cores, opções, perfis, capacidades e transporte são preservados. PS3/PS4 não ganham engine, sala ou perfil online. Cadastro no servidor e gameplay não são provados pela compilação.

## Reprodução

1. `ps4/recipe/build_owner.py`: confere APK/DEX oficial, as67 declarações JNI e gera owner.dex/material PKG privado autorizado. O decoder Java é `integration/psx-online/recipe/DecodeOneClass.java`.
2. `composition/recipe/prepare_assets.py`: confere APKs, PUP e derivados; prepara módulos privados, descritores e pins Java.
3. `recipe/patch_manifest.py`: altera a factory e acrescenta duas Activities privadas singleTask; exige inversão binária exata.
4. `recipe/compile_host.py`: compila somente o novo DEX e rejeita colisão com qualquer classe dos39 DEX da base.
5. `ps3/recipe/verify_jni.py`: compara dez classes/estruturas com o contrato oficial2.43; não relaxa assinaturas.
6. `recipe/build_runtime_identity.py`: vincula arquivos, fontes e recibos efetivos; renova apenas os marcadores existentes.
7. `recipe/assemble_apk.py`: congela inputs e monta o escopo fechado; `recipe/verify_final.py` confere cada entrada, assinatura original e alinhamento16KiB após assinatura local.

Recibos finais públicos ficam em `versions/station-sony-internal-r131-20261011/evidence`, fora do mapa de fontes produtivas, para evitar autorreferência. Temporários únicos em G:, backup completo único em F:. Não selecionar instalador por data nem promover a candidata antes da conferência final.

## Validação

APK final R131 corrigido `0273ab9ae1b7ef5a061fdcc76c49558db4180bedd10a8100e6d5f764ac2ab175`, 2.711.825.423bytes, fonte `8503c2e32d7487d3bb31397ba9533dc7e1bfe981`, assinado com certificado original e conferido em todas as entradas, v2/v3 e16KiB. A entrega e os mapas completos de hashes estão em `versions/station-sony-internal-r131-20261011`.

A primeira candidata teve preparação PS3 observada, mas o PS4 falhou antes do JNI por API JavaSE ClassLoader indisponível no Android. A candidata corrigida usa boot Android na compilação e sincronização da instância; stubs de compilação não são empacotados. O resumo físico anterior identifica somente o primeiro APK.

A candidata corrigida foi instalada no Motorola Edge30/Android14, com SHA integral, UID/dados e frontend oficial conferidos. Pelos botões reais de configuração, ambos os owners privados mostraram suas telas de preparo protegido e retornaram ao frontend. PS3 confirmou o firmware importado inicialmente e seu reuso após prepare/ensure. PS4 passou a carga JNI/initPKG/runtime e não repetiu a falha ClassLoader. Isso é evidência da UI e de seus pós-requisitos; arquivos privados não foram lidos independentemente. Nenhum ISO/PKG real foi iniciado/importado para jogar; gameplay/controles/temperatura/servidor não validados. Consulte os recibos `installation.json` e `physical-bootstrap.json` da entrega.

Leia STATUS.md e os recibos finais. Compilação, presença de assets, carga JNI, importação de firmware e jogo real são evidências distintas. Compatibilidade e desempenho PS3/PS4 dependem do motor e do aparelho; preparação automática não garante execução de todo título.
