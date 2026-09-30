# Wii U — Cemu Android 0.5.2 integrado

Estado em 30/09/2026: **APK corrigido instalado e aprovado pelo mantenedor**. O hash no telefone confere. Cemu 0.5.2 inicializou, Mario Kart 8 abriu, a captura mostrou os controles virtuais e o mantenedor confirmou que respondem e que Sair do jogo retorna às plataformas sem novo login. O port Android continua experimental e a licença comercial da TurboramaStation ainda depende do servidor.

## Pedido e origem

O mantenedor pediu atualizar o Wii U para **Cemu 0.5.2**, corrigir os controles na tela e manter um único aplicativo. O APK anterior da TurboramaStation incluía o Cemu 0.5 de SSimco. O doador novo é o [lançamento 0.5.2 de SapphireRhodonite](https://github.com/SapphireRhodonite/Cemu/releases/tag/0.5.2), um fork do port Android. Seu APK oficial é `Cemu.DualScreen.0.5.2.apk`, SHA-256 `e1630fc51a4bbb18ef8499829fad011601d575726f019090abada6c9dd258387`, guardado somente em E:. A licença do Cemu é MPL-2.0; as dependências mantêm suas licenças próprias.

A revisão 0.5.2 contém as funções adicionadas na linha 0.5.1, inclusive opções de armazenamento e telas externas. O lançamento 0.5.2 em si corrige o caminho dos Graphic Packs quando se usa uma pasta personalizada. Isso **não resolve por si só** o controle virtual desabilitado observado no aparelho; a ponte de configuração inicial trata esse defeito.

## O que foi compilado

- `prepare.py` decodifica o doador oficial, aplica o mesmo isolamento de classes e bibliotecas da integração Cemu anterior, compila **todas as classes do 0.5.2** e prepara suas oito bibliotecas ARM64. Os 6.027 identificadores de recursos, seus arquivos e os componentes do manifesto são idênticos aos do doador 0.5; o APK já contém esses recursos, preservados byte a byte.
- `WiiUBootstrap.java` e `build_bridge.py` recompilam a ponte entre a TurboramaStation e Cemu. Na primeira abertura, o GamePad do jogador 1 é habilitado apenas se estiver desativado; o controle fica configurável no menu do emulador. A sobreposição de botões é padrão em uma instalação nova, e preferências já gravadas continuam escolhidas pelo usuário.
- A biblioteca auxiliar DataStore foi reconstruída a partir das funções oficiais AndroidX para exportar os símbolos JNI no namespace isolado `twiiucor`; renomear bytes do ELF mantinha a tabela de hash antiga e falhou em uso. Fonte: `datastore_counter_jni.cpp`, Apache-2.0.
- A correção RAR5 em `../wiiu-rar5-fix-20260930/` permanece: um arquivo íntegro de Mario Kart 8 deixou de ser falsamente tratado como corrompido e abriu com imagem no Cemu anterior. O leitor atualizado ignora entradas de diretório e usa a biblioteca RAR5 corrigida.
- `build_candidate.py` troca as classes Cemu, a ponte, as bibliotecas que mudaram, a ponte RAR5 e o registro de procedência. Carrossel, catálogo, demais motores, recursos e vídeos ficam byte a byte iguais à base, excluindo metadados de assinatura do APK reconstruído.

## APK candidato

| Item | Valor |
| --- | --- |
| Base | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk` |
| SHA-256 da base | `1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7` |
| APK gerado | `E:\ESTUDO APK\work\native-carousel\implementation\emulator-completion\wiiu-052\TurboramaStation-WiiU-Cemu-0.5.2-candidato.apk` |
| SHA-256 gerado | `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b` |
| Tamanho | 1.063.390.870 bytes |

Montagem, alinhamento, assinatura, instalação e hash no aparelho passaram. Comparação entre base e candidato encontrou mudanças somente em `classes19.dex`, `classes20.dex`, `libCemuAndroid.so`, quatro bibliotecas auxiliares Wii U, `libturbo_wiiu_archive.so` e `assets/wiiu-integration/provenance.json`. `build-result.json` permanece em E: com a lista e os hashes. Não há APK, ROM, BIOS, firmware, chaves ou saves no Git.

## Reprodução e diretórios

1. Use a base privada com o SHA acima e o doador oficial com o SHA acima.
2. Execute `prepare.py` deste diretório. Ele lê os mapas de classes/recursos em `E:\ESTUDO APK\work\native-carousel\implementation\wiiu-integration`, gera `wiiu-052\cemu-052-module.apk` e `wiiu-052\libs` em E:.
3. Execute `build_bridge.py`. Ele usa o `WiiUBootstrap.java` deste diretório e `WiiUArchive.java`/`WiiUEntryActivity.java` de `E:\ESTUDO APK\work\native-carousel\implementation\emulator-completion\wiiu-archive-final\java\org\emulationstation\frontend`, e gera `wiiu-052\bridge-dex\classes.dex`.
4. Execute `build_candidate.py`. A biblioteca estática RAR5 em `E:\ESTUDO APK\work\native-carousel\implementation\emulator-completion\vita-rar-diagnosis\libarchive-rar5-eof.a` tem SHA-256 `2ef8d3f3e33ea14430f39da1487d3dc02bebe44e0c35e4c8036e0130ca8c8005`. O patch e o código JNI estão em `../wiiu-rar5-fix-20260930/`.

O Git contém a receita e os diffs. Os APKs e a biblioteca estática privada ficam em E:. As tags estáveis anteriores são imutáveis.

## Conferência para publicação estável

Confirmado no aparelho: `adb install -r` sem limpar dados, hash instalado igual ao APK, processo Cemu 0.5.2 inicializado, GamePad padrão habilitado, Mario Kart 8 aberto e controles virtuais visíveis na captura. O mantenedor confirmou resposta aos botões e retorno às plataformas sem login. Esta conferência cobre um jogo e um aparelho; o port Android continua experimental.
