# Candidata isolada — falhas de recursos ao iniciar o runtime

Preparada em 13/10/2026 a partir da fonte exata R138. **Não está no APK instalado, não tem novo runtime compilado e não foi executada no Android.**

O código atual cria mutex, condição, estado salvo, pipe e worker sem conferir todos os retornos. A falha de criação do worker deixa a UI esperando `running` sem existir uma thread que o publique. Outros retornos nulos podem chegar a `memcpy` ou às primitivas de condição. A falha do pipe perde as alocações de mutex/condição. É uma falha herdada, reproduzida com injeção controlada das seis falhas e um caminho de sucesso, além de quatro casos com estado salvo vazio.

`native/source/frontend/drivers/platform_unix.c` muda somente `android_app_create` e o trecho de erro de `ANativeActivity_onCreate`. Confere retornos, libera recursos próprios antes de existir worker, retorna sem esperar/join e pede `ANativeActivity_finish` somente quando a criação falha. O handshake de sucesso e todos os demais bytes da fonte R138 permanecem iguais. O caminho de estado salvo vazio é tratado sem alocar/copiar zero bytes.

Baseline SHA-256: `e4811bef12aeacd07947e51badaf8341be6c12c347c4952a9334ba22e56342f2`. Candidata: `b3ad1cbe5843d77a2f645707d3bb329fbbc8bb1a41d86e6cfe76d3d1626858dd`.

Reproduzir a qualificação em um diretório novo fora do repositório:

```text
python -B recipe/qualify_allocation_candidate.py --out CAMINHO_TEMPORARIO_NOVO --compiler CAMINHO_CLANG
```

A receita confere ambos os hashes, refaz a inversão exata do patch e extrai as funções produtivas para fixtures locais. Sucesso mantém o handshake; as seis falhas retornam sem espera, com zero alocações/FDs retidos e uma liberação/solicitação de fechamento; os quatro casos de estado vazio retornam como sucesso mesmo quando a alocação de estado é configurada para falhar. O teste intercepta caminhos inseguros da baseline sem bloquear ou provocar um crash real no PC. O worker das fixtures é simulado; não há prova de concorrência Android, JNI, driver, jogo ou desempenho físico.

O ajuste não muda o loop de quadros, frequência, fps, opções, controles, rede ou perfis. A futura integração exige build Android/NDK, identidade nova do runtime/motores, preservação integral do restante do APK, assinatura original e teste de início/saída nos aparelhos. Não aplicar o arquivo completo a uma base diferente; conferir o hash da R138 e usar a receita. A candidata não modifica os waits normais de lifecycle nem a criação de chaves TLS; esses riscos estão na auditoria.
