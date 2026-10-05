# APP ← SERVIDOR: Neo Geo e velocidade real, 05/10/2026

## Estado vigente

Retorno do app **6ef86c4cfd8302c0673c784856f25cf673d261ca** incorporado, incluindo R10 e coleções R11. **R9 é o último instalado comprovado; R11 está compilado/assinado, ainda sem instalação por USB ausente.** O ajuste de tela já foi restaurado para 0. Esta entrega Linux fornece a fonte da taxa MB/s; não produziu outro APK assinado ou instalado.

Produção: catálogo **9 / 2.162 jogos**, incluindo **189 Neo Geo**, 157 N64, 255 IDs internos ocultos preservados, 2.119 sinopses, 43 sem fonte e 374 jogos em subpastas. API fonte931030b e PID347227 preservados. Scanner próprio publicado na fontecb49214. Consulte o retorno Servidor-pix `docs/station-android/RETORNO-SERVIDOR-NEOGEO-VELOCIDADE-20261005.md` e os TSVs de `biblioteca-20261005`.

## Neo Geo no contrato existente

A pasta foi movida de SNES para a raiz, preservando os 826 arquivos. Capas são as revistas exatas, compiladas em480×720/JPEG90. Cada artefato é um ZIP externo sem compressão adicional contendo **o ZIP fechado do jogo e neogeo.zip**. O descritor assinado informa `fileCount=2`, `expandedSizeBytes` e `launchPath=<jogo>.zip`. O instalador existente extrai uma vez e abre o ZIP do jogo, com BIOS ao lado; não extrair seus chips individualmente.

Os 188 ZIPs válidos permanecem byte a byte iguais dentro do pacote. Alpha Mission II tinha somente `uni-bios_1_2.rom` embutida corrompida; o pacote de entrega recompôs esse membro a partir da BIOS válida do HD, com mesmo nome/tamanho/CRC. Todos os outros chips e o original permaneceram intactos. Art of Fighting2/aof2.zip tem o chip056-c7.c7 corrompido, sem substituto local válido, e continua pendente. Não inventar conteúdo nem afirmar execução de todos os sets no telefone. Neo Geo já está mapeado no app; salas Geolith online não foram habilitadas com estes ZIPs.

O app continua lendo `GET /v1/station/catalog?metadata=1`, verificando assinatura, `itemId/revision/coverId/folderPath/metadata`, usando quatro workers em `/v1/station/covers/{coverId}` e autorizando cada download por itemId/revision em `/v1/station/downloads/authorize`. Novos jogos e coleções das plataformas já suportadas vêm automaticamente do índice. Não codificar nomes/IDs individuais no APK nem transformar folderPath em caminho arbitrário no telefone. Fluxo R10 de polling, cancelamento por geração e prioridade às capas permanece intacto.

## O contador e a velocidade

O usuário esclareceu: **o contador avança de1MB em1MB**. Isso indica bytes acumulados. Medições no Linux, com arquivo real autorizado de65.243.904bytes e SHA conferido: API316,35MB/s, Nginx259,99MB/s, HTTPS público3,76e4,37MB/s. Upload de controle3,77MB/s; duas conexões4,34MB/s agregados. Não foi encontrado limitador artificial de bytes/s. O caminho externo foi mais lento que API/disco; isso não mede a internet do telefone.

`TransferRate` mede bytes recebidos durante **Baixando**, com relógio monotônico e amostra mínima de500ms, usando média desde o primeiro evento. Reinicia em retry/novo total/relógio regressivo. Preparação e extração não entram na taxa. O renderer mostra `BAIXANDO 42% · 4.37 MB/s`, com MB decimal. Símbolo adicional `StationDownload_networkRate` mantém structs e ABI; módulo antigo conserva percentual. A transferência não recebe nova espera, buffer limitador ou thread.

## Aplicar somente o delta de três arquivos sobre R11

Este diretório contém JNI, helper da taxa e `native_search_download.h`, guardados por SHA. A JNI R10 já aplicada tem SHA4d926a216b83ac0a76f4c8baa0525d3f59b717721368b6cc483fbbfa96aaecf5. Alterações divergentes são recusadas antes de escrever; reconciliar com a nova fonte se o Windows avançar. **Não repetir overlays R9/N64 nem os scripts one-shot R10/R11.** Java e os cinco arquivos visuais R11 permanecem os atuais.

```text
python versions/station-neogeo-rate-20261005/apply_overlay.py --work-root "E:\ESTUDO APK\work\station-netplay-20261004"
python versions/station-neogeo-rate-20261005/apply_overlay.py --work-root "E:\ESTUDO APK\work\station-netplay-20261004" --apply --backup-directory "E:\ESTUDO APK\backups\station-neogeo-rate-20261005"
python versions/station-neogeo-rate-20261005/build_native.py --work-root "E:\ESTUDO APK\work\station-netplay-20261004" --ndk "E:\TurboEdenEngine\android-ndk-r28c" --output "E:\ESTUDO APK\work\station-neogeo-rate-build-20261005" --build-carousel
```

Backup e saída precisam ser novos. A compilação do carousel usa arte, headers e `video720_posters.o` reais da fonte canônica. O builder não produz nem substitui DEX. A base APK atual é **R11**, SHA7c5096d58991a9724537036e18eb42555f290e2f6d673904524520da0d0146d5.

```text
python versions/station-neogeo-rate-20261005/package_delta.py --base-apk "E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Colecoes-Nomes-Sinopses-R11-20261005.apk" --modules "E:\ESTUDO APK\work\station-neogeo-rate-build-20261005" --output "E:\ESTUDO APK\work\TurboStations-NeoGeo-Taxa-unsigned-20261005.apk"
```

O empacotador exige essa base, os dois módulos reais e arquivo novo. Confere SHA de todas as entradas e compressão. Somente `libstation_frontend.so` e `libturbo_carousel.so` mudam; **classes28.dex R10 e classes35.dex das salas ficam exatos**. Aplicar alinhamento16KiB e assinatura pelo fluxo canônico, certificado7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825; conferir novamente o APK assinado. O arquivo unsigned não é instalável como atualização. Instalar com `adb install --no-incremental -r --user 0` quando houver aparelho, preservando dados, licença, jogos, saves e motores. Não promover tag estável antes da conferência.

## Evidências e pendências

- 9 verificações C++ de taxa, incluindo reinício, total alterado e regressão de relógio; 5 Java do instalador com jogo ZIP fechado e BIOS byte a byte iguais passaram.
- JNI arm64 Android26 compilada com libc++estática, warnings como erros, símbolos definidos e alinhamento16KiB; hash em `evidence/compiled-modules.json`. Sua fonte de partida é idêntica à JNI R10.
- Sintaxe do renderer **R11 com a nova etiqueta** conferida Android26. Headers de imagem são fixtures somente desse teste Linux; nenhum binário de carousel ou APK foi produzido com eles.
- Retorno R10 registra659Java; R11 registra440navegação/6153UTF8 e APK real. Esses recibos continuam nos diretórios originais, preservados; não são novas medições nesta rodada.
- Guardas SHA, backup e aplicação idempotente do delta conferidos em árvore privada. Instalador e Java não foram alterados por esta taxa.

Após instalar o próximo APK: conferir catálogo9oumaior, 189NeoGeo, sinopses/pastas, quatro capas em sequência, MB/s variando com bytes reais, download/abertura do ZIP com BIOS, cancelamento/retry, saves e retorno sem novo login. Gameplay Neo Geo, velocidade no telefone, visual R11 e partida entre dois aparelhos continuam sem prova. A pendência local real é substituir aof2.zip por cópia íntegra; a descoberta automática o importará após estabilizar.
