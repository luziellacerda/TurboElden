# R167 — capas vizinhas 10% mais largas

A R167 usa como doador **somente** o APK R166 PSX assinado, SHA-256
`4872f6dd0fef24930568c00c535a63afb66253f20a9c6a636627cadc52e71d6d`.
A capa grande selecionada, sua posição, a altura das capas vizinhas e os
botões permanecem como na R166. A largura das capas menores na seleção de
jogos aumenta exatamente 10% nos estilos normal, diagonal e projetado. A tela
de sistemas não muda. Desenho, toque e mapeamento da arte usam o mesmo
`coverSlot`; não há segundo desenho, temporizador, thread ou alocação nova.

O compilador nativo aceita apenas os 14 cabeçalhos exatos do recibo R165 e
permite alterar `native_formation.h`. A montagem da R167 muda exatamente
cinco entradas entre as 13.861 do APK R166:

- `lib/arm64-v8a/libturbo_carousel.so`;
- `assets/station-online/engines.json`;
- os três marcadores de identidade PSX, N64 e Dolphin.

`classes35.dex` da R166, incluindo o reparo PSX, todas as demais 39 partições
DEX, as bibliotecas executáveis, o AndroidManifest, os modos e as políticas
online permanecem byte a byte iguais. As identidades dos quatro motores online
precisam ser renovadas porque o manifesto assinado vincula também o carrossel
ao payload. Essa renovação **não** altera a lógica N64; o servidor precisa
cadastrar os novos IDs R167 antes de uma partida online com este APK.

## Compilar sem copiar APK para Git ou C:

Use um commit revisado que contenha as quatro fontes produtivas desta receita.
Não execute com fontes modificadas depois do commit. Mantenha a R166 intacta.
Os diretórios de saída `native`, `package` e `final` devem ser novos; o
assinador precisa de cerca de 6 GB livres em F: depois da montagem do APK sem
assinatura. Confira o espaço antes de cada etapa. O APK não entra no Git.

```powershell
$revision = '<SHA_COMPLETO_DO_COMMIT_R167>'
$tools = 'F:\TurboStations-Backup-Completo-20261011\ferramentas'
$base = 'D:\StationPsxDependencyR166-20261015\final\TurboStations-Premium-R166-psx.apk'
$native = 'E:\StationNeighborWidthR167-20261015\native'
$package = 'F:\StationNeighborWidthR167-20261015\package'
$scratch = 'F:\StationNeighborWidthR167-20261015\scratch'
$final = 'F:\StationNeighborWidthR167-20261015\final\TurboStations-Premium-R167-combined.apk'

python -B .\integration\game-selection-neighbor-width-r167\recipe\build_native.py `
  --out $native

python -B .\integration\game-selection-neighbor-width-r167\recipe\package_candidate.py `
  --base $base --native "$native\libturbo_carousel.so" `
  --ndk "$tools\ndk-r28c" --source-commit $revision --out $package

New-Item -ItemType Directory -Path $scratch -Force | Out-Null
python -B .\integration\game-selection-neighbor-width-r167\recipe\sign_private.py `
  --package $package --scratch $scratch --final $final
```

O recibo do pacote deve indicar cinco entradas alteradas, 13.856 preservadas,
40 partições DEX preservadas e quatro novas identidades. A prova final fica em
`$package\final-apk-proof.json`. O assinador verifica o certificado original,
assinaturas v2/v3 e alinhamento ZIP de 16 KiB, e apaga apenas o APK alinhado
temporário que criou. O APK assinado e a R166 de base ficam preservados.

Após a prova final, atualizar o instalador fixo para o usuário poder instalar
sob demanda em qualquer telefone USB, preservando dados:

```powershell
python -B .\tooling\usb-installer\publish_current_installer.py `
  --apk $final --proof "$package\final-apk-proof.json"
```

Enviar ao servidor somente o kit privado R167 sem APK, chave ou dados de
telefone. Pedir recibo **aplicado** e conferir a consulta pública dos quatro
IDs antes do teste físico PSX. A R167 substitui a entrega R166 ainda não
implantada; se o servidor já tiver aplicado a R166, registrar a R167 como
evolução aditiva sem desfazer o estado anterior. Não declarar estável antes
da partida real PSX em dois aparelhos na mesma R167.

```powershell
python -B .\integration\game-selection-neighbor-width-r167\recipe\package_server_kit.py `
  --apk $final --base-apk $base --package $package `
  --native "$native\libturbo_carousel.so" `
  --prior-kit 'E:\StationPsxDependencyR166-20261015\server-kit\Kit-Servidor-TurboStations-R166-Independentes.zip' `
  --app-repo 'E:\StationN64DexRecipeR165-20261015\app' `
  --out 'E:\StationNeighborWidthR167-20261015\server-kit'
```

O resultado é `Kit-Servidor-TurboStations-R167-Independentes.zip` e seu
recibo. O empacotador confere o APK assinado contra o doador R166, os cinco
arquivos alterados, 27 ELF, políticas e dependências preservadas, e recusa
qualquer APK dentro do ZIP. Publicar o kit apenas no Git privado.
