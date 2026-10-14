# Instalar TurboStations por USB

Conecte o telefone pelo cabo, desbloqueie a tela e aceite a autorização de **depuração USB**. Saia da partida, conclua qualquer download e deixe a tela inicial do TurboStations ou do Android aberta. Abra **Instalar-TurboStations-USB.exe**: a busca USB começa uma vez automaticamente e, se houver só um aparelho, ele já aparece selecionado. Marque a confirmação de que ele está livre e clique em **Instalar no telefone**. Quando trocar de telefone, clique em **Atualizar USB**. Modelos iguais aparecem com um sufixo do identificador USB apenas na lista local; o recibo não grava esse identificador. A janela mostra quatro etapas: conferir APK, preparar USB, instalar e validar. Na leitura do APK, a barra mostra a porcentagem real dos bytes conferidos na mesma passagem do SHA256. Durante as operações do Android, mostra atividade e tempo decorrido; o ADB não informa porcentagem confiável da transferência ou instalação. Na conclusão, as quatro etapas e a barra ficam completas. Se houver bloqueio, a etapa para, o motivo aparece em destaque e o instalador informa se a transferência chegou a começar. Os registros detalhados ficam em **Detalhes técnicos**, e os comprovantes em **Abrir recibos**. O botão **Verificar APK** confere tamanho e SHA256 sem acessar o telefone. A interface instala um aparelho por vez; o BAT mantém a opção de instalar em todos, um por vez. Não precisa abrir como administrador. O EXE usa o mesmo PowerShell do BAT e não cria serviço nem mantém consulta contínua. O servidor ADB, compartilhado com outras ferramentas de depuração, pode continuar em execução depois que a janela fechar.

O instalador confere primeiro o tamanho e depois o SHA256 do APK indicado em **turbostations-apk-teste.json**, identifica somente telefones USB autorizados e usa uma atualização que preserva os dados. Se abrir a janela antes de copiar o APK, a interface mostra o arquivo esperado e os telefones conectados. Após a cópia terminar, o instalador confere o SHA-256 automaticamente; **Verificar APK** permite repetir a conferência sem acessar o telefone. Depois da instalação, também tenta conferir o SHA256 do APK no telefone. Se essa leitura não for possível, informa a limitação; se o hash for diferente, informa a divergência. Cada resultado fica em **recibos-usb**, sem número de série do telefone.

Se o APK assinado já estiver no telefone com o mesmo SHA256, a janela informa **Versão já instalada** e não transfere o arquivo novamente. O relatório histórico **Last ANR service** do Android não é tratado como serviço em execução; downloads e serviços atuais continuam bloqueando uma atualização real.

Uma partida em segundo plano também bloqueia a atualização. Tocar em Home não basta: use **Sair da partida**. O instalador aceita as telas iniciais do TurboStations e de login quando não há jogo ou serviço ativo. Ele confere o processo online, o histórico de Activities dos jogos e os serviços do app, inclusive os de download, antes de atualizar. Se apenas o motor N64 permaneceu ativo após a saída e nenhuma tela de jogo, sessão online ou download existir, o instalador encerra o aplicativo ocioso, reconfere os serviços e prossegue sem apagar dados. Um download real continua bloqueando. Você também confirma que concluiu downloads; a verificação de serviços não substitui essa confirmação. Consultas ADB têm prazo de 60 segundos, a conferência do APK no telefone tem até dez minutos, e a instalação tem até 30 minutos. A janela também tem um limite para uma operação inteira. Se a instalação perder resposta, confira a versão no telefone antes de repetir: o estado pode ser incerto. O prazo encerra só o cliente ADB daquela operação, sem mandar desligar o servidor compartilhado. O instalador não desinstala, não apaga dados, não força uma versão anterior e não abre o aplicativo.

**O manifesto de teste identifica o APK candidato R159 conferido.** Ele contém nome, tamanho e SHA256 do APK, sem o arquivo de 2,7 GB no Git. Coloque o APK assinado ao lado do EXE, BAT, PowerShell e manifesto. A R157 permanece como retorno estável; a correção N64 da R159 precisa de partida física após o cadastro das novas identidades no servidor. O EXE chama o mesmo PowerShell do BAT, sem uma segunda lógica de instalação.

Para testar uma nova compilação, o manifesto deve ser atualizado com o caminho do APK, a revisão e o SHA256 conferidos durante sua criação. O instalador não escolhe arquivos pela data. Também é possível arrastar um APK sobre o BAT: o arquivo arrastado precisa ter o mesmo SHA256 do manifesto; isso permite usar uma cópia do APK em outra pasta.

Mantenha o EXE, o BAT, o PowerShell, o manifesto e o APK na mesma pasta. Os caminhos relativos do manifesto acompanham a pasta quando a letra da unidade muda. O instalador também procura ADB em `platform-tools` ao lado dos arquivos, no SDK Android configurado e no PATH. Não baixa ferramentas automaticamente.

Para reconstruir o EXE a partir de `UsbInstallerLauncher.cs` com o compilador .NET Framework do Windows, use a pasta do pacote como saída:

```powershell
& "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /out:"C:\pasta-do-pacote\Instalar-TurboStations-USB.exe" /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll .\UsbInstallerLauncher.cs
```

O Windows às vezes não mostra a indicação USB na lista do ADB. Nesse caso, o instalador confirma pelo alvo USB do ADB ou pelo dispositivo USB presente no Windows, comparando o identificador inteiro. Aparelhos por Wi-Fi e emuladores ficam excluídos. Se vários aparelhos não puderem ser identificados com segurança, conecte um de cada vez.

Se aparecer **sem autorização**, desbloqueie o aparelho e aceite a depuração. Se aparecer **offline**, reconecte o cabo. Se o instalador detectar qualquer tela do TurboStations além das telas iniciais permitidas, volte à tela inicial do aplicativo ou do Android antes de repetir. Esse bloqueio acontece antes de transferir o APK. Se o APK tiver assinatura incompatível ou for uma versão anterior, a instalação é recusada para preservar os dados.

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

Os testes cobrem seleção de USB, exclusão de rede/emulador, variantes Windows, bloqueio de jogo em segundo plano e resultados da conferência do SHA instalado. Em 14/10/2026, a lista USB detectou o moto g52 e a verificação do APK R159 conferiu tamanho e SHA-256 sem instalar novamente. A R159 já havia sido instalada no g52; o jogo N64 online ainda depende de teste após o cadastro no servidor.
