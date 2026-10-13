# R140 candidata — vínculo das opções privadas do core

Estado: fontes e receitas preparadas, ainda sem congelamento ou compilação.
O resolvedor real passou vinte casos no host; o responsável ainda deve revisar e
congelar as fontes antes de executar o build. Esta pasta não modifica a R139,
os ponteiros atuais ou o diagnóstico temporário instalado.

## Alteração proposta

O aplicativo já grava o arquivo privado `core-options.cfg` com as opções canônicas
do perfil aprovado e passa seu caminho em `core_options_path`. A proposta faz o
resolvedor usar esse arquivo, sem selecionar overrides de jogo/pasta/core:

```java
StringBuilder config = new StringBuilder();
set(config, "global_core_options", "true");
set(config, "game_specific_options", "false");
```

Esses dois flags pertencem apenas à configuração privada da sala. “Global” é o
nome da preferência interna do RetroArch: com o caminho explícito já existente,
ela seleciona o arquivo particular daquela sala, sem importar opções offline.
Os valores canônicos, inclusive HLE, continuam iguais; não acrescentar firmware
nem alterar core, controles, FPS, READY/ACK, capacidade ou protocolo.

A fonte pinada do motor possui defaults `global_core_options=false` e
`game_specific_options=true`. A falha observada no g52 foi solicitação de DSP4
seguida de falha de carga, apesar do arquivo HLE pretendido. A validação do
resolvedor demonstrou a seleção do caminho privado sob as condições controladas
abaixo. Não declarar correção física antes dos testes Android com o APK final e
o cadastro necessário.

## Qualificação e limites

[Recibo dos vinte casos](../../audits/station-r139-core-options-binding-20261013/evidence/host-resolver-qualification.json),
SHA `42db9aa7537486f15b555987ac05d0d4850de7b34af9ffa5063a014438bfc821`.
O resolvedor, seu wrapper e a chamada `SET_VARIABLES` foram extraídos byte exatos
de `runloop.c` SHA `13179287191fe00a76c6d35ddc75374388543b2c05607b14dc8c6efef135a012`,
correspondente ao runtime `ae72…`.

Os dois flags juntos selecionaram diretamente o arquivo canônico da sala em
cinco estados: ausência de overrides, override por core, por jogo, por pasta e
todos presentes. Somente `global_core_options=true` ainda permite a prioridade
de jogo/pasta LLE; somente `game_specific_options=false` ainda permite a
prioridade por core LLE. O arquivo, os parâmetros e os demais flags permaneceram
exatos nos vinte casos.

A existência de arquivos foi real no host, mas os helpers de descoberta e o
gerenciador de opções foram controlados/stubados. A qualificação não executou
bsnes, seu parser completo, Android ou gameplay e não leu o arquivo legado real
dos telefones. Ela demonstra a precedência permitida e a seleção corrigida, sem
atribuir uma leitura específica ao aparelho. Esses limites são mantidos no gate
de build e nos recibos derivados.

## Base e escopo fechado

Usar exclusivamente o APK original R139:

- APK `19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164`.
- Fonte release `42da152e54bbbb4a6d569ca26fe90835503bcccb`.
- DEX 35 `dd6ea401376aafcba86518038fa2589c3d626c076cdcfc21252efca1a93ab6a9`.
- RetroArch `ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378`.

Não usar o APK de diagnóstico como doador. Não incorporar Activity, helper Java,
sidecar JNI ou registros do diagnóstico. Apenas `StationRetroLaunch.prepare`
recebe duas chamadas `set()`, imediatamente após criar o StringBuilder. Os
registradores v3/v4 estão mortos nesse ponto e são escritos antes de serem lidos
pelo fluxo original; nenhuma quantidade de registradores ou desvio é alterada.

O inverso precisa recuperar a classe inteira original byte por byte. O DEX
permanece com 608 tipos, dos quais 607 são exatos; nenhum tipo é acrescentado ou
removido. Todos os outros métodos/campos de Launch, os demais DEX, Activity R137,
recursos, configurações globais e bibliotecas de jogo ficam iguais à R139.

Pacote proposto: cinco substituições (`classes35.dex`, `engines.json` e os três
marcadores vinculados ao DEX), zero adições/remoções, 13.855 entradas antigas
preservadas. Os marcadores conservam suas políticas e o mapa de 345 entradas;
somente o hash de DEX 35 muda nesse mapa. Renovar apenas os quatro IDs
PSX/N64/GameCube/Wii e exigir seu recibo real do servidor. Todos os nove
descritores RetroArch, oito IDs ativos, runtime `ae72…`, cores e perfis HLE
continuam exatos. A edição do flag não cadastra ou homologa partidas.

## Caminho de build proposto após validação e revisão

As receitas derivam da montagem qualificada do diagnóstico e retiram todos os
seus componentes de logging. Conservam os reparos de ferramentas:
separador exato no inverso, `copy.copy(ZipInfo)` e ZIP clássico Android abaixo
de 4 GiB (`ZIP64_LIMIT=2**32-1`, `allowZip64=False`, `force_zip64=False`).

```text
recipe/build_dex.py
  --base APK_R139 --jdk-bin JDK_BIN --apktool APKTOOL_303
  --source-commit COMMIT_R140 --resolver-receipt CLINICAL_RECEIPT --out DEX_OUT

recipe/build_identity.py
  --base APK_R139 --dex DEX_OUT/classes35.dex
  --dex-receipt DEX_OUT/dex-compilation.json
  --ndk NDK_R28C --source-commit COMMIT_R140 --out IDENTITY_OUT

recipe/assemble_apk.py
  --base APK_R139 --dex DEX_OUT/classes35.dex
  --dex-receipt DEX_OUT/dex-compilation.json --identity IDENTITY_OUT
  --source-commit COMMIT_R140 --out ASSEMBLY_OUT

recipe/verify_apk.py
  --apk SIGNED_R140_APK --receipt ASSEMBLY_OUT/unsigned-package.json
  --apksigner APKSIGNER_JAR --java JAVA_EXE --zipalign ZIPALIGN --out FINAL_PROOF
```

Os comandos acima estão implementados. `build_dex.py --check-inputs-only` faz a
conferência de entradas sem compilar; ambos os modos exigem o commit congelado e
o recibo clínico exato incluído naquele commit. Java 17 compila somente ferramentas
de leitura/montagem; nenhuma classe produtiva existente é recompilada por Java/D8.
O pacote não adiciona bibliotecas nem classes e será escrito como
`TurboStations-Premium-R140-core-options-unsigned.apk`. A assinatura usa o fluxo
privado do responsável, com a chave original, seguido de verificação integral.

Não compilar, congelar, assinar, instalar ou publicar novos IDs nesta preparação.
Logs brutos, APKs, bibliotecas, ROMs, BIOS e identificadores de telefones ficam
fora desta pasta e do Git.
