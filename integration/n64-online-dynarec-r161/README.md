# R161 — candidato isolado para N64 online com Dynarec

## Objetivo e escopo

A R159 usa `r4300Emulator=1` (interpretador em cache) nas partidas N64 online, enquanto o perfil offline usa `2` (Dynarec). Esta receita prepara um candidato online com `r4300Emulator=2`. O anfitrião aceita o mesmo modo sincronizado, e a identidade do motor declara `cpu=dynarec`. É uma hipótese técnica para o desempenho ruim observado apenas no online; a partida física ainda precisa validar o resultado.

O único DEX alterado é `classes35.dex`. Nele, apenas `StationN64Bridge$Session`, `StationN64Launch` e `StationN64Server` mudam. As outras 605 classes desse DEX foram recompiladas e comparadas sem diferença. Os outros 39 DEX, inclusive `classes36.dex`, permanecem byte a byte como na R159. O `inputDelay=2`, o transporte, a lógica offline, o ciclo de vida dos serviços, as bibliotecas do núcleo, o carrossel e os arquivos de jogos não mudam. O pacote renova as três identidades de execução vinculadas ao DEX e a entrada N64 de `engines.json`; os demais perfis e opções continuam iguais.

## Origem e provas

- APK assinado de origem R159: SHA-256 `4837be706f9ac1f913b4844353741f70c539674e125ae185239611cf5faac2b3`.
- DEX35 de origem: SHA-256 `59367f469277ef94b7b31cc2e2e7d0ab3b5ab0f102b41a8c2a95a05a6eb50e05`.
- DEX35 candidato: SHA-256 `59db81435a197d9e33ce20822a6bf86f2a6746e98998cdf721dff9eeafcd97bf`.
- APK candidato não assinado: SHA-256 `f33e037b39d42a4d672b87e29535d70a2db3ba588bb60092b1d88687a298630a`.
- APK R161 assinado: `E:\\StationN64OwnerAudit-20261014\\final-r161\\TurboStations-Premium-R161-n64-online-dynarec.apk`, SHA-256 `66f429d47af725a6767064c3623ee10c505171a85fbc8c0a50dc9e5bc4f80081`.
- Kit privado R161: `E:\\StationN64OwnerAudit-20261014\\kit-r161-dynarec-only\\Kit-Servidor-TurboStations-R161-Independentes.zip`, SHA-256 `bcfbe393e6e560cd04f8994de3267fd7ff76487c3e9f234aa5bd20abd7f0eadf` (39 arquivos, recibo de leitura conferido). Ainda não aplicado no servidor.
- Cinco entradas alteradas entre 13.860; 13.855 preservadas. O comprovante completo está em `E:\StationN64OwnerAudit-20261014\package-r161-dynarec-only\unsigned-package.json`.
- A identidade N64 e o registro do APK têm o mesmo texto de opções, com `cpu=dynarec` e `inputDelay=2`.

## Procedimento de revisão

Para refazer apenas a prova do DEX a partir da R159, executar na raiz do repositório:

```powershell
py -B integration/n64-online-dynarec-r161/recipe/build_dex.py --apk 'E:\StationN64OwnerAudit-20261014\final-r159\TurboStations-Premium-R159-n64-owner-20261014.apk' --jdk 'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot' --apktool 'E:\ESTUDO APK\TurboRetroEmu-build\tools\apktool_3.0.3.jar' --out 'E:\StationN64OwnerAudit-20261014\build-r161-dynarec-only'
```

O diretório de saída deve ser novo. Para montar o APK não assinado após a prova:

```powershell
py -B integration/n64-online-dynarec-r161/packaging/build_candidate.py --base 'E:\StationN64OwnerAudit-20261014\final-r159\TurboStations-Premium-R159-n64-owner-20261014.apk' --dex-dir 'E:\StationN64OwnerAudit-20261014\build-r161-dynarec-only' --ndk 'E:\TurboEdenEngine\android-ndk-r28c' --out 'E:\StationN64OwnerAudit-20261014\package-r161-dynarec-only'
```

1. Inspecionar `recipe/patch_profile.py`, `recipe/build_dex.py` e os comprovantes `dex-receipt.json` e `unsigned-package.json`. A receita recusa qualquer APK ou classe de origem com hash diferente dos valores fixados.
2. Revisar `packaging/sign_private.py`, cujo código integra o hash do pacote e está versionado para permitir reprodução. A autoridade de assinatura, a chave e as credenciais permanecem fora do Git. Não colocar APK ou dados dos aparelhos no repositório. Assinar somente depois da revisão do pacote.
3. Gerar o kit privado com `packaging/package_private_kit.py` a partir do APK assinado, conferindo os seis ELF, 20 dependências e o registro. Não usar o kit R159 para cadastrar o novo motor.
4. No servidor, registrar juntos o novo `engineId` N64, o hash do runtime, o registro e as opções `cpu=dynarec`. Aplicar as identidades independentes vinculadas conforme o comprovante do kit; rejeitar mistura de R159/R161. Manter `inputDelay=2` nesta etapa.
5. Depois de o servidor confirmar o cadastro, instalar o mesmo APK assinado nos aparelhos de teste e repetir a partida de dois ou mais jogadores. Registrar tempo até primeira imagem, fluidez, áudio, controle e saída, comparando com a R159 offline e online.

Até a revisão, cadastro do servidor e teste físico, esta é uma **candidata**, não uma versão estável nem uma correção comprovada. A correção R160 de remoção de tarefa foi excluída deste pacote porque requer revisão própria.

## Correção do gerador do kit

A primeira tentativa de gerar o kit falhou no helper R128 `build_incoming_manifest.py`. Ele fixa o hash N64 antigo `2966309729f8a19c03b564f0178f263170e1843172f6719002f35fb54e313f9c` e usa a serialização JSON do Python. A R157 provou no DEX Android que `JSONObject.quote` transforma `SN64/1` em `SN64\/1`; o hash correto do perfil antigo é `688d519ae641911804fe3286e6b5f50cc7f8c06c42ccb1be36781f0fb067b83d`.

O gerador privado R161 agora preserva a forma do manifesto R128 e calcula o hash com a mesma representação Android. Ele exige que o perfil antigo reproduza a prova R157, que a única mudança de opções N64 seja `cpu=cached-interpreter` para `cpu=dynarec`, e que os hashes PSX, GameCube e Wii coincidam com os valores aprovados. O hash calculado para o perfil N64 R161 é `ef8bfd6e6287a205da4f73422a194c7fc05b9246363a8311501a6efa3bca2b63`. O APK assinado e o repositório do servidor não são modificados por essa correção do kit.
