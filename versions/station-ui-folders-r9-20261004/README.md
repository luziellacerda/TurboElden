# TurboStations R9 — salas e subpastas

## Atualização posterior do servidor e das fontes — 04/10/2026

Servidor fonte `931030b` em produção, catálogo **8 / 1.973 jogos / 157 N64**. O campo `folderPath` foi publicado, com 313 jogos em subpastas. A importação automática e as capas exatas da revista estão ativas. As fontes desta pasta receberam leitura de metadata, cache de sinopses e consulta automática, conciliadas com a entrega R9 original.

**O APK R9 de hash b5c98ea4 abaixo identifica a compilação anterior a esta integração.** Para incorporar estas fontes ao próximo APK, siga `../station-library-autodiscovery-20261004/README.md` e o overlay com guardas, compilando Java/JNI/carrossel juntos. Os módulos Linux novos estão conferidos, mas não foram assinados nem instalados. R8 continua o último instalado comprovado.

O restante deste README e os recibos R9 registram a compilação original `a325e69`; suas referências à publicação pendente de pastas foram atendidas pelo servidor. A prova no aparelho e a partida entre dois aparelhos continuam pendentes.

## Estado desta entrega — 04/10/2026

**APK compilado, assinado e conferido no PC. Ainda não instalado: telefone ausente na USB.** R8 `8e76d832…` é o último APK instalado e observado; R8B `0a333155…` ficou somente no computador. Esta entrega é candidata, não uma nova versão estável.

| Identificação | Valor |
| --- | --- |
| APK | `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Salas-Subpastas-R9-20261004.apk` |
| SHA256 | `b5c98ea40b915f738e29ef2b2e7168fcdf2d327aa64c862596dff15b5620fdf1` |
| Tamanho | 1.982.754.504 bytes |
| Pacote | `org.turboramastation.frontend` |
| Certificado | `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825` |
| Base R7 | `827723436ac618d3b1745a873813c7781ff10e043abc6033de416c01d774703d` |
| Fonte canônica | `E:\ESTUDO APK\work\station-netplay-20261004` / junction `E:\StationNetplayWork` |

R7, R8 e R8B estão arquivados com hashes conferidos em `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais`. Preservar a tag de recuperação `estavel-station-snes-megadrive-20261003`.

O APK altera quatro entradas: `classes28.dex`, `classes35.dex`, `libstation_frontend.so` e `libturbo_carousel.so`. **11.098 entradas da base foram preservadas**, conferidas por SHA256 individual. Manifesto, motores, controles, mídias e runtime online permanecem iguais. Há um recibo novo em assets. Alinhamento de 16 KiB e assinatura foram verificados.

## Salas: visual e comportamento

- Banner com nome real, plataforma e capa do jogo selecionado.
- Fundo verde e preto, luz diagonal suave, bordas finas e ícones vetoriais próprios.
- Antes de entrar numa sala: jogadores e salas/convites. Depois de entrar: jogadores, sala e chat.
- Mensagens próprias diferenciadas por `fromPeerId`, campo confirmado na implementação do servidor.
- Telas estreitas colocam as ações em uma linha própria; o teclado redimensiona a área disponível.
- As seis ações dos jogos mantêm o acabamento verde e brilho. A fonte do botão online agora usa a mesma referência das outras cinco ações.

A capa do banner vem apenas do cache privado já validado, sem novo download. Leitura limitada a 5 MiB, decodificação reduzida a 256 pixels. O banner anima a cada 64 ms e cancela seus callbacks ao perder foco, ficar oculto ou sair da tela. Criar sala conserva seu brilho apenas quando habilitado, visível e com foco. Não há vídeos, texturas externas ou novas threads para esses efeitos. O consumo real ainda precisa ser medido no aparelho.

Rotas, assinaturas, sessão, snapshots, convites, chat, preparação e lançamento de partidas foram preservados. A tela mostra somente jogadores e salas recebidos do serviço; estados vazios e falhas são explícitos.

## Novo retorno do servidor

Durante este trabalho chegou o retorno `a4814d453a1f193fcbe40a92c8690c4eb5d41fc9`, no Servidor-pix. O operador relata as rotas online publicadas às 11h29, fonte da DLL `77d1dfb50a9982b01d8d649db477e6268dc7a5fb`, com testes HTTPS autenticados. As mudanças de validação foram lidas e preservam o contrato usado pelo app.

Portanto, **não tratar o 404 histórico do R7 como o estado atual das salas**. O R8 mostrou indisponibilidade em sua captura anterior, sem novo código HTTP registrado. Nenhuma conferência Android após a publicação foi feita nesta entrega. Partida P2P entre dois aparelhos continua pendente, mesmo com testes do servidor concluídos.

Os campos `serverDeployed: false` e `installed: false` no recibo do APK significam que **este trabalho Windows** não implantou o servidor nem instalou R9. Não negam a implantação relatada pelo operador.

## Subpastas: integração e limites

O pedido está implementado como organização do catálogo do servidor. A pergunta sobre também ler pastas locais do telefone permanece sem resposta. Não foi criada uma varredura de arquivos arbitrários ou uma nova rotina de importação.

O contrato anterior não enviava hierarquia. A extensão proposta acrescenta `folderPath`, um array opcional de segmentos, dentro de cada item do mesmo catálogo assinado:

```json
"folderPath": ["Selecionados", "Traduções"]
```

Ausente ou `[]` significa raiz. São permitidos até 8 níveis e 80 unidades UTF-16 por segmento. O app recusa tipos incorretos, nomes vazios, controles, barras, `.`/`..` e Unicode inválido. IDs, capas, plataforma, revisões individuais e destinos de download permanecem iguais. Não mudou o limite de 4.096 itens desta linha; o candidato de 40 mil continua separado.

**O servidor ainda precisa publicar o novo campo para as pastas aparecerem.** O código e o indexador estão preparados para o operador. Não houve implantação remota de subpastas. Catálogos atuais continuam funcionando como listas planas.

### Fluxo da navegação

1. Plataforma com hierarquia abre o carrossel nativo de pastas.
2. Na raiz aparecem Todos os jogos, Jogos sem subpasta quando aplicável e as pastas imediatas.
3. Um nível intermediário mostra seus filhos e Jogos desta pasta, quando existirem jogos diretos.
4. Uma folha abre seus jogos, mantendo os índices e IDs originais.
5. Voltar retorna um nível. Plataformas retorna à seleção de sistemas.
6. Plataformas sem pastas mantêm a abertura direta anterior.

Pesquisa, instalados e ações do jogo continuam limitados à plataforma e pasta selecionadas. Pastas vazias não aparecem, porque a hierarquia deriva dos itens. Elas exigiriam um contrato próprio; não foram simuladas.

### Caminho do código

- `StationCatalog.java`: validação do array imutável e persistência no cache.
- `StationFrontend.java`: sétimo campo NUL opcional na publicação Java/JNI.
- `station_frontend.cpp`: aceita seis campos antigos ou sete novos; troca o mapa de pastas junto com o catálogo na thread SDL.
- `station_collections.hpp`: filhos imediatos, contagens e isolamento entre plataformas; delimitadores exatos evitam confundir RPG com RPG2.
- `native_folders.h`: fachada de apresentação para pastas; jogos usam os índices da coleção real. Nenhum item sintético é enviado a baixar, jogar ou apagar.
- `native_carousel.cpp`: seleção, pesquisa e retorno ligados diretamente às ações nativas. A ação 4 continua sendo Voltar; Back do Android/controle também sobe um nível.
- `native_info.h`, `native_skin.h`, `native_laser.h`: informações e apresentação das pastas.
- `native_system_video720.h`: pausa vídeos nos níveis de pastas. Política anterior de 15/30/60 FPS preservada.

As estruturas nativas mantêm Item de `0xe8` e Catalog de `0x138` bytes. As novas funções `StationCatalog_folderRevision`, `StationCatalog_itemFolderPath` e `StationCatalog_visitFolders` são chamadas na thread SDL. Ponteiros emprestados são copiados durante a chamada.

## Testes executados no PC

| Área | Resultado |
| --- | --- |
| Cliente Java existente | 591 verificações: API, sessão, armazenamento, instalação, quatro capas concorrentes, TLS e publicação atômica |
| Metadado de pastas Java | 29 verificações de cache, identidade, compatibilidade e recusas |
| Parser real C# | 20 verificações; servidor compilado sem avisos/erros |
| Agrupamento C++ | 36 verificações, incluindo 4.096 itens |
| Navegação nativa | 429 verificações, incluindo 200 ciclos, níveis, Todos, Voltar e preservação de índices |
| Botões | 34 regressões de UI/rotas e 1.440 malhas reais |
| UI das salas | 6 verificações adicionais de cache, composição e ciclo de vida dos efeitos |
| Indexador | Entrada intacta, IDs/capas/descritores preservados, repetição sem alteração, saídas e raízes incorretas recusadas |
| Compilação | Android API 34, DEX e bibliotecas ARM64 |
| APK | Assinatura, alinhamento e comparação integral das entradas |

Os testes nativos de navegação usam o header real com uma coleção sintética no computador. Não equivalem à execução da ponte JNI no telefone. Os testes não comprovam visual Android, consumo, produção de subpastas ou sincronismo de partida.

## Reprodução

Esta pasta é uma sobreposição sobre a fonte R7 em `versions/station-online-20261004` (commit `dd6aff172761f40c9b8eea2d3e2c1c34a0c79034`) e R8 em `versions/station-ui-r8-20261004` (`ebd1199a4f024640a855dd891bc1bfd35d465d45`). Demais fontes e objetos grandes permanecem nessas bases e nos insumos locais identificados. Não misturar com a árvore de 40 mil itens.

1. Copiar `native/`, `netplay/` e `station/` desta versão para a raiz canônica, preservando os demais arquivos.
2. Executar `build_station_folders.py`: testes Java, DEX e ponte ARM64 em `folders/build`.
3. Executar `build_station_ui_r8.py` — nome histórico — para reconstruir carrossel e salas. `netplay/build-r8` contém o DEX R9 nesta rodada; não é o DEX do APK R8 arquivado.
4. Executar os testes R9 no workspace original. Os caminhos de referência e ferramentas estão explícitos nos scripts.
5. Executar `package_r9.py` somente com o destino inexistente e base R7 de hash conferido. O empacotador compara cada entrada e usa o certificado existente.
6. Instalar por atualização, fora da emulação: `adb install --no-incremental -r --user 0 <APK>`. Não desinstalar, limpar dados ou copiar correções manualmente para o telefone.

## Próxima conferência no aparelho

- Conferir nome/capa, botões, dimensões, teclado, paisagem/retrato e retorno sem login.
- Usar Reconectar para consultar o serviço online já relatado como ativo; testar sala, convite e chat com duas licenças.
- Homologar partida entre dois aparelhos e redes alcançáveis separadamente.
- Após publicação de `folderPath`, testar raiz, dois níveis, pesquisa, instalados, download do item correto e retorno.
- **Restaurar `stay_on_while_plugged_in=0` ao reconectar.** O valor foi alterado temporariamente para 3 na conferência R8; a USB caiu antes de restaurar. Não afirmar restauração sem comando bem-sucedido.

As pendências antigas de outras plataformas, células azuis e compatibilidade de novos motores permanecem no handoff R7. Esta entrega não declara essas questões resolvidas.
