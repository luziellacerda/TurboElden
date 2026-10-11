# Candidato isolado — primitivas de sessão EX+

Preparado em 11/10/2026 para o futuro adaptador do Snes9x EX+ e MD.emu/Genesis Plus GX. **Não está ligado aos motores, não usa ROM, não contém JNI/WSS e não está no APK R126.** Nenhuma rota produtiva ou biblioteca offline foi alterada.

`native/` contém um componente real de montagem de inputs e barreira não bloqueante de quadro/epoch, além de guardas iniciais de snapshots. `tests/` executa fixtures de owners sintéticos. `recipe/` compila a prova no host e um arquivo estático ARM64. Isso demonstra essas primitivas, não emulação online funcionando.

## Contrato

O caller de `InputAssembly.offer` deve fornecer identidade autenticada de cada participante separada do slot alegado no payload. Somente o host monta o quadro completo. `FrameGate.enqueue` aceita somente origem host=1, roster exato, máscaras de input válidas e uniqueDeliveryId crescente do endpoint. Cada ID/bytes deve permanecer igual em retries. Fila fixa32; backpressure é explícito, nunca descarte silencioso.

O mesmo owner chama checkpoint, callback de aplicação de estado, `begin` e `complete`. Uma lease válida autoriza somente um quadro; nenhum receipt de consumo sai de `enqueue`. `complete` é chamado depois que o core original realmente executar esse quadro. O módulo não executa o core e não pode conferir se um integrador chamou `complete` sem emular; essa correspondência precisa ser testada com os hooks reais.

STATE solicita epoch/serial; o owner reconhece somente em checkpoint após o quadro atual. O callback real de estado roda no owner, fora do mutex. Somente sucesso exato e serial/epoch ainda atuais permitem `resume`. Inicialização por si só não cria ACK. Não há timer, rede, disco, GPU ou desconexão automática. O caller de `authorizeHumanExit` precisa ser uma ação humana confiável; nenhum payload remoto pode chamar essa API.

O caller retém ownership do `std::span` de estado: os bytes precisam permanecer válidos e imutáveis até o retorno de `ownerApplyState`. O protótipo invalida sua fila lógica ao reconhecer uma nova pausa e aplicar snapshot. Ele não implementa a reconciliação dos DATA/IDs ainda pendentes no endpoint WSS durante essa invalidação. A ponte futura terá de definir a disposição por epoch/serial e seu ACK real; não pode simplesmente descartar bytes do stream por causa da limpeza da fila lógica. Nenhum transporte atual usa esse módulo.

`captureLocal` conserva os bits reais do frontend. O profile online ainda deve configurar o controlador local normal como P1 e publicar esses bits no slot Station assinado. Nenhum mapeamento físico/touch original foi alterado. As máscaras comprometidas de todos os participantes devem ser aplicadas ao core conjuntamente no começo da lease, respeitando `S9xGetJoypadBits` / `playerIdxMap` normais. Esse hook ainda não existe aqui.

`StationSnapshotGuard.hpp` aceita SNES somente quando o retorno upstream é SUCCESS=1. Para MD valida só o envelope raw contra tamanho/version local exatos e oferece cursor limitado. **Não chama nem torna seguro o decoder `state_load` existente**; é necessário aplicar bounds a todas as leituras/context loaders. Não expor snapshots de rede à API normal antes desse trabalho.

Capacidades de fixtures: SNES2..5, MD2..4. A política atual do app permite MD até2; estes testes não alteram nem autorizam esse teto e não catalogam jogos.

## Provas executadas

- `recipe/run_probe.py`: LLVM22.1.8, C++20/O2/Wall/Wextra/Werror, **82.297 checks**, gate de3.288 bytes no host, fila fixa32.
- `recipe/build_android_gate.py`: ARM64/API26, objeto ELF64 AArch64 e arquivo estático de27.932 bytes. Não é biblioteca de NativeActivity, não foi carregado em Android.
- Fixtures: roster incompleto, spoof, slots2/3/4/5, quadros ordenados, input concorrente, repeats/conflitos, limites, owner errado, serial/epoch, pausa durante quadro, estado recusado/exceção, saída humana e20.000 cabeçalhos de snapshot.

Receipts completos em `evidence/`; binários somente locais em `G:\StationExPlusCandidate20261011`.

Reprodução:

```powershell
& 'C:\Python314\python.exe' recipe/run_probe.py --out 'G:\StationExPlusCandidate20261011\host-new'
& 'C:\Python314\python.exe' recipe/build_android_gate.py --out 'G:\StationExPlusCandidate20261011\arm64-new'
```

Não há recipe que integre/empaque o emulador: código de integração incompleto não é publicado como migração pronta. A auditoria e o plano real de hooks estão em `audits/station-online-system-engines-20261011/snes-megadrive/README.md`.

## Preservação e limites

R126, SNES/MD offline, carrossel, GPUs/shaders/LED, economia/cache/preload/vídeos/30fps, controles, licenças e saves não receberam alterações. Não houve publicação, deploy, cadastro, telefone ou gameplay. Não medir/prometer queda de consumo/lag com esta prova sintética. Nova implementação deverá manter a API de autorização e o ACK real do contrato v3, gerar novos IDs e validar cada jogo/profile antes de alterar sua rota.
