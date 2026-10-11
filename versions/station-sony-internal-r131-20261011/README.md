# R131 — PS3 e PS4 internos com preparação automática

Fonte executável Sony corrigida: `8503c2e32d7487d3bb31397ba9533dc7e1bfe981`, em `integration/sony-internal`. Base exata R130: `d227b0af17600bf99ec097857bf182f6e7989f8ddc3b68b63e17c81f69eb30ad`. Esta pasta registra a entrega compilada e assinada; não escolhe instalador pela data e não substitui os recibos de instalação física.

## Resultado compilado

APK R131 corrigido: `0273ab9ae1b7ef5a061fdcc76c49558db4180bedd10a8100e6d5f764ac2ab175`, **2.711.825.423 bytes**. O instalador atual está no backup local, fora do Git. Certificado original `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`, assinaturas v2/v3 e alinhamento ZIP de 16 KiB conferidos pela receita final.

O montador preservou **13.555 entradas da R130 byte por byte**, inclusive todos os 39 DEX existentes, recursos, carrossel, vídeos, capas, LEDs, cache/preload, economia, controles e cores dos emuladores anteriores. O novo host tem 106 tipos em `classes40.dex`. São exatamente cinco substituições e 300 adições: Manifest, cadastro de engines e três marcadores de identidade; DEX40 e 299 assets Sony privados.

## O que mudou

- A factory existente delega a seleção Sony para um dispatcher interno. A ponte externa herdada permanece no DEX original, mas não é a Activity instanciada para abrir PS3/PS4 nesta composição.
- PS3 usa o core aPS3e 2.43 exato, JNI real e owner próprio em `:station_ps3`. O firmware Sony 4.93 está em `assets/sony/ps3/upstream/PS3UPDAT.PUP`, incluído no APK local por autorização específica. O worker verifica tamanho, SHA e formato e chama o importador nativo. A confirmação de preparo depende dos arquivos reais e de importação concluída.
- PS4 usa o runtime Bachata S4 0.2.4 exato em `:station_ps4`, com Surface Android, áudio, controle e importação PKG nativos. As 67 declarações JNI SDL3 foram conferidas com o APK oficial. O DEX JNI e as bibliotecas ficam isolados do SDL/libc++ da Station. O material comum de leitura de PKG foi autorizado exclusivamente para o APK local.
- Configurações e lançamento Sony usam os owners do próprio APK. A extração e o preparo começam no worker do sistema solicitado, sem novo serviço de carregamento no carrossel, downloader de firmware ou wizard externo obrigatório.
- PS3 abre ISO; PS4 importa PKG uma vez para seu armazenamento privado. Conteúdo criptografado pode exigir a chave válida do próprio jogo conforme o motor. As amostras DEMO não são jogos.

Os owners Android são fontes próprias mínimas sobre os artefatos nativos oficiais fixados. Esta entrega não afirma reconstrução integral das interfaces dos aplicativos upstream.

## Correção após a primeira conferência no Android

O primeiro APK R131, SHA `2149f31e6e268b4fde644dcd5cc604874afdff002c53f9d5f41655682a99d427`, teve preparação automática do firmware PS3 observada pela interface real no Motorola Edge 30/Android 14. O PS4 falhou antes do JNI com `NoSuchMethodError`: o host havia resolvido uma API de ClassLoader Java SE indisponível no Android. Esse resultado pertence somente àquela primeira candidata e está resumido, sem logs ou dados pessoais, em `evidence/first-bootstrap-failure.json`.

A fonte corrigida usa sincronização da própria instância para o classloader e ambiente de compilação boot Android. Os stubs do compilador são apenas de compilação e não entram no DEX. Hosts, JNI, assets derivados, identidades, montagem e assinatura foram refeitos a partir dos inputs corrigidos. A candidata corrigida foi instalada e conferida separadamente, conforme os recibos físicos abaixo.

## Identidades online preservadas por contrato

PS3/PS4 continuam exclusivamente offline. Nenhuma sala, engine ou perfil online Sony foi criado. As quatro identidades já existentes foram renovadas porque Manifest/DEX/assets integram o bundle compartilhado; cores, opções, perfis, transporte e capacidades anteriores permanecem iguais.

| Sistema | Engine R131 | Capacidade do perfil existente |
| --- | --- | --- |
| PSX | `pcsx-rearmed-ff81ed17-player-v3-7c182b392814` | 2, `standard-2p-v1` |
| N64 | `mupen64plus-ae-33bf7021-n64-v3-cf3c21e161fa` | 4, `direct-four-ports-v1` |
| GameCube | `dolphin-5102a033-gamecube-v3-cdfd3b17ee2b` | 4, `dolphin-gamecube-four-ports-v1` |
| Wii | `dolphin-5102a033-wii-v3-cdfd3b17ee2b` | 4, `dolphin-wii-remotes-four-v1` |

Capacidade do engine não aprova automaticamente qualquer jogo/modo. Aprovação do servidor e gameplay continuam etapas distintas. SNES/Mega Drive e os demais contratos anteriores não foram alterados por esta composição. Nenhum servidor foi implantado ou reiniciado.

## Evidências e reprodução

`evidence/receipt-index.json` lista o SHA e o tamanho de cada recibo público. `package-final.json` conserva os mapas completos de SHA das 13.555 entradas preservadas, cinco substituições e 300 adições; `unsigned-package.json` contém a atribuição original da montagem. `runtime-final.json` conserva fontes, transformações, ferramentas e payloads vinculados aos marcadores. `source-freeze-public.json` conserva os 305 inputs fixados.

Recibos públicos trocam caminhos absolutos privados por referências lógicas e guardam o SHA do recibo privado original. Portanto, o SHA original não é o SHA da cópia pública sanitizada. Hashes, nomes lógicos e metadados são publicados; APKs, binários, firmware, material PKG, jogos, mídias, seriais, sessões e logs pessoais permanecem fora do Git.

A reprodução usa as receitas em `integration/sony-internal/recipe` e os inputs privados exatos identificados pelos recibos. Usa somente o backup completo F: e a árvore de trabalho G: atuais. R130 permanece donor obrigatório; não apagar as bases necessárias nem gerar novos snapshots.

### Variantes de fim de linha no backup

A reconciliação identificou oito variantes LF/CRLF entre os blobs crus do Git e os arquivos congelados. O conteúdo é idêntico após CRLF→LF; para reproduzir os bytes exatos, a autoridade continua sendo o SHA congelado. O backup preserva o Git cru e um mapa separado das variantes congeladas.

O helper privado `work/finish_r131_backup.py` aceita `--restore-source-variants "G:\StationNormalOwnersR127\sony-internal\correction\reproduction-sources"`. Exige essa árvore isolada preparada com os blobs Git, valida todos os inputs e substitui exclusivamente as oito variantes conhecidas quando o SHA do destino é o Git esperado. Recusa outras diferenças e confere os SHA congelados finais; não altera o checkout produtivo C: nem o backup F:.

Não é necessária nova compilação produtiva por essa diferença de fim de linha: o APK atual já teve hash e instalação Android conferidos. A recompilação e a reassinatura integrais do backup **não foram executadas**.

## Estado comprovado desta entrega

Compilação corrigida, guarda JNI PS3 de dez classes/estruturas, montagem fechada, assinatura original e conferência de todas as entradas passaram. A candidata corrigida foi instalada diretamente no **Motorola Edge 30/Android 14 em 11/10/2026 às 18:33:09 UTC**. O SHA integral do APK no telefone conferiu `0273ab9a…`; UID e dados originais foram preservados, sem cópia extra de APK, desinstalação ou limpeza. O frontend oficial abriu. Evidência: `evidence/installation.json`.

Pelos botões visíveis de configuração do frontend, **Ps3Activity e Ps4Activity abriram nos processos privados da própria Station**. O PS3 mostrou “Sistema preparado · Vulkan · configuração original do motor”, cuja apresentação ocorre depois de `Ps3Bootstrap.prepare` e `Ps3Firmware.ensure`. A importação real do firmware foi observada na primeira R131; a candidata corrigida confirmou o reuso pelo pós-requisito protegido da UI.

O PS4 mostrou “Motor e arquivos internos preparados”. Essa tela ocorre depois da carga do owner filho, retorno de JNI `loadNative`, inicialização do material PKG e `Ps4Runtime.prepare`. A falha ClassLoader anterior não reapareceu; a filtragem do novo processo não apresentou erros do owner/AndroidRuntime. Os botões Sair/Voltar de ambos os owners retornaram ao frontend. Evidência: `evidence/physical-bootstrap.json`.

Essas observações são provas da interface real e dos seus pós-requisitos protegidos. **Os arquivos privados do sandbox não foram lidos independentemente**, e não houve bypass quando essa leitura foi negada. Nenhum ISO PS3 ou PKG PS4 real foi lançado/importado para jogar; gameplay, compatibilidade dos títulos, controles físicos, estabilidade prolongada, consumo térmico e ativação do servidor não foram validados. A assinatura e os assets, isoladamente, continuam sem provar essas etapas.

Os recibos de montagem/compilação conservam o estado do próprio estágio, anterior à instalação. Os recibos físicos e `STATUS.json` acrescentam somente os resultados observados, vinculados ao APK corrigido exato.
