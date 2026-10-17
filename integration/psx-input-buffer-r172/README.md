# R172 candidata: antecedência dos comandos PSX

## Defeito e evidência

Na mesma R171 instalada nos dois aparelhos, Capcom vs. SNK VS executou cerca
de 46 quadros por segundo, com produção de áudio próxima de 77% do normal.
O relay encaminhou os pacotes em menos de 0,45 ms na captura anterior.
Em 233 de 295 intervalos longos dessa captura, a entrada remota ainda não
estava no relay quando o anfitrião concluiu o quadro anterior.

O PXL1 espera entradas completas, publica o quadro canônico depois da execução
real do anfitrião e amostra comandos para N+4. Com os laços dos aparelhos fora
de fase e atraso variável, essa antecedência se esgota. A apresentação da tela
continua, mas o núcleo deixa de avançar; isso também reduz a produção de áudio.

O modelo isolado compila o protocolo real. Com quatro quadros e RTT constante
de 60 ms, produziu 43–50 quadros/s sem perdas; com 10–40 ms, manteve cerca de 60.
A soma dos tempos de confirmação de cópia dos dois aparelhos foi usada como
aproximação para outro modelo com variação de atraso; não é uma medida direta
de ida e volta entre celulares nem separa rede de processamento Android.

No modelo com essa variação: quatro quadros produziram 46–50 quadros/s; seis,
57–59; oito, 59,75–59,86. Foram 90 casos, com trabalho de 3/9/13 ms e duas fases
de execução. Esse resultado justifica a candidata e não comprova desempenho
nos aparelhos. A evidência sanitizada fica em `evidence/timing-model.json`;
dados privados da captura não entram no Git ou no APK.

## Diferença mínima

- A sessão PSX produtiva passa a usar oito quadros de antecedência. O valor
  vem de `station_psx::input_delay_frames`; política canônica, hash e perfil
  dos dois participantes devem corresponder. O componente genérico de
  protocolo conserva seu valor padrão, usado pelos testes e explicitamente
  substituído na construção da sessão produtiva.
- Custo: quatro quadros extras, aproximadamente **67 ms de atraso nominal no
  controle**. A intenção é impedir que a espera desacelere toda a emulação.
  Não há previsão de comandos, rollback, aceleração, salto ou quadro fictício.
- Núcleo, BIOS HLE, opções da CPU/GPU/áudio, mapeamento, transporte, relógios,
  callbacks e política de saída humana permanecem os mesmos. Nenhuma thread,
  timer, polling, permissão ou efeito visual novo. N64 e Dolphin mantêm a
  lógica; apenas suas identidades vinculadas ao payload precisam ser renovadas.

## Montagem

Usar o APK R171 assinado exato, SHA-256
`11231dae0ba776a56505102fdbb431632890ca3c4a85fcb086582930c316bbfd`.
O sucessor é `1.0.8-R172`/versionCode 14, com o mesmo certificado e SDK 26/34.
Somente seis entradas podem mudar: manifesto, `classes35.dex`, registro de
motores e três wrappers de identidade. As duas famílias Java recompiladas são
`StationPsxPolicy` e `StationPsxLaunch`, que incorpora as constantes da primeira.
Todas as demais classes dessa partição e as outras 39 partições devem ser
conferidas como preservadas. Fixtures nunca entram no APK.

Executar `recipe/build.py` nos estágios compile/native/package com fonte HEAD
congelada, saída privada e os insumos reais fixados. Assinar com a autoridade
original usando `signing/sign.py`; gerar o kit exato com
`signing/package_server_kit.py --r171-kit ...`. Não usar um finalizador antigo.

## Condição de entrega

Cadastro exige os quatro IDs exatos, opções PSX com oito quadros e fingerprints
correspondentes; preservar cada aprovação, recusa e modo anterior. Conferir
capabilities assinadas e admissão/recusa por versão. Nenhuma oferta geral de APK
ou promoção a estável antes de instalar a mesma candidata nos dois aparelhos e
medir velocidade, áudio, controles e saída. Instalar somente fora da partida,
preservando dados. O A56 foi observado em estado térmico severo na última
captura; isso precisa ser registrado na comparação física, não atribuído
automaticamente à rede ou a esta mudança.
