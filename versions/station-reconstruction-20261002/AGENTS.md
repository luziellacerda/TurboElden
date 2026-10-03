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
