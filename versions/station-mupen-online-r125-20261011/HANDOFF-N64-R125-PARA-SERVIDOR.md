# APP → SERVIDOR: N64 próprio na R125

> Documento histórico da candidata R125. A R126 incorpora N64 e Dolphin em um APK e atualiza o marcador N64 para `1aafea201355b58909ada9958bbe5bb5407e7ace7eb3848ade7ba04d235becac`, preservando o core e os plugins. Para a entrega atual usar exclusivamente `../station-dolphin-online-r126-20261011/HANDOFF-R126-PARA-SERVIDOR.md`; não cadastrar a identidade intermediária abaixo como se fosse a R126.

## Entrega exata

Engine `mupen64plus-ae-33bf7021-n64-v3-500d48cd10f3`, backend `mupen64plus-ae-station-v1`, plataforma `n64`, `station-stream.v3`, até quatro slots físicos diretos. O app abre Mupen64Plus AE real e mantém os motores anteriores das demais plataformas.

| Identidade | SHA-256 |
|---|---|
| Core `libstation_mupen64plus_core.so` | `fe6e810a1c7fc50a494b50b1dccf581b84385667191c0cbcd235d585a0703dd8` |
| Proveniência `libstation_mupen64plus_runtime.so` | `500d48cd10f31590a52418d8417994fa5d80c38eabc4b32b55940c4f11ba8814` |
| Perfil canônico `direct-four-ports-v1` | `2966309729f8a19c03b564f0178f263170e1843172f6719002f35fb54e313f9c` |
| Manifesto engines local | `273ed233e75558cd0bac7750c688e53d940b5bb61f2130ace69b9c3ab281797f` |
| APK local | `a3ed815c01fdb0bd06a3a2485991fe8d19a51c63fee0e9255a45ecd8a9b6d4a5` |

`native/RUNTIME-IDENTITY.json` contém os doze hashes de dependências, opções com newlines exatos, canonical JSON UTF-8, nomes de bibliotecas e extensão. Esse arquivo é a referência verificável; não recompor o perfil com espaços ou outra ordem.

## Ação do operador

1. Cadastrar esta identidade com o script existente `docs/station-android/scripts/cadastrar-motor-online-station.py`, respeitando a modalidade **multiplayer v3**, os arquivos/flags documentados pelo script e o registro de perfis exato. Preservar os registros anteriores. Não basta editar o antigo EngineRegistryFile.
2. Para cada edição/mode aprovado de N64, vincular **novo engine/core/runtime/profile** ao content hash real e à capacidade comprovada do jogo. Não aumentar `maximumPlayers` nem inventar `[2,3,4]` para jogos que não permitem esses grupos. Para jogos com modos diferentes, manter a classificação por modo.
3. Confirmar que o merge atômico foi efetivamente recarregado e que a resposta autenticada fresca de `POST /v1/station/online/command` apresenta a identidade/perfil corretos e a capacidade `station-multiplayer.v3`. HTTP 200, PONG, cache ou documento no Git isoladamente não confirmam ativação.
4. Criar **sala nova** com os participantes na mesma versão; verificar anfitrião/convidados, slots reais, saída humana, perda de WSS e retomada. Registrar gameplay como evidência nova, separado dos probes isolados.

Não há nova porta UDP pública, nova rota HTTP, alteração TLS, tickets, envelope, autorização ou protocolo do relay. SN64/1 fica inteiramente dentro de DATA opaco ordenado nos links host-star v3; preserva offsets/ACK/backpressure. Não fazer tradução de dados de jogo no servidor.

O app está compilado; o cadastro não foi confirmado. Não declarar R125 estável por este handoff. Não renomear a identidade antiga do ParaLLEl para simular compatibilidade. GameCube/Wii serão entregues somente com o adaptador Dolphin e suas próprias identidades concluídos.
