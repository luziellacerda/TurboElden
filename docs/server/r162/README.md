# R162 — handoff mínimo para liberar o teste N64 online

**Estado em 15/10/2026:** candidata assinada e instalada no moto g52; ainda não cadastrada no servidor nem homologada em partida física. O A56 permanece na R161 até a atualização. Não associar resultados de partidas R161 ao motor R162.

## Entrega exata ao servidor

Entregar apenas o ZIP privado `Kit-Servidor-TurboStations-R162-Independentes.zip`, SHA-256 **`a777e90a1c5add265aed328e13c884af1277a8dee6770be4ca109d431aeec942`**, 12.338.080 bytes. Cópia local: `E:\StationN64OwnerAudit-20261014\kit-r162-video\Kit-Servidor-TurboStations-R162-Independentes.zip`. O ZIP foi reaberto e seus 40 arquivos foram conferidos com o manifesto. Ele contém `incoming.json`, `engines-apk.json`, políticas, seis bibliotecas de motor, 21 dependências e provas de montagem; **não contém APK, ROM, BIOS, chave, serial de telefone ou log bruto**. Por orientação do proprietário, **não enviar o APK ao Git nem no handoff**. Para correlação, o SHA-256 do APK assinado e instalado no g52 é `7ec742c4cae7b663f2198e347253986b4c4c5d0d0461052dd75df56ca6335dd7`.

Os quatro `engineId` do kit são:

| Sistema | `engineId` R162 | `runtimeSha256` |
| --- | --- | --- |
| PSX | `pcsx-rearmed-ff81ed17-player-v3-bf682d6798e7` | `bf682d6798e74cb46cd221ecceb10475e4f7fb2d11e1da45a84e2f25ac7ad4ab` |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-57155617f470` | `57155617f470e39144ba050169bdf5801f0392f62995a95d0116a4497ce0fd1e` |
| GameCube | `dolphin-5102a033-gamecube-v3-3bfbe6be43a7` | `3bfbe6be43a7c507a381b4d5ef9a0f7571737031453eb7254835687199972796` |
| Wii | `dolphin-5102a033-wii-v3-3bfbe6be43a7` | `3bfbe6be43a7c507a381b4d5ef9a0f7571737031453eb7254835687199972796` |

## Por que o vínculo mudou

A [captura física R161](../r161/physical-n64-video-failure-20261015.md) demonstrou que a ponte Android registrava o vídeo no core offline, enquanto a partida online executava outro core. R162 acrescenta `libstation_ae_bridge.so`, SHA-256 `3d0a9e9dc5ca31629f478023b849fe2037b4a68b9ac3689ba413a5f542191986`, somente à cadeia N64. A `libae-bridge.so` offline permanece com SHA-256 `ba5a7582295215f159e197f805dbfe85851aa912462996870f61ccd752ecb360`. Os marcadores PSX e Dolphin mudam porque seus fingerprints vinculam os bytes globais do APK; suas políticas e opções não foram ampliadas. A [receita e prova de escopo](../../../integration/n64-online-video-extension-r162/README.md) explicam o delta.

## Ação delimitada no servidor

1. Ler uma baseline fresca e os recibos R161 já aplicados. Conferir o SHA-256 do ZIP, seu manifesto, as seis bibliotecas e as 21 dependências extraídas, inclusive a nova ponte N64. Não executar novamente o cadastro R161.
2. Usar o registrador vigente sob `scan.lock` e backup/rollback próprios do operador para cadastrar **aditivamente** os quatro `engineId` do kit. O N64 mantém `cpu=dynarec`, `video=glide64mk2`, `rsp=hle`, `inputDelay=2`, perfil `direct-four-ports-v1`, máximo de quatro jogadores e SHA canônico Android do perfil `ef8bfd6e6287a205da4f73422a194c7fc05b9246363a8311501a6efa3bca2b63`. Nenhuma aprovação PSX HLE nova.
3. Seguir o fluxo R161 vigente: vincular os 78 modos revisados; após o recibo e outra baseline fresca, vincular as 321 decisões N64 revisadas para 157 edições. Preservar as edições individuais sem sala e as contagens por modo. Conferir as capabilities assinadas, admissões e recusas com os identificadores R162 exatos.
4. Devolver recibo com hashes aceitos, baseline, transações, contagens e `serverApplied` real. Se a rotina atual exigir o APK completo, registrar essa exigência e **não** aceitar um APK antigo como substituto da R162. O proprietário não autorizou enviar APK no handoff.

Nenhuma mudança de DLL, API, scanner, catálogo, banda, licenças ou ROM é necessária por esta correção de vídeo. O servidor pode formalizar o cadastro e os testes sintéticos; isso ainda não comprova gameplay Android.

## Teste físico após o cadastro

Instalar a mesma R162 em dois telefones, com dados preservados. No g52, a primeira abertura R162 iniciou `LoginActivity` e `ESActivity`, sem `GameActivity`/`:n64core`. A dashboard de 24 plataformas abriu após 44,6 segundos de preparação do carrossel; a tela ficou em 0% nesse intervalo, sem ANR. O relato de abertura direta do N64 não se reproduziu no lançamento observado e ainda precisa ser esclarecido. Esse tempo de preparo antecede a R162: manifesto, frontend e carrossel têm bytes idênticos aos da R161.

Depois, confirmar 007 offline com imagem e abrir a mesma edição N64 online: primeiro quadro, vídeo, áudio, velocidade, controles dos dois jogadores e saída do anfitrião. Se o convidado continuar sem aviso ao sair, registrar os dois lados por pelo menos 25 segundos e tratar pela [auditoria separada](../../../integration/n64-online-video-extension-r162/HOST_EXIT_AUDIT.md). Não promover R162 a estável antes desses resultados.
