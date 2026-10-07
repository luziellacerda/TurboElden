# SERVIDOR → APP: proteção Station compatível — 07/10/2026

## Fonte e estado

Base Android publicada: 029612b06205ff66cc1c7dcb2a2dd1a4c47aa1f9. Composição congelada: R55/9d3d45f + visual R57/8980cd4 + prontidão f8b019d + acesso automático 1e0f862. Servidor implementado em defd38201ccbe331b2c0761c8e24dc4e47aef3ee, base 8d9c670; publicação Linux aguardando autenticação nativa, ainda não comprovada neste recibo. Consultar STATUS e retorno específico do servidor para o estado posterior.

APK privado base R57 SHA256 e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566; certificado 7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825; pacote org.turboramastation.frontend. URL, pin TLS e assertionKeyId atuais permanecem. Chave RSA principal turborama.station.device.v1 e licenseId não mudarão. App antigo permanece compatível no servidor.

## Contrato aditivo implementado nas fontes

1. Desafio de ativação/sessão continua assinado pelo servidor e traz security: requestProofVersion=1, keyAttestation=true, requireVerifiedApp, attestationChallenge e serverTime. Validar a assinatura e desafio derivado antes de gerar chave secundária.
2. Envelope tradicional mantém payload/signature RSA. Payload assinado oferece requestProof=rsa-pss-v1 ou ec-p256-v1, requestProofKey quando EC e allowUnverifiedApp explicitamente se a política permitir fallback. Envelope EC adiciona attestationChain (DER/base64url) e attestationKeySignature: a chave secundária também assina o mesmo payload do desafio de uso único. Corpo externo até64 KiB apenas em activations/complete e sessions; payload interno até8 KiB.
3. Servidor assina sessão com requestProof, verifiedApp e serverTime. Cliente ancora o relógio no serverTime assinado e elapsedRealtime; não depende do relógio de parede do telefone. verifiedApp=true exige pacote/certificado original, cadeia Google, revogação disponível, hardware e boot verificado. Sem essa validação nunca marcar autenticidade do APK.
4. Em cada pedido autenticado, header X-Station-Request-Proof contém v1.timestamp.nonce.signature. Nonce16bytes aleatório e assinatura RSA-PSS/SHA256 ou ECDSA P256 DER. Timestamp ±90s; repetição 409; header/assinatura ausentes ou inválidos 401. O servidor vincula método/rota+query/corpo/credencial e guarda nonce somente após a assinatura válida.

Texto canônico UTF8, com newline após todos os campos:

```text
TurboRamaStationAndroid/request/v1
METHOD
/v1/station/rota?query=exata
sha256_hex_minusculo_do_corpo_ou_vazio
sha256_hex_minusculo_da_credencial_ASCII
unix_seconds
nonce_base64url
```

Para covers/catalog/me/artifacts/download-authorizations e online, assinar o corpo JSON exatamente como transmitido e a rota exata. Nenhum hash da ROM é acrescentado. A implementação central no Session/Transport usa nonce novo em cada retry/renovação. Para WSS, assinar GET /v1/station/online/relay, corpo vazio e a credencial ticket, sem query: o ticket segue Authorization como antes. StationOnlineClient coloca a prova somente em room.relay.requestProof; StationRetroLaunch transfere relayRequestProof pelo arquivo privado de uso único; Tunnel manda o header. Não enviar bearer da sessão ao processo do motor nem assinar frames.

## Proteção persistente e recuperação

Migrations031/032 guardam request_proof_required/verified_app_required por vínculo e modo/chave na sessão. Flags só sobem em transação com licença bloqueada; sessão anterior é revogada ao renovar. Tentativa assinada de reduzir proteção retorna403 STATION_SECURITY_DOWNGRADE_DENIED. Vínculo de novo aparelho continua pelo painel, regras financeiras e uma licença por aparelho simultâneo. Não limpar dados nem trocar o alias RSA para escapar da proteção. APK anterior no mesmo vínculo pode exigir atualização ou retorno coordenado do backend.

Política global RequireVerifiedApp=false mantém clientes anteriores e fallback assinado dos modelos ainda não qualificados. Logo, não prometer “somente nosso APK” enquanto esse estado continuar. Após dois telefones qualificados, examinar a base instalada e recuperação antes de ativar a exigência global. App original em aparelho comprometido/operado pelo próprio usuário não é uma fronteira absoluta; os direitos continuam limitados à licença.

## Catálogo, mídia e desempenho

metadata=1 agora recebe objeto com strings vazias quando não há sinopse; o app existente rejeita metadata:null. IDs, catálogo rev14/2212, capas e quatro motores permanecem. Não chamar índices privados nem construir URLs pelo nome de ROM: usar itemId/coverId, descritor assinado e grant de uso único atuais. Capas quatro simultâneas, buffer/downloads e preparador permanecem. A prova calcula hash só do corpo de controle, nunca do jogo.

## Gates e entrega PC

190 Java8/API34 compilaram usando o cliente novo como classpath das salas. Integração Java real/API C# passou: ativação, 21 pedidos protegidos, renovação, catálogo, perfil, quatro capas e download exato. Servidor:28 negativas/positivas HTTP/WSS, replay, corpo/rota/chave/token e bytes bidirecionais passaram em PostgreSQL temporário; regressões emissão/bloqueio/transferência/revogação/financeiro passaram. Cliente anterior:75+13+41+180 checks passaram. Cadeias hardware reais e Google-status de produção não foram qualificadas em telefone.

Receitas build_candidate.py/package_candidate.py desta pasta produzem os dois DEX juntos e exigem o APK exato R57, SDK/D8/classpath original e assinatura original. Runtime 899e35279cf046242a7ae31f502078080bd6a94404770fe99e1e2e90be58a1ef é o já compilado de senha automática, não um novo motor; cores e controles preservados. Confere alinhamento16KiB, todas as outras entradas e duplicação de classes entre DEX. Gates sintéticos/recusa de api-check-only passaram; não são um APK real.

Teste físico: atualizar ambos sem limpar dados, conferir sessão antiga→protegida, capas quatro por vez, download/renovação, nome dos dois na sala, Pronto, entrada automática, inputs, saída/retorno e reconexão. Registrar pacote/versionCode/certificado, modo protegido e verifiedApp, modelo/SDK/boot e certificado recusado quando houver fallback. Não registrar tokens/códigos/senhas/cadeia contendo identificadores pessoais em Git. Novo DEX/APK, assinatura/instalação e gameplay continuam pendentes no PC de produção.
