# Entrega R159 — N64 online

## Conteúdo da pasta `SERVIDOR LER\R159-N64` na unidade USB de entrega

- `Servidor/`: kit independente privado, handoff técnico e recibos de assinatura, identidade e instalação.
- `App-APK-e-Instalador/`: APK assinado R159, instalador USB, manifesto com hash e ferramentas ADB.
- `Fonte-da-correcao/`: receita pública da mudança de posse do motor N64. A autoridade privada de assinatura permanece no backup local, fora do pen drive.

A cópia USB só estará concluída quando `Servidor/usb-delivery-receipt-r159.json` confirmar a leitura dos arquivos na própria unidade. Ignore qualquer arquivo com extensão `.partial`.

APK: `TurboStations-Premium-R159-n64-owner-20261014.apk` — SHA-256 `4837be706f9ac1f913b4844353741f70c539674e125ae185239611cf5faac2b3`.

Kit: `Kit-Servidor-TurboStations-R159-Independentes.zip` — SHA-256 `d1f0b3805392c13b597e85b4ef8ec1fa938c19f77f2e5f5ee6ee3f2948c5454c`.

O moto g52 recebeu exatamente esse APK por atualização que preserva dados, e o aplicativo iniciou. O servidor ainda precisa registrar as quatro identidades R159 descritas no handoff. O segundo telefone e a partida N64 física com dois aparelhos ainda não foram validados. A R157 permanece como retorno estável.

Correção N64: https://github.com/luziellacerda/TurboElden/commit/df3ef713
Instalador USB revisado: https://github.com/luziellacerda/TurboElden/commit/4680d369
Handoff com retorno do servidor: https://github.com/luziellacerda/TurboElden/commit/bcf771f3

Comece por `Servidor/N64-OWNER-HANDOFF.md`. Compare os hashes antes de aplicar o kit. Não substitua cadastros anteriores por identidade apenas aproximada.
