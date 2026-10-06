# R57 — barra superior fina e célula Criar sala

## Pedido final respeitado

O mantenedor esclareceu: **não alterar INSTALADO nem a faixa vermelha; afinar a barra preta superior**. A R57 final preserva byte a byte `native_formation.h`, `native_installed_tag.h`, `station_ribbon_placement.h`, `installed_art_asset.h` e `installed_art_r48.h` da R55. Mantém também o objeto de arte R51. Capas, faixa, letras, cor, escala e âncoras não mudaram. A tentativa intermediária de mover capas para reservar espaço foi descartada antes do APK final.

Barra superior: altura de10,5% para8,5% da tela, redução de19,05%; botões, nome/avatar e área de configurações reposicionados verticalmente para caber, mantendo funções e posições horizontais. A linha verde acompanha a nova borda. A faixa vermelha deixa de encostar no cabeçalho;8.820 casos de geometria passaram.

Criar sala: título do jogo em18sp; botões na coluna esquerda com limite de280dp e tamanho simétrico, capa inteira ao lado usando FIT_CENTER. Em largura insuficiente há disposição vertical. Reutiliza o mesmo bitmap do cabeçalho e o cache validado existente, sem segundo download, outro decoder ou animação contínua. As duas imagens são desvinculadas antes de reciclar o bitmap. Selecionar o mesmo jogo já exibido mantém sua imagem.

## Identidade

- APK: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R57-20261006.apk`.
- SHA-256: `e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566`.
- Tamanho:2.093.276.800 bytes.
- DEX35: `cf3a92bce2927c0561c64783ae0030c6e5dc90fa81264564d977974a746c74fd`.
- Carrossel nativo: `1dd67942358abebca8e82a4c457a9d4163a48b2e73aa856ce62ab78018cde922`.
- Certificado preservado: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

R56 é apenas o passo de compilação da célula Criar sala, não instalado. A R57 inclui esse DEX e altera somente `libturbo_carousel.so` em relação à R56. Assinatura, alinhamento16KiB e preservação das13.193 outras entradas foram conferidos no APK final. Consulte `STATUS.json` para a confirmação de instalação, separada da compilação.

## Fonte atual sem ambiguidades

Base completa de código publicada: `versions/station-current-r55-20261006`, commit `9d3d45f048aa44bb2ee9c41f567e985901628daa`. Esta pasta é um **overlay explícito** sobre essa base: substitui os arquivos homônimos e adiciona os novos listados em `SOURCE-MANIFEST.json`. Todos os outros fontes continuam sendo os da R55. Não é um projeto autônomo nem substitui os recursos privados enumerados na base.

Fontes de compilação:

- Java: `E:\ESTUDO APK\work\station-create-card-r56-20261006`;157 fontes compiladas Java8/API34/D8min26.
- Nativo: `E:\ESTUDO APK\work\station-compact-header-r57-20261006`; NDKr28c.
- `evidence/rooms-build.json` e `evidence/native-build.json` registram todos os hashes e entradas.

O teste Android isolado de layout foi encerrado pelo aparelho antes de produzir resultado; ele **não passou** e não comprova falha do APK. A compilação, a comparação de fontes, a preservação de pacote e os testes de geometria são evidências separadas. Gameplay em dupla e ganho térmico continuam sem prova nova.

## Aviso ao implementador do servidor

A revisão funcional online permanece a do [handoff R55](../station-current-r55-20261006/HANDOFF-APP-R55-PARA-SERVIDOR-20261006.md). `StationSessionChannel`, `StationGameSession`, `StationRetroActivity`, `StationRelayTunnel`, contrato, motor, opções e hashes de netplay estão preservados. O candidato de prontidão d1b535c ainda não foi integrado. A única Activity de salas alterada pela R56 é `StationRoomsActivity`, para a apresentação da capa/ações; usar esta edição se o retorno também mexer nela. Não voltar à R41 nem perder a correção Binder da R54.

Esta revisão não declara estabilidade geral nem solução do segundo jogador. O pedido de revisão no Servidor-pix foi publicado em `5722e50b19a19202bc01051277efb5fb7d712b89`.
