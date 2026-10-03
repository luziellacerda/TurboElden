# SERVIDOR-PIX — ampliação Station para 40.000 jogos

## Destinatário, base e autorização operacional

**Destinatário exclusivo:** equipe responsável pela API/índice Station do Servidor-pix. O mantenedor pediu salvar a estável SNES/Mega e depois ampliar a capacidade para40mil jogos. A estável foi publicada primeiro em TurboElden, tag `estavel-station-snes-megadrive-20261003`, commit **`97938400d3fa82d5d1564445c36fc70328add1c4`**. Ela permanece imutável e instalada no telefone.

Este documento pertence à branch Android **`capacidade-station-40000-20261003`**. Entrega código Android, APK candidato privado, testes e um **patch revisável de backend**. **Não registra implantação no Linux.** Não alterar outros serviços, reemitir licenças, remover jogos ou aplicar migrations para esta ampliação.

Leia antes o [handoff técnico completo da estável](https://github.com/luziellacerda/TurboElden/blob/97938400d3fa82d5d1564445c36fc70328add1c4/docs/server/HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md). Ele descreve o fluxo que já funciona, todas as rotas, fontes, métodos compilados, vínculos nativos, armazenamento, build e provas SNES/Mega. As instruções de40mil nele eram planejamento; este documento identifica a implementação posterior efetivamente produzida.

## 1. O que foi implementado no Android

Fontes no mesmo repositório: `versions/station-reconstruction-20261002/`.

| Arquivo | Mudança posterior à estável |
|---|---|
| `StationCatalog.java` | Máximo40000; `fromVerifiedText` lê um registro por vez após verificação da assinatura, preserva modelo tipado/indexado e evita manter a árvore JSON completa dos40mil objetos. Valida IDs, revisão, nomes, campos e duplicatas; rejeita40001. |
| `StationApi.java` | Caminho específico para catálogo assinado usando o parser incremental; identidade/domínio/licença/dispositivo/sessão verificados; cópia defensiva do cache feita depois do parse. ASCII de Base64/JSON escapado evita buffer UTF-16 adicional; UTF-8 não ASCII mantém decoder estrito. |
| `StationProtocol.java` | Envelope de catálogo até64MiB, antes12MiB. JSON de comandos continua8192 bytes; capa continua5MiB. |
| `StationConfig.java` | `clientVersion=1.0.8-station-capacity40000-20261003.1`. Host, pin, autoridade, produto e aplicação preservados. |
| `StationInstaller.java` | `recordedIds()` enumera uma vez o diretório privado de recibos; não faz40mil consultas a arquivos inexistentes. `find()` continua validando o recibo e o conteúdo de candidatos existentes. |
| `StationDownloads.java` | Expõe a enumeração dos recibos para publicação. Regras de sessão/grant/hash/instalação permanecem. |
| `StationFrontend.java` | Aloca lista na capacidade conhecida, consulta somente recibos encontrados, publica progresso a cada64 itens e ao concluir. |
| `station_capacity.hpp` | Limite nativo explícito40000. |
| `station_frontend.cpp` | JNI e contador de preparação aceitam40000; índice por ID no estado privado; busca de trabalho ativo percorre os trabalhos, sem varrer40mil itens a cada consulta. ABI pública preservada. |

**Não há rota nova, parâmetro novo, cursor ou API de paginação inventada.** O candidato aceita o mesmo envelope completo de `GET /v1/station/catalog`, com os mesmos cinco campos por item e mesma assinatura. Uma primeira ampliação compatível pôde ser implementada e testada nesse contrato. Paginação continua uma evolução conjunta possível; não foi implementada nem deve ser presumida.

Limites simultâneos: até40000 itens **e** envelope até64MiB. Não garantir que qualquer combinação arbitrária de metadados/novos campos caiba só porque a quantidade é40000. Testamos nomes de120 caracteres Unicode escapados, quatro plataformas conhecidas e IDs válidos, com envelope de43760842 bytes. Capas continuam sob demanda e limitadas; não baixar40mil capas ao iniciar. Não existem40mil ROMs adicionadas por essa mudança de capacidade.

## 2. Alteração preparada para o servidor — arquivo exato

Base lida sem trocar checkout: Servidor-pix commit **`fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61`**.

Arquivo: `src/TurboRamaSuiteOnlineServer/StationLibrary.cs`.

Patch entregue em [servidor-capacidade-40000.patch](../../versions/station-capacity-40000-20261003/servidor-capacidade-40000.patch). Hash do arquivo base e resultado proposto em [server-patch-manifest.json](../../versions/station-capacity-40000-20261003/server-patch-manifest.json). `prepare_server_patch.py` reproduz o patch a partir do commit exato, sem modificar o clone do servidor.

O patch faz apenas:

1. `MaximumItems`:4096 →65536 **entradas privadas totais**, incluindo compatibilidade oculta.
2. `MaximumCatalogItems=40000`: contador separado dos registros com `catalogVisible=true`, recusando o40001º público.
3. `MaximumIndexBytes=128MiB`: conferir tamanho do índice antes de `File.ReadAllText` para limitar a alocação.

65536 não significa65536 jogos públicos: reserva espaço para IDs de compatibilidade. O estado atual2071/1816 continua válido sem alteração de registros. Todas as verificações existentes de IDs, paths, coverId/revisão, formato, tamanho, hash, ZIP e mtime permanecem. A API não deve limitar a lista por `Take(40000)` silenciosamente; o índice inválido deve ser recusado na preparação.

**Não aplicar por número de linha nem por similaridade de nome.** Conferir o hash da base e usar `git apply --check` em uma branch de implementação do servidor; se o arquivo já mudou, reconciliar a diferença e repetir os testes. Não trocar o checkout de trabalho atual nem forçar o patch. A equipe Android não aplicou esse patch no clone nem na produção.

## 3. Testes e seus limites

| Prova | Resultado |
|---|---|
| Suíte Java/API34 |353 verificações locais:327 anteriores +26 específicas de capacidade; compila Java8 contra API34. |
| Catálogo assinado sintético |40000 itens,10000 por plataforma, nomes Unicode longos, assinatura/identidade/cache e último item preservados; limite antigo12MiB ultrapassado. Parser, duplicatas, dados inválidos e40001 rejeitados. |
| Ponte JNI no Android |35 verificações passaram, incluindo catálogo40000, índice e último item, contador de preparação, rejeição40001 e preservação do catálogo anterior. |
| Leitor Android isolado |Fixture final43760842 bytes:40000 registros em1997ms, heap máximo268435456 bytes, VmHWM437748KiB. Processo isolado, sem sessão real ou pedidos à produção; não é medição da UI completa. Resultado anterior24,56MB separado no JSON. Fixtures temporárias removidas. |
| Índice C# isolado |9 verificações;40000 públicos +255 ocultos aceitos,40255 descritores/hash conferidos em arquivos sintéticos;65536 privados aceitos, excesso público/privado e índice maior128MiB recusados. |
| Build APK |Novo candidato com mesma identidade/manifesto/motores; hash e caminho no manifesto desta revisão. |
| Produção40mil / UI completa |Ainda não comprovadas. O servidor atual publica1816; o telefone permanece na estável. |

Teste C#: `ServerCapacityTest.cs` compila o **StationLibrary.cs inteiro com o patch**, usando .NET9 e um adaptador que copia somente `StationProtocol.IsSafeLibraryId` do commit base. Não compila toda a API, banco, proxy ou autenticação. Usa arquivos sintéticos de4 bytes, não ROMs. O tempo dessa prova não estima o tempo de hashear40mil jogos grandes no Linux.

A API atual hasheia os artefatos ao carregar o índice. Antes de ampliar o acervo, medir sob o UID/armazenamento reais o tempo de startup, memória e janela de publicação. Não remover a conferência de integridade para encurtar a implantação sem um contrato de confiança substituto formalmente implementado.

## 4. Compatibilidade da publicação

| Combinação | Situação |
|---|---|
| APK estável9793840 + índice1816 |Fluxo SNES/Mega comprovado. |
| APK candidato40mil + API atual1816 |Contrato preservado; testes locais de regressão passaram. Instalação/fluxo real do candidato ainda dependem do aceite indicado no manifesto. |
| APK candidato40mil + backend com patch + catálogo≤40000/64MiB |Capacidade preparada; requer testes integrados e publicação do operador. |
| APK antigo4096 + catálogo acima4096 |**Incompatível:** o cliente antigo recusa. Não publicar volume maior antes de distribuir/aceitar o cliente compatível. |

Não existe negociação nova de capacidade no protocolo desta entrega. A implantação deve coordenar a versão de cliente dos consumidores antes de ultrapassar4096. Se houver clientes antigos que precisem continuar funcionando, a equipe servidor deve propor e testar política de compatibilidade explícita; não devolver truncamento silencioso nem um esquema desconhecido ao APK.

## 5. Tarefas exatas para a equipe Servidor-pix

1. Conferir commit/base/hash, revisar o patch e executar toda a suíte real da API no ambiente do servidor. Repetir os9 testes isolados como apoio, não como substituto.
2. Preparar catálogo sintético isolado40mil com as mesmas rotas, assinatura, vínculos de sessão, descriptors e capas. Conferir tamanho do envelope produzido pelo serializador real≤64MiB. Não publicar conteúdo sintético para clientes.
3. Conferir acesso como UID do serviço, limite de memória, tempo de carga/hash e configuração **efetiva** `Station:LibraryIndexFile`. Esse índice é carregado na inicialização; edição em disco não é prova de atualização viva.
4. Validar todas as nove rotas, catálogo íntegro sem corte, capa200, autorizar+GET com mesmo Bearer, SHA256/tamanho/descritor, grant de um uso e erros de replay/expiração. Preservar rate limit e correlação.
5. Definir rollout dos clientes, backup/retorno e publicação somente da Station. Não aplicar migrations028/029 de novo; não mudar chave, licença, SKU, pepper ou outros serviços por causa do volume.
6. Ampliar o acervo real por lotes, com manifesto IDs/revisões/nomes/ROMs/capas. Preservar IDs antigos e ocultos; incrementar revisão de itens quando bytes/capas mudarem.40mil é capacidade, não criação automática de jogos.
7. Publicar retorno técnico nesta mesma revisão: commit/DLL/hash, patch aplicado ou divergência resolvida, índice/revisão/contagens pública e privada, bytes do envelope, medições reais, provas HTTP correlacionadas e plano aplicado. Distinguir teste isolado, homologação e produção.

O retorno deve permitir Android conferir um catálogo real grande no candidato, navegar/pesquisar nas plataformas, carregar capas sob demanda, baixar/instalar/jogar/voltar e medir memória/tempo com o frontend completo. Somente depois marcar outra tag estável. **Não mover a tag estável9793840.**

## 6. Entrega Android e integridade

Pasta [station-capacity-40000-20261003](../../versions/station-capacity-40000-20261003/) reúne manifesto, testes, fonte do teste C#, patch e hashes. Fonte canônico e build continuam em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`, agora na revisão40mil; para recuperar o fonte estável usar a tag9793840. O APK estável congelado permanece em `E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive`.

Não executar o exportador da estável sobre o candidato novo: ele verifica o hash antigo e deve recusar. Não sobrescrever inventários/hashes da tag congelada. Para esta revisão, usar apenas o manifesto e inventários próprios de capacidade. As diferenças do APK em relação à estável são registradas por entrada, não inferidas do nome do arquivo.
