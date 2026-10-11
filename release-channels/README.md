# Fonte candidata atual — R129 corrigida

Estado atual em [evidence/STATUS.json](../integration/local-sony-demos/evidence/STATUS.json). A [falha da primeira tentativa](../integration/local-sony-demos/evidence/first-candidate-startup-failure.json) é histórica.

`ACTIVE.json.currentCandidate` e `ONLINE-SYSTEMS.json` identificam a R129 compilada, assinada e conferida, ainda sem promoção a estável. Fonte atual: `integration/local-sony-demos`, commit `cf623c7c5cf34d4aa59ad278dc98fa6d7a50721b`; instalador `TurboStations-Premium-R129-20261011-Final-Modal.apk`; APK SHA256 `89dd543986fdcb0c4b7ea53e82de87907f3b41ee0fe892479d8a63f52e4b7df0`, 2237505749bytes.

A variante R129 acrescenta demonstrações, arte e mídias locais PS3/PS4, além do acesso às configurações dos emuladores externos. PS3/PS4 continuam offline. Os emuladores não estão embutidos no Station; sua instalação separada no Motorola está no recibo independente Sony, vinculado à observação af3b/e701. A versão Final-Modal exclui os dois textos Sony do desenho fora das configurações, mantendo renderer e economia. Os quatro motores reais N64/GameCube/Wii/PSX preservam cores, opções, perfis, capacidade e protocolo; seus IDs no índice vinculam o bundle atual. SNES/Mega Drive, economia, renderer, vídeos existentes, cache e controles ficam preservados; as mídias Sony reutilizam o motor de vídeo atual.

A primeira R129 `83173d43737efa29e4e8e26309ec06b6e545909a`/`82bea84df62172214eedab6f52440e990ca599af75397cbbaebe800ac0da4279` foi instalada, mas apresentou recusa do caminho de capa DEMO no parser nativo. Essa tentativa é histórica e não escolhe o instalador atual; a fonte corrigida usa o cache privado já permitido.

O [handoff integrado único](../docs/server/normal-motors-r128-20261011/HANDOFF-UNICO-MOTORES-ONLINE-R128-20261011.md) mantém o mesmo procedimento e branch. Os recibos administrativos de testes R128 permanecem históricos; não são testes R129 ou gameplay. Usar os recibos atuais e o backup único em F:, sem selecionar APK por data. Instalação integral comprovada no Motorola Edge 30, com UID e dados preservados, conforme `../integration/local-sony-demos/evidence/installation-motorola-r129-menu.json`. A conferência física final no Motorola observou o catálogo e as listas DEMO dos dois sistemas, com capa, nome, sinopse/aviso e contador1/1; ambos os marcadores exatos tinham83bytes. Os heróis, miniaturas e frames/posters das mídias Sony apareceram; movimento dos vídeos não foi validado por imagens estáticas. Os dois botões de configurações abriram, por toque humano, aPS3e Welcome e Bachata S4 0.2.4 com seu aviso inicial de notificações; nenhuma permissão foi respondida nem setup concluído. Após retornar pelo Login público à ESActivity, os textos Sony não vazaram no carrossel. O recibo público agregado do app está em `integration/local-sony-demos/evidence/physical-observation-final.json`. Autenticação, ativação de servidor, gameplay e melhora térmica continuam não validados.

Os canais `stable-2p`/R76 e `test-4p`/R95 permanecem referências históricas identificadas por hash. O bloco abaixo descreve um estado anterior do backup em G:; ele foi substituído pelo backup único em F: e não seleciona a base atual por data nem autoriza sobrepor fontes antigas.

## Histórico dos canais — R76 e R87

`ACTIVE.json` identifica exatamente cada instalador e sua fonte completa. Não selecionar por data nem sobrepor Activities históricas.

- **stable-2p / R76:** referência de dois jogadores escolhida pelo mantenedor.
- **test-4p / R87:** evolução visual da R86; estrelas30%menores, detecção Dreamcast corrigida, perfis LED PS1/GameCube/WiiU/Switch e oito hardwares. Qualificação online continua restrita a perfis exatos; não está homologada em quatro aparelhos.

Backup único em `G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008`. Fontes Java completas, compilados, entradas do carrossel e receitas de reprodução por canal. `rebuild_verified.py` confere hashes e recompila. Histórico permanece no Git/bundle. R80 Dreamcast antigo continua arquivado; as molduras atuais usam o perfil laranja novo.

Recibos em `versions/station-platform-led-r87-20261008/`. R87 instalada no Samsung A56, com hash integral conferido e dados preservados. Motorola permanece na última R86 confirmada. A leitura do retorno do servidor e seus limites estão em `SERVER-REVIEW.md`; não implica implantação por este agente.
