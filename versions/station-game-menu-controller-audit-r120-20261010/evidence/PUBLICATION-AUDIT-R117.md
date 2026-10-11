# R117 — auditoria de publicação, somente leitura

## Escopo da conferência

Foi consultada a lista de candidatos não ignorados do próprio snapshot `versions/station-effects-server-r117-20261010/`, sem stage, commit, push, exclusão ou alteração das fontes/receita/manifestos congelados. A lista muda quando o responsável acrescenta recibos de build/instalação; os números abaixo descrevem a janela da análise, não um manifesto de publicação fechado.

A lista tinha cerca de 640 arquivos: fontes Java e nativas, textos/JSONs, testes, receitas, configurações de controle e licenças abertas. Não havia candidatos `.apk`, `.dex`, `.so`, `.o`, `.class`, vídeos, imagens, keystore, BIOS, ROM ou saves. Os objetos e arrays de pixels privados restaurados localmente são ignorados. Os headers públicos com extern/offsets de assets contêm vínculos/índices; não são os arrays de pixels.

Uma varredura dos JSONs não encontrou campos de serial, bearer, accessToken, sessionToken, password, privateKey ou licença de usuário com valor. Campos chamados `license` encontrados em `engines.json` e `autoconfig/SOURCE.json` identificam licenças abertas dos projetos; eles não são credenciais nem licenças pessoais e devem continuar com as fontes correspondentes. Essa varredura não é prova criptográfica de ausência de todo segredo: o responsável deve conferir o diff final que será enviado.

## Conjunto que deve ficar local

O `.gitignore` do snapshot já exclui:

- Objetos/stubs e arte privada de `native/d1` até `native/d8`, e os arrays privados nomeados em `native/d0`.
- APKs, `.so`, `.o`, logs, capturas/imagens, `__pycache__`, compilados e fixtures geradas.
- `evidence/physical`, `evidence/test-fixture-rerun` e `evidence/led-isolated`.
- Receitas `recipes/measure_motorola_*.py`, que foram feitas para um aparelho específico.
- `integrate_graphics.py`, usado somente durante a conciliação das fontes.

O recurso privado precisa continuar disponível para a reconstrução local por hash. Ignorá-lo no Git não autoriza apagar o único backup privado nem substituí-lo por outro asset. A R117 é uma receita de atualização do APK R116 exato, não uma alegação de criação do APK integral sem seus inputs privados.

## Cópias redundantes e históricas

### Duplicatas exatas de classes Java

- `java-alias/PerMessageDeflateExtension.java` é idêntica à classe completa em `java/dependency-src/org/emulationstation/frontend/relay/ws/extensions/permessage_deflate/PerMessageDeflateExtension.java`.
- `java-alias/WebsocketNotConnectedException.java` é idêntica à classe completa em `java/dependency-src/org/emulationstation/frontend/relay/ws/exceptions/WebsocketNotConnectedException.java`.

A receita R117 lê as 230 fontes na árvore `java/` e cria aliases curtos apenas no diretório temporário da compilação. Não precisa publicar estas duas cópias adicionais. Porém, receitas históricas `test_r110_integration.py`, `test_online_light_field.py` e `test_online_vertex_classifier.py` ainda mencionam `java-alias`. Portanto, excluir as cópias deve vir acompanhado de excluir essas receitas históricas do conjunto atual ou identificá-las claramente como testes da época; não declarar que elas são a reprodução vigente da R117.

### Arquivos históricos sem função no build R117

Os seguintes candidatos podem ficar fora do pacote Git da R117, mantendo o histórico que já existe no repositório:

- `frontend/baseline/station_catalog_abi.r112.hpp`.
- `frontend/baseline/station_frontend.r112.cpp`.
- `evidence/frontend/compiled-warmstart.json`.
- `evidence/frontend/r112-to-r113-native.diff`.
- `evidence/r112-base/README.md`.
- `evidence/r112-base/bytecode-hooks.txt`.
- `evidence/r112-base/frontend-r102/base-sources.json`.
- `evidence/r112-base/frontend-r102/compiled-profile-bridge.json`.
- `evidence/r112-base/package.json`.
- `evidence/r112-base/structural-checks.json`.
- `JAVA-SOURCE-MANIFEST-R115.json`, que não é utilizado pelo `build.py` R117.

Nenhum deles foi apagado nesta análise. Os documentos `README-R116-HERDADO.md`, `STATUS-R116-HERDADO.json`, `ALTERACOES-R116-HERDADAS.md`, `AUDIT-R106-GPU.md` e recibos `*-inherited*` podem servir como referência histórica, mas não são evidência de instalação ou validação física da R117. Eles não substituem `README.md`, `STATUS.json` ou os recibos nomeados R117.

`evidence/REVIEW-LIFECYCLE-GL.md` também é herdado. A frase de manter o ImageView até completar o campo descreve o gate da R116. Na R117, o código e os probes confirmam publicação depois do primeiro pacote válido. Para a publicação atual, identificar esse documento como histórico ou atualizar essa afirmação sem fabricar uma nova prova física. As evidências atuais são `LED-PROGRESSIVO-R117.md`, `led-progressive-checks.json` e `graphics-state-rows-r117.json`.

## Fontes grandes conferidas

O candidato público maior era `native/d0/station_game_infos.h`, cerca de 2,24 MB. Ele contém metadados/sinopses textuais identificados como herdados, com aviso de que os fatos históricos não foram todos verificados individualmente. Não contém ROM/BIOS nem pixels. A existência desse texto não prova que o catálogo autenticado atual tenha sinopse de cada item; a tela da sala continua usando a descrição do catálogo por itemId, conforme contrato.

Configs `.cfg` de controle/overlay e arquivos de licença `COPYING`, `LICENSE`, `LICENSES` e `.txt` são fontes públicas, não arquivos gerados binários. Devem ser classificados dessa forma, sem excluí-los apenas por não serem `.java`/`.cpp`.

## Pendências do responsável pela publicação

1. Definir explicitamente o conjunto R117, evitando incluir as outras versões locais que também aparecem como não rastreadas na raiz do repositório.
2. Aplicar as exclusões de duplicatas/históricos conforme o conjunto escolhido, sem alterar os inputs de compilação já congelados nem eliminar seu backup privado.
3. Acrescentar os recibos de compilação/pacote/instalação R117 e atualizar `STATUS.json`; nenhuma instalação, temperatura ou gameplay foi conferida por esta auditoria.
4. Conferir no diff final que nenhuma captura, segredo, ROM/BIOS, licença pessoal ou mídia privada escapou das exclusões.

Esta subtarefa não executou nenhuma etapa de publicação e não mudou a configuração do servidor.
