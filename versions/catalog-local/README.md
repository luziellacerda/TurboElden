# TurboRetroEmu 1.0.2 — catálogo local

Versão Android com senha local e snapshot de catálogo incorporado. **O usuário confirmou que o APK abriu e os jogos estão funcionando.** Essa é uma confirmação de uso relatada pelo usuário, não uma certificação de todos os itens/plataformas.

[Baixar APK e checksum](https://github.com/luziellacerda/TurboRetroEmu/releases/tag/v1.0.2-catalogo-local).

Senha provisória: `turbo123`. Pacote `org.emulationstation.frontend`; versionCode 5; Android 8/API 26+, ARM64. Assinatura técnica de desenvolvimento, igual à das builds locais anteriores.

## O que foi corrigido

A versão antiga pulava a criação da tela de licença e também o callback que abre GuiStore. Isso podia expor o erro de configuração ou uma biblioteca vazia. A versão atual mantém o fluxo original de abertura e substitui somente a etapa de entrada por senha, encaminhando a tela nativa anterior ao seu finish original. O usuário confirmou a abertura após essa correção.

O catálogo remoto depois respondeu 401 por exigir uma chave. Um snapshot foi obtido com acesso autorizado e incorporado ao APK. Somente o GET de `drawers.json` é servido pelo asset local; downloads de jogos, capas e cores continuam usando o código e os endereços originais. Não há chave de acesso ao catálogo embutida nas classes adicionadas ou no snapshot.

Os bloqueios extras de POST e consulta de IP presentes na antiga `1.0-funcoes` foram desfeitos. Telemetria e demais rotinas de rede originais permanecem nesta versão; portanto, o aplicativo não é inteiramente offline.

## Catálogo e preservação

- Snapshot de 25/09/2026: 46 grupos, 17.911 entradas de arquivos e 17.063 referências de capas. As entradas incluem jogos, vídeos e documentos; não equivalem a 17.911 jogos testados.
- JSON preservado integralmente, incluindo nomes, filtros de plataforma/visibilidade, destinos e metadados. A interface pode exibir menos itens por causa desses filtros.
- 404 das 408 entradas originais idênticas; quatro alteradas e duas adicionadas (`classes6.dex` e o catálogo).
- Todos os 164 assets originais idênticos. Sete bibliotecas nativas idênticas; somente oito bytes alterados na biblioteca principal, em dois pontos da tela de login.
- Biblioteca nativa e atividades de abertura idênticas à versão anterior cuja abertura foi confirmada.

## Testes e evidências

73 verificações Java passaram (36 de senha e 37 de catálogo). APK reaberto, assinatura v2 e alinhamento verificados. Os 29 corpos de métodos HTTP originais foram comparados, descontando o novo desvio inicial de catálogo em execute; o restante permanece intacto.

Os relatórios originais em `reports/` mantêm `RuntimeTested=false` porque foram produzidos antes do teste do usuário. A confirmação posterior está separada em `reports/user-runtime-confirmation.json`, sem inventar modelo do aparelho, nomes dos jogos ou abrangência do teste.

## Instalação

Faça backup da pasta EmulationStation, incluindo `.emulationstation`. Force a parada e instale por cima da versão local anterior, sem limpar dados. Se aparecer conflito de assinatura com o APK oficial, não desinstale sem backup. Entre com `turbo123`.

A lista é local, mas downloads e capas não armazenadas precisam de internet. Atualizar a lista nesta versão recarrega o snapshot; não busca novidades no servidor antigo. Links de terceiros podem deixar de funcionar.

## Arquivos e reprodução

`java/`, `tests/`, `LocalCatalogHook.smali`, `Build-Login.ps1` e `Verify-Login.ps1` contêm a implementação e verificações. A reprodução exige o APK original autorizado, ferramentas, snapshot com o hash indicado e o ambiente de comparação da versão anterior descrito nos scripts. Este repositório não recupera o código-fonte C++ integral do frontend.

O JSON autenticado não foi adicionado separadamente ao Git; é um insumo local de compilação e está **dentro do APK anexado à release**. O APK completo conserva componentes do original, incluindo BIOS/firmware/chaves de firmware. A publicação foi solicitada pelo mantenedor, que declarou autorização para distribuir os componentes herdados; isso não concede novas licenças sobre material de terceiros.

Nenhuma chave de acesso de usuário, token GitHub ou keystore foi incluído. Esta publicação contém somente o trabalho relacionado ao APK. A análise original na main e a versão histórica em `versions/functional` são preservadas.

SHA-256 do APK: `21E6045F69457A05ECBFA6495507C14BC00483C4ADCB490FE4C6D7DFCF90B15D`.
