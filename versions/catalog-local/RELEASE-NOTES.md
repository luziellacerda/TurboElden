# TurboRetroEmu 1.0.2 — catálogo local

**O usuário confirmou que o APK e os jogos estão funcionando.** O teste relatado não especificou aparelho ou lista de jogos; não significa validação de todas as plataformas.

## Alterações

- Corrige a abertura da interface original após a senha, preservando o callback de GuiStore.
- Incorpora o snapshot autorizado de catálogo e atende `drawers.json` localmente, sem enviar nem incorporar a chave antiga de acesso.
- Mantém URLs de jogos/capas, downloads, cores, recursos, BIOS e caminhos/configurações originais.
- Restaura as rotinas de rede que haviam sido desativadas na versão histórica `1.0-funcoes`.

Senha provisória: **`turbo123`**.

Instale por cima da build local anterior, sem desinstalar nem limpar dados. Faça backup de EmulationStation, incluindo `.emulationstation`. Se houver conflito com a assinatura do APK oficial, interrompa e preserve seus dados.

## Verificações

73 testes Java passaram; assinatura v2, alinhamento, reabertura do APK, hash do catálogo, 164 assets originais e preservação dos métodos HTTP conferidos. A confirmação de execução veio posteriormente do usuário e foi registrada separadamente dos relatórios de compilação.

Android 8/API 26+, ARM64; versão `1.0.2-catalogo-local`, código 5. APK assinado com chave técnica de desenvolvimento. A release permanece identificada como pré-release por não haver validação completa de compatibilidade/produção.

## Limites e conteúdo

A lista é local, mas arquivos de jogos e capas continuam em servidores externos e exigem internet quando não estão armazenados. O snapshot não recebe atualizações automáticas. Telemetria e outras funções de rede originais continuam ativas.

Este APK inclui o catálogo completo incorporado e componentes herdados do original, incluindo BIOS/firmware/chaves de firmware. A publicação foi solicitada pelo mantenedor após a integração do catálogo; a autorização declarada para componentes herdados não altera os direitos de terceiros. Não inclui chave de acesso de usuário, keystore ou token GitHub.

Somente material do APK é publicado nesta versão. O estudo original permanece na main; os fontes novos ficam em `versions/catalog-local` na branch `versao-funcional`.

SHA-256 de `TurboRetroEmu-catalogo-local.apk`:

`21E6045F69457A05ECBFA6495507C14BC00483C4ADCB490FE4C6D7DFCF90B15D`
