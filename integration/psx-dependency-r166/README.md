# R166 — correção delimitada da abertura PSX online

Esta receita parte **somente** do APK R165 assinado, SHA-256
`9e7ab2441e9d75568d5d2b741b4a0ed42e9a2d9f823698c0f39dccdcb7c19145`,
com 2.715.466.850 bytes e 13.861 entradas. A mudança produtiva permitida é
`StationPsxLaunch` em `classes35.dex`. Ela não recompila N64, Dolphin, frontend,
carrossel, recursos, outros DEX, núcleos nem pontes online/offline.

O mapa de identidade R165 vincula o hash de `classes35.dex` aos três marcadores
de runtime. Por isso, mesmo uma correção só da classe PSX exige atualizar os
marcadores PSX, N64 e Dolphin e os quatro `engineId` em
`assets/station-online/engines.json`. São **cinco entradas** alteradas e 13.856
preservadas byte a byte; as 39 outras partições DEX também são preservadas.
As políticas, opções, dependências e descritores dos motores ficam iguais.
Os novos IDs exigem cadastro aditivo no servidor antes de testar salas R166.
Os IDs R165 e o APK R165 continuam disponíveis para retorno.

Esta pasta contém somente receitas. Não contém APK, chave, senha, ROM ou kit
privado. As três etapas abaixo foram derivadas das receitas R165, mas exigem
o doador R165 e têm recibos R166 próprios. **Não executar as receitas R165 com
seus hashes antigos.** Não declarar partida Android validada pelo build.

## Preparação

Congele em um único commit a fonte PSX corrigida, os testes e estas três
receitas. Passe o SHA completo desse commit em `--source-commit`. As receitas
comparam os arquivos produtivos no disco com o commit antes e depois da
montagem; não há hash do código novo embutido antes do commit. A fonte é
`integration/psx-online/java/org/emulationstation/frontend/netplay/StationPsxLaunch.java`.

As ferramentas pinadas estão em
`F:\TurboStations-Backup-Completo-20261011\ferramentas`: JDK 17,
`android-34/android.jar`, `android-build-tools-35/lib/d8.jar`,
`apktool_3.0.3.jar`, NDK r28c, `apksigner.jar` e `zipalign.exe`.
`rooms.jar` e `client.jar` estão em
`F:\TurboStations-Backup-Completo-20261011\desenvolvimento\reconstrucao-atual`.
O compilador confere os hashes congelados dos sete insumos e três auxiliares.

Antes de gerar APKs, conferir espaço **no momento do build**. A montagem cria
um APK sem assinatura de cerca de 2,714 GB; a assinatura cria outro alinhado
e outro final de cerca de 2,715 GB. Usar D: para `package` e `final` (ao menos
5,7 GB livres antes da montagem), F: para `scratch` (ao menos 3,0 GB livres)
e E: apenas para o DEX pequeno. O assinador exige saída final no mesmo volume
do pacote e pasta scratch separada. Não colocar APK temporário em C: nem
duplicar o R165; nunca remover os APKs existentes para abrir espaço sem uma
decisão explícita sobre seus backups.

## 1. DEX35 de uma classe

Em PowerShell, no diretório do repositório:

```powershell
$revision = '<SHA_DE_40_CARACTERES_DO_COMMIT_R166>'
$tools = 'F:\TurboStations-Backup-Completo-20261011\ferramentas'
$jars = 'F:\TurboStations-Backup-Completo-20261011\desenvolvimento\reconstrucao-atual'
$donor = 'E:\StationVisualR165Combined-20261015\final\TurboStations-Premium-R165-combined.apk'
$dexOut = 'E:\StationPsxDependencyR166-20261015\dex'
python -B .\integration\psx-dependency-r166\recipe\build_dex.py `
  --donor $donor --jdk-bin "$tools\jdk17\bin" `
  --android-jar "$tools\android-34\android.jar" `
  --d8-jar "$tools\android-build-tools-35\lib\d8.jar" `
  --apktool "$tools\apktool_3.0.3.jar" `
  --rooms-jar "$jars\rooms.jar" --client-jar "$jars\client.jar" `
  --source-commit $revision --out $dexOut
```

O script requer saída nova ou vazia; decodifica a partição, compila Java 8
com D8 API 26, substitui só `StationPsxLaunch`, remonta e decodifica de novo.
O recibo exige 608 classes, 607 projeções de classe preservadas, mesmo DEX
039 e nenhuma classe adicionada ou removida. Os diretórios intermediários
isolados são limpos após a conferência. Uma falha mantém a saída para análise;
não reutilizar sem resolver o motivo.

## 2. APK sem assinatura e marcadores

```powershell
$package = 'D:\StationPsxDependencyR166-20261015\package'
python -B .\integration\psx-dependency-r166\recipe\package_candidate.py `
  --base $donor --dex-dir $dexOut --ndk "$tools\ndk-r28c" `
  --source-commit $revision --out $package
```

O pacote exige diretório de saída inexistente, reconfere o APK doador, a
fonte congelada, o recibo DEX, as 346 ligações do payload e os contratos ELF.
Recalcula os três marcadores e os quatro IDs sem mudar políticas. Lê de volta
as 13.861 entradas e grava `unsigned-package.json` com todos os hashes.
`classes36.dex`, carrossel, frontend e pontes são travados explicitamente.

## 3. Assinatura original e prova final

```powershell
$scratch = 'F:\StationPsxDependencyR166-20261015\scratch'
$final = 'D:\StationPsxDependencyR166-20261015\final\TurboStations-Premium-R166-psx.apk'
New-Item -ItemType Directory -Path $scratch -Force | Out-Null
python -B .\integration\psx-dependency-r166\recipe\sign_private.py `
  --package $package --dex-dir $dexOut --scratch $scratch --final $final
```

O assinador privado confere novamente todas as entradas, a fonte no commit,
o DEX e seu recibo, o certificado original SHA-256
`7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`,
assinaturas v2/v3 e alinhamento ZIP 16 KiB. Credenciais são obtidas pela
autoridade privada local e não são gravadas no Git ou no recibo. A saída final
é criada uma vez; o script recusa sobrescrevê-la. A prova sai em
`$package\final-apk-proof.json` com o novo SHA, IDs e estado de teste.

Só depois da prova final, atualizar o instalador fixo sob demanda:

```powershell
python -B .\tooling\usb-installer\publish_current_installer.py `
  --apk $final --proof "$package\final-apk-proof.json"
```

O publicador confere hash, tamanho, certificado, v2/v3, 16 KiB e nome do
pacote Android antes de trocar o manifesto. Ele não instala em telefones nem
copia outro APK de 2,7 GB. O EXE existente lê o novo manifesto na próxima
abertura. O usuário escolhe quando e em qual telefone instalar; preservar os
dados e verificar o hash instalado. Registrar separadamente a aplicação dos
quatro motores no servidor e a partida física PSX. Não enviar APK, chave ou
logs privados ao Git.

## 4. Kit privado independente para o servidor

Depois da assinatura, gerar o kit sem APK a partir do mesmo arquivo assinado:

```powershell
python -B .\integration\psx-dependency-r166\recipe\package_server_kit.py `
  --apk $final --package $package --dex-dir $dexOut `
  --prior-kit 'E:\StationVisualR165Combined-20261015\server-kit\Kit-Servidor-TurboStations-R165-Independentes.zip' `
  --app-repo 'E:\StationN64DexRecipeR165-20261015\app' `
  --out 'E:\StationPsxDependencyR166-20261015\server-kit'
```

O empacotador exige o APK assinado, o kit R165 de hash fixado, a prova de
preservação de todas as entradas e as políticas aprovadas. O ZIP contém os
binários e manifestos que o servidor precisa, sem APK, chave ou ROM. Entregar
esse kit pelo Git privado e exigir recibo de cadastro **aplicado** dos quatro
novos `engineId` antes de declarar a R166 pronta para partidas online.
