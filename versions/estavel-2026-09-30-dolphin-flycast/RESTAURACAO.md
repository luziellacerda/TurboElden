# Restaurar esta versão sem confundir pastas

## Identidade exata

Tag: `estavel-2026-09-30-dolphin-flycast`. O manifesto é o inventário verificável dos fontes. Recibos de versões anteriores dentro do snapshot são históricos e não identificam o APK final.

| Conteúdo | Caminho local |
| --- | --- |
| Fontes ativos | `E:\ESTUDO APK\work\native-carousel\implementation` |
| Integração Dolphin | `E:\ESTUDO APK\work\native-carousel\implementation\dolphin-integration` |
| Integração Flycast | `E:\ESTUDO APK\work\native-carousel\implementation\flycast-integration` |
| APK aprovado congelado | `E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk` |
| Saída de compilação aprovada | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Flycast-v2.7-44-retorno-rapido.apk` |
| Base imediata para empacotar | `E:\ESTUDO APK\work\native-carousel\implementation\TurboramaStation-Dolphin-2609-7.apk` |
| Fontes congelados no Git | `versions/estavel-2026-09-30-dolphin-flycast/snapshot/implementation` |
| Candidato não aprovado, somente local | `E:\ESTUDO APK\work\native-carousel\implementation\flycast-integration\experimental\3085-arraste-nao-instalado` |

Para materializar os fontes, execute `restaurar_fontes.py --destino E:\ESTUDO APK\restauracao-20260930` passando o destino entre aspas. O destino deve ser uma pasta nova. O script verifica os hashes, descompacta os fontes grandes e não instala nada. Não copie por cima da pasta ativa sem preservar seu estado.

## Voltar exatamente ao pacote aprovado

Use o APK congelado com SHA256 **55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85** (738.069.339 bytes). Confirme que não há partida em andamento e atualize com a mesma assinatura, preservando dados (`adb install -r`). Nunca desinstale, limpe dados ou substitua saves para restaurar a versão. O APK permanece privado; ele não é um anexo do Git.

## Dependências para reconstruir

A integração própria foi compilada; os motores oficiais foram incorporados de APKs identificados, sem reconstrução integral do C++ deles. O frontend original também depende de base binária privada, pois seu C++ integral não está neste repositório. Por isso, somente clonar não é suficiente e uma nova assinatura/compilação pode produzir hash diferente.

1. Base inicial antes do Dolphin: `TurboramaStation-pesquisa-corrigida.apk`, SHA256 `2cf4758572b98968e4ea3835e055f746e218795c059d71060a89522fedae25e6`.
2. Dolphin oficial 2609-7, commit `5102a0339c2177575378107b76541e47cc52122d`; doador SHA256 `d6b82232433ceed56c8745f3064244e54317a12176d03c96bce9e99d4481d6e9`.
3. Base resultante com Dolphin: `TurboramaStation-Dolphin-2609-7.apk`, SHA256 `5bce795e714ce943d887dd127bfb28c501b8fc55b2f748520348c705ed30dc03`.
4. Flycast oficial v2.7-44, commit `e36e9df2dcc1487acdb1dc7725766f1f5ba029b5`; doador SHA256 `d590819a7282a6487b0411356dfec0af839ca598c3b3dc57d57d0930bda1d5aa`.
5. BIOS locais autorizadas e mídias privadas já usadas, além da mesma chave de assinatura privada. Nunca incluí-las no Git. Licenças e proveniência dos motores estão nas respectivas pastas.

Ferramentas locais: Python `C:\Python314\python.exe`; JDK17 em `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot`; Apktool `E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar`; build-tools35 em `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15`; NDKr28c em `E:\TurboEdenEngine\android-ndk-r28c`; android.jar em `G:\Android\Sdk\platforms\android-34\android.jar`; LLVM em `C:\Program Files\LLVM\bin`. Compilação e temporários em E:.

## Ordem da integração atual

Os scripts contêm caminhos absolutos da pasta ativa. Se restaurados em outro destino, adaptar conscientemente as constantes e os caminhos, preservando os hashes de entrada e sem misturar versões.

- Para reconstruir a base Dolphin, usar seus scripts `prepare.py`, `integrate.py`, `native_patch.py` e `package.py`, com as bases decodificadas indicadas em seus fontes. Compilar `merged` com Apktool antes de empacotar. Consultar HANDOFF.md do Dolphin; falhas intermediárias ali registradas são históricas.
- Para Flycast, preparar `frontend-decoded` a partir da base Dolphin e `current-decoded` do doador oficial. `prepare.py` recria `merged`; executar `integrate.py` depois, pois recriar merged descarta as alterações anteriores.
- `integrate.py` compila a ponte Java e `native_bridge.c`. Preservar `-mno-outline-atomics`: a ponte usa atomics sem vincular compiler-rt.
- `native_patch.py` registra as rotas quando necessário; `build_native.py` na raiz compila o módulo do carrossel. O módulo desta versão tem SHA256 `102947e474e498c6f4e6c3a1e50c6fbfba21e7965e82d86d62889c91f632f17e`.
- Compilar `flycast-integration/merged` para `merged-template.apk` com Apktool, cache framework e temporários em E:. Só reutilizar o template se recursos/classes correspondentes não mudaram.
- `flycast-integration/package.py` usa a base Dolphin exata, a ponte, o módulo nativo e os ativos locais, alinha e assina. Resultado: `TurboramaStation-Flycast-v2.7-44-retorno-rapido.apk`.
- Não executar scripts finalizadores de marcos históricos (flight-rear-view, vídeos, pesquisas antigas) sobre o estado atual: podem reverter a base ou o perfil ativo.

## Dados no aparelho

Pacote `org.emulationstation.frontend`. Dolphin e Flycast têm processos e diretórios próprios dentro do aplicativo. Dados externos: `Android/data/org.emulationstation.frontend/files/Dolphin` e `.../files/Flycast`; internos e caches separados. Migração copia arquivos ausentes sem apagar origem. Save states de cores antigos não têm compatibilidade presumida.

A atualização estável mantém jogos, saves, opções e sessão. Os aplicativos Dolphin/Flycast separados não são dependência desta versão e não devem ser removidos para instalar esta atualização.
