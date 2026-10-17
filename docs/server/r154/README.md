# R154 — teste visual rejeitado; não aplicar o kit

O APK R154 foi instalado no Galaxy A56 em 14/10/2026. O instalador retornou
`Success`; o SHA-256 do `base.apk` no aparelho bateu com o APK assinado e o
`firstInstallTime` e o diretório de dados foram preservados.

O teste visual rejeitou esta revisão. A sombra virou uma faixa horizontal atrás
das capas pequenas, enquanto o pedido era um degradê contínuo com a luz azul
vindo da diagonal inferior direita. O modo Ondas Online exibiu céu e quatro
linhas finas; o pedido esclarecido é céu esfumaçado somente em Céu e quatro
faixas largas preenchidas no modo Ondas Online. A sala online foi capturada no
A56 como referência, sem alteração de sua lógica nesta revisão.

| Artefato | SHA-256 | Tamanho |
| --- | --- | ---: |
| APK R154 assinado | `c91d97ab5a6538c1498594fc70d24c10cec4ef8ee83a1739697d9c8dcc31a8fe` | 2.715.106.319 bytes |
| Kit privado R154 | `972d244bc412b98403a806e4c7606c6edc6d2c134be524a535c6277a809f634a` | 12.184.560 bytes |

Fonte congelada: `ce5855a495fc493cca58b39b486e8a06dfd2c41a`. O APK e o kit
partem diretamente da R152 assinada e cadastrada, não da R153 rejeitada. A
auditoria conferiu 13.860 entradas do APK: 13.855 preservadas, inclusive os
40 DEX e `libstation_frontend.so`; mudaram só o carrossel, três marcadores de
runtime e `assets/station-online/engines.json`. Certificado original, assinaturas
v2/v3 e alinhamento de 16 KiB conferidos. Os quatro IDs R154 não foram
cadastrados no servidor. Nenhuma partida física foi homologada por esta revisão.

**NÃO ENTREGAR NEM APLICAR O KIT R154.** O arquivo permanece apenas como
evidência; a substituta terá identidades e kit novos. A R152 é o estado
confirmado aplicado no servidor. Não reaplicar operadores ou kits anteriores.
