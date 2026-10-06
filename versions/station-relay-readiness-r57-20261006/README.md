# Prontidão online R55 conciliada com a sucessora visual R57

Base funcional recebida: `9d3d45f048aa44bb2ee9c41f567e985901628daa`, em `../station-current-r55-20261006`. Sucessora visual considerada: `8980cd422d63068299b5e9946c120f81a9c94f29`, em `../station-layout-r57-20261006`. APK atual de referência: SHA-256 `e6159fa3564f0b30c1415b062f42e08e47ea625832e1b2640375b3e8b2b55566`, instalado no Motorola segundo o recibo recebido. A versão do outro telefone precisa ser conferida.

Este diretório fornece **uma implementação de três arquivos sobre a composição R55 + R57**. O snapshot recebido permanece intacto. `R57.patch` mostra as alterações; `evidence/source-preservation.json` identifica os 155 arquivos Java preservados, os dois alterados e o arquivo adicionado.

## Funcionamento

1. O servidor aceita dois membros prontos e publica `starting`. Só o anfitrião abre o motor.
2. `StationHostConnector` espera a porta TCP real em `127.0.0.1`, com prazo de 45 segundos. A primeira conexão bem sucedida fica aberta como o fluxo da partida. O aviso JNI apenas acelera a próxima tentativa.
3. `StationRelayTunnel` só emite `ready` após TCP conectado e WSS aberto com o pin/protocolo esperados. A Activity descarta o callback se a sessão terminou, parou ou perdeu a conexão.
4. A Activity envia evento3 pelo canal `StationSessionChannel` da R54. O proprietário atual `StationGameSession` envia `host-listening`; o servidor muda para `connecting`, mantendo a geração do relay.
5. Só então o convidado inicia. ROM, motor, runtime e opções continuam sendo comparados pelos componentes atuais.

O canal normalizado em ambos os sentidos, `StationExitPanel`, saída idempotente em `finish/onDestroy`, evento4, limpeza do segredo e retorno às salas foram preservados. Falhas de motor e transporte aparecem em etapas distintas. Um aviso ocorrido antes de `onStart` é apresentado quando a Activity fica visível. O fechamento cancela a espera e fecha o socket pendente.

**Sem alteração de servidor necessária para este delta.** API, banco e serviços de produção não foram modificados. O catálogo, downloads, capas, controles locais e motores nativos não entram no delta. Os controles online continuam sendo os do RetroArch.

## Verificado neste Linux

- 346 arquivos da base R55 e 14 arquivos do overlay R57 conferidos por tamanho e SHA-256. A composição dos 157 Java R57 coincide com o recibo original de produção.
- 39 verificações de TCP/TLS/relay passaram na implementação funcional R55, mantida idêntica nesta composição R57; 12.583.029 bytes em cada direção e 50 entradas ordenadas.
- 255 verificações da política de salas, entrada, códigos, revisão e comunidade passaram; os componentes testados permanecem idênticos no overlay visual, sem repetir testes por mudança de layout.
- 158 fontes Java compilaram em Java8/API34. A compilação foi **api-check-only**, com um classpath derivado para conferir interfaces; não produziu DEX.
- O empacotador recusou recibos R41/R55 e compilação api-check-only antes de ler APK/chave ou criar pacote.
- O túnel recebido na R55 tem exatamente os mesmos bytes do túnel R41 (`d2e1cecc…`). A falha isolada sem JNI registrada no candidato anterior aplica-se a esse componente idêntico; não é uma nova reprodução no Android R55.

Os 454 checks Android de Parcel são evidência **recebida da R54**, cujo código foi preservado; não foram repetidos neste Linux.

## Compilar no PC de produção

Usar uma cópia do repositório que contenha este diretório e o snapshot R55 completo. Ler primeiro o retorno `docs/server/RETORNO-ANALISE-APP-R55-STATION-20261006.md`. Não executar as receitas antigas da R41 ou o empacotador da R55 sobre a R57.

```powershell
python versions/station-relay-readiness-r57-20261006/recipes/build_candidate.py --output "E:\ESTUDO APK\work\station-relay-readiness-r57-20261006"
```

O build normal exige o `station-client.jar` original de produção, SDK34 e D8 pelos hashes exatos, restaura 156 fontes R55, aplica a Activity de salas e o novo StationCreateGameCard da R57, verifica o overlay e aplica os três arquivos deste diretório. Os 158 fontes finais preservam a célula Criar sala, a barra fina e o bitmap compartilhado da sucessora. Gera Java8/DEX minAPI26. Recusa diretório de saída existente. Não substituir dependências ausentes por stubs; o modo api-check-only não pode ser empacotado.

`package_candidate.py` recebe a chave original e nomes de variáveis de ambiente contendo as senhas, definidos privadamente pelo operador do PC. Não passar uma senha literal em argumentos nem publicá-la no handoff.

```powershell
python versions/station-relay-readiness-r57-20261006/recipes/package_candidate.py --workspace "E:\ESTUDO APK\work\station-relay-readiness-r57-20261006" --output-apk "G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Conexao-Host-R57-Candidato-20261006.apk" --keystore "CAMINHO_DA_CHAVE_ORIGINAL" --ks-key-alias "ALIAS_ORIGINAL" --ks-pass-env STATION_SIGNING_PASSWORD
```

O empacotador exige o APK R57 integral pelo hash acima, verifica as fontes do workspace e o DEX, conserva todas as entradas funcionais exceto `classes35.dex`, confere assinatura original `7b16ee1a…` e alinhamento16KiB. `classes28.dex`, carrossel R57, HUD, mídia e bibliotecas dos motores são comparados byte a byte com o APK base. A saída só é copiada após as verificações; não sobrescreve um APK existente. A assinatura gera novos registros de assinatura próprios do pacote.

**Não há novo DEX/APK compilado ou instalado por esta entrega Linux.** O APK completo, classpath original e chave de assinatura estão no PC. O empacotador foi conferido por sintaxe e pelas recusas obrigatórias; assinatura, alinhamento e preservação do pacote final precisam passar no PC. Esta entrega Linux não gerou um novo APK sucessor da R57 instalada.

## Testar em dois aparelhos

Atualizar preservando assinatura e dados, sem desinstalar ou limpar o aplicativo. Conferir SHA integral instalado em cada aparelho e hashes dos motores. Criar uma sala nova, usar a mesma edição de Battletoads, juntar os dois membros, ambos Pronto e anfitrião Iniciar.

Capturar, em arquivos privados, horário UTC, APK/DEX por aparelho, sala, geração de início e papel. Cruzar `launch stage=prepare`, `relay-ticket-received`, `activity`, `native-listening` quando houver, `local-stream-ready`, `host-listening-ack`, estado `connecting` do convidado, bytes e inputs reais. `native-listening` pode faltar no novo fluxo; TCP real e WSS são os requisitos.

Verificar também Voltar, saída do menu nativo, retorno das configurações, perda de rede e segundo plano. O comportamento herdado encerra o relay em `onStop`; retornar do segundo plano exige uma nova partida. A chegada de `start200` ou WSS aberto sozinha não comprova gameplay.

Pendentes físicos: gameplay em dupla, saída online até catálogo, versão do outro telefone, latência externa, controles próprios no online e medição de aquecimento. Não marcar estabilidade geral até obter as provas correspondentes.
