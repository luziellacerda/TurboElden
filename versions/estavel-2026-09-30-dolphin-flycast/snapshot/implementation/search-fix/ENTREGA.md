# CONFIRMADO PELO USUÁRIO — Pesquisar corrigido

Em 30/09/2026, após instalar TurboramaStation-pesquisa-corrigida.apk, usuário respondeu "Abriu e filtrou" à solicitação de abrir a lupa das plataformas e pesquisar Nintendo. Registros nativos confirmam SEARCH opened; context=platforms; active=1; nativeKeyboard=0. Captura posterior já mostra PSP com a pesquisa fechada; não é evidência visual do filtro. Nenhum teste automatizado funcional foi executado. Evidências: implementation/search-fix/confirmation.json e user-confirmed-logcat.txt.

APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-pesquisa-corrigida.apk
SHA256: 2cf4758572b98968e4ea3835e055f746e218795c059d71060a89522fedae25e6
Fontes exatos salvos em implementation/search-fix/source. Git estável preservado; não publicado.

## Histórico anterior

# INSTALADO — correção do botão Pesquisar

Instalado em 2026-09-30T08:34:03.839999; atualização com Success e SHA256 confirmado.
APK: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-pesquisa-corrigida.apk
SHA256: 2cf4758572b98968e4ea3835e055f746e218795c059d71060a89522fedae25e6
Fontes: native_carousel.cpp e native_search_download.h.
Montagem: build_native.py e search-fix/build.py. Instalação: search-fix/install.py.
Backups anteriores: search-fix/*.before. Base preservada: TurboramaStation-pesquisa-downloads.apk.

Causa confirmada no código: topHook descartava ação 3 (Pesquisa) nas plataformas; searchHook também ignorava a abertura nesse modo. O bloqueio era anterior ao último redesenho. Agora ambas as entradas usam openSearch original. Na tela de plataformas pesquisa os nomes das plataformas; na lista de jogos mantém o filtro nativo de jogos do sistema aberto. O texto de busca deixa de ser apagado por rebuildHook nas plataformas. Retorno de um sistema aberto pela lista filtrada usa o índice real da plataforma, e reconstrução após atualização do catálogo traduz índice real para visível. Não utiliza cliques simulados nem tela Java.

Somente libturbo_carousel.so mudou. DEX, motores, mídia, login, carregamento e avisos de download permanecem idênticos à base. Instalação sem desinstalar ou limpar dados. Catálogo observado antes da atualização. Compilação e assinatura concluídas; funcionamento da busca após instalação aguarda interação do usuário, não afirmar teste funcional concluído.

Git estável estavel-2026-09-29-playlist-retro/acff0dc preservado; revisão não publicada/promovida. Integração comercial do site permanece pendente.

