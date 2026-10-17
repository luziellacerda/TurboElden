# Ferramentas locais de diagnóstico SNES

Esta pasta contém somente fontes C e receitas de compilação, sem executáveis, ROM, firmware, saves, comandos USB, identificadores de aparelhos ou runners de captura. Todas as dependências e saídas são fornecidas por parâmetros; não há caminhos de drives pessoais fixados nas receitas públicas.

Os dois nomes de ferramenta identificam escopos diferentes:

| Nome | Escopo |
| --- | --- |
| `native-core-probe` | `retro_init` e `retro_load_game`; zero chamadas de `retro_run`. |
| `native-core-frame-probe` | Carregamento seguido de exatamente 120 chamadas de `retro_run`, input zero, contadores de vídeo/áudio e serialização somente em memória. |

O namespace das variáveis do core continua `bsnes_*`. O argumento `LLE`/`HLE` seleciona `bsnes_chip_hle`; o argumento opcional `disabled`/`enabled` controla `bsnes_violate_accuracy` e tem padrão `disabled`. Mercury só consome a escolha HLE quando `bsnes_violate_accuracy=enabled`. As outras variáveis conservam o primeiro valor padrão declarado pelo próprio core.

## Compilação

Usar Python e o NDK r28c `28.2.13676358` para Windows, com o diretório do `libretro.h` da fonte Mercury fixada. Informar os caminhos locais:

```text
python -B build_probes.py --ndk CAMINHO_NDK --libretro-header-dir DIRETORIO_HEADER --output DIRETORIO_BUILD --kind all
```

A receita confere os hashes das duas fontes, compila ARM64 Android 26 PIE com `-Wall -Wextra -Werror`, verifica os segmentos LOAD de pelo menos 16 KiB e grava um recibo sanitizado no diretório de build fornecido. `--kind load` ou `--kind frames` compila somente a ferramenta selecionada. Não transfere nada a aparelhos.

`prepare_frame_probe.py --source FONTE_LOAD --output FONTE_FRAMES` reproduz a derivação da fonte de frames a partir da probe de carregamento pinada. Os padrões apontam para as duas fontes desta pasta; a receita recusa alterações inesperadas em uma saída existente e verifica que a fonte original continua intacta.

## Execução por operador autorizado

```text
native-core-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR LLE disabled
native-core-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR HLE disabled
native-core-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR HLE enabled
native-core-frame-probe CORE_PATH ROM_PATH EMPTY_SYSTEM_DIR HLE enabled
```

As duas ferramentas leem os bytes completos da ROM real, mas oferecem ao core um caminho sintético `/probe-content.sfc` dentro do diretório isolado. `GET_SYSTEM_DIRECTORY` e `GET_SAVE_DIRECTORY` usam esse mesmo diretório existente e vazio. Isso isola a pesquisa de firmware da pasta original da ROM sem copiar ou modificar a ROM. Cores que exigem `need_fullpath=true` são recusados. O conteúdo sintético tem extensão SFC, impedindo a rota Mercury de saves por manifesto BML. O estado serializado da ferramenta de frames é descartado na memória; nenhum save ou estado é gravado por esta ferramenta.

Os logs imprimem somente contagens e nomes conhecidos de firmware. Caminhos completos e mensagens integrais do core são suprimidos. A ferramenta de frames também imprime checksum FNV-1a64 não criptográfico do estado; ele identifica os bytes produzidos naquela execução e não comprova determinismo, compatibilidade ou sincronismo entre aparelhos.

Aplicar limite externo de tempo ao executar a ferramenta de frames: o número de chamadas é fixo, mas uma chamada bloqueada dentro do core exige controle do operador. Código 0 da probe de frames exige carregamento, vídeo com dados, áudio, serialização e zero erros do core. Falha de carregamento retorna 1, preparação/símbolo retorna 2 e indicadores de execução ausentes retornam 3.

As [evidências físicas](../../../audits/station-r138-snes-dsp-startup-20261012/README.md) qualificam somente carregamento e startup limitado, realizados fora da Activity e sem rede. Não demonstram READY, partida, controles humanos, reconexão, saída da Activity ou homologação do produto.
