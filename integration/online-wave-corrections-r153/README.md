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

O kit do servidor deve ser gerado do APK R153 assinado e registrar os novos
IDs de forma aditiva após leitura atual do servidor. A compilação nativa
isolada passou; assinatura, instalação no Galaxy, teste visual físico e
aplicação do kit no servidor ainda requerem seus respectivos recibos.
