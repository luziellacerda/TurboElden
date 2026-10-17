# R138 — causa do carregamento SNES e provas físicas limitadas

Em 12/10/2026, America/Fortaleza, o core SNES do APK instalado no moto g52 e as ROMs locais existentes foram executados por ferramentas isoladas. Super Mario Kart e Top Gear 3000 falharam com a configuração LLE por ausência de firmware DSP. Os mesmos conteúdos carregaram quando o HLE já existente no core foi habilitado corretamente. A comparação é independente de salas e do servidor e identifica uma causa local do carregamento nesses dois títulos.

## Cadeia causal

O APK R137 SHA-256 `fe4bc08fbc1f36d2790831f6bcd9593204ec0a032ca0d3a42c1cd385bc272719` conserva `bsnes_violate_accuracy=disabled` e `bsnes_chip_hle=LLE`. Seu `StationRetroLaunch` gera um diretório de sistema privado para o online; o `StationOnlineBios` real da R137 retorna sem preparar firmware para SNES. O inventário do APK não contém DSP1/DSP4, incluindo os ZIPs de BIOS conferidos. O core Mercury usado tem SHA-256 `0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527`, fonte fixada `79d7f9de218b6ffa65a80bbdc5828532bc239232`.

Na rota SFC por heurística, Mercury solicita `dsp1b.program.rom` e `dsp1b.data.rom` para Super Mario Kart; Top Gear 3000 solicita `dsp4.program.rom` e `dsp4.data.rom`. `Callbacks::loadFile` procura os arquivos no diretório da ROM ou no diretório de sistema e marca `load_request_error` quando não existem. `snes_load_cartridge_normal` e `retro_load_game` retornam falha. O frontend RetroArch retorna de `rarch_main` antes do encerramento normal e não chega à confirmação nativa de prontidão. As capturas anteriores registravam `nativeStatus=-1`, ausência de READY e PONG do túnel, combinação compatível com essa falha local.

O wrapper também contém uma condição que precisa ser respeitada: `read_opt()` só consulta opções de redução de precisão quando `bsnes_violate_accuracy=enabled`. Portanto, selecionar apenas `bsnes_chip_hle=HLE` com a condição ainda desabilitada mantém LLE. O DSP1–DSP4 em HLE já pertence ao core instalado; a candidata usa essa implementação existente com duas opções fixas iguais para toda a sala. SuperFX permanece em 100%; mudar as opções exige identidade e perfis canônicos novos conforme o contrato online.

## Comparação física de carregamento

A probe fornece todos os bytes da ROM ao core e um caminho SFC sintético em diretório vazio, isolando a busca de firmware. Ela não modifica o APK, não usa rede, não roda frames e não grava saves.

| Jogo | `bsnes_chip_hle` | `bsnes_violate_accuracy` | `retro_load_game` | Erros do core |
| --- | --- | --- | --- | --- |
| Super Mario Kart | LLE | disabled | false | 2: firmware DSP1b ausente |
| Super Mario Kart | HLE | disabled | false | 2: firmware DSP1b ausente |
| Super Mario Kart | HLE | enabled | true | 0 |
| Top Gear 3000 | LLE | disabled | false | 2: firmware DSP4 ausente |
| Top Gear 3000 | HLE | disabled | false | 2: firmware DSP4 ausente |
| Top Gear 3000 | HLE | enabled | true | 0 |

As seis execuções e hashes estão em [load-probes.json](evidence/load-probes.json). Essa comparação demonstra por que os dois jogos falham ao carregar com a configuração anterior e por que HLE precisa da condição habilitada. O padrão observado pelo usuário em títulos com mais jogadores não basta para atribuir a falha à capacidade de sala: Super Mario Kart tem modo de dois jogadores e apresentou a mesma dependência DSP.

## Execução física de startup

Uma segunda ferramenta executou 120 chamadas de `retro_run`, com entrada zero, depois do carregamento em HLE habilitado. Produziu vídeo, áudio e serialização em memória nos dois jogos, sem mensagens de erro do core.

| Jogo | Chamadas `retro_run` | Vídeos com dados | Dimensão final | Frames de áudio estéreo | Estado serializado | FNV-1a64 do estado |
| --- | --- | --- | --- | --- | --- | --- |
| Super Mario Kart | 120 | 120 | 256 × 224 | 63.933 | 325.179 bytes | `144479d8d0092c54` |
| Top Gear 3000 | 120 | 120 | 256 × 224 | 63.933 | 320.941 bytes | `193d7548d0a6e065` |

O core solicitou zero polls de input em Super Mario Kart e 70 em Top Gear 3000; a callback de estado sempre devolveu zero. A serialização ocorreu apenas na memória e foi descartada. FNV-1a64 não é um hash criptográfico nem uma prova de determinismo entre aparelhos. Os contadores e hashes estão em [frame-probes.json](evidence/frame-probes.json), extraídos da linha real `frame-probe-result` dos registros locais; o resumo de captura original havia omitido essa linha.

Esses 120 frames qualificam somente o startup limitado fora da Activity das salas. Não confirmam gameplay com jogadores, controles humanos, READY, rede, sincronismo, reconexão, saída Android, desempenho sustentado ou estabilidade geral.

## Encerramento nativo e reprodução da candidata

As capturas físicas R136/R137 também mostraram um segundo defeito: depois que a thread de emulação terminava, o pedido de saída tentava despertar seu looper já destruído. O tombstone R137 registrou SIGABRT em `stationRequestQuit`; a volta visual às salas ocorreu por morte do processo privado, sem validação de saída limpa.

A candidata nativa acrescenta fallback depois de `rarch_main` e torna `android_app_destroy` idempotente. Ela limpa os ponteiros do looper/config/input sob o mutex antes de publicar `destroyed`; quit usa o mesmo mutex e recusa a thread encerrada. `android_app_free` aguarda `sthread_join` antes de liberar os dados. Apenas `android_app_entry`, `android_app_destroy` e uma declaração antecipada mudam na fonte. Nenhum READY, ACK, protocolo ou capacidade foi fabricado.

Os [testes locais de lifecycle](../../integration/online-snes-startup-r138/native/lifecycle-tests.json) extraem funções reais e usam threads, mutexes e condições Windows. A base reproduz looper inválido após retorno antecipado e limpeza duplicada; a candidata passa os cenários normal, duplicado, erro inicial, 300 corridas de quit e join antes da liberação. Android e JNI nesses testes são fixtures.

A base instalada foi reconstruída a partir de 11.149 arquivos da fonte correspondente SHA-256 `b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a`. As seções produtivas de código, dados, símbolos e relocations foram conferidas como idênticas às do runtime instalado; `.comment` e `.note.gnu.build-id` são diferenças de metadados. Não se afirma identidade integral do ELF reconstruído. O [recibo da base](evidence/native-build-baseline.json) preserva a comparação e os hashes por seção.

A biblioteca candidata foi compilada em ARM64, Android 26, segmentos LOAD de 16 KiB, SHA-256 `463bdb0b409e028aa34f6c9a09d291a3715ffb3eacb8f18ee28843e7373eb80f`, 10.674.272 bytes. Só `frontend/drivers/platform_unix.c` mudou, SHA-256 `e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2`. O [recibo da candidata](evidence/native-build-candidate.json) é de compilação da biblioteca; não confirma APK, instalação ou saída física dessa candidata.

## Errata de capacidade dos relatórios R136/R137

A afirmação histórica de que o runtime instalado limitava quatro jogadores estava incorreta. A análise anterior consultou o header R77, que descrevia uma versão histórica de quatro posições. O APK instalado R136/R137 usava o runtime SHA-256 `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`, cuja fonte correspondente de cinco jogadores define `STATION_MULTIPLAYER_MAX_PLAYERS=5`, quatro bindings de convidados e máscara de dispositivos 31. A candidata R138 usa essa fonte exata e conserva essas definições.

Capacidade nativa de cinco posições não aprova cinco para todos os jogos. Super Mario Kart conserva dois; Top Gear 3000 conserva os modos de dois, três e quatro. Partida real de cinco telefones continua sem validação. A errata corrige a identificação da base auditada; ela não autoriza alterar limites por título ou relaxar o contrato de prontidão.

## Evidências públicas e aceite restante

[evidence-manifest.json](evidence/evidence-manifest.json) reúne os hashes de origem e dos resultados sanitizados. Os valores de captura originais correspondem ao stdout UTF-8 com LF; os TXT locais foram gravados com CRLF. Os recibos guardam ambos os hashes com essa distinção explícita. Não há seriais, IDs de sala, tickets, ROM, firmware, executáveis ou logs pessoais publicados nesta auditoria. As [fontes e receitas das probes](../../integration/online-snes-startup-r138/probes/README.md) recebem caminhos por parâmetros e não realizam operações USB.

As receitas públicas reconstruíram os dois executáveis em diretório privado de teste, com hashes integrais iguais aos das probes usadas fisicamente. O [recibo de reprodução](evidence/probe-recipe-reproduction.json) registra essa conferência; nenhum executável acompanha os arquivos públicos.

Para aceitar a release, ainda é necessário montar e conferir o APK final, instalar a mesma versão nos participantes, registrar as identidades/perfis HLE finais pelo operador existente do servidor, obter resposta assinada fresca e repetir início nativo/READY, partida de dois em Super Mario Kart, modos de dois/três/quatro em Top Gear 3000, perda de sinal e saída sem crash. A evidência de carregamento local sustenta a mudança de configuração; o teste de sala completo continua obrigatório.
