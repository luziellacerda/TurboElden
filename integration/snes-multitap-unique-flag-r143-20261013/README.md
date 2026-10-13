# R143 candidata — uma única flag de leitura do multitap

Base exata: R142 APK `f99b51a04f4967c086533157835868dcc6a22a3eb06eb63706886f9f60453b83`, fonte congelada `9a38881f467ee533b4f8bcff3ea6769b98401175`. A R142 falhou no teste humano de Top Gear 3000 Corrida VS3: opção3 segue indisponível. Não homologar ou promover R142 por seus testes host anteriores.

## Pesquisa e confirmação

- [Documentação do core Performance](https://docs.libretro.com/library/bsnes_mercury_performance/): multitap no dispositivo do usuário2.
- [Issue RetroArch10424](https://github.com/libretro/RetroArch/issues/10424): relatos de terceiro participante conectado sem entrada; procedimento de configurar/salvar antes de carregar e iniciar netplay tem resultados divergentes. Não constitui prova causal deste telefone.
- [Guia oficial de controles online](https://docs.libretro.com/guides/netplay-multiple-controllers/): distinguir dispositivos locais e dispositivos solicitados pela rede; solicitações explícitas devem ser coerentes. O Station já usa posições assinadas e pedido explícito por participante, sem depender da ordem de conexão; não alterar esse contrato.

O cruzamento revelou erro introduzido pela R142: prepare escreve `auto_remaps_enable=false`; o helper adiciona `auto_remaps_enable=true` depois. O parser correspondente ao runtime conserva a primeira ocorrência na tabela de chaves. O arquivo privado .rmp pode existir enquanto sua leitura continua desativada.

O teste host executou seis corpos extraídos byte exatos de config_file.c e a tabela hash real: falso seguido de verdadeiro continua falso; uma única ocorrência verdadeira habilita; uma única falsa permanece falsa. Três cenários reais de parser; o recibo também conserva a qualificação anterior do leitor de controles/inicializador. Headers e fonte conferidos contra o manifesto correspondente. Inclusão/referência são stubs que falham se chamados e nunca foram usados; adaptação strtok_r→strtok_s somente no fixture Windows. Não houve leitura de configuração privada Android nem prova de corrida.

## Correção única

Somente o final de `StationRetroLaunch.prepareSnesMultitap` muda: substituir a linha falsa existente por verdadeira, uma vez, em vez de adicionar outra chave. Se a política existente estiver ausente, recusar a preparação; não criar valor implícito ou abrir acesso. Guardas SNES/perfil assinado, vetor de dispositivos, arquivo .rmp privado, escrita atômica, demais flags e todos os métodos originais permanecem. Nenhuma classe/método novo.

Recuperação inversa da classe R142 exata, 607 classes da partição e39DEX/13.855 entradas preservados. Downloads R141, HLE R140, saída, runtime/core, perfis, controles, FPS, READY/ACK, autorização e transporte não mudam. Três marcadores e quatro IDs independentes precisam renovação por vincularem DEX35; SNES mantém seu cadastro atual. Teste físico de3/4 continua obrigatório. Não requisitar correção do servidor com base somente no relato histórico da web.

Captura atual do g52 registra canais2/3 e avisos JNI StackOverflowError ao tentar imprimir exceções; não há stack causal nesses avisos. Essa ocorrência é registrada separadamente, sem atribuí-la ao arquivo de controles ou declarar ANR resolvido. Capturas/seriais/logs/ROMs/BIOS/chaves/binários privados foraGit; manter fontes R142 e anteriores congeladas.
