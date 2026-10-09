# R91 — DOWNLOADS e vídeos atualizáveis

Base exata: R90 fonte `58839537f28be3fbf17d012dd764b1431db4acd6`, recibo `1cb887782b931a5a86dffc7a77278a9b07fb9f24`. Samsung atualizado diretamente em 09/10/2026 às 13:40:48 UTC; hash integral, assinatura, UID e dados preservados. Motorola permanece R86.

## Pedidos da central

- O botão ao lado de Plataformas passa a dizer **DOWNLOADS**, com largura, altura e escala de fonte iguais às do vizinho. O espaço da busca é ajustado apenas quando o botão está visível.
- Cancelar remove imediatamente a linha e o contador. A tentativa interna permanece identificada até a transferência terminar de cancelar, evitando que dois gravadores concorram no mesmo jogo. Erros permanentes também oferecem Cancelar.
- Aviso antigo, progresso, pausa, espera pela internet e persistência da fila continuam. O mantenedor confirmou a abertura da central R90; o mantenedor confirmou depois que a R91 deu certo. A central com transferência ativa também foi observada por captura privada; o agente não cancelou o download.

## Vídeos e capas

O cliente busca um catálogo assinado e autenticado em GET `/v1/station/media/catalog?requestId=<32hex>`, domínio `TurboRamaStationAndroid/media-catalog/v1`. Cada arquivo vem de GET `/v1/station/media/files/<sha256>`, na mesma origem com as proteções existentes. O índice vincula produto, aplicação, licença, aparelho, sessão e nonce; tamanho, hash e formato reais são verificados antes da publicação local.

O cache persistente usa a área privada `noBackupFilesDir/station-v2/menu-media`. Downloads são sequenciais, fora da interface, somente com o carrossel ativo. Jogos têm prioridade; sair do menu suspende a transferência de mídia. Não existe novo temporizador periódico: os eventos de seleção e a consulta de catálogo já existente alimentam o agendamento. Catálogo bem-sucedido no máximo a cada cinco minutos; falhas têm espera. Um vídeo atualizado só entra na próxima seleção, sem reiniciar o vídeo atual. Cache válido funciona offline; atualização incompleta mantém a versão anterior.

**Transição:** os 58 vídeos do carrossel permanecem embutidos nesta R91 até ativação do serviço. O vídeo de abertura continua separado. Os 58 arquivos somam 109.503.389 bytes, todos H.264, 720 × 720, 30 fps, sem áudio. O APK ainda tem 2.136.321.444 bytes: nenhuma redução de tamanho ou aquecimento é alegada. As capas continuam usando a rota autenticada e o cache por revisão já existentes.

O servidor foi implementado em código aditivo baseado em `2b04f591eb10ad76efc3b630ded4fff9ef2c2a27`; não foi implantado. A entrega contém as duas rotas, carregamento atômico de revisões e publicador `recipes/publish_media.py`. Flags novas desligadas por padrão. Após a primeira implantação coordenada pelo operador, atualizar somente os vídeos não exige reiniciar o serviço. `SERVER-DELIVERY.json` identifica o commit publicado quando disponível.

## Escopo e evidências

220 Java completos; somente `classes28.dex`, `classes35.dex` e `libturbo_carousel.so` mudam. 13.223 outras entradas do APK preservadas, incluindo os 59 MP4, engines, manifesto, emuladores, LEDs e arte. Menu 30 fps, estrelas/vídeos uma passagem e retenção dois quadros antes do final continuam.

645 verificações de download, 45 de mídia, cinco guardas de preservação e 20 do registro de servidor passaram. Compilação net8 do servidor sem avisos/erros. O publicador foi conferido com os 58 arquivos reais e atualização de um arquivo preservando os outros 57. Java e carrossel recompilados a partir do backup ficaram idênticos. São testes locais/sintéticos; não equivalem a corte físico de rede, ativação em produção ou gameplay online.

APK SHA-256: `af02c36dc143f1e82a683f86f4fa45240952eb621ed8da388298b82bf9436d1c`.

Git contém somente fontes e recibos. Mídia, APK, licenças e capturas privadas ficam fora. Canal ativo e instalador estão no backup único indicado em `release-channels/ACTIVE.json`.

Entrega ao servidor publicada: [26909e31](https://github.com/luziellacerda/Servidor-pix/commit/26909e31bc6bea8097988e0359f7f563b4050cda). Ativação em produção pendente do operador.
