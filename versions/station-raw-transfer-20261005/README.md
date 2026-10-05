# Downloads Station: CHD direto e ZIP sem CRC — 05/10/2026

## Estado desta entrega

Pedido do mantenedor: Neo Geo CD lento em **Baixando e Preparando**; remover conferências de integridade/conteúdo que atrasam downloads e reduzir a espera para iniciar. Fonte, DEX e biblioteca Android preparados e testados. **Esta entrega ainda não está em um APK assinado nem instalada no telefone.** O último retorno incorporado é R20 `ceb5efa`, instalado conforme seu recibo; seu APK SHA256 é `64eae3ab4dd253e25ee826dd23bf02c947e5cbd1db70e6b07f759d988d465904`. Preservar o ajuste visual posterior solicitado pelo mantenedor ao conciliar uma sucessora.

O delta altera quatro classes do cliente R16 e cinco linhas na ponte de extração. A instalação final deve substituir somente `classes28.dex` e `lib/arm64-v8a/libstation_archive.so`. O código de R16 permanece congelado. A ponte CD de `station-neogeocd-20261005` continua separada; este trabalho acelera o download/preparação, sem comprovar abertura CD ou fornecer BIOS.

## Causas encontradas

1. **Arquivo de CD grande:** Metal Slug tem 431.225.741 bytes; os 50 CHDs somam 15.170.394.032 bytes. R16 já retirou SHA de jogos, mas continuava lendo e gravando o arquivo inteiro novamente para instalar. A contagem RAW somava download + cópia: a rede terminava em 50% e o restante era preparação no armazenamento.
2. **Caminho público mais lento e variável:** Metal Slug completo chegou em 1,3851 s pela API local (311,329 MB/s) e 1,3855 s pelo Nginx local (311,232 MB/s). Pelo endereço público levou 133,7035 s (3,225 MB/s); janelas de dez segundos variaram de 0,913 a 4,426 MB/s. Neo Geo ZIP de 87.479.934 bytes fez 4,000 MB/s pelo mesmo endereço. Esses testes isolam o caminho externo; não distinguem operadora, túnel, destino ou Wi-Fi do telefone. São medições no servidor, **não no aparelho**.
3. **Espera redundante:** a renovação de sessão ou reabertura do catálogo offline podia exigir o catálogo completo antes da autorização do jogo selecionado. A autorização assinada já informa se a revisão desse item mudou.

## Implementado

- `StationDownloads` aproveita o recibo de bytes da transferência concluída. Não reabre o corpo do jogo para conferir hash, cabeçalho, tamanho ou referências CUE/M3U durante a instalação pela fila.
- `StationInstaller.installStaged` recebe esse recibo e consome somente `.station-v2/staging/transfer-*/artifact` da própria fila. Para RAW, usa renomeação atômica para uma geração nova. O mesmo arquivo passa a ser o jogo instalado; não há segunda gravação integral.
- A preparação publica os dois pequenos manifestos e o ponteiro privado. Cancelamento antes/depois da renomeação preserva o jogo anterior e os saves; arquivos externos não são adotados. O método legado `install` mantém compatibilidade para outros chamadores e testes históricos; a fila atual usa `installStaged`.
- RAW conta e reserva o corpo uma única vez: download chega a 100%, seguido da publicação curta. ZIP continua precisando de extração. Se um provedor não suportar renomeação atômica, a cópia transacional só ocorre se houver espaço; a porcentagem não volta para trás.
- `StationCoordinator.authorizeDownload` usa a sessão vigente e o item já autorizado no catálogo salvo. Busca o catálogo novamente somente se o grant indicar revisão diferente, com um refresh e uma nova autorização no máximo. Não consulta o perfil nesse caminho.
- A ponte nativa configura `zip:ignorecrc32=1`: não calcula nem valida o CRC do corpo dos ZIPs ao extrair. Usa as mesmas versões fixadas da reconstrução: libarchive 3.8.9 e xz 5.8.3. A implementação da opção está no [código oficial do libarchive](https://github.com/libarchive/libarchive/blob/v3.8.9/libarchive/archive_read_support_format_zip.c).
- O catálogo atual tem 849 RAW e 1.363 ZIP, cobrindo todos os 2.212 jogos publicados. RAW não passa pelo decodificador; ZIP lê os dados necessários para extrair. TLS, licença, descritor assinado, contagem de bytes enquanto recebe, caminhos, limites de extração e cancelamento continuam no fluxo de transferência/publicação. SHA de netplay identifica a sala e permanece fora deste ajuste de downloads.

## Evidência

- **821 verificações Java / 18 suítes**, incluindo recibo, mesma identidade de arquivo antes/depois do move, cancelamento, saves, permissões de sessão, cache, quatro capas simultâneas, fases e revisão alterada.
- **14 verificações JNI reais em Linux:** ponte anterior rejeita um ZIP com somente o CRC alterado; a nova extrai os mesmos bytes sem esse cálculo. ZIP UTF-8 válido funciona em ambas. Decodificador host Ubuntu 3.7.2; essa execução não é uma prova Android.
- Cliente compilado contra Android API36, bytecode Java8, D8 min26: `0f2748eaf8f4f1622f2537c94495d48843f2d8a69ae933485de2fa35772b9ddd`, 156.144 bytes.
- Biblioteca Android ARM64/API26: `3edbb4bd08af6ae4585b53c3243c56921f2bedac475298612bf88f042e62c54c`, 1.759.680 bytes. Todos os segmentos LOAD têm alinhamento 16KiB. Link com `-Wall -Wextra -Werror --no-undefined` aprovado.
- Seis downloads completos autenticados compararam API, Nginx e HTTPS de Neo Geo/Neo Geo CD. A licença sintética foi removida; PIDs e estados dos serviços mantidos. Hashes do corpo usados **somente pelo instrumento do teste**, sem acrescentá-los ao app.
- Produção permanece catálogo14, 2.212 visíveis/255 compatíveis; 50 CD. Índice `07ad4c3fda41a19c23745436c4c45c97a70b2c7688eff788612fe22743823a92`. API PID347227/DLL `0b3f5da385216d216fb55220789f55c40b8eb304b7b1a4759cc154b1aa3f3ab0`. Autorização local CD 8,23–16,37 ms; não há hash completo do jogo por autorização/GET, conversão durante HTTP ou limitador de MB/s. O link físico continua 100Mbps, sem erros nas amostras.

Recibos sanitizados em `evidence/`; sem grants, tokens, chaves, licença comercial ou URLs de jogos.

## Incorporar ao APK atual

Os módulos prontos estão no pacote privado Linux `station-download-sem-verificacoes-20261005.zip`, informado no retorno do servidor. O pacote inclui fontes, recibos e `modules/dex/classes.dex` / `modules/native/libstation_archive.so`. Pode-se usá-los ou recompilar com as receitas abaixo. Nenhum jogo ou BIOS entra no pacote.

1. Usar R20 ou sucessora conciliada por recibo. A receita `package_delta.py` desta entrega exige o SHA exato R20; se o ajuste de consoles apenas na sinopse já estiver instalado, registrar o novo SHA e conciliar a base antes de empacotar. Não instalar um APK anterior para aplicar o delta.
2. `build_and_test.py` monta uma árvore nova dos fontes R16 versionados e aplica os quatro deltas desta pasta. Informar `--output`, `--json-jar`, `--android-jar`, `--d8-jar`; Java/javac opcionais pelos argumentos. Não modifica fontes congelados. O teste de fase adapta somente a contagem esperada RAW na cópia temporária.
3. `build_archive.py --output <novo> --ndk <NDK>` recompila as dependências oficiais fixadas e a ponte. Windows: `--generator Ninja --make-program <ninja.exe> --cmake <cmake.exe>`. As saídas são privadas e novas.
4. `package_delta.py --base-apk <R20.apk> --dex <classes.dex> --java-report <result.json> --archive-so <libstation_archive.so> --archive-report <result.json> --output <candidato-unsigned.apk>` verifica fontes/recibos e todas as entradas preservadas. Se usar os módulos do pacote, os relatórios ficam em `modules/java-result.json` e `modules/archive-result.json`.
5. Alinhar com zipalign16KiB e assinar com o certificado original `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`. Conferir hash/assinatura/alinhamento e novamente todas as entradas de destino antes de atualizar por ADB com `-r`, preservando dados.
6. Medir no telefone um CHD grande: autorização, cabeçalhos, bytes/tempo de Baixando e Preparando separados. Confirmar CHD com rede a 100%, publicação curta, ZIP, cancelamento, saves, abertura e retorno. Registrar SHA do APK instalado. O Linux não tem o APK base, certificado privado ou aparelho conectado; não há recibo de instalação desta entrega.

O gargalo externo observado permanece separado da segunda cópia removida. Não afirmar que 311MB/s são a velocidade pela internet nem que esta fonte já acelerou a instalação R20 no telefone.
