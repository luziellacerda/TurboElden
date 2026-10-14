# R148 — montagem limitada à sinopse dos sistemas

Esta receita recebe somente o APK final e assinado R147, o novo
`libturbo_carousel.so` compilado após reprodução integral da base e os dois
recibos nativos. O compilador do carrossel é uma etapa anterior e separada.

O único comportamento solicitado é retirar o corpo da sinopse no modo de
sistemas. As sinopses de jogos e coleções, navegação e ações permanecem. Como
os três marcadores de motor guardam o SHA do carrossel, a montagem renova esses
três marcadores e os quatro IDs em `engines.json`. Portanto, o APK muda cinco
entradas: carrossel, três marcadores e registro de motores. Preserva as outras
13.855 entradas, inclusive os 40 DEX, bytes do core Dolphin e da rota direta
v3 R146. R147 e a estável R143 não são alteradas.

`recipe/build_native.py` reproduz o ELF R145/R147 byte a byte com os 158
inputs e o comando de compilação originais; depois injeta apenas o cabeçalho
R132 preparado. Compara ABI, rótulos e alinhamento e produz recibo nativo.

`recipe/build_candidate.py` exige SHA/bytes exatos do APK R147, fonte R148
congelada em commit, overlay de uma linha comprovado, reconstrução nativa
R147 idêntica antes da alteração, contratos ELF e 345 hashes de payload. Cria
um APK sem assinatura e um recibo com hashes por entrada em diretório novo no
namespace privado `E:/StationSystemSynopsisR148-20261014`.

`work/sign_r148_system_synopsis_private.py` usa a autoridade original em
armazenamento privado. Confere o certificado, assinatura v2/v3, alinhamento
16 KiB e todas as entradas novamente. O APK assinado permanece privado em E:.
Um kit de servidor com IDs/hashes R148 deverá ser preparado para esta revisão;
os ZIPs R147 e anteriores não comprovam cadastro R148. Compilação e assinatura
não comprovam instalação, aplicação no servidor ou partida física.
