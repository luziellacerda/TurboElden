# Integração do aplicativo com a produção Station — 03/10/2026

## Estado deste registro

**APK novo compilado, assinado e instalado com sucesso em 03/10/2026 às 16:17:03, horário de Fortaleza (UTC−03:00). O hash do `base.apk` instalado confere. O login abriu, mas uma tentativa de nova ativação retornou HTTP403; o fluxo completo de produção continua pendente. Não promover a estável.**

Destinatários: manutenção do aplicativo TurboStations TESTE e equipe do Servidor-pix. Este documento registra a aplicação das correções de fonte entregues pelo servidor no ambiente Android canônico do Windows. A implantação Linux já relatada pelo servidor é uma etapa distinta; este trabalho não republicou nem reiniciou a API.

Ramo desta integração: `integracao-station-producao-20261003`. Escopo exclusivo: pacote TESTE `org.turboramastation.frontend`. Classes Java permanecem em `org.emulationstation.frontend`. Outros produtos, aplicativos e referências estáveis não fazem parte desta integração.

## 1. Autoridades e versões exatas

| Componente | Referência |
|---|---|
| Handoff e fonte recebidos no repositório do app | `e1cf0657a3af2560e227883b444e618748ac4660` |
| Commit que contém as correções de runtime Android | `02c09dd36fcfa6c69ceb481f0934e84eef01e5ae` |
| Base da revisão de código | `db68b613cda008052afef8152400b9c595dfcffa` |
| Retorno operacional do servidor consultado | `b1511b9f75815aceb78dea801bb7ccc29f1036ab` |
| Release da API declarada implantada nesse retorno | `fd13c0d27eaab6a4dcf931a9cd64c3dcd7dd50c4` |
| DLL da API declarada em produção | SHA256 `f305ae3763cb77a53a27b2c168c8de290191b3a7e88e612850856b6f7be7e639` |
| Catálogo de produção declarado pelo servidor | Revisão `3`, `1816` jogos visíveis |
| `clientVersion` enviado pelo novo cliente | `1.0.8-station-review-20261003.1` |

Fontes fixados para revisão:

- [Correções do aplicativo no commit recebido](https://github.com/luziellacerda/TurboElden/tree/e1cf0657a3af2560e227883b444e618748ac4660/versions/station-reconstruction-20261002).
- [Commit de runtime Android](https://github.com/luziellacerda/TurboElden/commit/02c09dd36fcfa6c69ceb481f0934e84eef01e5ae).
- [Retorno único do servidor, fixado no commit consultado](https://github.com/luziellacerda/Servidor-pix/blob/b1511b9f75815aceb78dea801bb7ccc29f1036ab/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md).

O retorno do servidor relata HTTPS autenticado com catálogo revisão 3, cinco pares capa/download 200, assinatura/MIME/tamanho/SHA256 conferidos e rejeição de reuso dos grants. Relata também correção de permissões do usuário Linux da API, conciliação dos IDs anteriores e eco de `X-Correlation-ID` no proxy. Essas são provas da equipe do servidor, com origem identificada acima; não substituem as verificações deste novo APK no Android.

Distribuição esperada para a primeira conferência autenticada:

| Plataforma emitida pela API | Jogos |
|---|---:|
| `snes` | 644 |
| `snesbr` | 191 |
| `megadrive` | 887 |
| `megadrivebr` | 94 |
| Total visível | 1816 |

O retorno descreve 2071 entradas privadas no índice: 1816 visíveis e 255 ocultas de compatibilidade. `catalogVisible` é propriedade privada do servidor, não um campo novo a esperar no payload Android. Não somar as entradas ocultas à contagem da interface. As listas históricas maiores não demonstram que os demais arquivos foram publicados.

## 2. Artefatos e pastas da integração

Raiz canônica de fontes, builds e temporários:

`E:\ESTUDO APK\work\turbostations-reconstruction-20261002`

Foram sincronizados os 17 arquivos alterados/adicionados de runtime e testes, além de `AGENTS.md` e da evidência da revisão. A relação de caminhos e hashes foi registrada em `build\integration-source-manifest.json`. O arquivo de política nativa `station_cover_retry.hpp` e a classe `StationPublication.java` estão incluídos na integração; copiar somente os arquivos Java antigos seria insuficiente.

| Artefato | Identificação |
|---|---|
| APK novo | `E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build\apk\TurboStations-Station-CANDIDATO-20261003.apk` |
| SHA256 do APK novo | `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795` |
| Tamanho | `1902751638` bytes |
| Certificado de assinatura SHA256 | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| Pacote | `org.turboramastation.frontend` |
| Versão do pacote Android | `versionCode=11`, `versionName=1.0.8-turboeden-unico` |
| APK anterior preservado | `E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build\previous-f5b35419-20261003\TurboStations-Station-ANTERIOR-f5b35419.apk` |
| SHA256 anterior | `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a` |

O `clientVersion` de protocolo foi atualizado; o `versionName` Android permaneceu igual por preservação do manifesto. Não confundir esses dois campos ao identificar o cliente nos registros da API.

A montagem usa a base privada imutável:

`E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk`

SHA256 da base: `d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b`.

O relatório de empacotamento local está em `build\apk\apk-report.json`. A instalação retornou `Success` e o `base.apk` no aparelho tem SHA256 `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795`, idêntico ao candidato. A conferência de instalação/ativação desta rodada será consolidada em `versions/station-reconstruction-20261002/evidence/integration-production-20261003.json`. O estado de empacotamento não substitui esse registro posterior; o fluxo autenticado completo continua sem aprovação. O APK antigo arquivado não deve ser confundido com a base privada usada na montagem.

## 3. Correções efetivamente compiladas

### Capas e plataformas

- `StationPublication` separa itens com mapeamento confirmado dos itens de plataforma desconhecida. Os jogos suportados continuam disponíveis; a quantidade não publicada é registrada e avisada. Se todos forem desconhecidos, o cliente apresenta erro explícito.
- Os aliases `gamecube`, `psp`, `pspbr`, `ps2`, `ps2br` e `psvita` reutilizam os mesmos rótulos/pastas já existentes. Os quatro slugs do catálogo de 1816 estão mapeados.
- A política nativa de capas permite nova tentativa após 60 segundos de falha de carregamento e 5 segundos de falha imediata do comando JNI. Usa relógio monotônico e mantém o estado de repetição fora da estrutura binária `Item`.
- O ABI do catálogo e os endereços exigidos pelo renderer preservado não foram alterados. Não foi criado outro carrossel.

### Sessão, autorização e transferência

- `ready()` exige que a sessão corrente seja a mesma que autorizou o catálogo.
- A atualização explícita consulta novamente o perfil para receber o nome do comprador.
- Autorização, conferência de arquivo local e abertura do GET até os cabeçalhos compartilham o monitor do coordenador. Capas não renovam a sessão entre autorizar e consumir o grant.
- Depois de validados os cabeçalhos, a transferência do corpo e a instalação seguem fora desse monitor. O grant permanece de uso único; falha não provoca repetição automática do mesmo GET.
- A política de integridade continua verificando descritor assinado, tamanho, SHA256, formato, extração e `launchPath` antes de publicar o jogo como instalado.

### Diagnóstico e mensagens

- O cliente gera `X-Correlation-ID` para a requisição e registra categoria, status, correlação e tags SHA256 do item/capa. Não registra Bearer, código de ativação, licença, nome pessoal ou caminho privado.
- Timeout, interrupção e cancelamento têm mensagens distintas.
- A mensagem de item 404 solicita atualização do catálogo, sem concluir automaticamente de qual lado está a causa.
- A opção **Manter conectado** continua preservada: conserva a preferência de entrada automática e reutiliza licença/Keystore quando existem. Não armazena a senha/código de ativação nem um Bearer persistente.

## 4. Preservação do APK e limites da reconstrução

A receita recompilou os quatro DEX `classes5`, `classes6`, `classes8` e `classes28`, a biblioteca de serviço nativo e sua ligação com `libmain.so`. A biblioteca de extração e as licenças de terceiros permanecem incluídas. O catálogo legado `assets/turboretro/catalog.json` continua removido.

O empacotamento conferiu **10803 entradas preservadas por hash**, manifesto inalterado, certificado idêntico e ausência de novos tipos duplicados. Motores, design e recursos não foram substituídos por este lote. `libturbo_carousel.so` permanece na montagem preservada.

Na comparação dos conteúdos do candidato novo com o APK anterior `f5b35419...`, as únicas entradas de aplicação alteradas são **`classes28.dex`** e **`lib/arm64-v8a/libstation_frontend.so`**. Os demais DEX e bibliotecas recompostos pela receita mantiveram os bytes anteriores. Essa comparação entre candidatos é distinta da contagem de 10803 entradas preservadas contra a base privada de montagem; metadados de assinatura/empacotamento não são motores novos.

O frontend ainda contém renderer/launcher binários e rotinas nativas históricas residuais. Esta entrega não comprova retirada física integral do legado nem recuperação do C++ completo. As 32 entradas de serviço ligadas ao código novo mantêm os endereços originais; o restante exige a auditoria própria já documentada.

Os manifests de etapas isoladas podem registrar `apkIntegrated=false`: `build_frontend.py` e `link_native_services.py` não atualizam essa propriedade depois do empacotamento. A prova de montagem é o relatório final do APK; a instalação agora confirmada é registrada separadamente, com horário e hash do aparelho. Preservar as evidências históricas e identificar cada etapa pela sua revisão.

## 5. Verificações realizadas nesta integração

| Verificação | Resultado | Alcance |
|---|---|---|
| Testes Java no host Windows | 302 verificações aprovadas | Arquivos, protocolo, cache/sessão, coordenador, instalação e correções de revisão |
| Compilação das classes Android | API34, bytecode Java8 aprovada | Inclui os fontes novos; não é execução de jogo |
| Ponte JNI em Android | 28 verificações aprovadas | Fixture da ponte nativa, executada no aparelho |
| Política de repetição de capas | 7 verificações aprovadas | Binário compilado com NDK e executado no Android |
| Montagem/assinatura/alinhamento | Aprovados | Relatório do APK novo; 10803 entradas preservadas |
| Instalação do APK novo | `Success`, 03/10/2026 16:17:03 Fortaleza | SHA256 do `base.apk` igual ao candidato `fa3bc844...` |
| Abertura da tela de login | Confirmada | Mesmo aparelho Samsung Galaxy A56, após remoção anterior do TESTE pelo mantenedor |
| Nova ativação | Uma tentativa retornou HTTP403 às 16:19:13 | Correlação e tarefa do servidor na seção 6 |
| Catálogo, capas e jogo neste APK autenticado | Pendentes | Dependem de concluir a ativação; não cobertos pelos testes sintéticos |

O executável do teste de retry ainda imprime uma mensagem histórica contendo `host policy; Android bridge build pending`. Nesta rodada o binário foi compilado para Android pelo NDK e executado no aparelho; a frase fixa do stdout não identifica corretamente o ambiente dessa execução. As sete verificações são da política, enquanto as 28 verificações separadas cobrem a ponte JNI. Não tratar esse texto como prova de um build Android pendente nesta rodada, nem como comprovação de fluxo completo de produção.

Evidências e artefatos locais desta rodada:

- `build\integration-source-manifest.json`: commits e arquivos sincronizados.
- `build\test-results.json`: resultados dos 302 checks, compilação API34 e hashes dos fontes Java.
- `build\device-frontend\frontend-test.jar` e `libstation_frontend.so`: fixture de ponte, separada da biblioteca de produção.
- `build\device-frontend\station-cover-retry-test`: executável da política usado no Android.
- `build\frontend-manifest.json`: biblioteca de produção SHA256 `d4a3888eae21cdc3e57fd5e806b9eec643c59e4f612676bd3c8d8871fb7b8acc`.
- `build\native-link-manifest.json`: ligações e preservação dos endereços originais.
- `build\apk\apk-report.json`, `preserved-entry-hashes.json` e `apksigner-verification.txt`: conferência do APK.

Os relatórios antigos `closure-validation.json` e `closure-validation-eaebf48b.json` descrevem APKs anteriores. Eles não comprovam instalação ou autenticação de `fa3bc844...`. O registro consolidado desta rodada está no caminho `versions/station-reconstruction-20261002/evidence/integration-production-20261003.json`, com o novo hash, instalação e bloqueio de ativação descritos aqui.

## 6. Estado real do telefone e da ativação

O mantenedor confirmou o mesmo aparelho Samsung Galaxy A56 e confirmou ter desinstalado o TESTE antes desta instalação. A desinstalação removeu a licença privada local e a chave vinculada ao Android Keystore anterior. Não há identidade salva para retomada automática; a chave desta instalação não deve ser tratada como a chave anterior, embora o aparelho físico seja o mesmo.

O login do APK novo abriu. A pedido do mantenedor, o código foi localizado no handoff privado do commit `01c391bea72dc27de8597e0c6d908caa96b18021`, arquivo `docs/station-android/RETORNO-SENHA-STATION-48H-20261002.md`. A referência remota foi atualizada e continuava nesse mesmo commit. O código e a identificação da licença não são reproduzidos neste documento.

Foi feita **uma tentativa pela interface**, em 03/10/2026 às **16:19:13, Fortaleza (UTC−03:00)**, com o seguinte resultado:

| Campo | Valor observado |
|---|---|
| Operação | `ACTIVATION` |
| Rota a correlacionar no servidor | `POST /v1/station/activations/challenge` |
| HTTP | `403` |
| `X-Correlation-ID` | `1354b75f239f4fd7be8761df5efd7f8e` |
| Texto mostrado no login | “Acesso não autorizado. Confira seu código ou fale com o suporte.” |

Os registros disponíveis não mostram a causa específica do403. Não afirmar que o código foi consumido, que a licença está bloqueada ou que expirou sem consultar o registro correspondente no servidor. A perda da identidade local após desinstalação é confirmada; a razão exata de recusa pelo servidor ainda precisa ser determinada. Não apresentar o resultado como defeito do checkbox nem prometer recuperação da chave apagada.

### Tarefa exata para a equipe do Servidor-pix

1. Localizar a correlação `1354b75f239f4fd7be8761df5efd7f8e` no `POST /v1/station/activations/challenge`, por volta de 16:19:13 Fortaleza em03/10/2026 (19:19:13 UTC). Conferir o código interno da recusa e a regra aplicada.
2. Conferir, em ambiente privado, o registro da licença correspondente ao código do handoff: dispositivo/chave vinculados, eventual consumo do código, estado de liberação/bloqueio, prazo e limites. Não copiar dados pessoais ou segredos para o retorno no Git.
3. Se necessário, executar a **reemissão ou transferência oficial da mesma licença para a nova chave do mesmo celular**, conforme o procedimento autorizado de gestão e com trilha de auditoria. Não criar uma segunda licença para contornar o vínculo anterior.
4. Não alterar catálogo, índice ou rotas de jogos para corrigir esta recusa de ativação. Não remover verificação criptográfica, vínculo de dispositivo, estado, consumo ou expiração.
5. Se houver novo código, entregá-lo por canal privado autorizado, painel ou preenchimento na interface; **não commitar o segredo**. Devolver no Git somente causa comprovada, correlação, ação administrativa realizada e condição para nova tentativa.

Não publicar códigos, senhas, Bearer, chaves privadas, identificação de licença ou identificadores pessoais neste documento ou no Git. Não fabricar identificadores antigos, copiar chave privada ou contornar as regras do servidor.

Os arquivos externos de jogos e saves não foram apagados por esta integração. Como houve remoção anterior do TESTE pelo mantenedor, a disponibilidade efetiva dos arquivos e recibos deve ser conferida depois da instalação; não afirmar que dados privados removidos sobreviveram.

## 7. Conferência necessária para concluir no Android

1. **Concluído:** instalação `Success` e SHA256 instalado igual a `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795`. Preservar essa evidência.
2. **Bloqueio atual:** aguardar o diagnóstico/ação administrativa da seção 6, concluir nova ativação pelo fluxo Station autorizado e verificar o nome de perfil retornado. Conferir marcado/desmarcado de **Manter conectado** em abertura posterior sem expor o código.
3. Obter catálogo fresco, revisão 3, 1816 itens, com as quatro contagens desta seção 1. Não reutilizar a evidência antiga de996 como resultado novo.
4. Confirmar capa autenticada200 e renderização; sair/retornar e verificar reaproveitamento do cache. Exercitar uma falha recuperável e a repetição sem precisar reiniciar o app.
5. Baixar um jogo pequeno de uma plataforma publicada: autorização200 com descritor, GET do grant com o mesmo Bearer, MIME/tamanho/hash válidos e instalação concluída com recibo.
6. Conferir cancelamento/falha sem publicar arquivo parcial como instalado; nova tentativa deve obter nova autorização.
7. Abrir o jogo pelo botão Jogar, confirmar resposta do emulador e retornar às plataformas. Validar o `launchPath` real sob `.station-v2`, não somente a existência do arquivo.
8. Conferir um ZIP publicado e um raw; registrar o item de teste de forma sanitizada/correlacionável. Verificar Apagar apenas sobre arquivos de uma instalação de teste autorizada, preservando saves e arquivos desconhecidos.

Se algo falhar, correlacionar a requisição pelo `X-Correlation-ID`, `clientVersion` e tags SHA256 com os registros Station. O servidor deve comparar catálogo e índice da mesma revisão e responder com código/status/causa/evidência; o aplicativo deve informar a etapa exata. Um HTTP200 de prontidão, um log de compilação ou a existência do arquivo no Linux não substituem esse fluxo.

## 8. Pendências que não pertencem ao fechamento deste lote

- O cliente ainda limita catálogo/contadores JNI a4096 itens e mantém publicação integral. O pedido de **mais de15mil jogos** exige contrato versionado de paginação, carregamento por plataforma/janela, busca completa e cache adequados; está fora desta integração de1816.
- Não aumentar somente um número nem paginar HTTP para depois concatenar todo o acervo no modelo nativo. Nenhum teto de desempenho para15mil foi validado.
- Model2/Sufami permanecem sem mapeamento confirmado. Não criar rota/pasta/motor por inferência.
- Reconhecimento automático de todos os jogos antigos, limpeza de gerações substituídas e retirada física integral do legado nativo continuam tarefas distintas.

## 9. Retorno esperado das duas equipes

O próximo retorno do servidor deve primeiro responder à correlação de ativação da seção 6, com causa e ação administrativa comprovadas, sem segredos. Depois da ativação, o aplicativo deve registrar revisão/contagens de catálogo, exemplos correlacionados de capa e transferência, recibo/instalação, abertura do jogo e retorno. O hash instalado já foi confirmado. Qualquer etapa não executada deve ficar como pendente, com a causa concreta.

O servidor já tem um retorno operacional único fixado na seção 1. Acrescentar ali o diagnóstico da ativação e problemas operacionais constatados; não abrir outro ciclo de implantação baseado apenas em um handoff antigo. Este documento registra build, testes, instalação com hash conferido e login aberto. O fechamento autenticado está pendente do403 de nova ativação.
