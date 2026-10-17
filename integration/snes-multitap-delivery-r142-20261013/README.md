# R142 candidata — entrega do multitap SNES

Base exata: APK R141 `b5a76023860bceb2aa11c946c8003fa2d92951e700dbde3a498f8316857670d4`, fonte executável `240b7c0504252e542975089f585bd67d5264f074`. Fontes históricas intactas. Congelar esta receita em Git antes de compilar.

## Evidência e causa

O mantenedor relatou Top Gear 3000, Corrida VS, três telefones na mesma sala, opções 3/4 escuras e indisponíveis. Moto g52 autorizado por USB: dois links v3 para posições 2 e 3 atingiram estado 2; captura do menu e logs privados preservados. Isso não comprova corrida jogável nem leitura do adaptador físico pelo core.

O cadastro assinado R139 preservado na R141 autoriza Corrida VS `[2,3,4]`, controle `snes-multitap-port2-v1`, perfil `88568b97800afa017e3c75684effe23f3aad8e93f5b2ac947a0638a4268bd8f3`. Campeonato em dupla e Super Mario Kart continuam restritos a dois.

O Launch instalado escreve `input_libretro_device_pN` em retroarch.cfg. A configuração correspondente ao runtime exato, `configuration.c` SHA `67d33a5933bd3464df2c7846b05e644ca9d4da7596258e6814dcc782bdbffdca`, lê essas chaves somente em `input_remapping_load_file`; o outro uso é a gravação de remap. O arquivo geral não registra essas chaves. A falta de entrega é confirmada no código; a consequência física ainda precisa de teste após a correção.

## Mudança estritamente condicionada

Somente `StationRetroLaunch.prepare` recebe uma chamada adicional e a mesma classe recebe `prepareSnesMultitap`. Retorno imediato para qualquer jogo sem perfil, plataforma diferente de SNES ou perfil diferente de `snes-multitap-port2-v1`.

Para o perfil qualificado, gravar atomicamente `input-devices/bsnes-mercury/bsnes-mercury.rmp` dentro da pasta privada da sala. O nome é `retro_get_system_info.library_name` do core real, não o nome comercial Performance. Os dezesseis dispositivos são derivados do método existente `deviceForSlot`; `[1,257,1,1,1]` e zeros restantes, sem inventar mapeamento de botões, analógicos, turbo, número de humanos ou perfis.

Somente nessa condição, apontar `input_remapping_directory` para a pasta da sala, habilitar `auto_remaps_enable`, desabilitar classificação por controle e aviso técnico de remap. Nenhum remap offline/compartilhado é importado; a busca fica restrita à sala. O arquivo de dispositivos não contém senha, ticket ou identidade. A configuração mantém as proteções e a remoção de segredos já existentes.

## Preservação e qualificação

DEX35 somente uma classe; recuperação inversa de todos os campos, métodos e instruções originais, incluindo as duas flags HLE R140. 607 classes restantes da partição preservadas canonicamente. Nenhuma nova classe. Renovação obrigatória de três marcadores que vinculam DEX35 e quatro IDs independentes; nove descritores RetroArch preservados, nenhum core/runtime recompilado. APK: cinco substituições, zero adições/remoções, 13.855 entradas e 39 DEX exatos. Downloads R141, cache, filas, FPS, shader, saída humana, transporte, READY/ACK, licença e modos intactos.

O teste host executa corpos extraídos byte exatos do leitor de remap e inicializador de controles. Demonstra leitura 257 na porta 2 e manutenção dos botões/portas/turbo sob fixtures controladas. Não executa Android, corrida ou rede, nem mede as variáveis do aparelho. Recibo em evidence/host-control-reader.json. Capturas, binários, ROMs, BIOS, chaves e seriais permanecem privados.

Não promover ponteiros permanentes nem reclassificar gameplay com base na compilação. Instalar candidato assinado no telefone autorizado ocioso preservando UID/dados/primeira instalação; atualizar manifesto explícito do BAT de testes e exigir teste real com todos os participantes na mesma composição. Os IDs independentes renovados necessitam cadastro próprio antes de seus testes; Top Gear usa os mesmos IDs RetroArch/SNES já cadastrados.
