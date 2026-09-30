# Alterações da versão estável — 30/09/2026

Referência anterior: `estavel-2026-09-29-playlist-retro`, commit `acff0dcd750da9f6bc51c406aa19236729ce9d70`. Promoção solicitada pelo mantenedor após “tudo ok”. O APK aprovado foi recuperado do aparelho e congelado; não foi substituído pelo candidato posterior não instalado.

## Novidades desde a referência anterior

### Interface e sessão

- Botão Abrir com destaque verde e efeitos animados internos; ações conectadas à navegação nativa existente.
- Sessão persistente protegida pelo Android Keystore para retornar da emulação sem pedir login novamente; validação de acesso preservada. Sessão inexistente ou inválida continua exigindo autenticação.
- Carregamento e menu de saída do PS2 com identidade Turborama: preto, verde e detalhes vermelhos, mantendo as funções existentes.
- Layout nativo de pausa/saída reorganizado. Barra de carregamento com marcos 0/33/66/100 ligados às etapas de inicialização, carregamento do jogo e primeiro quadro. Não representa porcentagem contínua de compilação de shaders nem usa cronômetro para simular trabalho.
- Pesquisa, teclado e avisos de download redesenhados; progressos de download usam os dados disponíveis da transferência.
- Corrigida a entrada da lupa das plataformas e a correspondência entre resultado filtrado e sistema selecionado. O usuário confirmou “Abriu e filtrou”.

### Dolphin integrado atualizado

- Motor e menus oficiais Android **2609-7**, commit `5102a0339c2177575378107b76541e47cc52122d`, incorporados no mesmo APK, processo `:dolphin`.
- Dependências e recursos isolados; integração Java/nativa compilada. Não foi uma recompilação integral do C++ do Dolphin.
- Removidos da base `libdolphin_libretro_android.so` e `assets/packs/Dolphin.zip`. O Dolphin separado já instalado no celular permanece independente e não é requisito para executar esta integração.
- Configurações oficiais, diretórios próprios, cache e preferências separados. Migração de saves nativos copia somente arquivos ausentes e preserva a origem.
- Corrigidas as falhas de realocação de tipos e de stubs Android observadas nas compilações intermediárias. Elas não são versões estáveis.
- Configurações abertas e inicialização observadas; usuário confirmou jogo Wii funcionando e retorno às plataformas sem novo login.

### Flycast integrado atualizado

- Motor e menus oficiais **v2.7-44-ge36e9df2d**, commit `e36e9df2dcc1487acdb1dc7725766f1f5ba029b5`, no processo `:flycast` do mesmo APK.
- Rotas nativas Dreamcast/Atomiswave passam ao novo motor, conforme identificadores existentes do catálogo. Não cria plataformas inventadas.
- Dependências, recursos, armazenamento e bibliotecas auxiliares isolados. A rota do core Libretro anterior foi desativada; seus arquivos baixados foram removidos somente das duas pastas de cores conhecidas. O aplicativo Flycast separado não foi alterado.
- Configurações abertas pela função oficial do Flycast. Migração de VMUs, nvmem e suporte local copia arquivos conhecidos ausentes; não sobrescreve saves. Estados rápidos e configurações Libretro antigos não são convertidos automaticamente.
- Nove arquivos de BIOS locais provisionados quando ausentes; oito foram copiados e um já existia. Nove hashes conferidos. O Git contém apenas manifesto, rotina e descrição; nenhuma BIOS.
- Proteção contra imagem Dreamcast incompleta: procura descritor/imagem compatível pelo mesmo nome e verifica trilhas referenciadas. Uma faixa `.bin` isolada não é apresentada como disco completo. O Resident Evil encontrado permanece incompleto; não foi resolvido criando descritor fictício.
- Botão nativo verde **VOLTAR AO MENU** no cabeçalho principal. Encerra a Activity do Flycast preservando a tarefa, a sessão e o contexto do catálogo da TurboramaStation. Fechar jogo pode primeiro voltar à biblioteca do Flycast; dali o botão retorna ao frontend.
- Fundo estático Turborama preto/verde com detalhes vermelhos no menu, sem adicionar vídeo ou nave animada à emulação.

### Correção do retorno que exigia vários toques

- A leitura original de botão uma vez por quadro podia perder um toque rápido cujo início e fim ocorriam entre duas leituras.
- A ponte encaminha os eventos JNI originais e, apenas no menu principal do Flycast, conserva transições de toque para o processamento nativo da interface.
- Botão responde ao pressionar, impede saída duplicada e indica **VOLTANDO...**. Durante o jogo, a entrada original é preservada.
- Dois retornos foram observados nos registros da versão instalada, em 30/09 às 10:23:01 e 10:23:12. O usuário aprovou depois com “tudo ok”. Isso não é um benchmark de latência em todos os aparelhos.
- O candidato posterior de arraste com hash `3085d9fc91648aba324a8cba677f009a67f9f82c59c2cee29a6cecef924ba030` não foi instalado e está excluído desta versão. Os fontes da integração publicados foram extraídos do APK aprovado.

## Design e comportamento anteriores preservados

- Carrossel nativo de plataformas e abertura direta das listas; catálogo completo, Baixar, Instalados e Jogar; retorno ao contexto do menu.
- Identidade verde/preto/vermelho; informações dos sistemas, células de sistemas arredondadas, jogos sem arredondamento imposto pelo tema.
- Vídeos de sistemas 720p, velocidade normal 1x e repetição; cache de quadros vizinhos; LED da célula principal com a cor do sistema.
- F-16, estrelas/nuvens e movimento diagonal aprovados; playlist retrô local. Renderização e mídias do frontend seguem a pausa existente durante emulação e retomada no retorno.
- Base histórica 1.0.8/6727ab7 preservada nos demais motores. Não foram introduzidos nesta promoção novos ajustes experimentais de velocidade, resolução ou shaders de Switch.

## Conferência e limites

- Identidade do APK instalado verificada e fontes das integrações recuperados do próprio pacote; módulo nativo confrontado com o arquivo ativo. Aprovação do usuário é a base da designação de estável.
- Sonic confirmado pelo usuário; Wii confirmado pelo usuário; configurações, menu, fundo e retorno observados. Não houve teste de todos os jogos, benchmark prolongado ou garantia de FPS.
- Permanecem sete plataformas sem vídeo próprio encontrado na pasta indicada: Atari 7800, Game Gear, Game Boy Color, Jaguar, PC Engine, PC Engine CD e SuperGrafx. Não foram inventados vídeos substitutos.
- Clone do Git não recompila sozinho o frontend original: faltam seu C++ integral e as bases binárias privadas. Scripts, integração própria, recursos revisados, licenças e hashes estão no snapshot. APK, mídias privadas, BIOS, ROMs, saves, assinatura e credenciais ficam fora do repositório.
- Licenças e referências de origem de Dolphin/Flycast são preservadas. A política do projeto não elimina direitos das licenças de terceiros.
