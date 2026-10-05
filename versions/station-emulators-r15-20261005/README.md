# TurboStations R15 — Neo Geo corrigido e Nintendo 64 completo

## Estado em 05/10/2026

**Compilado, assinado e conferido no PC. Instalação e gameplay no Android pendentes de USB. Não é uma nova versão estável.**

Último APK instalado comprovado: R14, SHA-256 `a1566d3d34305e01f5f445b6b61fb3db4e35fc8a4bc8a2f3e493fb3a433a38bf`. R14B não foi instalado separadamente. O próximo APK reúne R14B, esta correção Neo Geo e o N64 completo.

| Item | Caminho/identificação exatos |
|---|---|
| APK candidato | `E:\ESTUDO APK\work\station-emulators-r15-20261005\TurboStations-NeoGeo-N64-R15-20261005.apk` |
| SHA-256 | `d99b051f50eb3b5069b68fe96e6501b4e3d4a66755ded8489d357789f72a8c5b` |
| Tamanho | 2.036.244.940 bytes |
| Pacote Android | `org.turboramastation.frontend` |
| Namespace do frontend Java | `org.emulationstation.frontend` |
| Certificado SHA-256 | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| Base R14B preservada | `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R14B-20261005.apk` |
| SHA-256 base | `661a8738faf2e598d448017bcb87f09e7d39ac7d2984a653fac4e9a642a9742f` |
| Commit base | `a9a9846ad3a581b46d2d40ba98fbcc2aa697a0d7` |
| Neo Geo: fonte/build | `E:\ESTUDO APK\work\station-emulators-r15-20261005\mame` |
| N64: fonte/build | `E:\ESTUDO APK\work\station-n64-complete-20261005` |
| Frontend candidato | `...\station-n64-complete-20261005\frontend-native` |
| Frontend canônico anterior | `E:\ESTUDO APK\work\station-netplay-20261004\native` permanece R14B |

A base R14B foi copiada para G:, comparada integralmente por tamanho e SHA-256, e somente então a duplicata em E: foi removida para liberar espaço. **Não procurar a base somente no antigo caminho de E:.** Builds, APK novo e temporários ficaram em E:.

## 1. Neo Geo: defeito comprovado e correção

### Evidência anterior à correção

O botão Jogar de Alpha Mission II chegou ao MAME4droid Current 1.41.2 / MAME 0.289. O motor identificou `alpham2`, mas declarou todos os chips NOT FOUND e encerrou. O instalador Station havia colocado o ZIP e `neogeo.zip` juntos no diretório `roms/.station-v2/neo-geo/<item>/install-<id>/content/`.

Os dois ZIPs foram conferidos por CRC: nenhum membro corrompido. Os chips citados como ausentes estavam presentes. Nenhum ROM ou BIOS foi alterado por esta correção.

Dois erros no bootstrap explicam a busca no lugar errado:

1. O app gravava `PREF_ROMsDIR`. O `PrefsHelper.getROMsDIR()` do MAME incorporado lê **`PREF_ROMsDIR_2`**.
2. `romDirFor()` devolvia a antiga pasta genérica `roms/neogeo`, mesmo quando o jogo estava em um artefato Station instalado em outro caminho. O MAME recebe o nome do ZIP e resolve os chips a partir da pasta configurada.

### Código final

- `MameEntryActivity.onCreate`: valida que o arquivo existe e pode ser lido antes de preparar o motor. Falha explícita se o arquivo estiver indisponível.
- `MameBootstrap.romDirFor(path)`: para um arquivo instalado existente, devolve seu diretório pai absoluto. Assim o jogo ZIP fechado e a BIOS ao lado são encontrados pelo próprio MAME.
- `MameBootstrap.seed(context,path)`: grava a chave exata `PREF_ROMsDIR_2`, remove a chave obsoleta, limpa o seletor SAF anterior para esta rota direta e valida a gravação.
- Pasta de instalação/saves já válida é preservada; caso não exista, prepara `files/mame/` dentro do aplicativo.
- Log operacional: tag `TurboMame`, diretório configurado e nome/caminho lançado.

Entrega binária: somente `classes30.dex`. Bibliotecas nativas do MAME, catálogo, download, extração, ROMs, BIOS e saves não foram trocados. Esta correção é do Neo Geo **local**; não libera Neo Geo online nem altera o protocolo das salas.

## 2. Nintendo 64: aplicativo de emulação completo

### Origem verificável

- Projeto oficial: <https://github.com/mupen64plus-ae/mupen64plus-ae>
- Commit: `33bf7021549d7873e976884370fbd1a8e7333bc7`.
- Versão do APK upstream: **3.0.249(beta)**, código 249, mínimo Android 9/API 28.
- Arquivo oficial: <https://github.com/mupen64plus-ae/mupen64plus-ae/releases/download/Pre-release/mupen64plus-ae-master.zip>
- SHA-256 do ZIP: `76a53ca6edbb076e677368284355063dcca48fb08736d7db9584475d075cfaa1`, confrontado com o digest publicado pelo GitHub.
- Asset atualizado em 28/08/2026; não confundir essa data com a criação antiga da release contínua “Pre-release”.
- Código correspondente: <https://github.com/mupen64plus-ae/mupen64plus-ae/tree/33bf7021549d7873e976884370fbd1a8e7333bc7>.

Foram incorporados a interface Android, controles de toque, configurações de vídeo/áudio/input, perfis, saves, núcleo e plugins do pacote oficial ARM64. A escolha não significa desempenho superior comprovado em todos os jogos/aparelhos; esse comparativo não foi realizado.

### Rota de jogo

`Catálogo Station → item instalado → n64CommandHook → n64RunHook → N64Bootstrap.launch → N64EntryActivity → SplashActivity oficial → GalleryActivity oficial → GameActivity/CoreService oficiais`.

- Aliases: `Nintendo 64`, `Nintendo 64 - BR`, `n64`, `n64br`.
- Identificador de despacho: `mupen64plus_ae_android.so`. É um identificador do roteador, não uma biblioteca libretro nova; `n64RunHook` intercepta antes da execução libretro e abre a Activity oficial.
- O identificador anterior `mupen64plus_next_gles3_libretro_android.so` também é reconhecido pelo novo despacho para evitar uma rota antiga em referências existentes.
- A ponte utiliza o campo real `ActivityHelper.Keys.ROM_PATH` do upstream, obtido por reflexão, e repassa o caminho completo do arquivo já instalado. Não abre seletor de jogo nem monta um link externo.
- `GalleryActivity` usa sua leitura de cabeçalho/cache para abrir o jogo. Foi removido somente o `finishAffinity()` prematuro do método `launchGameOnCreation`; o callback original de resultado continua fechando a galeria depois que o jogo sai.
- Controles dentro do jogo são os do Mupen64Plus AE; não foram desenhados controles pelo frontend Station.

### Rota de configurações

`Engrenagem Station → Nintendo 64 → n64SettingsHook → N64Bootstrap.launch(settings=true) → Splash/Gallery oficiais → onOpenDrawerButtonClicked(View)`.

A chamada ao método público abre diretamente o menu de configurações do emulador. Não usa coordenadas nem toques simulados. Todos os controles de configurações permanecem ligados às implementações oficiais.

### Processos, armazenamento e saída

- Interface de preparação/configurações: `:n64`.
- GameActivity/CoreService: `:n64core`, conservando a separação upstream.
- `YuzuApplication.onCreate()` chama `N64Bootstrap.initProcess()` e retorna nos dois processos N64, evitando inicializar os outros emuladores ali.
- `files/n64`, `cache/n64`, `externalFiles/n64`; se armazenamento externo privado não estiver disponível, usa a pasta privada interna.
- SharedPreferences com prefixo **`n64.`**, incluindo preferências gerais e individuais por jogo; não reutiliza as preferências do SNES, Mega ou frontend.
- Na primeira abertura, `gameDataStorageType=internal`; uma escolha posterior válida do usuário é mantida. O bootstrap não força esse valor em toda abertura.
- A preparação oficial extrai os arquivos de `assets/mupen64plus_data`. O início não exige escolher pasta de saves. As permissões efetivamente necessárias ao arquivo instalado continuam sendo verificadas pelo Android e pela ponte.
- Saída normal do GameActivity informa o resultado à Gallery; ao encerrar Gallery, o callback da ponte abre a ESActivity existente com `CLEAR_TOP|SINGLE_TOP`. O core usa seu encerramento oficial. A ponte encerra somente seu próprio processo de interface N64 após o retorno.
- Publicação/varredura de canais Android TV não é executada pelo bootstrap/galeria integrada. A limpeza automática de logcat do Splash upstream foi removida, preservando o diagnóstico.

### Isolamento de classes, recursos e bibliotecas

- Classes upstream `paulscode.android.mupen64plusae` e `com.sun.jna` conservadas para compatibilidade JNI; dependências UI/Kotlin realocadas sob `tn64core`.
- Recursos novos com prefixo `n6_`; todos os IDs públicos anteriores foram preservados.
- DEX 36 e 37: classes oficiais realocadas, com partição equivalente ao donor. DEX 38: ponte N64.
- A única colisão de nome nativo era `libc++_shared.so`. A cópia do N64 foi isolada como `libn64cpp.so`: alterados somente strings `DT_NEEDED`/`DT_SONAME` dos ELFs correspondentes, preservando código, símbolos e relocações. A libc++ anterior do APK ficou intacta.
- Providers privados com autoridades `org.turboramastation.frontend.n64.filesprovider` e `.n64.androidx-startup`.
- Perfis binários `assets/dexopt` do donor não substituem os do app: referem-se a outra partição DEX. O ProfileInstallerInitializer da cópia N64 foi removido; os inicializadores de UI necessários permanecem.

## 3. Preservação da R14B

Na comparação integral com a base, apenas cinco entradas existentes mudaram: `AndroidManifest.xml`, `resources.arsc`, `classes.dex`, `classes30.dex`, `lib/arm64-v8a/libturbo_carousel.so`. Foram preservadas 11.106 entradas e adicionadas 1.970.

`classes35.dex` das salas R12 permanece exatamente `8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae`.

O SO foi compilado de uma cópia da fonte R14B. Permanecem idênticos os arquivos de navegação por `path+kind`, pacing do carrossel visível a 60 fps, vídeo principal a 30 fps, formação quadrada das células, botões, prévias e netplay. Só foram adicionados `native_n64.h`, seu include e os nove destinos de hook.

Não houve alteração de servidor, contratos Station, licenças, capa, catálogo ou download. Não foi feita uma implantação Linux. O APK mantém o certificado; instalar por atualização, sem desinstalar ou limpar armazenamento.

## 4. Testes executados

| Verificação | Resultado |
|---|---|
| Neo Geo: métodos reais de paths/seed, chave comparada ao donor, primeira abertura, repetição e saves | 53 verificações passaram |
| N64: roteador C++ real, configurações e delegação dos demais sistemas | 154 verificações passaram |
| N64: classes, componentes, isolamento, hash oficial, recursos e lifecycle | 127 verificações passaram |
| N64: preparação real de armazenamento/preferências, escolhas persistentes e pasta inválida | 49 verificações passaram |
| Compilação Java/DEX, recursos e JNI ARM64 | Concluída |
| Assinatura original e alinhamento ZIP/SO 16 KiB | Conferidos |
| Hash de cada entrada, mídia e DEX das salas preservados | Conferidos |
| Neo Geo e N64 no aparelho após a correção | **Pendente** |
| Retorno à mesma coleção / fluidez sem toque no aparelho | **Pendente** |

Os testes locais não comprovam renderização, áudio, toque ou desempenho Android. Não marcar estes itens como aprovados somente porque o APK compilou.

## 5. Próxima conferência no aparelho

1. Confirmar USB autorizada, tela desbloqueada e frontend nas plataformas. Não encerrar partida ativa sem autorização.
2. `adb install --no-incremental -r --user 0 <APK R15>`; nunca desinstalar/limpar dados para resolver preparação.
3. Conferir SHA-256 do `base.apk` instalado.
4. Alpha Mission II → Jogar: sem pergunta de pasta; log `TurboMame` aponta para `content` exato; ausência de chips NOT FOUND. Repetir com outro Neo Geo instalado para testar a troca de diretório.
5. Nintendo 64 pela engrenagem: menu próprio; controles e opções próprios. Abrir jogo instalado pelo catálogo, testar resposta dos controles e saída normal sem login.
6. Abrir/voltar de uma coleção e verificar mesma seleção. Observar vídeo/animação sem tocar. Preservar o trabalho R14B.
7. Registrar atividades, versão/hash, falhas e evidências reais. Caso precise corrigir algo no telefone, incorporar a mesma correção à fonte e ao APK, sem deixar configuração manual indispensável.

## 6. Reprodução e manutenção

O diretório desta versão contém fontes da ponte, do MAME corrigido, roteador/cópia do frontend alterado, scripts de compilação, mapa de realocação e recibos. Leia `BUILD.md` para a ordem e entradas privadas. **Não executar scripts históricos de empacotamento sobre uma base diferente e não promover os snapshots automaticamente.**

Ferramentas usadas: JDK 17.0.20, apktool 3.0.3, build-tools 35.0.0, android.jar API 34, NDK r28c/sysroot ARM64 e LLVM local. O APK oficial usa APIs mínimas 28; a Station permanece minSdk26 e mostra mensagem explicativa ao tentar abrir este N64 em Android anterior a 9.

Não publicar APK, ROM, BIOS, logs privados, mídia, credenciais ou assinatura privada no Git. Preservar as licenças e atribuições upstream; o código fonte oficial permanece identificado pelo commit exato acima.
