# Candidato de retomada online após R67, conciliado com R68

Implementação pedida por REC-01–09. Não é uma instalação R69 nem recibo de produção. Servidor/contrato e matriz em `docs/server/RETORNO-IMPLEMENTACAO-RETOMADA-ONLINE-STATION-20261007.md` quando publicado. Fonte Java: composição R67 exata sobre R55→R57→R62→R63→R64, mais nove overrides e duas classes novas; **195 inputs**. Sucessora visual R68/c2a1a6d incorporada como pai desta branch; nenhum Java/DEX/runtime mudou nela. A montagem exige a R68 efetivamente instalada e preserva seu carrossel de cantos retos.

## Implementado

- Sessão lógica separada de WSS: o TCP nativo, motor e rings permanecem em RAM; credencial de retomada renovada com Bearer/prova/Binder privados. Nenhum `Leave` pela perda da rede.
- Fluxo TSR2 com offsets/ACK/replay limitado/deduplicação/backpressure. Callback WSS não bloqueia no TCP; controles continuam sendo processados.
- JNI confirmado pelo thread real antes de PAUSED; duas confirmações e buffers escoados antes de PLAYING. NEED_SYNC também cobre stall com WSS intacto. Fonte/patch/receita do runtime publicados nesta pasta, identidade distinta de899e.
- Background conserva estado sem criar outro motor. Espera mostra “Aguardando conexão…”, indicador indeterminado e “Sair da partida” com confirmação. Estado perdido/autorização negada é explicado; sem contagem de expulsão. Reinício do processo nativo/servidor **não** é recuperação persistida.
- V1 continua implementado para as identidades antigas; novo APK v2 exige servidor compatível e não entra em sala de runtime anterior. Alias, vínculo/licença e assinatura não mudam.

## Identidades

Java base R67/APK `d746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f`. Montagem atual sobre **R68** `72ce7c2cbb3d7cf14ad122b0b98e42a41563114bbbc5c925caedbdee49ff66c3`/2.110.287.488 bytes, original signer `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`. DEX28 compilado ficou idêntico à R67/R68; DEX35 novo em `evidence/java-build.json`. DEX30 BIOS R66 e libturbo_carousel R68 devem permanecer byte a byte.

Runtime Linux candidato arm64/API26/16KiB: `b1b9beeffd19dccaf5475dc58659763ab858563036ba13b075fe58c7adcf0edd`/10.668.472 bytes. Engines SNES/Mega novos: `bsnes-mercury-performance-79d7f9de-rs2-b1b9beeffd19`, `clownmdemu-d43c2708-rs2-b1b9beeffd19`. Geolith permanece sem launchReady/online aprovado. Core/opções/overlays R64 preservados.

Compilação no Windows pode produzir outro hash ELF. `generate_engines.py` e o empacotador derivam IDs/registro dos **bytes reais**; enviar o recibo/registro resultante ao servidor. Não copiar os IDs Linux para outro binário. Não publicar .so/DEX/APK, ROM, BIOS, vídeo, save, chave ou licença no Git. Os artefatos Linux ficam privadamente em `/mnt/DADOS/station-recovery-r67-check-20261007`.

## Reprodução e montagem no PC

Usar esta branch completa, com os snapshots R55/R57/R62/R63/R64/R67/R68 exigidos pela composição. Não usar empacotadores históricos. Python3.11+, **JDK17**, API34 jar hash `6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad`, D8 build-tools34 jar hash `d43c8a94c9b1f1da1a7cc49c32b81e8cee1708b37ee8b530a81a0688222b42c0`. Não usar javac21 com esse D8: a primeira tentativa Linux falhou internamente; a compilação JDK17 terminou e os dois DEX foram gerados. Requisitos de JDK no Android: [documentação oficial](https://developer.android.com/build/jdks).

1. `python recipes/build_java.py --android-jar <API34/android.jar> --d8-jar <build-tools34/lib/d8.jar> --jdk <JDK17> --output <nova-pasta-E:/java>`; gera ambos usando o mesmo client.jar. `--api-check-only` não serve para montagem.
2. `python recipes/build_native_runtime.py --source-zip <arquivo-oficial> --ndk <NDK-r28c> --output <nova-pasta-E:/runtime> --jobs 4`.
3. Fonte oficial RetroArch `69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576`, [arquivo exato](https://codeload.github.com/libretro/RetroArch/zip/69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576), SHA `cecf1e3f5446724f748124d097bb9c5169c6f599404d33a8447d88fd197d17fe`. Aplica dois patches históricos exatos + hooks de recuperação; manifesto congela fontes e patch unificado. NDK28.2.13676358; compara arquitetura/alinhamento e três exports JNI.
4. Prover privadamente `STATION_KEYSTORE`, `STATION_KEY_ALIAS`, `STATION_KS_PASS`, `STATION_KEY_PASS` originais. Não colocar valores em comando/relatório.
5. `python recipes/package_recovery.py --base-apk <R68-exato.apk> --java-build <java> --native-build <runtime> --workspace <nova-pasta-E:/package> --output <novo-candidato-G:/arquivo.apk> --tools <build-tools-35/android-15> --jdk <JDK17>`.
6. Empacotador verifica fonte/manifesta/DEX/JAR/runtime/core original, duplica nenhuma classe, valida certificado e16KiB, permite trocar somente DEX28/35, libstation_retroarch.so e engines.json; compara todas as outras entradas. Gera `server-engine-registry-additions.json` automaticamente. DEX28 pode permanecer igual. Nenhuma instalação ou alteração de dados acontece na receita.
7. Enviar somente recibos/metadados públicos ao servidor. Preparar/registrar o binário Linux em release imutável, adicionar engines sem remover os antigos, ativar v2 na qualificação coordenada. O APK candidato só inicia v2 depois de o snapshot anunciar capacidade/motor aprovados.
8. Antes de atualizar cada aparelho: conferir base/assinatura/UID/data, nenhuma Activity de jogo ativa; usar atualização `-r`, sem desinstalar/limpar dados. A receita de instalação R67/R68 anterior exige APKbaseR67 e **não deve ser usada sem conciliação** neste candidato. A instalação física será um passo de produção separado com recibo.

## Testes reproduzíveis e limites

`recipes/run_transport_tests.py --server-root <Servidor-pix-candidato> --java-build <java> --android-jar <API34> --json-jar <json-20250517.jar> --jdk <JDK17> --output <pasta-nova>` executa vectors32 + TLS/WSS/TCP46 com backend real .NET em loopback e autenticação/chaves sintéticas. O teste guarda o fixture privado temporário, fecha apenas o processo filho que criou e apaga as credenciais. Confirmou1.620.000 bytes nos dois fluxos, quedas host/convidado/ambos, foreground e stall. A pausa JNI é simulada neste teste; não é gameplay Android.

`cc -Wall -Wextra -Werror -std=c11 -pthread -Inative tests/native_recovery_test.c -o <saida>; <saida>` confirma13 invariantes do controle nativo em host. O patch unificado foi reaplicado sobre os três arquivos originais e reproduziu exatamente os quatro arquivos compilados. Testes de servidor/compatibilidade estão no retorno.

Ainda pendentes: montagem/assinatura/instalação do APK candidato, execução JNI real, estabilidade/determinismo dos cores SNES e Mega, dois aparelhos com comandos/som/imagem, quedas longas, modo avião/troca de rede, atrasos1/3/6/10/20, energia/CPU/temperatura e captura nativa do erro histórico. Nenhuma prova sintética fecha esse aceite. NG-01–07 cartuchos/CD permanecem uma frente separada; a BIOS R66 está preservada.
