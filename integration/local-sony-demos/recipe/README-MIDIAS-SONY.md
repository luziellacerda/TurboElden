# Vídeos locais de PS3 e PS4

`sony_media.py` prepara apenas os arquivos privados necessários ao motor de
vídeos existente. Os originais pertencem à pasta `caratulas` do tema TURBORAMAx;
não selecionar `caratulasnew`, vídeos de gameplay ou arquivos pela data.
Os dois hashes e tamanhos reais estão fixados na receita. São HEVC, 720 × 720,
24 fps, 6,041667 segundos e sem áudio. Os MP4 são copiados byte a byte, sem
recompressão nem ampliação da taxa de quadros. A apresentação continua limitada
a 30 fps pelo código atual.

## Preparação privada

```text
python -B integration/local-sony-demos/recipe/sony_media.py --native-inputs <inputs-R124> --ndk-bin <NDK-bin> --out <saida-privada> --ffmpeg <ffmpeg.exe> --ffprobe <ffprobe.exe> --media-root <pasta-com-ps3.mp4-e-ps4.mp4>
```

A API `prepare(native_inputs, ndk_bin, out, ffmpeg, ffprobe, *, media_root=None)`
devolve `payloads`, `includeDirectory`, `extraObjects`, `receiptPath` e
`sourceTransform`. A raiz de mídia pode ser a pasta original em G: ou a cópia
única de reconstrução em F:, com os mesmos arquivos e hashes. FFmpeg/ffprobe
também exigem os executáveis locais conferidos. Nenhum vídeo, poster, ferramenta
ou objeto binário é publicado com as fontes.

Cada primeiro quadro é extraído com FFmpeg em RGB565 little-endian, de baixo
para cima, exatamente 1.036.800 bytes. O objeto AArch64 usa `incbin` relativo e
símbolos ocultos; não altera a lista de símbolos públicos da biblioteca final.

## Integração no build

1. Reproduzir e conferir a biblioteca R128 de referência com os inputs antigos,
   antes de aplicar esta preparação.
2. Aplicar `result["sourceTransform"]` ao C++ atual. Ela muda somente o include
   de `native_system_video720.h` para `sony_native_system_video720.h`.
3. Acrescentar `result["includeDirectory"]` aos includes do compilador e
   `result["extraObjects"]` aos objetos da ligação. Manter o objeto original
   `d1/video720_posters.o` e todos os outros objetos existentes.
4. Acrescentar exclusivamente os dois `payloads` ao pacote:
   `assets/turbo-system-videos/720-ps3.mp4` e
   `assets/turbo-system-videos/720-ps4.mp4`.
5. Vincular o SHA da receita e `sony-media.json` aos recibos de compilação,
   identidade e montagem; conferir bytes/hashes dos assets finais e headers/objeto.

Os headers adicionais preservam todas as 44 entradas antigas do mapa e todas
as 58 entradas antigas dos posters; passam a 46 e 60, respectivamente. A
capacidade de identificação dos quadros deriva dessa tabela, mas o orçamento
de texturas residentes permanece o mesmo. Os nomes das plataformas são
exatamente `Playstation 3` e `Playstation 4`.

O corpo do motor nativo fica byte a byte igual, com somente dois includes de
dados redirecionados. Permanecem um único decodificador, reprodução única,
interrupção dois quadros antes do fim, suspensão ao ocultar/abrir menus e opções
de economia. Não se adiciona decodificação nos vizinhos nem trabalho por quadro.

Um diretório concluído pode ser reutilizado somente se fontes, ferramentas e
todos os arquivos gerados continuarem idênticos ao recibo. Diretórios parciais
ou desconhecidos não são apagados nem sobrescritos pela receita. Preparação não
comprova aprovação visual no aparelho nem gameplay dos emuladores.
