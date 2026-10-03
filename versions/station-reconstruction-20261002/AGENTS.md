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
