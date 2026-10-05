# Neo Geo CD — dados publicados e ponte compilada — 05/10/2026

## Atualização documental: base posterior R19B

O roteiro abaixo registra o delta preparado sobre R18. Depois dele, **R19B foi instalada e conferida para N64**: [estado e evidências](../station-n64-controls-r19b-20261005/README.md), [distinção entre reprodução R19B e próxima integração](../station-n64-controls-r19b-20261005/RECONSTRUCAO-E-FLUXOS.md). Para uma nova entrega CD, revisar a base e as guardas da receita para preservar R19B ou sucessora comprovada. Não reconstruir uma atualização sobre R18 descartando as correções N64. Nenhum código/receita CD foi alterado por esta nota; o delta abaixo não foi incorporado ao APK R19B.

## Registro original da preparação sobre R18

Servidor **catálogo14 / 2.212 jogos**, incluindo 50 Neo Geo CD, com 50 revistas exatas e 50 sinopses. Pasta original `neogeo/neogeocd` mantida. Os 50 arquivos `.img` são CHD v5: entrega assinada usa **`.chd`, formato `raw`, bytes idênticos**, sem recompressão ou limitação de MB/s. Scanner/produção fonte [`9cff9b3`](https://github.com/luziellacerda/Servidor-pix/tree/9cff9b333b5e0fcaec6d8a12f75b61519d8c7018). Índice SHA `07ad4c3fda41a19c23745436c4c45c97a70b2c7688eff788612fe22743823a92`.

**Esta pasta é um delta Java/DEX preparado, ainda não incorporado a um APK assinado/instalado.** A última instalação comprovada continua **R18**, SHA `a29151da312830d826f6ea71ebb61cb8a39fe1c21786f719e26a61568b29b1c4`. Preservar N64 completo, R17 navegação/60fps, R16 offline/download, salas R12, fontes do renderer, motores, certificado, licença, dados e saves. A R16 já incorporou MB/s e os ajustes de download/offline; não reaplicar o delta antigo R11 nem reintroduzir SHA do corpo dos jogos. Hash de build e de identidade do netplay continuam preservados.

## Abertura e BIOS

O usuário não possui BIOS CD. O catálogo e download estão disponíveis; a BIOS não foi inventada, baixada nem embutida. No próximo APK:

- Neo Geo CD é reconhecido pelo segmento de plataforma `neo-geo-cd`/`neogeocd`, nunca por uma palavra no nome de outro jogo.
- O CHD é montado no driver **neocdz**: URI de `neocdz.zip`, extra `cli_params` com `-rompath '<pai real>' -cdrom '<caminho absoluto>' -bios official|unibios33|unibios32`.
- **MAME4droid interpreta aspas simples** nesse extra. O parser nativo real foi conferido com nomes/espaços/parênteses. Não usar aspas duplas para agrupar o caminho. Nomes com apóstrofo/barra invertida/controles recebem mensagem; os 50 nomes publicados são compatíveis.
- Sem BIOS, aparece **IMPORTAR BIOS** / **VOLTAR**. O seletor Android aceita ZIP ou firmware `.bin/.rom`, confere conteúdo/tamanho/CRC/SHA1 e guarda apenas componentes identificados em armazenamento privado. A seleção é conferida em uma thread, com indicador de progresso; não exige ADB nem criação manual de pasta.
- Firmware CD e zoom `000-lo.lo` são necessários. O zoom pode ser reutilizado da BIOS Neo Geo já instalada; a BIOS Neo Geo inteira não substitui o firmware CD. A importação parcial preserva os componentes válidos e explica qual ainda falta.
- O driver é preparado atomicamente ao lado do CHD de cada instalação. São preservados CHD, recibo assinado, arquivos anteriores e saves. Importações posteriores não exigem programação por jogo.
- Neo Geo comum mantém a rota R18; `cli_params` mantém o rompath R18 e troca opções CD anteriores. O bootstrap usa `PREF_ROMsDIR_2=""` para manter o modo filesystem; não gravar o caminho físico nessa preferência, pois isso ativaria SAF sem URI. `MameBootstrap.java` é byte idêntico à R18.

O servidor também reconhecerá automaticamente BIOS válida em `neogeo/neogeocd/bios` e poderá entregar ZIP externo com CHD +`neocdz.zip` fechado. Isso muda a revisão do item, mantendo seu ID. O formato/launchPath do grant assinado determinam a instalação.

## Verificação local

- Java/DEX Android36/min-api26 compilado: DEX SHA `4cd9394219e7da86be9ab249d24a2c40862592f9e4595968769b8ce79fbfd6d9`.
- 25 verificações Java reais: identificação exata, BIOS ausente/incorreta, importação, limite de entrada, CHD truncado/parent, dependência zoom, ZIP de driver, idempotência e preservação.
- Parser CLI nativo: seis argumentos corretos com nome contendo espaços; [recibo](evidence/integration.json).
- Overlay de fonte: dry-run2 →apply2 →dry-run0; três fontes na compilação, dois arquivos alterados, bootstrap R18 igual.
- [Compilação](evidence/build.json), [teste host](evidence/host-tests.json). Os dados sintéticos do teste não entram no DEX.

Não há APK privado R18, certificado nem aparelho neste Linux. O empacotador foi revisado sintaticamente; **não foi executado com a base real**. Testes locais não comprovam gameplay, áudio, controles ou retorno Android.

## Receita sobre R18

1. Copie as fontes R18 de `E:\ESTUDO APK\work\station-neogeo-access-20261005\java` para uma **nova candidata**, por exemplo `E:\ESTUDO APK\work\station-neogeocd-after-r18-20261005\java`. Preserve a revisão R18 congelada. Execute `recipes/apply_overlay.py --target-java <nova-candidata/java/org/emulationstation/frontend> --dry-run`; depois aplique com `--backup <pasta nova>`. Ele confere as duas fontes R18 antes de escrever. Não alterar a fonte nativa N64/renderer.
2. `python recipes/build_java.py --android-jar <android.jar> --d8 <d8> --output <pasta nova>`: compila as três classes, gera`classes.dex` e recibo. Usar JDK17; caminho D8 Windows`.bat` aceito. O hash pode variar com SDK/D8; conferir fonte e conteúdo, além do hash.
3. `python recipes/package_delta.py --base-apk <APK R18 a29151da> --dex <novo classes.dex> --output <novo UNSIGNED.apk>`: guarda SHA da base/classes30/salas; muda somente `classes30.dex`, retira assinaturas ZIP antigas e confere SHA/compressão das demais entradas.
4. Alinhar APK/SOs a 16 KiB com o fluxo canônico; assinar com certificado original SHA `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`. Conferir assinatura/alinhamento e todas as entradas depois. O unsigned não é atualização instalável aprovada.
5. Instalar por atualização, sem desinstalar/limpar dados. Conferir hash do`base.apk`, catálogo 14 ou maior,50 CD, capa/sinopse/download`.chd`, mensagem/importaçãoBIOS, doisCD sucessivos→NeoGeo→N64, controles/áudio/retorno à coleção e saves. Preservar os quatro workers de capas e a transferência sem pacing.

## Fontes primárias

[Intent/cli_params MAME4droid](https://github.com/seleuco/MAME4droid-Current/blob/main/android-MAME4droid/app/src/main/java/com/seleuco/mame4droid/Emulator.java), [parser nativo](https://github.com/seleuco/MAME4droid-Current/blob/main/src/osd/myosd/droid/myosd_droid.cpp), [driver/identidadesCDZ](https://github.com/mamedev/mame/blob/master/src/mame/snk/neogeocd.cpp). Esses links explicam a interface; não substituem o donor binário existente no APK.
