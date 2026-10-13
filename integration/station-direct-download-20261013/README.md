# Downloads diretos protegidos — candidata sobre R139

**Servidor direto ativo; APK assinado com a chave original e quatro identidades
registradas no servidor. Instalação e medição física de velocidade pendentes.**
O celular não foi detectado pelo USB nesta etapa; o kit de instalação está preparado.

`StationHttp` usa `downloads-station.lzgames.com.br` somente no GET canônico de
artefato. As demais rotas continuam em `app.lzgames.com.br`, com o pin antigo.
A origem nova conserva a validação da CA pública, hostname e pin SPKI próprio.
Bearer, assinatura da requisição e correlação são preservados; redirects continuam
proibidos. Não há IP externo fixo no fonte, fallback do mesmo grant, aumento de
permissões ou mudança na autorização da API. O servidor atualiza seu registro DNS
automaticamente quando o IPv4 público muda e renova o certificado conservando a chave.

O donor assinado é a R139 exata:
`19acdeceef86bc66c2475300cbd142da783850c02f5a9e2068d8652ef8523164`.
Certificado Android original exigido:
`7b16ee1aca7db7a50e7cc6c8612cf2a3568f474894a468865d842bf720c89825`.

O transporte deriva da fonte histórica R124 preservada
(`StationHttp.java` SHA256 `9f897c3d30465f9bc77b4d71d02a051746788b7a9aade4b8e0a25ba3ef8a4460`).
Só as famílias HTTP e a nova identidade de download entram no overlay D8. A classe
`StationHttp$ResponseBody` é copiada do donor para conservar o controle original
de EOF/tamanho e a reutilização da conexão. `ScopedHttpDex.java` compara o smali
canônico, com debug e valores estáticos, de todas as 266 classes preservadas.
Partição final: 272 classes, contra 271 no donor.

O fingerprint dos wrappers existentes vincula DEX28. Por isso `build_wrappers.py`
renova seus marcadores e quatro IDs PSX/N64/GameCube/Wii, mantendo todas as políticas
e as sete fontes PSX originais por SHA. Exige o mesmo NDK r28c e compara exports,
dependências, SONAME e alinhamento 16 KiB. N64/Dolphin são marcadores de identidade;
nenhum core de emulador é recompilado. Os nove descritores RetroArch da R139 ficam
exatos. Esses quatro IDs novos ainda não foram registrados no servidor.

`package_direct.py` reutiliza o assembler clássico existente com cinco substituições
estritas: DEX28, três wrappers e `engines.json`. Verifica o mapa de 345 payloads
vinculados, freeze das fontes, políticas e hashes antes/depois da montagem e faz
leitura independente de todas as entradas. Preserva 13.855 entradas, 39 DEX, Manifest,
recursos, controles, opções, JNI do frontend, runtime RetroArch, catálogo e capacidade
NES atualmente instalada. Não inclui testes, fixtures, SDK, chaves, ROMs ou BIOS novos.

## Evidência atual

- Java8/API36 compilado; JAR produtivo fechado com quatro classes, D8/API28 sem avisos.
- 43 checks de host: seleção da origem, prova/sessão, pooling, cancelamento,
  método/path inválidos e recusa de redirects/Location.
- Três handshakes TLS reais com o certificado público do serviço: origem/pin corretos
  aceitos; pin diferente e hostname diferente recusados.
- DEX28 compilado; 266 classes preservadas por comparação canônica.
- Três wrappers renovados com NDK r28c, exports/dependências originais e LOAD 16 KiB.
- APK unsigned montado e todas as entradas relidas; ZIP clássico, sem ZIP64.
- Zipalign 16 KiB passou e os cinco payloads alterados foram conferidos novamente.

APK unsigned inicial: SHA256
`4165acec63b1ec33d9532afb4b5a78b9d84a595fa333cc029882ecb684c4bade`,
2.712.262.321 bytes. Este SHA identifica a montagem anterior ao zipalign e à assinatura;
não é o hash de um APK instalável ou publicado. Materiais privados permanecem fora do Git.

Artefato alinhado ainda unsigned: SHA256
`d8ac31fa84ea1a8bf704878bf740e03599524d342474ef12ecc9a757ed08c805`,
2.713.640.743 bytes. Este é o artefato anterior à assinatura final.

APK final assinado: SHA256
`e69616ee6377920f808f3b5a267f5592ffff9ae70c2bbe2063c6902cd903c02a`,
2.713.648.143 bytes. Certificado original, assinaturas v2/v3 e alinhamento 16 KiB
conferidos; todas as 13.860 entradas finais relidas e comparadas à montagem aprovada.
A chave original foi localizada no material privado fornecido pelo operador e
permanece fora do Git. Nenhum APK desta candidata foi publicado ou instalado.

## Registro administrativo aplicado

O registrador v3 vigente recebeu os seis binários reais extraídos do APK assinado.
Suas 20 dependências distintas também foram conferidas. Foram acrescentados os quatro
IDs renovados e 78 vínculos dos mesmos modos N64/GameCube/Wii já aprovados, com IDs de
perfil limitados ao novo owner. Core, opções, controles, modos e fontes de aprovação
permaneceram iguais; nenhuma aprovação HLE PSX foi acrescentada.

Os 31 motores, 11.448 perfis e 6.587 modos anteriores foram preservados integralmente.
Totais após aplicação: 35 motores, 11.526 perfis e 6.665 modos. Respostas v3 assinadas
locais e públicas confirmaram os vínculos das três plataformas; seis recusas de
conteúdo/engine/capacidade indevidos passaram. Catálogo46, configurações, identidades
de conteúdo, licenças reais, DLL e processo da API permaneceram iguais, sem restart.
O cadastro não confirma gameplay no aparelho. [Recibo sanitizado](registration.json).

O vhost de produção também foi testado com duas sessões sintéticas e prova real,
conservando CA pública, hostname e pin. Um download completo de 4 MiB conferiu o SHA;
sessão estrangeira, reuso e expiração foram recusados. Após fechar uma leitura parcial,
o grant foi recusado e uma nova autorização funcionou. As licenças sintéticas foram
removidas e as reais preservadas. O socket dessa prova chegou ao vhost local; não
mede Internet do cliente nem execução Android. [Recibo](protected-download-validation.json).

O APK e o instalador foram copiados ao pendrive indicado pelo operador; o arquivo
copiado foi relido e seu SHA final conferido antes da ejeção segura. O kit permite
instalação pelo Windows ou abertura do APK no Android por USB/OTG compatível.

## Conclusão necessária no aparelho

Instalar o APK final assinado por atualização no aparelho autorizado ocioso,
preservando UID/dados/Keystore/licença/jogos/saves. Não interromper partida ou download.
O manifesto USB já identifica o APK final assinado e o kit inclui ADB para Windows.

Conferir autorização, download completo e SHA, grant expirado/reuso recusados,
cancelamento e nova autorização para retomar. Comparar velocidade em rede externa
com origem direta e antiga usando grants diferentes e o mesmo conteúdo. Validar
login/catálogo/capas na origem antiga. Não presumir homologação física ou ganho de
velocidade a partir dos fixtures ou dos testes públicos sem autorização.
