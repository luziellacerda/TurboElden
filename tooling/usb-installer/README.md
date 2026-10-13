# Instalar TurboStations por USB

Conecte o telefone pelo cabo, desbloqueie a tela e aceite a autorização de **depuração USB**. Saia da partida e conclua qualquer download antes de atualizar. Dê dois cliques em **Instalar-TurboStations-USB.bat** e escolha o telefone. Com vários aparelhos conectados, também aparece a opção de instalar em todos, um por vez. Não precisa abrir como administrador.

O instalador confere o SHA256 do APK indicado em **turbostations-apk-teste.json**, identifica somente telefones USB autorizados e usa uma atualização que preserva os dados. Depois da instalação, também tenta conferir o SHA256 do APK no telefone. Se essa leitura não for possível, informa a limitação; se o hash for diferente, informa a divergência. Cada resultado fica em **recibos-usb**, sem número de série do telefone.

Uma partida em segundo plano também bloqueia a atualização. Tocar em Home não basta: use **Sair da partida**. O instalador confere o processo e a tela do jogo online antes de atualizar, sem encerrar nada à força. Se já saiu e ele ainda detectar o jogo, aguarde alguns segundos e execute novamente. A conclusão dos downloads é confirmada por você; o instalador não afirma ter verificado todos os downloads. Ele não desinstala, não apaga dados, não força uma versão anterior e não abre o aplicativo.

**O manifesto publicado identifica o APK final R139 conferido.** Coloque esse APK ao lado dos arquivos ou ajuste `apkPath` para sua cópia; o SHA deve permanecer exato. O manifesto de `outputs` no PC de testes aponta diretamente ao backup F:. Não há APK, chave, serial de aparelho ou caminho privado neste diretório do Git. A R139 está instalada no moto g52 com dados preservados. Seus novos identificadores aguardam cadastro v3 no servidor; partida e saída após perda de sinal continuam pendentes. O BAT e o PowerShell permanecem idênticos à versão anterior.

Para testar uma nova compilação, o manifesto deve ser atualizado com o caminho do APK, a revisão e o SHA256 conferidos durante sua criação. O instalador não escolhe arquivos pela data. Também é possível arrastar um APK sobre o BAT: o arquivo arrastado precisa ter o mesmo SHA256 do manifesto; isso permite usar uma cópia do APK em outra pasta.

Mantenha o BAT, o PowerShell e o manifesto na mesma pasta. Se o backup mudar de unidade, ajuste `apkPath` e `adbPath` no manifesto. O instalador também procura ADB em `platform-tools` ao lado dos arquivos, no SDK Android configurado e no PATH. Não baixa ferramentas automaticamente.

O Windows às vezes não mostra a indicação USB na lista do ADB. Nesse caso, o instalador confirma pelo alvo USB do ADB ou pelo dispositivo USB presente no Windows, comparando o identificador inteiro. Aparelhos por Wi-Fi e emuladores ficam excluídos. Se vários aparelhos não puderem ser identificados com segurança, conecte um de cada vez.

Se aparecer **sem autorização**, desbloqueie o aparelho e aceite a depuração. Se aparecer **offline**, reconecte o cabo. Se o TurboStations continuar em primeiro plano, saia da partida e volte à tela inicial do Android antes de executar novamente. Se o APK tiver assinatura incompatível ou for uma versão anterior, a instalação é recusada para preservar os dados.

Para conferir apenas o arquivo, sem acessar telefone ou instalar, abra o PowerShell nesta pasta e execute:

```powershell
.\Instalar-TurboStations-USB.ps1 -ValidateOnly
```

Para usar um manifesto alternativo de uma compilação conferida:

```powershell
.\Instalar-TurboStations-USB.ps1 -ManifestPath "C:\pasta\manifesto-da-compilacao.json"
```

Testes de simulação, sem telefone, ADB ou instalação:

    .\tests\Check-Installer-Simulations.ps1 -InstallerPath .\Instalar-TurboStations-USB.ps1

Os testes cobrem seleção de USB, exclusão de rede/emulador, variantes Windows, bloqueio de jogo em segundo plano e resultados da conferência do SHA instalado. Em 12/10/2026, a detecção real reconheceu o moto g52 USB pelo alvo USB do ADB no Windows, somente com leitura; isso não valida instalação ou gameplay.
