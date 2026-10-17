# Top Gear 3000: partida de três aparelhos em espera (12/10/2026)

## Evidência física

O usuário testou Top Gear 3000 (USA) em três telefones e relatou espera de conexão independentemente do aparelho que cria a sala. A única telemetria USB disponível nesta captura é do moto g52, Android 13, como convidado na posição 2. Não há rastros dos outros dois participantes nem snapshot assinado do servidor; não atribuir a causa exclusiva ao anfitrião ou ao servidor.

O processo `:station_netplay` entrou em `StationRetroActivity` às 02:25:39 (America/Fortaleza). A biblioteca nativa e o vínculo ao serviço da sessão foram iniciados; o RetroArch leu o caminho do core SNES e do conteúdo Top Gear 3000. O túnel WSS v3 recebeu `state=0`, `epoch=1` e cinco PONGs entre 102 e 122 ms. Em cinco diagnósticos, até 02:26:20, permaneceu `nativeStatus=-1`, `localReady=false`, `readySent=-1`, tx/rx/accepted zero. Às 02:26:24 houve `socket-close code=1006` e epochs 2/3; às 02:26:26 apareceu HTTP 409 sem corpo capturado. A thread que registrou a inicialização do RetroArch não constava mais no processo na leitura posterior, embora a Activity ainda estivesse em primeiro plano. Isso exige diagnóstico da saída/inicialização nativa; não prova qual retorno interno a encerrou.

`nativeStatus=-1` é o valor anterior à confirmação da epoch pelo runloop nativo (`station_recovery_status`), não um erro HTTP. O túnel só transmite PAUSED/READY depois da confirmação nativa da epoch e da conexão local. No caminho atual, `localReady` só vira true quando o socket TCP local do core conecta ou é aceito. Portanto o g52 não enviou READY. O servidor exige as quatro READY de dois links para uma sala com três participantes e permanece aguardando quando uma falta. Isso explica a tela de espera observada, mas a causa inicial da ausência de conexão local ainda não foi isolada. O encerramento do socket cerca de 45 segundos após o início é compatível com o prazo de conexão local do host, mas não confirma que esse prazo foi a causa sem o log do anfitrião.

Captura bruta privada, fora do Git: `work/live-top-gear-3000-20261012/logcat.txt` SHA-256 `6f284269a6737625d6cdc194fb7805ae4f61a515ec9df1f7aae0e7f7aa9090f7`. Não publicar identificadores de sala, URLs de sessão, tokens, serial, caminhos de ROM ou conteúdo.

## Limites por jogo e errata de cinco participantes

A matriz R134 marca Top Gear 3000 e a edição PT-BR como `[2,3,4]`; cinco não é um modo deste jogo. Oito entradas visíveis possuem contagens acima de dois compatíveis no histórico atual: NBA Jam `[2,3,4]`; Secret of Mana `[2,3]`; Super Bomberman, Super Bomberman 2 e a edição PT-BR de 2 `[2,3,4]`; Super Bomberman 3 `[2,3,4,5]`; Top Gear 3000 e PT-BR `[2,3,4]`. Esse histórico não substitui o perfil aprovado e a resposta assinada fresca da produção.

Errata R138: a auditoria inicial usou o header histórico R77, com teto de quatro, mas esse arquivo não descreve o runtime instalado. O APK R136/R137 contém `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`; sua fonte correspondente de 09/10 define cinco posições, quatro convidados e máscara 31. Não há motivo para alterar esse limite. O servidor e Java também permitem cinco nos perfis SNES específicos. Ainda falta comprovar gameplay em cinco aparelhos num modo que permita cinco. Top Gear 3000 continua limitado a quatro por seu próprio modo. Ver a [auditoria R138](../station-r138-snes-dsp-startup-20261012/README.md).

## Verificações necessárias antes da liberação

1. Capturar, em uma mesma tentativa, eventos do anfitrião e dos dois convidados: início/fim da thread RetroArch, abertura da porta TCP local, `onNetplayListening`, estado nativo por epoch, conexão local e PAUSED/READY por link. Guardar apenas códigos e contadores no handoff público.
2. Obter `barrierDiagnostics` member-only assinado do servidor, se o patch já estiver ativado, com dois links, quatro attachments, HELLO/PAUSED/READY, `pendingBytes`, `waitingReasons` e a mesma epoch. Sem recibo de deploy, não presumir disponibilidade do campo.
3. Testar Top Gear 3000 com 2, 3 e 4 aparelhos, todos no mesmo APK/identidade registrada, e entrada, vídeo, áudio, controles P1–P4, perda/retorno de rede e saída humana de anfitrião/convidado. Não usar o teste de 5 para esse jogo.
4. Para um modo SNES aprovado de cinco, validar o suporte nativo já existente; confirmar cinco entradas independentes P1–P5 em jogo, quatro links, oito attachments e READY para todos. Preservar as restrições de PSX e de cada outro jogo.
5. Repetir navegação e saída no moto g52 para confirmar a contenção do ANR de capa; a R136 de capa não altera o túnel, o core nem a barreira da partida.

Nenhum teste físico de 3/4/5 foi aprovado nesta investigação. A R136 final corrige apenas o vínculo dos marcadores da revisão de capa e não deve ser apresentada como correção da espera de Top Gear 3000.
