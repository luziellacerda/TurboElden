# R99 — retorno do servidor integrado sobre R98

APK compilado, assinado com o mesmo certificado e pronto para teste nos aparelhos. **Não instalado**: nenhum aparelho apareceu na USB na conferência final. Nenhuma partida física, controle BSP-D3 ou estabilidade em cinco telefones foi validada nesta entrega.

## Origem exata

- Servidor: `9f3739baba135354aa17c62de137090a801ea532`, branch `feat/station-online-all-platforms-20261009`. Contrato, código e registros lidos. A produção é confirmada pelo recibo do operador; não houve acesso/implantação/reinício Linux nesta tarefa.
- Cliente entregue pelo servidor: `2f435700c68b530e8d4542c0ed1db32824024bf2`, branch `feat/station-online-all-platforms-client-20261009`.
- Base atual: fontes R98 e APK `556fc80a4f5d403ac16a31a18390b156b99cbddce1d2e1a9c5540d0cd0538a77`, que incorpora R97. O retorno estava baseado em R81; suas Activities e DEX antigos não foram restaurados.

## Implementação

- Declara capacidade cinco ao servidor e aceita P1–P5 somente nos perfis exatos aprovados. SNES permite cinco; N64 quatro; limites das demais plataformas seguem o contrato. Metadados descritivos não autorizam vagas.
- Integrados o runtime entregue para cinco jogadores e os quatro novos núcleos PCSX, NeoCD, ParaLLEl N64 e FBNeo. Os dez registros habilitados conferem com o retorno do servidor. Geolith continua desabilitado; Neo Geo ZIP usa FBNeo.
- Corrigidos dois limites de quatro ainda presentes na própria entrega: `StationRoomRoster` e `StationRoomStartState`. Sem isso, uma sala de cinco teria participantes ocultos e não poderia iniciar.
- Modos, instruções e fontes do perfil assinado aparecem nas telas atuais, mantendo capas e seleção de quantidade. A composição de snapshots preserva `serverPlatforms` e `platformPolicy`; indisponibilidade do motor local não é apresentada como falta de ativação do servidor.
- `contentIdentityScheme` preservado no catálogo e cache. `cue-set-v1` vincula CUE e todas as faixas; ausente mantém o hash legado do arquivo. Esquemas não implementados são recusados, sem inferir identidade pela extensão.
- Preparação isolada das BIOS já contidas no APK, sem importar saves/configurações offline. N64 usa portas ativas do roster e overlay analógico; PSX usa perfil DualShock quando aprovado.
- Preservadas as correções R98: modal final opaco sem borda, autoconfig Bluetooth, perfil adaptativo Xbox/BSP-D3 condicionado aos códigos Android observados e ocultação de controles virtuais. O funcionamento físico do BSP-D3 continua pendente.

## Limites reais

Dreamcast, GameCube, Wii e Wii U têm contrato no servidor, mas ainda precisam dos respectivos adaptadores nativos no aplicativo. Eles não foram anunciados como jogáveis. O catálogo atual de Switch referido pelo servidor é individual; não foi inventado um modo para dois. Prontidão do servidor não implementa essas interfaces no APK. Esta entrega não declara todas as plataformas online concluídas.

## Evidências

224 fontes Java compiladas. 200 verificações de perfis, 12 de conteúdo, 51 de salas/quinta posição, nove de catálogo, 18 de BIOS e 1.181 de C nativo com 12 guardas passaram. Três verificações de links simbólicos da BIOS não rodaram: o usuário Windows não dispõe desse privilégio; as rejeições de links permanecem no código. Ensaios locais não equivalem a gameplay Android.

Os 13.548 arquivos do APK foram comparados integralmente. Mudaram classes28.dex, classes35.dex, engines.json e o runtime online; quatro bibliotecas e recursos/licenças foram adicionados. Carrossel nativo, LEDs, vídeos, 30fps, downloads, emuladores offline, layouts existentes de toque e 219 perfis de gamepad foram preservados. Assinatura e alinhamento de 16 KiB verificados.

APK final local: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R99-20261009.apk`, 2.218.245.512 bytes.
SHA256: `f124847e6f16b8b4b79afe48a79cbb1a66190f6e9a8494e480b78a4618791955`.

## Reprodução e continuidade

`build.py` recompila os dois módulos Java sobre esta pasta, usa o APK R98 local verificado e os arquivos do commit exato informado em `NATIVE-INPUTS.json`. Os inputs nativos e suas fontes/licenças estão preservados em `E:\ESTUDO APK\work\station-server-integration-r99-20261009\incoming`. A receita não substitui um APK final existente silenciosamente. Temporários ficam em E:; resultado em G:. Não publique APK, BIOS, ROM ou dados pessoais.

Nenhuma instalação/recompilação do servidor é exigida pelos dez motores recebidos. Para conferir fisicamente a R99, instalar nos participantes com a mesma assinatura após saírem da partida; usar sala nova e testar primeiro dois jogadores, depois as quantidades aprovadas, incluindo cinco no SNES. Não encerrar partida ativa automaticamente.
