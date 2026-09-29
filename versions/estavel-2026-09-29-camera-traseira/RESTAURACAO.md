# Identificar, restaurar e compilar

## 1. Identidade antes de qualquer troca

Leia ../../ESTAVEL.md. O APK congelado é:

`E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira\TurboramaStation-ESTAVEL-6727ab7-camera-traseira.apk`

SHA256: `54681d24d4ae912c0d081b276064264f95ad5e1d41e4e2851d2daa87169c4257`.

Confirmar com `Get-FileHash -Algorithm SHA256 -LiteralPath 'caminho-completo-do-apk'`. Uma recompilação pode mudar o hash do ZIP/assinatura; ela não substitui o APK congelado para uma restauração exata.

## 2. Instalar exatamente o APK preservado

Com o aparelho autorizado, sair da emulação pelo próprio menu e ficar nas plataformas. Selecionar o aparelho correto pela lista `adb devices`. Usar `adb -s SERIAL install -r 'caminho-completo-do-apk'`. Nunca executar uninstall, clear ou apagar a pasta EmulationStation. A instalação não deve interromper uma partida ativa.

ADB deste computador: `C:\Users\Admin\Documents\Codex\2026-09-28\turboramaemutestes-apk-e-estudo-apk-work\work\android-tools\platform-tools\adb.exe`. Definir `ADB_USB_LEGACY=1` no ambiente desta sessão, se necessário.

## 3. Recuperar os fontes do Git em uma pasta nova

```powershell
& 'C:\Python314\python.exe' '.\restaurar_fontes.py' --destino 'E:\ESTUDO APK\restauracoes\estavel-2026-09-29-camera-traseira'
```

Executar dentro desta pasta da versão no clone. O comando materializa `implementation/`, descomprime os dois cabeçalhos grandes e confere os hashes. Recusa sobrescrever uma pasta existente. Não instala aplicativo nem copia chaves. Não executar o código diretamente de snapshot/: os cabeçalhos grandes ainda estão comprimidos ali.

## 4. Compilação original neste computador

A pasta de trabalho ativa original é `E:\ESTUDO APK\work\native-carousel\implementation`. Os comandos de montagem são:

```powershell
$env:PYTHONUTF8='1'
Set-Location -LiteralPath 'E:\ESTUDO APK\work\native-carousel\implementation'
& 'C:\Python314\python.exe' '.\build_native.py'
if ($LASTEXITCODE -ne 0) { throw 'Falha na compilação nativa' }
& 'C:\Python314\python.exe' '.\package_apk.py' --full
if ($LASTEXITCODE -ne 0) { throw 'Falha no empacotamento' }
```

**O APK congelado já está preservado em `E:\ESTUDO APK\estaveis\2026-09-29-camera-traseira`. Não usar essa pasta como saída de compilação.** O empacotador atual usa o mesmo nome de saída camera-traseira.apk; não substituir inadvertidamente a referência de restauração. Não executar estes comandos apenas para instalar a versão já pronta.

Ao usar os fontes recuperados em uma pasta nova, substituir o Set-Location acima por aquela pasta e conferir os caminhos absolutos das ferramentas e da base no código. Os scripts originais foram preservados, não tornados portáteis silenciosamente.

Dependências locais:

- Python: `C:\Python314\python.exe` (Pillow; NumPy para regenerar o modelo).
- Clang: `C:\Program Files\LLVM\bin\clang.exe`.
- JDK: `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot`.
- SDK Android: `G:\Android\Sdk\platforms\android-34\android.jar`.
- Build tools: `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15`.
- Apktool: `E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar`.
- Base privada: `E:\ESTUDO APK\work\native-carousel\implementation\stable-reference-audit\original-1.0.8-alignment-preserved.apk`, SHA256 `5cd234d0ac57aa6f1b260db6278087b7d961c671385ecf47871570bc00e78814`.
- Identidade de assinatura existente: `C:\Users\Admin\.android\debug.keystore`, mantida privada. Certificado SHA256 `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

Os cabeçalhos e metadados necessários à compilação estão congelados. Não rodar prepare.py nem baixar novamente o catálogo para restaurar esta versão: esses processos usam fontes externas/históricas e podem gerar outro conteúdo. build_native.py gera os shaders a partir dos fontes locais e pode regenerar o atlas se seus insumos forem mais recentes; manter a cópia preservada do header para recuperação por hash.

O pacote original privado é necessário: esta publicação não recuperou o C++ original completo dos motores ou do frontend. Builds futuros só podem ser chamados de nova versão estável após pedido do mantenedor. A tag desta entrega não deve ser movida.
