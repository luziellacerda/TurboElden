# R130 — repetição do vídeo principal

Em **Configurações → Efeitos gráficos → Vídeos do carrossel**, as escolhas
**Com loop** e **Sem loop** ficam lado a lado. A escolha vale somente para o
vídeo da plataforma em destaque no carrossel principal. As coleções continuam
tocando uma vez; as células sem destaque continuam usando imagens estáticas.

**Com loop** é o padrão solicitado para o principal. **Sem loop** conserva o
último quadro válido e encerra o decoder ao terminar. Essa segunda opção reduz
o trabalho contínuo de vídeo depois da primeira passagem. O interruptor de
vídeos e o modo de economia continuam tendo prioridade; desligá-los preserva
a escolha de loop. Não há percentual de economia ou medida térmica nova.

## Reprodução

A receita `recipe/patch_video_loop.py` transforma três fontes efetivas,
identificadas por hash da R124 usada pelo donor R128. Ela não restaura Activities
antigas e não substitui todo o cliente:

| Fonte efetiva | Alteração delimitada |
| --- | --- |
| `StationGraphicsPreferences` | Booleano persistente `platform_video_loop`, padrão verdadeiro, separado dos seis flags e do estado gráfico existente |
| `StationGraphicsPanel` | Duas escolhas estáticas ao lado do controle de vídeos, com seleção, foco e estado desativado |
| `StationSinglePassVideo720` | Sobrecarga de `start` e retomada do mesmo player pelo trabalhador existente |

O carrossel passa `systemsMode && !folderMode` na nova sobrecarga JNI. A antiga
assinatura continua disponível e delega com loop não autorizado. A política de
um vídeo em destaque e o descarte anterior ao início permanecem intactos.

O player mantém `setLooping(false)`. Ao atingir o ponto de parada antecipada
existente, **Com loop** usa `pause → seek(0) → start` no mesmo `MediaPlayer`,
`SurfaceTexture`, `Surface` e decoder. Ele não reabre o asset nem executa outra
preparação a cada passagem. A imagem já exibida permanece durante o seek. Um
seek que excede o prazo original termina no caminho de imagem retida; não
provoca uma sequência de reinicializações. A duração do seek depende do aparelho;
continuidade visual perfeita ainda exige conferência física.

A preferência é carregada pelo singleton gráfico existente e salva apenas
quando a pessoa escolhe uma opção. Durante a reprodução, o trabalhador consulta
o booleano em memória somente ao finalizar uma passagem. Nenhuma leitura de
disco, chamada JNI ou novo temporizador por quadro foi acrescentado.

## API da receita

`transform_java_sources(repo)` retorna `(sources, receipt)`. `sources` contém
bytes sob estas três chaves:

- `client/src/java/org/emulationstation/frontend/station/StationGraphicsPreferences.java`
- `client/src/java/org/emulationstation/frontend/station/StationGraphicsPanel.java`
- `netplay-src/org/emulationstation/frontend/netplay/StationSinglePassVideo720.java`

Compilar primeiro as duas classes cliente. O JAR resultante deve preceder o
`client.jar` original no classpath do player, porque contém o getter novo.
`StationVideoEndFrame` é dependência original de pacote: usar o `rooms.jar`
efetivo no classpath ou compilar sua fonte original como dependência, excluindo
essa classe do JAR de substituição. Sua classe no donor deve ser preservada.

`patch(native_source, sony_video_header, original_graphics_header)` retorna
`(native_cpp, headers, receipt)`. Aplicar depois de `sony_media.sourceTransform`.
Gravar os headers no diretório nativo da compilação final e colocá-lo antes da
mídia preparada na busca de includes:

- `loop_native_system_video720.h`: header Sony com include de escopo, assinatura
  JNI da sobrecarga e um argumento adicional no início do vídeo.
- `native_platform_video_loop.h`: escopo puro `systems && !folders`.

O `native_graphics.h` é conferido e permanece byte idêntico. Os mapas/posters
Sony preparados e `sony_media.py` não são regravados por essa receita.

## Identidades de entrada

| Entrada | SHA256 |
| --- | --- |
| `StationGraphicsPreferences.java` | `0327cb2f25e05162e19f81b50128c478ebbc298e063d219fd391572b30199b52` |
| `StationGraphicsPanel.java` | `7b8483c4775e2f1c2c543f74308be153a4b5b601d1edde3f00881721d0e96654` |
| `StationSinglePassVideo720.java` | `dde13ca08170e98354a22a764a42f9a6a98e032389aba48e81fb5aab3d9e1673` |
| `sony_native_system_video720.h` | `f88f90d04a0da17ab96d4278f2b77ed60f071dcae715c7709bb840d5198a56e5` |
| `native_graphics.h` | `fb266e78ad9daffdf3742b0e3967bfbec7124930997afabc1a8a241cb6cd703d` |

Cada transformação tem inversão exata: qualquer alteração fora das substituições
permitidas impede a preparação. Não há tipo Java, classe anônima ou lambda nova.
A compilação deve comparar o conjunto real de classes do donor:

- DEX28: apenas famílias `StationGraphicsPreferences` e `StationGraphicsPanel`,
  além da mudança de demonstrações `StationFrontend` já delimitada pelo builder.
- DEX35: apenas família `StationSinglePassVideo720`; demais classes byte idênticas.

O native mantém capacidade, shaders, renderização, cache/preload, descarte de
slots, lifecycle e máximo de 30fps. LEDs, controles, emuladores e gameplay não
entram nesta alteração. Recibos de compilação, instalação, observação física e
ativação do servidor continuam sendo provas separadas.
