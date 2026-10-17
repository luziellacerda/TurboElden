# R165 N64 online: saída humana confirmada

Correção delimitada para a saída explícita do anfitrião. A base é a tag
`estavel-station-r164-20261015` (`a762b4614d4c1909ea9482028c4d6464de49f2a2`).
Este diretório é uma **candidata de fonte**. Não contém APK, DEX, chave, ROM,
instalação ou publicação no servidor.

## Mudança produtiva

Substituir somente `StationHumanDeparture` da camada R135 pela fonte em
`java/org/emulationstation/frontend/netplay/StationHumanDeparture.java`. A
assinatura pública e o caminho `StationGameSession.event(4)` não mudam. O
evento 4 continua sendo a única autorização humana; queda de sinal, callback
de ciclo de vida e retomada não criam saída.

Para o motor N64 v3 identificado pelo `engineId` da sala assinada, uma falha de
transporte (`Offline`, `SocketTimeoutException`, `SocketException`,
`EOFException` ou `UnknownHostException`) leva a
uma consulta da **própria sala** pela API autenticada. Se o alvo já não consta,
a saída está confirmada. Se a sala persiste, só uma igualdade de `roomId`,
geração e dos nove campos de identidade permite **uma única** repetição do
mesmo objeto de pedido. O `StationOnlineClient` congelado acrescenta
`clientMaximumPlayers=5`, `page=0` e `roomPageSize=32` ao primeiro envio; o
cliente desse evento é privado e sua página não muda. Reutilizar o objeto
mantém `requestId` e corpo completos iguais, exigência do recibo idempotente
do servidor. Resposta sem ausência, erro na segunda tentativa, perfil/licença
recusado, assinatura inválida, identidade ou geração alterada encerram a tarefa
como não confirmada. Não há timer, agendador, loop nem worker adicional.

Os demais motores v3 mantêm o comportamento R164 para falha de transporte. A
recuperação R135 de um **409 exato** `STATION_MULTIPLAYER_GENERATION_MISMATCH`
também permanece: essa recusa prova ausência de mutação e pode usar nova
geração e novo `requestId` somente após conferir a mesma identidade assinada.

## Teste reproduzível sem telefone

`tests/run_probes.py` exige os JDK17, Android API34, `rooms.jar` e
`client.jar` com os hashes congelados em
`integration/online-lifecycle-review-r135/SOURCE-PINS.json`. O JAR `org.json`
de teste é `json-20240303.jar`, SHA-256
`3cf6cd6892e32e2b4c1c39e0f52f5248a2f5b37646fdfbb79a66b46b618414ed`.
Passar os caminhos explicitamente; a saída deve ser uma pasta vazia fora do
repositório. O script não usa rede, servidor, ADB ou emulador Android.

```text
python integration/n64-host-exit-r165/tests/run_probes.py \
  --jdk-bin <JDK17_BIN> --json-jar <JSON_JAR> \
  --android-jar <ANDROID34_JAR> --rooms-jar <ROOMS_JAR> \
  --client-jar <CLIENT_JAR> --out <EMPTY_OUTPUT_DIR>
```

Resultado neste worktree: **71 verificações passaram**. O teste adversarial
compara a serialização JSON completa dos dois pedidos após os campos de página
serem acrescentados. Também cobre resposta perdida após mutação, resposta
perdida antes da mutação, segunda falha, geração/identidade divergente, sala
nova, snapshot inválido, recusa do servidor, cancelamento, erro genérico de
assinatura/protocolo e isolamento do PSX. A fonte produtiva compila com Java 8
contra as classes congeladas da API34. A fixture representa a borda de rede;
não comprova partida física nem substitui a verificação de assinatura real.

## Receita de montagem posterior

Usar **o APK R164 assinado exato** SHA-256
`903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210`
como doador. Compilar a fonte acima com os três JARs congelados e substituir
apenas a família `StationHumanDeparture` em `classes35.dex`; comparar o
inventário de tipos e todos os demais membros da partição. A receita R135
`build_dex.py` fixa um doador R134 e **não deve ser executada diretamente**
sobre a R164; preparar uma receita R165 com os novos hashes e a mesma checagem
de escopo. Preservar `classes36.dex`, a ponte de vídeo N64, o carrossel,
frontend, núcleos, bibliotecas offline e as demais entradas byte a byte.

Como `classes35.dex` integra a identidade de runtime, recalcular os três
marcadores ELF e `assets/station-online/engines.json` para os quatro motores,
preparar o kit privado e obter o recibo de cadastro R165 antes de uma partida.
Conferir as cinco entradas alteradas no APK candidato, assinatura original e
hash instalado em dois aparelhos. Testar saída do anfitrião com o convidado
conectado e perda de resposta de rede, observando o aviso e o retorno à sala.
Nenhum artefato privado desta receita deve ir ao Git público.
