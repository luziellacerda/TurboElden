# Retorno Android ao fechamento Station - 03/10/2026

Destinatario: equipe do **Servidor-pix**, exclusivamente produto `TURBORAMA_STATION_ANDROID` / aplicativo TESTE `org.turboramastation.frontend`. Nao e instrucao para alterar Turborama, Sambox, PIX ou outros produtos. Responde ao retorno do servidor `64912e1f2294b99967fc638d842f505cff7f629c`, ramo `feat/station-artifact-descriptor-20261002`.

## Evidencia real que bloqueia a entrega

No aparelho, em 03/10/2026 entre 12:16 e 12:18 (America/Fortaleza), o cliente instalado `eaebf48b9bf1902c151ea54b5d2cb0c0fe89c111ff1e91a2c68b671eed504680` retomou a licenca salva e recebeu:

- Sessao: 200; perfil `/v1/station/me`: 200.
- Catalogo `/v1/station/catalog`: 200, **996 itens recebidos da rede**, nao cache. Os mesmos 996 foram aplicados no renderer.
- Capas `/v1/station/covers/{coverId}`: 404.
- Autorizacao `/v1/station/downloads/authorize`: 404 nas tentativas do mantenedor. Nao houve grant aceito nem GET de artefato; nao chamar isto falha de extracao ou do emulador.

Os registros `closure-station-log-eaebf48b.txt` sao limitados a eventos numericos/categorias, sem itemId, coverId, Bearer, grant, ativacao ou dados pessoais. O status 404 isolado nao distingue proxy/rota/item/arquivo; o APK final abaixo classifica apenas codigos explicitamente conhecidos sem copiar corpos de resposta para logs. Conferir o indice efetivo e a versao efetiva, nao deduzir a causa pelo status.

## Confirmacao no APK final

A revisao final f5b35419 tambem recebeu sessao/perfil/catalogo 200 e 996 itens frescos da rede. A tentativa do mantenedor registrou **404 `STATION_COVER_NOT_FOUND`** e **404 `STATION_ITEM_NOT_FOUND`**. O item solicitado pertence ao catalogo em memoria (pre-condicao de StationDownloads/StationCoordinator). Conferir a consistencia do indice/catalogo e a disponibilidade do arquivo pela DLL efetiva. Ainda nao houve grant aceito nem transferencia; a causa interna exata exige acesso ao servidor. Evidencia: `evidence/closure-station-log.txt` e `evidence/closure-validation.json`.

Checkbox compilado e instalado; entrada com acesso salvo comprovada. Alternar a preferencia desmarcada/marcada individualmente na UI ainda nao foi exercitado. Tela ligada durante a carga restaurada ao valor original 0.

## Cliente entregue para a proxima etapa

Candidato final `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, 1.902.718.870 bytes, em:
`E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build\apk\TurboStations-Station-CANDIDATO-20261003.apk`.
Instalacao por atualizacao concluida em **03/10/2026 12:27:01**, hash do base.apk identico, licenca salva retomada e plataformas/catalogo abertos. Conferir o resultado de instalacao em `versions/station-reconstruction-20261002/evidence/closure-validation.json`. Nao confundir com a evidencia HTTP da revisao intermediaria acima.

- Login inclui checkbox **Manter conectado**. Preferencia privada controla entrada automatica; autorizacao continua remota. Licenca e Keystore preservados, sem guardar codigo de ativacao. Conferencia visual da preferencia deve constar na evidencia de aparelho.
- Integrado o alias `megadrivebr` do commit Android `59883435e9f65a3960d7a616a1cf647694407b48`, mais 15 aliases explicitos do inventario historico. Nenhuma inferencia de pasta. `model2` e `sufami` continuam sem rota verificada; o cliente informa plataforma sem integracao. Nao publica-las sem acordo de compatibilidade.
- Teste com catalogo sintetico **assinado** de 1.816 itens: `snes=644`, `snesbr=191`, `megadrive=887`, `megadrivebr=94`; sem corte. Isto testa o cliente, NAO prova publicacao real e NAO importa IDs provisórios do TSV para o app.
- 255 verificacoes locais aprovadas; 28 verificacoes da ponte nativa no Android. Assinatura, manifesto, identidade e 10.803 entradas preservados. Apenas TESTE atualizado; nenhuma referencia estavel promovida.
- Diagnostico distingue rede/cache, status das rotas, capa em cache, erro de recibo, reutilizacao local e resultado da instalacao. Nunca imprime conteudo das respostas ou IDs.
- Recibo invalido de um jogo deixa esse item sem marca de instalado, preserva arquivos e nao derruba todo o catalogo. Uma troca de label pelo alias da MESMA pasta nao invalida uma instalacao.
- Ao solicitar um jogo, procura arquivo preexistente somente na pasta verificada da plataforma (profundidade 6, ate 4096 entradas, ate 8 candidatos por tamanho, orcamento de hashing limitado). Reaproveita somente se tamanho e SHA256 coincidirem com o descritor ASSINADO. Revalida no instalador, cria instalacao transacional e preserva o original. Nao varre todas as ROMs no inicio. Busca longa renova a autorizacao antes do download. Arquivo ja extraido diferente do artefato nao e associado por nome.
- Descritor ausente continua recusado; mensagem informa dependencia do servidor. Arquivo ausente no servidor nao vira jogo instalado. Sem fallback para Miami/Sambox/catalogo local.

## Tarefas concretas restantes no SERVIDOR

1. Com acesso autorizado, obter o indice EFETIVO da 5192 sem expor `.env`/segredos, usando o exportador do proprio retorno. Conciliar com o candidato de 1.816 itens, preservando IDs/revisoes ja publicados e as outras plataformas. Nao substituir por uma lista exclusiva SNES/Mega Drive. O TSV com `catalogMatch=not_supplied` nao e catalogo de producao.
2. Validar existencia, leitura e hashes de cada capa/jogo pela conta REAL `turborama-suite`, no destino definitivo. Corrigir 404 de capa/autorizar observados neste retorno; comparar itemId da resposta autenticada com o indice efetivo em ambiente privado.
3. Verificar ledger 028/029, backup restauravel, DLL candidata `faa015c4...`/pacote `4f102ee5...`, configuracao efetiva, chave de assinatura e rollback. Publicar somente o canal Station com indice conciliado e descritores. Nao rodar codigo novo com indice antigo sem `artifact`.
4. Repetir por HTTPS publico: sessao, nome, catalogo fresco, capa 200 e autorizacao com `itemRevision`/`artifact` assinados, transferencia completa do mesmo grant/sessao, hashes. Registrar contagens e codigos sanitizados, nao credenciais.
5. Validar o fluxo comercial/admin Station (emissao, bloqueio, desbloqueio, revogacao e transferencia) e TTL real com conta de teste. Nao editar servicos compartilhados sem alvo e impacto verificados.
6. Atualizar o MESMO `docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md`: commit/DLL efetivos, revisao/contagens conciliadas, provas HTTPS, arquivos disponiveis/ausentes e estado real de implantacao. Nao marcar homologacao isolada como producao.

## Restante no ANDROID depois da publicacao

Conferir capa 200 persistida sem rebaixar no retorno, download/instalacao real, cancelamento, abrir jogo/voltar, apagar somente arquivos de recibo e reconhecer arquivos antigos comprovaveis. O teste real esta bloqueado antes da transferencia pela resposta atual do servidor. Continua pendente retirada fisica integral do legado nativo residual; chamadas comerciais novas estao ligadas ao cliente Station, mas o binario do renderer preservado ainda contem rotinas/strings antigas. Nao declarar reescrita nativa integral, e nao afirmar ausencia de trafego legado somente por inventario estatico.

Nenhum deploy, migration, restart ou alteracao de indice de producao foi executado nesta etapa Android. O mantenedor disse que disponibilizaria conexao autorizada; ate a ultima consulta nao havia acesso Linux disponivel no cliente de ferramentas. Fonte canonico continua em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`; publicacao em `TurboElden`, ramo `station-reconstrucao-20261002`.
