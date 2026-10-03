# Revisão atual — candidato de capacidade40mil, 03/10/2026

A estável SNES/Mega foi congelada e publicada ANTES desta ampliação: branch/tag `estavel-station-snes-megadrive-20261003`, commit `97938400d3fa82d5d1564445c36fc70328add1c4`, APK3b355b02. **Não mover essa tag nem sobrescrever seu APK/inventários.** Ela continua instalada.

Fonte canônico E: e este checkout agora contêm a revisão `capacidade-station-40000-20261003`, cliente `1.0.8-station-capacity40000-20261003.1`. APK candidato SHA256 `bced63f9b670b9098ffb983cf7e45335678b725d2944ee7133f77128724b9b7b`, em `E:\ESTUDO APK\candidatos\2026-10-03-station-40000\TurboStations-CANDIDATO-40000-20261003.apk`, não instalado.

Ler `docs/server/HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md` e `versions/station-capacity-40000-20261003/` na raiz do Git.353 checks locais,35 JNI Android,9 do índice C# isolado; leitor Android40000/43,76MB passou em1997ms. ABI/rotas/assinaturas preservadas; parser por registro, consulta de recibos existentes e índice nativo porID. Limites40000/64MiB no cliente, sem paginação. Patch de backend preparado para40000 públicos/65536 privados; NÃO aplicado em produção. Servidor continua1816. UI completa40mil não homologada.

As referências abaixo descrevem a estável ou história anterior. O handoff completo da estável continua como manual de funcionamento; este bloco identifica o fonte candidato atual. Builds/temporários somente E:, reparos no fonte/APK e preservação dos dados/licença continuam obrigatórios.

---

# Estado atual — estável Station SNES / Mega Drive, 03/10/2026

Referência: branch/tag `estavel-station-snes-megadrive-20261003`. Ler primeiro `docs/server/HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md` na raiz do Git (cópia na raiz canônica E:). Manifesto e inventários em `versions/estavel-station-snes-megadrive-20261003/`.

APK SHA256 `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`, 1902768022 bytes; congelado em `E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk`. Fontes em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`, mirror `versions/station-reconstruction-20261002`. Cliente `1.0.8-station-storage-20261003.3`.

Sessão/perfil/catálogo1816/capas e dois downloads/instalações/aberturas comprovados; SNES e Mega Drive retornaram sem login, conforme confirmação do mantenedor. Instalados persistiram ao reiniciar.327 verificações locais e10 de armazenamento no Android passaram. Raiz/permissão/recursos e consulta de espaço Android corrigidos no APK; nenhum reparo manual da árvore real do telefone. Assinatura, jogos, saves e licença preservados.

Escopo estável é o fluxo SNES/Mega observado, não todos os jogos/motores ou checkout comercial completo. Servidor: retorno fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61, API fd13c0d relatada em produção. Meta seguinte autorizada: preparar40mil jogos em revisão separada APÓS congelar esta tag. Nesta estável permanecem4096 itens/12MiB; não alegar40mil implementados. Não alterar a tag congelada. Limites, metadado Battletoads USA/ESP e legado nativo residual constam no handoff.

**Todos os estados abaixo são históricos. Este bloco e o handoff completo prevalecem.**

---

## Regra permanente — instalação nova e reinstalação

Toda correção de pasta, recurso ou configuração necessária ao funcionamento deve entrar no fonte e no APK, com preparação automática repetível que preserve arquivos existentes. Não depender de criação manual de pastas, cópias por ADB ou ajustes exclusivos do telefone de teste. Conferir a primeira inicialização com pastas ausentes e a retomada após permissão, além da atualização. Usar fixtures isoladas; não desinstalar/limpar o aplicativo principal para simular uma instalação nova, pois isso apaga a identidade Keystore/licença. Registrar qualquer recurso ainda não verificado sem alegar preparação completa dos emuladores.

# Integração Station instalada — 03/10/2026 16:17 — estado atual

As correções de runtime `02c09dd36fcfa6c69ceb481f0934e84eef01e5ae` foram integradas e compiladas no Windows/E:. Branch de entrega `integracao-station-producao-20261003`. APK `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795`, 1.902.751.638 bytes, instalado e hash no aparelho conferido. Fonte canônico `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`; APK `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`.

302 verificações Java/API34, 28 da ponte JNI Android e 7 de retry C++ compilado pelo NDK e executado no Android passaram nesta rodada. Em relação ao APK anterior f5b35419, só `classes28.dex` e `libstation_frontend.so` mudaram. Assinatura, manifesto, design e motores preservados. APK anterior guardado em `build/previous-f5b35419-20261003/TurboStations-Station-ANTERIOR-f5b35419.apk`.

**Impedimento atual comprovado:** o mantenedor confirmou ter desinstalado o TESTE antes desta instalação. Uma tentativa autorizada com o código do handoff privado retornou ACTIVATION HTTP403 às16:19:13, correlação `1354b75f239f4fd7be8761df5efd7f8e`. Não repetir o código nem retirar a autenticação. O operador deve conferir essa requisição e liberar/reemitir a ativação para a nova chave da instalação conforme as regras comerciais. Não atribuir a recusa a consumo/expiração/bloqueio sem a conferência no servidor. Código/licença não foram publicados.

Servidor b1511b9 relata APIfd13c0d implantada, catálogo revisão3/1816 e provas HTTPS. Esse catálogo ainda NÃO foi validado neste APK por causa da recusa de ativação. Capas, download, instalação de jogo e retorno continuam pendentes no aparelho. Limite4096/12MiB permanece; suporte a mais15mil não foi implementado. Não promover a estável. Nenhum serviço Linux foi alterado.

Ler `docs/server/INTEGRACAO-APP-PRODUCAO-STATION-20261003.md` na raiz do Git e `versions/station-reconstruction-20261002/evidence/integration-production-20261003.json`. Na pasta canônica E:, a cópia do handoff está na raiz. Os blocos abaixo são históricos; este estado tem precedência.

---

# Retorno confirmado do servidor — 03/10/2026, 15h21

**Ler primeiro o [handoff único atualizado](https://github.com/luziellacerda/Servidor-pix/blob/b1511b9f75815aceb78dea801bb7ccc29f1036ab/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md).** A API Station foi implantada em `fd13c0d27eaab6a4dcf931a9cd64c3dcd7dd50c4`, DLL SHA256 `f305ae3763cb77a53a27b2c168c8de290191b3a7e88e612850856b6f7be7e639`. HTTPS autenticado confirmou **catálogo revisão 3 / 1.816 jogos**, `snes=644`, `snesbr=191`, `megadrive=887`, `megadrivebr=94`; cinco pares capa/download 200 (2 raw/3 ZIP) com assinatura, MIME, tamanho e SHA256. Um ID anterior oculto também foi autorizado e transferido; reuso dos cinco grants foi negado. O eco de `X-Correlation-ID` passou após corrigir duas linhas nas rotas Station do proxy.

**Causa dos 404 localizada:** a identidade Linux da API não conseguia abrir nenhum dos 996 jogos nem suas capas. O índice também tinha plataformas/nome incorretos e duplicatas: os 99 registros de outras plataformas apontavam para arquivos SNES/Mega Drive. A conciliação preservou todos os 996 IDs e capas anteriores: 741 IDs de jogos canônicos + 255 entradas ocultas de compatibilidade, e 1.075 jogos novos. A API lista 1.816 jogos; o índice privado contém 2.071 entradas. Foram conferidos 4.142 arquivos/hash sob o usuário real do serviço. Migrations 028/029 e chave já existiam; backup foi restaurado em banco temporário e os serviços compartilhados preservados.

O mesmo handoff contém **listas completas** com nomes/IDs/revisão/capas/descritores/hashes e a tabela dos 996 IDs anteriores. O catálogo cruzado teve 1.816 correspondências exatas com a resposta HTTPS assinada e zero IDs faltantes. Usar catálogo fresco revisão 3, IDs exatos e o mesmo Bearer entre autorização e GET; cache revisão 1 precisa ser atualizado. `catalogVisible` é configuração privada do servidor e não entra no payload do app. O HD fornecido comprova SNES/Mega Drive; os 12.346 nomes históricos não provam acervo das demais plataformas.

**Fonte Android continua 02c09dd36fcfa6c69ceb481f0934e84eef01e5ae**, com 302 verificações Java no host e 7 da política C++. Esta atualização registra a implantação do servidor; **não gerou nem instalou APK novo**. Preservar assinatura/pacote/Keystore/licença/jogos/saves/motores, aplicar as correções de fonte no build canônico E: e testar no aparelho: catálogo fresco 3/1.816, capas, download/cancelamento, instalação/recibo, abrir jogo e voltar. ADB e a base privada de montagem/assinatura não estão disponíveis neste ambiente Linux; a prova HTTP não substitui UI/instalador/emulador.

Os blocos abaixo descrevem o APK auditado antes do rollout ou revisões anteriores. O total 996 e os 404 daquele recorte não identificam a API publicada agora; permanecem como evidência histórica. Não promover o APK a estável sem as provas no aparelho.

---

# Correções de fonte da revisão — 03/10/2026, 13h40

O pedido posterior do mantenedor autorizou implementar os achados. Ramo isolado `feat/station-review-fixes-20261003`, derivado da revisão `db68b613cda008052afef8152400b9c595dfcffa`. Capas voltam à fila após60 s; autorização/conferência local/GET até os cabeçalhos compartilham a sessão; a transferência pode prosseguir junto de capas e renovação. `ready()` exige a mesma sessão do catálogo; atualizar consulta perfil. Plataformas desconhecidas são contabilizadas e avisadas, mantendo os jogos com mapeamento verificado; seis aliases reutilizam pastas existentes. Timeout e404 têm textos precisos. Correlação usa `X-Correlation-ID` e SHA256 de item/cover, sem tokens, licença ou caminhos. `clientVersion` do próximo build: `1.0.8-station-review-20261003.1`.

Evidência de fonte:302 verificações Java no host e7 da política nativa; [resultado](evidence/review-fixes-validation-20261003.json). **Sem compilação Android/NDK, sem novo APK e sem instalação nesta rodada.** O APK instalado continua f5b35419, runtime629a55a8, com os404 documentados abaixo. Build/assinatura/aparelho seguem o ambiente E: descrito no handoff. Preservar identidade, Keystore, licença, jogos, saves e motores.

Retorno operacional único do servidor: [RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md](https://github.com/luziellacerda/Servidor-pix/blob/feat/station-artifact-descriptor-20261002/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md). Ele responde APP-01 a APP-14 e distingue release candidata, API instalada e bloqueios. O material abaixo descreve a revisão anterior e permanece como evidência do APK instalado.

# Revisão integral Station — 03/10/2026 — entrada atual

Leia primeiro [HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md](../../docs/server/HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md) e [mapa/integridade](../../docs/server/revisao-app-20261003/APPENDICE-MAPA-E-INTEGRIDADE.md).

Branch `revisao-integracao-station-servidor-20261003`, runtime `629a55a8cf48722460007944cf0bb737e9f8fb75`. APK instalado atual: SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, pacote `org.turboramastation.frontend`. Fonte: `versions/station-reconstruction-20261002/`. Esta revisão publica documentação e evidências; não gera outro APK nem promove a estável.

Sessão/perfil/catálogo200; total996 registrado na rede.176SNES/28SNESBR são contagens da exportação nativa, não histograma HTTP capturado. Capas404 e autorização404 não têm causa definitivamente localizada: revisar também o cliente. Há14 achados/limitações no handoff; inclusive retry de capas, concorrência de sessão, plataforma desconhecida, limite4096, instrumentação e texto de erro conclusivo demais. Não afirmar que o app está correto por receber200/404.

O código novo convive com renderer/launcher binários preservados; eliminação física integral do legado e execução de jogo por instalação Station ainda não comprovadas. Preservar Keystore, licença, dados, jogos, saves, design e motores. Build/temporários somente E:. Pedido ao servidor é revisão de código e evidências; não é deploy automático.

**Os estados e hashes abaixo são históricos. Este bloco e o novo handoff têm precedência para identificar o candidato atual.**

## Atualizacao de integracao e login - 03/10/2026

Candidato atual `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`, SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, 1.902.718.870 bytes. Inclui **Manter conectado**, preferencia privada que controla a entrada automatica; usa licenca + Keystore, nao guarda codigo de ativacao nem Bearer. Desmarcar exige toque em Entrar nas proximas aberturas, mantendo a ativacao existente. Servidor continua autorizando cada sessao. Estado de instalacao e conferencias no aparelho: `build/closure-validation.json` (Git: `evidence/closure-validation.json`).

Instalado em 03/10 12:27:01, hash conferido, acesso salvo retomado. Sessao/perfil/catalogo 200 (996 itens da rede); capas 404 STATION_COVER_NOT_FOUND e autorizacao 404 STATION_ITEM_NOT_FOUND. Tela durante carga restaurada a 0. Checkbox compilado/instalado; alternancia individual na UI ainda nao conferida.

255 verificacoes locais aprovadas e 28 da ponte nativa no Android. Aliases do servidor integrados, inclusive Mega Drive BR; 1816 itens sinteticos assinados conferidos sem corte. Reuso por hash/tamanho assinados de arquivos anteriores, isolamento de recibos invalidos e diagnostico numerico sem dados pessoais adicionados. Os testes sinteticos nao comprovam conteudo publicado.

A revisao intermediaria eaebf48b foi instalada e confirmou sessao/perfil/catalogo 200, **996 itens frescos da rede**, capas 404 e autorizacao de download 404. Nenhum jogo chegou a transferencia. Ler `RETORNO-APP-FECHAMENTO-STATION-20261003.md` (Git: `docs/server/RETORNO-APP-FECHAMENTO-STATION-20261003.md`) para tarefas EXATAS do servidor e limites do cliente. Retorno do servidor 64912e1f continua declarando candidata NAO implantada. Ainda faltam capa 200, download/instalacao/jogo/retorno reais, acervo conciliado e eliminacao fisica integral do legado nativo. Nao promover a estavel nem declarar implementacao total concluida.

Registros anteriores abaixo sao historicos; seus hashes nao identificam o candidato atual.

# Estado confirmado em 03/10/2026

Candidato 43670211 instalado, hash verificado. Login salvo e catalogo de 996 itens abriram. Loading corrigido e texto some ao concluir. SNES tem 176 porque corresponde ao catalogo Station publicado; mantenedor espera mais de 800. Ler handoff de catalogo incompleto. Ainda nao e estavel nem migracao integral concluida; faltam capas/downloads reais, indice completo e legado residual.

# Continuidade da reconstrução TurboStations

Leia HANDOFF-RECONSTRUCAO-TURBOSTATIONS.md e HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md antes de continuar.

- O usuário autorizou descompilação, recriação e testes locais. Não pedir a mesma autorização novamente.
- Trabalhar somente no TESTE org.turboramastation.frontend. Preservar a instalação, ROMs, saves e identidade Keystore existentes.
- O APK candidato 38e78fde esta integrado, com quatro DEX substituidos e 31 servicos nativos ligados ao fonte novo. Ainda nao e estavel: exigir validacao autenticada e resolver legado nativo residual/importacao verificavel de jogos antigos. Ler a atualizacao mais recente dos handoffs.
- Não transformar pseudocódigo Ghidra em alegação de fonte C++ completo recuperado.
- Não usar URLs artificiais nem fallback de senha local na reconstrução comercial.
- Não inventar extensão ou launchPath dos jogos. O contrato do descritor foi confirmado em 9c0d9d5, código final 1bfb619; a implantação no servidor ainda não foi comprovada. Recusar grant sem descritor.
- Build e temporários em E:. Executar prepare_test_dependency.py, run_tests.py e build_module.py. Os outros scripts de edição são histórico de execução única, não etapas de build.
- Antes de alterar o APK, fechar integração de login, serviço nativo, instalação e retirada das referências antigas; verificar cada diferença e preservar os motores/design.
- Não modificar nem reiniciar o servidor por inferência. Esta pasta entrega o cliente e o contrato solicitado ao mantenedor do servidor.
- Não publicar como estável com base somente nos testes locais. Exigir validação autenticada e uso real no aparelho.

- Ativação: STA- é licenseId; activationCode é Base64URL canônico de 32 bytes. A validação token(code) já estava correta. Ler a atualização de 03/10 no início dos handoffs.
