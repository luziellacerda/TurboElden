<!-- STATION-R168-APPLIED-CAPACITY-20261015 -->
## R168 aplicada: abertura PSX corrigida e cadastro conferido

**R168 cadastrada:** catálogo 100 com 4.744 itens, 91 motores, 16.896 perfis e
11.981 modos. Quatro owners e 492 vínculos novos; todos os anteriores preservados.
Kit privado c0de71c3a4e1: 51 arquivos, 50 hashes e 27 ELF ARM64 conferidos.
O APK R168 assinado 875fb0696c4f contém a correção XML bb045d81; assinatura e
APK por recibo do produtor, sem receber o APK neste Linux. Núcleos, 21
dependências, carrossel R167, opções e controles preservados.

PSX: 84 edições, 93 decisões, 23 modos para duas pessoas em 19 edições,
17 impedidos e 53 classificações individuais. N64: 157 edições e 387 perfis,
230 modos multiplayer e 157 individuais. GameCube nove modos; Wii três.
CTR e Crash Bash conservam suas recusas; títulos individuais não ganham vagas.
Tuplas completas foram requalificadas, sem aprovar por nome ou metadados.

O preflight original excedeu o orçamento de metadados do WinBack e não gravou.
A correção necessária ampliou somente esse teto por conteúdo de 128 para
256 KiB, no C# e no validador instalado. Mantidos 32 modos por binding,
128 motores, 50.000 perfis, arquivos de modos de 8 MiB e registros de 16 MiB,
limites de jogadores, protocolo, memória do relay e lógica N64/R165.
A regressão reproduziu a recusa antiga; passaram 1.470 verificações C#,
226 HTTP e quatro testes Python. A preparação completa manteve os prefixos.

Maior grupo preparado: 138.876 bytes. A resposta pública assinada WinBack
entregou os 133 perfis, incluindo os nove R168, em 189.469 bytes; limite Android
vigente de 524.288 bytes. Nenhuma linha foi cortada. A sombra usou o mesmo
sandbox e validou owners e saída. Dois ajustes do diagnóstico foram registrados:
nome de teste acima de 24 caracteres e seletor ainda preso ao prefixo R167.
Depois de corrigidos, as fases pendentes foram retomadas sem repetir cadastro
ou implantação.

**Um reinício controlado do Station, sem sala real em andamento.** Fonte
b1d53643cb0fdfebbc1bf351485d868a079664fe, DLL 3480b991ac8761692f8c962e87f7a5e717ba1aed77d89ce895fb6e804eeb0eca, PID 215916,
zero reinícios automáticos. DLL53d4 e seus dois overrides preservados;
somente um override R168 e um módulo do scanner foram atualizados.
Licenças reais, esquema, outros serviços, scanner ativo, catálogo, ROMs,
capas, saves e rede 100/800 preservados.

Capabilities assinadas locais e públicas das 84 PSX e 157 N64 passaram:
23 admissões/167 recusas PSX;
230 admissões/245 recusas N64.
Quatro owners e 12 modos GameCube/Wii conferidos. Transporte público PSX com
dois clientes e snapshot real de 4.456.448 bytes; N64 com quatro clientes,
seis WSS, TLS/SPKI, prioridade e pausa/retomada passaram. A saída entregou
STATE3 antes de close1000 e aceitou as três tentativas idênticas de leave.
**São diagnósticos; gameplay físico Android permanece pendente.**

Ler [recibo aplicado](server-return.json) e [consumo/piloto](README.md).
Autoridade: /mnt/DADOS/station-r168-capacity-20261015/completed.json, PASSED.
Não repetir cadastro, serviço, provas completas, R167 ou operadores antigos.
O recibo serverApplied=false do kit e a recusa anterior abaixo são históricos.
Após publicar os dados R168, o rollback exige conjunto compatível de software,
validador e dados; não retirar só o novo override. R164 estável preservada.

Produção: confirmar/publicar instalador USB permanente e instalar manualmente
o mesmo APK assinado R168 nos dois aparelhos, preservando dados e registrando
cada hash. APK esperado: 875fb0696c4fb50ce4af953bccd62fcd68dfdecb247f65d2fc027b71aa330b3d.
Piloto Capcom vs. SNK / VS, duas vagas; item station_767e5e92f2f353479e6120f1c28f96a7,
perfil psx-r168-20261015-005-versus. Conferir primeiro quadro, som,
controles independentes e retorno do convidado por 25 segundos após sair o
anfitrião. Não pedir outro kit R168; demais pendências globais mantidas.

## Histórico preservado

# R168 recebida; cadastro ainda não aplicado

O kit privado e a cadeia de recibos do APK final foram verificados. O preflight
conjunto foi recusado pelo orçamento de perfis de WinBack:137.167/131.072B já
nos primeiros78 vínculos. Nenhum registro R168 foi publicado. A R167 segue
registrada e o servidor está online.

Ler [retorno consolidado](server-return.json) e o topo do
[mesmo handoff](../HANDOFF-ONLINE-PLATAFORMAS-STATION-20261009.md).
A requalificação PSX isolada passou, incluindo as negativas de HLE/core/edição;
isso não representa cadastro, capabilities assinadas ou gameplay R168.
Não repetir cadastros anteriores nem pedir o kit novamente. Resolver o
orçamento com preservação dos históricos e do contrato antes de uma nova
baseline, validação completa e publicação transacional.
