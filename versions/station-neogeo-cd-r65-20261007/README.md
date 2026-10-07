# R65 — análise de Neo Geo cartucho/CD e integração do lançador de CD

Data: 07/10/2026. Escopo: TurboStations Android, pacote `org.turboramastation.frontend`.

**Candidato compilado, assinado e reproduzido. Não instalado nem declarado estável.** A última instalação conferida nos dois aparelhos é R63. A USB desconectou durante a investigação de KOF '98. Não houve desinstalação, limpeza de dados, alteração de configuração no telefone ou implantação Linux.

## Resultado comprovado

| Área | Constatação | Situação |
|---|---|---|
| Neo Geo CD | O código de preparação CD existia no Git, mas não estava no `classes30.dex` da R63/R64. O lançador antigo abria o CHD sem selecionar `neocdz` e sem montar `-cdrom`. | Corrigido no APK R65; execução Android ainda pendente. |
| Cartucho, coleção KOF | Seis nomes de conjuntos da coleção não constam no registro completo oficial MAME 0.289. | Precisa conferir os membros/CRC dos arquivos antes de escolher conjunto ou motor compatível. Nenhum arquivo renomeado por suposição. |
| KOF '98 padrão | `kof98.zip` consta no MAME. O telefone enviou o arquivo e `-rompath` corretos ao motor; uma captura curta mostrou imagem verde/branca corrompida. | Causa ainda não comprovada. Falta comparar ROM/BIOS e acompanhar a saída após a inicialização. |
| Motores | As duas bibliotecas MAME do APK são idênticas às do pacote oficial comparado. | Não foi detectada mistura/corrupção binária nessas bibliotecas; isso não prova que todo jogo funciona. |
| Catálogo | 189 cartuchos e 50 CDs no TSV publicado da revisão 14; 13 nomes de cartucho sem registro; dois jogos são de outro hardware. | Auditoria do documento publicado, não consulta HTTP atual nem teste físico dos 239 jogos. |

## Base, artefatos e fontes

- Fonte de partida: R64, commit `8812bacf8154f25fd7739f95a2db0729f36e4c72`, com recibo documental posterior `3d8ab18`.
- APK base: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R64-20261007.apk`.
- SHA-256 base: `e2bb778319e03d878ac5de3749f06af1b5e7bbffd06b8232402d2d2f610ba868`.
- Trabalho/compilação: `E:\ESTUDO APK\work\station-neogeo-cd-r65-20261007`.
- APK final: `G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R65-20261007.apk`.
- SHA-256 final: `1858459b62a38a85cdd9fbeaafc68d3560008f154f99dd1431752aa0594eb081` — 2.093.415.593 bytes.
- Certificado preservado: `7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.
- Única entrada funcional alterada sobre R64: `classes30.dex`, SHA `9dc641418b05663f0b548dbb01b3e2dab398fd73122a2b734b8509c19f68b080`.
- 13.218 outras entradas comparadas integralmente e preservadas; alinhamento de bibliotecas de 16 KiB e assinatura conferidos.
- `classes35.dex` continua R64: `b11459d8bf42e12d26ed5103b9ed62d1e0df674cfc31c79bffe49b48756f2a97`.

Esta revisão inclui os controles/diagnósticos R64, mas **não implementa recuperação da partida online**. Runtime, IDs de motores, protocolo, política de timeout, carrossel, faixa INSTALADO e bibliotecas dos emuladores permanecem iguais à R64.

## Caminho completo de abertura

1. Catálogo Station fornece plataforma, item e descritor. Coleções são organização do catálogo: o nome da coleção não escolhe outro motor.
2. `StationPlatforms` mapeia Neo Geo para `neo-geo` e Neo Geo CD para `neo-geo-cd`.
3. `StationInstaller.install` instala uma geração isolada em `roms/.station-v2/<plataforma>/<itemId>/install-*/content`, valida tamanho/formato/caminhos/contagem e publica o recibo privado. O `artifact.launchPath` determina o arquivo inicial. A política existente não calcula o hash completo dos jogos; não confundir isso com verificação dos chips pelo MAME.
4. `native_mame.h`: `mameCore` → `mameRunHook` → `openMame` → JNI `MameBootstrap.launch`. A ação também pausa o vídeo do sistema e a música. Não executar outra emulação paralela para diagnosticar.
5. `MameBootstrap` abre `MameEntryActivity` no processo MAME, prepara diretórios e usa o modo de arquivos do doador. `cliParamsFor` aponta para o **pai real do arquivo instalado**, inclusive dentro de coleções. Não depende de ROM/BIOS na raiz global.
6. Cartucho: `ACTION_VIEW` do ZIP original + `-rompath '<content real>'` → `com.seleuco.mame4droid.MAME4droid`. O ZIP interno do conjunto fica comprimido para o motor. O contêiner de transferência e o ZIP interno do conjunto são camadas diferentes.
7. CD na R65: valida CHD e dependências em thread de trabalho, seleciona `neocdz.zip` e passa `-cdrom '<disco.chd>' -bios <identificador reconhecido>` junto ao `-rompath`.
8. Configurações: a mesma entrada abre `com.seleuco.mame4droid.prefs.UserPreferences`; controles e opções continuam sendo os do MAME integrado. `returnToPlatforms` mantém a rota existente para `ESActivity` e encerra apenas o processo do emulador após a ação humana.

Arquivos de referência preservados na base:

- `versions/station-current-r55-20261006/native-dependencies/r16/native_mame.h`
- `versions/station-current-r55-20261006/client/src/java/org/emulationstation/frontend/station/StationPlatforms.java`
- `versions/station-current-r55-20261006/client/src/java/org/emulationstation/frontend/station/StationInstaller.java`

FBNeo continua separado. Geolith do online usa outro formato/contrato; sua disponibilidade no pacote não autoriza oferecer automaticamente esses ZIPs em netplay. Não trocar motor, controles ou elegibilidade do online para esconder uma falha local.

## CD: regras reais da implementação

`NeoCdSupport.java` já havia sido preparado em `versions/station-neogeocd-20261005`, mas não integrado no APK. Seu conteúdo é preservado na R65; `MameBootstrap.java` permanece idêntico ao lançador anterior. `MameEntryActivity.java` incorpora o helper e coloca validação/importação fora da thread da interface, com descarte de callbacks de uma Activity destruída.

- Identifica CD somente pelos ancestrais canônicos `neo-geo-cd` ou `neogeocd`, e não por uma palavra no título/coleção.
- Nesta entrega aceita CHD v5 autônomo. Os 50 caminhos CD no documento examinado terminam em `.chd`. A checagem do cabeçalho **não substitui** verificação completa de setores pelo motor/chdman.
- Não implementa CUE/BIN/ISO, discos dependentes de outro CHD ou escolha de multidisco nesta correção.
- BIOS própria do CD: `neocd.bin`, `uni-bioscd33.rom` ou `uni-bioscd32.rom`, mais o auxiliar `000-lo.lo`. Reconhecimento por tamanho, CRC e SHA-1 da tabela oficial, independentemente do nome recebido.
- Importação autorizada pelo usuário, por seletor Android, em `files/mame/station-bios/neogeocd`. BIOS ZIP/BIN/ROM com limites de entrada e expansão. Nenhuma BIOS é obtida na web, adicionada ao APK ou publicada no Git.
- BIOS presente em `content/neocdz.zip` também é reconhecida. O auxiliar de zoom pode ser reaproveitado de `neogeo.zip` já instalado e validado, com busca limitada, sem seguir links.
- Cria `neocdz.zip` atomicamente ao lado do disco, somente quando as dependências reconhecidas faltam. O disco, a BIOS doadora e saves não são reescritos.
- O arquivo auxiliar criado não pertence ao recibo original do download; a política de remoção atual preserva arquivos desconhecidos. Consequentemente pode restar essa pequena dependência após apagar um CD. Não remover diretórios recursivamente para contornar isso.
- Sem BIOS válida: apresenta erro e opção de importar. Falhas de disco/caminho também continuam explícitas; não fabricar sucesso ou voltar silenciosamente ao catálogo.
- A BIOS CD não é a mesma da máquina de cartucho. Importar `neogeo.zip` pode fornecer o auxiliar, mas não substitui o firmware CD.

## Auditoria de todos os nomes de cartucho publicados

Fonte: Servidor-pix, commit `8d9c670ba813fb970a61ff9bf329e6286b51ad07`, `docs/station-android/biblioteca-neogeocd-20261005/catalogo-completo.tsv` (revisão histórica 14). SHA do TSV: `3dae0cfa3877fba31b9a347b58795fe0df95333aea628b9ea8be597b7ccfed6e`.

Comparação com **todo** o `mame.lst` da tag `mame0289`, não apenas os `ROM_START` de `neogeo.cpp`: 176 de 189 nomes registrados. A lista completa está em `evidence/driver-catalog-audit.json`. Registro de nome não equivale a ROM/BIOS íntegra, conjunto completo ou gameplay aprovado.

| Nome inicial sem registro | Local no documento |
|---|---|
| `kof96ae20.zip` | Coleção The King of Fighters |
| `kof97xt.zip` | Coleção The King of Fighters |
| `kof98ae.zip` | Coleção The King of Fighters |
| `kf2k4pls.zip` | Coleção The King of Fighters |
| `kf2k2plb.zip` | Coleção The King of Fighters |
| `kf2k2plc.zip` | Coleção The King of Fighters |
| `kogplus.zip` | Raiz Neo Geo |
| `ltorb1.zip` | Raiz Neo Geo |
| `neonopon.zip` | Raiz Neo Geo |
| `neopong.zip` | Raiz Neo Geo |
| `zintrkcd.zip` | Raiz Neo Geo |
| `mosyougi.zip` | Raiz Neo Geo |
| `tws96.zip` | Raiz Neo Geo |

A coleção KOF tem 26 itens; 20 nomes registrados e seis não registrados. `kof98.zip` é reconhecido; `kof98ae.zip` é outro conjunto. Não renomear variantes/hacks como se fossem o conjunto padrão. Antes de mapear qualquer alias, comparar tamanho/CRC/SHA dos membros, dependências de conjunto pai e BIOS com o driver exato.

Outros hardwares classificados sob Neo Geo:

- `pspikes.zip`: `vsystem/pspikes.cpp`.
- `spy.zip`: `konami/spy.cpp`.

O motor MAME inclui esses nomes, mas eles não são da plataforma Neo Geo. Reclassificação deve preservar IDs, capas, instalações e saves mediante análise do servidor; nada foi migrado automaticamente.

## Evidência física e lacunas

O telefone R63 abriu Alpha Mission II e depois KOF '98. O registro de KOF confirmou o nome `kof98.zip`, o caminho privado da geração selecionada e `-rompath` correspondente. A captura aproximadamente cinco segundos após a abertura mostrou imagem verde/branca corrompida e os controles próprios do MAME. Não apareceu erro fatal ou ROM ausente nessa janela curta.

Não foi possível comprovar se a imagem persistia após a inicialização nem ler os membros das ROMs/BIOS antes da desconexão USB. Não atribuir a causa a coleção, Vulkan/ANGLE, BIOS, licença ou arquivo corrompido sem essa correlação. A ausência de override de driver na leitura não prova que toda configuração gráfica esteja correta.

Próxima conferência no aparelho, preservando os dados:

1. Registrar versão instalada e arquivo selecionado na coleção, sem instalar sobre partida ativa.
2. Ler apenas nomes, tamanhos e CRC dos membros do ZIP e da BIOS, comparar com MAME 0.289 e verificar pais/dependências; conservar jogos/saves/NVRAM/configurações.
3. Observar a imagem após a inicialização e capturar o erro completo do motor, se existir. Só então corrigir causa gráfica ou pacote, sem reset geral de configurações.
4. Após saída humana da emulação, instalar R65 com mesma assinatura e dados; conferir hash instalado.
5. Testar CD com firmware válido: abrir, controles, som, retorno e nova abertura. Testar cartucho padrão e pelo menos uma coleção, sem executar dois motores ao mesmo tempo.

## Testes e reprodução

- 37 verificações locais do helper/CLI: identificação de plataforma/coleções, cabeçalho, dependência de CHD, BIOS ausente/inválida, limites, preparação atômica/idempotente e preservação de disco/doador.
- Testes usam bytes sintéticos e substituem identidades apenas na JVM de teste por reflexão. Eles não provam que BIOS comercial ou jogo real funcionou. Os valores oficiais do código Android não foram modificados.
- Recompilação independente do snapshot produziu DEX **idêntico** ao empacotado.
- APK completo foi comparado à R64, assinado e alinhado; nenhum teste físico R65 ou gameplay em dupla alegado.

No Windows, com Python e JDK 17 disponíveis:

```powershell
python recipes/build_bridge.py --work 'E:\ESTUDO APK\work\r65-rebuild-novo'
python recipes/test_bridge.py --work 'E:\ESTUDO APK\work\r65-tests-novo'
python recipes/audit_catalog.py --catalog-tsv '<TSV publicado>' --registry '<mame.lst oficial registrado>' --output 'E:\ESTUDO APK\work\auditoria-nova.json'
```

Executar a partir desta pasta; as receitas localizam os fontes pelo próprio caminho. Usar pastas novas. O `build_bridge.py` confere os três hashes de fonte e o hash esperado do DEX. `reproduction.json` e `reproduction-tests.json` registram a repetição real feita no PC.

Para empacotar, copiar `recipes/package_r65.py` para a raiz da pasta E: gerada por `build_bridge.py`. Fornecer por ambiente `STATION_KEYSTORE`, `STATION_KEY_ALIAS`, `STATION_KS_PASS`, `STATION_KEY_PASS`, mantendo a assinatura original. A receita confere a base R64, exige espaço, recusa sobrescrever o candidato existente e preserva/verifica todas as entradas. Adaptar somente o destino de saída se for gerar uma segunda cópia; nunca trocar o certificado ou publicar essas variáveis. O APK base é dependência externa identificada pelo hash; esta pasta não contém ROMs, BIOS, APKs ou chaves.

Fontes oficiais e hashes constam em `evidence/official-sources.json`:

- [MAME 0.289: Neo Geo](https://github.com/mamedev/mame/blob/mame0289/src/mame/snk/neogeo.cpp)
- [MAME 0.289: Neo Geo CD](https://github.com/mamedev/mame/blob/mame0289/src/mame/snk/neogeocd.cpp)
- [Registro integral de máquinas MAME 0.289](https://github.com/mamedev/mame/blob/mame0289/src/mame/mame.lst)
- [Documentação oficial sobre conjuntos de ROMs](https://docs.mamedev.org/usingmame/aboutromsets.html)
