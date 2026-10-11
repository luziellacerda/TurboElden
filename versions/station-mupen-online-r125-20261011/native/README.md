# Adaptador nativo Station para Mupen64Plus AE

Fonte nova GPL-2.0-or-later para o fork online do AE `33bf7021549d7873e976884370fbd1a8e7333bc7`. O gerador lê cinco arquivos com SHA256 fixado e produz um overlay, diff e manifesto. Não modifica a árvore offline. Copiar o overlay para uma cópia separada dessa árvore antes da compilação Android. Não substituir a biblioteca offline no APK.

```
python apply_native_patch.py --upstream <raiz AE original> --out <overlay novo>
```

## API JNA

| Função C | Uso |
| --- | --- |
| `int StationMupenConfigure(int slot, int mask)` | Antes de NETPLAY_INIT/EXECUTE. Slot 0..3 e máscara exata do roster P1..P4. Rejeita solo, slot ausente, cinco jogadores e reconfiguração de uma sessão viva. |
| `void StationMupenControl(int64_t epoch, int pause, int visible)` | Solicita estado; ignora epoch antigo. A chamada não confirma a pausa. |
| `int64_t StationMupenStatus(void)` | Epoch confirmado multiplicado por 8, flags pausa=1, registro completo=2, falha=4. Epoch -1 (`-8` com flags) significa nenhuma confirmação da revisão atual. |
| `int StationMupenStalled(void)` | Input necessário ausente por pelo menos 2 s, com execução visível/conectada e sem pausa solicitada/falha. Solicita barreira de transporte; não encerra. |
| `void StationMupenRequestQuit(void)` | Ordem humana de saída: acorda gate e cancela os loops de IO. |

Apenas a thread que executa `main_run` pode confirmar uma revisão. A primeira confirmação ocorre depois de registro/configuração/roster, criação do dispositivo e inicialização do boot, antes de `run_device`. Novas pausas chegam no limite VI ou durante a espera pelo input. Os callbacks de quadro, áudio, render e CPU não são executados pelo loop pausado. Ele recebe UDP e dorme até 5 ms. Não segurar o mutex do gate durante IO.

O transporte Java precisa mover TCP de preparação antes de READY. Bloqueá-lo até a primeira confirmação causa um deadlock de bootstrap: o native precisa desse registro antes de confirmar. `connected` só aparece com os quatro registros recebidos, máscara exata e registro próprio no slot configurado; não se infere pela existência do socket. A configuração usa apenas participantes reais, não os quatro slots possíveis.

O registro TCP ocorre antes de anexar o plugin de input: nesse momento o array global `Controls[]` ainda está zerado e `NativeInput.setConfig` só armazenou os valores em cache. A variante Station obtém explicitamente MEMORY=2/raw=0 e o slot local de `StationMupenConfigure` antes de escrever o registro. O servidor local mantém MEMORY apenas em P1 e normaliza os convidados para NONE=1. O registro completo depois preenche os Controls reais. Essa preparação não confirma conexão/READY nem depende de executar um quadro.

## IO, espera e saída

No modo Station, o input faltante é solicitado novamente sem aumentar o contador, sem thread adicional, sem busy-spin e sem o timeout de 10 s que chamava STOP. Dados completos são consumidos uma única vez. O código original permanece no ramo não Station.

TCP Station usa `poll(20 ms)` e `send/recv(MSG_DONTWAIT)`; envia sem SIGPIPE. Antes de usar o descritor da estrutura SDL_net, verifica SO_TYPE, família, endereço e porta pelo peer API público. Uma estrutura incompatível falha antes de IO. EOF, erro permanente, pacote inválido, roster incorreto ou status explícito de desync marcam falha. Não restauram/recriam sessão nem encerram o emulador automaticamente.

Uma perda transitória de WSS deve preservar os sockets locais do multiplexador. EOF local é uma falha real de pipe/preparação; o código não tenta reinterpretar metade de um comando como um comando novo. `StationMupenStatus` bit 4 deve mostrar aviso e manter a pausa na bridge; não reutilizar o tratamento legado que fecha a Activity automaticamente.

Reset unilateral retorna `M64ERR_INVALID_STATE` e avanço manual de um quadro não altera o dispositivo enquanto Station estiver ativo. Os comandos normais continuam disponíveis no core offline e no fork quando a flag Station estiver desligada. Isso evita que um menu local faça um participante divergir dos outros.

Saída: `StationMupenRequestQuit` → ordem STOP humana → esperar EXECUTE terminar → NETPLAY_CLOSE. STOP sem o Quit explícito não encerra a execução Station. NETPLAY_CLOSE durante EXECUTE retorna INVALID_STATE sem autorizar Quit, fechar sockets ou liberar inputs sob a thread ativa. `cin_compats` pertence à stack de main_run; os eventos são liberados e seu ponteiro removido nessa thread antes do retorno. Depois, NETPLAY_CLOSE termina o gate. Não começar outra configuração antes de encerrar as threads de preparação anteriores.

## Limites

Esta recuperação mantém o fluxo/input determinístico parado enquanto o transporte reconecta. Não contém rollback de savestate. Desync real do CP0 é falha permanente da tentativa: permanece pausada até saída humana. Uma nova epoch não limpa essa falha. O modo Station não altera o emulador offline, seus controles, plugins, FPS ou saves; a bridge deve igualmente desativar autosave/forceExit por watchdog apenas na sessão online.

O binário online produzido exige nova identidade de engine/core/runtime e perfil aprovado do servidor. Não reutilizar hashes do parallel/R124. O formato Mupen continua protocolo nativo versão 1 dentro da multiplexação Station v3. Não há libretro nem engine RetroArch neste adaptador.

Provas locais registram somente gate e geração/compilação isolada. Ainda são necessários o build ligado aos plugins reais, bootstrap/roster em dois aparelhos, conexão durante perda de rede, saída humana e gameplay. Nenhum desses testes físicos é alegado por estes arquivos.
