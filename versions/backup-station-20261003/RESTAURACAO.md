# Restauração sem misturar versões

## 1. Conferir a cópia

Raiz: `G:\BAKUP SISTEMA APP 03-10-2026`.

1. Ler `RESUMO-BACKUP.json`: exigir `status=complete-copy-readback-verified`.
2. Calcular o SHA-256 de `MANIFESTO-ARQUIVOS-PRIVADO.json` e comparar com `privateManifestSha256` do resumo publicado no Git.
3. Para cada entrada desse manifesto, conferir tamanho e SHA-256 do caminho relativo à raiz. O processo de criação já realizou essa leitura integral após copiar.
4. Ler `git/BUNDLE-MANIFEST.json`, conferir o SHA-256 do bundle e executar `git bundle verify` em um repositório Git de recuperação. O bundle deve ser completo, sem commits prévios exigidos.

O bundle preserva os commits e referências disponíveis no clone local, incluindo a tag estável e o commit desta entrega. Não contém arquivos ignorados ou não versionados; eles estão na cópia de compilação quando pertencem às origens explicitamente listadas no manifesto.

## 2. Escolher a versão antes de restaurar

**Estável pronta, bytes congelados:**

`releases/estavel-station-snes-megadrive-20261003/TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk`

SHA-256: `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`.

**Candidato para 40 mil:**

`releases/candidato-station-40000-20261003/TurboStations-CANDIDATO-40000-20261003.apk`

SHA-256: `bced63f9b670b9098ffb983cf7e45335678b725d2944ee7133f77128724b9b7b`.

O diretório `compilacao/station-reconstruction-20261002` já contém o candidato. Para recuperar o fonte estável, usar o commit `97938400d3fa82d5d1564445c36fc70328add1c4` do bundle/repositório e seu módulo `versions/station-reconstruction-20261002`, com as dependências preservadas. Não sobrescrever a cópia congelada nem mover a tag estável.

## 3. Restaurar o ambiente de compilação

`sourceMapping` do manifesto é a autoridade para todos os caminhos. Os scripts atuais usam caminhos absolutos; copiar apenas a pasta G: para outro lugar não os reconfigura automaticamente.

| Conteúdo no backup | Caminho original usado |
|---|---|
| `compilacao/station-reconstruction-20261002` | `E:\ESTUDO APK\work\turbostations-reconstruction-20261002` |
| `inputs/TurboramaStation-TESTE-lado-a-lado.apk` | `E:\ESTUDO APK\work\native-carousel\implementation\side-by-side-turborama-20261001\TurboramaStation-TESTE-lado-a-lado.apk` |
| `ferramentas/android-ndk-r28c` | `E:\TurboEdenEngine\android-ndk-r28c` |
| `ferramentas/android-build-tools-35-android-15` | `E:\ESTUDO APK\TurboRetroEmu-build\android-build-tools\35.0.0\android-15` |
| `ferramentas/apktool_3.0.3.jar` | `E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar` |
| `ferramentas/sdk` | `G:\Android\Sdk` — API 34 e platform-tools copiados |
| `ferramentas/jdk-17.0.20.101-hotspot` | `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot` |
| `ferramentas/Python314` | `C:\Python314` |
| `ferramentas/CMake` | `C:\Program Files\CMake` |
| `ferramentas/Ninja-build` | Diretório WinGet exato registrado no manifesto |
| `ferramentas/dotnet` | `C:\Program Files\dotnet` |
| `assinatura-privada/debug.keystore` | `C:\Users\Admin\.android\debug.keystore` |

Restaurar em destinos vazios ou conferir os arquivos existentes antes de qualquer substituição. Não há script de restauração destrutiva nesta entrega. Em outro computador, instalações/registro de ferramentas e caminhos precisam ser conferidos; não foi executada uma reconstrução em máquina limpa a partir deste backup.

A base exigida pelo empacotador tem SHA-256 `d810434352f7ad2e7d1d08efe44f31eb76d132ffc43ba3b81b9ffc9e64efae1b`. Se houver divergência, parar e localizar a entrada correta. Não remover a conferência de hash.

## 4. Compilar

Usar a seção 13 do handoff técnico completo, mantido no Git e em `releases/estavel-station-snes-megadrive-20261003`. A ordem real é:

1. `prepare_test_dependency.py`
2. `run_tests.py`
3. `build_module.py`
4. `prepare_dex_input.py`
5. `build_archive.py`
6. `build_frontend.py`
7. `link_native_services.py`
8. `build_app_dex.py`
9. `package_apk.py`

Executar na pasta canônica E:, com temporários e `ANDROID_USER_HOME` em E:, verificando o código de saída de cada etapa. O backup inclui os pacotes de dependências já usados. Não executar finalizadores históricos nem o exportador da estável sobre o candidato.

Os hashes de `source-manifest.json` são dos arquivos locais lidos pelo build. O Git normaliza finais de linha conforme `.gitattributes`; o inventário `git-source-integrity.json` da revisão de capacidade registra também os bytes efetivamente publicados. Uma diferença só de CRLF/LF não identifica uma mudança de lógica; comparar com o inventário correspondente.

Um rebuild gera outro candidato e pode mudar metadados ZIP/assinatura. Conferir pacote, certificado, entradas preservadas e testes; não alegar igualdade de bytes apenas pelo nome do APK.

## 5. Instalação e servidor

Esta entrega de backup não instala o candidato nem implanta o patch do servidor. A estável continua no telefone. A capacidade de 40 mil foi testada com dados sintéticos; o último catálogo real conferido contém 1.816 jogos.

Preservar assinatura, pacote `org.turboramastation.frontend`, jogos, saves e identidade Keystore. Atualização é instalação sobreposta; não desinstalar nem limpar dados. A cópia da chave de assinatura do APK não é a chave de ativação de cada aparelho.

A equipe Servidor-pix deve seguir `HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md`, aplicar e homologar o patch em sua revisão, coordenar a atualização de clientes e só então ampliar o índice. Clientes antigos continuam limitados a 4.096 entradas.
