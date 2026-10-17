# Montagem DEX R145: literais somente nos donors reais

Execute apenas depois de revisar/copiar a preparação para `integration/sky-blue-waves-r145-20261013`, congelar todos os arquivos produtivos e registrar o commit completo. A preparação privada é recusada por `common.verify_commit`.

```powershell
python -B integration/sky-blue-waves-r145-20261013/recipe/build_dex.py --base 'F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R144-ondas-paletas-20261013.apk' --jdk-bin 'F:/TurboStations-Backup-Completo-20261011/ferramentas/jdk17/bin' --apktool 'F:/TurboStations-Backup-Completo-20261011/ferramentas/apktool_3.0.3.jar' --out 'E:/StationSkyBlueWavesR145-20261013/dex' --source-commit COMMIT_COMPLETO_CONGELADO
```

A receita exige APK R144 SHA01427, JDK17 e apktool3.0.3 pinados. Compila somente três ferramentas de decodificação/montagem/verificação, sem compilar classes Java históricas. Decodifica as partições reais DEX28/35/40, com 272/608/129 classes, copia-as integralmente e substitui exatamente dez cores em sete classes/nove métodos.

`VerifyScopedPartition` admite somente os três conjuntos de classes explícitos; não adiciona famílias ou classes. `AssembleScopedPartition` usa as APIs já qualificadas do apktool pinado e preserva as arrays de initializers estáticos de **todas** as classes, recusando qualquer novo campo ou mudança de valor. Isso conserva null/false/zero explícitos que a ferramenta antiga poderia aparar; não introduz valor novo. O guard posterior compara os bytes canônicos de todas as classes não alteradas.

Após a montagem, a receita decodifica os três DEX novamente. Cada classe alterada deve corresponder exatamente ao smali congelado em `evidence/proposed-smali`. Inverter os dez literais deve recuperar todos os bytes originais, incluindo outros métodos, fields, annotations, labels e debug metadata. Nenhuma relaxação de comparação ou reconstrução de Activity antiga é permitida.

Saídas: `classes28.dex`, `classes35.dex`, `classes40.dex` e `dex-compilation.json`, schema `station.r145.sky-blue-waves.dex.v1`. A prova inclui 1.009 classes, sete alteradas, 1.002 preservadas, maps completos, inversão por classe/método e hashes dos 37 DEX mantidos. O recibo declara montagem DEX, nunca instalação, gameplay ou aceite visual. Assinatura, identidade/runtime e montagem final do APK são etapas separadas com seus próprios guards.

As três fontes das ferramentas foram derivadas dos arquivos congelados da R144. Decoder limita as partições; verifier fixa hashes/conjuntos da R144; assembler preserva initializer arrays também nas classes com cores alteradas. Esta receita não acessa telefone, servidor, BIOS ou dados pessoais.
