# R64 — controles online e diagnóstico da queda — 07/10/2026

**Candidato compilado, ainda não instalado. A queda não está declarada corrigida.**

Base: R63 `8613d88d4f553e72e5fedcd1d3ea470010301734`, APK `d9a35602ddc1141617df70d4b2b1f202d8646c538d4508f5fb3e53ef6b7abc4c`. O mantenedor confirmou que a partida online funcionou e que os controles respondem; quer a aparência do modo normal. Não equivale a homologação de estabilidade, latência, saída ou todas as plataformas.

## Mudanças exatas

- SNES/Mega usam as texturas originais dos controles EX, extraídas por retângulos de `AppMeta.cc`, sem redesenhar os pixels. Atlas e licença estão em sprite-source; receita Java reproduz a extração. São controles adaptados à API de input overlay do RetroArch, não execução do Snes9x EX+/MD.emu no online. Posições normalizadas; SNES ABXY/L/R/Select/Start, Mega ABC e alternância 3/6 com XYZ/Mode. Configurações personalizadas do controle local não são importadas.
- `engines.json` muda somente os dois caminhos overlay. IDs, hashes de cores/runtime/opções, extensões, autenticação e protocolos ficam iguais à R63. Neo Geo continua não liberado no online.
- `StationRetroLaunch`: opacidade .75→.55. `StationRetroActivity`: três pontos no canto superior direito abrem o HUD online já existente (Continuar/Voltar às salas); toque dos jogos permanece nativo. Atalhos de menu RetroArch/troca de orientação/combos extras saíram dos novos layouts. Botão Voltar existente preservado.
- `StationRelayTunnel`: registra código e origem do fechamento, classe de exceção, contadores de bytes, idade do pong e duração da escrita local pendente. Não registra o texto recebido do servidor, token, endereço, ROM, nome, sala ou licença. Fechamento, limites e fluxo de bytes não foram alterados. Callback trace não pode derrubar a sessão.
- `StationGameSession`: registra sucesso/duração e correspondência de sala do heartbeat; Activity registra onStop. Não foi implementada reconexão automática nem alteração de timeout por suposição.

## Compilação e limites

161 Java / 157 preservados / quatro alterados. Java8/API34/D8mín26. Os302 checks existentes passaram, mais o teste de diagnóstico de fechamento/pong/idempotência/privacidade/timeout intacto. Validação dos layouts: bindings completos, imagens presentes, áreas dentro da tela e sem atalhos inseguros.

APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R64-20261007.apk`
SHA256: `e2bb778319e03d878ac5de3749f06af1b5e7bbffd06b8232402d2d2f610ba868`
DEX35: `b11459d8bf42e12d26ed5103b9ed62d1e0df674cfc31c79bffe49b48756f2a97`
Assinatura: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

Entradas alteradas: assets/station-online/engines.json, classes35.dex. 13193 entradas preexistentes preservadas e 24 adicionadas; todas comparadas por hash. Alinhamento16KiB. Motores locais, dados, carrossel, recursos, faixas, vídeos e licença preservados. Runtime online899e3527 idêntico; R63/R64 compartilham a identidade de partida.

Fonte/build: `E:/ESTUDO APK/work/station-online-controls-r64-20261007`. Restaurar com `python recipes/restore_sources.py E:/pasta-nova`, compilar `python build_java.py final`, testar `python run_local_tests.py`, definir as quatro variáveis privadas de assinatura STATION_KEYSTORE/STATION_KEY_ALIAS/STATION_KS_PASS/STATION_KEY_PASS e empacotar `python package_r64.py`. Esta receita exige o APKbaseR63 e não sobrescreve candidato existente. Dependências externas iguais ao handoffR63. Nunca usar o empacotadorR63 para esta revisão.

**Ainda sem conferência Android do novo layout, sem prova de retomada após queda, sem servidor alterado.** Instalar só após sair da partida, com atualização -r, mesma assinatura e sem limpar dados. Mantenedor confirma controles/diagonais/multitouch/Mega3e6/menu/Voltar. Registros privados da falhaR63 preservados apenas emE:.

Leia `HANDOFF-QUEDA-ONLINE-APP-PARA-SERVIDOR-20261007.md` para o diagnóstico e o pedido preciso ao operador. Não confundir este pedido com retorno do servidor.

Restauração em diretório novo da unidade E: conferida: 161 entradas Java com hashes idênticos e DEX recompilado `b11459d8bf42e12d26ed5103b9ed62d1e0df674cfc31c79bffe49b48756f2a97`, igual ao empacotado. Recibo em evidence/restoration-check.json. Isto verifica a reprodução do candidato, não a retomada de rede.
