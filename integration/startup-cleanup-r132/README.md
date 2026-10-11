# R132

Esta composição usa a R131 corrigida como donor exato. O estado e os recibos finais ficam em `versions/station-startup-cleanup-r132-20261011`, fora do conjunto produtivo congelado.

## Ordem de reprodução

1. `recipe/build_native.py` reproduz os dois nativos R131 por hash antes de compilar os overlays de loading e sinopses.
2. `recipe/build_switch_payload.py` decodifica o DEX8 real, aplica apenas as âncoras de `SwitchConfigPatcher` e verifica os conjuntos de classes e as classes não autorizadas antes/depois.
3. `recipe/build_runtime_identity.py` verifica o donor e as duas compilações, conserva cores/opções/perfis e renova somente os quatro IDs afetados pelo bundle compartilhado.
4. `recipe/assemble_apk.py --write-freeze` congela sete payloads. A montagem substitui somente esses sete arquivos, sem adições, e confere cada arquivo preservado.
5. `tooling/release/finalize_verified.py` exige o certificado original, alinhamento16KiB e `recipe/verify_final.py` antes de promover o APK final.

Fornecer sempre o commit executável explícito e os inputs privados preservados no backup único. Não selecionar arquivos pela data, usar receitas históricas como fallback, modificar fontes durante o build ou passar recibos sanitizados ao operador do servidor.

## Limites

Preparar os shaders no loading não elimina o tempo do driver. A migração Switch conserva qualquer caminho customizado ou legado com conteúdo; não remove diretórios. PS3/4 permanecem offline. Testes de compilação, instalação, preparo, ativação de servidor e gameplay têm evidências distintas.
