# Nave e propulsão — pesquisa e implementação de 28/09/2026

## Pedido e diagnóstico

O usuário rejeitou os jatos anteriores e pediu pesquisar como criar uma nave com aparência de jogo realista. A versão anterior usava uma imagem plana de nave, girada em duas dimensões, e jatos separados. Aumentar brilho ou acrescentar amostras de fumaça não resolve a ausência de geometria, parallax e iluminação coerente.

## Referências primárias consultadas

1. **Khronos — materiais glTF PBR:** https://www.khronos.org/gltf/pbr/ e https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html. Base color, metallic/roughness, normal, ambient occlusion e emissive separam aparência do material da iluminação. A implementação usa esses quatro mapas do modelo, conversão de cor e reflexos dependentes do ângulo.
2. **Google Filament:** https://google.github.io/filament/main/filament.html. Referência para materiais e luz em Android, com preocupação de qualidade e custo móvel. Usamos uma BRDF GGX/Schlick com rugosidade; não adicionamos o motor Filament ao aplicativo.
3. **Epic Niagara Fluids:** https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-fluids-in-unreal-engine. Efeitos volumétricos têm custo alto; a documentação apresenta alternativas apropriadas para jogos e imagens pré-calculadas.
4. **Epic Flipbook Baker:** https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-flipbook-baker-quick-start-guide-in-unreal-engine. Alternativa futura para reduzir custo, se a medição no aparelho exigir. Não foi incorporado vídeo nem sprite animado da nave nesta implementação.
5. **BabylonJS Space Pirates:** https://github.com/BabylonJS/SpacePirates. Fonte de um modelo 3D de jogo, com geometria, materiais e posições de motores, sob licença Apache-2.0 do repositório. Licença preservada em `space3d/LICENSE-SpacePirates.md` e no APK.

## Implementação adotada

- Casco 3D com 14.118 triângulos, 15.762 vértices e quatro mapas de material.
- Normais e tangentes, profundidade, perspectiva, rotação nos três eixos e pintura grafite.
- Quatro motores presos às posições originais da malha. Volume de emissão calculado em espaço 3D e visto pela mesma câmera da nave; núcleo quente, dispersão azul e cauda menos opaca.
- Câmera acompanha o voo. A nave mantém presença na tela; curva suavemente e muda de distância sem sumir e reaparecer abruptamente.
- Framebuffer privado 640x640; o estado OpenGL do carrossel é salvo e restaurado. Cena atualizada no máximo a 30 Hz, reutilizada entre quadros.
- Integração na biblioteca C++ existente. Sem Java, WebView, vídeo, sobreposição de interface ou mudanças nas rotas de jogos.
- Prévia no computador usa a mesma geometria e o mesmo conteúdo GLSL, com adaptação de sintaxe para OpenGL desktop. Não equivale a teste de desempenho/compatibilidade no Android.

## Limites

É um efeito visual de jogo; não uma simulação física completa de gases no vácuo. Não foi acrescentado motor Unreal/Filament. A licença e a origem do modelo devem acompanhar redistribuições. A aprovação estética ainda depende do usuário; não declarar “hiper-realista” ou “estável” sem avaliação e medição no aparelho. Os testes antigos de 36 plataformas não comprovam a nova integração gráfica.
