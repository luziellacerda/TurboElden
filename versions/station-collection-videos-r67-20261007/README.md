# R67 — nove vídeos, redução de renderização e segurança integrada

Estado em 07/10/2026: **APK compilado, assinado e instalado por atualização no Samsung A56; hash integral no aparelho conferido**. O app abriu na `ESActivity`; sessão, perfil e catálogo responderam HTTP 200, com 2.212 itens. O alvo nativo de 30 fps apareceu no registro. Isso não comprova aprovação visual, estabilidade online, modo de prova/atestação de hardware ou economia térmica medida.

## Base e pastas exatas

- Snapshot: `versions/station-collection-videos-r67-20261007` deste repositório.
- Compilação final e temporários: `E:\ESTUDO APK\work\station-collection-videos-r67-20261007-final`.
- Recibo nativo/mídia: `E:\ESTUDO APK\work\station-collection-videos-r67-20261007-final\evidence\build.json`, gerado em `2026-10-07T18:28:05.615193+00:00`.
- Recibo Java: `E:\ESTUDO APK\work\station-collection-videos-r67-20261007-final\java\evidence\build.json`, gerado em `2026-10-07T18:27:22.387215+00:00`.
- Base R66: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R66-20261007.apk`, SHA-256 `e4397fd743c410ea060f17446706d9475b5568caad379e1a6df37672c60398d1`.
- APK final: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R67-20261007.apk`, SHA-256 `d746cc02b602162b19509cd44ad7cf751e320de3b52199e7d48e86e9e897228f`, 2.110.287.552 bytes. Ver `evidence/package.json` e `evidence/installation-samsung.json`.

O diretório anterior sem sufixo `-final` contém a preparação de oito vídeos. Não misturar seus objetos ou recibos com esta compilação final de nove vídeos.

## Vídeos das coleções

Origem autorizada: `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\Sele;'ao`.

Foram convertidos os nove arquivos de `mapping.json`: Art of Fighting, Bomberman, Donkey Kong, Fatal Fury, Metal Slug, Samurai Shodown, The King of Fighters Hacks, The King of Fighters e Top Gear. Samurai usa o arquivo atualizado; Top Gear entrou na preparação final.

| Original atualizado | SHA-256 da origem |
| --- | --- |
| `samurayshodow.mp4` | `e7a75efd37e005921a92f6bed729a85007faa318707fa4d39bf6c905de675216` |
| `top gear coleção.mp4` | `a3476ce96f9bf7959f3ac73239de31aac3c89d05e52cc1c94539269d77610091` |

Os nove resultados passaram por inspeção de streams e decodificação integral: H.264 baseline, YUV420P, **720 × 720, 30 fps, sem áudio**, sem corte ou esticamento. A velocidade continua normal; duração conferida com tolerância de um quadro. A conversão amostra/repete quadros, sem interpolação. `0:V:0` exclui JPEG anexado ao original. Cada prévia estática usa o primeiro quadro do próprio vídeo convertido.

São seis substituições e três acréscimos, total de **55 vídeos conferidos no APK final** pela receita de embalagem. As rotas correspondem às coleções do catálogo; não criam listas ou alteram jogos. O recibo registra 22 verificações de rotas e aprovação da política de um decodificador.

Só a célula em evidência reproduz; as vizinhas usam quadros estáticos em cache. Mantidas as regras de suspensão ao entrar em jogos/configurações ou ocultar o menu. Os MP4s devem permanecer `ZIP_STORED` e alinhados, pois `AssetManager.openFd` depende disso.

## Consumo e limites de quadros

A composição nativa R57 presente na R66 foi preservada, com novos mapeamentos/prévias e dois headers da política de renderização. Biblioteca final: SHA-256 `ea4d4ee4b519b646dc367f66bbbc410be1365d4344458cd6cc8a7a859da90712`, 135.756.800 bytes.

- `GuiStore`/carrossel nativo: teto de **30 fps**, em movimento ou repouso.
- Diálogos cobertos/parados: **15 fps**, conservando o limite anterior. Oito combinações da política conferidas.
- Brilho do botão e avaliação Java: callbacks de **34 ms** (~29,4/s), duração da animação mantida pelo relógio real.
- Salas Java: **sem teto global de 30 fps**. Fundo, WebP e outras Views têm relógios próprios; invalidações desencontradas podem gerar mais quadros globais. Não declarar um limite global inexistente.
- Velocidade/loop dos emuladores preservados; vídeos não são interrompidos por alguns segundos de inatividade.

Ainda não há medição nova de CPU/GPU, bateria ou temperatura. Reduzir os quadros do carrossel de 60 para 30 não comprova redução de 50% no consumo total.

## Segurança conciliada sobre o app atual

Retorno do servidor: `b37c873b70bf361388b3a18fd58eed3b5452565a`. Delta originado no candidato `250a3e51a2876175155d148235af1fc402b84d08`, conciliado sobre a fonte atual da R66; as Activities antigas da R57 não foram restauradas. Ver `evidence/security-merge-provenance.json`, `recipes/source_composition.py` e `JAVA-SOURCE-MANIFEST.json`.

As **193 fontes Java** compilaram com Java 8/API 34, gerando:

| Módulo substituído | SHA-256 do novo DEX |
| --- | --- |
| `classes28.dex` — cliente autenticado | `4e912015b3daac63cf48f4621ee0022448e917927a41990e9bd22e96feecb810` |
| `classes35.dex` — salas e integração online | `b3a6e8c3fe7ba30665a2c7058216f51c1ec7e39025e30de502c96466f89904bb` |

Incluídas prova assinada nas chamadas e no ticket relay, chave secundária quando disponível e negociação de segurança. A identidade RSA principal e o vínculo de licença permanecem. Mantidos controles R64, Binder, saída, HUD e diagnósticos. Sessão, perfil e catálogo autenticados foram observados com HTTP 200 no A56. O modo de prova negociado não foi registrado; a atestação de hardware e o handshake de segurança específico continuam sem comprovação física.

## Preservação e verificações

- Empacotamento concluído sobre o APK R66 exato; DEX28/35 compilados juntos; fontes, classes preservadas e ausência de duplicações entre módulos conferidas. Todas as entradas do pacote foram verificadas, com 13.210 entradas preservadas.
- DEX30/BIOS automática manteve SHA-256 `1dcfa1e69686a326e22c54b9adc7c6013644e69d14642664e2ab7b5e2eee4ff4`.
- Emuladores, `libstation_retroarch.so`, `assets/station-online/engines.json` e demais entradas fora do conjunto declarado foram preservados e conferidos na embalagem. Nenhum motor foi trocado.
- Certificado conferido: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`. Alinhamento de 16 KiB e identidade das entradas também conferidos.
- **449 checks Java locais anteriores** aplicam-se ao mesmo código Java, sem alteração entre aquela execução e esta compilação. Evidência: `evidence/java-memory-tests.json`. Não equivalem a gameplay entre dois aparelhos. Nativo/mídia finais têm recibo próprio de nove vídeos.
- Publicar somente fontes e recibos apropriados. Não publicar APK, ROM/BIOS, mídia privada, segredos ou logs pessoais.

## Pendências reais

**Retomada de partida após queda não foi implementada.** A segurança não remove encerramentos automáticos existentes nem fornece recuperação de sessão, TCP ou estado do jogo. Isso requer contrato e implementação coordenada entre servidor, cliente e motor, tratada no pedido técnico separado. Não anunciar as quedas como resolvidas pela R67.

## Instalação e limites da conferência

Instalação no `SM-A566E` concluída em `2026-10-07T18:35:51.173063+00:00`, sem emulador ativo antes da atualização. Hash do APK instalado igual ao artefato final; UID e data original preservados. Sem desinstalação, limpeza de dados ou mudança de configurações do aparelho. Última observação do recibo: `2026-10-07T18:37:41.429407+00:00`.

Abertura na `ESActivity`, sessão/perfil/catálogo HTTP 200 e 2.212 itens foram comprovados; registro de alvo nativo de 30 fps observado. Não houve exceção fatal no processo observado. O recibo também contém eventos `REQUEST_FAILED` com status 200 e um evento anterior `CATALOG_PUBLISHED` com status 503, seguido de catálogo de rede 200. Esses eventos não foram explicados pela conferência e não permitem declarar ausência de falhas de rede.

Faltam medir consumo/temperatura, conferir visual e todos os vídeos no aparelho, identificar o modo de prova/atestação negociado e testar partida real entre dois aparelhos. A retomada online segue pendente. Não marcar estabilidade geral com base nesta instalação.

## Reexecução final dos testes locais

`python recipes/run_local_tests.py` reexecutou 449 verificações mais o diagnóstico de relay. Ver `evidence/local-tests-final.json`: 193 fontes de produção vinculadas aos hashes da compilação DEX, 11 fontes de teste, 307 classes em memória. Nenhuma partida real é simulada como prova de gameplay.

Fonte funcional desta compilação: `0d7a44f371e846a9821426a9082405836e250b0e`. Alterações posteriores de handoff/recibos não recompilam o APK.
