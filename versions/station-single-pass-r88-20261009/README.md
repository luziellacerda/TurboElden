# R88 — teste de consumo com menu em 30 fps

Base completa R87; 214 fontes Java, sem sobreposição de Activities históricas.

- Carrossel a 30 fps, inclusive diálogos. Nenhuma redução para 25 fps. Os relógios dos emuladores permanecem próprios.
- Prévia de vídeo 720 × 720, 30 fps e sem áudio: uma reprodução por seleção. O quadro final é copiado para o cache de imagens existente, depois o decodificador é liberado. Selecionar outra célula ou voltar ao carrossel permite nova reprodução.
- Estrelas: uma passagem pela animação, preservando sua duração e terminando no quadro final. O Java deixa de agendar atualizações após o fim.
- Efeitos LED mantidos exatamente como na R87, tanto no carrossel quanto online. O código nativo e o componente Java de iluminação são byte a byte iguais à base. A versão preliminar sem LEDs foi rejeitada pelo mantenedor e substituída; não é a versão final.

Layout, tamanho das capas, degradê, textos, INSTALADO, fontes, consoles e cores dos botões preservados. Não há recompressão dos vídeos. Nuvens e robô mantêm suas políticas anteriores de atualização; 30 fps é o limite do carrossel, sem aumentar processamento de recursos que já se atualizam mais devagar.

## Implementação e limites

`StationSinglePassVideo720` é carregado pelo carrossel via JNI. O novo nome evita substituir um DEX histórico compartilhado. O player anterior não é iniciado por esse caminho. Há somente um decodificador por vez, operações do MediaPlayer fora da renderização, descarte de callbacks obsoletos e encerramento ao ocultar o menu. O cache de imagens continua limitado.

Somente `classes35.dex` e `libturbo_carousel.so` mudam no APK. Foram conferidas todas as entradas: 13.224 preservadas, incluindo os 59 arquivos MP4, manifesto, runtime, cores e cadastro dos motores. A assinatura original foi conferida antes e depois da montagem. Nenhum ajuste no servidor nem novo cadastro de motores é necessário.

Os testes de política executam 1.011 asserções de compilação C++ e 24 verificações de integração de fonte. A reprodução das fontes Java e carrossel a partir do backup é byte a byte idêntica. Esses testes não comprovam gameplay nem economia térmica prolongada; consulte `STATUS.json`, `INSTALLATION.json` e as medições em `evidence` para o estado observado.

## Backup e reprodução

Use apenas o canal explícito `test-4p` de `release-channels/ACTIVE.json` e `release-channels/rebuild_verified.py`. O canal R76 escolhido pelo mantenedor continua como referência de dois jogadores. R88 é um teste de interface/consumo e não altera a qualificação online herdada. Não selecionar APK pela data do arquivo, nem executar montagens históricas como base atual.

Fontes e documentos podem ser publicados no Git. APK, imagens, vídeos, capturas pessoais, BIOS, ROMs, licenças e logs privados ficam exclusivamente no backup/local de trabalho.
