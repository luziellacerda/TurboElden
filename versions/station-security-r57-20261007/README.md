# Station: proteção de pedidos sobre R57 — 07/10/2026

Leia [HANDOFF-SEGURANCA-STATION-20261007.md](HANDOFF-SEGURANCA-STATION-20261007.md) e [STATUS.json](STATUS.json).

Este overlay compõe o cliente R55, visual R57, prontidão e entrada automática já publicados. Mantém licença/Keystore RSA, jogos/saves, capas quatro por vez, transferências, cores, controles e layout. Adiciona prova por pedido HTTP e abertura do relay WSS, mais chave EC opcional com atestação Android verificada pelo servidor. Não assina frames de jogo nem acrescenta verificação de ROM.

190 fontes compilaram Java8/API34; cliente Java real e API candidata se comunicaram em PostgreSQL isolado. Regressões de catálogo/capas/transferências e negativas de segurança passaram. Novo DEX/APK, assinatura, instalação e qualificação hardware continuam pendentes no PC Windows.

## Produzir no PC

1. Restaurar o repositório com os snapshots irmãos `station-current-r55-20261006`, `station-layout-r57-20261006` e `station-auto-room-access-r57-20261006`. Preservar os snapshots recebidos.
2. `python recipes/build_candidate.py --output <novo-diretorio-em-E>`: exige SDK34, classpath original e D8 pelos hashes de produção; compila cliente novo/DEX28 e salas/DEX35 usando o novo cliente como classpath. `--api-check-only` compila e não pode gerar APK.
3. `python recipes/package_candidate.py --workspace <novo-diretorio-em-E> --output-apk <novo-APK> --keystore <assinatura-original> --ks-key-alias <alias> --ks-pass-env <variavel-privada>`: exige APK R57 e6159fa3/certificado 7b16ee1a, substitui somente DEX28, DEX35, runtime auto-password 899e3527 e engines.json. Confere classes declaradas em todos os DEX, entradas preservadas e alinhamento 16 KiB. Não passar senha na linha de comando nem publicar assinatura privada.
4. Atualizar ambos os aparelhos sem desinstalar ou limpar dados; registrar licença/saves preservados, quatro capas, download, renovação, sala, senha automática, inputs e retorno. Conferir `verifiedApp` em resposta assinada e negativas de credenciais copiadas.

A política global do servidor continua compatível. Não ligar `RequireVerifiedApp` antes de qualificar todos os aparelhos necessários. Há aparelhos com cadeias antigas expiradas/sem hardware atestado: o verificador atual é estrito e nesses casos permite prova RSA compatível enquanto a política estiver desligada. Atestação hardware não foi testada em telefone aqui.

`recipes/` tem as novas receitas; não aplicar empacotadores R41/R55 ou apenas o DEX35 anterior sobre esta composição. `evidence/` distingue compilação API, integração real JVM/API e gates sintéticos do empacotador. Nenhum APK, ROM, BIOS, save, chave privada ou dado de cliente está neste delta.
