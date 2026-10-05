# TurboStations R18 — acesso Neo Geo e navegação de pastas

Registro técnico de 05/10/2026. O R18 reúne a correção de acesso aos arquivos do MAME/Neo Geo e a navegação de subpastas únicas do R17, sobre a base R16 exata.

## Estado

**Compilado, assinado e instalado por atualização**, sem desinstalar ou limpar dados. SHA do base.apk conferido igual ao APK gerado. A primeira tentativa ficou pendente pela USB; depois de trocar a porta, a atualização foi concluída. O recibo de empacotamento conserva o estado anterior `installed: false`; a prova posterior é `evidence/installation.json`. Gameplay e navegação têm seu estado nos recibos específicos, quando presentes. Não foi promovido a estável.

| Campo | Valor |
| --- | --- |
| APK | `TurboStations-NeoGeo-Pastas-R18-20261005.apk` |
| Pasta | `E:\ESTUDO APK\work\station-neogeo-access-20261005` |
| Bytes | `2036266872` |
| SHA-256 | `a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4` |
| Base R16 | `b52313bc6ef504b91239241b2a4bc8c9eb9f1eeeea937e61cbc4bd5628ef0eb1` |
| Conteúdo alterado | `classes30.dex` e `lib/arm64-v8a/libturbo_carousel.so` |
| Conteúdo preservado | 13.079 entradas, conferidas individualmente |
| Certificado SHA-256 | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| Alinhamento | 16 KiB; conferido após assinatura |

## Causa identificada

A ponte R15 gravava o caminho físico `.../content` em `PREF_ROMsDIR_2` e removia `PREF_SAF_URI`. No MAME4droid Current 1.41.2, um `ROMsDIR` não vazio ativa a flag nativa `USING_SAF=62`, mesmo quando a URI está ausente. Assim, o caminho correto era enviado ao mecanismo SAF, que não tinha uma árvore autorizada para abrir.

O encadeamento foi confirmado no donor local:

1. `MameBootstrap.java` R15, linhas 85/87: diretório físico em `PREF_ROMsDIR_2`, URI removida.
2. `Emulator$4.smali`, linhas 334–378: diretório não vazio provoca `setValue(62,1)` e `setValueStr(1, diretório)` (`SAF_PATH`).
3. `MAME4droid.smali`, linhas 804–813: `SAFHelper.setURI` só é chamado quando a preferência URI existe.
4. `Emulator.smali`, linhas 2995–3076: callback encaminha a abertura ao `SAFHelper.openUriFd`, sem tentativa de arquivo normal nessa camada.
5. `SAFHelper.smali`, linhas 692–705 e 4835–4843: URI ausente produz `SAF URI is not set.` e retorno de falha.

No código nativo oficial, a flag SAF ligada e o prefixo correspondente selecionam esse caminho; falha devolve `ENOENT`, sem fallback para `::open`. Com a flag desligada, o caminho normal usa `::open`. Isso explica por que arquivos no caminho físico correto podiam aparecer como `NOT FOUND`. [Fonte oficial posixfile.cpp](https://raw.githubusercontent.com/seleuco/MAME4droid-Current/main/src/osd/myosd/file/posixfile.cpp)

### Alcance da evidência do aparelho

Os logs de falha examinados são históricos, das **14:08**, e mostram `Configured ROM directory` apontando para o `content` de `svcplus.zip`, seguido de `myosd_safOpenFile`, URI SAF ausente e chips/BIOS `NOT FOUND`. A captura das **14:47** mostrou a tela de plataformas; não é uma nova execução do jogo nem validação da correção. A coleta atual preserva logs históricos do buffer.

`evidence\archive-directory.json` registra somente metadados do diretório central dos arquivos locais: `svcplus.zip` com 43.048.343 bytes e 17 entradas; `neogeo.zip` com 1.416.625 bytes e 25 entradas. Constam os programas `svc-p1p.bin`, `svc-p2p.bin`, `svc-p3p.bin`, gráficos/áudio e, na BIOS, `sm1.sm1`, `sfix.sfix` e ROMs de BIOS. Essa presença sustenta que a mensagem genérica `NOT FOUND` não demonstra, sozinha, que os arquivos estavam ausentes.

A leitura foi `metadataOnly: true`, sem alteração de runtime. CRC listado no diretório central é metadado, não CRC recalculado. Não houve teste novo de descompressão, integridade completa dos bytes, compatibilidade integral do set ou gameplay. `svcplus` é clone de `svc`; sets split podem exigir arquivos compartilhados, e dependências ainda podem aparecer depois que o acesso funcionar. [Definição MAME 0.289](https://raw.githubusercontent.com/mamedev/mame/mame0289/src/mame/snk/neogeo.cpp), [documentação de ROM sets](https://docs.mamedev.org/usingmame/aboutromsets.html)

## Correção aplicada à ponte

Os dois fontes alterados são [MameBootstrap.java](java/org/emulationstation/frontend/MameBootstrap.java) e [MameEntryActivity.java](java/org/emulationstation/frontend/MameEntryActivity.java).

- O seed grava `PREF_ROMsDIR_2=""`, mantém `PREF_SAF_URI` ausente e preserva a pasta de instalação/saves válida.
- `""` é diferente de `null`: `initMame4droid` testa somente `null` para abrir a configuração inicial. O próprio upstream usa string vazia e URI nula no fluxo Android TV. O worker pula a ativação de SAF quando o comprimento é zero.
- O lançamento permanece `ACTION_VIEW` com URI de arquivo e MIME. O caminho de busca dos ZIPs e da BIOS passa explicitamente no extra `cli_params`, no formato `-rompath 'diretório pai absoluto'`.
- O helper exige arquivo e diretório acessíveis. Não copia ROM, não acrescenta hash ou espera. As rotas de configurações e as preferências de saves existentes permanecem.
- Caminhos com apóstrofo, caracteres de controle ou ponto e vírgula são recusados com erro explícito. Não há escape comprovado no parser do donor; ponto e vírgula representa lista de caminhos para o MAME.

**As aspas precisam ser simples.** A desmontagem de `libMAME4droid.so`, função `myosd_droid_main`, confirmou delimitador `0x27` em `0x0a072604` e separador espaço `0x20` em `0x0a072644`. O trecho `0x0a072668–0x0a0727a8` remove os apóstrofos externos e copia o token sem escape. Aspas duplas não agrupam um caminho com espaços nesse parser. Os tokens são diagnosticados pelo formato `cli param %s`.

O donor recebe `CLI_PARAMS=5` antes de `runT()`: `Emulator$4.smali` chama `init` na linha 248, envia CLI na 800, aplica valores na 951 e executa na 964. `updateEmuValues` não sobrescreve esse argumento. O diretório extraído do `ACTION_VIEW` aparece no log `XX path`, mas esse log sozinho não comprova o `rompath` efetivo.

Não foi alterado `classes29.dex`, o worker do donor ou o motor nativo MAME. A correção usa a inicialização nova do processo MAME no fluxo atual. Uma hipótese separada sobre reutilização de motor já ativo não foi tratada neste delta; o fluxo de retorno atual encerra `:mame`. A ponte é compartilhada pelas plataformas que usam MAME, embora a falha investigada tenha sido Neo Geo.

## Navegação R17 incorporada

O R18 incorpora exatamente a biblioteca de navegação do commit **`8f2dbaa0d6a4dba663d670caa5112a9d9c9d39a4`**, snapshot `versions/station-single-folder-r17-20261005`.

O header `native_folders.h` abre diretamente plataformas sem subcoleções e segue cadeias de pastas com uma única subpasta e nenhum jogo direto. Quando existem jogos diretos ou várias opções, mantém a escolha. Voltar usa as telas realmente exibidas e restaura seleção por caminho/tipo. O conjunto passou por 3.030 verificações C++; o teste também rejeitou a implementação anterior.

Biblioteca incorporada: `E:\ESTUDO APK\work\station-single-folder-r17-20261005\libturbo_carousel.so`, SHA-256 **`4d2b962e09c7924e7b9b14042ee4b43e08d704bedae021131668303ae42fb39d`**. O comando NDK r28c completo está em `tests.json` daquela pasta.

## Escopo e preservação

A correção Neo Geo ocupa apenas `classes30.dex`. A segunda alteração do APK é o carousel R17. O empacotamento verificou todas as outras 13.079 entradas de conteúdo contra a base R16, sem adicionar/remover entradas de conteúdo ou aceitar duplicatas.

O cliente Station `classes28.dex`, a JNI Station, o donor MAME `classes29.dex`, o motor MAME, a integração N64 e os demais motores foram preservados. `classes35.dex` de salas conserva SHA-256 `8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae`. Desempenho/nohash/acesso offline do R16 permanecem; o SHA de identidade do netplay permanece. A preservação de conteúdo não equivale a novo teste de gameplay de cada motor.

## Fontes, build e reprodução

```text
C = C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work
W = E:\ESTUDO APK\work\station-neogeo-access-20261005
R17 = E:\ESTUDO APK\work\station-single-folder-r17-20261005
```

| Item | Local / prova |
| --- | --- |
| Fontes revisadas e congeladas | `C\work\neogeo-access-20261005\java` |
| Cópia usada no build | `W\java` |
| Receita dos testes | `C\work\neogeo-access-20261005\run_mame_filemode_tests.py` |
| Resultados / fixtures / classes host | `W\tests\result.json`, `result.log`, `filemode-rcss23gw` |
| Receita de javac e D8 | `C\build_neogeo_access_20261005.py` |
| Classes e DEX | `W\classes`, `W\dex\classes.dex` |
| Recibo da ponte | `W\bridge-build.json` |
| Empacotamento | `C\package_neogeo_r18_20261005.py` |
| Prova final | `W\build-result.json` |
| Logs de compilação | `W\compile.log`, `W\dex.log` |
| Logs de assinatura/alinhamento | `W\signature.log`, `W\alignment.log`, `W\unsigned-alignment.log` |
| Metadados dos ZIPs | `W\evidence\archive-directory.json` |
| Captura diagnóstica anterior ao R18 | `W\device-evidence\mame-144722.log`, `screen-144722.png` |

Base arquivada: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Desempenho-Offline-R16-20261005.apk`. A receita exige o SHA R16 indicado acima, o DEX novo e o carousel R17 exato. Ela preserva compressão, alinha bibliotecas armazenadas a 16 KiB, assina pelo fluxo local autorizado e compara o conteúdo final. Chave privada e credenciais não fazem parte deste handoff.

Build Java: JDK `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin`, `javac` UTF-8/source8/target8, API `G:\Android\Sdk\platforms\android-34\android.jar`; D8 de `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15\lib\d8.jar`, `min-api 26`. Os avisos registrados foram bootstrap class path de Java 8 e API obsoleta, sem erro. DEX final SHA-256: **`0d76beace3c7c427c670dc4cc59d60200d14b11f96b907fe79c8abc3e25d973f`**.

| Fonte congelada | SHA-256 |
| --- | --- |
| `MameBootstrap.java` | `947467469202c3f149df6115164a88fb4faed47774979410ff4ea1efad7b4d6f` |
| `MameEntryActivity.java` | `4ce5d99c446ded3611a9140b35f3897dc742765a7366b9b513870d87a227c8ee` |

Para reprodução, preparar outra cópia isolada e adaptar os destinos dos scripts. As receitas recusam sobrescrever classes/DEX/APK já existentes; não reexecutá-las sobre a revisão congelada nem empacotar bibliotecas por wildcard. Todos os produtos de teste/build desta correção foram gerados em E:. Nenhum servidor foi alterado ou implantado por esta entrega.

## Testes concluídos e limites

- **166 verificações com métodos reais**: extrai os métodos da ponte nova e o seed original R15. Demonstra que R15 combina SAF ativo e URI ausente, enquanto o novo modo vazio dispensa seleção inicial e não ativa SAF. Exercita pai do jogo, seis famílias MAME, espaços/Unicode, aspas simples, rejeição de caracteres incompatíveis, arquivo ausente, configurações, saves e falha de commit.
- **15 contratos estáticos**: chave efetiva do donor, testes de null/comprimento, extra CLI, ordem de inicialização, `ACTION_VIEW`, entrada inválida e preservação da rota de configurações.
- **Compilação Android das duas classes**: API 34 / Java 8 passou; D8 passou.
- **3.030 verificações C++ R17**: navegação e retorno, com rejeição da versão anterior; compilação Android passou.
- **APK**: assinatura, certificado, alinhamento e comparação integral das entradas passaram.

O teste de tokenização host reproduz o trecho nativo auditado; não executa o binário ARM64. Os testes de seed usam substitutos Android para preferências/contexto e métodos reais extraídos. Não são execução do jogo, medição de FPS nem prova de que todo ROM set é compatível.

## Referências oficiais e donor

Donor local: `E:\ESTUDO APK\work\native-carousel\implementation\mame-current\donor-decoded`, MAME4droid Current 1.41.2 / MAME 0.289. APK donor SHA-256 `b2e05497f4c7b8b0d5ac84a4755569050f60a4c9c69c7e219f6783bd9c5bb2ad`.

As referências abaixo foram conferidas pelo auditor de protocolo. URLs `main` podem mudar; os pontos decisivos também foram conferidos no smali/ELF do donor local exato.

- [Emulator.java](https://raw.githubusercontent.com/seleuco/MAME4droid-Current/main/android-MAME4droid/app/src/main/java/com/seleuco/mame4droid/Emulator.java): seleção de SAF e argumentos do lançamento.
- [MAME4droid.java](https://raw.githubusercontent.com/seleuco/MAME4droid-Current/main/android-MAME4droid/app/src/main/java/com/seleuco/mame4droid/MAME4droid.java): inicialização sem SAF com string vazia.
- [PrefsHelper.java](https://github.com/seleuco/MAME4droid-Current/blob/main/android-MAME4droid/app/src/main/java/com/seleuco/mame4droid/helpers/PrefsHelper.java) e [SAFHelper.java](https://github.com/seleuco/MAME4droid-Current/blob/main/android-MAME4droid/app/src/main/java/com/seleuco/mame4droid/helpers/SAFHelper.java): preferências independentes e falha sem URI.
- [myosd_droid.cpp](https://raw.githubusercontent.com/seleuco/MAME4droid-Current/main/src/osd/myosd/droid/myosd_droid.cpp): flag inicial, setter e tokenização dos argumentos.

## Conferência pendente no dispositivo

Após atualização preservando dados, conferir o SHA instalado e uma inicialização nova de MAME. Os logs devem mostrar `mode=filesystem`, `cli param -rompath` e o pai correto como um único token; a falha SAF por URI ausente não deve reaparecer nessa rota. Conferir Neo Geo, BIOS, retorno à coleção, segundo lançamento e troca de jogo. Se o motor então apontar arquivos específicos ausentes/incompatíveis, investigar o set com esse novo diagnóstico.

Conferir também a navegação R17: plataforma sem subcoleções abre os jogos; pasta única segue adiante; ramificações/jogos diretos mantêm escolha; Voltar restaura plataforma/menu e seleção. Essas provas e qualquer recibo de instalação posterior devem ser acrescentados pelo coordenador. **R18 foi instalado; estabilidade geral ainda não foi aprovada.**

## Validação Android posterior à instalação

SVC Plus foi aberto às 15:00 no processo MAME 18269. Os logs mostram `mode=filesystem`, `cli param -rompath` e o diretório real como um único argumento. Nenhum `SAF URI is not set`, `NOT FOUND` ou erro fatal aparece no recorte dessa execução. A captura local `evidence/screen-150111.png` mostrou a seleção de personagens com imagem e controles próprios do MAME. O mantenedor confirmou: “Os controles funcionam; saí do jogo”. A USB desconectou depois da captura: o retorno não recebeu nova captura ADB, e a navegação R17 no aparelho permanece pendente. Esta prova cobre SVC Plus; não comprova todos os jogos ou desempenho sustentado. Recibos públicos: `evidence/neo-geo-device.json` e `neo-geo-runtime.log`.
