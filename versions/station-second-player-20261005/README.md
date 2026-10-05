# Entrada do segundo jogador — delta sobre R30

Fonte b282b04, três classes Java; 143 de146 fontes/dependências R30 intactas. Oferece **Entrar na sala** no perfil do anfitrião e outras salas com vaga quando a própria sala tem uma pessoa; confirma Sair e entrar, prepara jogo antes de sair e comprova membro no destino. Pronto confirma a sala atual.

Leia [handoff para produção](../../docs/server/RETORNO-SEGUNDO-JOGADOR-SALAS-STATION-20261005.md). Evidências de build/preservação/diagnóstico estão em evidence;20+107+11 verificações passaram. DEX compilado, ainda sem APK instalado. Nenhum servidor/motor/licença/download/carrossel alterado.

## Compilar

No clone com snapshotsR27/R30 completos, executar `python recipes/build_second_player.py --android-jar CAMINHO --client-jar CAMINHO --r8-jar CAMINHO --output DIRETORIO_NOVO`. Opcionalmente informar java/javac/jar do JDK. A receita confere toda a fonte R30 antes de sobrepor este delta.

O resultado dex/classes.dex substitui apenas classes35.dex no R30 exato, SHA1768b7df. O handoff fornece todos os hashes/guards, assinatura/alinhamento e roteiro de instalação/teste. Se chegou APK posterior, conciliar antes; não alterar fontes congeladas ou instalar um APK anterior.

## Limite da troca

São leave e join existentes, após confirmação. A resposta de saída é aplicada antes da entrada. Se o destino fechar/lotar, a sala anterior já terá sido encerrada e a falha fica visível. Não há rollback fictício nem transferência silenciosa de partida em andamento.
