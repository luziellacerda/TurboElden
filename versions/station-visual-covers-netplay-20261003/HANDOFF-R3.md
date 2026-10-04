# R3 — correção comprovada das sinopses e da exportação de diagnóstico

## Estado atual e autoridade

Este documento prevalece sobre o estado R2 descrito no README histórico. Pasta de compilação: `E:\ESTUDO APK\work\station-visual-covers-20261003`. Branch `feat/station-capas-visuais-netplay-20261003`. Pacote `org.turboramastation.frontend`. APK candidato `E:\ESTUDO APK\work\station-visual-covers-20261003\TurboStations-Capas4-Sinopses-LED-Netplay-R3-20261003.apk`, 1922509146 bytes, SHA-256 **`8ece6384b83f565ec54615186a5940c6e5c47f79d4f03027332181799c4fb807`**. Ainda não instalado: USB ausente ao concluir. O telefone recebeu R2 `31ab80ef...`, por atualização, com hash remoto confirmado. A referência estável congelada não mudou.

R2 abriu com sessão salva e catálogo HTTP200/1816 itens; capas chegaram por quatro workers e apareceram no SNES. Shader MAGAZINE compilou/linkou no driver Android e a ilustração SNES apareceu à direita. Essas observações não representam um benchmark nem teste de partida em rede. A verificação detectou uma falha real nas sinopses; R3 corrige o fonte e o APK. Sem mudança no servidor, licença, saves, jogos ou motores.

## Causa, responsabilidade e primeira divergência

O gerador do app estava lendo `catalogo-candidato-cruzado-20261003.tsv`, uma lista preliminar com IDs `station_*`. O catálogo conciliado preserva os IDs já publicados: 741 itens mantêm seus identificadores anteriores e 1075 não mudam. Usar apenas o candidato foi um erro da preparação dos metadados do aplicativo.

O telefone registrou `GAMEINFO ... id=bba0ae28b358b6581357f6dff15799af; name=Clay Fighter; found=0`. O Java e a ponte JNI preservaram corretamente esse ID; a tabela compilada é que continha outro. Nenhuma alteração da rota ou do servidor é necessária para esta correção. Battletoads USA também mostrou `found=0`; após corrigir o ID ele terá o aviso explícito de ausência, pois está entre as 12 descrições não resolvidas.

Fonte correta e imutável: Servidor-pix commit `54bba11c52f35695fd47eabc7145f42af9990426`, arquivo `docs/station-android/catalogo-conciliado-jogos-capas-downloads-20261003.tsv`, SHA-256 `3542803f0887a3595bfcae6f2c1bd5e860b5ab81df32f308c2f3ac1fbd071f12`. Cópia verificável em `server-inputs/`. O casamento de **todos os 1816** usa plataforma + plataforma XML + ordinal + nome exato; zero itens sem correspondência. `evidence/production-metadata-identity-audit.json` registra as 741 mudanças. O APK não altera os IDs do catálogo nem adota correspondência aproximada por título.

## Alterações de código

- `prepare_visual_metadata.py`: lê somente o mapa conciliado fixado pelo hash, filtra `catalogVisible=yes`, admite os formatos de ID preservados e mantém nome/ordinal exatos. Mantém 1804 descrições e 12 ausências, 644 SNES,191 SNESBR,887 Mega,94 MegaBR.
- `native/station_game_infos.h` e JSONs de sinopses: regenerados com os IDs publicados; os XMLs descritivos existentes e os 36 arquivos legados continuam preservados.
- `native/native_catalog_identity.h` + `native/native_carousel.cpp`: gravação de `native-catalog.tsv` só no primeiro catálogo ou troca de vetor/tamanho. O `station_frontend.cpp::apply` publica catálogos trocando vetores; a conclusão de capa altera revisão/caminhos sem trocar o vetor. O tratamento normal da revisão e da apresentação continua. O TSV é um diagnóstico do catálogo publicado, não um recibo atualizado a cada transferência/instalação.
- `test_visual_metadata.py`: 16 testes, agora incluindo comparação integral com a fonte de produção e regressão dos IDs observados no telefone. A suíte R2 conferia consistência interna do mapa errado; não comparava o resultado à conciliação final. Esse ponto cego foi corrigido.
- `test_catalog_identity.cpp`: 9 casos de primeira carga, repetição de capas, troca de buffer, tamanho e catálogo vazio.

A saída de diagnóstico completa repetia-se em intervalos curtos durante as capas no aparelho R2. A correção retira esse trabalho redundante; não se atribui ganho numérico de FPS/temperatura sem medição no R3.

## Capas, apresentação e rede preservadas

Continuam quatro transferências simultâneas, reposição automática assim que libera vaga, **zero intervalo fixo após sucesso**, cache privado persistente por coverId/revisão e prioridade das capas visíveis seguida da mesma plataforma/pasta. Mantêm-se sessão protegida por leases, descarte de geração antiga, cancelamento quando oculto e respeito a Retry-After após429. A velocidade efetiva depende de rede/servidor/disco/decodificação/ciclo da tela; não é prometida instantaneidade.

O efeito vem do shader original do tema TURBORAMAx, aplicado à capa principal dos jogos. Mantêm-se menu ocioso15FPS, vídeo da plataforma principal30FPS, fotos de console SNES/Mega512RGBA, controles próprios e HUD LZ Games. Todas as regras de configuração/emulação permanecem as do R2.

“Jogar em rede” continua encaminhando às funções existentes de PSP, Flycast e Dolphin. Não existe lobby Station próprio nem Netplay SNES/Mega nesta entrega. Compatibilidade e partida entre dois aparelhos ainda não foram comprovadas; não anunciar suporte universal.

## Testes repetidos no PC

Todos os estágios concluíram sem falha em `E:\ESTUDO APK\work\station-visual-covers-20261003\pc-validation-20261003-221922`; [recibo](pc-validation-r3/PC-TEST-RESULT.json).

| Verificação | Resultado |
| --- | --- |
| Station Java | 384 verificações + 10 repetições adicionais de41 casos de concorrência |
| Fila simulada | 4096 pedidos, pico4, erros0 |
| Cache recriado | 4096 itens, 0 pedidos HTTP extras, 0 workers após fechar |
| C++ |18 casos de fila/retry executados;9 casos de identidade;98 casos de layout |
| Metadados |16 testes incluindo os1816 IDs efetivamente publicados |
| GLSL |Compilação/link GLES100 no ANGLE e leitura de pixels nos quatro quadros de teste |
| Netplay |26 verificações de contratos/caminhos; DEX recompilado idêntico |
| APK |Assinatura original, alinhamento16KiB, CRC completo, 10871 entradas antigas idênticas, quatro substituições previstas, manifesto anterior preservado |

Carga sintética usa fixtures locais; não mede a velocidade real das imagens. Componentes entregues não foram alterados durante a bateria. DEX Station e Netplay permaneceram idênticos; carrossel ARM64 foi recompilado com a correção. Os resultados R2 permanecem em `pc-validation/` e os recibos anteriores em `history/31ab80ef/`.

## Instalação e conclusão pendentes

1. Reconectar USB autorizada, conferir ausência de partida ativa e aplicar R3 por atualização (`adb install --no-incremental -r --user 0`). Nunca desinstalar/limpar dados.
2. Conferir hash do base.apk instalado, abertura com sessão salva, Clay Fighter com sinopse, passagem SNES/Mega e retorno; verificar capas/cache automáticos e ausência de repetição da exportação TSV por capa.
3. Abrir Jogar em rede para conferir a tela no Android; partida com dois dispositivos permanece outro teste.
4. Restaurar `stay_on_while_plugged_in` de3 para o valor original0. Remover somente os três probes próprios listados em `device-evidence/status-r3.json`. Essa limpeza aguarda USB e não envolve dados do aplicativo.

Os 12 textos restantes exigem XML inequívoco. Novas plataformas precisam de catálogo publicado e mapeamento exato; não são inferidas dos 167 XMLs importados. Capacidade40mil continua na revisão separada. A tag estável não foi movida.

## Reprodução e arquivos

Receita principal: `build/build_visual_delivery.py native`, depois `package`; manifesto foi preservado do R2 e validado por `build/verify_visual_manifest.py`. Para alterar o manifesto usar o estágio `manifest` e conferir novamente. `prepare_visual_metadata.py` reconstrói as sinopses usando o mapa pinado e os XMLs locais inventariados. Testes completos por `pc-validation-r3/run_pc_validation.py`, sempre em pasta isolada E:.

Base privada exigida: HUD LZ Games R2 `6b83ed083f825222970b8993ea3c7fc2a1021893da4e4129b73727e433d9ba9b`. Insumos privados documentados em `PRIVATE-BUILD-INPUTS.json`; assinatura original permanece fora do Git. R2 instalado continua guardado em E:. O APK antigo de controles `8f494041...` foi copiado a G:, conferido pelo hash e removido apenas de E: para espaço; ver `archived-controls-apk.json`. O backup de recuperação e o APK base HUD foram preservados.

O contrato HTTP completo, licenças e mapa de funções estão nas seções técnicas do README histórico. Para estado de instalação/hashes usar **este R3** e `device-evidence/status-r3.json`, não as afirmações históricas do R2.
