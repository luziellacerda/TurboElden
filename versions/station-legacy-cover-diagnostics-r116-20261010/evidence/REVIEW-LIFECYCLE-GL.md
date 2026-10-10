# Revisão lifecycle, GL, estado e filas

Resultado final: nenhum P0 identificado antes do build.

Confirmado no código:

- a capa base é desenhada enquanto o campo nativo está `PENDING`;
- no online, o `ImageView` permanece visível até o candidato ficar completo;
- candidato e campo confirmado usam objetos separados e troca atômica;
- a chave inclui contexto, textura, identidade, revisão de upload, modelo,
  viewport e dimensões;
- troca de seleção ou upload invalida o candidato;
- o scissor e o restante do estado GL alterado são restaurados;
- quando todas as linhas foram produzidas, uma tentativa de commit bloqueada
  por objeto ainda capturado não executa outro draw de zero linhas;
- publicação limita a janela a nove itens, a revelação a um caminho por 80 ms
  e a fila de capa a um worker;
- cancelamento e geração obsoleta interrompem a publicação em vez de serem
  tratados como falha recuperável.

Pontos para prova física:

1. repetir 20 ciclos de background/foreground e observar memória GL;
2. medir frame pacing durante as quatro linhas por quadro e o tempo até o LED;
3. trocar seleção rapidamente durante o bake;
4. destruir e recriar a surface online durante o bake;
5. validar a retomada do preload após cancelamento, rede ausente e reinício.

`releaseMagazineFieldObjects()` não foi conectado ao lifecycle sem prova de
que o contexto dono está current. Isso evita apagar handles de outro contexto.
