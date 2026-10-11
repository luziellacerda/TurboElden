# R133 — consoles PSP, PS3 e PS4 ao lado da sinopse

Extensão isolada da R132 executável `56ba83b7fcc5c243ae50052fec9b6f4141e1b5f1`, APK `47a619a194c095e70738a4d191fb8491ee410d868e4c11742530ffcaaf844f20`. A preparação das artes e o gerador de overlay estão concluídos. Este documento não declara compilação, instalação, aprovação visual, gameplay ou ganho térmico.

## Causa verificada

O painel nativo só reserva a coluna de console quando `stationConsoleAvailable(infoConsoleKey)` retorna verdadeiro. A tabela original contém 19 famílias e os aliases correspondentes; nenhuma entrada cobre PSP, PS3 ou PS4. A R132 adicionou as duas fichas de sistema Sony, mantendo esse consumidor. Ficha e console são recursos separados nesse código.

`native_formation.h` chama `drawSystemInfoLayer`; `native_info.h` obtém o identificador do jogo, calcula `stationInfoLayout` e chama `drawStationConsole`. Esse método encontra uma arte estática pela chave, cria uma textura uma vez por família/contexto, calcula os limites alfa e usa uma única quad no contexto SDL/GL existente. A extensão mantém esses corpos, o ajuste da imagem, as regras de visibilidade, a restauração de estado GL e o loading da R132.

## Mudança limitada

- Acrescenta três fotografias reais com transparência nativa, compiladas no formato atual de 512 × 512 RGBA.
- Acrescenta sete aliases: `PSP`, `Psp - BR`, `pspbr`, `Playstation 3`, `ps3`, `Playstation 4`, `ps4`.
- Mantém as 19 declarações RGBA, suas linhas da tabela e todos os aliases existentes por inversão de bytes.
- O C++ muda somente a inclusão do console; o consumidor muda somente as duas inclusões de atlas e aliases. Não muda shader, layout, métodos GL, política de cache, animador, timer ou decoder.
- Preserva os 40 DEX, frontend, manifesto, resources, emuladores, controles, vídeos, LEDs, economia, fundos, cache, limite de 30 fps e transporte online.

A compilação do carrossel altera um compartilhado das identidades. As receitas de composição renovam somente os quatro IDs já existentes de PSX, N64, GameCube e Wii e `engines.json`; não habilitam online Sony. A montagem admite cinco substituições e zero adições. Arte do console não altera o emulador ou demonstra suporte a jogos reais.

## Fotografias oficiais e inputs privados

As buscas no tema local e nos assets do backup não localizaram fotografias prontas de hardware para essas três famílias. Cartões de texto e o sprite PSP de 30 × 17 não foram usados. As fotos estão nas páginas oficiais de história da [PSP](https://www.playstation.com/en-us/playstation-history/2000-ps2-psp/), [PS3](https://www.playstation.com/en-us/playstation-history/2007-ps3-ps-vita/) e [PS4](https://www.playstation.com/en-us/playstation-history/2013-ps4-ps-vr/).

| Família | Fotografia oficial | Dimensões originais | Bytes | SHA-256 original |
|---|---|---:|---:|---|
| PSP | `ps2-PSPlarge-image-block-01-en-18nov24`, preset `$1600px--t$` | 1600 × 812 | 1516198 | `ecd1c3c878af94d35b88e37c08f28b866258cc0a2f07b36f03eecf85c24020a6` |
| PS3 | `ps3-ConsoleSlim-image-block-01-en-09oct24`, preset `$1600px--t$` | 1600 × 1739 | 2353287 | `66f117f627f806dcc203064a503f15e87415495ff76838c4815b9a6e00e10609` |
| PS4 | `ps4-console-image-block-01-en-09oct24`, preset `$1600px--t$` | 1600 × 607 | 648785 | `16ff2a69f7a1395c064c335afc9d252eefd5438e26d61a0d9d2234f0b721454b` |

Os URLs completos estão nos pins de `recipe/prepare_art_inputs.py`. O PS3 mostrado é o Slim da foto oficial. A foto frontal do modelo original possui fundo branco opaco; a variante Slim já fornece transparência e dispensa remoção ou recriação do fundo.

O compilador de input faz somente conversão de formato, redução proporcional por Lanczos e preenchimento transparente. Não redesenha hardware/logos nem recorta o console. Fotos, pixels, atlas, previews e recibos com caminhos locais ficam na árvore privada R133 em G:, fora do Git. O aplicativo não solicita essas artes pela rede.

| Input 512 × 512 | Bytes RGBA | SHA-256 RGBA |
|---|---:|---|
| `psp.rgba` | 1048576 | `f66ae0cb084fb47fc9c59a024f9e6919c60a862ba29cb5edebfe01bdc694ad47` |
| `ps3.rgba` | 1048576 | `336b86e2009a7e2506e71c863863f6f5f44d24868485dc662d23d4950ad789d9` |
| `ps4.rgba` | 1048576 | `986d4086a5ce411ac764cb141cec9bda2ac0ab9652a2a5a96dace5db954b1c72` |

## Guardas e reprodução

`patch_console_panel.py` exige o CPP R132 gerado `ffe60b497f7493d1c0d666c80ad499a6c94d271ee9009cd5e6a94c461313199b`, os dois headers originais R124 e o atlas privado `d252beffcdf89c7641d93c7aaaa104a5849560ef49cb9c81e3156505756cfc1a` de 54719245 bytes. Exige os três pixels acima e um recibo de preparação coerente com o gerador e as fontes oficiais. Recusa diretório de saída existente.

```text
python -B integration/console-panel-r133/recipe/prepare_art_inputs.py
  --psp <foto-oficial-PSP> --ps3 <foto-oficial-PS3-Slim>
  --ps4 <foto-oficial-PS4> --out <diretorio-privado-novo/prepared>

python -B integration/console-panel-r133/recipe/patch_console_panel.py
  --native-cpp <R132/native/overlay/native/native_carousel.cpp>
  --native-console <R124/native/d0/native_console.h>
  --console-keys <R124/native/d0/station_console_keys.h>
  --console-assets <input-privado-d2/console_assets.h>
  --art-receipt <prepared/art-receipt.json> --out <overlay-privado-novo>
```

Também manter `PYTHONDONTWRITEBYTECODE=1` no ambiente. O output contém `native_carousel.cpp`, `r133_native_console.h`, `r133_station_console_keys.h`, `r133_console_assets.h` e `overlay-receipt.json`. Para compilar o novo CPP, manter os include paths R132/R124 e priorizar os headers R133; nenhuma fonte congelada R132 é editada. A composição posterior deve reproduzir primeiro o carrossel R132 e conferir o APK real, fontes, identidade, certificado e cada entrada.

## Custo e limites

Os três buffers acrescentam exatamente 3145728 bytes de pixels, 3 MiB. Cada família nova visitada solicita 1048576 bytes de RGBA ao `TexImage2D` existente; visitar as três pode acrescentar 3 MiB desses pixels no mesmo contexto. Esse número não mede overhead do driver ou memória residente real. O cache passa de 19 para 22 posições, com o mesmo limite de uma textura por família e invalidação por contexto.

Permanecem a varredura alfa e o upload na primeira visita. Não há novos shaders, FBOs, decoders, threads ou timers. O ganho ou custo térmico e a ausência de atraso precisam de medição física; não são demonstrados pela preparação de inputs ou pelas inversões do código.
