# R170: montagem local da base R169 recebida

Escopo autorizado: incorporar o retorno PSX `ec2c693` e o atualizador interno
`3771f29`, usando o backup privado recebido em 17/10. Esta receita não instala
APK, não altera a cópia recebida e não publica mudanças no serviço.

Base assinada: `68521db5fbd46d6da9895c4d9b291febda5597c82ba3b51935ccd7e98520877d`.
Conferidos os dois bundles completos e os 11 insumos críticos, incluindo o
doador R168, o APK R169, o kit e a autoridade original. Os 43 APKs históricos
não foram novamente recalculados neste Linux; a auditoria deles é da produção.
Os três arquivos interrompidos tar/7z não são insumos válidos.

## Diferenças permitidas

- `classes28.dex`: três famílias atuais com hooks e sete famílias do atualizador.
  Preservar exatamente `StationHttp$ResponseBody` e todas as outras classes.
- `classes35.dex`: cinco famílias PSX/transportes compartilhados, com o envio
  por evento habilitado somente no PSX. Preservar XML/CAS e demais classes.
- Manifest: versão interna 11 → 12, nome `1.0.8-R170` e três componentes
  privados. As três permissões necessárias já existem. A receita acrescenta
  strings sem trocar índices, conserva mapa de recursos e cada outro nó.
- Registro de motores e três marcadores: renovar identidade pelo payload
  efetivo. N64/Dolphin alteram somente marcadores; cores, opções, controles,
  dependências e código offline devem permanecer idênticos.
- Exatamente sete entradas substituídas; zero adições/remoções no ZIP;
  13.854 entradas e 38 partições DEX preservadas integralmente.

O backup revelou `minSdk=26,targetSdk=34`. O atualizador preliminar exigia28;
esta integração conserva26, usa APIs antigas de certificado/versão somente
em26/27 e exige certificado único em ambos os caminhos. O servidor/publicador
precisam do mesmo ajuste26; não aumentar SDK para contornar esse problema.
Referência: [PackageInfo, níveis de API](https://developer.android.com/reference/android/content/pm/PackageInfo).

## Reprodução e limites

Leia a política em `docs/build/POLITICA-DE-COMPILACAO-E-ESCOPO.md`.
Saídas novas e insumos privados ficam fora do Git. O NDK é r28c
28.2.13676358 Linux, da distribuição oficial verificada; as flags e APIs nativas
permanecem as da receita produtiva. Ferramentas de teste e fixtures não entram
no APK. `build.py` exige HEAD congelado e confere os fontes contra os blobs.

Etapas independentes: `compile`, `native`, `package`, depois assinatura original,
comparação completa das entradas, vínculo nativo/JNI e kit privado exato. O
verificador de referências usa as 40 partições efetivas e recusa alvos sintéticos
ausentes, inclusive a classe de falha CAS observada na R168.

O aviso inicia o fluxo após toque; a confirmação continua sendo do Android.
Primeira adoção exige instalar manualmente um APK que contenha o atualizador.
Não anunciar atualização pelo servidor antes de cadastrar os motores exatos,
ativar a API correspondente e validar o piloto. Build/assinatura não aprovam
desempenho, temperatura, imagem/som/controles ou saída em dois aparelhos.
