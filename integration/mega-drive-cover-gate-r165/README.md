# R165: escopo do efeito na capa Mega Drive

Base exata: shader do carrossel R164, SHA-256
`35e81ef35a825441f303f93fe70d80afce6b272be2c6407fd32d937a2e00287a`.
Esta receita prepara **somente** `magazine_shader.h` para a próxima compilação
combinada. Não compila ou assina um APK, não muda a arte, o relógio da animação,
a intensidade, o mapa de emissores, os demais consoles nem a lógica online.

## O que a auditoria encontrou

* A capa Sonic enviada pelo usuário satisfaz a assinatura azul nova: quatro
  pontos nos trilhos e dois nas letras TURBORAMA medidos na imagem original.
  O perfil escolhido é 1.25; os quatro pontos do mapa antigo são escuros.
* Os perfis 1.0 (capas Mega Drive antigas) e 1.25 (chassi novo) são ramos
  exclusivos do mesmo shader. `drawMagazineCover` escolhe o campo estático ou
  o fallback integral, sem desenhar ambos no mesmo quadro. O antigo contorno
  laser externo não é chamado pelo `flowFormationHook`; o binário R164 contém
  `drawMagazineCover`/`drawMagazineStaticField`, mas não `drawFocusLaser`.
  Portanto, não foi comprovada a presença de dois motores ativos simultâneos.
* A seleção preliminar de fragmentos, `megaSupport`, ainda unia as caixas da
  arte antiga e da nova. Na capa nova, 196.916 de 373.246 pixels lógicos
  admitidos vinham **apenas** do mapa antigo e terminavam com luz zero. Isso
  desperdiça trabalho na preparação do campo e no fallback gráfico; não gera
  uma segunda luz. O nome SEGA na arte nova dependia acidentalmente de uma
  dessas caixas antigas para passar pelo filtro preliminar.

## Correção delimitada

`recipe/patch_mega_gate.py` separa sete limites do novo chassi dos nove limites
legados. O limite próprio do SEGA inclui seus pixels e o halo de 5 px. Com o
classificador de vértices existente, o perfil 1.25 visita somente os limites
novos, e o 1.0 somente os antigos. No fallback R104 sem classificador de
vértices, a união permanece para preservar as duas artes e a compatibilidade
gráfica. O mapa final de luz, as amostras de assinatura, o brilho e a
composição continuam byte a byte iguais.

O patch exige o hash exato da entrada, valida inversão integral, confere os
sete emissores e o halo, compara os nove limites antigos com o original e
mede a área delimitada. Saída do preflight: shader SHA-256
`05877559a10ac5b7cd2de66496a28cf46326dd4cbb768a93e310296619333a8d`;
176.330 pixels de suporte novo, 196.916 pixels legados evitados na capa nova.
Nenhum timer, thread, worker, textura ou desenho por quadro foi adicionado.

## Conferência necessária no pacote combinado

Ao integrar com a mudança de largura da célula, exigir que somente os headers
planejados do carrossel mudem e que ABI, alinhamento, avisos do compilador e
demais entradas do APK permaneçam conforme o manifesto R164/R165. Depois do
retorno PSX do servidor, instalar o único APK combinado nos telefones de teste
e conferir no aparelho a capa Sonic nova, uma capa Mega antiga, SNES, PSX e N64.
Registrar uma preparação do campo por troca real de capa e ausência de
reinícios repetidos do campo enquanto a capa fica parada. A verificação de
fonte não substitui essa observação física.
