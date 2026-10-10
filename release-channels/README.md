# Fonte candidata atual — R116

`ACTIVE.json.currentCandidate` identifica a R116 instalada no Motorola Edge30
e Samsung A56, com hash integral conferido em ambos. A fonte está em
`versions/station-legacy-cover-diagnostics-r116-20261010` e a explicação completa
em `ALTERACOES-DETALHADAS.md` nessa pasta.

A R116 reúne a linha de otimizações de carregamento e renderização posterior
à R99 e a fila sequencial de capas. Seu estado continua candidato: os testes
de fonte e a conferência física da lista no Motorola estão registrados;
gameplay, primeiro quadro online e ganho térmico prolongado não estão provados.
Java completo e receitas estão publicados, mas a reconstrução do APK requer
o APK privado R115 exato, ferramentas locais e a assinatura original.

Os canais `stable-2p`/R76 e `test-4p`/R95 permanecem referências históricas
identificadas por hash. O bloco abaixo descreve um estado anterior do backup;
não seleciona a versão atual por data nem autoriza sobrepor fontes antigas.

## Histórico dos canais — R76 e R87

`ACTIVE.json` identifica exatamente cada instalador e sua fonte completa. Não selecionar por data nem sobrepor Activities históricas.

- **stable-2p / R76:** referência de dois jogadores escolhida pelo mantenedor.
- **test-4p / R87:** evolução visual da R86; estrelas30%menores, detecção Dreamcast corrigida, perfis LED PS1/GameCube/WiiU/Switch e oito hardwares. Qualificação online continua restrita a perfis exatos; não está homologada em quatro aparelhos.

Backup único em `G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008`. Fontes Java completas, compilados, entradas do carrossel e receitas de reprodução por canal. `rebuild_verified.py` confere hashes e recompila. Histórico permanece no Git/bundle. R80 Dreamcast antigo continua arquivado; as molduras atuais usam o perfil laranja novo.

Recibos em `versions/station-platform-led-r87-20261008/`. R87 instalada no Samsung A56, com hash integral conferido e dados preservados. Motorola permanece na última R86 confirmada. A leitura do retorno do servidor e seus limites estão em `SERVER-REVIEW.md`; não implica implantação por este agente.
