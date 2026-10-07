# R72 — registro JNI e nomes assinados da própria sala

Base: R71 completa, APK `556170c32b6dd25fb5084693826d854adf736b4a1df156fd9229a8458b025018`, instalada nos dois aparelhos. Retorno servidor `c1e44a1225a101478ceb29f4e624885331872c0d`, branch `fix/station-r71-server-recovery-20261007`. Cópia exata dos documentos e hashes em `server/ORIGIN.json`.

## Implementação

- `StationRoomRoster` consome `room.memberProfiles`, somente com a capacidade assinada `own-room-member-profiles-v1`, na própria sala, por `peerId` pertencente a `members`. Perfis duplicados/ambíguos ou malformados não substituem o outro nome. `members` e `ready` continuam autoridade. Nomes atuais da própria sala prevalecem sobre a página social; fallback limitado e reset por instância preservados. A assinatura continua verificada pelo cliente antes de entregar snapshots ao modelo.
- `StationRetroActivity` usa o candidato exato do servidor, SHA `2c160af62ca00098a0a01a3eee266e8148bdc29d88e24de567468c2cc2e65fd8`. Registra a mesma biblioteca com `System.loadLibrary` após NativeActivity.onCreate e antes de nativeLoaded; confere os dois métodos JNI de leitura e registra tipo da falha. Nenhum runtime/core, protocolo ou engineID foi alterado.

## Diagnóstico e limites

Servidor confirmou publicação v2 em 07/10 às21:59:53UTC, fonteab192bf, DLL815fc8bc e seis motores incluindo os dois Windowsd662. `recovery-failed` do anfitrião antecedeu o401; isso não prova falha de licença. O mantenedor relata tela preta em qualquer aparelho anfitrião. A coleta USB nesta etapa não retornou linhas dos tags; categoriaNATIVE_HOOK/UnsatisfiedLinkError e correção física ainda não comprovadas. O patch corrige a omissão objetiva identificada no código, sem atribuir causa definitiva antes do teste.

Referências primárias: [NativeActivity AOSP](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/jni/android_app_NativeActivity.cpp) abre a entrada nativa; [ART](https://android.googlesource.com/platform/art/+/refs/heads/main/runtime/jni/java_vm_ext.cc) resolve JNI nas bibliotecas registradas para o carregador Java.

## Compilação e verificação

`recipes/build_candidate.py` restaura a R71 pelas suas fontes e recibo exatos, aplica apenas dois arquivos declarados e compila198 fontes em Java8/API34. DEX28 permanece idêntico. Os campos changedSources/addedSources herdados do recibo de compilação são relativos à composição R67; `evidence/lineage.json` explicita o delta R71→R72 de dois arquivos,196 preservados.

`recipes/run_tests.py` repete as1152 verificações executáveis da R71 com as fontes novas e29 casos de perfis da própria sala:1181 passaram. Teste local não comprova JNIAndroid/gameplay. Os testes estão vinculados ao recibo e DEX compilado.

`recipes/package_r72.py` exige base/hash/certificado originais, muda somente classes35.dex, compara todas as outras entradas e modos de compressão, verifica classes duplicadas e alinhamento16KiB. As58 mídias, BIOS, faixa, carrossel30fps, motores e controles ficam idênticos. Temporários E:, APK G:. Instalar diretamente, preservando UID/assinatura/dados, sem partida ativa.

## Etapa atual

Compilação, 1181 verificações e assinatura concluídas. A autorização explícita do mantenedor permitiu verificar a chave local: certificado idêntico ao original, conferido antes da assinatura. APK `a8d3d28bb70618c52debf6e4cb0acaaf1f3bd1de19fe410dda85f6953caaec8e`, 2122892378 bytes. Só classes35.dex foi substituído; 13224 entradas preservadas. Consulte STATUS.json e os recibos posteriores para instalação; não é aprovação de gameplay nem versão estável geral.
