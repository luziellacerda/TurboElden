# Handoff: TurboramaStation + TurboEden em um APK

**Data:** 28/09/2026  
**Entrega:** `TurboramaStation-TurboEden-UNICO-v1.0.8.apk`  
**SHA-256:** `5CD234D0AC57AA6F1B260DB6278087B7D961C671385ECF47871570BC00E78814`  
**Tamanho:** 440.660.722 bytes

## O que mudou

Esta versão instala **um único pacote Android**, `org.emulationstation.frontend`, versão `1.0.8-turboeden-unico` (`versionCode` 11), para ARM64 e Android 8.0 ou superior. A entrada exibida no aparelho é **TurboramaStation**. O frontend SDL/EmulationStation, os demais cores Libretro, o catálogo e o tema continuam no mesmo APK. O motor Switch é `libyuzu-android.so` do TurboEden; a biblioteca Suyu não foi incluída.

O fluxo Switch é interno ao mesmo aplicativo:

`TurboramaStation → BootstrapActivity → EmulationActivity → libyuzu-android.so`

A configuração Switch aponta para o **mesmo package ID** da TurboramaStation. O URI `content://` do jogo é fornecido pelo `FileProvider` incluído no APK. `YuzuApplication` inicia o motor nativo; as chaves são copiadas antes da primeira inicialização. A atividade de preparação instala o firmware no diretório NAND configurado, recarrega as chaves, confirma que o motor reconhece chaves e firmware e entrega o jogo à atividade de emulação.

O APK incorpora as duas chaves locais e o pacote com 238 arquivos NCA de firmware encontrados no computador do usuário. Arquivos de dados já existentes são preservados. A primeira preparação precisa extrair cerca de 340 MB; reserve pelo menos 1 GB livre para instalação e dados.

## Composição e conferência

- O pacote final contém **14 bibliotecas nativas ARM64**, inclusive `libmain.so`, `libSDL2.so`, os outros cores do frontend e `libyuzu-android.so`. `libsuyu_libretro_android.so` está ausente.
- Foram reunidas **6.952 classes Java/DEX sem definições de classe duplicadas**. Para as 672 classes comuns aos dois aplicativos, a montagem usa a versão TurboEden. Classes da TurboramaStation que não são usadas pelo frontend foram retiradas; a auditoria estática não encontrou chamadas dos componentes copiados a métodos ou campos ausentes nas classes compartilhadas. A abertura e a renderização inicial de um jogo foram verificadas em aparelho.
- O APK contém o catálogo local, 290 arquivos do tema Turborama, `prod.keys`, `title.keys` e `firmware.zip`. O ZIP interno do firmware contém os 238 NCA e passou pela conferência CRC.
- O manifesto anuncia **uma única atividade de abertura**: `org.emulationstation.frontend.auth.LoginActivity`. `ESActivity`, `BootstrapActivity`, `EmulationActivity`, serviço de downloads e provedores de arquivos estão registrados. O frontend e o motor compartilham um único `FileProvider` para entregar ROMs locais dentro do mesmo pacote.
- O APK passou pela recompilação com Apktool 3.0.3, conferência CRC, alinhamento ZIP e verificação de assinatura Android Debug v2/v3. Certificado SHA-256: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

## Auditoria do download de jogos

A fusão **não alterou o código de transferência** em `HttpBridge` nem o código nativo `libmain.so`. O catálogo, os demais recursos e as bibliotecas do frontend no APK único têm os mesmos bytes da versão TurboramaStation anterior: 460 entradas comparadas, nenhuma diferente ou ausente. O catálogo contém 17.911 itens com URL preenchida, como no snapshot anterior.

O desvio para o catálogo local só atende consultas GET aos caminhos do catálogo com destino em memória. Chamadas que baixam arquivos para um caminho de destino seguem pelo executor HTTP original. Na auditoria do primeiro APK único, foi encontrada uma incompatibilidade na **notificação** do `DownloadService`: ele chamava métodos ausentes na versão da biblioteca AndroidX selecionada na fusão. A revisão atual constrói as notificações pelo Android nativo e inicia o serviço pelo Android nativo, com tratamento para a versão da API. A lógica de transferência, progresso e gravação dos arquivos permaneceu igual.

Essa correção eliminou o erro identificado estaticamente. No ensaio no Samsung SM-A566E, `DownloadService` iniciou como serviço em primeiro plano, atualizou o progresso e **concluiu** o download de um jogo de 6,23 GB. O log do frontend registrou `Download finished ... (installed)`, e o arquivo `.nsp` de 6,2 GB apareceu na pasta Switch. Não houve exceção fatal nem erro de rede nessa transferência.

## Estado de execução

Em 28/09/2026, o APK foi instalado com `adb install -r` em um Samsung SM-A566E (Android 16, ARM64), atualizando a versão 1.0.6 para **1.0.7** sem apagar os dados. O Android confirmou a instalação e iniciou `LoginActivity`; o processo permaneceu ativo. O registro do processo confirmou que `libyuzu-android.so` carregou com sucesso e que o motor nativo iniciou seu registro de versão. Não houve exceção fatal nesse início.

O usuário desbloqueou o aparelho, entrou no frontend e iniciou um download. Com autorização específica do usuário, foram apagados **somente 27 arquivos `.apk`** da pasta de mídia enviada pelo WhatsApp Business; nenhum aplicativo foi desinstalado. A busca posterior confirmou que não restou `.apk` nessa pasta. O download terminou, e a atividade de preparação extraiu cerca de 325 MB de firmware para a NAND do aplicativo.

A tentativa de abrir o jogo na versão 1.0.7 revelou um erro real de integração: `The authority org.emulationstation.frontend.fileprovider does not match ... org.emulationstation.frontend.turboeden.provider`, seguido de `No game found in arguments or intent`. A versão **1.0.8** corrige isso usando o mesmo provedor de arquivos em ambos os lados. Foi recompilada, alinhada, conferida por CRC e assinada com a mesma chave.

Depois que o usuário liberou 2,7 GB, a **1.0.8 foi instalada com sucesso** por atualização (`adb install -r`). O jogo de 6,2 GB e os dados do aplicativo permaneceram no aparelho. O frontend lançou `BootstrapActivity` com um URI `content://org.emulationstation.frontend.turboeden.provider/...`, que abriu `EmulationActivity`. O TurboEden carregou o jogo, inicializou o renderizador Vulkan e exibiu a cena inicial de Animal Crossing New Horizons; uma captura está em `TurboEden-jogo-em-execucao.png`. O indicador na tela chegou a 30 FPS nesse trecho. Assim, **download, preparação do firmware, entrega do arquivo e vídeo foram confirmados de ponta a ponta**. O jogo estava em inglês; a pré-configuração não alterou o idioma do título.

O botão **A** virtual respondeu: após o toque, o diálogo avançou de Timmy para Tommy. O motor abriu uma saída de áudio Oboe/OpenSLES estéreo a 48 kHz nos registros, mas a audição real não foi confirmada. Continuidade por tempo prolongado, salvamento e retorno ao frontend também não foram confirmados. Um alarme do aparelho apareceu temporariamente sobre o jogo durante esse teste. A bateria estava em 3%, ainda carregando pela USB.

Para instalar, use **somente o APK 1.0.8**. Ele tem o mesmo pacote e a mesma assinatura dos APKs de teste TurboramaStation anteriores, com código de versão maior. Uma instalação original assinada por outra chave não pode ser atualizada diretamente. Não desinstale uma instalação anterior sem preservar os dados. Os dados internos do TurboEden instalado como aplicativo separado não são migrados automaticamente; o APK único já traz as chaves e o firmware para a nova instalação.

O tema ativo também foi mapeado em `GUIA-TEMA-TURBORAMA-ANDROID.md`, com uma cópia editável em `TURBORAMA-ANDROID-tema-editavel.zip`. Nenhum arquivo visual foi alterado na 1.0.8.

Este APK contém material privado do usuário (chaves e firmware). Mantenha-o privado; nenhum desses dados foi enviado ao GitHub.
