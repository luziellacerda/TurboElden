# R136 — contenção do ANR gráfico no moto g52

## Estado comprovado

A R136 foi compilada a partir do APK R135 exato e assinada com o certificado original. **A candidata** de SHA-256 `69d4103d86b7551f7f682d39e2ee52b01c326a92e48a0c3ca866e2550b8f2436` foi instalada somente no moto g52 em 12/10/2026: hash integral, UID, data original de instalação e diretório de dados conferidos, e frontend observado. Ela foi retirada da promoção porque os marcadores N64/Dolphin usavam a cadeia de parentesco anterior à R135. **O pacote final corrigido**, SHA-256 `fd14c522f51e717a636febf1ab9dee1970217339f37880421238eb2f30ce7b05`, 2.714.991.631 bytes, passou assinatura v2/v3, alinhamento 16 KiB e verificação de todas as entradas. Ainda não foi instalado: o usuário estava em uma partida de três aparelhos e a atualização não deve interrompê-la.

Edge 30 e Samsung A56 continuam na R135, SHA-256 `f6abe89490e7ba5e2cdd432625888bed6f40aea115d730cf612d509ec6ca9896`. A R136 não é uma promoção de estabilidade geral. O [incidente físico Top Gear 3000](../../audits/station-r136-topgear3000-live-20261012/README.md) mostra espera com três aparelhos, túnel WSS respondendo no g52 e nenhuma prontidão nativa/READY; a causa inicial do motor ainda requer correlação dos três aparelhos.

## Causa observada

No moto g52 Android 13, dois ANRs da R135 ocorreram em 12/10 às 01:58:47 e 01:59:13 (America/Fortaleza), no mesmo processo. O primeiro foi atribuído à tela de salas; o segundo, ao retorno para o frontend. Em ambos, a thread principal aguardava `HardwareRenderer.nSyncAndDrawFrame`, a `RenderThread` aguardava um mutex do driver `libGLESv2_adreno.so` durante a criação de programa GL, e a thread `Station-cover-GLES` estava dentro de `StationOnlineCoverView$Worker.link` / `GLES20.glLinkProgram`, passando pelo compilador Qualcomm `libllvm-glnext.so`. A mesma operação de link continuou presa nos dois snapshots, separados por aproximadamente 28 segundos. A thread de comunicação online estava em segundo plano; ela não era a espera da thread principal nesses dois incidentes.

O pacote R134 já tinha um ANR gráfico às 01:43:06, com a thread SDL em `prewarmMagazinePrograms` enquanto o Android aguardava o driver. Isso confirma que o problema gráfico antecede a correção de saída online da R135. O ANR da tela retro às 01:42:12 é outra ocorrência e não foi atribuído a esta causa. Não é possível identificar, apenas pelo stack, o proprietário interno do mutex Qualcomm nem garantir que todos os ANRs históricos tenham a mesma origem.

Os logs brutos do aparelho contêm dados privados e ficam fora do Git. Suas somas SHA-256 são `8054775d36204edc6f18d67854f4b58dcfcd950bdb06a4586b3bb042fc24bff8` para o Dropbox ANR e `6a47f64e376c941453fbf35464d34a05098e6d4628db4f5ac1cf33b6d722c1f1` para o logcat, preservados localmente em `work/anr-g52-20261012/` no workspace desta análise.

## Alteração exata

A única classe produtiva modificada é `org.emulationstation.frontend.netplay.StationOnlineCoverView`, em `classes35.dex`. Seu construtor detecta fabricante `motorola` e modelo `moto g52` sem distinguir maiúsculas. Só nesse aparelho, desliga o listener e oculta a `TextureView` do efeito de capa. O `ImageView` original permanece no lugar e mostra a mesma arte carregada; o worker `Station-cover-GLES` não é iniciado pela capa. Nos outros modelos, o fluxo permanece igual. Nenhum protocolo, sala, perfil, motor, jogo, opção ou controle foi alterado.

O DEX recomposto contém 608 classes, sem classes adicionadas ou removidas. As projeções das outras **607 classes** são idênticas às da R135; `classes35.dex` mudou de `a7a66724f26c06075ec1833e11866a073f93ee056aeabf58301cab016f96a4f5` para `84b8aa3935a8e84eb69f8f7cc45885ac693e38bf1f26cfb07b811d3df60b8c05`. A receita isolada [build_dex.py](../../integration/online-cover-anr-r136/recipe/build_dex.py) reproduziu esse SHA em uma segunda execução.

O contrato existente vincula o DEX a três marcadores de runtime e aos quatro IDs de motor online. Por isso o APK troca exatamente cinco entradas: `classes35.dex`, `assets/station-online/engines.json` e os três marcadores PSX/N64/Dolphin. As outras **13.855 entradas** do APK R135 têm conteúdo byte a byte igual. Manifest, resources, 39 DEX externos, frontend nativo, emuladores, jogos, mídias e perfis permanecem preservados. O certificado original v2/v3 e o alinhamento de 16 KiB foram verificados.

Novos IDs produzidos pelo vínculo de identidade:

| Plataforma | ID R136 |
| --- | --- |
| PSX | `pcsx-rearmed-ff81ed17-player-v3-2df6007ca0aa` |
| Nintendo 64 | `mupen64plus-ae-33bf7021-n64-v3-aee665f0ac42` |
| GameCube | `dolphin-5102a033-gamecube-v3-e8d6f6cf4387` |
| Wii | `dolphin-5102a033-wii-v3-e8d6f6cf4387` |

Eles ainda dependem do mesmo cadastro, perfil, conteúdo, modo e resposta assinada fresca do servidor. A alteração da capa não ativa qualquer motor no servidor.

## Reprodução e entrega

Usar [a receita R136](../../integration/online-cover-anr-r136/recipe/) com o donor R135 de SHA exato, JDK17, apktool3.0.3, NDKr28c, a identidade privada R135 original e a chave original. A sequência é `build_dex.py`, `build_identity.py`, `package_r136.py`, alinhamento16KiB, assinatura v2/v3 e verificação de todos os hashes. O [recibo sanitizado da instalação candidata](evidence/instalacao-r136-moto-g52.json) conserva o fato histórico. O [recibo do pacote final](evidence/package-final.json) tem `installed=false`; instalar somente quando a partida tiver terminado, sem limpar dados. APK, chave, fingerprints integrais de runtime e logs brutos ficam no backup privado, não no Git.

## Limites e aceite

A instalação candidata e a abertura do frontend não comprovam a ausência de ANR ao entrar/sair da tela online. O teste físico solicitado é abrir e fechar a tela de salas duas vezes no moto g52 e comparar novos registros com os eventos de 01:58/01:59. O prewarm do frontend observado na R134 continua como risco gráfico separado. Para consumidores, validar também o mesmo fluxo com sessão e jogo reais, retorno de jogo, e os modos de 3 e 4 participantes após o cadastro efetivo do servidor. O APK nativo atual limita a quatro mesmo quando o catálogo documenta cinco para Super Bomberman 3; ver o incidente. Não interpretar um teste de navegação como validação de gameplay ou de serviço.
