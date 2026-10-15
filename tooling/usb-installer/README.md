# Instalar TurboStations por USB

## Cadastro R165 confirmado pelo servidor — 15/10/2026

Os quatro motores e os modos R165 estão cadastrados e passaram na consulta
assinada pública. A correção de saída confirmada do anfitrião também está ativa.
Ler [recibo efetivo](../../docs/server/r165/server-return.json) e
[teste físico](../../docs/server/r165/README.md). O manifesto de exemplo deste
Git foi atualizado para esse estado. Nenhum APK, EXE, instalação ou arquivo
privado do computador Windows foi alterado por este retorno do servidor.
R165 continua candidata; R164 permanece estável até o teste nos aparelhos.

## Instalador sempre atual

Neste computador, abra sempre `E:\TurboStations-Instalador-Atual\Instalar-TurboStations-USB.exe` (ou o atalho na Área de Trabalho). A janela mostra a revisão disponível e permite escolher o telefone USB que você quiser atualizar. Preparar uma revisão nova **não instala em nenhum telefone** e não deixa serviço de atualização rodando.

Depois de assinar e conferir **cada** APK novo, a etapa final obrigatória é executar `publish_current_installer.py` com o caminho explícito do APK e da prova final de assinatura. O publicador confere tamanho, SHA-256, certificado original, assinaturas v2/v3, alinhamento e nome do pacote Android; só então troca o manifesto do instalador em endereço fixo. O APK continua no diretório privado de origem, sem segunda cópia de 2,7 GB. Não escolha APK por data, não publique um unsigned e não coloque APK ou chave no Git. Exemplo da R165:

```powershell
python .\tooling\usb-installer\publish_current_installer.py --apk 'E:\StationVisualR165Combined-20261015\final\TurboStations-Premium-R165-combined.apk' --proof 'E:\StationVisualR165Combined-20261015\package\final-apk-proof.json'
```

Na primeira preparação de um computador, acrescente `--bootstrap-from 'E:\StationVisualR165Combined-20261015\installer'`. O instalador fixo mantém o mesmo EXE nas revisões seguintes: ele lê revisão, aviso, APK e SHA-256 do manifesto atualizado. Só reconstrua o EXE quando seu próprio código mudar. Se uma publicação falhar, o manifesto anterior permanece; corrija a causa antes de disponibilizar a revisão nova. Se a janela estiver aberta durante uma publicação, feche e reabra antes de escolher o telefone. O publicador não acessa USB. A instalação começa somente quando o usuário abre o EXE, seleciona o aparelho e clica em **Instalar no telefone**.

Conecte o telefone pelo cabo, desbloqueie a tela e aceite a autorização de **depuração USB**. Saia da partida, conclua qualquer download e deixe a tela inicial do TurboStations ou do Android aberta. Abra **Instalar-TurboStations-USB.exe**: a busca USB começa uma vez automaticamente e, se houver só um aparelho, ele já aparece selecionado. Marque a confirmação de que ele está livre e clique em **Instalar no telefone**. Quando trocar de telefone, clique em **Atualizar USB**. Modelos iguais aparecem com um sufixo do identificador USB apenas na lista local; o recibo não grava esse identificador. A janela mostra quatro etapas: conferir APK, preparar USB, instalar e validar. Na leitura do APK, a barra mostra a porcentagem real dos bytes conferidos na mesma passagem do SHA256. Durante as operações do Android, mostra atividade e tempo decorrido; o ADB não informa porcentagem confiável da transferência ou instalação. Na conclusão, as quatro etapas e a barra ficam completas. Se houver bloqueio, a etapa para, o motivo aparece em destaque e o instalador informa se a transferência chegou a começar. Os registros detalhados ficam em **Detalhes técnicos**, e os comprovantes em **Abrir recibos**. O botão **Verificar APK** confere tamanho e SHA256 sem acessar o telefone. A interface instala um aparelho por vez; o BAT mantém a opção de instalar em todos, um por vez. Não precisa abrir como administrador. O EXE usa o mesmo PowerShell do BAT e não cria serviço nem mantém consulta contínua. O servidor ADB, compartilhado com outras ferramentas de depuração, pode continuar em execução depois que a janela fechar.

O instalador confere primeiro o tamanho e depois o SHA256 do APK indicado em **turbostations-apk-teste.json**, identifica somente telefones USB autorizados e usa uma atualização que preserva os dados. Se abrir a janela antes de copiar o APK, a interface mostra o arquivo esperado e os telefones conectados. Após a cópia terminar, o instalador confere o SHA-256 automaticamente; **Verificar APK** permite repetir a conferência sem acessar o telefone. Depois da instalação, também tenta conferir o SHA256 do APK no telefone. Se essa leitura não for possível, informa a limitação; se o hash for diferente, informa a divergência. Cada resultado fica em **recibos-usb**, sem número de série do telefone.

Se o APK assinado já estiver no telefone com o mesmo SHA256, a janela informa **Versão já instalada** e não transfere o arquivo novamente. O relatório histórico **Last ANR service** do Android não é tratado como serviço em execução; downloads e serviços atuais continuam bloqueando uma atualização real.

Uma partida em segundo plano também bloqueia a atualização. Tocar em Home não basta: use **Sair da partida**. O instalador aceita as telas iniciais do TurboStations e de login quando não há jogo ou serviço ativo. Ele confere o processo online, o histórico de Activities dos jogos e os serviços do app, inclusive os de download, antes de atualizar. Se apenas o motor N64 permaneceu ativo após a saída e nenhuma tela de jogo, sessão online ou download existir, o instalador encerra o aplicativo ocioso, reconfere os serviços e prossegue sem apagar dados. Um download real continua bloqueando. Você também confirma que concluiu downloads; a verificação de serviços não substitui essa confirmação. Consultas ADB têm prazo de 60 segundos, a conferência do APK no telefone tem até dez minutos, e a instalação tem até 30 minutos. A janela também tem um limite para uma operação inteira. Se a instalação perder resposta, confira a versão no telefone antes de repetir: o estado pode ser incerto. O prazo encerra só o cliente ADB daquela operação, sem mandar desligar o servidor compartilhado. O instalador não desinstala, não apaga dados, não força uma versão anterior e não abre o aplicativo.

**O manifesto de exemplo nesta fonte identifica o APK candidato R165 conferido.** Ele contém caminho, tamanho e SHA256, sem o arquivo de 2,7 GB no Git. No pacote privado R165, o APK assinado único fica em `../final/`; o instalador fixo usa caminho absoluto para esse mesmo arquivo e não cria cópia. A R164 permanece como retorno estável até a homologação R165. O servidor confirmou o cadastro das quatro identidades R165 no [recibo aplicado](../../docs/server/r165/server-return.json); faltam os testes físicos de partida e saída do anfitrião. O EXE chama o mesmo PowerShell do BAT, sem uma segunda lógica de instalação.

Para testar uma nova compilação, use o publicador acima ao terminar a assinatura; ele atualiza o manifesto com caminho, revisão, tamanho e SHA256 conferidos. O instalador não escolhe arquivos pela data. Também é possível arrastar um APK sobre o BAT: o arquivo arrastado precisa ter o mesmo SHA256 do manifesto; isso permite usar uma cópia do APK em outra pasta.

Mantenha o EXE, o BAT, o PowerShell e o manifesto na mesma pasta. No instalador permanente, o manifesto aponta para o APK assinado pelo caminho absoluto: mantenha esse arquivo no lugar até publicar a próxima revisão. Pacotes portáteis antigos podem usar caminho relativo `../final/`, desde que as duas pastas sejam movidas juntas. O instalador procura ADB em `platform-tools` ao lado dos arquivos, no SDK Android configurado e no PATH. Não baixa ferramentas automaticamente.

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

Os testes cobrem seleção de USB, exclusão de rede/emulador, variantes Windows, bloqueio de jogo em segundo plano e resultados da conferência do SHA instalado. A publicação do instalador fixo confere o APK único e termina sem acessar telefone ou instalar. O cadastro R165 no servidor foi confirmado; a instalação no segundo telefone, o gameplay Android e a saída do anfitrião ainda exigem conferência física separada.
