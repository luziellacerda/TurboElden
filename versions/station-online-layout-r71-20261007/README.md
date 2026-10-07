# R71 — salas, participantes e recuperação de conexão

Pedido de 07/10/2026: reorganizar Salas, Pessoas e Criar sala, mostrar os dois
participantes antes de iniciar, unir o novo retorno do servidor, acrescentar o
vídeo de Todos os jogos SNES e corrigir as janelas separadas do aplicativo.

## Base que deve ser preservada

- APK R70: `c12ee4e2928a629be4a2cc6dc9201fc7c5722e21a1fa8385d21da7a7dc69a32e`.
- Java-base R67: 193 fontes verificadas. A composição conciliada tem 198 fontes,
  com 19 arquivos no overlay declarado.
- A seleção de coleções R70, os 57 vídeos anteriores, o limite de 30 fps somente
  no menu, controles locais, BIOS automática R66, assinatura, identidade e dados
  existentes são preservados. O vídeo novo eleva o total a 58.
- Fonte da recuperação: `4d30401a80658dd56666ef10f48d9556b3fdd9e9`, preservada
  em `../station-online-recovery-r67-20261007`; entrega `65dd0aa05330ace8df0a91a89c895a3aab6428f8`.
- Servidor: retorno `6f8dcead3af84ed1c8323f6e241900bf2f36a938`; implementação
  `32ce9d2b30bb23deef17899e10fc285f38ea81ab`. O retorno declara **não implantado**.

## Interface

`StationActionButton` e `StationSocialIcon` padronizam os botões: corpo36dp,
alvo de toque48dp, raio8dp, texto13sp, ícone18dp e estados habilitado/desabilitado.
Seleção lateral, ação principal e saída têm hierarquia e cores próprias.
Não foram acrescentados timers de efeitos; a política anterior permite movimento
somente em ABRIR/VOLTAR quando explicitamente habilitado e visível.

`StationRoomsActivity` mantém uma seção visível por vez. Na própria sala:

1. Nome do jogo, capa existente e saída discreta.
2. Os dois participantes, com nome, anfitrião/convidado, indicação de você e Pronto.
3. Confirmação/início separados de conversa/convite.
4. Confirmação final com os mesmos participantes e capa. Uma troca de instância,
   sala ou jogo fecha a confirmação; o comando revalida um único snapshot.

`StationPlayerSheet` usa os mesmos botões, ícones e estados, preservando regras e
callbacks de convite, entrada, compartilhamento e bloqueio.

## Nomes: origem e limite real

`StationRoomRoster` lê **somente os IDs de room.members** para escolher os
participantes. `room.ready`, `room.hostId` e `selfId` determinam as indicações.
Nome vem de `peers[].nickname` correlacionado por `peerId`. Um cache limitado a256
nomes observados, separado por instância e limpo na reconexão, conserva nomes
quando a lista de pessoas muda de página. O cache nunca determina presença,
prontidão ou participantes e nunca equivale a uma porta de controle.

O código do servidor recebido ainda pagina peers em100 registros e não inclui
obrigatoriamente os perfis dos membros. Se um nome nunca veio, a interface informa
“Nome indisponível”; não inventa nome nem copia o nome do outro jogador. A garantia
para qualquer página exige complemento do contrato pelo servidor.

## Recuperação e ativação

O novo transporte preserva o TCP do motor e troca o WSS autenticado, com buffers
limitados, sequências/ACK e pausa/barreira JNI. Recuperação depende de o motor e o
servidor continuarem vivos; não restaura emulação depois de perda do processo.
O retorno contém provas isoladas, não homologação física de dois celulares.

**Não há downgrade automático do runtime novo para v1.** API antiga, flagfalse,
registro sem o hash novo ou outro aparelho com uma engine diferente impedem
iniciar v2. O operador precisa publicar a versão candidata e registrar as adições
geradas a partir do ELF efetivamente compilado, preservando todos os IDs antigos.
Não utilizar IDs Linux com um binário Windows diferente.

## Receitas e evidências

- `JAVA-OVERLAY-MANIFEST.json`: todos os arquivos conciliados, com hashes.
- `recipes/build_candidate.py`: restauração193 + overlay. DEX28 muda somente para
  a entrada Login e dois auxiliares de navegação; os demais fontes do cliente
  permanecem idênticos, inclusive autorização, prova, catálogo e downloads.
- `recipes/run_tests.py`: testes vinculados à composição final, não apenas à base.
- `recipes/package_r71.py`: comparação de todas as entradas com a R70, certificado
  original e alinhamento16KiB. Exige exatamente seis substituições (Manifest,
  DEX28, DEX35, carrossel, runtime online e engines) e uma adição de vídeo.
  O Manifest muda um único byte: modo de abertura de ESActivity. Exige recibos de
  testes vinculados aos mesmos fontes, JARs e DEX efetivamente empacotados.
- `evidence/ui-tests-before-recovery.json`: **passagem anterior, somente visual**,
  522 checks +42 guardas. Não é prova da composição final com recuperação.
- `evidence/server-source-origin.json`: origem dos arquivos recebidos, sem checkout
  das branches de trabalho nem exposição de credenciais.

Artefatos de trabalho ficam em E:, APK final em G:. A instalação deve ser direta,
sem copiar APK extra para o telefone, sem desinstalar/limpar dados e sem interromper
partida. Recibos posteriores de pacote/instalação prevalecem sobre esta preparação.

## Uma tarefa de navegação e sessões encerradas

Leia `NAVIGATION-AUDIT.md` e `evidence/device-task-observation.json`. A leitura
do A56 confirmou duas tarefas na R70; não comprovou duas renderizações ativas.
O carrossel passa a permitir Salas na mesma tarefa. A entrada reaproveita a tarefa
existente depois da autorização e mantém uma partida no topo. Aberturas repetidas
do lobby não criam novas cópias. O retorno real do jogo libera o registro local
de navegação; não altera o controlador, o motor nem encerra a partida por timer.

`StationGameSession` também corrige um problema no candidato recebido: o evento
terminal 6 deixava o heartbeat ativo. Agora cancela essa consulta e encerra o
executor original. A tela de falha pode continuar aberta; o evento humano 4
posterior permanece válido e faz uma única tentativa pontual de Leave, somente
se a mesma sala ainda existir.
Os eventos tardios não reativam o executor encerrado. Background normal v2 e
queda temporária continuam conservando a sessão e seu heartbeat necessário.

Testes locais incluem seleção das tarefas, destino de conversas/rascunhos,
sequências terminal→saída humana, idempotência e corridas entre encerramentos.
As verificações de transporte usam TLS/WSS/TCP reais com pausa nativa simulada;
não equivalem a gameplay Android, homologação de todos os emuladores ou ganho
térmico medido. Consulte os recibos finais em `evidence`.

## Mídia — Todos os jogos do Super Nintendo

O vídeo dedicado `todos jogos snes.mp4`, SHA256
`db7190e5798bb0976ede2e849089ba41904084ee54c5bee9ee1806c15aeac272`,
é acrescentado como `assets/turbo-system-videos/720-collection-snes-all.mp4`.
A rota exige coleção de tipo2 e plataforma `Super Nintendo` ou `snes`.
Plataformas principais, `Super Nintendo - BR`/`snesbr` e os57 vídeos da R70
conservam seus arquivos e rotas anteriores.

Saída720×720,30fps, sem áudio, poster RGB565 do primeiro frame. São58 posters
e58 registros de frames retidos; a política continua permitindo um único decoder.
Navegação, configurações, cantos e menu30fps permanecem da R70. Não há comprovação
visual no aparelho nesta etapa.

`NATIVE-CAROUSEL-MANIFEST.json`, `recipes/build_carousel_r71.py` e
`evidence/carousel-build-r71.json` vinculam os três headers ao carrossel compilado
`9671f553858ef1c98c320ea85cfa7aa29350c1a9c341a3fe08b8d46e4a8a48d7`.
O MP4 tem SHA256
`780ad95803b649cac38e2db19a796a9f8bcc103dd0b4d9ae1cb5a7d68f54ed7e`.
Passaram3444 checks de rotas/posters,66 de cantos,3584 de navegação,
199592 de política do decoder e as60 verificações de configurações.

Nesta composição ampliada com navegação única, o empacotador exige exatamente
seis substituições na R70: DEX28/35, Manifest, runtime online, engines e carrossel. Exige também
exatamente uma entrada nova: o vídeo dedicado. Confere todos os demais bytes,
os hashes de fontes/receitas/recibos, o poster embutido, alinhamento16KiB e a
assinatura original. O nome padrão do candidato é
`TurboStations-Premium-R71-Completa-20261007.apk`. O empacotamento e a assinatura
foram concluídos; `evidence/package.json` registra os hashes e a comparação integral.

## Instalação concluída — A56

R71 completa instalada diretamente no Samsung A56 em 07/10/2026 às21:22:46UTC.
SHA256 instalado e do pacote: `556170c32b6dd25fb5084693826d854adf736b4a1df156fd9229a8458b025018`.
UID e data original de instalação preservados; sem desinstalar, limpar dados,
alterar configurações ou copiar APK extra. A entrada oficial abriu LoginActivity,
mas a tela estava bloqueada/apagada: não equivale à confirmação de autologin,
menu, tarefa unificada ou gameplay. Conferências físicas ficam com o mantenedor.
Recibo: `evidence/installation-samsung-r71-20261007.json`.

Motorola Edge30 continua na última versão conferida R70 e precisa receber o mesmo
APK R71 antes de testes online em dupla. Servidor ainda depende da publicação,
registro dos hashes exatos e ativação declarados no handoff. R71 não é tag estável
geral e não substitui a tag estável de menu R69.

### Observação posterior à instalação

Após o desbloqueio pelo usuário, ActivityManager confirmou ESActivity em RESUMED:
o carrossel abriu no pacote instalado. O mantenedor atribuiu o relato de Voltar
à instalação/estado antigo aberto e informou que deixou de ocorrer. Não foi
demonstrado crash da R71 nem criado um novo patch por essa hipótese. Não equivale
a teste do retorno de salas ou gameplay. Recibo sanitizado:
`evidence/android-followup-samsung-r71.json`.
