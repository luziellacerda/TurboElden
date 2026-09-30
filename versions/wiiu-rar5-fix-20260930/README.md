# Wii U — correção do arquivo RAR5 e dos controles

Estado em 30/09/2026: esta pasta registra o diagnóstico RAR5 e um candidato intermediário com Cemu 0.5. O mantenedor esclareceu em seguida que deseja a atualização para **Cemu 0.5.2**; o candidato atual e o plano de instalação estão em `../wiiu-cemu-052-20260930/`. Não promover o candidato intermediário a estável. O doador desta etapa era Cemu Android 0.5, registrado em `versions/atualizacao-2026-09-30-gamecube-wiiu/snapshot/implementation/wiiu-integration/provenance.json`.

## Defeito e correção

- O arquivo do usuário `/sdcard/EmulationStation/roms/wiiu/MARIO KART 8 [AMKE01].rar` foi testado integralmente com 7-Zip: RAR5 íntegro, não criptografado, um volume, 3.636 entradas, 4.316.310.053 bytes descompactados e executável `code/Turbo.rpx`. A mensagem anterior de arquivo corrompido era falsa.
- O leitor `libarchive` retornava EOF em um bloco RAR5 final vazio e a ponte nativa tentava ler dados de diretórios. `libarchive-rar5-eof.patch` aplica a correção condicional do EOF, baseada na revisão 317730a do PR upstream 3361. `wiiu_archive_bridge.c` ignora corretamente o corpo de diretórios e registra o arquivo que causar uma falha verdadeira.
- A leitura completa do RAR no celular, **sem extrair**, passou com `status=1`, 3.636 entradas e 4.316.310.053 bytes. O APK intermediário com essa ponte foi instalado sem limpar dados; Mario Kart 8 extraiu e abriu com imagem. O jogo ainda estava sem botões na tela.
- A classe nativa do Cemu retorna lista vazia de botões quando o controle 0 está desabilitado. `WiiUBootstrap.java` configura o controle 0 como Wii U GamePad **uma vez**, somente se ele estiver desabilitado, e salva a opção. `InputOverlaySettings.patch` habilita por padrão a sobreposição para usuários sem preferência anterior. As escolhas seguintes permanecem no menu original do Cemu.

## Candidato atual

| Item | Valor |
| --- | --- |
| Base privada | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk` |
| SHA-256 da base | `1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7` |
| APK candidato | `E:\ESTUDO APK\work\native-carousel\implementation\emulator-completion\wiiu-rar5-fix\TurboramaStation-WiiU-RAR5-candidato.apk` |
| SHA-256 candidato | `19ce5b65303c288776aefb822dcc8d72dd07525b66c986d0c7587f36ae19abb8` |
| Entradas alteradas | `classes19.dex`, `classes20.dex`, `lib/arm64-v8a/libturbo_wiiu_archive.so` |

Assinatura e integridade das entradas do APK passaram na montagem. Esse candidato **ainda não foi instalado**: o aparelho caiu para 1% de bateria mesmo na USB. A instalação anterior de teste alterou só a biblioteca de arquivo e preservou os jogos e saves. O APK, jogos, BIOS, firmware, chaves e mídias privadas não pertencem ao Git.

## Arquivos e reconstrução

- `wiiu_archive_bridge.c`: ponte JNI recompilada para arm64 com NDK r28c.
- `libarchive-rar5-eof.patch`: mudança sobre libarchive 3.8.9. Fonte upstream: <https://github.com/libarchive/libarchive>; diagnóstico relacionado: <https://github.com/libarchive/libarchive/pull/3361>. O arquivo estático local corrigido é `E:\ESTUDO APK\work\native-carousel\implementation\emulator-completion\vita-rar-diagnosis\libarchive-rar5-eof.a`, SHA-256 `2ef8d3f3e33ea14430f39da1487d3dc02bebe44e0c35e4c8036e0130ca8c8005`.
- `WiiUBootstrap.java`: substitui a classe da ponte Wii U já documentada na revisão estável. Compilar junto de `WiiUArchive.java` e `WiiUEntryActivity.java` da mesma pasta `wiiu-archive-final/java/org/emulationstation/frontend`, usando Android SDK 34, Java 8 e D8; saída local `wiiu-rar5-fix/bridge-dex/classes.dex` para `classes20.dex`.
- `InputOverlaySettings.patch`: aplicar ao `smali/info/cemu/cemu/common/settings/InputOverlaySettings.smali` decodificado do `classes19.dex` da **mesma base** com apktool 3.0.3; remontar o módulo em `wiiu-rar5-fix/cemu-controls-module.apk`. Apenas o valor padrão da sobreposição muda. O doador original está registrado no arquivo `provenance.json` citado acima. Não misturar com outro Cemu.
- `build_candidate.py`: recompila a ponte nativa e substitui apenas as três entradas declaradas; confere alinhamento, assinatura e integridade. Exige as duas saídas DEX acima e o arquivo estático local. Temporários e APK são mantidos em E:.

## Conferência pendente

Com bateria adequada, atualizar pelo ADB com `install -r`, sem desinstalar nem limpar dados. Conferir hash instalado, abrir Wii U → Mario Kart 8 → Jogar, verificar botões virtuais e resposta ao Start; depois usar o menu do Cemu para sair e confirmar retorno às plataformas sem pedir login. Registrar qualquer falha real de outro RAR antes de promovê-lo a estável. O Cemu Android é experimental; este teste de um jogo não certifica toda a biblioteca Wii U.
