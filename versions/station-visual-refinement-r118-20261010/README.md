# R118 — cor estável do LED, loading preto e menus com ondas

Base: R117 publicada em `129ee9db892a327f720df8ae4f8e8a5ffab3f7ee`; pacote privado SHA-256 `fce3be2821abcb89da05b18370a36dadc0a78f1f5f8381ccbc8a0ba2c2645372`.

## Mudanças solicitadas

- A região geométrica que controla a cor da capa é preparada inteira antes de publicar parcelas de iluminação. A busca dos emissores e 16 amostras de halo continua incremental, quatro linhas por quadro. Equações de cor, ganho, rastro e iluminação final preservadas.
- Loading inicial somente com barra e percentual em preto. O fundo, cabeçalho, ícones e prewarm LED ficam bloqueados nesse estado; não se muda a preparação do catálogo ou das capas.
- Botão geral de efeitos removido do carrossel principal. Configurações → EFEITOS mantém a chave geral e seis controles individuais, reorganizados em duas colunas na paisagem.
- Ondas como padrão. Migração única troca o Céu legado por Ondas; preserva fundos desligados, preferências individuais e futuras escolhas explícitas de Céu.
- Online com cores azul/ciano, capa de “Estou pronto” nas mesmas dimensões de Criar sala/Modo e explicações de uso sem referências técnicas, links ou GitHub. Identidades, capacidades, mensagens, comandos e autenticação não mudam.

## Preservação

Fila única de capas com prioridade visível, cache persistente por revisão, warmup limitado, lifecycle/cancelamento, vídeos locais, uma passagem com retenção dois quadros antes do fim e menus a 30 FPS. Emuladores mantêm suas taxas. Nenhum motor novo, implantação ou reinício do servidor é feito por esta atualização.

## Compilação e evidências

Receita `build.py`, argumentos `recipes/build-r118-arguments.json`. Base APK R117 exata e dependências privadas conferidas por hash. As duas DEX e as duas bibliotecas UI são recompiladas; todas as demais entradas devem permanecer byte idênticas. Mesma assinatura e alinhamento 16 KiB exigidos.

Nenhum teste foi executado nesta revisão. Compilações de Java isoladas não validam o shader no aparelho. Testes e recibos nomeados R117/R116 são históricos; não representam provas de R118. Estado vigente em `STATUS.json`, `evidence/build-r118.json`, `evidence/package-r118.json` e recibo de instalação quando houver.

APK, artes, objetos privados, credenciais e capturas permanecem locais. Publicação somente de fontes, receitas e recibos agregados. Candidato para conferência; sem promoção a estável ou alegação de ganho térmico/gameplay.
