# Convites curtos e senha automática — candidato sobre R57

Pedido do mantenedor: o convidado não deve digitar a palavra passe do motor; o convite de sala precisa ser curto.

## Implementação

- A sala recebe **8 caracteres**, exibidos em dois grupos, por exemplo `7KPM-4XRT`. O app aceita letras minúsculas, com ou sem hífen, e mantém a leitura dos convites TS1 anteriores.
- Um toque em **Aceitar e entrar** continua entrando pelo convite enviado à pessoa. O código curto resolve a sala em uma consulta autenticada e assinada; depois o app prepara a mesma edição e executa o `join` existente. A consulta não entrega senha/ticket nem muda membros ou Pronto.
- RetroArch antes abria o diálogo ao receber o desafio, mesmo com `netplay_password` preenchido. O patch usa a senha de 64 caracteres já recebida na resposta assinada de membro, somente no lançamento Android tipado `client`. Envia NICK e depois PASSWORD, com salt/SHA256/formato e verificação do anfitrião originais. Credencial ausente/inválida falha sem pedir digitação; outros lançamentos mantêm o comportamento manual.
- Estão incluídos os três fontes de prontidão publicados em `station-relay-readiness-r57-20261006`: TCP real retido, WSS privado, canal ResultReceiver, fechamento idempotente e saída/HUD. Mantido o layout R57 de Criar sala, barra fina, capas e INSTALADO. São 152 fontes atuais preservados, cinco alterados e um novo: 158 Java/dependências.

## Motor e compatibilidade

Runtime compilado **arm64-v8a / API26 / NDK r28c**, alinhamento16KiB e export NativeActivity verificados. SHA256 `899e35279cf046242a7ae31f502078080bd6a94404770fe99e1e2e90be58a1ef`, 10666496 bytes. Flags originais HAVE_VULKAN=0/HAVE_CHEEVOS=0/HAVE_SAF=0 preservadas; 28 avisos upstream na compilação. O runtime anterior tinha10.666.280bytes; este tem10.666.496. Cores bsnes/ClownMDEmu, opções, controles, saves e jogos permanecem os anteriores. NeoGeo continua sem liberação de partida.

O binário GPL está em `runtime/libstation_retroarch.so`, com licença e fonte correspondente fixada. O manifesto em `assets/station-online/engines.json` usa IDs com sufixo `-autopass1` e o hash acima. O servidor precisa adicionar os dois registros de `server-contract/engine-registry-additions.json`, preservando os registros antigos. Os dois telefones precisam atualizar para a mesma edição para usar o novo motor.

## Verificação realizada neste Linux

- 318 verificações de códigos/salas; 41 de salas anteriores; 34 sociais; 53 de HTTP com assinatura e autenticação sintéticas.
- 278 verificações JVM de salas e convites, incluindo23 de digitação/código curto/TS1.
- 66 verificações executando o trecho real do cliente, gerador de digest e verificador original do anfitrião, com transporte/menu sintéticos; senha certa/errada, ordem NICK/PASSWORD, nenhuma chamada ao diálogo no caminho automático e falhas de envio.
- 39 verificações reais de TCP/TLS/relay Java/C#, 12.583.029bytes por direção. Transporte usa o servidor desta mudança.
- 158 fontes Java8/API34 compilados em `api-check-only`; patch reaplicado e duas recusas do empacotador passaram.

**Sem novo DEX/APK assinado, instalação, teste Android do motor ou gameplay em dois telefones neste Linux.** O classpath de produção, APK privado e chave original estão no PC. As provas não substituem o teste nos aparelhos.

## Compilação e empacotamento no PC

Usar esta pasta junto de `station-current-r55-20261006`, `station-layout-r57-20261006`, `station-relay-readiness-r57-20261006` e `station-online-20261004` do mesmo checkout. Fonte funcional9d3d45f, visual8980cd4 e prontidãof8b019d6 preservadas. Não aplicar deltas antigos R41/R55 nem usar seus empacotadores.

1. `python recipes/build_candidate.py --output <novo-diretorio-em-E>` compila as fontes desta composição, exige SDK34/station-client.jar/D8 pelos hashes de produção e produz DEX35/min26. `api-check-only` não pode gerar APK.
2. `python recipes/package_candidate.py --workspace <mesmo-diretorio> --output-apk <novo-apk> --keystore <chave-original> --ks-key-alias <alias-original> --ks-pass-env <nome-da-variavel-privada>` usa o APK **R57/e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566**. Certificado obrigatório7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825. A senha é fornecida privadamente no PC.
3. O empacotador substitui exatamente `classes35.dex`, `lib/arm64-v8a/libstation_retroarch.so` e `assets/station-online/engines.json`. Confere todas as demais entradas, assinatura e alinhamento16KiB; usa o binário entregue, não um rebuild de hash diferente.
4. Atualizar ambos por instalação sobre o app, preservando assinatura/dados/licença. Confirmar código curto e convite pela pessoa, dois membros, ambos Pronto, Iniciar, entrada sem palavra passe, inputs reais, saída e retorno. Não desinstalar/limpar dados.

Para reproduzir o motor, `recipes/build_native_runtime.py --source-zip <zip-oficial-fixado> --ndk <r28c> --output <novo-diretorio>` aplica o patch consolidado original e o incremental desta pasta. Um rebuild diferente exige atualizar os manifestos/registro e nova conferência; não substituir silenciosamente o binário pinado. O patch Java sobre a prontidão R57 está em `station-short-invite-over-readiness-r57.patch`; a composição completa desta pasta já inclui os fontes herdados.

Contrato e implantação do servidor: consultar `docs/station-android/RETORNO-CONVITE-CURTO-SENHA-AUTOMATICA-STATION-20261006.md` no Servidor-pix. O estado de produção será confirmado no recibo de publicação; esta pasta por si só não implica APK instalado.
