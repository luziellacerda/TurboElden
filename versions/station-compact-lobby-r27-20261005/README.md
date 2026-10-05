# R27 — lista compacta e painel de jogadores online

## Entrega e estado

Pedido: reduzir os cartões grandes de jogadores em **Jogar online** a uma lista de nomes. Um toque deve abrir informações, status e ações de convite em um painel organizado.

APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Salas-Lista-R27-20261005.apk`.

- SHA-256: `c1191ce1d531b1ec9171d6d4c2f57541349339e64e8941a33788c4067d616bd6`.
- Tamanho: 2.053.862.128 bytes.
- Base exata: R26 `1d4549da6a15a9a9b2e8c52491ecc4382e0b5e050900763aebf163d136a36e75`.
- Única entrada alterada: `classes35.dex`, SHA `ee0108d546daa061e701cf3817828b5cc1b32e9ef774c11c4de3e291d72ec6c5`.
- 13.083 entradas preservadas, inclusive todos os motores, recursos, licença, catálogo, downloads, mídia e demais DEX.
- Carrossel R26 preservado: `b2d706dc07d4423758798fe0d6d37ce01c8f395b344c685a7b796ce60d03dd70`.
- Certificado original e alinhamento de 16 KiB conferidos. Compilado e testado no PC. **Não instalado e sem conferência visual Android desta revisão.**

O telefone permanece na última instalação comprovada R25. A conexão USB estava vazia nesta conferência; a tarefa coordenada registrou o dispositivo Samsung com erro de inicialização do driver (ProblemCode 10). Não houve alteração de driver, configurações, dados ou sessão do telefone. Não afirmar que a nova tela já apareceu no aparelho. Não promover como estável ou visual aprovado.

## Interface

- Uma linha de 48 dp por jogador, nome em uma linha, indicador discreto de presença e área inteira tocável. Sem avatar grande, cartão externo ou botão Convidar repetido na lista.
- Nome longo usa reticências; leitura assistida identifica nome/status e abertura do perfil. A pesquisa filtra explicitamente a página atual, mantendo a paginação real do servidor.
- Toque no nome abre painel próprio, com nome completo, status publicado, jogo quando essa associação existe no snapshot, ação de convite, código da própria sala e bloqueio.
- Painel tem rolagem, largura limitada e altura adaptada ao espaço. Diálogos de código também são roláveis. Cores seguem preto/verde Turborama, com vermelho apenas no bloqueio.
- Cabeçalho do jogo reduzido de 100 para 76 dp; capa preserva proporção. Chat, salas, ações Pronto/Iniciar/Sair e transporte existente continuam funcionando pelas mesmas funções.
- As ações e os campos do painel vêm do estado real: não são adicionados jogadores simulados, ping, país, ranking, vitórias, foto ou histórico inexistentes no contrato.

## Dados reais e limites de presença

O snapshot assinado já traz `selfId`, `instance`, `revision`, `peers[{peerId,nickname,status}]`, `rooms`, `invites` e `room`. Os status conhecidos são `online` e `in-room`. Ausência de um jogador da página **não prova que ele ficou offline**; o painel informa presença não confirmada e desabilita o convite. Status futuro/desconhecido também não é convertido em disponibilidade.

O jogo de um contato só aparece se ele está nos membros da própria sala ou se há uma sala pública cujo `hostId` é o contato. O contrato não publica a sala de todo convidado; não inferir o jogo de um visitante por associação de nomes.

`StationPlayerModel` centraliza a apresentação e a habilitação das ações. Jogador ocupado, própria conta, sala cheia, anfitrião diferente e partida iniciada têm textos específicos. Verificações locais melhoram a interface; o servidor continua sendo a autoridade final.

## Convite direto

1. Usuário toca no nome de um jogador disponível.
2. Se ainda não existe sala própria, **Criar sala e convidar** prepara o jogo com `StationOnlineGame.prepare`, verifica ROM/core/runtime/opções, chama `create` e usa o `roomId` realmente recebido.
3. Envia `invite` com esse `roomId` e `peerId` selecionado. Não gera sala nem sucesso local fictício.
4. A confirmação só aparece após resposta real. O convite existente expira em 60 segundos, conforme o contrato do servidor.
5. Se criar a sala funcionar mas o convite falhar, a sala recebida é entregue ao reducer antes do erro. Ela continua visível; a interface não finge rollback nem cria uma segunda sala automaticamente.

Não enviar convites quando a pessoa já está em uma sala. Somente o anfitrião de uma sala aguardando, com vaga, pode convidar ou copiar seu código. Limites, bloqueios, identidade, prontidão e incompatibilidades continuam validados no servidor.

## Código de sala — formato local TS1

O botão **Código da sala** ou **Código da minha sala** abre o código e permite copiá-lo. O receptor usa **Código** no cabeçalho e cola o valor. O formato é:

```text
TS1:<instance>:<roomId>:<itemId>
```

- `instance`: identificador publicado pelo servidor, 32 caracteres hexadecimais minúsculos.
- `roomId`: identificador de uma sala realmente criada, 32 caracteres hexadecimais minúsculos.
- `itemId`: ID exato do catálogo, `[A-Za-z0-9_-]{8,64}`.
- Entrada limitada a 160 caracteres, quatro segmentos exatos, sem URL/caminho, normalização de ID ou prefixo presumido. Espaços externos de copiar/colar são removidos; caracteres inválidos internos são recusados.

Este é um **localizador público da sala**, não senha de licença, token de autenticação, senha do runtime, ticket de relay ou autorização de entrada. Não contém nenhum desses segredos. Não acrescenta rotas, PIN curto, código aleatório sem resolução nem registro no servidor. A comparação de `instance` recusa códigos anteriores a um reinício do hub.

Após validar o formato e confirmar que o usuário não está em outra sala, o app chama o fluxo existente `join(roomId,itemId)`. Este prepara o mesmo arquivo/motor e usa a API assinada atual. A sala pode ter fechado, lotado ou começado desde a cópia; o servidor decide e retorna o erro correspondente. O código é válido enquanto a sala existir e houver vaga; **não confundir com os 60 segundos do convite direto**.

Ambos os clientes precisam desta UI para copiar/colar TS1. Convites diretos existentes não exigem código. Códigos não tornam um sistema incompatível em compatível nem comprovam que o relay já foi publicado.

## Arquivos e fluxo

| Arquivo | Mudança |
| --- | --- |
| `StationRoomsActivity.java` | Lista compacta, filtro da página, painel, código, sequência create/invite e callbacks vinculados ao ciclo da tela |
| `StationPlayerSheet.java` | Painel nativo Android com rolagem e ações delegadas ao controlador |
| `StationPlayerModel.java` | Regras de disponibilidade, informação publicada e habilitação das ações |
| `StationInvitationCode.java` | Serialização/validação estrita do localizador TS1 |
| `StationOnlineClient.java` | Mensagens específicas para sala encerrada, jogador ausente, convite existente/expirado e limites |

O reducer `StationRoomState` é preservado: resposta antiga não restaura uma sala obsoleta. Callbacks conferem `active` e `epoch`; parar a tela cancela requests e fecha os painéis. Operações HTTP continuam fora da thread visual. Duplicações por toques são impedidas por `busy`. Reconectar reseta esse estado após cancelar a geração anterior.

As outras 139 fontes preexistentes/dependências não foram alteradas. Nenhum motor, túnel WSS, heartbeat, TLS/pin, identificação de ROM, overlay de controle ou chamada de inicialização de jogo mudou.

## Compilação, testes e reprodução

Workspace final: `E:\ESTUDO APK\work\station-compact-lobby-r27-20261005`. Compilação e temporários em E:. APK final é escrito em G: para evitar manter duas cópias de 2 GB simultaneamente em E:. A receita só elimina seu `unsigned.apk` temporário depois de validar assinatura e todos os payloads.

Primeiro foi recompilada a fonte R12 intacta (141 arquivos): o resultado reproduziu exatamente o DEX base `8961f4a11aece9cb0a7a264767043664e008359202dd55dbbfd6cc02079eb4ae`. Isso identifica a base real das salas que permaneceu em R26; não assumir que a data de uma pasta indica outra versão.

Entrega final: 144 fontes Java incluindo dependências realocadas, Java 8/API34, DEX mínimo26. Dependências upstream/licenças de R12 preservadas no APK e nesta cópia. Compilar usa `station-client.jar` de `E:\ESTUDO APK\work\station-library-r10-build-20261004`, SDK34, JDK17 e D8 conforme receita. Não rodar os scripts de preparação histórica sobre a pasta final existente. Para reproduzir, copiar `netplay-src`/`dependency-src` deste snapshot para uma pasta isolada, ajustar os caminhos de ferramentas e usar a receita de build. A receita de pacote exige a base R26 exata; para sucessora, comparar todos os recibos antes de mudar o guard.

Passaram **107 testes Java executáveis** de roundtrip/códigos inválidos, estados de jogador, sala cheia, convidado/anfitrião, dados desconhecidos e reducer; mais **18 verificações de preservação/fluxo**. Assinatura, alinhamento e igualdade de todas as entradas fora de classes35 foram conferidos. Estes testes não executam o renderer Android nem comprovam uma partida entre dois telefones.

## Próxima instalação e conferência no aparelho

1. Conferir USB autorizada e ausência de partida/download ativo. Atualizar com dados, sem desinstalar e sem limpar.
2. Aceitar a instalação comprovada R25 ou R26 como anterior, depois conferir o hash integral de `base.apk` contra R27.
3. Abrir um jogo compatível → Jogar online. Conferir a densidade da lista, nomes longos, busca da página e toque na linha.
4. Com duas sessões de homologação, abrir perfil, criar/convidar, aceitar e verificar o chat. Conferir também jogador ocupado/sala cheia/convite vencido.
5. Copiar código de sala real e colar no outro aplicativo. Conferir encerramento da sala e rejeição de código antigo após reinício controlado em homologação.
6. Conferir retorno às plataformas sem login. A aprovação estética e gameplay entre aparelhos são pendências reais.

## Para o servidor

Nenhuma implantação ou alteração de contrato é exigida por esta apresentação. Reutiliza `/v1/station/online/command` e `/v1/station/online/events`, campos e ações já documentados em R12. O estado de publicação do relay e a lista de motores liberados permanecem separados desta entrega. Não prometer Neo Geo/CPS/MAME/FBNeo online apenas por haver uma lista melhor. O delta de downloads `11be7f3` também continua separado, não incluído por esta montagem.

Não publicar APK, ROMs, BIOS, credenciais ou sessões no Git. Tags estáveis anteriores permanecem intactas.
