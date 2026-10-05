# R11 — nomes e sinopses das coleções, 05/10/2026

## Estado

**APK compilado/assinado e conferido no PC; ainda NÃO instalado, porque a USB não apresentou dispositivo.** Último instalado comprovado permanece R9. R10 e R11 são candidatos, não tags estáveis. Não afirmar visual Android ou gameplay sem conferência.

Este APK inclui integralmente a integração do novo servidor publicada no commit **894856e563233dc9d8564e63fa026e1f21f9fec0**. Leia também [handoff técnico R10](../station-library-r10-20261005/README.md), que explica todas as rotas, assinatura, sinopses, atualização automática e pendências Android. Aqui muda somente a apresentação nativa das coleções.

## Pedido atendido

1. Ao entrar numa plataforma com subpastas, a primeira célula continua **Todos os jogos**. Ela inclui também os jogos diretamente na raiz; nenhum jogo foi ocultado ou removido.
2. A célula sintética **Jogos sem subpasta** foi removida. Depois de Todos os jogos aparecem as coleções com os nomes exatos do `folderPath` assinado.
3. Cada célula de coleção recebeu uma faixa com seu nome real. O título da área usa **COLEÇÕES**; o nome específico aparece na informação da seleção. O identificador interno da plataforma permanece intacto para filtro/motor.
4. Se uma coleção contém subcoleções e jogos diretamente nela, a entrada para esses jogos usa o nome da própria pasta, em vez do rótulo genérico Jogos desta pasta. Abrir e Voltar conservam o nível correto.
5. Sinopse descritiva de cada coleção, montada localmente com nome, plataforma, quantidade real e até três títulos reais daquela seleção. Todos os jogos explica a biblioteca completa. Não inventa enredo, gênero, popularidade ou qualidade dos jogos; não consulta IA/servidor adicional.
6. A descrição não começa mais com o nome repetido do console/Todas as subpastas. As sinopses individuais dos jogos vindas do servidor no R10 continuam inalteradas.
7. O renderer permite a textura estática das coleções; o bloqueio de textura reservado aos vídeos das plataformas não se aplica às subpastas. Se já houver capa disponível no modelo, ela é usada; a arte da plataforma continua como fallback. Não cria novo download, vídeo, thread ou shader.

## Código e comportamento

- `native_folders.h`: construção da raiz sem grupo redundante, nome do grupo direto por último segmento, `describeFolder` consulta somente jogos da mesma plataforma/caminho. Kind2 abrange todos; kind1 apenas caminho exato; kind0 abrange coleção e descendentes com separador `/`, evitando confundir RPG com RPG2.
- `collection_presentation.h`: funções puras para nome/caminho e composição limitada da sinopse. Escrita termina em NUL e não corta código UTF-8; sem IO/rede.
- `native_info.h`: usa a descrição da coleção e desenha nomes por célula no renderer nativo. Textos são reaproveitados, no máximo20componentes vinculados à tela; nenhum ciclo próprio ou carregamento externo. Títulos não são desenhados duas vezes pelo loop nativo de filhos.
- `native_formation.h`: desenha os rótulos após as células, mantém efeitos existentes e habilita arte estática apenas no modo de coleções. Vídeos continuam pausados nas coleções.
- `native_carousel.cpp`: título COLEÇÕES no modo de subpastas. IDs de jogos, sessão, download, motores e acesso às salas permanecem os do R10/R9.

## Arquivos e recuperação

- Fonte canônica: `E:\ESTUDO APK\work\station-netplay-20261004`.
- Backup anterior ao ajuste: `collections-r11\before`.
- Novo módulo compilado: `collections-r11\libturbo_carousel.so`.
- APK final: `E:\ESTUDO APK\work\station-netplay-20261004\TurboStations-Colecoes-Nomes-Sinopses-R11-20261005.apk`.
- SHA256: **7c5096d58991a9724537036e18eb42555f290e2f6d673904524520da0d0146d5**; **1.982.770.888bytes**.
- Base R10: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Biblioteca-N64-Sinopses-R10-20261004.apk`, SHA256 **8bc1d2ef1b5864dc1d5359d1df05b90593cf483dff7f48819f7a7a6b52a84c0b**. A cópia idêntica de E: foi removida somente após validar o arquivo de G:.
- R9 instalado também está preservado na mesma pasta G:. `stay_on_while_plugged_in=0` já foi restaurado; nenhuma ação pendente nesse ajuste.
- Certificado **7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825**, pacote `org.turboramastation.frontend`.

## Evidências

- **440 checks** do header real de navegação: remoção da célula redundante, Todos os jogos com raiz, nomes, isolamento por plataforma/caminho, seleção/Voltar, exemplos de sinopse e200ciclos de atualização.
- **6.153 checks** de texto/caminho e limitesUTF8/NUL, incluindo buffers de1a2048bytes.
- Renderer Android26/arm64 compilado com NDKr28c usando imagens/objetos reais, alinhamento16KiB.
- APK assinado/alinhado, comparação SHA256 de todas as entradas com R10: somente **lib/arm64-v8a/libturbo_carousel.so** mudou; **11.102 entradas preservadas**, nenhuma adicionada/removida; compressão preservada. `classes28.dex` do servidor e `classes35.dex` das salas são idênticos aos do R10.
- Suite R10 anterior:659Java,465C++ e paginação de sinopse; não foi alterado Java nesta revisão.

Não houve instalação, desinstalação, limpeza de dados ou implantação Linux nesta revisão. Evidência de R11 no telefone, sincronia de dois aparelhos e medição de consumo permanecem pendentes.

## Compilação e próximo passo

Os scripts desta entrega registram a aplicação, testes e empacotamento. `implement_station_collections_r11.py` já foi executado; não reaplicar sobre a fonte corrente. A base completa e os insumos reais continuam em E:; o diretório Git é um delta de cinco arquivos nativos com manifesto, não um projeto vazio substituto.

Compilar `native/native_carousel.cpp` e `native/video720_posters.o` com o mesmo comando do builder R10 (`--target=aarch64-linux-android26`, `-std=c++17`, `-shared -fPIC -O2`, `-nostdlib -fno-exceptions -fno-rtti -fno-stack-protector -fno-builtin`, `-Wl,-z,max-page-size=16384`, `-Wl,--no-undefined`, soname libturbo_carousel.so, libs/stubs de native: c/dl/log). Scripts de pacote recusam sobrescrever candidato existente. Usar nova saída para uma nova compilação.

Quando o telefone estiver conectado e fora de partida, instalar R11 por atualização (`adb install --no-incremental -r --user 0`), sem limpar dados. Conferir nomes em todas as células, exemplos corretos por coleção, Todos os jogos, jogos da raiz, seleção aninhada/Voltar, textos longos, capa/fallback e sinopses individuais. Também concluir a validação R10 de catálogo/N64/downloads e salas. A integração não pede nova rota de servidor; novos jogos/coleções vêm do catálogo assinado.
