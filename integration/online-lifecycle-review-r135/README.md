# R135 — revisão de saída e lifecycle online

Estado: **candidata de fontes**, sobre a fonte R134 `4f9039eb9ce13907ce043870bfe1f6e294888556`. Esta pasta contém correções Java isoladas e testes locais. Não representa APK R135, instalação, ativação de servidor ou validação de gameplay.

## Correções concluídas

### 1. Saída explícita GameCube/Wii: ciclo entre monitores

Na fonte R126 efetiva, `StationDolphinSession.Session.closeByHuman()` mantinha o monitor da Session enquanto chamava `StationMultiplayerSession.close()`, que toma o monitor do transporte. O callback `unrecoverable()` do transporte mantém esse segundo monitor enquanto chama `Session.fatal()`, também sincronizado. Uma saída humana concorrente com uma falha da conexão produz a ordem Session → transporte na interface e transporte → Session no callback. Ambos ficam bloqueados, inclusive a interface Android.

A correção mantém a checagem, autorização humana e flags `closing`/`visible` dentro de um bloco curto da Session. O fechamento do transporte acontece depois de soltar esse monitor. A autorização JNI e o cancelamento do transporte continuam independentes do lock nativo `operations`, permitindo cancelar um Join em andamento. `StopEmulation`, `closeBlocking` e liberação do owner permanecem no worker serializado. Não foi acrescentado encerramento automático de partida nem encerramento forçado de processo.

O teste executa o método real `closeByHuman()` e o callback real de `StationMultiplayerSession`, com bordas Android/JNI/rede substituídas por fixtures. Latches criam a disputa de modo determinístico. `ThreadMXBean.findDeadlockedThreads()` comprova o ciclo na base. A candidata conclui os dois caminhos e o cleanup dentro do prazo do teste.

### 2. Saída humana v3 após rejeição por geração antiga

`StationGameSession.event(4)` enviava um único Leave com a geração guardada no lançamento e ignorava qualquer exceção. O servidor recusa a geração antiga antes de alterar a sala. O retorno ao lobby v3 não repetia essa saída. Portanto, o usuário podia voltar e continuar como membro remoto.

`StationHumanDeparture` trata somente a saída humana do evento 4. Primeiro envia a mesma operação para a geração original. Apenas uma rejeição HTTP 409 com código exato `STATION_MULTIPLAYER_GENERATION_MISMATCH` permite consultar um snapshot autenticado pela API existente. Uma sala própria ausente, ou outra sala própria, confirma que o alvo antigo já não pertence à sessão; nenhuma outra sala é alterada. Para repetir Leave, todos os campos abaixo devem corresponder ao lançamento: `roomId`, `recoveryProtocol`, `itemId`, `engineId`, `coreSha256`, `runtimeSha256`, `contentSha256`, `profileId`, `profileSha256`. A nova geração deve ser maior e positiva. A repetição acontece uma única vez, com outra `requestId`, porque a primeira rejeição já é prova de que não houve mutação.

As respostas de Leave devem mostrar ausência do alvo na sala própria antes de declarar a conclusão. Timeout, erro de rede, HTTP 500, outros códigos 409, negação de licença/perfil, snapshot antigo, identidade diferente ou cancelamento não autorizam nova mutação. Exceções recebem somente um diagnóstico categórico `human-leave-unconfirmed` e o nome da classe, sem texto de erro, credencial, conteúdo de pacote ou identidade pessoal.

## Verificação local

`tests/run_probes.py` exige caminhos explícitos para JDK, Android API34, JAR de classes online efetivas, cliente congelado e JSON; também exige os SHA256 previamente conferidos em um arquivo JSON. Não procura aparelhos, não acessa rede e não executa ADB. Os inputs e fontes são conferidos antes/depois dos testes.

Os dois cenários usam classes produtivas reais, primeiro sem a correção e depois com o overlay:

- Base Dolphin: ciclo de monitores comprovado. Candidata: saída e callback terminam.
- Base evento 4: membership persiste após rejeição da geração. Candidata: consulta própria, verifica identidade completa e conclui a saída.
- Casos adversariais: diferença de cada campo da identidade, outra sala, ausência, requestId diferente, cancelamento, snapshot antigo, resposta sem confirmação de ausência, erro de rede/perfil/membership e HTTP 500.
- Compilação das fontes reais contra Android API34, produção com alvo Java8. As fixtures Android/JNI não entram no payload.
- Receita e probes recusam um classpath sintético alternativo mesmo quando o arquivo de hashes do operador contém o digest correto desse outro arquivo; a recusa ocorre antes de criar saída ou compilar. Recibo: `evidence/input-pin-rejection.json`.

O recibo está em `evidence/test-receipt.json`. Cada sucesso comprova o cenário descrito; não mede latência Android, estabilidade em aparelho ou operação do servidor.

Exemplo de invocação, com paths definidos pelo operador:

```text
python tests/run_probes.py --jdk-bin <JDK_BIN> --android-jar <ANDROID_JAR> --rooms-jar <ROOMS_JAR> --client-jar <CLIENT_JAR> --json-jar <JSON_JAR> --out <WORK_OUTPUT> --input-hashes <INPUT_HASHES_JSON>
```

O arquivo de hashes contém exclusivamente os digests de `javac`, `java`, `androidJar`, `roomsJar`, `clientJar` e `jsonJar`. O JAR de cliente deve ser o congelado R124, SHA256 `011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313`. O JAR rooms deve corresponder ao overlay efetivo R124 → R125 → R126 → PSX do recibo atual, não a uma Activity histórica escolhida por data.

## Integração posterior

`recipe/build_payload.py` reproduz separadamente o JAR produtivo. Ele exige os hashes testados de JDK17, Android API34, rooms R134 e cliente R124 congelado, fixados no `SOURCE-PINS.json` público junto das fontes base e overlay exatas. O arquivo de hashes informado também deve corresponder a esses pins; outro SDK/JDK/classpath é recusado antes de compilar, mesmo que o operador informe o hash desse outro arquivo. Os probes exigem adicionalmente os mesmos pins de java e JSON. A receita compila somente as três fontes produtivas com alvo Java8 e sourcepath vazio. O JAR contém exatamente as nove classes enumeradas, sem fixture, SDK ou dependência incorporada. Timestamps ZIP determinísticos permitem repetir o mesmo SHA256. O recibo inclui hashes de inputs, fontes, classes, pins e receita. O diretório de saída deve estar vazio; a receita não remove arquivos.

```text
python recipe/build_payload.py --jdk-bin <JDK_BIN> --android-jar <ANDROID_JAR> --rooms-jar <ROOMS_JAR> --client-jar <CLIENT_JAR> --out <EMPTY_WORK_OUTPUT> --input-hashes <INPUT_HASHES_JSON>
```

A execução conferida reproduziu o JAR anterior byte a byte: SHA256 `8e746f8fa449cfebae14b9db68b0080ffa9a9bfb6a45300449c4d2f7c9ce2bc4`, nove classes Java8. O recibo público está em `evidence/compile-production.json`. Esta etapa não cria DEX, APK ou instalação.

Aplicar somente as três fontes desta pasta, como último overlay sobre a cadeia efetiva: `StationDolphinSession`, `StationGameSession` e `StationHumanDeparture`. As fontes congeladas R124/R125/R126/PSX permanecem intactas. Nenhuma assinatura pública, protocolo, porta, capacidade, perfil ou core foi alterado. O bundle final, se montado, precisará de verificação de classes/entradas/assinatura e identidade runtime renovada conforme os recibos; nenhum ID novo foi inventado nesta revisão.

## Pendências reais

1. Uma falha de rede na saída ainda pode deixar a participação remota ativa. Há um diagnóstico, porém esta candidata não grava um novo intent persistente nem altera o `StationRoomLeaveIntent`/Presence existente, que preserva geração exata. Essa pendência requer uma política de confirmação durável revisada e um teste de interrupção/reabertura; não é seguro repetir Leave de outra sala ou geração apenas por timeout.
2. O bloqueio Dolphin foi reproduzido em JVM. Não há trace Android que prove que o diálogo relatado pelo usuário veio desse caminho, nem teste físico da correção.
3. A NativeActivity RetroArch tem esperas sem prazo para estado/janela/input/destruição; o pedido de quit usa flag atômica e wake do looper. Esse wake não interrompe automaticamente um core, driver GL/audio ou save preso. Trata-se de hipótese concreta para investigação com trace, não defeito causal confirmado por esta revisão.
4. N64/PSX não mostram o mesmo ciclo Java da saída Dolphin. Os waits PSX de transporte/SDL estão fora da interface, mas uma thread que nunca termina pode impedir a conclusão humana indefinidamente; o teste JVM não valida drivers/emuladores reais.
5. Uma sala de três participantes tem dois links e quatro anexos relay. O estado Playing exige todos os Hello/Paused/Ready da época atual e buffers pendentes zerados. Um peer que mantém PING e não conclui READY pode deixar espera indefinida. Não há prova de qual emulador/link/barreira ficou preso na partida relatada. Não foram relaxados READY, ACK real, geração, perfil ou licença para forçar o início.

## Próxima validação autorizada

Confirmar primeiro jogo/edição, plataforma, APK/hash e sequência exata da falha. Depois do pacote final conferido e de autorização para teste em aparelhos: entrar com dois/três participantes, registrar somente categorias e estado de cada link/barreira, sair durante carregamento/sincronização/gameplay, repetir a saída concorrente com queda de rede, verificar retorno ao lobby e ausência da sala antiga no snapshot fresco. Uma nova saída ou uma falha não deve encerrar outra sala, iniciar outro jogo ou interromper downloads. Testar os mesmos cenários para N64/PSX/RetroArch preservando owners normais e rotas offline.
