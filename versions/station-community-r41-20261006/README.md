# TurboStations — Comunidade R41

Nova página online com menu lateral, salas públicas, pessoas online, criação de sala e conversas dentro do app. Leia o handoff APP→SERVIDOR nesta pasta para contratos completos, fluxos, limites e publicação. Não confundir esta entrega com servidor implantado.

APK pronto: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Comunidade-R41-20261006.apk`.
SHA256: `b6b19321ec529945870dc919c3de5f0eba75aa54330d3672227b8e632302b28d`.

Base R40 com céu azul/nuvens claras, menus pretos, seletor à direita e robô contínuo. Preserva emuladores/relay/controles/autenticação/downloads. Somente classes35 muda sobre R40;13.179 entradas preservadas. Segundo jogador conciliado com f7f0561.

**Não instalado, USB ausente. Não estável geral.** Conversa privada e pedir vaga exigem SocialEnabled no servidor com o delta fornecido. Convites/salas/chat da sala existentes permanecem compatíveis. Não implementa nem envia WhatsApp real/MenuIA; confirmação do usuário sobre esse canal está pendente após instrução para não usá-lo.

## Reproduzir

1. `python recipes/restore_r41.py E:\ESTUDO APK\work\station-r41-restored` em nova pasta.
2. Na pasta restaurada executar `python test_r41.py` e `python build_r41.py`; conferir DEX/hash e o EXTERNAL-BUILD-INPUTS.json.
3. `package_r41.py` exige APK R40 exato e material privado de assinatura. Por proteção não sobrescreve candidato existente. Para reproduzir em outro destino alterar apenas O; base e hashes continuam obrigatórios. APK/mídias privadas/chave/ROMs/BIOS não entram no Git.
4. Instalar por atualização com assinatura original, sem jogo/download ativo. Nunca desinstalar/limpar dados.

## Código e rastreio

- StationRoomsActivity: layout, navegação, salas, criar/escolher jogo, conversa, convites, pedido de vaga, polling e retorno.
- StationSocial: capabilities verificadas, seleção de conversa por par de IDs e pedidos pendentes.
- StationSocialIcon: ícones vetoriais sem animação contínua.
- StationPresence: foreground, cancelamento, retry limitado e aviso clicável no catálogo.
- StationPlayerSheet/Model: perfil, convite e entrada do segundo jogador.
- StationOnlineClient: rotas/leases assinados já existentes e mensagens de erro.
- StationRetroActivity/Launch/GameSession/Relay*: bytes de fonte preservados, sem trocar os controles/motores nesta revisão.
- server/: fontes novas e base exata para o operador aplicar somente o delta Station.

255 checks Java +64 C# passaram. O aparelho e gameplay de dois celulares não foram verificados nesta revisão. História privada efêmera32 mensagens por peer, sem promessa de armazenamento permanente ou confirmação de leitura.
