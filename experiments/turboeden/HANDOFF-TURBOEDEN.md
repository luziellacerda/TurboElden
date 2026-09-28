# Handoff — TurboEden para testes

**Data:** 2026-09-28  
**Entrega:** `TurboEden-teste-assinado.apk`  
**Status:** montagem, alinhamento e assinatura verificados; instalação e execução em dispositivo ainda não realizadas.

## Resultado

A versão de teste mostra **TurboEden** como nome do aplicativo. O identificador Android foi alterado para `dev.turboeden.turboeden_emulator`, de modo que esta instalação use um espaço de dados separado do pacote de origem. As referências explícitas a esse identificador em manifesto e Smali foram atualizadas, incluindo providers e a ação de lançamento com configuração personalizada. Textos localizados que exibiam o nome anterior foram alterados em 23 arquivos `strings.xml`. O banner para Android TV foi refeito com o texto **TurboEden**.

| Item | Valor da entrega |
|---|---|
| APK | `TurboEden-teste-assinado.apk` |
| Tamanho | 25.369.381 bytes |
| SHA-256 | `2D40E60CC58E1AEECCEB176868F9FCC344E111E90FEC354EBECBD113255CD342` |
| Package ID | `dev.turboeden.turboeden_emulator` |
| Nome exibido | `TurboEden` |
| versionCode / versionName | `32873047` / `1f6734c` |
| minSdk / targetSdk | 24 / 36 |
| ABI | `arm64-v8a` |
| Assinatura | Certificado Android Debug local; SHA-256 `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |

## Conferências realizadas

- A montagem pelo Apktool 3.0.3 terminou sem erro.
- `aapt` confirmou package ID, nome exibido, atividade inicial, SDK e arquitetura.
- `zipalign` confirmou o alinhamento do APK.
- `apksigner` validou os esquemas de assinatura v2 e v3.
- As sete bibliotecas `.so` ARM64 dentro da nova APK têm os mesmos bytes da APK de origem.
- O `classes.dex` da nova APK contém o identificador novo e não contém o identificador antigo como texto literal.
- Nos arquivos localizados `strings.xml`, não restou a palavra isolada com grafia antiga; os nomes visíveis usam **TurboEden**.

## Limites da substituição

O motor `libyuzu-android.so` permanece o binário original. Ele contém nomes de símbolos, logs, nomes de arquivos e referências à marca do projeto de origem. Trocar bytes dessa biblioteca por uma palavra maior sem recompilá-la pode corromper o executável; portanto esses registros internos não foram adulterados. Os nomes técnicos de recursos e classes legados foram mantidos quando mudá-los não alteraria o texto visto pelo usuário e poderia quebrar referências compiladas.

Os endereços de documentação, site, repositório e atualização ainda apontam para o projeto de origem. Substituí-los por endereços inventados produziria links inválidos. O atualizador embutido depende do serviço de origem e sua compatibilidade com o novo package ID **não foi testada**. Para uma substituição integral também no motor e nos serviços, é necessário recompilar o código C++ e Android da revisão correspondente, configurar serviços próprios e validar o resultado em aparelho.

O nome novo e o package ID **não transformam a arquitetura**: este aplicativo continua sendo um emulador de Nintendo Switch, não um conjunto de cores Libretro. A versão assinada localmente é uma APK experimental; o teste funcional ainda deve cobrir abertura, permissões, importação de dados próprios, execução de jogo, controles, GPU, providers e atualização.

## Proveniência e continuação

A base examinada foi `TurboramaEmuTestes.apk`, identificada internamente como Eden/Yuzu. O [handoff da auditoria original](HANDOFF-COMPLETO-TURBORAMA-EMU-TESTES.md) conserva os dados forenses, o mapa de funções e os hashes antes da mudança de marca. Há uma [tag pública v0.2.1 do código-fonte](https://github.com/eden-emulator/mirror/tree/v0.2.1), associada ao build ID `1f6734c` em um [relato do projeto](https://github.com/eden-emulator/Issue-Reports/issues/671); a correspondência byte a byte deste APK com uma release oficial ainda não foi demonstrada.

Para prosseguir com uma edição integral do programa, use essa tag como base de investigação, compare a APK original com a release oficial, construa Android/C++ com as dependências compatíveis e execute os ensaios em dispositivo ARM64/Vulkan. Preserve atribuições e licenças do código de origem na distribuição.
