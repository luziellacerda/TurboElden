# R139 — helpers JNI/TLS no Android real

A probe isolada passou no moto g52, Android API 33, em 13/10/2026. Usou uma `JavaVM` real e threads/destructors `pthread` reais, em processo próprio iniciado por `app_process64`. Não instalou APK companion, não abriu/parou o TurboStations, não acessou seus dados, jogos ou configurações. Os dois arquivos temporários e a pasta criada foram removidos nominalmente; a ausência da pasta foi conferida.

O teste extraiu sem edição `station_jni_key_ensure`, `jni_thread_getenv` e `jni_thread_destruct` da fonte R139 SHA-256 `24420118e5ce94376b077051084a84d4c52f152d00b9e2330333896bced798fb`. A biblioteca de diagnóstico continha um marcador de presença de contexto em `g_android`; não referenciava Activity ou memória do aplicativo. Um wrapper de `pthread_key_create` contou a criação e observou o destructor, chamando o destructor produtivo com a VM real. Essas bordas de observação não entram no APK.

## Resultados físicos

| Verificação | Resultado |
| --- | --- |
| Inicialização repetida | 100 chamadas aceitas, uma tentativa e uma chave criada |
| VM ausente/divergente | Ambas recusadas; outra chave não foi criada |
| Thread Java principal | 20 consultas com o próprio `JNIEnv`, zero registros na chave do helper |
| Outra thread criada por Java | 20 consultas com o próprio `JNIEnv`, zero registros na chave do helper |
| Threads nativas | Oito threads inicialmente desanexadas; 160 consultas corretas; oito registros TLS com a VM real |
| Destructor após limpar contexto | Oito callbacks executados na própria thread, todos depois de `g_android=NULL` |
| Estado da VM no destructor | As oito threads estavam anexadas antes e desanexadas depois do destructor produtivo; nenhuma já estava desanexada antes |
| Contexto ausente no getter | Recusa confirmada |
| Erros de VM/thread/ownership | Zero |

O recibo [android-jni-resource-probe.json](evidence/android-jni-resource-probe.json) guarda somente contagens, modelo, API, hashes, horário UTC e resultado da limpeza. Não contém serial, ponteiros, credenciais, conteúdo pessoal ou logs Android integrais. [build-receipt.json](evidence/build-receipt.json) registra os hashes da fonte extraída, receita, compilador, SDK e artefatos.

## Fontes e reprodução

`src/R139ResourceProbe.java` testa a thread Java principal e outra thread Java antes dos oito workers nativos. `src/resource_probe.c.in` observa a chave/destructor real, aguarda os oito workers terminarem suas consultas e publica `g_android=NULL` sob a sincronização da probe. Só depois permite que terminem, executando o teardown TLS do kernel. `GetEnv` antes/depois distingue o nosso detach de uma eventual limpeza automática anterior da VM. As funções extraídas mantêm sua licença original; ver `COPYING`.

`build_probe.py` exige a fonte R139 exata, NDK, JDK, D8, Android JAR e pasta de saída nova fora do repositório. Compila a biblioteca ARM64/API26 com alinhamento de 16 KiB e um JAR contendo DEX. Não executa USB, não instala APK e não abre conexão externa:

```text
python build_probe.py --source FONTE_R139/platform_unix.c --patch-recipe RECEITA_R139/patch_resource_lifecycle.py --ndk NDK_R28C --jdk-bin JDK17_BIN --d8-jar D8_JAR --android-jar ANDROID34_JAR --output PASTA_NOVA_FORA_DO_REPOSITORIO
```

A execução física autorizada utilizou somente `/data/local/tmp/station-r139-resource-probe-20261013`, que precisava estar ausente antes. JAR e biblioteca foram conferidos por SHA-256 no aparelho antes da execução. O processo tinha prazo de 20 segundos. A limpeza apagou somente os dois arquivos nominais criados e removeu a pasta vazia; não houve limpeza global de logs, dados ou diretórios.

## Limites

Esta prova acrescenta validação Android real aos testes locais de alocação/TLS. Ela não executa `android_app_create`, o handshake de uma NativeActivity, o renderer, o core, a saída de uma partida ou a rede. Não valida o APK completo nem mede CPU, temperatura ou FPS. A fonte produtiva e seu freeze permaneceram intactos; compilação e instalação do APK final têm recibos próprios.
