# Recuperação exata

1. Resolver a tag `estavel-station-snes-megadrive-20261003` sem mover tags históricas.
2. Ler o manifesto e comparar o SHA256 do APK privado `E:\ESTUDO APK\estaveis\2026-10-03-station-snes-megadrive\TurboStations-ESTAVEL-SNES-MegaDrive-20261003.apk` com `3b355b02e4efab1801ccf899f77a5bc0d4d95e1c622d8cb9c3a3e1f35c192d17`.
3. Com o jogo encerrado normalmente, atualizar o pacote `org.turboramastation.frontend` com a mesma assinatura, usando `adb install --no-incremental -r --user 0`. Não desinstalar nem limpar dados.
4. Conferir o APK instalado, sessão,1816 itens/revisão3, capas e os jogos já instalados.
5. A base de build é d8104343, não um dos APKs candidatos intermediários. Fontes canônicos em `E:\ESTUDO APK\work\turbostations-reconstruction-20261002`, mirror no Git `versions/station-reconstruction-20261002`. Receita detalhada no handoff, seção13.

O Git não guarda a chave privada, APK/base, ROMs ou BIOS. Se o APK congelado faltar, reconstruir com as dependências exatas e validar o novo artefato; não afirmar hash idêntico automaticamente. Se a chave Keystore do telefone tiver sido apagada, recuperação administrativa da licença é necessária; não contornar autenticação. Esta recuperação não troca índice/DLL do servidor.
