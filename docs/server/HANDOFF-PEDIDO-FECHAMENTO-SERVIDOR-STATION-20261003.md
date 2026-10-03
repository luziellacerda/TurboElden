# PEDIDO AO SERVIDOR — concluir a integração Station Android

Data: 03/10/2026. Solicitante: mantenedor do TurboStations Android.

## 1. Destinatário, objetivo e limites

**Este pedido é para a equipe/IA do repositório `luziellacerda/Servidor-pix`, responsável pelo backend Station Android.** O objetivo é implementar as pendências, preparar a publicação, publicar a revisão compatível no canal Station mediante os controles operacionais abaixo e comprovar o funcionamento contra o aplicativo. Não encerrar a tarefa entregando somente scripts ou resultados de ambiente isolado.

- Produto e `applicationId`: `TURBORAMA_STATION_ANDROID`.
- Aplicativo TESTE: `org.turboramastation.frontend`.
- Endereço do cliente: `https://app.lzgames.com.br/v1/station/*`.
- Serviço alvo documentado: `turborama-station-api.service`, loopback `127.0.0.1:5192`. Conferir o alvo efetivo antes de modificar qualquer coisa.
- Preservar PIX, Suite Windows, Sambox Manager, gateway e demais produtos. Não mudar 5190, 5191, 5194, seus contratos ou dados como consequência deste pedido.
- Este documento solicita trabalho no servidor. A equipe Android fará as alterações e os testes do APK; não alterar outro repositório ou instalar APK por inferência deste pedido.
- Preservar os dados locais e mudanças não commitadas. Não clonar outro repositório quando já houver checkout adequado.

Antes de uma implantação, concretizar artefato, configuração, migrations, backup e retorno. Se houver aprovação operacional obrigatória ainda não concedida, apresentar esse pacote já conferido para a aprovação final. Não interpretar a leitura do documento como ordem para reiniciar serviços imediatamente, nem repetir pedidos de autorização que o mantenedor já concedeu para o mesmo escopo.

## 2. Fontes de verdade e estado observado

### Servidor

Autoridade desta solicitação: branch `feat/station-artifact-descriptor-20261002`, commit completo **`134ae386eca5dd8bff3bf8eee7ec9f014f0b6835`**, documento:

`docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md`

Esse retorno registra:

- 835 ROMs SNES existentes, incluindo 191 da subcoleção BR; BR é subconjunto, não quantidade adicional.
- 981 ROMs Mega Drive existentes, incluindo 94 BR. Oito entradas XML sem ROM foram excluídas.
- Índice candidato privado de 1.816 itens: `snes=644`, `snesbr=191`, `megadrive=887`, `megadrivebr=94`, com capas e descritores.
- Carregador validou os 1.816 arquivos e capas. HTTP isolado validou uma capa e uma transferência real de cada categoria, além dos casos sintéticos. Isso não equivale a testar todos os downloads nem a implantar em produção.
- Ferramenta de conciliação testada com base sintética, ainda não executada sobre o índice efetivo.
- Produção ainda sem nova release/índice comprovados, com histórico de 48 capas 404 e nenhuma capa 200 observada naquela apuração.

### Aplicativo

Código: TurboElden, branch `station-reconstrucao-20261002`, commit **`7d5df08d922ef7c517979cf2263ff4bfe4be74ff`**. APK instalado:

`SHA256 43670211fe6de01438c0352b44875c43336c052d431582032680fa2c9265517f`

Login com licença salva e abertura do carrossel foram comprovados. O renderer recebeu 996 itens: Mega Drive 693; SNES 176; SNES BR 28; Game Gear 58; Game Boy 22; 32X 7; Game Boy Color 7; GBA 5. Não foi capturado o HTTP individual dessa leitura; pode ser resposta nova ou cache Station assinado. Não tratar essa contagem como prova de publicação recente.

O APK lê `artifact` e `itemRevision`, mas capa 200, download real, instalação e abertura pelo novo fluxo ainda não foram comprovados. Jogos anteriores foram preservados fisicamente, porém sua associação verificável aos novos IDs continua pendente. A barra de 100% prepara o catálogo, não baixa jogos.

## 3. Implementar e conferir no servidor, nesta ordem

### A. Identificar a produção real

1. Ler as instruções aplicáveis, o handoff único e as alterações posteriores a esta referência. Registrar o `ExecStart`, drop-ins, SHA256 da DLL em execução, revisão/contagem do índice efetivo e histograma de `platform`.
2. Conferir flags Station, chaves configuradas, permissões da conta do serviço e ledger real das migrations. Não deduzir versão instalada pelo branch, diretório de trabalho ou reinício do computador.
3. Obter acesso autorizado ao índice privado efetivo. Se a conta não puder lê-lo, informar exatamente o acesso ou a cópia privada necessária; não substituir o índice por aproximação e não publicar seus caminhos ou segredos no Git.

### B. Completar o índice sem perder o conteúdo existente

1. Conciliar o índice efetivo com o candidato de 1.816 itens usando as ferramentas já criadas e o mapa privado de origem. Preservar IDs publicados, instalações/cache associados e jogos das outras plataformas.
2. Usar caminho original exato ou SHA256 e plataforma, conforme o algoritmo revisado. Recusar correspondência ambígua; nomes parecidos não autorizam associação.
3. Validar cada ROM, capa, descritor e `launchPath` do resultado. Corrigir também as entradas herdadas: não basta os novos SNES/Mega Drive funcionarem.
4. Resolver os 404 de capas por existência, leitura pela conta real do serviço, MIME, tamanho e associação `coverId` → arquivo. Compartilhamento de `coverId` exige dados compatíveis; mudança de imagem exige revisão nova ou identidade nova conforme o contrato.
5. Publicar revisão superior à efetiva. Documentar IDs preservados/novos, itens excluídos e motivos, sem esconder falhas nem transformar arquivos ausentes em jogos baixáveis.
6. Inventariar as outras plataformas autorizadas. As 12.346 linhas históricas não provam que os arquivos estejam disponíveis. Informar por plataforma o que existe, o que foi preparado e o que falta acessar; não declarar biblioteca completa tendo conferido apenas dois sistemas.

### C. Fechar a compatibilidade com o APK antes da publicação

1. Entregar o conjunto literal final de valores `platform`, suas contagens e a revisão candidata. Não presumir que um rótulo visual equivalente seja um identificador aceito pelo APK.
2. O alias `megadrivebr` tem ajuste de fonte citado no commit Android `5988343`, mas não está no APK instalado identificado acima. Aguardar confirmação do APK compatível antes de disponibilizar esse valor ao aparelho de teste.
3. As outras 18 diferenças de identificadores levantadas no handoff devem ser conciliadas com a equipe Android por mapeamento explícito. Não mudar identificadores unilateralmente para contornar o cliente.
4. Limites atuais: 4.096 itens e envelope de 12 MiB, sem paginação. Se o índice final exceder isso, especificar e implementar um contrato versionado de paginação/revisão/assinatura, entregar exemplos sintéticos e coordenar o APK. Nunca truncar a lista silenciosamente nem publicar resposta que o cliente atual rejeitará.

### D. Concluir autenticação, perfil e gestão das licenças

1. Confirmar, usando o contrato atual, `POST activations/challenge`, `POST activations/complete`, `POST challenges`, `POST sessions` e `GET me`, todos sob `/v1/station/`.
2. Preservar autoridade pública, domínios assinados, identidade de produto/aplicação e chave do aparelho. `STA-` é `licenseId`; o código de ativação é Base64URL canônico de 32 bytes. Não mudar essa interpretação nem pedir segredo pelo chat.
3. Validar retomada por licença salva, expiração real de desafio/sessão, revogação, bloqueio e tentativa por outro aparelho. Conferir os prazos documentados de 60 segundos para desafio e 180 para sessão.
4. Confirmar que `GET me` entrega `displayName` e `profileVersion` do comprador autorizado. O texto de saudação no app é responsabilidade Android, mas o perfil correto precisa vir do servidor.
5. Auditar emissão, liberação, bloqueio e reemissão no mecanismo administrativo já existente. Implementar o que estiver ausente para Station com isolamento por produto; não duplicar painel/banco nem inventar preço, validade ou política comercial. Se faltar uma decisão comercial, apontá-la concretamente.

### E. Entregar capas e jogos pelo fluxo autenticado

1. `GET catalog`: envelope assinado, revisão e itens com os cinco campos atuais: `itemId`, `name`, `platform`, `revision`, `coverId`; sem URL ou caminho privado.
2. `GET covers/{coverId}`: bytes reais, MIME decodificável, limites compatíveis e respostas 404/429 tratáveis. Conferir hash dos bytes entregues contra a imagem selecionada, inclusive quando houver redimensionamento.
3. `POST downloads/authorize`: payload assinado com `itemRevision` e `artifact` obrigatório: `fileName`, `sizeBytes`, `sha256`, `format`, `launchPath`, `expandedSizeBytes`, `fileCount`. Não liberar grants incompletos.
4. `GET artifacts/{grantId}`: mesmo Bearer/sessão do grant, uso único, validade de 60 segundos, bytes íntegros, `application/octet-stream`, tamanho exato e sem redirect/URL privada. O contrato atual não aceita Range; queda exige nova autorização e nova transferência.
5. Conferir vínculo e descritor antes do consumo atômico do grant. Rejeitar item alterado, sessão errada, reutilização, expiração, licença bloqueada e identidade inválida.
6. Preparar arquivos reais raw/ZIP/RAR/7z e pacotes com vários arquivos apenas quando existirem no acervo a publicar, com escolha explícita de `launchPath`. Não extrapolar um teste SNES ZIP para Wii U ou BIN/CUE.
7. Para reconhecer jogos já existentes no telefone, coordenar uma correspondência verificável de identidade/hashes com a equipe Android. Definir formalmente qualquer informação adicional necessária antes de criar novos campos ou rotas. Não exigir que o app adivinhe por nome, extensão ou posição da lista; não apagar/rebaixar dados existentes como solução.

## 4. Preparação e publicação controlada

Entregar release imutável, commit completo, hashes, índice conciliado validado, permissões, configuração sem segredos, migrations necessárias e backup restaurável. Medir o custo da leitura/verificação dos arquivos na inicialização e conferir que o conteúdo permanece estável durante o grant.

Preparar o retorno para a DLL/configuração/índice anteriores, preservando o banco e suas compatibilidades. Conferir os serviços compartilhados antes e depois. Efetuar a publicação somente após cumprir os controles operacionais e confirmar a compatibilidade do APK da seção C. Se uma aprovação final for necessária, apresentar os dados concretos nessa etapa.

Depois da publicação, repetir o fluxo pelo endereço HTTPS público e pela conta autorizada de teste. `ready=200`, processo ativo ou computador reiniciado não comprovam catálogo, capa e download.

## 5. Evidências necessárias para concluir

| Prova | Evidência exigida em produção |
|---|---|
| Versão publicada | Commit/release, hash da DLL efetiva, revisão e contagens do índice, horário e alvo da mudança. |
| Acesso | Ativação/retomada, perfil correto, expiração real e negação após bloqueio/revogação. Sem expor código ou token. |
| Catálogo | Resposta assinada autenticada; revisão e contagem por plataforma; comparação com o inventário validado. |
| Capas | Validação em disco de todas as capas do índice e amostras HTTP reais por plataforma; MIME/tamanho/hash; inexistente 404. Registrar a amostra, sem afirmar que ela cobre cada transferência. |
| Download | Grant completo e transferência integral real por plataforma/formato disponível; tamanho/SHA256 conferidos. |
| Erros | Reuso, outra sessão/aparelho, grant expirado, arquivo alterado, bloqueio e interrupção seguidos de nova autorização, com resultado explícito. |
| APK | Em conjunto com Android: catálogo fresco, capa visível, baixar, instalar, abrir, sair, retomar acesso e apagar apenas o jogo. O servidor não pode declarar sozinho esses testes como aprovados. |
| Regressão | Saúde e fluxos dos produtos compartilhados preservados; plano de retorno conferido. |

Não publicar envelopes privados, Bearer, grants, códigos, chaves, DSNs, dados pessoais ou caminhos internos. Usar exemplos sintéticos para documentar corpos de requisição e resposta.

## 6. O que continua sob responsabilidade Android

Incorporar aliases confirmados, identificar rede versus cache, medir itens recebidos/publicados por plataforma, registrar falhas de capas sem segredos, concluir reconhecimento verificável dos jogos anteriores, retirar o legado ativo/residual do frontend e validar todos os fluxos no aparelho. Preservar certificado, pacote, Keystore, saves e emuladores. Não tratar este pedido ao servidor como evidência de que essas tarefas do app já terminaram.

## 7. Retorno obrigatório, no documento único existente

Atualizar **`docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md`**, conforme a convenção atual do servidor. Identificar este pedido e manter data, branch e commit completo do retorno.

Informar separadamente:

1. Implementado e testado em isolamento.
2. Implantado e comprovado em produção.
3. Depende do APK, com contrato/dado exato necessário.
4. Depende de acesso, conteúdo, decisão ou aprovação do mantenedor, com impedimento concreto.

Incluir tabela por plataforma com itens publicados, capas verificadas, downloads comprovados e exclusões restantes; versão exata do APK compatível; mudanças de contrato; e próximos passos de cada equipe. Não responder copiando este pedido nem chamar testes isolados de produção pronta.

**Critério de fechamento:** servidor publicado e compatível, catálogo autorizado completo para o acervo efetivamente disponível, capas/arquivos funcionando e fluxo no aparelho aprovado. Se alguma plataforma ou etapa continuar pendente, declarar entrega parcial com a lacuna identificada, sem promover a versão a estável.
