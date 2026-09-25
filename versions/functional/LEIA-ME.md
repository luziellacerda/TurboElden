# TurboRetro — versão com rede para funções de uso

APK desta etapa: `E:\ESTUDO APK\TurboRetroEmu-funcoes.apk`.

Senha provisória: **`turbo123`**. Versão `1.0-funcoes`, código 3. Android 8/API 26+, ARM64, pacote `org.emulationstation.frontend`.

## O que mudou

O app mantém a tela de senha local e os caminhos de catálogo, jogos, downloads, cores, capas, metadados e funções online dos emuladores. O tema e os arquivos da base foram preservados.

A comunicação do licenciamento antigo, o envio de telemetria/crash reports e a consulta do IP público foram desativados. A verificação de assinatura/plano no outro servidor permanece fora desta etapa; nenhum novo login remoto foi integrado.

A senha apenas abre o frontend local. Ela não é enviada a nenhum servidor e não é uma credencial do catálogo. A sessão fica em memória enquanto o processo estiver vivo. É uma proteção provisória, não um sistema de segurança de produção.

## Limite confirmado do catálogo

Em 25/09/2026, uma consulta GET **sem credenciais** a `https://samboxmanager.squareweb.app/drawers.json` retornou **HTTP 401** e `{"error":"Key obrigatória"}`.

O código tem duas rotas: `/drawers.json` sem chave e `/drawers.json/{chave}/android` com chave. A rota sem chave existe no código, mas o servidor atual não a aceitou anonimamente. O cache `/.emulationstation/store/catalog-cache.json` pode ser usado sem validação da licença se já existir e `StoreUrl` estiver configurada; o APK não inventa esse cache nem garante que o aparelho o tenha.

Portanto, manter o link não torna o catálogo público. Para obter uma lista nova será necessário acesso autorizado no servidor atual, um catálogo público fornecido pelo responsável ou a integração futura com seu servidor. Nenhuma autorização remota foi burlada. Arquivos/jogos locais e demais funções não dependem de tornar esse endpoint público.

## Alteração técnica limitada

- `HttpBridge.startPost` retorna um request com ID válido, erro local e `STATUS_INVALID=4`, sem criar tarefa de rede. No binário base auditado, seus únicos dois chamadores nativos são licença e telemetria. Isso cobre também um endereço personalizado de telemetria.
- Todas as outras rotinas do bridge HTTP permanecem iguais, inclusive GET, redirecionamentos, downloads, extração de pacotes e download segmentado. Não foi criada uma lista fechada de hosts: jogos e imagens podem vir de domínios diferentes, indicados no catálogo.
- O método nativo `TelemetryService::startIpLookup` retorna antes de executar qualquer instrução do prólogo. Isso impede a consulta de IP padrão e a configurável.
- A alteração de entrada nativa da versão anterior permanece: pula a construção da tela antiga de licença, sem declarar uma licença aceita e sem abrir automaticamente a loja.
- São 11 bytes efetivamente diferentes em duas regiões de `libmain.so`: oito na entrada e três na instrução de quatro bytes de consulta de IP.
- As strings históricas dos serviços permanecem no binário extraído, mas os caminhos de envio acima estão inativos. O subsistema de estatísticas/fila local não foi removido; pode registrar eventos e agendar tentativas que falham localmente, sem envio.
- O bloqueio de POST refere-se ao bridge do frontend desta versão, não às bibliotecas próprias dos emuladores. Antes de adicionar uma função nova que precise de POST, revisar esse ponto e integrar o serviço autorizado explicitamente.

## Compilar e conferir

```powershell
& 'E:\ESTUDO APK\TurboRetroEmu-funcional\Build-Login.ps1' -OutputApk 'E:\ESTUDO APK\TurboRetroEmu-funcoes-novo.apk'
& 'E:\ESTUDO APK\TurboRetroEmu-funcional\Verify-Login.ps1' -Apk 'E:\ESTUDO APK\TurboRetroEmu-funcoes-novo.apk'
```

Os scripts recusam sobrescrever a saída e trabalham em E:. JDK e SDK já instalados são usados como ferramentas; temporários, cópias e resultados ficam em E:. Código da senha em `java`, testes em `tests`, fonte integrada e logs em `runs`, inspeções do APK final em `verification`.

`build-result.json` e `verification-result.json` registram os resultados reais, inclusive hash SHA256. A verificação reabre o APK e compara todos os métodos HTTP não alterados com a fonte original, além de validar as duas regiões nativas, o login e o manifesto. O teste de senha possui 36 casos/verificações.

Os APKs original, recompilado e de login anterior foram preservados. Não houve instalação automática, alteração de dados de aparelho ou publicação de binário no GitHub.

## Teste no aparelho ainda necessário

As conferências de compilação, assinatura técnica, alinhamento e código não são teste de funcionamento no Android. Testar senha correta/incorreta, biblioteca vazia, controle remoto, jogos locais, retorno dos emuladores, capas, downloads autorizados, reinício, notificações e restauração pelo histórico.

O APK usa a chave técnica de desenvolvimento das versões recompiladas anteriores. Não instala como atualização sobre o original assinado com outra chave; não desinstale o original sem backup. A assinatura técnica do APK é independente da assinatura/plano a integrar no outro servidor.

Não redistribuir o APK ou o material extraído sem autorização para os componentes originais.
