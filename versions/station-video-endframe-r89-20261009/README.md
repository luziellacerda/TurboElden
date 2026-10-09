# R89 — quadro final do vídeo e distância das estrelas

Base completa: R88 corrigida, com os LEDs preservados. Este é o modelo solicitado para publicação antes da nova tela de downloads.

## Alterações

- Vídeo continua com uma reprodução por seleção. Antes de encerrar, pausa e busca o quadro situado dois quadros antes do último, usando `SEEK_CLOSEST`. Mantém a imagem e libera o decodificador.
- A busca tem limite de espera e, se não completar, conserva a imagem anterior disponível. Troca de seleção e saída cancelam os callbacks.
- Estrelas descem até 2% da altura da tela, dentro do espaço existente antes do título. Tamanho e posição horizontal preservados.
- LEDs, menu de 30 fps, vídeos, fontes, degradê, capas, emuladores e rede permanecem preservados. As estrelas continuam com uma passagem.

215 fontes Java completas; alteração de `StationSinglePassVideo720`, adição de `StationVideoEndFrame` e mudança de geometria em `native_info.h`. A política de quadros usa os vídeos CFR de 30 fps existentes. A busca pausada segue o [contrato oficial do MediaPlayer](https://developer.android.com/reference/android/media/MediaPlayer#seekTo(long,%20int)).

## Evidências e limites

Java e carrossel compilados. 10.603 verificações de cálculo/limites/geometria e nove guardas passaram. Arquivos responsáveis pelos LEDs e pela política de 30 fps conferidos por hash contra R88. Estas verificações não provam o comportamento de todos os decodificadores físicos nem redução de aquecimento.

Empacotamento, assinatura, reprodução do backup e instalação constam nos recibos posteriores de `evidence/` e `STATUS.json`. Não considerar compilação como prova de instalação.

## Próximo pedido, separado deste modelo

Adicionar um acesso a downloads ao lado de Plataformas, preservando o aviso existente. A lista deve apresentar capas, nomes, progresso, tempo, velocidade, pausa e cancelamento; interrupções de rede devem aguardar reconexão. Esse recurso não integra a R89.
