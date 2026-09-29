# F-16 TURBORAMA — revisão instalada e conferida

Registro: 2026-09-29T09:57:08.255627-03:00

## APK

- Arquivo: E:/ESTUDO APK/work/native-carousel/implementation/TurboramaStation-carrossel-nativo-completo.apk
- Tamanho: 561776134 bytes.
- SHA256 local e instalado: `33e5da3e4ae8b7c28c3dff13e21a3ad08b8554d0d27ed47ceb2ae641c0032c4b`.
- Instalação registrada: 2026-09-29 09:49:27; aparelho RQCY30751WY.
- Atualização por adb install -r; pacote e certificado mantidos.
- Certificado SHA256: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`; assinaturas v2/v3 conferidas.
- Módulo nativo e 6 arquivos de avisos/fontes iguais às cópias locais.

## Visual desta revisão

Duas inscrições TURBORAMA independentes nos ombros esquerdo e direito da fuselagem, com separação no dorso e proporção natural aproximada de 8,21:1. As inscrições nas asas e cauda também tiveram a proporção ajustada. Voo contínuo: inclinações suaves e pequenas mudanças de altura, sempre visível. A ação de entrada/saída do hiperespaço foi removida a pedido do usuário. O F-16 continua renderizado como geometria 3D; posição/tamanho/opacidade são compostos pelo renderer nativo. Nuvens por volume com 64 amostras em alvo 320×180 e névoa distante passam sob os controles, partindo do mesmo ponto de fuga das estrelas (0,65;0,32). O avanço usa o mesmo relógio nativo com velocidade constante. Não é vídeo nem sobreposição Java. Curva, inclinação, altura e motor têm variações suaves; bocal e volume do jato compartilham a transformação da aeronave.

30508 vértices, 40210 triângulos, 4 mapas 2048×2048, 1 saída de motor registrada no manifesto. A iluminação e os materiais usam aproximações para tempo real. A arte aprovada é referência visual; a aeronave animada é geometria 3D.

## Evidências desta revisão

- Android: inicialização, captura/vídeo e ausência de erro fatal no trecho coletado, vinculados ao hash acima.
- 36 catálogos: entrada e retorno nativo aprovados; 7211 itens contados nas listas.
- Computador: harness GLES2 e GLES3 aprovados, zero erros GL e estados registrados preservados; prévia com compilação de shader aprovada. Os relatórios são posteriores aos fontes gráficos atuais e não substituem a captura Android.
- Amostra curta no Android: 59.97 apresentações/s, mediana 16.68 ms, p95 16.75 ms; 0 intervalos acima de 25 ms em 126. Não é teste prolongado de temperatura/bateria nem mede jogos.
- Integridade: 1641 entradas originais preservadas, 439 adições, zero remoções; única entrada original alterada: classes5.dex, ponte nativa existente.
- ROM de referência: tamanho/data preservados conforme relatório: `7132794634|2026-09-28 21:48:50.061750359 -0300`. Isto não verifica todos os jogos nem o conteúdo dos saves.
- Permanecer ligado ao carregar, valor registrado: `0`.

Relatório Android: [f16-device-validation.json](E:/ESTUDO APK/work/native-carousel/implementation/space3d/f16-device-validation.json). Captura: [f16-device-final.png](E:/ESTUDO APK/work/native-carousel/implementation/space3d/f16-device-final.png). Vídeo: [f16-device-motion.mp4](E:/ESTUDO APK/work/native-carousel/implementation/space3d/f16-device-motion.mp4). Registro completo: [space3d-build.json](E:/ESTUDO APK/work/native-carousel/implementation/space3d-build.json).

## Limites e origem

Execução de jogos, downloads, saves e teste térmico/bateria prolongado não foram comprovados por esta verificação. Aprovação visual final cabe ao usuário.

Modelo-base: https://github.com/NikolaiVChr/f16, commit `0d0d3d425a9a852b9cd6a764dedee7c9c72cdf51`, licença GPL-2.0-or-later. Autores, avisos e fontes correspondentes permanecem no APK. A autoria original da geometria não é nossa; regras dos materiais privados não restringem a licença do modelo.
