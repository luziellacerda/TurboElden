# R87 — LEDs das capas e hardware na seleção

Base integral R86, APK `7b730f4f0ddc892909f0a69ca79618ca79ddcc501a0e682cbd09604d67fdd9b4`, com 213 fontes Java. Não recuperar Activities de versões históricas.

- Estrelas acima do título reduzidas em 30% após o ajuste responsivo.
- Dreamcast: detecção dos emissores laranja corrigida usando a captura real do Samsung, 18 Wheeler, e a referência BANG! enviada pelo mantenedor. Não usa a coleção antiga de molduras brancas do disco.
- Perfis de moldura GameCube roxo, Wii U azul, Switch vermelho e PS1 branco. Reutilizam envelope, velocidade, halo e composição do GLSL existente. A região central da arte fica fora do efeito.
- Mesmo GLSL no carrossel e na capa online. O ciclo de vida e a cadência do renderizador online permanecem iguais à R86.
- Hardware acrescentado: GameCube, Wii U, Switch, PS1, Wii, Saturn, Xbox 360 e painel arcade Final Burn Neo. Preserva os onze recursos anteriores e usa o layout delimitado da sinopse já existente.

Degradê, INSTALADO, fontes de título/contador, BAIXAR, emuladores, protocolo, motores e dados não são alterados. Somente `classes35.dex` e `libturbo_carousel.so` são substituídos no APK.

## Arte e referências

Ilustrações de hardware geradas com a ferramenta integrada e fundo transparente; não são fotografias históricas. Originais e texturas locais ficam em `assets/console` no backup privado, com hashes em `evidence/console-assets.json`. Não há geração de novas capas de jogos nesta entrega.

Prompt utilizado: “Product illustration for a retro game launcher, isolated [console e controle]. Accurate recognizable hardware proportions, polished realistic 3D catalog illustration, three-quarter front view from slightly above, soft studio lighting, centered and fully visible, compact square composition, true transparent background, no panel, no ground, no caption, no decorative effects, no games, no extra hardware. The subject should occupy about 85 percent of the frame and read clearly at 250 pixels.” Variação arcade: painel para dois jogadores, sem representar o FBNeo como console físico.

Mapas novos usam referências locais BloodRayne (GameCube), Bayonetta 2 (Wii U/Switch) e Alien Trilogy (PS1). Essas referências não provam correspondência com todas as capas publicadas. Capturas pessoais e imagens ficam fora do Git.

## Conferência

Compilação, testes isolados de renderização, preservação dos arquivos do APK, reprodução do backup e instalação têm recibos separados em `evidence`. Um teste no PC não comprova desempenho térmico, conferência visual no telefone nem gameplay. Consulte `STATUS.json` e `INSTALLATION.json` para o estado efetivo.

O retorno do servidor foi lido e registrado em `SERVER-REVIEW.md`. Esta atualização visual não altera identidades dos motores nem exige novo cadastro.
