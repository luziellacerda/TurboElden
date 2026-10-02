# Cliente Station e integração de login

Esta revisão conecta o layout atual de login ao cliente Station reconstruído. O controlador consulta sessão, perfil, catálogo e capas diretamente nas rotas do Servidor-pix. A senha local foi retirada destes fontes.

**A integração do catálogo nativo e o APK completo ainda não estão concluídos. Esta revisão não é uma versão estável e não foi instalada no aparelho.**

## Documentação

- [Continuação do aplicativo](HANDOFF-RECONSTRUCAO-TURBOSTATIONS.md).
- [Contrato necessário no servidor](HANDOFF-SERVIDOR-CONEXAO-E-INSTALACAO.md).
- [Handoff publicado no Servidor-pix](https://github.com/luziellacerda/Servidor-pix/blob/6a8fb3663ba40a53e4179f799e756b71a7398a8e/docs/station-android/HANDOFF-CLIENTE-RECONSTRUIDO-STATION-20261002.md).
- [Resultados das 142 verificações locais](evidence/test-results.json).

## Compilação

Execute com Python 3: `prepare_test_dependency.py`, `run_tests.py` e `build_module.py`. O build usa por padrão `E:\ESTUDO APK\work\turbostations-reconstruction-20261002\build`; a dependência de testes fica na pasta `tools` da mesma raiz em E:. As variáveis `STATION_BUILD_DIR` e `STATION_TOOLS_DIR` permitem outros destinos explícitos. Mantenha ambas em E: neste computador.

Requer JDK 17, Android SDK API 34 e D8 nos caminhos registrados nos scripts. A compilação gera AAR, DEX independente e pacote de fontes. Os binários não estão no Git. O módulo não deve ser simplesmente acrescentado ao APK existente: faltam a ligação nativa e a retirada das classes substituídas.

`StationAndroid.get(context)` mantém uma instância por processo. `StationCoordinator` é o ponto de entrada para login e biblioteca. `auth/LoginActivity` preserva o layout observado e usa `auth/StationLogin` para consultar o controlador fora da thread visual. Operações de rede e arquivo devem ocorrer em uma thread de trabalho.

## Preservação

APK de entrada, versão estável, emuladores, vídeos, ROMs e saves permaneceram intactos. Os testes utilizam respostas e chaves sintéticas; não comprovam o fluxo completo contra produção ou a execução no Android.
