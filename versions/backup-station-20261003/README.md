# Backup completo da compilação Station — 03/10/2026

Destino local: **`G:\BAKUP SISTEMA APP 03-10-2026`**.

Esta cópia reúne a pasta completa usada na compilação atual, entradas privadas, ferramentas externas, identidade de assinatura e os dois APKs congelados. A quantidade, o tamanho e o resultado da conferência estão em [RESUMO-BACKUP.json](RESUMO-BACKUP.json). Cada arquivo foi lido novamente no destino e comparado por SHA-256 com a origem.

## Versões identificadas

| Versão | Referência | Estado |
|---|---|---|
| Estável SNES/Mega Drive | Tag `estavel-station-snes-megadrive-20261003`, commit `97938400d3fa82d5d1564445c36fc70328add1c4` | Publicada; permanece instalada. |
| Candidato de capacidade 40.000 | Branch `capacidade-station-40000-20261003` | Compilado e testado em processos isolados; não instalado. |

O código e o histórico Git ficam também em `git/TurboElden-completo-20261003.bundle`. Esse arquivo é gerado após o commit desta entrega; o commit exato, referências, tamanho, hash e resultado da verificação ficam em `git/BUNDLE-MANIFEST.json` dentro do backup.

## Conteúdo

- `compilacao/station-reconstruction-20261002`: fonte atual, scripts, dependências locais, entradas extraídas, intermediários, bibliotecas, DEX, relatórios e saídas de compilação.
- `inputs`: APK base exato usado na montagem.
- `releases`: APK estável e candidato, com manifestos e documentação próprios.
- `ferramentas`: NDK, SDK API 34, platform-tools, build-tools, apktool, JDK, Python, CMake, Ninja e .NET usados neste computador.
- `assinatura-privada`: identidade de assinatura existente, preservada somente na cópia local.
- `MANIFESTO-ARQUIVOS-PRIVADO.json`: inventário individual de todos os arquivos copiados, hashes e mapa origem/destino.

O escopo é a compilação atual da Station: alguns motores e recursos são preservados a partir do APK base. O backup não transforma esses binários em fontes originais recuperados de todos os emuladores. Não inclui backup do banco/ROMs do servidor Linux nem dos dados privados do telefone.

## Publicação no Git

O Git recebe os fontes disponíveis, scripts, testes, handoffs e manifestos públicos de integridade. A cópia completa de 24,6 GB permanece na unidade G:, incluindo APKs, dependências e assinatura. O manifesto privado e a chave de assinatura não entram no repositório remoto.

[Guia de restauração](RESTAURACAO.md) · [Handoff do servidor para 40 mil](https://github.com/luziellacerda/TurboElden/blob/capacidade-station-40000-20261003/docs/server/HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md) · [Handoff completo da estável](https://github.com/luziellacerda/TurboElden/blob/97938400d3fa82d5d1564445c36fc70328add1c4/docs/server/HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md)

O resultado final da cópia está no resumo. O Git bundle, estes guias e os comprovantes produzidos depois da cópia ficam fora da contagem original de arquivos compilados e têm conferência separada.
