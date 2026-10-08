# TurboStations R74 — candidata de recuperação online

## Estado

Compilada e assinada com o mesmo certificado. **Não instalada e não homologada em partida real.** Ambos aparelhos continuam na R73 nesta entrega. O operador precisa cadastrar as duas identidades novas do runtime antes da conferência online.

- APK local: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R74-20261007.apk`
- SHA-256: `e56896f28b16645653bfd28311cd0a8a9a5458e6d443849916a4dede6dc7fafe`; `2122907720` bytes.
- Runtime: `804b2acfea4c6d615bf40dba30e1777015098bf7375d0745db8d117555eb2516`.
- Fontes: branch `fix/station-r74-session-lifecycle-20261007`; `SOURCE-FILES.json` identifica cada arquivo.
- Contrato/causas/evidências: [handoff ao servidor](HANDOFF-APP-R74-PARA-SERVIDOR-20261007.md).

## Alterações delimitadas

Vínculo privado do processo do jogo com a autoridade HTTP; identidade e ACK por Messenger; cleanup de lançamento com resultado Android; encerramento nativo sem inversão de mutex; reserva de uma Activity; reset somente em sessão nova; consumo da fila Android durante espera; retirada da escalada indevida de catch-up para NeedSync13. Permanecem autenticação, tickets, offsets, pausa real e barreira READY. Não houve ajuste arbitrário de temporizadores, resolução, controles, frames ou cores.

## Validação

201 fontes Java compostas de R73, 195 fontes existentes preservadas; 1.206 verificações históricas em execução separada das101 verificações de sessão e42 guardas. Três probes nativos com funções reais extraídas e partes Android modeladas; 200 ciclos de catch-up e2.400 eventos de entrada. Não são gameplay nem ensaio de rede real.

Exatamente quatro entradas APK substituídas e13.221 conferidas como preservadas. Cores, DEX28, mídia, carrossel e demais emuladores idênticos. Contagem efetiva do arquivo:59 entradas `.mp4`, todas preservadas; contagens58 fixas de recibos anteriores não são usadas como gate desta entrega.

## Reprodução neste computador

Base privada R73 identificada acima no handoff; JDK17, SDK/API34 e NDKr28c nos caminhos verificados pelas receitas. Fonte/temporários na unidadeE:, APK finalG:. Não executar receita antiga sobre este candidato.

1. `recipes/build_native_r74.py --repo <repo> --delta <snapshot>/native --output E:\R74fixed` reconstrói R73 e aplica os seis arquivos revisados. `--incremental` aceita apenas hashes já registrados; nunca aponta para fonte desconhecida.
2. `recipes/build_candidate.py --output <nova pasta em E:>` recompõe as201 fontes e gera DEX35. DEX28 deve continuar bit a bit igual.
3. `recipes/run_tests.py --workspace <mesma pasta>`; `tests/session/run_session_tests.py`; `tests/test_manifest.py`.
4. `recipes/patch_session_manifest.py --repo <repo> --workspace <mesma pasta> --base <APK R73>` e `recipes/prepare_engine_registry.py --workspace <mesma pasta>`.
5. `recipes/package_r74.py --snapshot <snapshot> --workspace <mesma pasta>` exige certificados idênticos e quatro variáveis de assinatura `STATION_*` já autorizadas. Não contém senha/chave. Recusa sobrescrever APK e verifica cada entrada após assinar.

Receitas de teste de sessão/manifesto têm diretórios de evidências emE: fixados neste snapshot. A assinatura e o APK base são privados; não fazem parte do Git. Não limpar dados, desinstalar ou trocar chave como atalho.

## Pendências reais

Medir o caminho completo DATA/PONG no servidor; explicar a primeira queda23:52:14UTC e a origem dos epochs2–19; registrar duas adições preservando os oito motores ativos; instalar a mesmaR74 nos dois aparelhos em momento sem partida; validar presença/renovações, toques durante espera, jogo com entradas reais, reconexão e saída/reabertura. Não chamar o candidato de estável antes dessas provas.
