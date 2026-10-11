# R122 — tema Ondas, organização online e downloads

## Mudanças

- O seletor Lottie existente alterna Ondas azul/escuro usando `station_appearance/theme`; Céu mantém suas cores. Apenas RGB e rótulos mudam, preservando forma, ritmo, 30 FPS e desligamento por economia/loading/lifecycle.
- O mesmo campo de nome online fica abaixo de JOGAR ONLINE, sem cartão e com fonte menor. Edição, limite e persistência mantidos. Estou pronto tem linha própria; anfitrião recebe Iniciar e Sair lado a lado. Sair permanece disponível nos estados em que já era permitido.
- Erros terminais de download aparecem também na tela de origem, quando o carrossel está em primeiro plano. O observador usa referência fraca e eventos de lifecycle; não abre aviso sobre emuladores e não usa polling novo. Cancelamento não gera aviso de falha.
- Central em carvão/azul/ciano: capa compacta, nome/estado/progresso, velocidade/tempo/quantidade e ações lado a lado. Tipografia e margens menores; área de toque preservada. Confirmação de cancelamento usa o mesmo visual.

## Preservação

Base exata R121. Reuso de cards/TextureView e init/teardown GPU nos Workers mantidos. LEDs, shaders, ganho/rastro, cache/preload, vídeos locais, loading preto, emuladores, runtime, controles, autenticação, partidas/slots/contrato/comandos e pausa/retomada/cancelamento de download preservados. Factory continua delegando ao AndroidX/Application originais; somente registra o observador de avisos de download. LoginActivity faz o registro idempotente também para Android API26/27, onde AppComponentFactory ainda não existe. Remover essas duas linhas reproduz integralmente os arquivos anteriores; os fluxos de autenticação não mudam. Servidor não alterado.

## Evidências desta revisão

233 fontes Java e123 identidades nativas congeladas. Sete fontes Java mudam, incluindo um arquivo novo; duas fontes nativas mudam apenas cores e rótulos. Salas:192 estados,1904 verificações e143 guardas. Ondas:34 verificações Java e16 helpers nativos. Downloads:30499 verificações host,35 guardas e compilação API34 dos49 arquivos do módulo. As fontes reais compilam separadamente das provas host. Recibos históricos não são contados como testes desta revisão.

## Limites da conferência

Testes host e compilação não comprovam aparência no Android, ausência de ANR, consumo ou gameplay em dupla. A R121 foi observada em Sua sala; o último ANR disponível continuou sendo anterior à instalação. Isto não demonstra estabilidade prolongada. R122 é candidata; canais históricos estáveis não são promovidos por esta entrega. Menus internos dos demais emuladores seguem separados e seus binários permanecem preservados.

## Reprodução

`build.py` exige APK R121 exato, manifestos congelados, JDK/SDK/NDK e inputs privados locais hash conferidos. Fases prepare, compile e package sequenciais. `recipes/build-r122-arguments.json` é configuração local ignorada. E: temporários/compilação, G: montagem/final. Mesma chave somente após certificado idêntico. Publicar apenas código, receitas, testes e recibos agregados; APK/mídias/ROM/BIOS/logs/capturas/chaves/seriais ficam locais.
