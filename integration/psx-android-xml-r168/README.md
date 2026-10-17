# R168 — correção delimitada da preparação XML do PSX online

Esta receita parte **somente** do APK R167 assinado, SHA-256
`dd6f8f8131cf5ee55d450c60e0b08963a662dc6cad092588f0db50153badd978`.
A fonte corrigida pelo servidor está em
`integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxLaunch.java`,
SHA-256 `bb045d8113c6ca7887a26c79b066a74ca79ad7f340d7032cf9399006db14ad4b`.
O método anterior falhava no framework XML do Android antes de abrir o núcleo PSX.
A fonte nova usa SAX com entidades externas recusadas e aceita os elementos
irmãos da configuração real do EmulationStation. A prova no Android está em
`integration/psx-android-xml-20261015/README.md`; ela não é gameplay.

O build altera exatamente `StationPsxLaunch` e adiciona sua classe interna
`StationPsxLaunch$1` em `classes35.dex`. As outras 607 classes da partição
mantêm a mesma projeção smali; as demais 39 partições DEX ficam byte a byte
iguais. N64, Dolphin, frontend, carrossel R167, pontes, núcleos, opções,
controles, recursos e manifesto permanecem iguais. O vínculo do payload exige
atualizar `engines.json` e os três marcadores de identidade; são cinco entradas
alteradas no APK e 13.856 preservadas. Os quatro IDs resultantes precisam de
cadastro aditivo no servidor antes da partida, sem repetir o operador R167.

Congele estas receitas em um commit antes do build e passe seu SHA completo em
`--source-commit`. As receitas conferem hash de fonte e ferramentas e recusam
saídas preexistentes. O APK, chave e logs privados ficam fora do Git.

```powershell
$revision = '<SHA_COMPLETO_DO_COMMIT_R168>'
$tools = 'F:\TurboStations-Backup-Completo-20261011\ferramentas'
$jars = 'F:\TurboStations-Backup-Completo-20261011\desenvolvimento\reconstrucao-atual'
$donor = 'F:\StationNeighborWidthR167-20261015\final\TurboStations-Premium-R167-combined.apk'
$root = 'F:\StationPsxXmlR168-20261015'

python -B .\integration\psx-android-xml-r168\recipe\build_dex.py `
  --donor $donor --jdk-bin "$tools\jdk17\bin" `
  --android-jar "$tools\android-34\android.jar" `
  --d8-jar "$tools\android-build-tools-35\lib\d8.jar" `
  --apktool "$tools\apktool_3.0.3.jar" `
  --rooms-jar "$jars\rooms.jar" --client-jar "$jars\client.jar" `
  --source-commit $revision --out "$root\dex"

python -B .\integration\psx-android-xml-r168\recipe\package_candidate.py `
  --base $donor --dex-dir "$root\dex" --ndk "$tools\ndk-r28c" `
  --source-commit $revision --out "$root\package"

New-Item -ItemType Directory -Path "$root\scratch" -Force | Out-Null
python -B .\integration\psx-android-xml-r168\recipe\sign_private.py `
  --package "$root\package" --dex-dir "$root\dex" `
  --scratch "$root\scratch" `
  --final "$root\final\TurboStations-Premium-R168-psx.apk"
```

`dex/dex-receipt.json`, `package/unsigned-package.json` e
`package/final-apk-proof.json` comprovam os três estágios. O assinador original
confere certificado, v2/v3 e alinhamento de 16 KiB, e escreve o APK final uma
vez. Exige espaço livre no volume F: para o pacote unsigned, alinhado e assinado.
Não executar assinatura antes de revisar os recibos; não instalar R168 sem o
cadastro aplicado e a escolha do usuário.

Após prova final, atualizar o instalador fixo com
`tooling/usb-installer/publish_current_installer.py --apk <APK_FINAL> --proof <FINAL_APK_PROOF>`.
Esse publicador não instala automaticamente. Entregar ao servidor o kit privado
independente montado **a partir do APK final**; não enviar APK, chaves ou dados
dos telefones ao Git. Testar Capcom vs. SNK Pro em dois aparelhos R168 e
registrar primeiro quadro, som, controles independentes e saída do anfitrião.
