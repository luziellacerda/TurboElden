# R165 combinada: registro anterior à publicação PSX

Estado posterior: [APK R165 assinado e cadastro dos motores pendente](R165-APK-ASSINADO-REGISTRO-PENDENTE-20261015.md). As informações abaixo documentam o ponto anterior ao retorno do servidor; não são o estado atual.

## Autoridades separadas

- O retorno estável dos telefones é a R164, tag `estavel-station-r164-20261015`, APK SHA-256 `903700d5d6dcd63779df636cfb11bf94e2fadbeece462d2cb7a6cdf1dfbd5210`.
- A correção R165 de saída humana do anfitrião N64 está provada na fonte e no DEX35, mas não foi empacotada, assinada ou instalada. A aplicação do [conserto correspondente no servidor](https://github.com/luziellacerda/Servidor-pix/blob/fix/station-r164-confirmed-host-exit/docs/station-android/r164/HOST-EXIT-HANDOFF.md) requer recibo próprio.
- O ramo PSX do servidor `feat/station-psx-online-20261015`, commit `1c56dec3628cafb0ae80cbdeee79a349a8965721`, é preparação. Seu `server-return.json` declara `serverDataPublished: false` e `physicalAndroidGameplayValidated: false`. Os 84 itens e 93 perfis/modos preparados não podem ser tratados como ativos ainda.

## Prontidão do app

O aplicativo R164 já contém o motor PSX HLE PXL1/`station-stream.v3`, com duas portas digitais. A implementação faz `enter`, lê capabilities assinadas, cruza a edição e o perfil com o motor instalado, valida ROM/core/runtime, executa `join` efetivo e depois `ready`/`start`. A classificação local sem vagas aprovadas não concede sala. O cliente genérico informa `clientMaximumPlayers=5` na descoberta, enquanto o modo PSX instalado limita as escolhas a dois; o servidor filtra perfis com `maximumPlayers <= clientMaximumPlayers`. Essa diferença da recomendação de enviar 2 merece observação no teste físico, mas não comprova falha nem autoriza mudar outro DEX preventivamente.

A fonte R165 combinada prepara três mudanças cirúrgicas: saída humana N64, largura da capa principal de seleção de jogos aumentada em 10% em relação à R164, e filtro da capa Mega Drive que usa só o suporte do seu perfil iluminado. Não foi encontrado um segundo motor de desenho Mega simultâneo. O filtro elimina 196.916 pixels lógicos de suporte legado desnecessário no perfil novo, preservando a capa antiga. O carrossel nativo compilado tem SHA-256 `3f20f862bed0d73668fdbc0fa06e7009011cbf8ea32c2cfff96029c2b8f23fc8`; ABI, SONAME, alinhamento de 16 KiB e avisos do compilador conferidos. O DEX35 preparado tem SHA-256 `7a5c1609df4d99ac4371bd4c1b06bc31dcfeeafa616c2b61f6d90bfd5694d020`. Ambos ficam fora do Git.

A [receita combinada](../../../integration/station-combined-r165/README.md) passou na prévia com o APK R164 exato. Se o retorno PSX não exigir código novo, a montagem trocará somente seis entradas: DEX35, carrossel, `engines.json` e três marcadores de runtime; preservará as outras 13.855 entradas byte a byte. **Ainda não há APK R165.** A R164 permanece instalada e estável.

## Vínculo que o servidor precisa devolver

O vínculo de runtime inclui os hashes de DEX e carrossel. Por isso o APK R165 combinado produzirá quatro `engineId` novos (PSX, N64, GameCube e Wii), mesmo mantendo as políticas e o core PSX R164. Os perfis PSX em preparação estão vinculados ao `engineId` R164 `pcsx-rearmed-ff81ed17-player-v3-1b315b86b4a7`; eles não habilitarão automaticamente o PSX do APK R165.

Antes de instalar a candidata combinada para teste online, devolver:

1. Recibo de publicação PSX efetiva, com `serverDataPublished: true`, edição/mode aprovados, identidade de conteúdo e capabilities assinadas.
2. Plano de cadastro aditivo dos quatro owners R165 e vínculo dos perfis PSX aprovados à identidade exata recebida no kit R165. Não copiar aprovações de motor antigo sem a revisão de identidade exigida pelo registrador.
3. Estado aplicado ou pendente do conserto de saída confirmada do anfitrião N64, separado da aprovação PSX.

Quando essas provas estiverem disponíveis, a produção monta **um único APK** R165, assina com o certificado original, confere as seis entradas, atualiza o instalador EXE para o hash final e entrega ao servidor somente o kit privado necessário, sem APK no Git ou pen drive. Após o cadastro, atualiza os telefones preservando dados e testa PSX em dois aparelhos na mesma edição e N64 com saída do anfitrião. O ensaio QEMU do servidor não substitui primeiro quadro, áudio, controles distintos e saída observados nos telefones.
