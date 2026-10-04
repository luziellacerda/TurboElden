# R4 — Mega com sinopses corrigidas, revisão de Netplay e publicação segura de capas

## 1. Estado atual

Este é o estado mais recente da branch `feat/station-capas-visuais-netplay-20261003`. R2/R3 são históricos. Pacote `org.turboramastation.frontend`, cliente Station `1.0.8-station-covers-20261003.5`.

- Pasta canônica: `E:\ESTUDO APK\work\station-visual-covers-20261003`.
- APK pronto: `E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R4-20261003.apk`.
- SHA-256: **`17e9b87bf268c2349874d1767d5ab315862eb09fb2705f9b79a7e307c0c63c77`**, 1922509146 bytes.
- Compilado, assinado e testes completos no PC aprovados. **Não instalado: USB ausente.** Último APK confirmado no aparelho é R2 `31ab80ef...`; ele ainda apresenta as sinopses mal associadas. R3 também não chegou a ser instalado.
- Fontes e evidências desta pasta; base HUD6b83ed, assinatura original e motores preservados. Nenhuma implantação Linux, alteração de licença ou dado do aparelho nesta revisão. Não promovido à tag estável.

## 2. Sinopses do Mega Drive — causa e prova

O R2 utilizava a lista preliminar de IDs. A conciliação definitiva do servidor preserva os IDs antigos. Entre os 741 IDs corrigidos, **617 são Mega Drive e 89 MegaBR**, total 706. O R3 já corrigia a tabela; R4 mantém essa correção e testa o mesmo código C++ chamado na tela.

| Plataforma | Jogos no catálogo | Sinopses de fonte confirmada | Sem texto inequívoco |
| --- | --- | --- | --- |
| Mega Drive |887|882|5|
| Mega Drive BR |94|93|1|
| Total |981|975|6|

O conjunto inteiro continua1816 jogos / 1804 descrições / 12 ausências. Fonte canônica: Servidor-pix 54bba11, `catalogo-conciliado-jogos-capas-downloads-20261003.tsv`, SHA3542803f0887a3595bfcae6f2c1bd5e860b5ab81df32f308c2f3ac1fbd071f12. IDs do servidor não foram alterados no app.

`native/station_game_lookup.h` contém a consulta binária exata extraída de `native_info.h`. O carrossel e `test_station_game_lookup.cpp` usam **a mesma função e a mesma tabela**. Foram3636 verificações: todos os 1816 IDs encontrados na plataforma correta, plataforma incorreta recusada, contagens Mega/BR, identidade ausente e **Cutthroat Island**, ID `ce3f245960b94e064f027ffd8aefe466`, texto613 caracteres antes da paginação. A biblioteca compilada do carrossel ficou idêntica ao R3, pois só a função foi extraída para testar sem alterar comportamento.

As seis ausências Mega são: Lethal-wedding; Columns III (USA); Tetris; Battletoads-Double Dragon (USA); Sonic The Hedgehog 3 (USA); Sonic Hedgehog 3D Blast (BR). Não foi inventada sinopse nem selecionada edição por semelhança. Ver `evidence/mega-synopsis-verification.json` e os motivos da busca XML já registrados.

## 3. Netplay — o que existe de verdade

O motor Mega integrado é MD.emu, upstream1c12fac5. O mantenedor do projeto ainda lista jogo em rede como melhoria solicitada, e o motor integrado não expõe essa função. [Pedido oficial](https://github.com/Rakashazi/emu-ex-plus-alpha/issues/330). O suporte local a controles de vários jogadores não cria uma conexão pela internet; as opções locais constam na [documentação MD.emu](https://www.explusalpha.com/contents/md-emu).

A tela “Jogar em rede” agora informa **antes dos botões** que Mega/SNES são locais com os motores atuais. Não existe botão que simule uma sala nem endpoint inventado. Mantêm-se as três integrações:

| Plataforma | Ação real |
| --- | --- |
| PSP |`PspBootstrap.launch(Activity,"",true)` abre configurações próprias; WLAN/ad hoc/relay configurados no PPSSPP; sala criada pelo jogo. [Guia oficial](https://www.ppsspp.org/docs/multiplayer/quickstart/) |
| GameCube/Wii |Snapshot privado de jogos instalados → processo Dolphin → GameFileCache → `NetplaySetupActivity` original. [Implementação Android upstream](https://github.com/dolphin-emu/dolphin/pull/14647) |
| Dreamcast/Naomi |`FlycastBootstrap.launch(Activity,"",true)` abre configurações próprias; opções de rede dependem do título/modo. [Opções upstream](https://github.com/flyinghead/flycast/blob/master/core/cfg/option.cpp) |

As signatures locais das pontes PSP/Flycast foram conferidas; os contratos do Dolphin, arquivos privados e texto da interface passaram28 verificações. Isso não comprova uma partida entre dois aparelhos. O catálogo Station atual de SNES/Mega não se torna jogável online por haver esse menu.

**Para Mega online real**, seria necessário implementar sincronização de entradas/quadros/estado no motor ou integrar um motor que ofereça isso, com compatibilidade de ROM/versão, conexão e testes de dessincronização. Não se fez essa troca nesta revisão: manter controles, saves e configuração atual foi preservado. Um lobby próprio Station também exigiria serviço separado; o contrato atual de licença/catálogo/capas/downloads não oferece salas de partidas. Não enviar pedido ao servidor dizendo que basta liberar uma rota existente.

## 4. Complemento ao commit do servidor1dc8c381

A revisão anterior já incorporava quatro workers, remoção de pausa fixa, cache persistente, TLS reutilizável após corpo completo e hash do arquivo exato antes da busca. A revisão do mantenedor identificou uma omissão real: limpar a fila nativa ao substituir catálogo e liberar slots enquanto a aplicação do catálogo aguarda um download ativo. R4 incorpora essa parte.

Sequência corrigida:

1. `StationCoverQueue.replaceCatalog`: sob o monitor de publicação, incrementa geração, captura as tarefas antigas e conclui cada uma uma única vez como cancelada. IO antigo pode terminar depois, sem emitir outra conclusão.
2. A troca do catálogo nativo ocorre **sob o mesmo monitor**. `Task.finish` também faz o teste de conclusão dentro dele. Não há janela para um resultado antigo entrar depois da publicação nova.
3. `publishCatalog` limpa `inbox.covers` sob seu mutex antes de depositar a lista nova.
4. No SDL, `resetCoverPublication` limpa slots/retry individuais e flagscoverPending, liberando a lista antiga enquanto o catálogo novo espera o download. Mantém o cache existente, progresso/recibo do jogo e a suspensão global de429.
5. A proteção por leases da sessão, geração, Retry-After e plano da plataforma/pasta permanece. Quatrocapas continuam, sem atraso fixo depois de sucesso.

O defeito foi reproduzido usando a `StationCoverQueue` congelada do R3: o novo teste falha em “Every old request must finish before JNI publishes a catalog”. No código corrigido,180 verificações em20 corridas passam. Ver `evidence/publication-red-green.json` e logs em `pc-validation-r4/logs/publication-*`. O fixture usa fila Java real e simula a caixa de entrada nativa; a política C++ usada na produção foi executada separadamente em10 casos.

A fixture Android `station/tests/station_frontend_test.cpp` recebeu os casos do handoff: imagem antiga descartada e slots livres com download ativo. Compilou arm64/API26/16KiB, SHA231252b39982199d364fe7a975c88c309b31052fdbf3b447c921554dfc8d9c72; ainda **não executou no Android**, pois não há USB.

## 5. Testes e limites

Execução completa: `E:\ESTUDO APK\work\station-visual-covers-20261003\pc-validation-20261003-223241`; [recibo](pc-validation-r4/PC-TEST-RESULT.json).

-564 verificações Java, incluindo180 novas;10 repetições extras da suíte de41 casos.
-28 casos C++ executados de planejamento/retry/publicação;9 asserts de exportação;98 de layout.
-17 testes de metadados e3636 consultas nativas de sinopse.
-28 verificações Netplay; shaders GLES100 compilados/linkados no ANGLE com leitura de pixels.
-4096capas simuladas, pico4, erros0;cache4096,HTTPextra0,workersapósfechar0.
-DEX Station/Netplay reconstruídos idênticos aos incorporados; ponte ARM64 recompilada; assinatura original, alinhamento16KiB, CRC integral e preservação de10871entradas antigas passaram.

A carga usa transporte sintético, não mede velocidade real no telefone. O driver Android foi observado no R2, mas os testes de UI R4, corrida nativa JNI e partida Netplay entre dois dispositivos seguem pendentes.

## 6. Reprodução e entrega

Usar `station/run_tests.py` → `station/build_module.py` e `station/build_frontend.py`; `netplay/test_contracts.py` → `netplay/build_netplay.py`; `build/build_visual_delivery.py native` → `package`; conferir `build/verify_visual_manifest.py`; bateria isolada `pc-validation-r4/run_pc_validation.py`. Compilar/temporários em E:. O manifesto das duasActivities internas permanece o doR2; toda a configuração antiga foi preservada.

O backup do candidato R3 está em G:, conforme `archived-r3-apk.json`; hash conferido antes de remover apenas a cópia de E: para espaço. R2 instalado, base HUD e estável de recuperação estão preservados. APKs/binários, jogos, BIOS e credenciais permanecem fora do Git; insumos privados no manifesto existente. O histórico R3 necessário para reproduzir a falha está em `history/8ece6384/`.

Quando a USB voltar: instalar **R4**, conferir hash, manter licença/dados, abrir Mega/Cutthroat Island e MegaBR, rolar capas e voltar; testar atualização de catálogo durante download em fixture isolada; abrir Jogar em rede e conferir retorno. Não desinstalar para testar. Restaurar `stay_on_while_plugged_in=0` e remover somente os probes próprios listados em `device-evidence/status-r4.json`.

## 7. Referências restantes

O mapa completo de funções/rotas Station, política de sessão, licença, cache e instalação está nas seções técnicas do README histórico; a correção de IDs e dados XML está no `HANDOFF-R3.md`. Para **estado de instalação e APK atual**, prevalecem este R4 e seu recibo. Nenhuma configuração Linux foi alterada. Os limites do servidor conhecidos continuam os do retorno 54bba11: API 4bb77ed2, catálogo 1816 / revisão 4, quatro capas,4096 pedidos/minuto por licença/aparelho. Capacidade 40 mil e novas plataformas continuam fora desta revisão.
