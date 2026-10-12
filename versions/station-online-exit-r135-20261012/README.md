# TurboStations R135 — correções de saída compiladas e instaladas

APK SHA256 `f6abe89490e7ba5e2cdd432625888bed6f40aea115d730cf612d509ec6ca9896`, 2,714,991,631 bytes. Fonte executável `ca8f1ccda18bef397e71e1c979a4f813acf608c0`. A R134 `f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2` é o donor exato preservado.

## Alterações autorizadas e preservação

As correções existentes de `StationDolphinSession` e `StationGameSession`, com `StationHumanDeparture`, entraram somente em `classes35.dex`. O ciclo de monitores da saída Dolphin foi removido; o Leave humano com geração antiga só é repetido após rejeição exata e snapshot próprio autenticado com identidade igual e geração maior.

O DEX foi conferido classe a classe: 606 → 608 tipos; 582 classes externas com a mesma projeção de código, dados, anotações e inicializadores; duas adições autorizadas, nenhuma remoção e 21 tipos modificados dentro das três famílias. O helper adicional do D8 apenas implementa a chamada atômica existente. O recibo registra os alvos Java8, Android API34 e DEX minAPI28.

Cinco substituições no ZIP: DEX35, três marcadores de identidade e engines.json. Zero adições e todas as outras 13.855 entradas byte idênticas. Os 39 DEX principais restantes e o owner.dex PS4 em assets, Manifest, resources, telas, frontend, mídias, shaders, cores, opções e controles estão preservados. Os marcadores usam as mesmas fontes, flags e políticas nativas, com novas identidades para vincular os bytes do bundle.

## Instalação

Edge 30 atualizado em 2026-10-12T04:33:05.661370+00:00; frontend oficial observado. O APK integral do telefone coincide com o instalador. Certificado original v2/v3, alinhamento 16KiB, UID, primeiro tempo de instalação e diretório de dados preservados. Não houve desinstalação, limpeza de dados, emulador externo ou alteração de configuração do Android.

A instrução do proprietário de instalar cada novo APK para testes está registrada no AGENTS. Esta entrega comprova compilação, assinatura, instalação e abertura; partida online/saída durante jogo com três aparelhos e aceite ao consumidor seguem pendentes. Os quatro IDs novos requerem confirmação no servidor; Git não aplica a ativação.

## Reprodução e evidências

- [Receitas fechadas](../../integration/online-lifecycle-review-r135/recipe/README-dex.md), com fonte congelada e ferramentas/inputs pinados.
- [Ordem completa de reprodução, assinatura e instalação](REPRODUCAO.md).
- [Estado](STATUS.json) e [índice público de provas](evidence/PUBLIC-EVIDENCE.json).
- [Pacote final](evidence/package-final.json), [DEX](evidence/dex-compilation.json), [instalação](evidence/instalacao-r135-edge30.json).

Executar build_payload/build_dex, build_runtime_identity, assemble_apk (freeze e unsigned), sign_verified e install_verified com os argumentos explícitos dos recibos. O build exige o commit completo da fonte, donor R134, JAR Java8 pinado, SDK34/build-tools35/apktool3.0.3, NDKr28c, recibos originais da identidade R134 e chave privada do certificado original. A assinatura usa senha por variável externa; nenhum segredo está na receita.

Os originais privados são inputs do registrador/reconstrução. Os arquivos de evidence foram sanitizados e conservam SHA de origem separados de seus próprios SHAs. APK, bibliotecas, jogos, BIOS, firmware, chaves e dados pessoais permanecem locais.
