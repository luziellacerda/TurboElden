# R149 — correção de carregamento offline do GameCube

O A56 registrou `LinkageError` antes de iniciar Wind Waker: a classe
`FragmentActivity` declara `onPause()V` como `public final` (0x11), enquanto
`EmulationActivity` introduzida na integração R126 declara o mesmo método
`protected` (0x04). A classe intermediária `AppCompatActivity` não declara
esse método. O binário oficial Dolphin 2609-7 não tinha o método filho; a
colisão surgiu na integração e permaneceu até a R148.

`recipe/patch_dex.py` exige o APK assinado R148 pelo tamanho e SHA-256, extrai
`classes10.dex` e localiza os dois métodos pelas tabelas de classes, métodos,
protótipos e dados de classe do DEX. Os offsets dos modificadores não são
codificados na receita. Ela altera somente os dois valores ULEB128 de um byte:

| Método | Antes | Depois |
| --- | --- | --- |
| `FragmentActivity.onPause()V` | `public final` (0x11) | `public` (0x01) |
| `EmulationActivity.onPause()V` | `protected` (0x04) | `public` (0x01) |

Corpos, bytecode, índices, tabelas, offsets e tamanho do DEX ficam idênticos;
apenas permissões de sobrescrita e acesso mudam. A receita confirma a cadeia
de herança e que a classe intermediária não declara `onPause()V`. Depois
recalcula o SHA-1 e Adler-32 do cabeçalho, valida a
estrutura resultante e aplica a inversão para reproduzir o DEX R148 byte a
byte. `--inspect` fornece esse recibo sem gravar a saída.

`recipe/build_candidate.py` recebe o DEX e recibo privados, confere a
reprodução da correção, a fonte congelada em commit, o APK R148 e os 345
hashes dos três marcadores de identidade. Renova somente o hash de
`classes10.dex` nesses marcadores e os quatro IDs associados em
`engines.json`. O APK candidato altera exatamente cinco das 13.860 entradas:
DEX10, três marcadores e `engines.json`. As outras 13.855 entradas ficam
idênticas por SHA-256, incluindo o carrossel R148, os outros 39 DEX, o core
Dolphin, downloads e perfis.

A assinatura privada verifica certificado original, v2/v3, alinhamento 16 KiB
e todos os hashes de entrada outra vez. O kit privado do servidor precisa dos
quatro IDs R149 correspondentes ao APK final; os kits anteriores não
comprovam esse cadastro. A preparação de APK/kit não confirma instalação,
aplicação no servidor nem sucesso de jogo físico. A versão visual seguinte
deve ser produzida separadamente da correção funcional.
