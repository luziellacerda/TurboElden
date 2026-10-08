# Empacotamento candidato R77

`package_candidate.py` recompõe o APK a partir da **R76 exata**. A receita não
compila Java/nativo, não instala, não acessa ADB e não publica nem implanta servidor.
Executar somente após congelar as fontes e revisar os recibos que compõem os gates.

Base privada local:
`G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Premium-R76-20261008.apk`

SHA-256 da base:
`d7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51`.

## Alterações permitidas

Cinco substituições obrigatórias:

- `classes28.dex` e `classes35.dex`, produzidas por `build_java.py` sobre as fontes R76 e overlays R77.
- `lib/arm64-v8a/libstation_retroarch.so`, SHA `351cee4540e916468a504788911e4c5fcb4fe141e3b544b1b1255d32e1d04a26`.
- `lib/arm64-v8a/libstation_bsnes.so`, SHA `0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527`.
- `assets/station-online/engines.json`, com três plataformas preservadas, identidades novas vinculadas aos binários e `androidPeerPlayValidated=false`.

Uma substituição opcional, somente quando declarada e revisada:

- `lib/arm64-v8a/libturbo_carousel.so`. A base deve ser `3c2e22bc94f3432280e2b08c2f26ab33508cd1278ee9bd750b48d45c35105a8b`; o SHA novo vem no manifesto e no gate específico. Sem esse campo, a biblioteca é preservada integralmente.

Adições são somente JSONs novos expressamente enumerados em `catalogAssets`,
nos prefixos `assets/station-online/`, `assets/station-metadata/` ou no caminho
exato `assets/station-catalog/player-evidence-v1.json`. Não podem substituir
entradas existentes. Limites: 32 arquivos, 32 MiB por arquivo e 64 MiB agregados.
O manifesto declara arquivos exatos; os prefixos não permitem inclusão automática
de diretórios. Não incluir licenças, dados pessoais, credenciais ou conteúdo de jogos.

## Manifesto de entrada

Preparar JSON com os seguintes campos. Os caminhos de payload devem ser absolutos
e seus hashes devem ser os recibos finais revisados. O campo `carousel` é opcional;
os demais são obrigatórios. Os valores abaixo descrevem o formato e não constituem
um manifesto pronto para execução.

```json
{
  "schemaVersion": 1,
  "baseApkSHA256": "d7145db3511a4056b16fdde10e4c07709a16b7f445596801b3535c1b28b06a51",
  "javaBuildDirectory": "E:\\ESTUDO APK\\work\\station-multiplayer-r77-20261008\\java-build-final",
  "javaBuildReceiptSHA256": "SHA256 do evidence/build.json final",
  "runtime": {"path": "caminho absoluto do runtime", "sha256": "351cee4540e916468a504788911e4c5fcb4fe141e3b544b1b1255d32e1d04a26"},
  "snesCore": {"path": "caminho absoluto do core", "sha256": "0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527"},
  "engines": {"path": "caminho absoluto do engines.json", "sha256": "SHA256 revisado"},
  "carousel": {"path": "caminho absoluto do carrossel opcional", "sha256": "SHA256 revisado"},
  "catalogAssets": [
    {"entry": "assets/station-catalog/player-evidence-v1.json", "path": "caminho absoluto do JSON", "sha256": "SHA256 revisado"}
  ]
}
```

## Gates finais

O arquivo indicado por `--gates` precisa declarar `reviewed=true`, `version=R77`,
o SHA do manifesto de entrada, do recibo Java, do runtime e do core. Se houver
carrossel novo, declarar também `carouselSHA256`. Cada recibo precisa de `kind`,
`path` absoluto e `sha256`.

Kinds obrigatórios: `java-contract`, `java-concurrency`, `native-runtime`,
`native-snes`, `server-candidate`, `catalog`; acrescentar `carousel` quando usado.
Podem existir recibos adicionais, como integração Java→C# em TLS. O revisor deve
conferir o sucesso e o vínculo com as fontes finais de cada recibo antes de marcar
`reviewed`; a receita confirma sua integridade e não transforma teste isolado em
homologação de jogos ou de produção.

```json
{
  "reviewed": true,
  "version": "R77",
  "inputManifestSHA256": "SHA256 do manifesto de entrada",
  "javaBuildReceiptSHA256": "SHA256 do evidence/build.json",
  "runtimeSHA256": "351cee4540e916468a504788911e4c5fcb4fe141e3b544b1b1255d32e1d04a26",
  "snesCoreSHA256": "0a3ac7b4fa5da318b1c993d8867aa944eaa2d012680b49e9929bf7a4a398f527",
  "carouselSHA256": "SHA256 opcional do carrossel novo",
  "receipts": [
    {"kind": "java-contract", "path": "caminho absoluto do recibo", "sha256": "SHA256 revisado"}
  ]
}
```

O exemplo abreviado não satisfaz todos os kinds e será recusado. Gates ausentes,
hashes antigos, fontes alteradas após compilação, ZIP com entradas inesperadas ou
qualquer diferença fora da lista permitida interrompem o empacotamento.

## Assinatura e execução

A sessão de assinatura autorizada deve fornecer `STATION_KEYSTORE`,
`STATION_KEY_ALIAS`, `STATION_KS_PASS` e `STATION_KEY_PASS` no ambiente. Não gravar
valores em receitas, manifestos, comentários, histórico de shell ou logs publicados.
A única chave permitida é `C:\Users\Admin\.android\debug.keystore`. Antes de assinar,
a receita exporta apenas seu certificado público e exige SHA-256
`7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`, também presente na base
e no APK final. Nenhum material da chave privada é exportado.

Exemplo de invocação depois de preencher e revisar os dois JSONs:

```powershell
C:\Python314\python.exe -X utf8 -B .\package_candidate.py --inputs 'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\PACKAGE-INPUTS.json' --gates 'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\package-gates.json'
```

Executar a partir desta pasta de receitas, ou usar caminho absoluto para o script.
O workspace padrão é um filho novo `E:\ESTUDO APK\work\station-multiplayer-r77-20261008\package-01`.
Se já existir, escolher outro filho novo via `--workspace`; a receita não apaga
tentativas anteriores. O APK final fica em G: e também não pode existir previamente.
Todos os temporários e logs das ferramentas ficam no workspace E:.

## Verificações e resultado

- Confere SHA integral da R76, certificado e inventário de 13.225 entradas de conteúdo.
- Concilia a lista completa de fontes Java R76 + overlays R77 e os dois DEX produzidos.
- Confere ELF ARM64, segmentos com alinhamento de 16 KiB e alinhamento ZIP antes/depois da assinatura.
- Compara SHA e compressão de **todas** as entradas. Preserva 13.220 entradas com cinco substituições, ou 13.219 com o carrossel opcional; as adições são contadas separadamente.
- Preserva todos os 59 vídeos, incluindo os 58 vídeos do carrossel, e todo conteúdo não declarado.
- Reconfere fontes, artefatos, gates e recibos antes de copiar o APK final; compara SHA integral da cópia em G:.
- Grava `evidence/package.json` em E:, com payloads/hashes, entradas alteradas/adicionadas e `installed=false`, `deployed=false`, `androidPeerPlayValidated=false`.

Somente os arquivos `unsigned-r77.apk` e `signed-r77.apk` criados pela própria
tentativa são removidos após a cópia verificada. Publicar apenas fontes e recibos
sanitizados; APK, logs privados, chave, ROMs, BIOS e dados pessoais ficam fora do Git.

O pacote não habilita quatro jogadores em produção. Registro de engines/perfis,
qualificação do jogo exato e ativação coordenada no servidor continuam separados.
Um catálogo sem vínculos confirmados permanece indisponível para multiplayer;
quantidade descritiva de jogadores não autoriza uma sala.
