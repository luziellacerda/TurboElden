# SNES Multitap — candidato R77

## Escopo e estado

Correção mínima no wrapper de `libretro/bsnes-mercury`, commit `79d7f9de218b6ffa65a80bbdc5828532bc239232`, perfil `performance`. Um único método mudou: `Callbacks::inputPoll`. Não altera o protocolo de rede, runtime RetroArch, opções do core, controles offline ou os demais dispositivos.

Compilação ARM64 concluída, sem empacotamento/instalação por esta receita. Core candidato: `E:\ESTUDO APK\work\station-multiplayer-r77-20261008\snes\candidate\libstation_bsnes.so`, 1.791.648 bytes, SHA256 `0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527`. O cadastro precisa de uma identidade nova vinculada a esse hash. Não pode continuar identificando este binário como o core antigo `cc144383…`.

O mapeamento correto do adaptador não demonstra compatibilidade de qualquer jogo com três/quatro jogadores. A configuração Multitap deve ser habilitada somente em títulos/modos documentados e compatíveis, junto do contrato de sala/transporte implementado e qualificado separadamente. Partida real de quatro aparelhos ainda não validada.

## Defeito e correção

O Mercury codifica o jogador do adaptador dentro de `id`: quatro pads com 12 botões, total de 48 IDs. A função anterior devolvia zero para `id > 11`. Assim, o primeiro pad do adaptador podia responder, mas os outros três nunca chegavam ao callback do frontend.

O patch traduz somente `Input::Device::Multitap`: porta lógica recebe `port + id / 12`, botão recebe `id % 12`, dispositivo recebe `RETRO_DEVICE_JOYPAD` e índice permanece zero. Rejeita IDs a partir de 48. A ordem de botões do Mercury já é igual à ordem RetroPad: B, Y, Select, Start, Up, Down, Left, Right, A, X, L, R. Nenhuma tabela de ordem de outro core foi copiada.

| Jogador | Entrada SNES | IDs recebidos | Callback libretro |
|---|---|---|---|
| P1 | Joypad na porta física 0 | 0–11 | porta 0, joypad, índice 0, botão 0–11 |
| P2 | Pad 0 do Multitap na porta física 1 | 0–11 | porta 1, joypad, índice 0, botão 0–11 |
| P3 | Pad 1 do Multitap na porta física 1 | 12–23 | porta 2, joypad, índice 0, botão 0–11 |
| P4 | Pad 2 do Multitap na porta física 1 | 24–35 | porta 3, joypad, índice 0, botão 0–11 |
| P5 físico | Pad 3 do adaptador | 36–47 | porta 4, joypad, índice 0, botão 0–11 |

O quinto pad físico foi preservado como comportamento do hardware; o aplicativo continua limitado à capacidade que seu contrato autorizar, no máximo quatro neste pedido. Não configure o adaptador por padrão para todos os jogos. Dois joypads normais permanecem nas portas 0/1. Mouse, Super Scope e Justifier continuam pelo caminho anterior, inclusive as limitações já existentes no upstream; esta entrega não afirma corrigir periféricos.

## Evidência oficial

- [Documentação oficial bsnes Mercury Performance: Multitap](https://docs.libretro.com/library/bsnes_mercury_performance/#multitap-support) descreve Multitap na segunda porta e até cinco pads físicos.
- [Implementação oficial bsnes-libretro fixada em commit](https://github.com/libretro/bsnes-libretro/blob/05439f96121d2b9d7ad7a5fc1f29d7eebdcc8c43/bsnes/target-libretro/program.cpp#L417) usa `libretro_port += input / 12`, botão módulo 12 e dispositivo base joypad. O Mercury usa ordem interna diferente do bsnes recente; o patch adapta só a divisão porta/botão, preservando a ordem correta do Mercury. Hash do arquivo consultado em `evidence/official-reference.json`.
- [API de entrada libretro](https://docs.libretro.com/development/input-api/) define a porta do jogador no primeiro argumento e índice zero no joypad.
- [Guia oficial de múltiplos controles](https://docs.libretro.com/guides/netplay-multiple-controllers/) usa Super Bomberman 2 como exemplo. O exemplo não comprova o transporte de quatro telefones da TurboStations.
- [Fonte Mercury fixada](https://github.com/libretro/bsnes-mercury/tree/79d7f9de218b6ffa65a80bbdc5828532bc239232) contém o adaptador em `sfc/controller/multitap/multitap.cpp`; o método serial foi usado diretamente na fixture.

## Reprodução

Pré-requisitos locais: Python 3, Git, LLVM host, NDK r28c e arquivo ZIP fixado já existente em `E:\ESTUDO APK\work\station-netplay-20261004\upstream`. A receita valida o SHA do ZIP antes de extrair. Nunca modifica essa fonte original e recusa alterações inesperadas na cópia isolada.

O caminho `E:\R77Snes` é uma junction para `E:\ESTUDO APK\work\station-multiplayer-r77-20261008\snes`, usada para que o NDK receba caminhos sem espaços. `E:\StationNetplayWork` aponta para a base existente. Ambas as relações devem ser conferidas antes de executar a receita; `build_core.py` verifica o destino novo.

Execute nesta ordem, a partir desta pasta:

```powershell
python -X utf8 -B prepare_source.py
python -X utf8 -B run_input_tests.py
python -X utf8 -B build_core.py --stage baseline
python -X utf8 -B build_core.py --stage candidate
```

A build usa `PROFILE=performance`, `APP_ABI=arm64-v8a`, `APP_PLATFORM=android-26`, NDK r28c e as receitas JNI originais. O artefato final é copiado da saída instalada pelo NDK (que usa `--strip-unneeded`), seguida de `--strip-debug`, conforme a entrega original.

## Verificações executadas

- 1.197 arquivos da fonte conferidos contra o ZIP; somente `target-libretro/libretro.cpp` difere.
- Reprodução base byte a byte: SHA integral `cc14438319709f3b7868b3e652c731f6df472ff21bb01e4a65234ba2cc6f368b`, igual ao core distribuído; também seção `.text` idêntica.
- 6.609 verificações da fixture: 60 combinações jogador/botão isoladas, separação dos estados entre pads, 128 leituras seriais nas duas metades do adaptador, assinatura de detecção/latch, limites inválidos e equivalência das rotas sem Multitap.
- O teste reproduz 36 botões bloqueados na base (12 botões de cada um dos pads P3/P4/P5 físicos), agora encaminhados corretamente.
- Os métodos `inputPoll`, conversores, `Multitap::data` e `Multitap::latch`, enums e `libretro.h` são extraídos da fonte real. Só o callback de estados, bit IO e invólucro do controlador são simulados.
- ELF candidato AArch64, segmentos LOAD de 16 KiB e exports libretro exigidos presentes.

Não foram usados ROMs, BIOS, rede, controles físicos ou execução Android nesta fixture. Compilação e teste de mapeamento não comprovam gameplay, sincronismo, desempenho ou suporte multijogador de um título. Os recibos em `evidence` deixam esses limites explícitos.

## Arquivos e licença

`multitap-input.patch` contém toda a alteração de produção. As receitas, template do teste e recibos não incluem binários, ROMs/BIOS ou dados pessoais. A fonte fixada e suas licenças GPL permanecem referenciadas na entrega original `versions/station-online-20261004`; o patch não muda a licença do core. O binário local não deve ser publicado no Git.
