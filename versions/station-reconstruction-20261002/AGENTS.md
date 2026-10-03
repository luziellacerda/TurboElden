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
