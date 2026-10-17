# R145 — azul céu e faixas solicitadas

Nova etapa visual sobre o APK real da R144. Azul céu `#287EB5` → `#5DAEDE` nos fundos azuis existentes: principal/carrossel, salas, downloads e painéis azuis Sony. Fundos neutros, verde/preto, textos e cartões conservados.

| Sistema | Faixas, na ordem |
|---|---|
| SNES | vermelho, vermelho, cinza |
| NES | roxo, vermelho, cinza |
| N64 | amarela fina, verde, azul, vermelho, amarela fina |
| GameCube | amarelo, verde, roxo, cinza |
| PSX / PS2 | vermelho, azul, amarelo |
| Dreamcast | verde, azul, vermelho, amarelo, laranja |
| FinalBurn Neo | verde, amarelo, laranja |

Outras paletas R144 e cores das ondas das salas permanecem iguais. Quantidade de faixas não altera número de jogadores. N64 amarelas com metade da largura prevista para cada faixa. Geometria central, tempo, 32 segmentos e buffer reutilizado permanecem; cinco faixas geram até 330 vértices/5 desenhos versus 198/3 na R144. Não há novo timer, thread ou alocação; desempenho físico ainda não medido.

Produção DEX usa exclusivamente os donors reais e substitui dez literais em sete classes/nove métodos. Java histórico é referência, nunca restauração de Activities inteiras. Inversão posterior deve recuperar todas as classes originais e preservar os reparos de multiplayer, saída, g52, HLE e downloads. Compilação nativa precisa reproduzir byte a byte a R144 com seus 158 inputs antes do overlay.

Receitas exigem commit novo completo e exatamente oito substituições, 13.852 entradas intactas, zero adições/remoções e 37 DEX integrais. Identidades independentes precisam de kit correspondente novo; não declarar cadastro ou gameplay online por compilar o visual. A investigação N64/PS1/GameCube/Wii continua em etapa posterior. R143 segue estável, sem mover tags/ponteiros. APK, chaves, ROM/BIOS, registros e seriais permanecem privados.
