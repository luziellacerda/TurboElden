# Entrada do segundo jogador — delta conciliado com R34

Fonte `f7f056125ad208d8a0e139b392d382d68f61787f`. Três classes Java alteradas;144 de147 fontes/dependências R34 intactas. O perfil do anfitrião oferece **Entrar na sala**; uma sala própria individual mostra outras salas com vaga. A troca confirma **Sair e entrar**, prepara o jogo antes da saída e confere o membro no destino. Pronto confirma a sala atual.

Leia [o handoff de produção](../../docs/server/RETORNO-SEGUNDO-JOGADOR-SALAS-STATION-20261005.md). Evidências em `evidence`:20+107+60+15 verificações Java e11 do servidor, total213. DEX final compilado; APK desta correção ainda sem montagem/instalação. O R34 do Samsung está confirmado; a versão exata do POCO não foi conferida.

## Compilar

No clone com os snapshots R27/R30/R34 completos, executar `python recipes/build_second_player.py --android-jar CAMINHO --client-jar CAMINHO --r8-jar CAMINHO --output DIRETORIO_NOVO`. Opcionalmente informar java/javac/jar. A receita confere a fonte exata R34 antes de sobrepor este delta.

O resultado `dex/classes.dex` substitui apenas `classes35.dex` no R34 exato, SHA513dd470. Manter o manifesto R34, incluindo o callback Voltar, recuperação de abertura, logs e design R33. O DEX inicial sobre R30 é histórico e foi substituído. O handoff traz hashes, assinatura/alinhamento, preservação integral e roteiro dos dois telefones.

## Limite da troca

São leave e join existentes, após confirmação. A saída é aplicada antes da entrada. Se o destino fechar/lotar, a sala anterior já terá sido encerrada e a falha ficará visível. A troca não é atômica. O servidor, runtime, licenças e arquivos dos jogos permanecem preservados.
