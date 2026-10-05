# Entradas e ordem de reconstrução

Não execute em diretório existente contendo uma montagem ativa. Os scripts falham se uma etapa que cria estado já foi executada. Preserve a versão aprovada e os dados do telefone.

## Entradas privadas e públicas

- Base R14B exata, SHA/tamanho do README. Ela está arquivada em G:, não mais no antigo caminho E:.
- Fonte nativa R14B completa: `versions/station-navigation-r14b-20261005/native` no Git para os arquivos dessa revisão, completada pela árvore canônica `E:\ESTUDO APK\work\station-netplay-20261004\native` que esta entrega não modificou. Dependências e objeto `video720_posters.o` são os do build R14B. O recibo lista os hashes de origem.
- APK oficial Mupen64Plus AE extraído do ZIP verificado. Código fonte upstream e commit no README. Licenças originais permanecem aplicáveis.
- JDK, SDK, apktool, NDK/LLVM e certificado original, nos caminhos de ferramentas dos scripts. Não publicar a chave de assinatura.
- Fontes Java desta pasta. MAME nativo vem da base; não baixar outro donor MAME para montar esta correção.

## Receita N64

Os scripts em `recipes` são cópias dos passos executados, com diretórios explicitados por variáveis de ambiente. Trabalhe dentro de `recipes` e use pastas novas em E:.

1. Definir `STATION_N64_WORK`, `STATION_EMULATORS_WORK`, `STATION_BASE_APK` e `STATION_BASE_NATIVE`. A última deve apontar para a árvore R14B completa, não um checkout antigo. Reservar espaço para duas cópias do APK durante assinatura.
2. Criar `tmp` e `framework` no diretório N64; decodificar o APK oficial com apktool3.0.3 para `<STATION_N64_WORK>/donor` usando o framework dessa pasta. O arquivo `mupen64plus-ae-master.zip` e `release.json` verificados são entradas de proveniência/testes.
3. `python prepare_n64_merge_r15.py`: extrai os recursos da base e aplica `merge_resources.py`, que está integralmente neste snapshot. Não depende do antigo `build_mame.py`.
4. `python finish_n64_runtime_r15.py`: isolamento de preferências, preparação inicial, partição DEX, bibliotecas C++ e compilação da ponte/recursos.
5. `python correct_n64_launch_lifecycle_r15.py`: preserva o recebedor de resultado do jogo e recompila a versão final da ponte.
6. `python final_runtime_adaptations.py`: retira sincronização de canais TV e o instalador de perfis do donor. Reexecutar somente `apktool b` em `merged`, produzindo `n64-resources-dex.apk`; não executar novamente as etapas de transformação.
7. `python prepare_n64_application_r15.py`: injeta a inicialização dos dois processos N64 no DEX base conferido.
8. `python build_n64_native_r15.py`: copia a árvore nativa R14B, adiciona o roteador N64 e compila o SO. Os sete arquivos de visual/pacing/mídia/netplay são comparados byte a byte à origem.
9. Conferir classes/recursos/rotas/preparação com os testes deste snapshot. Os testes de proveniência usam a base R14 arquivada, cujo DEX e recursos são idênticos aos da R14B; seus paths estão explícitos e podem ser atualizados para o arquivo arquivado correspondente.

## MAME corrigido

Compilar os dois arquivos em `mame/java` com javac UTF-8, source/target8 e android.jar34. Converter com D8, min-api26, lib android.jar34, para `classes30.dex` em `STATION_EMULATORS_WORK`. O recibo `evidence/mame/build.json` contém SHA anterior/final. Executar `test_mame_paths_r15.py`, apontando a pasta de fonte/tests para esse diretório. O teste compara a chave com o donor original já presente no PC.

## Empacotamento

`python package_emulators_r15.py` usa exclusivamente a base de hash R14B esperado e os artefatos das etapas acima. Preserva todas as entradas não previstas, adiciona recursos e assets oficiais, alinha na escrita e assina com o certificado original. Confere novamente cada entrada, certificado e alinhamento; registra `build-result.json`. Não inclui os perfis `assets/dexopt` do donor.

O hash do ZIP final pode variar com timestamps da reconstrução. Comparar também SHA de DEX/SO, recursos e manifesto de entradas; nunca assumir equivalência apenas pelo nome do APK. A execução Android continua sendo uma etapa distinta.

O ambiente original compilado permanece nas duas pastas E: descritas no README, com logs e arquivos intermediários. As receitas com diretórios parametrizados foram revisadas sintaticamente; a montagem executada/provada usa os diretórios exatos dos recibos. Não afirmar reconstrução limpa independente já repetida com essa cópia parametrizada.
