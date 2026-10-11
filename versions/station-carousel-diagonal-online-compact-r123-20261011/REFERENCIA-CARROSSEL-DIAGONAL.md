# R123 — Reta, Diagonal e De lado

## Referência local verificada

Referência pedida: `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx`. `es_settings.cfg` seleciona TURBORAMAx e gamecarousel. `theme.xml:488` inclui `_theme_views/gamecarousel-approved-dashboard.xml`; na linha 483 o tipo é **coverflow**, com pivô central `0.5 0.5`, transição slide/420 ms e fonte boxart. O XML PC pede até 13 itens e sete vídeos; Reta/Diagonal conservam seis vizinhos e nove prioridades. Pelo pedido posterior, De lado passa a dez vizinhos e até treze prioridades; a política de um decodificador permanece.

Hashes dos arquivos locais consultados:

| Arquivo do tema | SHA256 |
| --- | --- |
| `theme.xml` | `510ee9421e6cb372af83c97b077316a9eebc80e08d17e7b027cac35073650637` |
| `_theme_views/gamecarousel-approved-dashboard.xml` | `cab3d8fbc0c37d2a491ffd685b8301bbcb88ec3baa07c2f7c2332de85edb4ba5` |
| `_theme_views/gamecarousel-ps5-global-design.xml` | `857848b4fb526aca2820b1ac3d113356988807085084c898ba80fe2c2602454e` |

O XML não declara ângulo Y nem distância focal dos vizinhos. As rotações `selectedHeroPage*` são camadas repetidas da arte selecionada: -8,5/-14,357/-10,402/-6,551 graus, sobre origens comuns. Somente OuterFar tem opacidade literal zero; outras usam variáveis 0,55/0,75/0,95. Elas não representam a geometria dos índices vizinhos. Os storyboards active/deactive -3/+2 retornam a zero. O page-turn está desativado; o shader de curvatura de página não foi importado.

A implementação primária do [CarouselComponent RetroBat, commit45f37fd](https://github.com/RetroBat-Official/emulationstation/blob/45f37fd74819ee07118ca2e7680a907b25733ac5/es-core/src/components/CarouselComponent.cpp) enumera horizontal/vertical/wheels, sem parser coverflow nessa revisão. O wheel 2D usa ângulo padrão 7,5°; SHA256 do arquivo consultado `432d719dd697a5f2f7ecd5c5707fb38751daab680c57937ac0ec9889dd1c1952`. O executável local declara 7.3.0-stable-win64, mas sua extensão coverflow não foi vinculada a fonte pública exata. **De lado é uma adaptação Android explícita do modelo visual coverflow, não uma réplica comprovada desse renderer PC.** Os 45°/focal1,2 abaixo são parâmetros escolhidos na implementação Android, não valores atribuídos ao XML.

## Três escolhas preservadas

Configurações → Efeitos gráficos → Carrossel: **Reta / Diagonal / De lado**. Desenho estático, foco D-pad e alvos48dp. Reta0 continua padrão e preferências anteriores0/1 não migram. Sistemas, coleções e jogos usam o mesmo adaptador; capa selecionada e LED em evidência têm transformação identidade em todos os estilos.

- **Reta0:** geometria anterior, sem consultas GL novas.
- **Diagonal1:** geometria anterior mantida: esquerda +7,5°, direita -7,5°, pivô central. Escala uniforme `min(w/(c*w+s*h), h/(s*w+c*h))`, para conter a rotação no slot; constantes previamente calculadas.
- **De lado2:** rotação Y equivalente a45°, sinais opostos dos vizinhos e perspectiva central. `f=1.2*w`, `k=1-sin(45°)/2.4`, `d=±sin(45°)/f`. Para coordenadas locais `dx,dy`: `x'=cx+k*cos(45°)*dx/(1+d*dx)` e `y'=cy+k*dy/(1+d*dx)`. `W` fica entre0,7054 e1,2946 na capa; a escala mantém a projeção no slot original, sem novos itens ou sobreposição de slots.

A homografia H é composta na matriz MVP atual, `MVP*H`, sem alterar UV/cor. A divisão homogênea do GLES mantém a interpolação correta da textura em ambas as metades do strip; arte, vídeo/poster e faixa INSTALADO dos vizinhos passam pela mesma projeção. A arte, tamanho e posição local da faixa continuam os anteriores; a capa selecionada permanece idêntica. Clip usa bounds dos quatro cantos projetados e arredondamento exterior; toque usa a inversa exata antes de testar cantos. Índices, seleção, drag e comandos permanecem os existentes.

CELL_EFFECTS(bit16) ou mestre desligados desenham Reta sem apagar a escolha salva. Esta condição é aplicada antes de entrar nas consultas GL do modelo De lado. Nenhuma preferência Céu/Ondas/azul/escuro, economia, vídeo, LED ou FPS foi alterada.

## Uniformes e escopo GL

O renderer preservado da capa usa **u_mvp**; o programa existente de vídeo usa **MVPMatrix**. O lookup consulta os dois nomes no programa ativo. Não são guardados GLuint, localização de uniform ou recurso EGL; a resolução POD de quatro funções GLES ocorre uma vez, evitando IDs obsoletos após recriação de contexto. A presença de MVP é conferida antes de ativar a projeção, com fallback Reta e hit-test igualmente plano quando indisponível nesse ponto.

Cada strip De lado salva a MVP, compõe H, grava a MVP projetada, chama o mesmo renderer e restaura os16 floats por escopo RAII. Não troca programa, textura, FBO, blend ou viewport. `Renderer::drawTriangleStrips`0x2e5470/0x140 do ELF preservado não muda programa/MVP. Seus únicos calls GL são três atributos, buffer, blend e draw; o helper0x2e4de0/0x114 só chama glGetError e rotinas de logs/unwind. Setters de matriz ficam fora dessa função.

`tests/verify_renderer_mvp_r123.py` verifica o ELF exato: SHA256 `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6`, 4.588.272 bytes. Hash da função strip: `9d31095bde488e0edc038577aa430d218ed2be5a6774414eb743c90ac5337dc2`. O recibo público `evidence/renderer-mvp-r123.json` contém apenas hashes/bordas/calls agregados; ELF e disassembly permanecem privados.

Limite de fallback: se um programa externo sem ambos os uniformes fosse trocado depois do teste inicial, o adaptador existente de coordenadas pode projetar XY por CPU, com UV afim aproximado. Os programas próprios de capa/vídeo examinados usam os uniformes reconhecidos e seguem o caminho homogêneo testado. A prova não afirma suporte de shaders externos arbitrários.

## Persistência, custo e preservação

`StationCarouselStylePreferences` mantém arquivo separado `station_carousel_style_r123`, chave style. Começa em Reta sem IO na UI; bootstrap é agendado no worker Station-catalog existente. Mudança anterior à leitura é preservada; escolhas salvam e notificam somente ao mudar. O painel remove listener ao sair. `StationFrontend` publica pelo JNI no bootstrap/mudanças; campo atômico separado não reempacota graphicsState/mask/background/revision. O getter é resolvido uma vez via POD, sem static dinâmico/__cxa_guard, JNI ou IO por quadro. Remover somente campo e dois entrypoints adicionados recupera frontend R122 inteiro.

De lado tem custo novo **limitado, não medido no telefone**: por strip, GetIntegerv, uma ou duas consultas de localização, GetUniformfv, duas gravações de matriz e64 multiplicações/somas de composição. Reta/Diagonal/efeitos desligados não entram nesse caminho. A perspectiva usa os shaders existentes. A ampliação solicitada de seis para dez vizinhos adiciona até quatro desenhos de capas e as texturas correspondentes, além de ampliar a janela de prioridade para13 somente em De lado. Não cria shader, FBO, decoder, timer, worker ou loop; o custo total adicional não foi medido. Conserva30fps dos menus e FIFO/carregamento existentes. Emuladores/runtime/controles/rede/autenticação estão fora do recurso.

## Provas isoladas e limites

`tests/verify_carousel_diagonal_r123.py` usa corpos reais de draw/rounded/clip/hit e preferência real com stubs host: **81.435 geometry,64 preferências,19 guardas,512 ponte nativa**. Abrange três carrosséis/aspectos/sinais, Reta/Diagonal preservados, hero idêntico, UV/cor/count/blend, homografia/inversa, interpolação UV/W dos dois triângulos, clipping/hit, programa u_mvp/programaMVPMatrix, restauração byte exata de MVP e disponibilidade/fallback antes de desenhar. Ponte real resolve uma vez, suporta valores0/1/2 e vincula aarch64/Android26 com -nostdlib/--no-undefined sem símbolos indefinidos ou__cxa_guard.

Recibo atual `evidence/carousel-geometry-r123.json` referencia hashes finais, incluindo painel final de três opções. Vídeo/faixa recuperam fontes R122 retirando exclusivamente os encaminhamentos de geometria; shaders/hero/LED/Céu/Ondas/rede são guardados byte a byte. Syntax NDK do carousel completo e frontend foi conferida; warnings históricos de trigraph do catálogo são separados. Compilação integral/montagem/conferência física pertencem ao fechamento pelo mantenedor. Host e análise ELF não comprovam aparência Android, ganho térmico, gameplay ou estabilidade da GPU.
