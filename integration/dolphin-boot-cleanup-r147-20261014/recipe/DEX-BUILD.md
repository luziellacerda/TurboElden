# R147 — montagem DEX10 de posse do boot Dolphin

Somente depois de copiar a preparação completa para `integration/dolphin-boot-cleanup-r147-20261014`, revisar também os inputs nativos separados e congelar a closure global num commit completo distinto. A receita recusa execução dentro da preparação privada.

```powershell
python -B integration/dolphin-boot-cleanup-r147-20261014/recipe/build_dex.py --base 'F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R146-relay-direto-online-20261014.apk' --jdk-bin 'F:/TurboStations-Backup-Completo-20261011/ferramentas/jdk17/bin' --apktool 'F:/TurboStations-Backup-Completo-20261011/ferramentas/apktool_3.0.3.jar' --out 'E:/StationDolphinBootCleanupR147-20261014/dex' --source-commit COMMIT_COMPLETO_R147
```

O donor FINAL R146 é SHA049302…, 2.715.073.551 bytes, fonte bfea454d…. DEX10 SHA09ed47… tem 4.991 classes. Só `org.dolphinemu.dolphinemu.features.netplay.NetplaySession` muda, quatro métodos de posse/getter/recebimento/release de boot. Os 40 fields e 63 métodos são mantidos, com 59 métodos intactos e nenhum método/classe/field novo.

`evidence/dex10-scope.json` fixa os hashes de todas as classes, 39 DEX preservados, métodos originais/raw/canônicos e cinco provas auditadas. A receita regenera o overlay a partir da classe real do donor e exige os bytes aceitos SHA00869…. Não compila/restaura Java/Kotlin de fonte histórica. As fontes antigas e fixtures são referências/provas congeladas.

Três ferramentas são compiladas: decoder DEX10, verifier com classe exata e assembler que preserva arrays de initializers estáticos de todas as classes. Cópias/hashes do conjunto suportam caminhos longos no Windows: nenhum nome Kotlin é omitido por superar 260 caracteres.

Após montar o DEX, o decoder lê os bytes reais novamente. A classe canônica deve ter SHAed45e5…; `verify_projection.py` compara todos os campos/métodos e inverte apenas os quatro corpos. Isso deve recuperar a classe original inteira SHA7dcbc…. Os outros 4.990 hashes de classe precisam continuar exatos; os 39 DEX restantes são pinados e preservados na montagem do APK. Qualquer variação de campo, callback, protocolo, visual, profile, HLE, contrôles, READY/ACK ou metadata fora da allowlist falha.

Saídas: `classes10.dex` e `dex-compilation.json`, schema `station.r147.dolphin.boot-ownership.dex.v1`, um payload/scope e closure `sourceFiles` global de `common.verify_commit`. Todo código/prova consumido precisa estar nessa closure. A receipt distingue DEX compilado de APK, core nativo, instalação e gameplay.

Há três novos sites curtos do monitor `NetplaySession.class`, usados no ciclo de boot. Os únicos callsites anteriores de getter/consume no DEX10 são os três dentro da lambda `NativeEmulation`; não foi adicionado JNI por frame, thread, scheduler ou loop. Nenhum JNI/callback/join fica sob o monitor. Não há medição física de processamento; permanece necessária validação Android de entrada/saída/perda de sinal.

A limpeza nativa `s_is_booting.Clear()` é etapa separada e exige sua própria receita/receipt do motor sobre a baseline f7ebe048…. Este builder não compila o core, renova fingerprints, assina ou instala APK e não altera a rota R146. `prepare_dex_scope_private.py` foi apenas o preparo privado do map completo; não deve ser executado para trocar uma declaração congelada.
