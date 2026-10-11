# R128 — montagem atual

A implementação PSX abaixo permanece congelada. A montagem atual e seus quatro IDs estão em [overlay R128](../ps3-ps4-offline/README.md), que adiciona apenas PS3/PS4 offline. Usar os recibos R128 para o pacote atual; os hashes abaixo descrevem a R127 histórica.

## Implementação PSX R127 preservada

# PlayStation online com o emulador normal

Esta integração reutiliza o **LibretroPlayer original e o PCSX-ReARMed normal**. A entrada PSX online tem processo privado, autorização Station e transporte próprio PXL1 sobre `station-stream.v3`. Renderer, eventos SDL e controles pertencem ao Player original; esta rota PSX não abre StationRetroActivity nem cria um segundo loop de emulação.

## Estado da entrega

Código, compilação, assinatura e **verificação integral do APK candidato R127 concluídos**. Nenhuma instalação, ativação no servidor ou partida física aprovada está declarada aqui. A última instalação comprovada permanece R124; a base de desenvolvimento desta montagem é R126.

Os recibos finais são [package-final.json](evidence/package-final.json), [runtime-final.json](evidence/runtime-final.json) e [java-final.json](evidence/java-final.json). Eles identificam o pacote efetivamente verificado e prevalecem sobre resultados intermediários. A existência do código ou de `launchReady` no asset não comprova que o registro correspondente foi ativado em produção.

APK final: SHA256 `a350878cca5c1a65c51e79ac13e9e38c2053d76e5404edb515ad1ddd650c3038`, **2.235.617.465 bytes**. Foram conferidas 13.549 entradas preservadas, assinatura v2/v3 com o certificado original e alinhamento de 16 KiB. O APK e demais binários privados não são publicados nesta pasta.

## Identidade final da integração

| Campo PSX | Valor |
| --- | --- |
| Engine | `pcsx-rearmed-ff81ed17-player-v3-f9d762e9fe82` |
| Backend | `psx-player-station-v1` |
| Core normal | `libpcsx_rearmed_libretro_android.so` |
| SHA256 do core | `e7534aa6f4a993e03f4563152f0e017324b710f5a5c224b0f1f722abeabed2b9` |
| Owner normal | `libmain.so` |
| SHA256 do owner | `62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6` |
| Runtime integrado | `libstation_psx_online.so` |
| SHA256 do runtime final | `f9d762e9fe82b5346b65d29d356d6cb93776a983eb4bf9a9e25ab73388b1eb4f` |
| Perfil | `standard-2p-v1`, duas portas Standard, atraso de entrada fixo de 4 quadros |
| Protocolo | PXL1 interno; relay autenticado `station-stream.v3` |

O fingerprint integrado também registra N64 `mupen64plus-ae-33bf7021-n64-v3-9536fbd2a7d2`, GameCube `dolphin-5102a033-gamecube-v3-a206aed4b7bb` e Wii `dolphin-5102a033-wii-v3-a206aed4b7bb`. Seus cores e opções permanecem preservados; os IDs devem corresponder ao pacote completo atual. As entradas SNES/Mega Drive permanecem inalteradas.

## Política por jogo

A primeira política PSX aceita somente jogos individualmente aprovados para **HLE, dois jogadores simultâneos e duas portas Standard**. Não habilita multitap, analógicos, light guns ou quatro jogadores. Ter o core disponível não torna qualquer jogo elegível. O perfil e as opções assinadas precisam corresponder ao catálogo autorizado.

Os 59 defaults foram extraídos do core normal exato, conferidos novamente no registro de opções V2 e combinados com sete overrides explícitos. DRC permanece habilitado conforme o default compilado; threads auxiliares DRC/GPU/SPU, frameskip, multitap e combinação analógica ficam desativados nesta política. Nenhuma preferência offline é usada como opção silenciosa da partida. Consulte [profile.json](profile.json) e [pesquisa e limites](docs/RESEARCH-AND-LIMITS.md).

## Como a partida funciona

1. O app valida a engine, o perfil, a autorização da sala e um descriptor de uso único. No consumo, confere novamente o conteúdo: CUE inclui todos os tracks; CHD/PBP usam o arquivo de lançamento.
2. A Activity privada prepara home/saves novos e inicializa o renderer original. Só o owner real carregado, com callbacks/opções/serialize-size conferidos, cria a sessão nativa.
3. O owner amostra os controles originais. Entradas do quadro N alimentam N+4; o anfitrião reúne os dois slots e define o quadro canônico. Cada telefone continua processando seu próprio core.
4. Um quadro só ganha COMMIT de execução depois que `retro_run` real retorna. Confirmação de cópia dos bytes pelo relay é outro evento; não prova gameplay.
5. Pausa, foco, epoch e serial precisam de ACK real no owner. Estado inicial/recuperação só libera a barreira após tamanho/hash/identidade corretos e retorno positivo do decoder original. A espera não bloqueia a UI nem fabrica quadros.
6. Saída exige confirmação humana. Falha, conexão perdida, timeout ou lifecycle não autorizam desligar a partida. Após confirmação, IO/Binder e thread SDL real devem terminar antes de retirar somente o processo privado PSX.

## Preservação

Não há redesenho dos menus/carrosséis, alteração de LEDs, vídeos locais, cache/preload, limite de apresentação de 30 fps ou opções de economia por consequência desta integração. Bibliotecas normais, controles offline, licenças, jogos e saves não são substituídos. Para apresentação original, somente nomes de seleção dos dois controladores e `LibretroStretch` validado são copiados para o home privado. Saves online são novos e pertencem à sessão.

## Organização e provas

- [Contrato da entrada original](ENTRY-CONTRACT.md), [owner](native/OWNER-README.md) e [revisão da coordenação](evidence/OWNER-SESSION-REVIEW.md).
- [ABI/call sites](evidence/abi-probe.json), [owner/protocolo](evidence/owner-probe.json), [compilação standalone](evidence/build-receipt.json) e [Entry/JNI integrado](evidence/entry-build-receipt.json).
- [Session/Launch](evidence/session-launch-probe.json), [endpoint e regressões](evidence/endpoint-probe.json), [protocolo](evidence/protocol-probe.json), [saída humana](evidence/human-exit-gate.json) e [partições DEX completas](evidence/complete-dex-receipt.json).
- Fontes atuais em `native/` e `java/`; receitas em `recipe/`; fixtures exclusivas de auditoria em `tests/`. Fixtures não entram no app.

Campos como `notPackaged` em `sdl-hook-receipt`, `originalManifestUnchanged` em `factory-hook-receipt` e `apkChanged: false` em `optin-smali-assembly` descrevem provas isoladas anteriores à montagem. Não descrevem o pacote R127 final: os hooks foram incorporados às partições completas e o Manifest recebeu a entrada privada. O recibo `package-final.json` é a autoridade para os bytes realmente incluídos; o runtime final é `f9d762e9fe82…`, não o hash de uma compilação standalone/intermediária.

As provas isoladas incluem 80 verificações ABI, 16.090 de owner com 513 retornos simulados do core, 61 de Session/Launch, 186 de endpoint PSX e 470 de regressão Dolphin/TCP. Elas não demonstram gameplay Android, controle físico, desempenho, temperatura ou estabilidade prolongada. Os binários donors, APK, ROMs/BIOS, chaves e dados pessoais ficam fora do Git.
