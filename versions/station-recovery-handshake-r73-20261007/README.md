# R73 — envio de handshake durante sincronização

Leia [o handoff completo](HANDOFF-APP-R73-PARA-SERVIDOR-20261007.md) e STATUS.json.

Defeito reproduzido: o pump de espera da R72 retém MODE no buffer nativo; o convidado espera esse pacote para liberar READY. R73 envia sem bloquear, conserva bytes parciais e mantém pausa real. Painel de espera passa a Dialog próprio; diagnóstico numérico limitado.

1206 checks Java,22 nativos e39 guardas passaram. APK `b23ff3d1e319ee050e6eb867e2643a5f66661da481dd2e3a4e50089d1604f077` gerado com certificado original. **Instalada e hash integral conferido no Samsung A56 e Motorola Edge30 a pedido do mantenedor. Cadastro ativo no servidor e gameplay ainda aguardam confirmação.** Não misturar engines/versões numa mesma sala.

Fontes R72 preservadas, delta de dois Java e uma função nativa. Native `E:\R73fixed`; Java/temp em E:, APK final G:. Recibos e manifestos vinculam a composição. Não publicar APK, chaves, ROM/BIOS ou logs pessoais.
