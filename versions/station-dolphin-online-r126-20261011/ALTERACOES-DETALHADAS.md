# Alterações detalhadas R126

## 1. Emulador real e isolamento do modo normal

GameCube/Wii usam a fonte Dolphin `5102a0339c2177575378107b76541e47cc52122d`, mesma família presente no modo normal. A variante `libstation_dolphin_online.so` usa o NetPlay oficial e quatro hooks gráficos com nomes exclusivos. `libdolp.so` e os hooks normais não são substituídos.

A seleção acontece antes da inicialização JNI da Application no processo exclusivo `:dolphin`. O descritor privado valida versão, prazo, caminhos confinados, jogo, core/runtime, perfil, slots e dados autenticados. Uma partida normal ativa não é encerrada para tomar seu processo. Um processo normal ocioso retorna resultado controlado e somente então permite a abertura online. A preparação dos diretórios originais termina antes do uso do sistema de configuração do Dolphin.

O adaptador mantém a Activity/Fragment/renderer e o objeto NetplaySession reais. O callback oficial entrega BootSessionData e a Activity original executa RunNetPlay. Não há troca apenas de overlay nem renderer RetroArch nessas rotas. O observador de controle físico R120 continua ocultando apenas a entrada virtual, sem substituir os menus por botões A/B.

## 2. Transporte e barreira de execução

Um endpoint específico encapsula datagramas ENet em DPL1 dentro do DATA ordenado v3. Continua usando links autenticados anfitrião↔convidado, janelas/offsets/ACK/backpressure existentes e tamanho limitado. O caminho TCP original das outras sessões não recebe o endpoint Dolphin.

O ACK externo só é confirmado depois de o pacote completo ser consumido pelo receive real do ENet. Colocar dados numa fila não autoriza o ACK. A leitura de saída é contabilizada para não publicar READY enquanto bytes estão entre a fila nativa e a janela do relay.

Controles recebidos publicam epoch/serial/permissão de execução imediatamente. O worker confirma pausa real da CPU, drena filas e espera o estado global autenticado. A liberação exige a revisão exata mais recente; uma pausa posterior bloqueia uma retomada antiga. Run, SetStepping(false) e RestoreStateAndUnlock(true) respeitam a mesma barreira. Após boot, a barreira da CPU é confirmada novamente: um primeiro STATE já liberado não substitui esse passo.

Perda de WSS suspende o motor e congela os temporizadores virtuais do ENet. Uma falha nativa permanente permanece em pausa e exige decisão humana. Cancelamento/saída humana cancela Connect, aguarda o worker e libera a sessão sem usar ponteiros já destruídos. Não há encerramento automático da emulação por timeout de espera do adaptador.

## 3. Controles, perfis e saves

Cada slot autenticado é convertido ao PID real do NetPlay oficial antes do mapeamento. GameCube oferece quatro portas GC; Wii oferece quatro Wiimotes emulados. O catálogo assinado do jogo/modo continua determinando os números de participantes aceitos. Um perfil de quatro portas não transforma jogos de dois jogadores em jogos de quatro.

O Wii usa o estado completo serializado pelo código oficial, inclusive acessórios configurados, sem retirar arbitrariamente Nunchuk/Classic/MotionPlus. Controles e compatibilidade física precisam ser conferidos nos aparelhos. Real Wiimotes/GBA não são habilitados automaticamente.

O online possui diretórios privados de sessão. Copia apenas configurações de entrada/apresentação necessárias; não importa saves, cheats ou preferências de core do modo normal. O sincronismo de saves/opções oficiais opera nessa área privada. As opções exatas constam no fingerprint e nos perfis canônicos, incluindo fixeddelay, buffers 5/1, strictSettingsSync e saves=session-only.

## 4. Integração N64 e identidades finais

N64 continua no Mupen64Plus AE da R125. O core `fe6e810a…`, os doze plugins/dependências, o DEX36 e o perfil de quatro portas são byte idênticos. O marcador passa a `1aafea201355…`, pois o descritor de proveniência identifica também o DEX35/manifesto integrado da R126. GameCube/Wii usam o runtime `ca43a338d799…`; possuem perfis distintos mesmo compartilhando o core Dolphin.

Os dez registros restantes do manifesto local foram preservados. O servidor precisa cadastrar três identidades finais no registro multiplayer e vincular somente edições/modos aprovados. Editar o registro legado ou reutilizar o ID de outro core não atende o contrato. A entrega técnica consolidada contém os valores e a ação verificável do operador.

## 5. Preservação e provas

Sobre o APK R125 exato, só mudam manifesto, DEX10/12/35, engines.json e marcador N64. São adicionados cinco ELFs Dolphin e seu marcador. As 13.544 entradas restantes têm SHA-256 idêntico, incluindo bibliotecas normais, vídeos, recursos, UI nativa, caches, preload, economia, LED e menus 30 fps. A compilação das salas conserva as fontes R124 mais os deltas explicitamente identificados; não restaura Activities antigas.

| Prova | Escopo |
|---|---|
| 107 verificações nativas de geração | Pontos de pausa/retomada, hooks e transformação |
| 21 exports JNI / cinco ELFs | ABI, dependências, SONAME e alinhamento |
| 15.054 verificações smali + 84 de fonte | Símbolos, chamadas e preservação do donor |
| 470 verificações JVM, três execuções | Framing, fragmentação, backpressure e ACK do endpoint |
| 231 verificações JVM | Descritor, perfis, cópia privada e cancelamento |
| 98 verificações JVM | Parser produtivo de perfis e rejeição de inconsistências |
| 72 verificações de identidade | Transformação, perfis distintos e dez engines preservados |
| Verificador do APK assinado | Todas as entradas, assinatura real e alinhamento 16 KiB |
| 303 verificações independentes | Segundo auditor, sem reutilizar a comparação do packager: bytes, fontes congeladas, manifesto, JNI/hooks e fingerprints |

O probe ARM64 de transporte foi compilado, mas não executado em aparelho. Fixtures JSON não são uma resposta assinada de produção. As provas anteriores R125 pertencem àquela revisão e não devem ser somadas como gameplay desta entrega. Instalação, gameplay de dois/quatro aparelhos, recuperação física, latência e temperatura continuam sem validação R126.
