# N64 no pacote atual R127

A implementação Mupen64Plus AE publicada em `efd9878` continua preservada. A [integração PSX R127](../integration/psx-online/README.md) renovou o marcador do pacote compartilhado, sem alterar core, plugins, controles ou opções N64.

Identidades para **R127**: engine `mupen64plus-ae-33bf7021-n64-v3-9536fbd2a7d2`, core `fe6e810a1c7fc50a494b50b1dccf581b84385667191c0cbcd235d585a0703dd8`, runtime `9536fbd2a7d23713d1280a22276856924420dea9920bb557e0dda7117e5b3025`. [Índice e estados atuais](ONLINE-SYSTEMS.json). Cadastro/instalação/gameplay R127 não confirmados. IDs anteriores abaixo identificam seus APKs históricos.

## Entrega anterior R126

# Nintendo 64 online — entrega de código concluída

A integração usa **Mupen64Plus AE real**, com GameActivity, CoreService, renderizador, áudio, menus e controles próprios. A rota não abre StationRetroActivity. A implementação foi compilada, assinada e conferida; ativação efetiva do servidor e partida em aparelhos continuam sem confirmação.

## Fonte atual única

O [commit executável e publicado](https://github.com/luziellacerda/TurboElden/commit/efd9878df3e87ecf22d8fbddeddd30baccb8d3dc) integra N64 na R126. A [fonte N64](../versions/station-mupen-online-r125-20261011/README.md) contém os hooks, receitas, patches e testes. As alterações posteriores de integração e a identidade final estão na [fonte atual R126](../versions/station-dolphin-online-r126-20261011/README.md).

Essas referências apontam às fontes já existentes. Este registro não cria outra cópia de fonte, APK, snapshot ou branch. O único backup completo local permanece em F:. Os instaladores e a chave de assinatura ficam fora do Git.

| Item | Identidade atual |
| --- | --- |
| Engine | `mupen64plus-ae-33bf7021-n64-v3-1aafea201355` |
| Core | `fe6e810a1c7fc50a494b50b1dccf581b84385667191c0cbcd235d585a0703dd8` |
| Runtime | `1aafea201355b58909ada9958bbe5bb5407e7ace7eb3848ade7ba04d235becac` |
| Protocolo | `station-stream.v3`, envelope nativo `SN64/1` |
| Perfil | `direct-four-ports-v1`; quantidade depende do jogo/modo aprovado |
| APK atual local | R126, SHA256 `f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d` |

O runtime intermediário `500d48cd10f3` documentado na R125 foi substituído pelo runtime acima na integração R126. Não cadastrar aquela identidade intermediária para o APK atual.

## O que foi conferido

- [282 verificações JVM do protocolo](../versions/station-mupen-online-r125-20261011/evidence/n64-protocol-jvm-probe.json), com 2/3/4 slots e provas locais de fragmentação, filas e cancelamento.
- [Auditoria N64 independente](../versions/station-mupen-online-r125-20261011/evidence/n64-final-independent-audit.json): 20 hooks, pausa no owner real e 134 verificações do registro antes do input plugin.
- [Integração R126 independente](../versions/station-dolphin-online-r126-20261011/evidence/integration-independent-r126.json): core/plugins N64 normais, mídia, UI, cache, pré-carregamento e consumo preservados.
- [Assinatura e pacote final](../versions/station-dolphin-online-r126-20261011/evidence/package-final-r126.json), com certificado original e alinhamento 16 KiB.

As provas locais não confirmam estabilidade de uma partida, resposta Bluetooth ou consumo térmico nos aparelhos. O pacote candidato R126 ainda não foi instalado segundo os recibos atuais; a última instalação conferida continua R124.

## Servidor e sequência

A [entrega já publicada ao servidor](https://github.com/luziellacerda/Servidor-pix/commit/6e3a7fac6f728ec30a57bf4f4d42f00fdd1c1534) contém o contrato e as identidades. É uma entrega do app, não confirmação de ativação. A confirmação exige resposta autenticada fresca com envelope assinado e o registro exato do engine. Não há nova implantação de servidor nesta atualização documental.

Próximo motor: **PlayStation/PSX**, em um único trabalho atual. O mantenedor informou que SNES e Mega Drive funcionam e pediu mantê-los como estão; nenhuma migração adicional desses dois sistemas integra esta entrega. Os demais seguem individualmente. O [índice de progresso](ONLINE-SYSTEMS.json) separa implementação concluída, pacote candidato e validações ainda pendentes. O [levantamento dos demais sistemas](../audits/station-online-system-engines-20261011/README.md) registra suas rotas reais.
