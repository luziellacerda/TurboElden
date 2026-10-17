# Checkpoint estável R157 — 14/10/2026

O proprietário pediu **“SUBA COMO VERSÃO ESTAVEL”**. Esta designação seleciona
a R157 como ponto de recuperação do app. Ela não altera o código do APK.

| Item | Identidade confirmada |
| --- | --- |
| Fonte executável R157 | `c9906512faf4d80ca5fd6d66880772f02b29a359` |
| APK R157 assinado e instalado no A56 | SHA-256 `563625c40bfce77def6770a67448f83e2206e67a07023c58359ad2a0de4eee34` |
| APK R156 base para reconstrução | SHA-256 `a072af70c04f0b9f9455b22a856bcdf0995b42da5650c2f9ee87243d17f5d5a6` |
| Kit privado R157 preparado, não aplicado | SHA-256 `240ecba97b9b6773f3177eb127f8a065bfc8f6993f6f4918869e1ffb4b5acbd3` |
| Kit privado R156 base, retido | SHA-256 `05df528314c454d7ec5d94333337eb3dd524a8fa2a08d7051151f6878a9a3c13` |

O APK R157 foi instalado no Samsung A56 com `adb install -r`. O hash integral do
`base.apk` no aparelho coincidiu com o arquivo assinado; diretório de dados e
primeira instalação permaneceram iguais. Somente esse aparelho tem instalação
R157 comprovada neste checkpoint. A inspeção visual das ondas na sala online,
o desempenho/bateria e partidas físicas continuam **sem validação**. A
ocorrência anterior de HTTP 409 `STATION_REQUEST_PROOF_REPLAY` permanece
separada da alteração visual; não houve mudança na segurança ou no protocolo.

## Recuperação

O backup conferido está em `F:\TurboStations-Estavel-R157-20261014`:

- `apk/TurboStations-Premium-R157-visual-20261014.apk` é o APK instalável.
- `apk/TurboStations-Premium-R156-base-20261014.apk` é a base assinada exata da
  receita R157.
- `kit/Kit-Servidor-TurboStations-R157-Independentes.zip` é o kit privado exato
  do motor R157; seu preparo **não** confirma recebimento pelo servidor.
- `kit/Kit-Servidor-TurboStations-R156-base.zip` conserva a base da receita do
  kit R157, mas não deve ser aplicada como substituta.
- `proofs/` contém recibos do APK, DEX, instalação, promoção e do kit, além da
  receita privada do kit. `SHA256SUMS.json` registra os hashes dos arquivos.
- `TurboStations-R157-sources.bundle` conserva o histórico Git necessário para
  recuperar as fontes e o checkpoint. O tag é
  `estavel-station-r157-20261014`.

Para reinstalar no aparelho, conferir o SHA-256 do APK acima e usar a
atualização por cima da instalação existente, preservando os dados. Para
recadastrar os motores no servidor, usar **somente** o kit R157 e as duas
transações descritas no [handoff](README.md): 78 modos, recibo, baseline
efetiva fresca, 321 decisões N64 vinculadas ao runtime R157 e segundo recibo.
O ledger e o preparador N64 são obtidos do Git pelos hashes indicados no
handoff; não estão no ZIP. Conferir capabilities assinadas depois da aplicação.

O tag histórico `estavel-station-r143-20261013` é mantido como retorno anterior
com três participantes em Top Gear 3000 relatados pelo usuário. Não confundir
essa prova física da R143 com a R157. Os três arquivos locais de evidência
R141 já modificados antes desta promoção ficaram fora do checkpoint.
