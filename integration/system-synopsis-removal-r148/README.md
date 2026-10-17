# R148 — remoção das sinopses dos sistemas

Preparação limitada à tela nativa do carrossel. A R147 usa o cabeçalho R132
`r132_native_info.h` no `libturbo_carousel.so` preservado. Em `updateSystemInfo`,
somente o ramo `systemsMode` deixa de fornecer `SystemInfo.description` ao
componente de texto. O título do sistema, botão e seleção permanecem. O ramo
dos jogos continua a escolher a sinopse do servidor ou do catálogo local; o
ramo das coleções e as sinopses nas salas online Java permanecem intactos.

`recipe/prepare_overlay.py` lê o cabeçalho privado R132 com SHA-256
`e6c910b188018146a394ff2128f9f82144afcbe46d0bd3924d09b200661c5c75`,
confere os três ramos, altera uma linha e faz a inversão integral. Escreve um
novo `r132_native_info.h` e recibo em diretório novo. A receita não altera a
fonte privada original nem o APK e não declara compilação, instalação ou teste
visual. A inclusão deve preceder o diretório do cabeçalho R132 na próxima
compilação do carrossel; reproduzir primeiro o binário R147
`2e15a9a330c2562c71574921f5558d6142e3051bba64a315434e5714f38908a9`
e manter os demais inputs, opções, assinatura e entradas APK.

Exemplo de preparação em diretório privado novo:

```text
python -B integration/system-synopsis-removal-r148/recipe/prepare_overlay.py \
  --r132-native-info <R132/native/overlay/native/r132_native_info.h> \
  --out <R148/overlay-synopsis>
```

O conteúdo preparado deve entrar como primeira pasta `-I` na etapa produtiva
do carrossel. A publicação exige nova compilação, comparação de entradas do
APK, assinatura e instalação/teste físico. Não reutilizar um kit de motores de
outra revisão como prova de cadastro no servidor.
