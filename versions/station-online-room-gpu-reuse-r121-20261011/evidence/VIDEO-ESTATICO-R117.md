# Vídeos desligados com imagem preservada — R117

Na revisão independente, a opção de desligar vídeos retornava antes de pintar
os quadros, enquanto a formação nativa ocultava o JPG original. Isso deixaria
as células de plataformas/coleções escuras no modo leve.

## Correção

- `native_formation.h` preserva o JPG original quando VIDEO está desligado,
  mantendo a proporção e a regra dos cantos das coleções. É também a imagem
  de segurança se GLES, programa de preview ou poster não estiver disponível.
- `native_system_video720.h` aposenta os decoders pelo procedimento existente.
  O novo caminho estático prefere um quadro retido; quando falta, admite um
  único poster já incorporado por quadro do menu, começando pela seleção.
  Os demais aparecem progressivamente sobre os JPGs, sem tela vazia.
- O caminho estático não inicia MediaPlayer, não consulta capacidade nem
  atualiza a SurfaceTexture e não faz acesso de rede. O encerramento de um
  decoder que já estava aberto continua usando o stop existente até terminar.
- Depois de admitidos os posters, não há novos uploads. A restauração de estado
  GLES reutiliza o wrapper de desenho retido existente. Contexto diferente,
  decoder ainda sendo encerrado ou programa nativo inválido mantêm o JPG.
- Preparação/reprodução com VIDEO ativo é idêntica à R116 após o novo gate;
  resolução, quadros por segundo, UVs, matriz e política de uma reprodução
  não foram alterados.

## Evidência isolada

`tests/verify_video_static.py` extrai os helpers de produção, compila-os com
mocks de GLES e executa 156 verificações de prioridade, admissão limitada,
desenho/matriz/UVs/cantos, quadro retido, ausência de poster, contextos e falhas.
O teste também compara todo o trecho ativo com a R116. O teste existente
`video720_retained_draw_state_test.cpp` passou para VAO e atributos individuais.
`verify_graphics_integration.py` passou com 30 guardas de escopo/integração.

Os probes não representam medição térmica nem conferência visual no telefone.
