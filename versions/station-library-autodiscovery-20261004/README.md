# APP ← SERVIDOR: N64 e biblioteca automática, 04/10/2026

Base cliente: `ebd1199`, preservando as telas e os botões R8. Esta entrega acrescenta consulta de metadados do servidor e atualização automática do catálogo. **Fontes, DEX e JNI compilados no Linux; APK novo não assinado/instalado.** R7 continua o último instalado comprovado; R8 continua um candidato separado. Não promover esta alteração a estável sem conferir no Android.

## Produção conferida

Servidor fonte `77d8d5427941e2b0fc2a9f6a32e84aa71cc1fb7e`, DLL `14500ad850f41f6d361a8c29dd3a64ddd9b9642ad55133d14f814cbb0288e207`. Catálogo inicial6, atualizado automaticamente para7 sem reiniciar a API: **1.973 jogos visíveis**, incluindo **157 N64** (156ZIPs+1ROM alternativa), e255IDs ocultos preservados. As sinopses disponíveis são1.957;16edições sem fonte ficam explícitas no relatório de pendências do servidor. As capas N64 são as revistas exatas, compiladas em480×720/JPEG; os originais1024×1536 continuam no HD.

O servidor entregou157capas corretas por HTTPS em13.845,47ms, quatro requisições simultâneas,24.418.430bytes. Os156PNGs originais somam430.043.688bytes. É medição no Linux pelo caminho público, não no telefone nem promessa de tempo para qualquer internet. Downloads ZIP e RAW, hash/bytes, concessão de uso único e autorização pela mesma sessão passaram.

## Contrato e mudanças do cliente

- `GET /v1/station/catalog?metadata=1`, mesma base/pin/sessão e assinatura `TurboRamaStationAndroid/catalog/v1`. Campos antigos intactos; `metadata` opcional contém `description`, `developer`, `publisher`, `genre`, `players`, `releaseDate`. Não há caminhos do HD nem URLs de ROM na resposta.
- O parser guarda os seis campos e conserva sinopse/dados no cache. Catálogos antigos sem metadata continuam válidos. O limite da consulta com metadata é64MiB; o servidor limita cada item a8KiB, descrição até2000caracteres.
- A fila de comandos consulta o servidor a cada60s enquanto o catálogo estiver em primeiro plano, autorizado e sem downloads ativos. A primeira consulta ocorre5s após ativar acompanhamento. Catálogo com a mesma revisão não é republicado, evitando reiniciar a fila/cache de capas. Falhas comuns de rede mantêm a biblioteca já carregada; revogação continua passando pelo tratamento de sessão.
- A publicação JNI aceita as seis colunas anteriores e a sétima opcional de sinopse. Ela usa o slot de string anteriormente reservado/sem URL, sem alterar o tamanho0xe8 ou os offsets da ABI. **Atualizar Java e libstation_frontend juntos.** Nenhum endereço remoto é armazenado nesse slot.
- `native_info.h` exibe a sinopse assinada antes do complemento empacotado por ID. Páginas respeitam palavras e UTF-8; o tempo de paginação não reinicia a cada capa.
- N64 já estava em `StationPlatforms`: `n64` → `Nintendo 64`, pasta `nintendo-64`, motor `mupen64plus_next_gles3`. R7/R8 podem ver a biblioteca nova com Atualizar ou nova entrada no catálogo. Consulta automática e sinopses do servidor precisam desta atualização inicial do cliente; novos jogos posteriores não precisam de recompilação.

Quatro workers de capas, cache, leases de sessão, TLS reutilizável, descritores assinados, instalador, saves, licenças, salas R8, controles e motores são preservados. N64 não foi acrescentado ao registro de motores das salas online. Partidas em dois aparelhos e execução dos novos jogos no telefone continuam pendentes.

## Incorporar às fontes canônicas de E:

Não execute novamente a preparação R5/R7 que possa recobrir as fontes R8. Primeiro aplique o overlay verificado no work root atual:

```text
python versions/station-library-autodiscovery-20261004/apply_overlay.py --work-root "E:\ESTUDO APK\work\station-netplay-20261004"
python versions/station-library-autodiscovery-20261004/apply_overlay.py --work-root "E:\ESTUDO APK\work\station-netplay-20261004" --apply --backup-directory "E:\ESTUDO APK\backups\station-library-20261004"
```

O manifesto exige a fonte R7/R8 conhecida ou a fonte nova idêntica, normalizando apenas BOM/CRLF para comparação. Uma mudança adicional divergente interrompe a aplicação antes de escrever. Oito arquivos entram no overlay; `native_skin.h`, as telas de salas, shaders, vídeos, motores e arquivos privados não entram. A pasta de backup precisa ser nova.

`build_modules.py` compila Java8, DEX26+, JNI arm64 com libc++ estática, símbolos ocultos e alinhamento16KiB. Recebe `--work-root`, `--sdk`, `--ndk`, `--output` separado, opcional `--jdk` apontando para a pasta `bin` do JDK. SDK/NDK/API/build-tools devem apontar para instalações reais de E:/G:. `--build-carousel` usa os headers/artefatos reais já existentes no work root, incluindo `video720_posters.o` e arte das plataformas. Não gera substitutos para esses insumos privados.

Reempacotar a **base R8**, alterando somente:

| Entrada APK | Módulo novo |
|---|---|
| `classes28.dex` | `dex/classes.dex` do Station |
| `lib/arm64-v8a/libstation_frontend.so` | JNI Station recompilado |
| `lib/arm64-v8a/libturbo_carousel.so` | Carousel R8 com `native_info.h` novo |

Preservar `classes35.dex` das salas R8, todas as outras entradas por SHA256, nomes, compressão dos vídeos, manifesto e motores. Usar o processo canônico de alinhamento/assinatura e o **mesmo certificado original**. O Linux não recebeu a base APK privada, keystore nem aparelho; não foi criado APK assinado de teste com outra identidade. Atualizar por instalação sobreposta, sem desinstalar ou apagar dados.

## Evidências

`evidence/validation.json`:75protocolo,25coordenador,61instalador,41concorrência/capas,16TLS/arquivo,180publicação atômica,6N64/metadados/cache; total404checks Java nos grupos executados. API36Java8 e JNI Android26 reais compilados. Teste C++ de paginação passou. A sintaxe do renderer R8+native_info foi verificada com headers de imagem **sintéticos somente no teste**, sem empacotar essa compilação. `evidence/compiled-modules.json` identifica JAR/DEX/JNI compilados pelo builder entregue. Overlay testado com hashes, cópia de retorno e preservação R8.

Após assinatura/instalação: conferir1.973jogos,157N64, sinopse de edição com fonte,4capas simultâneas, download ZIP/RAW, abertura no motor real, saves existentes, retorno sem novo login, entrada automática de jogo novo, salas R8 e reconexão ao servidor online. Publicar recibo de APK/assinatura/instalação e diferenças por entrada. A fonte de verdade das ROMs/capas/IDs é o catálogo assinado do servidor, não um mapa preliminar empacotado.

Guia do operador: `Servidor-pix/docs/station-android/BIBLIOTECA-AUTOMATICA-STATION-20261004.md`. Retorno canônico: `RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md`; retorno desta entrega: `RETORNO-SERVIDOR-N64-BIBLIOTECA-20261004.md`.
