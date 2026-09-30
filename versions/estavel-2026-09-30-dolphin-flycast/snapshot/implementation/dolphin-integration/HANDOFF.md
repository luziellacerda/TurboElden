# Estado aprovado — 30/09/2026

Esta versão substitui os estados intermediários registrados abaixo. O usuário confirmou funcionamento e pediu publicação como estável. APK final SHA256: 55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85. Tag: estavel-2026-09-30-dolphin-flycast.
Dolphin: configurações abriram; usuário confirmou jogo Wii e retorno sem login. Flycast: Sonic funcionando conforme usuário; retorno nativo e fundo observados; correção de toque aprovada com “tudo ok”. Não houve benchmark prolongado nem validação de todos os jogos. BIOS ficam privadas. O candidato posterior 3085d9fc não foi instalado e não integra esta entrega.

## Registro histórico da implementação (estados e pendências abaixo são da época)

# CONFIRMADO PELO USUÁRIO — jogo e retorno às plataformas com Dolphin novo

Em 30/09/2026, o usuário respondeu "O jogo abriu" à solicitação de abrir um jogo Wii pelo botão Jogar da TurboramaStation. Nome do jogo não informado. A consulta USB posterior não encontrou aparelho; não foi possível observar a partida, medir desempenho ou coletar registros durante o jogo.

APK instalado: E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Dolphin-2609-7.apk
SHA256: 5bce795e714ce943d887dd127bfb28c501b8fc55b2f748520348c705ed30dc03

A tela de configurações e a inicialização do motor já foram observadas diretamente nesta revisão. A abertura do jogo está confirmada pelo relato do usuário. O usuário também confirmou explicitamente: "Voltou às plataformas sem pedir login". A abertura do jogo e o retorno com sessão preservada estão confirmados pelo usuário; a partida e o retorno não foram observados via USB. Desempenho prolongado não medido. Não declarar estabilidade de todos os jogos.

Evidências: dolphin-integration/user-game-confirmation.json, settings-latest.png, settings-confirmed-logcat.txt e settings-confirmed-activities.txt. Fontes, montagem e instalação: dolphin-integration/HANDOFF.md, build-result.json e installed.json.

Motor Dolphin antigo removido; outros motores, design e dados preservados. Sem nova compilação, reinstalação ou alterações de configuração nesta conferência. Git estável não promovido/publicado.

---

# Dolphin incorporado — substituição do motor antigo

## Escopo autorizado

O usuário solicitou substituir o Dolphin desatualizado já incorporado à TurboramaStation pelo Dolphin oficial atual, incluindo controles e configurações próprios. Explicitou um único APK e remoção do motor antigo. Outros motores e o design existente devem ser preservados. Compilar e usar temporários em E:.

## Localização exata

- Implementação: `E:\ESTUDO APK\work\native-carousel\implementation`
- Integração: `E:\ESTUDO APK\work\native-carousel\implementation\dolphin-integration`
- APK: `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Dolphin-2609-7.apk`
- Estado real, hash e instalação: `dolphin-integration/build-result.json` e `installed.json`. Consultar os dois; geração e instalação são etapas distintas.
- Base preservada: `TurboramaStation-pesquisa-corrigida.apk`, SHA256 `2cf4758572b98968e4ea3835e055f746e218795c059d71060a89522fedae25e6`.
- Fontes originais do frontend anteriores à integração: `dolphin-integration/before`.
- Fonte oficial correspondente: `dolphin-integration/source`, commit `5102a0339c2177575378107b76541e47cc52122d`, Dolphin **2609-7**.

## Proveniência

Motor e interface Java originais vêm do APK oficial `dolphin-official-2609-7.apk`. Seu SHA256 é `d6b82232433ceed56c8745f3064244e54317a12176d03c96bce9e99d4481d6e9`. Não afirmar que o motor C++ foi recompilado do fonte: compilamos a integração e reaproveitamos o binário oficial. A árvore Git correspondente foi clonada para comparação e manutenção.

- https://github.com/dolphin-emu/dolphin
- https://dolphin-emu.org/download/dev/5102a0339c2177575378107b76541e47cc52122d/
- https://dl.dolphin-emu.org/builds/3a/73/dolphin-master-2609-7.apk

O Dolphin separado no celular era **2609**, versionCode43092. Não foi desinstalado, alterado nem usado como dependência. Seus arquivos privados não foram importados. Licenças upstream e fontes da integração acompanham o APK em `assets/dolphin-integration`; nenhuma restrição privada se sobrepõe às licenças de terceiros.

## Arquitetura

1. `native_dolphin.h` intercepta relocações verificadas do frontend para a rota Dolphin; não substitui instruções do `libmain.so` original.
2. O botão Jogar chama `DolphinBootstrap.launch` no mesmo pacote Android. Não abre outro aplicativo nem usa coordenadas.
3. `DolphinEntryActivity` roda no processo interno `:dolphin`; aguarda a inicialização real dos diretórios. Em seguida usa o método de abertura oficial, incluindo suas verificações, ou o menu de configurações oficial.
4. `YuzuApplication.onCreate` somente desvia a inicialização no processo `:dolphin`. O processo principal conserva a inicialização original. O delegado `DolphinApplication` registra seu rastreador de atividades no Application real.
5. Dependências AndroidX/Kotlin/Material são realocadas para evitar conflito com o Switch. Nomes JNI `org.dolphinemu.dolphinemu` ficam preservados.
6. Recursos do Dolphin recebem prefixo `td_` e novos IDs. IDs originais do frontend permanecem. Bibliotecas auxiliares do Dolphin recebem nomes exclusivos.
7. `libdolp.so` contém o motor oficial Android. A troca dos nomes internos de bibliotecas e de uma referência JNI AndroidX tem comprimento constante; algoritmos da emulação não foram alterados.
8. Removidos do APK `lib/arm64-v8a/libdolphin_libretro_android.so` e `assets/packs/Dolphin.zip`. Não há fallback para o motor antigo. A inicialização também remove cópias baixadas desse binário específico das duas pastas de cores conhecidas. Não remove saves, configurações ou os motores de outros sistemas.
9. O processo do frontend recebe pausa normal do SDL quando perde a tela. Vídeos e música são parados na abertura. Nenhum desempenho sustentado foi medido.

## Dados

- Usuário Dolphin novo: `Android/data/org.emulationstation.frontend/files/Dolphin`.
- Sys e drivers internos: `<filesDir>/Dolphin`; cache separado `<cacheDir>/Dolphin`.
- Preferências Android: nome próprio com sufixo `_dolphin_preferences`.
- Saves nativos antigos encontrados no aparelho: `EmulationStation/.emulationstation/saves/User`, incluindo GC e Wii. A migração copia arquivos ausentes de GC, Wii, GBA, WFS e Triforce, preservando os originais. Não sobrescreve saves já existentes no destino.
- Configurações Libretro, shaders e estados rápidos antigos não são aplicados ao motor novo. Permanecem preservados na origem. Não prometer compatibilidade entre estados rápidos de versões diferentes.

## Compilação reproduzível

Executar nesta ordem em `dolphin-integration`:

1. `prepare.py`: parte de `frontend-decoded` e `dolphin-decoded`, recria `merged`, isola classes/recursos/bibliotecas.
2. `integrate.py`: aplica bootstrap, diretórios separados e compila as classes de integração para `bridge-dex`.
3. `native_patch.py`: registra as rotas; depois `../build_native.py` compila o módulo nativo.
4. Apktool 3.0.3: compilar `merged` para `merged-template.apk`, usando `framework` e temporários `tmp` desta pasta.
5. `package.py`: preserva classes2–9 e demais motores da base; integra classes10–12, novos recursos e Dolphin; alinha em 16KiB e assina com a mesma chave local. Gera `build-result.json` com as entradas alteradas/adicionadas/removidas.
6. Antes de `install.py`, observar uma captura recente `preinstall.png` e confirmar que não há partida ativa. Atualizar com `install -r`, nunca desinstalar nem limpar dados. O instalador confere o SHA256 instalado.

`prepare.py` é anterior às alterações de `integrate.py`; executá-lo novamente exige reaplicar `integrate.py`. Não copiar o antigo arquivo `libdolphin_libretro_android.so` que pode restar na pasta temporária `merged`: o empacotador o exclui explicitamente.

## Falha encontrada na primeira abertura

Primeiro APK, hash `13584abd296dd2319028d8cf8609183395291e7486f8c19acde469cd1382250f`, foi instalado e rejeitado na conferência: `VerifyError` em `tdolphin.lifecycle.LiveData$1`. A expressão usada para realocar descritores capturava nomes de campos que continham `L`, deixando alguns tipos de campos com o namespace antigo. A correção restringe o padrão aos caracteres válidos de descritores e verifica que não ficou nenhuma referência de tipo antiga. Registro: `first-runtime-error.txt` e `build-first-rejected.json`.

Compilar, assinar e instalar não comprovam jogo funcionando. Não declarar validação de partida, desempenho ou aprovação visual antes de obter evidência. Git estável não foi promovido nem alterado por esta tarefa.

## Segunda conferência — 30/09/2026 09:17

Motor oficial inicializou e migração dos saves nativos concluiu (GC 22K, Wii 331K, origem preservada). Configurações ainda falharam com NoSuchMethodError: um stub da API Android OnBackInvokedCallback foi realocado indevidamente. prepare.py agora preserva nomes dos nove stubs do framework Android e evita duplicação com os presentes no frontend. Nova compilação em andamento. Evidências: back-api-error.txt, runtime-observation.json e build-back-api-rejected.json. Não confundir inicialização do motor com partida testada.
