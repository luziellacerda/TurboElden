# R82 — informação de jogadores para teste

Atualização de apresentação sobre a fonte completa R81. Cinco edições conferidas em manuais/documentação original: Super Bomberman 2 (4 simultâneos na batalha), Super Bomberman 3 (5 na batalha original; aplicativo até 4), Bomberman Hero (1), Bomberman Online Dreamcast (4 na batalha local) e The Lost Vikings Mega Drive (3 com Team Player).

O carrossel usa esses fatos como alternativa quando não existe evidência específica confirmada. A sala apresenta os fatos do jogo separadamente das vagas online e mantém a informação descritiva quando a consulta online falha. IDs, plataforma, título e revisão precisam coincidir; não se aplica automaticamente a traduções, hacks ou edições divergentes. Fontes primárias estão em `source-additions/StationGamePlayerFacts.java` e na auditoria `audits/player-counts-20261008/`.

## Limites

O catálogo revision19 tem 3.734 IDs, dos quais 3.479 visíveis e 255 de compatibilidade. Apenas as cinco edições acima receberam fatos descritivos nesta atualização. Outros valores do relatório são candidatos ou pendências, não aprovação automática. Nenhuma quantidade foi inventada para preencher lacunas.

Esta alteração não libera vagas, perfis ou jogos online. As verificações estritas de admissão, o protocolo, runtime, cores e engines permanecem idênticos à R81. O ícone de pessoas é ilustrativo; o texto informa a quantidade. Não há alegação de gameplay validado em quatro aparelhos nem de ativação do servidor.

## Reprodução e pacote

210 fontes completas congeladas em `java/`; somente três fontes anteriores alteradas e uma classe adicionada. Compilação em E:. Para reproduzir a versão corrente após retirar o instalador anterior, usar `release-channels/rebuild_verified.py test-4p --build both --output <nova pasta em E:>` e o canal explícito de `ACTIVE.json`. `prepare.py` e a receita de empacotamento registram a origem R81 histórica; não restaurar essa base como versão atual.

60 verificações locais e 4 guardas de integração; não são gameplay Android. Apenas classes28.dex e classes35.dex mudam: 13.224 entradas e 59 vídeos preservados. Mesmo certificado e alinhamento de 16 KiB. Arte Dreamcast R80 continua arquivada, não integrada.

Recibos da instalação, quando concluída, ficam em `INSTALLATION.json` e `evidence/installation-motorola-r82.json`. As marcações installed:false no recibo de empacotamento registram a fase anterior à instalação.
