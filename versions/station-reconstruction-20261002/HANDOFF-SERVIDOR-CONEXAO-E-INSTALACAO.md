# Handoff do servidor para concluir a conexão do TurboStations Android

## Verificacao no aparelho em 03/10/2026, 10:07 - carregamento corrigido

APK atual `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, SHA256 `43670211fe6de01438c0352b44875c43336c052d431582032680fa2c9265517f`, 1.902.702.486 bytes. Instalado com atualizacao -r, hash do base.apk identico, lastUpdateTime 10:07:58. Licenca salva reutilizada sem redigitar o codigo. Nao promovido a estavel.

Causa observada do loading: `StationFrontend.configure` recusava `Symbolic path refused`. Raizes confiaveis do contexto Android e do diretorio nativo agora passam por `toRealPath` antes dos controles de descendentes. O root nativo nao mudou na canonicalizacao; a raiz privada do Android deixou de provocar a recusa. Links simbolicos dentro da instalacao continuam rejeitados. Quatro testes Android isolados confirmaram raiz canonica, criacao normal, recusa de redirecionamento e ausencia de escrita fora da pasta; 204 testes locais passaram.

O aparelho publicou e aplicou 996 itens, chegou a 100% e abriu as plataformas. A barra apresenta itens e bytes UTF-8 preparados para a interface, nao bytes transferidos pela rede. Corrigida a visibilidade dos TextComponents para o texto nao ficar sobre o carrossel depois da conclusao. Captura final conferida. Tela ligada durante a carga restaurada ao valor anterior 0.

Contagem divergente relatada pelo mantenedor: espera mais de 800 SNES, mas existem 176 SNES e 28 SNES BR no catalogo recebido. As oito contagens no telefone coincidem exatamente com o handoff servidor ac869429 (996 total). Isso nao e corte do filtro SNES no cliente. Pedir catalogo completo ao servidor pelo novo handoff `docs/server/HANDOFF-SERVIDOR-CATALOGO-INCOMPLETO-STATION-20261003.md`. Nao preencher a lista com catalogo/CDN antigo nem inventar itemId/coverId.

Continuam pendentes: capa autenticada 200, descritor implantado e transferencia real, importacao verificavel dos jogos anteriores e eliminacao fisica do legado nativo residual. Inventario de dominios e evidencia estatica, nao captura de trafego. Fonte novo usa app.lzgames.com.br/v1/station; strings antigas ainda existem nas bibliotecas preservadas. Nao alegar migracao integral concluida.

Os registros abaixo sao historicos e nao substituem esta verificacao.

## Atualizacao posterior em 03/10/2026 - ativacao e carregamento

Codigo localizado no retorno privado `docs/senha-station-48h-20261002`, commit `01c391bea72dc27de8597e0c6d908caa96b18021`, arquivo `RETORNO-SENHA-STATION-48H-20261002.md`. O valor nao foi copiado para este handoff nem para logs. A pedido do mantenedor, foi inserido pela UI do telefone; o controlador concluiu o login e abriu ESActivity. O catalogo nativo permaneceu no indicador giratorio: ativacao aceita NAO significa frontend pronto.

Foi corrigida a publicacao pendente para usar o vetor que o GuiStore realmente observa. Foi adicionada barra desenhada no renderer nativo, com contagem de itens preparados e bytes UTF-8 preparados para a interface. A animacao e limitada ao trabalho concluido, e 100% depende do commit do modelo. Nao e percentual por tempo nem contagem de bytes baixados de jogos. Falhas mostram estado interrompido e diagnostico de etapa. Ainda falta confirmar visualmente o resultado no aparelho desbloqueado e fechar a causa do bloqueio inicial; nao declarar corrigido so pela compilacao.

Candidato instalado: `ae78dab6ab0eebda5ab872c6be4d2e293237010a65f02c4c3cbc1eaa064cc13e`, mesmo caminho de saida, 1.902.702.486 bytes, lastUpdateTime Android `2026-10-03 09:36:34`. Instalador retornou Success; hash no telefone desta revisao conferido e identico ao APK gerado. Tela permanece bloqueada; validacao visual pendente. O candidato anterior 38e78fde saiu do login mas ficou no loading. Sao agora 32 entradas nativas substituidas. Testes: 204 locais, 28 nativos do frontend; carga ELF com consulta do simbolo da pasta passou. Codigo e licenca do telefone foram preservados.

Novo retorno do servidor lido: `43bb54847e55750be451b614bcf827fb32ad7de4`, mesmo ramo `feat/station-artifact-descriptor-20261002` e mesmo handoff tecnico unico. Acrescenta homologacao HTTP isolada e correcao `de08858eac95084c116f146b642acd8748b43c35` na ordem de consumo do grant. Continua declarando descriptor NAO implantado e capas reais pendentes. Nao alterar a 5192 como consequencia desta leitura.

## Integracao do APK em 03/10/2026 - estado mais recente

Candidato completo gerado: `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, 1.902.702.486 bytes, SHA256 `38e78fde7dce574969aadeab2cd709b32df12b94bcd819fe595bd079af8204d2`. Nao e versao estavel. Instalacao e validacao autenticada devem ser confirmadas pelo registro de aparelho mais recente; a geracao do pacote nao comprova login real.

Instalacao Android concluida em 03/10/2026, lastUpdateTime 09:18:57. SHA256 do base.apk instalado conferido: 38e78fde7dce574969aadeab2cd709b32df12b94bcd819fe595bd079af8204d2. LoginActivity abriu sem falha no buffer de crashes consultado. Usuario foi solicitado a digitar o codigo diretamente no aparelho. Ativacao real ainda aguarda resultado.

### Aplicativo efetivamente integrado

- Quatro DEX substituidos: classes5 (ciclo de vida/servico), classes6 (autorizacao SDL), classes8 (retirada do auth/catalog antigo), classes28 (cliente Station novo no lugar de GameDownload). LocalPassword, AuthSession, LocalCatalog, HttpBridge, StationTransfer e GameDownload antigos foram removidos, incluindo referencias de tipos nos DEX. Nenhuma classe nova duplicada.
- `libstation_frontend.so` conecta o CatalogService nativo aos comandos por itemId do cliente Station. Nao fabrica URL e nao intercepta cliques. `libstation_archive.so` instala ZIP/RAR/7z usando libarchive. Sessao, perfil, catalogo, capas e grants usam exclusivamente as rotas Station no cliente reconstruido.
- `libmain.so` teve 31 implementacoes de entrada de servicos substituidas por ligacoes ao fonte novo. Os 4.409 enderecos dos simbolos originais foram mantidos porque o renderer/carrossel depende desse layout. Isto e integracao binaria verificavel; NAO significa que o C++ completo original foi recuperado ou recompilado.
- Restam rotinas antigas sem uso demonstrado no frontend atual dentro do binario nativo (incluindo scrapers historicos e ponte HTTP). As entradas ativas de catalogo/licenca/telemetria foram substituidas, mas a eliminacao fisica integral de todo o legado nativo ainda nao foi concluida. Nao apresentar essa entrega como reescrita integral limpa.
- Removido `assets/turboretro/catalog.json`. Nao existe retorno automatico ao catalogo antigo se o servidor falhar. Recursos de design, motores, demais DEX e manifesto foram preservados; 10.803 entradas comparadas por SHA256. Assinatura igual a base, alinhamento 16 KiB verificado.
- Historico de uso local preservado; sem consulta de IP ou telemetria remota antiga. Downloads usam servico em primeiro plano apenas enquanto ativos, fila limitada e eventos. Capas persistem por ID/revisao; trabalho de capas e suspenso quando a interface fica oculta.

### Evidencias e limites

204 verificacoes locais (19 arquivos, 68 protocolo, 36 cache/sessao, 20 coordenacao, 61 instalacao). No Android: 26 verificacoes sinteticas da ponte nativa; oito de leitura segura de arquivos; carregamento ELF e compatibilidade ABI aprovados. `build/apk/apk-report.json`, `build/device-integration-results.json` e `build/test-results.json` registram as evidencias. Isso nao substitui ativacao, capa 200, download real e retorno de um jogo.

Jogos e saves anteriores nao sao apagados. Jogos antigos fora de `.station-v2` ainda nao sao importados para os novos recibos: falta correspondencia verificavel entre IDs do servidor e arquivos existentes. Nao associar por aproximacao de nome nem indicar tudo como instalado. Geracoes antigas de uma atualizacao bem-sucedida sao preservadas; limpeza controlada de versoes substituidas ainda e pendente. Remocao interrompida agora usa recibo com `removing=true`, permitindo repetir a operacao sem declarar instalacao valida.

### Responsabilidades do servidor (Servidor-pix, somente canal Station)

Ultimo retorno lido: `feat/station-artifact-descriptor-20261002`, `9c0d9d5dab83ad1037009e5150fb4174fcddcbd6`, arquivo `docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md`. Contrato implementado em `96326aa0aeb164820cec26f8b5911fcdb47fc8ee` e `1bfb619c21becffe40aaa597e100fcb3719c2e72`. Nao assumir implantacao porque o servidor foi religado. Comprovar descriptor assinado em producao e arquivos do indice, capa autenticada 200 e transferencia integral. O cliente recusa grant sem artifact/itemRevision e nunca volta ao CDN antigo.

`STA-` e prefixo de licenseId. O codigo de ativacao e Base64URL canonico de 32 bytes (43 caracteres). O usuario possui o codigo e o digitara no telefone; nao solicitar segredo pelo chat. Nome vem de /me. Nenhum servico Linux foi alterado.

### Receita exata, executada na raiz E:

1. `prepare_test_dependency.py`, `run_tests.py`, `build_module.py`.
2. `build_archive.py`, `build_frontend.py` (JDK17, SDK34, NDK r28c nos caminhos dos scripts; bibliotecas oficiais verificadas por hash).
3. `prepare_dex_input.py`: extrai/descompila DEX da base d8104343, nunca da arvore Java realocada obsoleta.
4. `link_native_services.py` (requer LIEF apenas para leitura/metadados), `build_app_dex.py`, `package_apk.py`.
5. Rodar fixtures nativas no Android; instalar apenas o candidato com assinatura igual usando atualizacao -r. Nao desinstalar, limpar dados ou sobrescrever o APK de entrada/estavel.

Raiz canonica: `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`. Base: `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk` (d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b). Git: TurboElden, ramo `station-reconstrucao-20261002`, pasta `versions/station-reconstruction-20261002`. Nao mover referencias estaveis nem publicar APK, ROM, BIOS, firmware ou credenciais no Git.

As secoes abaixo sao historicas. Onde disserem modulo isolado, 142/202 testes ou APK ainda nao gerado, prevalece este registro.

## Atualização confirmada em 03/10/2026 — prevalece sobre o estado histórico abaixo

Retorno lido: Servidor-pix `feat/station-artifact-descriptor-20261002`, commit `9c0d9d5dab83ad1037009e5150fb4174fcddcbd6`. Código do contrato: `96326aa0aeb164820cec26f8b5911fcdb47fc8ee` e `1bfb619c21becffe40aaa597e100fcb3719c2e72`.

- Correção da interpretação anterior: `STA-` identifica **licenseId**. O código digitado pelo comprador é Base64URL canônico de 32 bytes (43 caracteres). `StationApi.token(code)` já estava correto; não flexibilizar a validação por causa do texto antigo.
- `itemRevision` e `artifact` são agora contrato confirmado no código do servidor, com fileName, sizeBytes, sha256, format, launchPath, expandedSizeBytes e fileCount. A implantação e o índice de produção continuam pendentes no último retorno.
- Fontes locais consomem o descritor assinado, validam SHA256 antes de extrair e publicam um manifesto somente após instalação completa. ZIP, RAR e 7z usam libarchive nativa. O catálogo nativo e o APK integrado ainda não estão concluídos.
- Última execução local: 202 verificações passaram e os fontes compilaram para Android API 34. Leitor nativo Android: oito verificações sintéticas passaram (ZIP, 7z, RAR5 e recusas de arquivos inseguros/cancelamento). Isso não comprova download autenticado de produção.
- Consulta pública após o usuário informar reinício: `/v1/station/catalog` retornou 401 JSON `STATION_SESSION_INVALID`, sem credenciais. `/ready/station` no domínio público retornou HTML do portal; não usar esse 200 como prontidão da API. O handoff usa essa sonda apenas localmente no servidor.
- Nenhum APK instalado nem serviço Linux alterado nesta implementação. Ainda é necessário retirar os fluxos antigos, integrar a interface e testar com sessão real antes de liberar.

O restante é o registro histórico de 02/10/2026; propostas e pendências antigas devem ser confrontadas com esta atualização.


## Destinatário e identificação exata

Este pedido é para a equipe ou IA responsável pelo **backend Station no repositório Servidor-pix**. Implementar e comprovar as pendências do servidor descritas abaixo e devolver o contrato final para a equipe do aplicativo.

| Identificação | Valor conferido |
| --- | --- |
| Repositório do servidor | https://github.com/luziellacerda/Servidor-pix |
| Arquivo deste pedido | docs/station-android/HANDOFF-CLIENTE-RECONSTRUIDO-STATION-20261002.md |
| Branch deste documento | docs/cliente-reconstruido-station-20261002 |
| Aplicativo atendido | TurboStations Android TESTE |
| Pacote Android | org.turboramastation.frontend |
| productId e applicationId do protocolo | TURBORAMA_STATION_ANDROID, em ambos os campos |
| Base HTTPS configurada no cliente | https://app.lzgames.com.br |
| Prefixo das rotas | /v1/station/ |
| Serviço descrito pelo handoff do servidor | turborama-station-api, loopback 127.0.0.1:5192; confirmar no ambiente antes de qualquer implantação |
| Código do aplicativo analisado | TurboElden 0840028854034b03e5a1d3f2a162d66225932a6b, versions/station-reconstruction-20261002 |

A entrega deste pedido é código/contrato/evidência do canal Station. O escopo exclui os outros produtos Turborama, Suite Windows, PIX, seus serviços e dados. As pastas E: citadas neste documento identificam o trabalho Windows do aplicativo; não são destinos de implantação Linux. Esta revisão é documental e não autoriza reiniciar ou implantar serviços.

## Ordem de execução e responsáveis

1. **Servidor — confirmar a base.** Ler AGENTS.md desta pasta e o HANDOFF-HUMANO-COMPLETO-STATION-20261002.md. Conferir código efetivo, índice carregado e versão em execução. Os commits abaixo são as referências já examinadas, não prova do estado atual do Linux. Registrar diferenças encontradas.
2. **Servidor — confirmar a ativação e o perfil.** Devolver o formato real do código emitido ao comprador, o contrato dos desafios/sessões e o campo do nome em /me. Conferir a divergência específica de ativação registrada abaixo. Preservar as regras comerciais já estabelecidas.
3. **Servidor — reparar e comprovar as capas.** Resolver coverId para o arquivo do índice carregado. Entregar resultado autenticado 200 e validar a regra de revisão/cache; a existência da rota não encerra esta tarefa.
4. **Servidor — implementar ou confirmar o descritor do jogo.** Usar a seção de extensão proposta como requisitos a fechar. Devolver os nomes finais, tipos, limites, assinatura, erros e exemplos. Metadados devem corresponder exatamente aos bytes autorizados.
5. **Servidor — comprovar o fluxo completo.** Executar os casos da seção de evidências e informar separadamente o resultado local/homologação e o resultado de produção, caso exista. Publicar o retorno no arquivo indicado ao final.
6. **Aplicativo — depois do contrato confirmado.** Corrigir a validação de ativação, ligar o catálogo ao carrossel nativo, implementar o instalador, retirar os fluxos antigos do APK e verificar no aparelho. Essas tarefas continuam sendo responsabilidade da equipe Android.

Se faltar um dado, registrar qual campo, arquivo ou evidência falta. Não preencher com valor inventado, extensão genérica, rota vazia ou exemplo tratado como configuração real.

## Divergência de ativação que precisa constar no retorno

O handoff humano do servidor descreve códigos com prefixo STA-. O cliente publicado em 0840028 chama token(code) em StationApi.activate, que exige Base64URL canônico de 32 bytes. Esses formatos não são equivalentes; um código STA- no formato documentado pode ser rejeitado pelo cliente antes da requisição.

No servidor b1159c9, CompleteActivationAsync lê activationCode com RequireString e máximo de 256 caracteres; essa validação não exige o formato Base64URL usado pelo cliente. O retorno deve confirmar o formato emitido e as regras de espaços, maiúsculas e prefixo, usando exemplos sintéticos e indicando o código responsável. A correção correspondente é no cliente Android para obedecer ao contrato real; não alterar códigos já emitidos para acomodar a validação incorreta do cliente.

As 142 verificações locais anteriores não comprovam a aceitação do código comercial STA-. Essa divergência permanece pendente nesta revisão documental.

## Objetivo e estado comprovado

Destinatário: manutenção do Servidor-pix. Objetivo: fechar os dados necessários para o TurboStations baixar e abrir jogos usando exclusivamente `/v1/station/*`, com licença do comprador e sem divulgar o armazenamento interno.

O aplicativo possui agora um cliente independente escrito em Java e compilado para Android. Ele segue o código de `StationService.cs`, `StationEndpoints.cs` e `StationLibrary.cs` no commit `b1159c9`. O cliente ainda não foi integrado ao APK e não é uma versão liberada ao consumidor.

A leitura realizada na etapa anterior, em 02/10/2026, usou `07b4cab` como referência da auditoria de produção. Esta revisão documental não executou uma nova auditoria do ambiente. Essa auditoria informa falhas 404 nas capas e não comprova uma transferência completa de jogo. Este documento não solicita alterar serviços de outros produtos nem reiniciar a API antes de validar as alterações.

## Rotas existentes consumidas pelo cliente

| Método e rota | Dados e validações usados pelo cliente |
| --- | --- |
| POST `/v1/station/activations/challenge` | Identidade do aparelho, código de ativação e chave pública; resposta assinada vinculada ao aparelho; validade de 60 s |
| POST `/v1/station/activations/complete` | Prova RSA PSS com challengeId e nonce; licença devolvida deve corresponder ao challenge |
| POST `/v1/station/challenges` | Licença e identidade; challenge com a mesma licença e aparelho |
| POST `/v1/station/sessions` | Prova do aparelho; sessão assinada com validade de 180 s |
| GET `/v1/station/me` | Nome do comprador e versão do perfil; licença, aparelho e sessionId conferidos |
| GET `/v1/station/catalog` | Catálogo assinado, até 4096 itens, campos itemId, name, platform, revision e coverId |
| GET `/v1/station/covers/{coverId}` | Sessão válida; bytes da imagem, até 5 MiB; arquivo mantido no cache local por ID e revisão |
| POST `/v1/station/downloads/authorize` | itemId e identidade; concessão assinada vinculada ao item, licença, aparelho e sessão; validade de 60 s |
| GET `/v1/station/artifacts/{grantId}` | Uma tentativa por concessão; transferência sequencial, Content-Length obrigatório, sem redirects e sem Range |

Nenhum bearer ou grant é gravado em disco pelo cliente novo. O cliente reutiliza o alias de chave Android Keystore e o identificador de licença já presentes na instalação. MAC e IMEI não fazem parte do protocolo. As respostas assinadas são validadas contra a autoridade pública Station já configurada; os pins não foram trocados nesta reconstrução.

## Lacuna confirmada no artefato

Em `AuthorizeDownloadAsync`, a resposta assinada atual termina em itemId, grantId e expiresInSeconds. Em `ConsumeArtifactPathAsync` e no endpoint de bytes, o caminho permanece privado. O endpoint transmite `application/octet-stream` e Content-Length, sem Content-Disposition, extensão, hash ou seleção do arquivo inicial.

Isso permite transportar bytes, mas não informa ao instalador se são ROM crua, ISO, ZIP, RAR, 7z ou outro contêiner. Um arquivo compactado pode conter múltiplos BIN/CUE, diretórios de Wii U ou mais de um executável. O cliente não deve fabricar `.zip` nem escolher o primeiro arquivo encontrado.

## Extensão proposta para confirmação

**Esta seção é uma proposta ainda ausente no servidor e ainda não consumida pelo cliente compilado.** Confirmar o contrato antes de ligar o instalador. Manter as rotas atuais e acrescentar à resposta assinada de autorização:

| Campo proposto | Significado obrigatório |
| --- | --- |
| `artifact.fileName` | Nome base real do arquivo servido, com extensão; sem caminhos, separadores, NUL ou componentes `.` e `..` |
| `artifact.sizeBytes` | Tamanho inteiro positivo exato dos bytes que serão transmitidos |
| `artifact.sha256` | SHA256 desses mesmos bytes, em 64 caracteres hexadecimais minúsculos |
| `artifact.format` | `raw`, `zip`, `rar` ou `7z`, conforme artefato real; não inferido pela plataforma |
| `artifact.launchPath` | Para raw, o próprio fileName; para arquivo compactado, caminho relativo exato do jogo inicial após extração, sem escapar da pasta do item |
| `artifact.expandedSizeBytes` | Para compactados, limite conhecido do tamanho total extraído; para raw, igual a sizeBytes |
| `artifact.fileCount` | Número de arquivos regulares esperados; raw usa 1 |
| `itemRevision` | Revisão do item autorizada, correspondente ao catálogo entregue |

Não enviar URL do CDN, caminho Linux, credencial ou segredo. O aplicativo verificará assinatura, item e revisão, confrontará o tamanho com o cabeçalho, validará SHA256 antes da instalação e verificará o formato dos bytes. A publicação como instalado ocorrerá somente depois da extração segura e confirmação do launchPath.

O servidor deve obter esses dados do índice/arquivo efetivamente autorizado. Calcular hashes e inspecionar contêineres na preparação do índice, evitando recalcular arquivos grandes a cada clique do comprador. O artefato concedido deve permanecer imutável durante sua validade, ou o servidor deve rejeitar a concessão quando sua identidade mudar. Não servir bytes diferentes com o mesmo descritor assinado.

O servidor pode propor outro esquema equivalente. Nesse caso, devolver os nomes e regras exatos, exemplos sanitizados e a revisão do código. O aplicativo ainda não inventa esses campos como se já existissem.

## Capas e revisão

Restaurar a correspondência entre coverId e coverPath do índice efetivamente carregado pela 5192. Demonstrar pelo menos uma resposta autenticada 200 com MIME e bytes corretos, além do 404 para um ID inexistente. O cache do cliente mantém as capas já baixadas; trocar o conteúdo de uma capa requer nova revisão ou novo coverId para que o telefone saiba renová-la.

Confirmar também se a revisão de capa é a revisão do item, como foi adotado nos handoffs anteriores. Caso dois itens compartilhem coverId com revisões diferentes, documentar qual revisão é a autoridade. A API atual não traz coverRevision separado.

## Plataformas e jogos já instalados

O catálogo documentado em ac86942 usa megadrive, snes, snesbr, gamegear, gb, sega32x, gbc e gba. Esses oito identificadores foram mapeados a pastas observadas no aplicativo. Foram preservadas, por exemplo, `super-nintendo--br`, `megadrive--br` e `nintendo-64--br`, com dois hífens.

Antes de publicar outras plataformas, devolver a lista exata dos valores de `platform`, distinguindo edições BR. Não assumir que o nome de exibição é caminho de pasta. O cliente possui 50 mapeamentos locais comprovados, mas não inventará equivalência para identificadores novos. O servidor atualmente limita o índice a 4096 itens; a lista documental de 12346 jogos não cabe nesse limite sem uma evolução explícita do contrato.

## Evidências necessárias para o retorno

1. Commit e branch com o contrato confirmado do descritor; documentar tipos, limites e códigos de erro.
2. Catálogo autenticado de teste com revisão, quantidade e valores de platform, sem tokens no handoff.
3. Uma capa válida 200 e um coverId inexistente 404.
4. Autorização de um artefato de teste permitido, resposta assinada com metadados e transferência completa cujo tamanho/hash confiram.
5. Segunda utilização da mesma concessão negada; concessão expirada negada; licença bloqueada negada; sessão de outro aparelho negada.
6. Comportamento documentado quando a conexão cai após consumir a concessão. O cliente solicitará nova autorização para reiniciar; não retomará um grant já usado.
7. Exemplos para uma ROM crua, um contêiner com múltiplos arquivos e um jogo de Wii U com diretórios. Informar o arquivo inicial de cada um.

Não usar `/ready/station` 200 como prova de que catálogo, capa e jogo funcionam. Essa prontidão confirma um conjunto menor de condições.

## Arquivos entregues pelo aplicativo

- Raiz da reconstrução: `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`.
- Fonte do protocolo: `src\java\org\emulationstation\frontend\station\StationApi.java`.
- Biblioteca compilada: `build\station-client.aar`.
- Testes e hashes: `build\test-results.json` e `build\module-manifest.json`.
- Continuação do aplicativo: `HANDOFF-RECONSTRUCAO-TURBOSTATIONS.md`.

Foram concluídas 142 verificações locais, incluindo a integração do login nos fontes, e a geração do módulo Android. Ainda faltam a integração com a interface nativa, a instalação orientada pelos metadados confirmados e a verificação autenticada no aparelho. Este handoff não declara o APK como estável.

## Retorno publicado do aplicativo

A integração do login nos fontes foi publicada em TurboElden, commit `0840028854034b03e5a1d3f2a162d66225932a6b`, ramo `station-reconstrucao-20261002`.

[Fontes, testes e documentação da integração](https://github.com/luziellacerda/TurboElden/tree/0840028854034b03e5a1d3f2a162d66225932a6b/versions/station-reconstruction-20261002).

O layout de login atual passou a usar StationCoordinator para sessão, perfil e catálogo, com capas por itemId. A senha local foi retirada desses fontes. O controlador invalida a autorização quando o servidor nega a licença, reaproveita a licença salva e o cache verificável, e cancela consultas quando a tela de login fica escondida.

A etapa passou em **142 verificações locais**, com compilação Android e geração de DEX. Os exemplos são testes sintéticos, não credenciais de produção. A ligação ao catálogo nativo, o instalador orientado pelo descritor e o APK completo continuam pendentes; nenhum APK desta reconstrução foi instalado ou promovido a estável. A proposta de metadados acima permanece aguardando confirmação/implementação do servidor.

## Arquivo obrigatório de retorno do servidor

Publicar no repositório Servidor-pix:

docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md

Se esse arquivo já existir, atualizá-lo preservando evidências anteriores identificadas por data. Entregar à equipe Android o link com commit completo e informar a branch. O documento deve apontar explicitamente para este pedido e para o commit do cliente analisado.

Preencher todos os itens abaixo com evidência ou com a pendência exata:

| Item obrigatório | Conteúdo esperado |
| --- | --- |
| Revisões | Branch e SHA completo do código alterado, do contrato e dos testes; informar se houve implantação |
| Ambiente | Data, ambiente testado, serviço efetivo e hash do artefato em execução; separar desenvolvimento de produção |
| Ativação | Formato emitido ao comprador, normalização permitida, validação real e exemplo sintético |
| Perfil | Nome exato do campo do comprador, assinatura e comportamento quando o perfil ainda não estiver pronto |
| Contrato | Rotas, métodos, schemas e nomes finais dos campos; tipos, limites, códigos de erro e versão de assinatura |
| Capas | Resultado autenticado 200 e 404, tamanho/MIME/hash de exemplo permitido, regra de revisão e invalidação do cache |
| Catálogo | Revisão, total, valores exatos de platform e solução explícita caso exceda 4096 itens |
| Artefatos | Descritores sanitizados de raw, arquivo com múltiplos membros e diretórios Wii U; launchPath de cada exemplo |
| Transferência | Tamanho e SHA256 esperado/obtido; concessão usada, expirada, bloqueio e queda de conexão |
| Compatibilidade | O que continua compatível e o que requer mudança no cliente; nenhum campo proposto deve ser apresentado como já consumido pelo APK |
| Pendências | Responsável, arquivo/rota afetada e evidência faltante para cada ponto não concluído |

Não anexar credenciais, tokens, códigos reais de ativação, dados pessoais, URLs privadas nem caminhos de armazenamento de produção. Exemplos devem ser sintéticos ou sanitizados.

O resultado “servidor pronto” exige contrato confirmado e evidências dos fluxos acima. “Publicado no Git”, “compilou”, “health 200” e “ready 200” são estados distintos e devem ser identificados como tais. O APK integrado continuará pendente até a conclusão e a verificação da etapa Android.
