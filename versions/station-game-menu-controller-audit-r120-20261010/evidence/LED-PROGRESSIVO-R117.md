# LED progressivo R117 — 10/10/2026

O atraso tem uma causa concreta no código R116: o campo estático é calculado em quatro linhas por quadro, porém o carrossel e a capa online ocultavam todo o efeito até terminar o campo inteiro. Uma capa de 960 linhas exige 240 quadros, aproximadamente oito segundos a 30 fps. Esse cálculo explica o tempo de preparação; não é uma medição física desta revisão.

Na R117, a textura candidata recebe zero em toda sua área antes de qualquer publicação. Cada quadro prepara no máximo quatro linhas, distribuídas entre quatro faixas disjuntas. As primeiras parcelas passam pelo shader já existente: o campo zero mantém a imagem base; o campo calculado apresenta o LED. O efeito começa nas parcelas preparadas enquanto o restante continua a ser calculado. A conclusão integral ainda pode exigir os mesmos oito segundos nessa altura. Não se deve anunciar que todos os LEDs aparecem completos instantaneamente.

As faixas começam nas coordenadas de moldura já medidas: laterais em y=565, cabeçalho em y=80, laterais inferiores em y=1010 e rodapé em y=1454 no espaço de arte de 1536 linhas. O online ajusta essas sementes ao `FIT_CENTER`. As sementes apenas ordenam o trabalho: não forçam emissores numa capa, não mudam as regiões do shader e não garantem que toda arte possua um emissor em cada faixa. Cada linha acaba sendo calculada exatamente uma vez, inclusive em dimensões que não são múltiplas de quatro. Regiões ainda incompletas podem apresentar uma revelação gradual das luzes durante a preparação.

Os três arquivos que definem a matemática de cor, ganho, halo, velocidade, cabeça e rastro foram conferidos byte a byte contra a R116 e permanecem idênticos: `premium-magazine-led-android.glsl`, `magazine_shader.h` e `StationCoverLightingShader.java`. O campo nativo continua RGBA16F, e o online continua RGBA8. Nenhum cálculo monolítico, espera GL de conclusão ou retorno temporário ao kernel pesado foi introduzido no caminho otimizado.

Há até três campos completos guardados para revisitas no mesmo contexto GL. A retenção nativa é limitada a 8 MiB de texturas adicionais. A retenção online é limitada a 8 MiB incluindo as texturas e o tamanho de alocação dos Bitmaps retidos, de forma conservadora. Esse orçamento não inclui a textura/campo ativo e o candidato que já pertenciam ao renderer. Campos maiores que o orçamento não ficam guardados para revisitas. Não há cache GL compartilhado entre o contexto nativo e os diferentes workers online.

No nativo, as chaves incluem origem, identidade/revisão, modelo, dimensões e viewport completo. Upload, atualização ou destruição da origem retiram os campos correspondentes antes de reutilização do GLuint. Mudança de catálogo elimina as entradas guardadas. Na perda de contexto, os nomes antigos são esquecidos sem serem excluídos pelo novo contexto. No online, bitmap e seu `getGenerationId()`, modelo e dimensões compõem a identidade; alterações no conteúdo do mesmo Bitmap invalidam a entrada. Desligar o LED remove callbacks de animação, libera os recursos do renderer online e, no próximo desenho nativo, libera campos/candidatos/objetos auxiliares. Ativar novamente recria o contexto online e prepara o efeito da seleção atual.

Provas executadas no host:

- C++: **PASS 2.659.588** verificações do planejador real, alturas de 1 a 1536, quota de quatro linhas, cobertura completa e ausência de repetição.
- Java: **PASS 7.978.753** verificações do planejador real, mesmas alturas e três formas de letterboxing, quota e cobertura.
- C++: **PASS 818** verificações das funções reais de retenção extraídas do header de produção, com mocks estritos de nomes GL/contextos: orçamento/LRU, revisões, modelo, viewport, dimensões, origem atualizada, origem destruída, nome reciclado, mudança de contexto e campos grandes.
- Compilação Android isolada de `StationOnlineCoverView`, `StationMagazineRows`, shader e preferências: passou com Android 34 e Java 8.
- Identidade dos três shaders contra R116: passou.

O recibo sanitizado é `led-progressive-checks.json`. Esses testes não medem frame pacing, ganho de consumo, aquecimento, percepção visual das faixas ou gameplay. A distribuição em quatro draw calls curtos por quadro acrescenta algum trabalho de submissão/classificação, mantendo a mesma quota de pixels por linhas. O aparelho precisa confirmar o primeiro LED visível, o resultado completo, trocas rápidas, revisitas, perda de foco e liga/desliga. Não há alegação de redução térmica desta revisão.
