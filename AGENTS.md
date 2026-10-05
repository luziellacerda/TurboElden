# Candidato R15 Neo Geo / N64 — 05/10/2026

Leia `versions/station-emulators-r15-20261005/README.md` e `BUILD.md`. APK **d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b**, 2.036.244.940 bytes, em `E:\ESTUDO APK\work\station-emulators-r15-20261005\TurboStations-NeoGeo-N64-R15-20261005.apk`. Compilado/assinado, **NÃO instalado: USB ausente**. Último instalado continua R14 a1566d3d. Não promover a estável nem afirmar gameplay corrigido no aparelho.

Neo Geo: chave real MAME PREF_ROMsDIR_2 e diretório pai do artefato Station. N64: Mupen64Plus AE 3.0.249(beta), commit33bf702, completo com UI/controles/plugins próprios, processos:n64/n64core, prefs n64., storage interno preparado. 53checksMAME,154rotasN64,127integração,49storage passaram; assinatura/16KiB/integridade integral conferidas. Cinco entradas antigas alteradas,11106preservadas,1970adicionadas; classes35R12 exato. Sem deploy servidor.

Base R14B **arquivada em G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R14B-20261005.apk**, hash661a8738 completo no handoff; duplicataE removida só após conferência. Fonte canônica shared `station-netplay-20261004/native` permaneceR14B; fonte candidata completa `station-n64-complete-20261005/frontend-native`. Não perder pacing60 e retorno path+kind. Próxima instalação integrada é R15, coordenada com chat Desmonte o APK de testes (2). Atualizar sem desinstalar/limpar dados; conferir NeoGeo, N64/controles/settings, retorno à coleção e fluidez sem toque. Receitas históricas não devem ser reexecutadas sobre base nova.

## Histórico

# Estado vigente — R14B fluidez/retorno compilado, USB pendente — 05/10/2026

Leia `versions/station-navigation-r14b-20261005/README.md`. APK **661a8738faf2e598d448017bcb87f09e7d39ac7d2984a653fac4e9a642a9742f**, 2.006.925.798bytes, `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Visual-R14B-20261005.apk`. R14B mantém alvo60FPS no carrossel visível após parar toque (antes15/30 após650ms); vídeo30FPS permanece. Voltar e refresh restauram coleção por path+kind, inclusive após reordenação. 2080checks navegação,80política e600frames simulados passaram; ambos testes rejeitam código anterior. Apenas1SO alterado,11110entradas preservadas, assinatura/alinhamento verificados. **Não instalado: USB ausente na conferência. R14 a1566d3d continua último instalado/hash confirmado.** Sem medição nova GPU/temperatura/frame real. Não marcar estável.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004\native`; build/backup `navigation-r14b`. R14/R13/R12 e HUDR2 arquivados em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais` com hashes verificados. UsarR14B como base da próxima integração NeoGeo/N64 isolada no outro chat; não incluir inadvertidamente mame/classes30 de visual-r14. Motores, DEX, salas, vídeos, dados, cache e assinatura preservados. Nenhuma implantaçãoLinux ou alteração da configuração de tela.

## Histórico anterior

# Estado vigente — R14 visual instalado; 05/10/2026

Leia `versions/station-visual-r14-20261005/README.md` e `evidence/device-result.json`. APK **a1566d3d34305e01f5f445b6b61fb3db4e35fc8a4bc8a2f3e493fb3a433a38bf**, 2.006.925.798 bytes, instalado por atualização e hash do base.apk igual. Botões inferiores com ícones/cores por função observados no SNES. Vídeos das coleções: célula original quadrada, vídeo inteiro sem crop/deformação e fundo derivado preparado offline; prévias novas. PC: 4096 meshes,1836 posições quadradas,443 navegações e5 vídeos decodificados. USB caiu antes da conferência visual do vídeo/retorno no telefone; não alegar essa prova nem marcar estável.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004`; build `visual-r14`; APK `TurboStations-Visual-R14-20261005.apk`. R13 eR12 arquivados em G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais com hashes. Apenas4MP4 e1SO alterados sobreR13;11106entradas preservadas, classes35R12 e todos motores/DEX intactos. `native/video720_posters.o` canônico já contém49prévias; não adicionar novamente os5símbolos. Regeneração usa legado44 de `collection-video-r13/before/video720_posters.o`. Não reaplicar scripts one-shot. Nenhuma alteração em configuração de tela ou dados.

Trabalho NeoGeo/N64 separado em outro chat está em preparação; `visual-r14/mame` e `visual-r14/classes30.dex`, criados por aquele trabalho antes de sua separação em `E:\ESTUDO APK\work\station-emulators-r15-20261005`, NÃO fazem parte deste APK/snapshot. Não empacotar a pasta por wildcard. O próximo candidato deve partir do R14 verificado e preservar mídia/visual/salas. Netplay R12/servidor continua conforme handoff anterior; não houve deploy Linux aqui.

## Histórico anterior

# Estado vigente — R12 netplay internet preparado, instalado, servidor pendente — 05/10/2026

Leia `versions/station-internet-r12-20261005/README.md`. Pedido vigente usa o mesmo servidor Station para conectar redes distintas. Implementados WSS próprio, tickets individuais de uso único, bridge TCP local, encerramento e limites. Cem verificações locais passaram, inclusive Java→WSS C#→Java com 12.583.029 bytes em cada sentido. APK SHA256 **7684c6eee87985d8259becca9a22a9f4c7e3203f7c097df37da6998975596514**, 1.982.967.774bytes, em E:\ESTUDO APK\work\station-netplay-20261004. Fonte final `internet-r12`; netplay/src promovido com backup. R11 agora arquivado em G: com hash verificado.

**Sem implantação Linux e sem partida entre dois aparelhos validada.** Operador publicará quatro arquivos e habilitará Station:Online:RelayEnabled no serviço existente com proxy WSS. Motores online continuam SNES/Mega; NeoGeo/arcades pendentes não foram liberados. Não marcar estável. R12 instalado por atualização após reconectar USB, com SHA256 do base.apk conferido igual. Após desbloquear, ESActivity/carrossel com oito plataformas observado, sem login. USB caiu novamente ao entrar na plataforma; salas e partida seguem sem prova nesta revisão. Configuração de tela não alterada; último valor conhecido0. Todos os motores/design/coleções/dados preservados.

Retorno remoto c8e240a de Neo Geo/taxa foi lido e preservado na conciliação Git. O delta de taxa MB/s ainda NÃO foi aplicado ao APK R12; Neo Geo offline usa o catálogo existente, online Geolith continua bloqueado. Não executar package_delta.py do retorno com base R11 apagando classes35 R12; próxima montagem precisa preservar este DEX.

## Histórico e entrega paralela preservados

# Estado vigente — Neo Geo publicado e taxa MB/s sobre R11, 05/10/2026

Leia `versions/station-neogeo-rate-20261005/README.md`. Servidor catálogo 9, 2.162 jogos, 189 Neo Geo válidos, 255 IDs ocultos preservados, 2.119 sinopses e 374 jogos em subpastas. Neo Geo está na raiz do HD; 826 arquivos foram movidos sem alteração. Entrega mantém jogo ZIP fechado e BIOS ao lado. Alpha Mission II recebeu somente a BIOS exata no pacote de entrega; Art of Fighting 2 aguarda substituição do ZIP corrompido.

O retorno 6ef86c4 foi incorporado: R9 é último instalado comprovado; R11 é compilado/assinado, USB pendente e ajuste de tela já restaurado a 0. O delta novo tem somente JNI, helper de taxa e native_search_download, com guardas SHA/backup. Preserva Java R10, coleções R11, quatro capas, fila, ABI, salas, assinatura e dados. Não reaplicar overlays históricos, não substituir classes28/classes35 pelos DEX antigos nem executar scripts one-shot R10/R11.

O contador avança de 1 MB em 1 MB; isso não mede MB/s. Medições Linux: API 316,35 MB/s, Nginx 259,99 MB/s, HTTPS até 4,37 MB/s; sem limitador de bytes/s encontrado. Fonte nova mostra percentual e taxa real somente durante Baixando. 9 verificações C++ de taxa e 5 Java de ZIP/BIOS passaram; JNI compilada. Nenhum APK desta taxa foi assinado ou instalado no Linux. Incorporar JNI/carousel juntos sobre a base R11 canônica, mesmo certificado e atualização sem limpar dados. Gameplay Neo Geo e partida entre dois aparelhos ainda precisam de evidência.

## Histórico anterior

# Estado vigente — R11 coleções e servidor integrados, USB pendente — 05/10/2026

Leia `versions/station-collections-r11-20261005/README.md` e o handoff R10 referenciado. APK final **7c5096d58991a9724537036e18eb42555f290e2f6d673904524520da0d0146d5**, 1.982.770.888bytes, compilado/assinado; **NÃO instalado: USB ausente**. Inclui tudo do R10 e corrige coleções: remove célula Jogos sem subpasta, conserva Todos os jogos incluindo raiz, nomes exatos visíveis e descrição com quantidade/títulos reais.440checks de navegação e6153textoUTF8 passaram. UmSO alterado sobreR10,11.102entradas preservadas. Não alegar visual Android ou partidas validados.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004`; APK R11 na raiz; build/testes/backup em `collections-r11`. R10 eR9 arquivados comhash em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`. **R9 continua último instalado comprovado; tela durante carga restaurada0**, não há pendência nesse ajuste. Manter salas/controles/motores/dados, não reaplicar scripts one-shot, não mover tag estável. Nenhum deployLinux. Próximo passo: conectarUSB, atualizar sem desinstalar e conferir coleções+integraçãoR10.

## Histórico superado abaixo

# Estado vigente — R10 biblioteca compilado, USB pendente — 05/10/2026

Leia `versions/station-library-r10-20261005/README.md`. Retorno N64/biblioteca do Servidor-pix4e623bc aplicado sobreR9; fontes8do overlay ba669c mais cancelamento por geração, prioridade à fila de capas, validação metadata e diagnóstico de rota. APK R10 **8bc1d2ef1b5864dc1d5359d1df05b90593cf483dff7f48819f7a7a6b52a84c0b**, 1.982.754.504bytes, compilado/assinado, três entradas alteradas e11.100 preservadas.659checksJava,465C++ e paginaçãoUTF8, assinatura e integridade completa passaram. **Ainda não instalado: USB ausente.** Não alegar gameplay N64, visual, consumo ou partida2aparelhos validados.

**R9 foi instalado e seu hash conferido no aparelho em04/10**, recibo nesta versão/evidence/r9-installation.json. `stay_on_while_plugged_in=0` já restaurado e conferido; NÃO está pendente. Históricos que dizemR8 último instalado estão superados. R9 agora arquivado em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`; só cópia duplicada deEfoi removida após hashes iguais.

Fonte canônica `E:\ESTUDO APK\work\station-netplay-20261004`; build `E:\ESTUDO APK\work\station-library-r10-build-20261004`; APK R10 na raiz canônica. Não reaplicar overlay antigo, não misturar candidato40mil, não trocar classes35/salas/motores. Instalar atualização preservando dados quando USB disponível. Catálogo1973/revisão8/sinopses1957/N64157/folderPath313 são evidências do operador, não uma nova medição do telefone. Sem implantação Linux nesta rodada. Tag estável preservada.

## Histórico superado abaixo

# Estado vigente — N64, subpastas e biblioteca automática, 04/10/2026

Leia primeiro `versions/station-library-autodiscovery-20261004/README.md`. Servidor publicado: fonte `931030bba25ca8a783f096b72dcecd26a7b49387`, catálogo **8 / 1.973 jogos visíveis / 157 N64**, 255 IDs ocultos e 1.957 sinopses; 16 edições sem fonte. `folderPath` está publicado nos dois contratos do catálogo, com 313 jogos em subpastas. Timer de importação por minuto e reload da API a cada 10 segundos ativos. Capas N64 exatas da revista, compiladas em 480×720, conferidas por HTTPS com quatro workers.

A fonte R9 `a325e69` foi conciliada com a leitura de metadata assinada e consulta automática em primeiro plano, mantendo cache, leases, navegação por pastas, salas e ABI nativa. O overlay tem oito arquivos com guardas SHA e backup. Java, DEX e JNI compilados; **433 verificações Java, 36 C++ de coleções, 429 C++ de navegação e paginação UTF-8 passaram**. O renderer R9 teve sintaxe conferida com imagens sintéticas somente no teste.

**R8 é o último APK instalado comprovado. R9 é candidato assinado no Windows, ainda sem instalação; as mudanças desta biblioteca ainda precisam ser incorporadas ao próximo APK.** Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004`. Aplicar overlay à fonte R9, reempacotar a base R9 alterando somente classes28/libstation_frontend/libturbo_carousel e preservar classes35 das salas R9 e todas as outras entradas. Assinar com o certificado original e instalar por atualização. Não alegar gameplay N64 ou partida entre dois aparelhos sem prova. Restaurar `stay_on_while_plugged_in=0` quando a USB retornar; a desconexão deixou o valor temporário 3.

Os blocos abaixo registram estados anteriores. A pendência de publicação de `folderPath` do retorno R9 foi atendida pelo servidor; não usar essa pendência antiga como estado vigente.

# R9 — salas e subpastas compiladas; USB pendente — 04/10/2026

Ler `versions/station-ui-folders-r9-20261004/README.md`. APK `b5c98ea40b915f738e29ef2b2e7168fcdf2d327aa64c862596dff15b5620fdf1` pronto, **NÃO instalado**. Último instalado/observado: R8 `8e76d832…`. R8B somente PC, arquivado em G:. R9 inclui banner/capa real, efeitos leves, colunas adaptáveis/chat e subpastas no carrossel nativo. Campo opcional `folderPath` é novo e precisa de publicação pelo operador; catálogo anterior continua plano. Não há varredura de pastas arbitrárias do telefone. A pergunta sobre origem local/servidor ainda está pendente.

Novo retorno Servidor-pix `a4814d453a1f193fcbe40a92c8690c4eb5d41fc9` relata **salas online publicadas às 11h29**, com provas HTTPS. Foi lido e o contrato do app permanece compatível. Não usar o404 antigo como estado atual. Partida entre dois aparelhos e R9 visual/consumo Android seguem pendentes. Esta rodada não implantou Linux; implantação das subpastas também não ocorreu.

Testes: 591 Java existentes, 29 de pastas Java, 20 C#, 36 C++ de agrupamento, 429 de navegação, 34 regressões UI e 1.440 malhas. Quatro entradas do APK alteradas; 11.098 preservadas. Dados, assinatura, motores e tag estável preservados. **Restaurar `stay_on_while_plugged_in=0` quando a USB voltar**: desconectou com valor temporário3 após conferir R8. Fontes e compilação em `E:\ESTUDO APK\work\station-netplay-20261004`. Estados abaixo são históricos.

# R8 visual compilado — instalação pendente, 04/10/2026

Ler `versions/station-ui-r8-20261004/README.md` e evidence/build-result.json. APK `8e76d8328d140a6f423b9317a77bc4f154cb5de882d8e24db16df8b71f0ea783` pronto em E:, ainda não instalado por USB ausente; R7 continua último instalado comprovado. R8 uniformiza seis ações dos jogos com brilho verde animado e redesenha salas em três áreas (jogadores, salas/convites, chat). Duas entradas mudaram, 11.100 preservadas; 34 verificações e 1.440 geometrias C++ passaram. Sem mudança de API, auth, motores, vídeos ou implantação. Compilação reproduzida com hashes iguais. R7 arquivado em G: com hash, cópia duplicada de E: removida; não procurar R7 apenas no antigo caminho. Tag estável preservada. Não alegar visual Android, desempenho ou partidas validados. Operador publicará servidor; pendências de R7 continuam. Histórico abaixo.

# R7 instalado — salas aguardando operador, 04/10/2026

Ler atualização em `versions/station-online-20261004/README.md` e evidence/r7-rooms-runtime.json. APK82772343 instalado por atualização e hash no aparelho conferido; botão nativo abriu tela real das salas e Voltar retornou à lista sem login. Serviço vivo respondeu404, correlação060358fe191f4bd0af58b6ada9d45d75; operador aplicará branch feat/station-online-direct-20261004 por decisão do usuário. Não criar ou afirmar salas reais/partidas antes da implantação. Tela temporariamente ligada restaurada0, XML próprio removido. Células das plataformas continuam azuis; sinopse Battletoads conhecida ausente, SNES contadorinstalados0 observado sem auditoria. Preservar dados e investigar sem supor perda/causa. R7 continua candidato, sem teste2aparelhos. Pacote servidor portátil compilado e teste local flagoff passou, sem deploy. Histórico abaixo.

# Candidato R7 online — 04/10/2026 (não instalado / não estável)

Ler `versions/station-online-20261004/README.md`, o handoff APP→SERVIDOR nessa pasta e `evidence/online-build-result.json`. APK SHA256 `827723436ac618d3b1745a873813c7781ff10e043abc6033de416c01d774703d`, em E:\ESTUDO APK\work\station-netplay-20261004. R4 permanece instalado; USB ausente. R7 inclui R5 (vídeo sem espera fixa, prévias reais, SNES roxo), botão nativo Jogar online, salas assinadas, runtime direto em processo próprio com sessão controlada pelo processo principal e confirmação real listen() do host. SNES/ClownMDEmu candidatos; Geolith compilado mas Neo Geo não liberado (.neo/BIOS pendentes). Servidor social é código NOVO desativado, não implantação existente. Não alegar partida, visual, consumo ou compatibilidade determinística verificados sem Android e dois aparelhos. Preservar tag estável, fontes de E:, dados/assinatura/licença/jogos/saves/motores locais e produção. R6 anterior não deve ser instalado. Estados seguintes históricos.

# R5 preparado — vídeos e SNES roxo, 04/10/2026

Ler `versions/station-video-navigation-20261004/README.md`. APK `afa300d23dc57bb5b1973530dc83371fc892d6c37cf11ecc1750aed8ff22415b` compilado/assinado, não instalado: USB ausente. R4 segue instalado. R5 remove espera80ms, conserva prévias nas listas, usa quadro inicial real44vídeos e cacheGPU8texturas/8.294.400bytes, compositor próprio, SNESroxo e corrige texto solto da rede.109 verificações PC e shader/pixel ANGLE; Android/consumo pendentes. Não chamar estável. Netplay completo e servidor social ainda em implementação separada; não estão nesse APK. Fontes/temporários E:\ESTUDO APK\work\station-netplay-20261004. Preservar saves, sessão, assinatura, motores locais, tags estáveis e produção. Estados abaixo históricos.

# Estado atual em 04/10/2026 — R4 instalado

Ler a conferencia Android no HANDOFF-R4.md e device-evidence/r4-runtime.json. APK17e9b87b instalado/hash conferido; sessao1816/8instalados e sinopses Clay Fighter/Cutthroat/AddamsBR observadas. Limite real: arte das celulas de plataformas azul sem imagem, origem pendente. Netplay menu original ainda sem partida comprovada. Ajuste tela restaurado0 e tres probes HUD removidos. Proxima solicitacao Netplay com alternativas comerciais, partidas diretas, servidor proprio para salas/presenca/chat/convites; LED SNES roxo e botao Jogar online. Nao afirmar isso implementado no R4. Manter dados, assinatura, jogos, saves, branch/tag estavel e servidor produtivo. Blocos seguintes historicos.

# Revisão R4 — sinopses Mega, publicação de capas e revisão Netplay

Ler `versions/station-visual-covers-netplay-20261003/HANDOFF-R4.md`. APK `17e9b87bf268c2349874d1767d5ab315862eb09fb2705f9b79a7e307c0c63c77` em E: pronto, NÃO instalado (USB ausente). Telefone ainda R2 `31ab80ef`; R3 foi arquivado em G: com hash.706 IDs Mega/BR corrigidos desde R3,975/981sinopses confirmadas,6ausências explícitas. R4 adiciona180regressões que falham no R3 e passam no atual: publicação Java atômica e descarte/reset nativos do commit1dc8c381. Netplay Mega/SNES NÃO implementado pelo motor atual; menu informa antes dos botões, PSP/Dolphin/Flycast preservados, sem lobby Station nem partida2aparelhos comprovada.564Java,28C++,17metadados,3636lookup,98layout,9exportação,28netplay,GLSL e carga4096/cache passaram. FixtureJNI compilada não executada. Não promover a estável nem trocar motores. Preservar dados/licença/saves. Instalar R4 quando USB voltar; restaurar stay_on_while_plugged_in=0 e limpar apenas probes próprios do recibo.

# Revisão R3 — sinopses conciliadas; instalação pendente USB

Ler `versions/station-visual-covers-netplay-20261003/HANDOFF-R3.md`. R2 `31ab80ef` instalado/hash confirmado, sessão/capas/shader Android e foto SNES observados. Encontrado erro do app: mapa preliminar trocava741IDs preservados; R3 `8ece6384b83f565ec54615186a5940c6e5c47f79d4f03027332181799c4fb807` usa catálogo conciliado54bba11, todos1816casados exatamente;1804sinopses,12ausentes. Exportação TSV deixa de repetir por capa. Testes PC completos passaram; R3 NÃO instalado por USB desconectada. Não promover à estável. Reconectar, instalar por atualização, verificar sinopse/retorno e restaurar stay_on_while_plugged_in=0; probes próprios listados no recibo. Preservar dados, licença, jogos, saves e tag congelada. Estados R2 abaixo históricos.

# Candidato R2 — capas contínuas, sinopses, LED e Netplay, 03/10/2026

**Conferência posterior no PC concluída:** ler `versions/station-visual-covers-netplay-20261003/pc-validation/README.md`. 384 testes Java, 10 repetições de41 corridas, carga4096/cache4096 (4 simultâneos,0 erros,0 requisições extras no cache,0 workers após fechar),18 C++,13 metadados,98 layout,26 netplay,GLSL ANGLE e integridade integral APK passaram. DEX reconstruídos idênticos; APK31ab80ef inalterado. Nenhum ADB/produção usado neste turno. Teste no telefone adiado por pedido do mantenedor; não chamar estável. Correção apenas no lançador de teste e exportação do teste Netplay, documentadas no recibo.

Ler primeiro `versions/station-visual-covers-netplay-20261003/README.md` e `build-result.json`. Branch `feat/station-capas-visuais-netplay-20261003`; base publicada HUD `49d2b867daad584f7b6f82abccdc91798cb6d161`. APK final `31ab80ef2c77e9c5dff294d6f63807ab1e6d6cded81c2beec7aee171067f46d8`, 1922513242 bytes, em `E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R2-20261003.apk`. Compilado/assinado; quatro entradas alteradas, 10.871 preservadas, motores/HUD inalterados. **Ainda não instalado: telefone ausente na USB. Não chamar estável nem alegar velocidade/Netplay/visual Android comprovados.**

Quatro capas simultâneas, nenhuma espera fixa após sucesso, cache persistente, leases de sessão, TLS reutilizável somente após EOF íntegro e arquivo local exato validado antes da busca. 384 verificações Java + 18 C++ de fila/retry passaram. Sinopses1804/1816,12 sem fonte única,167 XMLs descritivos novos. Shader real do tema PC aplicado à capa de jogo selecionada; imagens de console SNES/Mega. Jogar em rede liga às interfaces originais PSP/Flycast/Dolphin; não há lobby Station nem Netplay SNES/Mega. 13 testes de metadados,98 casos de layout,26 verificações Netplay e GLSL100 no ANGLE passaram; ainda falta Android/dois aparelhos.

Servidor lido no retorno 54bba11c52f35695fd47eabc7145f42af9990426, API 4bb77ed2b8fb01fe967b90dc18ec3fbd1ee5d58b relatada em produção, limite4096 capas/min licença+aparelho e16384/origem. Medição48capas/4546,55ms é do Linux relatada pelo servidor, não deste telefone. Fonte upstream1dc8c381 foi comparada; apenas melhorias complementares TLS/arquivo portadas, preservando leases/gerações. Não houve alteração/deploy Linux.

Fonte/build canônico `E:\ESTUDO APK\work\station-visual-covers-20261003`. Builds e temporários E:. Insumos privados identificados, sem publicação de ROMs/BIOS/credenciais. Capacidade desta linha4096, candidato40mil continua separado. Tags estáveis preservadas. Primeira montagem62068502 não instalada foi arquivada com hash conferido em G:. Quando o telefone voltar, restaurar o ajuste temporário `stay_on_while_plugged_in` de3 para0 e remover somente os probes próprios listados no handoff HUD; não desinstalar/limpar licença para testar.

## Histórico anterior — não identifica o candidato atual

# HUD LZ Games R2 instalado — SNES/Mega, 03/10/2026

APK `6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b`, instalado por atualização e hash no telefone conferido. Ler `versions/hud-lzgames-20261003/README.md` e `evidence/device-runtime.json`. Visual do HUD nativo conferido nos dois motores; cinco ações: Continuar, Salvar/Carregar estado (dez posições), Configurações próprias e Sair. Novo save manual Mega `.00.gp` observado, mas posição10/carregar/cancelar/substituir e configurações pelo HUD ainda pendentes de teste controlado. R1 `3d3afc38` rejeitada por sobreposição de texto; R2 corrige Text::drawScaled e mostra cinco ações. Somente duas bibliotecas mudaram sobre base8f494041; 10.840 entradas preservadas. Fontes/build em E:\ESTUDO APK\work\station-hud-lzgames-20261003. Não misturar candidato40mil, não mover tag estável. USB desconectou; restaurar `stay_on_while_plugged_in` de3 para0 na próxima conexão (tentativa falhou por ausência do aparelho). Novos pedidos posteriores: efeitos do temaPC, sinopses por nome/IDStation, foto console, capas4concorrentes e investigação netplay; não fazem parte deste APK.

## Base anterior — controles SNES/Mega, 03/10/2026

APK8f494041ca4ae37fbd8becb50a1a7156ea2141e717af41452e5a1a923e0799b0 instalado por atualização e hash no telefone conferido. Ler `versions/mega-explus-20261003/README.md`, `evidence/storage-installed.json` e `storage-runtime.json` se existir. Revisãoe87a352b REJEITADA: MD.emu leu config compartilhado do SNES porque o helperfilesDir não é usado pelo nativo em API>=11. Correção nos overrides reais NativeActivity.getFilesDir/getExternalFilesDir/getCacheDir, raízes resolvidas pelo Application para não recursar.16 testes Android em fixture isolada passaram; Cutthroat Island observado em execução com controle próprio do Mega (direcional/A/B/C/Start), sem mistura com SNES. Evidência storage-runtime.json. Não testados individualmente todos os botões, salvar/carregar e saída nesta última revisão. Todos motores nativos e recursos permanecem iguais ao e87; somente4DEX+fontes atualizados. Não editar pastas do telefone manualmente, não importar config compartilhado, não chamar estável antes da conferência. Compilação E:\ESTUDO APK\work\station-mega-explus-20261003; APK terminadoCONTROLES-CORRIGIDOS-20261003.apk.

## Histórico da primeira instalação Mega

# Candidato atual instalado — SNES e Mega Drive completos, 03/10/2026

APK atual `e87a352bc61ce6b2f120d4657451471313a1e4e7671e37c572d9904fcc1ef7be`, instalado por atualização às18:42:35; hash no aparelho confirmado. Ler `versions/mega-explus-20261003/README.md` e recibo. MD.emu1.5.85 completo, processo:megadrive, controles/menus próprios; SNES completo preservado.30 testes de seleção executados no Android passaram. Host chegou às plataformas sem pedir login; painel/jogo Mega ainda aguardam conferência. GenPlusGX continua necessário para Master System/Game Gear; não apagar. Fonte/build E:\ESTUDO APK\work\station-mega-explus-20261003. Não promover a estável nem misturar com40mil. Nenhuma mudança de servidor. Branch de trabalho continua `snes-explus-completo-20261003`.

## Candidato anterior instalado — SNES completo

Branch `snes-explus-completo-20261003`, derivada da estável9793840. Ler `versions/snes-explus-20261003/README.md` e `evidence/installed.json`. Snes9x EX+1.5.85 oficial prerelease integrado com interface/controles próprios e painel próprio, processo:snes. APK62377e8d55617a9d0aefaed42d0b1a17948f9c5997b7be713dc760c4420f8c25 instalado por atualização, hash do aparelho conferido, host abriu nas plataformas. Ainda pendentes abertura do painel SNES e jogo/controles/saída; não declarar estável nem desempenho validado. Fonte/build isolados em E:\ESTUDO APK\work\station-snes-explus-20261003. Outros motores, Station/auth/catalog/download e recursos visuais preservados. Não misturar com candidato40mil; tag estável abaixo intacta. Licenças do upstream e limites de distribuição documentados no handoff.

# Estável de recuperação — Station SNES / Mega Drive, 03/10/2026

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

Evidência de fonte:302 verificações Java no host e7 da política nativa; [resultado](versions/station-reconstruction-20261002/evidence/review-fixes-validation-20261003.json). **Sem compilação Android/NDK, sem novo APK e sem instalação nesta rodada.** O APK instalado continua f5b35419, runtime629a55a8, com os404 documentados abaixo. Build/assinatura/aparelho seguem o ambiente E: descrito no handoff. Preservar identidade, Keystore, licença, jogos, saves e motores.

Retorno operacional único do servidor: [RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md](https://github.com/luziellacerda/Servidor-pix/blob/feat/station-artifact-descriptor-20261002/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md). Ele responde APP-01 a APP-14 e distingue release candidata, API instalada e bloqueios. O material abaixo descreve a revisão anterior e permanece como evidência do APK instalado.

# Revisão integral Station — 03/10/2026 — entrada atual

Leia primeiro [HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md](docs/server/HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md) e [mapa/integridade](docs/server/revisao-app-20261003/APPENDICE-MAPA-E-INTEGRIDADE.md).

Branch `revisao-integracao-station-servidor-20261003`, runtime `629a55a8cf48722460007944cf0bb737e9f8fb75`. APK instalado atual: SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, pacote `org.turboramastation.frontend`. Fonte: `versions/station-reconstruction-20261002/`. Esta revisão publica documentação e evidências; não gera outro APK nem promove a estável.

Sessão/perfil/catálogo200; total996 registrado na rede.176SNES/28SNESBR são contagens da exportação nativa, não histograma HTTP capturado. Capas404 e autorização404 não têm causa definitivamente localizada: revisar também o cliente. Há14 achados/limitações no handoff; inclusive retry de capas, concorrência de sessão, plataforma desconhecida, limite4096, instrumentação e texto de erro conclusivo demais. Não afirmar que o app está correto por receber200/404.

O código novo convive com renderer/launcher binários preservados; eliminação física integral do legado e execução de jogo por instalação Station ainda não comprovadas. Preservar Keystore, licença, dados, jogos, saves, design e motores. Build/temporários somente E:. Pedido ao servidor é revisão de código e evidências; não é deploy automático.

**Os estados e hashes abaixo são históricos. Este bloco e o novo handoff têm precedência para identificar o candidato atual.**

# Estado confirmado em 03/10/2026

Candidato 43670211 instalado, hash verificado. Login salvo e catalogo de 996 itens abriram. Loading corrigido e texto some ao concluir. SNES tem 176 porque corresponde ao catalogo Station publicado; mantenedor espera mais de 800. Ler handoff de catalogo incompleto. Ainda nao e estavel nem migracao integral concluida; faltam capas/downloads reais, indice completo e legado residual.

# Reconstrucao Station - APK candidato integrado

Leia versions/station-reconstruction-20261002/README.md e os handoffs. Candidato 38e78fde instalado em 03/10/2026, hash conferido; 204 testes locais e verificacoes nativas. Login real ainda aguarda validacao. Nao promover a estavel. Legado nativo residual e importacao de jogos antigos estao documentados como pendentes.

# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
## Cliente Android de licença comercial em preparação

[Fontes e receita](versions/station-android-client-20260930/) e [handoff para o servidor](docs/server/HANDOFF-CLIENTE-STATION-ANDROID-20260930.md): cliente compilado em APK candidato a partir da base 1189899e; login comercial desligado até entrega de URL, chave pública e rotas do servidor. Candidato não instalado nem promovido a estável. A tela nativa de catálogo/download ainda precisa de ponte direta para `StationContent`; não afirmar que as compras ou downloads comerciais já estão protegidos.

## Vídeos Arcade/Final Burn Neo/MAME instalados

[Atualização atual](versions/atualizacao-2026-09-30-videos-arcade/HANDOFF.md): APK1189899e, instalação e hash conferidos, base544fdecb preservada. Mapa Arcade corrigido e capacidade de prévias ajustada. Demais motores, vídeos BR e login preservados.

## Atualização posterior à estável — vídeos e handoff servidor

[Vídeos BR/NDS instalados](versions/atualizacao-2026-09-30-videos-br/README.md), APK544fdecb. [Handoff completo do servidor Android](docs/server/HANDOFF-TURBORAMASTATION-ANDROID-20260930.md), incluindo saudação com nome do comprador. Login remoto ainda não implementado. A referência ESTAVEL.md/tag05dd34b mantém o APK78accf4c de recuperação.

# Estável atual — estavel-2026-09-30-plataformas-emuladores

Versão instalada e promovida a pedido do mantenedor. **Comece por [ESTAVEL.md](ESTAVEL.md)** para identificar APK, fontes e limites. [Alterações completas](versions/estavel-2026-09-30-plataformas-emuladores/ALTERACOES.md) · [Pastas e restauração](versions/estavel-2026-09-30-plataformas-emuladores/RESTAURACAO.md) · [Manifesto](versions/estavel-2026-09-30-plataformas-emuladores/MANIFESTO-ESTAVEL.json).

43 plataformas; PSP BR; Xbox clássico integrado; PC Engine CD preciso/BIOS local; capas Jaguar/PCE CD; Naomi/Naomi2 preparados para receber jogos; vídeos PSP BR/Game Gear/SNES BR/MegaDrive BR/Xbox/Naomi atualizados. Capas baixadas persistentes. Economia de vídeos e remoção de nave/estrelas preservadas. PS2 permanece ARMSX2 e está parado por ordem expressa. Hash do APK **78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2**. Nem todos os jogos/motores novos têm execução individual comprovada; consulte os limites antes de diagnosticar.

## Documentação histórica — não identifica a versão atual

# Xbox 360 — candidato experimental de30/09/2026

[Atualização Xbox 360](versions/atualizacao-2026-09-30-xbox360/README.md): XenDroid0b11201,24 jogos/24 capas, vídeo720, configurações próprias e processo separado no mesmo APK. Candidato929339ae compilado/assinado, ainda não instalado. GameCube/WiiU incluídos; estável3573db1 preservada. Telefone descarregou, instalação adiada. Consulte manifesto e handoff para pastas e reprodução.

## Histórico

# GameCube / Wii U — 30/09/2026

[Atualização atual](versions/atualizacao-2026-09-30-gamecube-wiiu/README.md): GameCube integrado/instalado com 37 jogos carregados; Cemu Android 0.5 incorporado para Wii U, 9 jogos/9 capas, APK pronto e instalação adiada pelo mantenedor (telefone descarregou). PSP confirmado pelo mantenedor. Wii U e GameCube ainda sem conferência de jogo/retorno. Não promovida a estável. APK candidato b11f0acc, instalado cd1a8a55. Consulte manifesto e restauração para pastas e hashes.

## Histórico

# Atualização PS2/PSP em avaliação — 30/09/2026

Leia [a atualização](versions/atualizacao-2026-09-30-ps2-psp/README.md) e seu manifesto: ARMSX2 2.7.2 e PPSSPP 1.20.4 incorporados no mesmo APK, instalado com hash conferido. PS2 abriu GTA e retornou às plataformas; PSP em teste pelo mantenedor. Design e sessão preservados. Não promovida a estável.

Ramo `versao-funcional` contém esta atualização. Ramo `estavel` e tag `estavel-2026-09-30-dolphin-flycast` permanecem no commit `3573db1`, com o APK aprovado `55cd54a3`. Consulte [ESTAVEL.md](ESTAVEL.md) para restauração.

## Referência anterior preservada

# Referência estável atual — estavel-2026-09-30-dolphin-flycast

Leia ESTAVEL.md e versions/estavel-2026-09-30-dolphin-flycast/MANIFESTO-ESTAVEL.json no repositório. APK aprovado: 55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85.
Fontes ativos: E:\ESTUDO APK\work\native-carousel\implementation. APK congelado: E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk.
Usar carrossel, menus e rotas nativas. Preservar jogos, saves, configurações e sessão. Atualizar sem desinstalar nem limpar dados. Builds e temporários em E:.
Dolphin 2609-7 e Flycast v2.7-44 integrados no mesmo APK; outros motores preservados. Não reintroduzir os cores antigos nem aplicar presets de desempenho experimentais. Não executar finalizadores históricos como se fossem o build atual.
A base privada e a assinatura são necessárias: o Git não contém o C++ integral do frontend original. A integração foi compilada; os motores oficiais foram incorporados dos APKs identificados no manifesto.
Nunca publicar APK, BIOS, ROMs, firmware, chaves, saves, mídias privadas ou credenciais. Preservar licenças e fontes de terceiros. A manutenção expressamente solicitada pelo mantenedor está autorizada, inclusive com IA; texto de regras não impede tecnicamente engenharia reversa.
Tags antigas são imutáveis. A versão aprovada é 55cd54a3; o candidato local 3085d9fc não foi instalado nem aprovado.
