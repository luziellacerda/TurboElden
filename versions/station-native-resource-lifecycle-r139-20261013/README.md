# R139 — correções de recursos e encerramento JNI

13/10/2026. Esta revisão aplica exclusivamente os erros confirmados na auditoria de recursos da R138: criação de mutex/condição/estado/pipe/worker sem validação e uma chave JNI nova a cada partida com propriedade de detach incorreta. A fonte produtiva é `integration/native-resource-lifecycle-r139-20261013`, partindo do APK R138 exato. Conferir STATUS e os recibos atuais antes de tratar esta fonte como APK instalado.

O moto g52 conectado confirmou o SHA integral R138, tela ESActivity, nenhum jogo/download/serviço ativo, temperatura de bateria 31 °C e estado térmico Android zero. A amostra de menu observou SDLThread entre 55 e 57% de **um** núcleo; o telefone tem oito núcleos. PSS 250.979 KiB, RSS 238.740 KiB e Swap PSS 71.220 KiB. Isso não demonstra o consumo em partida nem compara ganho da R139. Nenhum ANR/crash do aplicativo apareceu no trecho de log capturado; o teste humano anterior continua separado.

A reconstrução da R138 em pasta nova conferiu código, dados, relocations e layout de carregamento exatos. Só comentários do compilador e GNU build ID variam; não se afirma igualdade do arquivo ELF inteiro. A fonte R139 passou 24 cenários de recursos/TLS, 100 lançamentos e concorrência com threads/TLS reais do Windows; Android/VM/Activity/worker e bordas de alocação são fixtures nesses testes.

Somente `frontend/drivers/platform_unix.c` muda em todas as 11.149 fontes do runtime. Não alterar runloop, tempos de recuperação, core/opções/controladores/capacidade, vídeos, shaders, cache, catálogo, DEX ou frontend. O APK deverá substituir apenas `libstation_retroarch.so` e `engines.json`, renovando as identidades de nove descritores RetroArch, oito ativos, com Geolith inativo. Os quatro motores independentes PSX/N64/GC/Wii e seus wrappers permanecem exatos. O overlay NES fica fora deste reparo.

Os novos IDs reais precisam de registro pelo operador administrativo v3 atual para serem aceitos em partidas. Manter todos os registros R138 e os modos/opções já aprovados; não reduzir READY/ACK/autenticação nem alterar o servidor por hipótese. A saída com driver que nunca retorna continua exigindo trace específico; nenhum timeout genérico ou liberação forçada de objeto vivo foi acrescentado.

Receitas de patch, qualificação, freeze por commit, build, embalagem e verificação integral estão na integração. O primeiro commit congela a fonte; os recibos de compilação, assinatura, instalação e Android serão acrescentados depois, preservando a referência executável desse commit.
