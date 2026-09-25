# TurboRetro 1.0-funcoes

Variante experimental com senha local, mantendo o frontend, tema, cores e caminhos de downloads. Código e histórico ficam na branch `versao-funcional`; a análise extraída permanece na `main`.

[Baixar pela release v1.0-funcoes](https://github.com/luziellacerda/TurboRetroEmu/releases/tag/v1.0-funcoes).

Senha temporária: **`turbo123`**. A senha é uma barreira provisória local, não autenticação de produção. Assinatura/plano em servidor próprio está fora desta versão.

## Conteúdo deste diretório

- `java/`: código novo da tela de senha e sessão em memória.
- `tests/`: 36 verificações de senha/sessão, executadas durante a compilação.
- `Build-Login.ps1`: recria a variante a partir da base extraída autorizada, com guardas de hash.
- `Verify-Login.ps1`: reabre o APK, verifica o login e compara os métodos HTTP e as alterações nativas.
- [Handoff técnico](LEIA-ME.md) e [mapa dos links](LINKS-FUNCIONAIS.md).
- `reports/`: resultados e evidências da compilação local publicada.
- `SHA256SUMS.txt`: hash do APK anexado à release.

## Alterações desta variante

Login Android nativo com senha provisória, proteção de restauração da activity, reinício e notificações. A abertura não apresenta a tela antiga de licença.

O envio da licença antiga, telemetria e crash reports pelo bridge HTTP foi desativado com erro local explícito. A consulta do IP público também foi desativada. Os outros **28 métodos HTTP** permanecem iguais, preservando GET, downloads, segmentos e extração. As bibliotecas dos emuladores não foram reescritas.

O APK preserva 404 das 408 entradas da base. Quatro foram alteradas e um DEX novo foi adicionado. Todos os 164 assets permanecem iguais. `libmain.so` tem 11 bytes efetivamente diferentes em duas regiões; sete bibliotecas nativas permanecem idênticas.

## Limitações importantes

- Android 8/API 26+, ARM64. Pacote `org.emulationstation.frontend`; versão `1.0-funcoes`, código 3.
- APK assinado com chave técnica de desenvolvimento; não é uma versão de produção. Não atualiza o original se a assinatura técnica for diferente. Faça backup antes de desinstalar qualquer versão.
- Sem teste de execução em aparelho nesta entrega. Conferidos compilação, assinatura v2, alinhamento de 16 KB, decompilação final, 36 verificações de senha e preservação de código/recursos.
- O catálogo público original respondeu `401 — Key obrigatória`. Links preservados não concedem acesso ao servidor; a lista online exige autorização ou um catálogo próprio. Nenhuma licença remota foi fabricada.
- O APK completo conserva BIOS, firmware e chaves herdadas do original. Sua publicação foi expressamente autorizada pelo mantenedor; os direitos/licenças dos componentes continuam sendo os respectivos originais. Esta release não é a publicação sanitizada do estudo.

## Reproduzir no ambiente local

O repositório público não contém o APK-base nem as bibliotecas/BIOS separadas. A reprodução exige a base autorizada identificada por SHA256 `9DC39817F23975F15E9FB75BBE98E7A7519567E06805F5746C1F475CBCF57396`, a pasta extraída e as ferramentas indicadas no handoff. Não é uma recuperação integral do código C++ original; os ajustes nativos são limitados e vinculados ao hash da base.

Execute os scripts a partir de uma cópia em E: e escolha uma saída nova:

```powershell
.\Build-Login.ps1 -OutputApk 'E:\ESTUDO APK\TurboRetroEmu-funcoes-novo.apk'
.\Verify-Login.ps1 -Apk 'E:\ESTUDO APK\TurboRetroEmu-funcoes-novo.apk'
```

Não adicionar keystores, tokens, dados de usuários ou catálogos autenticados ao Git. O APK desta entrega deve continuar como asset da release, não no histórico de código.
