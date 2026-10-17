# TurboStations — comparação integral e processamento

Auditoria de 13/10/2026. Referências: backup completo R124 da unidade F (`08cf0947538da796a9534d211467ecfefb4884e8`), base R134 antes dos reparos (`4f9039eb9ce13907ce043870bfe1f6e294888556`), APK R138 (`6dd36aeb353369eea4c80a0c27c9f1945bc983af`) e Git conferido `97fe6f3f3068f4c1d7ab5bd2de8ee549a0da03d8`.

**Não foi encontrada remoção das otimizações revisadas nem novo ajuste geral de velocidade nos reparos R135–R138.** A comparação integral dos arquivos e das classes modificadas corresponde aos reparos solicitados. Há falhas herdadas de recursos e riscos de montagem/driver que precisam de tratamento ou validação. Não há medição atual de CPU, GPU, RAM ou temperatura: nenhum telefone estava conectado na conferência. Esta análise não declara o produto livre de todos os erros.

## Referência da unidade F e Git

Foram lidos os documentos `LEIA-ME-BACKUP-R124.txt`, `LEIA-ME-ATUAL.txt`, `COPIA-VERIFICADA.json`, os ponteiros CURRENT/ATUAL e a documentação de desempenho/handoff no Git. O backup completo reconstruído é R124; a pasta plana `fontes/TurboElden` é histórica. A fonte posterior está nos bundles incrementais e no Git. O texto antigo LEIA-ME-ATUAL ainda chamava R135 de atual, mas os ponteiros e o hash instalado identificam R138. Selecionar fonte/APK por nome ou data pode restaurar uma versão errada.

O Git novo contém o retorno de recebimento do kit R138 e cadastro dos oito motores RetroArch, além da ampliação de catálogo NES. A ampliação NES é um overlay de fonte qualificado, **não está no APK R138**. O retorno administrativo do servidor não mede gameplay ou consumo dos telefones.

## Comparação de todos os arquivos dos APKs

Foram calculados SHA-256 dos APKs completos e de cada entrada ZIP descomprimida. CRC não foi usado como prova de igualdade. A candidata R136 descartada foi excluída; foi comparada a R136 final correta.

| Comparação | Substituições | Adições | Remoções | Entradas idênticas |
| --- | ---: | ---: | ---: | ---: |
| Backup R124 → R138 | 12 | 312 | 3 | 13.536 |
| Base R134 → R138 | 6 | 0 | 0 | 13.854 |
| R137 → R138 | 2 | 0 | 0 | 13.858 |

As 312 adições desde R124 incluem recursos dos módulos Sony, bibliotecas online, dois vídeos e duas partições DEX. As três remoções são entradas de assinatura ZIP v1; a assinatura atual original v2/v3 está registrada na entrega. As 12 substituições incluem Manifest, sete DEX, frontend, carrossel, engines e RetroArch. São mudanças das integrações/settings/loading/loops documentadas entre R125 e R134, mais os reparos online posteriores. Elas aumentam o tamanho do APK; tamanho de instalação não demonstra consumo de CPU em execução.

Desde R134, os seis arquivos substituídos são `classes35.dex`, `engines.json`, os wrappers de identidade PSX/N64/Dolphin e `libstation_retroarch.so`. Todos os demais arquivos ficaram exatos. Os wrappers foram religados com identidades atualizadas: não se afirma que todas as suas seções `.text` são byte exatas. O frontend/carrossel/cache/vídeo/preparação e 39 das 40 partições DEX são exatos da R134.

No DEX35, a projeção independente confirma R135 somente nas famílias DolphinSession/GameSession/HumanDeparture; R136 somente no construtor OnlineCoverView; R137 somente em requestHumanExit de RetroActivity; R138 conserva o DEX inteiro. Os recibos anexos listam classes, métodos e hashes. A recompilação D8 desde R124 muda também NOPs, layout de ramos/capturas e concatenações em dependências com fonte SHA idêntica; não foi alegada equivalência formal de todo bytecode recompilado. Comparações de DEX desde R124 distinguem mudanças de instruções, metadados de debug e classes sintéticas de recompilação.

## Regras de desempenho preservadas

| Parte | Comportamento conferido |
| --- | --- |
| Capas | Uma fila IO/decode compartilhada, um worker, fila limitada a nove; capa visível tem prioridade. |
| Preparação | Até 64 tentativas remotas ou 20 segundos por passe; sem repetir imediatamente erro de rede/autorização/404. |
| Segundo plano | Prefetch aguarda foreground; cancelamento e workers mantêm os gates de lifecycle. |
| Cache | Identidade exata coverId/revision, gravação atômica e caches limitados; sem abrir novo caminho concorrente. |
| LED | Geração incremental de até quatro linhas/quadro; campos/cache limitados, contexto e limpeza EGL conferidos. |
| Menu | Política de 30 fps e espera por SDL_Delay; não foi aplicada limitação nova aos emuladores. |
| Vídeos | Mídia local, decoder existente e regras de foco/pausa. Loop do vídeo de plataforma foi uma alteração solicitada R130 e mantém trabalho contínuo quando ligado. |
| Online | Filas/crédito limitados, sockets bloqueantes, espera de reconexão; nenhum loop puro sem espera encontrado no escopo efetivo. |
| SNES | Mesmo core; somente HLE DSP e a opção necessária para o core aceitar HLE. SuperFX continua 100%, sem overclock adicional. |

As fontes de Queue/Cache/Store/API/Catalog são exatas R116→R117→R124 e foram herdadas pelos overlays posteriores. As políticas de menu/pacing/vídeo foram conferidas por hash e pelas transformações de fonte. A R136 desliga o efeito GLES opcional da capa apenas no moto g52 após o ANR comprovado no driver; a imagem principal permanece. A R138 altera duas funções de encerramento nativo e uma declaração, com inversão exata do patch; não muda o loop de emulação.

## Falhas e riscos encontrados

**P1 — falta de memória/recursos ao criar a thread.** Em `platform_unix.c`, android_app_create não confere todos os retornos de mutex, condição, malloc, pipe e sthread_create. Se o worker não nasce, a UI espera running indefinidamente. Retornos nulos também podem chegar às primitivas de condição ou memcpy; falha de pipe vaza mutex/condição. A causa foi reproduzida com seis falhas injetadas na função produtiva. É uma falha herdada, não uma mudança de desempenho introduzida pelos reparos. Não é prova de CPU a 100% nem a causa demonstrada do ANR anterior do g52.

Foi preparada uma **candidata isolada** que confere as alocações, libera os recursos antes de existir worker e fecha a Activity apenas na falha de criação. Os seis cenários retornam sem espera, com zero recursos retidos; o caminho de sucesso preserva o handshake. Todos os demais bytes da fonte R138 são iguais. A candidata está em `candidates/station-native-resource-failure-20261013`; não foi compilada como runtime Android ou instalada e exige identidade nova se incorporada.

**P1 condicional — montar NES com uma fonte antiga.** O snapshot C++ NES é R124 com dois limites alterados. Copiá-lo inteiro sobre o frontend corrente removeria os exports de preparo/loading R132 usados pelo carrossel. A receita original pede o patch sobre a composição atual; foi acrescentada uma verificação de preservação que aceita somente sete limites e uma query, conserva todos os demais bytes e rejeita o snapshot antigo, workers extras, reescrita de finais de linha, fonte extra e edição não relacionada. Esse risco não entrou no APK instalado.

**Riscos herdados a acompanhar.** Os waits nativos normais de janela/estado/destroy e join não têm prazo; um core/driver que nunca retorne ainda pode bloquear a saída. A correção R138 cobre retorno precoce e looper obsoleto, sem comprovar recuperação de todo travamento de driver. A fonte completa também cria uma chave TLS JNI a cada Activity e não apresenta delete/reuso correspondente para essa chave. Se o mesmo processo ficar vivo entre partidas, as chaves podem acumular; é uma observação estática P2, sem reprodução física de esgotamento. Não foi incluída na candidata de alocações, porque o lifetime JNI exige revisão própria. Não foi aplicada liberação forçada de objeto vivo, timeout genérico ou mudança dos controles de reconexão.

O controle online tem custo periódico limitado: até quatro links no host, tick de 250 ms por link, loop de recuperação nativo com espera de 50 ms e heartbeat do owner a cada 20 segundos. Long-poll social depende do servidor aguardar quando a revisão não muda. Essas observações não demonstram consumo excessivo. Alterar frequências sem medir pode atrasar reconexão, ACK e READY.

## Verificações executadas e limites

Passaram 72 verificações de fila de capas, 54 de warm cache, 23 de diagnóstico, 46 de lifecycle GPU com 400 inicializações serializadas e 1.211 de balanço EGL. A fixture de symlink do ledger não é suportada neste Windows; a parte de acesso direto legado foi executada. A verificação NES aceitou a composição corrente e recusou cinco montagens indevidas. As seis falhas de recursos, o caso de sucesso e quatro casos de estado salvo vazio foram qualificados no host com funções reais extraídas e primitivas simuladas.

Essas provas verificam lógica e preservação. Não substituem perfil físico Android, driver Adreno, pressão real de memória, gameplay, retorno de sinal ou ensaio térmico. O APK R138, os dados, saves e configurações dos telefones não foram alterados por esta análise. A proposta de recursos e os guards pertencem à revisão de fonte; não constituem uma R139 instalada.

## Provas e reprodução

O diretório `evidence/` contém a comparação integral, auditoria de histórico, avaliação online, injeção de falhas e verificação NES. Os inventários integrais SHA de R124/R138 estão no ZIP entregue ao mantenedor. `recipe/verify_nes_preservation.py` é somente leitura e compara diretórios antes/depois da composição atual. `recipe/test_nes_preservation.py` reproduz seus testes em pasta nova fora das fontes congeladas. A candidata de recursos tem sua própria receita e STATUS.

Antes de uma futura entrega, aplicar somente overlays solicitados à composição corrente, validar classes DEX e todas as entradas finais, preservar certificado/dados, instalar em telefone autorizado ocioso e medir menu, fundo, abertura/saída, jogo/queda de sinal e pressão de memória. O diagnóstico de um novo ANR deve usar a thread/driver capturada, sem atribuí-lo automaticamente à CPU ou ao servidor.
