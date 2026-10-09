# Station: até cinco jogadores e avisos por modo

Entrega completa de fontes e componentes Android, derivada da R81. O documento único de integração está em [HANDOFF-COMPLETO-ONLINE-ATE-5-STATION-20261009.md](../../docs/server/HANDOFF-COMPLETO-ONLINE-ATE-5-STATION-20261009.md). Leia esse estado antes de montar o APK; não reaplicar operadores históricos no servidor.

## Estado e comportamento

Os 209 Java estão completos e compilados. `compiled/rooms.dex` implementa seleção de modos, vagas P1–P5, avisos assinados de campanha/batalha, capacidade do cliente e **Ver detalhes** nas salas. Essa consulta não recebe controle, ticket ou conexão de jogo. Uma sala cheia continua visível. Participação com controles e sincronização respeita o limite do jogo/modo. Não existe transmissão de gameplay para espectadores no contrato Station atual; não transformar um P6 sem controle em participante da barreira.

O runtime novo suporta quatro convidados independentes. Cinco vagas só existem nos perfis corretos de Super Bomberman3/Batalha. Super Bomberman1 permite campanha2/batalha4; Super Bomberman2, campanha solo/batalha4; Super Bomberman3, campanha2/batalha5. Perfis genéricos preservados continuam legíveis; quando há modos documentados, a seleção mostra esses modos específicos. Descrição, capa e nome não autorizam controles extras.

`compiled/client.dex` reproduz a R81: login, licenças, catálogo, capas, downloads e autenticação existentes. Somente cinco classes de salas/perfis/sessão mudaram. A lista e seus hashes estão em `evidence/java-build.json`.

**Ainda não há APK integral assinado nem instalação Android desta sucessora.** O APK completo e a chave original ficam no PC do APK. O ELF arm64 e os DEX desta pasta foram compilados de verdade; testes host não comprovam gameplay nos celulares.

## Montar uma candidata completa no PC do APK

1. Atualizar o ramo `feat/station-five-players-client-20261009` ou a branch de integração indicada no handoff. Este diretório e a R81 precisam estar presentes na cópia local.
2. Preparar uma pasta nova de saída em E:. Usar Python3.11+, JDK17 e build-tools35 já existentes no PC. O parâmetro `--jdk` aponta para a pasta **bin**, não para a raiz do JDK.
3. Usar exatamente o APK completo R81 do backup G:, com SHA `85fac8f51daa3a370eabb14d98832f75c2f30ff81422c549538ee715627032c6`. O certificado obrigatório é `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
4. Preparar `STATION_KS_PASS` e `STATION_KEY_PASS` no ambiente privado local pelo mecanismo já usado no PC. Não escrever valores em Git, logs publicados ou conversa. Keystore original: `C:\Users\Admin\.android\debug.keystore`; alias habitual `androiddebugkey`.
5. Executar a receita abaixo com os caminhos locais reais das ferramentas. Ela monta, alinha16KiB, assina e confere todas as entradas. Não instala nem limpa dados.

```powershell
$StationVersion = "<repo local>\versions\station-five-player-support-20261009"
python "$StationVersion\recipes\package_candidate.py" `
  --base-apk "G:\BAKUP SISTEMA APP 03-10-2026\ATUAL-2P-E-TESTE-4P-20261008\test-up-to-4-players-r81\TurboStations-Premium-R81-20261008.apk" `
  --work "E:\ESTUDO APK\work\station-five-player-support-20261009\package" `
  --jdk "<JDK17>\bin" `
  --build-tools "<Android build-tools35>" `
  --keystore "C:\Users\Admin\.android\debug.keystore"
```

Saída: `TurboStations-Premium-5P-20261009.apk`, com `evidence/package.json`. Substitui três entradas: `classes35.dex`, `lib/arm64-v8a/libstation_retroarch.so`, `assets/station-online/engines.json`. Confere as outras 13.223 entradas não relacionadas à assinatura, compressão, certificado e cores. Preserva AndroidManifest, client DEX, demais motores, mídia, jogos e identidade do app. A receita não escolhe automaticamente a maior revisão, não edita R81 e não usa empacotadores históricos.

Após a montagem e conferência do recibo, atualizar os aparelhos pelo fluxo existente, preservando dados. Usar a mesma candidata em todos os participantes. Não anunciar teste de cinco quando só houve instalação ou teste sintético. Canais R76 de referência/R81 de teste permanecem como estão até a montagem da sucessora pelo PC do APK.

## Reprodução e fontes correspondentes

| Receita | Entradas explícitas | Saída/limite |
|---|---|---|
| `recipes/build_java.py` | `--work`, `--jdk`, `--android-jar`, `--d8-jar` | Compila209Java e os dois DEX; pasta privada nova. API34/D8 fixados pela evidência R81. |
| `recipes/test_profiles.py` | `--work`, `--jdk`, `--json-jar` | 166 checks do parser real, capacidades, hashes, avisos e modos. org.json20250517, SHA no script. |
| `native/tests/run_native_tests.py` | Ver `--help` | 1.176 checks host com fonte C real, mutex/threads, slots P1–P5, epochs e ownership. |
| `recipes/build_native.py` | Ver `--help`; NDKr28c e pasta nova | Compila runtime arm64/API26/16KiB com a fonte correspondente integral; compara com ELF entregue. |

Runtime registrado: `81b3daa38fb9c051e1c83646b87df7120f84f31ed8b48fe6b0b362b617b847dc`. RoomsDEX: `82609bdcbf8c36f942944486cbfb28061c5523e4c19c06618d149b154fbb0756`. ClientDEX: `e7207a89517b168cc476e30a823bed3a1b6ad57339e1042f08a4660184543d63`.

O código completo correspondente GPL do runtime está em `native/retroarch-corresponding-source.tar.gz`, junto de `COPYING` e `CORRESPONDING-SOURCE-MANIFEST.json`: RetroArch commit69a4f0ea, 11.149 arquivos fonte, adaptações completas Station e dependências. SHA do archive: `b8f7649a5edacbe9e913d5e50f66482c0aa082fbd2237f5fd7800d00723b735a`. A fonte integral tem artefatos demonstrativos públicos do projeto original; não contém configurações privadas do servidor.

Se uma recompilação gerar ELF diferente, não trocar apenas o `.so`: atualizar em conjunto manifesto/engineId/registro servidor que usa esse runtime. A montagem desta entrega usa os componentes já registrados e conferidos. O manifesto de entrega enumera os arquivos e hashes; não usar `__pycache__` como fonte.

## Teste físico para concluir

Criar sala nova Super Bomberman3/Battle Single com cinco, conferir P1–P5 e todos Pronto, escolher MAN nas cinco posições e exercitar cada controle separadamente. Repetir Tag com duas equipes; interromper/retomar somente P5; verificar saída e limpeza. Conferir campanha2 de Super Bomberman1/3, solo do2 pelo fluxo local, Battletoads2, Super Bomberman2 até4 e Secret of Mana3. Registrar APK/core/runtime/perfil, slots, imagem/áudio, exclusividade dos inputs, epochs e primeira causa de erro. Usar o mesmo recibo da entrega única.

Gameplay Android, FPS, latência WAN, estabilidade longa e capacidade de centenas ainda dependem desses testes. Bomberman4/5 futuros estão no plano de importação do handoff; capas já existentes não comprovam que as ROMs estejam no catálogo.
