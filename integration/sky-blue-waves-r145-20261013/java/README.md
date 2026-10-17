# Preparação R145: fundos azuis mais claros

Pedido atual: o fundo azul deve ficar mais claro no menu principal e nas telas próprias que já o usam. Topo `#287EB5`, rodapé `#5DAEDE`. Esta preparação Android troca **dez literais**, em sete classes e nove métodos. Não compila nem opera o telefone.

| Partição | Classe e métodos | Constantes |
|---|---|---|
| DEX28 | `StationWaveBackground.onDraw` | Azul `ff050a15 → ff287eb5`; preto permanece |
| DEX28 | `StationDownloadPanel.onCreate` | Fundo `ff07111e → ff287eb5` |
| DEX28 | `StationDownloadUi.messageDialog` | Face `ff0d1a2a → ff287eb5` |
| DEX35 | `StationHyperspaceView.renderBackground` / `onDraw` | Topo/fallback `ff02040a → ff287eb5`, rodapé `ff071421 → ff5daede` |
| DEX35 | `StationRoomsActivity.build` / `applyGraphics` | Somente a base `ff02040a → ff287eb5` |
| DEX40 | `Ps3Activity.showSettings` / `Ps4Activity.showSettings` | Fundo `ff081017 → ff287eb5` |

As doze transparências da R144 em `StationWaveBackground.updatePalette` são exatas; não há paleta por plataforma na sala. Fundos pretos neutros, sidebar, cards, controles, texto, login verde, recuperação, saída, geometria, campos, métodos, callbacks, preferências e processamento são preservados. Gameplay, downloads, saída online, mitigação g52, HLE e multitap não recebem ajuste funcional nesta revisão. A etapa futura de investigação online não está incorporada.

## Baselines e montagem

`evidence/java-background-scope.json` fixa as partições reais R144, todas as classes, os métodos e as substituições únicas permitidas. `baseline-classes` contém os sete donors reais completos; `proposed-smali` contém a alteração direta dos dez literais, com inversão byte exata de cada classe. DEX40 foi decodificado diretamente do APK R144; DEX28/35 são as árvores finais verificadas dos DEX de hashes conferidos contra o APK.

As cópias Java registram os últimos fontes correspondentes disponíveis: Wave final R144, downloads/Hyperspace do snapshot completo R124, Rooms R126 e Sony final R134. Os únicos blocos modificados são os fundos listados. `baseline-java` guarda as fontes originais integrais e a inversão da alteração Java também recupera seus bytes exatos.

**Não restaurar classes Java históricas inteiras no APK.** A classe Rooms R126 antecede reparos funcionais posteriores. A montagem deve partir dos donors reais R144 e aplicar somente os literais dos métodos permitidos. Caso compile Java para transplante, provar antes a equivalência canônica dos métodos alvo ao donor; a prova de fonte desta preparação não afirma que esse gate já foi executado. Após a montagem, decodificar novamente e inverter os literais para recuperar todos os donors reais, preservando todas as outras classes/partições. Nenhum gate de assinatura, runtime, cadastro ou preservação deve ser relaxado.

Esta pasta é somente preparação privada e não representa fonte congelada, APK compilado, instalação ou aceite visual.
