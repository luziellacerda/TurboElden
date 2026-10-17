## Candidata R170 compilada em 17/10

O backup privado foi recebido. O atualizador e as correções PSX estão no APK
R170 assinado; cadastro, implantação e testes físicos continuam pendentes.
Leia [o recibo atual](../../docs/server/r170/README.md). O texto de preparo
abaixo é histórico e não exige receber novamente o backup.

# Atualizador interno protegido do TurboStation

Implementação de fonte preparada, com backend no Servidor-pix. **Ainda não
incluída em APK de produção nem ativada no serviço.** A primeira montagem
precisa da base privada atual e da assinatura original.

Contrato, segurança, operação e provas: [documentação consolidada](../../docs/server/updates-20261017/README.md).

## Integração

- `java/`: sete classes de atualização, tela, serviço e callback privados.
- `recipe/patch_sources.py`: acrescenta hooks aos `StationApi.java`,
  `StationHttp.java` e `StationAndroid.java` **atuais**, preservando o restante.
- `recipe/compile_overlay.py`: compila esses hooks e classes com commit
  congelado/dependências reais; produz overlay, não APK nem partição completa.
- `recipe/merge_manifest.py`: merge no Manifest atual decodificado, com
  versionCode crescente e SDK preservado; usar o empacotador privado existente.
- `SCOPED-TYPES.json`: dez famílias permitidas, incluindo suas classes internas
  e sintéticas. Descobrir partições atuais e preservar todo o resto. Nunca
  empacotar as fixtures nem acrescentar classes duplicadas em outro DEX.
- `tests/`: testes isolados e uma fixture de superfície do painel somente para
  compilação. Nenhum desses arquivos entra no app.

As correções PSX já presentes em `integration/psx-online` precisam acompanhar
a primeira nova compilação. Preservar R169/XML/CAS, assinatura, licença,
configurações, jogos/saves e SDK. Alterações de DEX/Manifest renovam as
identidades conforme os fingerprints efetivos; entregar o kit final exato e
cadastrá-lo antes de publicar um APK para atualização.

O toque no aviso inicia download e preparação. Esta implementação mantém a
confirmação do Android para a instalação. Emissão e GET usam a sessão/prova
existentes, grant60s de uso único, origem HTTPS pinada e APK privado. Não são
utilizados root, senha do painel ou caminho público fixo de APK.
