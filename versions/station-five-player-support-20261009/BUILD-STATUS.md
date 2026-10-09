# Estado da compilação de cinco jogadores — 09/10/2026

| Etapa | Estado | Evidência |
|---|---|---|
| Conjunto Java completo | Compilado, 209 fontes | `evidence/java-build.json`, `JAVA-SOURCE-MANIFEST.json` |
| DEX salas | Compilado e entregue | `compiled/rooms.dex`, SHA82609bdc |
| DEX client | R81 reproduzida e entregue | `compiled/client.dex`, SHAe7207a89 |
| Runtime Android | Compilado AArch64/API26/16KiB | `native/runtime/libstation_retroarch.so`, `evidence/native-build.json`, SHA81b3daa3 |
| GPL correspondente | Integral entregue | Archive, COPYING e manifesto em `native/` |
| Parser/avisos/modos Java | 166 checks passaram | `evidence/profile-tests.json` |
| Ownership C com threads host | 1.176 checks passaram | `native/tests/native-result.json` |
| Core P1–P5 | Recibo R77 preservado | `evidence/core-input-existing-r77.json`; 6.609 checks anteriores, não repetidos |
| APK integral assinado | Pendente no PC do APK | Receita pronta, requer APK/keystore privados originais |
| Instalação nos aparelhos | Pendente desta sucessora | Não inferir pelo recibo R81 |
| Gameplay de cinco Androids | Pendente | Teste físico descrito na entrega única |

As receitas de recompilação foram conferidas em sintaxe; Java e teste de perfis foram executados usando essas receitas. O runtime foi compilado na mesma fonte integral e opções registradas. A receita portátil de recompilação nativa e a montagem do APK completo não foram executadas novamente neste Linux. Nenhum APK, ROM, BIOS ou segredo privado foi publicado.
