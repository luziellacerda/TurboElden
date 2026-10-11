# R120 — lançamento do Switch, controles e menus de jogos

Base exata R119, fonte `13b21b9dc08adf7b1820fdeb09bec47a810c1ea5`; branch `fix/station-game-menu-controller-audit-r120-20261010`. Candidato experimental, sem promoção do canal estável R76 ou alteração do histórico R95.

## Entrega

- Switch: motor, DEX do emulador e recursos idênticos à referência estável. O XML físico do Motorola apontava para `org.emulationstation.frontend`, mas o aplicativo atual é `org.turboramastation.frontend`. A rota nativa corrige somente o pacote, conservando BootstrapActivity, ação, URI, MIME e conteúdo.
- Configurações, efeitos e online: identidade visual de console, superfícies carvão, ações azuis, seleção ciano e foco branco. Alvos de 48 dp e escolhas existentes preservados; sem animação contínua nova.
- Rotas por pasta: edições BR de Mega Drive/SNES ficam explicitamente nos seus motores EX+; PC Engine CD usa o core preciso já previsto, em vez do fallback rápido. Nenhuma biblioteca de emulação foi trocada.
- Dolphin/GameCube/Wii: observador de controle físico oculta somente o InputOverlay, libera entradas virtuais e restaura as preferências quando o último controle sai. Sem interceptar comandos físicos ou alterar o motor.
- Auditoria individual dos sistemas e dos controles: veja LAUNCH-AUDIT-R120.md, SWITCH-AUDIT.md e REVIEW-CONTROLLER-VISIBILITY-R120.md. Rotas existentes, disponibilidade dos motores e gameplay físico são evidências distintas. Não há garantia universal de ocultação automática em todas as famílias.

## Preservação e verificações

232 fontes Java compiladas. Apenas AndroidManifest.xml, classes28.dex, classes35.dex e libturbo_carousel.so diferem da R119; 13.544 outras entradas são byte idênticas. ApplicationYuzu original e demais atributos/componentes do manifesto são mantidos. O novo AppComponentFactory delega ao AndroidX original e registra a observação isolada do Dolphin.

68 verificações isoladas do observador, 43 da delegação Java, 1.505 do manifesto e 13 guardas dos métodos de sala e 146 verificações dos comandos de lançamento aprovadas. Compilação, assinatura e alinhamento de 16 KiB aprovados. Esses resultados não equivalem a gameplay ou teste de todos os controles no aparelho.

Mantém economia, filas de capas, preload, caches, seis miniaturas, LED, vídeos locais, carregamento preto, ondas/céu/desligado e 30 fps apenas nos menus. Emuladores, runtime online, perfis, identidades, autenticação, protocolo e servidor são preservados.

## Artefato e reprodução

APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R120-20261010.apk`.
SHA256: `d18c50da17b669373a183ba334e23f356c0521dfb3a2bac69301e8f10b9cbbe1`; 2.217.065.864 bytes.

Receita build.py em fases prepare/compile/package exige a base R119 SHA `f5d0e434cb383a7103c77fd1e853b9f4721d283c30941860a21f1831bf6be674`, manifestos atuais e congelados R119, SDK/JDK/NDK e objetos privados hash conferidos. Temporários em E:, montagem/final em G:. patch_component_factory.py modifica somente a propriedade necessária e exige reversão binária idêntica. Instalação direta via recipes/install_r120.py, mesma assinatura e dados preservados.

Git recebe fontes, receitas, manifestos, documentos e recibos agregados. APK, mídias, BIOS, jogos, chaves, seriais, sessões e capturas permanecem locais. Recibos R119 e anteriores são históricos; resultados R120 usam nomes R120. Consulte STATUS.json para instalação/publicação e limites atuais.

## Instalação final

Motorola Edge30 atualizado em 2026-10-11T02:54:58.386069+00:00; hash integral do APK final, UID e dados originais conferidos. Carrossel autenticado observado após abrir. Sem teste físico de gameplay ou controles; Samsung não atualizado nesta revisão.
Registro posterior do mantenedor: ANR físico na tela Sua sala às23:57:32; pilha main em espera de HWUI drawFrame. Causa em análise para revisão seguinte; esta entrega não é qualificada estável. Logs pessoais apenas locais.
