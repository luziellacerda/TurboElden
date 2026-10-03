# PARA O SERVIDOR: catalogo Station incompleto - 03/10/2026

## Destinatario e escopo exatos

Equipe/IA do backend **Station Android** no repositorio **luziellacerda/Servidor-pix**. Produto e applicationId: `TURBORAMA_STATION_ANDROID`. Este documento pertence ao cliente Android TESTE `org.turboramastation.frontend`, no repositorio TurboElden, ramo `station-reconstrucao-20261002`. Nao executar tarefas da Suite Windows, Sambox Manager ou PIX por causa deste pedido. Nao e ordem de reiniciar servicos; qualquer implantacao segue a autorizacao do mantenedor do servidor.

## Evidencia confirmada no telefone

APK SHA256 `43670211fe6de01438c0352b44875c43336c052d431582032680fa2c9265517f`, instalado 03/10/2026 10:07:58 America/Fortaleza, assinatura preservada. Login com licenca salva funciona. A ponte Station publica e aplica 996 itens; a interface abriu. O erro de caminho simbolico privado Android foi corrigido no cliente.

O mantenedor informa **mais de 800 jogos de SNES**, mas o telefone lista 176. Nao inventamos uma quantidade exata esperada. Contamos a lista real entregue ao renderer, sem cortar pelo filtro visual:

| platform do contrato | Itens no telefone |
|---|---:|
| megadrive | 693 |
| snes | 176 |
| snesbr | 28 |
| gamegear | 58 |
| gb | 22 |
| sega32x | 7 |
| gbc | 7 |
| gba | 5 |
| Total | 996 |

Estas quantidades coincidem exatamente com `docs/station-android/RETORNO-ESTADO-SERVIDOR-APP-STATION-20261002.md` no commit `ac869429eba3fd3dcc41f3bd9a55a08cd4985659`. O novo cliente aceita apenas catalogo Station assinado, ou cache do mesmo envelope assinado nas condicoes do contrato. O status HTTP individual da ultima leitura nao foi capturado, portanto nao confundir estas evidencias com um novo dump HTTP de producao.

O retorno do indice exato `1ac9dd8e9cf9913e2ea753ea3d5cb02736faef9a` relata 997 correspondencias puladas por falta de capa e indice nao criado. A contagem do indice antigo nao e prova de que toda a biblioteca esteja publicada.

## Trabalho solicitado ao servidor

1. Conferir, no ambiente autorizado, a origem do indice realmente carregado pelo canal Station e a revisao publicada. Cruzar com o inventario completo de ROMs autorizado e com a lista de referencia ja existente. Retornar contagens por plataforma, especialmente SNES e SNES BR, e motivos de exclusao com quantidades. Sem aproximar nomes nem inventar pares.
2. Resolver as lacunas de arquivos/capas do indice e disponibilizar o catalogo completo no canal `/v1/station/catalog`, com revisao crescente. O cliente nao buscara `/drawers`, squareweb, Miami ou outro CDN antigo para completar jogos faltantes. Nao disponibilizar URLs ou caminhos privados no catalogo.
3. Respeitar a capacidade negociada: hoje o contrato/cliente limitam a 4096 itens e envelope de 12 MiB. Se o catalogo completo exceder isso, devolver antes um contrato explicito e versionado de paginacao ou novos limites, incluindo consistencia de revisao e assinatura. Nao publicar silenciosamente uma resposta que o cliente rejeitara; o cliente sera atualizado conforme o contrato confirmado.
4. Confirmar em producao capa autenticada 200 e descritor assinado completo por itemId para um jogo autorizado de teste; depois transferencia integral com hash/tamanho. O ultimo retorno `43bb54847e55750be451b614bcf827fb32ad7de4` registra somente homologacao HTTP isolada do descritor, nao implantacao de producao. Reinicio do servidor nao comprova publicacao desses recursos.
5. Preservar IDs existentes sempre que a identidade do item continuar a mesma; explicar eventuais alteracoes para nao invalidar caches/instalacoes sem migracao.

## Retorno pedido

Publicar **docs/station-android/RETORNO-CATALOGO-COMPLETO-STATION-20261003.md**, informando branch e commit completo, codigo implantado (ou explicitamente nao implantado), revisao do catalogo, totais por plataforma, exclusoes restantes, contrato de tamanho/paginacao e evidencias HTTP sem segredos. Nao incluir ativacao, token, chaves, deviceId, nomes/caminhos privados de arquivos ou credenciais. Nao responder com este pedido como se fosse a conclusao.

## Limites do cliente nesta entrega

O cliente abre os 996 itens atuais, mas isso nao resolve o indice incompleto. Nenhum servidor foi modificado nesta rodada. Download real e capa 200 continuam pendentes. As bibliotecas nativas preservadas ainda contem legado residual; inventario estatico de dominios nao prova chamadas ativas e a eliminacao integral continua pendente. Nao apresentar esta entrega como producao integral aprovada.
