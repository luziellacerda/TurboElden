# R5 — navegação dos vídeos e SNES roxo, 04/10/2026

## Entrega e limites

APK `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Videos-Sem-Espera-SNES-Roxo-R5-20261004.apk`.
SHA-256 `afa300d23dc57bb5b1973530dc83371fc892d6c37cf11ecc1750aed8ff22415b`, 1.968.122.300 bytes.
Base R4 `17e9b87bf268c2349874d1767d5ab315862eb09fb2705f9b79a7e307c0c63c77`.
Compilado, assinado com o certificado preservado, alinhado a 16 KiB e conferido integralmente. **Não instalado: telefone ausente na USB. Não é estável.**
Não afirmar latência zero ou playback Android corrigido sem medir no aparelho. O R4 mostrou células azuis; a identificação completa desse sintoma ainda precisa de logs Android.

## Alterações reais

1. Removida a espera fixa nativa de 80 ms entre inícios de decodificação.
2. Entrar na lista ou em um diálogo libera os decodificadores e conserva prévias limitadas. Retornar reutiliza os quadros. Abrir emulador continua liberando os vídeos e as prévias.
3. Cache GPU limitado a oito texturas RGB565 de 720×720: 8.294.400 bytes. Texturas visíveis não são vítimas de descarte. Idade trata a volta do contador unsigned.
4. Um quadro real de cada um dos 44 vídeos é incorporado ao módulo nativo, para a célula ter imagem antes de chegar o primeiro quadro do MediaPlayer. Não são fotografias novas nem outro vídeo. Os 44 MP4 originais continuam idênticos e sem compressão ZIP, em 720p, velocidade 1×; só o foco continua tocando após as prévias.
5. O shader de desenho das prévias é independente do shader do antigo fundo; recriado quando o contexto GL muda. Não ativa nave, estrelas ou efeitos de fundo adicionais.
6. SNES e SNES BR passam a roxo `A855F7FF`, núcleo `F3E8FFFF`.
7. O texto anexado “JOGAR EM REDE” deixa de vazar pelo desenho automático dos filhos fora das configurações. O desenho das configurações verifica se a tela está aberta.

Mantidos: limite de FPS do menu, tratamento de falhas/recuo de tentativa, ciclo de vida Java e limite de decodificadores por hardware. Retirar limites de FPS aumentaria aquecimento; eles não são a espera fixa de carregamento removida.

## Integridade e testes

- Somente `lib/arm64-v8a/libturbo_carousel.so` mudou sobre R4; 11.048 entradas anteriores iguais. Acrescentado um aviso de compilação. DEX, motores, HUD, autenticação, catálogo, downloads, jogos, saves e MP4 preservados.
- 109 verificações de fonte, integridade de quadros e política de memória passaram. Não são 109 ensaios de telefone.
- OpenGL ES no ANGLE/Windows: shaders compilam; pixel RGB565 real do vídeo SNES resultou exatamente em `[156,154,173,255]`, sem erro GL. Isso não substitui a validação Android do OES/MediaPlayer.
- Falta: instalar por atualização, conferir primeiro quadro, alternância para ambos os lados, entrada/volta em SNES e Mega, vídeo central em movimento, consumo e saída de emulação. Nunca desinstalar ou limpar dados para isso.

## Reprodução

Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004`. Scripts nesta pasta Git. `prepare_station_r5.py` copia a base canônica R4; `patch_station_r5.py` aplica as mudanças com âncoras verificadas; `build_video_previews_r5.py` extrai quadros e compila o objeto; `build_station_r5.py native` compila e `package` empacota. Scripts recusam sobrescrever o APK final. Builds e temporários são E:.
Os arrays de mídia privados e o objeto com imagens não são publicados. A base R4, os arrays preservados do manifesto anterior e a chave de assinatura local são insumos necessários. Não executar scripts históricos de instalação/empacotamento sobre este candidato.

## Netplay solicitado — trabalho separado, não entregue por este APK

Alternativas oficiais auditadas: bsnes-mercury Performance (GPLv3), ClownMDEmu (AGPLv3), Geolith (BSD-3-Clause), com Netplay documentado pelo Libretro. Commits completos em `evidence/netplay-upstream-pins.json`.
SNES e Neo Geo compilados como candidatos Android ARM64; ainda não integrados ao APK nem aprovados em partida. ClownMDEmu e transporte RetroArch em preparação. Não substituir os controles locais aprovados por um protótipo.
O servidor no commit `54bba11c52f35695fd47eabc7145f42af9990426` não oferece salas/presença/chat/convites Station. A implementação nova exige contrato e publicação próprios. Nenhuma API inexistente foi apresentada como ativa. Nenhuma mudança em produção foi feita.
Restrição escolhida: partida direta entre aplicativos; sem lobby público nem retransmissor público. CGNAT pode impedir uma conexão direta. Geolith exige formato `.neo` para cartuchos; ZIP do catálogo não pode ser chamado como se fosse compatível. Licenças das alternativas exigem cumprimento das respectivas condições; isto não certifica a distribuição comercial dos outros motores já existentes.
