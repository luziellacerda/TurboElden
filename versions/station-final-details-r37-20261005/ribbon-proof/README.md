# Faixa INSTALADO — R37

Implementação: `native_installed_tag.h` e helper puro `station_installed_ribbon.h`.

A faixa mantém a diagonal, o canto e a largura usados na R36. A nova face usa oito gradientes verdes, dois chanfros, linhas finas de luz, dobras com três planos por extremidade e sombra de contato com queda suave em três níveis. Um reflexo oblíquo atravessa a superfície em 3,6 segundos; um pequeno brilho especular acompanha o chanfro inferior. A animação perde toda a intensidade antes de reiniciar. O texto INSTALADO conserva o componente, a cor clara, a posição e o ajuste de tamanho anteriores.

O teste de instalado, os bloqueios em modais e plataformas, o limite durante a navegação e a seleção do item são os mesmos da R36. Não há nova interação, imagem empacotada, relógio, thread ou log. O desenho usa o horário já disponível do SDL.

## Custo e validação

- Uma chamada de geometria nativa e uma chamada do texto em cache por quadro visível.
- 226 vértices sem o brilho especular; 274 com o brilho. Buffer limitado a 448.
- A conversão RGBA usa exatamente a inversão de bytes de `Renderer::convertColor` em `libmain+0x2e3980`; evita chamada nativa por vértice.
- Teste local: 18.000 malhas, cinco larguras de 160 a 800 pixels, 13.253.767 verificações. Conferidos limites finitos, superfície estática, buffer e continuidade entre 0 e 3.600 ms.
- Compilação isolada ARM64 Android, C++17, `-nostdlib`, sem exceções/RTTI e com avisos tratados como erros: passou.
- `ribbon-proof.png` é uma rasterização dos vértices reais para inspeção do desenho. A fonte do texto nessa prova é aproximada; não é uma captura do aparelho.

Não foram executados build principal, instalação, Git ou ações no telefone. O build integrado permanece a cargo do agente principal.
