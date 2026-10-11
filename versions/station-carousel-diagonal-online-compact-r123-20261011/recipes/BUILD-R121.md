# Receita R121 — base final R120

Estado: prepare, compile e package concluídos. APK instalado no Motorola com SHA integral e dados preservados; tela Sua sala observada. Fluxo completo, resolução do ANR e gameplay ainda não validados fisicamente.

## Identidades fixas

- Base APK R120: SHA256 d18c50da17b669373a183ba334e23f356c0521dfb3a2bac69301e8f10b9cbbe1, 2217065864 bytes.
- Manifesto: c4e9a6d69497bb928f53b35b49bef86d1b57a0b2b0bd5d0aa1953cfd5d9752a4. Já contém StationComponentFactory; permanece byte a byte idêntico. Nenhum patch do factory é executado na R121.
- Java baseline: 232 fontes R120. Fontes novas autorizadas podem ser adicionadas; o conjunto final deve corresponder exatamente ao manifesto congelado.
- Manifesto Java R120: 696453467a9ff0957ab266977158afe02c986364b8496fb3c76c3503b24fbc8a.
- Manifesto nativo R120: e431941e92243170eaff3e12595cf2d4640ba97304c012031800fcdabab21c7f.
- Recibo de compilação R120 herdado: 82f9a3fee527cdc56afdc34da5be058bbecdff439de6c47b4a279c2020168424.
- build.py: SHA256 5f4ecf6f19b39b0d8e068ee53b0fbe5243c302cbf2ffa44ec11a2c46ae1c78b8, 29899 bytes.

## Entradas permitidas

Somente classes28.dex, classes35.dex e lib/arm64-v8a/libturbo_carousel.so podem ser substituídas. DEX35 e carrossel devem conter a revisão; DEX28 pode permanecer idêntico caso não existam alterações no módulo client. Não se modifica código artificialmente para mudar esse hash.

Frontend recompilado deve ser idêntico à R120, mas não entra na lista de substituições. Todas as outras entradas do APK, incluindo Manifest/engine registry/runtime/recursos/assets/mídias, são comparadas byte a byte. Certificado original, assinaturas v2/v3 e alinhamento de 16 KiB são exigidos. A conferência AAPT exige a árvore inteira do manifesto idêntica, incluindo Application e factory.

native/d1/native_pause_menu.h é fonte pública nesta revisão. Deve existir na cópia atual: a receita recusa restaurar esse header da base privada. A exceção específica em .gitignore preserva a privacidade dos demais inputs de native/d1/. Objetos de mídia e stubs permanecem fixados pelos hashes R120.

## Procedimento

1. Encerrar alterações autorizadas e congelar JAVA-SOURCE-MANIFEST.json e CAROUSEL-INPUT-MANIFEST.json.
2. Usar os argumentos locais de recipes/build-r121-arguments.json, ignorados pelo Git e sem senhas. Eles apontam à base R120, trabalho E:, montagem/final G: e inputs privados da compilação final R120.
3. Executar --prepare, depois --compile, e por último --package. Na fase package, adicionar os argumentos packageOnly e fornecer as senhas somente pelas variáveis de ambiente selecionadas.
4. Ler evidence/build-r121.json e evidence/package-r121.json. Recibos desta receita começam com instalação/conferência física/gameplay falsos; instalação é uma etapa posterior autorizada.

A receita recusa fontes, manifestos ou ferramentas alterados entre fases, substituições adicionais e sobrescrita do APK base/final. Não opera telefones, servidor, rede, licenças ou saves. Não executa testes automaticamente.
