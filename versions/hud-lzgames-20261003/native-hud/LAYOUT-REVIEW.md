# Revisão responsiva e contratos — fontes corrigidos

A revisão R2 está na proposta de workspace e foi copiada pelo responsável para recompilação Android. Ainda não foi instalada nem validada no aparelho. A R1 compilou e foi instalada, mas a captura revelou texto sobreposto: este registro distingue os contratos de fonte da validação visual real.

## Defeito encontrado e corrigido

Antes: o painel limitava sua altura à janela, mas mantinha cabeçalho e aviso sem reservar a lista. Janela 640×240, fonte nominal 32 e aviso com altura completa 144 produziam lista de **−96 px**. Os avisos também limitavam o texto a quatro linhas.

Agora:

- `HudPage` possui seu próprio `ViewManager` e fontes normal/negrito. Esse gerenciador é construído antes e destruído depois de todos os textos e filhos. As preferências e fontes do emulador não são alteradas.
- A fonte local inicia com o tamanho do usuário e diminui quando cabeçalho, aviso completo e até cinco linhas de ações não cabem. O teste de aceitação usa `min(5, entries.size())`; o HUD principal tenta mostrar suas cinco ações, enquanto os seletores maiores mantêm rolagem.
- O mínimo real do upstream é 16 px (`Font::minUsablePixels`). O laço respeita esse mínimo e termina, mesmo se a área ficar muito pequena.
- Todos os títulos, subtítulos e avisos compilam com quebra de linhas, sem `maxLines` que esconda texto.
- A altura uniforme da linha vem da maior altura real de título + descrição; a mesma altura é aplicada ao `TableView` original que interpreta o toque e o controle.
- `StationHudLayout.hh` calcula regiões positivas e sem sobreposição. Se até a fonte mínima não couber, o desenho dos glifos é escalado para dentro da região física reservada. As entradas continuam sendo os eventos nativos da tabela; não há toque simulado nem tradução de eventos para botões do emulador.
- A lista continua rolável e nenhuma fonte global é modificada. O HUD não cria animação, temporizador ou thread adicional.

## Evidências locais

Comando: `python -m unittest discover -s explus-hud-proposed -p test_*.py -v`.

**21 casos aprovados**, sem `expectedFailure`. São três testes de aplicação protegida por hash e dezoito contratos dos fontes, incluindo a compilação do teste de layout C++, a transformação real da API de texto e a condição de cinco ações visíveis.

`test_hud_layout.cpp` inclui **o mesmo header usado pelo HUD** e verifica com `static_assert` 576 combinações: 640×240, 854×480, 1080×2340, 2340×1080, 320×240, 240×320, 1×1 e dimensões zero; fontes 16–128; notas equivalentes a 1–40 linhas; 2, 5 e 11 itens. Confere dimensões positivas, regiões dentro do painel, escala limitada e soma exata sem sobreposição. O caso antigo de −96 px tem regressão explícita.

Isso valida a matemática de alocação real e os contratos estáticos. **Não valida renderização Android, legibilidade em área excepcionalmente pequena ou interação em aparelho.** Continuam necessários compilação dos dois motores, captura visual, navegação, salvar/carregar e retorno às plataformas.

## Falha observada na R1 e correção R2

APK R1: `3d3afc380b109affe5615961b6930ffe7b88f1c96255e8cf39e6e688da66e0f7`. O painel e cartões apareciam em suas posições, porém os textos se sobrepunham no canto superior esquerdo. A captura foi salva pelo responsável como `hud-mega-menu.png`, mas a atividade observada era do SNES; o nome do arquivo não prova que o Mega tenha sido testado.

O fonte real `imagine/src/gfx/common/GfxText.cc` redefine `modelView` em `Text::draw`. A R1 transformava antes de chamá-lo e enviava coordenadas locais; o motor descartava a transformação. Isso não era detectado pela matemática do layout isolada.

R2 acrescenta `Text::drawScaled`: recebe posição absoluta, alinha pelo tamanho escalado e aplica translação/escala em uma única matriz. `draw` conserva sua assinatura e delega na escala 1. O HUD usa a API explícita em todos os textos e recorta cabeçalho/rodapé. Os testes agora leem a implementação real desse comportamento; a confirmação visual continua pendente. Aplicador agora prepara oito arquivos e verifica cinco hashes originais, incluindo os dois fontes Imagine.
