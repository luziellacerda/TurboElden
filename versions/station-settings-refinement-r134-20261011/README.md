# R134 — configurações organizadas e navegação Sony

<!-- R134_RESULT_START -->
Compilada, assinada, conferida e instalada no Edge 30 e Samsung A56 com dados preservados; ver os recibos em [handoff completo](../../docs/handoff-completo-r134-20261011/README.md). Fonte `4f9039eb9ce13907ce043870bfe1f6e294888556`; APK SHA `f8cb09184f41bc7c942ce84541dbd90d575b7240467ce0033d35be65e57caee2`, 2.714.991.631 bytes. Assinatura original v2/v3 e alinhamento16KiB. Ativação do servidor, controles, gameplay e térmica permanecem sem validação nesta documentação.
<!-- R134_RESULT_END -->

A candidata de fontes `e85a1a11b281ca57e1df771f15abfb797238efc2` foi retirada antes da instalação. A revisão independente encontrou um callback das configurações PS4 que podia submeter trabalho depois da destruição da tela. A fonte definitiva invalida esse retorno antes do fechamento do worker e preserva a gravação humana já enfileirada; a candidata retirada não representa o instalador atual.

## Alterações específicas

O painel de efeitos recebe páginas por grupo. Os botões PS3/PS4 do menu nativo passam a indicar **Configurações**; a correção desses dois textos mantém o tamanho e admite inversão exata. As telas Sony usam categorias compactas e **Voltar** persistente, incluindo o preparo inicial.

PS3 apresenta 18 campos reais do `config.yml` do motor: 16 editáveis e dois somente para leitura, além da preferência de controles de toque. A gravação usa o JNI original e arquivo atômico. Renderizador e modo de shaders ficam para leitura porque os nomes do enum publicado no XML divergem do padrão do binário oficial 2.43; nenhum valor foi convertido por inferência.

PS4 apresenta 11 campos do JSON nativo: oito editáveis e três somente para leitura, além de controles de toque. O pacote oficial 0.2.4 contém o catálogo de chaves e o writer correspondente; o código do motor confirma a leitura de `HOME/.local/share/shadPS4/config.json`. HOME/XDG são vinculados antes do carregamento das bibliotecas, no mesmo armazenamento privado usado pelo lançamento. Abrir a tela não cria arquivo de configuração nem regrava padrões. Somente uma ação humana grava a opção selecionada, preservando as demais seções/chaves. Backend de áudio, limites sem faixa comprovada e drivers não recebem controles inventados.

Ambas as telas concluem as gravações já enfileiradas antes de voltar. O [contrato das fontes Sony](../../integration/settings-refinement-r134/evidence/sony-settings-contract.json) registra as chaves, os consumidores reais e os hashes das fontes primárias. Ele comprova análise estática; a leitura da configuração por um jogo físico não foi validada.

## Composição e preservação

Composição final conferida: sete substituições e zero adições, com 13.853 entradas preservadas. DEX28 altera somente a família `StationGraphicsPanel`; DEX40 somente `Ps3Activity`/`Ps4Activity` e suas classes internas. Os outros 38 DEX e as classes fora dessas famílias foram conferidos e permanecem idênticos. O carousel admite somente dois textos de mesmo tamanho, com todo o restante invertido para o hash R133 original. Os três marcadores e `engines.json` vinculam os quatro motores ao novo bundle.

Assets Sony, firmware/importador, JNI/core, biblioteca frontend, fotos, vídeos/loop, LEDs, cache/loading, economia e opções dos outros emuladores permanecem preservados. Ajustes de configuração Sony só ocorrem após decisão humana. Não houve novo loop de animação, timer ou polling nas telas. Isso não comprova menor consumo, temperatura, latência ou estabilidade.

## Online e entrega única

A matriz integral permanece com 3.940 entradas, 3.685 visíveis e 255 aliases. O ledger final preparou 78 modos em 44 jogos, vinculados aos quatro IDs R134 atuais e preservando os 5.176 perfis e 321 modos originais. N64 tem 66 modos em 33 jogos; GameCube, nove em oito; Wii, três em três; PSX, zero nova aprovação. Esse preparo não confirma publicação ou ativação do servidor. PSX mantém 84 edições HLE pendentes e zero nova aprovação; dez dos 26 históricos multiplayer têm fontes primárias, 16 ainda carecem de fonte primária legível nesta janela. Os bloqueios específicos e os jogos individuais continuam explícitos na [matriz](../../audits/station-r134-online-mode-completion-20261011/summary.json). PS3/PS4 permanecem exclusivamente offline; fotografia PSP não cria engine online.

O último retorno real servidor `a6b58e9beb12eb564c1b58d9d4c32ed3e7513861` revisa R129, declara kit não recebido, motores finais não ativados e `covers.published=false`. Cadastro exige kit privado original, ledger por edição/conteúdo, administração nativa, candidata selada e confirmação assinada fresca v3. Os recibos públicos sanitizados não são o par de implantação. A entrega R134 e os incidentes desta revisão estão consolidados no servidor em `docs/station-android/r134`, no ramo `audit/station-consumer-online-r134-20261011`, preservando a entrega R133; não há alteração do contrato de ativação por consequência.

## Limites e reprodução

Usar somente as novas receitas R134 sobre o donor R133 exato SHA `945f7ded35e551d638135a05140c32218eb38277d10eaf21e3f83087d71da112`, 2.714.971.151 bytes, fonte `5966a8ad23ae9040c570d359b999c8a31de904b4`. Não editar fontes congeladas R131/R132/R133 nem criar outro snapshot completo; o backup único em F conserva a reconstrução necessária.

Compilação, assinatura, instalação, navegação física, consumo das configurações pelo jogo, controles, gameplay, térmica e ativação do servidor têm estados próprios no [STATUS](STATUS.json). Firmware, RSA, APKs, ROMs, bytes privados do kit, screenshots, seriais, sessões e logs pessoais ficam fora do Git.
