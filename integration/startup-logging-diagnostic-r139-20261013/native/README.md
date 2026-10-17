# Ponte opcional de registros de início

Esta biblioteca diagnóstica chama somente três funções exportadas pelo runtime R139 já carregado. Não incorpora nem altera RetroArch/bsnes e não modifica HLE, controles, opções do core, transporte, READY, FPS ou temporizadores. A identidade do runtime permanece `ae72f137…`; a identidade do APK diagnóstico precisa de seu próprio recibo.

Contrato Java: `StationStartupLogging.enable(String exactRuntimePath)` retorna `boolean`. O helper deve carregar `station_retroarch`, passar `getApplicationInfo().nativeLibraryDir + "/libstation_retroarch.so"` e chamar a ponte antes de `super.onCreate`, quando a thread NativeActivity ainda não iniciou. A biblioteca da ponte chama-se `station_startup_logging`. Falha da ponte é diagnóstica e deve retornar ao fluxo normal do jogo.

A resolução usa exclusivamente `RTLD_NOLOAD | RTLD_NOW` no caminho fornecido. Os três símbolos devem pertencer a essa mesma imagem segundo `dladdr`. Nenhum nome alternativo ou `RTLD_DEFAULT` é usado. O handle permanece válido durante todas as chamadas; ao retornar é liberada somente a referência adquirida pela ponte. Uma exceção da obtenção opcional da string JNI é limpa localmente; nenhum caminho, texto de loader, conteúdo, conta ou segredo é registrado.

O nível inicial INFO (1) permite observar o bloqueio de firmware anterior à leitura do cfg, que usa `RARCH_LOG`. O cfg diagnóstico pode continuar com `log_verbosity=true`, `frontend_log_level=3`, `libretro_log_level=3` e `log_to_file=false` para reduzir os registros posteriores aos erros. Não chamar `verbosity_disable` no teardown enquanto o worker puder usar o logger; a restauração do APK R139 encerrará o diagnóstico.

O ELF R139 exporta as três funções. A busca das fontes pinadas não encontrou reset do bool em `rarch_main`, `getargs`, alocação/liberação das configurações ou NativeActivity. `check_verbosity_settings` pode desabilitar se algum cfg contiver explicitamente `log_verbosity=false`. A console Android é nula e o attach inicial tem guard contra frontend ausente. Estas são evidências estáticas; o loader e o caminho real ainda precisam ser conferidos no Android.

## Compilação após congelar a fonte

```text
python native/build_sidecar.py --ndk NDK_R28C --runtime EXACT_R139_SO --source-commit FROZEN_40_HEX_COMMIT --output ABSOLUTE_NEW_DIRECTORY
```

A receita exige que C, receita, licença e recibo base coincidam byte a byte com o commit explícito antes de compilar. Confere NDK r28c, hash exato do runtime de entrada, ARM64/API26, alinhamento de 16 KiB, único export JNI e preservação do runtime. A saída deve ser nova e externa ao repositório, ao NDK e à pasta do runtime. Não usa ADB, assinatura ou instalação. `base-receipt.json` não afirma compilação nem execução.

Qualificação Android isolada possível após autorização: um probe `app_process64` carrega a biblioteca exata R139 com suas dependências e esta ponte, chama o export por Java e observa `INFO_ENABLED`. O probe precisará de recibo próprio; esse resultado não substitui inicialização NativeActivity nem gameplay.

Licença deste código: GPL-3.0-or-later, acompanhada do texto em `COPYING`.
