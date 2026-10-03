# Conferência no PC — revisão R2, 03/10/2026

Pedido do mantenedor: concluir os testes no PC; o telefone será conectado posteriormente. Não foi executado comando no telefone nem usada a sessão do servidor de produção.

## Resultado final

**Todos os estágios locais concluíram sem falha.** APK preservado: `31ab80ef2c77e9c5dff294d6f63807ab1e6d6cded81c2beec7aee171067f46d8`.

| Conferência | Resultado |
| --- | --- |
| Suíte Station | 384 verificações Java, incluindo protocolo, arquivos, instalação, hash, sessão, cache, quatro pedidos paralelos, cancelamento e reaproveitamento TLS |
| Corridas de sessão/cancelamento | 10 execuções adicionais de 41 verificações; 410 verificações adicionais aprovadas |
| Carga da fila | 4096 pedidos simulados; pico de 4 simultâneos; 0 erros; reposição automática |
| Cache depois de recriar o gerenciador | 4096 itens lidos; 0 requisições adicionais |
| Finalização da fila | 0 workers Station-covers vivos após fechar |
| Políticas C++ | Recompilação e execução: 11 casos de fila/plataforma/429 + 7 de retry |
| Sinopses/XML | 13 testes, incluindo 1816 IDs, 1804 descrições e as 12 ausências explícitas |
| Layout | 98 combinações verificadas por static_assert na compilação C++ |
| Shaders | GLES100 real compilado/linkado no ANGLE; aritmética nos quadros 0, 32767, 65535 e 1000000 conferida pela leitura de pixels |
| Netplay | 14 testes de snapshot/caminhos + 12 contratos do código/DEX doador |
| Compilação | Java API34, DEX Station e Netplay idênticos aos incorporados; bridge ARM64 recompilada na cópia isolada |
| APK | Assinatura, alinhamento16KiB, CRC de todas as entradas e comparação integral com a base aprovados; 10871 entradas preservadas, quatro mudanças previstas |

O ensaio de carga usa o protocolo e os componentes reais de sessão/fila/cache com um transporte sintético local e cabeçalhos de imagem de oito bytes. Serve para verificar concorrência, continuidade, cache e liberação de recursos; **não mede download real, decodificação de fotografias, consumo Android ou desempenho no telefone**. Tempos observados exclusivamente neste ensaio: 8206.59 ms na primeira passagem e 1988.32 ms no cache. Não usar esses tempos como promessa de velocidade ao cliente.

## Reprodução

Executar `run_pc_validation.py` com Python3 no computador que possui os insumos locais descritos no handoff principal. A receita cria uma nova pasta `pc-validation-AAAAmmdd-HHMMSS` em E:, copia fontes/fixtures e executa tarefas independentes. Nunca sobrescreve o APK nem os DEX/bibliotecas de entrega. Os hashes desses arquivos são conferidos antes e depois.

Pasta desta execução: `E:\ESTUDO APK\work\station-visual-covers-20261003\pc-validation-20261003-202338`. Resultado estruturado: `PC-TEST-RESULT.json`. Logs em `logs/`; evidências detalhadas em `evidence/`.

A primeira tentativa do novo ensaio encontrou um caminho mal escapado no **lançador do teste**, impedindo carregar a dependência JSON. O caminho foi corrigido e a bateria inteira repetida; recibo anterior e diagnóstico estão preservados. Também foi corrigida a exportação para incluir `NetplayPathsTest.java`, que existia localmente e era usado pela receita mas não tinha sido copiado ao Git. Essas correções não alteram o APK.

## O que depende do telefone

Não foi encontrado Android Emulator/AVD configurado nos caminhos SDK/AVD examinados. A execução integral deste APK ARM64, toque/controle, shader no driver do aparelho, tráfego real, temperatura, retorno de jogos e Netplay entre dois dispositivos permanecem pendentes. Não promover a estável com base somente nestes testes no PC.

As 12 sinopses sem origem única, fotos limitadas às famílias SNES/Mega e ausência de lobby Station/Netplay SNES-Mega permanecem como documentado no handoff da entrega. Nenhuma sessão de produção foi renovada ou invalidada por esta conferência.
