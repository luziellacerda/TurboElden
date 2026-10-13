# R139 — correções de recursos e encerramento JNI

13/10/2026. Esta revisão aplica exclusivamente os erros confirmados na auditoria de recursos da R138: criação de mutex/condição/estado/pipe/worker sem validação e uma chave JNI nova a cada partida com propriedade de detach incorreta. A fonte produtiva é `integration/native-resource-lifecycle-r139-20261013`, partindo do APK R138 exato. Conferir STATUS e os recibos atuais antes de tratar esta fonte como APK instalado.

O moto g52 conectado confirmou o SHA integral R138, tela ESActivity, nenhum jogo/download/serviço ativo, temperatura de bateria 31 °C e estado térmico Android zero. A amostra de menu observou SDLThread entre 55 e 57% de **um** núcleo; o telefone tem oito núcleos. PSS 250.979 KiB, RSS 238.740 KiB e Swap PSS 71.220 KiB. Isso não demonstra o consumo em partida nem compara ganho da R139. Nenhum ANR/crash do aplicativo apareceu no trecho de log capturado; o teste humano anterior continua separado.

A reconstrução da R138 em pasta nova conferiu código, dados, relocations e layout de carregamento exatos. Só comentários do compilador e GNU build ID variam; não se afirma igualdade do arquivo ELF inteiro. A fonte R139 passou 24 cenários de recursos/TLS, 100 lançamentos e concorrência com threads/TLS reais do Windows; Android/VM/Activity/worker e bordas de alocação são fixtures nesses testes.

Somente `frontend/drivers/platform_unix.c` muda em todas as 11.149 fontes do runtime. Não alterar runloop, tempos de recuperação, core/opções/controladores/capacidade, vídeos, shaders, cache, catálogo, DEX ou frontend. O APK final substitui apenas `libstation_retroarch.so` e `engines.json`, renovando as identidades de nove descritores RetroArch, oito ativos, com Geolith inativo. Os quatro motores independentes PSX/N64/GC/Wii e seus wrappers permanecem exatos. O overlay NES fica fora deste reparo.

Os novos IDs reais precisam de registro pelo operador administrativo v3 atual para serem aceitos em partidas. Manter todos os registros R138 e os modos/opções já aprovados; não reduzir READY/ACK/autenticação nem alterar o servidor por hipótese. A saída com driver que nunca retorna continua exigindo trace específico; nenhum timeout genérico ou liberação forçada de objeto vivo foi acrescentado.

Receitas de patch, qualificação, freeze por commit, build, embalagem e verificação integral estão na integração. O primeiro commit congela a fonte; os recibos de compilação, assinatura, instalação e Android serão acrescentados depois, preservando a referência executável desse commit.

## Compilação, aparelho e prova Android concluídos

Fonte executável congelada `42da152e54bbbb4a6d569ca26fe90835503bcccb`; APK final `19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164`, 2714991631 bytes. Assinatura original v2/v3 e alinhamento 16 KiB conferidos. Instalado no moto g52, hash integral e UID/tempo da primeira instalação/diretório de dados preservados. Frontend oficial observado: true. Duas entradas substituídas, zero adições/remoções e 13.858 preservadas por SHA; todos os 40 DEX idênticos. O manifesto USB passou a apontar explicitamente essa R139; BAT e PowerShell permanecem byte exatos.

A prova isolada no Android 13/API33 usou os três helpers produtivos extraídos byte a byte, JavaVM e pthread reais: 100 inicializações criaram uma chave; 40 consultas Java registraram zero detach; oito threads nativas somaram 160 consultas e oito destructors na própria thread após remover o marcador de Activity. Todas passaram de anexadas a desanexadas pelo destructor. O scratch foi removido e sua ausência conferida. Isso valida JNI/TLS; não reproduz uma NativeActivity inteira nem uma partida online.

O estado térmico posterior foi 0 e a bateria 32.0 °C. A captura anterior estava no menu; a posterior estava em StationRoomsActivity com DownloadService ativo, cenários diferentes. Elas não provam redução de CPU, memória ou temperatura. O vídeo da plataforma e seu loop solicitado continuam iguais. Registro R139 no servidor, teste físico da saída/perda de sinal e partidas 2/3/4/5 jogadores permanecem pendentes; R138 já registrada não aprova automaticamente os IDs novos.

Recibos finais ficam nesta pasta de versão; as fontes/receitas congeladas em `integration/` não foram alteradas. O freeze descreve seu momento anterior à compilação; o status final e recibos posteriores descrevem o APK efetivamente instalado.

## Tentativa de criar sala após a instalação

O usuário relatou não conseguir criar uma sala. Na captura do moto g52 entre 09:58:45 e 09:58:49 de 13/10, quatro chamadas terminaram em `StationOnlineGame.Unavailable` durante a seleção de perfis/modos, antes da preparação de ROM/core e do comando efetivo de criação. O Java permanece idêntico à R138. Seu filtro exige perfil aprovado e correspondência exata de jogo e engine; perfis R138 não vinculam as engines RetroArch R139. Isso é compatível com cadastro R139 pendente, mas o título, a mensagem visível e o payload fresco de capabilities ainda não foram confirmados nesta captura. Ver [observação sanitizada](evidence/room-create-observation.json). `REQUEST_FAILED` com HTTP200 é uma categoria de fallback do diagnóstico e não demonstra erro de rede. Nenhum ANR do app foi observado no trecho posterior à instalação.

## Kit privado final preparado

`Kit-Servidor-TurboStations-R139.zip`: 106499932 bytes; SHA256 `1449d2f93d3aa345809529a93bcdfb143381383574c79f507181a1b8c48f8fdd`. Cinco bibliotecas, oito engines, fontes completas do runtime, overlays R138/R139 congelados, helpers históricos e proveniência de compilação. O manifesto interno confere todas as 60 entradas. [Recibo externo do ZIP](evidence/private-kit-prepared.json). A documentação dentro do kit é o snapshot usado na criação; este recibo externo posterior registra o SHA do ZIP final. Preparação não confirma recebimento, aplicação administrativa ou gameplay.

## Tela confirmada: Battletoads

Uma segunda captura USB mostrou **Battletoads in Battlemaniacs (USA), SNES**, com “Não há modo aprovado para esta edição e o motor instalado. Atualize o aplicativo e o catálogo nos participantes.” O retorno assinado documentado R138 já aprova essa edição em modos de dois jogadores, mas vinculados ao engine `bsnes-mercury-performance-79d7f9de-mt1-mp5-hle-463bdb0b409e`. O APK R139 usa `bsnes-mercury-performance-79d7f9de-mt1-mp5-hle-ae72f1371e8e`; o filtro conserva identidade exata e não trata os perfis antigos como autorização do motor novo. O operador precisa conservar os modos/edições e registrar os vínculos R139 reais. A captura confirma título/mensagem, sem fornecer o payload fresco de capabilities. A tela bruta e o nome da conta permanecem privados; [o recibo sanitizado](evidence/room-create-observation.json) registra a evidência e os perfis anteriores.
