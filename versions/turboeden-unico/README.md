# TurboramaStation + TurboEden único

Esta pasta registra a versão 1.0.8 ensaiada no aparelho e o tema editável da interface EmulationStation. O fluxo pretendido é **carrossel de sistemas → jogos do sistema selecionado → iniciar jogo**.

## Tema

O tema está em [`theme/TURBORAMA-ANDROID/`](theme/TURBORAMA-ANDROID/). Em `_shared/common.xml`, a tela `system` define o carrossel horizontal de sistemas. As telas `basic`, `detailed` e `grid` definem a lista horizontal de capas de jogos. Os fundos vetoriais ficam em `_shared/background.svg` e `_shared/background-game.svg`.

Esta revisão mantém o carrossel como primeira navegação, mostra cinco capas por vez ao entrar em um sistema, realça a seleção e melhora a posição da grade em versões que ignoram `origin` em `imagegrid`.

Para usar o tema no aparelho, copie a pasta `TURBORAMA-ANDROID` para `/storage/emulated/0/EmulationStation/.emulationstation/themes/` e reinicie a TurboramaStation. Uma atualização do APK pode preservar a cópia antiga do tema nessa pasta; nesse caso, substitua somente os arquivos do tema. O tema não muda os arquivos dos jogos.

## Limite da tela nativa

A tela roxa de biblioteca e loja com os botões `JOGAR`, `SAVES` e `APAGAR` é desenhada pelo frontend nativo em `libmain.so`. Seus botões e a lógica de troca de telas não são controlados pelo tema XML. Esta pasta registra o desenho pretendido para essa tela, mas a versão publicada do tema não altera esse código nativo.

## APK e dados privados

O [handoff](HANDOFF.md) descreve a versão 1.0.8, o funcionamento confirmado no Samsung SM-A566E e as limitações. O APK de teste incorpora chaves e firmware privados do usuário e, por isso, não é publicado neste repositório. Este diretório não contém APK, chaves, firmware, jogos nem BIOS.
