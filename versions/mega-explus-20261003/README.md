# Correção dos controles — candidato 8f494041

A revisão `e87a352b…` abaixo abriu MD.emu, mas foi rejeitada: seus controles carregavam a configuração compartilhada anteriormente usada pelo SNES. O motor era MD.emu; o defeito era o arquivo de opções comum. Não distribuir essa revisão como concluída.

Correção compilada: `TurboStations-SNES-Mega-CONTROLES-CORRIGIDOS-20261003.apk`, SHA256 `8f494041ca4ae37fbd8becb50a1a7156ea2141e717af41452e5a1a923e0799b0`, em E:\ESTUDO APK\work\station-mega-explus-20261003. Instalado por atualização; hash lido do telefone igual. `evidence/storage-installed.json` registra16 testes de isolamento aprovados e `evidence/storage-runtime.json` registra Cutthroat Island em execução com direcional, A/B/C e Start na disposição própria do Mega, sem as posições/botões vazios do SNES. Não foi testado cada botão individualmente, salvar/carregar ou a saída após esta última correção. Não promovido a estável.

Causa comprovada: `imagine/src/base/android/ApplicationContext.cc`, linhas38–49, usa `ANativeActivity.internalDataPath` no Android>=11; o método helper `filesDir()` só é usado antes de API11. Android `NativeActivity.onCreate()` passa `getFilesDir()` e `getExternalFilesDir(null)` para o nativo. A primeira ponte só havia adaptado o helper e por isso não isolava o arquivo real.

`fix_native_storage.py` adiciona os overrides reais `getFilesDir/getCacheDir/getExternalFilesDir` em AMBAS as atividades. As pontes resolvem a raiz pelo `Application` para evitar recursão. O config compartilhado anterior fica intocado e não é importado automaticamente para nenhum motor. Cada um começa com seus próprios controles padrões e preserva suas opções futuras em diretórios diferentes. As receitas de reconstrução completas também receberam os overrides.

`package_storage_fix.py` exige o APK e87a352b, recompila/substitui apenas os quatro DEX de SNES/Mega e avisos de fonte. Manifesto, todas as bibliotecas nativas, jogos, recursos visuais e módulos Station ficam idênticos. Sem alteração manual do telefone. Teste de regressão em `StorageIsolationDeviceTest.java` usa somente uma pasta temporária isolada.

Evidência do Android: https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/app/NativeActivity.java (loadNativeCode/getFilesDir).

---

## Histórico da integração anterior (com defeito de isolamento)

# Mega Drive completo — MD.emu 1.5.85

## Entrega

Solicitado pelo mantenedor após a integração SNES: Mega Drive com controles do próprio emulador e suas configurações acessíveis no painel.

APK candidato: `E:\ESTUDO APK\work\station-mega-explus-20261003\TurboStations-SNES-Mega-EXPlus-20261003.apk`

SHA256 **`e87a352bc61ce6b2f120d4657451471313a1e4e7671e37c572d9904fcc1ef7be`**, 1.910.248.068 bytes. Compilado, assinado e instalado por atualização. Hash lido do APK no telefone confere; recibo em `evidence/installed.json`. Host voltou às plataformas; painel e jogo do MD ainda aguardam conferência. Não promovido a estável.

Base imediata: APK SNES `62377e8d55617a9d0aefaed42d0b1a17948f9c5997b7be713dc760c4420f8c25`. Recuperação estável original: `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`. A base SNES abriu Battletoads em processo próprio e seus controles oficiais foram vistos; esse teste não comprova controles/menus do Mega nem todas as funções de salvar/retornar.

## Motor e interface completos

MD.emu oficial **1.5.85**, versionCode16010585, artefato `Pre-release`, commit **`1c12fac5ce49badaadff2e2f210dcc30b89f4943`**. Proveniência, URL e hash do download em `evidence/upstream-provenance.json`. Não descrever como release estável upstream.

O motor, renderizador, menus de vídeo/áudio/sistema, controles de toque e configuração de entrada são do MD.emu. Não se desenhou controle do frontend por cima do jogo. O conjunto inteiro do Android upstream foi incorporado, com adaptações de integração descritas abaixo; o C++ upstream não foi recompilado nesta entrega.

Fonte oficial: https://github.com/Rakashazi/emu-ex-plus-alpha/tree/1c12fac5ce49badaadff2e2f210dcc30b89f4943

Página oficial: https://www.explusalpha.com/contents/md-emu

## Isolamento do SNES

O DEX original do MD.emu é byte a byte igual ao do Snes9x EX+ da mesma revisão. A imagem `gpOverlay.png` dos controles é diferente. Compartilhar essa imagem sobrescreveria os botões de um dos emuladores.

Por isso a integração preserva:

| Recurso | SNES | Mega Drive |
| --- | --- | --- |
| Atividade | `com.imagine.BaseActivity` | `com.mdimagn.BaseActivity` |
| Processo | `:snes` | `:megadrive` |
| Biblioteca | `libsnes9x_explus.so` | `libmdemu_station.so` |
| Imagem original dos controles | `assets/gpOverlay.png` | `assets/mdOverlay.png` |
| Configuração interna | `files/snes-explus/config` | `files/mega-explus/config` |
| Cache | `cache/snes-explus` | `cache/mega-explus` |
| Extra de lançamento | `station.snes.path` | `station.mega.path` |

Todos os shaders e `ui.png` foram comparados com os do SNES e são idênticos. Não se sobrescreveu nenhum recurso anterior. Classes auxiliares do MD foram isoladas em `tsmd/`; o SNES permanece intocado.

## Adaptação nativa exata

Biblioteca oficial MD SHA256 `79a4b7409044d34318255df35132b313617cb0aa485928e259cace945c909906`.

Biblioteca integrada SHA256 `636a50b0901afd3ebd5586883cc49277307cb7525ca1cc23744139168b8ff171`.

As diferenças são somente nove constantes em `.rodata`: oito descritores JNI `com/imagine` → `com/mdimagn` e o nome `gpOverlay.png` → `mdOverlay.png`. Substituições de tamanho idêntico, contagem e offsets registrados em `evidence/native-relocations.json`. Todos os bytes executáveis permanecem idênticos. Nenhuma rotina de emulação ou preset de desempenho foi alterado. `prepare.py` recusa contagens diferentes, localização em seção executável ou qualquer byte modificado fora dessas posições.

## Rotas do aplicativo

- `megaCommandHook` mapeia `MegaDrive`, `MegaDrive - BR`, `Mega Drive`, `megadrive`, `megadrivebr` e `genesis` para o identificador interno `mdemu_station.so`.
- O formato de comando continua o reconhecido pelo launcher original. A execução é interceptada por `megaRunHook` → `MegaBootstrap.launch(Activity, caminho, false)`, que abre a atividade completa MD.emu; não executa o runner Libretro para Mega.
- Flags nativas de motor embutido/instalado/recursos preparados reconhecem o novo identificador. Nenhum pacote de core antigo é solicitado para essa rota.
- **Configurações → Mega Drive** chama `megaSettingsHook` → `MegaBootstrap.launch(Activity, "", true)`, dando acesso ao menu original do MD.emu.
- O caminho de jogo real entregue pela instalação Station é validado como arquivo legível e não vazio; depois é consumido uma vez pela API original `intentDataPath`/`DocumentPickerEvent`.
- Ao entrar, as rotinas existentes suspendem vídeo do carrossel e música. `YuzuApplication` retorna cedo somente em `:megadrive`, antes de inicializar outros motores.
- A atividade é interna/não exportada. Ao sair normalmente, a ponte retorna à `ESActivity` já existente antes de o destrutor nativo encerrar apenas `:megadrive`.
- Não há alteração no servidor, licença, catalogação, instalação de jogos, recibos, busca ou mídia das plataformas.

**Genesis Plus GX antigo permanece no APK porque Master System, Game Gear e SG-1000 ainda dependem dele.** Ele não é o novo motor do Mega. Sega32X mantém PicoDrive. Os testes de rota incluem essas exclusões; não apagar a biblioteca compartilhada como se fosse exclusiva de Mega.

## Configurações e arquivos do cliente

Diretórios internos são preparados automaticamente e de forma idempotente no APK. Nada depende de criar pastas pelo computador. Cada emulador guarda suas opções em diretório próprio. A base Android continua API26; detecção de processo tem alternativa para API26–27.

Não se migrou nem converteu estados rápidos antigos do Libretro. Não se apagou save, ROM, configuração, licença ou identidade Keystore. Antes de alegar compatibilidade de SRAM/estado anterior, comparar formato e caminho realmente usados; a captura de um título não comprova isso.

## Construção e evidências

Fontes e temporários canônicos: `E:\ESTUDO APK\work\station-mega-explus-20261003`.

- `prepare.py`: valida artefato upstream, adapta namespaces/descritores/atlas, compila Java e DEX, manifesto e roteamento nativo. Depende das entradas verificadas da integração SNES e da base privada; não declarar checkout Git autossuficiente.
- `package.py`: exige o hash da base SNES; altera apenas manifesto, `classes.dex` e `libturbo_carousel.so`, adicionando módulos MD. Alinha e assina com a mesma identidade local, sem publicar a chave.
- 10.830 entradas da base preservadas; nenhum arquivo preexistente removido; 46.566 definições DEX, zero duplicatas.
- Classes/motor/controles SNES, motores restantes, recursos e mídias preservados byte a byte. O único arquivo de classe preexistente a adaptar é `YuzuApplication` para a inicialização de `:megadrive`.
- `route-test.cpp` é gerado a partir das funções de seleção reais e foi compilado para Android: 30 casos de seleção do Mega/BR e exclusão das outras plataformas. Após reconectar, executou no Android com `PASS 30 native Mega routing checks`; binário temporário removido. O teste não iniciou jogos nem alterou dados do app.
- Hash e relatório do APK: `evidence/build-result.json`. Testes de jogo, painel, salvar/carregar, controles e retorno dependem de validação no telefone, não da compilação.

## Licenças e recuperação

GPLv3 e proveniência oficial incluídas no APK. Créditos e obrigações dos componentes upstream permanecem. As limitações específicas de distribuição do SNES, já integrado, constam no handoff SNES; não confundir teste local com autorização comercial.

Para recuperar, instalar por atualização o APK SNES anterior ou a estável original com a mesma assinatura, preservando dados. Não desinstalar, não limpar armazenamento, não mover tags estáveis. A ampliação para 40 mil jogos continua em revisão separada.
