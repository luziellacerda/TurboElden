# N64 online R159: vínculo do CoreService

## Evidência no aparelho

No moto g52 com a R158, a lista de salas abriu e o início da partida avançou por `StationRoomsActivity` (`prepare` e `activity`), `StationN64Activity` e `paulscode.android.mupen64plusae.game.GameActivity`. O processo `:n64core` então iniciou `paulscode.android.mupen64plusae.jni.CoreService` e lançou `IllegalStateException: N64_OWNER_MISSING` em `StationN64Bridge.onServiceStart` (linha 33). O erro repetiu às 18:10:30, 18:10:32, 18:10:40 e 18:10:42, horário local do aparelho. Um ANR do serviço também apareceu depois. Esta evidência foi filtrada do logcat; não inclui serial, token, identificador de sala ou log bruto.

Portanto, a falha observada é ao **iniciar o jogo a partir da sala**, não ao abrir a lista de salas. O motor aberto nessa rota é o **Mupen64Plus AE integrado**, no processo do TurboStations; não é RetroArch/RetroC*.

## Causa e correção

`CoreFragment` passa `getApplicationContext()` para `ActivityHelper.startCoreService`. `ActivityHelper` chama `StationN64Bridge.propagate` antes de iniciar o serviço. A R158 só aceitava a Activity atual ou um serviço já registrado como contexto da sessão; por isso não colocava `station.n64.launch` no Intent do `CoreService`. A validação do serviço, corretamente, recusava a inicialização sem esse marcador.

A receita R159 permite esse contexto de aplicação **somente** dentro de `propagate`, se a sessão ainda estiver aberta, o contexto for exatamente o da Activity dessa sessão e o Intent apontar explicitamente para o `CoreService` do mesmo pacote. `isStationContext` e `onServiceStart` permanecem como eram. A nova exceção não aceita contexto arbitrário, serviço diferente, sessão ausente ou sessão encerrada; o fluxo offline continua sem receber o marcador. A alteração não cria thread, temporizador ou consulta periódica.

## Build e escopo

O APK assinado R159 foi montado a partir do doador R158, SHA-256 `fc1d2d983deb5179979a4aebac7fa64b1740da1c62ae46bfc0d1f4c11eb46cf0`. O build conferiu 13.860 entradas, preservou 13.855 delas e alterou somente `classes35.dex`, `engines.json` e três marcadores de identidade nativos. No DEX, 607 das 608 classes permaneceram iguais. O [recibo do DEX](recipe/dex-receipt.json), o [recibo do APK](../../docs/server/r159/final-apk-proof-r159.json) e o [recibo do kit](../../docs/server/r159/server-kit-receipt-r159.json) registram os hashes.

Para reproduzir em ambiente autorizado, forneça os caminhos locais do APK doador exato, JDK 17, apktool fixado, NDK e diretório de saída pelas opções dos scripts em `recipe/` e `packaging/`. A assinatura usa a autoridade privada mantida fora do repositório. O adaptador `packaging/sign_private.py`, SHA-256 `437aa6df4295b9b797ee055441cbb44b0f218c79214820033f6dfa2e14be5410`, está no backup privado R159 e é ignorado pelo Git público; a reconstrução exata exige restaurá-lo antes do empacotamento. O APK final tem SHA-256 `4837be706f9ac1f913b4844353741f70c539674e125ae185239611cf5faac2b3`.

A instalação no telefone, o cadastro dos novos fingerprints no servidor e a partida física ainda exigem recibos antes de declarar a R159 estável.
