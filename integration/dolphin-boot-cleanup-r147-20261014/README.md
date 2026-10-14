# Dolphin: posse do recurso de inicialização — preparação privada R147

Esta correção é independente da rota v3 R146 e da linha nativa que limpa `s_is_booting` quando `RunNetPlay` recebe zero. Nada foi publicado, compilado no produto ou instalado.

## Defeito demonstrado

O donor real `NetplaySession` está no DEX10 SHA `09ed47c40c4a6f5194bcb9ace23f85392b99c19c84cd654e61716de37b32e01c`, classe SHA `7dcbc2c67298d18e7ffe5b4839e73ca6967a0318e4628269598bef9a45ec2315`. R144/R145 mantêm esses bytes. A fonte Kotlin original R126 fornece contexto; a produção também contém os hooks Station adicionados no smali. O overlay usa essa classe real completa e mantém todos os hooks.

`consumeBootSessionData()` lê o campo e depois grava zero sem monitor. A saída autorizada, em `releaseNativeResources()`, também lê o campo, grava zero e chama o delete JNI sem compartilhar monitor com o consumidor. A thread `NativeEmulation` pode ler P, a saída liberar P, e a primeira thread ainda retornar P ao `RunNetPlay`, que cria um `unique_ptr` do mesmo endereço. O recurso já liberado ganha outro dono. Dois consumidores também podem ler P antes de qualquer gravação zero.

`audit_ownership.py` executou as instruções exatas desses métodos sob barreiras de duas threads e demonstrou ambos os casos. O JNI foi representado por um registro de posse, sem executar acesso/liberação indefinidos. A prova estabelece o defeito de código; não identifica uma ocorrência nos testes físicos relatados.

## Escopo mínimo

| Método real | Mudança |
| --- | --- |
| `consumeBootSessionData()` | Ler e retirar a posse sob monitor curto de `NetplaySession.class` |
| `isLaunching()` | Ler sob o mesmo monitor |
| `releaseNativeResources()` | Usar o claim existente acima; liberar recurso não nulo depois que o monitor saiu |
| `onBootGame(String,long)` | Oferecer ponteiro sob o mesmo monitor; após `isClosed`, descartar nova entrega; liberar pendência substituída fora do monitor |

Zero fields/métodos/classes novos. A classe proposta tem SHA `00869b191ffc794d32aaad2f787be11c80188395953ebd7f8a5c95bec69dd1de`. Inverter os quatro corpos recupera a classe original inteira. Todos os outros métodos, fields, annotations, debug metadata e o restante do callback de lançamento permanecem exatos. `closeBlocking()` e `finalize()` não mudam. Nenhuma alteração em CPU/JIT, motor/perfis, controles, entradas, salas, READY/ACK ou arquivos de jogos/firmware.

## Encerramento e ordem dos locks

O DEX10 completo, 4.991 classes, foi inspecionado por instruções de campos. O campo de boot é privado; as seis referências originais pertencem somente aos quatro métodos acima. `isClosed` é `volatile`; seu único writer de bytecode é `closeBlocking`, preservado. A leitura volatile do callback vê o fechamento sem exigir que esse store adquira o monitor de posse.

`closeBlocking` já segura o monitor da instância durante os deletes nativos. O destructor do cliente pode esperar uma thread que executa callback JNI. Por isso o novo callback **não** toma o monitor da instância. O monitor da classe contém somente acesso ao campo e condições, sem JNI, callback Station, join ou espera externa. O fechamento pode seguir instância → classe por tempo curto; não existe classe → instância no overlay. O teste de callback durante join concluiu; a variante negativa que usa `this` bloqueou o callback como previsto.

O monitor da classe cria uma relação explícita entre instâncias: pequenas operações de posse de boot ficam serializadas. Não serializa emulação, frames, I/O, liberação nativa ou callbacks e não cria timers/threads.

## Política de posse

- Claim entrega o ponteiro não nulo a um único consumidor e deixa zero.
- Fechamento, repetição de release/finalize e dois consumidores não liberam o ponteiro duas vezes.
- Uma nova pendência substitui somente a que ainda está armazenada; a antiga é liberada uma vez fora do monitor.
- Uma notificação repetida do mesmo ponteiro ainda pendente não o libera; o dispatch anterior permanece.
- Depois de `isClosed`, ponteiro novo não nulo é liberado e não dispara launch. Se ele ainda coincide com a pendência aguardando cleanup, a saída retém o único descarte.
- Ponteiro zero nunca vai ao delete JNI. Consume zero continua permitido; a limpeza nativa do boot flag é a correção separada.
- O produtor nativo deve transferir cada `unique_ptr` uma vez. Redelivery arbitrário de ponteiro já transferido exigiria geração/lease e não é declarado resolvido.

## Provas realizadas e limite

`fixed_ownership_probe.py` executou os quatro corpos smali propostos e os corpos originais de close/finalize. Onze verificações passaram: handoff único, cancelamento/repetição de cleanup, disputa com saída, dois consumidores, entrega atrasada, substituição/mesma pendência, zero, callback durante join, rejeição do lock incorreto e preservação da autorização humana. Todo JNI/callback do fixture verifica que o monitor de posse já saiu.

`evidence/ownership-scope.json` contém todos os hashes de métodos; `field-scan-proof.json` registra os fields exatos e scan completo; `baseline-race-proof.json` e `patched-ownership-proof.json` conservam os resultados. `reference-java` contém somente excertos legíveis, não fonte para substituir a classe Kotlin. `smali` contém o overlay produtivo candidato.

As instruções são interpretadas por fixture estrito, não executadas em ART/JNI. Opcode desconhecido alcançado é recusado. Os caminhos normais de monitor/cancelamento foram exercitados; catchall é declarado no smali, mas exceções dentro do monitor não foram injetadas. A montagem real deve usar o donor DEX10 exato, decodificar a saída, inverter a classe inteira e provar as outras 4.990 classes idênticas. Ainda faltam montagem/verificação de DEX e core, integração da linha nativa separada, APK/assinatura/kit e testes Android autorizados de entrada/saída/perda de sinal.

## Projeção canônica para o guard posterior

`CanonicalizeOwnership.java` qualificou a sintaxe com o parser pinado, mantendo o único ClassDef em memória; não escreveu DEX. O parse/emit da baseline recuperou seus bytes exatos. A candidata canônica tem SHA `ed45e5272b1d554d26e702b6d168b1e49ce1f14144b25451858e8cc78c542690`, em `evidence/canonical-proposed-NetplaySession.smali.txt`. Seus quatro métodos possuem as mesmas instruções, destinos de branches, registros e intervalos catchall da candidata legível; somente os nomes dos labels são normalizados.

`verify_projection.py` exige esses bytes canônicos exatos, compara 40 fields/63 métodos, conserva os 59 métodos não alterados e substitui apenas os quatro corpos permitidos pelas baselines. O resultado deve ser a classe original completa. Três guardas negativas recusaram mudança de volatile, lock da instância e callback Station. A receita real posterior precisa vincular esse guard ao decoder do DEX realmente gerado e provar as outras 4.990 classes; o parse em memória não substitui essa etapa.
