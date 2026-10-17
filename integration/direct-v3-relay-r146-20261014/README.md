# R146 — conexão direta do relay v3, preparação privada

Escopo produtivo proposto: `integration/direct-v3-relay-r146-20261014`. Esta preparação lê o APK final R145, SHA `275f31b34145eb77c457b1a9c09bbff4034cc28a990b74121b0b1fd4573c5df0`, 2.715.057.167 bytes, fonte `25d10b2322d2e5687c9dfacc71a826c3955fad5d`. Donor real DEX35: `5f36d5d9b2786a2877616bedffa227f83503621ec4e7eeb24b73a19264e4f089`, 608 classes.

## Fluxo e mudança

O cadastro, a autenticação, a sala e a emissão/renovação dos tickets continuam na API atual. `StationMultiplayerSession.Channel` continua verificando o ticket de cada ligação. Ao construir o túnel v3, passa a usar a URI fixa `wss://downloads-station.lzgames.com.br/v1/station/online/multiplayer/relay` e a fábrica dedicada `StationRelayTls.createMultiplayer()`. Essa fábrica usa o SPKI direto `bcd134d59fcdbb35e0343c86d31a666cc95cf158d70b27aceceefd19158d072f`, chama o mesmo gerenciador de confiança do sistema e reutiliza `pinned()` intacto.

`endpoint()` e `create()` permanecem exatos, com a origem `app.lzgames.com.br`, rota `/v1/station/online/relay` e pin API `13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7`. API/login/downloads e seus clientes TLS não mudam. O `StationMultiplayerTunnel.Remote.onSetSSLParameters()` real continua definindo identificação de hostname `HTTPS`. Não há fallback, pin permissivo ou URI fornecida por preferência.

O caminho assinado do ticket permanece `/v1/station/online/multiplayer/relay`, protocolo `station-stream.v3`, janela 262.144 bytes, provas/roles/slots/expiração e canais iguais. Callbacks, confirmação de prontidão, ACK, barreiras nativas, timeout, reconexão, saída, HLE, multitap, downloads e mitigação g52 estão fora do delta.

## Allowlist produtiva

| Classe real no DEX35 | Delta |
| --- | --- |
| `StationRelayTls` | Substituir somente `multiplayerEndpoint()`; adicionar uma fábrica `createMultiplayer()` igual a `create()` exceto nome/pin |
| `StationMultiplayerSession$Channel` | Uma invocação de fábrica na construtora: `create()` → `createMultiplayer()` |

Nenhum field/classe novo. Um método novo. As outras 606 classes do DEX35 e os outros 39 DEX devem ser preservados. As fontes Java de leitura/testes vêm da TLS R124 e da Session produtiva em `integration/psx-online`; as classes reais R145/R144/R143 conferidas são exatas para esses consumidores. Produção usa os dois donors smali reais, sem restaurar Session/Activity histórica.

## Provas e testes já executados

`evidence/route-scope.json` registra os hashes das 608 classes reais, 39 DEX preservados, métodos originais/propostos, fontes Java e retorno do servidor. Invertemos as duas classes completas e as duas fontes Java, recuperando os originais. `evidence/host-test-receipt.json` registra 20 verificações da fonte TLS proposta e cinco guardas negativas. O teste de CA/pin usa bordas JSSE inertes e certificados sintéticos; não abre sockets. Ele verifica a fábrica direta/API, delegação à CA do sistema, pin errado, cadeia vazia/nula e ausência de efeito sobre a fábrica antiga. A identificação `HTTPS` está no WebSocket real preservado e removê-la faz o guard recusar o conjunto.

Somente a fonte TLS e o probe foram compilados em JVM de teste. Não houve montagem DEX, APK, assinatura, servidor ou telefone. Gameplay Android pela rota direta e efeito de latência continuam pendentes. O servidor já provou duas ligações WSS autenticadas e recusou replay no seu retorno; isso não homologa os quatro motores em aparelho nem cria aprovações PSX HLE.

## Congelar e montar DEX depois da revisão

Copiar `java`, `recipe`, `tests`, `evidence` e este README ao escopo novo. `prepare_route_private.py` é apenas o gerador privado já executado: não é receita produtiva e não precisa ser publicado. Congelar tudo num novo commit completo antes de executar o builder. Ele recusa execução dentro da preparação privada, fonte diferente do commit, APK/tool/hash errado ou saída existente.

```powershell
python -B integration/direct-v3-relay-r146-20261014/recipe/build_dex.py --base 'F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R145-azul-ceu-faixas-20261013.apk' --jdk-bin 'F:/TurboStations-Backup-Completo-20261011/ferramentas/jdk17/bin' --apktool 'F:/TurboStations-Backup-Completo-20261011/ferramentas/apktool_3.0.3.jar' --out 'E:/StationDirectV3RelayR146-20261014/dex' --source-commit COMMIT_COMPLETO_NOVO
```

O builder compila somente três ferramentas, decodifica o DEX35 pinado, copia todas as classes e aplica a allowlist. O assembler conserva initializers estáticos explícitos inclusive nas classes alteradas. Após gerar o DEX, o decoder lê esses bytes reais novamente. As duas classes devem corresponder exatamente aos smali congelados; retirar a fábrica e inverter a URI/callsite precisa recuperar as classes completas originais. Qualquer método, field, annotation, label ou debug metadata adicional falha. As outras 606 classes são comparadas integralmente antes/depois.

Saídas: `classes35.dex` e `dex-compilation.json`, schema `station.r146.direct-v3-relay.dex.v1`, um payload/um scope, um método novo, zero fields/classes novos, maps completos, inverse por classe/método e 39 DEX preservados. O schema declara DEX compilado, não APK ou instalação. Identidade dos motores, montagem/assinatura, kit e testes físicos pertencem às etapas seguintes. Eventual correção nativa Dolphin autorizada tem evidência e receita própria, separada deste delta Java.
