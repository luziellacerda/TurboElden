# Revisao do owner original e coordenacao PSX

## Escopo e resultado

Fontes atuais unicas em `integration/psx-online`. O adaptador usa o LibretroPlayer normal e seu core PCSX normal, com hooks opt-in no processo privado. Os arquivos originais offline permanecem intactos. A revisao nao instalou APK, iniciou jogo, operou telefone ou alterou servidor.

Provas isoladas finais: 80 verificacoes ELF/ABI, 16.090 verificacoes de owner/protocolo com 513 retornos simulados de `retro_run`, 61 verificacoes JVM do Session/Launch, 186 de endpoint PSX e 470 de regressao Dolphin/TCP. Compilacao standalone ARM64/API28 do adaptador concluida. Os recibos respectivos registram hashes e limites. A biblioteca standalone nao substitui a biblioteca Entry/JNI integrada, cujo recibo e separado.

## Correcoes verificadas na coordenacao

- RendererReady e CoreReady sao preparacao. READY/resume exigem CPU ACK real do epoch e serial atuais, estado inicial aplicado, drain, core carregado e ausencia de frame em curso, aplicacao de estado, fechamento, falha ou pausa local.
- Controle e decisao de resume ficam serializados. A prova concorrente impede publicar uma permissao nova no meio da decisao sobre um snapshot anterior.
- CUE exige `cue-set-v1` e rehash de todos os tracks no consumo do descriptor; CHD/PBP usam hash do arquivo. Mutacao entre preparo e consumo, extensao divergente e CUE legado plano sao recusados. Outros motores e a identidade global de conteudo nao mudam.
- API28 e exigida antes da preparacao nativa PSX. O modo normal nao recebe essa restricao.
- Apenas nomes Player1Controller/Player2Controller e bool LibretroStretch verdadeiro/falso sao copiados das preferencias normais para o home privado. Preferencias normais permanecem byte identicas; core/options/saves nao sao copiados.
- Mensagens Session/Launch usam escapes Unicode deterministas em fontes ASCII. Nao ha texto com codificacao corrompida.

## Saida humana e limpeza real

Abrir a confirmacao, cancelar, sair de foco, desconectar, receber falha do owner ou exceder espera nao concede autoridade humana. Somente o botao positivo autoriza a saida nativa e comunica o resultado.

`awaitClosed` e uma extensao opt-in usada apenas pela limpeza PSX apos essa confirmacao. O close normal e o protocolo dos demais motores permanecem preservados. A limpeza aguarda threads input/output, executores e leitores e escritor WebSocket reais; fecha o Socket real da sessao humana se uma conexao tardia/graciosa ainda o mantiver aberto. `isClosed` do WebSocket sozinho nao e prova de encerramento. Registro cuja `connect` falha antes de iniciar a thread e removido; apos fechamento nenhum novo leitor e registrado. O campo privado writeThread pertence ao cliente shaded empacotado, nao a API escondida do Android; se mudar, a limpeza e recusada com seguranca. Um timeout deixa a limpeza incompleta e permite tentar novamente, sem matar o owner.

O Binder fecha na UI e sinaliza a conclusao efetiva. Somente depois de IO/Binder encerrados Session marca `humanCleanupComplete`. Activity ainda deve confirmar que a thread SDL original terminou e que o processo e o privado PSX exato antes de finalizar/retirar esse PID. `mSDLThread == null` sozinho nao serve como prova. A prova Activity/Entry e registrada separadamente em `human-exit-gate.json`.

## Limites

As fixtures JVM substituem Android/JNI/Binder/metadata assinada; nao comprovam criptografia, JSON real, Android ou servidor. O probe C++ usa SDL/core simulados e nao demonstra gameplay, desempenho, temperatura ou controle Bluetooth fisico. A analise ELF fixa enderecos/ABI, sem executar o owner Android. Compatibilidade real de serialize antes do primeiro quadro e os decoders internos do core continuam sujeitos a verificacao no aparelho; validacao do tamanho/hash externo nao prova seguranca de todos os campos internos.

Nao ha declaracao de estabilidade, ativacao do registro do servidor ou partida em dupla aprovada nestes recibos.
