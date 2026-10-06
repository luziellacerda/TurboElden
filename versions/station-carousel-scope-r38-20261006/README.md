# R38 — carrossel, coleções e selos de instalado

## Entrega e estado comprovado

APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Carrossel-R38-20261006.apk`. SHA-256 `58b337511bef62a98cae6d17982a4f139c1b0e6049def18894258d98dd5bbdfd`, 2054649656 bytes. Pacote `org.turboramastation.frontend`, classes Java `org.emulationstation.frontend`. Compilado e conferido no PC. **Instalação posterior confirmada no Samsung às 11:51:27 UTC de 06/10/2026, SHA integral igual ao APK; recibo em evidence/installation-samsung-20261006.json.** Conferência visual pendente; não declarar estabilidade geral nem teste online em dupla.

Fonte final: `E:\ESTUDO APK\work\station-carousel-scope-r38-20261006`. Compilação e temporários em E:, APK final em G:. Atualizar sem desinstalar nem apagar dados. Nenhuma alteração exclusiva no telefone e nenhum servidor modificado.

## Pedidos e causas confirmadas

1. **Efeito dentro dos jogos de Neo Geo e Neo Geo CD.** O desenho do vídeo possuía uma substituição explícita pelo programa `useNeoSquareProgram` quando a célula focada usava `720-neogeocd.mp4`. Ela também atingia a prévia estática. A chamada e o include foram removidos; os dois shaders quadrados não pertencem mais ao conjunto final de fontes. Vídeo e prévia agora usam os mesmos programas normais das demais plataformas. O LED externo de foco, as cores, o vídeo, a velocidade e o cache permanecem iguais.
2. O efeito de revista dos jogos continua em `native_magazine.h`, com mapa 3 para as duas famílias. A condição agora exclui expressamente plataformas **e coleções**. `magazine_shader.h` e sua máscara de pixels permanecem exatos da R37: reconhecem a moldura original, preservam as cores da arte e animam os emissores. Capas comuns sem essa moldura não recebem lâmpadas em posições inventadas. Não ligar esse shader aos vídeos novamente.
3. **Coleções: botão ABRIR com a largura exata da célula principal.** `stationCollectionAction` retorna x e largura do cartão, sem a redução antiga para 52% e sem o desconto de 12%. Voltar fica à direita com intervalo de 24% da altura do botão; largura de Voltar é três vezes sua altura. A mesma função fornece retângulos de desenho, texto e toque. O texto vem do nome real da coleção selecionada: `ABRIR Todos os jogos`, `ABRIR Coleção…` etc. A fonte é medida pelo renderer nativo; nomes longos terminam com reticências UTF-8 em uma linha. O nome não se repete fora do botão. Rotas, retorno à seleção e filtros não foram alterados.
4. **Selo em toda capa instalada visível, inclusive durante movimento.** A R37 consultava só o índice selecionado e escondia a faixa quando a distância animada passava de 0,30. A R38 consulta o índice real de cada cartão desenhado e o byte instalado em `item+0xa8`. `coverFormationHook` chama `drawInstalledCover(p,index,r)` imediatamente após a capa, na mesma ordem de pintura. A geometria e o texto usam a posição e a escala do cartão em cada quadro. Não depende da seleção ou da parada. Filtros e buscas continuam mapeando o índice correto; desinstalar remove o selo na próxima renderização. Plataformas/coleções/modal não recebem selo.
5. A faixa reaproveita a malha verde R37 e seu relógio existente. Um componente de texto por GuiStore, medido apenas quando muda o tamanho de referência; miniaturas usam a matriz de escala. Não cria textos por jogo, timer, thread, vídeo ou download. Trabalho limitado aos cartões visíveis, não ao catálogo inteiro. Sem alegar FPS/consumo medidos no Android.
6. **52 sinopses dos sistemas ampliadas em português**, incluindo aliases BR, preservando exatamente as 52 chaves existentes. Textos com ao menos 723 caracteres, parágrafos completos e descrição histórica/editorial. `system_infos.h` local sobrepõe o header antigo da dependência W16. A correspondência ignora caixa/espaço final; o catálogo não é renomeado. Model 2 deixa de ter texto vazio; textos cortados antigos são substituídos. Escopo apenas informativo, não promete que todo jogo citado está publicado ou que recursos do hardware original existem no emulador. Dados/proveniência em `data/`. Recorte das 2.212 sinopses de jogos R37 intacto. Área recortada e barra de rolagem continuam iguais.

## Preservação

Base exata R37: `75fd8b5806c6aa683796e1301fa8a92e3236f106a8837a0279b6d0ae094999fc`. Somente `lib/arm64-v8a/libturbo_carousel.so` mudou; **13086 entradas preservadas** verificadas por hash. Novo SO `4a581bea9f260354f645efca30a4722e4823d89814cfb08000d1e4da65f2c95e`. Frontend/perfil R37, todos os DEX, manifesto, recursos, emuladores, controles, salas, autenticação, downloads e licenças mantidos.

`classes35.dex` R34: `0db040a6b3406e744053c63467ed0f26e3582928ef5b84ecb9e360603ce870f6`. Retorno de segundo jogador a626b50 e delta de downloads11be7f3 continuam **separados**, não foram integrados nesta revisão visual. Certificado original e alinhamento16KiB conferidos.

## Testes realizados

- 56.800 verificações executando a função real do selo com funções gráficas simuladas: índices filtrados, 80 quadros de movimento, nove posições, instalado/não instalado, remoção, modais e uma única medição de texto por tamanho.
- 12.880 verificações de layout: largura exata da capa, Voltar separado, limites de tela em sete proporções/seis resoluções, metadados, botões dos jogos, rolagem e Lottie preservados.
- 15 contratos de integração: caminho normal dos vídeos, dois sistemas Neo, gating, máscaras intactas, escopo dos selos, sinopses, nome da coleção e rolagem.
- GLES2/ANGLE real no PC: compilação do shader e mudança de pixels ao longo do tempo em duas capas Neo Geo de referência; o mesmo mapa é selecionado para Neo Geo CD. Não equivale a medição do decodificador Android nem inspeção de todas as artes do servidor.
- Compilação Android ARM64/API26, assinatura original, alinhamento16KiB e comparação de todas as entradas do APK.

## Restaurar e compilar sem misturar versões

Execute `recipes/restore_r38.py` com uma pasta **nova em E:**. A receita restaura R37 integral, remove apenas dois shaders quadrados listados em `REMOVED-SOURCES.json`, aplica o delta e confere todos os hashes de `SOURCE-MANIFEST.json` (native/frontend/netplay/dependências).

Para reproduzir o binário no caminho canônico, consulte `evidence/native-build-input.json` e `recipes/build_r38.py`. Dois objetos de mídia devem ser ligados exatamente uma vez: W16 `video720_posters.o` e W22 `neogeo_previews.o`; includes/stubs de ligação são W16. Não copiar o header antigo `native_formation.h` por cima da R38: ele contém o ponto de desenho de cada selo. `system_infos.h` também deve vir do overlay R38.

`recipes/package_r38.py` exige o SHA completo da R37 e recusa sobrescrever um candidato. Mantém todos os arquivos, substitui apenas o carrossel, assina e compara o pacote inteiro. Não usar empacotadores antigos que troquem frontend/DEX sem necessidade. Os scripts editoriais/preparação são proveniência; para restaurar as fontes prontas use a receita de restauração, não reaplique modificações sobre arquivos já alterados.

## Conferência pendente no aparelho

1. Sem jogo ou download ativo, atualizar com `adb install --no-incremental -r --user 0` e conferir SHA integral do base.apk. Não desinstalar nem limpar dados.
2. Neo Geo CD no principal: vídeo normal, só LED externo do foco. Entrar nos jogos de Neo Geo/CD: efeito na moldura das revistas reconhecidas.
3. Abrir coleções SNES/Mega: botão do tamanho da capa com ABRIR + nome, Voltar separado, toque abre a coleção correta e retorno mantém seleção.
4. Jogos: todos os instalados visíveis marcados; arrastar nos dois sentidos e confirmar selo acompanha cada capa sem aparecer em títulos não instalados.
5. Ler sinopse de plataforma longa, rolar até o final e confirmar que texto não cobre cartões ou botões. Verificar nome do perfil e retorno sem login.
6. Registrar capturas e recibo; qualquer ajuste temporário de tela ligada deve ser restaurado ao valor original.
