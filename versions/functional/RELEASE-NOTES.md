## TurboRetro 1.0-funcoes — pré-release de teste

APK completo da variante com senha local e links de funções de uso preservados.

- **Senha provisória:** `turbo123`.
- **Android:** 8/API 26 ou superior, ARM64; pacote `org.emulationstation.frontend`, versionCode 3.
- **Código separado:** branch [`versao-funcional`](https://github.com/luziellacerda/TurboRetroEmu/tree/versao-funcional), pasta [`versions/functional`](https://github.com/luziellacerda/TurboRetroEmu/tree/versao-funcional/versions/functional).
- **Análise preservada:** `main`, commit `89e8e0848a73587e0cfd30fe7535e5dce82303af`. Nenhum arquivo da análise foi removido ou alterado.

### O que mudou

Tela Android de senha local, sessão somente em memória e guarda de restauração da tela principal. A validação antiga não aparece na abertura. O envio do licenciamento antigo, telemetria/crash reports e a consulta de IP foram desativados. Assinatura/plano no outro servidor permanece fora desta etapa.

Mantidos tema, recursos, caminhos de catálogo, downloads, cores e capas. Os 28 métodos HTTP não alterados foram comparados com a base. Os 164 assets e sete bibliotecas nativas permanecem idênticos; a biblioteca principal tem alteração limitada a 11 bytes em duas regiões.

### Conferências e limites

Compilação, assinatura APK v2, alinhamento de 16 KB e reabertura/decompilação aprovados; 36 verificações de senha/sessão passaram. **Ainda não testado em aparelho.**

O catálogo original sem chave respondeu **HTTP 401 — Key obrigatória**. Preservar os links não libera serviços protegidos. Jogos locais dependem dos arquivos/core compatíveis; catálogo e downloads remotos dependem de acesso autorizado.

O APK usa uma chave técnica de desenvolvimento. Não atualiza diretamente uma instalação original assinada com outra chave; faça backup antes de desinstalar. A senha local fixa não é segurança de produção.

Esta é uma publicação do **APK completo, não sanitizado**, incluindo BIOS/firmware e chaves herdadas do original, expressamente autorizada pelo mantenedor. Os direitos e licenças dos componentes de terceiros permanecem inalterados. Nenhum keystore privado, token GitHub ou dado de usuário foi anexado.

### Integridade do APK

Arquivo: `TurboRetroEmu-funcoes.apk` — 151.457.932 bytes.

SHA256:

```text
3F14E4FED3C42CB2AFA280EDCB2B2A0E0E51FC8C65F77D4C2069AE1525F67796
```

Confira também o anexo `SHA256SUMS.txt`. Código, scripts, handoff e relatórios estão na branch vinculada acima.
