# Política de continuidade: compilação, escopo e preservação

Esta é a regra de trabalho para outra IA ou pessoa continuar o TurboStations.
Ela vale para o aplicativo e para os handoffs que ele envia ao servidor. O
pedido mais recente e explícito do proprietário define o trabalho autorizado;
um pedido limitado não autoriza melhorias paralelas. Os registros históricos
continuam úteis como evidência, mas não são comandos para executar novamente.

## 1. Identificar o ponto de partida

1. Leia o pedido atual, `AGENTS.md`, o recibo da revisão em uso, a receita
   correspondente e `git status`. Anote o commit exato da fonte, a revisão
   realmente instalada e a referência estável separadamente. Não deduza uma
   instalação ou aprovação física a partir do Git.
2. Registre por escrito o defeito ou mudança solicitada, o comportamento
   esperado, os arquivos e entradas do APK que podem mudar, e os componentes
   que devem permanecer idênticos. Use uma pasta/ramo isolado para o delta.
3. Se a causa ainda for incerta, investigue de modo somente leitura. Uma
   hipótese sobre servidor, desempenho ou aquecimento não autoriza alterar
   motor, rede, renderizador ou configuração do telefone.
4. Antes de uma alteração produtiva, identifique a última fonte congelada e
   confira os hashes do APK de base, DEX, bibliotecas, ferramentas e recibos.
   Falta ou divergência de um insumo bloqueia a montagem daquela revisão;
   não substitua silenciosamente por uma versão parecida.

### Ponto R169 em 17/10/2026

- Fonte congelada da montagem R169: `e0fea23e96ccedad686f7d7d7d2a821780e486a0`.
- APK doador **R168 assinado**: SHA-256
  `875fb0696c4fb50ce4af953bccd62fcd68dfdecb247f65d2fc027b71aa330b3d`.
- APK R169 já assinado: SHA-256
  `68521db5fbd46d6da9895c4d9b291febda5597c82ba3b51935ccd7e98520877d`.
  Não remontar nem reassinar este arquivo por causa desta política.
- A receita em `integration/psx-cas-r169/recipe/` altera uma chamada no
  `classes35.dex` e, na montagem, somente cinco das 13.861 entradas. As outras
  13.856 entradas e 39 partições DEX permanecem iguais à base. O recibo
  `final-apk-proof.json` é a prova de montagem, não a prova posterior de
  instalação, cadastro público ou partida real.
- A R169 é uma **montagem incremental do APK R168**, não uma compilação integral
  do aplicativo a partir apenas do Git. Fontes, binários de base, ferramenta
  privada e assinatura original são insumos distintos. Não diga que se pode
  reconstruir tudo em qualquer PC sem restaurá-los e testar a reprodução.
- O proprietário informou que N64 funciona e determinou foco em PSX. O teste
  PSX R169 ainda precisa de observações específicas de imagem, som, controles
  de ambos os jogadores e saída do anfitrião para ser chamado de homologado.

## 2. Proteger o que já está pronto

1. Preserve o APK assinado e a versão estável como artefatos imutáveis.
   Produza uma revisão sucessora somente quando o pedido exigir novo binário.
   Nunca sobrescreva o doador, o APK final, tags estáveis ou recibos aplicados.
2. Não recrie de memória, descompile para substituir, troque por equivalente,
   recompile ou remonte um núcleo, biblioteca, DEX, recurso, capa, BIOS,
   catálogo, manifesto, certificado ou chave só porque parece mais simples.
   Identidade de nome não prova equivalência de bytes ou comportamento.
3. Preserve N64, SNES e Mega Drive enquanto o pedido tratar de PSX ou de
   documentação. Preserve também GameCube/Wii, controles, saves, ROMs,
   licenças, sessão, downloads, pacote, assinatura e dados instalados, salvo
   quando o proprietário pedir uma mudança específica nessas partes.
4. Não altere CPU/JIT, renderer, resolução, taxa de quadros, shaders, efeitos,
   áudio, sincronização, rede, buffers, wakelocks, serviços, downloads ou
   ciclo de vida por iniciativa de "melhorar" ou "otimizar". Não deixe dois
   efeitos fazendo o mesmo trabalho, função duplicada, código experimental,
   feature incompleta, fallback não comprovado ou arquivo solto no produto.
5. Se um reparo depender de uma parte protegida fora do escopo, documente o
   nexo causal, a diferença mínima e o risco; peça autorização específica
   antes de modificar essa parte. Não amplie o escopo por conveniência.

## 3. Preservar capacidade real de reconstrução

1. Faça inventário dos insumos da revisão: código e histórico Git completos,
   APK doador exato, binários nativos, receitas e recibos, JDK/SDK/NDK e
   ferramentas com versões/hashes, autoridade de assinatura, certificado e
   credenciais privadas, além do APK final. Registre origem, tamanho e SHA-256.
2. Guarde segredo, chave, APK, ROM, BIOS, dados de licença e logs privados
   somente em armazenamento privado apropriado. Nunca os inclua em Git,
   handoff público ou saída de ferramenta. Faça cópia verificável e protegida
   da autoridade de assinatura; não gere outra chave para atualizar o app.
3. Verifique a cópia pelo conteúdo, teste a leitura do arquivo e, para Git,
   verifique o bundle/clone. Uma pasta parcialmente copiada ou um tar ainda
   gravando não é backup completo. Marque explicitamente arquivos parciais
   como inválidos e não os use para restauração.
4. Um backup do código do servidor não inclui automaticamente banco de dados,
   volumes, contas, licenças, certificados ou segredos de produção. Só declare
   "sistema inteiro restaurável em outro PC" após inventário de todos esses
   itens, restauração isolada e teste de reprodução. Sem isso, diga exatamente
   qual parte é reconstruível e qual depende de dados externos.
5. Faça saída nova fora do Git e conserve o insumo original. Use apenas espaço
   temporário próprio e conhecido; confira destino e hashes antes de limpar
   temporários. Nunca apague backup, trabalho de outra revisão ou dados do
   usuário para abrir espaço sem identificar com precisão o alvo.

## 4. Aplicar apenas a diferença autorizada

1. Congele a lista permitida de fontes, entradas ZIP/DEX e comportamento antes
   da edição. A alteração deve ser pequena, rastreável, reversível e ter uma
   causa testável. Se uma dependência nova aparecer, atualize a análise de
   escopo antes de escrever nela.
2. Use a receita da revisão corrente e os hashes nela fixados. Não execute
   finalizadores de revisões antigas nem substitua a receita por uma montagem
   genérica. Para R169, leia `integration/psx-cas-r169/README.md`,
   `recipe/patch_dex.py`, `recipe/package_candidate.py` e
   `recipe/sign_private.py`; a simples leitura desses arquivos não manda
   executá-los outra vez.
3. Confira diff de fonte e comparação integral de entradas do APK. Toda
   entrada fora da lista permitida deve conservar SHA-256; a contagem total,
   DEX preservados, Manifest, opções de motor, certificado, alinhamento e
   assinatura devem bater com o recibo. Uma diferença inesperada reprova o
   candidato; não ajuste o recibo para fazê-lo passar.
4. Não abra código de produção incompleto: nenhuma chamada para método ausente,
   módulo sem vínculo, função sem uso justificado, referência experimental,
   código comentado como solução, efeito paralelo ou recurso anunciado antes
   de estar integrado. Exija verificação de compilação, vínculo e execução
   pertinente ao delta; uma simulação não cobre comportamento Android real.
5. Um commit deve conter só o escopo revisado. Revise `git diff`, arquivos
   não rastreados e segredos antes de criar o commit. Não misture alterações
   de servidor, visual, motores e limpeza geral com o reparo solicitado.

## 5. Evitar regressões e aquecimento

1. Para cada mudança, compare consumo de CPU/GPU, memória, bateria, tráfego,
   trabalho por quadro e processos de fundo com a base quando esses caminhos
   forem afetados. Não acrescente polling, thread, timer, redraw, shader ou
   cache que continua ativo sem necessidade do requisito.
2. Mantenha limites e modos de economia existentes. Uma mudança em efeitos
   visuais deve demonstrar que só o efeito pretendido fica ativo e que a capa
   principal, controles e comportamento fora do escopo permanecem iguais.
3. Contadores estáticos como `newThreadsTimersOrPolling=false` e
   `extraPerFrameDrawCalls=0` ajudam a revisar o delta, mas **não provam**
   ausência de aquecimento. Para afirmar temperatura ou desempenho, meça em
   aparelhos reais sob condições comparáveis, com jogo, duração, carga,
   temperatura ambiente e versão registrados. Sem medição, registre pendência.
4. Se surgirem calor, travamento, queda de quadros, consumo anormal ou serviço
   órfão em teste, pare a promoção da revisão, capture evidência e isole a
   causa antes de propor mudança em motor ou política global.

## 6. Separar app, servidor e teste físico

1. Handoff ou commit de código do servidor não significa implantação. Para
   versão cujo `engineId` mudou, confira cadastro dos IDs exatos, vínculo por
   edição/modo, recibo `serverApplied=true` e consulta pública autenticada.
   Não recadastre revisão já aplicada nem altere servidor por uma mudança
   apenas visual que não tenha mudado o contrato de identidade.
2. Nunca aprove todos os jogos por nome, capa ou `metadata.players`. A decisão
   online exige motor existente no APK, formato compatível e perfil/modo
   comprovado para aquele item e número de jogadores. Uma sala em `playing`,
   HTTP 200 ou transporte sintético não prova gameplay Android.
3. Para instalar, use apenas APK assinado e conferido, preserve dados e não
   interrompa partida/download ativo. O instalador permanente deve apontar
   para a revisão comprovada; não reinstale aparelhos já conferidos sem motivo.
4. Registre por aparelho o hash do `base.apk` instalado. Para homologar uma
   partida online, observe primeiro quadro e som em ambos, controles
   independentes, saída do anfitrião e retorno do convidado. Separe relato
   humano, log, simulação e consulta do servidor; nenhum substitui o outro.
5. Não envie APK, chaves, credenciais, logs brutos ou dados de usuários ao Git
   ou ao servidor. O kit/handoff contém somente o necessário, com hashes e
   escopo explícito. Não publique, reinicie serviços ou mude produção por
   consequência automática de um commit do app.

## 7. Encerrar e entregar

1. Confira que fonte, receita, APK, hashes e recibos se referem à mesma
   revisão. Confirme que entradas fora do escopo ficaram idênticas e que não
   há arquivos temporários próprios misturados no commit ou artefato final.
2. Informe claramente o que mudou, o que foi testado, o que foi observado em
   telefone, o que só foi verificado em código/servidor e o que falta. Não
   promova candidato a estável por build, instalação, HTTP ou relato vago.
3. Mantenha referência de retorno válida e backup verificado antes de qualquer
   distribuição ampla. Se faltar doador, ferramenta, autoridade de assinatura,
   espaço, recibo ou teste essencial, declare a dependência concreta e siga
   somente com trabalho independente seguro. Não invente peça ausente.

Esta política é instrução de processo. Ela reduz mudanças acidentais e deixa
diferenças auditáveis; não substitui revisão, teste físico, controle de acesso
nem garantia técnica de segurança ou temperatura.
