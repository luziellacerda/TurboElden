# Entrega única APP → SERVIDOR — R132

**Compilação/identidades finalizadas; instalada no Motorola; kit privado preparado, ainda não recebido/aplicado no servidor.** Fonte executável R132 `56ba83b7fcc5c243ae50052fec9b6f4141e1b5f1`; APK SHA256 `47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20`, 2.711.825.423 bytes. Assinatura original v2/v3 e alinhamento 16 KiB conferidos. [STATUS](STATUS.json), [recibos finais](evidence/PUBLIC-EVIDENCE.json) e [manifesto público do kit](evidence/server-kit-manifest.json) registram os selos. Decisões de modos, operação administrativa, ativação e gameplay não estão confirmados por esta entrega.

A instalação foi concluída **somente no Motorola Edge 30** em `2026-10-11T20:54:08.764316+00:00`, com SHA integral final, UID/dados/assinatura preservados e frontend oficial observado às `20:54:12.047096 UTC`. O [recibo de instalação](evidence/installation.json) não publica serial ou sessão. Isso não comprova sessão autenticada, gameplay, consumo térmico ou cadastro do servidor e não declara atualização do Samsung.

## Bloqueio físico reproduzido antes da sala

Na R132 instalada, **Criar sala** para a edição N64 selecionada exibiu exatamente: “Não há modo aprovado para esta edição e o motor instalado. Atualize o aplicativo e o catálogo nos participantes.” A primeira ação segura refez capabilities e manteve a recusa antes de criar sala ou iniciar jogo. O motor N64 instalado é `mupen64plus-ae-33bf7021-n64-v3-6b41b91a4914`; o operador precisa conferir o vínculo entre esse motor atual e a edição/conteúdo/modo aprovado, em vez de cadastrar uma identidade antiga.

Não capturamos código HTTP ou envelope bruto: **não declarar HTTP 409 físico**, prova assinada de ativação, nem qual dimensão específica do vínculo faltou. A mensagem de UI não exige gerar outro APK: a R132 exata já está instalada e esta entrega mantém suas validações. [Recibo físico agregado](evidence/physical-observation.json), sem nomes, capturas ou logs pessoais.

## Objetivo e lacuna concreta

Cadastrar em uma única transação os motores finais R132 de **PSX, N64, GameCube e Wii**, conservar os registros anteriores e devolver uma matriz única de modos aprovados/recusados com prova assinada fresca. PS3/PS4 são exclusivamente offline e não entram nesse cadastro. A R132 não pede modificação do transporte, core, opções, perfis de controle ou segurança do serviço.

O [retorno real a6b58e9](https://github.com/luziellacerda/Servidor-pix/blob/a6b58e9beb12eb564c1b58d9d4c32ed3e7513861/docs/station-android/online-plataformas-20261009/r128-retorno-servidor-20261011.json) revisou o **kit R129**. Declarou `scriptsEffectivePublicationConfirmed=false`, `privateKitReceived=false`, `newFinalEnginesActivated=false` e autenticação administrativa nativa necessária. As 68 verificações administrativas relatadas são isoladas; não comprovam a ativação R132. Código disponível no Git e PID/DLL históricos também não comprovam o estado atual.

A pendência do operador é concreta: receber o kit R132 exato, publicar os scripts administrativos no caminho efetivamente executado, autenticar a operação nativa e aplicar/verificar uma candidata selada. Não há razão para recompilar o app por mero cadastro. O código v3 examinado suporta hotreload dos dados em dez segundos; este procedimento não solicita reiniciar a API.

### Fechamento em quatro ações

1. Receber o kit atual de 16 arquivos/seis bibliotecas e conferir os hashes, o par original e os quatro IDs R132 desta entrega.
2. Confirmar os scripts/configuração efetivamente executados e realizar a autenticação administrativa na janela nativa Linux, com o operador real.
3. Aplicar em uma candidata selada o manifesto atual e os modos aprovados por edição/conteúdo/controller, preservando os anteriores; devolver recusas com o motivo específico.
4. Confirmar hotreload e capacidades assinadas frescas v3; informar separadamente a revisão publicada das capas N64 e o resultado físico de salas novas. Cadastro não exige recompilar este APK.

### Capas N64: publicação ainda não confirmada

O mesmo retorno `a6b58e9` declarou `covers.published=false`, 2.255 vínculos em preparação, incluindo **157 N64**. `covers.latestProductionBindings` enumerou apenas `megadrive=331`, `snes=671` e `psx=28`. Portanto, os 157 vínculos N64 preparados não podem ser anunciados como publicação concluída. Isso não comprova que inexiste qualquer capa N64 anterior.

O operador deve concluir a atualização de capas já preparada, preservar capas corretas não mapeadas/ambíguas e devolver catálogo efetivamente publicado: revisão, hash, contagens/vínculos N64 e verificação das imagens JPEG 480 × 720. A invalidação existente é `coverId + item.revision`; confirmar a revisão de item realmente publicada, sem reconstruir jogos ou alterar o motor/economia do app. Publicação de capas não habilita o online; ativação dos quatro motores requer as ações acima.

A capa do jogo N64 selecionado apareceu localmente no Motorola. O `covers.published=false` diz respeito à atualização em lote do servidor, não à inexistência de todas as capas locais; nenhuma auditoria física de todas as capas foi concluída.

## Identidade final obrigatória

| Plataforma | ID/runtime R132 | Core preservado | Perfil / teto |
|---|---|---|---|
| PSX | `pcsx-rearmed-ff81ed17-player-v3-6976f8ff2282` / `6976f8ff22820520540b3e5c13fbb1234c21294e3e8c2fd6aaf3a6b0a7e32e2c` | `e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9` | `standard-2p-v1` / 2 |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-6b41b91a4914` / `6b41b91a4914976ec2c5326a7081675d1a7bbf4cd7268dd1a3da8132e580d222` | `fe6e810a1c7fc50a494b50b1dccf581b84385667191c0cbcd235d585a0703dd8` | `direct-four-ports-v1` / 4 |
| GameCube | `dolphin-5102a033-gamecube-v3-f32c0c2f87aa` / `f32c0c2f87aa5ec5c8fb4edd3a8c4ee8b269807d084f7f85bb65fe511335fc2b` | `f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d` | `dolphin-gamecube-four-ports-v1` / 4 |
| Wii | `dolphin-5102a033-wii-v3-f32c0c2f87aa` / `f32c0c2f87aa5ec5c8fb4edd3a8c4ee8b269807d084f7f85bb65fe511335fc2b` | `f7ebe048e030a029c0667cf071ab4a49d702f77daf50d40ad40ed1f493ded37d` | `dolphin-wii-remotes-four-v1` / 4 |

Os tetos não aprovam jogos automaticamente. `allowedPlayerCounts` deve vir da edição/conteúdo/modo revisados. IDs R129/R131 não podem ser reutilizados para o novo bundle. SNES/Mega Drive permanecem preservados por ordem do mantenedor.

## Kit privado preparado e par de recibos

O inventário de 16 arquivos foi conferido por SHA/tamanho, com esta separação lógica:

- `server-kit-original-receipts/runtime-final.json`: original privado final de identidade, sem reserialização;
- `server-kit-original-receipts/package-final.json`: original privado final de verificação, sem reserialização;
- `server-kit-original-receipts/`: também `source-freeze.json`, `engines.json` e `psx-controller-profile.json` originais;
- `server-kit/`: seis bibliotecas, `artifact-kit-receipt.json`, `incoming-engine-manifest.json` e `profile-canonical-receipt.json`;
- `server-kit-tools/`: os dois helpers públicos pinados usados para geração/extração;
- recibo de preparação privado fora do inventário transferível, com proveniência referenciada no manifesto público de hashes.

Invariante conferida: `SHA256(runtime-final.json original) == package-final.json.identityReceiptSha256 == 0278f06066b2853784a66201f289dde21859dd3c647a2832a46159bfd3684b72`. O pacote original tem SHA `85c554c8b55e887a9697fa122444a4375fdee1a39e3852c8972b5a8df0c35728`; source freeze original `a8b360f490dad5e2815f6917f78ff5ef84cd8c0acf7afd5e63233dc339ae501a`. São cópias byte exatas de `runtime-identity.json` e `verified-final.json` originais da compilação. A proveniência de cada recibo público aponta ao SHA de seu original privado. **Não passar o par público sanitizado aos helpers:** os bytes públicos diferem do original cujo selo o pacote exige. Não reescrever o selo, relaxar validação nem interpretar proveniência como substituição do original.

As seis bibliotecas são `libpcsx_rearmed_libretro_android.so`, `libstation_psx_online.so`, `libstation_mupen64plus_core.so`, `libstation_mupen64plus_runtime.so`, `libstation_dolphin_online.so` e `libstation_dolphin_runtime.so`. O extrator validou o APK completo, seus recibos, 20 dependências e hashes, copiando somente essas bibliotecas; os dois JSON gerados depois são permitidos no kit. Sua pasta é uma folha: não colocar recibos originais, subdiretórios ou arquivos inesperados dentro dela. Não incluir firmware, BIOS, material RSA, jogos, mídia, saves, licença ou logs. O manifesto público contém apenas hashes/tamanhos/proveniência; nenhuma biblioteca ou original privado bruto entra no Git.

## Procedimento único do operador

Todos os caminhos das variáveis abaixo devem ser obtidos do kit recebido e da configuração realmente ativa. A [auditoria](../../audits/station-runtime-cleanup-r132-20261011/server-crosscheck.json) registra o callgraph e os 17 selos públicos. O [template administrativo preparatório](../../audits/station-runtime-cleanup-r132-20261011/r132-server-delivery-template.json) foi produzido antes da compilação; seus placeholders não são inputs executáveis. Usar as identidades finais desta entrega e o inventário exato do kit, sem copiar caminhos de configuração históricos.

### 1. Conferir a entrega R132 congelada

Os recibos finais confirmam fonte/APK acima, certificado `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`, assinatura v2/v3, alinhamento 16 KiB, sete substituições/zero adições e 13.853 entradas preservadas. DEX8 apenas `SwitchConfigPatcher`, 39 outros DEX byte idênticos incluindo DEX40, conjuntos de classes preservados. A revisão antecipa shaders no loading, adiciona duas fichas Sony e limita a migração do caminho vazio Switch; não autoriza mudar cores/controladores ou apagar workspaces.

O operador confirma os hashes do manifesto público contra os 16 arquivos privados recebidos. `RUNTIME_ORIGINAL` aponta ao `server-kit-original-receipts/runtime-final.json` privado; `PACKAGE_ORIGINAL` ao `package-final.json` privado; `ARTIFACTS` ao `server-kit/` real recebido. Os caminhos absolutos privados não são publicados. Não gerar novo APK nem novos IDs por essa operação administrativa.

### 2. Conferir o scanner e publicar os scripts efetivos

Registrar os valores atuais de `Type`, `ExecStart`, estado/PID e caminho do script da unidade do scanner. O código examinado usa `Type=oneshot`: `atualizar-biblioteca-station.py` importa `station_online_profiles.prepare` em cada execução; não tratar isso como um worker Python contínuo.

Resolver `CONFIG.outputDirectory` e `CONFIG.autoOnlineProfiles.{registry,engineManifest,preparedModes}`, além do caminho efetivo de `library-tools`, `module.__file__` e seus hashes. O operador controla apenas novos disparos do timer, aguarda a execução atual acabar sem matá-la, publica os scripts verificados, confirma importação em processo Python novo e restaura o timer. Credenciais/configuração privada não entram no retorno público.

Hashes do código administrativo em `a6b58e9`:

| Arquivo | SHA256 |
|---|---|
| `station_online_profiles.py` | `3d5d5b5563e2a6825ab9e798da80313cdbf2640522bc4dfd6b47e25c7f69eae1` |
| `cadastrar-motor-online-station.py` | `a3c81e0c379984d6b7736f79ce963c73a3f3250883f6304a32b5c6cfda73a096` |
| `build_incoming_manifest.py` | `362bcae9d8915f7f43aac4c48d06b35bdf57efc88d6acb9199aa06e3a0231426` |
| `extract_private_server_artifacts.py` | `27053b843d763adcf570e859b2c8658e216dbf6f80963b600fa5326958f70ef4` |
| `merge_scoped_modes.py` | `ddac598ca1671e6d682b626866a3b1984eb88c5ff7d677c7b4cd563a6a677783` |

Não reaplicar patches em arquivos já corrigidos. Registrar a publicação realmente executada, não apenas o commit remoto.

### 3. Fotografar os baselines e conferir os inputs gerados

Guardar snapshots privados byte exatos de catálogo, perfis, manifesto atual de engines e modos preparados; registrar SHA/revisão/contagens/horário. Registrar a configuração `autoOnlineProfiles` e flags C# efetivas, incluindo `Station:Online:MultiplayerProfileRegistryFile`. `EngineRegistryFile` legado não é a autoridade de cadastro v3.

O kit já contém o manifesto e o canonical receipt gerados pelos helpers pinados. Conferir seus hashes no inventário. As receitas abaixo documentam como foram obtidos e permitem reprodução controlada; não são necessárias para renomear ou reserializar arquivos já selados:

```sh
python3 "$TOOLS/build_incoming_manifest.py" --runtime-receipt "$RUNTIME_ORIGINAL" --package-receipt "$PACKAGE_ORIGINAL" --output "$PREPARATION/incoming-engine-manifest.json" --profile-receipt "$PREPARATION/profile-canonical-receipt.json"
python3 "$TOOLS/extract_private_server_artifacts.py" --apk "$APK_FINAL" --package-receipt "$PACKAGE_ORIGINAL" --runtime-receipt "$RUNTIME_ORIGINAL" --output "$KIT_PRIVADO_ATUAL"
```

A extração ocorre onde o APK completo está disponível; ao operador chega o kit de seis bibliotecas, originais e selos. Confirmar recebimento privado real e hashes, sem enviar APK ou binários ao Git.

### 4. Aprovar modos pela edição/conteúdo real

Gerar um ledger único com `itemId`, `contentSha256`, plataforma, core, perfil/controller canonical, modo, título/instruções, `maximumPlayers`, `allowedPlayerCounts`, decisão e fontes HTTPS. Migrar N64/GameCube/Wii apenas quando conteúdo/core/controller/canonical/capacidade forem idênticos. Perfis genéricos `gamecube-four-ports` ou `wii-four-remotes` não equivalem aos perfis `dolphin-*`.

PSX exige revisão explícita por edição/modo de compatibilidade HLE e duas portas padrão simultâneas: `biosPolicy=HLE-per-game-approved`, `reviewEvidence` HTTPS, máximo 2 e `allowedPlayerCounts=[2]`. Não herdar aprovação de um motor RetroArch anterior. CUE exige `cue-set-v1` com todas as trilhas referenciadas; hash de ZIP ou só do CUE não basta.

```sh
python3 "$TOOLS/merge_scoped_modes.py" --catalog "$CATALOG" --profiles "$PROFILES" --modes "$MODES" --runtime-receipt "$RUNTIME_ORIGINAL" --profiles-module "$PROFILES_MODULE" --decisions "$REVIEW_LEDGER" --output "$PREPARATION/prepared-modes-merged.json" --audit-json "$PREPARATION/scoped-mode-audit.json"
```

Manter o prefixo anterior exato, adicionar apenas modos dos quatro IDs finais e exigir `requireExplicitEngineModes=true`. Jogos sem revisão, futuros ou incompatíveis devem aparecer recusados com motivo preciso, não receber aprovação pelo teto da plataforma.

### 5. Aplicar uma candidata selada por administração nativa

```sh
pkexec python3 "$SERVER_OPERATOR" install --config "$CONFIG" --incoming "$PREPARATION/incoming-engine-manifest.json" --artifacts "$ARTIFACTS" --mode-additions "$PREPARATION/prepared-modes-merged.json" --output "$CANDIDATE"
```

`CANDIDATE` deve ser um diretório absoluto novo. O helper revalida baselines/selos/hashes sob `scan.lock`, publica modos/engines antes de perfis e mantém rollback byte exato. `--mode-additions` recebe os modos mesclados; o baseline ativo de modos continua sendo a referência de preparação. Se o catálogo/baseline mudou, preparar novamente contra o estado novo; não aceitar override permissivo. A autenticação deve ser a do operador real, sem simular `PKEXEC_UID` ou publicar senha.

Devolver receipt/candidate/apply e SHA de cada input/output. Caso rollback falhe, registrar a recuperação necessária sem declarar conclusão. Conservar registros, perfis, jogos/salas e modos anteriores.

### 6. Confirmar o hotreload e a resposta assinada v3

Observar o reload de `StationMultiplayerProfileMonitor` (intervalo dez segundos), flags efetivas, engineManifest/profiles/modes/catalog atuais, versão/DLL/PID/horário reais. Não reiniciar a API. Uma resposta histórica de produção não substitui essa observação.

Usar sessão autenticada existente: presence `enter` em `POST /v1/station/online/command` antes das consultas de multiplayer. Pedir `capabilities`/`snapshot` frescos em **`POST /v1/station/online/multiplayer/command`**, com `requestId` novo e item real. Validar assinatura e vínculo licença/device/session/request, `multiplayerVersion=3`, capability `station-multiplayer.v3` e o perfil completo: item/conteúdo/engine/core/runtime/controller/profile hash/modo/contagens. `serverReady` sozinho não significa `onlineAvailable` para um jogo aprovado.

O relay mantém `station-stream.v3`/TSR3, host-star, um link duplex por convidado, DATA máximo 16.384 bytes e janela de 262.144 por link/direção. Não cadastrar v3 no registro legado, exigir `snapshot.engines` v2, inventar GET snapshot ou usar HTTP200/PONG/cache como prova de ativação.

Devolver matriz por sistema/edição/modo com aprovados e recusados e motivos, mais verificações negativas de conteúdo/engine/perfil desconhecidos, quantidade inválida e import futuro. Publicar apenas evidência agregada sem tokens, envelopes pessoais ou sessões.

### 7. Separar cadastro de gameplay

Após confirmação dos quatro motores, os aparelhos devem usar o APK exato já compilado e uma sessão atualizada, testando **salas novas** aprovadas. Conferir roster, slots nativos únicos, geração, links host-star, start/COMMIT, recuperação e saída humana. Se faltar instalação R132, fazê-la separadamente sem interromper partida/download e preservando assinatura/dados.

Não afirmar estabilidade, gameplay, Bluetooth/USB, latência ou redução térmica por cadastro ou testes administrativos isolados. PS3/PS4 continuam offline; nenhum ISO/PKG real foi validado nesta revisão.

A conferência do Switch encontrou o caminho canônico e não encontrou o diretório SAMBOX legado naquele momento; o frontend havia retomado. Recriação contínua não foi reproduzida. A navegação/reabertura do usuário alterou a janela de medição: não foram validados tempo físico de shaders depois do loading, CPU em repouso, temperatura ou gameplay. Esses limites não autorizam alterar a fonte produtiva congelada `56ba83b7fcc5c243ae50052fec9b6f4141e1b5f1` para contornar o cadastro.

## Retorno final esperado, em uma resposta

1. Fonte/APK/IDs finais recebidos e seis hashes privados conferidos; selo do par original e recibo do kit.
2. Scanner/configuração/scripts efetivos com seus hashes, baselines atuais e autenticação nativa realizada.
3. Candidata/apply selados, preservação dos registros anteriores e reload observado sem restart.
4. Matriz assinada fresca de capacidades/modos aprovados ou recusados, com razões específicas e verificações negativas.
5. Pendências físicas explicitamente separadas; sem pedido genérico de outro handoff quando a pendência for autenticação, kit não recebido ou edição sem prova.

Fonte, compilação, identidade e kit privado desta entrega estão concluídos. Permanecem **recebimento efetivo pelo operador, publicação dos scripts/autenticação nativa, decisões específicas de modos, aplicação e prova assinada fresca**, sem ativação R132 confirmada. Instalação/gameplay/consumo físico são etapas separadas.
