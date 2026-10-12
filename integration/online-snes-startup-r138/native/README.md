# R138 — encerramento da thread nativa após falha de inicialização

A base corresponde ao runtime instalado de cinco jogadores, SHA-256 `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`. O `platform_unix.c` original tem SHA-256 `baa00df315ba604e1ac5612e2186a685c27b843c20bcaea2f27c6a4036f7e7db`; o arquivo `retroarch-corresponding-source.tar.gz` tem SHA-256 `b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a`. A receita exige essa fonte exata e confere o arquivo de fontes correspondente quando fornecido. Não usa a base R77 de quatro jogadores.

`rarch_main()` pode retornar antes de `frontend_unix_deinit()` quando o carregamento inicial falha. Antes, `android_app_entry()` terminava sem publicar `destroyed`; o ponteiro de looper permanecia preenchido mesmo depois de Android encerrar a thread. Um pedido de saída podia então chamar `ALooper_wake` no objeto já destruído. A R137 física registrou esse abort nativo.

O patch modifica somente `android_app_entry` e `android_app_destroy`, acrescentando uma declaração antecipada da segunda função. A entrada registra somente o código inteiro retornado por `rarch_main` e chama o encerramento idempotente. O encerramento reaproveita a limpeza existente, verifica `destroyed` sob o mutex, libera o estado uma única vez, limpa os ponteiros de input/config/looper e publica `destroyed` antes de a thread retornar. Pedidos de quit usam o mesmo mutex e passam a recusar uma thread encerrada. O callback Java existente permanece responsável pelo retorno à tela do aplicativo. O objeto continua vivo até `android_app_free()` completar `sthread_join()`.

Nenhuma prontidão ou ACK é fabricado; nenhum transporte, perfil de controle, capacidade de jogadores, core, opção de emulação ou fluxo de reconexão foi alterado por este patch. Ele encerra corretamente uma inicialização falhada. A correção da causa da falha de carregamento é uma parte distinta da candidata R138.

## Receita e escopo conferido

`../recipe/patch_native_lifecycle.py BASELINE [--archive ARCHIVE]` produz `source/frontend/drivers/platform_unix.c` e `lifecycle-source.json`. A receita aplica as duas alterações e as desfaz em memória para demonstrar que todos os bytes fora dessas funções e da declaração antecipada continuam idênticos. Ela recusa uma base de hash diferente e uma candidata existente com conteúdo inesperado.

`../recipe/test_native_lifecycle.py BASELINE --work DIRETORIO_TEMPORARIO` extrai sete funções reais da base e da candidata para a fixture `tests/lifecycle_harness.c.in`: `station_activity_release`, `android_app_request_quit`, `android_app_free`, `onDestroy`, `free_saved_state`, `android_app_destroy` e `android_app_entry`. O teste usa mutexes, condições e threads reais de Windows, compilados com Clang, `-Wall -Wextra -Werror`. Android, JNI, o looper e a configuração são representados por fixtures com contadores de vida e limpeza.

Os cenários verificam encerramento normal, deinit duplicado, retorno antecipado de erro, 300 corridas entre retorno nativo e 2.128 tentativas de quit por repetição, e `onDestroy` aguardando o join antes de liberar dados/reserva. A base falha em limpeza duplicada, retorno antecipado e quit após o fim da thread; a candidata passa nos cinco cenários. A verificação do join mantém a thread suspensa depois do deinit e confirma que `onDestroy` ainda não liberou o objeto antes do retorno efetivo da thread.

Resultados em `lifecycle-tests.json`. As provas são locais de lifecycle com fixtures. Não houve compilação integral da biblioteca por esta tarefa, execução Android, instalação, jogo real, sincronismo ou homologação do produto.
