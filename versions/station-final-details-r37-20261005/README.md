## Instalação em 06/10/2026

R37 instalada no Samsung A56 por atualização; SHA integral do APK no aparelho igual a 75fd8b5806c6aa683796e1301fa8a92e3236f106a8837a0279b6d0ae094999fc. Sem desinstalar ou limpar dados. Recibo em evidence/installation-samsung-20261006.json. A ausência de USB descrita no histórico abaixo foi resolvida. Conferência visual, quando registrada, está no recibo separado; não significa teste de partida online. Configuração temporária de tela ligada restaurada ao valor original e conferida.

# R37 — perfil do servidor, sinopses completas e acabamento visual

## Entrega e estado real

APK `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Visual-R37-20261005.apk`, SHA-256 `75fd8b5806c6aa683796e1301fa8a92e3236f106a8837a0279b6d0ae094999fc`, 2.054.631.976 bytes. Pacote `org.turboramastation.frontend`, mesma assinatura original. Compilado, testado no PC e conferido por entrada. **R37 não instalado nesta entrega: telefone deixou de aparecer na USB. R36 é a última instalação Samsung comprovada.** Não declarar nome real no aparelho, estética aprovada ou partida online validados.

Fontes canônicas: `E:\ESTUDO APK\work\station-final-details-r37-20261005`. `native/` contém overlay final do carrossel, `frontend/` a ponte recompilada, `data/` o índice completo/proveniência, `tests/` e `evidence/` as conferências. Não houve correção exclusiva no telefone.

## Pedidos incluídos

- Nome do jogo e valores da linha com fonte50% maior queR36: escala1,05→1,575, preservando a fonte comum anterior. Nome → pasta/contagem → jogadores → estrelas. **Cinco espaços reais** entre grupos, medidos com a fonte nativa; um espaço entre ícone e valor. Linha7,6% da altura e avanço9,3%; nome recebe reticências se necessário. Ícones compactam apenas em telas estreitas para manter a linha sem sobreposição; fonte não diminui. Sinopse completa continua recortada e rolável.
- Faixa INSTALADO com oito gradientes verdes, chanfros, dobras em planos, sombra de contato, reflexo oblíquo de3,6s e brilho na borda. Mesmo canto/diagonal/condição instalado. Uma chamada de geometria mais texto, máximo274v, buffer448; sem thread/timer/vídeo adicional. Preview local usa vértices reais e fonte aproximada, não é captura Android.
- Nome do comprador ligado ao perfil autenticado do servidor, em vez do perfil local antigo.
- **2.212 sinopses do catálogo publicado revisão14, zero vazios e placeholders.** Há2.168 descrições publicadas preservadas,27 recuperadas pelo XML NeoGeo exato e17 editoriais originais em português, pesquisadas/documentadas. Inclui Battletoads in Battlemaniacs. Proveniência por ID em data/synopses-complete.json e fontes web em data/synopses-editorial.json. Descrições existentes não foram individualmente verificadas/traduzidas. Não inventar cobertura de IDs futuros.
- R36 preservada: nome da plataforma dentro do botão, abreviações quando necessárias, BR mantido, sem duplicata ao lado; cinco botões secundários iguais e primeiro com largura da capa.

## Causa e correção do nome

Contrato já existente: GET `/v1/station/me`, envelope assinado `TurboRamaStationAndroid/profile/v1`, campos `displayName`/`profileVersion`. Java valida/cacheia e publica pela JNI `StationFrontend.publishCatalog`. Antes, a ponte apenas guardava inbox.name sem consumidor. GuiStore lia `LocalProfile::getName`/profile.json e mostrava JOGADOR. Arquivo station-display-name.txt gravado peloJava não é lido pela libmain exata. Não foi necessário endpoint ou DEX novo.

`frontend/station_profile_state.hpp`: revisão atômica e cópia sobmutex; publica primeira revisão e incrementa só quando nome muda; vazio limpa e republicação idêntica não muda. `station_profile_bridge.h` exporta `StationProfile_nameRevision` e `StationProfile_copyName`; buffer insuficiente falha sem cópia parcial. Carrossel `native_profile_name.h` consome esses símbolos via dlsym e aplica ao TextComponent existente apontado por gui+0x1468. Buffer1025 cobre limiteJNI; cache considera revisão/componente/tela/modo/geometria; refresh legado não volta a exibir JOGADOR. Nome longo usa fonte real e reticênciasUTF-8. Nenhuma rede, arquivo privado, log de nome ou chamadaJava porquadro. Offline usa a publicação do cache autenticado já existente. Ausência real de nome continua JOGADOR. A presença de nome válido na licença atual ainda requer conferência no aparelho.

ABIauditada libmainSHA62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6: layoutTopButtons0x214d78, setTextperfil0x215010, ponteirogui+0x1468. Não grava LocalProfile::setName, cujo limitelegado20caracteres não atende o contrato.

## Cobertura das sinopses e precedência

Catálogo público commitServidor-pix100e4bbd92aa4c85cda10a633e6463fbb24ae8ab, arquivo docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv, SHA3dae0cfa3877fba31b9a347b58795fe0df95333aea628b9ea8be597b7ccfed6e. Recorte: SNES644, SNESBR191, Mega887, MegaBR94, N64157, NeoGeo189, NeoGeoCD50. Não foi nova consultaHTTP viva.

Antes havia43vazios eOldTowers com apenas o título. XMLNeoGeo `G:\TURBORAMA\RetroBat\roms\neogeo\gamelist.xml`, SHA555672bfb311bcef62a5f5409e81a199b37e32eb082f2b04c5a1619bbcbe5463; vínculo por station_+SHA256('neogeo:'+pathPosix)[:32]. Os17editoriais usam identidades explícitas, não fuzzy por nome. Sands of Time é descrito como hack identificado no catálogo, não renomeado para Ocarina pelo nomeZIP. Tetris não recebe edição/ano não comprovados.

`native/station_game_infos.h` prevalece sobre headerantigoW16 noinclude. Lookupbinário ID+plataforma é preservado. Descrição servidor não vazia permanece prioritária; apenas IDab9773189dbfc1571ca0d56adb13ff32 com textoexato'Old Towers' usa oeditorial. Se servidor corrigir o texto, volta aprioridade normal. Native_info liga stationSynopsisNeedsOverride antes da escolha. Nome integral/catálogo/rotas inalterados.

Cache do catálogo no aparelho: `/data/user/0/org.turboramastation.frontend/no_backup/station-v2/catalog/<owner>.json`; ownerderivaidentidadelicença/aparelho. Não coletar nem expor tokens para validar a contagem.

## Preservação, testes e reconstrução

BaseR36SHA dfe9dd4ce24fdca80986919e885b0a09d146f29dd8ab156f0dffdf18d2a46f57. Apenas2entradas mudam: libturbo_carousel.so e libstation_frontend.so.13.085 entradas preservadas, todosDEX/manifesto/motores/recursos/classes35R34. Bibliotecas: carrossel beaa00d317ddaa5237c169eb5dff421f3d995ca77d70c0157549bf63a21c77d2; frontend d3bc8ef6fcd88a5cf16b577fdba83e5242a75f1d946a17019075ab56a9fe95ad. Assinatura original e16KiB conferidos.

Passaram:12.712 checksUI;20testesPython/13.284 checksC++ de sinopses comlookupreal;21checksperfil e16.237 leituras concorrentes durante20mil alterações/20mil republicações;13.253.767 verificações de malha/ribbon;8contratosdeintegração. Todas exportaçõesfrontend anteriores preservadas e apenas2novas. Testes não significam gameplay2Android nem aceite visual.

`python recipes/restore_r37.py E:\NOVO_DIRETORIO` restaura R36+JavaR34+overlayR37+pontefrontend e confere todoshashes. Diretório precisa sernovo. Para compilar, copiarrecipes/testes/evidence para raizW37 e ajustar somentecaminhosdocumentados no native-build-input; executar frontend/build_frontend.py, build_r37.py e package_r37.py. Frontendbuilder valida delta contra fonteR16 em work/station-native-rate-phase-20261005/client/src/native/station_frontend.cpp (cópiaexata tambémversionadastation-performance-offline-r16); essa referência e SOoriginalW16 são guardasdo build. Não usarJavaonline recebido como base implícita.

Dependênciascarrossel: W16frontend-native(headers/stubs/video720_posters.o) eW22neogeo_previews.o uma vez; NDKr28c/Android26/LLVM/JDK17/build-tools35. APKbase/objetos/keystore ficamforaGit; comandos/hashesevidenciados. Regenerador de sinopses lê o TSV fixado, os XMLs NeoGeo/SNES e o JSON editorial, conferindo SHA de cada entrada. Os caminhos padrão estão na receita; use --help para parâmetros. O JSON completo é também o resultado versionado, não uma consulta automática ao servidor. Não reexecutarpreparaçõeshistóricas.

## Online, servidor e próxima conferência

Retorno recebido a626b50a61c8ac1a82a2a5390bbf1a74f848dbe1 em docs/server/RETORNO-SEGUNDO-JOGADOR-SALAS-STATION-20261005.md foi lido e preservadonoGit, **não aplicado aoR37**, conforme pedido de aguardar nestaetapa. Prepara açãoEntrarnasala/leave→join; não corrigeoverlay nem comprova2Android. Classes35 continua0db040a6b3406e744053c63467ed0f26e3582928ef5b84ecb9e360603ce870f6. Downloads11be7f3 continuamfora. Servidor nãoalterado.

Ao reconectar, conferir estado/partida e instalar com adb install --no-incremental -r --user 0, semdesinstalar/limpar. Confirmar hash, perfilreal/nomelongo/offline, Battletoads/Neo/N64/OldTowers, cincoespaços e nome50%maior, brilhoemmovimento, botãojáR36/retorno. Preservar jogos/saves/licença. Novo catálogo maior precisa descriçõespublicadasouregeneração deíndice; nunca anunciar cobertura40mil pelos2.212testados.
