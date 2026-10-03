# Candidato Station — capacidade de40mil jogos

[Handoff específico para Servidor-pix](../../docs/server/HANDOFF-SERVIDOR-CAPACIDADE-40000-STATION-20261003.md) · [Manifesto](MANIFESTO-CANDIDATO.json) · [Patch de backend](servidor-capacidade-40000.patch) · [Fontes](../station-reconstruction-20261002/)

A estável SNES/Mega foi publicada antes e permanece na tag9793840. Este candidato amplia parser, envelope e ponte nativa, reduz leituras no disco e varreduras. Mantém as nove rotas Station e todas as verificações de assinatura/identidade/arquivo.

353 checks locais,35 nativos Android e9 do índice C# isolado. Catálogo sintético40000; não representa40mil jogos publicados. APK novo compilado/assinado, ainda não instalado; patch não aplicado no servidor. A fixture Android43,76MB também passou em1997ms, com heap máximo256MiB; VmHWM437748KiB mede todo o processo isolado, não apenas Java. Fixtures removidas; ver resultados específicos.

Executar prepare_server_patch.py somente para gerar/revisar patch e fixture local; não implanta. Teste .NET offline no diretório E: gerado pelo script. O manifesto identifica o APK privado; nenhum APK/ROM/BIOS/credencial é publicado no Git.
