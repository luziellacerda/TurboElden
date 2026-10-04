# Reprodução das alterações R7

## Insumos

Windows, Python 3.14, JDK 17.0.20, SDK android-34, build tools 35.0.0, apktool3.0.3, NDK r28c, CMake/Ninja, .NET SDK9 com target net8. Todos os caminhos reais estão nos scripts/recibos. Builds/temp em E:. O código compilado é o snapshot `station/src`, `netplay/src`, `native` desta entrega; scripts de preparo históricos descrevem a evolução e **não devem ser reaplicados cegamente** por cima dos fontes finais.

Base privada R5: G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Videos-Sem-Espera-SNES-Roxo-R5-20261004.apk, SHA256 afa300d23dc57bb5b1973530dc83371fc892d6c37cf11ecc1750aed8ff22415b.
Também necessários: arrays privados de imagens/metadados nativos preservados da base, objeto das 44 prévias R5, stubs/libc++ da receita nativa, chave de assinatura local. O repositório público não redistribui APK/ROM/BIOS, arte privada, fontes do servidor privado ou chaves. Ausência desses insumos deve produzir impedimento explícito, não arquivo vazio.

## Fontes dos motores

Usar **commits completos** de evidence/upstream-pins.json, não master atual. Baixar o arquivo oficial codeload `/OWNER/REPO/zip/COMMIT` ou recuperar esse commit de fonte oficial, conferir SHA do arquivo onde registrado e extrair sem sair do diretório alvo. Os diretórios canônicos usam os nomes do manifesto. Submódulos do ClownMDEmu: usar cada gitlink/commit de evidence/clown-submodules.json; um hash de arquivo null significa que o commit está fixado, mas o ZIP já existia na coleta, não usar null como checksum. Scripts fetch_clown_dependencies.py e fetch_station_overlays.py documentam dependências oficiais, sem mídias do usuário.

Aplicar em RetroArch somente **retroarch-station-all.patch**, consolidado e reaplicado sobre o ZIP oficial para comprovar igualdade do texto final dos arquivos modificados após normalizar CRLF para LF, conforme evidence/retroarch-patch-replay.json. Normalizar os arquivos afetados para LF antes de aplicar (o ZIP oficial mistura CRLF/LF). Os três patches incrementais anteriores são históricos: um repetia hunks do mesmo arquivo e não passava no git apply; não reaplicá-los. Não aplicar application-process-guard.patch ao RetroArch: pertence ao smali da Application original e contém somente a guarda do processo :station_netplay.

## Comandos nativos

Usar E:/StationNetplayWork sem espaços (junction para a raiz canônica). NDK_OUT/NDK_LIBS_OUT separados por motor, APP_ABI=arm64-v8a e APP_PLATFORM=android-26.

- bsnes: `ndk-build -C .../bsnes/target-libretro APP_BUILD_SCRIPT=<absoluto>/target-libretro/jni/Android.mk PROFILE=performance APP_ABI=arm64-v8a APP_PLATFORM=android-26 NDK_OUT=<raiz>/engine-build/bsnes/obj NDK_LIBS_OUT=<raiz>/engine-build/bsnes/lib -j4`.
- Geolith: mesmo formato, `-C <geolith>/libretro`, script absoluto libretro/jni/Android.mk, outputs engine-build/geolith.
- Clown: CMake -S diretório fixado -B engine-build/clownmdemu -G Ninja, CMAKE_TOOLCHAIN_FILE=<NDK>/build/cmake/android.toolchain.cmake, ANDROID_ABI=arm64-v8a, ANDROID_PLATFORM=android-26, CMAKE_BUILD_TYPE=Release, BUILD_SHARED_LIBS=ON, CMAKE_DISABLE_FIND_PACKAGE_Git=ON. `cmake --build ... --parallel 4`.
- RetroArch: ndk-build -C `<ra>/pkg/android/phoenix-common`, APP_BUILD_SCRIPT absoluto `/jni/Android.mk`, APP_ABI=arm64-v8a, TARGET_ABIS=arm64-v8a, APP_PLATFORM=android-26, HAVE_VULKAN=0, HAVE_CHEEVOS=0, HAVE_SAF=0, outputs engine-build/retroarch, -j2.

Executar prepare_station_online_engines.py: copia/valida quatro ELF, exports AArch64/alinhamento16KiB, licenças e registros de hashes. Alteração de qualquer binário exige novo registro para servidor e nova homologação; não manter hashes de build anterior.

## Java, manifesto e APK

`station/run_tests.py` compila fontes API34 e roda testes de host; `station/build_module.py` cria DEX após a compilação. `netplay/build_netplay.py` usa station-client.jar como classpath e Android API34, Java8/minAPI26. `test_online_policy.py` confere configurações contra fonte upstream, recursos e layout; não executa jogos.

Manifesto compilado a partir do XML entregue com recursos/manifesto originais preservados. Application: decodificar o classes.dex **do APK R5 exato** ou usar cache somente após conferir SHA256 216d1fd132111eb12a7ff77419944d6662511b3a1fefe59cd68ff3f07f1ee87f; aplicar guarda, reassemblar; todos os outros smali devem continuar idênticos. Não usar classes.dex de outro APK por semelhança de pasta.

Compilar carrossel com receita R5 `build_station_r5.py native` usando fontes finais R7 e insumos privados verificados. A receita R5 de package não entrega online; usar `package_station_online.py` final. Ela espera manifest-module.apk, application/module.apk, station/build/dex/classes.dex, netplay/build/dex/classes.dex, native/libturbo_carousel.so, runtime/*.so e assets/station-online. Recusa sobrescrever APK de saída; requer >2×base +200MiB livres.

O packager muda exatamente manifesto, classes.dex, classes28.dex, classes35.dex e libturbo_carousel.so. Acrescenta motores/controles/licenças/manifestos. Verifica todas as entradas antigas por SHA256, todos os acréscimos, classes únicas, certificado e alinhamento. Recibo é evidence/online-build-result.json; não usar apenas data/nome do arquivo como evidência.

## Testes e publicação

Os logs .NET são do servidor exportado isoladamente, com dados sintéticos. Os testes publicáveis ficam no repo privado, junto ao handoff. Os 591 Java são regressões da API/catálogo/cache/instalador; os 231 checks online são de fonte/recursos/layout e seis casos executáveis de estado, não simulação de partidas. Bibliotecas e APK somente foram compilados no PC. Não remover jogos/configurações reais para testar.

Instalação pendente USB. Servidor novo pendente de operador e homologação. Fonte/Git não implica API ativa. Depois da publicação registrar commits exatos nos recibos, conferir remoto e manter a tag estável anterior intacta.
