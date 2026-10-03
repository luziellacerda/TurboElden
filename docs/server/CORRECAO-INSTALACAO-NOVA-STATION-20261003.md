> Fechamento posterior: também conferida abertura Mega Drive às17:28:33 e retorno sem login confirmado pelo mantenedor. Entrega promovida como estável limitada a SNES/Mega. Consulte [handoff completo](HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md); o recorte abaixo é a sequência de diagnóstico.

# Instalação nova Station — correção do aplicativo em 03/10/2026

## Estado atual e destinatários

Para a manutenção do **TurboStations TESTE** e a equipe do **Servidor-pix**. Esta atualização substitui o bloqueio de ativação registrado às 16:19 no handoff anterior. **Login, catálogo, capas, dois downloads/instalações, abertura de SNES e retorno à biblioteca foram confirmados no aparelho.** Os dois jogos continuaram instalados após encerrar e reabrir o aplicativo. A falha do botão Baixar foi localizada no cliente e corrigida no fonte/APK. Essa amostra não homologa todos os jogos e emuladores; não promover globalmente a estável.

Ramo do aplicativo: `integracao-station-producao-20261003`, derivado de `2834e3b101ce4e957414bccd13154c8a70af2f01`. Este trabalho altera o cliente; não altera nem reinicia o servidor.

## APK e pastas exatas

- Fonte canônico: `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`.
- Espelho versionado: `versions/station-reconstruction-20261002/` deste Git.
- APK: `E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build\apk\TurboStations-Station-CANDIDATO-20261003.apk`.
- SHA256: `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`.
- Tamanho: 1.902.768.022 bytes. Pacote `org.turboramastation.frontend`, versionCode 11, versionName `1.0.8-turboeden-unico`.
- `clientVersion`: `1.0.8-station-storage-20261003.3`.
- Assinatura SHA256: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
- Instalação por atualização, sem apagar dados: `lastUpdateTime` 03/10/2026 17:20:39; hash do APK instalado conferido. `firstInstallTime` 16:17:03 permaneceu.
- APK anterior imediato preservado em `build/previous-22b2f05b-space-fix-20261003/TurboStations-Station-ANTERIOR-22b2f05b.apk`; revisão anterior fa3bc844 em `build/previous-fa3bc844-storage-fix-20261003/TurboStations-Station-ANTERIOR-fa3bc844.apk`.

Apenas `classes5.dex` e `classes28.dex` mudaram em relação ao APK anterior `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795`. Manifesto, identidade, design, mídia e motores foram preservados. A verificação do empacotamento também conferiu 10.803 entradas preservadas da base original e ausência de classes novas duplicadas.

## Falhas comprovadas e correções incluídas no APK

1. A pasta real `/storage/emulated/0/EmulationStation/roms` não existia. `StationFrontend.configure()` chamava `toRealPath()` antes de criá-la, gerando `NoSuchFileException` e impedindo publicar o catálogo. `StationStorage` agora prepara a raiz fornecida pelo aplicativo, resolve aliases do Android, cria os descendentes necessários, confere escrita e trata conflito/permissão. Os controles contra redirecionamento por links em arquivos de jogo permanecem.
2. Preparação de tema e configurações de emuladores podia ocorrer antes da permissão de armazenamento, com `AccessDeniedException`. O login agora solicita e aguarda essa permissão antes de iniciar a tela nativa; a volta das configurações tenta prosseguir com a sessão válida. O caso de permissão já concedida passou no aparelho. O fluxo visual de negar/conceder novamente ainda está pendente.
3. O instalador anterior procurava `assets/packs/Dolphin.zip`, inexistente no APK, embora o Dolphin incorporado já seja de outra integração. A implementação atual instala os recursos efetivamente empacotados. Não reinstala o motor antigo.
4. O marcador de versão não basta para considerar a preparação concluída: a nova rotina também repara recursos ausentes ou vazios. BIOS existentes não vazias e arquivos adicionados pelo usuário são preservados. Recursos fornecidos pelo APK são atualizados quando sua versão muda. Gravações usam arquivos temporários e substituição final.
5. Uma falha ao preparar armazenamento permite nova tentativa ao voltar ao aplicativo ou atualizar o catálogo. Não deixa o gerenciador de downloads permanentemente sem inicialização.
6. Após a reconexão, o registro de 17:10:15 mostrou `AUTHORIZE HTTP200` (correlação `a56c46dbb0184320b47193f623ac2e45`), seguido de `INSTALL_FAILED status=0` antes de qualquer GET do artefato. A reprodução isolada no mesmo Android confirmou `java.lang.SecurityException: getFileStore` em `Files.getFileStore(...).getUsableSpace()`, tanto no armazenamento compartilhado quanto no interno. `File.getUsableSpace()` mediu 16.409.522.176 bytes disponíveis. As duas ocorrências (fila de download e instalador) foram substituídas por `StationStorage.usableBytes`, usando a consulta compatível com Android e mantendo as reservas de espaço e a validação do diretório. É uma falha do cliente comprovada; não requer mudança no servidor.

**Regra permanente do mantenedor:** toda preparação necessária deve constar no fonte e no APK, funcionar novamente após reinstalação e preservar arquivos existentes. Não criar pastas, copiar BIOS/recursos nem ajustar configurações manualmente no diretório real do telefone para mascarar uma falha. Essa regra está nos `AGENTS.md`.

## Evidência observada no telefone

Horários locais UTC−03:00 de 03/10/2026:

- 16:52:43–44, antes deste APK: ativação HTTP200. A recusa HTTP403 das 16:19 é histórica; não é mais o bloqueio atual.
- 17:09:23–24, APK atual: sessão, perfil e catálogo HTTP200; `CATALOG_NETWORK count=1816`.
- 17:09:30: `Storage root prepared`, `UNSUPPORTED_PLATFORM count=0`, `CATALOG_PUBLISHED count=1816`, catálogo recebido e aplicado pelo nativo.
- Recursos: `Packaged resources ready: restored=199 bios=0`. Foram restaurados os recursos do APK; as BIOS já presentes foram preservadas. Não comprova o funcionamento de todos os emuladores.
- A própria aplicação criou `roms` e `roms/.station-v2/staging`. Nenhuma criação manual de diretório real ou cópia manual de recurso foi feita.
- 17:09:39: capa HTTP200, revisão 3, correlação `32d5985f366c4db097917ebae9f21000`. Tags SHA256: item `8aacde0a1c31dc997b24907ab39fc171ce4e69760f475f16bbf31ebffd2e6fc8`, capa `e9f9d990b15c1dffd1b2a1ddad540bfd1666f2776417b3832aab05701ae7da78`.
- Captura conferida: catálogo SNES, `1 DE 644`, capa de Battletoads in Battlemaniacs visível e botão Baixar. Isso não comprova download nem emulação.
- Durante a primeira tentativa de Baixar, a USB desconectou. Após reconectar, os registros preservados permitiram comprovar autorização200 seguida de falha local e reproduzir a chamada incompatível de espaço livre; ver item6 acima.
- 17:20:57–17:21:05, APK final 3b355b02: sessão/perfil/catálogo200 e publicação dos1.816 itens.
- 17:21:11–12: Battletoads, autorização200 (correlação `d55b3d11a91c440cb16d82a3dc2f9040`), artefato200 (`96068ccaac1f42b2b6401b3090722491`), `INSTALL_FINISHED count=1719028`. ZIP670.452 bytes, conteúdo1.048.576 bytes, um arquivo. A soma é trabalho de download+preparação, não tamanho do ZIP.
- 17:21:15: SNES iniciou a ROM; captura do jogo com apresentação Rare e controles visíveis conferida. O mantenedor saiu pelo menu e o catálogo voltou sem novo login.
- 17:21:43–44: Cutthroat Island, autorização200 (`e88520d765cf40548390a7d26e55c912`), artefato200 (`facb2b4f378a414292c8910845b689d3`), `INSTALL_FINISHED count=2982488`. ZIP885.336 bytes, conteúdo2.097.152 bytes, um arquivo. A instalação e o botão Jogar foram conferidos; não usar esta prova para alegar execução do Mega Drive nesta rodada.
- Os dois manifestos de instalação foram lidos. Hashes dos artefatos assinados: Battletoads `cd3a1292fdb5953ca414dd6a74ac0aa1886b2d132fce4c804e79d5e25ea029f6`; Cutthroat `5c18e99d2ec819ea207e0d5cef1513c1845c8417121022c047d216d4ef140124`. O código só publica `INSTALL_FINISHED` após conferir tamanho/hash e concluir a extração/recibo.
- 17:22:56–58: processo novo, sessão/catálogo200, 1.816 itens republicados. Tela reaberta confirmou `INSTALADOS (2)`, Battletoads `INSTALADO` e botão `JOGAR`. Não houve novo download para recuperar o estado.

As imagens locais incluem `temp/storage-fixed-start.png`, `temp/fresh-install-folder-error.png`, `temp/space-fix-games.png` (jogo aberto), `temp/space-fix-return.png` e `temp/space-fix-installed-persist.png`; não foram publicadas no Git. Credenciais, licença e tokens não foram copiados para a documentação.

## Testes e limites

- 327 verificações Java locais aprovadas, incluindo 25 de preparação de instalação nova; compilação para Android API34/Java8 aprovada.
- 10 verificações Android de raiz de armazenamento aprovadas em pasta temporária isolada, incluindo espaço livre, pasta ausente, preservação de arquivo, recusa de link, permissão negada e nova tentativa após restaurá-la.
- Os testes locais de download usam dados sintéticos assinados; não equivalem a uma transferência de produção no aparelho.
- Não foi desinstalado nem limpo o aplicativo principal. Licença e chave do aparelho preservadas na atualização.
- Houve comprovação atual de SNES aberto/retorno e persistência dos dois jogos. Não houve teste completo de todos os emuladores após instalação nova nem teste visual de negar/conceder a permissão no login.
- O catálogo chama Battletoads de USA, mas o descritor assinado aponta para `Battletoads in Battlemaniacs (ESP) (NTSC).smc`, que foi extraído exatamente assim. A apresentação em espanhol condiz com esse conteúdo. Se o operador quiser corrigir a edição/idioma, precisa revisar catálogo/arquivo/descritor no servidor; o cliente não deve renomear ou inventar outro launchPath.

## Continuidade e encerramento desta correção

1. O fluxo Baixar → instalar → Jogar → retornar foi conferido para SNES; persistência após reabertura também. O aplicativo foi deixado nas plataformas.
2. Para eventual nova falha, localizar a primeira etapa: autorização, cabeçalhos/bytes, hash, extração, recibo ou launcher. O cliente usa `/v1/station/downloads/authorize` por itemId e `/v1/station/artifacts/{grantId}`, mantendo a mesma sessão até consumir o grant. Não voltar a endpoints de catálogo/CDN antigos.
3. O instalador grava em `roms/.station-v2/<plataforma>/<itemId>/install-*/content/<launchPath>`, com recibo privado. Não inventar extensões nem mover arquivos manualmente para fazê-lo funcionar.
4. Permanecem limites gerais de4096 itens/12MiB sem paginação, quatro plataformas de jogos efetivamente publicadas no acervo atual e rotinas nativas legadas residuais documentadas na revisão anterior. Esta correção não declara suporte a15mil jogos nem eliminação integral de todo código legado.
5. `stay_on_while_plugged_in` restaurado ao valor anterior0 e conferido. Removidos somente `root-test.jar`, `space-probe.jar`, a pasta temporária própria vazia e `/data/local/tmp/station-folder-download.xml`. Nenhum jogo, save, licença ou chave foi removido.

Não há pedido de implantação ao servidor neste registro. A autoridade consultada continua [o retorno b1511b9](https://github.com/luziellacerda/Servidor-pix/blob/b1511b9f75815aceb78dea801bb7ccc29f1036ab/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md). Um eventual pedido ao servidor deve levar a operação, horário, correlação e resposta reais da tentativa que falhar.
