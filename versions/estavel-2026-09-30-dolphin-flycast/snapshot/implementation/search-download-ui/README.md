# Pesquisa e avisos de download — TurboramaStation

Pedido: refazer o visual do menu Pesquisar e de **todos** os avisos de download. Esta entrega altera a apresentação nativa; consulta, filtros, fila, transferência, instalação, falhas e confirmação continuam nas funções originais.

## Base e arquivos

- Base incremental: `../TurboramaStation-loading-progresso.apk`, SHA256 `0d5a0dccfa1a404759b93d9a32623a102b85e03dca240af0083a9bf04637226b`.
- Saída: `../TurboramaStation-pesquisa-downloads.apk`.
- Implementação: `../native_search_download.h`.
- Integração: `../native_carousel.cpp`, `../native_formation.h`, `../native_skin.h`, `../native_pause_menu.h`.
- Cópias dos quatro arquivos anteriores: `*.before` nesta pasta.
- Compilação: `../build_native.py`, seguida de `build.py` nesta pasta. Temporários na unidade E:.
- `build-result.json` registra hash, assinatura e diferença de entradas do APK. Apenas `lib/arm64-v8a/libturbo_carousel.so` pode mudar. O empacotamento interrompe se qualquer outra entrada mudar.

## Apresentação

- Paleta preta e verde, vermelho em erros. Bordas finas, cantos discretos, texto organizado.
- Pesquisa aberta em camada nativa acima do carrossel e sinopses. Campo largo; quando fechado, filtro compacto no cabeçalho.
- Teclado para controle mantém 5 linhas, quantidade, rótulos e retângulos calculados pelo componente original. A última tecla mostra VER RESULTADOS e continua executando a ação original OK.
- No toque, o teclado do Android é mantido. O retângulo SDL acompanha a posição visual do campo. A consulta nativa nunca é encurtada: somente a representação de consultas muito longas mostra o final do texto.
- Mensagem modal com título, texto original e botão OK. Seu retângulo é o mesmo usado pelo manipulador nativo de confirmação.
- Avisos transitórios em cartão preto e verde no canto superior direito. Título e mensagem originais preservados, inclusive nome do jogo. Detecção de palavras de erro afeta apenas a cor. A fila e duração de 3600 ms são nativas.
- Progresso sobre a capa usa bytes recebidos / total. Total desconhecido mostra indicador indeterminado, sem percentual fictício. 100% de bytes não declara instalação concluída.
- Componentes de texto reaproveitam caches; nada de player, imagem, thread ou temporizador adicional.

## Rotas verificadas no binário original

| Função | Endereço original | Relocação |
| --- | --- | --- |
| layoutSearch | 0x219034 | 0x3c1340 |
| drawPadKeyboard | 0x219c4c | 0x3c1388 |
| drawSearch | 0x22f270 | 0x3c16a8 |
| layoutMessage | 0x22cef4 | 0x3c1640 |
| drawMessage | 0x22d090 | 0x3c1648 |
| drawToast | 0x2302d8 | 0x3c16c8 |
| drawCoverProgress | 0x228e7c | 0x3c15b0 |

Mapas de desenho salvos nos arquivos `.asm` desta pasta. Não foram copiados trechos de instruções nem criados trampolins.

O renderer original de mensagens é chamado uma vez para preservar o encerramento e animação de estado; somente suas pinturas antigas são suprimidas nesse escopo. Depois são desenhados os componentes nativos com a nova apresentação. Ocultação dos triângulos limitada ao helper 0x21a3dc–0x21b0c8; do retângulo ao drawMessage; texto OK legado fica transparente apenas no retorno 0x22d578. O menu de pausa permanece com seu hook anterior.

Campos: pesquisa ativa 0x648, consulta 0x650, campo 0x6a8, limpar 0x6b8; teclado ativo 0x598, linha/coluna 0x59c/0x5a0, área 0x5a4. Mensagem ativa/fechando 0x1d98/0x1d99, tempo 0x1d9c, textos 0x1dd0/0x1f00, painel 0x2030, OK 0x2040. Toast textos 0x288/0x298, tempo 0x2a8. Posição real de GuiComponent 0x38/0x3c, tamanho 0x54/0x58, escala 0x60, alinhamento horizontal TextComponent 0x120.

## Estado e limites

Esta revisão não foi promovida ao Git estável. Não desinstalar nem limpar dados para instalar. APK deve ser instalado por atualização com a assinatura existente, depois de confirmar que o usuário saiu de qualquer partida. A USB estava sem aparelho durante a preparação.

Não foram executados testes novos de download, busca, navegação ou aparência no Android. Não afirmar aprovação visual nem desempenho verificado. Consulte `build-result.json` para o resultado da montagem e `installed.json`, se existir, para o estado real da instalação.
