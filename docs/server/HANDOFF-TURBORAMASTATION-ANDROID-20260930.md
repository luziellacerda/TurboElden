# TurboramaStation Android — handoff de integração comercial

Data: 30/09/2026. Destinatário: responsável pelo servidor e site Turborama. Estado: **análise dos fontes e proposta de implementação; nenhuma alteração de produção, banco, licença ou cliente comercial foi aplicada**.

## 1. Objetivo

Compra confirmada no site → servidor gera acesso individual → cliente ativa a TurboramaStation → painel acompanha licença, dispositivo e sessão → administrador pode liberar, bloquear, revogar a sessão ou autorizar troca de aparelho.

Reutilizar banco PostgreSQL, cadastro comercial, pagamentos, painel, auditoria e serviços existentes. Preservar integralmente Suite Windows, EmulationStation Windows, PIX e conteúdo já publicado. O aplicativo Android deve continuar com um APK, os mesmos emuladores, carrossel, downloads, saves e retorno das partidas sem pedir novamente a senha.

O acesso solicitado como “senha” deve usar o código individual de ativação gerado pelo servidor, de uso único, seguido por autenticação do aparelho. Não inserir uma senha universal no APK. Caso o produto precise também de login humano recorrente, reutilizar a conta autenticada do site: a posse de uma chave de aparelho não comprova a identidade civil do comprador.

## 2. Fontes e versões efetivamente examinadas

| Componente | Referência examinada | Papel |
|---|---|---|
| TRUBORAMA-SUITE | `main`, `86e7ae1ec54b304b080b3ecc71b37c7f0e3dd5ba` | Cliente WPF Windows, protocolo, documentação e catálogo |
| Servidor-pix | `codex/emulationstation-suite-extraction-linux-20260908`, `17af26cc8e1aa88edfaef0a4e25ab598e4f682e6` | API Suite, administração, comércio, sessões ES e migrations até 026 |
| Servidor-pix / main | `26486ef9ebf24e9e3212318504133fac047aafa5` | Linha legada: não contém toda a integração Suite examinada |
| Servidor-pix / vendas | ponta consultada `4ea972657355740485b3831970ef1fd21b186661` | Outra linha ativa; não foi tomada como árvore integral de produção |
| TurboElden | estável `05dd34b0ec067e8951670422fc0cbf2fa851a3d0`, tag `estavel-2026-09-30-plataformas-emuladores` | Snapshot publicado dos fontes Android e mapa de recuperação |

Fontes primárias: [cliente Suite](https://github.com/luziellacerda/TRUBORAMA-SUITE/tree/86e7ae1ec54b304b080b3ecc71b37c7f0e3dd5ba), [backend analisado](https://github.com/luziellacerda/Servidor-pix/tree/17af26cc8e1aa88edfaef0a4e25ab598e4f682e6), [Android estável](https://github.com/luziellacerda/TurboElden/tree/estavel-2026-09-30-plataformas-emuladores).

**Não presumir que qualquer uma dessas pontas está implantada hoje.** Os relatos de implantação encontrados nos documentos são históricos. Antes do trabalho no Linux, registrar commits/artefatos reais de API, admin, PIX, gateway, migrations e configurações. Integrar o delta na linha efetivamente instalada; não substituir produção por `main` nem pelo clone deste handoff.

### Pastas locais exatas

- Fontes Android: `E:\ESTUDO APK\work\native-carousel\implementation`.
- APK instalado após a atualização de vídeos: `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk`.
- SHA-256 instalado: `544fdecbc512a128827b392dcc96461573db9a16c09dc343bc3d958749980b81`.
- Receita e comprovante: `platform-videos-br-20260930\update_videos.py`, `build-result.json`, `installed.json`, sob a pasta de fontes.
- APK estável de recuperação: `E:\ESTUDO APK\estaveis\2026-09-30-plataformas-emuladores\TurboramaStation-ESTAVEL-plataformas-emuladores.apk`, SHA-256 `78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2`.
- Clone do cliente: `E:\ESTUDO APK\work\server-auth-handoff\TRUBORAMA-SUITE`.
- Clone do backend: `E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix`.
- Git Android: `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\TurboElden-git`.

O APK instalado contém somente uma atualização de vídeos sobre a estável publicada. O login remoto descrito abaixo **não está implementado nele**. A etiqueta estável anterior permanece imutável.

## 3. O que já existe e deve ser aproveitado

No backend, todos os caminhos desta seção são relativos a `Servidor-pix` na revisão examinada.

| Recurso comprovado nos fontes | Arquivos principais | Limite relevante |
|---|---|---|
| Compra e emissão idempotente | `src/TurboRamaSuiteAdminServer/CommerceEndpoints.cs` | Produto fixo `TURBORAMA_SUITE`, SKU `SUITE_LIFETIME_1_DEVICE` |
| Código de ativação | mesmo arquivo, método `Issue` | 32 bytes aleatórios, Base64URL, verificador HMAC-SHA256 com pepper; validade de 15 minutos |
| Primeiro aparelho | `src/TurboRamaSuiteOnlineServer/SuiteService.cs`, `Store.cs` | `FIRST_CLAIM`, `PENDING_ENROLLMENT`, consumo transacional e um aparelho ativo |
| Prova de posse da chave | `Protocol.cs`, `Contracts.cs`, `Signing.cs` | RSA-PSS-SHA256, SPKI, DeviceId = SHA256 do SPKI; serialização canônica própria |
| Sessão e renovação | `SuiteService.cs` | desafio 60 s, autorização 180 s, renovação indicada em 5 s |
| ES separado de Suite | `EmulationStationService.cs`, `EmulationStationStore.cs`, `SharedEmulationStation.cs` | Reutiliza a identidade já ativada Windows; adaptador não fornece ativação nem API de conteúdo |
| Painel | `src/TurboRamaPixOnlineServer/SuiteAdminPanel.cs`, `SuiteSessionManagement.cs`, `SuiteAdminBff.cs` | Consulta, autorização administrativa, confirmação e revogação de alvo exato |
| Sessões administrativas | `src/TurboRamaSuiteAdminServer/SessionManagementEndpoints.cs` | Escopos existentes Suite/ES; ampliar explicitamente para Android |
| Conteúdo e downloads | `ContentService.cs`, `ContentStore.cs`, `ContentProtocol.cs` e projeto `TurboRamaSuiteContentGateway` | Consultas de autorização usam `suite_sessions`; sessão ES não é automaticamente aceita |
| Banco existente | `migrations/suite/001` a `026` | Há CHECKs de produto/SKU e pressupostos Windows; não basta cadastrar uma etiqueta |

Rotas existentes de ativação: `POST /v1/suite/activations/challenge` e `/v1/suite/activations/complete`. Sessões Suite: `/v1/suite/challenges` e `/v1/suite/sessions`. ES dedicado: `/v1/suite/emulationstation/challenges` e `/v1/suite/emulationstation/sessions`.

O ES compartilhado usa as duas rotas Suite com o cabeçalho exato `X-TurboRama-Client: EMULATIONSTATION`, aceito somente nesses POSTs. Há quatro Kinds assinados específicos de ES e namespace de desafios separado. **Não colocar esse cabeçalho globalmente no cliente Android nem assumir que identifica uma compra Android.** O código rejeita cabeçalhos inesperados em outras rotas.

Comércio interno: `/commerce/events`, `/commerce/deliveries/{purchase}/{item}`, `/issue` e `/transfer` relativos à entrega. São endpoints de serviço administrativo; o APK não deve conhecê-los nem receber o token/socket administrativo. Aproveitar o BFF e as permissões existentes.

## 4. Estado real do login Android

Fontes ativos:

- `brand-login/java/org/emulationstation/frontend/auth/LoginActivity.java`: formulário atual; `submit` chama `AuthSession.authenticate`; `openFrontend` usa `NEW_TASK | REORDER_TO_FRONT`.
- `login-return/java/org/emulationstation/frontend/auth/AuthSession.java`: implementação real da sessão, não os compile-stubs do diretório de login.
- A classe compilada em `platform-xbox-pce-refresh/modules-decoded/smali_classes8/org/emulationstation/frontend/auth/AuthSession.smali` também chama `LocalPassword.matches`.

Hoje a autorização é local, e um marcador é cifrado por AES-GCM no Android Keystore e guardado em `getNoBackupFilesDir()/authenticated-session-v1.bin`. Isso mantém a sessão após recriação do processo, mas **não contém licença de compra, expiração remota ou revogação do servidor**. Uma cópia desse marcador não deve virar uma licença comercial por migração.

Mudança necessária: manter o visual e o retorno às plataformas, substituir a decisão local por sessão autenticada do servidor. Não adicionar chamadas de rede síncronas dentro de `authenticate` na thread da interface. Não recriar duas Activities/carrosséis ao retornar do emulador. Não alterar motores, presets ou vídeos para implementar login.

## 5. Desenho recomendado para mais um serviço

**Proposta para implementação, ainda não existente:** criar produto comercial `TURBORAMA_STATION_ANDROID` e escopo de aplicação de mesmo nome. Cada compra Android recebe licença própria ligada ao cliente/pedido já existentes. Uma licença Windows não deve ser transferida silenciosamente para o telefone, pois a política atual limita a um aparelho.

Manter o mesmo banco/schema `suite` e os mesmos processos de servidor. Introduzir um adaptador Android com protocolo próprio versionado, usando as primitivas de assinatura, transações, antifraude de replay, idempotência e auditoria existentes. Não alterar os bytes canônicos v1 de Suite/ES para aceitar o novo produto.

Rotas **propostas**, todas inicialmente desligadas por feature flag:

| Rota | Função |
|---|---|
| `POST /v1/station/activations/challenge` | Validar licença/código, vincular desafio à chave pública candidata |
| `POST /v1/station/activations/complete` | Validar prova, consumir código/desafio uma vez e vincular aparelho atomicamente |
| `POST /v1/station/challenges` | Desafio de abertura/renovação e das operações privilegiadas aprovadas |
| `POST /v1/station/sessions` | Abrir ou renovar somente a sessão Android |
| `GET /v1/station/me` | Obter o nome de exibição do comprador associado à licença/sessão autenticada |
| `GET /v1/station/catalog` | Catálogo paginado por plataforma, mediante autorização de sessão/prova definida no contrato |
| `POST /v1/station/downloads/authorize` | Autorizar item específico e emitir concessão curta de download |

O servidor deverá entregar OpenAPI, exemplos sintéticos completos e vetores binários de serialização/assinatura antes da integração Android. Campos mínimos: schemaVersion, productId, applicationId, licenseId, deviceId, sessionId, action, contextHash, challengeId, nonce, timestamps, clientVersion e assinatura. Produto, aplicação, ação, sessão e destino precisam fazer parte dos bytes assinados; cabeçalho ou nome da rota sozinho não fornece isolamento criptográfico.

Usar domínios e Kinds novos prefixados `TurboRamaStationAndroid/.../v1` e `TURBORAMA_STATION_ANDROID_...`, definidos em um único contrato versionado. Fixar UTF-8, ordem de propriedades, escapes, representação de números/Base64, PSS SHA256/MGF1-SHA256/salt32 e validações; não pressupor que JSON de Java equivale ao serializador .NET existente. Não negociar algoritmo menos seguro como fallback silencioso.

A identidade Android usa chave RSA 2048 no Android Keystore e DeviceId derivado do SPKI. Nome de binding próprio `ANDROID_KEYSTORE_ONLINE`; não declarar o telefone como TPM/CNG. Usar TEE quando disponível, aceitar o perfil de Keystore suportado dentro da política explícita do servidor; não exigir StrongBox de todos os celulares. Informação de hardware reportada pelo cliente não constitui atestação remota. Criptografia e rede ficam fora da thread visual. Referência: [Android Keystore](https://developer.android.com/privacy-and-security/keystore).

## 6. Banco e isolamento comercial

Preparar migrations aditivas **depois de consultar o ledger real de produção**. Não presumir que o próximo número livre é 027 e não executar SQL deste handoff automaticamente.

1. Reutilizar `suite_licenses`, `suite_license_deliveries`, `suite_commerce_inbox`, cadastro do comprador e auditoria. Ampliar CHECKs de produto/SKU com allowlist explícita somente nas tabelas compartilhadas necessárias; revisar constraints e consultas hardcoded, incluindo migrations 001 e 004.
2. Parametrizar o caminho comercial novo por produto com defaults antigos intactos. SKU Android e prazo comercial deverão ser configurados pelo responsável de vendas; não converter automaticamente todas as vendas em vitalícias. Plano, limite e vencimento devem ser validados pelo servidor, nunca inferidos do APK.
3. Criar tabelas Android de sessões/desafios sob o mesmo schema (`suite_station_sessions`, `suite_station_challenges`, nomes propostos), com FK para licença/dispositivo e geração de revogação. Não ampliar indevidamente o namespace `suite_es_sessions` que pertence ao ES Windows. Reaproveitar as abstrações de store.
4. Rever constraints de binding em dispositivos/enrollment. Primeiro vínculo, consumo do código, limite por licença e criação da sessão precisam ser transacionais. Duas ativações simultâneas não podem ocupar duas vagas.
5. Suspensão financeira, revogação, reativação e transferência devem alcançar explicitamente as sessões/desafios Android. Cada leitura/renovação/concessão revalida produto, geração, estado da licença e entitlement; não depender somente do job que atualiza linhas.
6. Nova tentativa de webhook com mesmo evento/conteúdo deve devolver o resultado anterior. Evento conflitante ou versão financeira antiga não pode reativar licença cancelada. Preservar a proteção de eventos fora de ordem/tombstones existente.
7. Consultas do painel precisam filtrar produto e aplicação; limite de um Android não consome a licença Windows separada. Índices devem atender licença/dispositivo/sessão e expiração, evitando varreduras a cada heartbeat.

## 7. Compra, entrega, ativação e recuperação

1. Site confirma pagamento com o provedor no backend e envia evento pelo canal interno autenticado existente. Nunca confiar no redirecionamento “pagamento concluído” do navegador.
2. Provisionar uma entrega por pedido/item/produto. Concluir a transação antes de notificar o comprador.
3. Entregar ID da licença e código de ativação individual no canal autorizado do comprador. Exibir como “Código de acesso” na tela Android. O padrão atual de 15 minutos exige reemissão pelo portal/suporte se o cliente abrir mais tarde; não apresentar como senha permanente.
4. Como o verificador HMAC não recupera o código original, desenhar a entrega com outbox seguro de curta duração ou geração no resgate autenticado. Retries não devem gerar silenciosamente novos códigos nem entregar um código antigo já invalidado. Código não aparece em logs ou auditoria.
5. Aplicativo gera chave local, pede desafio, valida assinatura/autoridade e campos, assina a prova; servidor vincula o primeiro aparelho e consome o código. Limpar o campo de senha depois do envio.
6. Nas próximas aberturas, autenticar pela chave do aparelho e licença guardada, sem pedir código novamente. Revalidar sessão online; persistir identidade e metadados cifrados, nunca transformar o marcador local antigo em autorização remota.
7. Troca de aparelho/reinstalação/perda da chave usa transferência autorizada e auditada no painel/portal. Revogar vínculo e sessões anteriores, emitir novo código para o novo aparelho, preservar compra e histórico. Não pedir que o cliente compre de novo por uma falha de sessão.
8. Usuários de teste atuais necessitam licença de migração emitida pelo administrador. A senha antiga ou instalação existente não demonstra compra paga.

## 8. Painel para atendimento e acompanhamento

### Saudação com o nome de quem comprou — pedido expresso do mantenedor

Na abertura do aplicativo e no cabeçalho das plataformas, substituir o texto genérico de jogador por **“Bem-vindo, {displayName}”**. O nome vem do cadastro comercial da pessoa vinculada à compra/licença autenticada. Não aceitar nome enviado pelo APK como prova da titularidade e não usar apelido fixo, nome do dispositivo ou nome encontrado em outra sessão.

O servidor resolve a relação licença → entrega/pedido → cliente cadastrado. `/v1/station/me` exige a sessão Android e sua prova de posse conforme o contrato; não aceita um `customerId` arbitrário para consultar outra pessoa. Resposta mínima proposta: `schemaVersion`, `productId`, `applicationId`, `licenseId`, `deviceId`, `sessionId`, `customerRef` opaco, `displayName` e `profileVersion`. Retornar apenas os dados necessários à saudação; CPF, endereço, email e telefone não precisam ir para o carrossel. Aplicar `Cache-Control: no-store` nas respostas HTTP e vincular qualquer assertion de perfil ao mesmo contexto autenticado.

**Evidência concreta do cadastro:** `SuiteAdminPanel.cs`, método `LoadCustomerLicenses` (linha 545), lê o export configurado por `TURBORAMA_SUITE_CUSTOMERS_FILE`, padrão `/var/lib/turborama-pix/suite-customers.json`. O modelo `SuiteCustomerLicense` (linha 623) já contém `LicenseId`, `CustomerId`, `Customer`, `OrderRef` e `PurchaseId`. Isso confirma que o nome já chega ao painel. Não foi localizada nesta análise a implementação da origem comercial que produz esse export. O responsável deve identificar seu produtor e usar a mesma relação confiável de compra/cliente; não criar novo cadastro nem expor o JSON completo aos celulares. A API pública não deve ganhar acesso irrestrito a dados pessoais do painel.

Buscar perfil após ativação/abertura de sessão e quando a versão mudar, sem criar polling de perfil por frame ou por heartbeat. Armazenar o nome mínimo cifrado no armazenamento privado junto à identificação da licença; invalidar ao sair da conta ou trocar de licença. Voltar de jogo não exige login nem nova consulta se o perfil correto está em cache. Atualização do nome no site deve refletir na próxima sincronização de perfil.

Exibir o nome como texto simples, limitado para layout (até 80 caracteres no contrato e elipse visual quando necessário), sem HTML/markup nem interpretação como instruções. Não truncar o nome original no banco. Durante a primeira consulta, mostrar **“Bem-vindo”**; se o cadastro estiver sem nome, manter esse texto e indicar a correção do cadastro no fluxo de suporte. Não inventar um nome. Esta alteração depende da nova resposta de perfil e ainda não está instalada no APK de vídeos.

Adicionar filtro e cartão “TurboramaStation Android” às páginas atuais `/admin`, `/admin/clientes/{licenseId}` e listagens de sessões. Mostrar comprador associado, pedido, licença, plano/vencimento, estado financeiro, aparelho, versão do app, ativado em, último contato e sessão vigente. Não coletar IMEI, MAC, contatos ou arquivos pessoais para licenciamento. IP visto pelo servidor é diagnóstico, não identidade nem causa automática de bloqueio.

Ações: liberar conforme política financeira; suspender/bloquear licença; revogar somente a sessão Android selecionada; reemitir código quando elegível; transferir aparelho; consultar auditoria. Preservar autorização administrativa, CSRF, confirmação recente e comparação do alvo exato no momento de revogar. Revogar uma sessão antiga não pode derrubar outra recém-aberta nem a Suite Windows.

Estado “Online” precisa respeitar o intervalo Android: o limiar Windows de 15 segundos produziria falsos offline com heartbeat mais espaçado. Mostrar “Em uso”, “Sem contato recente”, “Expirada”, “Bloqueada” e “Aplicativo em segundo plano”, somente quando sustentado pelos dados disponíveis. A ausência de contato não prova que o usuário saiu manualmente.

## 9. Sessão sem aquecimento e sem perda da partida

Proposta inicial para homologação Android: autorização de 180 s e renovação em 60 s enquanto o aplicativo estiver visível, com jitter e backoff limitado. O servidor declara os valores na resposta; revisar o perfil do painel junto. Não copiar automaticamente o intervalo Windows de 5 s nem abrir um timer por emulador.

Um coordenador de autenticação atende todos os processos. Frontend em pausa deve continuar sem nave/estrelas/vídeos e sem polling visual; durante jogo, somente uma renovação leve deve ocorrer pelo coordenador IPC, sem manter renderização do carrossel. Garantir posse única do heartbeat entre processos. Se o app inteiro ficar escondido, interromper polling e revalidar ao retornar. Android pode encerrar processos em cache: [ciclo de processos Android](https://developer.android.com/guide/components/activities/process-lifecycle).

Usar prazo monotônico derivado da assertion assinada; mudar o relógio do celular não prorroga licença. Ao reiniciar processo/dispositivo sem referência monotônica confiável, revalidar antes de conceder novo acesso. Não reutilizar booleano estático isolado em cada processo como prova.

Sem internet ou servidor indisponível, permitir somente o prazo já concedido e distinguir indisponibilidade de bloqueio. Na expiração, impedir novos jogos/downloads e oferecer recuperação; para partida aberta, pausar de forma segura e mostrar reconexão/retorno, sem matar processo nem apagar saves. Essa política precisa ser implementada na ponte de cada motor antes de prometer bloqueio durante jogo. Uma revogação não fecha instantaneamente um processo offline: a latência máxima depende do prazo concedido e da aplicação do cliente.

## 10. Catálogo e autorização de download

O catálogo Android atual possui 18.049 registros em 53 categorias no JSON privado analisado; o carrossel exibe 43 plataformas. Não substituir por catálogo PC de 902 itens e não confundir categoria bruta com plataforma visível. Manter IDs, pastas, agrupamento por fabricante, traduções BR, sinopses, capa persistente e estados Baixar/Instalados/Jogar.

O APK atual contém links de catálogo. Para controle comercial efetivo de novos downloads, o backend deve receber a tabela privada de itens e resolver URL por ID após autorização. O pacote público/Git não deve levar URLs privadas, credenciais ou arquivos de jogos. A listagem pode ser cacheada; o ato de baixar exige concessão válida. Definir paginação por plataforma/cursor, busca por plataforma e versão/ETag; não carregar 18 mil itens a cada heartbeat.

O serviço de conteúdo atual consulta sessões Suite, e o adaptador ES aceita apenas abertura/heartbeat. Implementar um adapter de autorização Android no conteúdo/gateway; não forjar uma sessão Suite só para atravessar essas verificações. Preservar concessão curta, consumo único, validação do item, redirects HTTPS permitidos, remoção de bearer antes do armazenamento e autorização de retomadas/Range.

URLs públicas antigas não se tornam privadas por esconder links no APK. Um redirect pode revelar a URL final; avaliar URLs assinadas de curta duração ou gateway com validação do stream conforme a origem. Revogar licença não apaga jogos já baixados. Capas locais continuam persistentes; atualizar por versão/ETag sem refazer downloads desnecessários. Eventos de download concluído devem distinguir concessão emitida, transferência concluída e extração concluída; não marcar sucesso só porque o gateway respondeu 307.

## 11. Divisão de trabalho e ordem de entrega

### Responsável pelo servidor/site

1. Confirmar release real, schema, domínio público, SKU/plano Android e autoridade pública aprovada; preparar backup/rollback.
2. Definir contrato Android/OpenAPI e vetores de assinatura; adicionar produto/rotas/migrations por feature flag, mantendo regressão Suite/ES/PIX.
3. Integrar checkout existente, confirmação financeira, emissão/entrega/reemissão de código e transferência.
4. Estender painel, consulta em lote, revogação e auditoria; adequar presença ao perfil móvel.
   Incluir `/v1/station/me` e o nome do cadastro comercial vinculado à licença para a saudação “Bem-vindo, {displayName}”.
5. Integrar catálogo Android privado e concessão de download, preservando IDs; disponibilizar ambiente de homologação e licença sintética.
6. Entregar à equipe Android: URL HTTPS, chave pública/keyId e rotação, contrato versionado, códigos de erro, limites/TTLs, licença sintética e instrução de revogação/transferência. Nunca entregar pepper, chave privada de assinatura, senha do banco ou token admin ao APK.

### Responsável pelo aplicativo Android

1. Partir dos fontes e APK identificados neste documento; manter compilação/temporários em E:.
2. Criar cliente assíncrono e identidade Keystore. Atualizar LoginActivity/AuthSession reais e ponte de sessão entre processos.
3. Guardar autorização em cada entrada pertinente: login, frontend, abrir plataforma protegida, baixar e iniciar jogo/configuração de motor. Inventariar Activities/exported/deep links/IPC antes de fechar a integração; essa auditoria completa ainda não foi realizada nesta entrega.
   Substituir o rótulo genérico no cabeçalho pelo nome do perfil autenticado, mantendo cache privado vinculado à licença e fallback “Bem-vindo”.
4. Integrar catálogo/concessões sem alterar destinos locais, gerenciamento de capas ou comportamento dos emuladores.
5. Tratar retorno do jogo/recriação de processo sem duplicar tela, player ou polling. Usuário ativado não deve ver login por simples retorno de partida.
6. APK comercial não pode depender da chave de teste atual como plano definitivo. Planejar assinatura de produção, atualização e continuidade de dados antes da venda; não trocar certificado num upgrade improvisado.

## 12. Critérios de aceite a executar em homologação

Estes são critérios futuros; **não foram executados nesta análise**.

- Compra paga gera uma licença Android; webhook repetido não duplica; cancelamento anterior/duplicado não reativa; Suite/PIX continuam funcionando.
- Código incorreto/expirado/usado é negado; prova adulterada, replay, licença de outro produto e sessão de outro aparelho são negados.
- Duas ativações simultâneas mantêm o limite contratado. Transferência revoga o aparelho anterior e libera somente o novo.
- Abrir app, retornar de cada emulador, matar/recriar processo e reiniciar telefone preserva identidade sem gerar autorização indevida nem pedir código toda vez.
- Compradores diferentes recebem seus próprios nomes; trocar licença elimina o nome anterior. Nome vazio/longo/acentuado não quebra o layout. Alterar o cadastro reflete na sincronização sem consultar perfil continuamente.
- Bloqueio no painel é aplicado no prazo documentado; restauração de rede não reativa licença revogada; confirmação administrativa antiga não afeta sessão nova.
- Relógio alterado, cabeçalhos removidos, servidor antigo, assinatura/keyId desconhecidos e timeout não concedem autorização por fallback local.
- Autorização de download verifica produto/item; URLs antigas, Range, resume e redirects são considerados. Download/extração não são marcados completos apenas pela emissão do link.
- Medir CPU/GPU/memória/rede com carrossel parado, configurações, partida e app escondido em aparelhos de capacidades distintas. Um único heartbeat; nenhum player ou nave em segundo plano.
- Preservar jogos, BIOS locais, saves, capas e configurações em atualização `install -r`; nunca desinstalar/limpar dados para resolver sessão.
- Rollback dos novos binários/flags conserva auditoria e schema aditivo; Windows Suite/ES e vendas existentes continuam ativos.

## 13. Pendências reais e limites

O backend Android proposto não existe nas rotas examinadas. Não foi confirmado o release atual do Linux, preço/plano/SKU Android, vínculo exato da conta do site com o novo produto, domínio/base URL final ou perfil de revogação comercial. Esses pontos devem ser fechados pelo responsável do servidor antes do rollout, sem recriar todo o sistema.

Este handoff não promete impedir engenharia reversa do APK. Controle servidor protege operações e recursos controlados por ele; texto de direitos, cifragem local e Keystore não tornam um cliente distribuído impossível de analisar ou alterar. Preservar licenças e fontes obrigatórias dos motores de terceiros.

Nenhuma migration, deploy, chamada autenticada de cliente real, compra, entrega de senha, notificação WhatsApp ou alteração de banco foi feita nesta rodada. A evidência foi leitura do Git e arquivos locais. A única mudança instalada no telefone nesta rodada foi a atualização de vídeos descrita no início.
