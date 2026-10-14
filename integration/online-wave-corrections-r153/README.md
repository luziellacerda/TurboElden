# R153: corrigir a rota do cabeçalho visual

A R152 assinada é a base exata desta candidata. Na compilação da R152,
`native_skin.h` incluiu seu `native_space.h` irmão por aspas. O compilador usou
o arquivo do overlay R145 antes do arquivo visual R152. Por isso o fundo de
ondas e o escurecimento novos não chegaram integralmente à biblioteca instalada.

A receita R153 reproduz primeiro a biblioteca R152 byte a byte. Depois roteia
o `native_space.h` corrigido ao lado de uma cópia verificada de `native_skin.h`
e confere no arquivo de dependências que esse cabeçalho foi usado. A paleta
efetiva da R151 e o movimento de Ondas já instalado são preservados. Os
arquivos R145 e R151 são lidos do backup pinado; não são alterados.

O empacotamento parte do APK R152 assinado, SHA-256
`f06747b7a953813de5281ddd71f15d8cf36bf8a0ab78920bbe226dabb3c7448e`.
Somente cinco das 13.860 entradas podem mudar: `libturbo_carousel.so`, três
marcadores de runtime PSX/N64/Dolphin e `assets/station-online/engines.json`.
Os 40 DEX, a ponte `libstation_frontend.so`, o restante dos motores, os dados
e as políticas permanecem byte a byte iguais à R152. Os marcadores precisam
ser renovados porque o contrato de identidade inclui o hash do carrossel.

O APK R153 foi compilado e assinado, SHA-256
`e99935da9308501f915e8b16f86c36857c7cbe2d20680d2e6e072bc6fc2b35ce`.
A prova final conferiu as 13.860 entradas, os 40 DEX preservados, certificado
original, assinatura v2/v3 e alinhamento de 16 KiB. A atualização por USB no
Galaxy A56 retornou `Success`; a leitura do APK instalado no aparelho produziu
o mesmo SHA-256, com os dados do aplicativo preservados. O teste visual
posterior rejeitou a R153: ela retirou o céu com névoa que aparecia na R152 e
escureceu toda a área à direita, embora o pedido fosse escurecer somente a
faixa atrás das células pequenas do carrossel. A R153 não foi aprovada.

O kit privado foi montado do APK R153 assinado, SHA-256
`9d0f4a5e98b4d1cf01c75981db1dc0e96043fc2095c5cbfbcf07560d7adc8e1e`.
O [handoff do servidor](../../docs/server/r153/README.md) identifica os quatro
IDs apenas para rastreio. O kit R153 não deve ser entregue nem aplicado; a
revisão substituta precisará de seu próprio kit exato. O recibo R153 marca
`serverApplied:false`; não há cadastro nem partida física R153 confirmados.
