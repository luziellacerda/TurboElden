# R141 — downloads diretos sobre a R140 preservada

**Fontes e receitas preparadas; nenhuma R141 foi compilada, assinada, instalada ou cadastrada nesta etapa.** A R140 foi instalada no moto g52; os demais telefones ainda não receberam a R140. O estado de cada instalação depende de seu recibo próprio. A futura R141 exige quatro novos IDs independentes e seu cadastro continua pendente.

## Base e mudança solicitada

A única base admitida é a R140 assinada, SHA256 `61e873e7bbd75a13fbd0d55515a3726f4debd8984cc0fe8f9d73401e0897792c`, 2.715.008.015 bytes, fonte `b93623b708bafe151441d3e4920acad51718e118`. `classes35.dex` deve continuar exatamente `49f381dc3ef375797d2db56b25a8a6c86a8150c2515ce115f4639b7bb243478e`: conserva `global_core_options=true` e `game_specific_options=false` e todos os reparos anteriores de sessão, capa e saída. Não há novo logger ou sidecar.

As duas fontes HTTP são cópias byte exatas do [commit revisado de downloads `4478e49`](https://github.com/luziellacerda/TurboElden/tree/4478e490041fe961ae7716c0aaed7bc71881066c/integration/station-direct-download-20261013). Seus hashes estão em [PROVENANCE.json](PROVENANCE.json). O APK de referência `e69616ee…` deriva da R139 e reverteria as duas chaves da R140; ele não é donor desta integração. Seu cadastro administrativo registra aqueles IDs anteriores, e não os futuros IDs da R141.

Somente o GET canônico `/v1/station/artifacts/{grant}` passa a usar `https://downloads-station.lzgames.com.br`, com pin SPKI próprio. Autorização, autenticação, catálogo, capas, mídia e comandos continuam na origem anterior. A validação da CA pública e do hostname, Bearer, prova da requisição, recusa de redirects, cancelamento, limites e controle de resposta são conservados. Não há IP fixo externo, fallback do mesmo grant, novo cache, novo timeout ou mudança de checksum de artefato.

## Preservação exigida

- Compilar apenas `StationHttp.java` e `StationDownloadOrigin.java`, Java8 com API34, usando dependências somente como classpath. JAR fechado com quatro classes; D8 release com mínimo API28.
- `ScopedHttpDex.java` aceita somente os seis tipos HTTP esperados e o novo helper. Copia `StationHttp$ResponseBody` do donor, substitui os outros cinco tipos da família e adiciona um tipo. DEX28 passa de 271 para 272 tipos; 266 tipos permanecem exatos na representação canônica com métodos, campos, inicializadores e debug.
- Todas as outras 39 partições DEX, incluindo DEX35 corrigida, ficam byte exatas. Manifest/SDK, recursos, frontend, vídeos, fila, cache, FPS, clocks, controles, opções HLE, catálogo e protocolo READY não entram na alteração.
- O runtime RetroArch permanece `ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378`. Todos os cores e seus nove descritores permanecem iguais. Os oito IDs RetroArch ativos conservam o cadastro atual.
- Os três wrappers independentes vinculam 345 payloads reais, incluindo DEX28 nova e DEX35 da R140. Renovam somente quatro IDs PS1/N64/GameCube/Wii. Suas políticas são iguais às dos fingerprints atuais da R140, e as sete fontes PSX originais são verificadas por hash. Exports, dependências, SONAME e alinhamento nativo são comparados.
- APK final: 13.860 entradas, cinco substituições (`classes28.dex`, `engines.json`, três wrappers), zero adições ou remoções e 13.855 entradas preservadas. ZIP clássico, `copy.copy(ZipInfo)`, leitura completa independente após montagem, assinatura original v2/v3 e alinhamento 16 KiB.

[PROPOSED-SCOPE.json](PROPOSED-SCOPE.json) contém o escopo fechado. [Licenças e origem das cópias](licenses/NOTICE.md) permanecem disponíveis. Nenhum APK, biblioteca, ROM, BIOS, chave, credencial, serial ou log bruto está nesta integração.

## Origem da qualificação e limites

A [qualificação clínica de seleção de opções R140](../../audits/station-r139-core-options-binding-20261013/evidence/host-resolver-qualification.json), SHA256 `42db9aa7537486f15b555987ac05d0d4850de7b34af9ffa5063a014438bfc821`, permanece aplicável ao código exato preservado de DEX35. Seu escopo é a seleção dos caminhos; ela não comprova qual arquivo antigo o telefone leu.

O produtor anterior publicou [43 verificações host e três cenários TLS reais](https://github.com/luziellacerda/TurboElden/blob/4478e490041fe961ae7716c0aaed7bc71881066c/integration/station-direct-download-20261013/qualification.json) e [validação do download protegido no servidor](https://github.com/luziellacerda/TurboElden/blob/4478e490041fe961ae7716c0aaed7bc71881066c/integration/station-direct-download-20261013/protected-download-validation.json). Esses recibos pertencem à candidata e ao serviço anteriores. Seus hashes constam na proveniência; não são execução Android, velocidade da Internet do consumidor ou testes físicos da R141.

Após a revisão, congelar toda fonte executável em um commit imutável. As receitas recusam commit ausente, fonte diferente, donor antigo, wrapper antigo, payload divergente ou saída existente. A origem revisada utilizou Java8/API36 e Linux; esta reconstrução usa os inputs Windows API34/JDK17/D8 já pinados do aplicativo. Não se exige que os bytes recompilados sejam iguais aos da candidata Linux: exige-se a mesma fonte revisada, somente a família permitida e preservação integral de tudo fora dela. A compilação e seus recibos ainda estão pendentes.

## Entradas privadas e ferramentas Windows

Raiz privada existente: `F:/TurboStations-Backup-Completo-20261011`. Saídas novas exclusivamente em `E:/StationDirectDownloadsR141-20261013/{dex,identity,assembly}`; G não tem espaço suficiente. Nada histórico deve ser removido.

| Entrada | Caminho relativo à raiz F | SHA256 exigido |
|---|---|---|
| Java | `ferramentas/jdk17/bin/java.exe` | `1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406` |
| Javac | `ferramentas/jdk17/bin/javac.exe` | `9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549` |
| API34 | `ferramentas/android-34/android.jar` | `6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad` |
| D8 | `ferramentas/android-build-tools-35/lib/d8.jar` | `305622ad00535684534eb8f742cbf5e628a9abc09d8ea4d39d1babb95bf0cee5` |
| APKtool | `ferramentas/apktool_3.0.3.jar` | `dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423` |
| Rooms, classpath | `desenvolvimento/reconstrucao-atual/rooms.jar` | `6b2929eb3621b208593a886b6f06a32de52af9c931663cb314e197af155f773d` |
| Client, classpath | `desenvolvimento/reconstrucao-atual/client.jar` | `011bce981b609d2cc5cfbad49c386e7f54dea1f560a17fe79bae3a56b3f8f313` |
| Apksigner | `ferramentas/android-build-tools-35/lib/apksigner.jar` | `00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7` |
| Zipalign | `ferramentas/android-build-tools-35/zipalign.exe` | `aa2475ce201962b871fb8daec020da03fd6292c9c1f422cd0fe2e39b20d4f673` |

NDK: `ferramentas/ndk-r28c`, revisão `28.2.13676358`. A rotina herdada `integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py` exige o conjunto Windows original completo de oito pins (incluindo `source.properties` e sete executáveis/wrappers); `clang.exe` SHA256 `7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`. Todas as dependências de fonte importadas constam e são congeladas por SHA em `PROVENANCE.json`; nenhuma receita histórica é editada.

## CLI após revisão e congelamento

Substituir somente o commit R141 completo abaixo pelo commit que realmente contém esta fonte revisada. Os caminhos são os inputs privados existentes. Executar as fases na ordem, em saídas novas; estes comandos não assinam nem instalam por si.

```powershell
$r141Recipe = "C:/Users/Admin/Documents/Codex/2026-10-11/temo/work/publication-app/integration/direct-downloads-preserved-r141-20261013/recipe"
$r141Source = "COMMIT_R141_COMPLETO_DE_40_HEXADECIMAIS"
$r141Private = "F:/TurboStations-Backup-Completo-20261011"
$r141Output = "E:/StationDirectDownloadsR141-20261013"
$r141Base = "$r141Private/desenvolvimento/TurboStations-Premium-R140-core-options-20261013.apk"

python -B "$r141Recipe/build_dex.py" `
  --base "$r141Base" --source-commit "$r141Source" `
  --jdk-bin "$r141Private/ferramentas/jdk17/bin" `
  --android-jar "$r141Private/ferramentas/android-34/android.jar" `
  --d8-jar "$r141Private/ferramentas/android-build-tools-35/lib/d8.jar" `
  --apktool "$r141Private/ferramentas/apktool_3.0.3.jar" `
  --rooms-jar "$r141Private/desenvolvimento/reconstrucao-atual/rooms.jar" `
  --client-jar "$r141Private/desenvolvimento/reconstrucao-atual/client.jar" `
  --out "$r141Output/dex"

python -B "$r141Recipe/build_identity.py" `
  --base "$r141Base" --source-commit "$r141Source" `
  --dex "$r141Output/dex/classes28.dex" --dex-receipt "$r141Output/dex/dex-compilation.json" `
  --ndk "$r141Private/ferramentas/ndk-r28c" --out "$r141Output/identity"

python -B "$r141Recipe/assemble_apk.py" `
  --base "$r141Base" --source-commit "$r141Source" `
  --dex "$r141Output/dex/classes28.dex" --dex-receipt "$r141Output/dex/dex-compilation.json" `
  --identity "$r141Output/identity" --out "$r141Output/assembly"
```

Recibos esperados: `dex/dex-compilation.json` (`station.r141.direct-downloads.dex.v1`), `identity/runtime-identity.json` (`identity.v1`) e `assembly/unsigned-package.json` (`package.v1`). APK unsigned: `assembly/TurboStations-Premium-R141-downloads-diretos-unsigned.apk`. O mapa completo privado de 13.860 hashes não deve ser publicado.

A assinatura será feita pelo fluxo privado que conserva a chave original. O resultado assinado em `assembly/signed.apk` deve ser verificado assim:

```powershell
python -B "$r141Recipe/verify_apk.py" `
  --apk "$r141Output/assembly/signed.apk" --receipt "$r141Output/assembly/unsigned-package.json" `
  --java "$r141Private/ferramentas/jdk17/bin/java.exe" `
  --apksigner "$r141Private/ferramentas/android-build-tools-35/lib/apksigner.jar" `
  --zipalign "$r141Private/ferramentas/android-build-tools-35/zipalign.exe" `
  --out "$r141Output/assembly/final-apk-proof.json"
```

Prova final: schema `station.r141.direct-downloads.final.v1`. O fluxo privado registra também `assembly/verified-final.json` e copia o resultado conferido para `F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R141-downloads-diretos-20261013.apk`, sem sobrescrever um APK existente. Só promover ponteiros após prova real de assinatura e pacote final; instalação requer telefone autorizado ocioso e preservação de dados.

## Repasse necessário ao servidor e aceite físico

Entregar privadamente os novos bytes exatos dos três wrappers, as dependências existentes, quatro descritores renovados e os recibos finais. Registrar os novos IDs pelo contrato vigente, preservando todos os IDs/perfis/modos anteriores. Nunca tratar o recibo do APK `e69616ee…` como registro da R141. Nenhum cadastro, deploy ou restart é executado pelas receitas acima.

Nos aparelhos, conferir download autorizado completo, integridade entregue pelo fluxo existente, cancelamento e nova autorização, recusas de grant expirado/reusado/sessão estrangeira e funcionamento das rotas anteriores. Velocidade deve ser medida em rede externa com grants distintos; não há ganho físico comprovado nesta preparação. As partidas Top Gear/Mario Kart continuam com a correção e com os critérios de homologação da R140 preservados.
