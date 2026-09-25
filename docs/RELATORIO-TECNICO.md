# Análise técnica — TurboramaStation-24-09.apk

Versão pública sanitizada. Consulte o [handoff](HANDOFF.md) e o [escopo de publicação](PUBLICACAO.md). As descrições de BIOS, chaves e bibliotecas abaixo documentam o APK original; esses arquivos não estão neste repositório.

Data da análise: 25/09/2026
Método: análise estática, sem instalar/executar o APK e sem usar uma licença de usuário.
SHA-256 do APK: `9DC39817F23975F15E9FB75BBE98E7A7519567E06805F5746C1F475CBCF57396`

## Resumo executivo

O APK é um frontend de emulação Android derivado do EmulationStation, com runtime SDL2 e Libretro. O nome técnico do pacote é `org.emulationstation.frontend`; no código aparecem os nomes `WayOs` (cliente HTTP/licença) e `SamEstation 2.12.0rp-dev` (identificação enviada pela telemetria). Não foi identificada uma biblioteca de ROMs jogáveis ou uma cópia do catálogo comercial. A relação efetiva de jogos disponíveis é entregue por um catálogo remoto após a validação de uma chave de licença. Há, porém, uma base auxiliar MAME com 38.353 pares de identificadores e nomes, que não comprova a disponibilidade desses jogos na loja.

O fluxo central é:

1. `ESActivity` carrega `libSDL2.so` e `libmain.so`.
2. O aplicativo usa `/storage/emulated/0/EmulationStation` como diretório principal.
3. Recursos, BIOS e pacotes internos são copiados para `.emulationstation`.
4. Uma licença é validada no KeyAuth; a resposta fornece uma sessão.
5. O catálogo é buscado em `StoreUrl/drawers.json/{chave}/android` e mantido em `catalog-cache.json`.
6. A loja baixa ROMs, capas, cores e pacotes de firmware. Arquivos grandes usam até 24 conexões HTTP Range.
7. O jogo é iniciado por um core Libretro dentro do processo ou por um Intent para outro aplicativo Android.
8. Metadados podem ser enriquecidos por TheGamesDB ou ScreenScraper.

## Identificação do aplicativo

| Item | Valor |
|---|---|
| Arquivo | `TurboramaStation-24-09.apk` |
| Tamanho | 166.871.026 bytes |
| Pacote | `org.emulationstation.frontend` |
| Activity principal | `org.emulationstation.frontend.ESActivity` |
| Version name / code | `1.0` / `1` |
| Android mínimo | API 26 |
| Android alvo | API 34 |
| Compilado com | API 35 |
| ABI | somente `arm64-v8a` |
| Nome interno HTTP/licença | `WayOs` |
| Nome/build nativo | `SamEstation 2.12.0rp-dev`, build `Sep 23 2026 - 19:14:42` |
| Depuração | `android:debuggable="true"` |
| Assinatura | APK Signature Scheme v2; certificado `CN=Android Debug, O=Android, C=US` |
| SHA-256 do certificado | `C54A0690C9C0803EFEAF9C77950A81460F8BE746D5C8FE8A88F2FBE552775F18` |

O fato de o aplicativo de distribuição estar depurável e assinado com certificado de debug é um forte indício de build de desenvolvimento/privado, não de release endurecida.

## Componentes Android

| Tipo | Componente | Exportado | Função |
|---|---|---:|---|
| Activity | `ESActivity` | sim | Tela/loop SDL principal |
| Activity | `RestartActivity` | não | Mata o processo antigo e reinicia o frontend |
| Service | `DownloadService` | não | Download em foreground, notificações, WakeLock e WifiLock |
| Provider | `FileProvider` | não | Compartilha ROMs por `content://` ao abrir em emuladores externos |
| Provider | AndroidX Startup | não | Inicialização de Profile Installer |
| Receiver | AndroidX ProfileInstallReceiver | sim, protegido por `android.permission.DUMP` | Perfil de desempenho |

Permissões relevantes: acesso amplo a armazenamento (`MANAGE_EXTERNAL_STORAGE`), Internet, notificações, serviço foreground de sincronização, WakeLock, Wi-Fi state e vibração. `allowBackup=false`.

## Estrutura interna

O APK contém cinco DEX, 164 arquivos em `assets`, 172 recursos Android desmontados, aproximadamente 6.198 arquivos Smali e oito bibliotecas nativas ARM64.

Bibliotecas nativas principais:

| Biblioteca | Papel |
|---|---|
| `libmain.so` | Frontend EmulationStation, loja, licença, catálogo, telemetria e player Libretro |
| `libSDL2.so` | Janela, áudio, controles e integração Android |
| `libarmsx2_libretro_android.so` | PlayStation 2 |
| `libdolphin_libretro_android.so` | GameCube/Wii |
| `libmupen64plus_next_gles3_libretro_android.so` | Nintendo 64 |
| `libsuyu_libretro_android.so` | Nintendo Switch |
| `libyabasanshiro_libretro_android.so` | Sega Saturn |
| `libc++_shared.so` | Runtime C++ |

Os assets incluem BIOS de várias plataformas, pacote de sistema Dolphin, recursos visuais/sonoros e chaves `prod.keys`/`title.keys` para Suyu. Os valores dessas chaves, credenciais e identificadores de serviço não são reproduzidos neste relatório.

## Mapa de armazenamento

```text
/storage/emulated/0/EmulationStation/
├── roms/                                  ROMs baixadas/instaladas
├── .emulationstation/
│   ├── bios/                              BIOS, firmware e pacotes de sistema
│   │   ├── dolphin-emu/
│   │   ├── PPSSPP/
│   │   ├── pcsx2/bios/
│   │   ├── neocd/
│   │   └── suyu/keys/
│   ├── downloaded_images/                 capas
│   ├── gamelists/                         gamelist.xml por sistema
│   ├── resources/                         UI, fontes, sons e XML auxiliares
│   ├── store/catalog-cache.json           catálogo remoto em cache
│   ├── core-options/                      opções dos emuladores
│   ├── es_input.cfg                       controles
│   ├── es_settings.cfg                    preferências
│   ├── themes/                            temas
│   ├── tmp/extracted/                     ROMs extraídas de ZIP/7z
│   └── license.json                       licença/cache de validação em texto
└── [armazenamento interno do app]/cores/  cores `.so` baixados
```

## Licença e catálogo

O identificador do aparelho é `SHA-256("WayOs:" + ANDROID_ID)`. A licença é enviada por POST ao KeyAuth junto com esse HWID. O protocolo observado usa as operações de inicialização e licença do KeyAuth e mantém `sessionid`, `key` e um instante `validated` no estado local.

O catálogo usa como base padrão `https://samboxmanager.squareweb.app`. Após a licença ser aceita, o frontend monta:

```text
https://samboxmanager.squareweb.app/drawers.json/{CHAVE_DE_LICENCA}/android
```

O caminho com a chave é deliberadamente mascarado nos logs Java. O cache local fica em `.emulationstation/store/catalog-cache.json`. A estrutura reconhecida pelo parser contém, entre outros, `Files`, `Id/id`, `Name/name`, `DisplayName/displayName`, `Url/url`, `CoverImage/coverImage`, `DefaultSubPath/defaultSubPath`, `SubDirectory/subDirectory` e `downloads`.

Sem uma chave válida ou um `catalog-cache.json` já criado pelo aplicativo, não é possível enumerar estaticamente os jogos disponíveis no catálogo remoto. Isso não significa ausência de nomes de jogos no APK: `assets/resources/mamenames.xml` contém 38.353 pares `mamename`/`realname`, usados como base auxiliar de nomes MAME. Essa base não é a lista comercial nem garante que existam ROMs correspondentes para download. O script [Parse-Catalog.ps1](../scripts/Parse-Catalog.ps1) incluído no handoff exporta os itens presentes em um cache de aparelho autorizado, sem consultar ou contornar o servidor; não foi validado contra um catálogo real deste serviço.

## Downloads e instalação

`HttpBridge` usa `HttpURLConnection` com timeout de conexão de 15 s e leitura de 30 s. Segue no máximo cinco redirecionamentos manualmente. Para arquivos com 8 MiB ou mais e suporte a `Accept-Ranges: bytes`, divide o download em 24 segmentos, com 12 tentativas por segmento e backoff de até 15 s. O serviço de foreground mantém CPU e Wi-Fi ativos, mostra progresso e continua mesmo com a Activity fechada.

ZIP e 7z são extraídos com validação de caminho canônico para bloquear Zip Slip. O download usa arquivo `.part` e renomeia no final. Não foi encontrada validação criptográfica de ROMs, cores ou pacotes baixados (hash ou assinatura); HTTPS é a proteção de transporte observada.

## Execução de jogos

Existem dois caminhos:

- `libretro:`: resolve e carrega um core `.so`, configura vídeo/áudio/controles, chama `retro_load_game` e mantém menu de pausa/save state dentro do frontend.
- `android:`: constrói um Intent explícito por pacote/classe, aceita extras `int`, `bool` e `string`, e pode compartilhar a ROM por FileProvider.

O frontend escolhe o comando associado à plataforma, verifica o core e baixa um core ausente do buildbot Libretro. Os cores grandes de PS2, GameCube/Wii, N64, Switch e Saturn já vêm dentro do APK.

## Sistemas e formatos

A relação consolidada está em [sistemas-suportados.csv](../data/sistemas-suportados.csv). Foram observadas referências para Arcade/CPS/Neo Geo, Atari 2600/7800/Jaguar/Lynx, ColecoVision, Dreamcast/Naomi/Atomiswave, Game Boy/GBC/GBA, Game Gear, Game & Watch, GameCube, Master System, Mega Drive, MSX, Neo Geo CD/Pocket, NES/FDS, Nintendo 64/DS/3DS/Switch, Odyssey 2, PC Engine/CD/SuperGrafx, PlayStation 1/2/PSP, Sega 32X/CD/Saturn/SG-1000, SNES, Virtual Boy, Wii e WonderSwan. Referências a sistemas, cores ou nomes MAME não equivalem a testes de compatibilidade ou à disponibilidade de jogos no catálogo remoto.

## Servidores ligados

A relação detalhada, com função, método e condição de uso, está em [servidores.csv](../data/servidores.csv).

| Destino | Uso direto pelo frontend |
|---|---|
| `samboxmanager.squareweb.app` | Catálogo e endpoint de telemetria; as URLs de ROMs/capas retornadas pelo catálogo podem apontar para outros hosts |
| `keyauth.win` | Inicialização e validação de licença |
| `api.ipify.org` | Descoberta do IP público para telemetria |
| `buildbot.libretro.com` | Download de cores ARM64 e pacotes Dolphin/PPSSPP |
| `api.thegamesdb.net` | Scraping de metadados |
| `www.screenscraper.fr` | Scraping de metadados |

Em 25/09/2026, a raiz do servidor Square Cloud e o índice de cores Libretro responderam HTTP 200; os dois pacotes de firmware responderam HTTP 200. KeyAuth e ScreenScraper responderam HTTP 403 a uma requisição HEAD sem credenciais; esse resultado isolado não confirma a causa da recusa nem o funcionamento das operações autenticadas. Nenhuma chave de usuário foi enviada durante esta verificação.

As bibliotecas Dolphin, ARMSX2 e Suyu também contêm suporte de rede próprio (lobby/STUN, RetroAchievements, Nintendo/Epic/2K etc.). Isso representa capacidade potencial dos emuladores e dos jogos, mas não significa que o frontend contate todos esses destinos automaticamente.

## Telemetria e privacidade

O endpoint padrão é:

```text
https://samboxmanager.squareweb.app/telemetry/android
```

O formulário observado pode conter: chave de licença, `device_id`, identificação/build do app, modelo (`ro.product.model`), fabricante/dispositivo, contador de crashes, megabytes baixados, evento, timestamp e dados do evento. Os eventos incluem `app_start`, `app_exit`, `game_start`, `game_end`, `game_error` e crash/saída não limpa. O aplicativo também calcula jogos mais executados e métricas de FPS/duração.

`Telemetry` aparece desativada por padrão, enquanto `CrashReports` aparece ativada por padrão. Portanto, telemetria de uso e relatório de falhas têm controles separados. A busca de IP usa `api.ipify.org` quando o subsistema correspondente é acionado.

## Achados de segurança

### Alta prioridade

1. **Build de debug distribuída** — `android:debuggable=true` e assinatura `Android Debug`. Facilita depuração/inspeção e não oferece identidade de release confiável.
2. **Sem integridade criptográfica dos downloads** — não foi encontrado hash/assinatura para ROMs, cores e pacotes. Um catálogo comprometido ou falha na cadeia HTTPS pode resultar em conteúdo ou código nativo adulterado.
3. **Licença e cache no armazenamento compartilhado** — `license.json` fica sob o diretório externo do aplicativo; aparelhos com acesso amplo ao armazenamento podem lê-lo/alterá-lo.
4. **Chaves de firmware incluídas** — `prod.keys` e `title.keys` estão empacotadas em `assets`. Isso é exposição de segredo e pode ter implicações legais/licenciamento.
5. **Telemetria associa licença e aparelho** — o formulário de telemetria inclui a chave e um identificador persistente derivado do `ANDROID_ID`; crash reports estão ativos por padrão.

### Média prioridade

1. **Permissão de todos os arquivos** — amplia significativamente a superfície de acesso e o impacto de uma vulnerabilidade.
2. **Downloader muito agressivo** — 24 conexões por arquivo grande podem causar bloqueio, carga elevada ou conflitos com limites do servidor.
3. **URLs aceitas do catálogo** — o downloader suporta `http://` e `https://`; as URLs padrão são HTTPS, mas não há restrição rígida de esquema nem pinagem de certificado.
4. **Versão/pacote genéricos** — versionCode `1`, versionName `1.0` e pacote do projeto upstream dificultam inventário, atualização e rastreabilidade.

### Controles positivos observados

- `allowBackup=false`.
- Activities/Service/FileProvider sensíveis não são exportados.
- Proteção contra Zip Slip em ZIP e 7z.
- Arquivos são baixados para `.part` antes da substituição.
- A chave inserida no caminho do catálogo é mascarada nos logs.
- Identificador de hardware é hash, não o `ANDROID_ID` bruto.

## Limitações

Esta foi uma análise estática. Não foram executados jogos, não foi usada uma licença e não foram feitas requisições ao caminho privado do catálogo. Foram extraídos 6.198 arquivos Smali dos cinco DEX e gerados 3.353 arquivos Java pelo JADX. Há 32 arquivos Java de bibliotecas de terceiros com marcações de erro ou método não decompilado; nenhum pertence ao pacote `org.emulationstation.frontend`. Ausência dessas marcações não garante equivalência perfeita com o código original. O núcleo funcional principal é C++ compilado em `libmain.so`; o material privado inclui símbolos dinâmicos, strings e disassembly ARM64, não o código-fonte C++ original. O catálogo efetivo e seus nomes de jogos só podem ser fechados com um cache gerado por uma conta/licença autorizada; a base auxiliar MAME tem finalidade distinta. A versão pública sanitizada omite BIOS, chaves, bibliotecas nativas e dumps nativos com possíveis credenciais, portanto não permite reconstruir integralmente o APK.
