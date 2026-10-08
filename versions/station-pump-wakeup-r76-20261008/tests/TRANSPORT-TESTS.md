# R76 — ensaio local de transporte real

A receita `recipes/run_transport_tests.py` testa os JARs de produção da R76 que geraram o DEX35, com verificação dos hashes dos 201 fontes, do manifesto, dos dois JARs e dos dois DEX. Não recompila uma cópia substituta da classe `StationRecoveryTunnel` para a fixture.

## Matriz

| Fonte do servidor | Diagnóstico TLS | Fixture | Verificações | Bytes TCP exatos |
|---|---|---|---:|---:|
| `32ce9d2b30bb23deef17899e10fc285f38ea81ab` | desligado | original | 46 | 1.620.000 |
| `32ce9d2b30bb23deef17899e10fc285f38ea81ab` | ligado | original | 46 | 1.620.000 |
| `ab192bf1585e30f303d041f13b36a1f9c96d2caa` | desligado | original | 46 | 1.620.000 |
| `ab192bf1585e30f303d041f13b36a1f9c96d2caa` | ligado | original | 46 | 1.620.000 |
| `ab192bf1585e30f303d041f13b36a1f9c96d2caa` | desligado | estendida | 72 | 12.168.608 |
| `ab192bf1585e30f303d041f13b36a1f9c96d2caa` | ligado | estendida | 72 | 12.168.608 |

Cada execução também mantém os 32 vetores originais de contrato. Os recibos `evidence/recovery-interop-*.json` identificam resultado, fonte, JAR/DEX e binários do serviço de teste. As contagens representam repetição da matriz; não são 328 funcionalidades diferentes.

Os 60 inputs do servidor são verificados contra o export congelado `32ce9d2`, e os bytes são obtidos do commit escolhido no clone existente, sem checkout/fetch/alteração do repositório do servidor. Em `ab192bf`, a única diferença dentro desses inputs é `StationOnline.cs`, que acrescenta os perfis dos membros à resposta. Relay e harness TLS são idênticos. O assembly recompilado local é um artefato de teste, não o hash da DLL que está em produção.

## O que é real

- Kestrel .NET nas rotas de produção, limitado a loopback, certificado TLS temporário com SAN para 127.0.0.1 e validação de nome habilitada.
- Provas de dispositivo RSA/PSS, respostas assinadas e contexto de requisição/licença conferidos; posse do ticket sem prova é recusada.
- WebSockets seguros e dois endpoints TCP reais usando os JARs/filas da produção R76.
- Transferência ordenada e exata, cortes de WSS do host/convidado/ambos, novo ticket, barreiras, ACK/crédito e preservação dos mesmos sockets nativos e sala lógica.
- Estendida: quatro rodadas de transferências bidirecionais concorrentes, envio de 8 MiB com leitor TCP temporariamente retido e crédito de transmissão esgotado, liberação e entrega integral, mais duas reconexões simultâneas.

O teste de crédito usa reflexão **somente para ler** o estado da fila real sob o monitor original; não altera filas, ACK, timeout ou executores da produção.

## Limites

A confirmação de pausa do motor é um hook sintético; não há core de emulação, jogo, Android físico, rede pública, proxy de produção ou dois aparelhos neste ensaio. O sucesso não comprova estabilidade de uma partida ou a causa das quedas antigas. Os testes são da DLL ativa `ab192bf` e do contrato anterior; não homologam a candidata servidor `6f27c6c`, cujo teste TLS sem logging apresentou falha no Linux.

## Portabilidade Windows e limpeza

Só no harness sintético, o certificado autoassinado é exportado/importado com os mesmos bytes DER e chave privada para uso pelo SChannel. Não instala certificado em loja e não solicita PersistKeySet. A parada pelo stdin encerra o host de forma ordenada para descartar certificado/chave; a fixture privada é apagada e o processo do loopback termina em cada execução. Esse ajuste já existia no ensaio R71 e fica registrado no patch/recibo de portabilidade. As credenciais, chaves e logs ficam apenas em E: e não entram no Git.

Os testes não chamam o servidor público, não operam telefone, não modificam instalação global, não criam sala real e não mudam fontes de produção.
