# Probe JNI separado e opcional

Não incluir esta classe no APK: ela possui o mesmo nome JNI do helper produtivo, mas é somente uma entrada `app_process64` em outro processo. A biblioteca ae72 tem somente dependências Android padrão e não exporta `JNI_OnLoad`; carregá-la não cria NativeActivity.

Compilar apenas depois do commit de fontes, junto da sidecar:

```text
python native/probe/build_probe.py --jdk-bin JDK17_BIN --d8-jar D8_JAR --android-jar ANDROID34_JAR --sidecar SIDECAR_SO --sidecar-receipt SIDECAR_RECEIPT --runtime EXACT_R139_SO --source-commit FROZEN_COMMIT --output ABSOLUTE_NEW_DIRECTORY
```

A receita gera somente JAR/dex e recibo local. Não usa ADB e não executa o probe. A execução Android exige coordenação/autorização própria e arquivos temporários nominados, sem APK auxiliar, dados/configuração do Station ou execução de jogo.

O operador deve conferir os hashes da biblioteca ae72 e da sidecar nos temporários. A biblioteca ae72 deve se chamar `libstation_retroarch.so` no caminho passado. A entrada Java é `org.emulationstation.frontend.netplay.StationStartupLogging`; argumentos: caminho absoluto do runtime e caminho absoluto da sidecar, nessa ordem.

Sete verificações: caminho nulo, relativo, basename diferente e traversal são recusados; runtime ainda não carregado é recusado sem fallback; após `System.load(runtime)` a habilitação passa; uma repetição passa após a ponte liberar sua própria referência. A emissão `INFO_ENABLED` implica resolução/origem das três funções e query verdadeira, usando o ELF real. Não testa exports ausentes, pressão de memória, concorrência de NativeActivity, core, driver, gameplay ou coleta do aplicativo. O processo isolado termina ao concluir; não interfere no logger do processo do Station.
