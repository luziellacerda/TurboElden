# Compilação e instalação do candidato atual

Estes utilitários ficam fora das receitas produtivas congeladas. Não alteram motores, identidades de runtime, interface, vídeos, cache, LEDs ou a economia dos menus. Nenhum comando seleciona APK pela data, pelo nome de uma pasta histórica ou por um arquivo “mais recente”.

## Conferir o instalador atual

Executar na raiz do repositório. O ponteiro local deve concordar com `CURRENT-LOCAL-ARTIFACTS.json` do backup único, `desenvolvimento/ATUAL.json` e a evidência final da integração correspondente. R128 usa `integration/ps3-ps4-offline`; R129/R130 usam `integration/local-sony-demos`. R131 usa `integration/sony-internal`, com a evidência final fora das fontes produtivas em `versions/station-sony-internal-r131-20261011/evidence/package-final.json`. Uma revisão desconhecida é recusada.

R131 exige `assemblyPath` explícito `G:/StationNormalOwnersR127/sony-internal/correction/assembly`, donor R130 exato no `desenvolvimento` do backup único, `source-freeze.json` na raiz dessa assembly e `identity/runtime-identity.json`. Os três ponteiros devem concordar também nos hashes do freeze e da identidade. A receita R131 confere as fontes, as cinco compilações/preparações privadas, os 305 payloads, os módulos Sony e os quatro IDs existentes renovados. Os APKs R126/R127 não são escolhidos como base da R131.

R132 preserva seus guards específicos: donor R131 corrigido, assembly `G:/StationNormalOwnersR127/startup-cleanup-r132/assembly`, sete substituições/zero adições e somente DEX8/SwitchConfigPatcher dentro de sua allowlist. A evidência final está em `versions/station-startup-cleanup-r132-20261011/evidence/package-final.json`; as fontes congeladas e os recibos privados continuam necessários.

R133 usa `integration/console-panel-r133`, donor R132 exato SHA `47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20`, assembly exclusiva `G:/StationNormalOwnersR127/console-panel-r133/assembly` e evidência `versions/station-console-mode-completion-r133-20261011/evidence/package-final.json`. Exige cinco substituições/zero adições, os 40 DEX e a biblioteca frontend preservados, escopo único `console-hardware-panel-psp-ps3-ps4` e vínculos integrais de freeze, compilação nativa, payloads e quatro IDs finais. As fotografias de PSP/PS3/PS4 usam o painel existente; esta revisão não habilita online Sony. Sem os três ponteiros concordantes e recibos finais, R133 é recusada.

```powershell
$stationRepo = (Resolve-Path .).Path
$stationCurrent = Join-Path (Split-Path $stationRepo -Parent) 'CURRENT-LOCAL-ARTIFACTS.json'
$stationTools = 'F:/TurboStations-Backup-Completo-20261011/ferramentas'
$stationPython = Join-Path $stationTools 'python314/python.exe'
$stationReceipt = Join-Path (Split-Path $stationRepo -Parent) 'current-release-check.json'
& $stationPython -B tooling/release/compile_current.py --current $stationCurrent --repo $stationRepo --phase verify --receipt $stationReceipt
```

`plan` somente resolve metadados. `preflight`/`verify` conferem o SHA integral do APK, assinatura real v2/v3, alinhamento16KiB, pacote/entrada Login exportada MAIN/LAUNCHER e vínculos das fontes, payloads e runtimes. Reutilizar uma verificação só é permitido para os mesmos bytes e vínculos exatos. Isso não recompila nem cria outro APK assinado.

## Recompilar

R128 admite `--phase rebuild-payloads --allow-build` e depois `--phase assemble --allow-build`. Usa o backup único e a árvore G: existente. Etapas concluídas com os hashes corretos são reutilizadas; uma saída incompleta ou diferente é recusada, sem sobrescrever o instalador atual. Temporários Python/Java ficam no G: e os processos iniciados têm prazo limitado.

R129 **não** usa a reconstrução R128 por fallback. Sua sequência própria é:

1. `integration/local-sony-demos/recipe/build_demo_payloads.py`, com donor R128 e entradas privadas explícitas/hash conferidos.
2. `integration/local-sony-demos/recipe/build_unsigned.py build`, com os recibos parent/demo e diretório único `G:/StationNormalOwnersR127/local-sony-demos/assembly`.
3. `build_unsigned.py check-unsigned`, com a base R126 exata e essa mesma assembly.
4. `tooling/release/finalize_verified.py`, com a receita dessa integração, `source-freeze.json` e `identity/runtime-identity.json`.

Consultar `--help` dessas receitas para seus argumentos explícitos. Não apontar a R129 à assembly, freeze ou identidade da R128.

R131 também recusa reconstrução/assembly pelo caminho R128 deste utilitário. A sequência própria em `integration/sony-internal/recipe` usa preparação privada de assets, host novo, Manifest fechado, identidade sobre o R130 e assembly/verify final específicos. `plan`/`preflight`/`verify` e a instalação somente verificam essas saídas; não compilam firmware/owners nem invocam emuladores externos. Temporários de verificação R131 ficam em `G:/StationNormalOwnersR127/sony-internal/correction/assembly/release-temp`, escolhidos pelo contexto R131.

R132/R133 também usam suas receitas próprias, sem fallback para R128. Para R133, `build_native.py` reproduz primeiro o carousel R132 byte exato e aplica o overlay de imagens; `build_runtime_identity.py` renova os quatro marcadores mantendo cores/opções/perfis; `assemble_apk.py` fecha cinco substituições; `verify_final.py` confere todas as entradas. O `finalize_verified.py` recusa promoção R133 fora desse escopo. `compile_current.py` permite somente `plan`/`preflight`/`verify` para essas revisões. A instalação recebe o candidato apenas depois da promoção verificada e atualização explícita dos três ponteiros. Temporários R133 ficam na própria assembly em `release-temp`.

## Assinar e promover

`finalize_verified.py` recebe candidato/base/freeze/identidade/receita/assembly/destino explicitamente. Antes de assinar, confere SHA/tamanho do `unsigned.apk` e seu `.package.json`, além dos vínculos freeze/runtime. A chave deve corresponder ao certificado original. A senha vem de uma variável de ambiente definida fora do repositório; não existe senha embutida no código, nos comandos de exemplo ou nos recibos públicos.

O APK é alinhado e assinado no diretório de montagem. A receita verifica assinatura, alinhamento, todos os payloads e entradas preservadas. Somente esses bytes verificados são copiados para um arquivo de estágio e promovidos por renomeação. Um instalador existente com outra identidade não é sobrescrito. Depois da evidência final completa, o responsável atualiza os três ponteiros concordantes; o finalizador não altera CURRENT automaticamente.

## Instalar em um telefone autorizado

Informar o serial USB e o modelo exatos já conferidos, sem gravá-los em código público. Exemplo com variáveis locais preenchidas pelo responsável:

```powershell
$stationInstallReceipt = Join-Path (Split-Path $stationRepo -Parent) 'current-installation.json'
& $stationPython -B tooling/release/install_current.py --current $stationCurrent --repo $stationRepo --serial $phoneUsbSerial --expected-model $phoneModel --receipt $stationInstallReceipt --allow-update --launch
```

Sem `--allow-update`, um APK diferente não é instalado. Se os bytes atuais já estiverem no telefone, a instalação é reutilizada. Uma base instalada que não conste no histórico explícito requer `--expected-installed-sha256` com o hash previamente inspecionado. O script nunca escolhe outro aparelho automaticamente nem instala os emuladores externos por consequência.

Antes de atualizar, confere usuário0, modelo, hash integral instalado, UID, data de primeira instalação e diretório de dados; revalida os painéis ativos e a ausência de serviços/downloads. Jogo, painel desconhecido ou serviço ativo exigem saída manual. Atualização direta por streaming preserva a assinatura e os dados; sem desinstalação, limpeza, alteração de configurações ou cópia extra do APK no telefone.

## Conferir a abertura real

A abertura usa exclusivamente Login oficial e observa a Activity realmente retomada por até30s. O recibo distingue frontend observado, autenticação pendente, emulador inesperado e resultado não observado. Instalação/hash corretos não significam login, ativação no servidor ou gameplay validado.

A primeira abertura física R128 mostrou a biblioteca Mupen restaurada de uma tarefa antiga com `LAUNCHED_FROM_HISTORY` (`0x00100000`); uma nova chamada da entrada oficial alcançou ESActivity. Por isso, uma Gallery própria pode ser reconhecida como menu histórico inativo somente se for uma única folha da tarefa, usuário0, invisível e marcada HISTORY. Após a abertura, há no máximo uma nova chamada de Login para essa mesma tarefa histórica previamente reconhecida, novamente sem jogo/serviço ativo. Não há remoção de tarefa, encerramento forçado, bypass de autenticação ou relançamento automático de partidas.

APK, chave, senha, serial, sessões, jogos, BIOS e logs pessoais permanecem locais. Somente fontes e recibos agregados sem esses dados podem ser publicados.
