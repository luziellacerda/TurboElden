# Handoff do cliente Android para o servidor TurboramaStation

Data: 30/09/2026. Referência recebida do servidor: `luziellacerda/Servidor-pix`, branch `docs/turboramastation-android-server-20260930`, commit `efcbbeefb6686aac790f98c0288f9d2bda63eed1`. Este documento responde ao plano e fixa o contrato que o cliente Android candidato já compila. Nenhum endpoint Android de produção foi declarado como existente naquele retorno.

## Entrega do aplicativo

- Fonte novo: `versions/station-android-client-20260930/java/org/emulationstation/frontend/auth/`.
- Montagem: `versions/station-android-client-20260930/build_candidate.py`, temporários e APK em `E:\ESTUDO APK\work\native-carousel\implementation\station-android-client-20260930`.
- Base exata: `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Plataformas-Organizadas.apk`, SHA-256 `1189899e780cd372e8e0efdbea7dad2926ecccf896542c3349d1b79caa8ac2c7`.
- Candidato compilado: `TurboramaStation-StationAndroid-candidato.apk`, SHA-256 `7b235395bd02b5c962e9c94b9d0ffc080f284ddbd7a516e62f4da219e01031ae`. Assinado com o mesmo certificado de desenvolvimento usado na base; **não instalado**. O arquivo não vai para Git.
- Entrada ZIP alterada: somente `classes8.dex`. Manifesto, recursos, bibliotecas, vídeos, catálogo embarcado e emuladores foram preservados byte a byte na montagem.
- `StationConfig.ENABLED=false`: o candidato conserva o login local enquanto faltam URL HTTPS e chave pública do servidor. Isso também deixa intactos jogos e saves do telefone. Ativar a flag exige nova compilação do código, não apenas editar o APK.

O módulo novo cria uma chave RSA 2048 no Android Keystore, deriva `deviceId = base64url(SHA256(SPKI DER))`, assina desafios RSA-PSS/SHA-256, verifica respostas assinadas pelo servidor, guarda apenas licença, ID do aparelho e nome em AES-256-GCM no diretório privado sem backup e mantém o token de sessão somente em memória. A verificação de rede roda fora da interface. Após ativação, a chave permite abrir nova sessão sem redigitar o código. A tela de login tem rótulo “Código de acesso” no modo comercial.

`StationAuth.welcomeText()` já fornece “Bem-vindo, {displayName}”, e `StationContent` expõe catálogo e autorização de download assíncronos para a ponte nativa. A tela nativa do cabeçalho e `GuiStore` ainda não chamam esses métodos; ver o bloqueio técnico abaixo.

## Identificação do aparelho e fraude

O cliente envia `deviceManufacturer`, `deviceModel` e `androidSdk` como informações auxiliares, vinculadas ao pedido/prova assinada. Não usa esses campos como prova de identidade: um cliente alterado pode falsificá-los. Não solicita IMEI, MEID, MAC físico, serial, telefone, contatos ou localização. Em Android comum, IMEI/serial exigem permissão privilegiada e MAC físico não está disponível de modo confiável para apps de terceiros. O servidor deve limitar ativações por licença, validar a posse da chave e auditar transferências. Atestação de hardware pode ser adicionada em protocolo versionado, com desafio emitido **antes** da geração da chave; o servidor deve validar cadeia, desafio e política de dispositivos. Não exigir StrongBox universalmente.

Referências oficiais: [restrições de identificadores](https://developer.android.com/about/versions/10/privacy/changes), [boas práticas de identidade](https://developer.android.com/identity/user-data-ids), [atestação de chave](https://developer.android.com/privacy-and-security/security-key-attestation).

## Contrato HTTP v1 que o cliente espera

Base URL: origem HTTPS sem caminho, query ou fragmento. O cliente não segue redirecionamento nas rotas da API e usa `Accept: application/json`; requisições POST usam `Content-Type: application/json; charset=utf-8`. Resposta bem-sucedida deve ser HTTP 200. `StationConfig` precisa receber, numa compilação comercial, `BASE_URL`, `SERVER_KEY_ID` e `SERVER_PUBLIC_KEY_SPKI_BASE64URL`. Enviar **somente** a chave pública SPKI; chave privada e pepper ficam no servidor.

Todas as respostas usam envelope `{ "keyId": "...", "payload": "base64url(UTF-8 JSON)", "signature": "base64url(RSA-PSS-SHA256(payload bruto))" }`. O cliente verifica a assinatura **antes** de analisar o JSON. O `payload` é a sequência exata de bytes UTF-8 enviada em Base64URL sem padding. O servidor não pode recodificar JSON depois de assinar. Algoritmo: RSA-PSS, SHA-256, MGF1-SHA-256, salt de 32 bytes, trailer `0xbc`. Cada payload inclui `schemaVersion: 1`, `domain`, `productId: TURBORAMA_STATION_ANDROID`, `applicationId: TURBORAMA_STATION_ANDROID`, `deviceId` e os campos da rota.

Pedidos com prova do aparelho usam `{ "payload": "base64url(UTF-8 JSON)", "signature": "base64url(assinatura do mesmo payload bruto)" }`. A ordem das propriedades JSON não importa porque a assinatura cobre os bytes reais. O servidor deve analisar o JSON **após** verificar a assinatura e exigir `domain`, produto, aplicação, licença, aparelho, ação, desafio e nonce esperados. `deviceId` deve corresponder ao SHA-256 da chave pública SPKI fornecida e à chave vinculada à licença. `activationCode` nunca deve entrar em log.

| Rota | Pedido do cliente | Payload assinado da resposta |
| --- | --- | --- |
| `POST /v1/station/activations/challenge` | JSON direto: `schemaVersion`, `domain=TurboRamaStationAndroid/request-activation-challenge/v1`, produto, aplicação, `deviceId`, `clientVersion`, fabricante/modelo/SDK, `activationCode`, `devicePublicKey` SPKI Base64URL | `domain=TurboRamaStationAndroid/activation-challenge/v1`, `deviceId`, `challengeId`, `nonce` Base64URL de 32 bytes, TTL do desafio |
| `POST /v1/station/activations/complete` | Envelope assinado pelo aparelho. Payload com `domain=TurboRamaStationAndroid/activate/v1`, identidade, `activationCode`, `devicePublicKey`, `challengeId`, `nonce` | `domain=TurboRamaStationAndroid/activated/v1`, `licenseId`, `deviceId`, os mesmos `challengeId` e `nonce` |
| `POST /v1/station/challenges` | JSON direto: `domain=TurboRamaStationAndroid/request-session-challenge/v1`, identidade, `licenseId` | `domain=TurboRamaStationAndroid/session-challenge/v1`, `licenseId`, `deviceId`, `challengeId`, `nonce` Base64URL de 32 bytes, TTL |
| `POST /v1/station/sessions` | Envelope assinado pelo aparelho. Payload com `domain=TurboRamaStationAndroid/open-session/v1`, identidade, `licenseId`, `challengeId`, `nonce` | `domain=TurboRamaStationAndroid/session/v1`, `licenseId`, `deviceId`, os mesmos `challengeId`/`nonce`, `sessionId`, `accessToken`, `expiresInSeconds` entre 30 e 3600 |
| `GET /v1/station/me` | `Authorization: Bearer <accessToken>` | `domain=TurboRamaStationAndroid/profile/v1`, `licenseId`, `deviceId`, `sessionId`, `displayName` (até 80 caracteres), `profileVersion` |
| `GET /v1/station/catalog?platform=...&cursor=...` | Bearer | `domain=TurboRamaStationAndroid/catalog/v1`, `deviceId`, `sessionId`, `platform`, itens/paginação ainda a fechar com o catálogo nativo |
| `POST /v1/station/downloads/authorize` | JSON direto com `domain=TurboRamaStationAndroid/request-download/v1`, identidade e `itemId`, mais Bearer | `domain=TurboRamaStationAndroid/download/v1`, `deviceId`, `sessionId`, `itemId`, `downloadUrl` HTTPS e `expiresInSeconds` entre 1 e 3600 |

O cliente rejeita chave desconhecida, assinatura inválida, `domain` incorreto, produto/aplicação/aparelho trocados, desafio diferente, licença ou sessão diferente, token malformado, expiração fora dos limites e download HTTP. O servidor precisa validar o bearer e o vínculo da sessão em cada rota protegida; a assinatura do envelope da resposta não substitui autorização no backend. Respostas 401/403 exibem acesso negado; 409 indica aparelho já vinculado; 410 indica código expirado.

## Trabalho necessário no servidor

1. Confirmar o release em execução, ledger real `suite.schema_migrations`, restrições produto/SKU e cadastro comercial antes de escolher migrations. O guia do próprio servidor registra releases diferentes entre PIX, API, admin e gateway.
2. Definir SKU, preço, prazo, limite de aparelhos, reemissão e transferência Android. A compra Windows não vira licença Android automaticamente.
3. Publicar OpenAPI v1 e vetores sintéticos de assinatura para cada `domain`. Retornar URL de homologação, `keyId`, chave pública SPKI e licença/código sintéticos. Resolver a origem do comprador para `/me` sem expor dados pessoais além do nome.
4. Criar produto, compra idempotente, licença, ativação transacional, sessão, revogação, painel e auditoria separados de Suite/EmulationStation Windows. Implementar feature flag inicialmente desativada.
5. Autorizar catálogo e downloads por item/licença/sessão Android. Não adaptar a sessão Android fingindo que é uma sessão Suite. Preservar IDs e pastas do catálogo Android atual; capas já baixadas devem permanecer em cache no aparelho.
6. Declarar política de expiração durante jogo, segundo plano e sem rede. Atualmente o cliente usa somente o prazo de sessão concedido na memória, sem transformar o marcador de senha local em licença comercial.

## Acrescentar a TurboramaStation à página administrativa existente

O mantenedor confirmou que já há uma página que gerencia outro serviço com o mesmo tipo de compra, licença e bloqueio. **Acrescentar as funções Android nessa página; não criar outro painel ou outro cadastro de clientes.** Os pontos identificados no backend são `/admin`, `/admin/clientes/{licenseId}`, as listagens de sessões e as rotas administrativas existentes de comércio, transferência e revogação. O servidor deve conferir a versão efetiva dessas páginas antes de editar, porque os binários implantados não vêm de uma única revisão Git.

Adicionar filtro de produto **TurboramaStation Android** e um cartão por licença na mesma consulta de cliente. Mostrar nome do comprador do pedido, referência do pedido, plano/validade, estado financeiro, código entregue ou expirado **sem exibir seu valor**, ativação, aparelho vinculado (`deviceId` abreviado), fabricante/modelo/versão do Android, versão do APK, último contato, sessão e estado de bloqueio. Esses dados auxiliares do aparelho não são identidade verificada. Se houver atestação futura, mostrar seu resultado em campo próprio.

Na mesma página, oferecer as ações **Liberar**, **Bloquear**, **Revogar sessão**, **Reemitir código**, **Transferir aparelho** e **Ver auditoria**. Cada ação precisa manter autorização administrativa, CSRF, confirmação recente e comparação transacional do alvo exato já empregados no painel. Uma ação Android deve filtrar `productId` e `applicationId` e não atingir licenças ou sessões Suite/EmulationStation Windows do mesmo comprador. Revogar uma sessão antiga não pode encerrar outra criada depois.

O estado “online” deve usar o TTL e o último contato da sessão Android, não o limiar de 15 segundos do cliente Windows. “Sem contato recente” não significa logout voluntário. Quando o cliente solicitar troca de telefone, preservar compra e histórico, revogar o vínculo antigo e emitir o novo código apenas pela política aprovada. A página não deve expor IMEI, MAC, chave privada, token de sessão, código de ativação ou URL privada de jogo.

## Bloqueios para ligar a versão comercial

- O servidor ainda não forneceu rotas implementadas, OpenAPI final, URL HTTPS, chave pública/keyId e licença sintética. O APK candidato mantém a flag comercial desativada.
- O frontend de jogos/downloads é nativo compilado; `GuiStore.cpp` e o ponto de chamada de download não estão disponíveis entre os fontes ativos encontrados. `StationContent` está compilado, mas a tela nativa ainda usa o catálogo e os links embarcados. Precisamos recuperar esse fonte ou identificar um ponto de integração nativo estável. Alterar só o tema ou simular toques não conecta a autorização por jogo.
- A saudação com `displayName` está no cliente Java, mas o cabeçalho nativo ainda não a lê. Integrar por ponte nativa após receber `/me`.
- O candidato foi compilado e assinado, mas não foi instalado nem homologado com servidor. Nenhum comportamento comercial foi declarado validado no telefone.
- Antes de vender, definir certificado de assinatura de produção compatível com futuras atualizações sem apagar dados do APK instalado.

Condição de aceite: após o servidor disponibilizar homologação, recompilar com `StationConfig.ENABLED=true` e valores reais, ligar o catálogo e o botão Baixar à ponte nativa, e só então validar compra sintética, ativação, retorno de emulador, bloqueio, transferência, catálogo, download e preservação dos dados existentes. Nenhum APK de homologação deve ser promovido a estável antes dessa conferência.
