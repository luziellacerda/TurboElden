# Conferência de todos os emuladores online — 11/10/2026

## Resultado atual

A seleção foi conferida individualmente nas **50 entradas de sistemas e nos 78 nomes aceitos pelo catálogo**, lendo o APK R126 assinado e executando o seletor Java real em uma prova isolada. **A migração universal para os emuladores normais ainda não está concluída.**

| Sistemas | Emulador normal | Execução online atual | Situação comprovada |
| --- | --- | --- | --- |
| Nintendo 64 e Nintendo 64 BR | Mupen64Plus AE | Mupen64Plus AE, variante Station | Integração nativa implementada na R126; partida física pendente |
| GameCube | Dolphin | Dolphin, variante Station | Integração nativa implementada na R126; partida física pendente |
| Wii | Dolphin | Dolphin, variante Station | Integração nativa implementada na R126; partida física pendente |
| PS1 | LibretroPlayer com PCSX ReARMed r26/ff81ed1 | StationRetroActivity com PCSX c8816799 | Versões do core e frontend diferentes; integração ao Player normal pendente |
| SNES e SNES BR | Snes9x EX+ | bsnes com runtime RetroArch | Motor diferente; adaptação nativa do EX+ pendente |
| Mega Drive e Mega Drive BR | MD.emu / Genesis Plus GX | clownmdemu com runtime RetroArch | Motor diferente; adaptação nativa do MD.emu pendente |
| Neo Geo e CPS1/2/3 | MAME4droid Current | FBNeo com runtime RetroArch | Motor diferente; adaptação MAME pendente |
| Neo Geo CD | MAME4droid Current | NeoCD com runtime RetroArch | Motor diferente; adaptação MAME pendente |
| FBNeo | LibretroPlayer / core externo | FBNeo com runtime RetroArch | Frontend diferente; core normal ausente no APK conferido |
| As 35 entradas restantes | Motores individuais na matriz abaixo | Sem engine Station v3 selecionável | O seletor bloqueia o lançamento; não há fallback online aprovado |

As quatro primeiras entradas representam **três sistemas e dois backends reais**; a duplicação N64/BR é mantida pelo catálogo. A presença de bibliotecas, classes, exports de rede ou quatro portas locais não valida uma partida online.

## Evidências atuais

- [Matriz completa, sistema por sistema e aliases](remaining-systems/MATRIX.md).
- [Leitura independente do APK, classes e bibliotecas](evidence/current-apk-audit.json).
- [Provas atuais de N64/Dolphin](evidence/native-system-jvm-probes.json): N64 282 verificações; perfis 98; lançamento 231; transporte 470. São provas JVM/loopback, sem execução de core ARM64, Android, ROM, servidor ou partida.
- [Seletor real executado para os 78 aliases](evidence/system-selection-jvm.json): 342 verificações; 25 aliases selecionam os motores locais existentes e 53 são bloqueados. A prova usa mocks delimitados de Context/AssetManager e os bytes do registro empacotado.
- [Auditoria PS1/MAME](psx-mame/README.md), [SNES/Mega Drive](snes-megadrive/README.md) e [demais motores](remaining-systems/README.md).

As classes dos componentes normais da matriz foram encontradas nos DEX atuais. As bibliotecas normais que estavam empacotadas na base R120 conservam tamanho e CRC. Os cores/runtimes online e as dependências N64/Dolphin coincidem com os hashes publicados; 21 métodos JNI Dolphin e cinco chamadas FFI N64 têm exports reais no APK. Os nomes `DT_NEEDED` diretos examinados correspondem a bibliotecas presentes ou à ABI Android reconhecida pelo auditor; a resolução de todos os símbolos no linker Android não foi executada.

O APK conferido permanece `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d`, 2.233.970.789 bytes. Esta auditoria não gera nem instala outro APK, muda motores offline, menus, cache, LEDs, vídeos, 30 fps dos menus ou lógica de economia.

## Lacunas concretas

1. **PS1 e famílias do LibretroPlayer:** foi localizado o loop real de eventos, execução, áudio e renderização no ELF. Sua fonte C++/receita exata não foi localizada nos locais e históricos examinados. Bloquear `retro_run` nesse loop bloquearia também os eventos; retornar sem quadro falsearia o avanço. É necessário adaptar a fronteira de quadro do Player real e validar sua reconstrução, com input e estados próprios por sessão. A versão de core normal é diferente da online.
2. **MAME/CPS/Neo Geo:** o protocolo nativo encontrado possui dois participantes e desconexões automáticas incompatíveis com a retomada Station. Precisa de adaptação de transporte, barreira real, cancelamento humano e perfil de periférico/jogo. A fonte oficial é um overlay; a receita completa de reprodução do core normal não foi localizada, e o `Android.mk` disponível recompila apenas o JNI. JNI `netplayInit` e metadados de capacidade não fazem essa adaptação.
3. **SNES/Mega Drive:** as fontes normais atuais e a cadeia de build existem. O SNES histórico não pode ser habilitado só com `NETPLAY_SUPPORT`; a build atual exclui o código e suas antigas escritas conflitam com campos constantes. MD.emu não possui integração de netplay nessa fonte examinada. A preparação isolada registra os hooks necessários, sem substituir a rota produtiva.
4. **Outros sistemas:** recursos próprios como Flycast GGPO, PSP Ad Hoc e redes de consoles não são protocolos intercambiáveis. Faltam adaptadores Station e a qualificação por jogo/modo; as restrições estão descritas por família no relatório.
5. **Oito dependências normais ausentes no APK:** melonDS, O2EM, Stella, ProSystem, blueMSX, FBNeo, Game & Watch e Virtual Jaguar. Nenhum telefone foi consultado para obter uma evidência nova de cores externos nesta conferência.

## Servidor e aparelhos

O fetch de todos os ramos dos clones existentes manteve a fonte do app em `4878e4d4a31de597f9258cc1614d1c25202d76ae`. O último código real do servidor examinado continua `141b488d6ad7fd3d2c8e74e76c1a004f1cb257fc`; `6e3a7fac6f728ec30a57bf4f4d42f00fdd1c1534` é nossa entrega R126, sem confirmação de ativação.

N64/GameCube/Wii precisam dos registros v3 e dos perfis exatos por edição/modo, de uma resposta autenticada fresca do servidor, de instalação e de salas novas nos aparelhos. A resposta deve vir de `POST /v1/station/online/multiplayer/command`; a API legada v2 não substitui essa prova. Os detalhes e objetos canônicos já estão na [entrega consolidada R126](../../versions/station-dolphin-online-r126-20261011/HANDOFF-R126-PARA-SERVIDOR.md).

Nenhum aparelho estava na depuração USB na leitura desta auditoria. Não houve instalação, criação de sala, encerramento de partida, deploy ou reinício do servidor. A compatibilidade física, recuperação de internet, controles reais e consumo continuam pendentes de medição.

## Reprodução

`tests/audit_current_package.py` exige o APK R126 exato e gera o recibo da matriz. `tests/run_current_probes.ps1` exige o rooms.jar R126 e o client.jar R124 com hashes fixos e uma pasta temporária nova. `tests/run_system_selection.ps1` também verifica o APK e o recibo estrutural antes de compilar `StationSystemSelectionProbe.java`, que roda o seletor real com os mocks em `tests/fixtures`; nunca se empacotam esses mocks no app. Os dois runners recebem os caminhos de JDK, Android API, JSON, jars e saída por parâmetros; as identidades dos inputs executáveis e das fixtures são gravadas nos recibos.

Os recibos são leitura estática e provas isoladas. A condição para declarar cada motor correto inclui o core/frontend real, o protocolo integrado, perfis assinados, periféricos/jogos suportados e partida validada; nenhuma flag local elimina essas etapas.
