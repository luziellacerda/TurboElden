# Fonte candidata atual — R126

`ACTIVE.json.currentCandidate` identifica a R126 compilada, assinada e conferida, ainda não instalada e sem promoção a estável. Fonte atual: `versions/station-dolphin-online-r126-20261011`, commit `efd9878df3e87ecf22d8fbddeddd30baccb8d3dc`. Última instalação comprovada: R124.

A [entrega N64](N64-ONLINE.md) reúne a fonte real Mupen64Plus AE, a identidade integrada R126 e suas evidências. O [índice dos motores](ONLINE-SYSTEMS.json) registra a continuidade de um sistema por vez: PSX é o próximo; SNES e Mega Drive ficam preservados a pedido do mantenedor. Não criar snapshots ou APKs adicionais para organizar o Git; atualizar os apontadores e manter o único backup completo em F:.

Gameplay e ativação efetiva do servidor para esses novos motores ainda exigem confirmação. A compilação não substitui essas provas.

Os canais `stable-2p`/R76 e `test-4p`/R95 permanecem referências históricas identificadas por hash. O bloco abaixo descreve um estado anterior do backup em G:; ele foi substituído pelo backup único em F: e não seleciona a base atual por data nem autoriza sobrepor fontes antigas.

## Histórico dos canais — R76 e R87

`ACTIVE.json` identifica exatamente cada instalador e sua fonte completa. Não selecionar por data nem sobrepor Activities históricas.

- **stable-2p / R76:** referência de dois jogadores escolhida pelo mantenedor.
- **test-4p / R87:** evolução visual da R86; estrelas30%menores, detecção Dreamcast corrigida, perfis LED PS1/GameCube/WiiU/Switch e oito hardwares. Qualificação online continua restrita a perfis exatos; não está homologada em quatro aparelhos.

Backup único em `G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008`. Fontes Java completas, compilados, entradas do carrossel e receitas de reprodução por canal. `rebuild_verified.py` confere hashes e recompila. Histórico permanece no Git/bundle. R80 Dreamcast antigo continua arquivado; as molduras atuais usam o perfil laranja novo.

Recibos em `versions/station-platform-led-r87-20261008/`. R87 instalada no Samsung A56, com hash integral conferido e dados preservados. Motorola permanece na última R86 confirmada. A leitura do retorno do servidor e seus limites estão em `SERVER-REVIEW.md`; não implica implantação por este agente.
