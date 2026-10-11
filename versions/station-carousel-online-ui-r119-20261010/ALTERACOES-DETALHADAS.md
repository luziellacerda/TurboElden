# R119 — alterações detalhadas

## Duas células sem capa

Captura local do Motorola R118: Fatal Fury Special, posição11/644, hero e quatro miniaturas presentes, últimas duas em placeholders. Lista de jogos confirmada pelo mantenedor.

O produtor nativo entregava prioridades simétricas `0,+1,-1,+2,-2,+3,-3,+4,-4,+5...`; StationCatalog_prioritize admite nove. O layout desenha seis miniaturas à direita, portanto +5/+6 ficavam fora da prioridade e o plano limitado já estava preenchido.

prioritizeHook entrega o hero selecionado primeiro, depois índices reais do vetor filtrado do anchor animado até+6, depois vizinhos até completar nove. Confere bounds/itens, elimina duplicatas e trata seleção rápida/início/fim/transições desligadas. Compara prioridade existente no Catalog, sem cache/alocação por quadro. ABI: vector de 24 bytes por constref, priorities em 0x100/0x108, item de 232 bytes, chamada 0x196020 preservada. Não muda frontend/fila/retry/cache/decoder/preload.

## Configurações e efeitos

native_settings.h conserva tabs/ações/salvamento/scroll nativos. Texto e hitboxes com mesmo mínimo48 dp; DisplayMetrics somente ao trocar dono/dimensões, sem JNI por quadro. Cor do céu sem sobreposição ao toggle. EFEITOS GRÁFICOS integrado à navegação; azul-marinho/ciano.

StationGraphicsPanel: Controle geral/Fundo/Capas e mídia/Interface, duas colunas em paisagem suficientemente larga, scroll em espaços menores, toggles48 dp. Estados claros para escolhas salvas mas paradas por mestre/Sem fundo. Preferências/migração/máscaras intactas. Não recoloca botão geral principal nem cria workers/animações contínuas.

## Organização online

StationRoomsActivity: Partidas/Acesso na lateral, botões48 dp com intervalos, área central mais útil, contêiner externo transparente nas salas, nome/pesquisa dimensionados e seleção coerente. Mantém comandos/callbacks/validações/fases/capas e medidas R118 da sala própria.

StationActionButton: azul-marinho/ciano, perigo discreto e foco claro. Hitboxes/estados/textos/handlers/gate e animações já restritas a Abrir/Voltar intactos. Nenhuma animação nova.

## Motor e menu online

SNES normal usa Snes9x EX+; online inicia a NativeActivity privada StationRetroActivity com runtime/core assinados, não app externo. R118 forçava menu_driver=rgui e mantinha menu_toggle em perfis/overlays.

R119: menu_driver=null, combo 0 e binds menu_toggle=nul apenas no CFG online. Cópias privadas retiram exclusivamente menu_toggle preservando geometria/PNGs/demais bindings. Back/Menu/Guide abrem painel próprio com saída humana existente; botões/eixos/adaptação BSP-D3 intactos. REVIEW-ONLINE-MENU-R119.md traz fonte upstream exata e aviso não fatal do driver null. Igualdade visual completa normal/online depende de conferência por plataforma.

## Preservação e limites

R118 preservada: passada geométrica completa antes do halo LED incremental; quatro linhas/quadro,16 amostras, shaders/ganho/rastro/velocidade finais; menus30 fps; vídeos locais uma vez segurando dois frames antes do fim; Ondas/Céu/Sem fundo; loading preto/barra/%; fila IO/decode única, cache por revisão e lifecycle. Não altera cores/runtime/engines/protocolo/roster/autenticação/recovery/servidor/emuladores standalone.

Compila230 fontes Java e duas bibliotecas UI; frontend sem alteração deve gerar bytes idênticos R118. Apenas dois DEX e carousel UI podem mudar. Confere assinatura original, alinhamento16 KiB e demais entradas integrais. Nenhum teste novo adicionado/executado. Compilações não comprovam gameplay/aparência/consumo. Capturas/seriais ficam locais; publicar fontes/receitas/recibos agregados.
