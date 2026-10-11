# Compilação e instalação do candidato atual

Estes utilitários ficam fora das receitas produtivas congeladas. Não alteram motores, identidades de runtime, interface, vídeos, cache, LEDs ou a economia dos menus. Nenhum comando seleciona APK pela data, pelo nome de uma pasta histórica ou por um arquivo “mais recente”.

## Conferir o instalador atual

Executar na raiz do repositório. O ponteiro local deve concordar com `CURRENT-LOCAL-ARTIFACTS.json` do backup único, `desenvolvimento/ATUAL.json` e a evidência final da integração correspondente. R128 usa `integration/ps3-ps4-offline`; R129 usa `integration/local-sony-demos`. Uma revisão desconhecida é recusada.

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
