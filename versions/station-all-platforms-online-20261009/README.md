## Catálogo33: capas atuais do site

36 capas corrigidas (PS2/PSP/Wii/WiiU),42 conferidas pela API pública. DEX inalterados. Buscar novamente o catálogo assinado; cache por coverId+item.revision. Não reaproveitar capas antigas nem limpar saves/dados. Origem, exceções e recibo no mesmo handoff do servidor.

## Catálogo 32: PSP e Sega 32X

Dados publicados; mapping e parser desta compilação conferidos com os 45 jogos reais. Capas/downloads seguem o contrato assinado. DEX inalterados. Consulte o mesmo handoff e os recibos de integração/limpeza; não executar operadores ou receitas por caminhos intermediários removidos.

# Station — candidata de integração de plataformas

Leia `../../docs/server/HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md` para o estado integral. Backup anterior publicado nos dois repositórios; código desta candidata está isolado. Servidor publicado com catálogo31/perfis5176 e 17 plataformas, incluindo PS2/Saturn; veja o recibo atual no mesmo handoff. Canais e instalações dos celulares permanecem anteriores; o APK completo ainda precisa ser montado no PCAPK.

212 Java e DEX compilados, quatro novos cores com fonte/licença e patches, runtime de cinco preservado. N64 e NeoCD passaram na transferência de estado em dois processos. Gameplay Android e APK completo assinado pendentes; Dreamcast quatro, Dolphin Station, Wii U, Switch, PS2 e Saturn ainda precisam de integração nativa no APK. Não anunciar todas as plataformas prontas.

## Sinopses na sala

`StationRoomsActivity` mostra `metadata.description` do catálogo assinado, pelo itemId, em Criar sala e Sua sala (quatro linhas, toque para a íntegra). A lista de outras salas mostra duas linhas e Ver detalhes inclui o texto completo. Os avisos do perfil ficam em Como jogar; limites, posições e confirmação continuam junto dos controles. Sem chamadas HTTP extras. Fallback explícito quando o texto ainda não foi cadastrado. Java/D8 compilados; a publicação do APK e a conferência visual nos celulares pertencem ao PCAPK. O mesmo handoff e `roomPresentation` do contrato descrevem a integração.

## Receitas

- `recipes/build_java.py`: JDK17/API34/D8 explícitos; mantém client DEX byte idêntico.
- `recipes/test_content_identity.py`: 10 verificações Java/Python da identidade CUE com suas faixas.
- `recipes/test_profiles.py`: 200 verificações do parser/presentação/portas.
- `tests/StationOnlineBiosTest.java.in`: 21 verificações reais do preparador de BIOS; compile com os dois jars da compilação e API34.
- `recipes/build_cores.py`: NDK r28c, fontes fixadas e patch NeoCD; resultados privados em diretório novo.
- `recipes/check_core_state.py`: compara transferência e sequência em dois processos de host. N64 requer `--frames 1200` para vídeo do fixture usado. ROMs/estados ficam privados.
- `recipes/package_candidate.py`: base completa R81 privada e assinatura original; acrescenta motores/controles/licenças, preserva todas as outras entradas. Não instala nem altera canais.

Usar Python 3.12+, saídas novas e, no PCAPK, E:. As bibliotecas já compiladas estão em `native/`; os arquivos de fonte correspondentes e licenças acompanham a entrega. Nenhuma BIOS proprietária ou ROM acompanha o pacote.

## Revisão de endpoints e lobby — 10/10/2026

Este mesmo pacote incorpora correções da navegação de pessoas/salas, páginas de 32 salas e retomada das consultas após falhas transitórias. Servidor corrigido já ativado e verificado às 21:49 UTC (fonte 7eb0e009/DLL 2c0d03447696), antes do APK: novos comandos incluem `page` e `roomPageSize`. A autoridade, os controles, os jogos e o Client DEX anterior continuam vinculados aos recibos existentes. Consultas e heartbeat usam recuo de 1–8 segundos e respeitam Retry-After até 60 segundos; falhas de acesso, TLS, assinatura e JSON não são repetidas. Ações de jogo não recebem repetição automática.

`recipes/test_lobby_recovery.py` verifica a implementação Java compilada com 36 casos; usa os mesmos inputs fixados da compilação completa. APK completo, instalação e gameplay físico continuam pendentes no PCAPK. Consultar o mesmo handoff e `server-integration-contract.json`.
