# R117 — retorno do servidor, LEDs progressivos e opções de efeitos

Base exata: R116 publicada em `2c7132bc2e023a8f8e17c3c15d8bc59fbe72ba7d`. Esta entrega concilia os três últimos retornos reais do Servidor-pix com a Activity atual. Não restaura Activities antigas nem o modo gráfico R100 rejeitado. Consulte `STATUS.json`, `SERVER-CROSSCHECK.md` e `evidence/`.

## Implementado

- Pessoas e salas possuem cursores separados; a lista v3 solicita 32 salas por página. A sala do usuário continua independente da página visível.
- Consultas de presença/eventos/snapshot retomam após falhas transitórias com recuo de 1/2/4/8 segundos e respeito a Retry-After. Criar, entrar, pronto, iniciar, sair e mensagens continuam sem repetição automática.
- Sinopses das salas usam o itemId do catálogo autenticado já em memória. Criar/Sua sala mostram quatro linhas; outras salas mostram duas, com leitura completa e instruções por toque.
- O LED exibe as primeiras parcelas válidas, começando em regiões luminosas, enquanto o restante é preparado. A capa original permanece intacta nas regiões ainda não preparadas. Caches limitados reutilizam campos completos da mesma capa/revisão/contexto.
- Botão ao lado do seletor de tema desliga todos os efeitos e restaura as escolhas individuais ao religar. Configurações ganha **EFEITOS**: LEDs, vídeos, fundo, Lotties, efeitos das células/botões e transições.
- Fundo pode ser **Céu**, **Ondas** ou **Sem fundo**. Ondas usam três faixas simples; somente a opção escolhida e visível é processada. O padrão mantém o céu do carrossel e o fundo estático atual do online.

## Preservado

Fila única de IO/decode de capas, prioridade visível, cache persistente por coverId+revision, warmup limitado a 64 tentativas/20 segundos, publicação nativa progressiva, nove itens visíveis e pulso de 80 ms. Vídeos continuam locais, uma passagem e retenção dois quadros antes do final. Menus continuam a 30 FPS. Shader, brilho, rastro, intensidade e relógio dos LEDs são os mesmos da R116. Controles, assinatura, autenticação e motores não são alterados.

Desligar efeitos não impede atualizar downloads, mensagens ou ações necessárias. O menu continua desenhando sua interface e recebendo comandos; não promete consumo zero. A taxa dos emuladores não recebe o limite de 30 FPS dos menus.

## Limites da conferência

O início do LED deixa de aguardar o campo inteiro. A conclusão completa ainda respeita quatro linhas por quadro: uma altura de 960 pixels pode levar cerca de oito segundos a 30 FPS. Provas locais verificam preparação progressiva, cache e limites; não são medição térmica ou aprovação visual física.

O servidor declara catálogo 33 e endpoints ativos em seus recibos. Nenhum serviço foi implantado ou reiniciado nesta entrega. Novas plataformas só permitem online quando perfil e adaptador real estiverem liberados; metadados de jogadores não fabricam capacidade de sala.

## Reprodução e publicação

`build.py` verifica APK privado R116 e manifestos, compila Java/frontend/carrossel e confere entradas preservadas. Objetos e artes privadas são dependências locais identificadas pelo manifesto; não são publicados no Git. Assinatura precisa corresponder ao certificado original. Nenhum APK, ROM, BIOS, licença, captura, token ou serial privado pertence à publicação.

Recibos R116 em `evidence/` são históricos da base. Estado atual somente em `STATUS.json` e recibos R117.

## APK final

Compilação completa e assinatura verificadas. APK privado local:
`G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R117-20261010.apk`.
SHA-256 `fce3be2821abcb89da05b18370a36dadc0a78f1f5f8381ccbc8a0ba2c2645372`;
2.217.033.096 bytes. Somente cinco entradas mudam; outras 13.543 entradas
permanecem byte idênticas à base. Certificado original, esquemas v2/v3 e
alinhamento de 16 KiB conferidos. R117 instalada diretamente no Motorola Edge30: hash integral, UID e dados originais preservados. Abertura autenticada, carrossel, aba EFEITOS, Modo leve e fundo Ondas conferidos; céu e efeitos ativos originais restaurados. Veja `evidence/installation-motorola-r117.json` e `evidence/physical-smoke-r117.json`. Samsung não atualizado nesta entrega. Medição térmica, tempo do primeiro LED e gameplay permanecem pendentes.

Para testes atuais, use as receitas R117 listadas em ALTERACOES-DETALHADAS.
Receitas antigas herdadas não substituem o build R117 por manifestos.
