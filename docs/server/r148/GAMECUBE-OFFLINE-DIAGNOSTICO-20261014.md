# GameCube offline — causa reproduzida na R148

Em 14/10/2026, o A56 com a R148 instalada exibiu **“Não foi possível preparar o Dolphin. Volte e tente novamente.”** ao abrir *The Legend of Zelda: The Wind Waker* sozinho. A falha repetiu às 09:20 e 09:21, horário local. O registro privado contém `TurboDolphin: Embedded launch failed`, seguido de `InvocationTargetException` e causa `java.lang.LinkageError`: `EmulationActivity.onPause()` tenta sobrescrever um método `final` de `tdolphin.fragment.app.FragmentActivity`. A imagem da mensagem e o registro bruto ficam fora do Git (`outputs/gamecube-windwaker-a56-erro-20261014.png` e `work/gamecube-offline-a56-private/logcat.txt`). Esta é uma falha **offline**, anterior à execução do jogo e independente do cadastro de salas no servidor.

## Origem e alcance

No APK oficial Dolphin 2609-7, `FragmentActivity.onPause()V` é `public final`, sinalizadores DEX `0x0011`, e `EmulationActivity` não declara `onPause()`. A receita de integração online R126 (`versions/station-dolphin-online-r126-20261011/recipe/patch_dolphin_smali.py`) acrescentou `EmulationActivity.onPause()V` como `protected`, sinalizadores `0x0004`, para notificar `StationDolphinSession.onGamePause()`. `EmulationActivity` estende `AppCompatActivity`, que estende `FragmentActivity`; a classe intermediária não declara `onPause()`. O resultado tenta sobrescrever um método final e ainda reduz a visibilidade de `public` para `protected`.

Os APKs assinados R126, R128, R134, R143 e R148 foram lidos diretamente por dexlib2: todos conservam esses mesmos dois sinalizadores em `classes10.dex`. Logo, o defeito existe **pelo menos desde a R126**; não foi criado pela R144 visual, R145, R146, R147 ou R148. A inspeção de 51.604 classes do APK R148, incluindo os 15 descendentes de `FragmentActivity`, encontrou essa como a única colisão de método virtual `final` ou de visibilidade menor nessa hierarquia. `FragmentActivity.onActivityResult()` também é final, mas `EmulationActivity` não o sobrescreve. Outros métodos de ciclo de vida não apresentam essa colisão.

O caminho de jogo normal é `gamecubeCommandHook` → `DolphinBootstrap` → `DolphinEntryActivity`/`EmulationActivity` → `libdolp.so`. O seletor usa `libstation_dolphin_online.so` somente para a preparação privada de uma sala. O motor offline `libdolp.so` é byte idêntico entre R143 e R148, SHA-256 `a436ab9d34e3e5895e3a5459cc140ce1832299fc492d47f04e7d6ba07d248c1d`; `libdolp_hook.so` também, SHA-256 `3910e6e2e0d04bf50ba485b3df3336e77c051760700933c451b5abe4df95e828`. `classes11.dex` e `classes12.dex` são idênticos (SHA-256 `6970325cc48b12ab9e1bebb50badbd743a114f82b3397742fc46c3108697f462` e `297084c7424ababd5bf31abf3af929b8c6312af34c02f78c24f588fd5584af41`). Das 13.860 entradas R143→R148, dez diferem; nenhuma substitui o motor offline.

O handoff estável de 30/09 confirmou a abertura de um jogo **Wii** e retorno ao menu, sem prova de uma partida GameCube. O APK oficial Dolphin usado como doador não tinha o override conflitante. A designação estável R143 se refere aos testes concluídos naquele ponto e não homologa o Dolphin offline.

## Reparo mínimo proposto

Em `classes10.dex`, alterar somente os sinalizadores de dois métodos existentes, conservando nome, protótipo, código e demais membros:

| Método | Atual | Proposto | Motivo |
| --- | --- | --- | --- |
| `Ltdolphin/fragment/app/FragmentActivity;->onPause()V` | `0x0011` — `public final` | `0x0001` — `public` | Permitir o override sem reduzir o acesso público já existente. |
| `Lorg/dolphinemu/dolphinemu/activities/EmulationActivity;->onPause()V` | `0x0004` — `protected` | `0x0001` — `public` | Igualar o acesso da base e manter a notificação online já implementada. |

Remover apenas `final` não basta: o override continuaria com visibilidade mais restrita. Tornar a base `protected` alteraria sua interface pública atual. Remover o método filho descartaria a notificação de pausa exigida pela integração online. A proposta mantém ambas as rotas e não mexe em CPU, JIT, renderer, configuração, controles, saves, conteúdo ou transporte. **Ela ainda precisa de montagem e teste Android real; esta auditoria não é recibo de correção instalada.**

Depois de montar, conferir que as duas alterações de sinalizador são os únicos bytes semânticos do DEX10, executar verificação de classes/inversão, assinatura e comparação integral das entradas do APK, e reproduzir primeiro o Wind Waker offline com a mesma edição no A56. Também exercitar pausa/retorno/saída e uma sessão Dolphin online real. Como DEX10 integra o vínculo das identidades independentes, qualquer APK novo precisa dos marcadores e do kit de servidor **exatamente correspondentes** antes de homologar salas online; o cadastro de servidor não é necessário para confirmar o reparo offline.
