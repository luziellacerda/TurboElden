# Publicar o handoff R77 no clone servidor existente

`publish_server_handoff.py` foi preparado, sem execução ou push na preparação. A receita exige `--app-commit` com o hash completo já publicado no ramo `feat/station-multiplayer-r77-20261008`. Se esse ramo mudar, usar `--app-branch` com o ramo exato cujo HEAD remoto corresponde ao commit.

## Prévia somente leitura

```powershell
python -X utf8 -B publish_server_handoff.py --app-commit HASH_COMPLETO_PUBLICADO
```

A prévia lê os bytes do commit, confere a publicação do app, retorno remoto do servidor, manifesto C#, perfis sem aprovação e recibos. Não usa arquivos modificados do checkout, não cria commit/branch nem grava arquivos. Precisa de acesso Git de leitura.

## Publicação autorizada

Depois de conferir a prévia, executar a mesma chamada com `--publish`. Grava temporários em um filho novo de `E:\ESTUDO APK\work\station-multiplayer-r77-20261008`, ou no filho novo explicitado por `--work`.

```powershell
python -X utf8 -B publish_server_handoff.py --app-commit HASH_COMPLETO_PUBLICADO --publish
```

A publicação:

1. Atualiza todos os ramos remotos com refspec explícito. Exige que `docs/station-r76-server-review-20261008` ainda aponte para `bee3dcd5c2c0c0a228805957fe89b9a6023e8402`; retorno posterior exige leitura e revisão da receita antes de publicar.
2. Exige ausência local/remota do novo ramo `docs/station-r77-multiplayer-candidate-20261008`.
3. Copia exclusivamente textos versionados para `docs/station-android/entrega-app-r77-20261008/` e o documento `ENTREGA-APP-R77-MULTIPLAYER-20261008.md`. Inclui candidata C#, contrato, fontes/testes/evidências, catálogo/perfis propostos e metadados, com manifesto SHA-256 por arquivo. Exige também `SOURCE-MANIFEST.json`, `PACKAGE-INPUTS.json` e os dois assets exatos `station-online/engines.json` e `station-catalog/player-evidence-v1.json`; nenhum outro asset é copiado. O bundle PEM permitido contém apenas os certificados públicos de atestação Android existentes.
4. Usa índice alternativo e `commit-tree` com pai exato, confere cada byte/path e faz push comum, sem force. Não muda checkout nem índice normal. Verifica HEAD, índice e estado antes/depois.
5. Produz `prepared-commit.json` e `server-publication.json` no diretório da tentativa em E:. O recibo final contém commit/link exatos, `linuxDeployed=false` e `apkUploaded=false`.

Não altera arquivos `src/` do servidor, AGENTS da raiz, aparelhos, APK, serviços ou cadastro efetivo. A autorização de perfis continua `approved:false`.

Se o push falhar após criar o ramo local, a receita para e mantém `prepared-commit.json` e o ramo para inspeção. Não apagar nem executar novamente às cegas: primeiro verificar o estado remoto/recibo e resolver o envio do commit já preparado. A receita deliberadamente não sobrescreve uma entrega existente.

As receitas Java cruzadas copiadas são evidências; para reproduzi-las, usar o snapshot completo do app no commit referenciado e as dependências fixadas. A candidata C# possui sua receita independente em `server/build_candidate.py`.
