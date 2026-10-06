# R39 — temas, Lotties, coleções, metadados e pesquisa

## Entrega comprovada em 06/10/2026

Pacote `org.turboramastation.frontend`, namespace Java `org.emulationstation.frontend`. Fontes canônicas: `E:\ESTUDO APK\work\station-theme-collections-r39-20261006`. APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Temas-Colecoes-R39-20261006.apk`.

- SHA-256 APK: `e1a38b502843e3506c06f510e79741a6a6e65247ef1246264b9a361ad56cc840`.
- Tamanho: 2.086.148.113 bytes.
- SHA-256 `libturbo_carousel.so`: `9bcb311321b90deb16e96ea462a912a354dfe85b6c991a06d22b5e7474f86cd6`.
- Base exata R38: `58b337511bef62a98cae6d17982a4f139c1b0e6049def18894258d98dd5bbdfd`.
- Assinatura original e alinhamento de 16 KiB conferidos; 13.086 entradas antigas idênticas. Só o módulo do carrossel foi substituído; recursos informativos e animações foram acrescentados. Consulte `STATUS.json` para todos os hashes dos novos assets.
- **R39 instalada no Samsung em 2026-10-06T14:33:15.734937+00:00, por atualização, com SHA integral conferido.** O aplicativo abriu ESActivity/plataformas sem pedir login. Recibo: `evidence/installation-samsung-r39.json`. Conferência visual/IME/Voltar no Android, consumo, FPS e partida online não estão aprovados nesta entrega.

Corrige-se o registro anterior: R38 foi instalada no Samsung SM_A566E em 06/10/2026 às 11:51:27 UTC, por atualização e com SHA integral conferido. Consulte `evidence/installation-r38.json`. A tela de login usa proteção contra captura; não houve aprovação visual da R38. O ajuste temporário `stay_on_while_plugged_in` 0 → 3 foi restaurado e conferido em **0** após a instalação R39; recibo `evidence/samsung-temporary-awake-restored.json`.

## Pedidos implementados

### Preto/Azul, configurações e botões

O tema é selecionável nas configurações e no canto inferior esquerdo do carrossel principal. Ambas as entradas usam o Dark Mode Button indicado pelo mantenedor. `native_theme_preferences.h` lê `SharedPreferences("station_appearance")`, chave inteira `theme`, uma vez quando o ambiente JNI está disponível. Apenas uma seleção explícita grava o valor. Se a gravação falhar, a escolha anterior permanece e a tela informa o erro. Não existe consulta de preferências por quadro.

`station_theme_palette.h` e o compositor já existente aplicam Preto/Azul às superfícies escuras. Cores de função e LEDs por sistema permanecem distintas. O compositor de nuvens utiliza o cache existente, com um uniforme de tema, sem outro passe de fundo. A linha do seletor nas configurações reserva espaço sem substituir os controles ou ações dos emuladores.

Botões superiores direitos usam a mesma família visual das ações inferiores, com ícones próprios e alinhamento ao lado do texto. Foram ocultados os componentes antigos redundantes de nome do sistema/estado no topo; o nome do perfil e os botões de navegação permanecem. O nome da plataforma dentro do botão principal desloca-se três espaços **medidos pela fonte nativa** à esquerda, respeitando ícone, abreviação e limites. `station_root_label.h` é a única regra desse deslocamento.

As estrelas ficam junto do texto do botão principal de jogo (Jogar/Baixar), com espaço medido para cinco posições e preenchimento proporcional à nota real. Nome, quantidade de jogos e jogadores continuam na linha de metadados com cinco espaços medidos entre itens. Sem nota, aparece **SEM NOTA**; cinco estrelas vazias não são usadas para afirmar avaliação zero.

### Animações originais solicitadas

| Uso | Arquivo/página original | Execução |
|---|---|---|
| Preto/Azul | `dark-mode-button-NrQ5WkuReW` / [página](https://lottiefiles.com/pt/free-animation/dark-mode-button-nrQ5WkuReW) | Trecho 30–115; transição reversível, mantendo posição em toques rápidos; estático em repouso |
| Nota | [stars-G6SjCsY2cp](https://lottiefiles.com/pt/free-animation/stars-G6SjCsY2cp) | 127 quadros a 60 quadros/s de origem; uma animação de 2,1 s por seleção, depois estrela estática |
| Configurações, substitui engrenagem | [live-chatbot-umPtBW5amb](https://lottiefiles.com/pt/free-animation/live-chatbot-umPtBW5amb) | 86 quadros a 30 quadros/s; um ciclo ao pressionar, estático em repouso |
| Pequeno acima de Jogar online | [robot-playing-computer-LljdYvKKM4](https://lottiefiles.com/free-animation/robot-playing-computer-LljdYvKKM4) | 242 quadros de origem; um ciclo de 4,034 s ao mostrar a lista/pressionar; depois estático |

JSONs, contêineres `.lottie`, autoria, licença Lottie Simple e licença MIT do lottie-web constam em `assets/`. Foram renderizados no PC com lottie-web 5.13.0, preservando desenho e proporção. No chatbot/robô, o recorte remove apenas a união das margens transparentes de todos os quadros. Não remove partes animadas da arte.

Em execução, o aplicativo usa o renderer OpenGL nativo, quatro texturas pequenas e um buffer RGBA compartilhado de 384×216. Os quadros RLE estão em `.rodata`; descompactação/envio à GPU ocorre somente quando muda o quadro. Não há WebView, reprodução pela internet, timer ou thread adicional. As taxas acima são da animação, **não uma promessa de FPS medido do aplicativo**. Créditos e hashes em `evidence/lottie-*-source.json` e `lottie-render-pack.json`.

As áreas de toque e funções existentes da engrenagem e de Jogar online permanecem. O robô é decorativo; não cria uma segunda ação invisível. Os selos de instalado em todas as capas móveis e os efeitos Neo Geo/CD restritos aos jogos continuam da R38.

### Coleções e entrada na lista

`collection_editorial.h` contém 14 sinopses ampliadas de coleções identificadas por plataforma/caminho exato. “Todos os jogos” combina a descrição da plataforma, a contagem real e exemplos realmente presentes. Coleções futuras sem texto editorial próprio recebem descrição factual com nome, número de títulos e exemplos, sem atribuir características inventadas. Os textos usam buffer de 6.144 bytes e a área de rolagem existente.

Entrar numa lista nova agora zera a seleção **depois** de `rebuildVisible`, pois essa função podia restaurar um cursor antigo. Voltar continua restaurando caminho e tipo da coleção, inclusive quando o servidor insere outra pasta antes dela. Teste de regressão com o comportamento antigo falhou como esperado; a revisão passa nos mesmos cenários. As 52 sinopses de plataformas e 2.212 sinopses de jogos da base permanecem disponíveis.

## Pesquisa — duas telas, causas e correções

O mantenedor confirmou travamento aparente tanto nas plataformas quanto nos jogos. A análise foi feita sobre as funções reais de `libmain` descompiladas, com hashes no `evidence/search-diagnosis.json`; os offsets são da ABI já usada pelo carrossel.

1. **Filtro oculto ao navegar.** Quatro transições apagavam somente a string em `GuiStore+0x650`. A lista de palavras em `+0x668` e seu cache não eram apagados. `rebuildVisible` usa essas palavras, mesmo com o campo visual vazio. Cada transição agora chama `closeSearch(clear=true)` (`0x219570`) antes de trocar o modelo, que passa por `setSearchQuery` (`0x21c414`) e limpa a estrutura completa. Não limpar primeiro a string: `setSearchQuery` retorna cedo se recebe o mesmo texto.
2. **Voltar do Android com IME.** A função original `input` (`0x2354d4`) encaminhava AC_BACK por um caminho que podia deixar a busca ativa quando o teclado nativo não estava ativo. O manipulador compartilhado agora fecha a pesquisa explicitamente. O primeiro Voltar fecha o editor mantendo os resultados; o seguinte limpa o filtro; depois a navegação normal retorna à pasta. A proteção já existente contra dois callbacks do mesmo toque também cobre esse caminho.
3. **Lista vazia reprocessada em todo quadro.** `rebuildVisible` (`0x21b134`) considera uma lista vazia motivo suficiente para refazer o trabalho. A revisão conserva um resultado vazio já concluído somente se dono, catálogo, armazenamento, revisão, termo, plataforma e filtro Instalados continuarem iguais. Invalidação de navegação e mudanças reais sempre refazem a lista. Não há espera artificial entre buscas.
4. **Escopo do termo.** O ramo de busca textual original admitia correspondências antes de verificar plataforma e instalado. A filtragem após a busca agora aplica os dois campos, depois a pasta exata já existente. Os índices continuam sendo os índices originais dos jogos. Os textos são atualizados após a filtragem final.
5. **Recuperação visível.** Resultado vazio mostra “Nenhum jogo/plataforma/coleção encontrado”, com **Limpar pesquisa** e **Editar pesquisa**. O editor com teclado Android oferece **Limpar pesquisa** e **Ver resultados**. As ações chamam as mesmas funções nativas; desenho e toque compartilham retângulos. Arrasto e outro dedo não ativam um botão acidentalmente. Eventos dessa ponte são 0=pressionar, 1=mover, 2=soltar, não os códigos brutos SDL_FINGER.

`native_search_state.h`, `station_search_actions.h` e os pontos de integração em `native_carousel.cpp`, `native_folders.h`, `native_search_download.h` contêm a implementação. **Causas demonstradas no código e em testes de PC; não afirmar reprodução/correção observada no telefone antes da conferência Android.**

## Metadados: o que está pronto e o que falta

Fonte pública: [LaunchBox Games Database, Metadata.zip](https://gamesdb.launchbox-app.com/Metadata.zip), snapshot com hash em `evidence/public-metadata-source.json`. O arquivo bruto de 108 MB e a extração ficam em `G:\BAKUP SISTEMA APP 03-10-2026\metadata-publica-20261006`; não são ROMs.

- No catálogo atual de 2.212 jogos: 2.211 possuem jogadores e 2.211 possuem avaliação. São **duas lacunas diferentes**: número de jogadores do hack Mega Drive *Super Mario World* (Chuanpu/Jazz, derivado de Squirrel King) e nota de *Dragon’s Heaven (development board)* no Neo Geo. Não substituir pelo jogo homônimo de outra plataforma.
- 2.096 correspondências públicas únicas; 2.082 registros foram enriquecidos/atualizados. Médias públicas exigem votos positivos. Notas anteriores do XML sem correspondência pública conservam a origem XML, não passam a ser “média de usuários”. Traduções BR podem herdar a nota da edição base, explicitada no audit.
- 72 XMLs, 72.033 registros e 91.838 chaves únicas preparados para plataformas clássicas até Xbox 360, além dos sistemas mais recentes já existentes (3DS/Wii U/Vita/Switch). **São metadados, não 72.033 downloads publicados.** O catálogo autenticado Station continua sendo a única lista de jogos disponíveis.
- Nessa preparação futura, 46.152 registros têm ambos os campos; 15.132 não têm nota e 17.173 não têm jogadores na fonte. As ausências podem se sobrepor. O XML marca `source_missing_fields`. Não declarar a base completa “sem exceções”.
- Correspondência por plataforma + título normalizado/alias oficial único. Sem aproximação por similaridade. Normalização não transforma títulos japoneses em um título ASCII diferente. Hacks/protótipos mantêm qualificadores. As 19 equivalências revisadas do catálogo atual têm justificativa registrada.
- `station_game_details.h` atende IDs atuais; `station_future_metadata.h` atende novos títulos por busca binária exata. Chaves ordenadas pela string serializada completa, importante para `gb|` e `gba|`. Não se percorre esse índice por quadro nem se baixa XML em cada abertura.

Consulte `metadata-xml/README.md`, `data/current-metadata-audit.json`, `current-metadata-pending.json` e `metadata-coverage.json`. XMLs não contêm `path` de ROM ou URL de download. `DatabaseID` do dump não pode ser convertido por suposição em URL de página do site.

## Preservação e servidor

Frontend de perfil R37, DEX, manifesto, recursos, licenças, downloads, controles, todos os motores e salas são byte a byte os da R38. `classes35.dex` permanece R34, SHA `0db040a6b3406e744053c63467ed0f26e3582928ef5b84ecb9e360603ce870f6`. Os deltas separados `a626b50` (segundo jogador) e `11be7f3` (downloads) **não** foram incorporados. Nenhum servidor foi alterado/implantado nesta revisão. Não anunciar netplay em dupla como resolvido por mudanças decorativas.

As fontes antigas de sinopses conservam URLs históricas como procedência textual; esta revisão não as usa como chamadas de rede. APIs, catálogo e transferências continuam com a implementação já instalada na base. Toda modificação desta entrega está no APK, sem ajustes exclusivos em dados privados do telefone.

## Testes e reprodução

- 31.452 verificações de tema/layout/descrições; adaptador JNI real com API Android simulada, incluindo falha de gravação e ausência de leitura por quadro.
- 3.541 verificações da navegação nativa de pastas, seleções e atualização; 12.670 verificações de layout; 56.800 verificações da função de selo em todos os cartões móveis.
- 13.839 verificações de pesquisa/Voltar/escopo/cache/toque/nome do botão. Catálogo simulado com 40.000 registros; 10.000 quadros sem repetir a pesquisa vazia. Isso não é medição de tempo no telefone.
- 405.264 verificações dos quatro conjuntos RLE e do índice binário; 186.006 verificações XML/dados públicos. Todos os quadros RLE conferidos contra os PNGs de origem.
- GLES2/ANGLE real no PC: compilação do compositor, Preto → Azul → Preto reproduzindo os pixels originais, alfa preservado, sem erro GL. Não equivale a validação visual de toda a interface no Android.
- Compilação NDK ARM64/API26, assinatura, alinhamento e comparação integral das entradas do APK.

`recipes/restore_r39.py` restaura a linhagem R38 e aplica este delta numa **pasta nova em E:**. Verifica integralmente `SOURCE-MANIFEST.json` (nativo/frontend/salas/dependências de fonte) e `ASSET-MANIFEST.json`. Os recursos RLE congelados estão no Git: não é necessário baixar/renderizar Lotties para compilar novamente.

`recipes/build_r39.py` recompila o objeto Lottie a partir dos RLE restaurados e liga o módulo. NDK, stubs/headers baseline de W16 e objetos de mídia W16/W22 são dependências externas locais; caminhos e hashes completos em `EXTERNAL-BUILD-INPUTS.json`. A receita falha se não corresponderem. Não substituir por headers antigos com nomes iguais. Esta restauração não é uma distribuição de SDK, ROMs ou BIOS.

`recipes/test_r39.py` executa novamente os testes com os fontes restaurados. `recipes/package_r39.py` exige a base R38 pelo SHA, usa temporários em E:, preserva todos os arquivos, assina com o certificado original e recusa sobrescrever o APK existente. Os scripts em `recipes/provenance/` explicam a geração; são histórico, não devem ser reaplicados indiscriminadamente sobre fontes já modificadas.

## Próxima conferência no Android

Atualizar com a mesma assinatura, sem desinstalar/limpar dados, sem partida ou download ativo. Conferir SHA integral após instalar. Testar nas plataformas, coleções e jogos: nome existente, nome inexistente, apagar/repetir termo, teclado Android, teclado de controle, Voltar, alternância de pasta/Instalados, rotação/retorno do app. Testar Preto/Azul, reiniciar para conferir persistência, rolar sinopses, pressionar chatbot e Jogar online, observar estrelas e todos os selos móveis. Restaurar a preferência temporária do Samsung ao terminar. Registrar resultados reais e qualquer limite antes de chamar a versão de estável.
