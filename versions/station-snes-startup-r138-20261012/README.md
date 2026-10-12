# R138 — início SNES DSP e encerramento nativo

A sala já tinha iniciado e o túnel respondia, mas o core não carregava Super Mario Kart ou Top Gear 3000. A configuração SNES exigia arquivos DSP1b/DSP4 externos em LLE; esses arquivos não estavam no APK nem eram preparados pelo caminho online. O retorno precoce de `rarch_main` deixava a Activity aberta e um looper inválido, que abortava ao pedir saída. Ver [provas físicas e errata](../../audits/station-r138-snes-dsp-startup-20261012/README.md).

A R138 usa o suporte DSP HLE já compilado no mesmo core, com as duas opções necessárias: `bsnes_violate_accuracy=enabled` e `bsnes_chip_hle=HLE`. Todas as demais opções, inclusive SuperFX 100%, permanecem exatas. A configuração é fixa e deve ser a mesma para todos os participantes; requer novos perfis assinados no servidor. O encerramento nativo passa a limpar a Activity após qualquer retorno de `rarch_main`, de forma idempotente, antes de a thread liberar seu looper.

No moto g52, o core instalado falhou com as opções originais nos dois jogos. Também falhou com HLE isolado sem habilitar sua porta de opções. Com a configuração completa, ambos carregaram e executaram 120 quadros, com 120 imagens, áudio e estado serializável, sem erros do core. Esses testes isolados não validam sincronização de uma partida online nem controles de três aparelhos. A correção de lifecycle passou nos cenários de retorno antecipado, limpeza duplicada, saída concorrente e espera pelo join.

## Pacote conferido

- APK R138 SHA-256 `9183462e4d45cfcf2d2599d9e682b81890fee7b094505bf3073ab8183dd1dd10`, 2.714.991.631 bytes, certificado original v2/v3, alinhamento 16 KiB.
- Donor R137 SHA-256 `fe4bc08fbc1f36d2790831f6bcd9593204ec0a032ca0d3a42c1cd385bc272719`.
- Somente duas entradas mudaram: `lib/arm64-v8a/libstation_retroarch.so` e `assets/station-online/engines.json`. As outras 13.858 entradas, incluindo todos os 40 DEX, foram conferidas por SHA integral.
- Runtime novo `463bdb0b409e028aa34f6c9a09d291a3715ffb3eacb8f18ee28843e7373eb80f`. A fonte preserva cinco posições e quatro convidados. Top Gear 3000 continua até quatro; Super Mario Kart até dois.
- Nove descritores de motores RetroArch recebem novo runtime/ID. Geolith mantém seu estado inativo. PSX, N64, GameCube e Wii, com os marcadores R137, permanecem exatos: nenhum payload vinculado a eles mudou.
- A reconstrução da base de cinco jogadores reproduziu todas as seções de código, dados e relocação; diferiu somente nos metadados `.comment` e `.note.gnu.build-id`. A compilação candidata muda um único arquivo de fonte, em duas funções e uma declaração antecipada.

## Reprodução e instalação

Instalado no moto g52 em 12/10/2026, por atualização: hash integral do APK, UID e dados preservados, tela inicial observada. Ver [recibo de instalação](evidence/instalacao-moto-g52.json). Edge 30 e A56 permanecem na última R135 conferida; atualizar todos os participantes antes de repetir partidas R138.

Usar [as receitas R138](../../integration/online-snes-startup-r138/recipe/): reconstruir a base correspondente de SHA pinado, aplicar o patch de lifecycle e montar `package_r138.py` com o donor R137 e o runtime compilado. A receita preserva o manifesto integral de entradas para assinatura/verificação independente. Alinhar e assinar com a chave original; conferir novamente todos os hashes antes da instalação. Fontes do core, probes e matrizes de perfis estão no mesmo overlay; APK, chave, logs privados e arquivos de conteúdo permanecem locais.

O [instalador USB](../../tooling/usb-installer/) oferece um ou todos os celulares autorizados, confere o manifesto explícito da versão e tenta verificar o APK instalado. Não desinstala nem apaga dados. Bloqueia uma partida online que continua em segundo plano. O manifesto de testes local deve apontar somente para o APK final conferido.

## Aceite ainda necessário

Registrar os oito motores RetroArch ativos, seus hashes reais e os perfis HLE de cada edição/modo no contrato v3 do servidor, preservando os registros anteriores. Obter recibo administrativo e resposta assinada fresca. Instalar R138 em todos os participantes. Repetir Super Mario Kart com dois e Top Gear 3000 com dois, três e quatro, conferir vídeo/áudio/controles, recuperação de sinal e saída sem crash em anfitrião e convidados. Cinco requer jogo/modo apropriado e teste específico. Cadastro, gameplay de rede, saída física R138 e homologação comercial continuam pendentes.
