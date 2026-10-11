# Alterações detalhadas — R120

## Switch: comparação com a referência estável

Comparados APK estável Cemu de 30/09, referência estável de dois jogadores R76 e R119. libyuzu-android.so SHA `c82b35d81aa4b9521a64bf79e7d617fb418df5e9b728b5b228b4860e55d1a72b`, 35.518.648 bytes, é idêntica. A tabela de 43 perfis nativos também é idêntica à de 30/09. A auditoria de DEX/resources está em SWITCH-AUDIT.md; não houve troca do motor nesta revisão.

O caminho ESActivity → SwitchConfigPatcher prepara um XML com package antigo. O dispatcher original transmite esse package ao GameLauncher.setClassName sem remapeamento; Bootstrap usa o próprio package somente no segundo salto. Leitura física do XML confirmou o valor antigo. O hook nativo da R120 intercepta aliases Switch e entrega exatamente o comando anterior, mudando apenas package para o aplicativo atual. O XML preparado por código original continua histórico, mas o comando executado na rota do carrossel é corrigido. Não se declara causa única de qualquer erro de jogo ou gameplay físico validado.

## Pastas canônicas e aliases

O dispatcher consulta a pasta interna, não o rótulo visível. presentationKeyEqual não remove hífens. O folder pc-engine-cd caía no perfil original mednafen_pce_fast, que não passa por pcePrepare do core preciso. A R120 reconhece o folder e usa mednafen_pce, destino já previsto pelo hook para o rótulo PC Engine CD. HuCards permanecem no core rápido.

megadrive--br e super-nintendo--br não tinham aliases nas tabelas/hooks; o fallback por extensão podia depender do arquivo. Foram ligados explicitamente aos mesmos motores já usados pelas plataformas base: mdemu_station e snes9x. Não se alterou engine, configuração ou ABI. Teste HOST compila seis funções reais de seleção de comando com mocks de string/fallback: 50 folders, 78 aliases resolvidos e 18 casos diretos/unknown; 146 verificações, 37 fallbacks preservados e zero falhas. Isso valida seleção estática do comando, não abertura de ROM, BIOS ou gameplay Android.

## Controles: ocultação por família

Inventário completo em REVIEW-CONTROLLER-VISIBILITY-R120.md. SNES/Mega Drive, Switch, Vita e Xbox clássico possuem mecanismos de presença próprios, com suas particularidades. Dolphin não possuía automatismo equivalente: o novo StationControllerPresence é registrado no Application original através de StationComponentFactory delegado ao AndroidX original.

O observador só acompanha EmulationActivity/InputOverlay exatos do Dolphin. Responde a adicionar/alterar/remover dispositivos e lifecycle/layout, sem polling. Exige GAMEPAD ou JOYSTICK completo, não virtual. Ao ocultar, envia CANCEL, libera somente overrides de toque pelo método público do overlay e torna-o INVISIBLE. Quando o último controle sai, refreshControls respeita preferências; visibilidade GONE definida por outro dono é preservada. Nenhum botão/axis físico é interceptado. Pause libera listeners; nenhuma camada de outro emulador é ocultada por esse helper.

Flycast/N64/PPSSPP/Cemu/Saturn/XenDroid/host privado e runtime online têm lacunas específicas documentadas. Forçar visibilidade sem restaurar estado ou apenas reescrever CFG após inicialização não é uma correção demonstrada. Não foi adicionada adaptação global que interfira em motores ou altere perfis online. Bluetooth/USB devem reportar fontes de gamepad/joystick; dispositivos em modo teclado têm comportamento diferente.

## Menus com identidade de jogos

Configurações nativas: abas e geometria de toque conservadas; regiões planas com seleção ciano/foco branco. Desenho fixo no pipeline existente, sem novos shaders/FBOs/blur/timers. Efeitos Java: mestre em faixa, ambiente e grade de opções, estados claros e foco de controle. Online: navegação lateral compacta, cabeçalho fixo com jogo/estrelas/jogadores/plataforma, ações angulares, informações secundárias legíveis e participantes sem moldura redundante. Veja MENUS-CONSOLE-R120.md para referências oficiais e detalhes.

StationRoomsActivity mantém corpos dos métodos de criação/entrada/comando/chat/estado/capas. Guardas de comparação com a R119 aprovados em evidence/online-presentation-guards-r120.json. A apresentação não muda contrato, elegibilidade, emuladores ou quantidade de jogadores.

## Preservação, testes e riscos

Economia R119 mantida: fila única, prioridades visíveis, caches por revisão, preload, lifecycle, vídeos locais uma vez, hold dois frames, halo LED incremental quatro linhas/quadro, menus 30 fps. Nenhuma conclusão de consumo ou temperatura foi extraída desta revisão.

Teste isolado controller-presence: 68 checks. ComponentFactory: 43 checks Java e 1.505 AXML, reversão binária exata e apenas appComponentFactory diferente no XMLTree. Guardas de sala: 13. Produção compilada sem alteração para testes. Não são testes com controle físico ou gameplay. Factory depende Android API28+; aparelhos desta entrega suportam. Delegado ausente falha explicitamente, em vez de trocar componentes silenciosamente.

APK compilado/assinado/alinhado; motores/cores/runtime/resources/frontend e todas as outras 13.544 entradas byte idênticas. AndroidManifest.xml conserva Application, processos, permissões e demais atributos. Mesma assinatura; instalação preserva UID/data/firstInstallTime e confere hash integral. Não desinstalar, limpar dados ou interromper partida/download. Instalação, observações e publicação são recibos separados; histórico anterior não substitui verificação desta revisão.
