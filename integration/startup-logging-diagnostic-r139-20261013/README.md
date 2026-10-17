# R139 — diagnóstico temporário de inicialização

Estado: fontes e receitas preparadas; este diretório não promove uma nova versão.
Nenhuma compilação, assinatura, instalação ou alteração dos ponteiros atuais faz
parte da preparação. O responsável pela entrega deve congelar estas fontes antes
de executar os comandos abaixo e restaurar a R139 original ao terminar a captura.

## Motivo e escopo

O motor release possui os registros necessários, mas `verbosity=false` suprime
inclusive `RARCH_ERR` e o callback libretro. `firmware_update_status` é executado
antes de a configuração particular da sala ser lida. Portanto, escrever somente
`log_verbosity` nessa configuração deixaria a primeira falha potencial silenciosa.

O novo auxiliar JNI abre apenas o caminho exato do RetroArch já carregado, por
`RTLD_NOLOAD`, e habilita o logger existente em nível 1. Não carrega outro motor.
`StationStartupLogging.begin(Context)` é inserido imediatamente após o
`System.loadLibrary("station_retroarch")` do ramo v3 em `onCreate`, antes de
configurar a sessão e chamar `NativeActivity.onCreate`. Uma falha do auxiliar é
registrada sem substituir o caminho original do jogo.

`StationRetroLaunch.prepare` acrescenta à configuração privada somente:

```text
log_verbosity = "true"
frontend_log_level = "3"
libretro_log_level = "3"
```

Depois da gravação atômica da configuração, `cfgWritten()` registra apenas esses
valores e `log_to_file=false`, que continua herdado. Assim, o nível inicial 1 cobre
o começo da carga; depois da configuração, o nível 3 conserva apenas os erros.
Nenhum registro novo contém senha, sala, ROM, endereço ou caminho particular.
Os registros internos originais do motor podem conter caminhos/conteúdo e devem
ser tratados como diagnóstico privado.

## Base obrigatória

| Item | Identidade |
| --- | --- |
| APK doador R139 | `19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164` |
| Tamanho doador | 2.714.991.631 bytes |
| Fonte release doadora | `42da152e54bbbb4a6d569ca26fe90835503bcccb` |
| DEX 35 doador | `dd6ea401376aafcba86518038fa2589c3d626c076cdcfc21252efca1a93ab6a9` |
| RetroArch preservado | `ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378` |
| Certificado original | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |

Usar o APK atual explícito, nunca uma R124/R135 inteira para reconstruir as
classes existentes. A fonte de Launch é herdada, mas sua projeção DEX atual inclui
recompilações antigas. Activity também inclui a alteração de saída R137 e todas
as suas demais rotinas são preservadas.

## Guardas da montagem

1. Java/D8 compilam somente `StationStartupLogging`: uma classe, sem dependências
   produtivas ou classes sintéticas novas.
2. As classes existentes recebem inserções smali em apenas `onCreate` e `prepare`.
   Remover os blocos inseridos precisa recuperar integralmente as duas projeções
   do doador. Todos os campos e outros métodos são recuperados byte por byte.
3. O DEX passa de 608 para 609 tipos; os outros 606 tipos são comparados com o
   doador real antes e depois de montar. Os 39 outros DEX da raiz e o DEX de
   processo PS4 permanecem exatos na comparação integral do pacote.
4. Os três marcadores independentes vinculam `classes35.dex`; seu fingerprint
   precisa ser renovado. A política, fontes dos owners, cores, controles e opções
   são conservados. O mapa comum possui 345 entradas herdadas e o novo sidecar:
   346 entradas, com DEX 35 sendo o único hash herdado alterado.
5. `engines.json` renova somente `engineId`/`runtimeSha256` dos quatro descritores
   PSX/N64/GameCube/Wii. Todos os nove descritores RetroArch, inclusive os oito
   ativos v3 e o Geolith inativo, são integralmente iguais à R139.
6. Pacote: cinco substituições e uma adição; zero remoções; 13.855 entradas antigas
   exatas. Nenhuma alteração em RetroArch, cores, Manifest, resources, telas,
   configuração global, HLE, dispositivos, número de jogadores, READY/ACK,
   transporte, FPS, timers, loop, cache, economia, BIOS ou catálogo NES.
7. A verificação final exige todas as 13.861 entradas, fingerprints coerentes,
   certificado original, v2/v3, alinhamento APK de 16 KiB e ELF AArch64 de 16 KiB.

Os quatro IDs independentes temporários não substituem os IDs R139 cadastrados
no servidor. O diagnóstico solicitado é SNES/RetroArch, cujos IDs seguem exatos;
portanto ele dispensa um novo cadastro. Outros owners não ficam homologados neste
APK temporário. Restaurar a R139 original restaura os quatro IDs já registrados.

## Sequência de execução do responsável

Argumentos são caminhos absolutos explícitos; `COMMIT` deve ser o commit completo
que contém todas as fontes deste diretório. Saídas devem ser diretórios novos fora
do repositório. As receitas históricas não são alteradas nem executadas com seus
doadores antigos.

```text
recipe/build_dex.py
  --base APK_R139 --jdk-bin JDK_BIN --android-jar ANDROID_API34
  --d8-jar D8_JAR --apktool APKTOOL_303 --source-commit COMMIT --out DEX_OUT

native/build_sidecar.py
  --ndk NDK_R28C --runtime RETROARCH_AE72
  --source-commit COMMIT --output SIDECAR_OUT

recipe/build_identity.py
  --base APK_R139 --dex DEX_OUT/classes35.dex
  --dex-receipt DEX_OUT/dex-compilation.json
  --sidecar SIDECAR_OUT/libstation_startup_logging.so
  --sidecar-receipt SIDECAR_OUT/sidecar-build-receipt.json
  --ndk NDK_R28C --source-commit COMMIT --out IDENTITY_OUT

recipe/assemble_apk.py
  --base APK_R139 --dex DEX_OUT/classes35.dex
  --dex-receipt DEX_OUT/dex-compilation.json --identity IDENTITY_OUT
  --sidecar SIDECAR_OUT/libstation_startup_logging.so
  --sidecar-receipt SIDECAR_OUT/sidecar-build-receipt.json
  --source-commit COMMIT --out ASSEMBLY_OUT

recipe/verify_apk.py
  --apk SIGNED_DIAGNOSTIC_APK --receipt ASSEMBLY_OUT/unsigned-package.json
  --apksigner APKSIGNER --zipalign ZIPALIGN --out FINAL_PROOF_JSON
```

`build_dex.py --check-inputs-only` confere as entradas sem compilar. A assinatura e
o alinhamento são feitos pelo fluxo privado do responsável, com a chave original.
O APK sugerido é `TurboStations-R139-DIAG-startup-20261013.apk`, separado do release
e dos três ponteiros CURRENT/ATUAL/BAT. Não atualizar o kit do servidor com estes
marcadores temporários.

## Captura e restauração

Instalar somente no aparelho autorizado e ocioso, preservando dados/UID/assinatura.
Capturar `logcat` antes de iniciar a sessão, incluindo o processo auxiliar online
e os registros `RetroArch`/`StationStartupDiagnostics`; não depender de run-as,
root ou tombstones antigos. Conferir `stage=early-logger enabled=true` e a mensagem
`stage=cfg-written`, depois registrar a primeira falha nativa e seu contexto.

Handoff solicitado: `logcat-topgear3000-vs.txt`,
`logcat-topgear3000-campeonato.txt` e `erro-inicializacao-retroarch.txt`, dos dois
telefones, do início à falha. Registrar modo, participantes e relógios sem publicar
senhas, tokens, seriais ou dados privados. VS usa 2/3/4; Campeonato em dupla usa 2.
Entrega privada prevista em `I:\SERVIDOR LER`; verificar novamente o volume antes
de copiar. Os registros e o APK temporário ficam fora do Git.

Ao terminar, encerrar o processo de diagnóstico e reinstalar a R139 SHA `19ac…`
preservando dados. Conferir o hash integral instalado e a abertura oficial. Esta
compilação aumenta temporariamente o trabalho de registros e não serve como
medição de desempenho. A preparação não comprova captura Android, causa do erro,
partida iniciada ou saída física.
