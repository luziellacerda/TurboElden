# Menus de configurações e efeitos — R120

## Pedido e base

O mantenedor rejeitou a aparência genérica da R119 e pediu identidade de aplicativo de jogos. Esta entrega parte da cópia exata R119 e modifica somente `native/d0/native_settings.h` e `java/client/src/java/org/emulationstation/frontend/station/StationGraphicsPanel.java`. O online é integrado separadamente pelo responsável pela R120.

## Referências primárias consultadas

- [Xbox Home, Microsoft](https://news.xbox.com/en-us/2023/07/26/welcome-to-your-new-xbox-home/): atalhos rápidos, espaço para arte de jogos e comunidade.
- [PS5 Control Center, Sony](https://blog.playstation.com/2020/10/15/first-look-playstation-5s-next-generation-user-experience/): ações acessíveis e cards relacionados ao jogo.
- [Big Picture atualizado, Valve](https://store.steampowered.com/news/posts/?enddate=1667322980): interface concebida para controle e acesso rápido às funções do sistema.
- [Foco, Android TV](https://developer.android.com/design/ui/tv/guides/styles/focus-system): distinguir foco, seleção, pressionado e desativado.
- [Cards, Android TV](https://developer.android.com/design/ui/tv/guides/components/cards): um assunto por card, hierarquia curta e variantes compactas.
- [Navegação, Android TV](https://developer.android.com/training/tv/get-started/navigation): navegação direcional previsível com indicação clara de foco.

As referências orientam a organização. Não foram copiados assets, marcas ou interfaces completas. A aplicação visual descrita abaixo é uma decisão de design desta R120.

## Design aplicado

Paleta comum: carvão `#06080D`, superfícies `#151F2E`, azul principal `#244EB3`, seleção ciano `#46DBFF`, foco branco `#EFF5FF`, informação secundária `#9EAABC` e opção ativa `#78DEAF`.

### Configurações nativas

- Mantém abas, rótulos, valores, ações, retângulos de toque, dimensões de 48 dp, rolagem e gestos da R119.
- Retira a camada arredondada de cada região: navegação lateral discreta e opções em linhas planas, com etiqueta e valor no mesmo fundo.
- Categoria selecionada recebe uma faixa ciano; o contorno de foco original é branco.
- ONLINE usa azul principal; VOLTAR permanece uma ação secundária. Pressionamento usa os estados já existentes.
- A cor do céu mantém o Lottie e a transição curta existentes, sujeitos às mesmas preferências.
- Cards planos são até seis quadriláteros em um lote fixo de 34 vértices. Usa o programa, arredondamento de vértices, matriz, scissor e blend existentes; mantém fallback por primitivas quando `mappingCover` está ativo. Não adiciona shader, textura, FBO, blur ou alocação dinâmica.

### Efeitos gráficos em Java

- Mestre em faixa única, com estado ATIVO/ECONOMIA e quantidade de opções ativadas.
- Paisagem a partir de 620 dp: AMBIENTE à esquerda e opções à direita em duas colunas; telas menores continuam com rolagem única.
- Ondas, Céu e Desligado usam seletores compactos. Movimento do fundo permanece ligado ao mesmo bit CLOUDS.
- LEDs, Vídeos, Ícones, Células e Transições usam cards de uma camada, desenhos vetoriais estáticos e estado explícito.
- Superfícies com pequenos cortes angulares são desenhadas em Canvas; os caminhos são reconstruídos somente quando os limites mudam.
- Botão Voltar, RadioButtons e Switches permanecem controles Android focáveis. O foco do Switch ilumina o card correspondente. O estado focado/pressionado tem contorno branco; a escolha persistida usa ciano.
- Não há interpretação própria de teclas, interceptação global de botões, novos atalhos ou mudança de mapeamentos. Usa a navegação direcional Android.
- Preserva as escolhas individuais, mestre, máscaras, modo de fundo, migração, listener, descarte e callbacks de lifecycle. ECONOMIA mostra PAUSADO sem apagar a escolha.

## Compilação isolada e limites

- Java: `StationGraphicsPreferences.java` preservada e `StationGraphicsPanel.java` compilaram com JDK 17, `source/target 8` e Android 34; saída 0. Avisos: bootstrap de Java 8 e API já depreciada.
- C++: `native_carousel.cpp` passou por `clang++ --target=aarch64-linux-android26 -std=c++17 -fsyntax-only`, com os headers R120; saída 0. Dois avisos herdados de trigraph em `game_infos.h`.
- A primeira tentativa Java não gravou em E: devido à permissão do ambiente; foi repetida com a gravação autorizada e concluiu. Não houve erro semântico Java nessa tentativa.
- Nenhum teste foi adicionado ou executado. Não houve link, montagem de APK, assinatura, instalação, operação no telefone ou mudança de manifestos nesta subtarefa.
- Ainda falta conferir a apresentação e a navegação direcional no telefone; a compilação não prova alcance físico de todos os controles.
- Não altera a cadência de 30 fps, carrosséis, efeitos LED, filas de capas, preload, rede, sessão, autenticação ou relógios dos emuladores. Não há medição térmica ou de gameplay desta revisão.
