# Correção posterior obrigatória — controles isolados

A integração inicial62377e8d reproduziu o SNES, mas a separação das configurações não cobria NativeActivity.getFilesDir(). Isso permitiu compartilhar o config com MD.emu adicionado depois. A correção está no candidato8f494041 e nas receitas atuais de SNES/Mega. Ler primeiro `../mega-explus-20261003/README.md` e os recibos `storage-*`. Não reutilizar a receita anterior sem os overrides reais. O arquivo compartilhado antigo foi preservado e não é importado automaticamente.

---

# SNES completo — Snes9x EX+ integrado, 03/10/2026

## Estado e escopo

Pedido: usar os controles do próprio emulador e acessar suas configurações pelo painel da TurboStations. Integração baseada na estável `97938400d3fa82d5d1564445c36fc70328add1c4`, sem misturar o candidato de 40 mil jogos.

APK gerado e instalado por atualização, sem desinstalar ou limpar dados:

`E:\ESTUDO APK\work\station-snes-explus-20261003\TurboStations-SNES-EXPlus-20261003.apk`

SHA256 `62377e8d55617a9d0aefaed42d0b1a17948f9c5997b7be713dc760c4420f8c25`, 1.903.595.552 bytes. Hash conferido diretamente no APK instalado. Assinatura anterior preservada: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

**Ainda não promovido a estável.** A abertura da TurboStations após atualizar chegou à `ESActivity`, mantendo a sessão. Conferência da interface própria, controles em jogo, salvamento e saída do SNES depende dos registros em `evidence/runtime.json`; enquanto esse arquivo não confirmar, não declarar esses fluxos aprovados.

## O que está incorporado

- Snes9x EX+ **1.5.85**, artefato oficial `Pre-release`, commit `1c12fac5ce49badaadff2e2f210dcc30b89f4943` de 13/04/2026. Não chamar esse artefato de release estável upstream.
- Biblioteca ARM64 oficial preservada byte a byte, renomeada de `libmain.so` para `libsnes9x_explus.so` para coexistir com o frontend. SHA256 `2f39f4ea597c054d7696f04ac679b1a3d97d63fcf6df345fa0877ca0f0ffa293`.
- `com.imagine.BaseActivity`, renderizador, menus, controles de toque, configuração de gamepad, áudio/vídeo e salvar/carregar são do EX+.
- Recursos originais `gpOverlay.png`, `ui.png`, shaders e homebrew distribuído pelo upstream; nenhuma ROM comercial foi adicionada.
- Processo interno `org.turboramastation.frontend:snes`; não depende de instalar um segundo aplicativo.
- Antigo `libsnes9x_libretro_android.so` removido **do novo APK**. Não apagamos cores, saves ou configurações existentes no armazenamento do cliente.

## Rotas e chamadas

1. Catálogo e instalação Station continuam byte a byte na versão estável. Seus IDs, recibos e caminho de lançamento não foram alterados.
2. A seleção SNES/SNES BR mantém a identificação `snes9x` que o launcher nativo já usa. O novo `snesRunHook` intercepta essa identificação e chama `SnesBootstrap.launch(Activity, path, false)`; não executa o runner Libretro para SNES.
3. O painel **Configurações → Super Nintendo** chama `snesSettingsHook` → `SnesBootstrap.launch(Activity, "", true)`, abrindo o menu original do EX+. As opções reais ficam nos menus nativos de vídeo, áudio, sistema e entrada do emulador.
4. O caminho é passado por extra interno `station.snes.path`, consumido uma única vez em `BaseActivity.intentDataPath()`. O evento original `DocumentPickerEvent` abre o jogo. O seletor de arquivos original continua funcionando; não se usa `file://` entre atividades.
5. Ao entrar, `stopSystemVideo()` e `pauseRetroMusicForGame()` suspendem a mídia do frontend conforme o mecanismo existente.
6. A atividade não é exportada. O manifesto declara `android.app.lib_name=snes9x_explus`, `singleInstance`, processo `:snes` e tema Android sem recursos duplicados.
7. `YuzuApplication.onCreate()` verifica o processo SNES imediatamente após `super.onCreate()`. Nesse processo prepara as pastas e retorna antes de iniciar os outros motores.
8. Na destruição por saída explícita, a ponte traz a `ESActivity` existente para frente antes de `NativeActivity.onDestroy()`. O destrutor oficial encerra somente o processo SNES. Não se apaga sessão nem se abre o login deliberadamente.

## Configurações e saves

Preparação embutida, idempotente e preservando conteúdo:

- `files/snes-explus/`: diretório interno fornecido ao native; arquivo `config` do EX+ e suas opções próprias.
- `cache/snes-explus/`: cache isolado.
- SRAM `.srm`: comportamento original EX+ usa a pasta do jogo por padrão, ou a pasta selecionada pelo usuário nos menus próprios.
- Estados rápidos do Libretro e EX+ não têm conversão implementada. Não prometer compatibilidade dos estados anteriores. Arquivos existentes são preservados.

Nenhuma criação manual de pasta no telefone é necessária. As duas pastas são preparadas tanto pelo launcher quanto pela primeira inicialização do processo. A versão mínima do host continua Android 8/API26; identificação do processo tem alternativa para API26–27.

## Reprodução e base exata

Todos os temporários e compilações em `E:\ESTUDO APK\work\station-snes-explus-20261003`.

Base privada congelada:
`E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk`

SHA256 `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`.

A fonte original em `native-carousel/implementation/native_carousel.cpp` possuía um hook posterior do nome do jogador que não estava na biblioteca estável. Ele foi retirado **na cópia isolada**, e a compilação reproduziu integralmente o SHA256 nativo estável `523eb3b3c87c53834ea172091aa2c9826874e7a3956077b1269069901283da24`. Não reaplicar esse hook como parte da integração SNES.

Baseline recuperada: `native/native_carousel.recovered-stable.cpp`; biblioteca comprobatória: `native/recovered-stable.so`. Dependências e hashes em `evidence/native-sources.json`. A alteração funcional do frontend é incluir `native_snes.h` e trocar três destinos de hooks: runner `0x2a9718`, definições `0x2a6850` e painel `0x2228f8`. Os demais continuam na cadeia da estável.

`prepare.py` recompila Java/DEX, copia e adapta o Java oficial em smali, gera manifesto e compila o módulo nativo. `package.py` parte exclusivamente da base por hash, adiciona módulos, verifica classes duplicadas e preservação dos demais arquivos, alinha e assina com a identidade local existente. O Git não contém base APK, chave privada, binários ou todos os recursos privados necessários: não afirmar build autossuficiente apenas do checkout.

Entradas locais adicionais: `official-decoded`, `host-decoded` (somente `classes.dex` da base), `manifest-decoded` (somente manifesto e recursos da base), fonte oficial pinada e headers nativos inventariados. Scripts não são um convite para usar fontes históricas com hashes diferentes.

## Verificações realizadas

- Baseline nativa reproduzida byte a byte antes da mudança.
- 46.499 definições de classes, zero duplicatas. Helpers obfuscados `a/`, `b/`, `c/` e suporte de anotação do doador isolados em `tsnes/`.
- Única classe preexistente modificada: `YuzuApplication` para a inicialização do processo SNES. Inventário smali comparado.
- 10.809 entradas da base idênticas; outros motores, mídias, `resources.arsc` e DEX do Station preservados.
- Entradas preexistentes alteradas: `AndroidManifest.xml`, `classes.dex`, `libturbo_carousel.so`; nova atividade e dois DEX adicionais.
- Assinatura e alinhamento de 16 KiB conferidos. APK instalado com `adb install --no-incremental -r --user 0`; hash lido do telefone igual ao arquivo local.
- Abertura do host após atualização chegou às plataformas. Battletoads abriu em :snes e os controles originais foram vistos na captura. Resposta dos botões, salvar/carregar, painel de configurações e retorno ainda não foram confirmados.

## Licenças e distribuição

Avisos originais `Snes9x/COPYING` e `COPYING.GPL` preservados no APK, junto da proveniência e fonte da ponte. O núcleo contém condições de uso não comercial; o wrapper/framework usa GPLv3 e a exceção de combinação descrita pelo autor se restringe ao release oficial sem modificações. Esta integração modifica o Java do wrapper. Não tratar o APK de teste como produto comercial liberado para distribuição sem resolver as permissões e obrigações dessas licenças com os titulares. Não retirar créditos nem aplicar regras privadas do projeto ao código de terceiros.

Origem oficial: https://github.com/Rakashazi/emu-ex-plus-alpha/tree/1c12fac5ce49badaadff2e2f210dcc30b89f4943

## Recuperação

A tag estável e o APK `3b355b02…` continuam intactos. Para voltar, atualizar com esse APK, mesmo pacote/assinatura/versão, usando `-r`. Não desinstalar nem limpar dados. As configurações próprias novas ficam isoladas e não sobrescrevem as opções Libretro anteriores. O candidato de 40 mil jogos e o servidor não foram modificados.
