# R90 — central de downloads

Base: modelo R89 publicado em `faf7e3e915a041812a72eb9a894c6d2f7dd34329`, recibo posterior `51331b0d1990f671215c7941f2eaac703369a9c8`.

## Interface

Um aviso adicional aparece na barra imediatamente à esquerda de **Plataformas**, depois de iniciar um download. Exibe o número de trabalhos ativos, incluindo pausados e aguardando conexão. Quando só há histórico, mostra **VER**. Ao tocar, abre uma tela com lista de capas, nomes, plataforma, progresso, velocidade, tempo transcorrido, estimativa restante, pausa, retomada e cancelamento confirmado. Voltar fecha a central e mantém o download.

O aviso inicial, a barra de progresso nas capas e a notificação Android existentes foram preservados. A central atualiza informações uma vez por segundo somente enquanto aberta. Capas usam o cache/autorização existente, são reduzidas para a lista e podem ser buscadas novamente após falha de conexão. Não há nova animação contínua.

## Fila e recuperação

- Uma transferência por vez, até 32 pendentes, com histórico em memória limitado a 48 linhas.
- Falhas de transporte, arquivo de rede incompleto e respostas temporárias 408/429/500/502/503/504 aguardam e tentam novamente; sem limite que cancele o jogo automaticamente. Intervalo cresce de 2 até 30 segundos e respeita `Retry-After`, limitado a uma hora. A volta da rede antecipa esperas de conexão.
- Pausados não fazem requisições; cancelar retira a tentativa e impede retorno automático. Preparação final mostra pausa desabilitada para proteger a publicação transacional.
- Fila e escolha de pausa ficam em um arquivo local limitado, somente IDs e estado. Ao reabrir o aplicativo, os itens são conferidos no catálogo autorizado antes de retomar. Encerramento do gerenciador drena o registro antes da nova instância.
- A autorização do servidor é de uso único. Cada nova tentativa pede **uma autorização nova**, com sessão e assinatura normais. A transferência recomeça do início; não há suporte comprovado a Range/retomada por bytes. A tela informa isso.
- Falta de espaço, rejeição de autenticação, descritor inválido ou erro permanente permanece visível e exige ação explícita. Não é tratado como queda de internet. Assinatura de respostas, TLS, tamanho e validação do instalador continuam ativos.
- O bloqueio de energia do serviço é liberado durante fila parada, pausa e espera de rede/servidor. Volta a ser adquirido apenas durante autorização, transferência ou preparação.

## Escopo preservado

217 fontes Java completas. Somente cliente de downloads e carrossel mudam; DEX das salas, motores, engines, manifesto, LEDs, degradê, vídeos e correções R89 permanecem idênticos. O servidor não foi alterado e não requer novo cadastro de motor.

## Verificação

641 verificações locais usando fila/API/instalador reais e dados sintéticos assinados: queda durante leitura, recuperação automática, nova autorização, duplicatas, pausa, cancelamento, recusa 403, persistência e preservação de instalação anterior. O teste achou e a implementação corrigiu a ordem de encerramento do registro da fila. Guardas por hash conferem aviso original, LEDs e vídeo R89.

São testes isolados, sem alegar teste físico de corte de internet, todos os jogos ou estabilidade prolongada. `evidence/package.json`, `STATUS.json` e `INSTALLATION.json` registram empacotamento, reprodução do backup e instalação conforme concluídos. A publicação contém código e recibos; nenhum APK, mídia, licença, ROM ou captura pessoal.
