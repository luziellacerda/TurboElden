# R69 — Todos os jogos arredondado e novos vídeos de coleções

## Pedido final confirmado

Na página de coleções de qualquer sistema, somente a célula **Todos os jogos** conserva os cantos arredondados. As coleções ficam quadradas, inclusive quando selecionadas e ampliadas. Não é uma regra para a célula em destaque: a identidade do item determina o formato. O carrossel principal de plataformas e as capas individuais de jogos conservam seus formatos.

A R69 sucede a R68, que havia deixado todas as células das coleções quadradas antes desta nova confirmação. Não restaurar a interpretação anterior nem aplicar o raio pelo cursor ou pela posição visível zero.

## Implementação nativa

`native_folders.h` herdado identifica Todos os jogos como `FolderMeta.kind == 2`; pastas reais usam 0 e grupos de jogos diretos usam 1. `native_formation.h::collectionAllGames` consulta esse campo pelo índice original, com validação dos limites. `CoverRect.allGames` acompanha cada célula desenhada. Pesquisa e ordenação podem mudar a posição visível sem mudar essa identidade.

`collection_corner_policy.h` aplica raio de 11,5% da menor dimensão somente às plataformas principais ou ao item Todos os jogos. Imagem, preenchimento de preparação, poster/frame, vídeo e área de toque recebem a mesma flag. O placeholder chamado por `native_skin.h` passa pelo mesmo `roundedCoverFill`. Não há dependência da seleção, listas de plataformas ou alteração das dimensões, UVs, faixa INSTALADO e ações.

## Atualização dos vídeos

| Coleção SNES | Arquivo fornecido | Mudança |
|---|---|---|
| Final Fight | `final figth coleção.mp4` | Novo |
| Mega Man | `mega man coleção.mp4` | Novo; áudio removido |
| Top Gear | `top gear coleção.mp4` | Substitui o vídeo anterior |

Origem: `G:\TURBORAMA\RetroBat\emulationstation\.emulationstation\themes\TURBORAMAx\_theme_inc\images\caratulas\Sele;'ao`. `mapping.json` contém hashes completos e destinos. Os oito outros arquivos desse diretório correspondem aos originais já usados na R67. Os vínculos exatos das três coleções foram conferidos no TSV usado pela R67; a evidência registra commit, hash e contagens daquele snapshot, sem alegar uma consulta nova ao servidor em produção.

Saída H.264 baseline, 720 × 720, 30 fps, sem áudio, duração/velocidade preservadas e sem corte ou distorção. Os originais são quadrados e têm 24 fps; a conversão para 30 fps repete quadros, sem acelerar a animação. Os posters são o primeiro frame dos vídeos efetivamente empacotados, não fotografias alternativas. Somente a célula selecionada mantém decoder; laterais usam frames retidos/posters. Loop e política de 30 fps do menu permanecem.

## Fonte, build e preservação

Base exata: R68, APK SHA-256 `72ce7c2cbb3d7cf14ad122b0b98e42a41563114bbbc5c925caedbdee49ff66c3`.

Este snapshot é um overlay de cinco headers sobre a árvore completa R68. `recipes/build_r69.py` valida todos os hashes da base, copia suas fontes e objetos, aplica somente os cinco headers e acrescenta o objeto dos três posters R69. O objeto R67 permanece no link. `evidence/build.json` registra comando, fontes, dependências e hashes finais.

Build: `E:\ESTUDO APK\work\station-collection-media-r69-20261007-final`.

APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R69-20261007.apk`.

`recipes/package_r69.py` substitui somente a biblioteca do carrossel e Top Gear e adiciona os dois vídeos novos. Compara integralmente todas as outras entradas, conserva assinatura/alinhamento 16 KiB e registra hashes em `evidence/package.json`. Todos os DEX, motores, controles, segurança, BIOS automática e runtime online permanecem iguais à R68. Não publicar APK, vídeos privados, objetos, segredos ou capturas pessoais.

Para reproduzir, restaure os pré-requisitos R67/R68 pelos respectivos manifestos, execute a receita de build em uma pasta E: nova e configure privadamente as quatro variáveis STATION_KEYSTORE, STATION_KEY_ALIAS, STATION_KS_PASS e STATION_KEY_PASS com a assinatura original. Em seguida execute a receita de empacotamento com saída G: nova. As receitas recusam sobrescrever saídas.

## Verificações e limites

66 verificações da política de cantos, incluindo listas reordenadas/filtradas, nove ligações de desenho/toque, regressão de um decoder e rotas de 13 definições de coleções. Os três vídeos são decodificados integralmente e seus formatos/durações conferidos. Compilação Android ARM64, assinatura e comparação integral do pacote completam as verificações locais. Os recibos de instalação registram separadamente o que foi observado no aparelho.

Atualizar por `adb install --no-incremental -r --user 0`; nunca desinstalar, limpar dados ou trocar assinatura. `recipes/install_verified.py`, derivada da receita R67, exige base exata R68 e ausência de Activity de emulação ativa, e confere hash integral/UID/data original após atualizar. A versão R69 conserva o erro retornado pelo Android em um arquivo local se a instalação falhar; esse arquivo não integra a publicação Git.

Retomada online continua pendente de implementação coordenada APP/runtime/SERVIDOR. Esta entrega não altera chamadas, contrato ou serviço Linux; o pedido REC-01 a REC-09 da R67 permanece válido. Conciliar este overlay visual ao gerar futuras versões.

## Instalação no Samsung A56

R69 instalada em 07/10/2026 às 19:53:44 UTC, SHA-256 `901e5eb495a858fc6877f7a22e325b5fcb3b73807af8c6d2888c90f1425773e4` conferido integralmente no telefone. 2.119.264.138 bytes; 13.220 entradas anteriores preservadas, dois vídeos adicionados e Top Gear substituído; total de 57 vídeos. Mesmo UID, data original e assinatura, sem limpeza, desinstalação ou alterações de configurações. Primeira tentativa falhou sem motivo capturado; a segunda concluiu. ESActivity abriu com a sessão existente. Plataformas e lista de jogos observadas; os cantos de uma coleção selecionada e a reprodução dos três vídeos novos ainda precisam de conferência visual. Capturas locais privadas não publicadas. Recibo `evidence/installation-samsung.json`.

Conferência posterior: no SNES, Todos os jogos arredondado e coleção Super Mario selecionada com cantos retos; miniaturas novas de Final Fight/Mega Man/Top Gear observadas. A captura nomeada screen-finalfight-focus mostra Super Mario porque a navegação mudou durante a conferência; não alegar outra seleção. Em seguida o mantenedor pediu salvar esta revisão como estável do menu/consumo. Tag `estavel-menu30fps-colecoes-r69-20261007`: registra o limite de renderização e um decoder já integrados, sem prova de redução térmica percentual. Bug posterior de seleção do último jogo, novo reposicionamento de configurações e novos vídeos serão tratados na R70; retomada online continua pendente.
