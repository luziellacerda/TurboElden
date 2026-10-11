# PlayStation 3 e PlayStation 4 offline na TurboStations

A R128 acrescenta rotas locais para os aplicativos Android oficiais aPS3e 2.43 e Bachata S4 0.2.4. Ambos são instalados separadamente; seus APKs, firmware e jogos não são incorporados ao instalador da TurboStations nem publicados neste repositório. PS3 e PS4 não têm engine ou salas online.

## Abertura dos jogos

| Sistema | Contrato conferido | Requisito |
| --- | --- | --- |
| PS3 | Activity exportada do aPS3e, extra `iso_uri` e URI de leitura temporária | ISO local, aPS3e 2.43 instalado e firmware preparado nele; encerrar uma partida anterior antes de escolher outro jogo |
| PS4 | MainActivity do Bachata S4 recebe PKG para importação; biblioteca abre os jogos importados | Android 12+, ARM64, aplicativo oficial 0.2.4 e preparação do runtime no emulador |

A versão, o certificado, a Activity exportada, o SDK e a arquitetura são conferidos antes do envio. Se faltar o emulador, o botão **Obter emulador** abre somente a página oficial da versão auditada. Não há download, instalação ou serviço persistente automático. No PS4, o identificador CUSA não é deduzido do nome do arquivo; importar um PKG não é apresentado como iniciar uma partida.

## Preservação e compilação

O catálogo recebe somente aliases PS3/PS4. Das 271 classes da partição28, 270 permanecem iguais e apenas o inicializador de StationPlatforms recebe esses aliases. A nova partição39 contém a ponte offline. O Manifest recebe uma Activity e duas consultas de pacote; a Factory e as Activities existentes são preservadas. No carrossel nativo, apenas o encaminhamento de comandos recebe os dois sistemas. LEDs, apresentação, vídeos locais, cache, preload, limites de30fps, emuladores existentes e autoridade online permanecem preservados.

Como Manifest, DEX28 e a biblioteca compartilhada mudam, os marcadores online de N64/GameCube/Wii/PSX são renovados para corresponder ao APK completo. Seus cores, opções, perfis, protocolos e processamento dos quadros continuam os mesmos da R127. SNES/Mega Drive não são alterados.

`recipe/build_offline_payloads.py` compila as quatro entradas offline sobre o donor R127 exato, verifica o inverso dos patches, redecodifica a partição28 final e reproduz primeiro o carrossel original. `recipe/build_runtime_identity.py` exige o recibo dessa compilação e rejeita fontes ou bytes posteriormente alterados. Os demais wrappers reutilizam a montagem e conferência integral congeladas da integração PSX.

## Pacote candidato

APK SHA256 `0189527c7537845562a2be4be15c0fab976c85f4f9c7f8ab884915c8bc3052dc`, 2234617901bytes, certificado original, assinatura v2/v3 e alinhamento16KiB conferidos. 13548 entradas preservadas byte a byte. [Recibos finais](evidence/package-final.json), [identidades](evidence/runtime-final.json), [build offline](evidence/offline-payloads.json) e [conferência de contratos](evidence/upstream-inspection.json).

O pacote não foi instalado nem testado com jogos nesta revisão. A [aPS3e](https://github.com/aenu1/aps3e/releases/tag/2.43) e a [Bachata S4](https://github.com/JICA98/Bachata-S4/releases/tag/v0.2.4) são experimentais; compatibilidade e velocidade dependem do jogo, GPU e aparelho. A integração de abertura não demonstra gameplay no A56/Edge30.
