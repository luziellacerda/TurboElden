# Protocolo PSX PXL1

Componente opt-in para duas portas Standard Pad (IDs libretro 0–13, máscara `0x3fff`). O frontend/owner normal executa o jogo; o transporte Station v3 leva dados opacos. Não reutiliza os datagramas Dolphin/ENet DPL1 nem cria comandos de servidor.

## Confirmações e autoridade

- Recepção: validar e copiar um pacote completo para mailbox nativo limitado gera receipt `copied(id)`. O cursor DATA v3 é confirmado antes de liberar esse receipt. Liberação repetida só retorna Duplicate para um receipt efetivamente aposentado no cache limitado.
- Gameplay: COMMIT Executed somente após o `retro_run` real no owner. Copiar dados ou começar uma lease não significa executar um quadro.
- Estado: aplicar somente no owner pausado, com tamanho real `serializeSize`, identidade e SHA exatos. AppliedState somente após `retro_unserialize` retornar sucesso.
- Epoch novo invalida entradas antigas como Superseded. Snapshot do anfitrião alinha o cursor do convidado sem fabricar execuções.
- Toda revisão de controle revoga o permit anterior, mesmo pause=false. Resume precisa de ACK real do owner para o epoch/serial exatos.
- Sair exige autorização humana e fechamento no checkpoint. Rede, timeout, exceção e erro pausam/registram falha.

## Framing

Cabeçalho de 8 bytes: `PXL1`, origem 1/2, destino 2/1, tamanho BE16. Payload de 28 a 1392 bytes; quadro completo até 1400 bytes.

Cabeçalho interno de 28 bytes: kind u8, topology=3, ports=2, reserved=0, epoch BE64, stateSerial BE64, frame BE64. O stateSerial é do snapshot; o serial de controle é uma revisão local independente.

| Kind | Corpo | Quem envia |
|---|---|---|
| INPUT 1 | pad BE16 | Convidado |
| FRAME 2 | dois pads BE16 | Anfitrião, após executar |
| StateBegin 3 | identity32 + SHA32 + bytes BE32 | Anfitrião |
| StateChunk 4 | offset BE32 + até 1360 bytes contíguos | Anfitrião |
| StateEnd 5 | SHA32 | Anfitrião |
| RequestState 6 | vazio | Convidado |
| Commit 7 | kind + outcome | Receptor do evento original |

Outcomes: Executed=1, Superseded=2, AppliedState=3, OwnerFailed=4. AppliedState aplica somente a StateEnd; StateEnd nunca é Executed. Replays de COMMIT com mesmo stamp/outcome são idempotentes; conflitos são recusados.

Limites: estado16MiB; janela de quadros32; receipts512 ativos +512 aposentados; eventos COMMIT512; histórico de COMMIT128; saída256KiB +128 pacotes pendentes. Backpressure não confirma nem enfileira uma resposta parcial.

## Pipeline fixo

O candidato usa `inputDelay=4`, ligado ao perfil/options assinados. Uma amostra original no quadro N alimenta N+4. Os quatro primeiros quadros usam pads neutros idênticos e são efetivamente executados. FRAME é emitido somente depois da execução do anfitrião; o convidado nunca fica adiante do cursor autoritativo.

O priming ocorre no Resume, depois de STATE aplicado e filas drenadas. Pausa com entradas futuras exige snapshot novo, classifica entradas pendentes como Superseded e reinicia o pipeline. O componente admite0–16 para provas e futuras opções assinadas; o lançamento produtivo atual fixa4.

Simulação isolada,2s/60Hz: D0/RTT50ms=30 quadros no host; D4/RTT50ms=120 host/119 guest; D4/RTT150ms=60 host. Não é medida Android nem prova de estabilidade. Uma política futura deve escolher o atraso canônico antes da partida de acordo com RTT/jitter medidos; não alterar o atraso durante uma sessão.

## Testes e limites

`tests/protocol_probe.cpp` usa owner/core sintéticos e testa estados, entradas, epochs, recibos, controle humano, bounds, replays e latência. `tests/run_endpoint_probe.py` executa fixtures JVM PXL1 e a regressão R126 DPL1/TCP sem modificar a fonte congelada. Fixtures não são empacotadas.

SHA/tamanho do estado garantem integridade de transporte; não demonstram segurança dos loaders internos PCSX diante de um estado remoto malformado. Compatibilidade HLE, controles físicos, desempenho, servidor ativo e partidas de dois aparelhos requerem conferência específica do conjunto final.
