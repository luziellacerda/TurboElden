# R153 — handoff das identidades independentes

**NÃO APLICAR ESTE KIT.** A R153 foi instalada no A56 para teste, mas o
mantenedor rejeitou seu visual: o céu com névoa da R152 desapareceu e o
escurecimento cobriu toda a área à direita. Este documento e o kit ficam
guardados apenas para rastreio. A revisão substituta terá APK e kit próprios.

Estado em 14/10/2026. Este handoff documenta o APK R153 e seu kit privado
correspondente. A fonte congelada está no commit
`dbcbe5abbfb4d876868ec37a57249465f56881a5`. A R152 assinada é a base
exata, SHA-256
`f06747b7a953813de5281ddd71f15d8cf36bf8a0ab78920bbe226dabb3c7448e`.

## Artefatos e escopo

| Artefato | SHA-256 | Tamanho |
| --- | --- | ---: |
| APK R153 assinado | `e99935da9308501f915e8b16f86c36857c7cbe2d20680d2e6e072bc6fc2b35ce` | 2.715.106.319 bytes |
| Kit privado `Kit-Servidor-TurboStations-R153-Independentes.zip` | `9d0f4a5e98b4d1cf01c75981db1dc0e96043fc2095c5cbfbcf07560d7adc8e1e` | 12.184.512 bytes |

A prova do APK assinado confirmou o certificado original
`7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`,
assinaturas v2/v3 e alinhamento de 16 KiB. De 13.860 entradas, 13.855 foram
preservadas byte a byte da R152. Mudaram somente:

1. `lib/arm64-v8a/libturbo_carousel.so`;
2. `lib/arm64-v8a/libstation_psx_online.so`;
3. `lib/arm64-v8a/libstation_mupen64plus_runtime.so`;
4. `lib/arm64-v8a/libstation_dolphin_runtime.so`;
5. `assets/station-online/engines.json`.

Os 40 DEX e `libstation_frontend.so` permaneceram byte a byte iguais à R152.
Os três marcadores de runtime foram renovados porque sua identidade inclui o
hash do carrossel. Os cores e as 20 dependências do kit permanecem iguais aos
da R152. O kit contém seis ELF, 20 dependências distintas e a proveniência dos
78 modos já revisados: 66 N64, nove GameCube e três Wii. Não adiciona aprovação
PS1 HLE. O ZIP não contém APK, ROM, BIOS, chave, serial ou logs brutos.

## Identidades exatas para conferência

| Plataforma | `engineId` R153 | SHA-256 do runtime |
| --- | --- | --- |
| PSX | `pcsx-rearmed-ff81ed17-player-v3-e3063108809a` | `e3063108809ad44dd6d38924796fd5814e4a208afe75e475720c0fe519eadc3e` |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-17f92c5307c7` | `17f92c5307c7f8e0446e17db697e62f9aeb915d7c18d0d139c1f1b04a767f0a1` |
| GameCube | `dolphin-5102a033-gamecube-v3-ba2856946295` | `ba2856946295a9dbe25805c7daaf0900373d0e71e14e73e3e5f4c742437b1416` |
| Wii | `dolphin-5102a033-wii-v3-ba2856946295` | `ba2856946295a9dbe25805c7daaf0900373d0e71e14e73e3e5f4c742437b1416` |

O manifesto completo do ZIP vincula os hashes dos seis ELF, das 20
dependências, dos perfis e dos modos ao APK acima. A coincidência parcial de
cores ou perfis com R152 não substitui a correspondência exata dos quatro
`engineId` R153.

## Procedimento histórico, suspenso

1. Conferir o SHA-256 do ZIP privado e do APK assinado, ler
   `MANIFESTO-KIT.json`, `MANIFESTO-ARQUIVOS.json`, `engines-apk.json` e as
   provas incluídas e rejeitar qualquer divergência de identidade ou hash.
2. Obter uma leitura **fresca** do catálogo, dos perfis, dos modos e do
   registro protegido atualmente aplicado. Comparar as quatro identidades
   R153 e suas decisões de modo com esse estado antes de preparar alterações.
3. Somente se a R153 fosse aprovada pelo responsável do servidor, usar o operador
   vigente sob `scan.lock` para registrar as identidades e os modos revisados
   de forma **aditiva**. Preservar integralmente registros, aprovações e recusas
   anteriores; não reaplicar operadores históricos R141/R149/R151/R152 nem
   ampliar os modos PS1 HLE.
4. Devolver recibo com baseline lido, diferenças aplicadas, quatro IDs e
   hashes efetivamente registrados, contagens de modos por plataforma,
   resultado da consulta de capacidade assinada para edição e motor exatos,
   horário e estado final. Conferir o cliente R153 após esse retorno.

Este documento e o kit não executam deploy, reinício, migração ou cadastro
automático. O recibo do kit registra `serverApplied:false` e
`serverRestarted:false`; ainda não há recibo de aplicação R153. A R153 foi
instalada por USB no Galaxy A56: o instalador retornou `Success`, a cópia do
APK no aparelho correspondeu ao SHA-256 acima e os dados foram preservados.
O teste visual posterior rejeitou a R153. Não há validação de partida física
online nesta revisão. Nenhuma etapa acima está autorizada para execução neste
kit rejeitado.
