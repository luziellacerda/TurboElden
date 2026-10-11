# R123 — orientação e dez capas no modelo De lado

Correção posterior solicitada pelo mantenedor: inverter a orientação das capas e preencher o espaço entre elas com mais quatro capas.

De lado usa dez posições à direita, com espaçamento calculado pela largura projetada. A apresentação continua no começo da lista quando necessário e não repete itens em listas menores. A orientação usa a posição desenhada, evitando inverter novamente as capas que voltam ao índice zero. A capa principal fica com a mesma dimensão. Reta/Diagonal mantêm seis vizinhas e os campos geométricos anteriores.

O plano de carregamento aceita até13 prioridades somente em De lado com efeitos de células ativos. Os demais modos mantêm9. Mudanças de orçamento são publicadas mesmo se uma lista pequena produzir os mesmos índices. Permanecem uma solicitação de capa por vez, fila Java/worker únicos, revelação sequencial, cache, retry/backoff e lifecycle. Não se adiciona decodificador.

Provas dos corpos C++ reais: 19.328 casos/572.308 verificações de slots, pintura, volta da lista, prioridades e toque; 19.901 casos/164.661 verificações do plano frontend; 81.435 verificações geométricas,64 de preferências e512 da ponte. A prova inicial de dez capas foi recompilada independentemente (10.544 casos/297.138 verificações); a prova final incorpora a ordem descendente real do renderizador e o limite de seis posições durante collapse. São testes isolados, não medição de Android ou gameplay.

Na posição17 de23, foram conferidos a capa principal17 e as vizinhas18..22,0..4, sem duplicatas. Picking/recorte usam a mesma transformação da imagem; MVP original é restaurado. O renderizador original foi inspecionado: não limita a distância em6; sua formação inicial já existente pode levar aproximadamente1,52s para completar a opacidade do décimo slot. Essa regra não foi alterada.

Quatro capas adicionais exigem até quatro desenhos adicionais e texturas. O consumo real não foi medido; não há alegação de custo zero ou melhoria térmica. Modos econômicos e30FPS dos menus continuam. Nenhum motor, controle, protocolo, registro, manifesto ou dado de jogo foi alterado.

Os documentos REVIEW-CAROUSEL-SIDE-R123 e seu recibo cobrem a implementação anterior de seis vizinhas com os hashes indicados na época. Para esta ampliação, usar evidence/carousel-ten-covers-r123.json, evidence/side-cover-plan-r123.json e evidence/carousel-geometry-r123.json. A instalação e a observação física têm recibos separados.
