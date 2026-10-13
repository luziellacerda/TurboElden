# Conferência final de rótulos

A tentativa b02a080 foi recusada na comparação pós-montagem. O assembler gerou nomes diferentes para o mesmo endereço; o guard26257869 unifica somente rótulos consecutivos sem instrução. Método produtivo idêntico ao b02a080; instruções/operandos/destinos completos continuam comparados. Nenhum APK dessa montagem recusada foi instalado.

# Fonte final antes da montagem

A preparação d6479ab permanece intacta e não gerou APK. Esta cópia usa um único rótulo de retorno em vez de dois rótulos no mesmo endereço, permitindo a comparação canônica após montagem sem relaxar o guard de instruções. A correção produtiva é a mesma substituição única da flag; todas as guardas e valores permanecem.

# R143 candidata â€” uma Ãºnica flag de leitura do multitap

Base exata: R142 APK `f99b51a04f4967c086533157835868dcc6a22a3eb06eb63706886f9f60453b83`, fonte congelada `9a38881f467ee533b4f8bcff3ea6769b98401175`. A R142 falhou no teste humano de Top Gear 3000 Corrida VS3: opÃ§Ã£o3 segue indisponÃ­vel. NÃ£o homologar ou promover R142 por seus testes host anteriores.

## Pesquisa e confirmaÃ§Ã£o

- [DocumentaÃ§Ã£o do core Performance](https://docs.libretro.com/library/bsnes_mercury_performance/): multitap no dispositivo do usuÃ¡rio2.
- [Issue RetroArch10424](https://github.com/libretro/RetroArch/issues/10424): relatos de terceiro participante conectado sem entrada; procedimento de configurar/salvar antes de carregar e iniciar netplay tem resultados divergentes. NÃ£o constitui prova causal deste telefone.
- [Guia oficial de controles online](https://docs.libretro.com/guides/netplay-multiple-controllers/): distinguir dispositivos locais e dispositivos solicitados pela rede; solicitaÃ§Ãµes explÃ­citas devem ser coerentes. O Station jÃ¡ usa posiÃ§Ãµes assinadas e pedido explÃ­cito por participante, sem depender da ordem de conexÃ£o; nÃ£o alterar esse contrato.

O cruzamento revelou erro introduzido pela R142: prepare escreve `auto_remaps_enable=false`; o helper adiciona `auto_remaps_enable=true` depois. O parser correspondente ao runtime conserva a primeira ocorrÃªncia na tabela de chaves. O arquivo privado .rmp pode existir enquanto sua leitura continua desativada.

O teste host executou seis corpos extraÃ­dos byte exatos de config_file.c e a tabela hash real: falso seguido de verdadeiro continua falso; uma Ãºnica ocorrÃªncia verdadeira habilita; uma Ãºnica falsa permanece falsa. TrÃªs cenÃ¡rios reais de parser; o recibo tambÃ©m conserva a qualificaÃ§Ã£o anterior do leitor de controles/inicializador. Headers e fonte conferidos contra o manifesto correspondente. InclusÃ£o/referÃªncia sÃ£o stubs que falham se chamados e nunca foram usados; adaptaÃ§Ã£o strtok_râ†’strtok_s somente no fixture Windows. NÃ£o houve leitura de configuraÃ§Ã£o privada Android nem prova de corrida.

## CorreÃ§Ã£o Ãºnica

Somente o final de `StationRetroLaunch.prepareSnesMultitap` muda: substituir a linha falsa existente por verdadeira, uma vez, em vez de adicionar outra chave. Se a polÃ­tica existente estiver ausente, recusar a preparaÃ§Ã£o; nÃ£o criar valor implÃ­cito ou abrir acesso. Guardas SNES/perfil assinado, vetor de dispositivos, arquivo .rmp privado, escrita atÃ´mica, demais flags e todos os mÃ©todos originais permanecem. Nenhuma classe/mÃ©todo novo.

RecuperaÃ§Ã£o inversa da classe R142 exata, 607 classes da partiÃ§Ã£o e39DEX/13.855 entradas preservados. Downloads R141, HLE R140, saÃ­da, runtime/core, perfis, controles, FPS, READY/ACK, autorizaÃ§Ã£o e transporte nÃ£o mudam. TrÃªs marcadores e quatro IDs independentes precisam renovaÃ§Ã£o por vincularem DEX35; SNES mantÃ©m seu cadastro atual. Teste fÃ­sico de3/4 continua obrigatÃ³rio. NÃ£o requisitar correÃ§Ã£o do servidor com base somente no relato histÃ³rico da web.

Captura atual do g52 registra canais2/3 e avisos JNI StackOverflowError ao tentar imprimir exceÃ§Ãµes; nÃ£o hÃ¡ stack causal nesses avisos. Essa ocorrÃªncia Ã© registrada separadamente, sem atribuÃ­-la ao arquivo de controles ou declarar ANR resolvido. Capturas/seriais/logs/ROMs/BIOS/chaves/binÃ¡rios privados foraGit; manter fontes R142 e anteriores congeladas.
