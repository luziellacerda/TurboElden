# R33 — faixa instalada, metadados maiores e barra completa

## Entrega e limites comprovados

APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Titulo-Barra-R33-20261005.apk`. SHA-256 `9313b3b893468270512b8e8ee3fa984763d6db334b4534a2f863216a0cc4a7ea`; 2053911349 bytes. Pacote `org.turboramastation.frontend`, certificado original `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`. SO `c55c9e43d380f24b83117bb9e3871bb07ce217471337db5f97c588a92ea885f4`.

Compilado e conferido no PC. **Não instalado nem conferido visualmente no aparelho nesta revisão**: a listagem ADB estava vazia. O usuário informou instalação manual anterior (R31B esperado), porém versão/hash e ativação no POCO continuam não verificados. Consulte o recibo desse relato. Não classificar esta revisão como estável geral ou partida online comprovada.

## Alterações finais

- `native_installed_tag.h`: substitui completamente a etiqueta pendurada por faixa diagonal de 45 graus, verde acetinado, dobras escuras, sombra e brilho suave. Texto INSTALADO acompanha a matriz da faixa. Aparece somente no jogo selecionado que o catálogo marca como instalado. Sem marca nas plataformas/coleções. Usa o relógio e desenho nativos existentes, sem thread, vídeo ou temporizador novo.
- `station_game_meta_row.h`: linha única nome → ícone de pasta/contagem → ícone/jogadores → estrelas. Altura 6% da tela, avanço da sinopse 7,5%. Divisão da largura disponível: contagem20%, jogadores11%, estrelas18%, três intervalos1,2%, restante para nome.
- `native_info.h`: escala comum do nome, contagem e jogadores = 0,70 × 1,50 = 1,05. Nomes longos recebem reticências em limites UTF-8; não são reduzidos novamente. Catálogo mantém o nome integral. Contagem numérica ao lado da pasta, sem o sufixo redundante jogos. Sinopse completa e rolagem preservadas; somente sua área útil muda para acomodar a linha maior. Valores de jogadores/notas ausentes seguem explícitos, sem inventar dados.
- `station_bottom_action_layout.h`: Jogar/Baixar tem a largura da capa focada dos jogos (`altura × 0,740 × 0,72`), com a mesma origem horizontal (`largura × 0,025`). Os demais botões ocupam sequencialmente o espaço até97,5% da largura: Online, Saves, Apagar, Atualizar, Voltar. Intervalo = altura do botão ×0,16; larguras remanescentes proporcionais a4,45/3/3,2/3,7/3,1. Retângulos são a fonte única do desenho e toque. Texto permanece à esquerda junto ao ícone, cores e efeitos anteriores mantidos. Coleções mantêm seu Abrir/Voltar anterior.

## Base, preservação e testes

Base exata R31B `76817d2dd48219bcd6e4d111b8471bf98925b02ab26ee517cea90e8df84b076c`. R32 intermediário somente com a faixa foi empacotado, mas não instalado; sua faixa já está integralmente incluída em R33. Não instalar R32 depois de R33.

Somente `lib/arm64-v8a/libturbo_carousel.so` mudou no APK. 13086 entradas anteriores verificadas byte a byte por SHA; DEX, motores, recursos e licença Lottie preservados. Mesma assinatura, alinhamento16KiB validado. Testes C++:9.604 verificações de botões em42 formatos, igualdade capa/Jogar, fim da barra, separação da linha, área rolável, Voltar das coleções, geometria da faixa e Lottie. Os testes geométricos não substituem a conferência visual real de fonte/clipping no aparelho.

Sem alteração de servidor, downloads, licenciamento ou netplay nesta revisão. Retorno61c0411 e os limites de latência pública/dois celulares continuam os descritos em R31. Delta downloads11be7f3 permanece fora. Atualizar mantendo dados; nunca desinstalar ou limpar dados para aplicar este visual.

## Fontes e reprodução

Fontes canônicas: `E:\ESTUDO APK\work\station-title-actions-r33-20261005\native`. Receitas build/package ficam na raiz desse workspace; testes/evidências nas subpastas. Build: Python3.14, LLVM host, NDKr28c/Android26, JDK17/build-tools35. `evidence/native-build.json` registra o comando exato, hashes de todos os fontes e SO. `STATUS.json` registra pacote/base/certificado/verificação.

Este snapshot contém os quatro arquivos alterados e restaura os demais pelos ancestrais R31 → R30 → R26/R27. Execute `python recipes/restore_r33.py E:\NOVO_DIRETORIO` para restaurar fontes completos nativos e Java e conferir cada hash. O diretório de destino deve ser novo. A restauração não instala, compila ou modifica o servidor.

Para recompilar em outro workspace, copie os testes e receitas para sua raiz e atualize os caminhos de saída/entrada no recibo antes de executar. Não execute a receita diretamente na pasta recipes do Git: build usa sua própria pasta como workspace. Dependências externas de link mantidas no comando: W16 frontend-native (headers, stubs e video720_posters.o) e W22 neogeo_previews.o, cada objeto exatamente uma vez. SDK/NDK/keystore/APK base não são incluídos neste snapshot. Não aplicar scripts de preparação históricos sobre os fontes finais. O empacotador recusa sobrescrever candidato existente, confere o APKbase e todas as entradas finais.

## Próxima conferência no aparelho

Conferir título longo/curto, contagem, jogadores e estrelas no mesmo alinhamento; texto em cada botão e respectivas ações; faixa após baixar/apagar; todas as plataformas; rolagem da sinopse. Confirmar primeiro hash da instalação manual POCO e sessão, sem supor ativação. A configuração temporária de tela ligada do Samsung (serialRQCY30751WY,0→3) ainda precisa ser restaurada para0 quando esse aparelho voltar; não aplicar esse ajuste ao POCO.
