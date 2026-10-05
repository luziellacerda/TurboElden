# Retorno Neo Geo CD — 05/10/2026

## Atualização de precedência após a conferência N64

O relato abaixo foi preparado sobre R18. A revisão posterior **R19B foi instalada e conferida para N64**, conforme [handoff](../../versions/station-n64-controls-r19b-20261005/README.md) e [mapa de reconstrução](../../versions/station-n64-controls-r19b-20261005/RECONSTRUCAO-E-FLUXOS.md). O delta Neo Geo CD abaixo continua separado; sua receita deve ser conciliada com R19B ou sucessora comprovada, preservando o SO e os recursos N64. A menção histórica a R18 como última instalada não identifica mais a instalação após R19B. Esta nota não compila, instala nem valida Neo Geo CD.

## Retorno original do servidor e delta preparado sobre R18

Produção Station **catálogo14 / 2.212 visíveis / 255 compatíveis**,50NeoGeoCD,50capas revista480×720 e50sinopses. Disco`.img` original já éCHDv5; entrega`.chd` byte idêntica, sem recompressão. Originais ficam em`neogeo/neogeocd`. API931030b/PID347227 preservada, autoimport/reload ativos e nenhuma restrição artificial de MB/s adicionada.

Servidor scanner9cff9b333b5e0fcaec6d8a12f75b61519d8c7018; índice SHA07ad4c3fda41a19c23745436c4c45c97a70b2c7688eff788612fe22743823a92. Catálogo/grants assinados, oito pares capa/download/compatibilidade, metadata/folderPath e50capas HTTPS/4workers aprovados. A BIOS CD continua ausente; download/catalogação independem dela.

Cliente: [ponte/CD e receita sobre R18](../../versions/station-neogeocd-20261005/README.md) compilada emDEX,25 checks Java/parser/overlay passaram. Implementa driverneocdz +montagemCHD e importaçãoBIOS pelo seletorAndroid com verificação exata. **Delta ainda sem APK assinado/instalação. R18 continua instalada/hash comprovado**, filesystem/rompath da R18, navegação R17, R16 offline/download e N64 completo preservados. O retorno concorrente 9547071 foi incorporado integralmente. SVC Plus/controles já têm prova na R18; NeoCD ainda não tem gameplay comprovado. Não retroceder para R15/R16/R11, não executar package R18 sobre outra base novamente, não substituir renderer/SOs ou classes35 das salas.

Pendência real: compilar o delta sobre o APK R18 exato, assinar/instalar por atualização e provar NeoCD com BIOS legítima do usuário, NeoGeo/N64 e retorno/saves no telefone. Não alegar gameplay sem isso. Nenhuma senha, chave, BIOS, ROM ou APK é publicada no Git.
