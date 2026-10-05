# R14B — fluidez do menu parado e retorno à coleção selecionada

## Dois defeitos reproduzidos e corrigidos

1. `native_menu_power.h` alterava o limite de renderização de 60 para15FPS na lista de jogos (ou30FPS em plataforma com vídeo) após650ms sem interação. A animação dos LEDs/botões continuava visível; portanto, a mudança era perceptível ao soltar a tela. R14B mantém o **alvo de60FPS para o carrossel visível**, com ou sem toque. Modal parado continua15FPS; toque/loading no modal60. A programação monotônica/SDL_Delay permanece, sem espera ocupada. Vídeos continuam codificados30FPS, um em reprodução; não foram reencodificados nem acelerados. Cadência real, temperatura e consumo no aparelho precisam de medição; alvo60 não garante60 em hardware sobrecarregado.
2. `showFolderMenu` invalidava/reconstruía a lista, e `invalidate` zerava cursor e posição animada. `backFromFolder` restaurava o diretório pai, mas não a célula de origem. R14B guarda/restaura **path exato + kind da linha**, não o índice nem o ID sintético `collection_N`. Voltar dos jogos seleciona a mesma coleção; voltar de submenu seleciona a pasta filha no pai. Atualização automática conserva seleção mesmo se novas pastas mudarem a ordem. Se a pasta selecionada for removida do catálogo, usa a primeira célula válida como fallback.

## Implementação

- `native_folders.h`: `folderReturnKind`; `showFolderMenu(p,path,selectedPath,selectedKind)` copia as chaves antes de liberar o facade, reconstrói e localiza a linha na lista visível; `enterFolderGames` recebe kind0/1/2 da ação de origem; `backFromFolder` passa chave correta; refresh no mesmo diretório preserva chave selecionada. Cursor0xf0 e posição animada0xf4 são restaurados juntos antes do refresh. Raiz plataforma, nomes de pastas, IDs de jogos, filtros e rotas permanecem.
- `native_menu_power.h`: `storeMenuTargetFps(dialog,interacting,loading)` centraliza a política. Não depende mais do término do toque no carrossel. Nenhuma mudança em lifecycle Android, player, pausa em emulador/configurações ou renderização oculta. Não foram criados workers ou timers.
- Nenhuma mudança no servidor ou emuladores. Mantidos vídeos inteiros, células originais, botões com ícones/cores da R14 e salas/transporteR12.

## Artefatos exatos

- APK final: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Visual-R14B-20261005.apk`.
- SHA256: **661a8738faf2e598d448017bcb87f09e7d39ac7d2984a653fac4e9a642a9742f**.
- Tamanho: 2.006.925.798 bytes. Certificado original `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`; alinhamento16KiB verificado.
- Base R14: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R14-20261005.apk`, SHA256 `a1566d3d34305e01f5f445b6b61fb3db4e35fc8a4bc8a2f3e493fb3a433a38bf`. R14 estava instalado/hash conferido, botões vistos; R14B é atualização posterior, ver estado abaixo.
- Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004\native`.
- Build/testes/backup: `E:\ESTUDO APK\work\station-netplay-20261004\navigation-r14b`.
- Snapshot base R14: commit `34cf674`, pasta `versions/station-visual-r14-20261005`; esta entrega adiciona dois headers e scripts. Não substituir pelo snapshot R14 depois de aplicar R14B.

Durante a preparação, também foi arquivado o APK histórico HUD R2 em G:\BAKUP SISTEMA APP03-10-2026\apks-candidatos-visuais (caminho exato no recibo `archive-hud-r2.json`), hash6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b conferido antes de remover apenas a duplicataE:. Nenhum fonte/saves/jogo removido. Bases anteriores continuam no backupG:.

## Reprodução e testes

`apply_navigation_pacing_r14b.py` é patch de aplicação única sobreR14, com backup/guardas. Os dois headers publicados já são finais; não reaplicar o patch sobre eles.

`test_build_navigation_r14b.py` compila/executa fixtures com os headers reais e os anteriores. Resultado:

- **2.080 verificações de navegação**: fluxo existente, IDs originais, Todos, pastas aninhadas, volta ao item de origem, distinção da linha de jogos diretos, inserção anterior mudando índice, remoção da pasta selecionada,200ciclos de refresh e200ciclos de retorno. O código R14 falha na verificação447, exatamente no retorno à pastaRPG2.
- **80 cenários de política de quadros**, variando modal/plataforma/vídeo/loading e tempo sem toque. Mais600frames com relógio simulado em10.000.000µs, espera porSDL_Delay sem busy-wait, recuperação após suspensão/overrun. O código anterior falha com alvo15 quando esperado60 após650ms no carrossel de jogos.
- Biblioteca arm64/API26 compilada com o objeto consolidado49prévias daR14. Três avisos antigos de trigraph em sinopses, sem erro.
- `package_navigation_r14b.py` usa baseR14 exata, substitui **apenas libturbo_carousel.so**, mantém11.110entradas byte a byte, nenhuma adicionada/removida. Mantém DEX/classes30/classes35, vídeos e motores. `classes35.dex` segue8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae. Alinhamento, assinatura e comparação integral passaram.

Não executar builders históricos R11/R12/NeoGeo contra esta base sobrescrevendo classes35 ou carrossel. Compilar novos motores preservando este APK e estas duas alterações.

## Aparelho e coordenação

Na montagem, telefone estava ausente da USB. `evidence/build-result.json` registra R14B **não instalado** naquele momento. Consultar `evidence/device-result.json` se publicado posteriormente; somente recibo positivo confirma instalação e teste. A R14 anterior está instalada, não confundir. Configurações de tela não alteradas.

O outro chat `Desmonte o APK de testes (2)` prepara NeoGeo/N64 isoladamente, conforme autorização explícita do mantenedor para coordenar. Seus arquivos `station-emulators-r15-20261005/classes30.dex` e `station-n64-complete-20261005` **não estão neste APK**. A montagem dele deve usar a R14B acima como base final, aguardando liberação combinada de USB/checkout. Sem implantaçãoLinux nem promoção a estável nesta entrega.
