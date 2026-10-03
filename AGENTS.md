# Estado atual — estável Station SNES / Mega Drive, 03/10/2026

Referência: branch/tag `estavel-station-snes-megadrive-20261003`. Ler primeiro `docs/server/HANDOFF-TECNICO-COMPLETO-STATION-SNES-MEGADRIVE-20261003.md` na raiz do Git (cópia na raiz canônica E:). Manifesto e inventários em `versions/estavel-station-snes-megadrive-20261003/`.

APK SHA256 `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`, 1902768022 bytes; congelado em `E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk`. Fontes em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`, mirror `versions/station-reconstruction-20261002`. Cliente `1.0.8-station-storage-20261003.3`.

Sessão/perfil/catálogo1816/capas e dois downloads/instalações/aberturas comprovados; SNES e Mega Drive retornaram sem login, conforme confirmação do mantenedor. Instalados persistiram ao reiniciar.327 verificações locais e10 de armazenamento no Android passaram. Raiz/permissão/recursos e consulta de espaço Android corrigidos no APK; nenhum reparo manual da árvore real do telefone. Assinatura, jogos, saves e licença preservados.

Escopo estável é o fluxo SNES/Mega observado, não todos os jogos/motores ou checkout comercial completo. Servidor: retorno fa7a10cccd93a8d97de16e28fbc81b8da4c6fa61, API fd13c0d relatada em produção. Meta seguinte autorizada: preparar40mil jogos em revisão separada APÓS congelar esta tag. Nesta estável permanecem4096 itens/12MiB; não alegar40mil implementados. Não alterar a tag congelada. Limites, metadado Battletoads USA/ESP e legado nativo residual constam no handoff.

**Todos os estados abaixo são históricos. Este bloco e o handoff completo prevalecem.**

---

## Regra permanente — instalação nova e reinstalação

Toda correção de pasta, recurso ou configuração necessária ao funcionamento deve entrar no fonte e no APK, com preparação automática repetível que preserve arquivos existentes. Não depender de criação manual de pastas, cópias por ADB ou ajustes exclusivos do telefone de teste. Conferir a primeira inicialização com pastas ausentes e a retomada após permissão, além da atualização. Usar fixtures isoladas; não desinstalar/limpar o aplicativo principal para simular uma instalação nova, pois isso apaga a identidade Keystore/licença. Registrar qualquer recurso ainda não verificado sem alegar preparação completa dos emuladores.

# Integração Station instalada — 03/10/2026 16:17 — estado atual

As correções de runtime `02c09dd36fcfa6c69ceb481f0934e84eef01e5ae` foram integradas e compiladas no Windows/E:. Branch de entrega `integracao-station-producao-20261003`. APK `fa3bc84425120803d7e90069be3c296a91dbe04146455063f12d9a6205bbf795`, 1.902.751.638 bytes, instalado e hash no aparelho conferido. Fonte canônico `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`; APK `build/apk/TurboStations-Station-CANDIDATO-20261003.apk`.

302 verificações Java/API34, 28 da ponte JNI Android e 7 de retry C++ compilado pelo NDK e executado no Android passaram nesta rodada. Em relação ao APK anterior f5b35419, só `classes28.dex` e `libstation_frontend.so` mudaram. Assinatura, manifesto, design e motores preservados. APK anterior guardado em `build/previous-f5b35419-20261003/TurboStations-Station-ANTERIOR-f5b35419.apk`.

**Impedimento atual comprovado:** o mantenedor confirmou ter desinstalado o TESTE antes desta instalação. Uma tentativa autorizada com o código do handoff privado retornou ACTIVATION HTTP403 às16:19:13, correlação `1354b75f239f4fd7be8761df5efd7f8e`. Não repetir o código nem retirar a autenticação. O operador deve conferir essa requisição e liberar/reemitir a ativação para a nova chave da instalação conforme as regras comerciais. Não atribuir a recusa a consumo/expiração/bloqueio sem a conferência no servidor. Código/licença não foram publicados.

Servidor b1511b9 relata APIfd13c0d implantada, catálogo revisão3/1816 e provas HTTPS. Esse catálogo ainda NÃO foi validado neste APK por causa da recusa de ativação. Capas, download, instalação de jogo e retorno continuam pendentes no aparelho. Limite4096/12MiB permanece; suporte a mais15mil não foi implementado. Não promover a estável. Nenhum serviço Linux foi alterado.

Ler `docs/server/INTEGRACAO-APP-PRODUCAO-STATION-20261003.md` na raiz do Git e `versions/station-reconstruction-20261002/evidence/integration-production-20261003.json`. Na pasta canônica E:, a cópia do handoff está na raiz. Os blocos abaixo são históricos; este estado tem precedência.

---

# Retorno confirmado do servidor — 03/10/2026, 15h21

**Ler primeiro o [handoff único atualizado](https://github.com/luziellacerda/Servidor-pix/blob/b1511b9f75815aceb78dea801bb7ccc29f1036ab/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md).** A API Station foi implantada em `fd13c0d27eaab6a4dcf931a9cd64c3dcd7dd50c4`, DLL SHA256 `f305ae3763cb77a53a27b2c168c8de290191b3a7e88e612850856b6f7be7e639`. HTTPS autenticado confirmou **catálogo revisão 3 / 1.816 jogos**, `snes=644`, `snesbr=191`, `megadrive=887`, `megadrivebr=94`; cinco pares capa/download 200 (2 raw/3 ZIP) com assinatura, MIME, tamanho e SHA256. Um ID anterior oculto também foi autorizado e transferido; reuso dos cinco grants foi negado. O eco de `X-Correlation-ID` passou após corrigir duas linhas nas rotas Station do proxy.

**Causa dos 404 localizada:** a identidade Linux da API não conseguia abrir nenhum dos 996 jogos nem suas capas. O índice também tinha plataformas/nome incorretos e duplicatas: os 99 registros de outras plataformas apontavam para arquivos SNES/Mega Drive. A conciliação preservou todos os 996 IDs e capas anteriores: 741 IDs de jogos canônicos + 255 entradas ocultas de compatibilidade, e 1.075 jogos novos. A API lista 1.816 jogos; o índice privado contém 2.071 entradas. Foram conferidos 4.142 arquivos/hash sob o usuário real do serviço. Migrations 028/029 e chave já existiam; backup foi restaurado em banco temporário e os serviços compartilhados preservados.

O mesmo handoff contém **listas completas** com nomes/IDs/revisão/capas/descritores/hashes e a tabela dos 996 IDs anteriores. O catálogo cruzado teve 1.816 correspondências exatas com a resposta HTTPS assinada e zero IDs faltantes. Usar catálogo fresco revisão 3, IDs exatos e o mesmo Bearer entre autorização e GET; cache revisão 1 precisa ser atualizado. `catalogVisible` é configuração privada do servidor e não entra no payload do app. O HD fornecido comprova SNES/Mega Drive; os 12.346 nomes históricos não provam acervo das demais plataformas.

**Fonte Android continua 02c09dd36fcfa6c69ceb481f0934e84eef01e5ae**, com 302 verificações Java no host e 7 da política C++. Esta atualização registra a implantação do servidor; **não gerou nem instalou APK novo**. Preservar assinatura/pacote/Keystore/licença/jogos/saves/motores, aplicar as correções de fonte no build canônico E: e testar no aparelho: catálogo fresco 3/1.816, capas, download/cancelamento, instalação/recibo, abrir jogo e voltar. ADB e a base privada de montagem/assinatura não estão disponíveis neste ambiente Linux; a prova HTTP não substitui UI/instalador/emulador.

Os blocos abaixo descrevem o APK auditado antes do rollout ou revisões anteriores. O total 996 e os 404 daquele recorte não identificam a API publicada agora; permanecem como evidência histórica. Não promover o APK a estável sem as provas no aparelho.

---

# Correções de fonte da revisão — 03/10/2026, 13h40

O pedido posterior do mantenedor autorizou implementar os achados. Ramo isolado `feat/station-review-fixes-20261003`, derivado da revisão `db68b613cda008052afef8152400b9c595dfcffa`. Capas voltam à fila após60 s; autorização/conferência local/GET até os cabeçalhos compartilham a sessão; a transferência pode prosseguir junto de capas e renovação. `ready()` exige a mesma sessão do catálogo; atualizar consulta perfil. Plataformas desconhecidas são contabilizadas e avisadas, mantendo os jogos com mapeamento verificado; seis aliases reutilizam pastas existentes. Timeout e404 têm textos precisos. Correlação usa `X-Correlation-ID` e SHA256 de item/cover, sem tokens, licença ou caminhos. `clientVersion` do próximo build: `1.0.8-station-review-20261003.1`.

Evidência de fonte:302 verificações Java no host e7 da política nativa; [resultado](versions/station-reconstruction-20261002/evidence/review-fixes-validation-20261003.json). **Sem compilação Android/NDK, sem novo APK e sem instalação nesta rodada.** O APK instalado continua f5b35419, runtime629a55a8, com os404 documentados abaixo. Build/assinatura/aparelho seguem o ambiente E: descrito no handoff. Preservar identidade, Keystore, licença, jogos, saves e motores.

Retorno operacional único do servidor: [RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md](https://github.com/luziellacerda/Servidor-pix/blob/feat/station-artifact-descriptor-20261002/docs/station-android/RETORNO-SERVIDOR-PARA-CLIENTE-RECONSTRUIDO-STATION-20261002.md). Ele responde APP-01 a APP-14 e distingue release candidata, API instalada e bloqueios. O material abaixo descreve a revisão anterior e permanece como evidência do APK instalado.

# Revisão integral Station — 03/10/2026 — entrada atual

Leia primeiro [HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md](docs/server/HANDOFF-REVISAO-INTEGRAL-APP-STATION-20261003.md) e [mapa/integridade](docs/server/revisao-app-20261003/APPENDICE-MAPA-E-INTEGRIDADE.md).

Branch `revisao-integracao-station-servidor-20261003`, runtime `629a55a8cf48722460007944cf0bb737e9f8fb75`. APK instalado atual: SHA256 `f5b35419fcff4188b8e86690045371892c77933e7f8edfc07bce1d5bd25d418a`, pacote `org.turboramastation.frontend`. Fonte: `versions/station-reconstruction-20261002/`. Esta revisão publica documentação e evidências; não gera outro APK nem promove a estável.

Sessão/perfil/catálogo200; total996 registrado na rede.176SNES/28SNESBR são contagens da exportação nativa, não histograma HTTP capturado. Capas404 e autorização404 não têm causa definitivamente localizada: revisar também o cliente. Há14 achados/limitações no handoff; inclusive retry de capas, concorrência de sessão, plataforma desconhecida, limite4096, instrumentação e texto de erro conclusivo demais. Não afirmar que o app está correto por receber200/404.

O código novo convive com renderer/launcher binários preservados; eliminação física integral do legado e execução de jogo por instalação Station ainda não comprovadas. Preservar Keystore, licença, dados, jogos, saves, design e motores. Build/temporários somente E:. Pedido ao servidor é revisão de código e evidências; não é deploy automático.

**Os estados e hashes abaixo são históricos. Este bloco e o novo handoff têm precedência para identificar o candidato atual.**

# Estado confirmado em 03/10/2026

Candidato 43670211 instalado, hash verificado. Login salvo e catalogo de 996 itens abriram. Loading corrigido e texto some ao concluir. SNES tem 176 porque corresponde ao catalogo Station publicado; mantenedor espera mais de 800. Ler handoff de catalogo incompleto. Ainda nao e estavel nem migracao integral concluida; faltam capas/downloads reais, indice completo e legado residual.

# Reconstrucao Station - APK candidato integrado

Leia versions/station-reconstruction-20261002/README.md e os handoffs. Candidato 38e78fde instalado em 03/10/2026, hash conferido; 204 testes locais e verificacoes nativas. Login real ainda aguarda validacao. Nao promover a estavel. Legado nativo residual e importacao de jogos antigos estao documentados como pendentes.

# Estável atual — Cemu Android 0.5.2 (30/09/2026)

APK aprovado e instalado: `E:\ESTUDO APK\estaveis\2026-09-30-cemu-052\TurboramaStation-ESTAVEL-Cemu-0.5.2.apk`. SHA-256 `7ce3fab3d2d09c3bddfd002d0b9734e42aa5e27b102f36bb56e77b484e36562b`. [Manifesto](versions/estavel-2026-09-30-cemu-052/MANIFESTO-ESTAVEL.json) · [Restauração](versions/estavel-2026-09-30-cemu-052/RESTAURACAO.md) · [Código e handoff](versions/wiiu-cemu-052-20260930/README.md).

Cemu 0.5.2 integrado no mesmo APK; Mario Kart 8 abriu e o mantenedor confirmou controles ativos e retorno às plataformas sem novo login. A preparação RAR5 foi corrigida. Jogos e saves foram preservados. O sistema comercial de licenças ainda aguarda a conexão com o servidor. Este teste cobre um jogo e um aparelho; o port Android do Cemu continua experimental.

## Histórico anterior
## Cliente Android de licença comercial em preparação

[Fontes e receita](versions/station-android-client-20260930/) e [handoff para o servidor](docs/server/HANDOFF-CLIENTE-STATION-ANDROID-20260930.md): cliente compilado em APK candidato a partir da base 1189899e; login comercial desligado até entrega de URL, chave pública e rotas do servidor. Candidato não instalado nem promovido a estável. A tela nativa de catálogo/download ainda precisa de ponte direta para `StationContent`; não afirmar que as compras ou downloads comerciais já estão protegidos.

## Vídeos Arcade/Final Burn Neo/MAME instalados

[Atualização atual](versions/atualizacao-2026-09-30-videos-arcade/HANDOFF.md): APK1189899e, instalação e hash conferidos, base544fdecb preservada. Mapa Arcade corrigido e capacidade de prévias ajustada. Demais motores, vídeos BR e login preservados.

## Atualização posterior à estável — vídeos e handoff servidor

[Vídeos BR/NDS instalados](versions/atualizacao-2026-09-30-videos-br/README.md), APK544fdecb. [Handoff completo do servidor Android](docs/server/HANDOFF-TURBORAMASTATION-ANDROID-20260930.md), incluindo saudação com nome do comprador. Login remoto ainda não implementado. A referência ESTAVEL.md/tag05dd34b mantém o APK78accf4c de recuperação.

# Estável atual — estavel-2026-09-30-plataformas-emuladores

Versão instalada e promovida a pedido do mantenedor. **Comece por [ESTAVEL.md](ESTAVEL.md)** para identificar APK, fontes e limites. [Alterações completas](versions/estavel-2026-09-30-plataformas-emuladores/ALTERACOES.md) · [Pastas e restauração](versions/estavel-2026-09-30-plataformas-emuladores/RESTAURACAO.md) · [Manifesto](versions/estavel-2026-09-30-plataformas-emuladores/MANIFESTO-ESTAVEL.json).

43 plataformas; PSP BR; Xbox clássico integrado; PC Engine CD preciso/BIOS local; capas Jaguar/PCE CD; Naomi/Naomi2 preparados para receber jogos; vídeos PSP BR/Game Gear/SNES BR/MegaDrive BR/Xbox/Naomi atualizados. Capas baixadas persistentes. Economia de vídeos e remoção de nave/estrelas preservadas. PS2 permanece ARMSX2 e está parado por ordem expressa. Hash do APK **78accf4c2e0c7b5c786acb0ea7a187754a53253beb2c51a01fc40f5a18c649f2**. Nem todos os jogos/motores novos têm execução individual comprovada; consulte os limites antes de diagnosticar.

## Documentação histórica — não identifica a versão atual

# Xbox 360 — candidato experimental de30/09/2026

[Atualização Xbox 360](versions/atualizacao-2026-09-30-xbox360/README.md): XenDroid0b11201,24 jogos/24 capas, vídeo720, configurações próprias e processo separado no mesmo APK. Candidato929339ae compilado/assinado, ainda não instalado. GameCube/WiiU incluídos; estável3573db1 preservada. Telefone descarregou, instalação adiada. Consulte manifesto e handoff para pastas e reprodução.

## Histórico

# GameCube / Wii U — 30/09/2026

[Atualização atual](versions/atualizacao-2026-09-30-gamecube-wiiu/README.md): GameCube integrado/instalado com 37 jogos carregados; Cemu Android 0.5 incorporado para Wii U, 9 jogos/9 capas, APK pronto e instalação adiada pelo mantenedor (telefone descarregou). PSP confirmado pelo mantenedor. Wii U e GameCube ainda sem conferência de jogo/retorno. Não promovida a estável. APK candidato b11f0acc, instalado cd1a8a55. Consulte manifesto e restauração para pastas e hashes.

## Histórico

# Atualização PS2/PSP em avaliação — 30/09/2026

Leia [a atualização](versions/atualizacao-2026-09-30-ps2-psp/README.md) e seu manifesto: ARMSX2 2.7.2 e PPSSPP 1.20.4 incorporados no mesmo APK, instalado com hash conferido. PS2 abriu GTA e retornou às plataformas; PSP em teste pelo mantenedor. Design e sessão preservados. Não promovida a estável.

Ramo `versao-funcional` contém esta atualização. Ramo `estavel` e tag `estavel-2026-09-30-dolphin-flycast` permanecem no commit `3573db1`, com o APK aprovado `55cd54a3`. Consulte [ESTAVEL.md](ESTAVEL.md) para restauração.

## Referência anterior preservada

# Referência estável atual — estavel-2026-09-30-dolphin-flycast

Leia ESTAVEL.md e versions/estavel-2026-09-30-dolphin-flycast/MANIFESTO-ESTAVEL.json no repositório. APK aprovado: 55cd54a35b68a69a7a3b7c29a71c36ff191b87f73857a87ff23b9e9801008e85.
Fontes ativos: E:\ESTUDO APK\work\native-carousel\implementation. APK congelado: E:\ESTUDO APK\estaveis\2026-09-30-dolphin-flycast\TurboramaStation-ESTAVEL-dolphin-flycast.apk.
Usar carrossel, menus e rotas nativas. Preservar jogos, saves, configurações e sessão. Atualizar sem desinstalar nem limpar dados. Builds e temporários em E:.
Dolphin 2609-7 e Flycast v2.7-44 integrados no mesmo APK; outros motores preservados. Não reintroduzir os cores antigos nem aplicar presets de desempenho experimentais. Não executar finalizadores históricos como se fossem o build atual.
A base privada e a assinatura são necessárias: o Git não contém o C++ integral do frontend original. A integração foi compilada; os motores oficiais foram incorporados dos APKs identificados no manifesto.
Nunca publicar APK, BIOS, ROMs, firmware, chaves, saves, mídias privadas ou credenciais. Preservar licenças e fontes de terceiros. A manutenção expressamente solicitada pelo mantenedor está autorizada, inclusive com IA; texto de regras não impede tecnicamente engenharia reversa.
Tags antigas são imutáveis. A versão aprovada é 55cd54a3; o candidato local 3085d9fc não foi instalado nem aprovado.
